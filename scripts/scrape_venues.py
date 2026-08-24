#!/usr/bin/env python3
"""Read each venue's own ticketing page and offer the gigs it lists.

    python3 scripts/scrape_venues.py              # look and report, writes nothing
    python3 scripts/scrape_venues.py --write      # insert the new ones, unverified
    python3 scripts/scrape_venues.py --only oztix # just the venues on one platform

The registry is the database, not this file: any row in `venues` with an
`events_url` gets read. Adding a venue is filling in that cell — never editing
code. There is deliberately no per-venue special case here; a source that needs
one is a source we do not take.

Strategy ladder, best first. A venue that reaches the bottom is reported, not
guessed at:

  1. schema.org Event on the page itself.
  2. Ticketing links found on the page, then each ticket page read for
     schema.org Event (Humanitix, TryBooking) or Oztix's patterned title.
  3. Nothing machine-readable — say so and move on.

**Date confidence.** A ticket page is the organiser's own, so by the research
rules in CLAUDE.md it is first-party and sufficient on its own. Where the date
came out of a machine-readable `startDate` it lands `high`. Where it was picked
out of a title with a regex it lands `medium`, because a regex can misfire and
a wrong date wearing a confident badge is the exact failure this project has
already paid for. Nothing is ever inserted `verified` either way.

**Who is asking.** Every request identifies as whattodo-janjuc and honours the
host's robots.txt (see eventlib.robots_ok). Humanitix permits that crawler but
refuses ClaudeBot, so an assistant must not fetch those pages on your behalf —
run this yourself the first time.
"""
import sys, re, json, html, datetime, urllib.parse
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import eventlib as E

SKIP = set()          # platforms to leave alone this run, via --skip
SEEN_FILE = E.ROOT / 'scripts' / 'venues_seen.json'
SEEN_NOTE = ('Gigs already offered by scrape_venues.py. Delete a line to be offered '
             'it again — otherwise something you rejected comes back next week.')
HORIZON   = 300          # days ahead worth caring about

# Every one of these white-labels a subdomain per venue — Torquay Hotel's gigs
# sit on BOTH tickets.oztix.com.au and torquayhotel.oztix.com.au, and hardcoding
# the first cost us half that venue's listings. Match the domain, not a guess at
# the subdomain.
TICKETERS = [
    ('humanitix',  'Humanitix',  r'https://(?:[a-z0-9-]+\.)?humanitix\.com/[a-z0-9\-/]+'),
    ('oztix',      'Oztix',      r'https://(?:[a-z0-9-]+\.)?oztix\.com\.au/outlet/event/[a-z0-9\-]+'),
    ('trybooking', 'TryBooking', r'https://(?:[a-z0-9-]+\.)?trybooking\.com/[A-Za-z0-9\-/]+'),
    ('eventbrite', 'Eventbrite', r'https://(?:[a-z0-9-]+\.)?eventbrite\.com(?:\.au)?/e/[A-Za-z0-9\-]+'),
]
# Eventbrite publishes a free API; scraping it is the worse road, so we only
# note that a venue uses it and leave the row for a human.
API_INSTEAD = {'Eventbrite'}

MONTHS = {m.lower(): i for i, m in enumerate(
    ['January','February','March','April','May','June','July','August',
     'September','October','November','December'], 1)}

# Oztix builds this title from its own database, so it is machine-made rather
# than typed by a publican: "<gig> Tickets at <venue> (<suburb>, VIC) on
# Saturday, 5 September 2026".
OZTIX_TITLE = re.compile(
    r'^(?P<name>.+?)\s+Tickets at\s+(?P<venue>.+?)\s*\('
    r'(?P<suburb>[^,)]+),\s*(?P<state>[A-Z]{2,3})\)\s*on\s+'
    r'\w+,\s*(?P<d>\d{1,2})\s+(?P<mon>[A-Za-z]+)\s+(?P<y>\d{4})', re.S)

