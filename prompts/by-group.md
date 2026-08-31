# Nine research prompts, one per group

Copy one block into Cowork with this folder open. Each is a **loop** — it works
every type in its group without stopping to ask, and posts one summary at the
end. Run them one at a time; two at once will both add the same café.

Counts in each prompt are as at **26 Aug 2026**. They will be wrong after the
first pass, which is fine — every prompt starts by reading the real numbers with
`scripts/have.py`, so a stale figure in the prompt only sets the reading order.

## Getting the repo — read this before pasting any prompt

**Every prompt below starts by cloning. Do not go looking for a folder on the
Mac, and do not accept a folder someone suggests.** Three Cowork sessions have
been lost to this, twice by being pointed at `~/surfcoast-events` — which is a
real repo and the wrong one. That is `Scott-Designed/surfcoast-events`, an older
scraper project last touched in March; none of this tooling has ever been in it.

The project is **public**, so an anonymous clone needs no SSH key and no token:

```bash
git clone https://github.com/Scott-Designed/whattodo.git
cd whattodo
```

Three reasons this beats connecting a folder. The real checkout lives in iCloud
Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Clients/whattodo`,
**not** `~/Desktop`), and this project has a documented history of sandboxed
processes getting `PermissionError` on that path while the terminal reads it
fine. A cloud VM has no route to the Mac's filesystem at all. And a clone is
guaranteed to be at `origin/main`, which is where every pass's tooling lands.

**A pass never writes to the database and never needs a credential.** Scott
pastes the results back and applies them himself. So do not ask for `.env`, do
not ask for `SUPABASE_SERVICE_KEY`, and do not try to write — hand back the
batches and the worklog as files.

Validate them properly rather than by eye:

```bash
python3 scripts/sync.py check batch.json
```

`check` needs no credentials. It reads the live vocabularies with the public
anon key out of `public/notice-data.js` and runs **the same `check()` `add`
runs** — types, kinds, conditions, season, cost, daypart, the URL rules, the
four-decimal coordinate rule, unknown fields — plus the same name-clash query
against every existing listing. A batch that passes it will apply cleanly.

This exists because it did not: the arts and ocean passes each hand-rolled
their own copy of `check()` when no `.env` arrived, and two copies of a
validator is the drift this project keeps paying for.

Nothing gets pushed.

Three commands the prompts lean on:

```bash
python3 scripts/have.py                 # all 43 types with counts and groups
python3 scripts/have.py hospitality     # every type in a group, thinnest first
python3 scripts/have.py cafe            # the actual listings, names and towns
python3 scripts/have.py places          # the places table, and which have a feed
```

The shared rules — the vocabulary, the URL and coordinate rules, what goes in
which table — are in [prompts/RESEARCH_RULES.md](RESEARCH_RULES.md). Every
prompt reads it rather than repeating it.

---

## 1 · The ocean

> beach 25 · swimming 10 · paddling 9 · surfing 8 · water 8

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The ocean group.

Work its five types thinnest first: water (8), surfing (8), paddling (9), swimming (10), beach (25).
Target 12 rows per type, or every honest candidate in the region if that is fewer. Never pad to hit a number.

This is a loop. For each type, in order:
  1. Run `python3 scripts/have.py <type>` and read what is already there — names and towns.
  2. Search for candidates that are not on that list. Good sources: Parks Victoria, Surf Coast
     Shire and City of Greater Geelong beach pages, Life Saving Victoria's patrolled beach list,
     Visit Great Ocean Road, the Bellarine bay beaches, individual surf club and boat ramp pages.
  3. For each candidate get a first-party source, geocode it, and build the row. Drop anything
     you cannot source. Leave km null.
  4. Write the batch to the scratch directory, run `python3 scripts/sync.py add <file> --dry-run`,
     fix what it complains about, then run it again without --dry-run.
  5. Append to prompts/log/ocean.md: what you added, what you rejected and why, what is still open.
  6. Go straight to the next type. Do not ask me between types.

Specific to this group:
  - A surf break is not a beach. Give it `surfing` first and pin the car park or the access
    track — somewhere a person can actually stand — never a point out in the water.
  - Bay beaches on the Bellarine are a different thing from the ocean beaches and the site is
    thin on them: calm, shallow, and the honest answer for anyone with small kids. `swimming`
    first, `beach` second.
  - `water` is the on-it types — boat ramps, sailing, fishing spots, snorkelling trails.
    `paddling` is kayak and SUP put-ins. If a spot is both, pick the one someone would search for.
  - Conditions earn their keep here more than anywhere else: low-tide, high-tide, calm-sea,
    low-wind. Only write one you can justify from the source, and never write `any-weather` on
    an ocean listing just to fill the field.
  - Run the water check on anything you pin near the coast: a coastal point that reverse-geocodes
    to bare "Victoria, Australia" is in Bass Strait.

Do not stop until all five types have been through the loop. An empty search is a finding to log,
not a reason to stop. If sync.py refuses the same row twice, log it and carry on.

When every type is done, post one summary: rows added per type, near-duplicates you spotted in
the existing data, and anything you found that the 43-type vocabulary had no word for.
```

---

## 2 · The landscape

> nature 59 · walk 34 · night 23   — 101 rows and only **42 pinned**

**HALF ONE IS DONE — 31 Aug 2026, 23 rows pinned, group 45% → 65%.** Erskine,
Triplet, Hopetoun, Beauchamp, Kalimna and Sheoak Falls all resolved as
`waterway=waterfall`, Teddy's Lookout and Cape Otway as named features, and
seven were refused rather than guessed (see below). Run HALF TWO only.

**Seven stay unpinned and three of those were refused on reading the match**,
which is the part worth keeping: Frog ID matched a `waterway=river`, a LINE
feature; Swan Bay Birdwatching matched `railway=halt`, the Bellarine Railway's
Swan Bay *station* rather than the wetland — a name collision, not a location;
and You Yangs Rock Climbing matched the whole regional park polygon, which
CLAUDE.md already flags as reading like a placeholder on two other rows. A
returned coordinate is not the same as a found place.

