# The outdoors pass — 31 Aug 2026

Ran from a fresh clone of `Scott-Designed/whattodo` in a cloud container. No
credentials, no writes: every batch is a file, validated with
`python3 scripts/sync.py check`, for Scott to apply.

**`nearby.py --refresh` failed and was not retried.** All three Overpass
endpoints refused from this container — `overpass-api.de` reset the connection,
`kumi.systems` and `private.coffee` answered `403 Forbidden` through the
container's egress proxy. The committed `scripts/osm_cache.json` (fetched
2026-08-31 12:50, 2796 POIs, kinds arts/bike/food/landscape/ocean/produce) was
used instead. **Nominatim works fine from here**, which is the signature the
script's own error text describes, so every coordinate below is a real forward
geocode with a reverse check on top.

The cache carries no `golf`, `camping`, `skatepark` or `playground` tag set —
`--kinds` covers arts, bike, food, landscape, ocean, produce only. So for six of
the eight types the map genuinely was not the source, exactly as the brief said.
Where an enumeration was still wanted, **bounded Nominatim searches** over the
region's bounding boxes did the job Overpass would have.

---

## golf — 2 existing, 15 rows written

`batches/outdoors-golf.json` · 15 rows · `check` clean.

**This type is not small. The region is golf country and the database had two
rows.** A bounded Nominatim sweep over four boxes covering the Surf Coast,
Bellarine, Geelong and the Otways enumerated 21 distinct courses, of which two
were out of scope (Sorrento and Portsea, Mornington Peninsula) and one is
explicitly private in its own OSM name (Bellarine Lakes Resort).

Written, each off the club's own page unless said otherwise:

| Row | Where | url source |
|---|---|---|
| RACV Torquay Golf Course | Torquay | racv.com.au own golf page, fees read |
| The Sands Torquay Golf Course | Torquay | thesandstorquay.com/golf |
| Lorne Country Club (Golf & Tennis) | Lorne | lornecountryclub.com.au |
| Apollo Bay Golf Club | Apollo Bay | apollobaygolfclub.org.au, fees read |
| Winchelsea Golf Club | Winchelsea | winchelseagolf.com.au (confirmed via SWGA) |
| Birregurra Golf Club | Birregurra | birregurragolfclub.com.au, fees read |
| 13th Beach Golf Links | Barwon Heads | 13thbeachgolf.com |
| Barwon Heads Golf Club | Barwon Heads | barwonheads.golf |
| Ocean Grove Golf Club | Ocean Grove | oceangrovegc.com.au, fees read |
| Lonsdale Links | Point Lonsdale | lonsdalelinks.com.au |
| Queenscliff Golf Club | Queenscliff | queenscliffgolfclub.com.au |
| Portarlington Golf Club | Portarlington | port.golf |
| Curlewis Golf Club | Curlewis | curlewisgolf.com.au |
| Barwon Valley Golf Club | Belmont | **url null — none verified** |
| Queens Park Golf Course | Geelong | City of Greater Geelong own page |

**Six rows carry `cost: null`** because no green fee was published on the page
read. That is the honest value and it is a real follow-up: Lorne, Winchelsea,
Queenscliff, Portarlington, Curlewis, Barwon Valley, Queens Park. Where a fee
*was* read it is quoted in `notes` and the band comes from it.

**Barwon Valley Golf Club went in with `url: null`.** OSM has no website tag for
it and no first-party page was confirmed. A directory listing is not a
substitute and a Maps link is refused, so null it is.

### Coordinate notes worth keeping

- **A golf course polygon centroid is a fairway, not a place you can stand.**
  Used the clubhouse building or an addressed node wherever OSM had one. The
  Sands' course centroid is 1.3 km from its pro shop; Lonsdale Links' polygon is
  600 m from its clubhouse; Apollo Bay's polygon lands on Breakwater Road.
- **Geocoding a council's own street address returned a road centreline.**
  "150 Queens Park Road, Newtown" resolved to `highway=secondary` — the coin
  toss the brief warns about. Asking for `Queens Park Golf Club` by name
  returned the named feature. Ask for the feature, then the street.
- **Curlewis Golf Club has no OSM match under its own name.** Searching the
  address `1345 Portarlington Road, Curlewis` returns the named golf_course
  feature. Two spellings of the club name returned nothing.

### Suburbs that are not in the vocabulary

- **Swan Island** (Queenscliff Golf Club) → written as `…, Swan Island, Queenscliff`.
- **Newtown** (Queens Park) → written as `…, Newtown, Geelong`. OSM's own
  boundary says Highton; the council says Newtown; both answer as Geelong.
- **Connewarre** is in the vocabulary, and OSM puts 13th Beach in it, but the
  club's own address says Barwon Heads 3227. Location follows the club.
- **RACV Torquay reverse-geocodes to Jan Juc.** The resort sits inside the Jan
  Juc boundary; its own address is 1 Great Ocean Road, Torquay. Location follows
  the club, and the source_note records the disagreement.

### Golf candidates verified but NOT written — for a later pass

Each of these was enumerated and has a coordinate; they were left out to keep the
batch at target and move the loop on. All are in scope.

- **Clifton Springs Golf Club** — -38.1540698, 144.5640634, 92-94 Clear Water
  Drive, Clifton Springs. OSM website tag `cliftonspringsgolfclub.com.au`. Note
  Clifton Springs is not in SUBURBS; nearest is Drysdale.
- **St Leonards Golf Club** — -38.1663216, 144.7020682, 282-320 Ibbotson Street,
  St Leonards. OSM website tag `stleonards.golf`.
- **East Geelong Golf Club** — -38.1490526, 144.3840934, Eastern Park Circuit.
- **Geelong Golf Club** — -38.1281773, 144.3424243, Ballarat Road, Hamlyn
  Heights. OSM website tag `geelonggolf.com.au`. Hamlyn Heights → Geelong.
- **Inverleigh Golf Club** — -38.0810259, 144.0536163, 244 Common Road, Inverleigh.
- **Bannockburn Golf Club** — -38.0424115, 144.1340261, Stephens Road, Bannockburn.
- **Colac Golf Club** — -38.3700649, 143.5793888, Harris Road, Elliminyt. Colac is
  in SUBURBS, Elliminyt is not. **Direction argument needed** — it is 75 km west
  on the Princes Highway, the Otways gateway rather than inland-toward-Ballarat,
  so probably in, but it is the edge.
- **Beeac Golf Club** — -38.1942102, 143.6591030, Troys Road, Beeac. Beeac is not
  in SUBURBS and is north-west of Colac. **Probably out of scope.**

### Rejected

- **Sorrento Golf Club** and **Portsea Golf Club** — Mornington Peninsula,
  explicitly out of scope even though they are 12 km across the heads and appear
  in a Bellarine bounding box.
- **Bellarine Lakes Resort Golf Club** — Moolap. OSM's own name for it ends in
  "(private)". Not a place the reader can go.
- **Fore Fun Golf Club**, 154A Ryrie Street, Geelong (`forefun.com.au`) — an
  indoor simulator bar, not a course. **Genuinely unclear where it files.** It is
  `bar` + something the vocabulary has no word for. Logged under vocabulary gaps.

