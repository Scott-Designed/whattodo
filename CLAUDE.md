# WhatToDo Jan Juc — working notes

A community listings site for Jan Juc and the Surf Coast, Victoria. Live at
**https://whattodo-nu.vercel.app** (Vercel project `whattodo`).

## Shape of it

```
public/index.html     the entire site — one file, no build step, no framework
api/enrich.mjs        Vercel function: Claude drafts missing fields, user approves
                      Takes a name OR a url. Events lead with the url.
supabase/             schema, seed data, setup SQL
scripts/              configure.py (keys into the page), sync.py (seed/export/moderate),
                      eventlib.py (shared plumbing for both scrapers),
                      scrape_events.py (the Surf Coast Events feed),
                      scrape_venues.py (each venue's own ticketing page)
.github/workflows/events.yml  runs that feed Mon + Thu
tools/event-inbox.html  published Artifact — capture links and poster photos on the go
```

Deploy is a push to `main` — GitHub `Scott-Designed/whattodo` is connected to the
Vercel project, which builds every push. There is no build step; Vercel just
serves `public/` and the function in `api/`. `npx vercel --prod` still works if
you need to force a deploy without a commit.

## How this project is worked on

Solo. Commit straight to `main` and push — no pull requests, no asking which
branch. `main` auto-deploys, so the safety net is `git revert <sha> && git push`
and a six-second redeploy, not review. Use a branch only when a change could
plausibly break the live site; note that `ANTHROPIC_API_KEY` is Production-only,
so a preview build cannot exercise Autofill.

One task per session. CLAUDE.md is the handover — when something is learned or
decided, write it here, so the next session starts cold and still knows it.

## The database is the source of truth

Supabase project ref `xpnsrtylcqjcoqitskwy`. Two tables — `activities` (evergreen
places) and `events` (dated things) — plus a `listings` view that unions them into
one shape for the page. 150 + 31 at seed.

The spreadsheet `JanJuc_WhatToDo_Database.xlsx` seeded this and is now an archive.
**Do not edit it and do not sync from it.** Two live copies is how the same festival
ended up in both sheets with two different dates, one of them wrong.

## Conventions that are enforced, not just documented

- **26 types**, foreign-keyed to the `types` table. An unknown type is rejected by
  the database, not just by the form. `null` is allowed and means "not sorted yet".
  Adding one means four places, not one: a row in `types` (with its `band`),
  `THEME_OF` in the page or it shows under no theme filter, `TYPES_PLACE`/`TYPES_EVENT`
  in `api/enrich.mjs`, and the seed insert in `supabase/schema.sql`. `shop` was added
  23 Aug 2026 — a retail place you buy from, as distinct from `market`, which is an
  event and also carries the What's on theme.
- The **At home** theme is hidden from the unfiltered list. Those entries are all
  `km = 0`, so under the default Closest first sort six of them led the page ahead
  of anywhere you would leave the house for. Picking the At home theme or typing a
  search still finds them, and the tally says how many are held back. See
  `atHomeHidden()`.
- **14 condition tags**, checked by `conditions_valid()`. Thirteen are gates;
  `good-in-rain` is a boost — it never hides anything, it promotes on a wet day.
- `dry-trails` = no rain for 48h (MTB, unsealed tracks). `dry-ground` = not raining
  right now (skateparks, markets, picnics). These are deliberately separate.
- Community additions land `verified = false`. RLS refuses any insert that sets
  `verified = true` or `added_by = 'Research'` — a submission cannot dress itself up
  as researched data.

## Venues

`supabase/VENUES_RUN_THIS.sql` creates a `venues` table and seeds 38 of them from
Scott's music venue spreadsheet, then adds `venue_id` to both `events` and
`activities` and rebuilds `listings` so an event inherits its venue's coordinates.
**Run it in the Supabase SQL editor** — PostgREST cannot create tables, so this
cannot be applied from a script.

Until it is run, `events.venue` stays free text and events cannot be plotted.
After it is run, an event with a `venue_id` carries lat/lng and a map becomes
possible; `venue` stays for one-offs and "various venues".

`venues.lat`/`lng` are seeded null on purpose — coordinates need a real geocoder,
never an estimate. OpenStreetMap's Nominatim is reachable from this environment and
is a legitimate source (`https://nominatim.openstreetmap.org/search?format=json`);
its policy is max 1 request/second and a real User-Agent. Geocoding is a separate
pass, not something to eyeball.