def meta(page, key):
    for m in re.findall(r'(?is)<meta[^>]+>', page or ''):
        k = re.search(r'(?i)(?:property|name)\s*=\s*["\']([^"\']+)', m)
        v = re.search(r'(?i)content\s*=\s*["\']([^"\']*)', m)
        if k and v and k.group(1).lower() == key: return html.unescape(v.group(1)).strip()
    return None

def from_oztix(page, url):
    t = re.search(r'(?is)<title>(.*?)</title>', page or '')
    if not t: return None
    m = OZTIX_TITLE.match(html.unescape(t.group(1)).strip())
    if not m: return None
    mon = MONTHS.get(m.group('mon').lower())
    if not mon: return None
    try: d = datetime.date(int(m.group('y')), mon, int(m.group('d')))
    except ValueError: return None
    return {'name': m.group('name').strip(), 'starts_on': d.isoformat(),
            'ends_on': None, 'time_text': None,
            'description': E.text(meta(page, 'og:description')),
            'url': E.clean_url(url), 'conf': 'medium'}

GIG_PATHS = ['', '/gigs', '/events', '/whats-on', '/live-music', '/gig-guide']

def source_page(venue):
    """The page to read, and where it came from. events_url is the deliberate
    answer; falling back to the website and trying the usual paths is a
    convenience that reports what worked, so you can pin it down properly."""
    pinned = venue.get('events_url') or venue.get('ticketing_url')
    if pinned:
        u = E.clean_url(pinned if pinned.startswith('http') else 'https://' + pinned)
        return (u, E.fetch(u), '') if u else (None, None, 'events_url is not a url')
    site = venue.get('website')
    if not site: return None, None, 'no website on file'
    site = E.clean_url(site if site.startswith('http') else 'https://' + site)
    if not site: return None, None, 'website is not a url'
    if site.startswith('http://'): site = 'https://' + site[7:]
    for path in GIG_PATHS:
        u = site.rstrip('/') + path
        page = E.fetch(u)
        if page and re.search(r'(?i)(humanitix|oztix|trybooking|eventbrite)', page):
            return u, page, f' [found at {path or "/"} — set events_url to lock it in]'
    return site, E.fetch(site), ' [homepage; no gig page found]'

def gigs_for(venue):
    """Everything readable for one venue, plus a note on how we got it."""
    src, page, hint = source_page(venue)
    if src is None: return [], hint
    if page is None:
        return [], ('robots.txt asks us not to read it' if not E.robots_ok(src)
                    else 'site did not respond')

    # 1 — the page speaks schema.org itself
    direct = [g for g in (E.from_jsonld(o) for o in E.jsonld_events(page)) if g]
    if direct:
        for g in direct: g['conf'] = 'high'
        return direct, f'schema.org Event on the page ({len(direct)})' + hint

    # 2 — follow the ticketing links it carries
    found, how = [], []
    for key, label, pat in TICKETERS:
        links = sorted(set(re.findall(pat, page)))
        if key in SKIP:
            if links: how.append(f'{label} ({len(links)} links) skipped')
            continue
        links = [l for l in links if not l.rstrip('/').endswith(('/host', '/outlet'))]
        if not links: continue
        if label in API_INSTEAD:
            how.append(f'{label} ({len(links)}) — has a free API, left for a human')
            continue
        got = 0
        for link in links[:80]:
            tp = E.fetch(link)
            if tp is None: continue
            rows = [g for g in (E.from_jsonld(o) for o in E.jsonld_events(tp)) if g]
            for g in rows:
                g['conf'] = 'high'; g['url'] = g.get('url') or E.clean_url(link)
            if not rows and key == 'oztix':
                one = from_oztix(tp, link)
                if one: rows = [one]
            found += rows; got += len(rows)
        if got: how.append(f'{label} ({got} of {len(links)} links)')
        elif links: how.append(f'{label} ({len(links)} links, nothing readable)')
    # The same gig is often reachable at two urls, and an organiser's /host
    # page lists every one of them a second time. Collapse on name and date.
    uniq = {}
    for g in found:
        uniq.setdefault((E.norm(g['name']), g['starts_on']), g)
    return list(uniq.values()), ('; '.join(how) or 'nothing machine-readable') + hint

