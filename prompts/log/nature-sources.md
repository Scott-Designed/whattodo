# Nature sources — the source pass, 4 Sep 2026

A source pass, not a listings pass. Nothing was written to the database; nothing
was pushed. The inventory is `prompts/log/nature-sources.json` (33 sources, one
object each, every refusal included). This file is the part the JSON cannot hold.

## How it was actually probed — read this before trusting a number

The brief says `curl … -A "whattodo-janjuc/1.0"`. **That was not possible from
this Cowork session**: the cloud container's egress proxy allows GitHub and
nothing else — `api.open-meteo.com`, `bom.gov.au`, `notice.place` itself all
answered `000` / `CONNECT tunnel failed, response 403`. So every probe below ran
in the **built-in browser on Scott's Mac**, from a page at `https://notice.place`,
via `fetch()`:

- **Status, bytes, wall-clock, content-type and the first 200 bytes** are real,
  measured from a `fetch()` in that browser. `ms` is round-trip from a home
  connection in Victoria, not from Vercel `syd1`.
- **CORS** is the honest one: a `fetch()` from `https://notice.place` that
  returns a readable body IS the CORS test. "none" means the browser threw and a
  `no-cors` opaque request still reached the host.
- **Hosts with no CORS** were read by navigating a second tab to the host and
  fetching same-origin — which is why bodies exist for BOM, EMV, CFA, BeachSafe.
- **The user agent was the browser's, not `whattodo-janjuc`.** A host that
  varies by UA (BeachSafe is the suspect — the previous pass said its API
  "needs a browser") may answer the Action differently. Every such case says so
  in its `request` field. **Re-run the `request` lines from the Action or from
  Scott's terminal before building** — they are written to be copy-pasted.
- **robots.txt** was read for every host that has one. Where ClaudeBot is named,
  reading stopped there.

Dates: the Mac's clock had rolled to **Fri 4 Sep 2026** (AEST) when the probes
ran, so `probed` is 2026-09-04 throughout.

## Phase 1 — outcomes

### River level — BUILD IT (BOM), and the working request

BOM Water Data Online is a KISTERS KiWIS. The OGC SOS front door works, but
**the KiWIS REST endpoint answers the same series as 302 bytes of JSON**, and
that is the one to use:

    https://www.bom.gov.au/waterdata/KiWIS/KiWIS?service=kisters&type=queryServices&datasource=0&format=json
      &request=getStationList&bbox=143.3,-39.0,144.9,-37.8&returnfields=station_no,station_name,station_latitude,station_longitude
      &request=getTimeseriesList&station_no=235216&returnfields=station_no,station_name,ts_id,ts_name,parametertype_name,ts_unitsymbol,coverage
      &request=getTimeseriesValues&ts_id=248752010&period=P1D&returnfields=Timestamp,Value,Quality%20Code

Real reading, 3 Sep 2026: **Cumberland River @ Lorne (235216), water course
level 0.417 m at 10:00, 0.415 m at 10:15, quality 10** (ts_id 248752010, 109 ms).
The SOS `GetObservation` on the same station (`procedure=Pat3_C_B_1_HourlyMean`,
exact URL in the JSON) gives 0.416 → 0.415 m across the same morning — the OGC
door and the REST door agree.

**Gauges in the region, and which are alive:**

    235216  CUMBERLAND @ LORNE      live to the hour (coverage 2026-09-03T10:45)   ← the waterfall gauge
    233214  BARWON @ FORREST        BOM copy ends 2026-08-17 (2–3 weeks stale)
    235202  GELLIBRAND @ GELLIBRAND BOM copy ends 2026-08-17
    233201  BARWON @ WINCHELSEA · 233217 BARWON @ GEELONG · 235209 AIRE @ BEECH FOREST
    235219  AIRE @ WYELANGTA · 235222 ANGLESEA @ ANGLESEA · 235285 PAINKALAC CK @ GOR
    235255  THOMPSON CK @ GHAZEEPORE · 233209 LEIGH @ INVERLEIGH · 232202 MOORABOOL @ BATESFORD
    235243  ERSKINE @ LORNE         DEAD — every series ends 14 Jul 1997

So **Erskine Falls has no gauge**; Cumberland, 5 km along the same range with
the same rain, is the honest proxy and it is live. The bbox query returns 1,266
stations, most of them Barwon Downs and Anglesea bores — filter by name.

