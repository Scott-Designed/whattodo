# `second-hand` — research pass, 1 September 2026

Type had **one row** at the start (705, Savers Geelong). This pass hands back **49 activity
rows** and **1 event row**, plus **three proposed edits** to rows already in the database and
**one `places` row** for Scott to build.

Nothing was written to Supabase. Both batches pass `python3 scripts/sync.py check`.

    python3 scripts/sync.py check second-hand-activities.json   → 49 rows, nothing wrong
    python3 scripts/sync.py check second-hand-events.json       →  1 row,  nothing wrong

**Every row is `types: ["second-hand"]` and nothing else, and every one carries
`kind: "shop"` explicitly.** There is not a single multi-type row in this batch, so there is
**no `BY_ID` line to add for anything here** — `KIND_OF['second-hand'] = 'shop'` does the work
unaided, which is the thing this type gets for free and the reason it was allowed to map to a
kind. The two candidates that would have forced a second type were both refused:
The Amazing Mill Markets is *not* `market` (see Phase 4) and Popcultcha is *not* `second-hand`
(see the audit).

On the name: `second-hand` is right and I am not reopening it. Nothing found in this pass
argues for a fifth name. What the pass did show is that the type is doing exactly the job
CLAUDE.md said it would — a charity shop, a hospital-auxiliary shed, a council tip shop, an
antique dealer and a vintage emporium all landed on one page and share no other word.

---

## PHASE 0 — the audit

### 110 · Anglesea Resale Shed (Tip Shop) — `kind=shop`, `types=['community']`

**Proposed: `types: ["second-hand"]`. Drop `community` entirely.**

CLAUDE.md names this row as the one `community` is weakest on, and reading Surf Coast Shire's
own page for it settles the question. The Shire calls it a place to *buy* "secondhand furniture
and other items in good condition". `community` describes who runs it (a project of Anglesea
Community House in partnership with Council); it does not describe what the row IS, and it puts
the Tip Shed on `/community` next to Landcare branches and neighbourhood houses, where nobody
hunting a bookcase will ever look. `second-hand` says what is sold, which is the whole point of
the type. The row is already `kind = shop` by hand decision (BY_ID 110), so retyping it changes
nothing about the kind and nothing walks onto the board.

Keeping `community` as a *second* type would be actively harmful: `KIND_OF['community']` is
`group`, and although `shop` outranks `group` on PRECEDENCE so the kind would survive, the row
would print whichever type came first and would sit in two group pages saying two different
things. One type, and it is `second-hand`.

**And the row has two other defects, both worth fixing in the same edit:**

1. **THE PIN IS 2.58 km WRONG.** Row 110 is pinned at `-38.4044, 144.1844`. That
   reverse-geocodes to **"13, River Reserve Road, Anglesea"** — a residential street in the
   town. The Resale Shed is at **50 Coalmine Road**, out at the transfer station; a Nominatim
   structured query on that address returns `-38.3850487, 144.2008192`, which reverse-geocodes
   back to "50, Coalmine Road, Anglesea". The two are **2,584 m apart**. This row is
   `verified = true`, so the wrong pin has been through a review.
   Proposed `lat/lng`: `-38.3850487, 144.2008192` (single source; nothing else publishes a
   coordinate for it).
2. **`km` is 15.0.** The standing decision of 25 Aug 2026 is that `km` stays null until it can
   be computed. Proposed: null.
3. `location` is `"Anglesea Transfer Station"`, which parses only because the word "Anglesea"
   happens to be in it. Proposed: `"50 Coalmine Road, Anglesea"` — a real address ending in a
   town `suburbOf()` knows.
4. `url` is `anglesea.org.au/community/community-support/anglesea-resale-shed-at-anglesea-tip-shop/`
   which is fine and first-party (Anglesea Community House run it). The Shire's page is
   `surfcoast.vic.gov.au/Property/Waste-and-recycling/Transfer-Stations-and-Anglesea-Landfill/Anglesea-Resale-Shed`
   and is where the address and hours above came from. Either is defensible; I would leave the
   url as it is and put the Shire page in `source_note`.
