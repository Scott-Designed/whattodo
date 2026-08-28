# The produce group — worklog

Ran 27–28 Aug 2026. **Both halves complete.** 38 rows written — 12 market
events (156–167) and 26 activities (465–490).

    market      13 -> 25
    produce     17 -> 42
    nursery      7 -> 10
    farm life    6 ->  9

The pass was interrupted twice by the bridge to the repo machine dropping;
nothing was lost, and no row was written twice.

**The group prompt is out of date in one important way.** It asks for
`shop (6)` as the fifth type in this group. `shop` was **retired as a type on
27 Aug 2026** — 43 types down to 42 — and is a *kind* now. So this group is four
types, not five, and a shop is written as `kind: "shop"` plus a hand line in
`BY_ID`. No row in this pass needed that: every candidate that might have been a
shop is a place you go for its own sake, which the Chocolaterie rule makes a
**venue**. Worth fixing in `by-group.md` before this prompt is run again.

---

## market — the 13 we hold, checked against their organisers

Read with `python3 scripts/have.py market` and the full rows pulled from
`events` via the anon key. Today is 27 Aug 2026.

The prompt said "ten are monthly or annual". The real split is **eight**
monthly/annual, **two** weekly, and **three** with no recurrence at all —
eleven rows that never roll forward, not ten.

### Agrees with the organiser — no action

| id | Row | Organiser publishes | Verdict |
|----|-----|--------------------|---------|
| 26 | Cowrie Market, Torquay, 2026-09-20, 9am–2pm | "Sunday 20 September" under "The 2026/27 dates as follows", 9am-2pm | ✅ exact |
| 38 | Portarlington Market, 2026-09-27, 9:00am–2:00pm | "September 27th 2026 (Sunday)", "9am - 2pm" | ✅ exact |
| 39 | Ocean Grove Market, 2026-10-04, 9:00am–1:00pm | "Sunday, 4 October 2026", "9.00 am to 1.00 pm" | ✅ exact |
| 48 | Aireys Inlet Market, 2026-10-11, 9am–1pm | "Sunday 11 October", "9am to 1pm" | ✅ exact |
| 5  | Farmers Market, Torquay, weekly Sat 8:30am–1pm | "Saturday mornings from 8.30am to 1.00pm" | ✅ weekly, rolls safely |

### Disagrees — needs /admin

**id 6 — Sunday Market (Belmont). Wrong hours, wrong name, and a Maps search url.**
The City of Greater Geelong owns and runs this market, so its page is the
organiser. It publishes *"8:00am - 1:00pm every Sunday"*. We hold **7am–12pm** —
an hour out at both ends. The council also calls it **"Belmont Market"**, not
"Sunday Market". And `info_url` is
`https://www.google.com/maps/search/Belmont+Sunday+Market+Geelong+Victoria` —
one of the 37 standing Maps-search defects. The honest url is
`https://www.geelongcity.vic.gov.au/services/venues-and-facilities/belmont-market`.
Council also publishes closures worth carrying: final market of 2026 is
Sun 13 Dec, then closed 20 Dec, 27 Dec and 3 Jan 2027.
⚠️ Council's own two pages disagree on the address — "1 Barwon Heads Road" vs
"1A Barwon Heads Road".

**id 14 — Night Markets (Geelong After Dark). Dead listing. Delete or rewrite.**
This is the worst of the thirteen. **Geelong After Dark no longer exists.** Its
surviving site says it was "a landmark night-time arts festival (2014–2019)",
paused for COVID, and "the festival did not return, marking the end of an
important chapter in Geelong's cultural history" —
https://geelongafterdark.squarespace.com/ . It was an **annual one-night arts
festival**, never a monthly night market, so `recurrence = monthly` was never
right either.
Two further traps on this row:
- **`geelongafterdark.com.au` has been taken over.** It now serves an
  auto-generated local-news portal calling itself "Geelong Hub". Do not cite
  that domain as the festival.
- The Johnstone Park night market was the **Geelong Nightjar Festival**, and
  that operator has moved to Torquay — nightjarfestival.com.au lists Torquay
  Common events only, no Geelong, no Johnstone Park.
No organiser anywhere publishes a market at Johnstone Park on **2026-11-07**.
The row's `info_url` is a generic council events index, not an organiser page.

**id 21 — Community Market (Anglesea, at the Surf Life Saving Club). No such
market.** Checked the club's own site (angleseaslsc.org.au — patrols, nippers,
gym, venue hire, Jimpy's Bar, Love House, nothing about a market) and Anglesea
Community House (anglesea.org.au), whose site is the row's own `info_url` and
which lists only its **Twilight Farmers Market** and the **Aireys Inlet
Market**. No source anywhere associates a market with the Anglesea SLSC.
The row's date **2026-09-13** is unsupported by its own info_url.