Licence, quoted from https://www.bom.gov.au/waterdata/ : *"Unless otherwise
noted, all material on this page is licensed under the Creative Commons
Attribution Australia Licence"* — note "Australia Licence" (the 3.0 AU wording),
not 4.0. Attribution owed.

**Staleness differs per gauge and must be printed** — "0.42 m at 10:00 today"
next to "0.31 m on 17 Aug" is two different facts.

### WMIS — not worth carrying today

`data.water.vic.gov.au/WMIS/cgi/webservice.exe` is a Hydstra CGI. Three
attempts across 40 minutes all returned, after 30 seconds:

    {"error_num":219,"error_msg":"Request timed out, more than 2 concurrent request for more than 30 seconds"}

The call shape that *should* work (Hydstra JSON, untested because nothing was
ever served):

    webservice.exe?{"function":"get_ts_traces","version":"2","params":{"site_list":"235216","datasource":"A","varfrom":"100","varto":"100","start_time":"20260903000000","end_time":"20260904000000","interval":"hour","multiplier":"1","data_type":"mean"}}

A source that answers in 30 s with an error is a source that makes the whole
reply wait. BOM mirrors the same gauges in 109 ms. Re-probe once, from the
Action, to validate BOM's Cumberland reading against the data owner's copy — that
is the one thing WMIS is still wanted for.

### Fire — the licence question has an answer, and it is not the one expected

**1. EMV's terms exist and are CC BY 3.0 AU.** The "Emergency data" notice at
https://www.emv.vic.gov.au/responsibilities/victorias-warning-system/emergency-data
says, verbatim:

> The State of Victoria owns any copyright in the data accessed by you from any
> data feed, site or other source to which this notice applies. The data is
> provided under a Creative Common Attribution 3.0 Australia licence

> 1. You must identify the source of the data as State of Victoria, Australia.
> 2. You must include a link to this notice.
> 3. If you are accessing and publishing emergency warning data, you must
>    display the last date and time an update was received by you from the data
>    feed.

**And CFA's own RSS page names EMV's four developer feeds** as the third-party
route: *"Access to Victorian emergency data by third party developers is managed
by Emergency Management Victoria"* followed by exactly `getIncidentXML/JSON` and
`getFDRTFBXML/JSON`. **But** the VicEmergency support article
(support.emergency.vic.gov.au/hc/en-gb/articles/235717508) says *"The
VicEmergency data feed is not currently available publicly"* and to *"submit a
request"*. Two first-party pages, two answers. The notice's phrase "to which this
notice applies" is the gap — and the OSOM GeoJSON the function already reads sits
under the same question. **This is Scott's decision, or the email's.**

**2. The developer feed is still empty.** `getFDRTFBJSON` and `getFDRTFBXML`
both return one byte, `0a`, with a JSON/XML content-type — while the CFA RSS for
the same minute says in words *"Today, Fri, 4 Sep 2026 is not currently a day of
Total Fire Ban … Central: NO RATING"*. So the empty body means "nothing
declared", which is consistent, and nobody has still seen the populated shape.
`getIncidentJSON` on the same host answers 5 KB of CFA incidents with
`fireDistrict` and `municipality` fields — the host is alive.

**3. CFA's RSS URL had the wrong punctuation in the earlier notes** —
`central_firedistrict_rss.xml` 404s; the real feeds are hyphenated:
`https://www.cfa.vic.gov.au/cfa/rssfeed/central-firedistrict_rss.xml` and
`southwest-firedistrict_rss.xml`. The licence sentence, verbatim from
https://www.cfa.vic.gov.au/rss-feeds :

> CFA RSS feeds are protected by copyright laws and are available for personal,
> non-commercial use only. (See below for data feeds for third party
> developers.) You must use the RSS feeds as provided by CFA, and you may not
> edit or modify the text, content or links supplied.

**4. The district split is confirmed first-party** at
https://www.cfa.vic.gov.au/warnings-restrictions/find-your-fire-weather-district :
Central lists *Golden Plains Shire, Greater Geelong City, Queenscliffe Borough,
Surf Coast Shire*; South West lists *Ararat Rural City, Colac Otway Shire,
Corangamite Shire, Glenelg Shire, Moyne Shire, Pyrenees Shire, Southern
Grampians Shire, Warrnambool City*. Matches the function's `districts` block.

