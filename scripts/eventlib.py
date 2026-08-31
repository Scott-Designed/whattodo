"""Shared plumbing for the event scrapers.

Two jobs read from the outside world — `scrape_events.py` (the Surf Coast
Events calendar) and `scrape_venues.py` (each venue's own ticketing page).
What they have in common lives here so they cannot quietly drift apart:
talking to Supabase, cleaning third-party text, remembering what has already
been offered, and asking a site's robots.txt for permission before reading it.

Nothing here calls a model. A run costs nothing on the API meter.
"""
import os, re, sys, json, html, pathlib, datetime, urllib.request, urllib.error, urllib.parse
import urllib.robotparser as robotparser

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA   = 'whattodo-janjuc/1.0 (+https://whattodo-nu.vercel.app; community events listing)'

def log(*a): print(*a, file=sys.stderr)

# ── the database ────────────────────────────────────────────────────────────
def load_env():
    f = ROOT / '.env'
    if f.exists():
        for line in f.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

# PostgREST caps a response at 1000 rows on Supabase whatever `limit` says, and
# it says nothing about it — 200 OK and a short array. Pass all_rows=True to page
# with Range until a page comes back short, which is the only end-of-data signal
# it gives. Found three times on 30 Aug 2026: the board, /admin, and have.py.
PAGE = 1000

def db(method, path, body=None, extra=None, all_rows=False):
    if all_rows:
        out, lo = [], 0
        while True:
            chunk = db(method, path, body,
                       {**(extra or {}), 'Range-Unit': 'items',
                        'Range': f'{lo}-{lo + PAGE - 1}'})
            out += chunk
            if len(chunk) < PAGE:
                return out
            lo += PAGE

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

# ── reading other people's sites ────────────────────────────────────────────
_ROBOTS = {}

def robots_ok(url):
    """Ask the host's robots.txt before reading, and obey a refusal.

    We fetch robots.txt ourselves rather than letting RobotFileParser.read() do
    it, because that uses Python's default user-agent, which a lot of firewalls
    answer with 403 — and RobotFileParser reads a 403 as "forbidden from the
    whole site". That turned a site whose robots.txt plainly allows us into a
    silent skip. A missing or unreadable robots.txt means no rules; only an
    actual 401/403 on robots.txt itself is treated as a refusal.
    """
    try:
        p = urllib.parse.urlsplit(url)
        root = f"{p.scheme}://{p.netloc}"
    except ValueError:
        return False
    if root not in _ROBOTS:
        rp = robotparser.RobotFileParser()
        req = urllib.request.Request(root + '/robots.txt')
        req.add_header('User-Agent', UA)
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                rp.parse(r.read(200_000).decode('utf-8', 'replace').splitlines())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): rp.disallow_all = True   # a real refusal
            else: rp = None                                   # 404 etc: no rules
        except Exception:
            rp = None                                         # unreachable: no rules
        _ROBOTS[root] = rp
    rp = _ROBOTS[root]
    if rp is None: return True
    # Ask as ourselves and as a plain crawler; obey the stricter answer.
    return rp.can_fetch(UA, url) and rp.can_fetch('*', url)

def fetch(url, cap=250_000, timeout=15):
    """GET a page, honouring robots.txt. Returns None rather than raising."""
    if not robots_ok(url):
        return None
    q = urllib.request.Request(url)
    q.add_header('User-Agent', UA)
    q.add_header('Accept', 'text/html,application/json;q=0.9,*/*;q=0.5')
    try:
        with urllib.request.urlopen(q, timeout=timeout) as r:
            return r.read(cap).decode('utf-8', 'replace')
    except Exception:
        return None

# ── tidying third-party text ────────────────────────────────────────────────
def text(s, limit=600):
    """Strip someone else's HTML to plain prose. Their markup is data, never
    instructions, and nothing here evaluates it."""
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s or '')
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    # stripped markup leaves venue names stuttering; collapse repeats
    s = re.sub(r"\b(\w[\w'-]*)(\s+\1\b)+", r'\1', s, flags=re.I)
    if len(s) > limit:
        s = s[:limit].rsplit(' ', 1)[0] + '…'
    return s or None

def clean_url(u):
    u = (u or '').strip()
    if not u.startswith(('http://', 'https://')): return None
    if 'maps.app.goo.gl' in u: return None      # these get fabricated — CLAUDE.md
    return u

def norm(s):
    return re.sub(r'[^a-z0-9]+', '', html.unescape(s or '').lower())

def clock(hhmm):
    h, m = int(hhmm[:2]), int(hhmm[3:5])
    ap = 'am' if h < 12 else 'pm'
    hh = h % 12 or 12
    return f"{hh}:{m:02d}{ap}" if m else f"{hh}{ap}"