**This pass is different from the other eight: it is a PINNING job first and a
research job second.** The landscape group is not short of rows, it is short of
coordinates — 42% pinned, by far the worst of any group (produce, the next
worst, is 76%). And the unpinned ones are not vague ideas: 22 genuinely name no
single place and are correctly null, but **37 name a real, findable place** and
simply have never been geocoded. Erskine Falls, Triplet Falls, Hopetoun Falls,
Maits Rest, Melba Gully, Teddy's Lookout, the Otway Redwoods, Ironbark Basin,
Cape Otway Lightstation — the region's headline walks, none of them on the map.

Nearly every one is a named Parks Victoria or GORCPA feature, which is the case
where "ask for the feature by name" works best. `nearby.py --kinds landscape`
already matches several of them to their existing rows.

```text
Clone the repo — do not go looking for a folder on the Mac and do not accept one
somebody suggests. It is public, so this needs no key and no token:

    git clone https://github.com/Scott-Designed/whattodo.git
    cd whattodo

Then `python3 scripts/nearby.py --refresh` once. Never run --refresh again mid-pass.

**You need no credentials for any of this and you will not write to the database.** Scott
applies the results. Do not ask for .env. Half one hands back a table of pins; half two
hands back JSON batches validated with `python3 scripts/sync.py check <file>`, which needs
no credentials and runs the same checks the real write does.

Do not push.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work The landscape group.

DO HALF ONE BEFORE HALF TWO. They are different jobs.

── HALF ONE: pin what is already here ──

`python3 scripts/have.py walk`, then `nature`, then `night`. Rows printed with a leading
`·` have NO COORDINATE. There are about 37 that name a real place, and putting them on the
map is worth more than any number of new rows.

For each one:
  1. Ask Nominatim for the FEATURE BY NAME — "Erskine Falls", not "Lorne". A named
     waterfall, lookout, reserve or lightstation resolves to the feature; the same place
     asked for as a town or a street resolves to a boundary or a road centreline, and this
     week a street query returned two segments 4.5km apart.
  2. REFUSE `type=administrative`. That is a suburb or park boundary, not a place — "Bells
     Beach" resolves to a polygon whose centre is 2.6km from the beach.
  3. Reverse-geocode every candidate before you accept it. Nothing under it means do not
     write it.
  4. **A walk's coordinate is its TRAILHEAD**, not the middle of the track and not the
     summit. If the feature you matched is the falls but the walk starts at a car park,
     say which one you used in `source_note` — several rows written this week pin the
     access rather than the thing, and each says so.
  5. Anything you cannot place stays null, and the reason goes in the log. A null pin is
     honest; a wrong one is the failure this project has already paid for.

You cannot patch existing rows from sync.py. Produce the pins as a table in the worklog —
id, name, lat, lng, what Nominatim matched, and the reverse-geocode result — and I will
apply them.

── HALF TWO: what is missing ──

Then, and only then, look for rows that do not exist. Work the three types thinnest first:
night (23), walk (34), nature (59).

  1. `python3 scripts/nearby.py "<town>" --kinds landscape --radius 6000`. Use a bigger
     radius than usual — Otway features are a long way from the town centre they belong to.
  2. Then check by hand. Parks Victoria, the Great Ocean Road Coast and Parks Authority,
     the Otway Ranges walks guides, ANGAIR, council reserve pages, Trust for Nature.
  3. Before writing, search existing names for the candidate's distinctive word.
  4. Build the row, `python3 scripts/sync.py check <file>`, fix whatever it names, and
     leave the batch as a file. Append to prompts/log/landscape.md.

Judgement on what the sweep returns:
  - **`natural=peak` is mostly noise.** The Otways are full of named hills nobody visits —
    Cockerill Hill, Hall Hill, Camp Hill, Black Hill all came back on a test sweep. A peak
    earns a row only if a land manager describes a walk or a lookout there.
  - **`historic=ruins` is the monument-and-landmark vocabulary gap**, not a type. The
    Former Beech Forest Hotel and the Goods Shed are real and there is no honest type for
    them. Log them; do not force them into `nature`.
  - `tourism=attraction` is a grab bag — it returned a horse-riding business at Cape Otway.
    Judge each.

Specific to this group:
  - **The line between landscape and outdoors is being in it versus doing something in it.**
    A walk and a glow-worm hunt are landscape; a mountain bike trail is outdoors. CLAUDE.md
    calls this the one grouping decision worth arguing with — if a row sits badly, log the
    argument rather than quietly filing it in the other group.
  - `night` is after dark outdoors — stargazing, glow worms, sunset points, moonrise. Those
    carry real conditions: `clear-sky`, `new-moon`, `full-moon`, `geomagnetic-storm`. OSM
    will not help here at all; this type is entirely source-driven.
  - **Do not write `any-weather` to fill the field.** The ocean pass put it on 34 of 41 rows
    against a convention of 2 in 44, and `met()` returns TRUE for it, so it claims the
    listing suits any weather. A rainforest walk in a storm does not.
  - Seasonal things — wildflowers, glow worms, fungi, whales — belong in `season` and
    `notes`, and `season` is a LIST from any/spring/summer/autumn/winter and nothing else.
    The sentence about when the season actually runs goes in `notes`.
  - Distance and grade of a walk come from the park's own page into `duration` and `notes`.
    Do not estimate either. km stays null always.
  - A dated thing needs a `place_id` or it cannot be on the map. `have.py places` first.

Do not stop until both halves are done and all three types have been through the loop.

Post one summary: the pin table from half one, rows added per type in half two, everything
you could not place and why, and anything the 43-type vocabulary had no word for.
```