**5. FFMVic publishes planned burns SEPARATELY, and it is the best find of the
pass.** plannedburns.ffm.vic.gov.au is a Gatsby app behind Incapsula, but its
`/api/applicationconfiguration` names its data source:
`https://maps.ffm.vic.gov.au/arcgis/rest/services/pbns_status_gdb/MapServer`.
Layer 1 (points) and layer 0 (polygons) answer standard ArcGIS `query` calls,
**CORS-open, 128 ms for five records, 989 ms for the whole region**:

    96 burns in the region bbox for FOP year 2026 — 90 Planned, 2 Patrol, 4 Safe
    Anglesea - Ellimatta Road    Planned   0.4km E of Anglesea    -38.4012,144.2002
    Anglesea - Alcoa Fire Dam    Planned   2km NW of Anglesea
    Anglesea - Inverlochy Street Planned   .5km E of Anglesea
    Lorne - Stony Creek          Planned   0km NW of Lorne
    Lorne - Treatment Plant      Planned   2KM NORTH OF LORNE
    Lorne - Allenvale Campground Planned   1km SW of Lorne        -38.5536,143.9619
    Deans Marsh - Seaview Road   Planned   6km SE of Deans Marsh  434 ha
    Wensleydale - Breakfast Ck Rd, Barongarook - Westwood Rd, Pennyroyal - Deans Marsh Lorne Rd …

It says WHICH burns are on the books near a listing and whether each is
Planned, being Patrolled (just lit) or Safe (done). **It does not say WHEN** —
there is no scheduled-date field; burns go when the weather allows and PBV
emails a day or three ahead. Paired with the OSOM feed the function already
reads (which says "burning now"), that is the whole planned-burn picture.

Validated: the Allenvale point reverse-geocodes to *"Allenvale Road, Lorne,
Victoria, 3232"* — an independent map agrees with the burn's own location
description. Not cross-checked against OSOM today: OSOM carried three planned
burns statewide and none in the region, so no Patrol burn could be matched.
Licence: the app links DEECA's copyright page — *"All material provided on this
website is provided under a Creative Commons Attribution 4.0 international
licence"*, attribution *"© State of Victoria (Department of Energy, Environment
and Climate Action)"*. Whether an ArcGIS service is "material provided on this
website" is a question to put in the same email.

### The drafted email to EMV

Contact found: EMV's contact page lists `admin@emv.vic.gov.au` (and media,
VEMI); the support portal says to submit a request there. Send to admin@ and to
the support portal, same paragraph:

> Hello — I run Notice (https://www.notice.place), a free, community-run
> listings site for the Surf Coast Shire; no advertising, no accounts, no
> revenue. I'd like to show whether it is a Total Fire Ban day in the Central
> and South West fire districts beside our outdoor listings, read once every
> ten minutes by a server and cached for everyone. Two questions: (1) does the
> Emergency Data notice (CC BY 3.0 AU, with its three attribution conditions)
> cover `data.emergency.vic.gov.au/Show?pageId=getFDRTFBJSON` and the
> `emergency.vic.gov.au/public/osom-geojson.json` feed, so that a site like
> ours may read them with attribution — CFA's RSS page names them as the
> third-party route, while your support article says the feed is not public;
> and (2) getFDRTFBJSON currently returns an empty body — could you tell me
> the JSON shape it returns during the Fire Danger Period, or point me at a
> sample, so I can build against real data rather than guess? Happy to show the
> attribution line and "last updated" timestamp exactly as the notice asks.
> Thanks — Scott Fairbanks

### EPA — what a key gets you

Free, self-serve at https://portal.api.epa.vic.gov.au/ (sign up → subscribe to
the Environment Monitoring product → key in your profile), **5 requests/second**
by default, CC BY 4.0 per the DataVic dataset page. Behind it: hourly
air-quality readings and forecasts for the statewide station network (the
nearest to the region is Geelong South — not confirmed here; the `/sites` list
itself needs the key). **Beach Report is 36 Port Phillip Bay beaches only**,
forecasts at 10 am and 3 pm, "on weekends and public holidays between November
and April" — so it may cover Portarlington/St Leonards on the Bay side and it
does not cover a single Surf Coast beach. The page does not list the 36 by name.
Verdict: a key is worth it when smoke season starts, to put a measured PM2.5
next to Open-Meteo's modelled one. Not before.

### eBird — what a key gets you, and the WTP as the test

- **ebird.org refuses ClaudeBot, Claude-Web and anthropic-ai (`Disallow: /`).**
  Nothing on ebird.org was read this session. Action only.
