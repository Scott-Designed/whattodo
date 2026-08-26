#!/usr/bin/env python3
"""What OpenStreetMap knows is in a town, against what we have listed.

    python3 scripts/nearby.py Anglesea               # food and drink (default)
    python3 scripts/nearby.py Torquay --kinds produce
    python3 scripts/nearby.py "Aireys Inlet" --radius 3000
    python3 scripts/nearby.py Lorne --missing         # only the ones we lack

Why this exists. The first big research pass (hospitality, 26 Aug 2026) searched
by town name — "cafes in Anglesea", the main-street strip, one town at a time —
and its own log worked out the flaw after Scott corrected it: a town-name search
cannot find a venue whose name does not contain the town. Love House, Skinny
Legs Café, The Captain of Aireys and Mr. T & Me were all missed that way, and
Anglesea finished with 5 listings against the 17 places OSM already had.

So walk the map instead. Overpass is free, needs no key, and answers "everything
of this kind within N metres" in one request — which is the question a research
pass is actually asking.

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

The town centre used to centre the search is Nominatim's own result for the town,
which is usually an administrative centroid. That is fine for *searching* and is
never written anywhere — a centroid is exactly what this project refuses to
accept as a listing's coordinate.
"""
import json, re, sys, time, pathlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = 'whattodo-janjuc'

KINDS = {
    # what a hospitality pass is looking for
    'food': ('nwr(around:{r},{lat},{lon})["amenity"~"^(cafe|restaurant|pub|bar|'
             'fast_food|ice_cream|biergarten)$"];\n'
             'nwr(around:{r},{lat},{lon})["shop"~"^(bakery|deli|pastry|'
             'confectionery|coffee)$"];\n'
             'nwr(around:{r},{lat},{lon})["craft"~"^(brewery|winery|distillery)$"];'),
    # what a produce pass is looking for
    'produce': ('nwr(around:{r},{lat},{lon})["shop"~"^(greengrocer|farm|garden_centre|'
                'deli|butcher|seafood|cheese|wine|health_food)$"];\n'
                'nwr(around:{r},{lat},{lon})["amenity"="marketplace"];\n'
                'nwr(around:{r},{lat},{lon})["landuse"="orchard"]["name"];\n'
                'nwr(around:{r},{lat},{lon})["shop"="alcohol"];'),
}


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def town_centre(town):
    q = urllib.parse.urlencode({'format': 'json', 'limit': 1,
                                'q': f'{town}, Victoria, Australia'})
    hits = get('https://nominatim.openstreetmap.org/search?' + q)
    if not hits:
        sys.exit(f"Nominatim does not know '{town}'. Check the spelling.")
    return float(hits[0]['lat']), float(hits[0]['lon'])


def overpass(kind, lat, lon, radius):
    body = KINDS[kind].format(r=radius, lat=lat, lon=lon)
    q = f'[out:json][timeout:40];\n(\n{body}\n);\nout center tags;'
    d = get('https://overpass-api.de/api/interpreter',
            urllib.parse.urlencode({'data': q}).encode())
    out = {}
    for e in d.get('elements', []):
        t = e.get('tags', {})
        name = t.get('name')
        if not name:
            continue
        label = t.get('amenity') or t.get('shop') or t.get('craft') or t.get('landuse') or '?'
        out.setdefault(name, set()).add(label)
    return out


def listed_names():
    """Every name already in the database, normalised for comparison."""
    data = (ROOT / 'public' / 'notice-data.js').read_text()
    url = re.search(r'SUPABASE_URL\s*=\s*"([^"]+)"', data).group(1).rstrip('/')
    key = re.search(r'SUPABASE_ANON\s*=\s*"([^"]+)"', data).group(1)
    req = urllib.request.Request(url + '/rest/v1/listings?select=name,location&limit=2000')
    req.add_header('apikey', key)
    req.add_header('Authorization', 'Bearer ' + key)
    with urllib.request.urlopen(req) as r:
        return [(norm(x['name']), x['name'], x.get('location') or '') for x in json.load(r)]


GENERIC = {'the', 'a', 'an', 'and', 'of', 'co', 'cafe', 'café', 'coffee', 'restaurant',
           'bar', 'pub', 'hotel', 'bakery', 'kitchen', 'bistro', 'eatery', 'takeaway'}
SUBURBS = {w.lower() for w in re.findall(r"'([^']+)'",
           (ROOT / 'public' / 'notice-vocab.js').read_text()
           .split('const SUBURBS=[', 1)[1].split('];', 1)[0])}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', re.sub(r"[’']", '', s.lower()))


def keywords(s):
    """The words that actually identify a venue: not generic, not the town it is in.

    Matching on a normalised whole string is what went wrong first: stripping the
    type words off "Anglesea Bakery" left the key "anglesea", which is a substring
    of "Love House Anglesea", so a real miss was reported as already listed. So
    compare the distinctive words instead, and only trust ones long enough to mean
    something."""
    words = re.split(r'[^a-z0-9]+', re.sub(r"[’']", '', s.lower()))
    return {w for w in words if len(w) >= 4 and w not in GENERIC and w not in SUBURBS}


def match(name, listed):
    """Catches 'Blackmans Brewery' vs "Blackman's Brewery, Torquay" without
    catching 'Anglesea Pub' vs 'Aireys Pub'."""
    n, kw = norm(name), keywords(name)
    for k, original, _ in listed:
        if k == n:
            return original
        other = keywords(original)
        if not kw:
            continue
        # One shared word is not a venue. "Yo! Chicken" and "Piping Hot Chicken
        # Shop" both keep `chicken`, and reporting a real miss as already-listed
        # is the expensive direction to be wrong in — it hides the gap this
        # script exists to show. Two words, or the whole keyword set matching.
        if kw == other or (len(kw) >= 2 and kw <= other):
            return original
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    if not args:
        sys.exit(__doc__.strip().split('\n\n')[1])
    town = ' '.join(args)
    kind = 'food'
    radius = 2000
    for f in flags:
        if f.startswith('--kinds'):
            kind = f.split('=', 1)[1] if '=' in f else 'food'
        if f.startswith('--radius'):
            radius = int(f.split('=', 1)[1])
    if kind not in KINDS:
        sys.exit(f"--kinds must be one of {sorted(KINDS)}")
    only_missing = '--missing' in flags

    lat, lon = town_centre(town)
    time.sleep(1)                       # Nominatim asks for one request a second
    found = overpass(kind, lat, lon, radius)
    listed = listed_names()

    have, missing = [], []
    for name in sorted(found):
        labels = '/'.join(sorted(found[name]))
        hit = match(name, listed)
        (have if hit else missing).append((name, labels, hit))

    print(f'\n{town} — {kind}, {radius}m around {lat:.4f},{lon:.4f}')
    print(f'{len(found)} named in OpenStreetMap · {len(have)} already listed · '
          f'{len(missing)} not\n')
    if not only_missing and have:
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
