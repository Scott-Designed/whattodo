# Landscape pass — walk · nature · night

Worked 31 Aug 2026. Repo cloned fresh from GitHub. `nearby.py --refresh` was run
once as instructed and **failed**: every Overpass endpoint refused (main endpoint
reset the connection, kumi and private.coffee both 403 through the egress proxy).
The committed `scripts/osm_cache.json` is stamped `2026-08-31 12:50` and holds
2796 POIs across all six kinds, so the sweep ran off that cache and nothing was
lost. `api.openstreetmap.org` is also blocked from this container, so no raw OSM
tag queries were possible — only Nominatim, which answered normally throughout.

---

## HALF ONE — pinning what was already here

54 rows carrying `walk`, `nature` or `night` had no coordinate. Of those, **29
name a real findable place** and 25 genuinely name none ("Anywhere outdoors",
"Home", "Several Surf Coast beaches") and are correctly null.

Result: **23 pinned, 1 better solved by a `place_id` link, 5 left null.**

Every coordinate below was found by asking Nominatim for the **feature by name**,
and every one was reverse-geocoded before acceptance. No `type=administrative`
match was accepted anywhere in this pass.

### Pins to apply

| id | name | lat | lng | Nominatim matched | reverse-geocode |
|---|---|---|---|---|---|
| 4 | Surf Coast Walk – Jan Juc to Torquay | -38.3474775 | 144.3060142 | `natural=beach` "Jan Juc Beach, Jan Juc" | Surf Coast Walk, Jan Juc |
| 222 | Erskine Falls Walk | -38.5071785 | 143.9136205 | `tourism=viewpoint` "Erskine Falls Upper Lookout" (osm_cache) | Lemonade Creek Track, Lorne |
| 223 | Sheoak Falls & Swallow Cave Walk | -38.5547716 | 143.9436494 | `tourism=picnic_site` "Sheoak Picnic Area, Garvey Track" | Nature Loop, Lorne |
| 224 | Kalimna Falls Walk | -38.5547716 | 143.9436494 | `tourism=picnic_site` "Sheoak Picnic Area, Garvey Track" | Nature Loop, Lorne |
| 225 | Teddy's Lookout Walk | -38.5542391 | 143.9789488 | `tourism=viewpoint` "Teddy's Lookout" | Teddy's Lookout Trail, Lorne |
| 226 | Hopetoun Falls Walk | -38.6666475 | 143.5691648 | `highway=unclassified` "Hopetoun Falls Access Road" | Hopetoun Falls Access Road, Beech Forest |
| 227 | Beauchamp Falls Walk | -38.6513900 | 143.6066700 | `tourism=camp_site` "Beauchamp Falls Campround, Beauchamps Falls Walking Track" | Beech Forest (hamlet only — see note) |
| 228 | Triplet Falls Walk | -38.6705824 | 143.4952171 | `amenity=parking` "Triplet Falls, Phillips Track" | Phillips Track, Beech Forest |
| 229 | Melba Gully Rainforest Walk | -38.6980077 | 143.3704556 | `information=board` "Melba Gully National Park, 5 Melba Gully Road" | Madsens Track Nature Walk, Lavers Hill |
| 230 | Maits Rest Rainforest Walk | -38.7558846 | 143.5544606 | `amenity=parking` "Maits Rest" | Maits Rest Rainforest Walk |
| 231 | Otway Redwoods – Aire Valley Reserve | -38.6684405 | 143.5801606 | `tourism=picnic_site` "The Redwoods Picnic Area" (osm_cache) | Aire Valley Road, Beech Forest |
| 232 | Cape Otway Lightstation Walk | -38.8567813 | 143.5118194 | `building` "Cape Otway Lighthouse" | Great Ocean Walk |
| 233 | Point Addis – Ironbark Basin Circuit | -38.39531 | 144.25389 | *no OSM feature* — Point Addis access, see note | Point Addis Road, Bells Beach |
| 234 | Queenscliff Dune Walk | -38.271478 | 144.650101 | walkingmaps.com.au/walk/1664 published start | The Esplanade, Queenscliff |
| 235 | Geelong Waterfront & Bollard Trail | -38.1442761 | 144.3637041 | `leisure=park` "Steampacket Gardens" | Eastern Beach Road, Geelong |
| 236 | Buckley Falls Reserve Loop | -38.1508531 | 144.3068313 | `waterway=waterfall` "Buckley Falls, Geelong" | Buckley Falls Walking Trail, Highton |
| 237 | Cumberland River Trail | -38.5738216 | 143.9488672 | `tourism=camp_site` "Cumberland River Holiday Park" | Cumberland River Trail, Lorne |
| 238 | Point Lonsdale Lighthouse Walk | -38.2920052 | 144.6139189 | `man_made=lighthouse` "Point Lonsdale Lighthouse" | Point Lonsdale Road, Point Lonsdale |
| 239 | Buckley's Cave – Point Lonsdale | -38.2921428 | 144.6136958 | `natural=cave_entrance` "Buckley's Cave" (osm_cache) | Point Lonsdale Road, Point Lonsdale |
| 277 | Eagle Rock Marine Sanctuary Snorkelling | -38.4681990 | 144.1048101 | `tourism=viewpoint` "Eagle Rock Lookout" (osm_cache) | Surf Coast Walk, Aireys Inlet |
| 280 | Swan Bay Birdwatching – Queenscliff | -38.2706333 | 144.6382712 | `railway=halt` "Swan Bay, Bellarine Peninsula Rail Trail" | Bellarine Peninsula Rail Trail, Queenscliff |
| 281 | Lake Connewarre & Breamlea Shorebirds | -38.2868649 | 144.4050986 | `leisure=nature_reserve` "Breamlea Flora and Fauna Reserve" | Breamlea Road, Breamlea |
| 282 | Werribee Open Range Zoo | -37.9227928 | 144.6628586 | `tourism=zoo` "Werribee Open Range Zoo" | Pula Trail, Werribee South |

