"""Geelong Arts Centre — geelongartscentre.org.au

The what's-on page draws its list in JavaScript, but the site publishes a
sitemap per section and the EVENT one lists every event page (132 on 7 Sep
2026). Each event page prints, as plain text:

    Performances:
    Tue, 22 Sep 2026   10:00am
    Tue, 22 Sep 2026   01:00pm
    Wed, 23 Sep 2026   10:00am
    ...
    Ticket Prices:
    ...
    VENUE:
    The Story House
    50 Little Malop Street

so the parser reads the sitemap, fetches each page a second apart, and reads
those two blocks. The weekday is checked against the date — a line whose
weekday is wrong is thrown away, not guessed at. No schema.org anywhere on the
site, which is why this file exists.

Shape: consecutive dates carrying the same session times fold into ONE row
with ends_on (a two-day kids' show, a week-long season), and every other date
is its own row — the review queue folds same-name rows into one line anyway.
Two sessions on one day print as "10am & 1pm" in time_text; the board prints
that fine and the ON NOW badge simply cannot read it, which is accepted.
"""
import re, json, time, datetime, html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import eventlib as E

HOST     = 'geelongartscentre.org.au'
SITEMAP  = f'https://{HOST}/sitemaps-1-section-event-1-sitemap.xml'
LEDGER   = E.ROOT / 'scripts' / 'parser_counts.json'
POLITE   = 1.0
WD       = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MON      = {m: i for i, m in enumerate(['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'], 1)}
# One line per performance: "Tue, 22 Sep 2026 10:00am". The time is optional
# on the line because a page can print a date with no clock.
DATE_RE  = re.compile(r'^(?P<wd>Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+(?P<d>\d{1,2})\s+(?P<mon>[A-Za-z]{3})[a-z]*\s+(?P<y>\d{4})'
                      r'(?:\s+(?P<h>\d{1,2}):(?P<mi>\d{2})\s*(?P<ap>am|pm))?\s*$', re.I)

def lines_of(page):
    h = re.sub(r'(?is)<(script|style).*?</\1>', ' ', page)
    h = re.sub(r'(?i)<(br|/?p|/?div|/?li|/?h[1-6]|/?tr|/?section|/?article|/?dt|/?dd)[^>]*>', '\n', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    return [re.sub(r'\s+', ' ', l).strip() for l in html.unescape(h).splitlines() if l.strip()]

def clock(h, mi, ap):
    h = int(h) % 12 + (12 if ap.lower() == 'pm' else 0)
    hh = h % 12 or 12
    return f"{hh}:{int(mi):02d}{'am' if h < 12 else 'pm'}" if int(mi) else f"{hh}{'am' if h < 12 else 'pm'}"

def performances(lines):
    """{date: [time, …]} off the Performances block, weekday-checked."""
    out = {}
    try: i = next(k for k, l in enumerate(lines) if l.lower().startswith('performances'))
    except StopIteration: return out
    for l in lines[i + 1:i + 200]:
        m = DATE_RE.match(l)
        if not m:
            if l.endswith(':') or l.lower().startswith(('ticket prices', 'venue')): break
            continue
        mon = MON.get(m.group('mon').lower())
        if not mon: continue
        try: day = datetime.date(int(m.group('y')), mon, int(m.group('d')))
        except ValueError: continue
        if WD[day.weekday()].lower() != m.group('wd').lower():     # the checksum
            continue
        d = day.isoformat(); out.setdefault(d, [])
        if m.group('h'):
            h24 = int(m.group('h')) % 12 + (12 if m.group('ap').lower() == 'pm' else 0)
            tt = (h24 * 60 + int(m.group('mi')), clock(m.group('h'), m.group('mi'), m.group('ap')))
            if tt not in out[d]: out[d].append(tt)
    # Clock order, not page order — the first write printed "8pm & 5pm".
    return {d: [tt for _, tt in sorted(v)] for d, v in out.items()}

def after(lines, label):
    try:
        i = next(k for k, l in enumerate(lines) if l.lower().rstrip(':') == label)
        return lines[i + 1]
    except (StopIteration, IndexError):
        return None

def read_page(url, page):
    lines = lines_of(page)
    title = (re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S) or [''])[0]
    title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
    perf  = performances(lines)
    if not title or not perf: return []
    room  = after(lines, 'venue')
    dur   = after(lines, 'duration')
    age   = after(lines, 'age recommendation')
    prose = [l for l in lines if len(l) > 120][:2]
    desc  = ' '.join(prose)
    if dur or age: desc = (desc + ' ' if desc else '') + ' · '.join(x for x in (dur, age) if x)
    desc  = E.text(desc) if desc else None
    # Fold consecutive dates with identical sessions into one run.
    days  = sorted(perf)
    gigs, i = [], 0
    while i < len(days):
        j = i
        while (j + 1 < len(days) and perf[days[j + 1]] == perf[days[i]]
               and (datetime.date.fromisoformat(days[j + 1]) - datetime.date.fromisoformat(days[j])).days == 1):
            j += 1
        gigs.append({'name': title[:200], 'starts_on': days[i],
                     'ends_on': days[j] if j > i else None,
                     'time_text': ' & '.join(perf[days[i]]) or None,
                     'description': desc, 'url': E.clean_url(url),
                     'venue_name': room, 'conf': 'high'})
        i = j + 1
    return gigs

def read(venue, src, page=None):
    """(gigs, how) — the whole answer for this venue."""
    from . import WRITE
    sm = E.fetch(SITEMAP)
    if not sm: return [], 'parser failed — the event sitemap did not answer'
    urls = [u for u in re.findall(r'<loc>([^<]+)</loc>', sm) if '/whats-on/all-events/' in u]
    gigs, pages, perfs = [], 0, 0
    for u in urls:
        time.sleep(POLITE)
        pg = E.fetch(u, cap=4_000_000)
        if not pg: continue
        pages += 1
        got = read_page(u, pg)
        perfs += sum(len(v) for v in performances(lines_of(pg)).values())
        gigs += got
    # ── the zero guard ──
    led = {}
    try: led = json.loads(LEDGER.read_text())
    except Exception: pass
    prev = led.get(HOST) or {}
    if WRITE:
        led[HOST] = {'events': len(gigs), 'pages': pages, 'urls': len(urls),
                     'at': datetime.date.today().isoformat()}
        LEDGER.write_text(json.dumps(led, indent=1) + '\n')
    if not gigs and prev.get('events'):
        return [], (f"parser failed — found 0 events on {pages} of {len(urls)} pages where it "
                    f"found {prev['events']} on {prev.get('at')}; the site has probably changed")
    if not gigs:
        return [], f'parser found nothing on {pages} of {len(urls)} pages'
    return gigs, f'Geelong Arts Centre parser ({len(gigs)} events, {perfs} performances, {pages} pages)'