**id 40 — Community Market (Drysdale). Time_text is a shrug, and the organiser
contradicts itself.** Real name **"Drysdale Community Market"**, run by
**Drysdale Primary School** as a fundraiser, at *"Drysdale Recreation Reserve,
Duke Street, Drysdale"*. They publish **"9am – 1pm"**; we hold the useless
*"Sunday morning"*. We hold venue "Drysdale Reserve" — the organiser's own
wording is "Drysdale Recreation Reserve".
⚠️ The school states its own season two different ways on two of its own pages:
"October through April" vs "October through until May". Flagged, not resolved.

**id 88 — Community Market (Winchelsea). Venue disagrees.** Organiser is
**Growing Winchelsea Inc.**, who call it **"The Winchelsea Community Market"**
and give the venue as *"Leisure Time Centre (LTC) Indoors Market - 15 Gosney
Street, Winchelsea 3241"*. We hold **Winchelsea Shire Hall** (place 78), which
is what the shire calendar says. A Growing Winchelsea post from Jan 2026 says
they are "Trialling a new venue and layout", so this looks like a real move
rather than a data error. Their own better url is
https://growingwinchelsea.com/project/winchelsea-community-market/ ; we hold a
surfcoastevents aggregator link.
⚠️ Separately, the Shire Hall's street number is given as both 20 and 28 Hesse
Street across council and organiser sources.

**id 22 — Surf Industry Sample Sales – Baines Crescent. Not an event, and a
Maps search url.** No organiser publishes this. Baines Crescent is a permanent
surf factory-outlet precinct that discounts over the summer holidays; the
26 Dec – 6 Jan window is folklore, not a published date. `info_url` is
`https://www.google.com/maps/search/Baines+Crescent+Torquay+Victoria` — the
second Maps-search defect in these thirteen.
**This belongs in half two as a `shop` row, not in `events`.** It is a genuine
reason-to-go retail precinct; it is not a dated happening.

### Dates that are worked out rather than published

These three match their organiser's stated pattern exactly, so they are not
*wrong* — but no organiser publishes the specific date we hold, which is the
Arts Trail failure mode one step from happening.

- **id 53** Anglesea Twilight Market, 2026-11-06 — organiser publishes only
  *"1st and 3rd Friday of the Month from November to March"*. 6 Nov 2026 is
  indeed the first Friday.
- **id 40** Drysdale, 2026-10-18 — *"3rd Sunday of the month"*; 18 Oct is the
  third Sunday.
- **id 88** Winchelsea, 2026-09-06 — *"First Sunday every month"*; 6 Sep is the
  first Sunday.

### The three with no recurrence — what they actually are

- **id 48 Aireys Inlet Market — an irregular seasonal series, and `null` is the
  right answer.** The organiser publishes *"Markets run from October to July -
  9am to 1pm"* and then names each date individually: "Sunday 11 October",
  "Saturday 31 October 9am-3pm (Aireys Fair)", "Sunday 29 November", "Sunday 13
  December", "Sunday 27 December". That is neither monthly nor fortnightly —
  October alone has two, one of them a Saturday at different hours. Setting
  `monthly` here would publish dates the organiser never announced. Leave null
  and let a person set each `starts_on`.
- **id 52 Anglesea Riverbank Market — seasonal, and our time is wrong.** The
  organiser's own TryBooking page for the 2025/26 season gives *"9am to 3pm"*
  and an irregular set of dates (2 Nov 2025, 1 Jan, 4 Jan, 11 Jan, 8 Mar,
  5 Apr 2026). We hold **9am–4pm**. Visit Great Ocean Road describes the
  frequency as "Public holiday weekends and select summer dates", which matches.
  **No 2026/27 season has been published anywhere I can reach**, so our
  2026-11-01 is unconfirmed. Recurrence should stay null; this is a series of
  named dates, not a cycle.
- **id 53 Anglesea Twilight Market — twice monthly, seasonal, and there is no
  word for it.** *"1st and 3rd Friday of the Month from November to March"* is
  not weekly, not fortnightly (the gap between the 3rd Friday and the next 1st
  Friday is 14 or 21 days), and not monthly. `null` is the least wrong value.
  Its venue also disagrees with ours: the organiser says *"Anglesea Community
  House Car Park, 5 McMillan Street, Anglesea"*, we hold "Anglesea Community
  Precinct" with `place_id` null.

### The three called just "Community Market"

What their organisers actually call them:

| id | Town | Organiser's own name |
|----|------|---------------------|
| 21 | Anglesea | **no such market exists** — see above |
| 40 | Drysdale | **Drysdale Community Market** (Drysdale Primary School) |
| 88 | Winchelsea | **The Winchelsea Community Market** (Growing Winchelsea Inc.) |

Also mis-named, though not a "Community Market":
- **id 6** is **Belmont Market**, per the council that runs it.
- **id 39** is the **Ocean Grove Rotary Summer Market** — Rotary Ocean Grove
  uses both "Ocean Grove Summer Market" and the Rotary form; "Ocean Grove
  Market" is neither.

### Better first-party urls for rows that currently hold weaker ones

