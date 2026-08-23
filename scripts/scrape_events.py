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

SOURCE   = 'https://www.surfcoastevents.com.au'
API      = SOURCE + '/wp-json/tribe/events/v1/events'
ROOT     = pathlib.Path(__file__).resolve().parent.parent
SEEN     = ROOT / 'scripts' / 'events_seen.json'
HORIZON  = 270          # days ahead to bother with
UA       = 'whattodo-janjuc/1.0 (+https://whattodo-nu.vercel.app)'

# ── the source's categories -> our 26 types, most specific first ────────────
# Every listing carries one or two categories, and the vaguer one ('Community',
# 'Major') is always paired with a sharper one, so first match wins is enough.
TYPE_PRIORITY = [
    ('Markets',                  'market'),
    ('Live Music',               'gig'),
    ('Sport',                    'sport-event'),
    ('Workshops & Talks',        'workshop'),
    ('Festivals & Celebrations', 'festival'),
    ('Major',                    'festival'),
    ('Art & Culture',            'cultural'),
    ('Health & Wellbeing',       'community'),
    ('Food & Wine',              'community'),
    ('Community',                'community'),
]

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
def text(s, limit=600):
    """Source text is third-party HTML. Strip it to plain prose; never eval it."""
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s or '')
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Stripping their markup leaves the venue name stuttering at the end
    # ("Torquay Torquay Torquay"). Collapse any word repeated back to back.
    s = re.sub(r'\b(\w[\w\'-]*)(\s+\1\b)+', r'\1', s, flags=re.I)
    if len(s) > limit:
        cut = s[:limit].rsplit(' ', 1)[0]
        s = cut + '…'
    return s or None

def clean_url(u):
    u = (u or '').strip()
    if not u.startswith(('http://', 'https://')): return None
    if 'maps.app.goo.gl' in u: return None     # these get fabricated — CLAUDE.md
    return u

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

def pick_type(inst):
    have = {html.unescape(c.get('name', '')) for c in inst.get('categories') or []}
    for name, t in TYPE_PRIORITY:
        if name in have: return t
    return 'community'

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
    info = clean_url(first.get('website')) or clean_url(first.get('url'))

    note = f"surfcoastevents.com.au/{slug}"
    if len(instances) > 1:
        note += f" — {len(instances)} occurrences listed, next {dates[0]}"
        if not rec: note += ", spacing irregular"
    note += f"; imported {datetime.date.today().isoformat()}, date not yet checked against a first-party page"

    row = {
        'name'           : html.unescape(first['title']).strip(),
        'type'           : pick_type(first),
        'starts_on'      : dates[0].isoformat(),
        'time_text'      : time_text(first),
        'venue'          : place,
        'location'       : where,
        'description'    : text(first.get('description') or first.get('excerpt')),
        'info_url'       : info,
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
        k = norm(r['name'])
        if k not in best or len(series[slug]) > len(series[best[k]]):
            best[k] = slug
    keep = {}
    for k, slug in best.items():
        dupes = [s for s, r in rows.items() if norm(r['name']) == k and s != slug]
        if dupes:
            rows[slug]['source_note'] += f"; also listed as {', '.join(sorted(dupes))}"
        keep[slug] = rows[slug]
    return dict(sorted(keep.items()))

# ── the database ────────────────────────────────────────────────────────────
def load_env():
    f = ROOT / '.env'
    if f.exists():
        for line in f.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

def db(method, path, body=None, extra=None):
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    key = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not key:
        sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY (environment or .env).")
    r = urllib.request.Request(url + path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    r.add_header('apikey', key); r.add_header('Authorization', 'Bearer ' + key)
    r.add_header('Content-Type', 'application/json')
    for k, v in (extra or {}).items(): r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}\n{e.read().decode()[:400]}")

def norm(s):
    return re.sub(r'[^a-z0-9]+', '', html.unescape(s or '').lower())

def seen_ids():
    if SEEN.exists():
        try: return set(json.loads(SEEN.read_text()).get('offered') or [])
        except json.JSONDecodeError: pass
    return set()

def save_seen(ids):
    SEEN.write_text(json.dumps(
        {'note': 'Series already offered by scrape_events.py. Delete a line to be '
                 'offered it again — otherwise something you rejected comes back '
                 'every week.',
         'offered': sorted(ids)}, indent=1) + '\n')

# ── main ────────────────────────────────────────────────────────────────────
def main(argv):
    write   = '--write' in argv
    as_json = argv[argv.index('--json') + 1] if '--json' in argv else None
    need_db = write or '--json' not in argv

    log(f"reading {API} …")
    raw = fetch_all()
    cands = collapse(raw)
    log(f"  {len(raw)} listings -> {len(cands)} series in the next {HORIZON} days")

    already = seen_ids()
    fresh   = {s: r for s, r in cands.items() if s not in already}

    if as_json and not need_db:
        pathlib.Path(as_json).write_text(json.dumps(list(fresh.values()), indent=1) + '\n')
        log(f"wrote {len(fresh)} row(s) to {as_json} — check them, then `sync.py add`")
        return

    load_env()
    existing = db('GET', '/rest/v1/events?select=id,name,starts_on,verified,source_note,added_by')
    by_name  = {}
    by_slug  = {}
    for e in existing:
        by_name.setdefault(norm(e['name']), e)
        m = re.search(r'surfcoastevents\.com\.au/([a-z0-9\-]+)', e.get('source_note') or '')
        if m: by_slug[m.group(1)] = e

    new, clash, drift = [], [], []
    for slug, row in cands.items():
        prior = by_slug.get(slug)
        if prior:
            if prior.get('starts_on') and prior['starts_on'] != row['starts_on']:
                drift.append((prior, row))
            continue
        hit = by_name.get(norm(row['name']))
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
        print(f"  {r['starts_on']}  {r['type']:<12} {r['name'][:44]:46} {(r['location'] or '?')[:16]}{rec}")

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
        got = db('POST', '/rest/v1/events', r, {'Prefer': 'return=representation'})
        print(f"added event {got[0]['id'] if got else '?'}: {r['name']}")
    for old, r in drift:
        if old['verified']: continue      # a human vouched for that date; ask them
        db('PATCH', f"/rest/v1/events?id=eq.{old['id']}",
           {'starts_on': r['starts_on'], 'source_note': r['source_note']})
        print(f"moved event {old['id']}: {old['starts_on']} -> {r['starts_on']}")

    save_seen(already | set(cands))
    print(f"\n{len(new)} added unverified. Review: python3 scripts/sync.py pending")

if __name__ == '__main__':
    main(sys.argv[1:])
