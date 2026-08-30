#!/usr/bin/env python3
"""Pull the Geelong Regional Libraries calendar.

    python3 scripts/scrape_library.py             # look, report, write nothing
    python3 scripts/scrape_library.py --write     # insert the new ones, unverified
    python3 scripts/scrape_library.py --branches  # just the branch/place audit

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

  * **The `days` filter does nothing.** days=1, 20 and 90 return the identical
    500 items covering about 20 days. The server caps at 500 and hands back a
    rolling window, so this is polled, not asked for a range. Twice a week
    against 20 days is enormous margin.
  * **It explodes recurring sessions**, hard: 72 Toddler Times, 52 Baby Times,
    51 Preschool Story Times in one window. They are separate real occurrences
    at different branches, so they are imported as separate events rather than
    collapsed — but it is why this source is much bigger than the others.

`eventlib.fetch` caps reads at 250KB and this feed is bigger, so the cap is
raised here explicitly. For HTML a truncated tail is survivable; for iCal it
produces a document that ends mid-event.

Nothing is ever inserted verified.
"""
import os, sys, json, re, base64, pathlib, datetime, argparse, collections
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

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--branches', action='store_true')
    a = ap.parse_args(argv)

    if MELB is None:
        sys.exit("no Australia/Melbourne timezone available — refusing to guess "
                 "an offset, because Melbourne is +10 in winter and +11 in summer.")

    raw = E.fetch(feed_url(), cap=CAP, timeout=45)
    if not raw:
        sys.exit(f"could not read {SOURCE} (robots.txt allows /feeds; only /results* is denied)")
    evs = parse(raw)
    print(f"\n{SOURCE} — {datetime.date.today().isoformat()}")
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

    # Two guards, and the database one is the load-bearing half. The ledger is a
    # local file that is only written at the end of a run, so a run that dies
    # partway leaves rows imported and unrecorded — which happened on the first
    # real import (307 of 500 in, ledger unwritten). Asking the database which
    # UIDs it already holds makes a re-run idempotent whatever the ledger says.
    seen = E.Seen(SEEN)
    have = set()
    for r in E.db('GET', '/rest/v1/events?select=source_note&added_by=eq.grlc&limit=5000'):
        m = re.search(r'UID (\d+)', r.get('source_note') or '')
        if m: have.add(m.group(1))
    fresh = [e for e in evs if e['uid'] not in seen and e['uid'] not in have]
    print(f"\n{len(fresh)} to import — {len(have)} already in the database, "
          f"{sum(1 for e in evs if e['uid'] in seen)} in the seen ledger")
    kinds = collections.Counter()
    for e in fresh:
        ts = types_for(e['title'])
        kinds[ts[0] if ts else '(unsorted)'] += 1
    print("  types proposed:", dict(kinds))
    print(f"  of which look like children's sessions: "
          f"{sum(1 for e in fresh if KIDS.search(e['title']))}")

    for e in fresh[:15]:
        ts = types_for(e['title'])
        print(f"   {e['start'].date()}  {time_text(e):<12} {e['title'][:38]:40} "
              f"{e['branch'][:24]:26} {','.join(ts) or '-'}")
    if len(fresh) > 15: print(f"   … and {len(fresh)-15} more")

    if not a.write:
        print(f"\nnothing written. --write to insert the {len(fresh)} new one(s) as unverified.")
        if missing:
            print(f"WARNING: {len(missing)} branch(es) have no place row, so their events "
                  f"would land with no pin and no curated suburb. Create those first.")
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
        for r, uid in batch: seen.add(uid)
        seen.save(SEEN_NOTE)
        added += len(batch)
        print(f"  wrote {added}/{len(fresh)}")
        batch = []

    for e in fresh:
        p, _ = linked[e['branch']]
        row = {
            'name': e['title'], 'types': types_for(e['title']),
            'starts_on': e['start'].date().isoformat(),
            'time_text': time_text(e), 'recurrence': 'none',
            'place_id': p['id'], 'location': p.get('suburb'),
            'description': e['desc'] or None,
            'info_url': f'https://{SOURCE}/event/{e["uid"]}',
            'date_confidence': 'high',       # the library's own calendar
            'added_by': 'grlc',
            'source_note': (f'{SOURCE} UID {e["uid"]}; imported '
                            f'{datetime.date.today().isoformat()} from the iCal feed. '
                            f'Room as published: {e["room"]}'),
        }
        batch.append((row, e['uid']))
        if len(batch) >= 50: flush()
    flush()
    print(f"\n{added} added unverified. Review: python3 scripts/sync.py pending")

if __name__ == '__main__':
    main(sys.argv[1:])
