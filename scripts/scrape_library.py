#!/usr/bin/env python3
"""Pull the Geelong Regional Libraries calendar.

    python3 scripts/scrape_library.py             # look, report, write nothing
    python3 scripts/scrape_library.py --write     # insert the new ones, unverified
    python3 scripts/scrape_library.py --branches  # just the branch/place audit
    python3 scripts/scrape_library.py --expire    # stand down series the feed has dropped
    python3 scripts/scrape_library.py --collapse  # fold rows imported one-per-occurrence

**Read the iCal feed, never the RSS one.** Both come off the same endpoint and
only the `feedType` in the base64 payload differs, but they are not equivalent:

  * iCal has LOCATION and GEO. The RSS has neither, so the branch is only ever
    in the prose ("Join us at the Leopold Library") and 481 of 500 items never
    say it at all. Every event would land unplaceable.
  * iCal has DTSTART/DTEND in real UTC. The RSS pubDate says `+0000` while
    carrying local wall time, so reading it as UTC shifts every event ten hours.
    That is the nextDate bug wearing a different hat, and nothing would catch it.
  * iCal has UID, which is the same number as the RSS guid, so the seen ledger
    keys the same either way.

Two things about the source that shape the code:

  * **No parameter reaches the server.** Probed 31 Aug 2026: days=1/20/90/365,
    a filters.startDate/endDate pair, an r=range/start/end triple copied off the
    site's own UI, and limit=2000 all return the identical 500 items covering
    21 days. Unknown keys are ignored silently. The date-range control on
    events.grlc.vic.gov.au is widget state that never reaches the feed, and the
    page itself carries no events in its HTML at all — it is a Communico
    front end that draws the list client-side. So this is polled, not asked for
    a range, and the only route past 500 is Communico's own authenticated API
    at api.communico.co, which needs credentials from the library.
  * **It explodes recurring sessions**, hard. That is what eats the cap: the
    500 items read on 31 Aug 2026 were only 252 real series, and 376 of the
    occurrences belonged to something that repeats. They are collapsed on the
    way in — see `series_of` — so one standing session is one row with a
    `recurrence`, and nextDate() keeps its date right.

`eventlib.fetch` caps reads at 250KB and this feed is bigger, so the cap is
raised here explicitly. For HTML a truncated tail is survivable; for iCal it
produces a document that ends mid-event.

Nothing is ever inserted verified.
"""
import os, sys, json, re, base64, pathlib, datetime, argparse, collections, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eventlib as E

try:
    from zoneinfo import ZoneInfo
    MELB = ZoneInfo('Australia/Melbourne')
except Exception:                      # no tzdata: refuse rather than guess
    MELB = None

SOURCE = 'events.grlc.vic.gov.au'
SEEN   = E.ROOT / 'scripts' / 'library_seen.json'
SEEN_NOTE = ('Event UIDs already offered by scrape_library.py. Delete a line to '
             'be offered it again.')
CAP = 8_000_000

def feed_url(days=90):
    """The payload is base64 JSON. `days` is relative, so this URL never goes
    stale — there is no absolute date in it to expire."""
    p = {"feedType": "ical",
         "filters": {"location": ["all"], "ages": ["all"], "types": ["all"],
                     "tags": [], "term": "", "days": days}}
    blob = base64.b64encode(json.dumps(p, separators=(',', ':')).encode()).decode()
    return f'https://{SOURCE}/feeds?data={blob}'

# ── the branch is the venue; the room after " - " is not ────────────────────
# "Newcomb Library - Children's Area" and "Newcomb Library" are one building.
# Every branch carries exactly one GEO across every event, checked.
def branch_of(location):
    return re.split(r'\s+-\s+|\s+-\s*$', location.strip())[0].strip(' -').strip()