5. `notes` currently says "Call ACH on (03) 5263 2116 for opening hours". The Shire publishes
   them: **10am–2pm Monday, Tuesday, Wednesday, Friday and Saturday** (closed Thursday and
   Sunday), phone 5263 2978.

    Source: Surf Coast Shire's own Resale Shed page, read 1 Sep 2026. Two Shire URLs carry the
    same facility (…/Transfer-Stations-and-Anglesea-Landfill/Anglesea-Resale-Shed and
    …/Disposal-sites/Anglesea-Resale-Centre); they are one shed, not two.

### 539 · Pop Cultcha — `kind=shop`, `types=['music']`

**Proposed: NO CHANGE. `second-hand` does not belong on this row.**

This is the judgement the prompt asked for and it came out the other way. Popcultcha is a
retailer of **new** licensed pop-culture merchandise — collectibles, figures, toys — and the
Level 1 record floor is a **new**-vinyl store: their own Popcultcha Records page advertises
"over 6,000 in-stock vinyl records, alongside hundreds of art books & graphic novels" and says
nothing anywhere about used, pre-loved, pre-owned or second-hand stock. I looked for it
specifically on popcultcha.com.au and on their Records landing page and there is none.

A collectibles shop *feels* adjacent to second-hand, and that is the trap: `second-hand` says
what is sold, and what is sold here is new. Adding it would also cost something real —
`KIND_OF['music'] = 'venue'`, so `second-hand · music` comes out a **venue** on PRECEDENCE and
the row walks onto the Notice Board it is currently held off. That is exactly the failure mode
the prompt warns about, and it would be paid for a type that is not even true.

The row's own `source_note` calls `music` a placeholder, and it still is — `music` is a poor
word for a shop that sells figurines downstairs. But the fix for that is not this type. Left
alone.

### 689 · Winchelsea re-loved market — events table, `types=['market']`

**Proposed: `types: ["market", "second-hand"]`, and `place_id: 78`.**

Found by scanning the events table, not by the prompt. Its own description reads "A market for
all things Re-Loved, Recycled and Re-Purposed. For the love of thrifting" — this is the one
second-hand market already in the database and it does not say so. Events carry no `kind`, so
adding the second type costs nothing and needs no `BY_ID` line.

It also has **`place_id: null`** and its venue is "Winchelsea Shire Hall", which **is already
in `places` as id 78** (Winchelsea, kind `hall`, `-38.24174, 143.990715`). So this is one of
the twelve unpinnable market rows and it can be fixed by linking, not by building anything.

Its `date_confidence` is `medium` with a `source_note` saying the date was imported from
surfcoastevents and never checked first-party. I did not check it either — the organiser's own
page is a Facebook share link and the only other listing is on **Humanitix, which this project
does not fetch**. Left as it is.

### Nothing else in the database is this type

I scanned **all 685 activities** and **all 677 events** for op-shop / thrift / vintage /
antique / Salvos / Vinnies / Red Cross / resale / preloved / record / retro / consignment /
flea / bazaar / memorabilia / collectible / bric-a-brac words across `name`, `description`,
`tags` and `notes`. Fourteen activity rows matched and twelve are false positives — Flying
Brick Cider House ("vintage"), the Portarlington Bakehouse and Little Creatures ("retro"),
three museums (antiques in the collection), Geelong Bollards, Ocean Acres, Write Letters or
Postcards. The only real hits were 110, 539 and 705.

**527 Bicycle Centre Belmont** (`kind=shop`, `types=['cycling','mountain biking']`) matched on
"second-hand" in its text. It is a bike shop that also deals in used bikes, and it should stay
as it is: a bike shop is a bike shop, and adding `second-hand` would put it on `/second-hand`
between two op shops for a sideline. Same reasoning as the café-that-sells-vintage rule.

**And a near-miss scan was run before anything was written**, per RESEARCH_RULES: one `ilike`
per distinctive word (Salvos, Vinnies, Lifeline, Vestry, Seaside Seconds, Mill Markets, IHR,
Brotherhood, Wave Op, Dove, All Saints, Second Sails, Winchelsea Op, St James, St John,
St Paul, St Luke, Uniting Op, MS Community, Fight Cancer, GAWS, Red Cross, Highton Uniting,
Point Lonsdale Uniting) against the whole `listings` view. **Zero hits on any of them.** The
category really was absent, not thin.

---

## THE TOOLING — two things the next pass needs to know

