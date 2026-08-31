# The home pass — 31 Aug 2026

Group at 43 listings, all carrying the single type `at-home`. This was an audit
first and an adding job second, as instructed. **Nothing was written to the
database.** Three rows are proposed in `/tmp/home/home-batch.json`, validated
with `sync.py check` — 0 complaints.

Headline: the group's real problem is not that it is too small or too big. It is
that **12 of the 43 are not at home** — they tell you to drive somewhere — and
because `at-home` is in their type list, `atHomeHidden()` holds every one of
them off the default board. The listing that says *"Not at home. Pick a reserve
with a free electric BBQ — Coogoorah Park, Lorne foreshore, Geelong waterfront"*
is invisible on the front page for being an at-home activity.

---

## How the audit was done

`python3 scripts/have.py at-home` for the 43, then the full rows straight off
`activities` with the anon key out of `public/notice-data.js`. `location` was
resolved by evaluating the real `suburbOf()` out of `public/notice-vocab.js`
rather than reading the regex by eye, because the question "does the page
recognise this as home" is only answerable by the function that decides it.

### Correction to the brief's premise

The brief says a location that is not a home phrase means the listing "lands in
no place at all". That is not what happens. `suburbOf()` falls through to
`NO_FIXED=/anywhere|any beach|surf coast|bellarine wide/` and returns
**`'Surf Coast wide'`**, which is a real bucket and first in `PLACE_ORDER`. So:

    Home              18
    Surf Coast wide   23
    Car                1   (207, "In the car" — the only Car row on the site)
    Jan Juc            1   (22 — a home listing on a town's place page)

Nothing lands nowhere. What actually happens is worse in a quieter way: **23 of
43 at-home listings file themselves onto the region-wide place page**, next to
beaches and walks, which is precisely where an at-home idea should not be.

### The km split, and what it does to the order

30 rows have `km = null`, 13 have `km = 0`. `sortFn` reads `(a.km??999)`, and
Closest first is the default sort. So with The home picked, the group renders as
**13 rows at the top and 30 rows at the very bottom, below every real place at
90 km, with nothing in between.** The two halves are not distinguishable by
anything a reader can see. This is the one type where the brief is right that 0
is correct and null is wrong, and it is also a direct conflict with the standing
`RESEARCH_RULES` line "Never write `km`" — worth writing the carve-out into that
file so the next pass does not have to decide it again.

---

## LIST ONE — rows that are fine

Four are clean on every count checked (home location, `km = 0`, real specific
description, `source_note` present, no url needed and none claimed):

| id | name |
|----|------|
| 201 | Make Pizza From Scratch |
| 202 | Bake Bread Together |
| 203 | Make Your Own Ice Cream |
| 205 | DIY Pub Quiz at Home |

Seven more are clean on substance and carry only the systemic `km = null`
defect listed above — they need one number each, nothing else:

| id | name | note |
|----|------|------|
| 179 | Backyard Badminton | "a shuttlecock and Surf Coast wind do not mix" is the kind of local line the rest of the site keeps |
| 184 | Slip and Slide | |
| 185 | Water Balloon Fight | |
| 186 | Nerf Battle | |
| 187 | Hide and Seek in the Neighbourhood | "Your neighbourhood" resolves to Home correctly |
| 197 | Neighbourhood Walk – Spot Something New | "Local neighbourhood" → Home; `walk` primary is right |
| 207 | 20 Questions / I Spy – Long Drive Version | resolves to Car, not Home. Honest, and the only row in that bucket — flagging rather than changing it |

The writing across the 34 `Ideas Pipeline` rows is good and should not be
touched. It is specific, it has real detail, and it avoids the generic-family-fun
register. That part of the group is working.

---

## LIST TWO — rows that need work, and exactly what is wrong

### 2a. Twelve rows are not at-home activities at all

Each of these tells the reader to leave the property, and each is held off the
default board by `atHomeHidden()` because `at-home` is in its `types`. For seven
of them `at-home` is not even the primary type — the row prints *nature* or
*arts* and is hidden anyway, because the function reads groups, not the primary.

| id | name | where its own description sends you | types |
|----|------|-------------------------------------|-------|
| 200 | Cook a BBQ Somewhere New | *"Not at home."* Coogoorah Park, Lorne foreshore, Geelong waterfront | `at-home` |
| 199 | Make a Picnic and Eat Somewhere New | "Pack whatever is in the fridge and **drive twenty minutes**" | `at-home` |
| 198 | Read Outside Somewhere New | a headland, a riverbank | `at-home` |
| 177 | Fly a Kite | "Beaches and clifftops beat parks" | `at-home` |
| 182 | Stone Skimming | Anglesea River, Barwon estuary at Barwon Heads | `at-home`, `water` |
| 183 | Build and Race Boats | a creek or a rock pool | `at-home`, `water` |
| 176 | Frisbee Golf to Natural Targets | "any patch of bush or parkland" | `at-home` |
| 189 | Nature Scavenger Hunt | heathland or beach | **`nature`**, `at-home` |
| 190 | Nature Journal Walk | beach, heathland, forest | **`nature`**, `walk`, `at-home` |
| 191 | Make a Nature Mandala | "wherever you are", left for the next person to find | **`nature`**, `at-home` |
| 193 | Cloud Watching | "in a park or on the beach" | **`nature`**, `at-home` |
| 195 | Sketch or Draw Outside | "a clifftop, the beach, a park bench" | **`nature`**, `arts`, `at-home` |

The fix is one edit each — drop `at-home` from `types` — and it is a decision
about the group's boundary, not a typo, so it is here rather than in a batch.
Doing it moves twelve real activities onto the front page and takes The home
from 43 to 31, which is the size the group probably ought to be.

Two more sit on the line and I would leave them: **192 Press Flowers and Leaves**
(you collect outside, you press at home, and the pressing is the activity) and
**194 Photography Challenge** (portable, and the description's "compare at the
end over something to eat" is the at-home half).

### 2b. Nine rows have no `source_note`

Every row the site writes gets one. These predate the rule:

    11  Karaoke Night at Home        12  Backyard Camping
    13  Movie Marathon – Theme Night 17  Board Game Evening
    20  Cook a New Recipe Together   22  Scavenger Hunt – Neighbourhood
    25  Backyard Sports Day         102  Backyard Bonfire / Fire Pit Night
                                    103  Outdoor Movie Night at Home

Seven are `added_by = 'Family'` and two `'Research'`. For the Family rows the
honest note is that they came from the household, which is a real provenance and
better than a blank. The 34 `Ideas Pipeline` rows all carry the same boilerplate
— *"Ideas Pipeline shortlist — generic activity, no venue or URL claimed."* —
which is formulaic but true and says the one thing a reader needs to know.

### 2c. Two rows have the wrong `kind`

| id | name | kind now | should be |
|----|------|----------|-----------|
| 103 | Outdoor Movie Night at Home | **`venue`** | `idea` |
| 195 | Sketch or Draw Outside | **`venue`** | `idea` |

`venue` puts both in the `place` family, which per CLAUDE.md means "can carry a
coordinate and host a Happening". Neither can. Anything that asks the family
"can this hold a pin?" gets the wrong answer for these two, and they are also
the two rows in the group that `OFF_BOARD` reasoning would treat as places.

### 2d. Two urls do not go anywhere real

| id | url | problem |
|----|-----|---------|
| 11 Karaoke Night at Home | `https://www.youtube.com/results?search_query=karaoke` | a search-results page, not a page about anything. This is the same category as the `maps.app.goo.gl` and Google-Maps-search links the project is already clearing out — a url shaped like a citation that cites nothing. Null is the honest value. |
| 22 Scavenger Hunt – Neighbourhood | `https://www.geocaching.com` | points at a different activity from the one described ("write your own list"); geocaching is mentioned as an aside |

The third url in the group is good and should stay: **102 Backyard Bonfire**
links to the VicEmergency fire danger ratings page, which is the exact thing a
reader needs before lighting anything, and is a first-party government source.

### 2e. One row files itself onto a town page

**22 Scavenger Hunt – Neighbourhood**, `location = 'Jan Juc'`, resolves to the
Jan Juc place page. An at-home idea listed among Jan Juc's beaches and cafes.
`'Your neighbourhood'` (as 187 uses) would fix it — see List Three, where I
think this row should go instead.

### 2f. The mirror problem — 16 `idea` rows outside The home

`kind = 'idea'` is 57 rows; only 41 of them carry `at-home`. The other 16 are
at-home-shaped things filed under `nature`, `night` and `cultural`, so they are
**not** held off the board and **not** in the group:

    86 Milky Way Stargazing · 87 Aurora Australis Chase · 88 Bioluminescence
    95 Moonrise Watch · 104 Meteor Shower Watching · 105 ISS Spotting
    106 Planet Watching · 151 Hooded Plover Spotting · 154 Wadawurrung Country
    158 iNaturalist · 159 Aussie Backyard Bird Count · 160 eBird & Birdata
    161 WhaleFace & Two Bays · 165 Redmap · 181 Sandcastle Competition
    196 Sunrise Beach Walk

Most of these are correctly outside the group. But **159 Aussie Backyard Bird
Count** has `location = 'Anywhere – your backyard or local patch'`, which hits
the `backyard` branch of `AT_HOME` and files under **Home** — so it prints on
the Home place page while sitting in The landscape group. One row, two answers.

This matters for half two, below: the citizen-science layer the brief asked me
to go looking for **is already in the database**. It is just filed under
`nature`.

---

## LIST THREE — rows I think should go

Named individually with reasons, not proposed as a batch. Four rows out of 43,
and I would not press hard on any of them except the first.

**174 Carpark Cricket** — 173 Backyard / Beach Cricket already says "Grass, sand
or a quiet cul-de-sac". 174 says "a quiet carpark, a cul-de-sac or a campsite
loop". Same game, same equipment, one description is a subset of the other, and
the weaker surface got its own listing. 173 is rated 5 and 174 is rated 3, which
suggests whoever wrote them knew. Merge the carpark line into 173 and drop 174.

**206 Digital Detox Afternoon** — it is the absence of an activity. Its own
description names the fallback: "cards, a board game, a walk" — all three
already listed (17, 197, and the group generally). A listings site that answers
"what shall we do" with "nothing, deliberately" is fine as a sentence in an
About page and thin as a row.

**180 Hacky Sack / Juggling** — nothing of this place, nothing a reader could not
have reached alone, no source beyond the shortlist boilerplate, rated 3. It is
the clearest example of the filler the brief warns about: it does not make the
list wrong, it makes it longer.

**22 Scavenger Hunt – Neighbourhood** — the weakest of three overlapping hunts
(188 Treasure Hunt, 189 Nature Scavenger Hunt), with the shortest description,
no `source_note`, a url pointing at a different activity, and a `location` that
files it under Jan Juc. 188 covers "works at home, around the neighbourhood, at
a campsite or along a beach" and 189 covers the nature version. If it stays, it
needs four separate fixes; if it goes, nothing is lost.

**Not proposed for removal, though I looked at them:** 13 Movie Marathon vs 103
Outdoor Movie Night (genuinely different — indoors on a wet day vs a projector
in the backyard in summer); 12 Backyard Camping vs 102 Backyard Bonfire (the
tent is the point of one, the fire of the other); 25 Backyard Sports Day (a
container for other activities, but the stations give it a real shape).

---

## HALF TWO — what was searched, and what is worth adding

### The finding that shortened this half

The brief's own examples — "a citizen-science project wanting Surf Coast
observations" — are **already in the database**, six of them, all with real
first-party urls, all `kind = 'idea'`, none carrying `at-home`:

    158 iNaturalist – Record Local Biodiversity   159 Aussie Backyard Bird Count
    160 eBird & Birdata – Bird Surveys            161 WhaleFace & Two Bays Whale Project
    165 Redmap – Report Unusual Marine Species    151 Hooded Plover Spotting

So the citizen-science seam is worked out. I checked **Redmap** (real, Victoria
region page, already row 165), **FrogID**, **Wild Pollinator Count** and
**ClimateWatch** — all national platforms with no Surf Coast hook the six above
do not already give, and adding a national app because it technically works here
is the definition of filler. I also checked **Tangaroa Blue / Australian Marine
Debris Initiative** — real, and you do enter the data at home after a beach
clean — and rejected it as an at-home listing because the activity is the beach
clean; it belongs in The community or The ocean if it goes anywhere, and it is
worth someone's time there.

**Gardens for Wildlife** exists at Cardinia, Mornington Peninsula and elsewhere;
I could find no Surf Coast Shire or City of Greater Geelong program of that name.
Surf Coast Shire publishes an indigenous planting guide (a 2003 PDF for rural
areas) and runs community gardens, neither of which is a backyard at-home
listing. If Scott knows of a G4W equivalent here I did not find it.

**GRLC Home Library Service** is real (delivery to your door) and I rejected it:
it is an access service for people who cannot get to a library, not a thing to
do on a Saturday. Its page returned 403 to a fetch as well, so I could not read
the eligibility terms first-hand.

### Three rows worth adding

All three are things you do at your own kitchen table or in your own garden, all
three are free, all three have a first-party url, and all three are specific to
this coast in a way the existing 43 mostly are not — two are Surf Coast library
programmes and one is an Anglesea-district reference nobody else publishes.

**1 · Seed Library — Borrow Seeds, Grow Them at Home**
Geelong Regional Libraries. Borrow up to three seed packets free, grow them,
donate seed back when the plants mature. **Torquay is one of seven permanent
branches** (with Bannockburn, Biyal-a Armstrong Creek, Colac, Boronggook
Drysdale, Newcomb and Ocean Grove); a roving box visited Corio and Belmont
March–May 2026. `https://www.grlc.vic.gov.au/seed-library`
Duplicate check: `ilike '%seed%'` returns only 438, a one-off Bannockburn
library event. No standing listing.

**2 · Library of Things — Borrow a Projector, a Bird Kit or a Podcast Rig**
Also GRLC, free with membership. The collection is a mobile podcasting kit,
three digital film scanners, an air quality detector, a portable projector, a
home energy efficiency kit, thermal imaging cameras, a C-PEN reader and a bird
watching kit. Launched 11 Nov 2024. This one also retires bad advice sitting in
an existing row: **103 Outdoor Movie Night at Home** currently tells readers
"budget projectors from ~$80 on Amazon", and the answer on this coast is that
their library lends one. The bird watching kit pairs with row 159.
`https://www.grlc.vic.gov.au/news/library-things-borrow-more-just-books`
GRLC publishes no standalone Library of Things page — items are catalogued
individually — so the url is their own announcement page, which is first-party.
Duplicate check: `ilike '%things%'` returns 0.

**3 · Identify What You Found — ANGAIR's Knowledge Bank**
Free, browsable lists for flowers, orchids, birds, mammals, reptiles,
butterflies, fungi and weeds, **every one of them scoped to the Anglesea and
Aireys Inlet district** rather than to Victoria, plus downloadable factsheets
from the member newsletter. This is the brief's own example — the thing you
identify at the kitchen table after a beach walk — and it exists, locally
compiled, and is not listed. `https://angair.org.au/knowledge-bank/`
Duplicate check: ANGAIR has three rows already — 138 Plant Propagation Centre
(`venue`), 125 Working Bees (`group`), 30 Wildflower & Art Weekend
(`happening`). This is a fourth ANGAIR appearance and I think a legitimately
different thing: the at-home reference, not the organisation, the nursery or the
show. **Worth Scott's eye** — if four rows for one small society reads as too
many, this is the one to drop, and I would not argue.
I gave it `types: ["at-home","nature"]` so it also reaches `/nature` and The
landscape, where someone would actually look for it. Note that this contradicts
nothing in List 2a: those twelve rows are outdoor activities wrongly carrying
`at-home`, this is an at-home activity legitimately carrying `nature`.

### What I did not add, and why not more

That is three, and I stopped. The region does not have a fourth. Everything else
I turned up was either already in the database under a different type, a national
platform with no local hook, or a service rather than an activity. The group is
already 43 rows for a coastline, twelve of them not even at home; adding to it
before the audit above is applied would make a worse list, not a bigger one.

---

## Recommendation on whether this group needs more attention

**Not more listings. One structural decision and about twenty small edits.**

In the order I would do them:

1. **Decide the boundary** — drop `at-home` from the twelve rows in List 2a.
   One decision, twelve edits, and it moves twelve real activities onto the
   front page. This is the whole pass in one step.
2. **`km = 0` on the 30 nulls**, so the group stops rendering in two halves at
   opposite ends of the list, and write the carve-out into `RESEARCH_RULES.md`
   beside "Never write `km`" so the next pass does not re-litigate it.
3. **`location` to a home phrase** on the rows that survive step 1 and still say
   "Anywhere ...", so they stop filing under Surf Coast wide.
4. **`kind = 'idea'`** on 103 and 195.
5. **Null the two urls**, add the nine missing `source_notes`, decide the four
   in List Three.
6. Then, and only then, the three rows in the batch.

Two things worth writing into CLAUDE.md when the above is done, because both are
conventions and not entries:

- **`atHomeHidden()` reads groups, not the primary type**, so any row carrying
  `at-home` anywhere in its list is off the default board even when it prints as
  *nature*. That is the mechanism behind List 2a and it is not documented.
- **`km = 0` is required on `at-home`** and is the one exception to "never write
  `km`", because `sortFn` reads `(a.km??999)` and a null sends the row below
  every real place on the default sort.

`kind = 'idea'` already says everything `at-home` is being asked to say, and
says it on a column that cannot be a list. When the four kind filters land,
**At home = Idea** should replace `atHomeHidden()`, and the twelve rows in List
2a resolve themselves: they are `idea` rows about outdoor places, and they stop
being a type problem.

---

## Batch

`/tmp/home/home-batch.json` — 3 rows, `sync.py check` clean, no credentials
used, nothing written.
