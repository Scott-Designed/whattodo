#!/usr/bin/env python3
"""The outline of every town in the Place menu -> public/notice-places.geojson.

The map draws these under the pins so it is clear which towns the site covers.

    python3 scripts/place_outlines.py            # fetch (cached), build, report
    python3 scripts/place_outlines.py --refetch  # ignore the cache

The town list is read out of public/notice-vocab.js, never kept here, so a
town added to SUBURBS gets an outline the next time this runs and one that is
missing is named in the report rather than silently absent.

Source is OpenStreetMap through Nominatim (1 request a second, a real
User-Agent). Only a LOCALITY boundary is accepted — a suburb, town, village or
hamlet polygon. A council area is refused by name: "Geelong" must be the
suburb, not the City of Greater Geelong, which would paint half the region.

The suburbs the site folds into Geelong are dissolved into one shape. OSM
boundaries share their nodes, so an edge two suburbs both carry is an internal
border and is dropped; what is left is stitched back into rings. Nothing is
simplified until after that, or the shared edges stop matching.
"""
import json, math, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB = os.path.join(ROOT, 'public', 'notice-vocab.js')
OUT = os.path.join(ROOT, 'public', 'notice-places.geojson')
CACHE = os.path.join(ROOT, 'scripts', '.place_outlines_cache.json')
UA = 'whattodo-janjuc (notice.place; place outlines)'

# What Nominatim calls a locality. Anything else — municipality, county,
# state, a park, a road — is not the town.
LOCALITY = {'suburb', 'town', 'village', 'hamlet', 'locality', 'city', 'neighbourhood',
            'quarter', 'city_district', 'borough'}
# How the vocabulary spells it -> how the map spells it.
ASK_AS = {'Mt Duneed': 'Mount Duneed'}
TOLERANCE = 0.00035        # degrees, about 35 m — invisible at the zooms the map uses


def vocab():
    src = open(VOCAB, encoding='utf-8').read()
    def names(decl):
        body = re.search(decl + r'\s*=\s*(?:new Set\()?\[(.*?)\]', src, re.S).group(1)
        return re.findall(r"'([^']+)'", body)
    return names('const SUBURBS'), set(names('const GEELONG'))


def ask(name):
    q = urllib.parse.urlencode({'q': f'{ASK_AS.get(name, name)}, Victoria, Australia',
                                'format': 'jsonv2', 'polygon_geojson': 1, 'limit': 8,
                                'countrycodes': 'au'})
    req = urllib.request.Request('https://nominatim.openstreetmap.org/search?' + q,
                                 headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def pick(results):
    for r in results:
        g = r.get('geojson') or {}
        if g.get('type') not in ('Polygon', 'MultiPolygon'):
            continue
        if r.get('addresstype') not in LOCALITY:
            continue
        return {'geojson': g, 'osm': f"{r.get('osm_type')}/{r.get('osm_id')}",
                'addresstype': r.get('addresstype'), 'display': r.get('display_name')}
    return None


def polys(g):
    return [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']


def dissolve(geoms):
    """Union by cancelling shared edges. Returns a list of closed rings."""
    seen = defaultdict(int)
    for g in geoms:
        for poly in polys(g):
            for ring in poly:
                pts = [tuple(p) for p in ring]
                for a, b in zip(pts, pts[1:]):
                    if a != b:
                        seen[(a, b) if a < b else (b, a)] += 1
    nxt = defaultdict(list)
    for (a, b), n in seen.items():
        if n == 1:
            nxt[a].append(b); nxt[b].append(a)
    rings, used = [], set()
    for start in list(nxt):
        for first in nxt[start]:
            if (start, first) in used:
                continue
            ring, prev, cur = [start], start, first
            used.add((start, first)); used.add((first, start))
            while cur != start:
                ring.append(cur)
                onward = [p for p in nxt[cur] if (cur, p) not in used]
                if not onward:
                    break
                step = onward[0]
                used.add((cur, step)); used.add((step, cur))
                prev, cur = cur, step
            if cur == start and len(ring) >= 3:
                rings.append(ring + [start])
    return rings


def simplify(ring, tol):
    """Douglas-Peucker, iterative. The ring stays closed."""
    pts = ring[:-1]
    if len(pts) < 5:
        return ring
    # split at the point furthest from the first, so both halves are open lines
    far = max(range(len(pts)), key=lambda i: (pts[i][0]-pts[0][0])**2 + (pts[i][1]-pts[0][1])**2)
    def line(seg):
        keep = [False] * len(seg); keep[0] = keep[-1] = True
        stack = [(0, len(seg) - 1)]
        while stack:
            a, b = stack.pop()
            (x1, y1), (x2, y2) = seg[a], seg[b]
            dx, dy = x2 - x1, y2 - y1
            norm = math.hypot(dx, dy) or 1e-12
            best, at = 0, None
            for i in range(a + 1, b):
                d = abs(dy * (seg[i][0] - x1) - dx * (seg[i][1] - y1)) / norm
                if d > best:
                    best, at = d, i
            if at is not None and best > tol:
                keep[at] = True; stack += [(a, at), (at, b)]
        return [p for p, k in zip(seg, keep) if k]
    out = line(pts[:far + 1])[:-1] + line(pts[far:] + [pts[0]])
    return out if len(out) >= 4 else ring


def area(ring):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:])) / 2