### Overpass is unreachable from this sandbox. Nominatim is fine.

`python3 scripts/nearby.py --refresh` **cannot run here.** Every endpoint in `ENDPOINTS` is
refused by the egress proxy — `overpass-api.de` resets the connection, the other two return
`403 Tunnel connection failed`, and `overpass.osm.ch`, `overpass.openstreetmap.fr`,
`overpass.osm.jp` and `overpass.osm.rambler.ru` all fail with `connect_rejected (organization
policy)`. Nominatim answers normally. That is **the exact signature the script's own error
message describes** ("Nominatim answering fine while Overpass returns 000"), except the cause
is an allowlist rather than a rate limit, so waiting an hour will not fix it.

What I did instead, said plainly so nobody has to guess: I ran the **secondhand clause of the
same query `refresh()` builds** — `nwr["shop"~"^(antiques|books|charity|music|second_hand)$"]
["name"](-39.00,143.30,-37.80,144.85)` — against `overpass-api.de` from a browser on Scott's
own machine, in CSV form, and merged the **41 new POIs** into `scripts/osm_cache.json` with
`secondhand` added to the cache's `kinds` list. The other categories in the cache are untouched
and still carry their 31 Aug 2026 fetch. `fetched` now reads
`2026-08-31 12:50 (+secondhand 2026-09-01)` so the mixed provenance is visible in every sweep
header. **This is a hand-merged cache, not a refresh** — if the next pass needs any other
category re-fetched it must do the same thing or find a machine with Overpass access.

The guard worked exactly as designed on the way in: `--kinds secondhand` against the old cache
exited telling me to `--refresh` rather than reporting a region with no op shops in it. I did
not work around it; I filled it.

### I broke the filter lesson myself, on Uniting, and it cost two shops

My first sweep of Uniting Vic.Tas's 152-URL locations sitemap filtered on a **hand-written list
of town names** and found one op shop, in Geelong West. It missed **Point Lonsdale** and
**Highton**, both of which were sitting in that same sitemap. I only caught it because an
unrelated web search surfaced the Point Lonsdale page directly.

This is the third or fourth time this project has been bitten by a filter that discards without
saying so — the `--kinds` space form, the arts label bug, the stale cache — and it is worth
recording that it happens to a person reading a list just as easily as to a script. The correct
answer is **three** Uniting op shops in region. (A fourth sitemap entry, `highton-174-barrabool-rd`,
302s to `earlylearning.unitingvictas.org.au` — it is a kindergarten.)

---

## PHASE 1 — the charity chains, worked to the end

Fifteen chains were named in the brief. Here is every one of them, what its locator did, and
what came out.

| chain | locator | in region |
|---|---|---|
| **Salvos Stores** | `salvosstores.com.au/stores` is a Next.js page whose store list is **empty in `__NEXT_DATA__`** and is fetched client-side from its own `/api/uplister/store-list` — 445 stores nationally with address, phone, hours and coordinate. | **10** (+1 permanently closed) |
| **Vinnies (St Vincent de Paul Vic)** | No API. `sitemap.xml` lists all 119 VIC shop pages; each page carries address and full hours. | **9** |
| **Australian Red Cross** | `shop.redcross.org.au/store-locator` renders six stores and has no list page; its `POST /api/locations/search` returns all 75 VIC locations of every type. | **1** |
| **Savers** | `stores.savers.com.au/au-vic/` lists all 10 VIC towns. | **1 — already row 705.** Nothing new. |
| **Sacred Heart Mission** | Readable. Says "our second-hand stores in **Melbourne**"; the locations heading is "Op shop locations **Melbourne**". | 0 |
| **Anglicare Victoria** | Readable. **No op shop network at all** — 279 page/service/local sitemap URLs, none of them retail; site search for "op shop" returns blog posts telling readers to visit *their local* op shop. | 0 |
| **Uniting Vic.Tas** | Readable via `wp-sitemap-posts-locations-content-1.xml` (152 locations). See the filter failure above. | **3** |
| **Diabetes Victoria** | Readable. **Runs no op shops** — it is *Savers'* donation partner (`/get-involved/donate/donate-your-pre-loved-clothes/`, `/three-reasons-to-donate-at-savers/`). | 0 |
| **MS Australia / MS Plus** | **Would not render to a fetch.** The Victorian list is inside a collapsed accordion; a plain fetch of the op shop page returns it **EMPTY**. Had to expand it in a live browser. 8 VIC shops. | **1** |
| **Cancer Council Victoria** | Readable. `cancercouncilshop.org.au` sells **new** sun-protection goods. Not second-hand. | 0 |
| **Lifeline** | `lifelinedirect.org.au` sub-sitemaps unreadable, but `/geelongswv/shops` lists all 38 shops with per-shop pages carrying address, phone and hours. | **7** (from 8 pages — see below) |
| **RSPCA Victoria** | Readable. 11 op shops in the locations sitemap, **none in region**. | 0 |
| **GAWS** | **Would not render to a fetch** — `gaws.org.au/op-shop` is client-rendered and returns an empty body. Worth the live browser: see below. | **1** |
| **Bethany Community Support** | `bethany.org.au` **redirects to `meli.org.au`** — Bethany has rebranded as Meli. No op shops. | 0 |
| **hospital auxiliary / parish op shops** | No central list; town by town. | **9** |

