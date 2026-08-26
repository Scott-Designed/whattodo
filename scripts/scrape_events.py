#!/usr/bin/env python3
"""Pull the Surf Coast Events calendar and offer what's new.

    python3 scripts/scrape_events.py              # look, report, write nothing
    python3 scripts/scrape_events.py --write      # insert the new ones, unverified
    python3 scripts/scrape_events.py --json out.json   # emit rows for `sync.py add`

surfcoastevents.com.au runs WordPress with The Events Calendar, which publishes
a plain JSON API. Nothing here parses HTML and nothing here calls a model, so a
run costs nothing on either meter — see "Two meters" in CLAUDE.md.

Three things about the source that the code below exists to handle:

  * It explodes a recurring series into one listing per occurrence. Aireys Inlet
    Market is sixteen listings. Importing naively puts sixteen markets in the
    database. Instances of a series share a `slug`, so that is the grouping key.
  * It is edited constantly — about a third of listings changed in the week this
    was written — so dates drift after we import them. Drift on a row you have
    already verified is reported, never silently overwritten.
  * It is a calendar someone curates, not the organiser's own page. Everything
    lands `date_confidence = 'medium'`; only a human who has read a first-party
    page may raise that to high. See "Research rules" in CLAUDE.md.

Nothing is ever inserted verified. New rows show up in `sync.py pending`.
"""
import os, sys, json, re, html, pathlib, datetime, urllib.request, urllib.error, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eventlib as E

SOURCE   = 'https://www.surfcoastevents.com.au'
API      = SOURCE + '/wp-json/tribe/events/v1/events'
ROOT     = pathlib.Path(__file__).resolve().parent.parent
SEEN     = E.ROOT / 'scripts' / 'events_seen.json'
SEEN_NOTE = ('Series already offered by scrape_events.py. Delete a line to be '
             'offered it again — otherwise something you rejected comes back '
             'on Thursday.')
HORIZON  = 270          # days ahead to bother with
UA       = 'whattodo-janjuc/1.0 (+https://whattodo-nu.vercel.app)'

# ── the source's categories -> our types, most specific first ───────────────
# Every listing carries one or two categories, and the vaguer one ('Community',
# 'Major') is always paired with a sharper one, so first match wins is enough.
#
# A listing carries a LIST of types now, but this still proposes exactly one.
# The source's categories are far coarser than the vocabulary — 'Sport' covers
# surfing, running, swimming and cycling, and nothing in the feed says which —
# so guessing a second type here would be inventing data. A person adds the
# rest; `scripts/retype.py` is the record of what that looks like.
#
# Two of these changed meaning in the 26 -> 43 split. 'Sport' used to map to
# `sport-event`, which no longer exists and covered six sports; there is no
# honest single word for it now, so it lands unsorted and asks for a human.
# 'Art & Culture' used to map to `cultural`, which now means Wadawurrung
# Country specifically — a generic arts listing is `arts`.
TYPE_PRIORITY = [
    ('Markets',                  'market'),
    ('Live Music',               'gig'),
    ('Workshops & Talks',        'workshop'),
    ('Festivals & Celebrations', 'festival'),
    ('Major',                    'festival'),
    ('Art & Culture',            'arts'),
    ('Health & Wellbeing',       'community'),
    ('Food & Wine',              'community'),
    ('Community',                'community'),
]
# Categories with no honest single answer. The row is written with no type at
# all, which is what `null` has always meant here — "not sorted yet" — and it
# shows in the back-of-house flags rather than being quietly wrong.
TYPE_UNSURE = {'Sport'}

def log(*a): print(*a, file=sys.stderr)

# ── source ──────────────────────────────────────────────────────────────────
def fetch_all(horizon=HORIZON):
    """Every published listing from today to the horizon, following pagination."""
    today = datetime.date.today()
    params = {
        'start_date': today.isoformat(),
        'end_date'  : (today + datetime.timedelta(days=horizon)).isoformat(),
        'per_page'  : 50,
        'status'    : 'publish',
    }
    out, page = [], 1
    while True:
        q = dict(params, page=page)
        req = urllib.request.Request(API + '?' + urllib.parse.urlencode(q))
        req.add_header('User-Agent', UA)
        req.add_header('Accept', 'application/json')
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                doc = json.loads(r.read())
        except urllib.error.HTTPError as e:
            # Tribe answers 404 for a page past the end rather than an empty list.
            if e.code == 404 and page > 1: break
            sys.exit(f"{API} page {page} -> {e.code}\n{e.read().decode()[:300]}")
        except urllib.error.URLError as e:
            sys.exit(f"could not reach {SOURCE}: {e.reason}")
        batch = doc.get('events') or []
        out += batch
        if page >= (doc.get('total_pages') or 1) or not batch: break
        page += 1
    return out