### Link instead of a pin

| id | name | action |
|---|---|---|
| 273 | The Blues Train – Bellarine Railway | set `place_id = 141` (Queenscliff Railway Station, -38.264327,144.661633). The train departs the station; linking beats a second copy that can drift. |

### Which coordinate each walk actually pins — declared

Per the trailhead rule, these pin the **access**, not the feature, and say so:

- **223 / 224** both pin **Sheoak Picnic Area**, which is what each row's own
  description names as the start ("From the Sheoak Picnic Area…"). Note that
  Nominatim also offers a "Sheoak Falls" information board on the Great Ocean
  Road (-38.5687564,143.9648244) — that is the *other* approach to Sheoak Falls,
  from the coast. It was **not** used, because the rows describe the inland walk.
  Two rows now share one coordinate; that is correct, they share a trailhead.
- **226 Hopetoun Falls** pins the **access road / car park**, ~160 m north of the
  falls, not the falls (-38.6680828,143.5686931) which sit at the bottom of a
  steep staircase.
- **227 Beauchamp Falls** pins the **campground at the top of the walk**. Its
  reverse-geocode returns only `hamlet=Beech Forest` with no road under it — the
  weakest reverse in this batch. The forward match is a named `tourism=camp_site`
  on "Beauchamps Falls Walking Track", so it is a real feature, but flagging it.
- **229 Melba Gully** pins the **day visitor area information board** at 5 Melba
  Gully Road; it reverse-geocodes onto Madsens Track, which is the loop itself.
- **231 Otway Redwoods** pins the **picnic area / parking**, not the grove.
- **232 Cape Otway** pins the **lighthouse building itself**, not the lightstation
  entry gate, which OSM does not name.
- **235 Bollard Trail** pins **Steampacket Gardens** on the central waterfront.
  The trail runs Rippleside→Limeburners Point; this is a mid-trail access point,
  not an end.
