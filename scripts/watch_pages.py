#!/usr/bin/env python3
"""Pages worth watching that cannot be parsed — tell me when they change.

Some sources will never have a feed, and a few of those are worth knowing
about anyway. This is the cheap half of a scraper: it fetches a page, strips it
to text, fingerprints it, and says whether it has moved since last time. It
never writes a listing and never guesses a date.

    python3 scripts/watch_pages.py            # look and report
    python3 scripts/watch_pages.py --write    # and remember what it saw

WHY THIS EXISTS, AND WHY IT IS NOT A PARSER. Scott's ask, 4 Oct 2026, was
"I don't want to miss next time" about ParkConnect's Junior Ranger program.
There is no honest parser for it: the page is server-rendered and currently
says the program has concluded for the term, and the `/community-events/` grid
beside it is a Dynamics list that answers "you don't have permissions to view
these records" to an anonymous fetch. So the machine cannot read the dates —
but it CAN notice the day the page stops saying nothing is on, which is all
anyone needed. Watching is the honest thing a machine can do here; parsing is
not, and writing a parser against an empty endpoint is how a source comes to
read green while returning nothing.

`expect` is the sentence that means "still nothing". While it is there the
page is quiet whatever else moved on it — a cookie banner, a footer year, a
promo tile — so a watcher keyed on the hash alone would cry wolf every week and
be ignored within a month. When that sentence GOES, the run says so loudly.
A page with no `expect` reports on the hash alone.

The fingerprint is of the page's TEXT, not its HTML, for the same reason:
markup churns and prose does not.
"""
import sys, re, json, hashlib, argparse, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eventlib as E

STATE = pathlib.Path(__file__).parent / 'watch_pages.json'

# key      goes in the report and in the state file; renaming one forgets the page.
# expect   the "nothing on" sentence, lowercased. Optional.
PAGES = [
    {
        'key':    'parkconnect-junior-ranger',
        'name':   'Parks Victoria — Junior Rangers',
        'url':    'https://www.parkconnect.vic.gov.au/junior-ranger/',
        'expect': 'there are currently no activities available',
        'note':   ('School-holiday activities across the Victorian parks. The list is '
                   'server-rendered — the empty message is in the HTML — so if sessions '
                   'ever appear the same way, this becomes parseable. Parks Victoria is '
                   'an organiser across a hundred parks, so it could never be a places '
                   'row; a reader for it would have to take the park off each activity.'),
    },
    {
        'key':    'parkconnect-find-activities',
        'name':   'Parks Victoria — Find activities',
        'url':    'https://www.parkconnect.vic.gov.au/find-activities/',
        'expect': 'the junior ranger holiday program has concluded for this term',
        'note':   ('The page above it, which states the program status in a sentence. '
                   'Two pages rather than one because they can disagree, and the day '
                   'they do is the day something has been published.'),
    },
    {
        'key':    'ppf-fish-club',
        'name':   'Port Phillip Fish Club',
        'url':    'https://www.portphillipferries.com.au/portarlington-bellarine/port-phillip-fish-club/',
        'note':   ('Belt and braces. scrape_fareharbor.py reads the dates for this one '
                   'out of the operator\'s own booking calendar, which is the real '
                   'answer; this notices a change in the page itself — a new price, a '
                   'different operator, the charter being withdrawn — which the '
                   'calendar cannot say.'),
    },
]


def plain(html):
    """The page as prose. Scripts, styles, markup and whitespace all go."""
    s = re.sub(r'<script.*?</script>', ' ', html, flags=re.S | re.I)
    s = re.sub(r'<style.*?</style>',   ' ', s,    flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->',          ' ', s,    flags=re.S)
    s = re.sub(r'<[^>]+>',             ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='remember what was seen')
    args = ap.parse_args()

    was = {}
    if STATE.exists():
        try:
            was = json.loads(STATE.read_text()).get('pages') or {}
        except json.JSONDecodeError:
            pass

    today, now, failed, changed = E.today().isoformat(), {}, 0, 0
    for p in PAGES:
        prev = was.get(p['key'], {})
        if not E.robots_ok(p['url']):
            print(f"watch {p['key']} — failed: robots.txt refuses us")
            failed += 1
            now[p['key']] = prev
            continue
        page = E.fetch(p['url'], cap=4_000_000)
        if not page:
            print(f"watch {p['key']} — failed: the page did not answer")
            failed += 1
            now[p['key']] = prev          # silence from a server says nothing
            continue

        body = plain(page)
        digest = hashlib.sha1(body.encode()).hexdigest()[:12]
        quiet = p['expect'] in body.lower() if p.get('expect') else None

        # The loud case first: the "nothing on" sentence has gone.
        if quiet is False and prev.get('quiet') is True:
            print(f"watch {p['key']} — OPENED UP: \"{p['expect']}\" is gone from "
                  f"{p['name']}. Go and look: {p['url']}")
            changed += 1
        elif quiet:
            since = prev.get('since', today)
            print(f"watch {p['key']} — quiet since {since} ({p['name']})")
        elif prev.get('hash') and prev['hash'] != digest:
            print(f"watch {p['key']} — CHANGED ({p['name']}) {p['url']}")
            changed += 1
        elif not prev:
            print(f"watch {p['key']} — first read ({p['name']}), {len(body)} characters")
        else:
            print(f"watch {p['key']} — unchanged since {prev.get('since', '?')} ({p['name']})")

        moved = prev.get('hash') != digest or prev.get('quiet') != quiet
        now[p['key']] = {
            'hash':  digest,
            'chars': len(body),
            'quiet': quiet,
            'since': today if moved or not prev else prev.get('since', today),
            'read':  today,
        }

    print(f"watch — {len(PAGES)} page(s), {changed} changed, {failed} did not answer")

    if args.write:
        STATE.write_text(json.dumps({
            'note': ('What each watched page looked like last time. `quiet` is whether '
                     'its "nothing on" sentence was present; `since` is when it last '
                     'moved. Delete an entry to be told about that page afresh.'),
            'pages': now,
        }, indent=1) + '\n')

    sys.exit(1 if failed == len(PAGES) else 0)


if __name__ == '__main__':
    main()
