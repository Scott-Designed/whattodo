#!/usr/bin/env python3
"""Write what a scheduled run actually did into scripts/run_log.json.

Why this exists. The workflow already prints everything the scrapers say into
the GitHub job summary — and a job summary is a page on github.com that nobody
visits. CLAUDE.md names that as the most likely way this database goes wrong
next: every event is verified now, so the feed updates nothing and a date that
moves at the source becomes one line in a summary no one reads.

So the run writes its own record into the repo, the workflow commits it, and
the back-of-house page reads it straight off raw.githubusercontent.com. No
token, no deploy — raw sends Access-Control-Allow-Origin: * and the commit is
[skip ci], so the log is current without rebuilding the site.

**The raw text is the record; the parsed numbers are a convenience.** If a
scraper changes its wording the counts go null and the page still prints every
line the run produced. Never make the page depend on a regex here.

    python3 scripts/run_log.py            # reads run.txt / venues.txt in cwd

Metadata comes from the GitHub Actions environment when there is one, so a
local run is recorded as a local run rather than pretending to be scheduled.
"""
import json, os, pathlib, re, datetime

HERE = pathlib.Path(__file__).resolve().parent
LOG  = HERE / 'run_log.json'
KEEP = 30           # about four months of Mon/Thu runs

DATE = r'\d{4}-\d{2}-\d{2}'


def _int(pattern, text):
    """The count off a header line, or None if the wording has moved on.

    re.M is not optional: every pattern here anchors with ^ to a line in the
    middle of the output, and without it ^ only ever matches the start of the
    whole string, so each count comes back null while looking fine.
    """
    m = re.search(pattern, text, re.M)
    return int(m.group(1)) if m else None


def read_events(text):
    """What scrape_events.py said. Drift is the part a person has to act on."""
    drift = []
    for m in re.finditer(rf'^\s+(\d+)\s+(.+?)\s+({DATE}) -> ({DATE})\s+\((.+?)\)\s*$',
                         text, re.M):
        idn, name, was, now, lock = m.groups()
        drift.append({'id': int(idn), 'name': name.strip(), 'from': was, 'to': now,
                      # 'VERIFIED, left alone' means the bot would not touch it and
                      # is handing the decision to you. That is the whole signal.
                      'locked': lock.startswith('VERIFIED')})
    listings = _int(r'^\s+(\d+) listings,', text)
    series   = _int(r'(\d+) distinct series', text)
    return {
        'listings':  listings,
        'series':    series,
        'new':       _int(r'^NEW — (\d+)', text),
        'clashes':   _int(r'^SAME NAME already in the database — (\d+)', text),
        'added':     len(re.findall(r'^added event \d+:', text, re.M)),
        'moved':     len(re.findall(r'^moved event \d+:', text, re.M)),
        'drift':     drift,
        # One source, shaped like the venue ones so the page can list them all
        # together. It is the only real feed anywhere in this project.
        'sources':   [{
            'name':  'surfcoastevents.com.au',
            'how':   f'WordPress JSON API ({listings} listings → {series} series)'
                     if listings else 'WordPress JSON API',
            'hint':  None,
            'state': 'read' if listings else 'nothing',
            'via':   ['The Events Calendar'],
            'own':   False,
        }],
    }


def source_state(how):
    """Sort one venue's result line into a word the page can colour.

    The scraper prints a sentence per venue — "Oztix (10 gigs from 10 of 10
    links)", "site did not respond", "nothing machine-readable [homepage; no
    gig page found]". These are the states that sentence can be in, and they
    are what tells you whether a source is working, broken, or simply has
    nothing to read. Order matters: 'skipped' has to be tested before the
    platform names, or a skipped Humanitix line reads as a successful one.
    """
    low = how.lower()
    if 'skipped' in low:                   return 'skipped'
    if 'did not respond' in low:           return 'dead'
    if 'robots.txt' in low:                return 'refused'
    if 'left for a human' in low:          return 'manual'
    if 'nothing machine-readable' in low:  return 'nothing'
    return 'read'