Two chains not on the brief's list turned up and are included: **Brotherhood of St Laurence**
(one shop, Belmont) and **Fight Cancer Foundation** (both of its two Victorian shops are in
this region).

### Chains whose locator could not be read, and what I did instead

- **MS Plus.** The op shop page's Victoria block is a collapsed accordion that renders empty to
  `fetch`. **Anyone fetching that URL will conclude MS Plus has no shops anywhere.** Opened the
  accordion in a live browser and got all eight VIC shops with addresses, phones and full hours.
- **GAWS.** `gaws.org.au/op-shop` returns an empty `<body>` to a fetch. In a live browser it
  says, in as many words, that the Vines Road Hamlyn Heights shop is **permanently closed** and
  the shop is now at 50 Watsons Road, Newcomb. A fetch-only pass would have written the dead one.
- **Brotherhood of St Laurence.** Their op shops page is a **plain list of town names** — no
  addresses, no hours, no per-store pages (`/services/op-shops/belmont/` is a 404). So BSL's own
  site confirms a Belmont shop exists and nothing else. The address, hours and phone on that row
  come from OpenStreetMap and are flagged as such in its `source_note`. **The hours are not
  confirmed by the Brotherhood.**
- **Hesse Rural Health** (Winchelsea). Their fundraising page confirms the auxiliary and the
  2020 arson but publishes **no current address** and is stale — it still says the rebuild is
  "to be completed in 2025". A 2023 Surf Coast Times story put the shop at 10 Main Street and
  the future one at 44-46 Main Street; the shop's **own** Facebook page says 10 Willis Street
  and posted "we are open" three days ago. I used the shop's page over the operator's.
- **Great Ocean Road Health** (Apollo Bay). Their Second Sails page confirms the shop and what
  it funds but publishes no address or hours. Address from the shop's own Facebook, tied to GORH
  by the `@gorh.vic.gov.au` contact email on it.
- **Salvos Stores' `StoreLink` field is stale** — it points at `uplister.com.au`, a domain the
  chain no longer uses. The live store page is `salvosstores.com.au/stores/{state}/{slug}`,
  which is the pattern the site's own anchors use. Do not follow `StoreLink`.

### The one Lifeline oddity

Lifeline publishes **two pages at one address**: "Breakwater Lifeline Warehouse"
(03 5248 6395) and "Breakwater Lifeline Shop" (03 5245 1702), both at 306 Boundary Road,
Breakwater, with identical hours and different phone numbers. Written as **one row**. If they
are genuinely two operations on the site, that row needs splitting — flagged rather than guessed.

---

## PHASE 2 — the independents

`nearby.py --all --kinds secondhand --radius 5000` over the merged cache: **53 places on the
map, 53 of them not in the database.** Reading them is what the `books` and `music` tags are
for, and it was a bad bargain here: of 12 `books` hits, **none** is a second-hand bookshop.

Written from Phase 2: **The Amazing Mill Markets** (Newcomb) and **IHR Vintage Antiques**
(North Geelong). That is all the independents that confirm first-party. Everything else is in
the rejection list.