- **236 Buckley Falls** pins the **falls / viewing platform** on the Buckley Falls
  Walking Trail, not the Buckley Falls Road car park, which OSM does not name.
- **222 Erskine Falls** pins the **upper lookout** at the top of the steps, beside
  the car park — not the falls at the bottom.
- **277 Eagle Rock** pins the **clifftop lookout on the Surf Coast Walk**, i.e.
  the land access, **not a water entry point**. Anyone using this row to snorkel
  still has to find their own way in.
- **281** pins **Breamlea Flora and Fauna Reserve**, matching the row's stated
  location (Breamlea). The Lake Connewarre Wildlife Reserve centroid was rejected:
  it reverse-geocodes to bare `hamlet=Connewarre` with nothing under it.
- **233 Point Addis – Ironbark Basin Circuit** — **flagged, please check.** The
  circuit's real trailhead is the "Ironbark car park on Point Addis Road", ~500 m
  from the Great Ocean Road turnoff (Bushwalking Victoria and Friends of Eastern
  Otways both describe it that way). **That car park is not a named feature in
  OSM** and `Ironbark Basin` returns nothing from Nominatim, bounded or not. What
  is pinned is the **Point Addis car park access**, which Bushwalking Victoria
  names as the documented *alternative* start for this same circuit, and which
  four sibling rows (3, 91, 153, 163) already share. It is ~1.5 km from the
  intended trailhead. If you can get the Ironbark car park coordinate another
  way, this row should be moved.

### Left null, with reasons

| id | name | why |
|---|---|---|
| 274 | Sea All Dolphin Swims – Queenscliff | Their own site gives "Shop 3, Building 6, **Queenscliff Boat Harbour**". OSM has no such feature. "Queenscliff Marina" resolves to **Queenscliff Yacht Club, Larkin Parade** — a different place ~400 m away. "Wharf Street East" returns a road centreline. Refused all three. |
| 275 | Scubabo Dive – Queenscliff Shipwrecks | Same harbour, same problem. Boat departs Queenscliff Harbour, which OSM does not name. |
| 279 | Cape Otway Koala Drive – Lighthouse Road | It is a **drive**, a linear feature with no single standing point. The only named Nominatim match on Lighthouse Road is the Cape Otway Conservation Ecology Centre, a private business — pinning that would send people to the wrong thing. |
| 287 | You Yangs Rock Climbing | The row names **Gavel Pit Tor** as the climbing site. Neither "Gavel Pit", "Big Rock" nor "Turntable Creek Picnic Area" resolves in Nominatim. The You Yangs Regional Park polygon centroid reverse-geocodes to Rockwell Road, which is a real road but is **not the climbing area**. Places 117/118/119 are You Yangs car parks but they are the mountain-bike ones. |
| 543 | Bellarine Catchment Network | "865 Swan Bay Road, Mannerim" resolves only to a **road centreline at Marcus Hill** — the exact street-query failure the brief warns about. Refused. Should link to **place 82** (Bellarine Catchment Network), but **place 82 itself has no coordinate**, so the link gives no pin until that row is geocoded. |

25 further rows were left null on purpose because they name no place at all:
Aussie Backyard Bird Count, Cloud Watching, Make a Nature Mandala, Nature Journal
Walk, Nature Scavenger Hunt, Photography Challenge, Press Flowers and Leaves,
Sketch or Draw Outside, iNaturalist, eBird & Birdata, Redmap, WhaleFace, Hooded
Plover Spotting, Backyard Bonfire, Outdoor Movie Night at Home, ISS Spotting,
Planet Watching, Meteor Shower Watching, Aurora Australis Chase, Milky Way
Stargazing, Bioluminescence Watch, Moonrise Watch, Neighbourhood Walk, Sunrise
Beach Walk, Frog ID.

### Rejected candidates worth recording

- **`Erskine Falls Road, Lorne`** returned **two segments 4.3 km apart**
  (-38.5207506,143.9330049 at Lorne and -38.5174645,143.8824459 at Benwerrin) —
  the same street-query failure the brief describes. Refused; asked for the
  waterfall by name instead.