---

## rock climbing — 2 existing, 4 rows written

`batches/outdoors-rock-climbing.json` · 4 rows · `check` clean.

**The brief was right that this type is small, and wrong about where it is
small.** Outdoor climbing in the region really is the You Yangs and nothing
else — the Otways are soft sedimentary and hold no established crag, and no
land manager sanctions the sea cliffs. But there are **three indoor venues
inside the region**, and the database had none of them.

- **Big Rock Climbing Site – You Yangs** — Parks Victoria names two climbing
  sites in the park and this is one. Coordinate is **Parks Victoria's own
  published one** (-37.955437, 144.412521), reverse-checked onto Big Rock Road.
- **Gravel Pit Tor Climbing Site – You Yangs** — the other. Parks Victoria's own
  words: "some of the best and steepest climbs in the park", two anchor points.
  Again a first-party coordinate, reverse-checked onto Great Circle Drive, which
  matches the page's own access instruction. **Spelling: Parks Victoria writes
  Gravel Pit Tor.** Existing listing 287 says "Gavel Pit Tor" in its description.
- **The Rock Adventure Centre**, Newtown, Geelong — 12 m roped walls plus a
  bouldering room. Not in OSM at all; pinned on the 403 Pakington Street address
  node, which is the street frontage and about 50-80 m from a door that is at the
  rear. Said so in `source_note`.
- **Industry Boulders**, Grovedale — bouldering only, 4.3 m, $23 a day.

`good-in-rain` on the two indoor gyms. That is what the tag is for — it is a
boost, not a gate, so an indoor climbing wall gets promoted on a wet day and
hides from nothing. `dry-trails` on the two outdoor sites: wet granite is
unclimbable and both approaches are steep unsealed track.

### Existing row that needs a person

- **Listing 287 `You Yangs Rock Climbing` is an umbrella with no pin and a
  generic url.** It points at `parks.vic.gov.au/things-to-do/rock-climbing`,
  which is the state-wide climbing page, not this park's. With Big Rock and
  Gravel Pit Tor written as their own rows it is now a third, vaguer copy of the
  same thing. **Recommend retiring it**, or repointing its url at the You Yangs
  park page and treating it as the park-level entry. This is the Anglesea-MTB
  situation in miniature: name the sites, do not keep a blur beside them.
  Not touched — flagged. Its description also carries the Gavel/Gravel misspelling.

### Rejected

- **The Boulder Bunker, "Torquay"** (`theboulderbunker.com`) — comes up in an
  Australian search for Torquay climbing and is **Torquay, Devon, England**:
  11 South Street, TQ2 5AE, prices in pounds. A trap worth recording, because the
  name and town match perfectly and nothing on the search result says England.
- **Supatramp Geelong** — trampoline park. Not climbing.
- Indoor gyms in Melbourne and Ballarat — out of region, per the brief.

---

## cycling — 13 existing, 11 rows written

`batches/outdoors-cycling.json` · 11 rows · `check` clean.

**The bike sweep found shops, and the shops were the wrong answer.**
`nearby.py --all --kinds bike` off the committed cache reports 19 mapped places,
15 not listed — and reading them, almost all are surf shops, Kathmandu, Rebel,
BCF and SportsPower that OSM tags loosely. Only three were real leads
(below), and bike shops are the August pass's territory anyway. **The map is
genuinely not the source for this type**, exactly as the brief said.

What filled it instead was **two council pages nobody had read**:

- **Surf Coast Shire, "Bike tracks & bike parks"** — seven council bike
  facilities, of which only Anglesea Bike Park was already listed. This is the
  single best find of the pass and it includes **a jump park in Jan Juc itself**.
- **City of Greater Geelong, "Paths, tracks and trails"** — five named trails,
  of which only the Bellarine Rail Trail was listed.

Written: Bob Pettitt Bike Park (Jan Juc), Spring Valley Bike Park (Torquay),
Kalkarra BMX & Pump Track (Mt Duneed), Connewarre BMX Track, Moriac BMX Track,
Deans Marsh BMX Track, Barwon River Trail, Bay Trail, Waurn Ponds Trail, Ted
Wilson Trail, Geelong Cycling Club.

### Start lines, as the brief asked

Every trail row says **which end it is pinned at, in `notes` and in
`source_note`**:

- **Barwon River Trail** → the Buckley Falls Reserve car park end, because that
  is the entrance the council names a car park for.
- **Bay Trail** → the Eastern Beach end. The Rippleside end has no usable
  feature: "Rippleside Park" returns a **motel of that name** first, then only a
  `type=administrative` suburb boundary. Both refused.
- **Waurn Ponds Trail** → the Belmont Common end, where it joins the Barwon
  River Trail.
- **Ted Wilson Trail** → **null pin.** Six OSM matches, all segments of one
  linear cycleway, spread 15 km from Corio to Waurn Ponds, and the council names
  no car park. Pinning a segment is the coin toss.

### Four rows carry a null pin and each is the same refusal

**Connewarre, Moriac and Deans Marsh BMX tracks**: the council publishes a road
and no street number, OSM has no feature under any of the three names, and the
road geocodes to a centreline. Pennyroyal Valley Road returns **two segments
3.4 km apart**. Moriac is the sharpest case — the Moriac Skatepark is already
listed at 830 Hendy Main Road, the same road, and **borrowing that pin would be
exactly the placeholder problem the brief warns about**, so it was not borrowed.

### `dry-trails` vs `dry-ground`, applied

- **`dry-trails`** on the six dirt facilities — the jump lines and BMX loops.
  A dirt jump line is a bog for two days after rain.
- **`dry-ground`** on the four sealed shared trails and the club. Sealed path,
  rideable on damp ground, not in rain.
- **`any-weather` appears on none of the 11 rows.** It is on 9 of the 13 existing
  cycling rows, which is the pattern the brief flagged.

### Type call worth arguing, not hiding

**BMX tracks, pump tracks and dirt jump lines have no word in the 43.** Written
as `cycling` primary, with `mountain biking` second on the two jump parks (Bob
Pettitt, Spring Valley) because jump lines are gravity riding and the existing
`Anglesea Bike Park – Camp Rd (4X / Jumps)` row sets that precedent. The BMX
loops and the pump track got `cycling` alone: they are neighbourhood facilities
for kids on whatever bike they own, not mountain biking. If Scott disagrees the
fix is one field. Logged rather than filed quietly.

### For `places` — a registration Scott should make

- **Geelong Cycling Club** → `places` row, `events_url`
  **`https://entryboss.cc/calendar/geelong`**. CLAUDE.md already records EntryBoss
  as the best HTML source this project has found and the August bike pass wired
  the mountain-bike clubs to it. **This is the region's road/track club and it
  was not among them.** Address: Russell Mockridge Pavilion, 1 Barwon Heads Road,
  Belmont, Geelong, -38.1712085, 144.3513546. Website `geelongcycling.com`.
  A `places` row here is a permanent fixture feed instead of hand-typed races.

### Existing rows this pass found wrong