# ── schema.org Event, wherever it appears ───────────────────────────────────
# schema.org names most Event subtypes with "Event" in them — MusicEvent,
# EducationEvent, SportsEvent — so a substring test catches nearly everything.
# Three do not, and Festival is the one that matters here: `'Event' in 'Festival'`
# is False, so every festival on every source was being dropped in silence.
# Moshtix types Spilt Milk and the Queenscliff Music Festival exactly that way.
EVENT_SUBTYPES = {'Festival', 'Hackathon', 'CourseInstance'}

def is_event_type(t):
    """Is this @type a schema.org Event? `t` may be several types, space-joined."""
    toks = set(str(t or '').split())
    if not toks: return False
    return (any('Event' in x and x != 'EventVenue' for x in toks)
            or bool(toks & EVENT_SUBTYPES))

def jsonld_events(page):
    """Every schema.org Event in a page's JSON-LD blocks, flattened."""
    if not page or 'application/ld+json' not in page: return []
    out = []
    for block in re.findall(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page):
        try: doc = json.loads(block)
        except json.JSONDecodeError: continue
        stack = [doc]
        while stack:
            o = stack.pop()
            if isinstance(o, list): stack.extend(o); continue
            if not isinstance(o, dict): continue
            stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
            t = o.get('@type')
            t = ' '.join(t) if isinstance(t, list) else str(t or '')
            if o.get('startDate') and is_event_type(t):
                out.append(o)
    return out

def from_jsonld(o):
    """schema.org Event -> the fields this database keeps. None if unusable."""
    start = str(o.get('startDate') or '')
    m = re.match(r'(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}))?', start)
    if not m: return None
    day, hhmm = m.group(1), m.group(2)
    end = str(o.get('endDate') or '')
    me = re.match(r'(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}))?', end)
    tt = None
    if hhmm:
        tt = clock(hhmm)
        if me and me.group(2) and me.group(1) == day:
            tt += '–' + clock(me.group(2))
    name = o.get('name')
    name = ' '.join(name) if isinstance(name, list) else name
    # Where the gig actually happens. A host page can belong to an organisation
    # that runs events all over the shire, so the source row cannot be assumed
    # to be the room — only the event itself knows that.
    loc = o.get('location')
    loc = loc[0] if isinstance(loc, list) and loc else loc
    vname = vsub = vaddr = None
    if isinstance(loc, dict):
        vname = loc.get('name')
        vname = ' '.join(vname) if isinstance(vname, list) else vname
        a = loc.get('address')
        if isinstance(a, dict):
            vaddr = a.get('streetAddress'); vsub = a.get('addressLocality')
        elif isinstance(a, str):
            vaddr = a
            m2 = re.search(r',\s*([A-Za-z \'-]+?)\s+(?:VIC|NSW|QLD|SA|WA|TAS|NT|ACT)\b', a)
            if m2: vsub = m2.group(1).strip()
    # The publisher's own classification of what this IS. jsonld_events has
    # already read it to decide the object is an Event at all, and it was being
    # thrown away here — which left scrape_venues.py with nothing to type a row
    # from, so it typed all 83 of them `music`.
    st = o.get('@type')
    st = ' '.join(st) if isinstance(st, list) else str(st or '')
    return {
        'schema_type'  : st or None,
        'venue_name'   : html.unescape(str(vname)).strip() if vname else None,
        'venue_suburb' : html.unescape(str(vsub)).strip() if vsub else None,
        'venue_address': html.unescape(str(vaddr)).strip() if vaddr else None,
        'name'     : html.unescape(str(name or '')).strip(),
        'starts_on': day,
        'ends_on'  : me.group(1) if me and me.group(1) > day else None,
        'time_text': tt,
        'description': text(o.get('description')),
        'url'      : clean_url(o.get('url')),
    }

# ── Eventbrite, through its own API ─────────────────────────────────────────
# The right road for this one: an organiser page lists its events behind JS,
# and the API hands them over with the VENUE attached, which is the fact that
# matters — the organiser is not the room. Needs EVENTBRITE_TOKEN in the
# environment; without it the caller reports the venue as needing a person
# rather than guessing.
#
# The token is read from the environment and nowhere else. It never goes in a
# place row, in the page, or in a log line.
EB_API = 'https://www.eventbriteapi.com/v3'

def eventbrite_org_id(url):
    """The organiser id out of any /o/ URL — bare, or slug-then-id."""
    m = re.search(r'/o/(?:[a-z0-9\-]*?-)?(\d{6,})', str(url or ''), re.I)
    return m.group(1) if m else None