def build(venue, g):
    """One gig -> an events row. The venue is ours, so it is trusted."""
    return {
        'name'           : g['name'][:200],
        'type'           : 'gig',
        'starts_on'      : g['starts_on'],
        'ends_on'        : g.get('ends_on'),
        'time_text'      : g.get('time_text'),
        'venue'          : venue['name'],
        'venue_id'       : venue['id'],
        'location'       : venue.get('suburb'),
        'description'    : g.get('description'),
        'info_url'       : g.get('url'),
        'ticket_url'     : g.get('url'),
        'date_confidence': g.get('conf', 'medium'),
        'added_by'       : 'venue-feed',
        'source_note'    : (f"read from {urllib.parse.urlsplit(g.get('url') or '').netloc} "
                            f"for {venue['name']}; imported {E.today().isoformat()}"),
    }
    # km is deliberately absent — see CLAUDE.md. Fill it in on review.

def main(argv):
    write = '--write' in argv
    only  = argv[argv.index('--only') + 1].lower() if '--only' in argv else None
    skip  = {x.strip().lower() for x in argv[argv.index('--skip') + 1].split(',')} \
            if '--skip' in argv else set()
    if skip: print(f"  (skipping: {', '.join(sorted(skip))})")
    globals()['SKIP'] = skip

    E.load_env()
    venues = E.db('GET', '/rest/v1/venues?select=id,name,suburb,website,events_url,ticketing_url'
                         '&order=name')
    live = [v for v in venues if (v.get('events_url') or v.get('ticketing_url')
                                  or v.get('website'))]
    if only:
        live = [v for v in live if only in ((v.get('events_url') or '') +
                                            (v.get('ticketing_url') or '') +
                                            (v.get('website') or '')).lower()]

    print(f"\nvenue feeds — {E.today().isoformat()}")
    print(f"  {len(venues)} venues, {len(live)} with somewhere to look"
          + (f" (filtered to '{only}')" if only else ""))
    if not live:
        print("\n  Nothing to read. Put a ticketing page in venues.events_url and run again.")
        return

    existing = E.db('GET', '/rest/v1/events?select=id,name,starts_on,venue_id,verified,source_note')
    by_name  = {E.norm(e['name']): e for e in existing}
    by_slot  = {(e.get('venue_id'), e.get('starts_on')): e for e in existing if e.get('venue_id')}
    seen     = E.Seen(SEEN_FILE)
    horizon  = (E.today() + datetime.timedelta(days=HORIZON)).isoformat()
    today    = E.today().isoformat()

    new, dupe, quiet = [], [], []
    for v in live:
        gigs, how = gigs_for(v)
        gigs = [g for g in gigs if g.get('name') and today <= g['starts_on'] <= horizon]
        print(f"\n  {v['name']} — {how}")
        if not gigs:
            quiet.append(v); continue
        for g in sorted(gigs, key=lambda x: x['starts_on']):
            row = build(v, g)
            key = f"{v['id']}:{g['starts_on']}:{E.norm(g['name'])[:40]}"
            if key in seen:
                continue
            hit = by_slot.get((v['id'], g['starts_on'])) or by_name.get(E.norm(g['name']))
            if hit:
                dupe.append((hit, row))
                print(f"     {g['starts_on']}  {g['name'][:44]:46} already there as {hit['id']}")
                continue
            new.append((key, row))
            print(f"     {g['starts_on']}  {g['name'][:44]:46} NEW  [{row['date_confidence']}]")

    print(f"\n{len(new)} new, {len(dupe)} already in the database, "
          f"{len(quiet)} venue(s) with nothing readable")
    if not write:
        print(f"nothing written. --write to insert the {len(new)} new one(s) as unverified.")
        return
    for key, row in new:
        got = E.db('POST', '/rest/v1/events', row, {'Prefer': 'return=representation'})
        print(f"added event {got[0]['id'] if got else '?'}: {row['name']}")
        seen.add(key)
    seen.save(SEEN_NOTE)
    print(f"\n{len(new)} added unverified. Review: python3 scripts/sync.py pending")

if __name__ == '__main__':
    main(sys.argv[1:])
