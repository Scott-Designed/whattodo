#!/usr/bin/env python3
"""Give every listing its real types, now that a listing can have more than one.

    python3 scripts/retype.py           # what would change, writes nothing
    python3 scripts/retype.py --write   # apply it
    python3 scripts/retype.py --check   # exit 1 if anything is still pending

TYPES_MULTI.sql renamed the obvious things — surf→surfing, bike track→mountain
biking, camping→camping ground, park+playground→parks & playgrounds — because a
rename is not a decision anyone needs to review. This file is the decisions.

Every row below was read one at a time. A pattern matcher would have filed the
four Wadawurrung Cultural Education Sessions as gigs, because that is what the
scraper called them and they happen at a venue on a date; they are guided
natural-history walks. It would have filed Blackman's Brewery as a cafe, which
is what the seed spreadsheet called it. There is no rule that gets those right,
so there is no rule here — only a list, and a person who read it.

What is NOT here keeps the single type the migration gave it. 75 gigs are gigs.
21 beaches are beaches. Only the rows that change are listed.

Three judgement calls worth arguing with, all visible in the output:

  * **Whale watching is not a night activity.** Both rows were typed `night`,
    which also made their daypart wrong. They are `nature` now and `night` is
    gone from them. Nothing else loses `night`.
  * **`brewery` was added to the vocabulary for this** (26 Aug 2026), because
    filing Blackman's as a cafe or a bar loses the reason anyone goes. The
    cider house and the distillery are still `bar` plus `produce`: they are the
    same shape of thing, but calling either a brewery would be wrong, and
    `place_kinds` already has `cidery` and `distillery` if those are wanted as
    types too.
  * **Two `festival` rows are not festivals.** Christmas Day Buffet Lunch and
    Coastal End of Year Social, both at Mantra Lorne. They are `restaurant` and
    `community`.

The first type in each list is the primary — the word the row prints and the
icon it draws. Order matters for that and nothing else.
"""
import os, sys, json, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ══ the decisions ═══════════════════════════════════════════════════════
# key -> types, first one is the primary. Grouped by what the row was.