## 3 · The outdoors

> mountain biking 33 · parks & playgrounds 20 · skatepark 19 · camping ground 17
> · running 16 · cycling 13 · golf 2 · rock climbing 2

Never run. 110 rows, 74% pinned. Two of its eight types are already well covered
and should not be re-walked: **`mountain biking` was worked by the bike pass**
(four clubs, eight shops, the EntryBoss fixtures), and `camping ground` and
`skatepark` are council assets seeded early. The real gaps are `golf` and
`rock climbing` at two rows each, and `cycling` and `running` at the thin end.

**OSM is only half a net here.** `nearby.py --kinds bike` covers the cycling
types and nothing else in this group is mapped usefully — a skatepark, a
parkrun start and a golf course come off council and club pages, not the map.

```text
Clone the repo — public, no key, no token:

    git clone https://github.com/Scott-Designed/whattodo.git
    cd whattodo

Then `python3 scripts/nearby.py --refresh` once. Never run --refresh again mid-pass.
You need no credentials and you will not write to the database. Scott applies the results.
Validate every batch with `python3 scripts/sync.py check <file>` — no credentials needed,
same checks the real write does. Do not push.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research The outdoors group.

Work the eight types thinnest first: golf (2), rock climbing (2), cycling (13), running (16),
camping ground (17), skatepark (19), parks & playgrounds (20), mountain biking (33).
Run `python3 scripts/have.py outdoors` for today's real counts.

Do not re-walk mountain biking, camping ground or skatepark without reading what is there
first — the first two were worked in August and the third was seeded early.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>`.
  2. `python3 scripts/nearby.py "<town>" --kinds bike` for the cycling types. For everything
     else the map is not your source — go to the land managers.
  3. Sources that beat OSM here: Surf Coast Shire and City of Greater Geelong recreation and
     facility pages, Parks Victoria, parkrun Australia, AusCycling, the Forrest and You Yangs
     trail networks, Skate Victoria, golf club sites, the Bellarine Rail Trail and Barwon
     River loop pages, caravan park operators, Parks Victoria hike-in campsites.
  4. Before writing, search existing names for the candidate's distinctive word.
  5. Build the row, `python3 scripts/sync.py check <file>`, fix what it names, leave the
     batch as a file. Append to prompts/log/outdoors.md.
  6. Straight to the next type. Do not ask me between types.

Specific to this group:
  - A council facility has a street address. Geocode the FACILITY, not the town. Ask for the
    feature by name before its street: a named reserve resolves, an address resolves to a
    road centreline that is a coin toss between segments. Refuse `type=administrative`.
  - `running` and `cycling` want a START LINE, not a region. A parkrun has a fixed start; a
    rail trail has two ends, so pin the one with the car park and say which in source_note.
  - `dry-trails` is no rain for 48 hours, for unsealed tracks. `dry-ground` is not raining
    now, for a skatepark. Deliberately different, and the two conditions that earn their
    place here.
  - Do NOT write `any-weather` to fill the field. The ocean pass put it on 34 of 41 rows
    against a convention of 2 in 44, and met() returns TRUE for it — it claims the listing
    suits any weather, which a mountain bike trail in a storm does not.
  - `golf` and `rock climbing` have two rows each. If the region honestly holds four golf
    courses, add four and log that the type is small. Do not stretch rock climbing to indoor
    gyms outside the region.
  - A camping ground needs booking information in `notes` and a real operator or Parks
    Victoria URL. Never a fabricated one.
  - `parks & playgrounds` is where duplicates live — a park often already exists in `places`.
    Run `python3 scripts/have.py places` before writing this type.
  - The line between outdoors and landscape is doing something in it versus being in it. If a
    row sits badly, log the argument rather than filing it in the other group quietly.
  - Any dated thing — a race, a ride, a working bee — needs a `place_id` or it cannot be on
    the map. `have.py places` first; log the address if there is no row.

Do not stop until all eight types have been through the loop.

Post one summary: rows added per type, which types the region genuinely cannot fill, existing
rows needing correction, and anything the 43-type vocabulary had no word for.
```

## 4 · The hospitality

> restaurant 7 · cafe 6 · winery 6 · bar 3 · pub 2 · bakery 1 · brewery 1

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The hospitality group.

Work its seven types thinnest first: bakery (1), brewery (1), pub (2), bar (3), cafe (6),
winery (6), restaurant (7).

This is the thinnest group on the site and the biggest gap: 26 listings for a coastline whose
main street is cafés. Target 15 rows per type, or every honest candidate if fewer. Torquay,
Jan Juc, Anglesea, Lorne, Barwon Heads, Ocean Grove, Queenscliff and Geelong should all be
represented in `cafe` before you call it done.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>`, then `python3 scripts/have.py places` — a venue can
     already be a place row without ever having a listing, and adding it as an activity would
     make a second copy of it.
  2. Search for candidates. Good sources: the venue's own site or Instagram, Broadsheet Geelong,
     Visit Great Ocean Road, the Bellarine Taste Trail, Wine Geelong, the Surf Coast Shire
     business directory, individual main-street strips town by town.
  3. First-party source, geocode to the street number, build the row. km stays null.
  4. Batch to scratch, `--dry-run`, fix, write.
  5. Append to prompts/log/hospitality.md.
  6. Next type, without asking.

