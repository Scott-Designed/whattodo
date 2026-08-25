# WhatToDo Jan Juc — working notes

A community listings site for Jan Juc and the Surf Coast, Victoria. Live at
**https://whattodo-nu.vercel.app** (Vercel project `whattodo`).

**The site is called `Notice`** (renamed 24 Aug 2026; it was "What to do"), and
the listing area is the **Notice Board**, which is where its count lives —
"Notice Board · 395 things pinned". The repo, the Vercel project, the URL and
this file keep the old name: renaming those buys nothing and breaks the deploy
hook. So `whattodo` is the project and `Notice` is the product.

## Shape of it

```
public/index.html     the entire site — one file, no build step, no framework
public/admin.html     back of house: the automations, every listing, and an editor
public/sunset.css     the Sunset face, so admin.html can wear it too
api/enrich.mjs        Vercel function: Claude drafts missing fields, user approves
                      Takes a name OR a url. Events lead with the url.
api/admin.mjs         Vercel function: the only write path from a browser.
                      Holds the service key; needs ADMIN_PASSWORD.
supabase/             schema, seed data, setup SQL
scripts/              configure.py (keys into the page), sync.py (seed/export/moderate),
                      eventlib.py (shared plumbing for both scrapers),
                      scrape_events.py (the Surf Coast Events feed),
                      scrape_venues.py (each venue's own ticketing page),
                      run_log.py (records what a scheduled run did → run_log.json)
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

`supabase/VENUES_RUN_THIS.sql` created the table (then `venues`, now `places`) and seeded 38 of them from
Scott's music venue spreadsheet, then added `venue_id` to both `events` and
`activities` (now `place_id`) and rebuilt `listings` so an event inherits its venue's coordinates.
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

## Aliases, and the duplicates the scraper makes

`places.aliases` (a `text[]`, added 25 Aug 2026) holds the other names a source
calls a place. `scrape_venues.py` builds its match registry from **name plus
every alias**, which is the only thing that makes a merge stick: the ticket
listing says "Blackman's Brewery, Torquay", the row is called "Blackmans
Brewery", `venue_key` normalises punctuation but not a trailing suburb, so
without the alias the scraper simply creates the duplicate again on Thursday.
**Merging two places means three steps, not one** — repoint the events, add the
loser's name to the winner's `aliases`, then delete the loser.

Three were merged 25 Aug 2026, all created by the venue scraper on 24 Aug from
ticket listings:

- 93 `Blackman's Brewery, Torquay` → 49 (event 120)
- 94 `Elephant & Castle Hotel Geelong` → 12 (event 121)
- 95 `Oneday Estate Winery & Function Centre` → 24 (events 122–124)

`Blackmans Brewery Geelong` (92, Grovedale) looks like a fourth and is not — it
is the second taproom, a genuinely different building, and it now has its own
pin.

**The duplicate caught a wrong address.** Row 24 `Oneday Estate` carried
2255 Portarlington Rd off the music spreadsheet; onedayestate.com.au says
45 Curlewis Rd, Curlewis VIC 3222. The row the scraper made was the correct one.
Two rows disagreeing is a better bug report than one row being quietly wrong —
the same way the Torquay Farmers Market error surfaced.

No two venues share a coordinate — **with one honest exception**. `The HOOP
Gallery` (98) and the `Australian National Surfing Museum` (46) are both at
77 Beach Rd, Torquay, because the gallery is the Torquay Multi-Arts Centre
inside that complex. That is two things in one building, which the map already
handles (five listings share the Bells Beach pin); it is not the placeholder
problem. Four Winchelsea ones briefly did — OpenStreetMap
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

  **As of 25 Aug 2026 every event in the database is verified**, so that first
  branch is now dead: the feed updates nothing and every drifting date is a line
  in the job summary waiting for a person.

  That used to be the end of the sentence, and it was the most likely way this
  database went wrong next — a job summary is a page on github.com nobody
  visits, so a date that moved at the source went stale here silently. **Fixed
  25 Aug 2026**: the run now writes `scripts/run_log.json` and commits it, and
  the back-of-house page reads it and puts every locked drift in a red box at
  the top, each one a link straight into that event's editor. See the Back of
  house section. The report reaching somewhere Scott looks is the whole point;
  if that page stops being opened, this hazard is back.
- **It is a curated calendar, not the organiser's own page.** Everything lands
  `date_confidence = 'medium'`. Only a human who has read a first-party page may
  raise it to `high`. **The page no longer prints that distinction** (25 Aug 2026)
  — see the date-confidence note below.

Nothing is ever inserted `verified`. New rows appear in `sync.py pending` like any
community addition. `scripts/events_seen.json` records every series ever offered,
so something you rejected does not come back on Thursday — delete a line to be
offered it again.

