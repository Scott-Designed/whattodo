# Nine research prompts, one per group

Copy one block into Cowork with this folder open. Each is a **loop** — it works
every type in its group without stopping to ask, and posts one summary at the
end. Run them one at a time; two at once will both add the same café.

Counts in each prompt are as at **26 Aug 2026**. They will be wrong after the
first pass, which is fine — every prompt starts by reading the real numbers with
`scripts/have.py`, so a stale figure in the prompt only sets the reading order.

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

> nature 54 · walk 32 · night 21

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The landscape group.

Work its three types thinnest first: night (21), walk (32), nature (54).
This is the best-covered group, so the target is not volume — it is filling the gaps the existing
54 nature rows leave. Read them first and work out what is missing before you search.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>` — read the existing rows and note which towns are absent.
  2. Search for what is missing. Good sources: Parks Victoria, the Great Otway National Park
     pages, the Surf Coast Walk stage descriptions, Otway waterfall and rainforest walks,
     ANGAIR, Bellarine Catchment Network, council reserve pages, Trust for Nature.
  3. First-party source, geocode, build the row, drop what you cannot source. km stays null.
  4. Batch to scratch, `sync.py add --dry-run`, fix, then write for real.
  5. Append to prompts/log/landscape.md.
  6. Straight on to the next type.

Specific to this group:
  - The line between landscape and outdoors is being in it versus doing something in it. A walk
     and a glow-worm hunt are landscape; a mountain bike trail is outdoors. CLAUDE.md says this
     is the one grouping call worth arguing with — if a listing sits badly, log the argument
     rather than quietly filing it in the other group.
  - A walk's coordinate is its **trailhead**, not the middle of the track and not the town.
    "Bells Beach" geocoding to an administrative polygon 2.6 km from the beach is the trap here;
    check the `type` Nominatim returns and reject `administrative`.
  - Put the distance and the grade of a walk in `duration` and `notes`, from the park's own
    page. Do not estimate either.
  - `night` is after dark outdoors — stargazing, glow worms, sunset points, moonrise, bioluminescence.
    Those carry real conditions: clear-sky, new-moon, full-moon, geomagnetic-storm. A dark-sky
    listing that is 100 km inland is out of the region regardless of how good the sky is.
  - Seasonal things — wildflowers, whale watching, fungi, glow worms — belong in `season` and
    `notes`, and the source has to say the season, not you.

Do not stop until all three types have been through the loop. Post one summary at the end:
rows added per type, the towns still with nothing in this group, and any grouping calls you disagreed with.
```

---

## 3 · The outdoors

> parks & playgrounds 20 · skatepark 19 · camping ground 17 · mountain biking 11 · running 9 · cycling 4 · golf 2 · rock climbing 1

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The outdoors group.

Work its eight types thinnest first: rock climbing (1), golf (2), cycling (4), running (9),
mountain biking (11), camping ground (17), skatepark (19), parks & playgrounds (20).
Target 12 rows per type, or every honest candidate if that is fewer. The first four are genuinely
thin and are where this pass earns its keep.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>`.
  2. Search for what is missing. Good sources: Surf Coast Shire and City of Greater Geelong
     recreation and facility pages, Parks Victoria, parkrun Australia, AusCycling and the
     Forrest and You Yangs trail networks, Skate Victoria, golf club sites, Bellarine Rail Trail
     and Barwon River loop pages, camping and caravan park operators, the Great Ocean Road
     hike-in campsites.
  3. First-party source, geocode, build the row. km stays null.
  4. Batch to scratch, `--dry-run`, fix, write.
  5. Append to prompts/log/outdoors.md.
  6. Next type, without asking.

Specific to this group:
  - A council facility has an address. Geocode the facility, not the town — a skatepark pinned
    at a town centre is the placeholder problem wearing a different hat.
  - `running` and `cycling` want a start line, not a region. A parkrun has a fixed start; a rail
    trail has two ends and you should pin the one with the car park and say so in notes.
  - `mountain biking` is the trail network, and the pin is the trailhead car park. `dry-trails`
    is the condition for unsealed tracks — no rain for 48h — and `dry-ground` is the one for a
    skatepark. They are deliberately different; do not use them interchangeably.
  - `rock climbing` in this region is essentially the You Yangs and whatever the Otways offer.
    If the honest answer is that there are three, add three and log that the type is small,
    rather than stretching it to indoor gyms unless the gym is genuinely in the region.
  - A camping ground needs booking information in `notes` and a real booking or park URL in
    `url` — Parks Victoria bookings, or the operator's own site. Never a fabricated one.
  - `parks & playgrounds` is the most likely place for duplicates, because a park often already
    exists in `places`. Run `python3 scripts/have.py places` before you write this type.

Do not stop until all eight types have been through the loop. Post one summary: rows added per
type, which types the region genuinely cannot fill, and any park or reserve worth a `places` row.
```

