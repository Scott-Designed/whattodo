#!/usr/bin/env python3
"""Read each venue's own ticketing page and offer the gigs it lists.

    python3 scripts/scrape_venues.py              # look and report, writes nothing
    python3 scripts/scrape_venues.py --write      # insert the new ones
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
import os, sys, re, json, html, time, datetime, urllib.parse
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import eventlib as E

SKIP = set()          # platforms to leave alone this run, via --skip
LINK_CAP = 80         # ticket pages fetched per venue, per platform
POLITE   = 1.0        # seconds between fetches to one host — one request a
                      # second is plenty for a twice-weekly run over 15 sites
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
# Moshtix is deliberately NOT here. Its event pages do carry clean JSON-LD, so
# adding the pattern is a one-liner and it was tried on 27 Aug 2026 — but a
# Moshtix VENUE page links to other venues' shows, so following those links
# off Queenscliff Town Hall proposed twelve gigs at The Night Cat, Brunswick
# Ballroom, Howler and The Toff in Town, and offered to create those rooms.
# That is this file's own rule broken: a listing must never claim a ticket
# link it cannot prove is its own. A safe reader would take the venue page's
# OWN JSON-LD, which already lists only that venue's events, rather than
# crawling outward. Until that exists, Moshtix rows read nothing.
#
# Eventbrite is read through its own API, not by scraping — see step 2b in
# read_venue(). It stays in this set so the link-following branch never touches
# an /e/ page: an organiser id is what the API needs, and a loose ticket link on
# somebody's website does not carry one.
API_INSTEAD = {'Eventbrite'}

# A host page links to its own help pages, search, categories and back to
# itself. Fetching those is rude to them and pointless for us.
NOT_AN_EVENT = re.compile(r'(?i)/(host|search|help|support|about|terms|privacy|blog|'
                          r'categor|collection|organiser|profile|login|signup|gift|'
                          r'checkout|refund|contact)(/|$|\?)')
LISTING_WHEN_ANY = re.compile(r'(Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day,\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}')
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

# A venue's own gig listing, read straight off the page. This is the road that
# does not need a ticket to exist: a gig sold at the door has no ticket page,
# and following ticket links can never see it. These sites (a shared Surf Coast
# agency build) all print "NAME" then "Saturday, Oct 17, 2026 @ 7:00pm", so one
# parser serves the family.
#
# The stated weekday is used as a checksum: if "Saturday" is not actually a
# Saturday, the regex has misfired and the row is thrown away rather than
# guessed at. That check is what lets a date off this page count as high
# confidence — it is the venue's own listing, which CLAUDE.md treats as
# first-party for its own gig.
LISTING_WHEN = re.compile(
    r'^(?P<wd>Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day,\s+(?P<mon>[A-Z][a-z]{2})\s+'
    r'(?P<d>\d{1,2}),\s+(?P<y>\d{4})\s*(?:@\s*(?P<h>\d{1,2})(?::(?P<mi>\d{2}))?\s*(?P<ap>[ap]m))?',
    re.I)
ABBR = {m[:3].lower(): i for i, m in enumerate(
    ['January','February','March','April','May','June','July','August',
     'September','October','November','December'], 1)}
WD = ['Mon','Tues','Wednes','Thurs','Fri','Satur','Sun']

def to_lines(page):
    """Page -> visible text lines, block boundaries preserved."""
    h = re.sub(r'(?is)<(script|style).*?</\1>', ' ', page)
    h = re.sub(r'(?i)<(br|/?p|/?div|/?li|/?h[1-6]|/?tr|/?section|/?article)[^>]*>', '\n', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    out = []
    for line in html.unescape(h).splitlines():
        line = re.sub(r'\s+', ' ', line).strip()
        if line: out.append(line)
    return out

def from_listing(page, base):
    """Gigs read off a venue's own listing page. Ticket link optional."""
    lines = to_lines(page)
    out = []
    for i, line in enumerate(lines):
        m = LISTING_WHEN.match(line)
        if not m: continue
        mon = ABBR.get(m.group('mon').lower())
        if not mon: continue
        try: d = datetime.date(int(m.group('y')), mon, int(m.group('d')))
        except ValueError: continue
        if WD[d.weekday()].lower() != m.group('wd').lower():   # checksum
            continue
        name = next((lines[j] for j in range(i - 1, max(-1, i - 4), -1)
                     if len(lines[j]) > 3 and not LISTING_WHEN.match(lines[j])
                     and not re.fullmatch(r'(?i)buy tickets!?|tickets|more info', lines[j])), None)
        if not name: continue
        tt = None
        if m.group('h'):
            hh = int(m.group('h')) % 12 + (12 if m.group('ap').lower() == 'pm' else 0)
            tt = clockish(hh, int(m.group('mi') or 0))
        out.append({'name': ' '.join(name.split())[:200], 'raw_name': name, 'starts_on': d.isoformat(),
                    'ends_on': None, 'time_text': tt, 'description': None,
                    # The listing cannot say which ticket link is this gig's —
                    # taking the first on the page stamps one gig's ticket page
                    # onto all of them. merge() attaches the real one by date.
                    'url': E.clean_url(base),
                    'conf': 'high'})
    return out