Specific to this group:
  - The type split is load-bearing and CLAUDE.md explains why: filing Blackman's as a cafe or a
    bar loses the reason anyone goes. A `brewery` is where it is brewed. A `winery` is a cellar
    door. In Australia a **hotel is usually a pub** — every "Hotel" in this region's music
    listings is one.
  - `cidery` and `distillery` are not types and are not to be invented. Flying Brick and The
    Whiskery are filed as `bar` + `produce`; follow that.
  - A place that is genuinely two things carries both, primary first — a winery with a proper
    restaurant is `["winery","restaurant"]`, a bakery you sit down in is `["bakery","cafe"]`.
  - Hours belong in `notes` and they go stale, so quote the source and its date in `source_note`.
    Gather's row is the model for that.
  - `url` is the venue's own site, or its Instagram if that is all it has. Never a Google Maps
    search link, never a maps.app.goo.gl link, never an aggregator's page for it.
  - A venue that publishes its own gigs or sells tickets is worth more as a `places` row with
    `events_url` than as a listing — that gets read twice a week forever. You cannot write
    `places` from a script, so collect those in the log with name, suburb and URL for /admin.

Do not stop until all seven types have been through the loop. Post one summary: rows added per
type and per town, the venues worth a `places` row with a feed, and any near-duplicate of an
existing name you had to think about.
```

---

## 5 · The produce

> market 25 · produce 42 · nursery 10 · farm life 9   — **four** types; `shop` is a kind now

Rewritten 27 Aug 2026 after the two hospitality passes. Three things they taught
that change this one:

- **OSM is the wrong net for markets.** A monthly market in a shire carpark is
  not a mapped point of interest. `nearby.py --kinds=produce` will find shops and
  farm gates and almost no markets, so markets are source-driven, not map-driven.
- **`shop` was retired as a type on 27 Aug 2026** — 43 down to 42 — and is a
  **kind**. This group is four types. A shop is `kind: "shop"` plus a hand line
  in `BY_ID` in classify_kinds.py, because a shop can no longer be inferred from
  its types. If you would go to it for its own sake it is a **venue** — the
  Chocolaterie rule. The produce pass of 28 Aug found no row that needed the
  shop kind at all.
- **`season` is a list**: `any / spring / summer / autumn / winter`, nothing
  else. "Strawberry picking November to May" is a `notes` line. sync.py refuses
  anything else now — it used to fail mid-batch with a raw Postgres error after
  three rows were already written.
- **All 13 markets we hold are events, and eleven never roll forward** — eight
  `monthly`/`annual`, three with no recurrence at all; only two are weekly. They are all current
  today; they go stale one at a time, silently, and only a person can move them.
- **A url is null or it is the venue's own.** `sync.py` now refuses a Google
  Maps search link outright, because two passes wrote them and one called it
  policy.

```text
First run `git pull`.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research The produce group. Also read
prompts/log/hospitality.md — the two hospitality passes logged produce candidates they
deliberately left for you (The Olive Pit and The Beach House Lolly Shop in Ocean Grove, the
Apollo Bay lolly shop, and others marked "produce pass"). Start from that list.

This group splits in two and the halves work differently. Do BOTH, in this order.

── HALF ONE: market (13) — source-driven, not map-driven ──

Markets are events, not places, and OSM does not map them. Do not use nearby.py for this half.

  1. Read the markets we already hold: `python3 scripts/have.py market`. Most never roll
     forward — monthly, annual, or no recurrence at all.
  2. For EACH of those, open the organiser's own page and check the next date we hold is still
     what they publish. Monthly and annual never roll forward, so a date that has passed is a
     dead listing and a date that moved is a wrong one. Report every disagreement with the id —
     do not edit existing rows, that goes through /admin.
  3. Then find the markets we do not have. Sources: the Victorian Farmers Markets Association
     accredited list, Surf Coast Shire and City of Greater Geelong event pages, Bellarine
     Taste Trail, individual market Facebook pages, the towns' own community pages.
  4. Write each as an EVENT: `starts_on`, `time_text`, `recurrence`, `location`, `info_url`.
     An event's link is info_url or ticket_url, never url. The next date comes off the
     organiser's own page — a worked-out "third Sunday" is not a date, and that is exactly
     how this database published the Arts Trail wrong.
  5. Where a market runs at a fixed venue, check `python3 scripts/have.py places` and note the
     match in the log so the event can be linked and get a pin.
  6. Three we hold have NO recurrence set at all (Aireys Inlet Market, Anglesea Twilight
     Market, Riverbank Market). Find out what they actually are and report it.

Three of our markets are called just "Community Market". That is what is left after the town was
stripped out of the name, and on a Markets page they are indistinguishable. Say in the log what
each one is actually called by its organiser — a rename is a /admin job, not yours.

── HALF TWO: farm life, nursery, produce — town-driven ──

Once: `python3 scripts/nearby.py --refresh`. One Overpass query for the whole region, cached.
Do NOT run it again between towns — querying per town is what got the last run throttled, and a
throttled town prints as an empty one, which hides the gaps this pass is looking for. If it says
every endpoint refused, stop and tell me.

Then walk every town in the Place menu, big ones first:

  Torquay, Geelong, Ocean Grove, Barwon Heads, Queenscliff, Drysdale, Portarlington, Lorne,
  Anglesea, Apollo Bay, then: Aireys Inlet, Armstrong Creek, Beech Forest, Bellarine, Bellbrae,
  Bells Beach, Birregurra, Breamlea, Cape Otway, Connewarre, Cumberland River, Curlewis,
  Deans Marsh, Eastern View, Fairhaven, Forrest, Freshwater Creek, Indented Head, Inverleigh,
  Jan Juc, Kennett River, Lara, Lavers Hill, Leopold, Little River, Moggs Creek, Moriac,
  Mt Duneed, Point Addis, Point Lonsdale, Skenes Creek, St Leonards, Wallington, Werribee,
  Winchelsea, Wye River, You Yangs

For each: `python3 scripts/nearby.py "<town>" --kinds=produce`, take every unlisted name as a
candidate, confirm it first-party, geocode, write. `--radius=3000` for spread-out towns; Geelong
at `--radius=4000` plus Geelong West, Newtown, Belmont, Grovedale, Waurn Ponds and South Geelong
separately. Batch, `sync.py add --dry-run`, fix, write. Log per town. Do not ask between towns.