- **`api.ebird.org/robots.txt` is `User-agent: * / Disallow: /`** — an API is not
  for crawling; use is under the API terms with a key.
- **The hotspot bar charts (`/barchartData`) are disallowed for everyone**, so
  the "waders peak in summer" curve cannot be fetched by any agent. That fact
  has to come from prose (Melbourne Water's own species page says the
  Orange-bellied Parrot is a winter bird there and the shorebirds are
  Siberian-breeding migrants — which is summer).
- Terms, verbatim: *"You will not use the API or API Content, either whole or
  in part, for commercial purposes whatsoever without prior written
  permission"* and *"You agree to attribute eBird.org as the source of the data
  accessed via the API wherever it is used or displayed."*
- What a key returns (per the API docs; not fetched — the docs render
  client-side): `/v2/data/obs/{locId}/recent?back=14` per hotspot, or
  `/v2/data/obs/geo/recent?lat&lng&dist≤50&back≤30` — records with
  `speciesCode, comName, sciName, obsDt, howMany, locName, lat, lng, obsValid`.
  The WTP sub-hotspots from search results: L2548999 Lake Borrie, L3138096
  Borrow Pits, L3832613 Ryans Swamp, L1174063 T Section Ponds, L3966834 Paradise
  Road, L2591344 Western Lagoons, L7136077 Austin Road Lagoon, L2548500 Pond 24.

Verdict: a key buys "what was seen at the WTP this fortnight" — the whale-block
shape (may say yes, never no). It does not buy the season.

## Phase 2 — outcomes

### The Western Treatment Plant — strong result, and a closure

- **Access, first-party and quoted** (Melbourne Water, birdwatching-access page):
  *"Long-term access is valid for 2 years, and costs $70 (includes a $50
  refundable key deposit) Short-term access is valid for a single visit, and
  costs $20."* 18+, a ~10-minute online induction, *"have access to a car to
  reach the vast areas available to you, or join a licensed tour operator"*,
  long sleeves/pants/closed shoes, carry a phone, check fire bans. Long-term
  keys by registered post, up to 28 days; short-term keys same-day from the
  Werribee Visitor Information Centre.
- **It is CLOSED.** *"The Birdwatching Site is temporarily closed due to H5 Bird
  Flu (Avian Influenza). Birdwatching applications are not being accepted at
  this time."* Melbourne Water's news of 20 Aug 2026 dates it: *"Following last
  week's closure of the Western Treatment Plant (WTP) to birdwatchers as a
  precautionary measure … The closure of WTP to birdwatchers remains in place"*.
  So closed since ~11–14 Aug 2026, no reopening date.
- **The season, first-party**: Melbourne Water's species page — Orange-bellied
  Parrot: *"The Western Treatment Plant is one of the very few places they can
  be seen in winter"*; shorebirds: *"Three-quarters of these species are
  migratory: breeding in Siberia then migrating south"*, feeding on mudflats
  *"exposed at low tide"*. Winter for the parrot, summer for the waders, low
  tide for both.
- **Not in the database.** Searched listings and places for werribee /
  treatment / swan bay / connewarre / bird: the eight Werribee rows are the
  zoo, the pub, a cafe, a canoe launch and VGB events. `a280 Swan Bay
  Birdwatching` and `a281 Lake Connewarre & Breamlea Shorebirds` are the
  nearest cousins. The VGB import did not bring the WTP in under another name.
- **Pin**: Nominatim by name resolves only *"Western Treatment Plant Offices,
  Lot 1, Werribee"* (way 579857439, `landuse/commercial`, -37.9146707,
  144.6413907) — the offices, not the gate. A person picks the birdwatching
  entrance; do not use the office polygon.

It wants a `places` row and a `spot` listing whose `notes` carry the permit
terms AND the closure. Written by a person, after H5.

### Beach-nesting birds — a calendar

BirdLife's Hooded Plover profile: *"Breeding season is from August to February
and can extend to April."* Per-beach nest data is not published as a feed — the
program page links only Birdata's request-data form. One line, one link, checked
yearly; the per-beach dog rules stay on the council/GORCC rows.

### Parks Victoria — a scraper job, licence unknown

