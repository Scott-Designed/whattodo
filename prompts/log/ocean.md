# The ocean — worklog

Pass run 31 Aug 2026. Repo cloned fresh from `origin/main` per the note at the top of
`prompts/by-group.md`; `scripts/nearby.py --refresh` run once (2278 named places, 49 town
centres cached 00:37).

**Nothing has been written to Supabase.** `.env` was not supplied to this session, and
`sync.py` exits on the missing `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` before it parses
anything — so `--dry-run` is blocked too, not just the write. All five batches are built and
have passed an offline mirror of `check()`; they need one `--dry-run` each and then the real
run. See **Handover** at the bottom.

Counts at the start of the pass, from `scripts/have.py ocean`:
`water 8 · paddling 9 · swimming 10 · surfing 11 · beach 25` = 63.

---

## water — 8 existing, 10 built

**Searched.** `nearby.py --kinds ocean` across every coastal town at 4–5 km, then by hand:
City of Greater Geelong's boat ramps / jetties / boardwalks directory, Bellarine Bayside's
boat ramps page (they are the committee of management for the northern Bellarine ramps),
Better Boating Victoria's ramp-upgrade pages, Colac Otway Shire.

The database had **no boat ramp, no yacht club, no marina and no named fishing jetty at all**
— `ilike` on "boat ramp", "yacht", "marina", "slipway" returned zero. The three `water` rows
with real pins were all fishing spots. This is the emptiest part of the group and it is the
easiest to fill, because ramps and jetties are exactly what councils publish well.

**Built (10):** Torquay Boat Ramp – Fishermans Beach · Queenscliff Boat Ramp · St Leonards
Boat Ramp · Indented Head Boat Ramp – Wrathall Reserve · Point Richards Boat Ramp · Fairfax
Street Boat Ramp – Steeles Rock · Limeburners Point Boat Harbour · Apollo Bay Harbour ·
Rippleside Jetty · Griffins Jetty.

Queenscliff Boat Ramp carries `["water","paddling"]` rather than getting a second row: the
2023 low-landing kayak pontoon is part of the same ramp, and two rows on one coordinate is
the duplicate problem.

**Rejected / could not place.**
- **St Helens Boat Harbour** (Swinburne St, North Geelong), **Clifton Springs Boat Harbour**
  (Jetty Rd), **Ocean Grove Boat Ramp** (Guthridge St) and **Barwon Heads – River Parade**:
  all real, all on the council's own list, none named in OpenStreetMap and none resolvable in
  Nominatim. Street-only geocodes would be road centrelines. Left out rather than pinned on a
  guess — these four are the best candidates for a hand-pinned pass through /admin.
- **Grammar School Lagoon**, **Corio Bay Boat Club beach**, **Mackey Street Breakwater**,
  **Clifton Springs Fishing Jetty**, **Lascelles Fishing Jetties**, **Swan Bay boat ramp**:
  same reason — sourced from the council, no geocode.
- **Eliza Ramsden** and **Castle Rock** came back from the sweep as `sport=scuba_diving`.
  Both are submerged wreck/reef dive sites with no shore access. Refused on the standing
  rule that nothing in this database may be pinned in water.
- **Royal Geelong Yacht Club**, **Queenscliff Yacht Club**, **Bay City Scuba**: real, but a
  club with a door and a bar is a `venue` or a `group`, not an ocean `spot`, and deciding
  that properly is a separate call. Left for Scott.

**No condition tags written on any water row.** A trailer-boat ramp plainly wants a calm sea
and low wind, but no land manager says so on the page, and the brief is explicit that a tag
has to be earned from the source.

---

## paddling — 9 existing, 6 built

**Searched.** The sweep's `sport=canoe` / `leisure=slipway` hits, then Parks Victoria, Great
Ocean Road Coast and Parks Authority, City of Greater Geelong, Wyndham City, Bellarine
Bayside, and operators' own sites.

**Built (6):** Point Henry Beach Paddle Launch · Aire River Paddle – Great Otway National
Park · Swan Bay Paddlers – Queenscliff Lonsdale Yacht Club (`kind: group`) · Riverbend
Historical Park Canoe Launch · Apollo Bay Surf & Kayak (no pin) · Southern Exposure –
Kayaking Programs (no pin).

Point Henry is the pick of them: the council's own directory lists it as beach-launch only
with **no vehicle-assisted launching permitted**, which is the only paddle-specific launch
restriction published anywhere in the region.