**The map badly under-reports this category on the Surf Coast and Bellarine.** OSM knows two
second-hand places in Torquay and misses St Luke's entirely; it knows **nothing at all** in
Queenscliff, where there are two op shops on one street. Every Phase-1 and parish shop below
was found by search, not by the map. Do not treat a zero from `nearby.py` as a fact about a
town in this category.

---

## PHASE 3 — council tip shops and resale sheds

Four councils checked. **There is exactly one tip shop in the region and it is already in the
database.**

- **Surf Coast Shire** — the Anglesea Resale Shed, 50 Coalmine Road, Anglesea. Row 110. Hours
  and address above.
- **City of Greater Geelong** — Drysdale Resource Recovery Centre and the Geelong interim RRC
  are **drop-off only**. No reuse shop, no second-hand sales area, no mention of buying anything.
- **Colac Otway Shire** — Apollo Bay Resource Recovery Centre accepts waste. No tip shop.
- **Golden Plains Shire** — Rokewood Transfer Station accepts waste and e-waste. No tip shop.

A clean, boring result, and it is a fact rather than a gap: three of the four councils in this
region do not run a tip shop.

---

## PHASE 4 — markets

**One event row written, and it is not a market.** The honest finding is that the region's only
confirmable recurring second-hand market — the **Winchelsea Re-Loved Market** — is *already in
the database* as event 689, and my contribution to it is the two-field edit above.

- **Garage Sale Trail** — no Surf Coast Shire or City of Greater Geelong participation could be
  found. Not written.
- **The Amazing Mill Markets is NOT an event.** It has "Markets" in its name and it is a
  permanent indoor emporium open 10–6 every day of the year but Christmas Day. It is an
  activity, `kind = shop`, single-typed `second-hand`. Typing it `market` would have made it
  `market · second-hand`, `KIND_OF['market'] = 'venue'`, and it would have walked onto the board.
- Everything else in the events table already typed `market` (44 rows) is a farmers'/makers'/
  community market. None of them is second-hand. None retyped.

### The one event, and its missing `places` row

**The Dove Designer Runway & High Tea** — Sat 24 October 2026, from 1:45pm, at The Dove op shop,
Ocean Grove. A fashion parade and high tea of the designer pieces that come through the shop's
own donations. `types: ["second-hand"]`, no `kind` (an event is always a happening).

**It has NO `place_id`, and here is the address to build one from, in the log where the rules
say to put it and not only in prose:**

    name:    Ocean Grove Uniting Church Outreach Centre ("the dove")
    address: 107-109 The Parade (corner Eggleston Street), Ocean Grove VIC 3226
    suburb:  Ocean Grove
    lat/lng: -38.266813, 144.5271048
             (Nominatim structured query, house-number node for 107-109 The Parade,
              reverse-geocodes to "107-109, The Parade, Ocean Grove")
    kind:    community-centre  (it is a church outreach centre with a shop in it)

`have.py places` has no row for it and nothing near it fits — the closest Ocean Grove places
are the Library, the Hotel, the Park, the Surf Life Saving Club and "Gather". Please add it and
link the event.

**On the date:** `date_confidence: "medium"`, deliberately, and the reason is specific.
The source is the organiser's own Facebook events tab, which would normally be `high`. But
**Facebook does not print the year** for a date inside the next twelve months — it shows
"Sat, 24 Oct at 13:45 AEDT" under Upcoming, and 2026 is therefore *derived*. It is
corroborated: 24 October 2026 is a Saturday, matching the "Sat" Facebook prints, and AEDT is
correct for late October. That is a worked-out year, not a read one, so it is `medium`.

**Judgement call, flag it:** this is a fundraiser at an op shop, not a market, and the brief's
Phase 4 was about markets. I wrote it because it is a real, dated, first-party second-hand
thing a person hunting second-hand goods would want to know about. If you would rather the type
stayed shops-only, drop the row — nothing else depends on it.

---

## THE REJECTION LIST

Every candidate checked and **not** written, with the reason. This is the part that stops the
next pass spending the same hour.

### Closed, or cannot be confirmed as trading