**Why twice a week.** The shortest notice anything on that site has ever been
published with is **9 days** (measured across every listing; only two were under a
fortnight). Twice a week means the worst case is hearing about an event five days
out, and a skipped run still leaves days in hand. Daily is seven times the runs
for margin nobody needs. Weekly is the floor, not a comfort.

The feed does not set `km`, and **that is now the standing decision, not a gap**
(25 Aug 2026): distance stays null on imported rows until there is a way to
compute driving distance automatically. Distances here are already shaky, and
hand-entering 101 of them is how a hundred more guesses get in. Do not fill `km`
during a review.

## The venue feed — one worker, driven by the database

`scrape_venues.py` reads gigs from the venues themselves. **The registry is the
`places` table, not the code**: any row with an `events_url` gets read, and a row
with only a `website` gets its usual gig paths tried as a convenience (the run
says which one worked so you can pin it down). Adding a venue is filling in a
cell — never editing this script. A source that would need a per-venue special
case is a source we do not take.

    python3 scripts/scrape_venues.py                    # look and report
    python3 scripts/scrape_venues.py --write            # insert, unverified
    python3 scripts/scrape_venues.py --only oztix       # one platform
    python3 scripts/scrape_venues.py --skip humanitix   # leave a platform alone

It reads **both** the venue's own listing and the ticket pages behind it, then
merges them on date. Neither is a superset: the listing is the only thing that
sees a gig nobody ticketed (Torquay Hotel sells its Grand Final afterparty on the
door), while the ticket page carries the blurb, the link and exact times. The
listing is the spine; ticket data fills it in.

**Follow the pagination.** These sites show nine gigs a page and draw the pager
in JavaScript, so a fetch — and even a headless browser scrolling to the bottom —
only ever sees the first nine. `/gigs/page/2/` is a real url and has the rest.
Torquay Hotel went from 8 gigs to 13 on that alone.

A listing row must never claim a ticket link it cannot prove is its own. Taking
the first ticket url on the page stamped one gig's ticket page onto all thirteen,
including the one with no tickets at all — exactly the fabricated-url failure this
project already paid for. `merge()` attaches a ticket link only where the date
matches.

**Confidence.** A ticket page and a venue's own gig listing are both first-party,
so both land `high` — but only because the listing parser uses the printed weekday
as a checksum: if "Saturday, Oct 17" is not actually a Saturday the row is thrown
away rather than guessed at. A date picked out of an Oztix `<title>` by regex, with
no such check, stays `medium`. Nothing is inserted `verified` either way.

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

## Back of house — /admin

`public/admin.html`, live at **https://whattodo-nu.vercel.app/admin**. One page,
no build step, same as the site. Four tabs: **Automations**, **Events**,
**Activities**, **Places**. Built 25 Aug 2026.