PLATFORMS = ['Oztix', 'Humanitix', 'TryBooking', 'Eventbrite', 'Moshtix']


def read_venues(text):
    """What scrape_venues.py said, including a line per source it looked at."""
    m = re.search(r'^(\d+) new, (\d+) already in the database', text, re.M)

    sources = []
    for line in text.splitlines():
        # "  Torquay Hotel — own listing (15 gigs over 2 pages); Oztix (14 …)"
        hit = re.match(r'^  (\S.*?) — (.+?)\s*$', line)
        if not hit or line.startswith('  ('):
            continue
        name, how = hit.group(1), hit.group(2)
        # A trailing [..] is the scraper telling you how to pin this source down.
        note = re.search(r'\[(.+)\]\s*$', how)
        sources.append({
            'name':  name,
            'how':   re.sub(r'\s*\[.+\]\s*$', '', how),
            'hint':  note.group(1) if note else None,
            'state': source_state(how),
            'via':   [p for p in PLATFORMS if p.lower() in how.lower()],
            'own':   'own listing' in how,
        })

    return {
        'venues':   _int(r'^\s+(\d+) venues,', text),
        'readable': _int(r'(\d+) with somewhere to look', text),
        'new':      int(m.group(1)) if m else None,
        'dupes':    int(m.group(2)) if m else None,
        'rooms':    _int(r'rooms not previously on file — (\d+)', text),
        'added':    len(re.findall(r'^added event \d+:', text, re.M)),
        'sources':  sources,
        'drift':    [],
    }


def step(name, script, out, rc, parse):
    """One scraper's leg of the run. Missing output is itself worth recording —
    it means the step never got to run, which the page should say out loud."""
    text = pathlib.Path(out).read_text() if pathlib.Path(out).exists() else ''
    code = pathlib.Path(rc).read_text().strip() if pathlib.Path(rc).exists() else ''
    d = {'name': name, 'script': script,
         'exit': int(code) if code.isdigit() else None,
         'text': text.strip()}
    d['ok'] = d['exit'] == 0
    d['ran'] = bool(text) or code != ''
    d.update(parse(text) if text else {'drift': []})
    return d


def main():
    env = os.environ.get
    repo = env('GITHUB_REPOSITORY', 'Scott-Designed/whattodo')
    run_id = env('GITHUB_RUN_ID')

    steps = [
        step('Surf Coast events calendar', 'scrape_events.py',
             'run.txt', 'run.rc', read_events),
        step('Venue ticketing pages', 'scrape_venues.py',
             'venues.txt', 'venues.rc', read_venues),
    ]

    record = {
        'recorded_at': datetime.datetime.now(datetime.timezone.utc)
                        .isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'run_id':     run_id,
        'run_number': env('GITHUB_RUN_NUMBER'),
        # 'schedule' is the one that matters; workflow_dispatch means you pressed it.
        'trigger':    env('GITHUB_EVENT_NAME', 'local'),
        'url':        f'https://github.com/{repo}/actions/runs/{run_id}' if run_id else None,
        'steps':      steps,
        'ok':         all(s['ok'] for s in steps),
        # The headline number: dates that moved at the source on rows a person
        # vouched for. Nothing updates these automatically and nothing will.
        'needs_you':  sum(1 for s in steps for d in s['drift'] if d['locked']),
    }

    try:
        history = json.loads(LOG.read_text())
        if not isinstance(history, list): history = []
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.insert(0, record)
    LOG.write_text(json.dumps(history[:KEEP], indent=1) + '\n')

    say = 'ok' if record['ok'] else 'FAILED'
    print(f"run_log.json: recorded run {record['run_number'] or '(local)'} — {say}, "
          f"{record['needs_you']} thing(s) waiting on you")


if __name__ == '__main__':
    main()