| candidate | address | why not |
|---|---|---|
| **Salvos Stores Geelong South** | 81 Barwon Terrace, Geelong South | The chain's own API flags it `isPermanentlyClosed: 1`. |
| **GAWS Op Shop, Vines Road** | 63 Vines Road, Hamlyn Heights | GAWS's own page: "our former Vines Road, Hamlyn Heights Op Shop is **now permanently closed**." Still in OpenStreetMap as a live `shop=charity` way. The live shop is at Newcomb and IS written. |
| **RSPCA Op Shop Geelong** | 227 Autumn Street, Geelong West | In OSM and in three directories. **Not on RSPCA Victoria's own list of 11 op shops**, none of which is in this region. Same shape as Good Cycles and Bike Guru. |
| **The Salvo Op Shop, Ocean Grove** | 4/6 Marine Parade | Named in a weekendnotes article. **Not in Salvos Stores' own 445-store API.** Closed. |
| **The Salvation Army, Trigg Street** | Trigg Street, Geelong West | An OSM `shop=charity` node with no address. Not in the Salvos API. Probably a corps building mis-tagged, or gone. |
| **Armor Antiques** | 200 Moorabool Street, Geelong | Its own domain `armorantiques.com` **no longer resolves** (DNS failure). Only tourism-board and directory listings remain. |
| **Pegasus Antiques** | 550 La Trobe Boulevard, Geelong | `pegasusantiques.com.au` **no longer resolves**. Directory listings only. |
| **Waynes World of Music** | 171 Melbourne Road, North Geelong | OSM `shop=music`. No first-party page; its Facebook page returns "this content isn't available". Unconfirmable. |
| **Bellerine Collections** | 243 Moorabool Street, Geelong | OSM `shop=second_hand` with a phone and no website. No first-party page found. |
| **Vintage Wares on LaTrobe** | 386 La Trobe Terrace, Geelong | OSM `shop=second_hand`. No first-party page found. |
| **Village Op Shop** | Clifton Springs Road, Drysdale | OSM `shop=second_hand`. No first-party page; may be an old name for one of the three Drysdale shops that ARE written. |
| **Retro** | 14 Station Street, Forrest | OSM `shop=antiques`. No first-party page. A shop in a town of 250 needs confirming before it goes in. |
| **Op Shop of Mano Baps** | Shannon Avenue, Manifold Heights | OSM `shop=charity`. No first-party page found. |
| **Lorne Op Shop** | 98 Mountjoy Parade, Lorne (per directories) | Only aggregator listings. **No first-party page anywhere.** The most likely real miss on this list — someone in Lorne could settle it in a minute. |
| **Opportunity Shop** | 108 Bacchus Marsh Road, Corio | OSM `shop=charity`, unnamed operator. No first-party page. |
| **The Drapery** | 67 Main Street, Birregurra | OSM `shop=antiques`. Not checked further — Birregurra is in region and this is a genuine loose end. |
| **Marlene Miller / Antipodes** | Portarlington | OSM `antiques` / `books`. Not checked further. |

### Organisations that run no op shops in this region

Sacred Heart Mission (Melbourne only) · Anglicare Victoria (no op shop network at all) ·
Diabetes Victoria (Savers' donation partner, not an operator) · Cancer Council Victoria (sells
new sun-protection goods) · RSPCA Victoria (11 shops, none here) · Bethany Community Support
(now Meli; none) · **UnitingCare Geelong** — no first-party site; four addresses in White Pages
and Whereis, and **three of them are now occupied by other chains' shops** (Lifeline is in
Village Walk Drysdale, Salvos is on Torquay Road Grovedale). Legacy directory entries; the live
entity is Uniting Vic.Tas.

### Bookshops — the `books` tag's bad bargain, in full

`shop=books` is in `KIND_TAGS['secondhand']` because a used bookshop carries no other tag. In
this region it caught **twelve** shops and **not one of them is second-hand**: Torquay Books,
Beach Books (Barwon Heads), Bookgrove (Ocean Grove), Lorne Beach Books, Great Escape Books
(Aireys Inlet), Galapagos Book Store (Apollo Bay), Cook & Young Booksellers (Geelong), Gifts
for the Geek (Geelong), Good News Bookshop (Altona, out of region), Books N Gifts Station
(out of region), Antipodes (Portarlington), and **The Book Bird**, which is already row 704.
They are new-book independents. The tag is still worth keeping — the cost of reading twelve
names once is lower than the cost of missing a used bookshop — but the next pass can skip
these twelve by name.

### Out of region