78 venues now: 38 from the spreadsheet plus 40 created from events' free-text
`venue` strings. 72 are pinned, 68 of 88 events are linked, and 66 events are
plottable (was 5). The mapping from venue string to canonical venue is curated by
hand in the commit history, not fuzzy-matched — fuzzy matching wanted to file the
Bells Beach surf comp at Bells Beach Brewing.

20 events stay unlinked on purpose: "Various venues – Surf Coast", "Rotates —
check website", "Surf Coast Shire", bare "Torquay". They name no single place you
can stand at, so inventing a pin for them would be the placeholder problem again.

No two venues share a coordinate. Four Winchelsea ones briefly did — OpenStreetMap
has the town but not its halls — and were resolved by finding the real addresses
instead of accepting the town centre: the Globe Theatre is 17 Willis St (its
heritage listing says so), the Shire Hall is on Main St, Lions Park is on Barwon
Terrace. Cheaper than arguing about how a map should draw an approximation.

Two venues stay unpinned: `Eureka Hotel Geelong` and `The Whiskery` (Drysdale).
Neither resolves in OpenStreetMap and neither has a usable address on file.

34 of the 38 spreadsheet venues were geocoded (24 Aug 2026) — 11 to the building, 14 to the
street, 9 by name and suburb where the sheet had no address; every row's
`source_note` says which. Four did not resolve in OpenStreetMap under any query
tried and are deliberately left null: Eureka Hotel Geelong, Princess Park
Playground, The Whiskery, Torquay Common.

Five events are linked so far — the licensed venues. The other 38 happen at parks,
beaches, reserves, halls and cenotaphs, which the music spreadsheet never covered.
Those need venue rows of their own before the map can show everything. The spreadsheet also holds a `Barwon Heads Hotel` gig history
and per-venue Facebook/Instagram/Oztix feed URLs, which is the raw material for
an automated what's-on check later.

## The name says what, the Where column says where

An event called "Open Mic Night – Torquay Hotel" in a row whose next column
reads *Torquay Hotel* prints the venue twice, and on a phone the duplicate is
what pushes the actual event off the edge. Names carry the thing; Where carries
the place.

Two halves make that work:

- **`listings` has a `venue` column of its own.** It used to fold the two facts
  into one — `coalesce(e.location, e.venue) as location` — so the page could
  print the suburb or the venue but never both, and it printed the suburb.
  `supabase/VENUE_IN_LISTINGS.sql` splits them. For a linked event the suburb
  comes from the venue row, not the event's own free text: `venues` is curated
  and geocoded, while `events.location` came off the feed and has drifted
  (event 20 said Torquay for a gig at The Sound Doctor, which is in Anglesea).
  Activities get the column too — a union needs the same shape both sides — but
  it stays null unless the activity is one of the licensed venues, because an
  activity is usually its own venue and printing it twice helps nobody.
- **`scripts/name_rules.py` takes the place back out of the names.** Dry run by
  default, `--write` to apply, `--check` for a non-zero exit if anything drifts.

The gate that keeps the rules from doing damage: **a name may only shed a place
when the event has a `venue_id`.** A linked venue is a real row with an address,
so Where definitely has something to show. An event carrying only free text
("Various venues – Surf Coast", "Rotates — check website", a bare suburb) keeps
every word of its name — which is why *Repair Café Surf Coast* and *ANGAIR
Wildflower & Art Weekend* were left alone. Link a venue and the row becomes
eligible, which is the right incentive.

What the rules do, in order: drop a venue after `–` or `at` at the end, drop one
before `–` or `presents` at the front, drop one mid-name after `at`, then drop a
bare leading **suburb** — suburb only, or "Great Ocean Road Running Festival"
loses its own name to a venue string that mentions the road. Two adjustments
follow: a chunk that mentions a place without being one is a series, and keeps
its name in brackets (*Night Markets (Geelong After Dark)*); and a one-word
remainder is too bare to stand in a list, so it gains its type (*Ceramics* →
*Ceramics Workshop*).

That bracket rule is deliberately narrow — it wants two non-place words. A place
plus one word is an organisation named after its town, not a banner: the Torquay
RSL *runs* the dawn service, it is not what the dawn service is called.

