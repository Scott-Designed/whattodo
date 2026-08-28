#!/usr/bin/env python3
"""What OpenStreetMap knows is in a town, against what we have listed.

    python3 scripts/nearby.py --refresh          # fetch the region ONCE (do this first)
    python3 scripts/nearby.py Anglesea           # food and drink there, vs what we list
    python3 scripts/nearby.py Torquay --kinds produce
    python3 scripts/nearby.py Lorne --missing    # only the ones we lack
    python3 scripts/nearby.py --all              # every town in the Place menu, as a table

Why this exists. The first big research pass (hospitality, 26 Aug 2026) searched
by town name — "cafes in Anglesea", the main-street strip, one town at a time —
and its own log worked out the flaw after Scott corrected it: a town-name search
cannot find a venue whose name does not contain the town. Love House, Skinny
Legs Café, The Captain of Aireys and Mr. T & Me were all missed that way, and
Anglesea finished with 5 listings against the 17 places OSM already had.

So walk the map instead.

**Ask once, not once per town.** The first version of this script queried
Overpass per town, which is the obvious shape and the wrong one: a sweep of the
47-town Place menu earned a wall of 429s, completed 18 towns, and then got this
address blocked outright by the main endpoint. Overpass is a free shared service
with a real usage policy. `--refresh` fetches the whole region in a single query
and caches it in scripts/osm_cache.json; every town lookup after that is local
and instant. Refresh when the cache is stale, not when you change towns.

**This is a search surface, not a source.** A name here is a lead: the row still
needs a first-party page for its hours and its url, and a proper geocode for its
pin, exactly as RESEARCH_RULES.md says. OSM is a second net, not a complete one —
a place nobody has mapped is not here, and the labels are contributors' opinions
(a pub that mostly does dinner may be tagged `restaurant`).

The "already listed" match is deliberately biased towards **false negatives**: it
wants two distinctive words in common, so "Le Comptoir" does not recognise itself
in "Le Comptoir Bakehouse" and gets shown as missing. That is the cheap direction
to be wrong in. The expensive one is reporting a real gap as already covered,
which is what the first version did — it matched "Love House Anglesea" to
"Anglesea Bakery" and hid the exact miss this script was written to catch.

Town centres are Nominatim's own results, usually administrative centroids. Fine
for *searching*, and never written anywhere — a centroid is exactly what this
project refuses to accept as a listing's coordinate.
"""
import json, math, re, sys, time, pathlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / 'scripts' / 'osm_cache.json'
UA = 'whattodo-janjuc'

# Mirrors, for when one is down or has had enough of us.
ENDPOINTS = ['https://overpass-api.de/api/interpreter',
             'https://overpass.kumi.systems/api/interpreter',
             'https://overpass.private.coffee/api/interpreter']

# Cape Otway up to Little River, the coast out past the Bellarine.
BBOX = '-39.00,143.30,-37.80,144.85'

# One query covers both passes; `--kinds` filters the cache afterwards.
#
# **OSM's tags are not a category system, and this list is the scar tissue.**
# The hospitality round-two pass found two venues the food query could not see:
# the Little River Hotel is tagged `tourism=hotel` because it has rooms, and
# Kennett River's Kafe Koala is tagged `shop=convenience` because it is also the
# general store. Both are pubs/cafes to anyone standing outside them. A tag says
# what one contributor thought the building was, so widen the net and judge
# afterwards — the cost of a wrong extra name is one look, and the cost of a
# missing one is a gap nobody knows is there.
#
# `convenience` in particular is noisy: in Geelong it is servos and milk bars, in
# Kennett River it is the only shop in town. Keep it, and judge by the town.
KIND_TAGS = {
    'food': {'amenity': {'cafe', 'restaurant', 'pub', 'bar', 'fast_food',
                         'ice_cream', 'biergarten', 'food_court'},
             'shop': {'bakery', 'deli', 'pastry', 'confectionery', 'coffee',
                      'convenience'},
             'craft': {'brewery', 'winery', 'distillery'},
             'tourism': {'hotel', 'guest_house'}},
    'produce': {'shop': {'greengrocer', 'farm', 'garden_centre', 'butcher', 'seafood',
                         'cheese', 'wine', 'health_food', 'alcohol', 'deli',
                         'chocolate', 'honey', 'dairy', 'convenience', 'confectionery',
                         'nursery'},
                # `florist` was here and came out 28 Aug 2026: it put nine Geelong
                # flower shops into the produce sweep, a quarter of that town's
                # misses, and a florist is neither produce nor a nursery.
                'amenity': {'marketplace'},
                'craft': {'winery', 'distillery'},
                'landuse': {'orchard', 'vineyard'}},
}
ALL_TAGS = {}
for kd in KIND_TAGS.values():
    for k, v in kd.items():
        ALL_TAGS.setdefault(k, set()).update(v)