**Rejected / could not place.**
- **Apollo Bay Surf & Kayak** and **Southern Exposure** publish no street address on their
  own pages. Written with null pins rather than pinned at a guessed shopfront.
- **Lake Colac pontoon** — Better Boating Victoria says plans are still being finalised,
  targeted end of 2026. Not built, so not a place. Revisit.
- **Lake Connewarre / Reedy Lake** — Parks Victoria and the council mention canoeing only as
  a generic activity category, no launch point, no access, no hazard. A third-party angling
  site names a "Tait Point Ramp" on Staceys Rd; unverifiable, left out.
- **Werribee South Boat Ramp** — a six-lane trailer facility, and closed for a major upgrade
  at the time of checking.
- **Coogoorah Park, Anglesea** — geocodes cleanly and is obviously a river access, but no
  first-party page confirming a canoe launch was found. Worth ten minutes next pass.
- **Geelong Canoe Club** — Nominatim has it at building level (11 Marnock Rd, Newtown). No
  club website was verified, so no row. It would be a `group`, like Swan Bay Paddlers.
- **Erskine River, Lorne** — the authority's Lorne page covers the pier, beaches and walking
  tracks only. No put-in documented.
- **Wye River / Kennett River** — nothing. Searches for "Wye River kayak" return the River
  Wye in the UK.

---

## swimming — 10 existing, 10 built

The brief's read was right: of the ten existing rows, **six are dated swim races** and only
four are places. There was almost nothing for a family with small children.

**Built (10):** Fishermans Beach · Clifton Springs Foreshore – The Dell · Queenscliff Pier
Beach · Barwon Bluff Marine Sanctuary · Portarlington Harbour Swimming Only Zone (no pin) ·
Kardinia Aquatic Centre · Lara Swimming Pool · Apollo Bay Aquatic Centre · Bellarine Aquatic
& Sports Centre · Northern Bellarine Aquatic Centre.

Four condition tags written, each off the land manager's own words and no others:
- `low-tide` on **The Dell** — the council states high tide may restrict access to the beach.
- `low-tide` on **Barwon Bluff** — Parks Victoria states there is no provision for safe
  access at higher tides.