# ── title -> types, conservative ────────────────────────────────────────────
# Only what the title actually says. Everything else lands with no type and
# shows as *unsorted*, which asks for a person instead of inventing data — the
# same choice scrape_events.py makes for the feed's 'Sport' category.
#
# The children's sessions are the biggest group in this feed by far, which is
# why `kids` was added to the vocabulary (27 Aug 2026) before the first import —
# retyping 183 rows afterwards is more work than typing them right on the way in.
TYPE_RULES = [
    # kids leads, because the first type is the word the row prints. These are
    # story times: `reading` is true but says nothing about who they are for.
    (r'story ?time|baby time|toddler time|rhyme|little kids|preschool', ['kids', 'reading']),
    (r'\bkids\b|children|lego|code club|junior|school holiday',        ['kids']),
    (r'book club|author|book chat|writers?|poetry|library lovers',      ['reading']),
    (r'makers?|3d print|craft|sewing|knit|workshop|induction',          ['workshop']),
    (r'exhibition|gallery|art[s]? ',                                    ['arts']),
    (r'history|heritage|genealog|local history',                        ['cultural']),
    (r'tech|computer|digital|device|online',                            ['workshop']),
    (r'garden|nature|bird',                                             ['nature']),
    (r'music|concert|sing',                                             ['music']),
]
KIDS = re.compile(r'story ?time|baby time|toddler time|rhyme|preschool|kids|children', re.I)

def types_for(title):
    t = title.lower()
    for pat, types in TYPE_RULES:
        if re.search(pat, t):
            return types
    return []

def unfold(text):
    """RFC5545 folds long lines with a leading space. Unfold before parsing or
    a LOCATION longer than 75 characters is silently cut in half."""
    return re.sub(r'\r?\n[ \t]', '', text or '')

def field(block, key):
    m = re.search(rf'^{key}[^:\r\n]*:(.*)$', block, re.M)
    return m.group(1).strip() if m else ''

def ical_dt(v):
    """20260827T140000Z -> an aware datetime. Z means UTC and here it is
    honest, unlike the RSS pubDate."""
    m = re.match(r'^(\d{8})T(\d{6})(Z?)$', v.strip())
    if not m: return None
    d = datetime.datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M%S')
    return d.replace(tzinfo=datetime.timezone.utc) if m.group(3) else d

def local(dt):
    if dt is None or MELB is None: return None
    return dt.astimezone(MELB) if dt.tzinfo else dt

def parse(text):
    out = []
    for b in re.findall(r'BEGIN:VEVENT(.*?)END:VEVENT', unfold(text), re.S):
        loc = field(b, 'LOCATION')
        start, end = local(ical_dt(field(b, 'DTSTART'))), local(ical_dt(field(b, 'DTEND')))
        if not start: continue
        geo = field(b, 'GEO').split(';')
        out.append({
            'uid':    field(b, 'UID'),
            'title':  re.sub(r'\s+', ' ', field(b, 'SUMMARY')).strip(),
            'desc':   E.text(field(b, 'DESCRIPTION').replace('\\,', ',').replace('\\n', ' '), 600),
            'branch': branch_of(loc), 'room': loc,
            'start':  start, 'end': end,
            'lat':    geo[0].strip() if len(geo) == 2 else None,
            'lng':    geo[1].strip() if len(geo) == 2 else None,
        })
    return out

def time_text(ev):
    """"9:30am–10am". An exhibition running 00:00 to 23:59 is an all-day thing
    and saying "12am–11:59pm" is technically true and useless."""
    def hhmm(d):
        return d.strftime('%-I:%M%p').lower().replace(':00', '')
    s, e = ev['start'], ev['end']
    if not e:
        return hhmm(s)
    if s.hour == 0 and s.minute == 0 and (e.hour, e.minute) >= (23, 55):
        return 'all day'
    if e.date() != s.date():
        return f"from {hhmm(s)}"
    return f"{hhmm(s)}–{hhmm(e)}"

# ── one thing that happens every week is ONE listing ────────────────────────
# The feed explodes a recurring session into one item per occurrence, and the
# server caps a response at 500 whatever you ask for, so the exploded repeats
# are what eats the window: measured 31 Aug 2026, 500 occurrences were only 252
# real series, and 376 of those occurrences belonged to something repeating.
# Collapsing them is what stops the cap being the constraint — and it is also
# just true, because "Toddler Time, Torquay, Tuesdays 10:30" is one thing.
#
# `recurrence` then does the work: nextDate() rolls weekly and fortnightly
# forward, so one row keeps saying the right date. It deliberately does NOT
# roll monthly or annual, which is why nothing here ever claims those.
#
# The 21-day window is exactly big enough to PROVE weekly and fortnightly and
# nothing more — three occurrences for one, two for the other. A monthly shows
# up once and is indistinguishable from a one-off, so it stays a dated one-off,
# which is the honest answer rather than a shortcoming.
def skey(e):
    """Stable for the life of the series, and derived rather than stored twice.
    Title + branch + weekday + clock time is what makes two occurrences the same
    standing session; the UID does not, because every occurrence has its own."""
    raw = f"{e['title'].lower()}|{e['branch'].lower()}|{e['start'].weekday()}|{e['start']:%H:%M}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]