def fetch(url, data=None, tries=3, timeout=60):
    # 60s, not 180. A blocked endpoint hangs rather than refusing, and three
    # tries across three mirrors at 180s each is a twenty-minute wait to learn
    # nothing. Fail fast and let the next mirror answer.
    delay = 5
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            if attempt == tries - 1:
                raise
            print(f'    ({getattr(e, "code", None) or e} — waiting {delay}s)',
                  file=sys.stderr, flush=True)
            time.sleep(delay)
            delay *= 3
    raise RuntimeError('unreachable')


def town_list():
    vocab = (ROOT / 'public' / 'notice-vocab.js').read_text()
    subs = re.findall(r"'([^']+)'", vocab.split('const SUBURBS=[', 1)[1].split('];', 1)[0])
    geel = set(re.findall(r"'([^']+)'", vocab.split('const GEELONG=new Set([', 1)[1]
                          .split(']);', 1)[0]))
    return sorted(s for s in subs if s not in geel or s == 'Geelong'), {s.lower() for s in subs}


def refresh():
    """One Overpass query for the whole region, plus one Nominatim call per town."""
    clauses = '\n'.join(f'  nwr["{k}"~"^({"|".join(sorted(v))})$"]["name"]({BBOX});'
                        for k, v in ALL_TAGS.items())
    q = f'[out:json][timeout:180];\n(\n{clauses}\n);\nout center tags;'
    print(f'asking Overpass for the whole region in one query '
          f'({sum(len(v) for v in ALL_TAGS.values())} tag values)…')
    data = urllib.parse.urlencode({'data': q}).encode()
    d = None
    for ep in ENDPOINTS:
        try:
            print(f'  {ep}')
            d = fetch(ep, data)
            break
        except Exception as e:
            print(f'    unavailable: {getattr(e, "code", None) or e}', file=sys.stderr)
    if d is None:
        sys.exit('Every Overpass endpoint refused.\n\n'
                 'Usually this means the address you are running from is rate-limited or\n'
                 'blocked from an earlier run — it happened here on 26 Aug 2026 after a\n'
                 'town-by-town sweep. Nominatim answering fine while Overpass returns 000\n'
                 'is the signature. Wait an hour, or run --refresh from somewhere else and\n'
                 'commit scripts/osm_cache.json; every town lookup reads the cache, so the\n'
                 'fetch only has to succeed once, anywhere.')

    pois = []
    for e in d.get('elements', []):
        t = e.get('tags', {})
        name = t.get('name')
        lat = e.get('lat') or (e.get('center') or {}).get('lat')
        lon = e.get('lon') or (e.get('center') or {}).get('lon')
        if not name or lat is None:
            continue
        label = t.get('amenity') or t.get('shop') or t.get('craft') or t.get('landuse')
        pois.append({'name': name, 'lat': lat, 'lon': lon, 'label': label})
    print(f'  {len(pois)} named places in the region')

    towns, _ = town_list()
    old = json.loads(CACHE.read_text())['towns'] if CACHE.exists() else {}
    centres = {}
    print(f'geocoding {len(towns)} town centres (1/sec, Nominatim policy)…')
    for t in towns:
        if t in old:                              # centres do not move
            centres[t] = old[t]
            continue
        qs = urllib.parse.urlencode({'format': 'json', 'limit': 1,
                                     'q': f'{t}, Victoria, Australia'})
        try:
            hits = fetch('https://nominatim.openstreetmap.org/search?' + qs)
            if hits:
                centres[t] = [float(hits[0]['lat']), float(hits[0]['lon'])]
        except Exception as e:
            print(f'  {t}: {e}', file=sys.stderr)
        time.sleep(1.1)
    CACHE.write_text(json.dumps({'fetched': time.strftime('%Y-%m-%d %H:%M'),
                                 'pois': pois, 'towns': centres}, indent=1))
    print(f'cached {len(pois)} places and {len(centres)} town centres → {CACHE.name}')


def load():
    if not CACHE.exists():
        sys.exit('no cache yet — run:  python3 scripts/nearby.py --refresh')
    c = json.loads(CACHE.read_text())
    # The town centres and the places are fetched from different services, and
    # the committed cache may hold only the centres — Nominatim answered while
    # Overpass was blocking, 26 Aug 2026. Empty places would otherwise report
    # every town as having nothing, which is the failure this script exists to
    # prevent, so say so instead.
    if not c.get('pois'):
        sys.exit('the cache has town centres but no places yet.\n'
                 'Run:  python3 scripts/nearby.py --refresh\n'
                 '(one Overpass query; the centres are already done and are reused)')
    return c


def km(a, b, c, d):
    p = math.pi / 180
    return 12742 * math.asin(math.sqrt(
        0.5 - math.cos((c - a) * p) / 2
        + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2))


# ── matching a name against what we already list ────────────────────────────
GENERIC = {'the', 'a', 'an', 'and', 'of', 'co', 'cafe', 'café', 'coffee', 'restaurant',
           'bar', 'pub', 'hotel', 'bakery', 'kitchen', 'bistro', 'eatery', 'takeaway'}
_, SUBURB_WORDS = town_list()


def norm(s):
    return re.sub(r'[^a-z0-9]', '', re.sub(r"[’']", '', s.lower()))


