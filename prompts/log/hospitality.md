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