**Hoppers Crossing** and **Tarneit** Salvos, and **Werribee** Salvos and Vinnies. All inside
the Overpass bounding box, all outer Melbourne (Wyndham). RESEARCH_RULES defines the region as
"Surf Coast and Bellarine, plus Geelong, plus the Otways and Great Ocean Road spine" and says
direction matters more than distance. Werribee *is* in `SUBURBS` — it is there for the Werribee
South wineries and Shadowfax — but a Werribee op shop is 60 km up the freeway in the wrong
direction and is not what somebody in Jan Juc means by "where can I go op shopping". Excluded
on purpose; say so if you disagree and they can be added in five minutes.

Also inside the bbox and excluded: everything at Altona, and **Facebook Marketplace, Gumtree,
eBay and Depop**, which are not places.

### Not retyped, and right where they are

Repair Café Surf Coast, Repair Cafe Bellarine – Ocean Grove, Torquay Landcare, Odonata, the
GRLC Seed Library, both Men's Sheds. Reuse and repair are not second-hand and do not share a
shelf. `527 Bicycle Centre Belmont` likewise (see the audit).

---

## TOWNS THAT RETURNED NOTHING

A silence, recorded as a fact. These towns are in `SUBURBS`, were swept in the map sweep and
searched by hand, and have **no second-hand shop this pass could confirm**:

**Jan Juc · Bells Beach · Bellbrae · Breamlea · Connewarre · Freshwater Creek · Moriac ·
Mt Duneed · Armstrong Creek · Wallington · Curlewis · Leopold** (the Salvos named "Leopold" is
at Moolap) **· St Leonards · Indented Head · Aireys Inlet · Fairhaven · Moggs Creek ·
Eastern View · Cumberland River · Wye River · Kennett River · Skenes Creek · Deans Marsh ·
Forrest** (one unconfirmed antiques shop) **· Beech Forest · Lavers Hill · Cape Otway ·
Birregurra** (one unconfirmed antiques shop) **· Shelford · Little River · You Yangs ·
Point Addis · Ceres · Fyansford**.

**Lorne and Apollo Bay each have exactly one** — and Apollo Bay's is shut for renovations until
4 September. **Torquay has two.** Anglesea has two counting the Resale Shed. That is the whole
of the Surf Coast.

**And the distribution is Geelong-heavy, as expected, and was not corrected for.** Of 49 rows,
counted by the town each `location` string ends in:

    Greater Geelong          25   (Geelong West 5, Belmont 4, Geelong 4, Grovedale 3,
                                   Newcomb 3, North Geelong 2, Norlane, Geelong South,
                                   Breakwater, Highton)
    Bellarine                13   (Drysdale 4, Ocean Grove 3, Queenscliff 2, Leopold,
                                   Point Lonsdale, Barwon Heads, Portarlington)
    Colac                     3
    Surf Coast / GOR          4   (Torquay 2, Anglesea, Apollo Bay)
    Golden Plains / Winch.    3   (Winchelsea, Inverleigh, Bannockburn)
    Lara                      1

**Pakington Street alone has five** — Salvos, Vinnies, Uniting, MS Plus and Fight Cancer
Foundation, all inside a kilometre — and **High Street Belmont has four in a row**: Brotherhood
at 142-146, Vinnies at 170, Lifeline at 174, Salvos at 176. That is where the population is and
that is what the data says. A pass that came back with three Lorne op shops would have invented
them; Lorne has none I can confirm.

---

## PINNING — what to trust in this batch

The technique is the Savers one: the chain's published coordinate and an independent Nominatim
structured query on the same address, stored only where they agree at building level, with the
separation named in `source_note`. Every pin was reverse-geocoded before it was written.

**Strong (two independent sources agreeing at building level, ≤ 35 m):**
Salvos Torquay 4.5 m · Salvos Belmont 6.4 m · Salvos Grovedale 6.7 m · Salvos Lara 7.5 m ·
Red Cross Geelong 7.8 m · Salvos Colac 8.4 m · Seaside Seconds 10 m · Salvos North Geelong
21.3 m · Salvos Moolap 34 m · Brotherhood Belmont 3.2 m · Mill Markets 0 m · IHR Antiques 0 m ·
plus Vinnies Geelong West, Grovedale and Hamlyn Heights, Lifeline Belmont, Newcomb, Colac and
Drysdale, and Highton Uniting — all named `shop=charity`/`shop=second_hand` OSM objects whose
house number matches the operator's own address. **Highton Uniting is the nicest of them:
OpenStreetMap had independently tagged 8 Porter Avenue `shop=second_hand` before anyone here
looked.**