---

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

> market 13 · produce 16 · nursery 7 · shop 6 · farm life 6

Rewritten 27 Aug 2026 after the two hospitality passes. Three things they taught
that change this one:

- **OSM is the wrong net for markets.** A monthly market in a shire carpark is
  not a mapped point of interest. `nearby.py --kinds=produce` will find shops and
  farm gates and almost no markets, so markets are source-driven, not map-driven.
- **All 13 markets we hold are events, and ten are `monthly` or `annual`** — the
  two recurrences that deliberately never roll forward. They are all current
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

  1. Read the 13 we already hold: `python3 scripts/have.py market`. Ten are monthly or annual.
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

── HALF TWO: shop (6), farm life (6), nursery (7), produce (16) — town-driven ──

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
  - `shop` is the vague one and that is why it has six. Use it for shops that are a REASON TO GO
    somewhere — a farm store, a bookshop, a surf shop with a museum in it. Not retail in general.
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

> arts 15 · cinema 13 · museum 10 · cultural 9 · art gallery 6 · theatre 1

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The arts & culture group.

Work its six types thinnest first: theatre (1), art gallery (6), cultural (9), museum (10),
cinema (13), arts (15). Target 12 rows per type, or every honest candidate if fewer.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>`, and `python3 scripts/have.py places` for the venues.
  2. Search. Good sources: Geelong Arts Centre, Geelong Gallery, the National Wool Museum,
     Torquay Multi-Arts Centre and the HOOP Gallery, the Australian National Surfing Museum,
     Lorne Theatre, Winchelsea's Globe Theatre, Geelong Regional Libraries, council arts and
     public art pages, the Surf Coast Arts Trail, artist-run and cellar-door galleries.
  3. First-party source, geocode, build the row. km stays null.
  4. Batch to scratch, `--dry-run`, fix, write.
  5. Append to prompts/log/arts.md.
  6. Next type, without asking.

Specific to this group:
  - `cultural` means Wadawurrung Country, and it is the one type to be careful with. Take it
    **only** from the Wadawurrung Traditional Owners Aboriginal Corporation, Parks Victoria, or
    a council page written with Traditional Owners. Do not describe a site's significance in
    your own words, do not source it from a tourism blog, and do not list a place unless the
    source says it is open to visitors. If you are unsure, leave it out and log it for Scott.
  - `art gallery` is a room you can walk into; `arts` is the thing that is on — an exhibition, a
    trail, a workshop with a date. A gallery gets an activity row; its current show, if it has a
    real published run, gets an event row with `starts_on` and `ends_on`.
  - `theatre` has one listing. Include the venues that programme theatre even when they are also
    something else — a hall with a season, a cinema that stages live shows.
  - A cinema's `url` is the cinema's own site, not a booking aggregator.
  - The Surf Coast Arts Trail is the reason this project has a rule about dates. If you touch a
    dated arts listing, the date comes off the organiser's own page or it does not go in.

Do not stop until all six types have been through the loop. Post one summary: rows added per
type, anything under `cultural` you left out and why, and any venue worth a `places` row.
```

---

## 7 · The music

> gig 57 · festival 21 · party 4 · comedy 3

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work on The music group.

Read this part before you plan anything. `gig` already has 57 listings and they arrive by
themselves: scrape_events.py reads the Surf Coast Events feed and scrape_venues.py reads the
venues' own pages, both twice a week. **Hand-entering gigs is the wrong job** — each one goes
stale the day after it happens, and the same gig will arrive from the feed anyway and have to be
deduplicated. So this pass is mostly about the plumbing, and the loop is in two halves.