| id | Now | Should be |
|----|-----|-----------|
| 6  | Google Maps search | https://www.geelongcity.vic.gov.au/services/venues-and-facilities/belmont-market |
| 22 | Google Maps search | null — no organiser page exists |
| 39 | council event page | https://www.rotaryoceangrove.org.au/summer-market |
| 40 | visitgeelongbellarine | https://drysdaleps.vic.edu.au/drysdale-community-market/ |
| 48 | surfcoastevents | https://www.aireysinletmarket.com.au/ |
| 88 | surfcoastevents | https://growingwinchelsea.com/project/winchelsea-community-market/ |
| 14 | council events index | none — the event does not exist |

---

## market — the ones we do not have

Twelve written as events (batch prepared, **not yet applied**). Only rows whose
date comes off a first-party page, or off a first-party pattern plus a council
listing for the year, were included.

**high confidence — the organiser publishes the actual date**
- Queenscliffe Community Market — 27 Sep 2026, 9am–2pm, Lower Princess Park
- Apollo Bay Farmers Market — 20 Sep 2026, 9am–1pm, Youth Club, 19-21 Moore St
- Strawberry Fair, Wallington — 15 Nov 2026, 10am–3pm, Wallington Primary
- Portarlington Twilight Market — 16 Jan 2027, 3pm–8pm, W.G. Little Reserve
- Warralily Market, Armstrong Creek — 5 Sep 2026, 9am–2pm, Mirambeena Park
- Geelong Dog Lovers Market — 30 Aug 2026, 11am–3pm, Little Creatures

**medium — first-party pattern, date from a council listing or a weekly roll**
- Apollo Bay Community Market — weekly Sat, 8:30am–1pm, foreshore, since 1978
- Barwon Heads Makers Market — 29 Aug 2026, riverbank, Ewing Blyth Drive
- Portarlington Makers Market — 6 Sep 2026, Senior Citizens Hall, 65 Newcombe St
- South Geelong Farmers Market — 6 Sep 2026, South Geelong Primary, 200 Yarra St
- Geelong City Market — 29 Aug 2026, weekly Sat, Little Malop Street Central
- Point Lonsdale Market — 13 Sep 2026, Point Lonsdale Primary, Bowen Rd

Two pairs that must not be merged:
- **Barwon Heads Makers Market** (Issimo, riverbank, Ewing Blyth Dr, 9am–2pm)
  vs **Barwon Heads Market** (Community Hall, cnr Hitchcock/Ozone, 9am–1pm) —
  same town, same last-Saturday pattern, different organiser and venue.
- **Portarlington Makers Market** (Issimo, Senior Citizens Hall, first Sunday)
  vs **Portarlington Market** (Lions, W.G. Little Reserve, fourth Sunday) — id 38
  is the second of these.

### Real markets found but NOT written, and why

Each of these is live; none publishes a date I could stand behind.

- **Barwon Heads Market** ("The Original Barwon Heads Market") — Community Hall,
  cnr Hitchcock Ave & Ozone St. Last Saturday Feb–Nov plus every Saturday in
  Dec and Jan, 9am–1pm. **No website at all** — Facebook only. No date.
- **Geelong Waterfront Makers and Growers Market** — Rotary Club of Geelong
  Central, Steampacket Gardens, Eastern Beach Rd. First Sunday monthly.
  Organiser's own T&Cs PDF gives seasonal hours: 9.30am–3pm Sep–Feb,
  9.30am–2pm Mar–Aug. Its ClubRunner pages are JavaScript-rendered and return
  nothing to a fetch, and the council event page 403s. **This is the biggest
  one still missing** — worth a browser session.
- **Bellarine Farmers' Market** — Ocean Grove Park, third Saturday, 9am–1pm.
  No organiser website; details come from the venue's site, not the organiser.
- **Beckley Park Market**, Corio — 41 Broderick Rd, every Saturday, 40+ years
  running. No website, times unverified.
- **Lara Community Market** — Rotary Lara District with Lara RSL, cnr McClelland
  Ave & Rennie St, second Sunday, no January. The club's own site says nothing
  about it.
- **Little River Market** — That's Mine Events, Possy Newland Reserve, second
  Saturday. No times published. (The organiser's own page mislabels the reserve
  as being in Werribee.)
- **Wyndham Makers and Farmers Market** — Werribee Racecourse, third Sunday.
  No organiser times or dates.
- **Lorne Markets** — Lorne P-12 Parents & Friends, Lorne Foreshore, Mountjoy
  Parade. Four long-weekend markets a year. **Site is stale on 2025 dates**; the
  only 2026 date anywhere is a TryBooking stallholder page for 6 Jun 2026, past.
  The Melbourne Cup weekend market is the expected next one, unannounced.
- **Deans Marsh Market** — Deans Marsh Recreation Reserve, Nov–Mar season.
  **In operator transition** — the Community Cottage handed it to an external
  operator for 2025/26 and the 2026/27 status is unknown.
- **Birregurra Sunday Market** — Birregurra Park, cnr Strachan & Main St, second
  Sunday Nov–May, 9am–2pm. Whole 2025/26 season is past; no 2026/27 dates.
  Its organiser domains (birregurrafestival.com, meetmeinbirre.com) would not
  resolve — the one organiser page that could not be read at all.