RETYPE = {

# ── sport-event, deleted: every one becomes the sport it actually is ─────
'e56': ['surfing'],                      # Bells Beach Junior
'e57': ['surfing'],                      # Bioglan Bells Beach Longboard Classic
'e3':  ['surfing'],                      # Rip Curl Pro Bells Beach
'e74': ['surfing'],                      # Surf Coast Classic – Men
'e75': ['surfing'],                      # Surf Coast Classic – Women
'e79': ['surfing', 'festival'],          # The Great Ocean Road Womens Surf Fest
'e84': ['running'],                      # Parkrun
'e86': ['running'],                      # Trebeck Reserve Parkrun
'e36': ['running'],                      # Surf Coast Century
'e89': ['running'],                      # Gather Athletics Shop Run
'e25': ['running', 'festival'],          # Great Ocean Road Running Festival
'e46': ['running', 'night'],             # Afterglow Night Trail Runs
'e9':  ['swimming'],                     # Lorne Pier to Pub Swim
'e64': ['swimming'],                     # Danger Ocean Swim Series
'e72': ['swimming'],                     # Rock2Ramp Ocean Swim
'e34': ['cycling'],                      # Cadel Evans Great Ocean Road Race
'e50': ['cycling'],                      # Amy's Great Ocean Road Gran Fondo
'e66': ['cycling'],                      # Great Ocean & Otway Classic Ride
'e80': ['paddling'],                     # The Impossible Ocean Paddle
# Surf lifesaving carnivals are a swim, a board paddle and a beach sprint.
'e67': ['swimming', 'running'],          # Jim Wall Classic Iron Event
'e82': ['swimming', 'running'],          # Tim Gates Classic
'e85': ['swimming', 'cycling', 'running'],  # Torquay Triathlon Super Sprint

# ── sport, deleted: nine backyard games and four unrelated venues ────────
'a173': ['at-home'],                     # Backyard / Beach Cricket
'a179': ['at-home'],                     # Backyard Badminton
'a178': ['at-home'],                     # Bocce / Pétanque
'a174': ['at-home'],                     # Carpark Cricket
'a177': ['at-home'],                     # Fly a Kite
'a175': ['at-home'],                     # Frisbee
'a176': ['at-home'],                     # Frisbee Golf to Natural Targets
'a180': ['at-home'],                     # Hacky Sack / Juggling
'a172': ['at-home'],                     # Kick of the Footy
'a286': ['golf'],                        # Bellarine Adventure Golf
'a287': ['rock climbing', 'nature'],     # You Yangs Rock Climbing
'a34':  ['parks & playgrounds'],         # Jumpz Anglesea
'a133': ['farm life'],                   # Spring Creek Horse Rides – Bellbrae

# ── cafe: four of the twenty-one were cafes ──────────────────────────────
'a28':  ['cafe'],                        # Swell Café
'a29':  ['cafe'],                        # Pond Café
'a30':  ['cafe'],                        # Mavis Mavis
'a291': ['cafe'],                        # Gather
'a168': ['cafe'],                        # The Fives
'a31':  ['bakery', 'cafe'],              # Maple Bakery & Café
'a292': ['restaurant'],                  # Sora
'a253': ['winery'],                      # Scotchmans Hill Winery
'a256': ['winery'],                      # Leura Park Estate
'a250': ['winery', 'restaurant'],        # Jack Rabbit Vineyard
'a251': ['winery', 'restaurant'],        # Oakdene Vineyards – Upside Down House
'a254': ['winery', 'restaurant'],        # Terindah Estate
'a255': ['winery', 'restaurant'],        # Basils Farm – Swan Bay
'a32':  ['brewery'],                     # Blackman's Brewery
# A cidery and a distillery are the same shape of thing — you drink where it is
# made — but calling either one a brewery would be wrong. `bar` plus `produce`
# says both true things until the vocabulary has their own words.
'a252': ['bar', 'produce'],              # Flying Brick Cider House
'a257': ['bar', 'produce'],              # The Whiskery – Bellarine Distillery
'a258': ['produce'],                     # Bellarine Taste Trail
'a260': ['produce'],                     # Lard Ass Butter
'a36':  ['produce'],                     # Great Ocean Road Chocolaterie
'a35':  ['produce', 'farm life'],        # Surf Coast Strawberry Fields
'a259': ['farm life', 'produce'],        # Common Ground Project – Freshwater Creek

# ── cultural: narrowed to indigenous, the rest redistribute ──────────────
'a152': ['cultural'],                    # Narana / Wathaurong Booln Booln
'a154': ['cultural'],                    # Wadawurrung Country
'a153': ['cultural', 'walk'],            # Point Addis Koorie Cultural Walk
'a156': ['cultural', 'walk'],            # Split Point Wathaurung Discovery Trail
'a155': ['cultural', 'nature'],          # You Yangs – Wurdi Youang
'a271': ['art gallery'],                 # Geelong Arts Centre
'a272': ['theatre'],                     # The Palais Geelong
'a169': ['art gallery', 'arts'],         # Ashmore Arts
'a269': ['art gallery', 'arts'],         # Qdos Arts – Lorne
'e69':  ['arts', 'art gallery'],         # 'Ocean Deep' exhibition
'e148': ['arts', 'art gallery'],         # Linda Judge Exhibition at Hoop Gallery
'e54':  ['arts'],                        # Art of the Minds
'e63':  ['comedy'],                      # Comedy Night featuring Dave O'Neil
'e59':  ['music', 'community'],            # Carols by the Barwon
'e47':  ['festival', 'community'],       # Aireys Inlet Fair
'e51':  ['festival', 'nature', 'arts'],  # Angair Wildflower & Arts Show

# ── festival: keeps festival, gains what it is a festival OF ─────────────
'e27': ['festival', 'surfing', 'cinema'],   # Bells Beach Surf Film Festival
'e29': ['festival', 'cinema'],              # Geelong Pride Film Festival
'e30': ['festival', 'nature', 'arts'],      # ANGAIR Wildflower & Art Weekend
'e10': ['festival', 'music'],                 # Anglesea Music Festival
'e41': ['festival', 'music'],                 # National Celtic Folk Festival
'e33': ['festival', 'music'],                 # Queenscliff Music Festival
'e42': ['festival', 'arts'],                # Lorne Sculpture Biennale
'e7':  ['festival', 'arts'],                # Surf Coast Arts Trail
'e37': ['festival', 'produce'],             # Portarlington Mussel Festival
'e12': ['festival', 'walk'],                # Surf Coast Walk Festival
'e28': ['festival', 'community'],           # Deans Marsh Festival
'e31': ['festival', 'community'],           # One Planet Festival
'e35': ['festival', 'community'],           # Pako Festa
'e61': ['restaurant'],                      # Christmas Day Buffet Lunch — not a festival
'e62': ['community'],                       # Coastal End of Year Social — not a festival

# ── shop ────────────────────────────────────────────────────────────────
'a290': ['produce'],                     # Bellarine Wholefoods
'a171': ['produce', 'farm life'],        # Bird Rock Farm

# ── night: keeps night, gains what it is a night thing ABOUT ─────────────
'a86':  ['night', 'nature'],             # Milky Way Stargazing
'a87':  ['night', 'nature'],             # Aurora Australis Chase
'a104': ['night', 'nature'],             # Meteor Shower Watching
'a105': ['night', 'nature'],             # ISS (Space Station) Spotting
'a106': ['night', 'nature'],             # Planet Watching
'a95':  ['night', 'nature'],             # Moonrise Watch
'a93':  ['night', 'nature'],             # Sunset at Point Danger / Yellow Bluff
'a94':  ['night', 'nature'],             # Sunset at Split Point Lighthouse
'a164': ['night', 'nature'],             # Frog ID – Listen for Frogs at Night
'e18':  ['night', 'nature'],             # Eta Aquarid Meteor Shower
'a88':  ['night', 'nature', 'beach'],    # Bioluminescence / Sea Sparkle Watch
'a89':  ['night', 'walk', 'nature'],     # Glow Worm Walk – Sheoak / Allenvale
'e11':  ['night', 'beach'],              # Full Moon Bonfire
'a96':  ['night', 'water'],              # Night Fishing – Jan Juc Creek / Rocks
'a97':  ['night', 'water'],              # Night Fishing – Torquay Pier
'a102': ['night', 'at-home'],            # Backyard Bonfire / Fire Pit Night
'a103': ['night', 'at-home', 'cinema'],  # Outdoor Movie Night at Home
'a100': ['night', 'pub'],                # Pub Trivia Night – Surf Coast
'a273': ['music', 'night'],                # The Blues Train – Bellarine Railway
'a91':  ['nature'],                      # Whale Watching – Point Addis — daytime
'a92':  ['nature'],                      # Whale Watching – Teddy's Lookout — daytime

# ── gig: the ~28 that were never music ──────────────────────────────────
'e103': ['party'],                       # 2000s + 2010s Party
'e136': ['party'],                       # Classic Club Anthems Party
'e104': ['party', 'music'],                # AFL Grand Final After-party
'e140': ['party', 'music'],                # Grand Final Afterparty ft. MAD.DAY
'e130': ['reading'],                     # August Quiet Club at The Sewing Collective
'e131': ['reading'],                     # Quiet Club
'e133': ['reading'],                     # Quiet Club
'e134': ['reading'],                     # Quiet Club
'e135': ['reading'],                     # Quiet Club
'e132': ['reading'],                     # Book Club – Sense & Sensibility
'e100': ['comedy'],                      # Jimeoin
'e119': ['comedy'],                      # Laughs & Lagers Comedy Night
'e125': ['cinema'],                      # Environmental Film Series – October 23
'e129': ['cinema'],                      # Environmental Film Series – October 9
'e126': ['cinema'],                      # Re-screening | Environmental Film Series
'e127': ['arts', 'cinema', 'art gallery'],  # Spring Creek Valley Exhibition & Screening
# Guided natural-history tours led by Ash Skinner, not performances.
'e112': ['cultural', 'nature'],          # Wadawurrung Session – Lake Lorne
'e115': ['cultural', 'nature'],          # Wadawurrung Session – The Bluff
'e117': ['cultural', 'nature'],          # Wadawurrung Session – Lower Bluff
'e118': ['cultural', 'nature'],          # Wadawurrung Session – The Narrows
'e113': ['paddling', 'nature'],          # Mangrove Canoe Adventure – 12:30pm
'e114': ['paddling', 'nature'],          # Mangrove Canoe Adventure – 10am
'e116': ['nature', 'walk'],              # Orchids in the Park – Barwon Heads
'e128': ['community'],                   # SCEG AGM 2026 at Patagonia Torquay
'e120': ['festival', 'bar'],             # Point Break – Brewery Invitational
'e95':  ['music', 'festival'],             # DRENCHER FESTIVAL 2026
'e99':  ['music', 'festival'],             # Stars & Bars Festival Geelong
'e87':  ['music', 'restaurant'],           # Waterloo – Abba Tribute Dinner & Show

# ── community: keeps community, gains what it actually is ───────────────
'a270': ['community', 'arts'],           # Anglesea Art House
'e55':  ['community', 'arts'],           # Art of the Minds – HER Story
'e44':  ['community', 'pub'],            # Birdy Bingo
'e76':  ['community', 'walk'],           # Surf Coast Trek
'a289': ['community', 'swimming', 'beach'],  # Nippers – Junior Surf Life Saving
'a19':  ['community', 'reading'],        # Torquay Library – Kids Programs
'a288': ['community', 'reading'],        # Geelong Library & Heritage Centre
'e45':  ['community', 'farm life'],      # A Day on The Farm
'e43':  ['community', 'farm life'],      # Bellarine Agricultural Show

# ── nature: the citizen-science and do-it-anywhere half ─────────────────
'a193': ['nature', 'at-home'],           # Cloud Watching
'a191': ['nature', 'at-home'],           # Make a Nature Mandala
'a189': ['nature', 'at-home'],           # Nature Scavenger Hunt
'a194': ['nature', 'at-home'],           # Photography Challenge
'a192': ['nature', 'at-home'],           # Press Flowers and Leaves
'a190': ['nature', 'walk', 'at-home'],   # Nature Journal Walk
'a195': ['nature', 'arts', 'at-home'],   # Sketch or Draw Outside
'a14':  ['nature', 'golf'],              # Anglesea Golf Course (Kangaroos!)
'a146': ['nature', 'walk'],              # Kennett River Koala Walk
'a148': ['nature', 'walk'],              # Ocean Grove Nature Reserve
'a163': ['nature', 'water'],             # Reef Life Survey – Point Addis
'a165': ['nature', 'water'],             # Redmap – Report Unusual Marine Species

# ── water: a canoe hire is paddling, a dive is swimming ─────────────────
'a141': ['paddling'],                    # Anglesea Paddle Boat & Canoe Hire
'a33':  ['paddling'],                    # Anglesea Paddleboards & Canoe Hire
'a144': ['paddling'],                    # Barwon River – Self-Guided Kayak or SUP
'a142': ['paddling'],                    # Kayaking the Anglesea River
'a143': ['paddling'],                    # Paddle Life – Barwon River
'a145': ['paddling', 'nature'],          # Lake Elizabeth Platypus Canoe Tour
'a277': ['swimming', 'nature'],          # Eagle Rock Marine Sanctuary Snorkelling
'a275': ['swimming', 'nature'],          # Scubabo Dive – Queenscliff Shipwrecks
'a274': ['swimming', 'nature'],          # Sea All Dolphin Swims – Queenscliff
'a183': ['at-home', 'water'],            # Build and Race Boats
'a182': ['at-home', 'water'],            # Stone Skimming

# ── odds and ends ───────────────────────────────────────────────────────
'a196': ['walk', 'beach'],               # Sunrise Beach Walk
'a197': ['walk', 'at-home'],             # Neighbourhood Walk – Spot Something New
'e14':  ['market', 'night'],             # Night Markets (Geelong After Dark)
'e17':  ['workshop', 'arts'],            # Ceramics Workshop
'e73':  ['workshop', 'festival', 'arts'],   # Sketch and Scribe Festival
'e16':  ['workshop', 'reading', 'community'],  # Torquay Library Activities
}