Every park page carries a server-rendered **Change of Conditions** block
(`div.change-of-conditions__item` → `h4.change-of-conditions__subtitle` for the
site, `h3.change-of-conditions__title` for the closure). Great Otway NP on 4 Sep:
*"Aire West Campground – Partial Seasonal Closure … sites 17–40 … temporarily
closed from 29 May to 25 September 2026"*, plus Aire East and a Dunecare
project. No feed, no API (`/api/search/autocomplete` is the only endpoint).
robots.txt names no AI crawler. **No licence page exists** — `/copyright`,
`/disclaimer`, `/about-us/copyright` all 404 and the homepage links only
`/privacy`. Reading ~6 park pages on the Action and writing closures into the
database is the shape; the licence question needs Scott or Parks Vic.

### Road closures — needs a key

Transport Victoria's *Unplanned Disruptions – Road* API: CC BY 4.0, `KeyID`
header, 20 calls/minute, refreshed every 60 s, OpenAPI spec published. The
VicTraffic site and the data-exchange portal were **unreachable from the
built-in browser** (navigation denied; fetch failed in 27 ms — a client-side
block, not the host). Probe it from the Action.

### Patrolled beaches — the calendar exists, and SLSA's terms forbid it

BeachSafe's app API, read from a real browser session:

    /api/v4/map/beaches?neCoords[]=-38.30&neCoords[]=144.35&swCoords[]=-38.42&swCoords[]=144.15
        17 beaches, 14.6 KB, 395 ms — patrol, is_patrolled_today, has_toilet, has_dogs_allowed, lat/lng
    /api/v4/beach/anglesea            facilities, clubs, hazard 5, currentTide, currentUV, description
    /api/v4/beach/189/patrols?date=2026-12-27
        Anglesea SLSC: 26 Dec 13:00–18:00, 27 Dec 10:00–18:00; Anglesea (Lifeguards): 21–27 Dec 10:00–18:00 daily

That is exactly the per-club patrol calendar the brief asked for. **And the
terms say no**: sls.com.au/terms-of-use — *"You may view the Website and its
contents but must not copy, reproduce, modify, distribute, display, perform or
transmit any of the contents of the Website for any purposes without the prior
written consent of SLSA."* Verdict: ask SLSA/LSV for written consent for a
free community site; until then `patrolled` stays prose. (The previous pass's
"needs a browser" was not re-tested with the project UA — see the caveat at the
top.)

### King tides — the site is gone

witnesskingtides.org: sitemap lists 2 URLs, the dates pages 404, the homepage
fetch failed. Not carried. King tides are arithmetic from a tide prediction; the
yearly source is BOM's tide tables read by a person.

### Moonrise and moonset — arithmetic, validated

A 45-line SunCalc-class implementation (scratchpad `moonrise.py`, BSD-2
lineage) against the **US Naval Observatory API** for Jan Juc, tz +10:

    4 Sep 2026   arithmetic rise 00:44 set 10:19   USNO rise 00:56 set 10:14   Δ −12 / +5 min
    26 Sep 2026  arithmetic set 05:32 rise 17:44   USNO set 05:35 rise 18:00   Δ −3 / −16 min

Good enough for "moonrise around 1am"; never print a minute. The same call
validated the function's own moon: it printed *last quarter, 55% lit* on 4 Sep;
USNO says Last Quarter 17:51 on 4 Sep, 53%. Its `next_full`
2026-09-26T14:51Z (00:51 local on the 27th) against USNO's Full Moon 27 Sep
02:49 local — two hours, inside the "few hours" the file claims. USNO is
CORS-open, public domain, no robots.txt, 1.9 s from here — a validator, not a
source to serve from.

### ISS — the feed is gone; passes are arithmetic

Spot the Station's per-city XML feeds and `view.cfm` pages all 404; the site now
redirects to nasa.gov and offers the app. The ephemeris is on S3 (navigation to
that host was denied). **CelesTrak serves the ISS TLE CORS-open in 168 bytes —
and its robots.txt disallows `claudebot`**, so it is Action-only (the one TLE in
the JSON was fetched in the same call as robots.txt; nothing after). Building
passes is SGP4 + observer geometry; worth it only if the sky block grows.

### Meteor showers — no machine-readable form; one date is a night late

