#!/usr/bin/env python3
"""Pull the WordPress event calendars we watch and offer what's new.

    python3 scripts/scrape_events.py              # look, report, write nothing
    python3 scripts/scrape_events.py --write      # insert the new ones, unverified
    python3 scripts/scrape_events.py --json out.json   # emit rows for `sync.py add`
    python3 scripts/scrape_events.py --only coastandbay   # one source

Both sources run WordPress with The Events Calendar, which publishes a plain
JSON API at the same path on every install — so a second site costs a row in
SOURCES and no new parser. Nothing here parses HTML and nothing here calls a
model, so a run costs nothing on either meter — see "Two meters" in CLAUDE.md.

WHAT IS PER-SOURCE, and why it is not just the URL. This script was hardwired to
surfcoastevents for months, and the URL was the least of it: the provenance note,
`added_by`, the regex that finds a row's own slug again, and the seen ledger were
all written as if there could only ever be one feed. The ledger is the sharp one
— it was keyed on SLUG ALONE, and two WordPress sites can each publish a series
called `spring-market`. The second one would have been read, matched against the
first's ledger entry, and silently never offered. No error, no row, nothing to
notice. Keys are `<site>/<slug>` now, and bare ones are read as surfcoastevents,
which is the only source there has ever been.

A source that cannot be read does not stop the others — one site having a bad
morning is not a reason to skip the rest — but the run still exits non-zero, so
the Action goes red and somebody looks.

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
import os, sys, json, re, html, time, pathlib, datetime, collections
import urllib.request, urllib.error, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eventlib as E

# ── the sources ─────────────────────────────────────────────────────────────
# `key` is what lands in `added_by`; `site` is what lands in `source_note` and
# keys the seen ledger. Both are written into rows that outlive this file, so
# neither may be renamed without migrating the database and the ledger with it.
#
# Adding a WordPress/Events Calendar site is a row here and nothing else. Adding
# anything that is NOT that is not this script's job — the API path below is the
# whole reason one parser covers both.
SOURCES = [
    {'key': 'surfcoastevents', 'site': 'surfcoastevents.com.au',
     'root': 'https://www.surfcoastevents.com.au', 'label': 'Surf Coast Events'},
    # Coast & Bay disallows ClaudeBot for the whole site and allows everyone
    # else, so the Action and a terminal read it and an assistant must not —
    # the Humanitix rule, one domain wider. robots_ok() below is what enforces
    # it rather than a note somebody has to remember.
    {'key': 'coastandbay', 'site': 'coastandbay.com.au',
     'root': 'https://coastandbay.com.au', 'label': 'Coast & Bay'},
]
API_PATH = '/wp-json/tribe/events/v1/events'
# The site a bare ledger key belonged to, back when a slug alone was the key.
FIRST_SITE = 'surfcoastevents.com.au'
# Finds a row's own source and slug in its source_note, so a re-run recognises
# what it wrote last time. Built from SOURCES so a new site cannot be forgotten.
SLUG_RE = re.compile(r'(' + '|'.join(re.escape(s['site']) for s in SOURCES)
                     + r')/([a-z0-9\-]+)')


class SourceDown(Exception):
    """This site could not be read. The others still can."""
ROOT     = pathlib.Path(__file__).resolve().parent.parent
SEEN     = E.ROOT / 'scripts' / 'events_seen.json'
SEEN_NOTE = ('Series already offered by scrape_events.py, keyed <site>/<slug> '
             'because two sites can publish the same slug. Delete a line to be '
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
    ('Live Music',               'music'),
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
def fetch_all(src, horizon=HORIZON):
    """Every published listing from today to the horizon, following pagination.

    Raises SourceDown rather than exiting, so one site being unreachable does
    not take the rest of the run with it.
    """
    api   = src['root'] + API_PATH
    today = datetime.date.today()
    # Asked once per host and cached, so this is one request per run per site.
    if not E.robots_ok(api):
        raise SourceDown("robots.txt says no — not read")
    params = {
        'start_date': today.isoformat(),
        'end_date'  : (today + datetime.timedelta(days=horizon)).isoformat(),
        'per_page'  : 50,
        'status'    : 'publish',
    }
    out, page = [], 1
    while True:
        q = dict(params, page=page)
        req = urllib.request.Request(api + '?' + urllib.parse.urlencode(q))
        req.add_header('User-Agent', UA)
        req.add_header('Accept', 'application/json')
        # Retry a slow or dropped read rather than losing the whole run to it.
        # A bare socket TimeoutError is NOT a URLError, so it used to propagate
        # straight out and fail the job — 30 Aug 2026, twenty minutes of venue
        # scraping wasted because the calendar timed out in the first second.
        doc = None
        for attempt in (1, 2, 3):
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    doc = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                # Tribe answers 404 for a page past the end, not an empty list.
                if e.code == 404 and page > 1: doc = None; break
                # A 5xx is the site having a moment, not an answer. It was
                # serving 503 on 30 Aug 2026 while this was being written.
                if e.code >= 500 and attempt < 3:
                    E.log(f"  {src['site']} answered {e.code} — retry {attempt} of 2")
                    time.sleep(5 * attempt); continue
                raise SourceDown(f"page {page} answered {e.code}") from None
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                why = getattr(e, 'reason', e)
                if attempt == 3:
                    raise SourceDown(f"unreachable after 3 tries: {why}") from None
                E.log(f"  {src['site']} timed out ({why}) — retry {attempt} of 2")
                time.sleep(5 * attempt)
        if doc is None: break
        batch = doc.get('events') or []
        out += batch
        if page >= (doc.get('total_pages') or 1) or not batch: break
        page += 1
    return out

# ── tidying ─────────────────────────────────────────────────────────────────
# The stamp a Tribe install writes is NOT a fixed width, and reading it by
# character position is how the second feed crashed on its first run:
# surfcoastevents pads its hours ("2026-09-05 09:00:00") and coastandbay does
# not ("2026-09-05 9:00:00"), so s[11:13] came back "9:" and int() threw. Two
# installs of the same plugin disagreeing about a format is the ordinary case,
# not a broken site — so nothing here may assume a width, a separator, or that
# the seconds are present at all.
STAMP = re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?')

def stamp(s):
    """(date, hour, minute) out of whatever the API wrote, or None.

    A date with no time reads as midnight, which is what an all-day listing is.
    """
    m = STAMP.match((s or '').strip())
    if not m: return None
    y, mo, d, h, mi = m.groups()
    try: date = datetime.date(int(y), int(mo), int(d))
    except ValueError: return None
    return date, int(h or 0), int(mi or 0)

def day(s):
    got = stamp(s)
    if not got: raise ValueError(f"cannot read a date out of {s!r}")
    return got[0]

def clock(s):
    _, h, m = stamp(s)
    ap = 'am' if h < 12 else 'pm'
    hh = h % 12 or 12
    return f"{hh}:{m:02d}{ap}" if m else f"{hh}{ap}"

def time_text(inst):
    """What to print for the time, or None if the source did not say.

    None rather than a guess: a listing with no readable time still belongs in
    the database, and the row says nothing about when rather than something
    wrong. Same rule as km and the conditions default.
    """
    if inst.get('all_day'): return 'All day'
    a, b = stamp(inst.get('start_date')), stamp(inst.get('end_date'))
    if not a: return None
    if not b: return clock(inst['start_date'])
    ha, hb = a[1:], b[1:]
    if ha == (0, 0) and hb in ((23, 59), (0, 0)): return 'All day'
    if ha == hb: return clock(inst['start_date'])
    same_day = a[0] == b[0]
    return (f"{clock(inst['start_date'])}–{clock(inst['end_date'])}"
            if same_day else clock(inst['start_date']))

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
def build(src, slug, instances):
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

    note = f"{src['site']}/{slug}"
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
        'added_by'       : src['key'],
        # NOTHING FROM AN AUTOMATION GOES ON THE SITE UNTIL A PERSON SAYS SO.
        # Scott's rule, 1 Sep 2026, generalised from the one source it was
        # written for: "Anything from scrapers goes in for review, and doesn't
        # go on site until I approve." Before this, a scraped row was live from
        # the moment it was written and merely wore an `unverified` badge — so
        # the review queue was reviewing things readers could already see.
        'published'      : False,
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

def merge(cands, twice, src, one):
    """Fold one source's series into the run, keeping a thing carried twice once.

    Two local calendars covering one coast WILL carry the same market and the
    same festival — Coast & Bay is a Surf Coast publication, so overlap with the
    shire's own calendar is the expected case, not the edge one. Within a source
    `collapse` has already settled a name carried under two slugs; across sources
    the earlier entry in SOURCES wins and the loser is written into the winner's
    source_note, so the row says where else it was seen.

    Keying on the NAME rather than the slug is the whole point: the two sites
    have separate slug spaces and will never agree on one, so a slug match would
    catch nothing. Reported every run whether or not anything is written.
    """
    have = {E.norm(r['name']): k for k, r in cands.items()}
    for slug, row in one.items():
        first = have.get(E.norm(row['name']))
        if first:
            twice.append((first, src['site'], row['name']))
            cands[first]['source_note'] += f"; also listed by {src['site']}/{slug}"
            continue
        cands[(src['site'], slug)] = row
    return cands


def collapse(src, events):
    series = {}
    # A listing whose start date cannot be read is dropped and counted, never
    # guessed at and never allowed to kill the run — one malformed row out of a
    # hundred is not a reason to lose the other ninety-nine.
    unreadable = [e.get('slug') for e in events if not stamp(e.get('start_date'))]
    for e in events:
        if e.get('slug') in unreadable: continue
        series.setdefault(e['slug'], []).append(e)
    if unreadable:
        log(f"  {src['site']}: {len(unreadable)} listing(s) with an unreadable "
            f"start date, skipped: {', '.join(sorted(set(unreadable))[:5])}")
    rows = {s: build(src, s, i) for s, i in sorted(series.items())}

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
    only    = argv[argv.index('--only') + 1] if '--only' in argv else None
    need_db = write or '--json' not in argv

    sources = [s for s in SOURCES if not only or only in (s['key'], s['site'])]
    if not sources:
        sys.exit(f"--only {only}: no such source. Known: "
                 + ', '.join(s['key'] for s in SOURCES))

    # ── read every source ──
    # Candidates are keyed (site, slug), because a slug is only unique within
    # the site that published it. Sources are read in SOURCES order and that
    # order is what settles a cross-source duplicate below.
    cands, counts, down, twice = {}, {}, {}, []
    for src in sources:
        log(f"reading {src['root'] + API_PATH} …")
        try:
            raw = fetch_all(src)
        except SourceDown as why:
            down[src['site']] = str(why)
            log(f"  {src['site']}: {why}")
            continue
        one = collapse(src, raw)
        counts[src['site']] = (len(raw), len(one))
        log(f"  {src['site']}: {len(raw)} listings -> {len(one)} series")
        merge(cands, twice, src, one)

    # The ledger was keyed on slug alone when there was one feed. A bare key is
    # read as the source that wrote it; the file is rewritten qualified on the
    # next --write, so this upgrade runs once and then does nothing.
    seen    = E.Seen(SEEN)
    seen.ids = {k if '/' in k else f"{FIRST_SITE}/{k}" for k in seen.ids}
    already = seen.ids
    fresh   = {k: r for k, r in cands.items() if f"{k[0]}/{k[1]}" not in already}

    if as_json and not need_db:
        pathlib.Path(as_json).write_text(json.dumps(list(fresh.values()), indent=1) + '\n')
        log(f"wrote {len(fresh)} row(s) to {as_json} — check them, then `sync.py add`")
        return 1 if down else 0

    E.load_env()
    # all_rows, or PostgREST caps this at 1000 and says nothing about it. This is
    # the duplicate check, so a short read does not fail — it silently offers
    # things the database already holds. Events was 502 when this was fixed.
    existing = E.db('GET', '/rest/v1/events?select=id,name,starts_on,verified,'
                           'source_note,added_by', None, None, all_rows=True)
    by_name  = {}
    by_key   = {}
    for e in existing:
        by_name.setdefault(E.norm(e['name']), e)
        m = SLUG_RE.search(e.get('source_note') or '')
        if m: by_key[(m.group(1), m.group(2))] = e

    new, clash, drift = [], [], []
    for key, row in cands.items():
        prior = by_key.get(key)
        if prior:
            if prior.get('starts_on') and prior['starts_on'] != row['starts_on']:
                drift.append((prior, row))
            continue
        hit = by_name.get(E.norm(row['name']))
        if hit:
            clash.append((hit, key, row)); continue
        if f"{key[0]}/{key[1]}" in already: continue
        new.append((key, row))

    # ── report ──
    # One line per source, prefixed `source `, because run_log.py reads these
    # back and the page shows each feed's own state. A source that could not be
    # read says `failed` in words — run_log's classifier defaults to success, so
    # a failure it has never been taught reads as green.
    # Each source's own new/duplicate counts, so the page can show one feed
    # working and another quiet. Derived here rather than tracked through the
    # read loop, because `new` is only known after the database has been read.
    newby   = collections.Counter(site for (site, _), _ in new)
    dupeby  = collections.Counter(site for _, (site, _), _ in clash)
    print(f"\nevent feeds — {datetime.date.today().isoformat()}")
    for src in sources:
        if src['site'] in down:
            print(f"  source {src['site']} — failed: {down[src['site']]}")
        else:
            n, s = counts[src['site']]
            print(f"  source {src['site']} — {n} listings, {s} series, "
                  f"{newby[src['site']]} new, {dupeby[src['site']]} already held")
    raw_n = sum(n for n, _ in counts.values())
    print(f"  {raw_n} listings, {len(cands)} distinct series, "
          f"{len(existing)} events already in the database")

    print(f"\nNEW — {len(new)}")
    for (site, _), r in new:
        rec = f"  [{r['recurrence']}]" if r.get('recurrence') else ''
        kinds = ' · '.join(r['types']) or 'unsorted'
        print(f"  {r['starts_on']}  {kinds:<12} {r['name'][:40]:42} "
              f"{(r['location'] or '?')[:16]:18}{site[:20]}{rec}")

    if twice:
        print(f"\nCARRIED BY MORE THAN ONE SOURCE — {len(twice)}, kept once")
        for (site, slug), other, name in twice:
            print(f"  {name[:52]:54} {site} (also {other})")

    if drift:
        print(f"\nDATE MOVED since we imported it — {len(drift)}")
        for old, r in drift:
            lock = 'VERIFIED, left alone' if old['verified'] else 'unverified, updated'
            print(f"  {old['id']:>6}  {old['name'][:40]:42} {old['starts_on']} -> {r['starts_on']}  ({lock})")

    if clash:
        print(f"\nSAME NAME already in the database — {len(clash)}, skipped")
        for hit, (site, _), r in clash:
            print(f"  {hit['id']:>6}  {r['name'][:52]:54} {site}")

    if not write:
        print(f"\nnothing written. --write to insert the {len(new)} new one(s) as unverified.")
        return 1 if down else 0

    # ── write ──
    for _, r in new:
        got = E.db('POST', '/rest/v1/events', r, {'Prefer': 'return=representation'})
        print(f"added event {got[0]['id'] if got else '?'}: {r['name']}")
    for old, r in drift:
        if old['verified']: continue      # a human vouched for that date; ask them
        E.db('PATCH', f"/rest/v1/events?id=eq.{old['id']}",
           {'starts_on': r['starts_on'], 'source_note': r['source_note']})
        print(f"moved event {old['id']}: {old['starts_on']} -> {r['starts_on']}")

    # Only what was actually read is remembered. A source that was down this
    # morning has offered nothing, so nothing of its is marked as offered.
    for site, slug in cands: seen.add(f"{site}/{slug}")
    seen.save(SEEN_NOTE)
    print(f"\n{len(new)} added unverified. Review: python3 scripts/sync.py pending")
    return 1 if down else 0

if __name__ == '__main__':
    # A source that could not be read is a red run, even though the ones that
    # could were still written. The workflow reads this exit code.
    sys.exit(main(sys.argv[1:]))