- **Booln Booln Community Mob Market Day** — Wathaurong Booln Booln Cultural
  Centre, 410 Surf Coast Hwy, Grovedale. Council lists 19 Sep 2026, 10am–2pm;
  the organisation's own site does not mention it. Only its second ever, so no
  pattern. One source only — left out.
- **Mano Makers and Growers Market** — Manifold Heights Primary. Facebook only.
- **Gellibrand River Market** — Rex Norman Park, 5 Main Rd, Gellibrand. Annual,
  February. Dormant: the community house's calendar shows nothing after Feb 2025
  and its homepage currently leads with bushfire relief.
- **Tranquility Fair**, Ocean Grove Park — annual, first Saturday of the new
  year, 4pm–9pm, 70+ stalls. Organiser's page still shows 3 Jan 2026, past.
- **Winchelsea Re-Loved Market** — 10 Oct 2026 per the shire calendar.
  Deliberately left: it is in the surfcoastevents feed, so `scrape_events.py`
  owns it. Same reasoning for the **Aireys Inlet Fair** (31 Oct 2026).
- **Nightjar Festival**, Torquay Common — not a market and not currently dated.
  Its 2025/26 run was Fri 2 and 9 Jan 2026, 4pm–10pm, plus The Big Thrift
  Market on Mon 29 Dec 2025, 12pm–8pm. No 2026/27 dates published.

### Out of the suburb vocabulary

- **Golden Plains Farmers' Market**, Bannockburn — cnr Milton & High St, first
  Saturday excluding Jan and Dec. Golden Plains Shire runs it and publishes
  **"Saturday 5 September 2026"**, 9am–1pm. Also **Golden Plains Twilight
  Market**, "Friday, 4 December – 4.00pm – 8.00pm" 2026, at the Bannockburn
  Heart. Both are real, dated and first-party — and **Bannockburn is not in
  `SUBURBS`**, and is the direction of Ballarat. Not written; Scott's call.
  (The shire's own dedicated twilight page is stale on a 2021 date, and
  goldenplainsfarmersmarket.com.au is stale on a 2025 one — use the shire
  community page.)
- **Colac Growers and Makers Market** — Colac Showgrounds, 54 Chapel St, first
  Saturday, 9am–1pm. Nearest monthly produce market to Forrest, Gellibrand and
  Beech Forest, so arguably on the Otways spine, but Colac is not in the Place
  menu. Organiser publishes no dates. Not written.

### Dead, and worth recording so nobody re-researches them

- **Geelong After Dark** — ended 2019, domain taken over (see id 14).
- **Geelong Showgrounds Market** — closed October 2019.
- **Pako Farmers' Market** — closed ~2018; its domain no longer resolves.
- **Werribee Racecourse Market** — closed, superseded by the Wyndham market.
- **Geelong Nightjar Festival / Johnstone Park night market** — operator moved
  to Torquay; nothing at Johnstone Park now.
- **Geelong City Night Market** — a one-off launch, 19 Jun 2026, already past.
- **Inverleigh Community Market** — shire page stale on a 2022 date. An
  Inverleigh Hotel twilight market ran once in Nov 2024 as a trial; a news
  report at the time noted Inverleigh "hasn't had a market for quite some time".
- **Piccadilly Market at Mt Duneed Estate** — last dates 2019.
- **Ocean Grove Craft Market** — a stale duplicate of the Rotary Summer Market
  under an old venue. Do not list separately.
- **Bellarine Taste Trail** — checked as a market source and it is not one. It
  is a farmgate/winery/provedore trail of ~50 destinations and names no market.
  **It is a strong source for half two** and should be worked then.
- Markets checked and not found: Jan Juc, Bells Beach, Point Addis, Moggs Creek,
  Eastern View, Fairhaven, Moriac, Mt Duneed, Connewarre, Breamlea, Forrest,
  Beech Forest, Lavers Hill, Cape Otway, Skenes Creek, Kennett River, Wye River,
  Cumberland River, Clifton Springs, Indented Head, Leopold, Curlewis, Marcus
  Hill, You Yangs.

### Venues already in `places`

Not yet checked — `have.py places` needs the repo. The obvious candidates to
match on are Ocean Grove Park, W.G. Little Reserve, Little Creatures Brewery,
Steampacket Gardens and Torquay Common. **Torquay Common** is already on the
"build a place row" list in CLAUDE.md (event 77), which the Nightjar entry
would also use.

### Sources that would not open

- **facebook.com and instagram.com** — robots.txt disallows our fetching. This
  matters more here than in any previous pass: **Barwon Heads Market, Beckley
  Park, Lara Community Market, Bellarine Farmers' Market and Mano Makers have no
  other web presence at all.** For those five, Facebook is the only live date
  source and a person has to look.
- **JavaScript-only, returns nothing to a fetch:** every
  `issimomarkets.com/calendar/...` page (which almost certainly holds the dates
  for both Makers Markets), and the ClubRunner sites for Rotary Geelong Central
  and Rotary Lara District.