What this group specifically needs you to judge:
  - A retail place that is a REASON TO GO — a farm store, a bookshop, a surf shop with a
    museum in it — is a `venue` carrying `produce`, not a `shop`. `shop` is the kind for a
    row that exists only so a type page has a stockist, and it takes a hand line in `BY_ID`.
    The hospitality pass's own test is the right one: is this a reason to go, or somewhere you
    happen to end up. If it is just a shop, leave it out and log the decision.
  - `farm life` is a farm you can VISIT — animals, u-pick, open gate. A farm that only sells at a
    market is `produce`, and the market gets its own row in half one.
  - `shop=convenience` is in the sweep on purpose and it is noisy: in Geelong it is servos and
    milk bars, in Kennett River it is the only shop in town. Judge by the town.
  - Season comes from the source, never from the month — strawberry picking, cherry season, olive
    harvest, mussel season. Put it in `season` and `notes`.
  - Several wineries and cafes already carry `produce` as a secondary type. Read
    `python3 scripts/have.py produce` before you search or you will list a cellar door twice.

Rules the tooling now enforces, so do not fight them: no `km` ever; no coordinate under four
decimal places; no Google Maps search url — null is the honest value when a venue has no site.

OSM tags are one contributor's opinion and the last pass proved it: a pub tagged `tourism=hotel`
and a general store tagged `shop=convenience` were both invisible to the food query. So after you
have worked a town's list, spend one look at the town itself and say in the log where OSM was
thinner than reality.

Do not stop until half one and every town in half two are done. A town with nothing is a real
answer, one command, log it and move on.

Summary at the end: market dates that disagree with their organiser (with ids), rows added per
type and per town, markets whose venue is already a `places` row, towns where OSM was thin, and
anything the 43-type vocabulary had no word for.
```

## 6 · The arts & culture

> arts 16 · cinema 13 · museum 10 · cultural 9 · art gallery 6 · theatre 1

Rewritten 28 Aug 2026, after hospitality (twice) and produce. **55 listings, the
second-thinnest group**, and `theatre 1` on a coast with the Lorne Theatre, the
Globe at Winchelsea and GPAC is the clearest single gap on the site.

Four things the earlier passes taught that change this one:

- **OSM is comparatively GOOD here** — a museum or a cinema is a landmark and
  somebody maps it — but blind to exactly what this group is short of:
  artist-run spaces, open studios, a gallery inside a cafe. The produce lesson
  in a new coat: *the map has shopfronts, not the thing you were looking for.*
- **An event needs a `place_id` or it cannot be on the map.** Twelve markets were
  written without one and none could be plotted. An exhibition with a run of
  dates is an event and hits this the same way.
- **Set `kind` explicitly.** `cultural` maps to **spot**, and a spot whose
  `location` will not parse is demoted to an **idea** — so a Wadawurrung site
  described as "along the Surf Coast Walk" silently becomes an at-home idea.
  Every other arts type maps to venue.
- **`shop` is a kind, not a type** (retired 27 Aug 2026). A gallery that sells
  is a `venue` carrying `art gallery`.

```text
First run `git pull`, then `python3 scripts/nearby.py --refresh` once — a single
Overpass query for the whole region, cached. Never run --refresh again mid-pass.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research The arts & culture group.
Also read prompts/log/hospitality.md and prompts/log/produce.md — earlier passes logged
arts candidates they left behind (the HOOP Gallery, Bellbrae Clay, Salt & Pepper Gallery at
557 Great Ocean Rd, Art Reach Studio). Start from that list.

Work the six types thinnest first: theatre (1), art gallery (6), cultural (9), museum (10),
cinema (13), arts (16). Run `python3 scripts/have.py arts` for today's real counts.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>` — read what is already there.
  2. Sweep the map: `python3 scripts/nearby.py "<town>" --kinds arts` across the towns that
     plausibly hold this type. It catches museums, galleries, cinemas, theatres, arts
     centres, public artwork and makers' studios.
  3. THEN check the town by hand. On produce, nearby.py returned ZERO for Wallington while
     Grubb Road held four real producers. Expect the same here for artist-run spaces and
     open studios — they are not landmarks and nobody maps them. The council arts pages,
     the Surf Coast Arts Trail and Geelong Arts Centre's programme are better sources than
     the map for those.
  4. Before writing any candidate, search the existing names for its distinctive word.
     nearby.py under-reports what is already listed on purpose.
  5. Build the row: first-party source, geocode, `location` ending in the suburb,
     km stays null, `kind` set explicitly.
  6. `python3 scripts/sync.py add <file> --dry-run`, fix what it says, then write for real.
  7. Append to prompts/log/arts.md — added, rejected and why, still open.
  8. Straight on to the next type. Do not ask me between types.

Specific to this group:

  - `cultural` means Wadawurrung Country and is the one type to be careful with. Take it
    ONLY from the Wadawurrung Traditional Owners Aboriginal Corporation, Parks Victoria, or
    a council page written with Traditional Owners. Do not describe a site's significance in
    your own words, do not source it from a tourism blog, and do not list a place unless the
    source says it is open to visitors. Unsure means leave it out and log it for Scott.
  - Set `kind` on every row. `cultural` classifies as a SPOT, and a spot whose location does
    not name a town gets demoted to an IDEA — which would file a Wadawurrung site under
    "things to do at home". A place with a door and hours is `kind: "venue"`.
  - `art gallery` is a room you walk into. `arts` is the thing that is ON — an exhibition, a
    trail, a workshop with a date. The gallery gets an activity row; its current show gets an
    EVENT row with starts_on, ends_on and a place_id pointing at the gallery.
  - **Every event needs a place_id.** Run `python3 scripts/have.py places` and link it. If
    there is no place row, log the venue's full address so one can be built — you cannot
    write `places` from a script. An event without a place_id is invisible on the map and
    nothing warns you.
  - `theatre` has ONE listing. Include venues that programme theatre even when they are also
    something else — a hall with a season, a cinema that stages live shows, a surf club that
    hosts a play. Lorne, Winchelsea, Geelong and Queenscliff all have rooms that qualify.
  - A cinema's url is the cinema's own site, never a booking aggregator. A Google Maps search
    link is refused by sync.py now; null is the honest value when there is no site.
  - The Surf Coast Arts Trail is why this project has a rule about dates. Any dated arts
    listing takes its date from the organiser's own page or it does not go in. `annual` and
    `monthly` never roll forward, so an annual festival needs a real published next date.
  - Public artwork from the OSM sweep (`tourism=artwork`) is a genuine answer to "what is
    there to see" and is mapped nowhere else — but only list one that is a destination, not
    every mural. Judge by whether someone would walk to it.

