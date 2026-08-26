#!/usr/bin/env python3
"""What the database already holds, for a type or a whole group.

    python3 scripts/have.py cafe            # every listing carrying that type
    python3 scripts/have.py hospitality     # every type in that group, with counts
    python3 scripts/have.py                 # all 43 types, counts only
    python3 scripts/have.py places          # the places table, and which have a feed

A research pass runs this before it searches anything: `sync.py add` refuses a
name that already exists but knows nothing about near-misses, and re-researching
a place that is already in there is the cheapest way to waste an hour.

Read-only, and it uses the public anon key out of public/notice-data.js — no
.env, no service key, nothing here that isn't already on the live page.
"""
import sys, json, re, pathlib, urllib.request, urllib.parse, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
data  = (ROOT/'public'/'notice-data.js').read_text()
vocab = (ROOT/'public'/'notice-vocab.js').read_text()
URL = re.search(r'SUPABASE_URL\s*=\s*"([^"]+)"', data).group(1).rstrip('/')
KEY = re.search(r'SUPABASE_ANON\s*=\s*"([^"]+)"', data).group(1)

# GROUP_OF lives in notice-vocab.js and is read from there rather than copied,
# for the usual reason: two lists of which type is in which group would drift.
block = vocab.split('const GROUP_OF={',1)[1].split('};',1)[0]
GROUP_OF = {k.strip().strip("'\""): v.strip().strip("'\"")
            for k, v in re.findall(r"([^,{:]+):\s*'(\w+)'", block)}

def get(path):
    r = urllib.request.Request(URL + path)
    r.add_header('apikey', KEY); r.add_header('Authorization', 'Bearer ' + KEY)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read())

arg = ' '.join(sys.argv[1:]).strip()

# `places` is a separate table from `listings` and a research pass has to check
# both: a venue can be a place row the scraper reads without ever having a
# listing on the board, and re-adding it as an activity makes a second copy.
if arg == 'places':
    ps = get('/rest/v1/places?select=id,name,suburb,kind,website,events_url&limit=500')
    print(f'{len(ps)} places\n')
    for r in sorted(ps, key=lambda r: ((r.get('suburb') or 'zz'), r['name'])):
        feed = 'feed' if r.get('events_url') else ('site' if r.get('website') else '·')
        print(f'  {feed:5s} {r["name"][:44]:46s} {(r.get("suburb") or "—")[:18]:20s}'
              f'{r.get("kind") or "(no kind)"}')
    sys.exit()

rows = get('/rest/v1/listings?select=key,name,types,location,is_event,starts_on,lat&limit=2000')
count = collections.Counter(t for r in rows for t in (r.get('types') or []))

if not arg:
    for t, n in sorted(count.items(), key=lambda x: (GROUP_OF.get(x[0], 'zz'), -x[1])):
        print(f'{n:4d}  {t:22s} {GROUP_OF.get(t, "—")}')
    print(f'\n{len(rows)} listings, {len(count)} types in use')
    sys.exit()

# A group name expands to its types, thinnest first — that is the order a
# research pass should work them in. Anything else is taken as one type.
if arg in set(GROUP_OF.values()):
    types = sorted([t for t, g in GROUP_OF.items() if g == arg], key=lambda t: count[t])
else:
    types = [arg]
    if arg not in count and arg not in GROUP_OF:
        sys.exit(f"'{arg}' is not one of the 43 types or the nine groups. "
                 f"Run with no argument to see them all.")

for t in types:
    hits = [r for r in rows if t in (r.get('types') or [])]
    print(f'\n── {t} — {len(hits)} ─────────────────────────────')
    for r in sorted(hits, key=lambda r: (r.get('location') or 'zz', r['name'])):
        pin  = ' ' if r.get('lat') else '·'          # · means no coordinate yet
        kind = r.get('starts_on') or ('event' if r['is_event'] else '')
        prim = '' if (r.get('types') or [None])[0] == t else '  (secondary)'
        print(f'  {pin} {r["name"][:52]:54s} {(r.get("location") or "—")[:26]:28s}{kind}{prim}')
