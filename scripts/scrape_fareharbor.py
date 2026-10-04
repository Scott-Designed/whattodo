#!/usr/bin/env python3
"""FareHarbor — an operator's own booking calendar, read through its public API.

Found 4 Oct 2026 chasing the Port Phillip Fish Club, which Scott captured with
the note "see if can be scraped". The Fish Club's page on the operator's own
site carries no dates at all — only "Mondays, Wednesdays and Fridays during the
holidays" and a booking widget — so the page is not the source. The widget is
FareHarbor, and FareHarbor publishes:

    /api/v1/companies/<shortname>/items/                      the catalogue
    /api/v1/companies/<shortname>/items/<pk>/calendar/<y>/<m>/  a month of dates

Both answer 200 JSON to a plain request with no key, no token and no cookie,
and fareharbor.com's robots.txt allows our crawler (checked 4 Oct 2026), so a
Claude session may run this as well as the Action.

    python3 scripts/scrape_fareharbor.py            # look and report, writes nothing
    python3 scripts/scrape_fareharbor.py --write    # insert the new ones, held
    python3 scripts/scrape_fareharbor.py --only ppf # one operator

THE REGISTRY IS `SOURCES` IN THIS FILE, NOT `places.events_url`, and that is
deliberate. FareHarbor is a PLATFORM — the same shape as Oztix or Humanitix —
and a FareHarbor company is an OPERATOR whose experiences happen in several
places. `scrape_venues.py` sets place_id to the row it read from, so
registering Port Phillip Ferries there would file a Portarlington mussel lunch
at "Port Phillip Ferries". That is the organiser-is-not-the-venue trap this
project has already paid for with Creative Geelong and Coast & Bay.

AN ITEM IS ONLY IMPORTED IF IT IS IN THE OPERATOR'S `items` MAP, AND EVERY
UNKNOWN ITEM WITH DATES IS PRINTED EVERY RUN. That is the whole design, and it
is what makes this safe AND what answers the thing Scott actually asked for.
Measured 4 Oct 2026 over three months, Port Phillip Ferries publishes 1,297
availabilities and 1,100 of them are the scheduled ferry crossings, gift cards
and memberships — a timetable, not a what's-on. An allow-list keeps those off
the board; printing the leftovers means a new experience, or the Fish Club's
next school-holiday season, turns up in the report rather than being silently
dropped. Nothing has to be remembered.

Three things the implementation gets right that a naive one would not:

- `start_at` is LOCAL WALL TIME and `utc_start_at` is the same instant with an
  offset. This reads the local one, the same call made for Eventbrite's
  `start.local`. Reading the UTC field would shift every row ten or eleven
  hours — the nextDate bug in a third hat.
- SEVERAL SESSIONS ON ONE DAY ARE ONE ROW, printed "10:40am & 1:30pm", the
  shape parsers/geelongartscentre.py already uses. Six seatings is not six
  things to do.
- `calendar/<y>/<m>/` 404s past the operator's publishing horizon, so the walk
  stops at the first 404 rather than treating it as a failure. Measured: Port
  Phillip Ferries answers three months ahead and 404s on the fourth.

THE `description` FIELD ON THIS API IS NOT TRUSTWORTHY AND IS NEVER WRITTEN.
Measured 4 Oct 2026: "Port to Plate Mussel Experience", "Taste the Bellarine
Experience" and "Port Phillip Fish Club" all carry the IDENTICAL description,
and it is about a lunch package at the Portarlington Grand Hotel — none of them
is that. The operator reuses item records, exactly as Canvas and Cork reuse
Shopify product handles. The name, the dates and the times are what this reads;
prose is a person's job.

`date_confidence` is `high`: this is the operator's own booking system and the
times are structured datetimes, not prose. THERE IS NO WEEKDAY CHECKSUM here
and none is possible — the checksum exists to catch a page whose printed
weekday refutes its own date, and an API prints no weekday to refute. Nothing
is auto-verified; everything lands held, like every other write path.
"""
import sys, json, argparse, datetime, pathlib, urllib.request, urllib.error, time, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eventlib as E