Do not stop until all six types have been through the loop. An empty search is a finding to
log, not a reason to stop.

When every type is done, post one summary: rows added per type, anything under `cultural` you
left out and why, events still needing a places row (with addresses), existing rows that need
correcting, and anything the 42-type vocabulary had no word for.
```

## 7 · The music

> music 73 · festival 22 · comedy 4 · party 4 — 109 rows, **106 of them events**

Rewritten 31 Aug 2026 after a survey of the places registry. **Do not research
gigs.** 106 of the 109 rows are events and they arrive by themselves twice a
week from the scrapers; a hand-entered gig goes stale the day after it happens
and the feed will import it again anyway. The work in this group is the
plumbing, and the survey found exactly where it is.

**A listing is not a places row, and 57 venues are proof.** CLAUDE.md already
records the fault in one direction — a `places` row is not a listing, so a
venue can be fully researched and invisible to readers. This is the mirror:
**86 listings could host live music and 57 of them have no `places` row and no
`place_id`, so nothing can ever be attached to them.** Klein's Anglesea Hotel,
Lorne Theatre (whose own site carries a dated live programme), Geelong Arts
Centre, Forrest Brewing, Great Ocean Road Brewing, the Inverleigh and Lara
hotels — all real rooms, all unable to hold an event.

The registry as it stands: **140 places, 32 with an `events_url` a machine can
read, 38 with a website and no feed, and 70 with nothing on file at all.**

```text
Clone the repo — do not go looking for a folder on the Mac and do not accept one
somebody suggests. It is public, so this needs no key and no token:

    git clone https://github.com/Scott-Designed/whattodo.git
    cd whattodo

Then `python3 scripts/nearby.py --refresh` once. Never run --refresh again mid-pass.

**You need no credentials and you will not write to the database.** Scott applies the
results. Do not ask for .env. This pass produces tables and a worklog, nothing else —
`places` cannot be written from a script by anyone, so that was always the shape here.

Do not push.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work The music group.

**DO NOT ADD GIGS.** 106 of this group's 109 rows are events and the scrapers bring them
in twice a week. A gig you type today is stale tomorrow and the feed will import it again
as a duplicate. Everything below is about the registry that makes the scrapers work.

You cannot write `places` from a script. Every half produces a TABLE in the worklog for
Scott to apply through /admin: name, suburb, address, website, events_url, and one line
saying what you found and why it is worth watching.

── HALF ONE: the venues already carrying gigs that nothing reads ──

These earn the most, because the events are demonstrably there.

  1. `python3 scripts/have.py places` — the `feed` / `site` / `·` column says what is on
     file for each.
  2. For every place that already carries music events but has no `events_url`, find its
     gig page. The survey found these carrying the most:
       Barwon Club Hotel   11 events, website only
       Anglesea Memorial Hall 4 events, NOTHING on file
       The Sands Torquay    3 events, NOTHING on file
       Oneday Estate        3 events, website only
     Work the whole list, not just those four.
  3. Register the ORGANISER or venue page, never a single event link. An Eventbrite `/e/`
     url dies when that night is over; the `/o/` page does not.
  4. Note which platform it is — Oztix, Humanitix, TryBooking, Eventbrite, Moshtix, or the
     venue's own listing. **Do not fetch humanitix.com**: its robots.txt permits
     `whattodo-janjuc` and disallows ClaudeBot, so that path is the scheduled Action's to
     run, not yours. Record the URL without fetching it.

── HALF TWO: the 57 listings that can never hold an event ──

86 listings carry a type that could host live music — pub, bar, brewery, winery, theatre,
music — and 57 have no `places` row and no `place_id`. A gig at any of them has nowhere
to attach, so it cannot be on the map and cannot be scraped.

  1. Get the list: pull `activities` where types include any of those and `place_id` is
     null, and check each name against `places` and its `aliases`.
  2. For each, decide honestly: **does this room actually put music on?** A winery cellar
     door that hosts two concerts a summer does; a wine bar that plays records does not.
     Read the venue's own site for a gigs, events or what's-on page.
  3. For the ones that do, produce the `places` row: name, suburb, address, website,
     events_url if it has one, and the `kind` from the place_kinds vocabulary.
  4. Where a place row already exists under a different spelling, say so — the fix is an
     alias on the existing row, not a new one. `scrape_venues.py` matches on name plus
     aliases, and that is how duplicates get recreated on the next run.

Lorne Theatre is the standing example: its masthead reads "THE OLDEST & LARGEST LIVE VENUE
ON THE SURFCOAST", the arts pass found a dated live programme on its own site, and it has
no place row at all.

── HALF THREE: venues in neither ──

  1. `python3 scripts/nearby.py "<town>" --kinds food` returns the region's pubs, bars and
     breweries. Compare against `places` rather than against listings.
  2. **71 OSM pubs have no place row.** Not all are music venues and many are outside the
     region — the cache bbox reaches Altona and Tarneit, which are not the Surf Coast.
     Judge by town first, then by whether the venue's own site shows live music.
  3. A venue with no evidence of music is not a finding. Log it and move on.

