# nature sources — a source pass, not a listings pass

The other prompts in this folder produce rows. This one produces **an inventory
of data sources** — what the weather, the sea, the sky and the living world are
doing on this coast, and where a machine can honestly read that from. Its
nearest relative is the music pass, which was a registry pass rather than a gig
pass: the output is a table of what can be read, with the evidence, not a batch
of listings.

Twenty-eight signals were already probed on 31 Aug – 2 Sep 2026 and ten of them
are live in `api/conditions.mjs`. That work is the floor, not the job. The job
is the next layer down: the sources that were found and not finished, the ones
that need a key, the ones that need a licence answered, and the ones nobody has
looked for yet.

The clone instruction is inside the block, because this file holds one prompt
and the thing you copy has to stand on its own.

---

```text
═══ GETTING THE REPO — DO THIS FIRST ═══

Clone it. Do not go looking for a folder on the Mac, and do not accept a folder someone
suggests. Three Cowork sessions have been lost to this, twice by being pointed at
~/surfcoast-events — which is a real repo and the WRONG one.

  git clone https://github.com/Scott-Designed/whattodo.git
  cd whattodo

The project is public, so an anonymous clone needs no SSH key and no token.

**You never write to the database and never need a credential.** You will not be adding
listings. You are producing files — a source inventory and a worklog — and Scott applies
what he chooses. Do not ask for .env. Nothing gets pushed.

═══ READ FIRST, IN THIS ORDER ═══

1. concepts/AUTOMATING_NATURE.md — the architecture that was decided and why. One function,
   edge-cached, because six of the sources are CORS-open and it STILL should not be called
   from the browser (Open-Meteo allows 10,000 calls a day; three per page load caps the site
   at ~3,300 views, a ceiling that tightens as the site gets busier).

2. The "natural world — /api/conditions" section of CLAUDE.md. Every decision, every
   licence finding, every validation. Read the whole thing — it is where the traps are.

3. api/conditions.mjs itself, top to bottom. The comments are the record of what was
   checked and what was refused, and every source you find has to fit beside these.

4. Then hit the live endpoint and read what it says about itself:

     curl -s https://www.notice.place/api/conditions | python3 -m json.tool | less

   The `sources` block names every source, its host, its licence and whether it answered.
   The `fire` block is a source that was found and deliberately NOT read, with the reason.
   That is the shape of an honest inventory and it is the shape you are producing.

═══ WHAT IS ALREADY DONE — DO NOT REDO IT ═══

Live in the function, all verified against real responses:

  Open-Meteo forecast     air temp, wind, cloud, rain 48h, UV, sunrise, sunset   Jan Juc
  Open-Meteo marine       wave, swell, period, direction, sea state, sea temp    Bells
  Open-Meteo marine       the TIDE, from sea_level_height_msl — verified lunar
                          (mean high-to-high 12.32h against M2's 12.42; spring-neap visible)
  Open-Meteo forecast     wind at 28 beaches in one call, against stored bearings
  Open-Meteo air quality  PM2.5, PM10 (pollen fields return null — Europe only)
  NOAA SWPC               planetary Kp, 1-minute
  VicEmergency OSOM       fires and planned burns as points with coordinates
  iNaturalist             orchids, fungi, all plants — species counts, 30 days, against a
                          stored 12-month baseline; and recent cetacean sightings
  computed                moon phase, next new/full; meteor shower peaks (a fixed table)

Found, probed, and settled as NOT available or NOT wanted — do not re-litigate without new
evidence:

  BOM api.weather.bom.gov.au   forbidden in its own payload: "You must not use, copy or
                               share it." Off the table.
  Open-Meteo pollen            null for Australia. CAMS is Europe only.
  WhaleFace                    the authoritative Victorian sightings source; robots.txt
                               disallows /api/. Link it, do not read it.
  Bioluminescence              five iNaturalist records EVER in the region, three on one
                               night. Not a season, not forecastable. Only the conditions
                               (dark, calm, warm) can honestly be printed.
  Shark sightings              no Victorian feed; NSW SharkSmart is the wrong state and
                               Cloudflared; LSV 403s. And probably should not be carried
                               even if it could be — hours-old safety information on a
                               listings page is worse than none.
  Koala season from iNat       1,377 records, 3x swing — flat. The season people mean is
                               the bellowing, which is a sound, and iNat records sightings.
  Hooded Plover from iNat      peaks in FEBRUARY, nests from AUGUST. February is when
                               people are on the beach. The curve would contradict the
                               fact that matters.

The last two are the rule, not two exceptions: the observation method works where the
organism's visibility IS the phenomenon (a flower is only recorded when it is out) and
fails where it is not. Do not propose an animal season from iNaturalist counts. Propose
where the nesting or migration dates are PUBLISHED and by whom.

═══ THE METHOD — EVERY SOURCE, THE SAME EIGHT CHECKS ═══

This is the whole discipline of the pass. A source that skips a check is not in the
inventory. Do them in this order because each one can end the enquiry:

1. FETCH IT. Do not search for it and describe the search result. curl the endpoint with
   this project's own user agent and record status, content-type, byte count, and the first
   200 bytes:

     curl -sS -A "whattodo-janjuc/1.0 (+https://www.notice.place)" -D - -o body.out \
          --max-time 30 "<url>" ; head -c 200 body.out

   A single newline byte is NOT an empty array. EMV's fire feed returns `0a` out of season
   and nobody has seen its populated shape. If a body is empty, say "empty body" and do
   not describe what it probably contains.

2. ROBOTS. Read /robots.txt on the host and record two verdicts, because they differ:
     - for `whattodo-janjuc` and `User-agent: *` — what the scheduled Action may read
     - for `ClaudeBot` / `anthropic-ai` — what YOU may read, this session
   Coast & Bay, Humanitix and the Victorian Heritage Database all allow the first and
   refuse the second. If the second says no, you stop reading that host right there and
   write "Action only" in the inventory. Also record any Content-Signal line verbatim.

3. LICENCE, IN THE SOURCE'S OWN WORDS. Find the terms page and QUOTE the sentence that
   governs a free community website. Do not paraphrase. CFA's RSS says "available for
   personal, non-commercial use only" and points websites at EMV instead — that sentence
   is the whole reason the fire half is not built. The quote goes in the inventory.

4. CORS. Send `-H "Origin: https://www.notice.place"` and record the
   Access-Control-Allow-Origin header or its absence. This decides nothing on its own
   (see AUTOMATING_NATURE.md) but it is a fact worth having.

5. TIME AND SIZE. Wall clock and bytes. The function gathers everything in parallel and a
   source that takes eight seconds is a source that makes the whole reply wait.

6. WHAT DOES IT ANSWER, AND WHERE. A number with no location is one nobody can check —
   the readings table had to grow a "taken at" column because three different places
   answered one reply. For every value: what is it, what unit, what point on the map,
   how often does it change.

7. VALIDATE ONE VALUE AGAINST SOMETHING INDEPENDENT. This is the check that separates a
   source from a rumour, and this project has three worked examples to copy:
     - the tide: high-water intervals measured at 12.32h against the lunar constituent's
       12.42h — a solar artefact would sit at 12.00
     - the beach bearings: Bells came out 136°, making its offshore a north-westerly,
       which everyone already knows is the Bells offshore
     - the moon: from 20 Aug 2026 it returns a full moon on 28 Aug, which event 11's own
       note already carried from timeanddate
   Pick one value the source gives you and find a second, independent statement of the
   same fact. If you cannot, say so — "unvalidated" is a legitimate entry. "Looks right"
   is not.

8. WHICH OF THE FIVE KINDS. Every source is exactly one of these and the build cost is
   completely different for each:
     live feed        read on a cache window        → api/conditions.mjs
     arithmetic       no network at all             → a function in the page
     measured         slow, from records            → a scheduled job into the database
     a calendar       written once, checked yearly  → a person, and a place to put it
     not carried      unavailable, or wrong to carry → a line in the log saying why

═══ PHASE 1 — FINISH WHAT WAS FOUND ═══

These were located, probed once, and left. Each has a specific open question.

RIVER LEVEL — the best waterfall and paddling signal there is, because it measures the
thing rather than its cause.
  BOM Water Data Online is Creative Commons Attribution (quote it from the page) and serves
  an OGC SOS 2.0 (KISTERS KiWIS) at bom.gov.au/waterdata/services. GetCapabilities answers.
  Find the gauges: Barwon River, Erskine River, Cumberland River, Aire River, Gellibrand,
  anything in the Otways. Get ONE real reading out of GetObservation and record the exact
  request that produced it. It is XML and verbose — this is a scraper job, and the
  deliverable is the working request, not an opinion about whether it could work.
  Victoria's own WMIS at data.water.vic.gov.au/WMIS/cgi/webservice.exe is live and answered
  a malformed request with a well-formed JSON error. Work out the call. The Kisters
  "get_site_list" / "get_ts_traces" shape is documented on other KiWIS installs.

FIRE — the one signal that gates a listing, blocked on a licence, not on code.
  Do NOT build against the empty endpoint. Do THREE things instead:
    - find EMV's developer terms for data.emergency.vic.gov.au and quote them
    - find who at EMV manages third-party access, and draft the one-paragraph email —
      a free community site for one shire, asking whether the district RSS may be used
      and what getFDRTFBJSON returns in season
    - check whether FFMVic (Forest Fire Management Victoria) publishes planned burns
      SEPARATELY from the VicEmergency incident feed — a planned-burns SCHEDULE, ahead of
      time, would be worth more than the live one
  And confirm the district split from a first-party CFA page: Central holds Surf Coast,
  Greater Geelong, Golden Plains, Queenscliffe; South West holds Colac Otway. The feeds
  said so; find the page that says so.

TWO SOURCES THAT WANT A FREE KEY — register nothing yourself; find out exactly what
registering gets:
  EPA Victoria     gateway.api.epa.vic.gov.au answers 401 "missing subscription key".
                   What is on the other side — air monitoring sites near Geelong, and the
                   summer Beach Report water-quality forecasts? Which beaches? What terms?
  eBird            api.ebird.org 403s without a key. The waders at Swan Bay and Lake
                   Connewarre are RAMSAR-listed and arrive from Siberia in spring. What
                   does a recent-observations call return for the region, at what
                   cadence, under what terms? Test the question against the Western
                   Treatment Plant (next section) — it is one of the most-recorded eBird
                   hotspots in the country, so if eBird is worth a key anywhere here, it
                   is there.

═══ PHASE 2 — LOOKED FOR, NOT FOUND, OR NOT LOOKED FOR ═══

These have no probe on file. Some will be quick refusals — that is a finding.

THE WESTERN TREATMENT PLANT, WERRIBEE — Scott's addition, and the one first-party site
in this whole pass that is genuinely among the best of its kind in the country. Melbourne
Water's sewage treatment lagoons at Werribee are RAMSAR-listed and carry something near
300 recorded species; birders travel from overseas for it. Werribee is already inside the
region by Scott's own ruling on the VGB pass ("close enough — still only an hour away").
Establish, first-party and quoted:
  - access. It is not a park you walk into. Melbourne Water issues a birdwatching access
    permit and a physical key to the gates. Find the page, the process, the cost, the
    conditions, and whether it is currently open — that page IS the listing's `notes`.
  - the season. Which months, which species, and who says so — BirdLife, Melbourne Water,
    or the eBird hotspot's own bar chart, which is a published seasonal record and the
    honest way to say "waders peak here in summer" without inventing it.
  - what a machine can read. The eBird hotspot page, the eBird API recent-observations
    call for the hotspot id, and whether any of it survives the eight checks. This is the
    site that decides whether eBird earns a key.
  - what is already in the database. `python3 scripts/have.py water` and
    `python3 scripts/have.py nature`, and grep the activities for Werribee — the VGB
    import brought eight Werribee products in, and this may already be one of them,
    filed under something else.
It is a `spot` (nobody owns the birds; Melbourne Water owns the gate), it wants a `places`
row, and it will not be pinned by a street address — ask Nominatim for the feature by name.

BEACH-NESTING BIRDS — the Hooded Plover nesting season is the fact that puts dogs on leads
from August to March, and it is the one iNat gets exactly backwards. BirdLife Australia's
Beach-nesting Birds program publishes it. Find the first-party page, the dates, and
whether any per-beach nest data is published (they map active nests some seasons).
BirdLife's robots.txt allows everything relevant with a 10-second crawl delay.

PARKS VICTORIA — Great Otway National Park track and campground closures. Lake Elizabeth's
car park was closed Jan–Mar 2026 and the database found out from a listing's own notes.
Is there a feed, an alerts page, an API? Parks Vic has a "changed conditions" system.

ROAD CLOSURES — the Great Ocean Road closes for landslips, and the Otways closes for fire.
VicTraffic / VicRoads publishes closures. Machine-readable? Licence?

PATROLLED BEACHES — the single most useful fact about a beach for a family lives in prose
in `notes` where nothing can filter it. Surf Life Saving publishes patrol seasons and
hours per club. BeachSafe is a JS app whose API needs a browser (already probed). Is there
a per-club patrol calendar, or an LSV page, that a fetch can read?

KING TIDES — the tide model is in; the highest tides of the year are a calendar. Witness
King Tides (Victoria) publishes dates. Fixed calendar or feed?

MOONRISE AND MOONSET — the function computes phase and nothing else. Open-Meteo's forecast
endpoint does not carry them (checked). Either an algorithm — Meeus, or a small library
with a clear licence — or a source. Validate it against a published moonrise time for
Melbourne on a known date.

ISS PASSES — NASA Spot the Station, Heavens-Above. A pass is a dated event with no
organiser, which is exactly the shape this whole exploration is about. Feed or calendar?

METEOR SHOWERS — the function carries a hand-written table of nine. Does the International
Meteor Organization publish it machine-readable (they have a calendar page; is there a
CSV or JSON behind it)? Northern-only showers are already excluded — keep that.

POLLEN — Open-Meteo is null here. Deakin University runs the Melbourne Pollen count and
publishes Geelong. Page, feed, or API? Licence? Grass pollen Oct–Dec is the season.

FROST, FOG, SEA MIST — Open-Meteo forecast has fields for some of these. Which, and are
they any good for a coastal site? A frost forecast for Deans Marsh is a real thing to say.

OSM TAGS ON THE PINNED ROWS — not a feed, a one-off read. The database has a coordinate
for 980 rows and OpenStreetMap carries `wheelchair`, `opening_hours`, `surface`, `toilets`
on many of the same features. That is the accessibility gap two research passes reported
independently. How many of the site's pins resolve to an OSM feature carrying those tags?
Sample fifty. ODbL — quote the attribution requirement.

═══ PHASE 3 — THE GENUINELY NEW ═══

Things nobody has named yet. Spend a third of the pass here and no more. For each,
the same eight checks — or a one-line refusal with the reason.

Think in terms of what changes what a person would DO on this coast in a given week, and
ask where that fact is published by whoever measures it:
  - the sea: water clarity/visibility for snorkelling, rip forecasts, bluebottle or
    jellyfish warnings (probably none here — say so), salmon and whiting runs (VFA is
    Cloudflared; is there a fishing-club calendar?)
  - the land: fungi foray calendars from the Fungimap network, first-flowering records
    from ClimateWatch (Earthwatch) — a phenology database, which is the thing iNat is
    being used as a proxy for
  - the sky: satellite passes, planets at opposition, eclipses (a fixed calendar), the
    Milky Way core season as a date range for this latitude
  - fauna with a PUBLISHED season: shearwater arrival (Parks Vic or BirdLife),
    penguin colonies with visitor programs, seal haul-outs, echidna (already measured
    and works — 22x swing), glow-worms (Melba Gully — is there a first-party page)
  - the air: bushfire smoke FORECAST rather than reading (BoM/CSIRO AQFx?), UV alerts
    from ARPANSA (they publish UV by city, with a licence — check it)

Anything that turns out to be Melbourne-only, Bay-only, or national-with-no-local-cut is
a refusal. Record it in one line and move on.

═══ WHAT NOT TO DO ═══

- Do not write listings. Not one. The five-kinds question comes first and it is not yet
  answered for most of these.
- Do not read a host whose robots.txt names ClaudeBot as disallowed. Say "Action only".
- Do not register for anything. Report what registering would get.
- Do not claim a season from thin records. The whale count is 22 a year; a curve from
  that is decoration. Five records is not a feed. State the count and let it speak.
- Do not describe an endpoint you did not fetch. "Probably returns JSON" is not a finding.
- Do not paraphrase a licence. Quote it.
- Do not invent a beach bearing, a coordinate, or a date. The 28 bearings that exist were
  measured from OSM coastline and one of them corrected a figure asserted from memory by
  64 degrees.
- Do not build a parser against an empty response. Ever.

═══ WHAT AN HONEST RESULT LOOKS LIKE ═══

Most of Phase 3 will be refusals, and a page of clean one-line refusals is worth more than
three speculative sources. The first pass found that of 28 signals, roughly a third were
live feeds, a third were calendars a person writes, and a third were unavailable or wrong
to carry. Expect the same shape. A pass that comes back with twenty new live feeds has not
done check 1.

The Western Treatment Plant is the exception to expect a strong result from: it is a real
place, a real first-party access page exists, and eBird has years of records on it. If that
one comes back thin, the method has failed, not the site.

There is no target count. Finish Phase 1. Do Phase 2. Spend what is left on Phase 3.

═══ HAND BACK ═══

Two files, and the second is the more valuable one.

1. prompts/log/nature-sources.json — one object per source, this shape, nothing missing:

   {
     "name":        "BOM Water Data Online",
     "org":         "Bureau of Meteorology",
     "answers":     "river level and streamflow, per gauge, hourly",
     "where":       "named gauges — list them",
     "endpoint":    "the exact URL that produced a real value",
     "request":     "the exact curl or query, copy-pasteable",
     "sample":      "the first 200 bytes of a real response",
     "status":      200,
     "bytes":       5116,
     "ms":          840,
     "robots":      {"action": "allowed", "claude": "allowed", "content_signal": null},
     "cors":        "none",
     "licence":     "QUOTED, from the page, with its URL",
     "validated":   "what you checked it against, and the result — or 'unvalidated'",
     "kind":        "live | arithmetic | measured | calendar | not-carried",
     "cadence":     "how often it changes, and therefore how often to read it",
     "verdict":     "one sentence: build it / needs a key / needs a licence answer /
                     not available / not worth carrying, and why",
     "probed":      "2026-09-04"
   }

   Every source you touched goes in, including every refusal. A refusal has status, bytes,
   robots and licence filled in and a verdict that says why. A source with an empty body
   says "empty body" in sample and does not guess.

2. prompts/log/nature-sources.md — the worklog, and it must carry:
   - the Phase 1 outcomes: the working river-gauge request, the WMIS call format, the
     EMV terms and the drafted email, the FFMVic finding, the EPA and eBird "what a key
     gets you" answers
   - THE REFUSAL LIST — every source looked at and not recommended, one line each, with
     the reason. This is the part nothing else records and the part that stops the next
     pass spending the same hour.
   - every host that refused ClaudeBot, so the Action can be pointed at it
   - every licence sentence that would need Scott to make a decision
   - every value you could not validate, and what would validate it
   - a short section headed "the five kinds" that sorts everything you found into them,
     because that sort is what turns the inventory into a build order
```
