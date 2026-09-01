#!/usr/bin/env python3
"""Pull Visit Geelong & The Bellarine's What's On, held back for a person.

    python3 scripts/scrape_vgb.py            # look and report, writes nothing
    python3 scripts/scrape_vgb.py --write    # insert, UNPUBLISHED
    python3 scripts/scrape_vgb.py --json f   # rows for `sync.py add` instead

EVERY ROW LANDS `published = false`, and that is Scott's instruction for this
source specifically: "I would like for events not to appear until they have been
published by me." Nothing here can ever put something in front of a reader —
only `/admin` can, behind the password. The board reads
`listings?published=is.true`, so an unpublished row is not in the list, not in a
facet count, not in the tally, not on the map and not findable by search.

`published` is NOT `verified` and both are written here: the rows arrive
unverified too, because nobody has checked them. See supabase/PUBLISHED.SQL for
why one flag could not do both jobs.

── WHERE THE DATA COMES FROM, AND WHY NOT THE OBVIOUS PLACE ──────────────────

The URL a person would send you — /search/What's+On/ — cannot be scraped. It is
139KB of chrome with no events in it, drawn client-side; /Whats-On is 250KB of
the same. The site is built on Roam and its search is Algolia, so the listings
only exist in the index.

The app id and a SEARCH-ONLY key are published in the page's own HTML for the
browser to use, and this asks the same index the same way the page does. Two
things to know about that: the key is not documented as an API and could be
rotated without notice (the run says so plainly rather than reading as an empty
region), and robots.txt on the site allows everything, names no AI crawler, and
its Content-Signal says `ai-input=yes` — so unlike Coast & Bay a Claude session
may read this one.

── THE PRODUCT PAGES CARRY schema.org Event AND IT MUST NOT BE USED ──────────

Each /products/… page has one JSON-LD block containing `"@type": "Event"`. It
looks exactly like the thing to parse and it has NO `startDate` — only
`datePublished` and `dateModified`, which are when the PAGE was written.
`eventlib.jsonld_events` requires a startDate and therefore correctly returns
zero; a looser reader would file every event on its publication date.

That is the GMBC `wp/v2/mec-events` failure in a new hat, and it is now the
second time this project has met it: a first-party-looking page is authoritative
about intent, not about correctness. The dates are only in the index.

── THE DATES ARE MELBOURNE INSTANTS, NOT DAYS ────────────────────────────────

`roam_products_eventDates` is a list of unix timestamps carrying a real start
time, and they have to be read in Australia/Melbourne. Measured, 1 Sep 2026:
Dave Hughes reads 7pm Melbourne and 9am UTC; a Father's Day lunch reads 12pm
Melbourne and 2am UTC. 251 of 1312 are exact UTC midnight, which looks like a
day-only convention and is not — those are simply the 10am starts.

A Melbourne 00:00 means no time was published, and that lands `time_text` null
rather than 'All day': we cannot tell the two apart, and a null is honest.

`roam_products_next_event` uses a DIFFERENT convention — Melbourne midnight, all
117 of them — so it is a day, not an instant. It is not used here; the dates are.

── ONE PRODUCT IS ONE ROW ────────────────────────────────────────────────────

A naive import is 556 rows for 119 things: 'Dinos at the Zoo' carries 258 dates
and an art exhibition 93. Measured shape of the 119, future dates only:

    single date  83   consecutive run  18   irregular  13   weekly  4   fortnightly  1

    consecutive  every gap exactly 1 day -> ONE row, starts_on + ends_on.
                 That is a season or an exhibition, not a series.
    weekly       >= 3 dates, every gap exactly 7   -> recurrence, nextDate rolls it
    fortnightly  >= 3 dates, every gap exactly 14  -> same
    irregular    one row at the next date, every date written into source_note,
                 NO recurrence — a pattern nobody published is not ours to invent.

Weekly needs three, not two: two dates a week apart is a coincidence. Monthly is
deliberately absent, because `nextDate()` does not roll monthly forward and a
recurrence the page cannot honour is worse than none.

── WHAT THIS SOURCE CANNOT GIVE ──────────────────────────────────────────────

No venue name and no address, anywhere — not in the index, not in the page, not
in its JSON-LD. So no `place_id` and no pin, and `venue` is null. The index does
carry a coordinate per product, and it goes in `source_note` for a person who
wants to build a places row rather than being silently dropped.

`km` is not set. Standing decision, not an omission.
"""
import os, sys, json, re, time, pathlib, datetime, zoneinfo, collections
import urllib.request, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eventlib as E