# "SELLING FAST", "SOLD OUT" and "18+" are how a venue is selling the gig this
# week, not what the gig is called — and they go stale the moment it sells out.
# The venue's own name on the end is noise too; the row already knows the venue.
STATUS = re.compile(r'(?i)\b(selling fast|sold out|cancelled|canceled|postponed'
                    r'|rescheduled|new show|final release|last release|just announced)\b')

def tidy_name(raw, venue_name):
    n = STATUS.sub('', raw)
    n = re.sub(r'(?i)\s*\b18\+\s*$', '', n)
    if venue_name:
        n = re.sub(r'(?i)\s*[–—-]\s*' + re.escape(venue_name) + r'\s*(18\+)?\s*$', '', n)
    n = re.sub(r'^[\s–—\-|:,]+|[\s–—\-|:,]+$', '', n)
    n = re.sub(r'\s{2,}', ' ', n)
    n = re.sub(r'\s*[–—-]\s*[–—-]\s*', ' – ', n)
    return n.strip() or raw.strip()

def clockish(h, mi):
    ap = 'am' if h < 12 else 'pm'
    hh = h % 12 or 12
    return f"{hh}:{mi:02d}{ap}" if mi else f"{hh}{ap}"

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
    # An events_url is normally a deliberate claim that THIS page belongs to
    # THIS place — but 18 library branches carrying the identical URL is not 18
    # claims, it is one page that cannot say which branch a gig is at. Same
    # refusal as a shared website, one field along.
    if pinned and venue.get('__shared_pin'):
        return None, None, 'events_url is shared with other places — the feed importer covers these'
    if pinned:
        u = E.clean_url(pinned if pinned.startswith('http') else 'https://' + pinned)
        return (u, E.fetch(u), '') if u else (None, None, 'events_url is not a url')
    site = venue.get('website')
    if not site: return None, None, 'no website on file'
    # A website shared by several places cannot say which one a gig belongs to.
    # 18 library branches all carry grlc.vic.gov.au, so this read the same
    # homepage 18 times, found the one TryBooking link on it, and attributed it
    # to every branch — the organiser-is-not-the-venue trap wearing a new hat,
    # and the reason the back of house said "TryBooking" for a source whose 500
    # events all came from the iCal feed.
    #
    # An events_url is exempt above, because setting one is a deliberate claim
    # that THIS page belongs to THIS place. Guessing from a shared homepage is
    # not.
    if venue.get('__shared_site'):
        return None, None, 'website is shared with other places — set events_url to read it'
    site = E.clean_url(site if site.startswith('http') else 'https://' + site)
    if not site: return None, None, 'website is not a url'
    if site.startswith('http://'): site = 'https://' + site[7:]
    for path in GIG_PATHS:
        u = site.rstrip('/') + path
        page = E.fetch(u)
        if page and re.search(r'(?i)(humanitix|oztix|trybooking|eventbrite)', page):
            return u, page, f' [found at {path or "/"} — set events_url to lock it in]'
    return site, E.fetch(site), ' [homepage; no gig page found]'

def paged(src, page, limit=6):
    """The listing page and any /page/2/, /page/3/ … behind it. These sites show
    nine gigs a page and draw the pager in JavaScript, so a fetch only ever sees
    the first nine unless you ask for the rest by url."""
    pages = [page]
    base = src.rstrip('/')
    if re.search(r'/page/\d+$', base): return pages
    for n in range(2, limit + 1):
        nxt = E.fetch(f'{base}/page/{n}/')
        if not nxt or not LISTING_WHEN_ANY.search(nxt): break
        pages.append(nxt)
    return pages

