# The hospitality — worklog

Pass started 26 Aug 2026, run from a Cowork cloud session. The Mac's local VM
has no network, so the scripts ran from the cloud against the live database;
this log was written back to the repo at the end of the pass.

## bakery — 26 Aug 2026

Had: Maple Bakery & Café (Torquay). Searched: venue sites, Broadsheet Geelong,
Visit Great Ocean Road, Yelp/AGFG for addresses, town strips one by one
(Torquay, Anglesea, Lorne, Barwon Heads, Ocean Grove, Queenscliff, Portarlington,
Geelong, Apollo Bay, Winchelsea, Freshwater Creek).

**Added (13, ids 293–305, all unverified):**
- Zeally Bay Sourdough — Torquay (bakery door, own-site hours quoted)
- Anglesea Bakery — Anglesea (81 GOR)
- Oaks Bakery Cafe — Anglesea (87 GOR; OSM POI)
- Starfish Bakery — Barwon Heads (own-site hours, closed Tue)
- Rolling Pin Pies & Cakes — Ocean Grove (Australia's Best Pie 2021/22/24; other outlets in notes, not separate rows)
- Apollo Bay Bakery — Apollo Bay (scallop pie; own-site hours)
- Brunch Box Lorne — Lorne (RENAMED from Great Ocean Road Bakery — kept both names in description; insta is still @greatoceanroadbakery)
- Louttit Bay Bakery — Lorne (est. 1993)
- Alchemy Woodfire Bakehouse — Queenscliff
- Bakery by Local — East Geelong (from The Local cafe)
- Born & Bread Bakehouse — Newtown/Pako (geocode is 364A next door — building-level, close enough; no 364 in OSM)
- The Portarlington Bakehouse — Portarlington (heritage scotch oven)
- Freshwater Creek Cakes — Freshwater Creek (OSM POI; directories say "650 Anglesea Rd Mt Duneed", filed under Freshwater Creek where the OSM POI sits)

**Rejected / left out:**
- Kentry's (Kenty's) Bakeries, Winchelsea — only Tripadvisor/restaurant-guru
  traces, no first-party presence found, spelling inconsistent. Not confident it
  is current. Revisit if someone local confirms.
- Rolling Pin outlets (Queenscliff, Drysdale, Leopold, Sth Geelong) — same
  business; kept as notes on the Ocean Grove row rather than five rows.