# ══ plumbing ════════════════════════════════════════════════════════════

def load_env():
    p = ROOT / '.env'
    if p.exists():
        for line in p.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

def req(method, path, body=None):
    r = urllib.request.Request(URL+path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    r.add_header('apikey', KEY); r.add_header('Authorization', 'Bearer '+KEY)
    r.add_header('Content-Type', 'application/json')
    r.add_header('User-Agent', 'whattodo-janjuc')
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}\n{e.read().decode()[:400]}")

def split_key(k):
    """'a123' -> ('activities', 123). Ids collide across the two tables, which
    is the bug sync.py reject still has; the view's own key is the fix."""
    return ('activities' if k[0] == 'a' else 'events'), int(k[1:])

def main():
    args = set(sys.argv[1:])
    load_env()
    global URL, KEY
    URL = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    KEY = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not URL or not KEY:
        sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY (in the environment or .env).")

    vocab = {t['name'] for t in req('GET', '/rest/v1/types?select=name')}
    if 'types' not in (req('GET', '/rest/v1/listings?select=types&limit=1') or [{}])[0]:
        sys.exit("The listings view has no `types` column — run supabase/TYPES_MULTI.sql first.")

    rows = {r['key']: r for r in
            req('GET', '/rest/v1/listings?select=key,name,types&limit=2000')}

    # A typo here would write a type the check constraint rejects, and the
    # first the caller would know is a 400 from row 90 of 190.
    bad = [(k, t) for k, ts in RETYPE.items() for t in ts if t not in vocab]
    missing = [k for k in RETYPE if k not in rows]
    if bad or missing:
        for k, t in bad:     print(f"  {k}: '{t}' is not one of the {len(vocab)} types")
        for k in missing:    print(f"  {k}: no such listing")
        sys.exit(f"\n{len(bad)+len(missing)} problems — nothing written.")

    changes = [(k, rows[k], RETYPE[k]) for k in RETYPE
               if rows[k]['types'] != RETYPE[k]]

    by_old = {}
    for k, row, new in changes:
        by_old.setdefault((row['types'] or ['—'])[0], []).append((k, row, new))
    for old in sorted(by_old, key=lambda o: -len(by_old[o])):
        group = by_old[old]
        print(f"\n── {old} ({len(group)}) " + "─"*max(0, 52-len(old)))
        for k, row, new in sorted(group, key=lambda x: x[1]['name']):
            print(f"  {k:5} {row['name'][:48]:48} → {' · '.join(new)}")

    print(f"\n{len(changes)} of {len(rows)} listings would change.")
    multi = [c for c in changes if len(c[2]) > 1]
    print(f"{len(multi)} of those end up with more than one type.")
    left = sorted({t for r in rows.values() for t in (r['types'] or [])
                   if t in ('sport', 'sport-event')} -
                  {t for k in RETYPE for t in RETYPE[k]})
    still = [k for k, r in rows.items()
             if set(r['types'] or []) & {'sport', 'sport-event'} and k not in RETYPE]
    if still:
        print(f"\n{len(still)} rows still on a retired type and not listed here: "
              + ', '.join(sorted(still)))

    if '--check' in args:
        sys.exit(1 if changes else 0)
    if '--write' not in args:
        print("\nNothing written. Read the list, then run again with --write.")
        return

    for k, row, new in changes:
        table, idn = split_key(k)
        req('PATCH', f'/rest/v1/{table}?id=eq.{idn}', {'types': new})
    print(f"\nWrote {len(changes)}.")
    print("`sport` and `sport-event` can now be deleted from the types table.")

if __name__ == '__main__':
    main()