def gigs_for(venue):
    """Everything readable for one venue, plus a note on how we got it."""
    # --skip has to cover the venue's own events_url too, not just links found
    # on it: pinning a Humanitix host page as the source would otherwise walk
    # straight past the guard and fetch the very thing we agreed not to.
    pinned = (venue.get('events_url') or venue.get('ticketing_url') or '').lower()
    for key, label, _ in TICKETERS:
        if key in SKIP and key in pinned:
            return [], f'{label} skipped (it is this venue\'s events_url)'

    src, page, hint = source_page(venue)
    if src is None: return [], hint
    if page is None:
        return [], ('robots.txt asks us not to read it' if not E.robots_ok(src)
                    else 'site did not respond')

    # 1 — the venue's own listing, across every page of it. Preferred, because
    #     it sees gigs that were never ticketed.
    sheets = paged(src, page)
    listed = [g for sheet in sheets for g in from_listing(sheet, src)]
    for g in listed: g['name'] = tidy_name(g['name'], venue.get('name'))
    listed = dedupe(listed)
    how = []
    if listed:
        how.append(f'own listing ({len(listed)} gigs'
                   + (f' over {len(sheets)} pages' if len(sheets) > 1 else '') + ')')

    # 2 — schema.org on the page itself
    direct = [g for g in (E.from_jsonld(o) for o in E.jsonld_events(page)) if g]
    for g in direct: g['conf'] = 'high'
    if direct: how.append(f'schema.org on the page ({len(direct)})')

    # 2b — Eventbrite, through its own API rather than its pages. An organiser
    #      page renders its list in JS, so there is nothing to follow; the API
    #      hands the events over WITH the venue attached, which is the fact that
    #      matters here. The organiser is not the room — all nine Creative
    #      Geelong events name the Makers Hub, not Creative Geelong Inc.
    eb_id = E.eventbrite_org_id(venue.get('events_url') or '')
    if eb_id:
        token = os.environ.get('EVENTBRITE_TOKEN')
        if not token:
            how.append('Eventbrite — set EVENTBRITE_TOKEN to read it')
        else:
            try:
                gigs = E.eventbrite_events(eb_id, token)
                # First-party and structured, with a real venue on each event:
                # the same standing as a venue's own gig listing.
                for g in gigs: g['conf'] = 'high'
                direct += gigs
                how.append(f'Eventbrite API ({len(gigs)})')
            except RuntimeError as e:
                how.append(f'Eventbrite API failed — {e}')

    # 3 — follow the ticketing links, for the detail the listing does not carry.
    #     Across every sheet: a gig on page 2 deserves its blurb too.
    page = '\n'.join(sheets)
    found = list(direct)
    for key, label, pat in TICKETERS:
        links = sorted(set(re.findall(pat, page)))
        links = [l for l in links if not NOT_AN_EVENT.search(l)]
        if key in SKIP:
            if links: how.append(f'{label} ({len(links)} links) skipped')
            continue
        links = [l for l in links if not l.rstrip('/').endswith(('/host', '/outlet'))]
        if not links: continue
        if label in API_INSTEAD:
            # Already read above when this row is an organiser page. Otherwise
            # these are loose /e/ links on somebody's website, and the API
            # cannot help with those without an id to ask about.
            if eb_id: continue
            how.append(f'{label} ({len(links)}) — needs an organiser page, or a person')
            continue
        got = 0
        for link in links[:LINK_CAP]:
            time.sleep(POLITE)
            tp = E.fetch(link)
            if tp is None: continue
            rows = [g for g in (E.from_jsonld(o) for o in E.jsonld_events(tp)) if g]
            for g in rows:
                g['conf'] = 'high'; g['url'] = g.get('url') or E.clean_url(link)
            if not rows and key == 'oztix':
                one = from_oztix(tp, link)
                if one: rows = [one]
            found += rows; got += len(rows)
        if got: how.append(f'{label} ({got} gigs from {min(len(links), LINK_CAP)} '
                           f'of {len(links)} links)')
        elif links: how.append(f'{label} ({len(links)} links, nothing readable)')
    # The same gig is often reachable at two urls, and an organiser's /host
    # page lists every one of them a second time. Collapse on name and date.
    # The listing knows which gigs exist — including the ones nobody ticketed.
    # The ticket pages know the blurb, the link and the exact times. Neither is
    # a superset of the other, so keep the listing as the spine and let the
    # ticket data fill it in.
    merged = merge(listed, dedupe(found), sheets, src)
    return merged, ('; '.join(how) or 'nothing machine-readable') + hint