Half one — the actual bottleneck. CLAUDE.md's audit found 63 of the places have no website on
file at all, and that number, not the parsers, is what caps coverage at 15%.
  1. `python3 scripts/have.py places` — the rows with `·` have neither a site nor a feed.
  2. Loop through them, oldest towns first. For each, find the venue's real website, and its
     gig or ticketing page if it has one. Register the **organiser** page, never a single event
     link — an Eventbrite `/e/` URL dies when that night is over, the `/o/` page does not.
  3. You cannot write `places` from a script, so collect them in prompts/log/music.md as a table:
     name, place id, website, events_url, and which platform it is (Oztix, Humanitix, TryBooking,
     Eventbrite, the venue's own). Scott adds them through /admin.
  4. Do not fetch humanitix.com. Their robots.txt permits `whattodo-janjuc` but disallows
     ClaudeBot, so that path is the scheduled Action's to run, not yours.

Half two — the three thin types the scrapers do not cover: comedy (3), party (4), festival (21).
For each, in order:
  1. `python3 scripts/have.py <type>`.
  2. Search: the region's festival calendars, council event pages, venue what's-on pages,
     Visit Great Ocean Road, individual festival sites.
  3. A festival is `annual`, and annual is **never rolled forward**, so every one needs a real
     published date for its next run. No published date means no row — put it in the log
     instead. That is the Arts Trail rule and this project has already paid for breaking it.
  4. Batch to scratch, `--dry-run`, fix, write. Append to the log.
  5. Next type, without asking.

Do not stop until both halves are done — every website-less place looked at, and all three types
through the loop. Post one summary: the places table you built for /admin, rows added per type,
festivals that had no published next date, and any duplicate you spotted between the feed's
listings and the venues' own.
```

---

## 8 · The community

> community 25 · reading 9 · volunteering 7 · workshop 3

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then research listings for The community group.

Work its four types thinnest first: workshop (3), volunteering (7), reading (9), community (25).
Target 12 rows per type, or every honest candidate if fewer.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>`.
  2. Search. Good sources: the Surf Coast Shire community directory, neighbourhood houses and
     community hubs town by town, Geelong Regional Libraries programmes, Landcare and Coastcare
     groups, ANGAIR, Bellarine Catchment Network, men's sheds, CFA and SES brigades, Repair Café
     Surf Coast, U3A, toy libraries, playgroups, book clubs, Rotary and Lions.
  3. First-party source, geocode the venue, build the row. km stays null.
  4. Batch to scratch, `--dry-run`, fix, write.
  5. Append to prompts/log/community.md.
  6. Next type, without asking.

Specific to this group:
  - Nearly everything here recurs, so get the recurrence right. `weekly` and `fortnightly` roll
    forward safely — the weekday is preserved. `monthly` and `annual` do not roll, so a monthly
    group needs a real next date from the organiser and will need a person again after that.
    Say so in `notes` when you write one.
  - The day of the week has nowhere to live except the name and `time_text`. CLAUDE.md already
    lists four events carrying "– every Saturday" for this reason. Put it in `time_text`
    ("Saturdays, 8:30am–1pm") and keep it out of the name.
  - A group that meets at a hall is worth linking to that hall — check `python3 scripts/have.py places`
    and note the match in the log so the event can get a pin.
  - `volunteering` needs a real contact route in `url` — the group's own page or its council
    listing. Never a personal email, never an invented form.
  - A standing programme with no fixed date (a library's school-holiday programme, a
    neighbourhood house term timetable) is better as an activity with the timetable in `notes`
    than as an event with a date that expires.

Do not stop until all four types have been through the loop. Post one summary: rows added per
type, which towns have nothing in this group, and any group that meets somewhere already in `places`.
```

---

## 9 · The home

> at-home 43

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then work on The home group — the single type
`at-home`, which has 43 listings.

Read this first, because the shape of this group is different from the other eight. These
entries are things to do at home, not places to go. They are all `km = 0`, they have no
coordinate, and the board deliberately holds them out of the unfiltered list — six of them once
led the page ahead of anywhere you would leave the house for. So more is not automatically
better here, and 43 is already a lot.

This is a loop in two halves.

Half one — audit what is there. Volume is not the problem; quality might be.
  1. `python3 scripts/have.py at-home` and read all 43.
  2. Pull the full rows and check each one against the standard the rest of the site holds:
     does it have a real description, a source, a url that goes somewhere real? Is `location`
     one the page recognises as home — it must match "home", "backyard" or "neighbourhood", or
     the listing lands in no place at all. Is `km` actually 0 and not null?
  3. Write the findings to prompts/log/home.md as a list: the rows that are fine, the rows that
     need work and what is wrong with each, and any you think should be deleted and why.
     Do not delete anything yourself — that is Scott's call.

Half two — add only what is genuinely worth adding, and stop early if the answer is "not much".
  1. Look for at-home things that are specifically of this place rather than generic: a
     citizen-science project that wants Surf Coast observations, a Landcare planting you do in
     your own yard, a local library's borrow-at-home programme, a regional recipe or a beach
     find you identify at the kitchen table.
  2. Each one still needs a real source and a real url or none at all. A generic craft idea with
     no source behind it is not a listing, it is filler — and filler is what makes a reader stop
     trusting the whole list.
  3. Batch to scratch, `--dry-run`, fix, write. `location` must be a home phrase, `km` is 0
     (this is the one type where 0 is correct and null is wrong), `lat`/`lng` stay null.
  4. Append to the log.

Do not stop until both halves are done. If half two turns up only three things worth adding,
add three and say so — "the region does not have more of these" is a real answer and I would
rather have it than forty invented ones.

Post one summary: the audit findings, rows added, and your recommendation on whether this group
needs any more attention at all.
```

---

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