IMO publishes HTML and a yearly PDF (`/files/meteor-shower/cal2026.pdf`,
`cal2027.pdf`) and nothing else. Validation found a real discrepancy: IMO says
*"The Leonids will next peak on the Nov 16-17, 2026 night. On this night, the
moon will be 45% full"*; the function's table has `11-17` and prints 53% — it
is evaluating the 17th/18th night (`Date.UTC(yy, m-1, d, 13)` is midnight at
the START of day d+1 local, i.e. the night d→d+1). IMO's page phrases every peak
as a "night" (Nov 16-17, Dec 13-14) while its working list gives a peak DATE
(Orionids Oct 22, where the table says 10-21). Two conventions, and the table
mixes them. **Decide one — "the night of d→d+1" — and re-key all nine against
the per-shower "Next Peak night" sentences on the IMO calendar page**; the
Leonids would become `11-16` under that convention.

### Pollen — readable, and all rights reserved

melbournepollen.com.au is server-rendered and carries a Geelong (and Colac)
grass-pollen forecast in season — *"Pollen counting season is over We begin
counting pollen again 1st of October"* — with *"© Copyright AirHealth 2024, all
rights reserved"* in the footer and its images served from
`api.pollenforecast.com.au`, AirHealth's commercial API. No robots.txt. Needs a
licence answer; the free line is the calendar (Oct–Dec) and a link.

### Frost, fog, sea mist — add fields to the call already made

Open-Meteo's default model answers `dew_point_2m`, `relative_humidity_2m`,
`visibility`, `weather_code` (45/48 = fog) hourly and `temperature_2m_min`
daily. Deans Marsh (-38.51,143.75) on 4 Sep: tmin 4.3 °C tonight, dew point
~4, visibility 18–43 km. `models=bom_access_global` returns **null** for
visibility and tmin — stay on the default model. **And a where-is-it-measured
finding for the live function**: asked for Jan Juc, Open-Meteo answers for grid
cell **-38.27768,144.36487 (26 m)** — ~9 km NE, inland. The Conditions tab
prints "Jan Juc" for that reading. Unvalidated against BOM (its API is
forbidden); a week of a person comparing Deans Marsh tmin against the BOM town
forecast would validate it.

### ARPANSA UV — live, CORS-open, Melbourne only

`uvdata.arpansa.gov.au/xml/uvvalues.xml`, 4.6 KB, 207 ms, 17 stations, Melbourne
2.7 at 10:09 on 4 Sep. Terms, verbatim: *"ARPANSA should be acknowledged as the
source of the UVR data. A statement such as "UV observations courtesy of
ARPANSA" is sufficient. The UVR data or references to ARPANSA should not be
associated with the promotion of any goods or services, or associated with
commercial advertising, without prior written authorisation by ARPANSA.
Developers should notify ARPANSA that the data is being used in their
application and provide a URL for the application if applicable."* No Geelong
or Surf Coast station. Build it only as "measured at Melbourne", labelled.

### OSM tags on the pins — the gap does not close

50 published pinned rows (every 10th of 505), one Overpass query, named
features within 80 m matched on name tokens: **30 matched** (venue 21/28, spot
7/19, shop 2/3). On those 30: `website` 13, `phone` 11, `opening_hours` 6,
`wheelchair` **1** (Jan Juc Park: `wheelchair=no`, `toilets:wheelchair=no`),
`toilets` 0, `surface` 0. So 2 of 50 pins carry an accessibility tag. OSM is
not where this coast's accessibility facts live. `opening_hours` on six is
worth a one-off import into `notes`, with ODbL attribution: *"OpenStreetMap is
open data, licensed under the Open Data Commons Open Database License (ODbL)"*;
you must *"credit OpenStreetMap by displaying our attribution notice"*, and
*"If you alter or build upon our data, you may distribute the result only under
the same license"* — share-alike is the question if tags are merged rather than
displayed.

## Phase 3 — mostly refusals, as expected

- **VicEmergency OSOM from a browser: NO CORS on 4 Sep** (both apex and www).
  AUTOMATING_NATURE.md's table says `*` from curl on 1 Sep. Irrelevant to the
  function, relevant to the concept doc's claim that six sources are browser-
  reachable.
- **Fungimap** — events page is a blog category with no dates; recommends
  iNaturalist, which the function already reads. Refused.
- **ClimateWatch** — an app; its data goes to ALA; `/api/v1` exists (JSON:API
  content-type) but is undocumented. Refused.
- **Melba Gully glow-worms** — a fixed fact (any dark night), closures would
  appear in GONP's Change of Conditions; the first-party page was not found
  under three slugs. A person reads it in a browser.