WEEKDAY = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def series_of(evs):
    """Group occurrences into series and say which repeat.

    Conservative on purpose. Two occurrences seven days apart could be a
    coincidence — a school-holiday session that happens to fall on the same
    weekday twice — so weekly needs three. Anything that does not prove itself
    is imported as separate dated one-offs, exactly as before."""
    g = collections.defaultdict(list)
    for e in evs:
        g[skey(e)].append(e)
    out = []
    for k, members in g.items():
        members.sort(key=lambda e: e['start'])
        dates = sorted({e['start'].date() for e in members})
        gaps = {(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)}
        recur = ('weekly'      if len(dates) >= 3 and gaps == {7} else
                 'fortnightly' if len(dates) >= 2 and gaps == {14} else None)
        out.append({'key': k, 'recur': recur, 'evs': members,
                    'dates': dates, 'gaps': gaps})
    return out

def event_url(uid):
    return f'https://{SOURCE}/event/{uid}'

def note_series(s, first_seen, last_seen):
    e = s['evs'][0]
    return (f'{SOURCE} series {s["key"]}; {s["recur"]}, '
            f'{WEEKDAY[e["start"].weekday()]} {time_text(e)}. '
            f'{len(s["dates"])} occurrences in the window read {last_seen}. '
            f'First imported {first_seen}. Last seen {last_seen}. '
            f'UIDs {",".join(x["uid"] for x in s["evs"])}. '
            f'Room as published: {e["room"]}')

def note_single(e, day):
    return (f'{SOURCE} UID {e["uid"]}; imported {day} from the iCal feed. '
            f'Room as published: {e["room"]}')