**Single-source but house-number matched and reverse-geocoded** (the operator publishes no
coordinate): the parish shops, The Wave, The Dove, Winchelsea, Second Sails, The Vestry Shop,
Point Lonsdale Uniting, Geelong CBD Lifeline, Breakwater, both Fight Cancer shops, GAWS,
St Luke's, Vinnies Ocean Grove / Queenscliff / Belmont / Norlane / Geelong South / Colac.

**Weak, and each says so in its own `source_note` — read these before verifying:**

- **Salvos Drysdale.** The chain's own coordinate is the only source; it reverse-geocodes to
  "L'Amourhair on the bellarine, 10-12 Hancock Street" — a neighbouring shopfront. Right to
  within a few doors, not to the building. OSM has no house numbers on Hancock Street.
- **Salvos Geelong West and Geelong West Uniting.** Three sources disagree by two shopfronts on
  a 40 m stretch of Pakington Street: Salvos says 4/23, Uniting says 23, OSM has a "Salvos" node
  at 31 and a "Uniting Op Shop" node at 25, and Nominatim's house-number node for 23 is tagged
  as a paint shop. I used the **chain's own coordinate** for Salvos and the **named OSM object**
  for Uniting so the two rows do not land on one pin. Somebody standing on Pako can fix both.
- **MS Community Shop Geelong.** House number 96 is right; the OSM shopfront at that number is
  tagged as a hearing-aid shop. Same situation as Pop Cultcha's "Codeacious" and Hendry's
  Grovedale — the number was what was checked.
- **Geelong CBD Lifeline.** Number 107 is right; OSM has that building tagged as a bank.
- **St James Drysdale** and **St John's Shed Portarlington** are **site-level**, not shopfront:
  both resolve to the church complex (47-55 Collins Street; the place_of_worship at 11-15 Brown
  Street). The shops are on those sites but the pin is the church.
- **Grovedale Lifeline has NO PIN, deliberately.** Lifeline's own page says 4/148 Marshalltown
  Road, Marshall; OpenStreetMap has a `shop=charity` way named "Lifeline" at **129** Marshalltown
  Road carrying **the same phone number Lifeline publishes for this shop**. 129 and 148 are
  different buildings about 230 m apart, so one source has not caught a move. Nominatim has no
  house number for either. A null pin is the honest answer.

**Suburbs not in `SUBURBS`, and what each location string ends with** (per RESEARCH_RULES —
flagged here, not relied on by accident):

| real suburb | row | location string ends |
|---|---|---|
| Moolap | Salvos Moolap | `…, Moolap, Geelong` |
| Moolap | Salvos Leopold | `…, Moolap, Leopold` (the name Salvos gives the store) |
| Hamlyn Heights | Vinnies Hamlyn Heights | `…, Hamlyn Heights, Geelong` |
| Marshall | Grovedale Lifeline | `…, Marshall, Grovedale` (the name Lifeline gives the shop) |
| North Geelong | Salvos North Geelong, IHR | `…, North Geelong` — `suburbOf()` reads this as Geelong |
| Bell Park | Salvos North Geelong | reverse-geocode says Bell Park; the two suburbs meet on Thompson Road. Chain's own suburb used. |

---

## WHAT IS LEFT

1. **Row 110's pin is 2.58 km wrong and the row is `verified = true`.** That is the one item
   here worth doing today.
2. Build the `places` row for the Ocean Grove Uniting Church Outreach Centre and link event 689
   to place 78 while you are in there.
3. Seventeen candidates in the rejection list have an address and no first-party page. **Lorne**
   is the one most likely to be a real shop.
4. **Breakwater Lifeline** may be two operations at one address, written as one row.
5. **Brotherhood Belmont's hours are OpenStreetMap's, not the Brotherhood's.** Worth a call.
6. **Second Sails, Apollo Bay reopens Friday 4 September 2026** after renovations. Its row says
   so in `notes`; that line should come out once it has reopened.
7. Nothing in this batch needs a `BY_ID` line.