Things that are decided already and should not be re-litigated:
  - **Do not register an aggregator as a place.** `scrape_venues.py` sets `place_id` to the
    row it read from, so every event from a Coast & Bay or Fever row would be filed with the
    aggregator as its venue. That is why surfcoastevents lives in a different scraper.
  - **The organiser is not the venue.** Creative Geelong's events happen at the Makers Hub;
    Geelong Sustainability's happen in other people's rooms. Read the venue off the event.
  - A festival is `annual`, and annual never rolls forward, so any festival row needs a real
    published next date or no date at all.

Post one summary: the three tables, how many venues each half found, which platforms they
sit on, and any venue where the room and the organiser are genuinely different things —
that last one is a gap this schema still has no answer for.
```

## 8 · The community

> reading 104 · kids 88 · workshop 65 · community 32 · volunteering 12

**The group looks like 222 rows and is not what that suggests.** `reading`,
`kids` and most of `workshop` are the Geelong Regional Libraries import — one
automated feed that arrives twice a week on its own. It is handled. The real gap
is **`volunteering` at 12** and the non-library half of `community` at 32, on a
coast whose community life is Landcare, surf clubs, neighbourhood houses and
men's sheds.

**The trap here is inventing dates.** A group that meets "third Saturday" has no
published date, and working one out is the failure this project is named after.
CLAUDE.md settled it: a group earns its place as reference on its type page, not
by having a date.

```text
Clone the repo — public, no key, no token:

    git clone https://github.com/Scott-Designed/whattodo.git
    cd whattodo

Then `python3 scripts/nearby.py --refresh` once. You need no credentials and you will not
write to the database — validate with `python3 scripts/sync.py check <file>` and hand the
batches back. Do not push.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work The community group.

READ THIS BEFORE PLANNING. Of this group's rows, `reading` (104), `kids` (88) and most of
`workshop` (65) are the Geelong Regional Libraries feed. They are automated, they are
handled, and they are NOT this pass. Do not add library story times.

Work `volunteering` (12) first, then the non-library half of `community` (32).

For each:
  1. `python3 scripts/have.py <type>` — read carefully, the library rows will dominate. What
     you are looking for is what ISN'T a library.
  2. Sources: the Surf Coast Shire community directory, neighbourhood houses and community
     hubs town by town, Landcare and Coastcare groups, ANGAIR, Bellarine Catchment Network,
     men's sheds, CFA and SES brigades, Repair Café Surf Coast, U3A, toy libraries,
     playgroups, Rotary and Lions. OSM will not help with this group.
  3. Before writing, search existing names for the candidate's distinctive word.
  4. Build the row, `sync.py check`, hand back the batch. Append to prompts/log/community.md.

Specific to this group, first point first:
  - A GROUP IS NOT A ROOM AND NOT AN EVENT. Do not invent event rows for a group's working
    bee. If a group's happening goes in it must come off a first-party page with a real
    published date — never inferred from "third Saturday".
  - Set `kind: "group"` explicitly on anything you join rather than visit. Groups are held
    OFF the board by design — they are things you look up, not things the board suggests —
    and KIND_OF will classify a `volunteering · nature` row as a spot if you leave kind out.
  - A group usually has NO coordinate and that is correct. The four mountain bike clubs carry
    none: not one publishes premises. Do not pin a group at a hall it merely hires — that is
    the organiser-is-not-the-venue trap. `km` stays null always.
  - `volunteering` needs a real contact route in `url` — the group's own page or its council
    listing. Never a personal email, never an invented form.
  - `weekly` and `fortnightly` roll forward safely; `monthly` and `annual` never roll, so
    those need a real next date and will need a person again after it. Say so in notes.
  - The day of the week lives in `time_text` — "Saturdays, 8:30am–1pm" — not in the name.
  - A standing programme with no fixed date is better as an activity with the timetable in
    `notes` than an event with a date that expires.

Do not stop until both types have been through the loop.

Post one summary: rows added per type, which towns have nothing in this group, groups whose
hall is already a `places` row, and any group running real dated events worth registering
as a source.
```

## 9 · The home

> at-home 43, none pinned and none should be

**Mostly not an adding job.** These are things to do at home, not places to go —
all `km = 0`, no coordinates, and the board deliberately holds them out of the
unfiltered list because six of them once led the page ahead of anywhere you
would leave the house for. 43 is already a lot for a listings site about a
coastline, so this pass audits first and adds second, if at all.

```text
Clone the repo — public, no key, no token:

    git clone https://github.com/Scott-Designed/whattodo.git
    cd whattodo

You need no credentials and you will not write to the database. Do not push.

Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work The home group — the single type
`at-home`, 43 listings.

READ THIS FIRST. This group is a different job from the other eight and mostly is not an
adding job. More is not better here: the board holds these out of the default list on
purpose, so every weak one dilutes the group without earning a place on the page.

── HALF ONE: audit what is there. This is the real work. ──

  1. `python3 scripts/have.py at-home` and read all 43.
  2. Pull the full rows and hold each to the standard the rest of the site keeps: a real
     description, a source_note, a url that goes somewhere real. Is `location` one the page
     recognises as home — it must match "home", "backyard" or "neighbourhood", or the
     listing lands in no place at all. Is `km` actually 0 rather than null?
  3. Write the findings to prompts/log/home.md as three lists: rows that are fine, rows that
     need work and exactly what is wrong, rows you think should go and why.
  4. DO NOT propose deletions as a batch. Name them with reasons; Scott decides.