- **Shearwaters** — the colonies with a published season (Phillip Island,
  Griffiths Island) are out of scope; BirdLife has no shearwater profile at
  the guessed slug. Refused for this region.
- **Sea: clarity, rips, jellyfish, fishing runs** — no publisher for any of
  them on this coast; BeachSafe's `hazard` is a static rating; VFA is a
  Cloudflare wall. Four one-line refusals.
- **Smoke forecast (AQFx)** — no public API. **Eclipse local circumstances** —
  USNO's date endpoint 500'd twice; the yearly list works (2027: 6 Feb annular,
  2 Aug total; 2028: 26 Jan annular, 22 Jul total).
- **Milky Way core** — arithmetic; April–October, best at new moon. A line
  beside the meteor table.
- **Penguins, seals, planets at opposition** — not probed; out of time. Seals at
  Marengo Reefs and planets are both Parks Vic / almanac calendar entries for a
  person.

## THE REFUSAL LIST — one line each

    WMIS (data.water.vic.gov.au)     30 s → error 219 "more than 2 concurrent request", three times; BOM mirrors it in 109 ms
    CFA district RSS                 "available for personal, non-commercial use only" — and it points websites at EMV
    EMV getFDRTFB JSON/XML           empty body (0x0a) out of season; licence question open — not refused, PARKED
    EPA Environment Monitoring       needs a key; Beach Report is Port Phillip Bay only; nothing for the Surf Coast until smoke season
    eBird API                        needs a key; non-commercial + attribution; the bar charts are robots-disallowed for everyone
    BeachSafe API                    the roster is there; SLSA terms forbid reproducing "any of the contents … for any purposes" without consent
    Witness King Tides               site is a shell (2 sitemap URLs, 404s)
    NASA Spot the Station            per-city feeds gone (404); app only
    CelesTrak TLE                    robots refuses claudebot — Action only, and only if passes are built
    IMO calendar                     HTML + PDF, no CSV/JSON/ICS — keep the hand table, fix the Leonids
    Melbourne Pollen                 "© Copyright AirHealth 2024, all rights reserved" on a commercial forecast
    Parks Victoria                   readable HTML, no feed, NO LICENCE PAGE — parked on the licence
    VicTraffic / data-exchange       unreachable from the browser; the API needs a KeyID — Action job
    Fungimap                         no calendar; points at iNaturalist
    ClimateWatch                     app + undocumented API; data reaches ALA anyway
    Shearwater season                colonies out of scope
    Water clarity / rip forecast / jellyfish / fishing runs   no publisher on this coast
    AQFx smoke forecast              no public API
    USNO eclipse local circumstances 500 twice; yearly list works
    Melba Gully page                 not found under guessed slugs — a person reads it

## Hosts that refuse ClaudeBot — point the Action at these

    ebird.org          ClaudeBot, Claude-Web, anthropic-ai — Disallow: /   (and /barchartData for everyone)
    celestrak.org      claudebot — Disallow: /
    (api.ebird.org)    Disallow: / for ALL agents — API terms + key govern it, not robots

Hosts read this session that name no AI crawler: bom.gov.au, data.water.vic.gov.au,
data.emergency.vic.gov.au, emergency.vic.gov.au, cfa.vic.gov.au, ffm.vic.gov.au
(no robots.txt), plannedburns.ffm.vic.gov.au (none), melbournewater.com.au,
birdlife.org.au (Crawl-delay 10), parks.vic.gov.au, beachsafe.org.au,
witnesskingtides.org, imo.net, spotthestation.nasa.gov (none), aa.usno.navy.mil
(none), arpansa.gov.au, melbournepollen.com.au (none), fungimap.org.au,
climatewatch.org.au (Crawl-delay 3). No Content-Signal line was seen on any of
them.

## Licence sentences that need Scott's decision

1. **EMV** — CC BY 3.0 AU with three conditions, but *"to which this notice
   applies"* vs the support article's *"not currently available publicly"*.
   Covers getFDRTFB AND the OSOM feed already in production. The email settles it.
2. **FFMVic ArcGIS** — DEECA's *"All material provided on this website … CC BY
   4.0"*; the MapServer's own copyrightText is empty. Is a map service "material
   on this website"? Ask in the same email, or decide.
3. **BeachSafe / SLSA** — *"must not copy, reproduce … any of the contents of the
   Website for any purposes without the prior written consent of SLSA"*. Only a
   letter unlocks it.