# The database is the load-bearing idempotency check, not the local ledger — a
# run that dies partway leaves rows written and the ledger unsaved. Two keys are
# read because two generations of row exist: everything imported before the
# series collapse carries `UID <n>` and one row per occurrence, and a series row
# carries `series <hex>` plus every member UID it was built from. A feed series
# counts as already present if EITHER matches, so the collapse can ship without
# a migration and `--collapse` can tidy up afterwards at leisure.
def read_rows():
    rows = E.db('GET', '/rest/v1/events?select=id,name,starts_on,time_text,'
                'recurrence,verified,info_url,source_note&added_by=eq.grlc',
                all_rows=True)
    by_uid, by_key = {}, {}
    for r in rows:
        n = r.get('source_note') or ''
        m = re.search(r'\bseries ([0-9a-f]{12})\b', n)
        if m: by_key[m.group(1)] = r
        for u in re.findall(r'\bUID (\d+)', n):
            by_uid[u] = r
        m = re.search(r'\bUIDs ([\d,]+)', n)
        if m:
            for u in m.group(1).split(','):
                by_uid[u.strip()] = r
    return rows, by_uid, by_key

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--write',    action='store_true', help='insert the new ones, unverified')
    ap.add_argument('--branches', action='store_true', help='just the branch/place audit')
    ap.add_argument('--collapse', action='store_true',
                    help='fold already-imported occurrences into series rows')
    ap.add_argument('--expire',   action='store_true',
                    help='stand down series the feed has stopped carrying')
    ap.add_argument('--force',    action='store_true',
                    help='let --collapse delete verified rows')
    a = ap.parse_args(argv)

    # This was missing: the file only ever ran where SUPABASE_* was already
    # exported (the Action), so a plain terminal run died on "Set SUPABASE_URL".
    # scrape_events.py and scrape_venues.py both do this in their own main().
    E.load_env()

    if MELB is None:
        sys.exit("no Australia/Melbourne timezone available — refusing to guess "
                 "an offset, because Melbourne is +10 in winter and +11 in summer.")

    raw = E.fetch(feed_url(), cap=CAP, timeout=45)
    if not raw:
        sys.exit(f"could not read {SOURCE} (robots.txt allows /feeds; only /results* is denied)")
    evs = parse(raw)
    today = datetime.date.today().isoformat()
    print(f"\n{SOURCE} — {today}")
    days = sorted({e['start'].date() for e in evs})
    print(f"  {len(evs)} events, {days[0]} → {days[-1]} ({(days[-1]-days[0]).days} days ahead)")

    # ── the branches, and which have a place row ──
    places = {p['name'].lower(): p for p in
              E.db('GET', '/rest/v1/places?select=id,name,suburb,lat,lng,aliases')}
    def match(branch):
        b = branch.lower()
        if b in places: return places[b]
        for p in places.values():
            if b in [str(x).lower() for x in (p.get('aliases') or [])]: return p
            if p['name'].lower() in b or b in p['name'].lower(): return p
        return None

    by_branch = collections.Counter(e['branch'] for e in evs)
    linked, missing = {}, {}
    for br, n in by_branch.items():
        p = match(br)
        (linked if p else missing)[br] = (p, n)
    print(f"\nbranches — {len(linked)} already a place, {len(missing)} not on file")
    for br, (p, n) in sorted(linked.items()):
        print(f"   {n:>3}  {br[:44]:46} -> place {p['id']} {p['name'][:26]}")
    for br, (_, n) in sorted(missing.items()):
        g = next(e for e in evs if e['branch'] == br)
        print(f"   {n:>3}  {br[:44]:46} -- NO PLACE  {g['lat']},{g['lng']}")
    if a.branches:
        return

    # ── occurrences -> series ──
    ser = series_of(evs)
    repeat  = [s for s in ser if s['recur']]
    singles = [s for s in ser if not s['recur']]
    weak = [s for s in singles if len(s['dates']) == 2 and s['gaps'] == {7}]
    print(f"\n{len(evs)} occurrences -> {len(ser)} series")
    print(f"   {sum(1 for s in repeat if s['recur']=='weekly'):>4}  weekly "
          f"(3+ occurrences, every gap 7 days)")
    print(f"   {sum(1 for s in repeat if s['recur']=='fortnightly'):>4}  fortnightly")
    print(f"   {len(singles):>4}  not proved repeating — imported as dated one-offs "
          f"({sum(len(s['evs']) for s in singles)} rows)")
    if weak:
        print(f"         of those, {len(weak)} show a 7-day gap but only twice — "
              f"too few to call weekly, so they stay one-offs")

    rows, by_uid, by_key = read_rows()
    print(f"   {len(rows)} grlc rows already in the database "
          f"({sum(1 for r in rows if (r.get('recurrence') or 'none') != 'none')} recurring)")

    if a.collapse:
        return collapse(repeat, by_uid, by_key, today, a)

    seen = E.Seen(SEEN)
    def known(s):
        return s['key'] in by_key or any(e['uid'] in by_uid for e in s['evs'])
    def offered(s):
        return all(e['uid'] in seen for e in s['evs'])

    fresh_rep = [s for s in repeat  if not known(s) and not offered(s)]
    fresh_one = [e for s in singles for e in s['evs']
                 if e['uid'] not in by_uid and e['uid'] not in seen]

    # ── does anybody ELSE already have this night ──
    # read_rows() reads `added_by=eq.grlc` because it answers a different
    # question: is this feed's own series already a row. Nothing asked whether
    # another source had got there first, so "Holly Ringland - The World
    # Beneath Her Feet" was imported on 31 Aug 2026 against a row
    # scrape_venues.py had written off TryBooking the day before — same name,
    # same date, two place rows, and 143 is a ROOM INSIDE 128. scrape_venues.py
    # has checked name+date across every source since the day it was written;
    # this is that same check from the other side.
    #
    # Name AND date, never name alone. Dropping on a bare name match is what
    # swallowed every later night of a recurring gig in scrape_venues.py, and
    # reported the gap as duplicates rather than as anything missing.
    #
    # The branch case is safe and is why this cannot be name-only either way:
    # one story time runs at five libraries on one date, but all five are grlc,
    # so they never reach this map.
    elsewhere = {(E.norm(r['name']), r.get('starts_on')): r
                 for r in E.db('GET', '/rest/v1/events?select=id,name,starts_on,'
                                      'added_by,place_id', all_rows=True)
                 if (r.get('added_by') or '') != 'grlc'}
    held = []
    def elsewhere_has(title, date):
        hit = elsewhere.get((E.norm(title), date))
        if hit: held.append((hit, title, date))
        return hit
    fresh_rep = [s for s in fresh_rep
                 if not elsewhere_has(s['evs'][0]['title'],
                                      s['evs'][0]['start'].date().isoformat())]
    fresh_one = [e for e in fresh_one
                 if not elsewhere_has(e['title'], e['start'].date().isoformat())]
    if held:
        # Reported every run, never remembered — the same standing report
        # scrape_events.py prints for a name clash. A row that keeps appearing
        # here is telling you two sources are both carrying one thing, which is
        # worth knowing more than once.
        print(f"\nALREADY HERE FROM ANOTHER SOURCE — {len(held)}, skipped")
        for hit, title, date in held:
            print(f"  {hit['id']:>6}  {title[:44]:46} {date}  "
                  f"{hit.get('added_by') or 'by hand'}")

    total = len(fresh_rep) + len(fresh_one)
    print(f"\n{total} to import — {len(fresh_rep)} recurring series, "
          f"{len(fresh_one)} one-off occurrences")

    kinds = collections.Counter()
    for t in [s['evs'][0]['title'] for s in fresh_rep] + [e['title'] for e in fresh_one]:
        ts = types_for(t)
        kinds[ts[0] if ts else '(unsorted)'] += 1
    if kinds: print("  types proposed:", dict(kinds))

    for s in fresh_rep[:10]:
        e = s['evs'][0]
        print(f"   {s['recur']:<12} {WEEKDAY[e['start'].weekday()]} {time_text(e):<12} "
              f"{e['title'][:36]:38} {e['branch'][:24]:26} x{len(s['dates'])}")
    for e in fresh_one[:10]:
        print(f"   {'one-off':<12} {e['start'].date()} {time_text(e):<12} "
              f"{e['title'][:36]:38} {e['branch'][:24]:26}")
    if total > 20: print(f"   … and {total-20} more")

    # ── series the feed has stopped carrying ──
    # A weekly row rolls forward for ever, so a session that quietly ends — a
    # school term finishing — would keep being promised. The window is the
    # check: a series still running is always in the next 21 days, so one that
    # is absent has stopped. Standing it down sets `recurrence` to none and
    # leaves the date alone, so the row ages out of the board by itself. That is
    # reversible and deletes nothing, which a guess about a school holiday
    # should be.
    live = {s['key'] for s in ser}
    gone = [r for k, r in by_key.items()
            if k not in live and (r.get('recurrence') or 'none') != 'none']
    if gone:
        print(f"\n{len(gone)} recurring row(s) the feed no longer carries:")
        for r in gone[:12]:
            print(f"   {r['id']:>4}  {r['name'][:44]:46} {r.get('recurrence')} "
                  f"from {r.get('starts_on')}")
        print("   --expire stands these down (recurrence -> none; nothing deleted)")

    if not a.write and not a.expire:
        print(f"\nnothing written. --write to insert the {total} new one(s) as unverified.")
        if missing:
            print(f"WARNING: {len(missing)} branch(es) have no place row, so their events "
                  f"would land with no pin and no curated suburb. Create those first.")
        return

    if a.expire:
        if len(evs) < 100:
            sys.exit(f"refusing to expire on a thin read ({len(evs)} events) — a short "
                     f"feed would stand down series that are running perfectly well.")
        for r in gone:
            E.db('PATCH', f"/rest/v1/events?id=eq.{r['id']}",
                 {'recurrence': 'none',
                  'source_note': (r.get('source_note') or '') +
                                 f' Stood down {today}: absent from the feed window.'},
                 {'Prefer': 'return=minimal'})
        print(f"\n{len(gone)} stood down.")
        if not a.write:
            return

    if missing:
        sys.exit(f"refusing to write: {len(missing)} branch(es) have no place row "
                 f"({', '.join(sorted(missing))}). Their events would be unplaceable. "
                 f"Create the places first — the GEO above is the coordinate.")

    added, batch = 0, []
    def flush():
        """Insert in batches and checkpoint the ledger after each one. 500
        single POSTs is slow enough to hit a socket timeout, and any row written
        after the last checkpoint would otherwise be invisible to the next run."""
        nonlocal added, batch
        if not batch: return
        E.db('POST', '/rest/v1/events', [r for r, _ in batch], {'Prefer': 'return=minimal'})
        for _, uids in batch:
            for u in uids: seen.add(u)
        seen.save(SEEN_NOTE)
        added += len(batch)
        print(f"  wrote {added}/{total}")
        batch = []

    def base(e):
        p, _ = linked[e['branch']]
        return {
            'name': e['title'], 'types': types_for(e['title']),
            'starts_on': e['start'].date().isoformat(),
            'time_text': time_text(e),
            'place_id': p['id'], 'location': p.get('suburb'),
            'description': e['desc'] or None,
            'info_url': event_url(e['uid']),
            'date_confidence': 'high',       # the library's own calendar
            'added_by': 'grlc',
        }

    for s in fresh_rep:
        e = s['evs'][0]
        row = {**base(e), 'recurrence': s['recur'],
               'source_note': note_series(s, today, today)}
        batch.append((row, [x['uid'] for x in s['evs']]))
        if len(batch) >= 50: flush()
    for e in fresh_one:
        row = {**base(e), 'recurrence': 'none', 'source_note': note_single(e, today)}
        batch.append((row, [e['uid']]))
        if len(batch) >= 50: flush()
    flush()

    # ── keep the standing rows pointing somewhere real ──
    # A series row's info_url is one occurrence's page, and that occurrence
    # passes. Every run repoints it at the next one and restamps Last seen.
    # ONLY those two fields, and only on rows this importer owns: the name, the
    # date, the time, the types and the place are where a person's judgement
    # lives, and a scraper overwriting those is the thing this project refuses
    # to do to a verified row.
    touched = 0
    for s in repeat:
        r = by_key.get(s['key'])
        if not r: continue
        url = event_url(s['evs'][0]['uid'])
        note = re.sub(r'Last seen \d{4}-\d\d-\d\d', f'Last seen {today}',
                      r.get('source_note') or '')
        if r.get('info_url') == url and note == (r.get('source_note') or ''):
            continue
        E.db('PATCH', f"/rest/v1/events?id=eq.{r['id']}",
             {'info_url': url, 'source_note': note}, {'Prefer': 'return=minimal'})
        touched += 1
    if touched:
        print(f"{touched} standing row(s) repointed at their next occurrence")

    print(f"\n{added} added unverified. Review: python3 scripts/sync.py pending")