**A dated event happens somewhere.** If a row has a date and a time then it has
a place, and the place belongs in Where. The dry run prints every dated event
with no `venue_id` under the renames — 18 of them — because that is the same
list as the names that still have to carry a suburb. Several only need a venue
row built from the text they already hold (`Baines Crescent outlets`, `Anglesea
Community Precinct`, `Torquay Common`); the rest genuinely have no single place.
*Repair Café Surf Coast* was in that list on a false premise — the database said
"Rotates — check website" but repaircafesurfcoast.tech says "Where: Aireys Inlet
Community Hall", one hall, every session. Given a venue, the region came out of
the name.

`KEEP` is for names where the place **is** the name — Lorne Pier to Pub Swim,
Portarlington Mussel Festival, Rip Curl Pro Bells Beach. `OVERRIDE` is for the
few where the right answer is a rewrite rather than a subtraction (Torquay
Library – School Holiday Program → *Torquay Library Activities*, Dawn Service –
Torquay RSL → *Anzac Day Dawn Service*, Repair Café Surf Coast → *Repair Café*). Both are one
line each with the reason. **The rules propose; a person accepts** — no pattern
matcher knows that Falls Festival is not named after Lorne. Read the dry run
before every `--write`, and add the exception rather than loosening a rule.

32 of the 87 events were renamed 24 Aug 2026. Each one's `source_note` now
carries `Published as "<old title>"`, so nothing the organiser wrote is lost.

Renaming before the view is split would strip the venue out of the name while
Where still showed the suburb alone, so `--write` refuses until `listings` has
the column. Both were done 24 Aug 2026, in that order — and the order matters
in the other direction too: the renames were applied a few minutes before the
page shipped, so the live site briefly showed bare names beside bare suburbs.
Deploy the page first next time.

## Two meters — know which one you are spending

Researching a listing inside Claude Code costs nothing beyond the Claude
subscription. The site's **Autofill** button costs org API credits per press,
wherever it runs — production, a preview, or `vercel dev` on the laptop. The bill
follows `ANTHROPIC_API_KEY`, not the machine, so there is no free local path.

While this site is still for one person, research here and write with `sync.py add`.
Capture on the go with the **Event Inbox** artifact
(https://claude.ai/code/artifact/93362d84-79a0-43b9-89e5-65eff75d74e2, source in
`tools/event-inbox.html`): paste links or photograph posters. **Read it directly** —
WebFetch that URL and the queue comes back in a `<script id="queue">` JSON island;
photos are base64 data URIs you can decode to a file and look at. No export step.
After filing, clear the queue by republishing `tools/event-inbox.html` (its committed
copy always has an empty queue) with the artifact URL. The Export button is only a
fallback for getting the data out of Claude entirely. It cannot enrich or write to Supabase
itself — a published artifact has no inference capability and its CSP blocks every
external request. It is a notebook, not an uploader.
Autofill exists for the community members who cannot ask Claude directly — keep it
working, but do not use it as the everyday route.

## The events feed runs itself

`surfcoastevents.com.au` is WordPress with The Events Calendar, so it publishes
a JSON API and **nothing here parses HTML**:

    https://www.surfcoastevents.com.au/wp-json/tribe/events/v1/events

`scripts/scrape_events.py` reads it, and `.github/workflows/events.yml` runs that
**Monday and Thursday, 7am Melbourne**. Free on both meters — GitHub Actions
minutes, and no model call anywhere in the path, so it keeps working while
Autofill is dead. robots.txt allows it (`Disallow:` is empty).

    python3 scripts/scrape_events.py            # look and report, writes nothing
    python3 scripts/scrape_events.py --write    # insert the new ones, unverified
    python3 scripts/scrape_events.py --json f   # rows for `sync.py add` instead

Three things about that source, each of which the script exists to handle:

- **It explodes a recurring series into one listing per occurrence.** Aireys Inlet
  Market is sixteen listings. 98 listings are 46 real things. Instances share a
  `slug`, so that is the grouping key — not the title, because the source
  sometimes carries one market under two slugs. Spacing is only called
  `weekly`/`monthly` when the occurrences actually keep to it; irregular ones say
  so in `source_note` and wait for a human.
- **It is edited constantly** — about 30 of ~100 listings changed in the week this
  was built. So dates drift after import. Drift on an **unverified** row is
  updated silently; drift on a row you **verified** is reported and left alone,
  every run, until you deal with it. Your verification is not overwritten by a bot.