HOST   = 'fareharbor.com'
SEEN   = pathlib.Path(__file__).parent / 'fareharbor_seen.json'
MONTHS = 4          # how many months ahead to try before giving up
NOTE   = ('Every FareHarbor availability ever offered, keyed <shortname>/<item pk>/<date>. '
          'Delete a line to be offered that date again.')
PAUSE  = 0.4        # between requests; the API is somebody else's

# One entry per FareHarbor company we read.
#
#   key        goes in `added_by` and is what --only matches. It outlives this
#              file, so renaming one means migrating the database and the ledger.
#   shortname  FareHarbor's own company slug, out of the booking widget's URL.
#   items      THE ALLOW-LIST. pk -> what to write for it. Every pk here is a
#              hand decision with its reason; anything not here is reported.
#
# Each item carries its own `place_id`, because an operator's experiences do
# not all happen in one room. Port Phillip Ferries' local ones all come ashore
# at the Portarlington pier, which is places row 183 — the pier deck, not a
# centroid. The crossings themselves are deliberately absent: a timetable is
# not a listing, and nobody opens a what's-on board to find the 4pm ferry.
SOURCES = [
    {
        'key':       'ppf',
        'shortname': 'portphillipferries',
        'name':      'Port Phillip Ferries',
        'site':      'portphillipferries.com.au',
        'items': {
            756421: dict(name='Port Phillip Fish Club', place_id=183,
                         types=['water', 'kids'], ages=['kids'],
                         url='https://www.portphillipferries.com.au/portarlington-bellarine/port-phillip-fish-club/',
                         why='the school-holiday fishing charter Scott captured; '
                             'runs out of Portarlington Pier with Freetime Adventure Charters'),
            608094: dict(name='Port to Plate Mussel Experience', place_id=183,
                         types=['produce', 'water'],
                         url='https://www.portphillipferries.com.au/portarlington-bellarine/port-to-plate-mussel-experience/',
                         why='a mussel-farm tour off Portarlington — the thing the town is known for'),
            725256: dict(name='Taste the Bellarine Experience', place_id=183,
                         types=['produce', 'water'],
                         url='https://www.portphillipferries.com.au/portarlington-bellarine/taste-the-bellarine/',
                         why='a Bellarine food and wine day, ashore at Portarlington'),
            761973: dict(name='Whisky by the Bay', place_id=183,
                         types=['produce', 'water'], ages=['adults'],
                         url='https://www.portphillipferries.com.au/packages/whisky-by-the-bay/',
                         why='one-off tasting days on the Bellarine'),
            757104: dict(name='Fashions on the Ferry', place_id=183,
                         types=['party', 'water'], ages=['adults'],
                         url='https://www.portphillipferries.com.au/packages/fashions-on-the-ferry/',
                         why='a one-off spring racing day on the water'),
            739821: dict(name='Junior Captain Adventure Cruise', place_id=183,
                         types=['water', 'kids'], ages=['kids'],
                         url='https://www.portphillipferries.com.au/portarlington-bellarine/junior-captain-adventure-cruise/',
                         why='the other school-holiday one; nothing published today, '
                             'which is exactly why it is listed here rather than remembered'),
        },
    },
]