def eventbrite_events(org_id, token, horizon_days=400):
    """Live events for one organiser, in the same shape as from_jsonld.

    Paged: the API caps a page at 50 and says so in `pagination`, and an
    organiser with more than that would otherwise be silently truncated.
    """
    # `venue` is what this reader exists for — the organiser is not the room.
    # `category`/`subcategory` are what lets the caller type the row from the
    # platform's own classification instead of guessing. They are asked for
    # separately because this runs unattended twice a week: if a future API
    # rejects the wider expand, the venue must still import rather than the
    # whole organiser failing over a nice-to-have. A 400 is the only code that
    # can mean "I do not know that expansion" — 401/403/404 are about the token
    # or the organiser and retrying with fewer fields would only hide them.
    out, page, expand = [], 1, 'venue,category,subcategory'
    while page <= 10:
        q = urllib.parse.urlencode({
            'status': 'live', 'order_by': 'start_asc',
            'expand': expand, 'page': page})
        req = urllib.request.Request(f'{EB_API}/organizers/{org_id}/events/?{q}')
        # .strip(): a token set from a prompt or a copied line arrives with a
        # trailing newline often enough to be worth defending against, and it
        # fails as a flat 401 that looks like the wrong token entirely.
        req.add_header('Authorization', 'Bearer ' + token.strip())
        req.add_header('User-Agent', UA)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                doc = json.loads(r.read().decode('utf-8', 'replace'))
        except urllib.error.HTTPError as e:
            if e.code == 400 and expand != 'venue':
                expand = 'venue'
                continue
            # Say which failure it is. A 401 is about the token and no amount of
            # re-running fixes it; a 404 is about this organiser and the others
            # may still be fine.
            why = {401: 'token rejected — it must be the PRIVATE TOKEN from '
                        'eventbrite.com/platform/api-keys, not an API key, public '
                        'token or OAuth client secret',
                   403: 'token lacks permission for this organiser',
                   404: 'no such organiser — it may have been deleted',
                   429: 'rate limited; try again later'}.get(e.code, 'unexpected')
            raise RuntimeError(f'{e.code} {why}') from None
        except Exception as e:
            raise RuntimeError(f'Eventbrite unreachable: {str(e)[:60]}') from None

        for ev in doc.get('events') or []:
            g = eventbrite_one(ev)
            if g: out.append(g)
        pg = doc.get('pagination') or {}
        if not pg.get('has_more_items'): break
        page += 1
    cutoff = (today() + datetime.timedelta(days=horizon_days)).isoformat()
    return [g for g in out if g['starts_on'] <= cutoff]

def eventbrite_one(ev):
    """One API event -> the fields this database keeps."""
    # `local` is the wall time at the venue, which is what a listing should say.
    # `utc` is also given and using it would shift every Melbourne event.
    start = ((ev.get('start') or {}).get('local') or '')
    m = re.match(r'(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?', start)
    if not m: return None
    day, hhmm = m.group(1), m.group(2)
    end = ((ev.get('end') or {}).get('local') or '')
    me = re.match(r'(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?', end)
    tt = None
    if hhmm:
        tt = clock(hhmm)
        if me and me.group(2) and me.group(1) == day:
            tt += '–' + clock(me.group(2))
    v = ev.get('venue') or {}
    a = v.get('address') or {}
    # Eventbrite classifies every event itself — "Music", "Arts", "Food & Drink".
    # Needs expand=category on the request; without it this is simply None and
    # the row falls through to its title, then to unsorted.
    cat = ((ev.get('category') or {}).get('name') or '').strip() or None
    sub = ((ev.get('subcategory') or {}).get('name') or '').strip() or None
    return {
        'category'     : cat,
        'subcategory'  : sub,
        'venue_name'   : (v.get('name') or '').strip() or None,
        'venue_suburb' : (a.get('city') or '').strip() or None,
        'venue_address': (a.get('address_1') or '').strip() or None,
        'name'         : ((ev.get('name') or {}).get('text') or '').strip(),
        'starts_on'    : day,
        'ends_on'      : me.group(1) if me and me.group(1) > day else None,
        'time_text'    : tt,
        'description'  : text((ev.get('description') or {}).get('text') or ''),
        'url'          : clean_url(ev.get('url')),
    }

# ── remembering what has been offered ───────────────────────────────────────
class Seen:
    """Every source id ever offered, so something rejected does not come back
    next Thursday. Delete a line in the file to be offered it again."""
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.ids = set()
        if self.path.exists():
            try: self.ids = set(json.loads(self.path.read_text()).get('offered') or [])
            except json.JSONDecodeError: pass
    def __contains__(self, k): return k in self.ids
    def add(self, k): self.ids.add(k)
    def save(self, note):
        self.path.write_text(json.dumps(
            {'note': note, 'offered': sorted(self.ids)}, indent=1) + '\n')

def today(): return datetime.date.today()