- **It is a curated calendar, not the organiser's own page.** Everything lands
  `date_confidence = 'medium'`, which is why the site shows it as "est.". Only a
  human who has read a first-party page may raise it to `high`.

Nothing is ever inserted `verified`. New rows appear in `sync.py pending` like any
community addition. `scripts/events_seen.json` records every series ever offered,
so something you rejected does not come back on Thursday — delete a line to be
offered it again.

**Why twice a week.** The shortest notice anything on that site has ever been
published with is **9 days** (measured across every listing; only two were under a
fortnight). Twice a week means the worst case is hearing about an event five days
out, and a skipped run still leaves days in hand. Daily is seven times the runs
for margin nobody needs. Weekly is the floor, not a comfort.

The feed does not set `km`. Distances in this database are already known to be
shaky and inventing more is exactly how it got burned — fill it in on review.

## The venue feed — one worker, driven by the database

`scrape_venues.py` reads gigs from the venues themselves. **The registry is the
`venues` table, not the code**: any row with an `events_url` gets read, and a row
with only a `website` gets its usual gig paths tried as a convenience (the run
says which one worked so you can pin it down). Adding a venue is filling in a
cell — never editing this script. A source that would need a per-venue special
case is a source we do not take.

    python3 scripts/scrape_venues.py                    # look and report
    python3 scripts/scrape_venues.py --write            # insert, unverified
    python3 scripts/scrape_venues.py --only oztix       # one platform
    python3 scripts/scrape_venues.py --skip humanitix   # leave a platform alone