- **`865 Swan Bay Road`** — house number ignored, road centreline returned in a
  different suburb (Marcus Hill, not Mannerim). Refused.
- **`Point Addis Road, Bellbrae`** — road centreline. Refused.
- **`Cumberland River, Lorne`** — resolves to the `waterway=river` linear feature,
  whose returned point is arbitrary. Refused; used the holiday park at the
  trailhead instead.
- **`Lake Connewarre Wildlife Reserve`** — reverse-geocodes to bare
  `hamlet=Connewarre`, nothing under it. Refused.
- **`Buckley Falls Park`** centroid (-38.1498795,144.3027787) reverse-geocodes to
  **Rivergum Drive**, a suburban street at the park edge, not the falls. Refused
  in favour of the waterfall feature.
- **`You Yangs Regional Park`** centroid — a 2000 ha polygon. Refused.
- **`Queenscliff Marina`** → Queenscliff Yacht Club. Wrong entity. Refused.

---

## HALF TWO — what was missing

Swept with `nearby.py "<town>" --kinds landscape --radius 6000` (off the cached
Overpass dump) for Lorne, Aireys Inlet, Anglesea, Forrest, Beech Forest, Lavers
Hill, Apollo Bay, Kennett River, Torquay, Ocean Grove, Wye River and Cape Otway.
Then checked by hand against Parks Victoria (site pages **and** their visitor
guide PDFs, which is where the distances and grades actually live), Friends of
Eastern Otways, ANGAIR, Bushwalking Victoria and Visit Great Ocean Road.

**Batch file: `/tmp/landscape_batch.json` — 10 rows, validated clean.**
Primary types: **walk 6 · night 2 · nature 2**. Nine of ten carry a coordinate.

`scripts/sync.py check <file>` **does not exist** — see the note at the end of
this log. Validation was run through `scripts/checkfile.py`, added by this pass,
which calls sync.py's own `check()` against the live vocabulary.

### Rows built

| name | types | location | pinned |
|---|---|---|---|
| Melba Gully Glow Worms | night, nature | Lavers Hill | yes |
| Kennett River Glow-Worm Walk | night, walk | Kennett River | yes |
| The Canyon – Lorne Waterfalls Circuit | walk | Lorne | yes |
| Little Aire Walk | walk | Beech Forest | yes |
| Cape Otway Cemetery Walk | walk | Cape Otway | yes |
| Currawong Falls Circuit | walk | Aireys Inlet | yes |
| Marriners Lookout Walk | walk, night | Apollo Bay | yes |
| Marengo Reefs Marine Sanctuary | nature | Apollo Bay | yes |
| Ocean Acres Nature Reserve | nature, walk | Torquay | yes |
| Station Beach & Rainbow Falls Walk | walk | Cape Otway | **no — see below** |

Every distance and grade is quoted from the land manager's own page or guide.
Nothing was estimated. `km` is null on all ten. **`any-weather` appears on zero
of ten** — the conditions actually used are `new-moon`, `low-wind`, `dry-trails`,
`good-in-rain`, `low-tide`, `calm-sea`, `clear-sky`, `dry-ground`.

### Two deliberate near-misses, argued rather than avoided

- **Melba Gully Glow Worms** sits beside existing row 229, *Melba Gully
  Rainforest Walk*, same place. It is a different activity at a different time of
  day with different conditions (`new-moon`, `daypart: night`), and the database
  already does exactly this: row 225 *Teddy's Lookout Walk* and row 92 *Whale
  Watching – Teddy's Lookout* are one place and two rows. Kept, on that precedent.
- **Kennett River Glow-Worm Walk** sits beside existing row 146, *Kennett River
  Koala Walk (Grey River Road)*, same road. Koalas by day, glow worms after dark,
  and Parks Victoria publishes them as separate named sites. Kept.

If either reads as a duplicate to you, the glow-worm row is the one to drop.