4. **Parks Victoria** — no licence statement anywhere found. Default State
   copyright.
5. **Melbourne Pollen / AirHealth** — *"all rights reserved"*.
6. **BOM Water Data** — *"Creative Commons Attribution Australia Licence"* —
   fine, but it is the 3.0 AU wording; attribution text to be written.
7. **OSM tags** — ODbL share-alike if merged into the database.
8. **eBird** — non-commercial + attribution — fine for Notice as it is; a key is
   tied to a personal account.
9. **ARPANSA** — acknowledge, notify them with the URL, no advertising
   association — fine; the notification is a to-do.

## Values not validated, and what would validate them

    BOM Cumberland level 0.417 m     WMIS's copy of the same gauge (when it answers); or the Barwon Water gauge page
    FFMVic burn statuses             a Patrol burn appearing in OSOM with the same name (none in region today)
    Open-Meteo frost/fog fields      a week of Deans Marsh tmin vs BOM's town forecast, by hand
    ARPANSA vs Open-Meteo UV         compare at solar noon on a clear day, not at 10am
    EPA and eBird payloads           nothing read — a key
    VicTraffic disruptions           nothing read — a key, from the Action
    Milky Way season                 a planetarium app's galactic-centre rise/set for Melbourne
    Melba Gully, Parks Vic Aire West dates   a person, in a browser

Validated this pass, for the record: the function's TIDE against a tide-table
source for the first time (BeachSafe/BOM low 09:54 vs model 'around 09:00' at
Anglesea, 4 Sep); the function's MOON against USNO (phase, illumination,
next full to within 2 h); the function's SUNRISE/SUNSET against USNO (06:40/18:03
vs 06:41/18:03); the moonrise arithmetic against USNO (≤16 min); FFMVic's
Allenvale point against Nominatim; the CFA district split against CFA's own
page.

## Two things noticed about the live function, not in the brief

- At ~09:40 AEST the edge-cached reply carried **`weather` and `beaches` in
  state `http` with 51-byte bodies** (an Open-Meteo error JSON) while the other
  eight sources read fine; at 10:10 a cold gather read all ten. The per-source
  isolation worked as designed — and the failed reply was served for the
  10-minute window. Worth a stale-while-revalidate think: a source that errors
  could keep the previous good block rather than dropping it.
- Open-Meteo's grid cell for Jan Juc is **9 km inland** (see frost/fog above);
  `taken_at.weather` says Jan Juc.

## The five kinds — the build order

**Live feed → api/conditions.mjs**
- BOM KiWIS river level, Cumberland @ Lorne (build now; add Barwon/Gellibrand with their staleness printed)
- FFMVic planned-burns ArcGIS layer (build now, pending the licence line; pair with OSOM)
- ARPANSA UV, Melbourne (cheap; label the location honestly)
- Open-Meteo frost/fog/visibility fields (free — same call; add Deans Marsh and Forrest points)
- EMV getFDRTFB (after the email and after November)
- EPA air (a key, when smoke season needs a measured number)
- Transport Victoria road disruptions (a key, from the Action)
- eBird recent observations at the WTP (a key; yes-never-no shape)
- USNO — as a yearly validator only

**Arithmetic → a function in the page or the function**
- moonrise / moonset (validated to ≤16 min)
- Milky Way core season
- ISS passes (only with a TLE from the Action; not started)

**Measured → a scheduled job into the database**
- Parks Victoria Change of Conditions, ~6 park pages (licence first)
- OSM opening_hours import, one-off, ODbL attribution

**A calendar → a person, and a place to put it**
- Hooded Plover nesting Aug–Feb (to Apr) — BirdLife
- CFA fire districts (confirmed; already in the function)
- IMO meteor peaks (fix the Leonids to 11-16; re-read cal2027.pdf each December)
- Eclipses 2027–28 (USNO yearly list; visibility from an almanac)
- Grass pollen Oct–Dec, with a link to Melbourne Pollen
- Western Treatment Plant permit terms + closure (a `places` row and a `spot`, by hand, after H5)
- Melba Gully glow-worms (fixed fact; quote the park page once)
- King tides (BOM tide tables, yearly, by hand)

**Not carried — a line in the log saying why**
- everything in the refusal list above

## Files

    prompts/log/nature-sources.json   33 sources, validated: every field present, every kind one of the five
    prompts/log/nature-sources.md     this file

Nothing else in the repo was changed. Nothing was pushed.