- **`Bellarine Rail Trail` (listing under `mountain biking`, "Geelong to
  Queenscliff") carries no `cycling` type.** It is a 35 km sealed rail trail and
  the City of Greater Geelong lists it under paths and trails. It should carry
  `cycling`. Not touched — flagged.
- **`Old Beechy Rail Trail` (`mountain biking`, "Birregurra / Otways")** — same
  argument, same fix.

### Leads found and not written

- **Good Cycles**, Geelong — a real bike shop, not listed. **Sprockt**,
  Queenscliff — a real bike shop, not listed. Both are `shop` kind and belong to
  the bike-shop pass's conventions, which CLAUDE.md says are hand decisions the
  classifier would undo. Left for that pass rather than written here.
- **Hendry Cycles, Ocean Grove** and **Bicycle Superstore, Geelong** show as
  "not listed" in the sweep but are both already in the database under slightly
  different names (`Hendry's Ocean Grove`, `Bicycle Superstore Geelong`). That is
  the script's deliberate false-negative bias working as designed.
- **Currawong Falls Shared Trail**, Aireys Inlet — listed by Surf Coast Shire
  under regional bike trails, but Currawong Falls is reached from Distillery
  Creek by what is normally described as a walking track. **Not written: could
  not confirm it is rideable.** The falls themselves are at -38.4227727,
  144.0891152 if someone wants to settle it.
- **The Hill MTB Park, Geelong** — named on the Surf Coast Shire trails list, no
  OSM feature, not researched further. Belongs to mountain biking.

---

## running — 16 existing, 7 rows written

`batches/outdoors-running.json` · 7 rows (4 activities, 3 events) · `check` clean.

**Three parkruns were missing and the database had two.** Ocean Grove,
Portarlington and Balyang Sanctuary all run every Saturday at 8am and none was
listed.

**parkrun.com.au is fetchable — but only some paths.** `/oceangrove/course/`
and `/special/eventdirectory/` both answer **405** to an automated fetch; the
event home page `/oceangrove/` serves normally. That is worth writing down,
because the obvious first move (fetch the course page) fails in a way that looks
like the whole site is closed. All three rows are therefore **`date_confidence:
"high"` off the event's own page** rather than medium off an aggregator — which
is better than the two parkrun rows already in the database, both of which point
at surfcoastevents.com.au and say medium.

**The full parkrun event directory could not be enumerated.** `/events/events/`
loads its list from JavaScript, and the directory path 405s. So there may be more
parkruns in the region than these five. Worth one manual look at the parkrun map.

### The three parkruns have no `place_id`, and that is the known fault

Per RESEARCH_RULES: none of these venues has a `places` row, so all three go in
**unpinned**. Addresses for Scott to build rows from:

| parkrun | Address for the `places` row | Coordinate |
|---|---|---|
| Ocean Grove | Barwon Estuary Picnic Area, Peers Crescent, Ocean Grove 3226 | **none found** — "Barwon Estuary" returns no OSM feature; "Peers Crescent" is a road centreline |
| Portarlington | The Esplanade, Portarlington 3223 | **none found** — parkrun gives no number; the only "The Foreshore" features near Portarlington are cycleway segments reverse-geocoding to Indented Head |
| Balyang Sanctuary | Balyang Sanctuary, 50 Marnock Road, Newtown 3220 | **-38.1643286, 144.3306496** — OSM named feature, reverse-geocodes to Marnock Road, Newtown, agrees with parkrun's own address |

Balyang is ready to paste. The other two need a person who knows where the start
line actually is.

### The rest

- **John Landy Athletics Field** — the region's athletics track, council-run,
  free parking, playground, open to the public outside booked use. **Note OSM
  tags it `leisure=playground`**, which is wrong for an athletics track; the name
  and street are right, so the pin stands and the mis-tag is recorded.
  Pavilion and grandstand are fenced off for capital works right now.
- **Geelong Athletics** — the senior body since 1962, six member clubs, summer
  track at Landy Field and winter cross country. Pinned at Landy Field.
- **Geelong Little Athletics Centre** — since 1964, nine member clubs including
  Ocean Grove Barwon Heads and Leopold. **The wheelchair-access line is quoted
  from Little Athletics Victoria's own centre listing, not inferred** — the
  standing rule on accessibility claims.
- **The Happy Runner**, 15 Bell Street, Torquay — Torquay's *second* running
  shop, found by the bike sweep of Torquay where OSM had tagged it `sports`.
  Its own site publishes no address and no hours, so `notes` says so rather than
  quietly borrowing a directory's.

### Existing rows this pass found wrong

- **Event 84 is named `Parkrun – every Saturday` with no town in the name.**
  Every other parkrun row carries its town (`Trebeck Reserve Parkrun – every
  Saturday`). With three more added, a bare "Parkrun" is unreadable in a list.
  It is the Torquay one, venue Fishermans Beach. **Rename to
  `Torquay Parkrun – every Saturday`.** Not touched — flagged.
- **Events 84 and 86 both say `date_confidence: medium`** and link
  surfcoastevents.com.au. Both have first-party parkrun pages that would make
  them high. Cheap fix, same shape as the three written here.

### Not written

- **Geelong Runners Club** — `geelongrunnersclub.com.au` **404s on the homepage
  and on the one deep link a search returned**, while its Instagram and Facebook
  are live. A club with a dead website is a `url: null` row at best; left for a
  person to check whether the club still runs.
- **Surf Coast / Torquay Little Athletics** — Little Athletics Victoria's Geelong
  centre page lists nine member clubs and none is on the Surf Coast. Either there
  is no centre this side of Mt Duneed or it sits under a different centre. Not
  resolved.
- Athletics South West, Corio, Deakin, Geelong Guild, Bellarine Athletics,
  Athletics Chilwell, South Barwon — seven named senior clubs, each a plausible
  `group` row. Not written; they need their own pages and that is an hour.

---

## camping ground — 17 existing, 12 rows written

`batches/outdoors-camping.json` · 12 rows · `check` clean.

**Read what was there first, as instructed.** The 17 existing rows are the
caravan parks and the four best-known Otway bush campgrounds. What was missing
was **the whole Parks Victoria layer** — the Aire River complex, the inland bush
campgrounds, and **every Great Ocean Walk hike-in campsite except Blanket Bay**.

### Parks Victoria is now two websites and this matters

Great Otway National Park campgrounds on the coast are managed by the **Great
Ocean Road Coast and Parks Authority**, and `parks.vic.gov.au` **302-redirects**
to `greatoceanroadauthority.vic.gov.au` for them. The authority's pages are much
richer — site counts, closure dates, bridge load limits — while the Parks
Victoria pages that do NOT redirect (Aire Crossing, Hammond Road, Herberts) are
thin but **publish a first-party coordinate**. Both are first-party. Which URL a
row carries depends on which one actually serves it.

**Three rows use a Parks Victoria published coordinate rather than a geocode**,
each cross-checked against an independent OSM node: Aire Crossing (30 m apart),
Hammond Road (10 m), Herberts (60 m). That agreement is worth more than either
source alone.

### Written

Drive-in: Aire Crossing, Aire River West, Aire River East, Johanna Beach,
Hammond Road, Herberts (Wymbooliel).
Hike-in on the Great Ocean Walk: Elliot Ridge, Aire River, Cape Otway,
Johanna Beach.
Bellarine: Victoria Park Queenscliff, Queenscliff Recreation Reserve.

**Every row carries booking information in `notes`**, as the brief required, and
a real operator or Parks Victoria / GORCAPA url. No fabricated URLs.

### Live closures a reader would want today (31 Aug 2026)

- **Aire River East is CLOSED** 29 May to 30 October 2026, reopening 31 October.
- **Aire River West sites 17-23 closed** late May to September, **24-40** late
  May to October — most of a 40-site campground.
- **Victoria Park Queenscliff is shut** until 1 September, opening tomorrow.

### The trap this type sets: three campgrounds on one river bend

**Aire River West, Aire River East and the Great Ocean Walk's Aire River hike-in
campground are three different places**, and OSM's nodes for the West and the
hike-in site are **110 metres apart**. Same for Johanna: the drive-in
`Johanna Beach Campground` and the walkers' `Johanna (GOW)` camp are 380 m
apart on the same beach. Both pairs are written as separate rows with the
distinction stated in `notes` and `source_note`, on the Anglesea-MTB precedent.
Anyone merging them later should read this paragraph first.

### Suburbs not in the vocabulary — five of them here

| Campground | Real locality | Written as | Note |
|---|---|---|---|
| Aire Crossing | Glenaire | Lavers Hill | ~10 km |
| Aire River West | Glenaire | Cape Otway | ~8 km |
| Aire River East | Hordern Vale | Cape Otway | ~8 km |
| Johanna Beach (both) | Johanna / Yuulong | Lavers Hill | ~12 km |
| Hammond Road | Wensleydale | **Deans Marsh** | ~7 km, but **Aireys Inlet is the town most people would name** — arguable |
| Herberts | Benwerrin | Lorne | OSM's own parent; the road climbs from Lorne |

**Wensleydale is the one to look at.** It already appears in the database
implicitly (Painkalac Dam is filed "Aireys Inlet (hinterland)"), it holds at
least three mapped campgrounds, and it has no vocabulary entry.

### Ten rows carry `cost: "Cheap"` as a tier, not a quoted fee

Parks Victoria and GORCAPA publish "fees apply" and a booking link, never an
amount, on every page read. `Cheap` is the honest band for a bush campground in
a scheme whose alternatives are Free, Moderate and Splurge, and **each
`source_note` says explicitly that the band is the tier and no fee was
published**. Aire Crossing is `null` — it is non-bookable first-come and the
page says neither a fee nor that it is free.

### Region edge — two Great Ocean Walk campsites deliberately left out

The walk has seven hike-in campsites. Blanket Bay was already listed and four
are written here. **Ryans Den and Devils Kitchen are not**, because they sit
west of Moonlight Head, past the Otways/Great Ocean Road spine CLAUDE.md names
(Cape Otway, Beech Forest, Kennett River, Lavers Hill, Forrest, Apollo Bay), at
roughly 135 km and 145 km. **The argument against leaving them out is real**:
they are two nights of one continuous walk whose other five nights are in the
database, so the walk is now listed with a hole in it. Logging rather than
deciding, per the brief. If Scott wants them:
Ryans Den and Devils Kitchen, both `greatoceanroadauthority.vic.gov.au` pages.

### Found, mapped, not written — a queue for the next camping pass

All have OSM `tourism=camp_site` nodes and none is in the database:

- **Beauchamp Falls Campground**, Beech Forest — -38.65139, 143.60667. It is in
  **Otway Forest Park**, not Great Otway NP, so its Parks Victoria URL is
  `/places-to-see/sites/beauchamp-falls-reserve` — which **404s on fetch**
  despite being indexed. Needs a person.
- **Dandos Campground**, Gellibrand — -38.5538801, 143.6190107.
- **Stevensons Falls Campground**, Barramunga — -38.5643092, 143.6555174. A
  well-known Otways riverside campground and a clear gap.
- **Goat Track Camping**, Barwon Downs — -38.5095824, 143.7710118.
- **Apollo Bay Recreation Reserve** camping — -38.7639512, 143.6672595. Apollo
  Bay has no campground in the database at all despite being a named in-scope town.
- **Skenes Creek Beachfront Park** — -38.7246661, 143.7139653.
- **BIG4 Anglesea (Noble Street)** — -38.4090313, 144.1803851. Distinct from the
  listed Anglesea Family Caravan Park.
- **Geelong Showgrounds Camping**, Breakwater — -38.1709294, 144.3726170.
  Note **Geelong Showgrounds is already a `places` row** (id 60-ish range,
  kind `showground`), so this one should link by `place_id`.
- **Golightly Park, Point Lonsdale** and **Royal Park, Point Lonsdale** — the
  other two Queenscliffe Tourist Parks, both from $44, Royal Park open
  1 Sep - 30 Apr and never pet friendly. **Neither has an OSM feature**, so both
  need an address before they can be pinned.

### Existing row worth a second look

- **`Jamieson Creek Campground`, listed at Skenes Creek.** OSM's only nearby
  feature is `Jamieson Track Camping Area` on Jamieson Track at
  **Separation Creek** (-38.5966006, 143.9180082), which is 25 km east of Skenes
  Creek. Either the listing's location is wrong or they are two different places.
  Not touched — flagged. Note this is the same Separation Creek that the ocean
  pass already flagged over the two Wye River rows.
- The `camping ground` type carries **`any-weather` on 5 of 17** existing rows.
  None of the 12 written here uses it.

---

## skatepark — 19 existing, 9 rows written, and an AUDIT that matters more

`batches/outdoors-skatepark.json` · 9 rows · `check` clean.

The brief said skateparks were seeded early as council assets and not to
re-walk them. **They were seeded early and they were seeded badly**, so the
work here was half audit.

### The two council lists — neither had been read

- **City of Greater Geelong, "Skate parks in Geelong"** — names **fifteen**
  council skate parks. The database held nine of them.
- **Surf Coast Shire, "Skate parks"** — names **ten**, each with a street
  address AND a feature-by-feature description (bowl depths, quarter pipes,
  rails). The database held eight and, more importantly, had none of the
  descriptions.

Written: Deans Marsh, Winchelsea (Surf Coast); Portarlington (WG Little
Reserve), Hamlyn Park, St Leonards Lake Reserve, Jetty Road Reserve
(Clifton Springs), Fountain of Friendship Park (Norlane), Sparrow Park
(Geelong West), Grinter Reserve (Moolap).

**Six of the nine are pinned on the PARK, not the skate bowl**, because OSM has
no feature for the ramp. Every one says so in `source_note` in those words.
Portarlington and Winchelsea have real pins — an OSM `Portarlington Skate Park`
feature and a street-number node. Deans Marsh links `place_id` 52.

### THE PIN AUDIT — every existing skatepark coordinate reverse-geocoded

Seventeen of the twenty rows carry a pin. Reverse-geocoded all seventeen and
compared against the councils' published addresses and OSM's own named skatepark
features. **This is the finding of the pass.**

**BROKEN — listing 49 `Moriac Skatepark` is pinned about 12 km from Moriac.**
It holds `-38.284, 144.3031`, which reverse-geocodes to **915 Blackgate Road,
FRESHWATER CREEK, Torquay 3228**. Its own `notes` field says "830 Hendy Main Rd,
Moriac". Surf Coast Shire's skate parks page gives the site as **Newling
Reserve, 830 Hendy Main Road, Moriac 3240**, which Nominatim resolves to a named
`leisure=park` feature carrying that house number at **-38.2455631,
144.1710807**, reverse-geocoding to "Moriac Playground, Lavinia Court, Moriac".
That is the correction. This is the same shape of fault as listing 163 in the
ocean pass — a pin in the wrong township with the right address sitting in the
row's own notes.

**MISSING — two listings have `lat`/`lng` NULL but a coordinate hidden in their
`url`.**
- Listing 1 `Jan Juc Skatepark` — url `…maps?q=-38.3657,144.2979`. **That is the
  Jan Juc placeholder CLAUDE.md says was cleared from 48 rows in August**, and it
  is 2.3 km offshore in Bass Strait. It survived in the url field. The real
  address is **87 Sunset Strip, Jan Juc** per Surf Coast Shire — the same address
  as Bob Pettitt Bike Park, i.e. Bob Pettitt Reserve, pinnable at
  **-38.3481528, 144.2936439** (reserve) or on the OSM `BMX jumps` way used for
  the bike park row.
- Listing 5 `Torquay Skatepark – Beach Rd` — url `…maps?q=-38.3374,144.3278`.
  The council address is **79 Beach Road, Torquay**, which geocodes to
  **-38.3259145, 144.3155063** and sits **16 metres** from OSM's named
  `Torquay Skate Park` feature. The url's coordinate is about 1.5 km off.

**SUSPECT — pins that disagree with the council's published address:**

| Listing | DB pin | Council address / OSM feature | Apart |
|---|---|---|---|
| 51 `Djila Tjarri Skate Park` | -38.3168, 144.3238 → "10 Lune Court, Torquay" | Cnr Merrijig Drive & Wadawurrung Way | ~1.0 km |
| 45 `Anglesea Skatepark` | -38.4044, 144.1829 → "7 Fraser Avenue" | Lions Park, cnr Cameron Rd & Great Ocean Rd; OSM `Skate Park, Inverlochy Street` at -38.4025311, 144.1965789 | ~0.9-1.2 km |
| 46 `Aireys Inlet Skatepark` | -38.4594, 144.1023 → "40A Bambra Road" | Cnr Inlet Crescent & Great Ocean Road | ~0.67 km |
| 54 `Ocean Grove Skatepark` | -38.266, 144.5168 → "Ocean Grove **Bowls Club**" | OSM `Ocean Grove Skatepark, Shell Road` at -38.2583424, 144.5396058 | ~2.1 km |
| 52 `Waurn Ponds Skatepark` | -38.2116, 144.3027 | OSM `Waurn Ponds Skate and Bike Park, Pioneer Road, Grovedale` at -38.1987284, 144.3214119 | ~2.2 km |
| 58 `Corio Skatepark (Stead Park Bowls)` | -38.1166, 144.3454 | OSM `Northern Skate Park, St Georges Road, Corio` at -38.0838938, 144.3594645 | ~3.9 km |
| 56 `Leopold Skatepark` | -38.1748, 144.4638 | OSM `John Hansen Memorial Skate Park, Bellarine Hwy` at -38.1864168, 144.4568817 | ~1.5 km |
| 50 `Geelong Waterfront Skatepark` | -38.1477, 144.3616 → "**Witchery**, Malop Street" | council names Poppy Kettle Playground on the waterfront | pin is in the CBD mall, not on the water |
| 57 `Lara Skatepark` | -38.0189, 144.4053 | OSM `Lara Skate Park, Station Lake Road` at -38.0228410, 144.4115827 | ~0.7 km |
| 59 `Norlane Skatepark (North Shore)` | -38.0938, 144.3444 | sits BETWEEN Windsor Park (-38.0890177, 144.3629677) and Fountain of Friendship Park (-38.0925937, 144.3382086) | **ambiguous** |

**Checked and fine:** 47 `Lorne Skatepark` is 100 m from 81 Mountjoy Parade;
55 `Barwon Heads Skatepark` is 600 m from OSM's Sheepwash Road feature, which is
the reserve-vs-bowl gap rather than an error.

**Listing 59 is the one to resolve before applying the new Fountain of
Friendship row**, because Norlane genuinely has two council skate parks and 59
could be either. The new row warns about this in its own `source_note`.

### The near-duplicate already in the database

**Listing 51 `Djila Tjarri Skate Park` (Torquay North, has a pin) and listing
243 `Djilla Tjarri Play & Skate Zone` (Torquay, no pin, council url) are the
same place with two spellings.** One L versus two. `sync.py add` would never
have caught it and did not — both are already in. Surf Coast Shire spells it
**Djila Tjarri** on its skate parks page and **Djilla Tjarri** on its parks and
reserves page, so the council is the source of the confusion. Merge needed.

### Every skatepark url in the database is a Google Maps link

Sixteen of the twenty carry `https://www.google.com/maps?q=<lat>,<lng>` and one
(61, Inverleigh) carries a `google.com/maps/search/` link — **which `sync.py
check` refuses outright today**, so that row could not be written now. These are
the coordinate form rather than the search form, so they slip the check, but they
are the same thing: a link to a map pin instead of a page about the place. **Both
councils publish a real page for every one of these**, and the nine rows written
here use them. Repointing the existing sixteen is a mechanical job worth doing.

### What this unlocked for the cycling batch

The Surf Coast skate parks page gave street numbers for three reserves the bike
page had named only by road, so **the three BMX tracks that were written with
null pins earlier in this pass now have coordinates**: Connewarre Reserve
(15 Randles Road), Newling Reserve (830 Hendy Main Road) and Deans Marsh
Memorial Reserve (`place_id` 52). Each `source_note` states plainly that the
reserve-equals-BMX-site step is an inference from two council pages sharing a
street, not something either page says.

### Still not written

- **Windsor Park Skate Park, Norlane** — held back until listing 59 is resolved.
- **Poppy Kettle Playground** (Geelong waterfront), **Pioneer Park** (Grovedale),
  **Stead Park** (Corio), **Shell Road Reserve** (Ocean Grove), **Austin Park**
  (Lara), **Barwon Heads Village Park**, **Leopold Memorial Recreation Reserve** —
  these are the council's names for skate parks the database already lists under
  other names. They are the audit table above, not new rows.

---

## parks & playgrounds — 20 existing, 9 rows written

`batches/outdoors-parks-playgrounds.json` · 9 rows · `check` clean.

**`have.py places` first, as instructed** — 176 places, of which sixteen are
parks, reserves or playgrounds. Cross-checked every candidate against both that
list and the 20 existing listings before writing. **One row links `place_id`
instead of carrying a coordinate** (Deans Marsh, in the skatepark batch); none
of the nine here needed to, because none of them already has a `places` row.

### The scale of what is missing

- **Surf Coast Shire lists roughly 40 council playgrounds** across Aireys Inlet,
  Anglesea, Bambra, Bellbrae, Connewarre, Deans Marsh, Freshwater Creek, Jan Juc,
  Lorne, Modewarre, Moriac, Torquay (16 of them alone) and Winchelsea. The
  database has four of them.
- **The City of Greater Geelong says it manages 380 public play spaces.**

So this type cannot be "finished". What was written is the set worth driving to,
each off its own council reserve page, with the equipment actually named.

Written: Bob Pettitt Reserve Pavilion Playground (Jan Juc), The Quay Reserve
Playground (Torquay North), Bark Hut Reserve Playground (Aireys Inlet), Erskine
Paddock Playground (Lorne), Newling Reserve All Access Playground (Moriac),
Barwon Valley Fun Park (Belmont), Rippleside Park & Inclusive PlaySpace
(Geelong), Poppy Kettle Playground (Geelong), Kingston Park Playground
(Ocean Grove).

### Accessibility statements are quoted, never inferred

Four rows carry one: The Quay ("accessible toddler and junior playground"),
Bark Hut, Newling Reserve ("all access", "accessible playground suitable for
toddlers and juniors"), and Rippleside (inclusive PlaySpace, four accessible
parking bays, **a registered Changing Places facility**). Every one is the
council's own wording and every `source_note` says so. **Barwon Valley Fun Park
deliberately carries none**, because the council makes no accessibility claim
about it — only that the outdoor gym suits "a range of ages and abilities",
which is not the same statement.

### Pins

Six of nine are **addressed nodes** from a council-published street number,
which is the best kind of pin this type gets. Erskine Paddock uses **Surf Coast
Shire's own published coordinate**. Kingston Park uses OSM's playground way, not
the park polygon. **Poppy Kettle is the weak one** — OSM has no feature for the
playground, so it is pinned on the Poppy Kettle Fountain the playground is named
after, and the row says so.

### Three cross-references this type turned up

- **Poppy Kettle Playground's site includes the skatepark** the database lists as
  `Geelong Waterfront Skatepark` — whose pin is in the Malop Street mall, about
  1.3 km inland. The Poppy Kettle row gives the right coordinate for that area.
- **Bob Pettitt Reserve is three listings' worth of one place**: the council
  gives 87 Sunset Strip for the skate park, 89 for the playground, and the bike
  page gives 87 for the jump lines. Written as three rows, all in one reserve,
  because they are three different things a family would choose between.
- **Newling Reserve, Moriac** holds the playground, the skate park and the BMX
  track. The playground row carries the correct reserve coordinate; the existing
  skatepark listing is 12 km away.

### Vocabulary gap found here

**Barwon Valley Fun Park has a free 18-hole disc golf course, open 24 hours.**
There is no word for disc golf in the 43 and it is not golf. The database's only
existing acknowledgement of the sport is `Frisbee Golf to Natural Targets`, an
`at-home` idea. Filed under `parks & playgrounds` with disc golf in the tags and
description; logged rather than forced.

### Not written, and worth a next pass

- The other seven of Geelong's own top ten: **Coolabah Park** (Grovedale),
  **Gateway Sanctuary** (Leopold), **Goldsworthy Playground** (Corio),
  **Hammersley Road Playground** (Bell Park), **Kevin Kirby Reserve**
  (Herne Hill), **The Heights Playground** (Fyansford), **Unity Drive Playspace**
  (Armstrong Creek). Each has a council page; none was fetched.
- Surf Coast: **Anderson Roadknight Reserve** and **Painkalac Creek Playground**
  (Aireys Inlet), **Lions Park** and **Moonah Park** (Anglesea), **Bellbrae
  Reserve**, **Freshwater Creek**, **Torquay Boulevard Playground** (Jan Juc),
  **Clerke Court** and **Moriac Community Centre**, **Dwyer Street**, **Hesse
  Street Reserve**, **Riverbank** and **Wurdale** (Winchelsea), and twelve more
  in Torquay. The reserve-page URL pattern
  `surfcoast.vic.gov.au/Experience/Parks-and-reserves-listing/<Reserve-Name>`
  works and each page carries an address, an equipment line and sometimes a
  coordinate — this is a mechanical hour for someone.
- **Bambra Reserve** and **Modewarre Recreation Reserve** are on the Surf Coast
  list and **neither Bambra nor Modewarre is in the SUBURBS vocabulary**, which
  RESEARCH_RULES already names as a known gap.

---

## mountain biking — 33 existing, 1 row written, and four broken pins found

`batches/outdoors-mountain-biking.json` · 1 row · `check` clean.

**Read before searching, as instructed.** The August bike pass did the four
clubs, the eight shops and the EntryBoss fixtures, and that work is sound. The
trail networks were seeded earlier and **that is where the faults are.** So this
section is one new row and an audit.

### Written

- **The Hill Mountain Bike Park**, Newtown, Geelong. Four hectares of
  council-built park in the middle of Geelong — three XC trails, a skills track,
  a pump track and three grades of jump line, recently refurbished. It was named
  on Surf Coast Shire's own regional trails list and was not in the database.
  **Pinned at the council's own car park (23-31 Newcastle Street), not the trail
  entrance**, per the trailhead rule. E-bikes and e-scooters are banned, which is
  the kind of thing that ruins a trip if you learn it on arrival.

### The pin faults — reverse-geocoded, all four confirmed

**1. Listings 16 and 44 have effectively swapped their pins, and this is the
exact confusion CLAUDE.md's "do not conflate" note exists to prevent.**

- `Surf Coast MTB Trails – Ironbark Basin` (16), location "Anglesea", pin
  `-38.3893, 144.2314` → **reverse-geocodes to Hurst Road, Bells Beach.** Hurst
  Road IS the Hurst Rd / Eumeralla network, which is listing 44.
- `Anglesea MTB – Hurst Rd / Eumeralla Network` (44), pin `-38.4203, 144.1578` →
  **reverse-geocodes to Point Roadknight, Anglesea.** That is a beach. It is
  about 6 km from Hurst Road and is not a trail network.

  On top of that, **CLAUDE.md's three Anglesea areas are Anglesea Bike Park
  (Camp Rd), Hurst Rd / Eumeralla, and Ironbark Spur** — *Spur*, a trail inside
  the broader network. **Ironbark Basin is a different place entirely**: it is at
  Point Addis, and the database's own listing 233 `Point Addis – Ironbark Basin
  Circuit` describes it as a 7 km walking circuit. So listing 16 looks like
  **Ironbark Spur renamed as Ironbark Basin and pinned on Hurst Road**. Whether
  mountain biking is even sanctioned in Ironbark Basin was not established here
  and should be, before the row is repaired rather than retired.

**2. Three listings share one identical coordinate, and one of them is 35 km
from where it says it is.** `-38.5238, 143.7259` → reverse-geocodes to
**15 Kaanglang Road, Barramunga, Forrest** and is carried by:

- 38 `Forrest MTB Trails – Southern Network`
- 39 `Forrest MTB Trails – Yaugher Network`
- 42 `Lorne & Otways MTB / Gravel Trails`

The Forrest Southern and Yaugher networks are on **opposite sides of Forrest**
and cannot share a point; and **listing 42 says Lorne**, which is 35 km east
over the range. Three rows on one coordinate is the copy-paste signature the
ocean pass named for the two Wye River rows.

**3. Listing 37 `Anglesea Bike Park – Camp Rd` carries the wrong url.** It
points at `trailsplus.com.au/ironbark-basin` — the same url as listing 16, for a
different place. Surf Coast Shire publishes 80 Camp Road, Anglesea on its own
Bike tracks and bike parks page and has a reserve page for the bike park.
**Its pin, though, is the best in the type**: `-38.39732, 144.19399`
reverse-geocodes to "Anglesea Bike Park 4X Track" — the feature itself.

### A row that sits badly, logged rather than moved

**`Currawong Falls Circuit` (591) is filed as a `walk` in The landscape, and
Surf Coast Shire lists Currawong Falls Shared Trail among its bike trails.**
Under the group rule — doing something in it versus being in it — a shared trail
you ride is outdoors and a walk is landscape, and this one is claimed by both.
The Friends of Eastern Otways page the row cites describes a walk. **Not
touched.** If the council's "shared" is literal, the row should gain `cycling`
or `mountain biking` as a second type rather than move; if it is a walking track
the council has miscategorised, nothing changes. Someone who has been there can
settle it in a sentence. It also carries `good-in-rain`, which is unusual for a
fern-gully circuit and probably right.

### Two rows that should gain `cycling`

Repeated from the cycling section because they belong to both: **Bellarine Rail
Trail** and **Old Beechy Rail Trail** are typed `mountain biking` only. Both are
rail trails; the City of Greater Geelong lists the Bellarine one under paths and
trails. One extra element in `types`.

### Not written

- **Ironbark Spur** as its own row — the honest third Anglesea area under
  CLAUDE.md's own note. Held back until listing 16 is resolved, because writing
  it now would make three rows for two places.
- **Individual Forrest trails** (Red Carpet, Marriner's Run, Grasstrees) — named
  inside the existing network rows' descriptions. A trail is not a listing unless
  Scott wants that granularity.

---

# Close of pass — 68 rows, verified

| Type | Existing at start | Rows written | File |
|---|---|---|---|
| golf | 2 | **15** | `outdoors-golf.json` |
| rock climbing | 2 | **4** | `outdoors-rock-climbing.json` |
| cycling | 13 | **11** | `outdoors-cycling.json` |
| running | 16 | **7** (4 activities, 3 events) | `outdoors-running.json` |
| camping ground | 17 | **12** | `outdoors-camping.json` |
| skatepark | 19 | **9** | `outdoors-skatepark.json` |
| parks & playgrounds | 20 | **9** | `outdoors-parks-playgrounds.json` |
| mountain biking | 33 | **1** | `outdoors-mountain-biking.json` |
| | | **68** | |

`python3 scripts/sync.py check` passes clean on all eight files: 65 rows to
`activities`, 3 to `events`.

Kinds: 42 spot, 19 venue, 3 group, 3 happening, 1 shop.

## Verification actually run, not claimed

**Every one of the 61 coordinates written was reverse-geocoded after the batches
were finished**, in one pass, and the output checked against three failure modes
the project has already paid for:

1. **Fewer than four decimal places** — none. `sync.py check` also enforces this.
2. **A point that reverse-geocodes to bare "Victoria, Australia"** with no road
   and no suburb, which on this coast means open water — **none**. Every pin
   returned a road, a named feature or a street number.
3. **`type=administrative`** on the forward match — refused three times during
   the pass (Rippleside twice, Queenscliff Golf Club's first spelling once) and
   never written.

That pass changed five `source_note` fields, because Nominatim named the nearest
way differently on the second lookup: Winchelsea Golf Club (Schroeter vs Dwyer
Street), Gravel Pit Tor (Great Circle Drive vs Northern Range Walk), Big Rock
(Big Rock Road vs Big Rock Track), Bay Trail (Ritchie Boulevard), and Geelong
Cycling Club — which improved, reverse-geocoding to **"The Geelong Criterium
Track, Settlement Road"** and independently confirming the circuit the club says
it races on. The notes now say what was actually seen, twice.

## `any-weather` appears on ZERO of the 68 rows

Conditions written: `dry-ground` 50, `dry-trails` 12, `good-in-rain` 3,
`low-wind` 1, null 3.

The split follows the brief exactly: **`dry-trails` on unsealed ground** — dirt
jump lines, BMX loops, granite crag approaches, 4WD campground access, the
mountain bike park; **`dry-ground` on sealed or built ground** — skate parks,
shared trails, golf courses, playgrounds, campgrounds you drive into.
`good-in-rain` on the two indoor climbing gyms and the running shop, where it
does what it is for: promotes on a wet day, hides nothing. `low-wind` once, on
The Hill Mountain Bike Park, because the council itself names strong winds as a
reason not to ride it. The three nulls are the parkruns, matching the two
parkrun rows already in the database.

## Null fields, and why

- **`cost: null` on 12 rows.** Eleven are venues whose page publishes no fee
  (seven golf clubs, two athletics clubs, Lorne Country Club, Geelong Cycling
  Club) and one is Aire Crossing, which is non-bookable and says neither a fee
  nor that it is free. Where a fee *was* published it is quoted in `notes` and
  the band comes from it. Where the band is a tier rather than a quote — the
  Parks Victoria campgrounds, three championship golf clubs — **the
  `source_note` says so in those words.**
- **`url: null` on 1 row.** Barwon Valley Golf Club. No first-party site was
  found, OSM has no website tag, and a directory or a Maps link is not a
  substitute.
- **Pins: 61 written, 2 linked by `place_id`, 5 null.** The five are the three
  parkruns (no `places` row for their start lines), Ted Wilson Trail (a linear
  cycleway with no published trailhead car park), and nothing else.

## What the region genuinely cannot fill

- **rock climbing outdoors is the You Yangs and nothing else.** No Otway crag
  exists, no land manager sanctions the sea cliffs. The type's honest ceiling is
  the two Parks Victoria sites plus whatever indoor venues open in Geelong. It
  finished at 6 and that is the type, not a shortfall.
- **golf is the opposite of thin.** 21 courses enumerated, 15 written, 8 more
  logged with coordinates. Whoever wrote "golf (2)" into the reading order was
  reading the database, not the region.
- **parks & playgrounds cannot be finished at all** — Surf Coast Shire lists
  ~40 council playgrounds and the City of Greater Geelong says it manages 380
  play spaces. This type needs a policy on what earns a listing, not more hours.
- **mountain biking is genuinely well covered** and was left alone, as asked.
  Its problem is four broken pins, not missing rows.

## Everything the 43-type vocabulary had no word for

1. **BMX track / pump track / dirt jump line.** Six rows this pass. Written as
   `cycling`, or `cycling` + `mountain biking` where the jumps are the point.
   Neither word is right: a BMX loop is not mountain biking and a pump track is
   not "cycling" the way a rail trail is.
2. **Disc golf.** Barwon Valley Fun Park has a free 18-hole course open 24 hours.
   It is not `golf`. Filed under `parks & playgrounds` and tagged.
3. **Tennis.** Lorne Country Club runs bookable courts alongside its golf; the
   Surf Coast playground list includes "Anglesea Tennis Club". No word.
4. **Lawn bowls.** `Torquay Bowls Club` is already a `places` row with a feed,
   and Ocean Grove Bowls Club turned up in the skatepark audit. No word.
5. **Athletics / track.** John Landy Athletics Field, Geelong Athletics and
   Geelong Little Athletics are all written as `running`, which is the nearest
   word and not the right one — Little Athletics is javelin and long jump as much
   as it is running.
6. **Horse riding.** Kalkarra Park has a mapped horse riding area beside the BMX
   track. Nothing to file it under.
7. **Fishing.** Aire River East's own page sells it on the fishing; Point
   Lonsdale pier fishing is already in the database filed as `water`.
8. **An indoor-sport / simulator venue.** Fore Fun Golf Club, Ryrie Street
   Geelong, is a golf-simulator bar. `bar` plus nothing.
9. **Accessibility.** Not a type, but the same shape of gap the ocean pass found
   for beach patrol status: **"registered Changing Places facility", "all
   access", "accessible toilet" are the facts that decide a trip for some
   families, and they can only live in prose in `notes` where nothing can filter
   them.** Five rows this pass carry one. This is the second pass in a row to
   report it.

## For `places` — rows only Scott can add

1. **Geelong Cycling Club**, Russell Mockridge Pavilion, 1 Barwon Heads Road,
   Belmont, Geelong. `-38.1712085, 144.3513546`. Website `geelongcycling.com`.
   **`events_url` = `https://entryboss.cc/calendar/geelong`** — a permanent
   fixture feed, the same mechanism the August bike pass wired up for the
   mountain bike clubs, for the region's road and track club which was not
   among them. **This is the highest-value single item in this log.**
2. **Balyang Sanctuary**, 50 Marnock Road, Newtown, Geelong.
   `-38.1643286, 144.3306496`. Needed to pin Balyang Sanctuary parkrun.
3. **Barwon Estuary Picnic Area**, Peers Crescent, Ocean Grove 3226. **No
   coordinate found** — needed to pin Ocean Grove parkrun.
4. **Portarlington parkrun start**, The Esplanade, Portarlington 3223. **No
   coordinate found** — needed to pin Portarlington parkrun.
5. **John Landy Athletics Field**, 230 Swanston Street, South Geelong.
   `-38.1662381, 144.3601208`. Three rows written this pass sit on it; a `places`
   row would let them link instead of each carrying a copy.

## Existing rows that need a person — consolidated

**Wrong coordinates**

| # | Listing | Fault | Fix |
|---|---|---|---|
| 49 | `Moriac Skatepark` | pinned ~12 km away at 915 Blackgate Road, **Freshwater Creek** | `-38.2455631, 144.1710807` (Newling Reserve, 830 Hendy Main Road — the address in the row's own notes) |
| 44 | `Anglesea MTB – Hurst Rd / Eumeralla` | pin reverse-geocodes to **Point Roadknight**, a beach 6 km from Hurst Road | needs the Hurst Road trailhead |
| 16 | `Surf Coast MTB Trails – Ironbark Basin` | pinned **on Hurst Road** — i.e. on listing 44's network — while named for Ironbark Basin at Point Addis | probably Ironbark **Spur**, renamed and mispinned. Resolve before repairing |
| 38, 39, 42 | Forrest Southern, Forrest Yaugher, **Lorne & Otways** | all three share `-38.5238, 143.7259` (Kaanglang Road, Barramunga). The two Forrest networks are on opposite sides of town; Lorne is 35 km away | three separate trailheads |
| 50 | `Geelong Waterfront Skatepark` | pin is in the **Malop Street mall** (reverse: "Witchery"), 1.3 km from the water | the Poppy Kettle row written this pass gives the area: `-38.1427457, 144.3610991` |
| 54, 52, 58, 56, 57, 45, 46, 51 | Ocean Grove, Waurn Ponds, Corio, Leopold, Lara, Anglesea, Aireys Inlet, Djila Tjarri skateparks | 0.7 km to 3.9 km from the council's published address or OSM's named skatepark feature | see the skatepark audit table |
| 1, 5 | `Jan Juc Skatepark`, `Torquay Skatepark – Beach Rd` | `lat`/`lng` **null**, but a coordinate survives in the `url` — and Jan Juc's is the **2.3 km-offshore placeholder** CLAUDE.md says was cleared in August | Jan Juc: Bob Pettitt Reserve, 87 Sunset Strip. Torquay: 79 Beach Road = `-38.3259145, 144.3155063`, 16 m from OSM's named feature |

**Duplicates and near-misses**

- **51 `Djila Tjarri Skate Park` and 243 `Djilla Tjarri Play & Skate Zone`** are
  one place with two spellings. Surf Coast Shire spells it both ways on two of
  its own pages.
- **59 `Norlane Skatepark (North Shore)`** could be either of Norlane's two
  council skate parks. Resolve before applying the Fountain of Friendship row.
- **287 `You Yangs Rock Climbing`** is now a vaguer third copy beside Big Rock
  and Gravel Pit Tor. Retire or repoint at the park page.

**Wrong or weak URLs**

- **37 `Anglesea Bike Park – Camp Rd`** points at `trailsplus.com.au/ironbark-basin`,
  the same url as listing 16, for a different place.
- **Sixteen skatepark rows** carry `google.com/maps?q=<lat>,<lng>` and **61
  `Inverleigh Skatepark` carries a `google.com/maps/search/` link that
  `sync.py check` refuses today.** Both councils publish a real page for every
  one of these.
- **84 and 86**, the two existing parkruns, say `date_confidence: medium` and
  link an aggregator; both have first-party parkrun pages that make them high.

**Naming**

- **84 `Parkrun – every Saturday`** has no town in its name. With three more
  parkruns added it is unreadable. It is the Torquay one.

**Other**

- **`Jamieson Creek Campground`** is listed at Skenes Creek; OSM's only nearby
  feature is `Jamieson Track Camping Area` at **Separation Creek**, 25 km east.
- **`Bellarine Rail Trail`** and **`Old Beechy Rail Trail`** are typed
  `mountain biking` only and should carry `cycling`.
- **`Currawong Falls Circuit`** is a `walk`; Surf Coast Shire lists it as a
  shared *bike* trail. Argument logged in the mountain biking section rather
  than the row being moved.

## Vocabulary suburbs missing, found this pass

`Glenaire`, `Hordern Vale`, `Johanna`, `Yuulong`, `Wensleydale`, `Benwerrin`,
`Barramunga`, `Gellibrand`, `Barwon Downs`, `Clifton Springs`, `Newtown`,
`Rippleside`, `Moolap`, `Hamlyn Heights`, `Swan Island`, `Bambra`, `Modewarre`.
Each row that hit one says so in its `source_note` and ends its `location` with
the nearest town that IS in the vocabulary, per RESEARCH_RULES. **`Wensleydale`
is the one worth adding** — it holds three mapped campgrounds and a Parks
Victoria campground 40 minutes from Jan Juc, and the database already fudges it
once ("Aireys Inlet (hinterland)").