**It is a page on the site, not an Artifact, and that was forced.** A published
Claude Artifact's CSP blocks every external host — it cannot reach Supabase at
all, so it could never be live and an edit made in one could never be written
back. The runtime capabilities an Artifact *can* have (self-publishing,
downloads, calling the viewer's claude.ai connectors) do not include "fetch a
URL". Don't re-litigate this next session: if the answer has to be live data,
it has to be served from Vercel.

**Reads use the anon key, exactly like index.html.** Everything the page shows
is already public — the listings, the venues, the vocabularies. It reads the
raw `activities`, `events` and `places` tables rather than the `listings` view,
because the view flattens both halves into one shape and the editor needs the
real columns.

**Writes go through `api/admin.mjs` and nothing else.** Anon may select and
insert but never update or delete, and the service key must never be in the
page, so the function holds it and is the entire write surface. It needs
`ADMIN_PASSWORD` in the Vercel project — without it the endpoint refuses
everything with `no_password`, which is the correct failure: no password, no
writing. The password unlocks *writing only*; nothing on the page is hidden by
it, because none of it is secret.

The function re-checks every rule server-side — vocabularies, the URL rules, the
date shape, the four-decimal coordinate rule, verified-needs-a-source_note. The
same checks exist in the browser, and those are decoration: this is a public URL
and the page cannot be trusted to have run them.

Things that are load-bearing:

- **Only what changed is sent.** The editor diffs the form against the row it
  opened and patches the difference. That is what lets you fix a name on a row
  whose coordinate has two decimal places without being told to geocode first —
  the coordinate rule only fires if you touched the coordinate. Sending the
  whole row would make every pre-existing flaw block every unrelated edit.
- **A coordinate under four decimal places is refused, not warned about.** 0.01°
  is 1.1km, which on this coast is often open water. A deliberate round number
  written out (`-38.3400`) still passes; a guess usually will not.
- **Deleting a verified row takes two presses.** Same guard as `sync.py reject`.
- The flags are computed in the page, never stored, so fixing a row clears its
  flag the moment it saves. `at-home` rows are exempt from the pin and distance
  flags — `km = 0` means *here* and "Nerf Battle" has nowhere to be.
- **A Google Maps `?q=-38.37,144.28` link is a pin, not a search.** All 36 of
  those are coordinates and are fine; the 37 `/maps/search/Some+Name` ones are
  the standing item on the list. Flagging both put 73 rows on the worklist, half
  of them finished. `mapsSearch()` tells them apart.

### Where the events come from

The Automations tab lists **every source anything is ever read from** — the
calendar plus all 98 places — with what was tried and what came back. The
registry is the `places` table, so the list is built from place rows and not
from anything in the code; a row's status comes from the last run's own output.

`scrape_venues.py` already prints a sentence per venue ("Oztix (10 gigs from 10
of 10 links)", "site did not respond", "nothing machine-readable [homepage; no
gig page found]"), and `run_log.py` sorts those into states — reading, nothing
to read, site did not answer, robots.txt says no, skipped, needs a person. The
`[bracketed]` tail is the scraper telling you how to pin a source down ("found
at / — set events_url to lock it in") and is printed under the row.

**Ordering in `source_state()` is load-bearing**: `skipped` must be tested
before the platform names, or a skipped Humanitix line reads as a successful
Humanitix read.

The headline the view exists to show, as of 25 Aug 2026: **5 reading, 18 with a
site but nothing machine-readable, 5 dead, 1 refused by robots.txt, 1 needing a
person (Eventbrite, which has a free API), and 63 with no website on file at
all.** That last number is what caps coverage — not the parsers.

Six Humanitix sources show as skipped because the run that filled the log was
driven from here, and Humanitix disallows `ClaudeBot`. The scheduled Action
reads them normally; the page says so under the table.

### How the runs went

Run history is GitHub's public API — `api.github.com/repos/Scott-Designed/whattodo/actions/runs`
— read straight from the browser with no token, because the repo is public and
GitHub sends `Access-Control-Allow-Origin: *`. 60 requests an hour per address,
which one person opening a page will never approach.

**What the scrapers actually printed is not in any public API.** Job summaries
are a UI feature and job logs need `actions:read`. So the run writes its own
record: `scripts/run_log.py` parses `run.txt` and `venues.txt` into
`scripts/run_log.json`, the workflow commits it with the seen ledgers, and the
page reads it from **raw.githubusercontent.com** — also CORS-open, also no
token, and no redeploy needed, which is why the commit can keep `[skip ci]`.

**The raw text is the record; the parsed counts are a convenience.** If a
scraper changes its wording the numbers go null and the page still prints every
line. Never make the page depend on a regex in `run_log.py`.

**The log can be up to five minutes stale, and that is not a fault.** raw caches
on the path for 300s, **ignores the query string**, and its edges expire
independently — measured 25 Aug 2026, when curl here and the browser on the
deployed page disagreed for about nine minutes after a commit. The `?t=` in the
fetch busts the browser's own cache and nothing more. So a page that looks a run
behind just after a run is the CDN, not a broken automation. Don't go hunting.

Two things in the workflow that are easy to get wrong:

- Each scraper now records its exit code and lets the job carry on, so one
  source being down does not skip the other; a final step fails the job if
  either crashed. **`set +e` is required** for that — GitHub runs steps under
  `bash -e`, which aborts the step on a crash before the exit code is written.
- The commit step is `if: always()`, because a crashed run is exactly the one
  worth having on file.

### Serving it locally

**The preview process cannot read the iCloud project. Full stop** — probed
25 Aug 2026: `os.listdir()` on `public/` raises `PermissionError` from inside a
launched dev server, though the same call from the Bash tool succeeds. The two
run under different sandbox profiles. So the server has to serve a **copy**.

There are two separate failures and it is worth knowing both, because fixing
only the first gets you a server that starts and then 404s everything:

1. **Imports fail** when the cwd is the denied path — Python stats the cwd while
   searching `sys.path`. `python3 -I` drops the cwd from `sys.path` and fixes it.
2. **Reads fail** regardless. `SimpleHTTPRequestHandler` turns the
   `PermissionError` into a plain 404, so the symptom looks like a wrong path
   rather than a denial.

`.claude/launch.json` now serves **`~/.cache/notice-preview`**, which is outside
iCloud, readable, and — unlike the session scratchpad — the same path every
session, so the config is safe to commit. It also sets `"autoPort": true` and
takes its port from `$PORT`, because 4173 is often held by another session.

**It serves a copy, so re-copy after every edit:**

    cp public/*.html public/*.css ~/.cache/notice-preview/

`/api/admin` does not exist under a static server either, so the lock cannot be
tested locally. Test the function directly in node instead by importing the
handler and passing a mock `req`/`res`. **Only refusal cases belong in that
harness** — it runs against the live database, and a case that passes validation
is a real write. One did, and it overwrote Aireys Pub's coordinate with a Jan
Juc one (restored the same day by re-geocoding from the `source_note`).

`/api/admin` does not exist under a static server, so the lock cannot be tested
locally. Test the function directly in node instead by importing the handler and
passing a mock `req`/`res`. **Only refusal cases belong in that harness** — it
runs against the live database, and a case that passes validation is a real
write. One did, and it overwrote Aireys Pub's coordinate with a Jan Juc one
(restored the same day by re-geocoding from the `source_note`).

## Research rules — this project has been burned before

- **Never invent a URL.** Earlier versions of the database were full of fabricated
  `maps.app.goo.gl` links. `api/enrich.mjs` strips them server-side.
- **Never state a date without a source.** The Surf Coast Arts Trail sat in the
  database on the wrong date for months. Events carry `date_confidence`
  (high/medium/low). The column is still filled in honestly on every row; what
  changed on 25 Aug 2026 is that the **page stopped showing it**. Scott is happy
  with the dates as they stand, and a hedge on every imported row was teaching
  the reader to ignore the whole column. Nothing was raised to `high` to make the
  label go away — the record of what was actually checked is intact, so putting
  the label back is a one-line change in `render()` whenever it earns its place.
  Do not read the missing label as permission to guess a date.
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

## Type icons in the row gutter

Scott's own artwork. Five are in so far: `skatepark` → skate, `bike track` →
bike, `cafe` → coffee (from `../Notice.Place/Icons/SVG/`), plus `nature` →
nature and `sport`/`sport-event` → run (from `../Notice.Place/Icons Test/SVG/`,
which is a two-colour direction still being tried). That reaches 111 of 417
rows.

Each icon is a `<symbol>` in a hidden `<svg class="sprite">` at the top of the
body, and a row draws it with `<use href="#i-…">`. **Do not inline the path per
row** — it is ~4KB and the list is 400 rows. `ICON_OF` maps type → symbol id, so
adding one is two lines: the symbol, and the map entry.

- **Only one of the icon's two edges can be true, because the artwork is not one
  width.** The ink inside the 48×28 box runs from 22.5px (the cup) to 48px (the
  skateboard), so flush-left and a constant gap-to-the-name are the same
  requirement only if every icon is drawn to the same width. Both have been
  tried: `xMinYMid meet` starts every icon's ink on one line at `--gut` and lets
  the gap to the name run 24–49px; `xMaxYMid meet`, which is what ships, puts
  every icon's ink 24px from its name and leaves the left edges ragged — 60px
  for the skateboard, 85px for the cup, because the cup is portrait and the
  skateboard is 3:1 and both have to fit 28px tall. **The real fix is in the artwork**: draw each icon to
  fill the same 48px width and both edges come out true at once.
- **The box is 48px wide and always drawn**, even for a type with no icon, or
  every name would step left and right down the list.
- **Both ends of a row leave the same white space, and `--gut` is that number.**
  The icon's ink starts `--gut` in from the left edge and the pin's ink ends
  `--gut` in from the right — 60px, just inside the page's own 64px margin,
  which the full-bleed list can do and the text columns cannot. One number moves
  both ends; 64 would line the icons up with the masthead exactly.
  Two things make it hold: the row's right padding is `--gut + 40px`, the pin's
  lane, so the text stops ~24px short of the mark; and the pin is aligned to the
  *end* of its 36px button rather than centred in it, because an emoji's advance
  width differs by platform and a fixed offset would only be true on this one.
  The hit area runs inwards from there, into the padding.
- **The slot is a fixed 48×28 box, not a fixed width.** The set is not one
  proportion — the skateboard is 3:1, the bike is square, the cup is taller than
  wide — so sizing on width alone made the cup 60px tall and pushed the 57px row
  open. Each symbol carries its own `viewBox` and scales to fit inside, centred.
- **The empty slot is still drawn** for a type with no icon, or every name would
  step left and right down the list.
- `fill:currentColor`, so one copy serves both colour schemes. The artwork ships
  as `fill="black"`; that gets swapped on import.
- **Two-colour icons: the black follows the row, the yellow does not.** The
  test set is `#FFBB02` plus black. The yellow is the accent and is held in
  `--icon-accent`; the black is ink and becomes `currentColor` like the mono
  icons. That is the only treatment where nothing disappears — checked all four
  combinations side by side. Keeping the black literal is crisper for `nature`,
  whose dark centre sits *on* the yellow, but it erases the runner's head, which
  floats on the page ground and vanishes in dark mode.
- **The accent is an inline `style` on the path, not a CSS rule, and has to be.**
  `<use>` clones the symbol into a shadow tree that a selector in this stylesheet
  cannot reach — `.c-icon .accent{}` matches nothing and fails silently. An
  inline style is part of what gets cloned, and `--icon-accent` still reaches it
  because custom properties inherit across the boundary.
- **Colour only appears on hover.** At rest every icon is the one grey, whether
  its artwork is one colour or two, so a list of 400 rows is not a field of
  yellow; hovering brings the ink up and lets the accent through. This settled
  an inconsistency the two-colour set introduced — a saturated yellow beside a
  dimmed grey detail read as a fault rather than a decision — and it matches
  what the 📌 already does.

  The mechanism: the inline fill cannot be overridden by a rule here, but it is
  a `var()` lookup, so **the variable changes meaning per state** rather than
  the path changing. `.c-icon{--icon-accent:currentColor}` collapses the icon to
  one grey at rest; `.rowhead:hover .c-icon{--icon-accent:var(--accent)}` lets
  the brand colour through. `--accent` on `:root` stays the single home of the
  yellow. Note this makes `--icon-accent` a *state*, not a colour — do not put a
  literal in it.

  A **pinned** row is the exception: it holds the hover look for good, tint and
  coloured icon both, so what you have saved is picked out of the list without
  hovering. That is also the one way either colour reaches a touch screen.
- **The bike does not survive 28px.** Its frame and spokes merge and it reads as
  a cog. Checked at 2×; it is the artwork meeting the size, not a bug. The other
  two are fine. Any icon with this much line detail will need a simplified
  small-size version before the set reaches all 26 types. The two-colour pair
  hold up far better at this size than the bike does — solid masses survive the
  reduction where line work does not, which is the useful lesson for the rest of
  the set. The runner is unmistakable; `nature` reads as a starburst or a sun
  rather than as anything specifically natural, so it may be carrying the wrong
  shape rather than the wrong size.

## Light, dark, or follow the system

The pill beside the saved count cycles **Auto → Light → Dark**. Auto is a real
third state, not a default: it clears `notice.theme` and follows the system, so
a laptop that flips at sunset takes the page with it. Storing `light` records
that the reader has overruled that on purpose.

The stylesheet already had the three-state shape — bare `:root` is light, the
`prefers-color-scheme` block is guarded with `:not([data-theme="light"])`, and
`[data-theme="dark"]` overrides both — so the switcher **sets or clears one
attribute and redefines no colour**. Keep it that way.

Two things are load-bearing:

- **A script in `<head>` applies the stored choice before the first paint.**
  Doing it with the rest of the JS at the end of the body draws the page in the
  system scheme and then flips it.
- **The basemap has to be told.** It is a CARTO stylesheet on a CDN and does not
  read this page's tokens, so the click handler calls `MAP.setStyle()`.
  `isDark()` already checked the attribute before the media query, so it was
  right in all three states without changing it. The existing `matchMedia`
  listener still handles a system change and correctly ignores it when the
  reader has forced a scheme.

## A row hovers in its own theme's colour

`.rowhead` carries `data-tint="<first theme>"` and hover paints `--tint`, so
running the eye down the list the colour says what kind of thing a row is before
the type column is read. A row with no theme keeps the grey it always had.

**The colours are `oklch` and that is not decoration.** Its lightness is
perceptual, so all twelve hues land at the same brightness. The same twelve
written in `hsl` at identical numbers give a yellow that reads almost white and
a blue that reads nearly black — the list would look like some rows were
shouting. Light and dark each set one `--tint-l`/`--tint-c` pair; the twelve
hues are shared and are spaced roughly evenly around the wheel. Tuning the whole
set is two numbers.

**A pinned row keeps its tint permanently**, along with its icon in colour —
`.rowhead.saved` matches everything `.rowhead:hover` does. So the saved rows are
picked out of the list at a glance, and colour reaches a touch screen, where
there is no hover at all.

The class is set two ways and needs both: from `kept` in the row template, so it
survives a re-render, and toggled directly on the pin click, because a click
outside the saved view deliberately does not re-render.

## Saved listings — a wishlist with nobody logged in

Every row carries a 📌 in its right-hand gutter. It is invisible until you hover
the row and stays lit once it is on; on a touch screen, where there is no hover,
it is always faintly there. The count sits in an outline pill at the top right of
the page, and pressing that pill holds the list down to what you saved — a chip
reading *Saved only* and the usual Clear all are the ways back out.

The keys live in this browser's `localStorage` under `notice.saved` and nowhere
else. No account, no server, nothing about the reader leaves the page — which
also means the list does not follow them to their phone, and clearing the browser
clears it. A write can fail outright in private browsing; the pin still works for
that visit rather than not working at all.

Four things that are load-bearing:

- **The key is `e13`/`a90`, not `13`.** Ids collide across the two tables, so a
  bare id would file event 13 and activity 13 as the same saved thing — the same
  collision `sync.py reject` still has. `keyOf()` puts the table letter on it.
- **The pin is a sibling of the row button, never inside it.** A `<button>` inside
  a `<button>` is invalid markup and swallows the row's own click. It sits in a
  `.rowhead` wrapper and is positioned into the gutter `--pad` already leaves.
- **It is `.savebtn`, not `.pin`.** `.pin` is the map's marker and any rule that
  matches both ends up on the map, where a stray `position` drops every marker
  out of the canvas.
- **Toggling only re-renders inside the saved view**, where the row has just left
  the list. Anywhere else a re-render would shut every open row on the page.

**Pressing one puts it in the board.** The 📌 travels down-left, which is where
its needle points, shrinking as it goes — away from you, not smaller — and the
board gives a little back on the way out. The overshoot is what reads as *in*:
the travel is two pixels at this size and would pass for a wobble on its own.
Coming out is the same move reversed and shorter, because taking something off
a list is not an occasion.

Three things that keep it honest: the animation is on a `.glyph` span inside the
button, so the 36px hit area does not move with the mark; the class is removed
and re-added around a forced reflow, or a second press on the same pin does
nothing; and the page's blanket reduced-motion rule only turns off *transitions*,
so `.savebtn .glyph` names `animation:none` itself. Unpinning inside the saved
view fades the row and waits 260ms before the re-render, so the pin is seen
coming out rather than vanishing with the row — and that wait is skipped
entirely under reduced motion.

Saving something is asking for it, so the At home entries the default list holds
back are not held back from your own list (`ok()` skips `atHomeHidden` when the
saved view is on). The map reads the same filter, so it shows your saved pins too.

## A weekly event still happens next week

`recurrence` used to be display-only — printed in the row, never read by the
filter. An event therefore surfaced only on the single date in `starts_on`, so a
standing Saturday gig was invisible six days in seven and fell out of the list
entirely the day after. Three were already stale when this was found: live music
at Blackman's and the Aireys Pub, and the Belmont Sunday Market.

`nextDate()` rolls **weekly** and **fortnightly** events forward by 7 or 14 days.
That is safe because it preserves the weekday, so the rolled date is the truth and
not a guess. It feeds the list filter, the When filter, Soonest first, and the
date label.

**Monthly and annual are deliberately not rolled.** Adding a month turns "third
Sunday" into "the 20th"; adding a year moves the weekday too. Either would publish
a date nobody announced — the Arts Trail failure exactly. Those need a person to
set the next `starts_on`, which is the same gap as the recurrence-in-the-name item
below.

Parse *and* format in UTC inside that function. The first version parsed
`"YYYY-MM-DDT00:00:00"` as local time and formatted with `toISOString()`, which
shifts back a day at +10 — every rolled Saturday gig landed on Friday. A unit test
caught it before it shipped; clicking around the page would not have.

## Known outstanding

- An activity's single `url` is whatever it is — a map pin for some, the venue's own
  site for others. The row labels it by inspection (`isMapLink`), so don't assume the
  slot means "map". 87 of 203 activities carry a website there. `Directions` is built
  separately from `lat`/`lng`. 128 of 272 activities are pinned; the rest are the
  At home entries and the roving ones, which have nowhere to be
- 42 entries use Google Maps *search* URLs rather than pinned coordinates
- `Gather` (activity 291, venue 84) and `Gather Athletics Shop Run` (event 89),
  both Ocean Grove, added 24 Aug 2026 from photographs in the event inbox. Neither
  has a `km`. The run's `recurrence = weekly` rests on Scott confirming it is still
  current, **not** on the source: the Instagram post behind it is dated 20 March and
  its caption reads as a one-off. Recheck if it goes quiet.
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
- `Snake Valley Dark Sky Site` (activity 90) was deleted 25 Aug 2026 — 100 km
  inland toward Ballarat, which is the wrong direction. Everything else past
  75 km is Otways and Great Ocean Road (Cape Otway, Beech Forest, Kennett River,
  Lavers Hill, Forrest), and those sit on the region's spine rather than outside
  it, so distance alone is not the test — direction is. It was `verified = true`,
  which again only recorded that a person had looked.
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
- `Point Lonsdale Dog Beach` (place 91) will not geocode. Nominatim has no such
  feature under that name or "Narrows Beach", and the nearest candidate
  ("Point Lonsdale (Back) Surf") is not provably the same spot. Left null.
- `Barwon Heads Community Park Playground` (89) is pinned at the park polygon's
  centre, which reverse-geocodes to the pony club inside the same park. Right
  precinct, possibly not the playground — worth a better point if it matters.
- **The moderation queue is empty because everything was verified in bulk**
  (25 Aug 2026, all 101 at once, on Scott's instruction). Each row's
  `source_note` says so, in those words. A `verified` flag on one of these
  records that Scott accepted the queue, not that anyone read that row's own
  page — treat it as weaker evidence than a flag set one row at a time, and do
  not let it stop you questioning a date. `Ashmore Arts` (169) and `The Fives` (168) are both
  verified; both had their distance cleared rather than guessed and still need real ones,
  as does `Bird Rock Farm` (171)
- Distances unverified; Waurn Ponds known wrong
- **Autofill is dead until the Anthropic account is topped up.** Every call returns
  400 "credit balance is too low". The page now says so in English rather than
  printing the JSON. Nothing else on the site depends on it.
- A stray Vercel env var called `Whattodo2` exists and nothing reads it

## Gotchas already paid for

- **The preview pane cannot serve this project from iCloud — it serves a copy.**
  The dev-server process launched by `.claude/launch.json` starts with its cwd
  set to the project directory, and the sandbox denies that path to *that*
  process (the Bash tool can read it fine; different profiles). A committed
  `scripts/serve.py` would not help; the launcher cannot read that file either.

  **This was solved properly 25 Aug 2026** — `launch.json` serves
  `~/.cache/notice-preview`, a stable path outside iCloud, with `-I`,
  `"autoPort": true` and the port from `$PORT`. Re-copy after every edit with
  `cp public/*.html public/*.css ~/.cache/notice-preview/`. See "Serving it
  locally" under Back of house for the two distinct failures involved — the
  second one 404s instead of erroring, which is what makes it confusing.
  Verifying against the deployed site works too, once a push has built.

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

## Places — a taxonomy, RUN 24 Aug 2026

`supabase/PLACES_TAXONOMY.sql` renamed `venues` to `places` (and `venue_id` to
`place_id`), and split `kind` into two columns. **Applied 24 Aug 2026** via the
Management API, in one transaction. `listings` now carries `place` and
`place_kind` instead of `venue`; there is no `venue_id` anywhere.

`classify_places.py --write` ran straight after: **101 places, 89 with a kind,
12 left null**, 43 carrying at least one offer (live-music 38, food 35,
drinks 35, tickets 2). `place_kind` reaches 113 of the 417 listings.

The page's `r.place ?? r.venue` fallback is now dead weight on the `venue` side
— harmless, and worth deleting next time that block is touched.

**Renaming the table broke two scripts, and one of them runs unattended.**
`scrape_venues.py` is on the Mon/Thu Action; it wrote `kind: 'event venue'`,
which the new foreign key rejects, and read `venue_id` throughout. Both it and
`name_rules.py` were repointed at `places`/`place_id` in the same commit as the
migration. Two traps worth remembering if this pattern repeats:

- **`kind` changed meaning, it did not just move.** `kind` is now the checked
  vocabulary and the old free text is `kind_legacy`. `scrape_venues.py` decided
  which names were organisers with `kind == 'organiser'` — a legacy value — so
  reading the new column would have silently stopped detecting them rather than
  erroring. Provenance text new rows write goes to `kind_legacy`.
- **`name_rules.py`'s safety gate probed `listings?select=venue`.** After the
  rename that probe fails, so the gate would have reported "the page cannot
  print the venue yet" when in fact the opposite was true. A guard that fails
  closed on a schema change is still a guard that lies. It reads `place` now.

`events.venue` — the free-text column — is deliberately **not** renamed, and
`eventlib.py`'s `venue_name`/`venue_suburb` keys are its own vocabulary, not
the database's. Neither needed touching.

Why the split. `venues.kind` was doing two jobs badly. 40 of 79 rows said
"event venue", which records how the row got created rather than what the place
is — it covered beaches, a cenotaph, a library, a street, a carpark and a
resort. The ~30 real values came off a music-venue spreadsheet, so the whole
vocabulary was a music-industry one applied to a coastline. And it was already
two axes fighting over one column: `Hotel` and `Beach` say what a place **is**,
`Live Music Venue` says what **happens** there, which is why the Torquay Hotel
— a pub, a restaurant and a live music room — could only be filed as one.

So `kind` is one value foreign-keyed to `place_kinds` (the `types` pattern) and
`offers` is a `text[]` checked against `place_offers` (the `conditions`
pattern). The old free text survives in `kind_legacy`.

There is deliberately **no `hotel` kind**. In Australia a hotel is usually a
pub, and every "Hotel" in the music sheet is one; the place that is actually
accommodation, Mantra Lorne, was never labelled a hotel. Pubs are `pub`, places
you sleep are `accommodation`, food and drink live in `offers`.

`classify_places.py` proposed a kind and offers for all 101 — 28 kinds used, 12
left null. Read the dry run before `--write`.

The 12 with no kind are not failures; they are places the vocabulary has no word
for: four shops (`4 Pines X Boardriders Torquay`, `Patagonia Torquay`), three
organisations that are not rooms (`Bellarine Catchment Network`, `Surf Coast
Environment Group`, `The Book Club Social`), two walks, a boat ramp, a lake, and
`Bloom`, which still has nothing on file but a name and a suburb.

**`The Sound Doctor` (32) is filed as `hall` and probably should not be.** Its
`kind_legacy` says Live Music Venue, so the rules had no reason to doubt it, but
this file records elsewhere that it is a promoter who hires Anglesea Memorial
Hall — an organiser, not a room. There is no `organiser` kind to move it to, and
inventing one to hold a single row is how `kind` got into trouble the first
time. Left as it is, flagged here, for a person to decide. Its ordering is the rule and it is load-bearing: first
match wins, so the noun a name ends on must be tested before the geography it
mentions, or Bells Beach Brewing files as a beach and Fishermans Beach Reserve
does too. Both did, on the first pass.

Offers stay conservative — 39 of 79 carry any. `live-music` only where the row
was seeded from the music spreadsheet, since that sheet is a list of places
that put music on. `food`/`drinks` follow from a licensed kind, `tickets` from
having a ticketing URL. Nothing else is guessed, and **no accessibility claim
is ever inferred** — a wrong one sends someone to a place that cannot take them.

## Next things worth doing

0. **`/admin` cannot save until three variables exist in the Vercel project.**
   Checked against the live deploy 25 Aug 2026: the function answers 501
   `not_configured`, because the Vercel project only ever held
   `ANTHROPIC_API_KEY` — the scrapers read Supabase from **GitHub** secrets, so
   the keys have never been needed on Vercel before. Add, then redeploy:
   `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (both are in `.env`) and
   `ADMIN_PASSWORD` (anything you like). Vercel dashboard → whattodo →
   Settings → Environment Variables, Production.
   The reading half of the page works without any of them.
1. Give `The Sound Doctor` (place 32) the right kind, or decide `hall` will do
   — see the Places section. The other 11 unclassified places need a word the
   vocabulary does not have yet (shops, organisations, two walks, a boat ramp).
2. Build place rows for the four dated events whose free text already names a
   real place: `Baines Crescent outlets` (22), `Anglesea Community Hub` (30),
   `Anglesea Community Precinct` (53), `Torquay Common` (77). Each one then
   gets a pin and a tidier name. `name_rules.py` lists all 18 that have a date
   and a time but no venue.
3. **Give the 16 place-less events a place.** Every event is verified now, so
   `sync.py pending` is empty and this is what is actually left. Four only need
   a place row built from the name they already carry (`The Mac`, `Anglesea
   Community Precinct`, `Torquay Common`, `Surf Coast Walk`); six name only a
   suburb and need a real start line; two are genuinely shire-wide; four are
   the `Quiet Club` nights, parked 25 Aug 2026 — their venue is missing from
   the source, not from us (see below).
4. Verify community additions — `python3 scripts/sync.py pending`, then `verify <id>`
   to approve or `reject <id>` to delete. `reject` refuses verified rows and asks
   before deleting; `--yes` skips the prompt.
   `add file.json` (or `-` for stdin) writes a researched entry, one object or a
   list. It checks types, conditions, enums, date shape and URLs against the live
   vocabularies before writing, so a bad field in a batch names itself instead of
   failing an opaque insert. It refuses a name that already exists — pass `--force`
   only when it genuinely is a different thing. `--verified` requires a
   `source_note`; `--dry-run` checks without writing. An event's link is
   `info_url`/`ticket_url`, never `url`.
5. Pin the 42 entries whose `url` is a Google Maps *search* rather than a
   coordinate — each one is a missing pin on the map
6. Promote the Ideas Pipeline into the database
7. A scheduled job that re-checks estimated event dates as real ones get announced