- **robots.txt disallows all paths:** geelongcitymarket.com.au,
  stleonardsps.vic.edu.au, bellbraemayfair.com, mymarketsvic.com.au.
- **Would not resolve:** birregurrafestival.com, meetmeinbirre.com,
  lornelionsclub.com.au, pakofarmersmarket.org.au, youyangsregion.org.
- City of Greater Geelong event pages 403'd intermittently — the Waterfront
  Makers & Growers, Lara Community Market and Piccadilly-at-Deakin pages all
  failed repeatedly and probably hold date lists.

---

## Vocabulary gaps found in half one

- **No recurrence word for "first and third Sunday"** (South Geelong Farmers
  Market) or **"1st and 3rd Friday"** (Anglesea Twilight Market, id 53) or
  **"every two months"** (Geelong Dog Lovers Market). All three are left null,
  which reads as "unknown" when it actually means "no word for this".
- **No type for a school fair.** Strawberry Fair, the Aireys Inlet Fair and the
  Bellbrae Mayfair are annual fairs with market stalls, filed as `market`
  because nothing fits better.
- **`SUBURBS` has no Bannockburn**, which strands two dated, first-party
  Golden Plains markets.

## Half two — not started

`nearby.py --refresh` was never run: the bridge to the machine holding the repo
dropped before half two began, and the OSM sweep, the geocoding and every write
run there. Nothing in half two has been researched, so nothing here should be
read as coverage of shop, farm life, nursery or produce.

Two things already found that belong to it when it runs:
- **Baines Crescent, Torquay** — a permanent surf factory-outlet precinct.
  Currently mis-filed as annual event id 22. A `shop` row.
- **The Farm Next Door**, 26 Forster Street, Norlane — farm gate with a Saturday
  10am–12pm market day. `produce`, possibly `farm life`.
- The **Bellarine Taste Trail** (~50 farmgates, wineries and provedores) is the
  single best source for the produce half and was confirmed to contain no
  markets, so it was left untouched today.

---
---

# HALF TWO — complete, 26 activities written (465–490)

`nearby.py --refresh` ran successfully: **1679 named places** cached for the
whole region in one Overpass query, plus 47 town centres. No throttling.
`--kinds=produce` across all 47 towns gives **110 places, 99 not in the
database**.

**Tooling bug worth fixing.** `nearby.py`'s own docstring says
`nearby.py Torquay --kinds produce`, with a space. The parser at line 263 only
reads `--kinds=produce`, with an equals sign, and **silently falls back to
`food`** otherwise — and the bare word `produce` is then swallowed as part of
the town name. A sweep run the way the docstring shows returns the wrong
category with no error. The group prompt in `by-group.md` has it right.

## What the OSM sweep is mostly made of

Of the 99 unlisted, the clear majority fail the "reason to go" test outright:
7-Eleven, EG Australia, Foodary, Reddy Express, Shell, APCO, Coles Express,
Pie Face, FoodWorks, BWS, Liquorland, Dan Murphy's, Thirsty Camel, Bottlemart,
Premix King (three towns), Cellarbrations, The Bottle-O, First Choice Liquor,
LicorZone, IGA Liquor, Vintage Cellars, Harry Brown, and about a dozen milk bars.

**`shop=florist` is in `KIND_TAGS['produce']` and should probably come out.**
It contributed nine Geelong rows — A Natural Bunch, Charlie and Co, Clover
Flowers, Lustre Blooms, Mr Collins, Peony & Weasel, Petals By Parisa, Smellies,
The Red Poppy — and a florist is neither produce nor a nursery. That is 9 of
the 35 Geelong "misses" being noise.

## Where OSM was thinner than reality — the headline

**The by-hand town check found more than the map did, and it is not close.**
Grubb Road, Wallington is effectively an unmapped farm-gate strip: Lomas
Orchards, Van Loon's Nursery, Wattle Grove Honey, Wallington's Local Pantry and
Ket Baker are all on it and **OSM had none of them** — Wallington returned
`0 on the map · 0 not listed`. Drysdale returned four OSM names, all servos and
bottle shops, while the real Drysdale holds Tuckerberry Hill, the Bellarine Farm
Gate market, Bellarine Smokehouse, Bellarine Fungi, Bellagreen and Becks Honey.

Towns where OSM was thin: **Wallington** (worst — zero mapped, five real),
Drysdale, Portarlington, Leopold, Marcus Hill, Winchelsea, Deans Marsh, Moriac,
Mt Duneed, Bellbrae, Birregurra, Ocean Grove.
Towns where OSM was honest: Jan Juc, Lorne, Anglesea, Apollo Bay, Barwon Heads,
Queenscliff, Indented Head, Breamlea, Connewarre — genuinely nothing there.

## Confirmed candidates, first-party, ready to write

### nursery (thinnest at 7 — biggest proportional win)
- **Van Loon's Nursery & Café**, 405 Grubb Rd, Wallington — big retail nursery
  with licensed café, 9–5:30 daily. vanloonsnursery.com.au. Not in OSM.