def merge(spine, extra, sheets, src):
    """Listing rows enriched from ticket rows. Matched on date — one venue very
    rarely runs two gigs on a night, and the two sources name a gig differently
    ("SELLING FAST - Mudhoney..." against "Mudhoney"), so the date is the more
    reliable key. Where a date does carry two, the names must overlap."""
    if not spine: return extra
    by_date = {}
    for g in extra: by_date.setdefault(g['starts_on'], []).append(g)
    for g in spine:
        cands = by_date.get(g['starts_on']) or []
        if len(cands) > 1:
            words = set(re.findall(r'[a-z0-9]{4,}', g['name'].lower()))
            cands = [c for c in cands
                     if words & set(re.findall(r'[a-z0-9]{4,}', c['name'].lower()))] or cands
        if not cands: continue
        t = cands[0]
        g['description'] = g.get('description') or t.get('description')
        g['url']         = t.get('url') or g.get('url')
        g['time_text']   = g.get('time_text') or t.get('time_text')
        g['ends_on']     = g.get('ends_on') or t.get('ends_on')
    seen = {g['starts_on'] for g in spine}
    # a ticketed gig the listing never showed still counts
    return dedupe(spine + [g for g in extra if g['starts_on'] not in seen])

def dedupe(rows):
    """One gig is often reachable at several urls, and an organiser's /host page
    lists every one of them again. Collapse on name and date."""
    uniq = {}
    for g in rows:
        uniq.setdefault((E.norm(g['name']), g['starts_on']), g)
    return sorted(uniq.values(), key=lambda x: x['starts_on'])

# ── adding a room we have not met ───────────────────────────────────────────
# A ticketing platform's schema.org `location` carries a real name, suburb and
# street address, all written by the organiser. That is good enough to create a
# venue from — unlike the surfcoastevents feed, whose "venue" is as often a town
# or a beach. The guards below are what keep the difference honest.

# Names that are not places. The last two are a ticketing platform's own
# boilerplate: Humanitix publishes `location.name = "Hosted on Humanitix"` when
# the organiser has set no physical venue, and that string reached four Quiet
# Club rows as if it were an address you could stand at. A platform naming
# itself is the absence of a venue, not a venue.
GENERIC = {'online','tba','tbc','various','venue','virtual','zoom','to be advised',
           'hosted on humanitix','hosted online'}

def venue_key(name):
    """Match key that forgives 'The' and punctuation — Blackmans/Blackman's."""
    return E.norm(re.sub(r'(?i)^the\s+', '', (name or '').strip()))

def worth_adding(g):
    """Is this location solid enough to become a row? Reasons, not a bare no."""
    name = (g.get('venue_name') or '').strip()
    if len(name) < 3:               return None, 'no venue name'
    if name.lower() in GENERIC:     return None, f'"{name}" is not a place'
    sub = (g.get('venue_suburb') or '').strip()
    if sub and E.norm(name) == E.norm(sub):
        return None, f'"{name}" is just the suburb'
    if not (g.get('venue_address') or '').strip():
        return None, f'"{name}" has no street address'
    return name, None

def ensure_venue(g, src, registry, made, write, organisers=frozenset()):
    """place_id for this gig, creating the room if it is new and solid.

    A gig read off a venue's own listing carries no location of its own — the
    venue is the site we are reading, so the source row is the answer. That is
    only true when the source is a room: an organiser's page says nothing about
    where its events happen, so without a location we have to admit we do not
    know.
    """
    if not (g.get('venue_name') or '').strip():
        if (src.get('kind') or '').lower() == 'organiser':
            return None, 'organiser listing gave no venue'
        return src['id'], None
    key = venue_key(g.get('venue_name'))
    # Some listings name an organiser where the room should be — The Sewing
    # Collective runs its nights somewhere different each time, exactly as The
    # Sound Doctor does. There is no way to tell from the data, so this is
    # learned: mark one `kind = 'organiser'` in the venues table and it is never
    # mistaken for a room again.
    if key and key in organisers:
        return None, f'"{g["venue_name"]}" is an organiser, not a room — venue left unset'
    if key and key in registry: return registry[key], None
    name, why = worth_adding(g)
    if not name: return None, why
    row = {'name': name, 'suburb': g.get('venue_suburb') or None,
           'address': (g.get('venue_address') or '').split(',')[0].strip() or None,
           'kind_legacy': 'event venue',
           'source_note': f"added from a ticketing listing for an event held there, "
                          f"{E.today().isoformat()}"}
    if not write:
        made.append(('would add', name, row['suburb']))
        return None, f'new venue "{name}" — would be added'
    got = E.db('POST', '/rest/v1/places', row, {'Prefer': 'return=representation'})
    vid = got[0]['id'] if got else None
    if vid: registry[venue_key(name)] = vid
    made.append(('added', name, row['suburb']))
    return vid, f'added venue {vid} "{name}"'