# ── tidying ─────────────────────────────────────────────────────────────────
def day(s):  return datetime.date.fromisoformat(s[:10])
def clock(s):
    h, m = int(s[11:13]), int(s[14:16])
    ap = 'am' if h < 12 else 'pm'
    hh = h % 12 or 12
    return f"{hh}:{m:02d}{ap}" if m else f"{hh}{ap}"

def time_text(inst):
    if inst.get('all_day'): return 'All day'
    a, b = inst['start_date'], inst['end_date']
    if a[11:16] == '00:00' and b[11:16] in ('23:59', '00:00'): return 'All day'
    if a[11:16] == b[11:16]: return clock(a)
    same_day = a[:10] == b[:10]
    return f"{clock(a)}–{clock(b)}" if same_day else clock(a)

def pick_types(inst):
    have = {html.unescape(c.get('name', '')) for c in inst.get('categories') or []}
    for name, t in TYPE_PRIORITY:
        if name in have: return [t]
    if have & TYPE_UNSURE: return []      # a person picks the sport
    return ['community']

def recurrence_of(dates):
    """Name the pattern only if the instances actually keep to one."""
    if len(dates) < 3: return None
    gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
    bands = [('weekly', 6, 8), ('fortnightly', 13, 15),
             ('monthly', 27, 32), ('annual', 358, 372)]
    for name, lo, hi in bands:
        hits = sum(1 for g in gaps if lo <= g <= hi)
        if hits >= len(gaps) * 0.7: return name
    return None     # irregular — let a human look at it

# ── one series -> one candidate row ─────────────────────────────────────────
def build(slug, instances):
    instances = sorted(instances, key=lambda e: e['start_date'])
    first = instances[0]
    dates = [day(e['start_date']) for e in instances]
    rec   = recurrence_of(dates) if len(instances) > 1 else None

    venue = first.get('venue') or {}
    where = html.unescape(venue.get('city') or '') or None
    place = html.unescape(venue.get('venue') or '') or None

    # The organiser's own link if the source has one, else the source's page for
    # it. Both came from the source; neither is invented here.
    info = E.clean_url(first.get('website')) or E.clean_url(first.get('url'))

    note = f"surfcoastevents.com.au/{slug}"
    if len(instances) > 1:
        note += f" — {len(instances)} occurrences listed, next {dates[0]}"
        if not rec: note += ", spacing irregular"
    note += f"; imported {datetime.date.today().isoformat()}, date not yet checked against a first-party page"

    row = {
        'name'           : html.unescape(first['title']).strip(),
        'types'          : pick_types(first),
        'starts_on'      : dates[0].isoformat(),
        'time_text'      : time_text(first),
        'venue'          : place,
        'location'       : where,
        'description'    : E.text(first.get('description') or first.get('excerpt')),
        'info_url'       : info,
        # Explicitly null, never the column's {any-weather} default. That
        # default was cut from 60% of entries to 16% in the Aug 2026 retag;
        # a scraper quietly restoring it would undo that within months. No
        # source publishes this vocabulary — a null is honest, a guess is not.
        'conditions'     : None,
        'date_confidence': 'medium',
        'added_by'       : 'surfcoastevents',
        'source_note'    : note,
    }
    if rec: row['recurrence'] = rec
    # A single listing that spans days is a run, not a series.
    if len(instances) == 1:
        end = day(first['end_date'])
        if end > dates[0]: row['ends_on'] = end.isoformat()
    # km is deliberately absent: the database's distances are already known to be
    # shaky, and inventing more is how this project got burned. Fill it on review.
    return row