### Rejected, with reasons

- **Marriners Falls, Apollo Bay** — **rejected on safety grounds.** The track has
  been closed for years after landslip; third-party write-ups call it "the
  forbidden waterfall" and there is an active local campaign to reopen it. Parks
  Victoria's own Marriners Day Visitor Area page will not confirm the falls track
  is open. Writing this row would send people down a closed track. Revisit only
  when Parks Victoria says it is open.
- **Castle Rock Lookout, Lorne** — already inside existing row 223, whose own
  source is the Bushwalking Victoria "Swallow Cave, Sheoak Falls and Castle Rock"
  circuit. A separate row would be the same walk twice.
- **Phantom Falls / Henderson Falls / Won Wondah Falls** — all three are features
  *of* The Canyon circuit in Parks Victoria's guide, not separate walks. Covered
  by the one row rather than four.
- **All `natural=peak` results** — Black Hill, Langdale Pike, Mount Saint George,
  Scaw Fell, Cockerill Hill, Hall Hill, Hallett Hill, Madden Hill, Websters Hill,
  Amiets Hill, Crowes Hill, Mount Chapple, Berthon Hill, Lookout Hill, Mount
  Ingoldsby, Scrubby Hill, Tip Hill, Burst My Gall Hill, Crows Nest, Mount
  Meuron, Sugarloaf Hill, Camp Hill, E S Hill, Guerards Hill, Lawrys Hill,
  Payters Hill, Red Hill, Ter Hill, Toms Hill, Barwon Bluff (Mount Colite).
  **Thirty of them.** Not one has a land-manager page describing a walk or a
  lookout. The Cape Otway sweep returned 8 peaks out of 13 results. The brief is
  right: `natural=peak` is close to pure noise in this region.
- **`tourism=attraction` grab bag** — "Bimbi Park Horse Trail Rides" (Cape Otway)
  is the horse-riding business the brief warned about, "Apollo Bay Aviation" is a
  charter operator, "Horse and Cart" (Anglesea) and "Westies Seat" are street
  furniture. All rejected. "Wildlife Wonders" (Apollo Bay) is a real paid wildlife
  attraction and a fair future candidate, but it is a ticketed business rather
  than landscape, so it belongs to another pass.
- **Marriners Day Visitor Area** — open and real, but Parks Victoria's page gives
  no walk, no distance, no facilities. There is nothing to write a description
  from that would not be padding. Left for a pass that can get better material.
- **Lonsdale Lakes Wildlife Reserve**, **Aireys Inlet Bushland Reserve**,
  **Anglesea Bushland Reserve**, **Edna Bowman Nature Conservation Reserve**,
  **Barham Paradise Scenic Reserve** — all genuine reserves, none with a
  first-party page carrying enough to write two honest sentences. Named here so
  the next pass does not spend the hour again.
- **Bunjil Mirr Lookout / Anglesea Lookout / Cape Patton Lookout / Carisbrook
  Falls / Urquharts Falls / Jebbs Pool / Splitter Falls** — real features, all
  geocodable, but no land-manager page with distance or grade was found in this
  pass. Good candidates, left unwritten rather than written thin. Carisbrook
  Falls (-38.6872473,143.8098422) and Cape Patton Lookout (-38.6919681,143.8299680)
  both geocode cleanly if someone finds the source.

### Left unpinned on purpose

**Station Beach & Rainbow Falls Walk** — Parks Victoria documents it properly
(8km, 3.5 hours return), so the row is worth having, but neither "Rainbow Falls,
Cape Otway" nor "Station Beach, Cape Otway" resolves in Nominatim, and the
Lightstation car park it starts from is not a named OSM feature either. Null
rather than a guess.

---

## Things this pass could not do, or found broken

### `sync.py check <file>` does not exist

The brief says to validate with `python3 scripts/sync.py check <file>`, "which
needs no credentials". Neither half of that is true of the code in the repo:

1. **There is no `check` subcommand.** sync.py's dispatch (line 384) handles
   `seed`, `export`, `pending`, `verify`, `reject` and `add`. Anything else
   prints the docstring. `check()` at line 215 is an internal function `add`
   calls; it has no CLI path.
2. **It exits before argv is read.** Lines 33–36 run at import time and
   `sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY…")` when they are unset —
   so with no `.env` every invocation dies before it can parse a subcommand,
   which is also why `add --dry-run` is blocked without credentials.

So this pass added **`scripts/checkfile.py`**, which does what the brief intended:
it imports sync.py's *own* `check()` — the same function `add` runs before it
writes — and feeds it the types, conditions, kinds and place ids read with the
**public anon key** out of `public/notice-data.js`, the way `have.py` already
does. No service key, no network writes. It also reproduces `add`'s exact-name
`ilike` clash check. Output on this batch:

```
checked 10 row(s) against 43 types, 14 conditions, 7 kinds, 140 places
no validation complaints
no exact-name clashes
```

If a real `sync.py check` subcommand is wanted, the fix is small: move the
URL/KEY guard out of module scope and into the functions that actually make
requests, then add `elif cmd=='check'` to the dispatch.

### `nearby.py --refresh` could not run

Every Overpass endpoint refused from this machine — the main endpoint reset the
connection, `overpass.kumi.systems` and `overpass.private.coffee` both returned
403 through the egress proxy. `api.openstreetmap.org` is blocked too, so raw OSM
tag queries were not possible either and features that exist in OSM but are
unnamed (the Ironbark car park, the Cape Otway Lightstation car park) could not
be reached at all. Nominatim answered normally throughout. The committed
`osm_cache.json` is stamped the same day, so the sweep lost nothing.

### Vocabulary gaps found

- **The monument-and-landmark gap is real and bigger than the brief suggests.**
  The sweeps returned, with no honest type for any of them: *Former Beech Forest
  Hotel*, *Goods Shed*, *Old Stockyards*, *Old Tennis courts* (all Beech Forest),
  *Crowes Buffer Stop* (Lavers Hill), *Werribee Manor Ruins*, *Fort Pearce
  (Bunkers)* and *South Channel Fort* (Queenscliff), *Memorial Arch* (Eastern
  View — the Great Ocean Road memorial arch, one of the most photographed objects
  in the region), *Bark Hut* (Aireys Inlet), *Historic Tramway Track* and
  *Historic Tree Log Tram Carriage* (Lorne). None were written. A `landmark` or
  `heritage` type would take all twelve.
- **No type for a marine sanctuary as a thing to look at.** *Marengo Reefs* went
  in as `nature`, which is the least-wrong option, but the row is really "a seal
  colony you can watch from a rock platform". `nature` also carries citizen-science
  apps, cloud watching and a zoo, so it is doing a lot of work.
- **Suburbs missing from `SUBURBS`:** **Marengo** and **Wongarra** are both real
  and both in scope. Marengo Reefs had to be filed as "…, Apollo Bay"; Carisbrook
  Falls and Cape Patton Lookout are both in Wongarra and would need the same
  workaround. **Hordern Vale** also appeared in reverse-geocodes near Cape Otway.
  (Previously-noted absentees Mannerim and Marcus Hill bit again on listing 543.)

### The landscape / outdoors line — one argument to log

The brief's test is being *in* it versus *doing something in* it, and it mostly
held. Two rows sit badly:

- **Existing row 16, "Surf Coast MTB Trails – Ironbark Basin"**, is filed in the
  landscape sweep's territory but is a mountain-bike trail — outdoors by the
  brief's own example. It also carries a coordinate (-38.3893,144.2314) with **no
  `source_note` at all**, which is worth a look independently of its grouping.
- **Currawong Falls Circuit**, added by this pass as `walk`, is explicitly shared
  with mountain bikes for part of its length (Friends of Eastern Otways say so).
  Filed as `walk` because the row describes walking it. Flagging rather than
  quietly filing.