── HALF TWO: add only what is genuinely of this place, and stop early if that is little ──

  1. Look for at-home things specific to this coast rather than generic: a citizen-science
     project wanting Surf Coast observations, a Landcare planting you do in your own yard, a
     library borrow-at-home programme, something you identify at the kitchen table after a
     beach walk.
  2. Each still needs a real source and a real url or none at all. A generic craft idea with
     nothing behind it is not a listing, it is filler — and filler is what makes a reader
     stop trusting the whole list.
  3. `location` must be a home phrase, `km` is 0 (the one type where 0 is correct and null is
     wrong), `lat`/`lng` stay null.
  4. `python3 scripts/sync.py check <file>`, hand back the batch.

If half two turns up three things worth adding, add three and say so. "The region does not
have more of these" is a real answer and I would rather have it than forty invented ones.

Post one summary: the audit findings, rows added, and your recommendation on whether this
group needs any more attention at all.
```

## 4b · The hospitality, round two — depth

The first hospitality pass added 71 rows and stopped early. Two reasons, and
neither was its sourcing, which was the part that worked:

- **The prompt made town coverage the finish line.** "These eight towns should
  all be represented" got read as one-per-town, and real finds were deferred in
  writing: *"Napona / Parade Espresso (Ocean Grove), Ocean Grind (Torquay) —
  real, but the towns are already represented."*
- **It searched town names**, which cannot find a venue not named after its town.
  Love House, Skinny Legs Café, The Captain of Aireys, Anglesea Pub, Mr. T & Me,
  Onda Food House — all missed, all sitting in OpenStreetMap the whole time.
  Anglesea finished on 5 listings against 17 that OSM already had.

`scripts/nearby.py` is the fix for the second one. This prompt is the fix for the
first: the unit of work is a **town**, not a type, and the floor is per town.

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then do a depth pass on The hospitality group.
The last pass got breadth — one or two venues per town. This pass gets depth.

The unit of work is a TOWN, not a type, and the list is EVERY town in the site's Place menu —
all 47, not a shortlist of the ones with obvious main streets:

  Aireys Inlet, Anglesea, Apollo Bay, Armstrong Creek, Barwon Heads, Beech Forest,
  Bellarine, Bellbrae, Bells Beach, Birregurra, Breamlea, Cape Otway, Connewarre,
  Cumberland River, Curlewis, Deans Marsh, Drysdale, Eastern View, Fairhaven, Forrest,
  Freshwater Creek, Geelong, Indented Head, Inverleigh, Jan Juc, Kennett River, Lara,
  Lavers Hill, Leopold, Little River, Lorne, Moggs Creek, Moriac, Mt Duneed,
  Ocean Grove, Point Addis, Point Lonsdale, Portarlington, Queenscliff, Skenes Creek,
  St Leonards, Torquay, Wallington, Werribee, Winchelsea, Wye River, You Yangs

Work the big ones first — Torquay, Geelong, Anglesea, Lorne, Ocean Grove, Barwon Heads,
Queenscliff, Aireys Inlet, Apollo Bay — then the rest in the order above.

A town with nothing in it is a real answer and takes one command to establish. Log it and move
on; do not skip it unchecked. Kennett River has a kiosk, Forrest has a brewery and a bakery,
Wye River has a general store — the small ones are exactly where the site is thinnest.

Geelong is not one town. `nearby.py Geelong` at the default radius will miss most of it, so run
it at `--radius=4000` and then run Geelong West, Newtown, Belmont, Grovedale, Waurn Ponds and
South Geelong separately. They all file under Geelong on the board, but they are separate
strips on the ground.

Before the loop, once: `python3 scripts/nearby.py --refresh`. That is a single Overpass query
for the whole region, cached to scripts/osm_cache.json — after it, every town lookup is local and
instant. The 58 town centres are already cached and will be reused. Do NOT skip this and do NOT
run it again between towns: querying Overpass town by town is what got the previous run blocked,
and a throttled town reads as an empty one, which hides the exact gaps this pass is looking for.
If --refresh says every endpoint refused, stop and tell me — do not fall back to searching by
town name, that is the method this pass exists to replace.

Then the loop. For each town, in order:
  1. `python3 scripts/nearby.py "<town>"` — every food and drink place OSM knows there, split
     into what we already list and what we do not. Try `--radius=3000` for the spread-out towns.
  2. Take EVERY name under "NOT in the database" as a candidate. Do not pre-filter by whether
     the town already has listings — that is the mistake this pass exists to correct.
  3. For each candidate, find its own site or Instagram and confirm it is currently trading.
     Then geocode it and build the row. Drop it only if you cannot source it or it has closed —
     never because the town "has enough already".
  4. `nearby.py`'s match is biased towards showing things as missing, so before writing, search
     the existing names for the candidate's distinctive word. "Le Comptoir" will be reported as
     missing even though "Le Comptoir Bakehouse" is already there.
  5. Write the batch, `python3 scripts/sync.py add <file> --dry-run`, fix, then write for real.
  6. Append to prompts/log/hospitality.md under a "round two — <town>" heading.
  7. Go straight to the next town. Do not ask me between towns.

Judgement on what OSM offers:
  - `fast_food` and `ice_cream` include chains and pure takeaways. A fish and chip shop that is
    part of a town's summer is worth listing; KFC is not. Use the site's own test — is this a
    reason to go somewhere, or somewhere you happen to end up.
  - OSM labels are contributors' opinions. Check the venue's own page before you pick the type:
    the Anglesea "Pub" tag, a `restaurant` that is really a wine bar, a `cafe` that is a roaster.
  - OSM is not complete either. When you have worked its list, spend one look at the town's own
    main street — a strip that is obviously missing from OSM is worth saying so in the log.
  - Anything already listed with the wrong town, wrong type or a dead url: note it in the log
    with the id. Do not edit existing rows, that goes through /admin.

Do not stop until every town on the list has been through the loop. There is no per-type target
this time — the target is that a person who lives in each of those towns would not be able to
name three obvious places you missed.

When every town is done, post one summary: rows added per town, the towns where OSM was clearly
thinner than reality, existing rows that need correcting, and any venue worth a `places` row
with an events_url.
```