Ladder, best first: schema.org `Event` on the page → ticketing links followed and
read (schema.org, or Oztix's patterned `<title>`) → report and stop. Never guess.

**Confidence.** A ticket page is the organiser's own, so it is first-party and
sufficient on its own. A date read from a machine-readable `startDate` lands
`high`; a date picked out of a title by regex lands `medium`, because a regex can
misfire and a wrong date wearing a confident badge is what this project has
already paid for. Nothing is inserted `verified` either way.

**It sets `venue_id`**, because it knows which venue it is reading. The
surfcoastevents feed cannot and does not.

**Cross-source duplicates** are caught on venue + date as well as name — the same
gig reaches us as "Telenova" from Humanitix and "Telenova at The Sound Doctor"
from surfcoastevents, and a name check alone would miss it.

What the audit of all 78 venues found (24 Aug 2026): **zero** publish an events
feed. 12 are automatable via a ticketing platform, 13 have a site with nothing
machine-readable, 4 have a dead URL, and **49 have no website recorded at all** —
that last number, not the parsers, is what caps coverage at 15%.

Platforms: Oztix 6 venues (no JSON-LD; its `<title>` is template-generated and
carries name, venue, suburb, date), Humanitix 2 (clean schema.org), TryBooking 2,
Eventbrite 2 (has a free API — use that, don't scrape it).

**Who is asking matters.** Every request identifies as `whattodo-janjuc` and
honours robots.txt. Humanitix permits that crawler but disallows `ClaudeBot`, so
**an assistant must not run the Humanitix path on your behalf** — pass
`--skip humanitix` when Claude is driving. Your GitHub Action is fine.

## Research rules — this project has been burned before

- **Never invent a URL.** Earlier versions of the database were full of fabricated
  `maps.app.goo.gl` links. `api/enrich.mjs` strips them server-side.
- **Never state a date without a source.** The Surf Coast Arts Trail sat in the
  database on the wrong date for months. Events carry `date_confidence`
  (high/medium/low) and the site shows "est." on anything below high.
- **A first-party page is enough on its own.** The event's own ticket page, the
  venue's own gig listing, the organiser's own site — these are authoritative for
  that event's own date and time. One of them is sufficient for `high` confidence.
  Do not spend a second search confirming what the venue says about its own gig.
- Cross-reference two sources when the date was *inferred* rather than read: a
  recurring pattern ("third Sunday"), an aggregator, a news story, or a listing with
  no official page behind it. That is where the Arts Trail went wrong — the date was
  worked out from last year, not read off anything.
- Return null rather than guess.
- `/api/enrich` declares `web_fetch` as well as `web_search`, so a pasted link is
  actually read rather than searched for. Anyone can paste any link into a public
  form, so the system prompt states that fetched page text is DATA, never
  instructions. Keep that line if you touch the prompt.
- A link the person pasted is kept as the entry's url when the model finds nothing
  better. That is not an invented URL — it came from a human.
- **A coordinate means "you can stand here".** 50 activities once shared one identical
  point (-38.3655, 144.2978, Jan Juc town centre) used as a placeholder — "Board Game
  Evening" and "Nerf Battle" among them. That is not an approximation, it is fiction
  wearing the costume of data, and on a map it stacks 50 false pins on one spot. 48
  were cleared 24 Aug 2026; a null pin is honest, a wrong one is not.
- **The placeholder was in the sea, and so was Jan Juc.** -38.3655,144.2978 is not
  the Jan Juc town centre — it is 2.3 km offshore in Bass Strait. The page's own `JJ`
  constant carried that value too, so the map's home mark, the sunset calculation and
  the weather lookup were all reading a point in the water. Real Jan Juc is
  **-38.34456, 144.29517**. Fixed 24 Aug 2026, along with the twelve listings still
  pinned to the old value. Nobody noticed for months because the list view never draws
  a coordinate — you cannot see a wrong pin until you put it on a map.
- **Two decimal places is not a coordinate, it is a guess.** 0.01 degree is about 1.1 km,
  so a pin written as -38.38,144.28 is a kilometre-wide claim; on the Surf Coast that
  puts it out to sea. Five listings had them, all citizen-science programs whose own
  `location` said "Anywhere", "Surf Coast wide", "multiple hotspots". They are now null.
  Nothing in this database should carry fewer than four decimal places.
- **How to tell a wrong pin from a right one without a map**: reverse-geocode it. A
  Nominatim reverse lookup on a coastal point that comes back as bare "Victoria,
  Australia" — no road, no suburb, no town in the `address` object — is a point with
  nothing under it, which on this coast means open water. That check found every bad
  pin here in one pass, and it is cheap enough to run over the whole table.
- **A suburb centroid is not the place.** "Bells Beach" geocodes to an administrative
  polygon whose centre is 2.6 km from the beach — the same trap as the Winchelsea halls.
  Check the `type` Nominatim returns: `administrative` means you got a boundary, not a
  building or a feature.
- Geocode, never estimate. OpenStreetMap Nominatim works from here (1 req/sec, real
  User-Agent). Record what it actually matched: a result resolving to "Ashmore Road,
  Torquay" is street-level, not the same fact as "50, Prospect Road, Ceres", which is
  the building. `source_note` carries that distinction for every geocoded row.
- Which coordinate wins: an activity uses **its own** `lat`/`lng`. `venue_id` is only
  for an activity that *is* one of the licensed venues in `venues`. The `listings` view
  coalesces own-first, venue-second.
- Distances are approximate DRIVING distances from Jan Juc, not straight-line —
  the Great Ocean Road makes those differ by 40%.
- `km = 0` means *here* — Jan Juc itself, or your own house. `km = null` means the
  entry has no location to measure ("Anywhere outdoors", "Any beach"): the sort
  treats null as furthest, so unlocated ideas fall to the bottom of Closest first
  instead of burying the real places. Never write 0 to mean "don't know".

## The map

The page has two views of one filtered list — `List` and `Map`, switched by the
segmented control under Sort. Both read the same `ok()` filter, so whatever the
dropdowns say, the map shows exactly that and nothing else.

MapLibre GL JS, pinned to **5.24.0** off jsDelivr. 6.x is ESM-only, split across a
shared chunk and a module worker, which wants a bundler; this file has no build
step, so the UMD build that puts `maplibregl` on `window` is the one that fits.
The library is fetched **only when someone opens the map** — if jsDelivr is
unreachable the map says so and the list is untouched. Nothing about the list may
ever depend on a third party to render this database.

Basemap is CARTO's **Positron** (light) / **Dark Matter** (dark), vector, no API
key, swapped from the page's own `prefers-color-scheme`. Attribution rides along
in their TileJSON and fills the control in by itself — adding a `customAttribution`
on top prints it twice.

Things that cost time here:

- MapLibre's stylesheet and this page's own use the same selectors at the same
  weight, so whichever loads later wins. Appended to `<head>` it repaints the
  popups white over a dark page. It is inserted **first** in the head instead.
- Never set `position` on a marker element. MapLibre positions its markers
  absolutely and this page's stylesheet now outranks it, so `.pin{position:relative}`
  silently drops every marker out of the map and stacks them down the page in
  document order.
- Pins are drawn straight after the map is constructed, not on `load`. They are
  HTML over the canvas, not part of the style, so they do not need the basemap —
  and an animated `fitBounds` started before the tiles arrive gets dropped and
  leaves the map on its opening view. The first fit jumps; later ones ease.

Several listings genuinely share one coordinate — five sit on Bells Beach. Those
share a pin, the pin carries the count, and the popup lists all of them. They are
**not** nudged apart: five coordinates that are not true is how this database got
burned before.

Under the map is a count of what is *not* on it — `196 of 359 on the map · 163
have no coordinates yet`. A map that quietly shows half the database is a map
that lies, so the gap is printed rather than hidden.

**Every pin has been checked against the water.** All 196 were probed at zoom 16
against the basemap's own `water` layer (`queryRenderedFeatures` on the marker's
projected point); none is in the sea. Re-run that check after any geocoding pass —
it is the only test that catches a pin a few hundred metres offshore, which is
close enough that reverse geocoding still snaps it to a coastal road and calls it
land.

## Known outstanding

- An activity's single `url` is whatever it is — a map pin for some, the venue's own
  site for others. The row labels it by inspection (`isMapLink`), so don't assume the
  slot means "map". 87 of 203 activities carry a website there. `Directions` is built
  separately from `lat`/`lng`. 128 of 272 activities are pinned; the rest are the
  At home entries and the roving ones, which have nowhere to be
- 42 entries use Google Maps *search* URLs rather than pinned coordinates
- Four events sit on estimated dates: Bells Beach Surf Film Festival, Deans Marsh
  Festival, Geelong Pride Film Festival, One Planet Festival
- Ideas Pipeline (177 rows, in the old spreadsheet) is not in the database
- Tide, moon and fire-ban conditions have no data source wired up. Only the
  weather-derived tags actually evaluate: dry-ground, dry-trails, warm, low-wind,
  clear-sky, good-in-rain
- The feed's backfill is done: 44 imported 24 Aug 2026, ids 45–88, all
  unverified and all `date_confidence = 'medium'`. Four collided by name with
  events already there and were skipped. None has a `km` yet.
- Imported events carry no `km` and no `cost` (the source publishes no price at
  all — 0 of 101 listings had one)
- **`sync.py reject <id>` does not say which table.** It matched activity 83
  when the event 83 was meant, and only refused because that activity happened
  to be verified — otherwise it would have deleted `Lake Elizabeth Campground`
  instead of a duplicate market. Ids are per-table and they collide. Make it
  take `e83`/`a83`, or the `key` the listings view already builds.
- `Lorne Falls Festival` (15) was deleted 24 Aug 2026. Its own site says the
  festival is on hiatus with no dates; the row had it running 28–31 Dec 2026 at
  the Lorne foreshore, which was never the site even when it ran. Kept for the
  record, since the reasoning is the useful part:
  fallsfestival.com's own front page says the team are "taking this New Years'
  season off to rest, recover and recalibrate"; the festival has not run since
  2022 and the Lorne site — a 68ha farm at Murroon — was sold in 2025. The row
  was `verified = true` on a date nobody had announced. A verified flag is not
  evidence; it only records that a person looked.
- `Lorne Schoolies Week` (23) was deleted 24 Aug 2026 at Scott's request. It was
  a warning to stay away rather than something to do.
- The two Torquay Farmers Market rows were merged 24 Aug 2026 (5 kept, 83
  deleted) — and both had it in the wrong place. myfarmersmarket.com.au and
  visitgreatoceanroad.org.au agree it is "the carpark of the Surf Coast Shire
  Offices ... every Saturday, morning from 8.30am to 1.00pm", not Fishermans
  Beach Reserve, and not finishing at 12:30. Place 79 was created and geocoded
  for it. The duplicate is what exposed the error: two rows disagreeing is a
  better bug report than one row being quietly wrong.
- Four event names still carry their recurrence — "– every Saturday", "– first
  Sunday of Month". The `recurrence` column says `weekly`/`monthly` but has
  nowhere to put the day, so the name is the only place *Saturday* is written
  down. Left alone until `time_text` carries it ("Saturdays, 8:30am–1pm").
- The moderation queue is empty. `Ashmore Arts` (169) and `The Fives` (168) are both
  verified; both had their distance cleared rather than guessed and still need real ones,
  as does `Bird Rock Farm` (171)
- Distances unverified; Waurn Ponds known wrong
- **Autofill is dead until the Anthropic account is topped up.** Every call returns
  400 "credit balance is too low". The page now says so in English rather than
  printing the JSON. Nothing else on the site depends on it.
- A stray Vercel env var called `Whattodo2` exists and nothing reads it

## Gotchas already paid for

- **DDL can be run from here after all.** PostgREST cannot create a table or
  redefine a view, which is why every schema file says "run it in the SQL
  editor" — but the Supabase **Management API** can:

      POST https://api.supabase.com/v1/projects/{ref}/database/query
      {"query": "..."}                      Authorization: Bearer sbp_…

  It needs a Personal Access Token from supabase.com/dashboard/account/tokens,
  which is **account-wide** — it can read and change every project on the
  account, not just this one. Scott issued one on 24 Aug 2026 to apply
  `VENUE_IN_LISTINGS.sql`. If `SUPABASE_ACCESS_TOKEN` is not in `.env`, it was
  revoked afterwards and the SQL editor is the route again. Send a real
  `User-Agent`; the default `Python-urllib` gets a Cloudflare 1010.
- Vercel functions: `.mjs`, or a `package.json` with `"type": "module"`. A bare
  `.js` using `export default` silently fails to deploy and the route 404s.
- Don't create Supabase tables in the Table Editor — run the SQL. A hand-made table
  has only `id` and `created_at` and the CSV importer then refuses everything.
- The site ships with a baked-in copy of the data so it renders instantly and still
  works if Supabase is down. The badge by the date says `live` / `offline copy` /
  `built-in copy`. Don't remove that fallback.
- A GitHub Actions step that pipes through `tee` reports **tee's** exit status,
  not the script's, so a crash shows a green tick. `set -o pipefail`, and `2>&1`
  or the traceback never reaches the job summary. The events job shipped with
  both bugs and its first real run failed invisibly.
- GitHub secrets are set from the terminal — `… | gh secret set NAME` — not by
  pasting into the web form. Pasting put the text of the shell command into the
  secret, and the failure surfaced three layers away as `unknown url type`.
- `RobotFileParser.read()` fetches robots.txt with Python's own user-agent, which
  plenty of firewalls answer with 403 — and the parser reads a 403 as "forbidden
  from the entire site". That silently skipped a venue whose robots.txt plainly
  allowed us. `eventlib.robots_ok` fetches robots.txt itself with our real UA and
  only treats a 401/403 **on robots.txt** as a refusal.
- Python buffers stdout when it is redirected to a file, so a long background run
  looks like it produced nothing until it exits. It has not hung.
- Sunset is computed in-page (no API) for the When filter. Verified against
  WillyWeather: 22 Aug 2026 gives sunrise 6:59, sunset 5:52pm.

## Next things worth doing

1. Build place rows for the four dated events whose free text already names a
   real place: `Baines Crescent outlets` (22), `Anglesea Community Hub` (30),
   `Anglesea Community Precinct` (53), `Torquay Common` (77). Each one then
   gets a pin and a tidier name. `name_rules.py` lists all 18 that have a date
   and a time but no venue.
2. Work through the 44 imported events — `sync.py pending`. Each needs a
   distance from Jan Juc and its date checked against the organiser's own page
   before `date_confidence` can go to high; until then the site shows "est.".
3. Verify community additions — `python3 scripts/sync.py pending`, then `verify <id>`
   to approve or `reject <id>` to delete. `reject` refuses verified rows and asks
   before deleting; `--yes` skips the prompt.
   `add file.json` (or `-` for stdin) writes a researched entry, one object or a
   list. It checks types, conditions, enums, date shape and URLs against the live
   vocabularies before writing, so a bad field in a batch names itself instead of
   failing an opaque insert. It refuses a name that already exists — pass `--force`
   only when it genuinely is a different thing. `--verified` requires a
   `source_note`; `--dry-run` checks without writing. An event's link is
   `info_url`/`ticket_url`, never `url`.
4. Pin the 42 entries whose `url` is a Google Maps *search* rather than a
   coordinate — each one is a missing pin on the map
5. Promote the Ideas Pipeline into the database
6. A scheduled job that re-checks estimated event dates as real ones get announced