SITE   = 'visitgeelongbellarine.com.au'
ROOT   = 'https://www.' + SITE
APP    = 'C8OQZFNOEK'
# Search-only, published in the site's own HTML for its browser search to use.
KEY    = 'f583c7fa0a4fe0ec5fb178195c8cdb3c'
INDEX  = 'products_default_events'
FACET  = "roam_products_categories.lvl0:What's On"
MEL    = zoneinfo.ZoneInfo('Australia/Melbourne')
SEEN   = E.ROOT / 'scripts' / 'vgb_seen.json'
SEEN_NOTE = ('Products already offered by scrape_vgb.py, keyed on the objectID. '
             'Delete a line to be offered it again.')
HORIZON = 270           # days ahead to bother with

# ── the site's own sub-categories -> our types, most specific first ──────────
# One type, never a guess at a second: the site's categories are far coarser
# than the vocabulary, which is the same call scrape_events.py makes.
TYPE_PRIORITY = [
    ("What's On > Markets",            'market'),
    ("What's On > Classes & Worksops", 'workshop'),   # their spelling, not ours
    ("What's On > Festivals & Shows",  'festival'),
    ("What's On > Food & Wine",        'community'),
    ("What's On > Community",          'community'),
]
# 'Sports' covers running, cycling, swimming, surfing and paddling and the
# source never says which — so the row lands unsorted and asks for a person,
# exactly as the Surf Coast feed's 'Sport' does.
TYPE_UNSURE = {"What's On > Sports"}

def log(*a): print(*a, file=sys.stderr)

