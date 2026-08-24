#!/usr/bin/env python3
"""Propose a kind and a set of offers for every place.

    python3 scripts/classify_places.py           # the proposal, writes nothing
    python3 scripts/classify_places.py --write   # apply it

`kind` is what the place is — one value. `offers` is what you can do there —
any number. See supabase/PLACES_TAXONOMY.sql for why they are separate.

Two rules keep this from inventing things:

  * A kind is read off the place's own name, or off the word the music
    spreadsheet used. Where neither says anything, the kind is left null and
    the row is listed as needing a human. Null is a question; a wrong kind is
    an answer nobody checked.
  * An offer needs evidence. `live-music` comes from the row having been seeded
    from a music-venue spreadsheet — that sheet is a list of places that put on
    music, so membership is the evidence. `food`/`drinks` follow from being a
    licensed venue. Nothing else is guessed: no toilets, no parking, no
    accessibility claims, because nobody has checked those and a wrong one
    sends someone to a place that cannot take them.
"""
import os, re, sys, json, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent

# the music sheet's word -> our kind
FROM_LEGACY = {
  'hotel':'pub', 'pub':'pub', 'bar':'bar', 'piano bar':'bar',
  'winery':'winery', 'brewery':'brewery', 'cidery':'cidery', 'distillery':'distillery',
  'showground':'showground', 'performing arts centre':'theatre',
  'live music venue':'hall', 'entertainment venue':'hall', 'council offices':'civic',
}
# Read off the place's own name. FIRST MATCH WINS, so the order is the rule:
# the specific noun a name ends on beats the geography it happens to mention.
# "Bells Beach Brewing" is a brewery and "Fishermans Beach Reserve" is a
# reserve — both were filed under `beach` until brewery and reserve moved up.
FROM_NAME = [
  (r'\bsurf life saving club\b', 'surf-club'),
  (r'\bplayground\b',            'playground'),
  (r'\bshowgrounds?\b',          'showground'),
  (r'\bbowls club\b',            'sports-ground'),
  (r'brew(ing|house|ery)',        'brewery'),
  (r'\breserve\b',               'reserve'),
  (r'\bbeach\b',                 'beach'),
  (r'\bpier\b',                  'pier'),
  (r'\bforeshore\b|\bcommon\b|elephant walk', 'foreshore'),
  (r'\bpark\b',                  'park'),
  (r'\bcenotaph\b|\bmemorial\b(?! reserve)', 'memorial'),
  (r'\bcarpark\b',               'carpark'),
  (r'\bstreet\b',                'street'),
  (r'\bschool\b',                'school'),
  (r'\blibrary\b',               'library'),
  (r'\bmuseum\b',                'museum'),
  (r'art space|\bgallery\b',     'gallery'),
  (r'\btheatre\b|playhouse',     'theatre'),
  (r'community (house|hub|centre|precinct)', 'community-centre'),
  (r'\bhall\b',                  'hall'),
  (r'\boffices?\b',              'civic'),
  (r'\bwines?\b|\bestate\b',     'winery'),
  (r'\bhotel\b|\btavern\b|\binn\b|\bpub\b', 'pub'),
  (r'\bbar\b',                   'bar'),
  (r'\bcafe\b|café',        'cafe'),
]
# a handful the patterns cannot reach, each because the name says nothing
BY_HAND = {
  'Mantra Lorne':          ('accommodation', 'a resort; it hosts dinners and shows'),
  'The Sands Torquay':     ('accommodation', 'a golf resort with function rooms'),
  'Common Ground Project': ('farm',          'a working market-garden farm'),
  'Bird Rock':             ('bar',           'a bar in Jan Juc, not the surf break of the same name'),
  'Bloom':                 (None,            'nothing on file but a name and a suburb'),
  'Gateway Hotel':         ('pub',           'a Corio pub'),
  'The Mac':               (None,            'unresolved'),
  'Princess Park Playground': ('playground', 'the sheet said Showground; it is a playground'),
  'Workers Club Geelong':  ('bar',           'a bar that puts on bands, not a hall'),
}
LICENSED = {'pub','bar','brewery','winery','distillery','cidery'}

def kind_for(place):
    name = place['name']
    if name in BY_HAND:
        k, why = BY_HAND[name]
        return k, f'by hand — {why}'
    legacy = (place.get('kind_legacy') or place.get('kind') or '').strip().lower()
    if legacy in FROM_LEGACY:
        return FROM_LEGACY[legacy], f'the spreadsheet called it "{legacy}"'
    for pat, kind in FROM_NAME:
        if re.search(pat, name, re.I):
            return kind, f'its name says so (/{pat}/)'
    return None, 'nothing in the name or the sheet says what it is'

def offers_for(place, kind):
    out, why = [], []
    note = place.get('source_note') or ''
    if 'music venue spreadsheet' in note:
        out.append('live-music'); why.append('seeded from the music-venue spreadsheet')
    if kind in LICENSED:
        out += ['food','drinks']; why.append(f'a {kind} serves both')
    elif kind == 'cafe':
        out += ['food','coffee']; why.append('a cafe serves both')
    if place.get('ticketing_url'):
        out.append('tickets'); why.append('it has a ticketing URL on file')
    return sorted(set(out)), '; '.join(why)

def load_env():
    f = ROOT/'.env'
    if f.exists():
        for line in f.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

def req(method, path, body=None):
    r = urllib.request.Request(URL+path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    r.add_header('apikey', KEY); r.add_header('Authorization', 'Bearer '+KEY)
    r.add_header('Content-Type', 'application/json'); r.add_header('Prefer', 'return=representation')
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read(); return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}\n{e.read().decode()[:400]}")

def main():
    load_env()
    global URL, KEY
    URL = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    KEY = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not URL or not KEY:
        sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY (in the environment or .env).")

    table = 'places'
    try:
        req('GET', '/rest/v1/places?select=id&limit=1')
    except SystemExit:
        table = 'venues'
        print("note: still reading `venues` — PLACES_TAXONOMY.sql has not been run,")
        print("      so this is a proposal only and --write will refuse.\n")

    rows = req('GET', f'/rest/v1/{table}?select=*&order=name')
    props, unknown = [], []
    by_kind = {}
    for p in rows:
        k, why = kind_for(p)
        offers, owhy = offers_for(p, k)
        props.append((p, k, why, offers, owhy))
        (by_kind.setdefault(k or '(none)', [])).append(p['name'])
        if not k: unknown.append((p, why))

    for k in sorted(by_kind):
        print(f"{k:<18} {len(by_kind[k]):>2}  {', '.join(sorted(by_kind[k]))}")
    print(f"\n{len(rows)} places, {len(by_kind)-(1 if '(none)' in by_kind else 0)} kinds used, "
          f"{len(unknown)} left for a human.")
    withoffers = [p for p in props if p[3]]
    print(f"{len(withoffers)} carry at least one offer; the rest stay empty rather than guess.")

    if '--write' not in sys.argv:
        print("\nNothing written. Add --write to apply.")
        return
    if table != 'places':
        sys.exit("Run supabase/PLACES_TAXONOMY.sql first — there is nowhere to write kind or offers.")
    for p, k, why, offers, owhy in props:
        req('PATCH', f"/rest/v1/places?id=eq.{p['id']}", {'kind': k, 'offers': offers})
    print(f"{len(props)} places classified.")

if __name__ == '__main__':
    main()