- **The Beach Willow**, 3/1135 Surfcoast Hwy, Mt Duneed — nursery + café +
  homewares, Mon–Sat 9:30–4:30, Sun 10–4. thebeachwillow.com.au. Nearest real
  garden centre to Jan Juc.
- **Great Ocean Road Nursery**, **500 Grossmans Rd, Bellbrae**, 9–4 daily.
  greatoceanroadnursery.com.au. ⚠️ **OSM is stale** — it maps
  "Bellbrae Art & Garden" at 557 Great Ocean Rd, which is the precinct it
  *moved out of*. 557 still holds Salt & Pepper Gallery and Bowside Cafe.
- **Portarlington Nursery**, 1/44 Newcombe St — no website found.
- **Plant Addicts Anonymous**, Geelong (OSM garden_centre) — unconfirmed.

### farm life (thinnest at 6 — a farm you can VISIT)
- **Lomas Orchards**, 570 Ocean Grove Rd, Wallington — heritage orchard, farm
  shop, farm café, orchard tours, 32+ apple varieties. **PYO strawberries
  November–May**, per kg. Wed–Sat 10–4. Cash only, no pets (biosecurity).
  lomasorchards.wordpress.com. The best family farm visit on the peninsula.
- **Tuckerberry Hill Berry Farm**, 35 Becks Rd, Drysdale — u-pick blueberries
  and strawberries, café, produce shed, est. 1976. tuckerberry.com.au.
  **Season is announced by them, not fixed** — their own site had it closed from
  21 March last season. Check before listing a season.
- **Ravens Creek Farm**, Hendy Main Rd, Moriac — 90-acre working farm with cafe,
  own bacon/beef/honey, summer PYO berries. ⚠️ **status unverified**, main
  coverage is 2017 and the street number varies (742 vs 778).
- **Heritage Alpaca Co**, Moriac — alpaca farm tours by appointment.
- **Yan Yan Flowers**, Deans Marsh — spray-free native flower farm, farm gate
  and tours by appointment.
- **Portarlington Mussel Tours** — on-water tour of a working mussel farm with
  cooking demo and tasting, departs Portarlington Pier.
  portarlingtonmusseltours.com.au. Booked dates only, no walk-up.
- **Freshwater Creek Eggs** — free-range egg farm, buy at the farm, meet the
  hens. No website, no street address published — needs a phone call.
- **Pennyroyal Raspberry Farm & Cidery**, 115 Division Rd, Murroon — u-pick
  raspberries, farm shop, cider, alpacas. ⚠️ their own site says **"closed for
  the 2025/26 berry season"**. Murroon is not in `SUBURBS`.

### produce
- **Dustys Bulk Foods**, 2/12 Gilbert St, Torquay — certified-organic bulk
  wholefoods and refill. dustysbulkfoods.com. OSM mis-tags it `convenience`.
- **Peach's Torquay**, 132 Surfcoast Hwy — destination greengrocer/provedore,
  deli, cheese, local wine. peachstorquay.com.au. OSM mis-tags it `convenience`.
  ⚠️ `peachs.com.au` is a **different business** — do not merge.
- **Winchelsea Wholefoods**, 25 Main St — bulk wholefoods, Mon–Fri 9–5,
  Sat 9–3, Sun 10–1:30. Direct peer to Dustys. Not in OSM.
- **The Store Deans Marsh**, 1419 Birregurra-Deans Marsh Rd — general store,
  cafe and bottle shop in one, house-made and locally sourced.
  thestoredeansmarsh.com.au. OSM's `shop=convenience` badly undersells it; in a
  town this size it is the destination.
- **Hilbilby Cultured Food**, 2/4 Sawmills Way, Torquay — fermented foods
  producer with a factory door, Mon–Fri 9–3. hilbilby.com.au.
- **Farmers Harvest**, 1680 Bellarine Hwy, Marcus Hill — farm-gate grocery grown
  out of the owners' own hydroponic farm. farmers-harvest.com.au.
- **Lard Ass Butter**, 10–11 Sykes Pl, Ocean Grove — artisan cultured-butter
  factory with tasting room and factory sales. lardass.com.au. **Closed
  weekends**, which blunts it as a weekend outing.
- **White Fisheries**, 1/35–39 Murradoc Rd, Drysdale — whole fish, shellfish,
  smoked. whitefisheries.com.au. Mon–Fri 9–5, Sat 9–12.
- **Bellarine Smokehouse + Provedore**, 16/93 Murradoc Rd, Drysdale — own smoked
  fish. bellarinesmokehouse.com. ⚠️ hours conflict between its own site and the
  Taste Trail map.
- **Wattle Grove Honey**, 459 Grubb Rd, Wallington — honey from own hives, farm
  shop with tasting. wattlegrovehoney.com.au. ⚠️ publishes no hours itself;
  Taste Trail says Thu–Mon 9–5:30.
- **Lonsdale Tomato Farm**, **239 Hood Rd, Portarlington** — hydroponic grower,
  **farm gate Fridays 10–4 only**. lonsdaletomatofarm.com. ⚠️ the name says
  Lonsdale, the farm is in Portarlington — a naming trap.
