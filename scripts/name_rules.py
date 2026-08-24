#!/usr/bin/env python3
"""Take the place out of an event's name — the Where column is for that.

    python3 scripts/name_rules.py           # what would change, writes nothing
    python3 scripts/name_rules.py --write   # rename, keeping the published title
    python3 scripts/name_rules.py --check   # exit 1 if anything needs renaming

"Open Mic Night – Torquay Hotel" in a table whose next column says Torquay
Hotel prints the venue twice and pushes the actual event off the edge on a
phone. The name should say what is happening; Where says where.

The rules below propose; a human accepts. That is deliberate — a place inside a
name is sometimes the name ("Rip Curl Pro Bells Beach", "Lorne Pier to Pub
Swim"), and no amount of pattern-matching knows which. Those live in KEEP, one
line each with the reason. OVERRIDE is for the handful where the right name is
a rewrite, not a subtraction.

The gate that stops this doing damage: **a name may only shed a place when the
event has a venue_id.** A linked venue is a real row with an address and, in
most cases, coordinates, so the Where column definitely has something to show.
An event with only free text ("Various venues – Surf Coast", "Rotates — check
website", a bare suburb) keeps every word of its name. Link its venue and it
becomes eligible — which is the right incentive.
"""
import os, re, sys, json, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── the exceptions, one line each ────────────────────────────────────────
# A place that IS the name. Matched on the current name, exactly.
KEEP = {
  'Lorne Pier to Pub Swim':        'the swim is named for the pier and the pub',
  'Portarlington Mussel Festival': 'the festival is named for the town',
  'Queenscliff Music Festival':    'the festival is named for the town',
  'Anglesea Music Festival':       'the festival is named for the town',
  'Rip Curl Pro Bells Beach':      'the WSL event is named for the break',
  'Bells Beach Surf Film Festival':'named for the break, not held at it',
  'Lorne Sculpture Biennale':      'the biennale is named for the town',
}
# Where the right answer is a rewrite rather than a subtraction.
OVERRIDE = {
  'Torquay Library – School Holiday Program': 'Torquay Library Activities',
  'Dawn Service – Torquay RSL': 'Anzac Day Dawn Service',   # what it is, not who runs it
  'Repair Café Surf Coast': 'Repair Café',                  # it has one hall, in Aireys Inlet
}
# Words that are part of a place name rather than a place: they may appear in a
# chunk being tested without making it something other than the venue.
GEO = {'the','a','of','and','at','main','beach','reserve','park','hall','club',
       'centre','center','rooms','oval','precinct','hub','foreshore','cliff',
       'common','pier','carpark','car','st','street','rd','road','ave','avenue',
       'terrace','lane','ln','outlets','venue','venues','surf','life','saving'}
# A one-word name is too bare to stand alone; the type says what kind of thing.
TYPE_WORD = {'workshop':'Workshop','market':'Market','festival':'Festival',
             'class':'Class','course':'Course'}
DASH = r'[-–—]'

def toks(s):
    return set(re.findall(r"[a-z0-9]+", (s or '').lower().replace("'", '')))

def is_place(chunk, places):
    """True when the chunk names the venue or the suburb and nothing else."""
    c = toks(chunk)
    if not c:
        return False
    pool = set(GEO)
    for p in places:
        pool |= toks(p)
    return c <= pool

def distinctive(places):
    """Place words worth recognising. 'The' and 'Beach' are in every second
       venue name; 'Geelong' is the one that means something."""
    pool = set()
    for p in places:
        pool |= toks(p)
    return pool - GEO

def umbrella(chunk, places):
    """A festival or series that mentions a place without being one — 'Geelong
       After Dark' keeps its name, in brackets. Two tests keep this narrow: a
       long chunk is a subtitle rather than a banner, and one that is a place
       plus a single word is an organisation named after the town — 'Torquay
       RSL' runs the dawn service, it is not what the dawn service is called."""
    c = toks(chunk)
    if not (c & distinctive(places)) or is_place(chunk, places):
        return False
    rest = [w for w in chunk.split() if not toks(w) <= (distinctive(places) | GEO)]
    return 2 <= len(rest) and len(chunk.split()) <= 4