- `calm-sea` on **Queenscliff Pier Beach** (council's own word), **Portarlington Harbour**
  (a barrier-marked enclosure) and **Fishermans Beach** ("calm blue waters", and the land
  manager's own line about toddlers, SUP and nervous swimmers).
- `warm` on **Apollo Bay Aquatic Centre** — 31°C, stated on the centre's own site.

No `any-weather` was written anywhere in this pass.

**Rejected / could not place.**
- **Eastern Beach Swimming Enclosure** — this is listing 283, *Eastern Beach Reserve & Sea
  Baths – Geelong*. Not added. See corrections below; that row needs a pin and a `swimming`
  type, not a twin.
- **Point Roadknight** — already listing 209. The land manager calls it one of the safest
  beaches in Anglesea and a popular destination for families with young children, and
  Anglesea SLSC confirms employed lifeguards midweek and Saturday mornings 27 Dec–25 Jan.
  That is a correction to 209, not a new row.
- **Splashdown (Moolap)** — the council page publishes no address. A third-party listing says
  Coppards Rd; unconfirmed.
- **Lorne Sea Baths** — the site presents as a members'/wellness precinct. Could not confirm
  casual public swimming, hours or price. Needs a phone call.
- **Santa Casa Beach** and **Springs Beach** (both Queenscliffe) — good council pages, no
  geocode. Santa Casa's page also claims summer patrols, which no other Borough bay beach
  claims; worth a cross-check with Queenscliff SLSC before anyone repeats it.
- **Point Henry Foreshore** — the council's reserve page describes saltmarsh conservation
  land, not a swimming beach. Filed under `paddling` instead, which is what the boating page
  actually supports.
- **Swan Bay** — Parks Victoria mentions swimming on sheltered beaches but names none, and
  lists deep water, submerged obstacles and strong currents. Too vague to pin.
- **Indented Head foreshore**, **St Leonards foreshore** — real bay beaches, but the council
  pages are community profiles with no water description, patrol status or facilities.

---

## surfing — 11 existing, 7 built

This was the thinnest type and it is the hardest, for a reason worth writing down: **of the
eleven existing rows, nine are dated events or shops.** There was essentially one surfable
place listed on a coastline that holds Bells.

The obstacle is not finding breaks, it is that **land managers do not publish surf breaks**.
Councils publish reserves, car parks, toilets and patrol partnerships. A break like Guvvos or
Suicide or Cathedral Rock appears only on surf-forecast and tourism sites, which the URL rule
excludes. Everything below came off a land manager naming the break in passing.

**Built (7):** Winkipop · Steps – Jan Juc · Bird Rock Lookout – Jan Juc · Point Danger –
Torquay · Urquhart Bluff · Go Ride A Wave – Torquay (`venue`) · Point Lonsdale School of
Surfing (`venue`, no pin).

Judgement calls, stated plainly:
- **Winkipop shares the existing Bells Beach coordinate.** No land manager names a separate
  Winkipop car park and OSM has no feature for one — the access genuinely is the Bells car
  park and the clifftop track. Two different waves, one honest pin; that is the case
  CLAUDE.md already describes for the five listings on Bells.
- **Steps, Boobs and Evos come off one stairway.** GORCC's own chairman says so. One row for
  the access, named Steps, rather than three rows on one point.
- **Bird Rock is named "Bird Rock Lookout – Jan Juc"** because listing 326 *Bird Rock* is the
  bar and restaurant at 2 Princes Terrace. The offline duplicate check caught it; `sync.py`
  would have refused it on the exact name.
- **Urquhart Bluff's only source is a surf school's own page.** That is first-party for their
  lessons and their rip warning, and it is not a land manager. Flagged on the row and here.

**Rejected / could not place.**
- **Southside** — a GORCA have-your-say land-transfer document names a "Southside car park"
  in passing; that is the only reference found, and OSM only has the clothing-optional beach
  node. Not enough.
- **Thirteenth Beach – Cylinders** — Barwon Coast's own notice names the 13th Beach Road
  staircase, but **has closed it**: an engineer found it unsafe for public use after tidal
  surge and erosion damage. Adding an access that is shut would be worse than not adding it.
  Barwon Coast names an alternate access, "The Corner" (formerly 30W). Revisit once the
  stairs reopen. Note also that listing 212 *13th Beach* has no pin.
- **Point Impossible as a surf row** — the authority's masterplan page calls it "ideal for
  surfing" but does not name the car park. Written as a beach row with `["beach","surfing"]`
  instead, which is one place and one row.
- **Torquay Point / Cosy Corner, Lorne Point, Marengo/Infinities, Wye River, Kennett River,
  Skenes Creek, Moggs Creek, Guvvos, Suicide, Cathedral Rock, Addiscot, Point Impossible's
  own break** — all real, all searched, none with a land-manager page naming an access point.
  This is the single biggest remaining gap in the group and it will not close through web
  search. It needs either a local, or a decision that a surf-forecast site is an acceptable
  source for a break's existence (it is not, under the current rule).

---

## beach — 25 existing, 8 built

**Built (8):** Jan Juc Beach · Torquay Back Beach · Point Impossible Beach · Point Lonsdale
Back Beach · Queenscliff Ocean View Beach · Narrows Beach (no pin) · Cumberland River Beach ·
Marengo Beach.

Four carry `["beach","surfing"]` — Jan Juc, Torquay Back, Point Impossible and Point Lonsdale
Back. Each is one place where the break and the beach are the same sand, so each is one row,
per the brief.

**Patrol status is quoted, never inferred.** Only three rows claim a patrol and each names its
source: Point Lonsdale Back Beach (PLSLSC's own page, with days and season), Jan Juc Beach and
Torquay Back Beach (the land managers' own wording, which does not give a season — so neither
row gives one either).

**Rejected / could not place.**
- **Whites Beach** — GORCC's page describes the playground beach between Point Impossible and
  Fishermans. That is listing 242, *Whites Beach Playground*. The OSM sweep returns "Whites
  Beach" under both Torquay and Breamlea because the 4 km radii overlap; it is one place.
- **Breamlea Beach** — no distinct first-party page; believed to be listing 213, *Bancoora
  Beach – Breamlea*.
- **Mothers Beach (Apollo Bay)**, **Collendina**, **RAAFs Beach**, **Kennett River beach**,
  **Springs Beach**, **Santa Casa Beach** — all real and all named by their land manager, none
  geocodable. Mothers Beach additionally carries a 2024 safety exclusion zone (retaining wall
  at risk of collapse, change rooms closed); confirm current status before adding.
- **Kennett River** geocodes only to `type=administrative` — a suburb boundary — and to the
  river as a linear feature. Both refused.
- **Marengo** does the same: `type=administrative`. Pinned instead at the Marengo Holiday
  Park, which is the access, and said so on the row.
- **Sunnymead, Step, Smelly, Sandy Gully, Red Rocks (Aireys), Eumeralla, Guvvos, Southside,
  Godfrey Creek, Station Beach (Cape Otway), Reedy Creek, Grassy Point, Red Bluff** — the
  sweep names them, no land manager does. They read as informal local names along stretches
  already covered by a listed beach.

---

## Coordinates — what was done

Every pin was geocoded through Nominatim by **feature name first**, at 1 req/sec with a real
User-Agent, and **every one was reverse-geocoded** before it went in the batch. All 41 rows
came back with a road and a suburb or town in the `address` object; none returned bare
"Victoria, Australia". Two forward matches were **refused for `type=administrative`**
(Marengo, Kennett River) and one for being a linear river feature (Cumberland River). Nine
rows carry a null `lat`/`lng` because no match could be trusted; none carries a guess. No
`km` was written on any row.

Where the pin is not the thing itself — the Point Henry beach toilets, the Marengo Holiday
Park, the Ocean View Kiosk, the Cumberland River Holiday Park, three surf life saving clubs —
the `source_note` says exactly what Nominatim matched, so nobody later reads a car park as a
beach centroid.

---

## Existing rows that need correcting — for /admin, not a script

1. **Listing 163, `Reef Life Survey – Point Addis Marine National Park`, is pinned in the
   wrong place.** `-38.4049,144.12` reverse-geocodes to **Denham Track, Wensleydale** — inland
   bush roughly 11 km from Point Addis and nowhere near the marine national park. The
   longitude also has **two decimal places**, which `sync.py add` would refuse today. Either
   repin it on the Point Addis access (`-38.39531,144.25389`, which listings 3, 91 and 153
   already share) or null it.
2. **Listing 74, `Cumberland River Holiday Park`, is pinned about 2.3 km off.**
   `-38.5559,143.9601` reverse-geocodes to **Allenvale Mill Camp Site, Allenvale Road, Lorne**.
   Nominatim puts the holiday park itself at `-38.573822,143.948867` (2680 Great Ocean Road).
3. **Eleven ocean rows have no coordinate at all**, and geocodes exist for most of them:
   Ocean Grove Main Beach (215), St Leonards Pier & Beach (217), Indented Head Beach & Ozone
   Wreck (219), Wye River Beach (221), Anglesea Main Beach (208), 13th Beach (212), Barwon
   Heads River Beach (214), Point Lonsdale Front Beach & Rock Pools (216), Portarlington Beach
   & Pier (218), Eastern View Beach (220), Eastern Beach Reserve & Sea Baths – Geelong (283).
   OSM names Thirteenth Beach at `-38.285686,144.462092` and the Eastern Beach Swimming
   Enclosure at `-38.146140,144.373583`; the rest are a short geocoding pass.
4. **Listing 209, `Point Roadknight Beach`, should gain `swimming`** and a patrol note.
   GORCC calls it one of the safest beaches in Anglesea and a popular destination for families
   with young children; Anglesea SLSC lists employed lifeguards there midweek and Saturday
   mornings, 27 Dec–25 Jan. Dogs are strictly prohibited for Hooded Plover nesting.
5. **Listing 208, `Anglesea Main Beach`, should gain `surfing`.** GORCC's own page calls it
   "a great place to learn to surf" and confirms Anglesea SLSC volunteer patrols Saturday
   afternoons, Sundays and public holidays from late November to mid-April, plus LSV
   lifeguards in peak summer.
6. **Listing 283, `Eastern Beach Reserve & Sea Baths – Geelong`, should gain `swimming`.**
   It is currently `parks & playgrounds` only, so the region's best-known enclosed swimming
   beach does not appear on `/swimming` at all.
7. **Listing 18, `Jan Juc Rockpools`, has `season: ["low tide","any"]`.** "low tide" is not in
   the season vocabulary — `sync.py`'s season check would refuse that row today. It is a
   `conditions` value that ended up in the wrong column, and the row already has
   `conditions: ["low-tide"]`, so the season entry can just go.
8. **Listing 212, `13th Beach`** — worth a note that the Cylinders staircase on 13th Beach
   Road is currently closed by Barwon Coast for structural safety.

## Places rows worth adding — for /admin

None of these can be written from a script. Each is a venue that publishes its own timetable
or bookings, so a `places` row with `events_url` is the durable move rather than dated rows:

- **Queenscliff Lonsdale Yacht Club** — `qlyc.org`, runs the Swan Bay paddling sessions;
  address is the clubhouse at `-38.266833,144.648492`, Queenscliff.
- **Go Ride A Wave** — `gorideawave.com.au`, 15 Bell Street, Torquay. Seven branches in
  region (Torquay, Anglesea, Ocean Grove, Lorne, Breamlea, Wye River, Apollo Bay), each with
  its own location page.
- **Apollo Bay Aquatic Centre** — `apollobayaquaticcentre.com.au`, Costin Street, Apollo Bay.
  Publishes its own hours and closures.
- **Point Lonsdale Surf Life Saving Club** — `plslsc.com.au/beach-patrol`. The only surf club
  found in this pass that publishes exact patrol days and season dates; a feed here would
  answer "is it patrolled today" for the whole Bellarine ocean side.
- **Anglesea SLSC** — `angleseaslsc.org.au/beach-patrols`, same reason for the Surf Coast.

## Vocabulary — where the 43 types had no word

- **No word for a boat ramp, jetty or harbour.** All ten `water` rows are the same shape as a
  fishing spot, so `water` is carrying "on the water", "beside the water" and "launching into
  the water" at once. It works, but `/water` will now read as a list of concrete ramps with
  three night-fishing entries in it. Not proposing a new type — just noting that `water` is
  the least self-explanatory word in the vocabulary and this pass made it broader.
- **No word for a marine sanctuary or a marine national park.** Barwon Bluff, Point Danger,
  Marengo Reefs, Eagle Rock and Point Addis are all the same kind of thing, and they are
  currently split across `beach`, `nature`, `swimming` and `water` depending on who wrote the
  row. `nature` is the nearest and is doing the work.
- **No word for a surf break as distinct from a beach.** `surfing` covers the break, the
  surf school, the shop and the contest. That is defensible, and the four `["beach","surfing"]`
  rows in this pass show the multi-type list handling it.
- **Nothing for patrol status.** It lives in prose in `notes` on every row that has it, so it
  cannot be filtered or surfaced. Given that "is it patrolled" is the single most useful fact
  about a beach for a family, it may deserve a column rather than a type.

## What is still open

- The nine null-pin rows in these batches (four that could not be geocoded, five operators and
  zones with no published address).
- The surf-break gap above — the largest remaining hole in the group.
- The four northern-Bellarine and Geelong ramps that are on the council's list but not in OSM.
- Whether yacht clubs and dive shops belong in this group at all, and as which kind.

---

## Handover — how to land these

`.env` was never available to this session, so nothing was written. The five batches are built
and have passed an offline mirror of `sync.py`'s `check()` (types, conditions, kinds, cost,
daypart, season, url rules, four-decimal rule, unknown fields) plus an exact-name clash check
against all 1230 current listings, and every `location` was run through the real `suburbOf()`
out of `public/notice-vocab.js` under node — all 41 resolve to a suburb, so none will be
demoted to an idea.

With `.env` in place, in this order:

```bash
for f in water paddling swimming surfing beach; do
  python3 scripts/sync.py add /tmp/ocean/$f.json --dry-run
done
# then, once each is clean:
for f in water paddling swimming surfing beach; do
  python3 scripts/sync.py add /tmp/ocean/$f.json
done
```

Expect `add` to have opinions the offline check cannot reproduce: it does an `ilike` against
the live tables, so anything added since this snapshot may clash. Do not pass `--force`
without reading what it caught, and do not pass `--verified` — these are all
`added_by = 'Research'`, `verified = false`, and belong in `sync.py pending`.

Rows per type: **water 10 · paddling 6 · swimming 10 · surfing 7 · beach 8 = 41.**
Rows per town (via the real `suburbOf()`): **Torquay 7 · Queenscliff 5 · Geelong 5 ·
Apollo Bay 4 · Portarlington 3 · Jan Juc 3 · Drysdale 2 · Point Lonsdale 2 ·
St Leonards 1 · Indented Head 1 · Barwon Heads 1 · Ocean Grove 1 · Bells Beach 1 ·
Aireys Inlet 1 · Cumberland River 1 · Lara 1 · Werribee 1 · Cape Otway 1.**