- **Sweet View – The Great Ocean Road Lolly Shop**, 39 Great Ocean Rd, Apollo
  Bay — **this is the "Apollo Bay Lolly Shop" the hospitality pass left**. Real
  name is Sweet View. sweetview.com.au, 7 days 10–5.
- **The Olive Pit**, 71 The Terrace, Ocean Grove — deli and café, the
  hospitality pass's leftover. olivepit.com.au.
- **The Beach House Lolly Shop**, Shop 3, 11 Park Lane, Ocean Grove — the other
  hospitality leftover. **No website found**, Facebook and Instagram only.
- **The Pier View Lolly Shop**, 92A Newcombe St, Portarlington — 150+ pick-and-mix,
  7 days 10–5. ⚠️ pierviewlollyshop.com.au would not resolve.
- **Anglesea Fruitz Provedore**, Shop 2, 63 Great Ocean Rd — greengrocer and
  provedore. ⚠️ **angleseafruitz.com 404s** — treat the domain as dead.
- **Wildings Pantry Essentials**, 3/1376 Murradoc Rd, St Leonards. wildings.com.au.
- **Wallington's Local Pantry**, 370 Grubb Rd, Wallington. wallingtons.com.au.
- **Griggs Creek Providore** — **two sites**, 103 Centennial Blvd, Curlewis and
  1370 Murradoc Rd, St Leonards. ⚠️ domain would not resolve.
- **Adelia Fine Foods / Bellarine Brownie Co**, 13–14 Sykes Pl, Ocean Grove.
- **Bellarine Fungi**, Drysdale — gourmet mushroom farm, **by appointment only**,
  no street address published. bellarinefungi.com.au.