def get(path):
    """One JSON read. A 404 is an answer, not a crash — the month walk needs it."""
    url = f'https://{HOST}{path}'
    req = urllib.request.Request(url, headers={'User-Agent': E.UA, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    finally:
        time.sleep(PAUSE)
    return json.loads(body)


def months_ahead(n):
    d = E.today().replace(day=1)
    for _ in range(n):
        yield d.year, d.month
        d = (d.replace(day=28) + datetime.timedelta(days=7)).replace(day=1)


def read_company(src):
    """Every availability this operator publishes, as {item pk: {date: [HH:MM]}}.

    Walks month by month and stops at the first 404 — that is the horizon, not
    an outage. An operator with nothing at all still returns an empty calendar
    for the current month, so a 404 on the FIRST month is a real failure and
    is raised.
    """
    cat = get(f"/api/v1/companies/{src['shortname']}/items/")
    if not cat:
        raise RuntimeError(f"{src['shortname']}: the item catalogue 404'd")
    names = {i['pk']: i['name'] for i in cat['items']}

    found = collections.defaultdict(lambda: collections.defaultdict(list))
    pks = sorted(names)
    for n, (y, m) in enumerate(months_ahead(MONTHS)):
        got = False
        # The API takes a comma-joined list of pks, so a month is a handful of
        # requests rather than one per item.
        for k in range(0, len(pks), 10):
            chunk = ','.join(str(p) for p in pks[k:k + 10])
            cal = get(f"/api/v1/companies/{src['shortname']}/items/{chunk}/calendar/{y}/{m}/")
            if cal is None:
                continue
            got = True
            for week in cal['calendar']['weeks']:
                for day in week['days']:
                    if day['month'] == 'other':
                        continue
                    for a in day['availabilities']:
                        pk = int(a['uri'].split('/items/')[1].split('/')[0])
                        # start_at is LOCAL wall time. Never utc_start_at.
                        found[pk][day['at']].append(a['start_at'][11:16])
        if not got:
            if n == 0:
                raise RuntimeError(f"{src['shortname']}: the current month 404'd")
            break
    return names, found


# A tour that runs most days is a STANDING OFFER, not a happening, and this
# refuses to import one. Measured 4 Oct 2026: Port Phillip Ferries' "Taste the
# Bellarine" and "Port to Plate Mussel Experience" each publish about seventy
# dates in ninety days, which is 75 rows apiece saying the same sentence — the
# library story-time flood in a different costume. Those belong in `activities`
# as a thing you can do at Portarlington, written once by a person, and the run
# says so rather than dropping them in silence.
#
# The two numbers are deliberately loose. DENSE_MIN stops a three-night run
# being called standing; DENSE_FRAC is well above a weekly series (14%) and a
# every-weekend one (29%), and well below a daily tour (79%).
DENSE_MIN  = 10
DENSE_FRAC = 0.40


def standing(dates):
    """Does this item run so often that it is an offer rather than an occasion?"""
    if len(dates) < DENSE_MIN:
        return False
    first = datetime.date.fromisoformat(min(dates))
    last  = datetime.date.fromisoformat(max(dates))
    span  = (last - first).days + 1
    return span > 0 and len(dates) / span > DENSE_FRAC


def runs(by_date):
    """Consecutive days with identical times collapse into one row.

    The call scrape_vgb.py already makes: every gap exactly one day is a season
    or a run, not a series of separate things. Anything else stays its own row.
    Yields (start, end_or_None, times).
    """
    out = []
    for d in sorted(by_date):
        day, times = datetime.date.fromisoformat(d), sorted(set(by_date[d]))
        if out and out[-1][2] == times and (day - out[-1][1]).days == 1:
            out[-1][1] = day
        else:
            out.append([day, day, times])
    for a, b, times in out:
        yield a.isoformat(), (b.isoformat() if b != a else None), times


def when(times):
    """'10:40am', or '10:40am & 1:30pm' where a day has more than one seating."""
    seen, out = set(), []
    for t in sorted(times):
        if t in seen:
            continue
        seen.add(t)
        out.append(E.clock(t))
    return ' & '.join(out) if out else None


def build(src, pk, spec, date, ends, times, cat_name):
    """One held row. Nothing here is inferred — every field is published."""
    note = (f"Read from {src['name']}'s own FareHarbor booking calendar "
            f"({HOST}/api/v1/companies/{src['shortname']}/items/{pk}/calendar/), "
            f"{E.today().isoformat()}. Dates and times are the operator's own structured "
            f"start_at values, read as local wall time; there is no printed weekday to "
            f"check them against and none is needed. The catalogue calls this item "
            f"\"{cat_name}\". Linked to places row {spec['place_id']}. No km.")
    return {
        'name':            spec['name'],
        'types':           list(spec['types']),
        'starts_on':       date,
        'ends_on':         ends,
        'time_text':       when(times),
        'ages':            list(spec.get('ages', ['all-ages'])),
        'place_id':        spec['place_id'],
        'info_url':        spec['url'],
        'date_confidence': 'high',
        'added_by':        src['key'],
        'verified':        False,
        'published':       False,
        'source_note':     note,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='insert the new rows, held for review')
    ap.add_argument('--only', help='one operator key')
    args = ap.parse_args()
    E.load_env()

    if not E.robots_ok(f'https://{HOST}/api/v1/companies/'):
        print(f'source {HOST} — failed: robots.txt refuses us')
        sys.exit(1)

    seen = E.Seen(SEEN)
    # Name + date across EVERY source, not just this one. The library importer
    # learned this the hard way: a check that only sees its own rows writes
    # straight past something another feed got to first.
    held = {(E.norm(r['name']), r['starts_on'])
            for r in E.db('GET', '/rest/v1/events?select=name,starts_on', all_rows=True)
            if r.get('starts_on')}

    rows, failed = [], False
    for src in SOURCES:
        if args.only and args.only != src['key']:
            continue
        try:
            names, found = read_company(src)
        except Exception as e:
            print(f"source {src['site']} — failed: {e}")
            failed = True
            continue

        listed = unlisted = new = dupe = 0
        standing_items = []
        for pk, spec in src['items'].items():
            ahead = {d: v for d, v in found.get(pk, {}).items()
                     if d >= E.today().isoformat()}
            if not ahead:
                continue
            if standing(ahead):
                standing_items.append((pk, spec['name'], len(ahead),
                                       min(ahead), max(ahead)))
                continue
            for date, ends, times in runs(ahead):
                listed += 1
                key = f"{src['shortname']}/{pk}/{date}"
                if key in seen:
                    continue
                if (E.norm(spec['name']), date) in held:
                    dupe += 1
                    seen.add(key)
                    continue
                rows.append(build(src, pk, spec, date, ends, times,
                                  names.get(pk, spec['name'])))
                seen.add(key)
                new += 1

        # The leftovers. This is the half that means nothing has to be
        # remembered: an experience the operator adds, or a season they reopen,
        # appears here on the next run with its pk and its next date.
        spare = []
        for pk, by_date in sorted(found.items()):
            if pk in src['items']:
                continue
            ahead = [d for d in by_date if d >= E.today().isoformat()]
            if not ahead:
                continue
            unlisted += 1
            spare.append((pk, names.get(pk, '?'), min(ahead), len(ahead)))

        print(f"source {src['site']} — {len(src['items'])} items listed, "
              f"{listed} dated, {new} new, {dupe} already held, "
              f"{unlisted} items not listed")
        for pk, name, first, n in spare:
            print(f"   NOT LISTED — {pk} {name[:46]:<48} {n:>3} dates, next {first}")
        for pk, name, n, a, b in standing_items:
            print(f"   RUNS MOST DAYS — {pk} {name[:42]:<44} {n:>3} dates {a} to {b}; "
                  f"a standing offer, not an occasion — it belongs in activities")
        for pk, spec in src['items'].items():
            if not [d for d in found.get(pk, {}) if d >= E.today().isoformat()]:
                print(f"   nothing published yet — {pk} {spec['name']}")

    for r in rows:
        print(f"   + {r['starts_on']}  {r['time_text'] or '':<18} {r['name']}")
    print(f"{len(rows)} new row(s)")

    if args.write and rows:
        for k in range(0, len(rows), 50):
            E.db('POST', '/rest/v1/events', rows[k:k + 50])
        seen.save(NOTE)
        print(f'wrote {len(rows)} row(s), all held for review')
    elif args.write:
        seen.save(NOTE)

    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