def tidy(name, *, venue=None, suburb=None, location=None, free_venue=None,
         type_=None, linked=True):
    """-> (new_name, why) or (name, None). See the module docstring."""
    name = (name or '').strip()
    if name in OVERRIDE:
        return OVERRIDE[name], 'named by hand'
    if name in KEEP:
        return name, None
    if not linked:
        return name, None

    places = [p for p in (venue, suburb, location, free_venue) if p]
    if not places:
        return name, None

    def finish(rest, chunk, how):
        rest = rest.strip(' -–—:,')
        if len(rest.split()) < 1 or len(rest) < 3:
            return name, None                       # nothing left worth showing
        if not re.match(r"[A-Z0-9'‘“]", rest):
            return name, None                       # remainder starts mid-phrase
        if not is_place(chunk, places):
            if not umbrella(chunk, places):
                return name, None                   # not a place at all
            rest = f'{rest} ({chunk.strip()})'       # a festival name, kept
            how += ', series name kept in brackets'
        if len(rest.split()) == 1 and TYPE_WORD.get(type_):
            rest = f'{rest} {TYPE_WORD[type_]}'
            how += f", '{TYPE_WORD[type_]}' added — one word is too bare"
        return rest, how

    # 1. a trailing place:  Queenie at The Sound Doctor, Open Mic Night – Torquay Hotel
    #    "at" first, and the LAST dash — "Budjerah – The Gentleman Tour at The
    #    Sound Doctor" is one event with a subtitle, not two dashes to guess at.
    for pat in (r'\s+(?:at|@)\s+(.+)$', rf'\s*{DASH}\s*([^-–—]+)$'):
        m = re.search(pat, name)
        if m:
            out, how = finish(name[:m.start()], m.group(1), 'venue dropped from the end')
            if how:
                return out, how

    # 2. a leading place before a separator:  Anglesea Community House – Ceramics
    m = re.match(rf'^(.+?)\s*{DASH}\s*', name) or re.match(r'^(.+?)\s+presents\s+', name)
    if m:
        out, how = finish(name[m.end():], m.group(1), 'venue dropped from the front')
        if how:
            return out, how

    # 3. a place mid-name after "at":  Comedy Night at The Sands featuring …
    for m in re.finditer(r'\s+at\s+(.+?)(?=\s+(?:featuring|feat\.?|with|presents)\s)', name):
        if is_place(m.group(1), places):
            return (name[:m.start()] + name[m.end():]).strip(), 'venue dropped from the middle'

    # 4. a bare leading suburb, no separator:  Torquay Cowrie Market
    #    Suburb only — never the venue name, or "Great Ocean Road Running
    #    Festival" loses its own name to a venue string that mentions the road.
    for place in sorted({p for p in (suburb, location) if p}, key=len, reverse=True):
        base = re.split(r'\s*[(/]', place)[0].strip()      # "Belmont (Geelong)"
        m = re.match(rf'^{re.escape(base)}\s+(?=\S)', name, re.I)
        if m:
            rest = name[m.end():]
            if len(rest.split()) >= 2 and re.match(r'[A-Z0-9]', rest):
                return rest, 'suburb dropped from the front'
    return name, None

# ── the database side ────────────────────────────────────────────────────
def load_env():
    f = ROOT/'.env'
    if f.exists():
        for line in f.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

def req(method, path, body=None, extra=None):
    r = urllib.request.Request(URL+path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    r.add_header('apikey', KEY); r.add_header('Authorization', 'Bearer '+KEY)
    r.add_header('Content-Type', 'application/json')
    for k, v in (extra or {}).items(): r.add_header(k, v)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}\n{e.read().decode()[:400]}")

def view_shows_the_venue():
    """The renames only make sense once the page can print the venue instead."""
    try:
        req('GET', '/rest/v1/listings?select=venue&limit=1')
        return True
    except SystemExit:
        return False

def proposals():
    events = req('GET', '/rest/v1/events?select=id,name,type,venue,venue_id,location,source_note&order=id')
    venues = {v['id']: v for v in req('GET', '/rest/v1/venues?select=id,name,suburb')}
    out = []
    for e in events:
        v = venues.get(e['venue_id'])
        new, why = tidy(e['name'], venue=v['name'] if v else None,
                        suburb=v['suburb'] if v else None,
                        location=e['location'], free_venue=e['venue'],
                        type_=e['type'], linked=e['venue_id'] is not None)
        if new != e['name']:
            out.append((e, new, why, v))
    return out

def main():
    args = set(sys.argv[1:])
    load_env()
    global URL, KEY
    URL = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    KEY = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not URL or not KEY:
        sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY (in the environment or .env).")

    props = proposals()
    for e, new, why, v in props:
        where = f"{v['name']} · {v['suburb']}" if v else '—'
        print(f"{e['id']:>3}  {e['name']}\n     → {new}\n     {why}; where says {where}\n")
    print(f"{len(props)} of the events would be renamed.")

    # An event with a date and a time is happening somewhere in particular, so
    # it should say where. These are the ones that cannot be renamed, and the
    # reason their names still carry a suburb or a region.
    homeless = [e for e in req('GET', '/rest/v1/events?select=id,name,starts_on,'
                               'time_text,venue,venue_id&venue_id=is.null&order=id')
                if e['starts_on'] and e['time_text']]
    if homeless:
        print(f"\n{len(homeless)} dated events have no venue — a date and a time "
              "means it happens somewhere:")
        for e in homeless:
            print(f"  {e['id']:>3}  {e['name']}  ({e['venue'] or 'no venue at all'})")

    if '--check' in args:
        sys.exit(1 if props else 0)
    if '--write' not in args:
        print("Nothing written. Add --write to apply.")
        return
    if not view_shows_the_venue():
        sys.exit("`listings` has no venue column yet, so the page would show the "
                 "suburb alone and these names would lose the venue entirely.\n"
                 "Run supabase/VENUE_IN_LISTINGS.sql in the Supabase SQL editor first.")
    for e, new, why, v in props:
        note = (e['source_note'] or '').strip()
        titled = f'Published as "{e["name"]}"; venue moved to the Where column, 24 Aug 2026.'
        req('PATCH', f"/rest/v1/events?id=eq.{e['id']}",
            {'name': new, 'source_note': (note+' — '+titled if note else titled)})
        print(f"renamed {e['id']}: {new}")
    print(f"{len(props)} renamed.")

if __name__ == '__main__':
    main()