# ── what a row is about ───────────────────────────────────────
# `types` on every row this scraper has ever written was a hardcoded literal
# naming one type. That was defensible while the registry WAS a music-venue
# spreadsheet and the type was called `gig`; it stopped being true the day an
# Eventbrite organiser page for a makers' hub and a wildlife sanctuary went in.
# Measured 31 Aug 2026: 54 of the 83 rows still carry it, and on Eventbrite
# nine of thirteen were wrong — four life-drawing classes, an eco-resin
# workshop and a Saturday market, all filed as live music. The same function's
# own docstring warns against "attributing a wildflower show to a live music
# promoter"; it then typed the wildflower show that way.
#
# So: evidence, or nothing. Empty shows as *unsorted* and asks a person, which
# is the choice scrape_events.py already makes for the feed's 'Sport' category
# and scrape_library.py makes for 161 of its rows.

# 1. schema.org's own subtype, published by the venue or the ticketer, and the
#    strongest of the three — it is the publisher saying what the thing is.
#    Deliberately partial: SportsEvent could be any of five types here, and
#    SocialEvent / BusinessEvent say nothing, so those fall through.
SCHEMA_TYPE = {
    'MusicEvent':      ['music'],
    'TheaterEvent':    ['theatre'],
    'ComedyEvent':     ['comedy'],
    'ScreeningEvent':  ['cinema'],
    'DanceEvent':      ['arts'],
    'LiteraryEvent':   ['reading'],
    'ExhibitionEvent': ['art gallery'],
    'ChildrensEvent':  ['kids'],
    'EducationEvent':  ['workshop'],
    'CourseInstance':  ['workshop'],
    'FoodEvent':       ['produce'],
    'Festival':        ['festival'],
}

# 2. Eventbrite's own category, which it applies to every event. An empty list
#    is a deliberate "it says something, and that something does not narrow to
#    one of our types" — which sport, which hobby — so the row falls through
#    to its title rather than taking a word nobody meant.
EB_CATEGORY = {
    'music':                       ['music'],
    'film, media & entertainment': ['cinema'],
    'arts':                        ['arts'],
    'food & drink':                ['produce'],
    'community & culture':         ['community'],
    'charity & causes':            ['community'],
    'family & education':          ['workshop'],
    'sports & fitness':            [],
    'hobbies & special interest':  [],
    'seasonal & holiday':          [],
}

# 3. What the title actually says. Same shape and same restraint as
#    scrape_library.py's TYPE_RULES — first match wins, and the first type in
#    the list is the word the row will print.
TITLE_RULES = [
    (r'life drawing|still life|drawing|painting|ceramic|pottery|print ?making',
                                                          ['arts', 'workshop']),
    (r'\bmarkets?\b',                                     ['market']),
    (r'live music|open mic|\bgig\b|\bband\b|\bdj\b|acoustic', ['music']),
    (r'comedy|stand.?up',                                 ['comedy']),
    (r'\bfilm\b|screening|cinema|\bmovie',                ['cinema']),
    (r'theatre|theater|pantomime',                        ['theatre']),
    (r'workshop|masterclass|\bclass\b|\bcourse\b|induction', ['workshop']),
    (r'festival',                                         ['festival']),
    (r'quiz|trivia',                                      ['community']),
    (r'book club|author talk|poetry|writers?\b',           ['reading']),
    (r'birdwatch|wildlife|spotlight tour|nature|\bwalk\b',  ['nature']),
    (r'\bkids\b|children|school holiday|toddler',          ['kids']),
    (r'tasting|degustation|long lunch',                   ['produce']),
]