# ── the index ───────────────────────────────────────────────────────────────
def algolia(body):
    req = urllib.request.Request(
        f"https://{APP}-dsn.algolia.net/1/indexes/{INDEX}/query",
        data=json.dumps(body).encode(),
        headers={'X-Algolia-Application-Id': APP, 'X-Algolia-API-Key': KEY,
                 'User-Agent': E.UA, 'Content-Type': 'application/json'})
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            # 401/403 is the key, and no retry fixes a rejected key. Say which,
            # or a rotated key reads as a region with nothing on in it.
            if e.code in (401, 403):
                sys.exit(f"{SITE}: Algolia refused the key ({e.code}). It is the "
                         f"public search key published in the site's HTML and it "
                         f"has probably been rotated — read a fresh one out of "
                         f"{ROOT} (window.algolia) and update KEY.")
            if e.code >= 500 and attempt < 3:
                log(f"  {SITE} answered {e.code} — retry {attempt} of 2")
                time.sleep(5 * attempt); continue
            sys.exit(f"{SITE}: Algolia {e.code}\n{e.read().decode()[:300]}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            why = getattr(e, 'reason', e)
            if attempt == 3: sys.exit(f"could not reach Algolia after 3 tries: {why}")
            log(f"  {SITE} timed out ({why}) — retry {attempt} of 2")
            time.sleep(5 * attempt)

def fetch_all():
    """Every What's On product, following the index's own pagination."""
    out, page = [], 0
    while True:
        d = algolia({'query': '', 'hitsPerPage': 100, 'page': page,
                     'facetFilters': [[FACET]]})
        out += d['hits']
        page += 1
        if page >= d.get('nbPages', 1): break
    return out

# ── tidying ─────────────────────────────────────────────────────────────────
def melb(ts):
    """A timestamp as Melbourne wall time. Reading these in UTC shifts a 7pm gig
    to 9am the same day and a midday lunch to 2am — see the module docstring."""
    return datetime.datetime.fromtimestamp(ts, MEL)

def clock(dt):
    if dt.hour == 0 and dt.minute == 0: return None   # no time published
    ap = 'am' if dt.hour < 12 else 'pm'
    hh = dt.hour % 12 or 12
    return f"{hh}:{dt.minute:02d}{ap}" if dt.minute else f"{hh}{ap}"

def pick_types(h):
    have = set(h.get('roam_products_categories.lvl1') or [])
    for name, t in TYPE_PRIORITY:
        if name in have: return [t]
    if have & TYPE_UNSURE: return []      # a person picks the sport
    return ['community']

def shape_of(dates):
    """('run'|'weekly'|'fortnightly'|'one'|'irregular') for a product's dates.

    Conservative on purpose. Weekly wants three occurrences because two a week
    apart is a coincidence, and monthly is not offered at all — nextDate() does
    not roll it, so claiming it would promise a date the page cannot show.
    """
    if len(dates) == 1: return 'one'
    gaps = {(b - a).days for a, b in zip(dates, dates[1:])}
    if gaps == {1}:                      return 'run'
    if gaps == {7}  and len(dates) >= 3: return 'weekly'
    if gaps == {14} and len(dates) >= 3: return 'fortnightly'
    return 'irregular'

# ── one product -> one row ──────────────────────────────────────────────────
def build(h, today, horizon):
    stamps = sorted(melb(t) for t in h.get('roam_products_eventDates') or [])
    ahead  = [s for s in stamps if today <= s.date() <= horizon]
    if not ahead: return None
    days = sorted({s.date() for s in ahead})
    kind = shape_of(days)
    first = ahead[0]

    geo  = ((h.get('roam_products_locations') or {}).get('_geoloc') or [{}])[0]
    town = (geo.get('city') or '').strip() or None

    note = f"{SITE}{h['roam_products_url']}"
    if len(days) > 1:
        note += f" — {len(days)} dates listed, {kind}, {days[0]} to {days[-1]}"
    if kind == 'irregular':
        # No recurrence is claimed, so the other dates would otherwise be lost.
        shown = ', '.join(d.isoformat() for d in days[:12])
        note += f"; dates: {shown}{' …' if len(days) > 12 else ''}"
    if geo.get('lat') is not None:
        # The source's own coordinate. NOT written to a pin: an event is pinned
        # through place_id and this source names no venue to make a place from.
        note += (f"; source gives {geo['lat']},{geo['lng']}"
                 f"{' (' + geo['postcode'] + ')' if geo.get('postcode') else ''}"
                 f" — no venue named, so no place row was made")
    note += ("; imported " + today.isoformat() +
             ", held unpublished, date not checked against a first-party page")

    row = {
        'name'           : (h.get('title') or '').strip(),
        'types'          : pick_types(h),
        'starts_on'      : days[0].isoformat(),
        'time_text'      : clock(first),
        'venue'          : None,
        'location'       : town,
        'description'    : E.text(h.get('roam_products_description')),
        'info_url'       : ROOT + h['roam_products_url'],
        'conditions'     : None,
        # A tourism board republishing ATDW is a curated calendar, not the
        # organiser's own page — the same standing as surfcoastevents.
        'date_confidence': 'medium',
        'added_by'       : 'vgb',
        'source_note'    : note,
        # The whole point of this source. Never true from here.
        'published'      : False,
        'verified'       : False,
    }
    # EVERY row carries BOTH keys, null included. PostgREST refuses a batch
    # insert whose objects have different key sets — a bare 400, PGRST102 "All
    # object keys must match", naming no field. A run of 115 where some have an
    # end date and some have a recurrence is exactly that shape, and this file
    # already records the same failure from a places batch where one row had a
    # `kind` and the other did not.
    row['ends_on']    = days[-1].isoformat() if kind == 'run' else None
    row['recurrence'] = kind if kind in ('weekly', 'fortnightly') else None
    return row

# ── main ────────────────────────────────────────────────────────────────────
def main(argv):
    write   = '--write' in argv
    as_json = argv[argv.index('--json') + 1] if '--json' in argv else None
    need_db = write or '--json' not in argv

    today   = datetime.datetime.now(MEL).date()
    horizon = today + datetime.timedelta(days=HORIZON)
    log(f"reading the {INDEX} index at {SITE} …")
    hits = fetch_all()
    rows = {}
    for h in hits:
        r = build(h, today, horizon)
        if r and r['name']: rows[str(h['objectID'])] = r
    log(f"  {len(hits)} What's On products -> {len(rows)} with a date ahead")

    seen    = E.Seen(SEEN)
    already = seen.ids
    fresh   = {k: r for k, r in rows.items() if k not in already}

    if as_json and not need_db:
        pathlib.Path(as_json).write_text(json.dumps(list(fresh.values()), indent=1) + '\n')
        log(f"wrote {len(fresh)} row(s) to {as_json}")
        return 0

    E.load_env()
    # all_rows, or PostgREST caps this at 1000 and says nothing — and this is the
    # duplicate check, so a short read silently re-offers what we already hold.
    existing = E.db('GET', '/rest/v1/events?select=id,name,starts_on,published,'
                           'source_note,added_by', None, None, all_rows=True)
    by_name = {}
    by_id   = {}
    for e in existing:
        by_name.setdefault(E.norm(e['name']), e)
        m = re.search(r'visitgeelongbellarine\.com\.au(/products/[a-z0-9\-.]+)',
                      e.get('source_note') or '')
        if m: by_id[m.group(1)] = e

    new, clash, drift = [], [], []
    for oid, r in rows.items():
        path  = r['info_url'][len(ROOT):]
        prior = by_id.get(path)
        if prior:
            if prior.get('starts_on') and prior['starts_on'] != r['starts_on']:
                drift.append((prior, r))
            continue
        hit = by_name.get(E.norm(r['name']))
        if hit:
            clash.append((hit, r)); continue
        if oid in already: continue
        new.append((oid, r))

    # ── report ──
    print(f"\nsource {SITE} — {len(hits)} products, {len(rows)} dated, "
          f"{len(new)} new, {len(clash)} already held")
    print(f"  every row lands UNPUBLISHED — release them in /admin")

    print(f"\nNEW — {len(new)}")
    for _, r in new:
        kinds = ' · '.join(r['types']) or 'unsorted'
        span  = f"–{r['ends_on']}" if r.get('ends_on') else ''
        rec   = f"  [{r['recurrence']}]" if r.get('recurrence') else ''
        print(f"  {r['starts_on']}{span:<12} {kinds:<10} {r['name'][:42]:44} "
              f"{(r['location'] or '?')[:16]:18}{r['time_text'] or '—'}{rec}")

    if drift:
        print(f"\nDATE MOVED since we imported it — {len(drift)}")
        for old, r in drift:
            print(f"  {old['id']:>6}  {old['name'][:40]:42} "
                  f"{old['starts_on']} -> {r['starts_on']}")

    if clash:
        print(f"\nSAME NAME already in the database — {len(clash)}, skipped")
        for hit, r in clash:
            print(f"  {hit['id']:>6}  {r['name'][:52]}")

    # Which towns the site's vocabulary can actually file. A city it does not
    # know reaches no filter and no town page, and the symptom is a row with no
    # town rather than an error — the Mt Duneed lesson.
    towns = sorted({r['location'] for r in rows.values() if r['location']})
    known = suburbs_for(towns)
    lost  = [t for t in towns if not known.get(t)]
    if lost:
        n = sum(1 for r in rows.values() if r['location'] in lost)
        print(f"\nTOWNS suburbOf() DOES NOT KNOW — {len(lost)}, on {n} row(s)")
        print('  ' + ', '.join(lost))
        print('  Those rows reach no filter and no town page. Add them to SUBURBS '
              'in public/notice-vocab.js, or fold them into an existing town.')

    if not write:
        print(f"\nnothing written. --write to insert the {len(new)} new one(s), unpublished.")
        return 0

    # ── write ──
    # Batched, and the ledger is checkpointed after every batch: scrape_library
    # lost 307 rows' worth of ledger to a socket timeout because it only saved at
    # the end, and a naive re-run would have duplicated all of them.
    todo = [r for _, r in new]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        got = E.db('POST', '/rest/v1/events', batch, {'Prefer': 'return=representation'})
        for r in got or []: print(f"added event {r['id']} (unpublished): {r['name']}")
        for oid, r in new[i:i + 50]: seen.add(oid)
        seen.save(SEEN_NOTE)
    for oid in rows: seen.add(oid)
    seen.save(SEEN_NOTE)
    print(f"\n{len(new)} added, none of them on the site. "
          f"Release them at /admin -> Automations -> Review.")
    return 0

def suburbs_for(locations):
    """suburbOf() for a batch of town names, out of the site's own vocabulary.

    Evaluated through node rather than reimplemented here — one copy of the rule,
    the same trick classify_kinds.py uses. A second copy would disagree with the
    site eventually, which this project has already paid for twice.
    """
    import subprocess
    if not locations: return {}
    js = ("const fs=require('fs'),vm=require('vm');const b=vm.createContext({});"
          "vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),b);"
          "const f=vm.runInContext('suburbOf',b);"
          "const inp=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));"
          "const o={};for(const s of inp)o[s]=f(s);"
          "process.stdout.write(JSON.stringify(o))")
    tmp = E.ROOT / '.vgb.suburbs.json'
    tmp.write_text(json.dumps(sorted(locations)))
    try:
        out = subprocess.run(['node', '-e', js,
                              str(E.ROOT / 'public' / 'notice-vocab.js'), str(tmp)],
                             capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            log('could not read suburbOf from notice-vocab.js:\n' + out.stderr[:400])
            return {}
        return json.loads(out.stdout)
    finally:
        tmp.unlink(missing_ok=True)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