- No bakery found for Jan Juc or Bells Beach — believed true, not a search gap.
  (The same claim for Aireys Inlet was WRONG: Scott pointed at Le Comptoir
  Bakehouse, 85 Great Ocean Rd — added as id 363 later the same day. Lesson:
  town-strip searches miss venues whose name doesn't contain the town.)

**Suburb-vocab note:** Newtown and East Geelong are not in SUBURBS; wrote
locations as ", Newtown, Geelong" / ", East Geelong, Geelong" so suburbOf()
files them under Geelong.

## brewery — 26 Aug 2026

Had: Blackman's Brewery (Torquay). Places already held six brewery-kind rows,
five with no listing.

**Added (5, ids 306–310, all unverified):**
- Bells Beach Brewing — Torquay (own-site hours; matches existing place row, which has NO website on file — fill it, and it stages gigs: places/events_url candidate)
- Blackmans Brewery Geelong — Grovedale (kids play area; named to match place 92 exactly)
- Little Creatures Brewery — South Geelong (playground, tours; matches place row)
- Great Ocean Road Brewhouse — Apollo Bay, ["brewery","pub"] (Prickly Moses brewed onsite, pub since 1887; matches place row)
- Forrest Brewing Company — Forrest, ["brewery","cafe"] (NOTE: closed for winter, reopening 25 Sep 2026 per own site — noted on the row)

**Rejected / redirected:**
- Valhalla (Geelong) — entered voluntary administration (Crafty Pint news) and
  the Union St taproom is closing/closed per Forte. Status too unstable to list.
- Salt Brewing Co (ex Rogue Wave) — brews INSIDE the Aireys Pub, 425 Great Ocean
  Rd Aireys Inlet. Not a separate venue; handled in the pub pass as Aireys Pub
  ["pub","brewery"].
- Queenscliff Brewhouse — queenscliffbrewhouse.com.au now 302-redirects to
  esplanadequeenscliff.com.au: the venue trades as **The Esplanade Hotel
  Queenscliff** and its site no longer mentions brewing. Handled in the pub pass;
  places row 'Queenscliff Brewhouse' needs a rename/alias via /admin.
- Prickly Moses' own Otways cellar door (Barongarook) — outside the suburb
  vocabulary and their beer is poured at GOR Brewhouse anyway.

## pub — 26 Aug 2026

Had: two *events* typed pub (Birdy Bingo, Pub Trivia) and zero evergreen pub
listings. `places` already held eleven pub-kind rows — used their curated
addresses/coordinates where present (source_note on each row says so).

**Added (14, ids 311–324, all unverified):**
Torquay Hotel · Aireys Pub ["pub","brewery"] (Salt Brewing onsite) · Lorne Hotel
· Barwon Heads Hotel · Apollo Bay Hotel · Grand Hotel Portarlington · The
Esplanade Hotel Queenscliff (ex-Brewhouse, kids' play area, own-site hours) ·
Ocean Grove Hotel (fenced beer garden, own-site hours) · Wye Beach Hotel (Wye
River) · The Barwon Hotel (Winchelsea) · Mount Moriac Hotel (own-site hours) ·
Royal Mail Hotel (Birregurra) · Elephant & Castle Hotel · Barwon Club Hotel
(ages=adults, daypart=night — band pub, honest filing)

**Rejected / redirected:**
- Eureka Hotel Geelong — nightclub, no coordinate or website on file, wrong fit
  for a family what-to-do board.
- Gateway Hotel (Corio) — big suburban gig barn; music side is already covered
  by its place row. Left off the board; add later if pokies-pub listings are wanted.
- Last One Inn (Anglesea) — its own site presents an asado restaurant, not a
  pub ("authentic asado BBQ", Thu–Sat 4pm, Sunday asado). Moved to the
  restaurant pass. NOTE: own site says **113** Great Ocean Rd; places row 20
  says 143 — address discrepancy to fix via /admin.
- Queenscliff Hotel / Vue Grand (Queenscliff) — boutique accommodation and
  dining rather than pubs; Esplanade covers the town's pub slot.

**Near-duplicate thought:** "The Barwon Hotel" (Winchelsea) vs existing "Barwon
Heads Hotel" and "Barwon Club Hotel" — three different venues in three towns;
names kept as each venue styles itself.

**Places corrections for /admin:**
- places 28 'Queenscliff Brewhouse' → now trades as The Esplanade Hotel
  Queenscliff (add alias, update name/website esplanadequeenscliff.com.au).
- places 20 'Last One Inn' address 143 → 113 Great Ocean Rd per own site.

## bar — 26 Aug 2026

Had: The Whiskery, Flying Brick (both bar+produce, the cidery/distillery
convention) and the Point Break event. Eight bar-kind place rows, none listed.

**Added (9, ids 325–333, all unverified):**
- Bomboras — Torquay ["cafe","bar"] — its own site now sells "daytime dining",
  6am–4/5pm, so cafe leads; counts for Torquay cafe coverage too
- Bird Rock — Jan Juc ["bar","restaurant"] (own-site hours; Birdy Bingo's home)
- Cuda Bar — Lorne ["bar","restaurant"]
- Piping Hot Chicken Shop — Ocean Grove ["restaurant","bar"] — also a Music
  Victoria-listed venue: strong places/events_url candidate
- Saints & Sailors — Portarlington ["bar","restaurant"] (place row spells it
  "Saints and Sailors" — near-dup thought: same venue, listing uses the
  ampersand from their own branding; flag if it bothers the matcher)
- The 18th Amendment Bar, Piano Bar Geelong, Workers Club Geelong, Lambys
  Tavern — Geelong, all ["bar"], ages=adults, daypart=night, honest filing

**Rejected / discovered:**
- Growlers (23 The Esplanade, Torquay) — GONE. Nominatim returned "Ela" at that
  address; Broadsheet and Surf Coast Times confirm Ela, a new Greek/
  Mediterranean restaurant, has replaced it. Ela added in the restaurant pass.
- 4 Pines X Boardriders Torquay — place row with no kind; a taproom inside a
  surf shop. Left off the board pending a first-party check of current hours.

## cafe — 26 Aug 2026

Had: Gather, The Fives, Swell, Maple (2nd), Mavis Mavis, Pond. The brief said
Torquay, Jan Juc, Anglesea, Lorne, Barwon Heads, Ocean Grove, Queenscliff and
Geelong must all be represented before the type is done.

**Added (9, ids 334–342, all unverified):**
- Café Moby — Torquay (kid & dog friendly, Esplanade)
- 4 Kings Coffee & Food — Anglesea (lat/lng NULL — 63 GOR has no OSM house
  number or POI; left honest rather than guessed)
- Aireys Inlet General Store — Aireys Inlet ["cafe","shop"]
- Annie's Provedore — Barwon Heads ["cafe","produce"]
- Pasquini's Café & Deli — Point Lonsdale
- King of the Castle — Geelong West / Pako
- Hello Coffee — Apollo Bay (roaster; OSM POI, no house number published)
- Moriac General Store — Moriac ["cafe","shop"] (own-site hours)
- Common Ground Project — Freshwater Creek ["cafe","farm life"] — same venue as
  the farm place row; their events run via a Humanitix organiser page (feed
  candidate — Action only, ClaudeBot is disallowed on Humanitix)

**Town coverage after the pass:** Torquay (Moby, Mavis Mavis, Pond, Maple,
Bomboras) · Jan Juc (Swell, Bird Rock) · Anglesea (4 Kings, Oaks) · Lorne
(Brunch Box) · Barwon Heads (Annie's, Starfish) · Ocean Grove (Gather) ·
Queenscliff (Alchemy) · Geelong (King of the Castle, Born & Bread, Bakery by
Local) — all eight represented, plus Aireys, Pt Lonsdale, Apollo Bay, Moriac,
Freshwater Creek, Bellbrae.

**Rejected / uncertain — worth a local's eye:**
- Swing Bridge Cafe & Boathouse (Lorne) — an Instagram post reads "Formerly
  Lorne Swing Bridge Cafe, the Birregurra Grocer..." and GORCAPA news suggests
  an operator change. Status unclear; not added. If it has reopened it belongs
  here — the boathouse setting is exactly this site's kind of thing.
- Martians Cafe (Deans Marsh) — conflicting signals: a "Looks like it's closed?"
  Tripadvisor review vs Songkick gig listings. Not added; ask a local.
- The Willows Tea House (Aireys) — Facebook-only presence, currency unclear.
- Napona / Parade Espresso (Ocean Grove), Ocean Grind (Torquay) — real, but the
  towns are already represented; add on a future pass if depth is wanted.

## winery — 26 Aug 2026

Had: Jack Rabbit, Terindah, Leura Park, Scotchmans Hill, Basils Farm, Oakdene —
all Bellarine. Five winery-kind place rows, none listed.

**Added (9, ids 343–351, all unverified):**
- Bellbrae Estate — the Surf Coast's own cellar door (place row 6)
- Mt Duneed Estate — ["winery","restaurant"], Barrel Hall, summer concerts —
  places row 23 has NO website; fill mtduneedestate.com.au, and it is an
  events_url candidate (concert announcements)
- Provenance Wines — Fyansford paper mill (place row 27)
- Oneday Estate — Curlewis (place row 24)
- Bellarine Estate Winery — (place row 5)
- McGlashan's Wallington Estate — ["winery","brewery"] — FarmDog Brewing brews
  on the estate per their own site. lat/lng NULL (no OSM number/POI)
- Banks Road Vineyard — Marcus Hill ["winery","restaurant"] (OSM wine-shop POI)
- Brown Magpie Wines — Modewarre, pinot specialist
- Dinny Goonan Wines — Bambra ["winery"]. lat/lng NULL (address not in OSM)

**Rejected / out of scope:**
- Clyde Park, Austins & Co, Lethbridge Wines — Moorabool Valley (Bannockburn/
  Sutherlands Creek/Lethbridge): no suburb in the vocabulary and genuinely a
  different sub-region. If the Moorabool Valley is ever wanted, that is a
  vocabulary decision first (log rather than force — per RESEARCH_RULES).
- Yes said the seal — poured at Flying Brick; not a separate cellar door row.
- Spray Farm (Bellarine) — events estate, not a standing cellar door.

**Suburb-vocab note:** Modewarre, Marcus Hill and Bambra are not in SUBURBS —
locations written to carry Moriac / Bellarine / (bare Bambra) respectively.
Dinny Goonan's location contains "Winchelsea-Deans Marsh Road", and suburbOf()
matches the "Deans Marsh" inside it (longest-first, hyphen counts as a
boundary), so it files under Deans Marsh — accidental but correct enough.

## restaurant — 26 Aug 2026

Had: Sora plus winery secondaries and two events. Everything below is a place a
family (or a date night) would actually drive to.

**Added (11, ids 352–362, all unverified):**
- Ela — Torquay ["restaurant"] — NEW, in Growlers' old room at 23 The
  Esplanade; no own website found yet, Maps-search placeholder used per policy
- Last One Inn — Anglesea ["restaurant","bar"] — asado; own site says 113 GOR
  (places row says 143 — fix)
- The Bottle of Milk — Lorne (Torquay outpost noted on the row)
- Captain Moonlite — Anglesea SLSC — coordinate reused from place 45; a
  'Save Captain Moonlite' petition exists (undated) — someone should confirm
  current trading before verifying this row
- A La Grecque — Aireys Inlet (Wed–Sun per own posted notice)
- Ipsos — Lorne (same family, next generation)
- At The Heads — Barwon Heads (OSM POI on Jetty Rd)
- The Dunes Ocean Grove — Surf Beach Rd
- 360Q — Queenscliff Harbour
- Chris's Beacon Point — Skenes Creek (fifty years of Talimanidis cooking)
- The Q Train — Drysdale ["restaurant"] — dining train; geocoded to the station
  precinct (playground POI), not the platform

**Rejected / left for later:**
- Igni (Geelong) — status not confirmed this pass; add after checking it still
  runs (Aaron Turner's projects move).
- Wah Wah Gee / Fishermans Pier (Geelong waterfront) — real, but Geelong
  restaurant depth felt less urgent than coast coverage; next pass.
- La Bimba (Apollo Bay) — not verified this pass.
- Samesyn (Torquay) — new fine diner, worth a look next pass.

## Pass summary — 26 Aug 2026

61 rows added, all `verified = false`, all `added_by = 'Research'` → they are
sitting in `sync.py pending` / the /admin queue. Type counts (a row counts in
every type it carries): bakery 1→14 · brewery 1→8 · pub 2→17 · bar 3→14 ·
cafe 6→27 · winery 6→15 · restaurant 7→24. Group total 26 → 119.

### Venues worth a `places` row / events_url — for /admin
- **Bells Beach Brewing** (place exists, Torquay) — no website on file; set
  website bellsbeachbrewing.com.au. They stage gigs and film premieres.
- **Mt Duneed Estate** (place 23, Waurn Ponds) — no website on file; set
  mtduneedestate.com.au. Summer concert announcements = feed candidate.
- **Piping Hot Chicken Shop** — NEW place candidate, Ocean Grove,
  pipinghotchickenshop.com.au — Music Victoria-listed venue, regular gigs.
- **Common Ground Project** (place exists, Freshwater Creek) — events run via a
  Humanitix organiser page; register the /o/ page as events_url (Action reads
  Humanitix; a Claude-driven run must --skip humanitix).
- **Grand Hotel Portarlington** (place 17) — website field already points at
  /whats-on/; consider copying it into events_url so the scraper reads it as a
  feed rather than a convenience guess.
- **Great Ocean Road Brewhouse** (place 18) — live entertainment weekly per own
  site; site has an entertainment page worth pinning as events_url.

### Places corrections — for /admin
- place 28 'Queenscliff Brewhouse' → trades as **The Esplanade Hotel
  Queenscliff**; rename or alias, website → esplanadequeenscliff.com.au.
- place 20 'Last One Inn' → address 113 (not 143) Great Ocean Rd per own site.
- place 10 'Bomboras' — fine, but note the venue now presents as daytime dining.

### Near-duplicates thought about, resolved
- Blackmans Brewery Geelong (listing 307) vs Blackman's Brewery (listing, Torquay)
  vs places 49/92 — two real buildings, names matched to their place rows.
- Saints & Sailors (listing) vs 'Saints and Sailors' (place 29) — same venue,
  ampersand from their own branding.
- The Barwon Hotel (Winchelsea) vs Barwon Heads Hotel vs Barwon Club Hotel —
  three venues, three towns, all real.
- Common Ground Project listing vs place row — same venue, deliberate (the
  Gather pattern).
- Ela vs Growlers — same address, different venue; Growlers is closed and was
  never listed, so nothing to merge.

### Left open
- 4 Kings Coffee & Food and McGlashan's and Dinny Goonan have NULL pins (no OSM
  match at their addresses) — a phone-pin pass would fix all three.
- Swing Bridge Cafe (Lorne), Martians Cafe (Deans Marsh), Captain Moonlite
  (lease question), Igni (Geelong) — need a person or a later pass.
- Geelong restaurant/bar depth deliberately thinner than the coast; next pass.

## bakery addendum — 26 Aug 2026, from Scott

- **Le Comptoir Bakehouse** — Aireys Inlet, 85 Great Ocean Rd (id 363,
  unverified). French bakery, everyday 7am–2:30pm, own-site sourced, geocoded
  house-level. Corrects the pass's wrong claim that Aireys had no bakery.

# Round two — the depth pass (26 Aug 2026)

Unit of work is the town, driven by `scripts/nearby.py`'s Overpass sweep. The
egress proxy only admits ~1 in 5 connections to overpass-api.de, so the sweep
ran through a keep-alive tunnel helper (sweep.py, session-local) that retries
until a connection sticks and then reuses it; the reports are nearby.py's own
matching, unchanged.

## round two — Torquay (+ Jan Juc spillover)

OSM: 55 named, 9 already listed, 46 not. **Added 17 (ids 364–380):**
Salty Dog Cafe · Fisho's · Bell Street Fish & Chips · Bells Bakery · 9grams ·
Ginger Monkey · Mikro Coffee Roasters (OSM says Baines Cres, a directory says
57 Geelong Rd — flagged on the row) · Bob Sugar · Il Matto · Italo's ·
Pholklore · Samesyn · Third Wave Kiosk · Surfside Patisserie · Sandbah ·
Solhouse · The Cave Woodfired Pizza (actually Jan Juc — Princes Tce, beside
Bird Rock).

Chains skipped: KFC, McDonald's, Subway, Zambrero, Betty's Burgers, La
Porchetta, Bakers Delight, Squires Loft, Routleys (regional chain).
Matcher notes: "Swell Foods & Coastal Catering" is Swell Café (OSM name);
"The Beach Hotel" was FALSE-matched to Wye Beach Hotel — but the venue itself
could not be confirmed to exist in Torquay VIC at all (UK-Torquay pollution);
left unadded, someone local should say what OSM is pointing at.
Checked, not added (no first-party confirmation or ends-up category):
Las Olas (TA-only, may be closed) · Torquay Larder · Villa & Hutt · Panache ·
Norden Fine · frenchy's · Point Danger Beach House (Surf Coast Times mention
only) · Dough Bros · Flippin' Fresh · Jashin Courtyard · Rokuden · Sober Ramen
· Torquay Thai · Lentil's Indian · Sizzling Indian · Quicksilver Bar 61 ·
Zeally's Bar & Grill.

## round two — Geelong (all strips)

Swept Geelong at 4000m plus Geelong West, Newtown, Belmont, Grovedale, Waurn
Ponds and South Geelong separately. OSM knows **383 named venues inside 4km**
of the CBD alone; "take every name" is not an honest instruction against a
regional city, so the judgment applied was the site's own test — venues a
family or a visitor would *go to Geelong for*, not a business directory.

**Added 19 (ids 381–399):** Fisherman's Pier · Wharf Shed Cafe · The Yot ·
Igni · The Continental (own-site service times) · ALMA · The Hot Chicken
Project · Sober Ramen · Geelong Cellar Door · Union Street Wine · Little Green
Corner · Winter's Cafe (Pako/Newtown) · Cartel Roasters · James Street Bakery
· Mavs Greek · Das Bierhaus · Hecho En Mexico · Tulip (site live but
rate-limited — confirm hours) · Ket Baker (WALLINGTON original, Belmont
second store in notes).

Notable and deliberately left for a future pass (all real, all with sites):
Bistrot St Jean / Bistrot Plume / La Cachette (the French cluster), Caruggi,
Baah Lah, Osteria Fiorenza, Empire Grill, Lipari, Justin Lane, Rook, frankie,
Sweet Cheeks, There There, Non Disclosure Bar, Archive Wine Bar, Beav's Bar,
Murphys, Malt Shovel Taphouse, The Arborist, The Paddock Bakery (franchise),
Panache Cafe & Creperie (couldn't read site — is this the ex-Queenscliff
creperie?), plus ~60 suburban fish-and-chippers, kebab shops and franchise
outlets that fail the "reason to go" test. Geelong depth is now defensible but
not exhausted — the log above is the shortlist for round three.

Matcher note: "Geelong Bakehouse" was FALSE-matched to "The Portarlington
Bakehouse" (shared word 'bakehouse' + both keyword sets small) — Geelong
Bakehouse itself was not assessed; and "The Brewery" at geelong.bellsbeachbrewing.com.au
is apparently a Bells Beach Brewing Geelong venue — worth a person's look, that
is news to this database.

## round two — Anglesea

OSM: 17 named, 2 listed, 15 not. **Added 6 (ids 400–405):** Love House
(["restaurant","bar"], the surf club's restaurant — **supersedes Captain
Moonlite, id 355: same building, new operator; 355 needs /admin removal or a
closed note**) · Klein's Anglesea Hotel (["pub"], 1 Murch Cres, kids play area
— the pub the whole first pass missed) · Morgans Bar & Grill (live acts — gig
feed candidate; address discrepancy OSM 12-14 vs listings 87 GOR) · Minerva &
the Bean · Umisango Anglesea (sister room in Lorne) · Fish by Moonlite.

Checked, not added: Cannoli 73, Coast Side Cafe, Nördenfine Ice Cream, Uber
Mama, Anglesea Pizza & Pasta, Anglesea Fish & Chips (second chippy), Jums
Chicken, Yo! Chicken, Four Kings Crepe (no first-party trace / ends-up
category). The "Anglesea Pub" OSM tag is Klein's Anglesea Hotel — the prompt's
warning about contributor labels was right.

## round two — Lorne

OSM: 27 named, 3 listed, 24 not. **Added 6 (ids 406–411):** Totti's Lorne
(Merivale's Italian in the Lorne Hotel — **MoVida Lorne closed permanently;
OSM tag stale**; Lorne Hotel row 313 should note Merivale ownership + Totti's)
· Lorne Beach Pavilion · Umisango Lorne (lat/lng NULL — not in OSM, needs a
pin) · Moons Espresso & Juice Bar · Mexican Republic · The Salty Dog Fish &
Chippery (no relation to Torquay's Salty Dog Cafe — logged as the near-dup
thought).

Checked, not added: The Larder (it is Mantra Lorne's in-house brasserie),
Swingbridge Cafe (STILL unresolved — OSM lists it, but its old operators
announce themselves as the Birregurra Grocer now; a person should walk past),
Grandma Shields Bakery (OSM VIC tag conflicts with Tripadvisor's Lorne NSW —
suspect bad import), Lorne Central, Maple Tree Seafood, Almyra, Saporitalia,
Mestizio, Riverbank, Lorne Bowls Club, Lorne SLSC cafe, Summer Garden Bar
(probably the Lorne Hotel's own garden), Chopstix, Pizza Pizza, Milkbar,
Andrews Chicken Joint, Pit stop, Health & Hire kiosk.

## round two — Ocean Grove

OSM: 29 named, 3 listed, 26 not. **Added 6 (ids 412–417):** The Dill ·
The Covenant Wine Bar · The Driftwood Café · Paradise Parlour (ice cream,
conditions=warm) · Hello Birdie (family cafe, Grubb Rd) · Alchemy Bakehouse
(71 Madeley St — DISTINCT from Queenscliff's Alchemy Woodfire Bakehouse,
near-dup noted on the row).

Checked, not added: Chang Noi Thai, King Koi, Ming Terrace, The Mex, Woodies
Pizza, OG Pizza & Pasta, both unnamed fish'n'chip shops, Bean Squeeze
(drive-through chain), Betty Blue Coffee Van, Groove, Parade Espresso Bar,
Kiosk, Ocean Grove Bowls Club, The Olive Pit (deli — produce pass), The Beach
House Lolly Shop (confectionery — belongs to a produce/shop pass, noted there).

## round two — Barwon Heads

OSM: 11 named, 3 listed, 8 not. **Added 3 (ids 418–420):** Barwon Orange (OSM
misspells it "Bacman Orange") · Bakery Bar & Lounge (old bakery building,
pizza-bar) · Gilligan's Fish & Chips.
Matcher false negatives handled: "Annie's Provedore & Produce Store" is
already listed (Annie's Provedore); false-positive: matcher paired Barwon Heads
Hotel with "Barwon Heads Skatepark" — the hotel is listed, no harm done.
Checked, not added: Shack Dining Co. (no trace found), Australian Ice Cream
Company (van), Kebabs on the Coast, Barwon Heads Fish & Chips (second chippy).

## round two — Queenscliff

OSM: 8 named, 1 listed, 7 not — OSM is visibly thin here (no Alchemy, no
Esplanade Hotel, no Athelstane House in its data; the sweep's own blind spot).
**Added 3 (ids 421–423):** Trident Fish Bar · Panache Cafe & Creperie (68
Hesse St — likely the creperie remembered from older Queenscliff guides; its
domain would not render, flagged on the row) · Willow Tree Cafe.
Checked, not added: Rip View Bistro (the bowls club's bistro), Wharf St Pantry
and Ocean View Kiosk (no first-party trace), Scully's fish & chippery (second
chippy; Trident is the town's).

## round two — Aireys Inlet

OSM: 9 named, 2 listed, 7 not. **Added 5 (ids 424–428):** Skinny Legs Cafe &
Deli · The Captain of Aireys · Mr T & Me (lat/lng NULL — Nominatim only offers
the town centroid) · Onda Food House · The Lighthouse Tea Rooms (own-site
hours). All three of nearby.py's docstring known-misses are now in. "Le
Comptoir" reported missing = Le Comptoir Bakehouse, already listed (matcher
bias working as designed). Not added: Aireys Inlet Fish & Chips (no
first-party trace).

## round two — Apollo Bay

OSM: 24 named, 2 listed, 22 not. **Added 4 (ids 429–432):** Apollo Bay
Distillery ["bar","produce"] · Apollo Bay Seafood Cafe · Apollo Bay
Fisherman's Co-op ["restaurant","produce"] (NOT IN OSM at all — found by the
main-street double-check; lat/lng NULL, pin needed) · Dooley's Premium Ice
Cream. GOR Brewhouse's OSM listing appears as bare "Brewhouse" (matched fine).
Checked, not added: Casalingo, Sandy Feet, Waves, Coco, Iluka, George's, Rawr
Bar, Icaro, Tiki Bar/Cafe 153, Dragon Bay Inn, Masala Bay, Chopstix ×2, lolly
shop (produce pass), The Harbour Fish Shop (Co-op covers the harbour), The
Icecream Tub (=Dooley's second door). La Bimba still unassessed — not in OSM
either; round three.

## round two — the hinterland and Bellarine small towns (part 1)

**Added 8 (ids 433–440):**
- Birregurra: **Brae** (Dan Hunter — how was this not in the database?), Yield
  Restaurant & Providore, Otway Artisan Gluten Free (fully GF bakery).
- Curlewis/Drysdale: Claribeaux (Curlewis Golf Club), Ground Zero Cafe.
- Bellarine: Bennetts on Bellarine, Baie Wines (both small cellar doors).
- Armstrong Creek: Town and Country Pizza (Warralily).

**Nothing-there towns established by sweep (a real answer, one command each):**
Bells Beach (0 food venues in OSM — correct, it's a beach), Breamlea (0),
Cape Otway (0 — lightstation cafe not in OSM; known gap, it's a `places`/
attraction question), Connewarre (0), Cumberland River (0 — the campground
kiosk is not in OSM), Eastern View (0), Moggs Creek (0), Little River (0 in
radius — town centre is beyond), Indented Head (0 — OSM thin, see below),
Kennett River (0 — WRONG, the Kafe/kiosk exists; OSM gap, see part 2),
Point Addis (0), You Yangs (0), Freshwater Creek (all listed already).

**Checked, not added:** The Ridge Organic Store (Beech Forest) — CLOSED per
Foursquare/Yelp, so Beech Forest honestly has nothing; Art Reach Studio
(gallery, marginal); Salt Brewing Co "Deans Marsh" (OSM tag but
saltbrewing.co/deans-marsh 404s — stale, log only); Bowside Cafe (Bellbrae,
no trace); Cottage@Iona (Armstrong Ck, no trace); Café Zoo + Bungalow
(Drysdale — real, roadside, round three); Enchanted Tastes (Birregurra).
Matcher false negatives correctly skipped: "Jack Rabbit Winery"=Jack Rabbit
Vineyard, "Le Comptoir"=Le Comptoir Bakehouse, "Forrest Brewery (Company)"=
Forrest Brewing Company, Fairhaven's list = Aireys' venues re-reported.

## round two — small towns (part 2)

**Added 17 (ids 441–457):**
- Inverleigh: Inverleigh Hotel. (Matilda's — no current trace; log.)
- Wye River: Wye River General Store (the prompt called it, OSM had it).
- Kennett River: Kafe Koala General Store — NOT in the OSM food sweep (tagged
  as a convenience shop); found by the town double-check, as predicted.
- Winchelsea: Winchelsea Tavern (20 Willis St — the town's SECOND pub,
  distinct from The Barwon Hotel; Yelp calls it Winchelsea Hotel).
- Lavers Hill: The Perch at Lavers Hill. (McDuff's Bakehouse — maps-only
  trace; YatZies, Otway Junction Motor Inn — log.)
- Point Lonsdale: Noble Rot Wine Store & Bar (OSM's anonymous "Wine Store &
  Bar"; own-site hours). Cafe 3225, Lix Cafea — log.
- St Leonards: St Leonards Hotel by the Sea (placeholder url — no site found)
  · Salty Cow · Lenny's Ice Creamery. (Two Daughters, St Leonards Bakery,
  Shugar Beach, chippies — log; the Murradoc strip is deeper than expected.)
- Wallington: The Paddock Cafe.
- Lara: Millar's Café (Westlakes) · Lara Hotel. (Founders and Co, Rod's
  Bakery — real, round three; the rest of Lara's list is franchise sprawl.)
- Portarlington: Pier St · Edina Waterfront Cafe · The Little Mussel Cafe
  (Advance Mussel's farm-gate cafe, ["cafe","produce"]).
- Werribee: Teddy Picker · Bridge Hotel Werribee — enough to feed a zoo day,
  which is why Werribee is in the Place menu at all.

**Leopold and Mt Duneed:** deliberately zero adds — both lists are franchise
and takeaway sprawl (Rolling Pin's Leopold outlet already noted on the Ocean
Grove row; Mt Duneed Estate already listed). Melaleuka Bakery (Leopold) is the
one worth a round-three look.

## round two — Little River addendum

OSM food sweep said 0 — wrong: **The Little River Hotel** exists (tagged as
tourism/hotel, invisible to the food query). Added as id 458. Second case
(with Kafe Koala) of the sweep's tag blindness: pubs tagged `hotel` and cafes
tagged `convenience` do not answer an amenity=food query. Worth remembering
for the next nearby.py revision — or adding tourism=hotel to the KINDS.

## Round two summary — 26 Aug 2026

**95 rows added (ids 364–458), all unverified, all `added_by = 'Research'`.**
The hospitality group now carries: cafe 65 · restaurant 66 · bar 25 · pub 24 ·
bakery 21 · winery 17 · brewery 8 (a row counts in every type it carries).
Every one of the 47 Place-menu towns has been through the loop, plus six
Geelong strips swept separately.

**Rows per town (round two):** Torquay 16 · Geelong (all strips) 18 ·
Portarlington 3 · St Leonards 3 · Aireys Inlet 5 · Anglesea 6 · Lorne 6 ·
Ocean Grove 6 · Apollo Bay 4 · Barwon Heads 3 · Queenscliff 3 · Birregurra 3 ·
Lara 2 · Werribee 2 · Bellarine 2 (+ Baie at Curlewis) · Curlewis 2 ·
Drysdale 1 · Jan Juc 1 (The Cave) · Wallington 2 (Ket Baker, Paddock) ·
Inverleigh 1 · Wye River 1 · Kennett River 1 · Winchelsea 1 · Lavers Hill 1 ·
Point Lonsdale 1 · Little River 1 · Armstrong Creek 1 · Freshwater Ck 0 (done
round one) · Moriac 0 (done round one) · genuine zeros: Bells Beach, Breamlea,
Cape Otway, Connewarre, Cumberland River, Eastern View, Moggs Creek, Point
Addis, You Yangs, Indented Head, Beech Forest (store closed), Bellbrae (extra),
Deans Marsh, Forrest, Leopold, Mt Duneed, Fairhaven (=Aireys).

**Where OSM was thinner than reality:**
- Queenscliff (8 names for a whole tourist town; no Alchemy, no Esplanade)
- Kennett River & Little River (venues tagged shop/hotel, invisible to a food
  query — Kafe Koala and the Little River Hotel both found by hand)
- Apollo Bay harbour (Fisherman's Co-op absent entirely)
- Umisango Lorne, La Bimba (Apollo Bay), Swing Bridge (Lorne) absent
- Indented Head shows zero — believed nearly true (general store only), but a
  local should confirm.
- OSM staleness caught: "Movida Lorne" (now Totti's), "Growlers" (now Ela,
  round one), "The Ridge" Beech Forest (closed), "Salt Brewing Deans Marsh"
  (404), "The Beach Hotel" Torquay (unidentifiable).

**Existing rows needing /admin correction (do not script-edit):**
- **355 Captain Moonlite** — superseded by Love House (400) at the Anglesea
  SLSC. Remove 355 or mark closed; the petition explains itself now.
- **313 Lorne Hotel** — now a Merivale venue; add Totti's note, check
  lornehotel.com.au still resolves (may redirect to merivale.com).
- places 28 'Queenscliff Brewhouse' → The Esplanade Hotel Queenscliff (round
  one finding, still open).
- places 20 'Last One Inn' → 113 Great Ocean Rd (round one finding).
- 370 Mikro Coffee Roasters — OSM (Baines Cres) vs directory (57 Geelong Rd)
  address conflict, flagged on the row.
- 402 Morgans Bar & Grill — OSM 12-14 vs listings 87 Great Ocean Rd.

**Null pins needing a person (7):** 4 Kings (335), McGlashan's (348), Dinny
Goonan (351), Umisango Lorne (408), Mr T & Me (426), Apollo Bay Fisherman's
Co-op (431), plus Ela's url is still a Maps placeholder (352).

**places/events_url candidates from round two:**
- Piping Hot Chicken Shop (round one, still standing)
- Morgans Bar & Grill, Anglesea — hosts live acts
- Bells Beach Brewing GEELONG (?) — geelong.bellsbeachbrewing.com.au appeared
  in OSM as "The Brewery": if Bells Beach Brewing has opened a Geelong venue,
  that is both a listing and a place row nobody has
- Totti's/Lorne Hotel under Merivale — merivale.com will carry what's-on pages
- Lorne Beach Pavilion, Wharf Shed, Little Creatures — event-capable venues
  already having sites worth a feed look on /admin.

**Round three shortlist (logged, verified-adjacent, not added):** the Geelong
French cluster (Bistrot St Jean, La Cachette, Bistrot Plume), Caruggi, Rook,
frankie, Empire Grill, Archive Wine Bar, There There, Sweet Cheeks, La Bimba,
Casalingo, Sandy Feet, Founders and Co (Lara), Rod's Bakery (Lara), Melaleuka
Bakery (Leopold), Café Zoo + Bungalow (Drysdale), Two Daughters + St Leonards
Bakery, Cottage@Iona, Torquay's long tail (Las Olas, Larder, Villa & Hutt,
frenchy's, Point Danger Beach House, Norden Fine).