# ── folding the rows that were imported one-per-occurrence ──────────────────
# Everything imported before the collapse is one row per occurrence, so the
# board carries 72 Toddler Times where it should carry one. This folds them,
# and it uses the FEED to decide rather than re-deriving a series from the rows
# themselves: the feed knows which UIDs belong together, so nothing has to be
# guessed back out of a name and a time string.
#
# Dry run by default, and it refuses to delete a verified row without --force —
# every grlc row is verified today, because the queue was accepted in bulk, so
# this WILL need --force and that is the point at which somebody reads it.
def collapse(repeat, by_uid, by_key, today, a):
    plans = []
    for s in repeat:
        if s['key'] in by_key: continue           # already folded
        found = {}
        for e in s['evs']:
            r = by_uid.get(e['uid'])
            if r: found[r['id']] = r
        if len(found) < 2: continue
        keep = min(found.values(), key=lambda r: (r.get('starts_on') or '9999'))
        drop = [r for r in found.values() if r['id'] != keep['id']]
        plans.append((s, keep, drop))

    if not plans:
        print("\nnothing to collapse — no series has more than one row on file.")
        return
    kills = sum(len(d) for _, _, d in plans)
    ver   = sum(1 for _, _, d in plans for r in d if r.get('verified'))
    print(f"\n{len(plans)} series to fold, {kills} row(s) to delete "
          f"({ver} of them verified)")
    for s, keep, drop in plans[:15]:
        e = s['evs'][0]
        print(f"   keep {keep['id']:>4} {e['title'][:34]:36} {e['branch'][:22]:24} "
              f"{s['recur']:<12} delete {len(drop)}")
    if len(plans) > 15: print(f"   … and {len(plans)-15} more")

    if not a.write:
        print("\nnothing written. --collapse --write to apply"
              + (" (and --force, because verified rows would be deleted)" if ver else ""))
        return
    if ver and not a.force:
        sys.exit(f"refusing: {ver} of the rows to delete are verified. Read the list "
                 f"above, then re-run with --force if it is right.")

    for s, keep, drop in plans:
        E.db('PATCH', f"/rest/v1/events?id=eq.{keep['id']}",
             {'recurrence': s['recur'],
              'info_url': event_url(s['evs'][0]['uid']),
              'source_note': note_series(s, keep.get('starts_on') or today, today)
                             + f' Folded {today} from {len(drop)+1} imported occurrences.'},
             {'Prefer': 'return=minimal'})
        ids = ','.join(str(r['id']) for r in drop)
        E.db('DELETE', f"/rest/v1/events?id=in.({ids})", None, {'Prefer': 'return=minimal'})
    print(f"\n{len(plans)} folded, {kills} deleted.")

if __name__ == '__main__':
    main(sys.argv[1:])