def assemble(rings):
    """Rings -> MultiPolygon coordinates: big rings are shells, a ring inside one is its hole."""
    def inside(pt, ring):
        x, y = pt; hit = False
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                hit = not hit
        return hit
    rings = sorted(rings, key=lambda r: -abs(area(r)))
    shells = []
    for r in rings:
        home = next((s for s in shells if inside(r[0], s[0])), None)
        (home.append(r) if home else shells.append([r]))
    return shells


def rounded(ring):
    out = []
    for x, y in ring:
        p = [round(x, 5), round(y, 5)]
        if not out or out[-1] != p:
            out.append(p)
    if out[0] != out[-1]:
        out.append(out[0])
    return out


def main():
    suburbs, geelong = vocab()
    cache = {}
    if os.path.exists(CACHE) and '--refetch' not in sys.argv:
        cache = json.load(open(CACHE))
    for n in suburbs:
        if n in cache:
            continue
        try:
            cache[n] = pick(ask(n))
        except Exception as e:                       # one town failing is not the run failing
            print(f'  {n}: request failed — {e}'); continue
        json.dump(cache, open(CACHE, 'w'))
        time.sleep(1.1)

    towns = defaultdict(list)                         # the town a reader sees -> its geometries
    missing = []
    for n in suburbs:
        hit = cache.get(n)
        if not hit:
            missing.append(n); continue
        towns['Geelong' if n in geelong else n].append((n, hit))

    feats = []
    for town in sorted(towns):
        members = towns[town]
        rings = dissolve([h['geojson'] for _, h in members])
        rings = [rounded(simplify(r, TOLERANCE)) for r in rings]
        rings = [r for r in rings if len(r) >= 4]
        coords = assemble(rings)
        feats.append({'type': 'Feature',
                      'properties': {'name': town, 'made_of': [n for n, _ in members],
                                     'osm': [h['osm'] for _, h in members]},
                      'geometry': {'type': 'MultiPolygon', 'coordinates': coords}})
        print(f'  {town:22} {len(members):2} boundary  {len(coords):2} shape  '
              f'{sum(len(r) for p in coords for r in p):5} points')

    json.dump({'type': 'FeatureCollection',
               'source': 'OpenStreetMap contributors, ODbL — locality boundaries via Nominatim',
               'features': feats}, open(OUT, 'w'), separators=(',', ':'))
    print(f'\n{len(feats)} towns -> {os.path.relpath(OUT, ROOT)}  ({os.path.getsize(OUT)//1024} KB)')
    if missing:
        print('NO LOCALITY BOUNDARY IN OPENSTREETMAP, so no outline: ' + ', '.join(missing))


if __name__ == '__main__':
    main()