def types_for(g):
    """What this row is about, from evidence only. [] means a person sorts it."""
    for t in str(g.get('schema_type') or '').split():
        if t in SCHEMA_TYPE:
            return list(SCHEMA_TYPE[t])
    for key in (g.get('subcategory'), g.get('category')):
        hit = EB_CATEGORY.get((key or '').lower())
        if hit:
            return list(hit)
    name = (g.get('name') or '').lower()
    for pat, types in TITLE_RULES:
        if re.search(pat, name):
            return list(types)
    return []

def build(venue, g, registry):
    """One gig -> an events row.

    The source row is not necessarily the room. A Humanitix host page can belong
    to a community organisation that runs events all over the shire, or to a
    promoter who hires a hall — The Sound Doctor puts its gigs on at Anglesea
    Memorial Hall. So the venue comes from the event where the event says, and
    place_id is set only when that name matches a row we already hold. No match
    means null, not a guess: attributing a wildflower show to a live music
    promoter because they share a hall is how this table got muddled.
    """
    vname = g.get('venue_name') or venue['name']
    # A generic is worse than nothing in the Where column: it prints as though
    # the row knows where it happens. `worth_adding` already refuses to make a
    # place from one; this refuses to write it as free text either.
    if (vname or '').strip().lower() in GENERIC:
        vname = None
    vsub  = g.get('venue_suburb') or (venue.get('suburb') if not g.get('venue_name') else None)
    vid   = g.pop('_place_id', None)
    conf  = g.get('conf', 'medium')
    # ── auto-verify, and exactly what it is claiming ────────────────────────
    # This file used to say nothing is ever inserted verified. That rule was
    # protecting two different things at once: "the machine's checks passed"
    # and "a person judged this belongs on the board". The first is entirely
    # mechanical, and refusing to state it left a queue nobody worked.
    #
    # A row earns `verified` here only when all four hold:
    #   * high confidence — read off a first-party page, AND the weekday printed
    #     on that page matched the date. A page that says Saturday 17 Sep when
    #     the 17th is a Thursday is refuted by its own contents and never gets
    #     here.
    #   * a real date,
    #   * a linked place, so the venue is a curated row and not a guess,
    #   * a source_note saying where it came from.
    #
    # A `medium` row — a date pulled out of a title by regex with no weekday to
    # check it against — still goes to the queue, which is what the queue is for.
    # Judgement calls a machine cannot make (is this worth listing, has it been
    # cancelled) remain a person's, and unverified is how they are asked for.
    auto = bool(conf == 'high' and g.get('starts_on') and vid)
    return {
        'name'           : g['name'][:200],
        'types'          : types_for(g),
        'starts_on'      : g['starts_on'],
        'ends_on'        : g.get('ends_on'),
        'time_text'      : g.get('time_text'),
        'venue'          : vname,
        'place_id'       : vid,
        'location'       : vsub,
        'description'    : g.get('description'),
        'info_url'       : g.get('url'),
        'ticket_url'     : g.get('url'),
        # Explicitly null, never the column's {any-weather} default. That
        # default was cut from 60% of entries to 16% in the Aug 2026 retag;
        # a scraper quietly restoring it would undo that within months. No
        # source publishes this vocabulary — a null is honest, a guess is not.
        'conditions'     : None,
        'date_confidence': conf,
        'added_by'       : 'venue-feed',
        'verified'       : auto,
        'source_note'    : (f"read from {urllib.parse.urlsplit(g.get('url') or '').netloc} "
                            f"for {venue['name']}; imported {E.today().isoformat()}"
                            + ("; auto-verified: first-party page, printed weekday "
                               "matched the date, linked to a known place"
                               if auto else "")),
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
    venues = E.db('GET', '/rest/v1/places?select=id,name,aliases,suburb,kind_legacy,website,events_url,ticketing_url'
                         '&order=name')
    # Mark the websites more than one place claims, so source_page can refuse
    # to guess from them.
    seen = {}
    for v in venues:
        w = (v.get('website') or '').strip().lower().rstrip('/')
        if w: seen[w] = seen.get(w, 0) + 1
    for v in venues:
        w = (v.get('website') or '').strip().lower().rstrip('/')
        v['__shared_site'] = bool(w and seen[w] > 1 and not
                                  (v.get('events_url') or v.get('ticketing_url')))
    pins = {}
    for v in venues:
        u = (v.get('events_url') or v.get('ticketing_url') or '').strip().lower().rstrip('/')
        if u: pins[u] = pins.get(u, 0) + 1
    for v in venues:
        u = (v.get('events_url') or v.get('ticketing_url') or '').strip().lower().rstrip('/')
        v['__shared_pin'] = bool(u and pins[u] > 1)

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

    # A place answers to its own name and to every alias on the row. Aliases are
    # what a merged duplicate leaves behind: the ticket listing calls it
    # "Blackman's Brewery, Torquay" and the row is called "Blackmans Brewery",
    # so without this the scraper creates the duplicate again on the next run.
    registry   = {venue_key(v['name']): v['id'] for v in venues}
    for v in venues:
        for a in (v.get('aliases') or []):
            registry.setdefault(venue_key(a), v['id'])
    organisers = {venue_key(v['name']) for v in venues
                  if (v.get('kind_legacy') or '').lower() == 'organiser'}
    made = []
    # all_rows, or PostgREST caps this at 1000 and says nothing about it — and
    # this is the duplicate check, so a short read does not fail, it silently
    # re-offers things the database already holds. Same fault as the one in
    # scrape_events.py; events was 502 when both were fixed, 1 Sep 2026.
    existing = E.db('GET', '/rest/v1/events?select=id,name,starts_on,place_id,'
                           'verified,source_note', None, None, all_rows=True)
    # Name AND date. Name alone silently swallowed every later occurrence of a
    # recurring thing: Mt Rothwell publishes "Into the Woodlands X Creatures of
    # the Night" on 12 Sep and again on 10 Oct, and the October one matched the
    # September row and was dropped as "already there". Its organiser page
    # listed seven events and the database held four, with the run reporting
    # the gap as duplicates rather than as anything missing.
    #
    # The date does not weaken what this map is FOR — the Holly Ringland case
    # below is one event on one date offered by 18 library sites, so all 18
    # still collapse to a single key. What it stops is two genuinely different
    # nights collapsing into one.
    by_name  = {(E.norm(e['name']), e.get('starts_on')): e for e in existing}
    by_slot  = {(e.get('place_id'), e.get('starts_on')): e for e in existing if e.get('place_id')}
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
            vid, vnote = ensure_venue(g, v, registry, made, write, organisers)
            g['_place_id'] = vid
            row = build(v, g, registry)
            if vnote: print(f"       venue: {vnote}")
            key = f"{v['id']}:{g['starts_on']}:{E.norm(g['name'])[:40]}"
            if key in seen:
                continue
            hit = (by_slot.get((row['place_id'], g['starts_on'])) if row['place_id'] else None) \
                  or by_name.get((E.norm(g['name']), g['starts_on']))
            if hit:
                dupe.append((hit, row))
                where = hit['id'] if hit.get('id') else 'another venue in this run'
                print(f"     {g['starts_on']}  {g['name'][:44]:46} already there as {where}")
                continue
            new.append((key, row))
            # A row queued THIS RUN has to join the dedupe maps too. They are
            # built once from the database before the loop, so without this the
            # same event found at a second venue passes the check again — every
            # one of the 20 GRLC library sites links the same TryBooking page,
            # and "Holly Ringland - The World Beneath Her Feet" was inserted 18
            # times on 30 Aug 2026. The `seen` key cannot catch it either: it is
            # keyed on the venue being read, so 18 libraries make 18 keys for
            # one event.
            queued = {'id': None, 'name': row['name'], 'starts_on': g['starts_on'],
                      'place_id': row['place_id']}
            by_name[(E.norm(g['name']), g['starts_on'])] = queued
            if row['place_id']:
                by_slot[(row['place_id'], g['starts_on'])] = queued
            print(f"     {g['starts_on']}  {g['name'][:44]:46} NEW  "
                  f"[{row['date_confidence']}{'  verified' if row['verified'] else ''}]")

    if made:
        print(f"\nrooms not previously on file — {len(made)}")
        for what, name, sub in made:
            print(f"   {what:9} {name[:40]:42} {sub or ''}")
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
    auto_n = sum(1 for _, r in new if r.get("verified"))
    print(f"\n{len(new)} added — {auto_n} auto-verified, {len(new)-auto_n} "
          f"waiting for you at /admin")

if __name__ == '__main__':
    main(sys.argv[1:])