def keywords(s):
    """The words that actually identify a venue: not generic, not the town it is in."""
    words = re.split(r'[^a-z0-9]+', re.sub(r"[’']", '', s.lower()))
    return {w for w in words if len(w) >= 4 and w not in GENERIC and w not in SUBURB_WORDS}


def listed_names():
    data = (ROOT / 'public' / 'notice-data.js').read_text()
    url = re.search(r'SUPABASE_URL\s*=\s*"([^"]+)"', data).group(1).rstrip('/')
    key = re.search(r'SUPABASE_ANON\s*=\s*"([^"]+)"', data).group(1)
    req = urllib.request.Request(url + '/rest/v1/listings?select=name&limit=2000')
    req.add_header('apikey', key)
    req.add_header('Authorization', 'Bearer ' + key)
    with urllib.request.urlopen(req) as r:
        return [(norm(x['name']), x['name'], keywords(x['name'])) for x in json.load(r)]


def match(name, listed):
    """Catches 'Blackmans Brewery' vs "Blackman's Brewery, Torquay" without catching
    'Yo! Chicken' vs 'Piping Hot Chicken Shop'. One shared word is not a venue, and
    reporting a real miss as already-listed hides the gap this script exists to show."""
    n, kw = norm(name), keywords(name)
    for k, original, other in listed:
        if k == n:
            return original
        if kw and (kw == other or (len(kw) >= 2 and kw <= other)):
            return original
    return None


def town_pois(cache, town, kind, radius_km):
    if town not in cache['towns']:
        sys.exit(f"no centre cached for '{town}'. Run --refresh, or check the spelling.")
    tlat, tlon = cache['towns'][town]
    want = KIND_TAGS[kind]
    keep = {v for vs in want.values() for v in vs}
    out = {}
    for p in cache['pois']:
        if p['label'] not in keep:
            continue
        if km(tlat, tlon, p['lat'], p['lon']) <= radius_km:
            out.setdefault(p['name'], set()).add(p['label'])
    return out, (tlat, tlon)


def main():
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--refresh' in flags:
        return refresh()

    # Both `--kinds produce` and `--kinds=produce`. The first version read only
    # the equals form while the docstring above showed the space form, so a sweep
    # run exactly as documented silently fell back to `food` AND swallowed the
    # word `produce` as part of the town name. Silently wrong is the worst
    # failure a search tool can have — found by the produce pass, 28 Aug 2026.
    def opt(name, default):
        for i, f in enumerate(sys.argv[1:]):
            if f == '--' + name:                       # --kinds produce
                rest = sys.argv[i + 2:]
                if rest and not rest[0].startswith('--'):
                    return rest[0]
            if f.startswith('--' + name + '='):        # --kinds=produce
                return f.split('=', 1)[1]
        return default

    kind = opt('kinds', 'food')
    radius = float(opt('radius', 2000)) / 1000
    # A bare value consumed by a flag is not part of the town name.
    for name in ('kinds', 'radius'):
        v = opt(name, None)
        if v in args:
            args.remove(v)
    if kind not in KIND_TAGS:
        sys.exit(f'--kinds must be one of {sorted(KIND_TAGS)}')

    cache = load()
    listed = listed_names()
    towns, _ = town_list()

    if '--all' in flags:
        print(f"\nevery town in the Place menu — {kind}, {radius:g}km "
              f"(OSM cache {cache['fetched']})\n")
        rows = []
        for t in towns:
            if t not in cache['towns']:
                continue
            found, _c = town_pois(cache, t, kind, radius)
            miss = [n for n in found if not match(n, listed)]
            rows.append((t, len(found), len(miss)))
        for t, o, m in sorted(rows, key=lambda r: -r[2]):
            bar = '█' * min(m, 40)
            print(f'  {t:18s} {o:4d} on the map · {m:4d} not listed  {bar}')
        print(f'\n  {sum(r[1] for r in rows)} places, {sum(r[2] for r in rows)} of them '
              f'not in the database')
        print('  A name here is a lead, not a source — each still needs a first-party page.')
        return

    if not args:
        sys.exit(__doc__.strip().split('\n\n')[0])
    town = ' '.join(args)
    found, (tlat, tlon) = town_pois(cache, town, kind, radius)
    have, missing = [], []
    for name in sorted(found):
        hit = match(name, listed)
        (have if hit else missing).append((name, '/'.join(sorted(found[name])), hit))

    print(f'\n{town} — {kind}, {radius:g}km around {tlat:.4f},{tlon:.4f} '
          f"(OSM cache {cache['fetched']})")
    print(f'{len(found)} named in OpenStreetMap · {len(have)} already listed · '
          f'{len(missing)} not\n')
    if '--missing' not in flags and have:
        print('  already listed')
        for name, labels, hit in have:
            same = '' if norm(name) == norm(hit) else f'   (listed as "{hit}")'
            print(f'    ·  {name[:40]:42s} {labels}{same}')
        print()
    print('  NOT in the database')
    for name, labels, _ in missing:
        print(f'    +  {name[:40]:42s} {labels}')
    print('\n  A name here is a lead, not a source. Each one still needs a first-party')
    print('  page for its hours and url, and its own geocode for the pin.')


if __name__ == '__main__':
    main()