- **Advance Mussel Supply**, 230–250 Queenscliff Rd, Portarlington — 25-yr family
  mussel farm with on-site café. (The Little Mussel Cafe is already listed and is
  this farm's cafe — check before adding a second row.)
- **Glenkeen Honey**, 615 Great Ocean Rd, Bellbrae — no own site, farm-gate
  access not published.
- **Bliss + Co Wholefoods**, 64A The Terrace, Ocean Grove. ⚠️ its domain has a
  **TLS hostname mismatch** and will not load; published hours are from a 2020
  article and are stale.
- **Lara Quality Meats** and **The Produce Corner** (greengrocer), Lara —
  OSM leads, not yet confirmed first-party.
- **The Little Deli & Panini Bar**, Werribee — OSM lead, not confirmed.
- Geelong destinations worth confirming: **Freckleberry Chocolate Factory**,
  **Cheese Therapy**, **Geelong Vintage Market** (3 Mackey St, North Geelong —
  permanent indoor market, a `shop` kind), **Organic Larder**.

### market — one more found by the sweep
- **Bellarine Farm Gate**, 218 Murradoc Rd, Drysdale — growers' market run by the
  Bellarine Peninsula Growers, Producers and Consumers Association, **Sat 9–2 and
  Sun 10–1**. bellarinefarmgate.com.au. This is where most of the no-door
  producers below actually sell. It was not in the market half's sources and is a
  real gap.
- OSM's Apollo Bay entry "Saturday homemade market" (`amenity=marketplace`) is
  the **Apollo Bay Community Market**, written this pass as event 158. Match confirmed.

### Confirmed NOT to list — no public door
Sea Bounty (wholesale, no retail door), Bellagreen Organic Farm (veggie boxes,
no farm gate), Shire House Farm (own site says "not yet fully open"), Bella Flora
Farm (no visits), Storm Haven Produce, Mayfarm, Becks Honey, Birdland Seeds,
Wild Earth Tallow, The Boroughs Own — all markets/online only.
Inglenook Dairy, Otway Beef and Symons Organic Dairy are listed by Bellarine Farm
Gate but are **not on the Bellarine** (Inglenook is Dunnstown, near Ballarat).
Mt Moriac Olives is online-only — **no farm gate, do not list as a visit**.

### Two negative findings worth keeping
1. **There is no visitable olive grove on the Bellarine.** Bellarine olive oil
   appears only as a stocked product. **No olive harvest season to record** —
   the group prompt asks for olive harvest as a season and the honest answer is
   that there is nothing here to hang it on.
2. **No cherry farm and no apple u-pick in the region.** The only u-pick is
   strawberries at Lomas (Nov–May, from their own page) and berries at
   Tuckerberry Hill (season announced each year, not fixed). Apples at Lomas are
   farm-shop, not u-pick.

## Suburb-vocabulary gaps found in half two
`SUBURBS` has no **Murroon** (Pennyroyal Raspberry Farm), no **Ceres** (already
used by Bird Rock Farm), no **Gellibrand** (a whole u-pick cluster: Otway
Blueberries, The Little Organic Paddock, Glen Loch Apple Farm, Country Dahlias),
no **Warncoort**, **Kawarren** or **Yeo**, and no **Bannockburn**.
The Gellibrand cluster is the significant one — four u-pick farms with real
seasons, stranded.

## Best recurring source found
The **Otway Harvest Trail** annual guide PDF
(otwayharvesttrail.org.au) and **bellarinefarmgate.com.au** between them produced
most of what OSM missed, with member status and seasonality already curated.
Both are worth treating as an annual import rather than a one-off search.

## What was written — 26 activities, 465–490

**nursery (3):** Van Loon's Nursery & Café 465 · The Beach Willow 466 ·
Great Ocean Road Nursery 467
**farm life (3):** Lomas Orchards 468 · Tuckerberry Hill Berry Farm 469 ·
Portarlington Mussel Tours 470
**produce (20):** Dustys Bulk Foods 471 · Peach's Torquay 472 · Winchelsea
Wholefoods 473 · The Store Deans Marsh 474 · Hilbilby Cultured Food 475 ·
Farmers Harvest 476 · White Fisheries 477 · Bellarine Smokehouse + Provedore 478
· Wattle Grove Honey 479 · Lonsdale Tomato Farm 480 · Sweet View 481 ·
The Olive Pit 482 · The Beach House Lolly Shop 483 · The Pier View Lolly Shop 484
· Anglesea Fruitz Provedore 485 · Wildings Pantry Essentials 486 ·
Wallington's Local Pantry 487 · Griggs Creek Providore 488 · Adelia Fine Foods 489
· Bliss + Co Wholefoods 490

Per town: Wallington 4, Ocean Grove 4, Drysdale 3, Torquay 3, Portarlington 3,
Bellbrae 1, Mt Duneed 1, Winchelsea 1, Deans Marsh 1, Apollo Bay 1, Anglesea 1,
St Leonards 1, Curlewis 1, Marcus Hill 1.

All 26 carry `kind: "venue"`, set explicitly. That matters: `KIND_OF` maps
`farm life` to **spot**, so Lomas and Tuckerberry Hill would have been
classified as spots on their primary type. Each carries `produce` alongside
`farm life` and an explicit kind, which is the `Common Ground Project` pattern.

**21 of 26 are pinned; 5 are deliberately null.** Every pin was reverse-geocoded
after writing and all 21 came back to a road and a suburb — none is in the water.
The five without pins are The Beach Willow, Great Ocean Road Nursery,
Tuckerberry Hill, Farmers Harvest and Anglesea Fruitz: Nominatim would only offer
a road centreline for each.

**Anglesea Fruitz is the clearest argument this project has for that rule.** Two
queries for the same address returned two different Great Ocean Road centrelines
**1.5 km apart**. Either would have looked like a coordinate in the column.

Two geocodes are honest but odd and are recorded on their rows: Dustys Bulk Foods
sits on the building OSM labels *Torquay Toys* (right address, the map knows a
different tenant), and The Pier View Lolly Shop is pinned to 92B rather than 92A
Newcombe Street — the adjacent unit in the same building.

## Two things the duplicate sweep caught

- **`Lard Ass Butter` was already listed** as activity 260. It came through the
  Bellarine Taste Trail research as a new find; one `ilike` on the distinctive
  word stopped it. This is the third pass in a row where the near-miss check has
  earned its place, and `sync.py add` would not have caught it — the names match
  exactly, so it *would* have been refused, but only after the batch failed.
- **Portarlington Nursery was dropped.** No website, and the only geocode for
  1/44 Newcombe Street resolved to a Bendigo Bank. Not enough to write a row.

## Two tooling bugs found

1. **`nearby.py --kinds` needs an equals sign and its own docstring says
   otherwise.** Line 263 reads only `--kinds=produce`; given `--kinds produce`
   it silently falls back to `food` and swallows the word `produce` as part of
   the town name. A sweep run the way the docstring shows returns the wrong
   category with no error at all. `by-group.md` has it right, the docstring does
   not.
2. **`season` is an array column and `RESEARCH_RULES.md` does not say so.**
   Writing `"season": "Strawberry picking November to May"` failed mid-batch with
   a raw Postgres `22P02 malformed array literal`, after three rows had already
   been written. The vocabulary in use is `any`, `spring`, `summer`, `autumn`,
   `winter` (plus one stray `low tide` on an existing row). The rules file lists
   `season` as a field but never says it is a list or what the values are —
   worth adding beside the `conditions` list.

## Still open after this pass

- **Geelong and the northern towns got the OSM sweep but not the by-hand check**
  the other regions got. Geelong's 35 unlisted are mostly neighbourhood
  greengrocers, butchers and nine florists, which fail the reason-to-go test —
  but Freckleberry Chocolate Factory, Cheese Therapy, Geelong Vintage Market and
  Organic Larder are real destinations and are unconfirmed.
- **The Gellibrand u-pick cluster is stranded** by the suburb vocabulary: Otway
  Blueberries, The Little Organic Paddock, Glen Loch Apple Farm and Country
  Dahlias, four farms with real seasons.
- **Bellarine Fungi** — a real producer, appointment only, but publishes no
  street address, so there is nowhere to stand.
- The 12 market events are all `verified = false` and sit in `sync.py pending`.
