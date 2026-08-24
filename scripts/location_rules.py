#!/usr/bin/env python3
"""Take the slash out of a location.

A slash was doing four different jobs in this column, and only one of them was
a location:

  1. A single place with its region bolted on  — "Waurn Ponds / Geelong".
     The region is redundant; the specific locality is the answer.
  2. Genuinely several places — "Jan Juc / Lorne / Surf Coast beaches".
     A list of places is not a place. Name the area that covers them, or say
     plainly that it is several.
  3. Home, with a hint attached — "Home / anywhere with a hose".
     The hint belongs in the description, not in Where.
  4. A street number — "2/80 Murradoc Road, Drysdale". Not a separator at all,
     and the reason this file is a curated list rather than a regex.

Two shapes are deliberately kept, because they are one place and read as one:
a route ("Jan Juc -> Torquay") and a named area ("Surf Coast reefs & beaches").

Where a row is pinned, the suburb was checked by reverse-geocoding the pin
rather than picking a half. That overruled the obvious guess three times, so
rows where OpenStreetMap disagrees with both halves are marked CHECK and left
for a person.

    python3 scripts/location_rules.py            # dry run
    python3 scripts/location_rules.py --write    # apply
"""
import sys, json, urllib.request, io, os

REF = 'xpnsrtylcqjcoqitskwy'

# id -> (new location, why).  None means leave it alone.
RULES = {
    # ── one place; the slash carried a redundant region ──
    2:   ('Bells Beach',        'region dropped; pin reverse-geocodes to Bells Beach'),
    52:  ('Waurn Ponds',        'region dropped; pin agrees'),
    56:  ('Leopold',            'region dropped; pin agrees'),
    82:  ('Skenes Creek',       'region dropped; pin too remote for OSM to name'),
    157: ('Torquay',            'Cosy Corner is a spot inside Torquay, not a second place'),
    64:  ('Moggs Creek',        'the picnic area has its own locality between the two'),
    22:  ('Jan Juc',            '"surrounds" is not a place'),

    # ── OSM disagrees with the sheet; pin wins, but worth a look ──
    53:  ('Mount Duneed',       'CHECK — named Armstrong Creek Skatepark, pin says Mount Duneed'),
    58:  ('North Geelong',      'CHECK — pin says North Geelong, not Corio'),
    59:  ('Norlane',            'CHECK — pin says Bell Park; name says North Shore'),
    144: ('Barwon Heads',       'CHECK — river runs between both; pin says Barwon Heads'),
    43:  ('Birregurra',         'CHECK — trailhead; pin sits mid-trail at Benwerrin'),
    # 43, 53, 58 and 144 stay as they are by decision, not oversight: naming a
    # place after one suburb while its pin sits in another is a judgement about
    # which of the two facts is wrong, and nobody has made it yet.
    #
    # 59 is gone from this list because it was a different bug. It read "Djila
    # Tjarra Skatepark (North Shore / Norlane)", but Djila Tjarri is in Torquay
    # on Merrijig Drive — the row had borrowed a name from a park 33 km away.
    # Its own description, "two skateparks linked together, old and new", is
    # Norlane exactly. So a59 became Norlane Skatepark (North Shore) and a51,
    # filed as "Torquay North Skatepark", took the name it always had.

    # ── genuinely several places ──
    95:  ('Surf Coast headlands',   'two beaches -> the area that holds them'),
    128: ('Several Surf Coast beaches', 'two beaches'),
    86:  ('Several Surf Coast beaches', 'three beaches'),
    104: ('Several Surf Coast beaches', 'three beaches'),
    87:  ('Several Surf Coast beaches', 'three beaches'),
    88:  ('Surf Coast beaches',         'three named, all on this coast'),
    289: ('Surf Coast surf clubs',      'runs at four clubs'),
    100: ('Several Surf Coast pubs',    'a roving trivia night'),

    # ── home, with the hint stripped back out ──
    12:  ('Home', 'the hint belongs in the description'),
    102: ('Home', 'the hint belongs in the description'),
    103: ('Home', 'the hint belongs in the description'),
    179: ('Home', 'the hint belongs in the description'),
    184: ('Home', 'the hint belongs in the description'),
    185: ('Home', 'the hint belongs in the description'),
    186: ('Home', 'the hint belongs in the description'),
    201: ('Home', 'the hint belongs in the description'),
    187: ('Your neighbourhood', 'the game is the street, not the house'),
    105: ('Anywhere clear',  'needs a clear sky, not a suburb'),
    106: ('Anywhere clear',  'needs a clear sky, not a suburb'),

    # ── not a separator ──
    290: (None, 'KEEP — "2/80" is a street number'),
}

def env():
    d={}
    with io.open(os.path.join(os.path.dirname(__file__),'..','.env')) as f:
        for l in f:
            if '=' in l and not l.startswith('#'):
                k,v=l.strip().split('=',1); d[k]=v.strip().strip('"').strip("'")
    return d

def q(sql):
    tok=env()['SUPABASE_ACCESS_TOKEN']
    r=urllib.request.Request(f'https://api.supabase.com/v1/projects/{REF}/database/query',
        data=json.dumps({'query':sql}).encode(),
        headers={'Authorization':'Bearer '+tok,'Content-Type':'application/json',
                 'User-Agent':'whattodo-janjuc/1.0 (location rules)'}, method='POST')
    return json.load(urllib.request.urlopen(r,timeout=60))

def esc(v):
    return "'" + v.replace("'", "''") + "'"

def main():
    write = '--write' in sys.argv
    include_check = '--include-check' in sys.argv
    rows = q("select id,name,location from activities where location like '%/%' order by id")
    unhandled = [r for r in rows if r['id'] not in RULES]
    changes, held = [], []
    print(f"{len(rows)} activities have a slash in their location\n")
    for r in rows:
        rule = RULES.get(r['id'])
        if not rule:
            continue
        new, why = rule
        if new is None or new == r['location']:
            print(f"  a{r['id']:<4} keep   {r['location']:<42} {why}")
            continue
        check = why.startswith('CHECK')
        print(f"  a{r['id']:<4} {'CHECK ' if check else '      '} {r['location']:<42} -> {new}")
        print(f"        {'':<49}{why}")
        (held if check and not include_check else changes).append((r['id'], new))
    if unhandled:
        print(f"\n  {len(unhandled)} not covered by a rule:")
        for r in unhandled:
            print(f"     a{r['id']} {r['location']}")
    print(f"\n{len(changes)} would change." + (f"  {len(held)} held back for a person "
          f"(--include-check to apply them too)." if held else ""))
    if not write:
        print("Nothing written. Add --write to apply.")
        return
    for i, new in changes:
        q(f"update activities set location={esc(new)} where id={i}")
    print(f"{len(changes)} updated.")

if __name__ == '__main__':
    main()