def collapse(events):
    series = {}
    for e in events:
        series.setdefault(e['slug'], []).append(e)
    rows = {s: build(s, i) for s, i in sorted(series.items())}

    # The source sometimes carries one thing under two slugs (an old series and
    # its replacement). Offer the busier one and say the other exists, rather
    # than pushing two rows with the same name at a database that refuses them.
    best = {}
    for slug, r in rows.items():
        k = E.norm(r['name'])
        if k not in best or len(series[slug]) > len(series[best[k]]):
            best[k] = slug
    keep = {}
    for k, slug in best.items():
        dupes = [s for s, r in rows.items() if E.norm(r['name']) == k and s != slug]
        if dupes:
            rows[slug]['source_note'] += f"; also listed as {', '.join(sorted(dupes))}"
        keep[slug] = rows[slug]
    return dict(sorted(keep.items()))

# The database, text tidying and the seen-file all live in eventlib now, so
# this script and scrape_venues.py cannot drift apart on them.

# ── main ────────────────────────────────────────────────────────────────────
def main(argv):
    write   = '--write' in argv
    as_json = argv[argv.index('--json') + 1] if '--json' in argv else None
    need_db = write or '--json' not in argv

    log(f"reading {API} …")
    raw = fetch_all()
    cands = collapse(raw)
    log(f"  {len(raw)} listings -> {len(cands)} series in the next {HORIZON} days")

    seen    = E.Seen(SEEN)
    already = seen.ids
    fresh   = {s: r for s, r in cands.items() if s not in already}

    if as_json and not need_db:
        pathlib.Path(as_json).write_text(json.dumps(list(fresh.values()), indent=1) + '\n')
        log(f"wrote {len(fresh)} row(s) to {as_json} — check them, then `sync.py add`")
        return

    E.load_env()
    existing = E.db('GET', '/rest/v1/events?select=id,name,starts_on,verified,source_note,added_by')
    by_name  = {}
    by_slug  = {}
    for e in existing:
        by_name.setdefault(E.norm(e['name']), e)
        m = re.search(r'surfcoastevents\.com\.au/([a-z0-9\-]+)', e.get('source_note') or '')
        if m: by_slug[m.group(1)] = e

    new, clash, drift = [], [], []
    for slug, row in cands.items():
        prior = by_slug.get(slug)
        if prior:
            if prior.get('starts_on') and prior['starts_on'] != row['starts_on']:
                drift.append((prior, row))
            continue
        hit = by_name.get(E.norm(row['name']))
        if hit:
            clash.append((hit, row)); continue
        if slug in already: continue
        new.append((slug, row))

    # ── report ──
    print(f"\nsurfcoastevents.com.au — {datetime.date.today().isoformat()}")
    print(f"  {len(raw)} listings, {len(cands)} distinct series, {len(existing)} events already in the database")

    print(f"\nNEW — {len(new)}")
    for _, r in new:
        rec = f"  [{r['recurrence']}]" if r.get('recurrence') else ''
        kinds = ' · '.join(r['types']) or 'unsorted'
        print(f"  {r['starts_on']}  {kinds:<12} {r['name'][:44]:46} {(r['location'] or '?')[:16]}{rec}")

    if drift:
        print(f"\nDATE MOVED since we imported it — {len(drift)}")
        for old, r in drift:
            lock = 'VERIFIED, left alone' if old['verified'] else 'unverified, updated'
            print(f"  {old['id']:>6}  {old['name'][:40]:42} {old['starts_on']} -> {r['starts_on']}  ({lock})")

    if clash:
        print(f"\nSAME NAME already in the database — {len(clash)}, skipped")
        for hit, r in clash:
            print(f"  {hit['id']:>6}  {r['name'][:52]}")

    if not write:
        print(f"\nnothing written. --write to insert the {len(new)} new one(s) as unverified.")
        return

    # ── write ──
    for slug, r in new:
        got = E.db('POST', '/rest/v1/events', r, {'Prefer': 'return=representation'})
        print(f"added event {got[0]['id'] if got else '?'}: {r['name']}")
    for old, r in drift:
        if old['verified']: continue      # a human vouched for that date; ask them
        E.db('PATCH', f"/rest/v1/events?id=eq.{old['id']}",
           {'starts_on': r['starts_on'], 'source_note': r['source_note']})
        print(f"moved event {old['id']}: {old['starts_on']} -> {r['starts_on']}")

    for slug in cands: seen.add(slug)
    seen.save(SEEN_NOTE)
    print(f"\n{len(new)} added unverified. Review: python3 scripts/sync.py pending")

if __name__ == '__main__':
    main(sys.argv[1:])
