# WhatToDo Jan Juc — working notes

A community listings site for Jan Juc and the Surf Coast, Victoria. Live at
**https://notice.place** (Vercel project `whattodo`; the
`whattodo-nu.vercel.app` address still resolves and is the deploy's own URL).

**The site is called `Notice`** (renamed 24 Aug 2026; it was "What to do"), and
the listing area is the **Notice Board**, which is where its count lives —
"Notice Board · 395 things pinned". The repo, the Vercel project, the URL and
this file keep the old name: renaming those buys nothing and breaks the deploy
hook. So `whattodo` is the project and `Notice` is the product.

## Shape of it

```
public/index.html     the board — one file, no build step, no framework.
                      Serves TWO paths: / is Everything, /noticeboard is
                      what's on. Same rows, one extra condition in ok().
public/about.html     what this is, and what it will not do
public/place.html     a town: what's on there, and what's there anyway
public/type.html      one kind of thing, everywhere it is, grouped by town
public/nav.js         the bar across all four, and its two menus
public/notice-nav.css  ·  notice-page.css  ·  notice-page.js   the shared chrome
public/notice-vocab.js  suburbOf, typesOf, nextDate — lifted out of index.html
public/notice-data.js   the Supabase keys and fromRow — configure.py writes here
public/admin.html     back of house: the automations, every listing, and an editor
public/sunset.css     the Sunset face, so admin.html can wear it too
api/enrich.mjs        Vercel function: Claude drafts missing fields, user approves
                      Takes a name OR a url. Events lead with the url.
api/admin.mjs         Vercel function: the only write path from a browser.
                      Holds the service key; needs ADMIN_PASSWORD.
api/subject.mjs       Vercel function: serves /<slug> — /anglesea, /surfing —
                      with its title and description already in the HTML.
supabase/             schema, seed data, setup SQL
scripts/              configure.py (keys into notice-data.js), sync.py (seed/export/moderate),
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

- **42 types, and a listing carries a list of them.** `activities.types` and
  `events.types` are `text[]`, checked by `types_valid()` against the `types`
  table — the `conditions` and `offers` pattern, used a third time. **The first
  element is the primary**: the word the row prints, the icon it draws, the
  colour it tints. An empty list means "not sorted yet" and shows as *unsorted*.
  See `supabase/TYPES_MULTI.sql` for the migration and `scripts/retype.py` for
  the 169 per-row decisions that followed it.

  Adding a type means **five** places: a row in `types` (with its `band`),
  `GROUP_OF` in `notice-vocab.js` or it belongs to no group, `TYPE_PLURAL` in
  the same file or its page heading prints the raw column value,
  `TYPES_PLACE`/`TYPES_EVENT` in `api/enrich.mjs`, and `PLACE_TYPES`/`EVENT_TYPES`
  in `notice-vocab.js` for the Add form. `supabase/schema.sql` is a historical
  seed and is **not** one of them any more — `TYPES_MULTI.sql` supersedes it.

  **Removing one is the same five in reverse, rows first.** `types_valid()` is
  a live check, so a vocabulary row cannot be deleted while any listing still
  carries it — strip every row, confirm none is left with an empty list, then
  delete. `shop` came out that way on 27 Aug 2026; see below.

  `brewery` was added 26 Aug 2026, because filing Blackman's as a cafe or a bar
  loses the reason anyone goes. `cidery` and `distillery` exist in `place_kinds`
  and are still not types; Flying Brick and The Whiskery are `bar` + `produce`.
- **Nine groups**, in `GROUPS`/`GROUP_OF` in `notice-vocab.js` — The ocean, The
  landscape, The outdoors, The hospitality, The produce, The arts & culture, The
  music, The community, The home. Every type is in exactly one, so a new type has
  one obvious home. They are the first filter and they set the row's hover tint,
  so the colour down the list and the word in the dropdown say the same thing.

  **The group counts do not sum to the number of listings, and that is not a
  fault.** 69 rows carry types from more than one group: Bells Beach Surf Film
  Festival is `festival · surfing · cinema`, so it is in The music, The ocean and
  The arts & culture at once. 494 across nine groups, 419 rows.
- **The Type menu leaves out what it cannot offer** rather than greying it. It was
  greyed while the menu was short — a grey row said "not with these filters"
  without lying — but that does not survive 42 types, where picking The ocean left
  38 dead entries to read past. Anything already ticked stays whatever its count,
  or it could not be unticked.
- **With a group picked, the Type menu is that group's own types and nothing
  else.** The first version showed every type still capable of narrowing the
  list, which is a defensible answer to a different question and read as a bug:
  The arts & culture offered `surfing`, because Bells Beach Surf Film Festival is
  `festival · surfing · cinema` and therefore lands in three groups. True, and no
  help. The first filter teaches the shape of the site, so the menu under it has
  to be the fixed list that belongs to it. The film festival is still found by
  surfing under The ocean, which is where anyone would look.
- The **At home** group is hidden from the unfiltered list. Those entries are all
  `km = 0`, so under the default Closest first sort six of them led the page ahead
  of anywhere you would leave the house for. Picking The home or typing a search
  still finds them, and the tally says how many are held back. See
  `atHomeHidden()`.
- **14 condition tags**, checked by `conditions_valid()`. Thirteen are gates;
  `good-in-rain` is a boost — it never hides anything, it promotes on a wet day.
- `dry-trails` = no rain for 48h (MTB, unsealed tracks). `dry-ground` = not raining
  right now (skateparks, markets, picnics). These are deliberately separate.
- Community additions land `verified = false`. RLS refuses any insert that sets
  `verified = true` or `added_by = 'Research'` — a submission cannot dress itself up
  as researched data.

## Six kinds of listing — COLUMN BUILT AND EVERYTHING CLASSIFIED 27 Aug 2026

Decided with Scott over a long session on 27 Aug 2026, after reading all 585
rows, then applied the same day.

**What is done:** `supabase/KINDS.sql` (the `kinds` table, `activities.kind`,
and `listings` carrying `kind` + `family`), and `scripts/classify_kinds.py`,
which classified all 438 undated rows.

**What is deliberately NOT done:** the reader-facing filters still say what they
said yesterday — Scott asked for the recategorisation without the dropdown
change. And `places` has not been merged into the listings tables, which is the
destructive half and the one that fixes the 32 duplicates.

    venue 215   spot 145   idea 57   group 21   happening 150   shop 0   maker 0

Shop and maker being empty is correct, not a bug: they are what Scott is about
to add, and the kinds exist so there is somewhere for them to go.

### Why the current split is wrong

`activities` vs `events` is not *activity vs place*. It is **undated vs dated**,
and the name came off the seed spreadsheet. So one table holds Bells Beach,
Anglesea Bakery, a surf school and Backyard Cricket, which have nothing in
common. The columns have been saying so for months:

- `place` is filled on **97%** of events and **0%** of activities — the `places`
  table only ever served events.
- `km` is on **98%** of outdoor rows and **17%** of hospitality — nobody
  measures the drive to a bakery.
- The 62 at-home rows have a coordinate **2%** of the time. They were never
  places, and `atHomeHidden()` is a patch over that.
- **32 things exist in both `activities` and `places`** — Bells Beach, Torquay
  Hotel, Aireys Pub. Three disagree about where they are: Blackman's Brewery by
  999 m, Last One Inn by 391 m, Point Roadknight Beach by 357 m. Anglesea Main
  Beach has a pin as a place and none as a listing.

### The six

`kind` is one value on the row, `family` comes off the `kinds` table, and
`types` stays a list on top of both. **`family` is what a kind can DO** — a
`place` can carry a coordinate and host a happening, `people` may have neither
— so anything asking "can this hold a pin?" asks the family rather than
keeping its own list of kind names in step.

**Shop was briefly a boolean flag on venue and is now a kind.** Both were
tried, in that order, on the same day. As a kind it costs nothing extra —
shop and venue share every property because both are in the `place` family —
and it means anything separating shops out reads one column instead of
inspecting a list of types.

**`place`** — an address, a pin, and can host a Happening.

- **spot** (145) — no door, no hours, nobody owns it. *Bells Beach, Jan Juc
  Skatepark, Erskine Falls Walk.*
- **venue** (215) — a door, hours, a price. **Bakeries are venues**, decided
  explicitly: a bakery you can sit outside is a cafe that sells bread.
  *Torquay Hotel, Surf World Museum, Anglesea Bakery.*
- **shop** (0) — a door, hours, and it is here so a type page has somewhere to
  buy the gear. *A surf shop on `/surfing`.*

**`people`** — a contact, and possibly no address at all.

- **group** (21) — you join in. *Torquay Landcare, Anglesea Movie Club,
  Nippers.* Scott is building this out, which is why it is a kind.
- **maker** (0) — you buy from them. *A shaper in his garage, a jeweller
  at a market.*

**`time` — happening** (150) — it has a date, and it points at a Place. Events
are always this, so the view carries a literal rather than a column: there is
no such thing as an event without a date, and a column would be a value free to
drift away from a fact.

**`idea` — idea** (57) — no anchor of any kind. *Backyard Cricket, Cloud
Watching.*

### What the reader sees

**NOT BUILT — the dropdowns still say what they said yesterday.** Scott asked
for the recategorisation without the filter change, so this is the next step and
not a description of the page. Four filters on the Notice Board:

    Go somewhere   Spot + Venue
    What's on      Happening
    At home        Idea

**Group came off the board 27 Aug 2026**, with Shop and Maker. What belongs on
a list answering "what shall we do on Saturday" is the group's HAPPENING, not
the group: Torquay Landcare is not a plan, its working bee is. So there is no
"Join in" filter — three kinds are on the board and three are not.

**Shop, Maker and Group are held off the board TODAY, by `OFF_BOARD` in
index.html**,
because the rows exist and the filters do not. That was a real gap for about an
hour: Patagonia and Shyama Buttonshaw were added, and both walked straight onto
the Notice Board, because `ok()` filtered on types and had never heard of
`kind`. Adding a kind whose whole point is being off the board, while the thing
that would keep it off is unbuilt, is the shape of mistake to watch for here.

When the four filters land, `OFF_BOARD` should become a case of the filter
rather than a rule sitting beside it — and `atHomeHidden()` goes the same way.

**Shop and Maker are in none of them, and that is the mechanism.** An earlier
draft had an `on_board` flag to hold shops back; splitting Shop out killed it.
A row is off the board by *being* a Shop, so there is nothing to remember when
adding one and no rule that can be broken.

The awkward case resolves itself too: **Great Ocean Road Chocolaterie is a
Venue**, not a Shop, because people drive there for its own sake. If you would
go for the thing itself it is a Venue; if it exists so a type page has a
stockist it is a Shop. The kind is the decision, made once, at creation.

**The reader never sees the word "venue".** Kind is plumbing — it decides what
fields a row needs and how it renders. The word on screen comes from `types`,
so a surf shop's row says *shop* and a cafe's says *cafe*. This was Scott's
point and it is the reason `kind` and `types` are both needed: nobody is ever
told a surf shop is a venue, because nothing ever says it.

### The nurseries, and what `community` cannot decide

Taking Group off the board immediately exposed that seven of the 22 groups were
not groups: **every plant nursery**. `nursery` mapped to `group` in the first
pass, which put Nick's Natives and the Otways Indigenous Nursery in with
Landcare and the working bees. A nursery has a door, hours and a till — being
run by volunteers does not stop a thing being a place you go to. `nursery` is a
**venue** now, and `Geelong Library & Heritage Centre – The Dome` moved with
them, by hand: `community` makes a group, which is right for a Landcare branch
and wrong for a reading room.

That leaves 14 groups, and **only one has a happening attached** — Gather
Athletics has its Saturday run. **That is fine and is not a backlog**, decided
by Scott 27 Aug 2026: a group earns its place as reference on the type page it
belongs to, not by having a date. Somebody reading `/volunteering` wants to know
Torquay Landcare and the Jan Juc Coast Action working bees exist and how to
reach them; whether either has a published date this month is a different
question. All three off-board kinds work the same way — Shop, Maker and Group
are things you look up, not things the board suggests.

So do NOT go and invent event rows for the 13. If a group's happening is ever
added it must come off a first-party page with a real date, never inferred from
"third Saturday" — that is the failure this file opens with.

`Anglesea Resale Shed (Tip Shop)` is a **shop** — Scott, 27 Aug 2026, settling
the Chocolaterie question for this row: it sells things, so it is a shop, and
the fact that people enjoy browsing it does not make it an outing. It gained
`shop` as a type at the same time, or being `community` alone would have put it
on `/community` and nowhere a person hunting for second-hand goods would look.

**That second half no longer holds — `shop` was retired as a type later the
same day** (see below), so this row is `community` alone and is found by its
kind rather than by a type page. The worry it records is still the real one:
the Tip Shed is the row with the weakest type, and if anything ever hides it,
it will be this one.

### `shop` is a kind and NOT a type — retired 27 Aug 2026

Scott's call, the day after the kind landed, on noticing a new row filed as
`shop · running`. **It was a second copy of a fact the row already carried.**

The ten rows holding it split cleanly, and the split is the whole argument:

- **Three were `kind = shop` AND `types = {shop, …}`** — Patagonia, The Running
  Company, the Tip Shed. One fact, two columns. On The Running Company `shop`
  was also the **primary**, so the row printed *shop* — the least informative
  word available — where `running` is the thing separating it from Patagonia.
- **Seven were `kind = venue` with `shop` in their types** — the four general
  stores, the Chocolaterie, Bellarine Wholefoods, Bellbrae Clay. There it meant
  *this venue also sells goods*, which the kind genuinely does not say.

That second group is what the retirement costs, and it is worth being honest
about: **there is now nowhere to record that a venue sells things.** If it is
wanted back it belongs in `places.offers` as a `retail` value — the column for
what a place DOES, not what it IS — and not in `types`, where it was competing
with `cafe` and `produce` for the one slot that prints.

Nothing was lost from the rows themselves. Each kept its other types and prints
a better word than before: the general stores say *cafe*, the Chocolaterie and
Bellarine Wholefoods say *produce*, the Tip Shed says *community*.
`supabase/SHOP_TYPE_RETIRED.sql` is the record, with the ten before-and-afters.

**The sharp edge: a shop can no longer be INFERRED, and that is permanent.**
`KIND_OF` in `classify_kinds.py` now has nothing mapping to the shop kind, and
`PRECEDENCE`'s `shop` entry is unreachable. All three shops carry activity types
— surfing, running, community — which are things you go and DO, so the rules
make them **spots**. They survive only because they are hand decisions in
`BY_ID`, and `--reclassify` would flatten any shop that is not listed there.

So **adding a shop means adding a line to `BY_ID`**, with the reason. There is
no rule that will work it out, by design: the type used to say it, and saying it
twice is exactly what got the type retired. 463 was added to `BY_ID` in the same
commit, which is how this was caught — the classifier's dry run reported it as a
disagreement the moment the type went.

`/shop` now 404s, which is correct: it was a page listing things the Kind menu
already gathers.

### How 438 rows were classified

`scripts/classify_kinds.py` — dry run by default, `--write` to apply,
`--show venue` to read one kind in full. Three things decide a kind, in order:

1. **A hand decision in `BY_ID`.** There is exactly one.
2. **`types`.** `KIND_OF` is exhaustive over all 42 types, and the script
   **exits** if the database has a type the map has never heard of, rather than
   defaulting it to venue. A row with several types is resolved by
   `PRECEDENCE` — `idea < group < maker < shop < spot < venue`, weakest first —
   so `bakery · cafe` is a venue and `farm life · cafe · produce` is a venue.
3. **Nothing else, and in particular never the name.** Scott's rule.

Then **one correction, and it is the only thing that reads a column other than
`types`: a spot with no anchor is an idea.** `night` and `nature` say what a row
is *about*, not whether it is anywhere, so "Milky Way Stargazing" and "Jan Juc
Skatepark" arrive identical — both spots, both unpinned. `location` separates
them, and `suburbOf` is what reads it:

    Jan Juc Skatepark      "Jan Juc"                   -> a town  -> spot
    Milky Way Stargazing   "Several Surf Coast beaches" -> nowhere -> idea

**`suburbOf` is evaluated through node out of `public/notice-vocab.js`, not
reimplemented in Python.** Same trick as `.claude/launch.json`. A second copy
would disagree with the site eventually, which is the failure this project has
already paid for twice. It fired on 26 rows, every one of them right — Cloud
Watching at "Anywhere outdoors", Sandcastle Competition at "Any beach".

The correction only ever **demotes a spot**. A venue, shop, group or maker keeps
its kind whatever `location` says, because a door and a contact do not stop
existing when a location string fails to parse.

**The one hand decision is `Nippers` (289).** It is `community · swimming ·
beach`, so spot beats group on precedence and then the correction demotes it to
an idea — both steps right in general, both wrong here. It is run by the surf
clubs and you enrol a child in it, so it is a group. Left in `BY_ID` rather than
reordering `PRECEDENCE`, because it is **the only row in 438 carrying both a
group type and a spot type**; a rule change would be fitted to one row.

**`--write` only fills rows that have no kind.** A row that already has one
was either set by the first run or set by a person afterwards, and the script
cannot tell those apart — so re-running it must never quietly undo a decision.
This is not hypothetical: on the day it was added, a plain re-run would have
turned `Shyama Buttonshaw Designs` from a maker and `Patagonia Torquay` from a
shop into spots, because both carry activity types that outrank their kind on
`PRECEDENCE`. Disagreements are printed every run either way, so nothing is
hidden; `--reclassify` is how you apply them.

**56 rows have a kind and a coordinate that disagree** — a spot with no pin, or
an idea carrying one. That is a data job, not a kind job: the spots need
geocoding and the ideas need their pin removed. The script lists them every run.

### Rules that come with it

- **Anything with a door defaults to Venue.** Moving a row out of Venue needs
  research, never a word in its name. A first-pass classifier filed *Barwon Club
  Hotel* and *Workers Club Geelong* as Groups because their names say "Club",
  and reported it as a decision — the same failure mode this file records from
  the hospitality pass.
- **`types` stays a list, and that is what puts a surf shop on `/surfing`.**
  Multi-type already works: *Bells Beach Surf Film Festival* is
  `festival · surfing · cinema` today. (*Wye River General Store* was the
  example here until `shop` was retired as a type — it is `cafe` now.)
- **A Maker gets a pin only if they publish a visitable address themselves.**
  Not an ABN record, not an Instagram geotag, not a search result. A maker
  working from home has a home address and it is findable, so a research pass
  *will* find it and *will* report finding it as a success. This has to be
  enforced in `check()` on both write paths, not left in prose.
- **Makers appear at Happenings** rather than hosting them — the market stall.
  No other kind has that relationship, and it is the most useful thing a maker
  row can say: not "here is a jeweller" but "here is a jeweller, and she is at
  the Aireys Inlet Market on the third Sunday."

### `kind` is a loaded word — it means two things

**On `activities` it is the listing kind** (spot, venue, shop, group, maker,
idea). **On `places` it is the place taxonomy** (pub, hall, beach) and always
was. Same word, two vocabularies, and either would silently accept the other's
values. Both write paths now dispatch on the table before checking.

**`sync.py`'s `kind` used to mean a third thing** — which table to write to,
taking `'place'` or `'event'` — and it *popped the field before inserting*. So
the moment the real column existed, `kind: 'maker'` was accepted, dropped, and
written as an activity with no kind and no error. It is fixed: `kind` is the
listing kind and gets written, both old values are refused **by name** with a
message saying what to write instead, and which table a row goes to is derived
from whether it carries a date rather than declared. `events` has no `kind`
column — there is no such thing as an event without a date — so the router pops
it there and only there.

The Maker address rule is enforced on both paths now, as far as code can:
**a maker with a coordinate must carry a `source_note` in the same write.**
Code cannot tell a self-published address from one dug out of an ABN record, so
it insists the author writes down which it is and leaves a person to read it.
`/admin` only fires this when the edit actually touches the kind or the
coordinate, because that editor sends only what changed.

### Still open

- How you reach a Maker: open studio, market stall, or online only. Three
  different sets of fields.
- ~~Whether Shop and Maker appear on town pages.~~ **Decided 27 Aug 2026: yes,
  in their own "Shops & makers" section.** Not under "Places to go" — a shop is
  not somewhere to go on a Saturday and a maker is not a place at all, which is
  the same reason they are off the board. Still worth knowing about in a town
  you are already in.
- Whether the type page grows a third section (*Shops*) under What's on and
  Places to go. The heading is a design decision: "Where to buy" breaks as soon
  as a shop also hires or repairs.

### The first Shop — WRITTEN 27 Aug 2026, activity 460

**Place 99 is now a monitored source** (27 Aug 2026, Scott's request): its
`website` and `events_url` are both the store page. It reads nothing today and
the run says so — *"Patagonia Torquay — nothing machine-readable"* — because the
site is a JS-rendered Shopify storefront and a plain fetch gets nav chrome, no
JSON-LD and no dates. That is the point of registering it anyway: every run now
checks it, and it appears on the back-of-house source list where a dead source
is visible rather than forgotten.

**The store page's own "Local Events" section is empty**, and that is why
registering the source found nothing — checked in a real browser 27 Aug 2026,
the heading is there and its container is 34px tall with nothing in it. So the
store page is worth watching but has never yet listed anything.

**Patagonia's Torquay events are published somewhere else entirely.** The first
one, `Roaring Journals Happy Hour` (event 154, 17 Sep 2026), lives at
`torquayhappyhour.splashthat.com` — a Splash page linked from nowhere the
scraper can reach. **That domain must never go in `events_url`**: splashthat.com
sits behind DataDome and serves a captcha page instead of a robots.txt, so
`eventlib.robots_ok` returns False and a scheduled run would be bot-blocked. It
was read once in a browser, by hand, because Scott sent the link.

The lesson for this shop: its events will keep arriving as one-off links from a
person, not from a feed. Registering the store page is still right — it costs
nothing and catches the day they start publishing — but do not expect it to work.

**`patagonia.com.au/pages/events` exists and was deliberately NOT used.** It is
a national list, so attaching it to the Torquay row would file a Sydney event in
Torquay — the same organiser-is-not-the-venue mistake this file records for
Creative Geelong. A store's own page is the only URL that can honestly be
attributed to that store.

The link Scott sent carried a `?srsltid=` Google click-tracking parameter. It is
stored clean; a tracking parameter changes between visits, so keeping one would
mean every run compares against a slightly different address.

**Patagonia Torquay**, 116 Surf Coast Highway — patagonia.com.au/pages/torquay-store
Types `surfing · mountain biking · rock climbing · running`, taken from
the categories the store's own page lists. Worth a look if a type page starts
feeling padded: five types puts one shop on five pages, and whether that is
useful or noisy is a judgement nobody has made yet.

**It carries no coordinate of its own.** `place_id = 99` — the `places` row for
Patagonia already existed, already geocoded building-level, already used by an
event. The `listings` view coalesces own-first, place-second, so the pin arrives
without a second copy that could drift. **This was the first activity in the
database to use `place_id`; the other 438 all carry their own lat/lng**, which
is how 32 things ended up existing in both tables with three of them
disagreeing. Anything that already has a place row should be linked, not
duplicated — `Gather Athletics` (461) is the second, linked to place 84.

### The first Maker — WRITTEN 27 Aug 2026, activity 459

**Shyama Buttonshaw Designs** — surfboard shaper, Bells Beach.
https://www.shyamabuttonshaw.com · @shyamabuttonshawdesigns ·
YouTube @shyama_buttonshaw_designs · shyama.buttonshaw@gmail.com · 0434 559 960

Custom shapes — shortboards, fishes, mid-lengths, logs, and the gliders he is
known for (mini gliders 6'10"–8'3", full gliders 9'0"–12'). Son of surfer-artist
Simon Buttonshaw and shaped under Wayne Lynch's influence. Stocked by Wild
Things Gallery (Byron), Pilgrim Surf Supply (Brooklyn), Ride Surf and Sports
(Tokyo). Types would be `surfing`; kind Maker.

**Pinned at -38.358398, 144.255318 on Scott's instruction.** Nominatim,
structured query, matched `type=house` at "100-100A, Addiscott Road, Bells
Beach, Bellbrae" — a building, not a street and not a suburb centroid.

The reasoning is in the row's `source_note` and is worth keeping here too,
because it is the precedent for every maker after this one. 100 Addiscott Rd is
in his own site's footer, so recording it is his own publication, and Scott
supplied the same address independently — two sources, neither of them dug up.
What the site does *not* do is invite a visitor: no studio, no hours, no "by
appointment". The "face-to-face consultation at his studio" line that turns up
in search results is **NobodySurf's editorial, not his**. That is why the rule
asks for a `source_note` rather than trying to decide in code — the note is
where the difference gets written down.

`km` is null, not guessed.

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

## The Where column prints the town, not the street

`suburbOf` answers "which town is this in", which is what the filters and the
town pages want. **`townOf` answers "what should the Where column say"**, and
that is a different question — added 27 Aug 2026.

The research passes write `location` as a full street address ending in the
suburb. That is the documented convention and it is correct: `suburbOf` reads
the last comma-separated chunk, so every filter has always been right. What was
wrong was printing it raw — "1A Harding Street, Portarlington" in a column two
words wide, truncated to "…Portarling…", which is the one part of the string
nobody needed. **176 of 441 activities are written that way.**

The rule is narrow on purpose: only a location containing a comma is collapsed,
and only to a town `suburbOf` actually recognises. A location that is a
description keeps its own words — *"Several Surf Coast beaches"* says more than
`Surf Coast wide` would.

**Nothing was deleted.** The full string moves into the open row as an
**Address** line, via `addressOf`, which prints it only when it says more than
the town already does.

**`townOf` lives in `notice-vocab.js`, beside `suburbOf`, and that matters.**
Three pages print a Where column — the board's `whereParts`, and `row()` and
`item()` in `notice-page.js` — and all three had their own copy of
`(i.loc || '').trim()`. One rule, one home; this project has already paid twice
for the same fact living in two places. Keep the function DOM-free, because
`api/subject.mjs` evaluates that file in a `node:vm` sandbox.

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

### The inbox is not only an event inbox

**Most of what arrives is a `share.google` link, and it is usually a business,
not an event.** Those short links resolve to a Google **Knowledge Panel** search
URL — `google.com/search?...&kgmid=/g/...&q=Bellbrae+Clay` — which is what the
Google Maps share sheet produces. So the capture is Scott standing in front of a
shop or a studio, not a poster with a date on it. Three of the five items in the
27 Aug 2026 pull were exactly that. **Resolve the redirect first** (`curl -sL -o
/dev/null -w '%{url_effective}'`), read the `q=` parameter for the name, then
research it first-party from there — the Google URL itself is never the row's
`url`, because it is a search result, which is the same defect as the 37 Google
Maps *search* urls this file already records.

**Pulling the inbox therefore means classifying before researching**: a business
becomes an activity (venue / shop / maker), a dated thing becomes an event, and a
page that turns out to be last year's becomes a line in the report and nothing
else.

**27 Aug 2026 — five items in, four rows out.**

- **Bellbrae Clay** (activity 462, venue, `arts · workshop`) — hand-building
  pottery studio, 590 Great Ocean Road, Bellbrae, run by Lauren Barton. Walk-In
  Fridays 2–6pm plus booked workshops. Pinned house-level.
- **The Running Company Torquay** (activity 463, **shop**, `running`) —
  3/1 Haystacks Drive. The second shop in the database after Patagonia, and the
  Chocolaterie rule decided it the same way: you go for the gear, so it is a
  Shop, off the board, and it earns its place on `/running`.
- **Mortadeli** (activity 464, venue, `cafe · restaurant · produce`) — Mediterranean
  deli, sandwich shop and pasta bar, Shop 9/4-6 Gilbert Street, Torquay.
- **Climate Connect – Snapshot: The Summer Ahead** (event 155, 10 Sep 2026,
  5:30–7pm, free) — Geelong Sustainability, at the **National Hotel** (place 108,
  created for it, `pub`, pinned to Nominatim's own `amenity=pub` node at 191
  Moorabool St). `date_confidence = high`: the organiser's own page carries the
  date, and its body names "Thursday September 10", which is a weekday checksum
  that passes.

**The fifth was a dead end, and it is the useful one.** The `/shd2025/` link is
Geelong Sustainability's **Sustainable House Day 2025** page — October 2025, long
past. SHD is annual and run nationally by Renew; the **2026 edition was 17 May
2026**, also past. So there was nothing to file, and nothing to infer: a page for
last year's edition is not evidence of this year's date, which is the Arts Trail
failure wearing a different hat. Worth putting a reminder somewhere for **May 2027**.

**Geelong Sustainability was deliberately NOT registered as a source.** Its
`/events/` page is a real, readable calendar — but it is an **organiser**, and
its events happen at other people's rooms (this one at the National Hotel). A
place row for it would be the Creative Geelong mistake exactly. The open question
is that there is nowhere in this schema for "an organiser worth watching that is
not a room", which is the same gap `The Sound Doctor` sits in.

**`bellbraeclay.com/booknow` is a live first-party workshop list and is not yet
registered.** It carried seven dated sessions Sep–Oct 2026 when it was read
(12, 13, 22, 24, 29 Sep and 1, 4 Oct), and **every printed weekday checks out
against the calendar** — the same checksum `scrape_venues.py` applies. Note the
URL needs the `www.`; bare `bellbraeclay.com/booknow` does not resolve. Its old
TryBooking landing page (event 1182007) is **stale** — a closed March 2024
booking — so do not register that one. Registering the booknow page means
creating a `places` row for Bellbrae Clay and repointing activity 462 at it with
`place_id`, rather than leaving it with its own coordinate; that is a decision
for Scott, and doing it carelessly is how 32 things ended up in both tables.

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

**The schedule fires at :17, not on the hour, and that is deliberate.** The
first scheduled slot this workflow ever had — Wed 26 Aug 2026, 21:00 UTC —
produced no run at all. Checked 90 minutes later: nothing queued, nothing
delayed, simply absent, while the workflow was `active`, the cron was on the
default branch, and `workflow_dispatch` had worked the same day. GitHub's
scheduled events are best-effort, the top of the hour is when every cron on the
platform fires at once, and under load runs there are dropped rather than caught
up. Moved to `17 21 * * 0,3` on 27 Aug 2026. **That is a mitigation, not a
proven fix** — the next slot is Mon 31 Aug 07:17 AEST, and if that one is
missing too the cause is something else.

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

`public/admin.html`, live at **https://notice.place/admin**. One page,
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

### Run it now

The Automations tab has a **Run the scrapers now** button. It does not fetch
anything itself — it dispatches the GitHub Action, and that indirection is the
point rather than a convenience: the job runs as itself, identifying as
`whattodo-janjuc`, which is the identity Humanitix's robots.txt permits. It is
therefore the honest way to pick up the Humanitix venues on demand, which a run
driven from a Claude session cannot do.

It needs `GITHUB_TOKEN` in the Vercel project — a fine-grained PAT with
**Actions: read and write** on this repo, or a classic one with `workflow`. The
public API is read-only, so without it the button answers 501 with that message
and the page offers the terminal commands instead. **A browser cannot do this
job itself**: CORS blocks reading humanitix.com from the page, so there is no
version of this button that scrapes client-side.

Under the button, a disclosure holds the by-hand equivalent
(`scrape_venues.py --only humanitix`). Scott's own terminal is not Claude
either, so that path is fine.

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

**`skipped` is drawn green, on purpose.** It was orange, and Scott read it as
"this automation is broken" — which is the opposite of true. A skipped source is
a working automation that this particular run did not exercise, so it says
*reading · not this run* in the same green as a live one. Orange is reserved for
things that genuinely need a person, like Eventbrite.

The aggregator table's venue count is the **union** of what is on file and what
the last run actually reached. Stored URLs alone undercount, because the scraper
also *discovers* a platform link by trying a venue's usual gig paths — Elephant
& Castle's TryBooking page is found at `/events` and appears on no row, so a
URL-only count showed TryBooking as "none on file" while its status said
"reading".

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

**The push races the run, and the run is long.** The commit step lost that race
on the very first real run of this workflow (25 Aug 2026): both scrapers
succeeded, the database was written, and the job went red on
`! [rejected] main -> main (fetch first)` because the run took **14m50s** and
three commits landed on `main` while it worked. Nothing was saved — no run log,
no seen ledgers.

That step is now a rebase-and-retry loop, three attempts. The three files are
append-only ledgers so rebasing on top of whatever landed is right; a *conflict*
is not, because it means two runs raced or somebody hand-edited a ledger, and
picking a side silently would drop a record — so it fails loudly instead.

Note this got worse rather than appearing from nowhere: the step used to commit
only when a seen-ledger changed, which was seldom. Now it commits a run log on
nearly every run, so a rare race became a frequent one.

Two more things in the workflow that are easy to get wrong:

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

    cp public/*.html public/*.css public/*.js ~/.cache/notice-preview/

The `*.js` half is new: since 26 Aug 2026 the page is not one file, and a
preview that copies only HTML and CSS runs the previous session's JavaScript.

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

## Eventbrite, and the organiser-is-not-the-venue trap

Three Eventbrite organiser pages were registered 25 Aug 2026 (Scott's links).
**17 events are sitting behind them, detected and unread.**

- `Torquay Bowls Club` (place 35) — an existing row the venue scraper had been
  reporting as "nothing machine-readable", because the club's own site carries
  no gig page. Its `events_url` is now the Eventbrite organiser page. 1 event.
- `Creative Geelong Makers Hub` (place 103) — new. 9 events.
- `Mt Rothwell Safe Haven` (place 104) — new, Little River, a fenced
  conservation reserve at the You Yangs end of the region. 7 events.

**Register the organiser, never the single event.** Scott sent Mt Rothwell as
one event link (`/e/…into-the-woodlands…`), which dies once that night is over.
The organiser page behind it (16088076701) carries all seven of their tours and
whatever they list next, so that is what went in `events_url`. The rule
generalises: an `/e/` link is a symptom, the `/o/` page is the source.

Mt Rothwell is pinned to a **house-number** match — Nominatim's structured query
resolves "5, Mount Rothwell Road, Little River" as `type=house`, the address the
tickets publish. Nominatim also carries "Mount Rothwell Biodiversity
Interpretation Centre" ~420m west on the same road; the published address won.
No website is recorded because `mtrothwell.com.au` 404s.

**The organiser on an Eventbrite page is not the venue.** The second one was
first created as *Creative Geelong Inc*, which is the organiser — Scott caught
it. The venue is in the event data: all nine events give
`location.name = "Creative Geelong Makers Hub"`, 15/132 Little Malop Street,
Centrepoint Arcade. Read the location off the events; do not name a venue after
whoever is selling the tickets. The organiser's name is kept in `aliases` so the
scraper can still match the listing back to this row.

That row's coordinate is the **arcade**, not the unit. Nominatim has no house
number on Little Malop Street and returns three separate segments of it up to a
kilometre apart, so a street match would have been a coin toss; `Centrepoint
Arcade` resolves as `type=pedestrian` — a real feature, and the building the
address names. `kind` is null: it is a workshop and market space and
`place_kinds` has no honest word for it, so it sits in the back-of-house "no
kind" flag for a person to decide.

**Nothing reads either of them yet.** `scrape_venues.py` has
`API_INSTEAD = {'Eventbrite'}` — it detects the events (it reports "Eventbrite
(9) — has a free API, left for a human") and deliberately refuses to scrape.

Worth knowing before that is revisited: the premise has weakened. Eventbrite's
event pages carry **clean schema.org JSON-LD**, and `eventlib.jsonld_events`
already parses them today — the same shape this file praises Humanitix for. One
caveat found while checking: a workshop is typed `EducationEvent`, not `Event`,
so any stricter filter than `jsonld_events` will silently drop them. robots.txt
allows `/o/` and `/e/` for our UA and names no AI crawler. So reading the pages
needs no token, while the API needs one stored in two places. **Scott has not
decided** — offered 25 Aug 2026 and left open, so `API_INSTEAD` stands.

## Two boards, one file

`/` is **Everything** — every kind that belongs on a board: somewhere to go,
something on, something to do at home. `/noticeboard` is **the Notice Board**,
and it is just what's on. Split 27 Aug 2026 on Scott's call.

They are the same page. `index.html` reads its own path, sets `EVENTS_ONLY`,
and `ok()` gains one condition; the word over the list comes from
`BOARD_TITLE`. A second file would be a second copy of a 400KB page carrying
the baked-in data, and it would drift from this one the first time either was
touched.

**The rewrite has to come before the catch-all.** Vercel matches rewrites in
order, so `/:slug` would otherwise swallow `/noticeboard` and hand it to
`api/subject`, which would answer 404 for a slug that is neither a town nor a
type. `noticeboard` is in that function's `RESERVED` set as well, as a second
lock, and `.claude/launch.json` has the same rule so the preview agrees.

**`nav.js` reads the path for this one, not `body.dataset.nav`.** Both paths
are the same file, so the attribute says `board` on both. A literal path needs
no vocabulary, so reading it is safe there even though `notice-vocab.js` loads
after the bar is drawn.

## The Kind menu

`Any kind` leads the filters on `/` — **Spots, Venues, Happenings, Ideas**, with
counts. Added 27 Aug 2026. It is the first of the four reader-facing kind
filters to exist, and it does the job of all four in one control rather than as
four buttons.

**It offers four of the seven.** Shop, maker and group are never in the list to
be narrowed, so listing them would be four dead rows — the same rule the Type
menu follows, which leaves out what it cannot give you rather than greying it.

**`/noticeboard` does not get the control at all.** Everything there is a
happening, so the menu would have one entry. `MULTI.kind` therefore does not
exist on that path, which is why `refreshFacets` guards the paint.

**This is the first place a reader is shown the word "venue".** This file
recorded that the site deliberately never did that — kind was plumbing and the
word on screen came from `types`. Scott asked for the kind filter, so the
dropdown is where that changed. The labels are in `BOARD_KINDS` if they should
read as something else.

**Two counting bugs were fixed to make the numbers true**, and both are worth
knowing because the same trap is waiting for the other three filters:

- `pass()` — which builds every menu's counts — did not apply `OFF_BOARD` or
  `EVENTS_ONLY`, so every menu was counting rows the list cannot show. It had
  been harmless until a kind menu made it visible.
- `atHomeHidden()` holds 43 rows back until you ask for something. Picking a
  kind is asking, so `S.kind` now counts alongside `S.type`; and `pass()` lifts
  the hold when it is computing the kind pool. Without the first change the menu
  promised 57 Ideas and delivered 14; without the second it promised 16.

## The nav bar, and the pages behind it

Built 26 Aug 2026. The site is four pages now, not one, and they share a bar
across the top: the **Notice** wordmark on the left, then **About**,
**Noticeboard**, and two menus — **Place** and **Type**.

```
public/notice-nav.css   the bar
public/nav.js           draws it, and works the two menus
public/notice-page.css  the template place/type/about are built from
public/notice-page.js   what a Place page and a Type page share
public/place.html       a town        /place?p=Torquay
public/type.html        a kind        /type?t=cafe
public/about.html       /about
```

### The URL a subject page lives at

```
notice.place/anglesea
notice.place/surfing
```

Flat. A town and a type sit at the top level with nothing in front of them —
Scott's call, 27 Aug 2026, overriding the `/place/anglesea` shape that shipped
earlier the same day. The reasoning against it was namespace collision; the
reasoning for it is that the segment repeated what the nav, the URL and the
word itself already said.

**Nothing collides today, and that was checked, not assumed.** No suburb slug
equals a type slug (50 against 43), and none of either equals a page, an asset
or an endpoint. **That check is now a standing cost of this shape**: a new type
called `about`, or a suburb called `admin`, silently becomes unreachable. Run
the collision check before adding either.

Routing, and the order matters because Vercel's does:

- **`redirects` run before the filesystem**, so `/place/:slug` and `/type/:slug`
  301 to `/:slug`. Links shared in the few hours the old shape was live keep
  working and are told, once, where the page moved to.
- **`rewrites` run after the filesystem**, so `/about`, `/admin`, `/nav.js` and
  every other real file is found first and never reaches the catch-all. This is
  the only reason a single `/:slug` rewrite is safe. `api/subject.mjs` also
  keeps a `RESERVED` set as a second lock.
- `/place?p=` and `/type?t=` still work, served straight off the filesystem.

**Which page a bare slug belongs to is decided in one place** —
`api/subject.mjs`, which tests places before types. Nothing is currently both,
so the order decides nothing today; it is written down so that the day one
collides the answer is already fixed rather than accidental. A town is the more
specific thing, so the town wins.

**The slug is derived, never stored.** `slugify`/`unslug` in `notice-vocab.js`
turn "Aireys Inlet" into `aireys-inlet` and back against the vocabulary the
site already has. A slug column would be a second copy and would go stale the
first time a type was renamed — the failure that file exists to prevent.

**The nav reads `document.body.dataset.nav`, not the URL.** `/anglesea` and
`/surfing` are both a bare slug, and telling them apart needs the vocabulary,
which loads *after* `nav.js` — the bar is drawn before the first paint. A page
naming itself needs nothing and cannot be wrong. Every page carries the
attribute; a new page without one falls back to `board`.

**Three URL shapes still reach `NoticePage.subject()`** and all three must keep
working: the flat path, an old `/place/<slug>` (a bookmark can land before the
301), and `?p=`. Whichever way it arrived, `canonical()` puts the address bar
back to the flat form with `replaceState` — no reload, and no extra back-button
entry for a URL the reader never chose. A made-up slug keeps the URL that was
typed, because rewriting it would hide the mistake the page then explains.

**A plain static server does none of this.** `.claude/launch.json` stands in
for all three rules, and for the catch-all it borrows the real vocabulary —
node evaluates `notice-vocab.js` exactly as the function does, so the preview
cannot disagree with the deploy about which page `/surfing` is. **A rewrite is
still the one thing local cannot prove** (see below); check routing on the
deploy.

**The `cleanUrls` collision, paid for once.** With `cleanUrls` on, Vercel 308s
`/place.html` to `/place`, so a rewrite destination written as
`/place.html?p=:slug` collides with that redirect and every subject URL 404s.
Destinations must be the clean path. This shipped broken (27 Aug 2026) and
passed every local test first, because the preview server stands in for
cleanUrls by *serving* the file and never issues the redirect that causes the
collision.

### Each subject carries its own title and description

`api/subject.mjs` serves `/<slug>`. The catch-all rewrite points at it rather
than at a static file, and it reads the page off disk and edits
the head on the way past — `<title>`, `description`, `canonical`, Open Graph
and Twitter card.

**The problem was link previews, never Google.** Google renders JavaScript, so
a title set by `document.title` is indexed fine. iMessage, Slack, WhatsApp,
Facebook and Twitter read the raw HTML and stop, so every one of the 93 subject
pages was being shared as "Place — Notice" with no description — the same card
93 times.

**Why a function and not 93 generated files.** This project has no build step
and should not get one. A file per subject would also be a second copy of the
page shell and would drift from `place.html` the first time either was touched.

**The vocabulary runs in a `node:vm` sandbox.** `notice-vocab.js` is a classic
browser script so it cannot be imported, but it is pure data and functions with
nothing of the DOM in it. Evaluating it keeps ONE copy of the suburb list, the
type labels and the slug rules, which is the whole reason that file exists.
**Keep it DOM-free** — a single `document.` in there breaks this function.
`NOT_A_TOWN` moved there for the same reason: the description uses the same
sentence the page does.

**It does not query the database, on purpose.** A count would read better in a
preview, but it would put a Supabase call in front of every page view and give
these pages a way to fail that they do not currently have. The count is already
on the page, where the reader is.

**A made-up slug answers 404 and `noindex`**, with the real page as the body so
it still explains itself. And if the function throws, it 302s to the
query-string form: the metadata is lost, the page still opens.

**The canonical names the host the request arrived on.** `notice.place` 308s to
`www.notice.place`, so a hardcoded apex made every `canonical` and `og:url`
point at a redirect.

**Still no `og:image`.** There is no artwork cut for the 1200x630 slot, and a
card with no picture beats one pointing at a picture that is not there. This is
the one obvious thing left in the preview.

### These are pages, not the board with a filter on it

This was the first shape tried and it was wrong. A Place menu that set
`S.suburb=['Torquay']` and re-titled the masthead is cheaper and reuses
everything, but it produces one flat list sorted by *closest first* on a page
about a single town, which is a sort with nothing to say. What the two pages do
that the board cannot:

- **A town splits.** What's on (dated, soonest first) above Places to go
  (evergreen, alphabetical). The board can only interleave them.
- **A type breaks out by kind.** Seven lists side by side, so a row filed
  wrong is obvious. See below — it used to group by town, and that changed on
  27 Aug 2026.

So each page arranges its own listings, and `row()` takes the facts the page has
**already established at the top** and leaves them out — a Torquay page does not
print Torquay 71 times. That is `skip`, and it is a comma list because a Type
page groups by town and has therefore said two things (`'type,suburb'`).

**`'suburb'`, never `'where'`.** The first version passed `'where'` and dropped
the venue with the suburb, which left every gig on the Torquay page with nowhere
to be. The town is the page's subject; the Torquay Hotel is still the thing you
need to read.

### A type page is a monitoring view

Rebuilt 27 Aug 2026, the day `kind` landed. It used to group by town, which is
the better arrangement for a reader and the wrong one for checking a
classification. Now it draws **seven lists, one per kind**, plus an eighth for
anything with no kind at all — because on a page whose job is showing how
things are filed, an unfiled row is the most important thing on it.

**Every kind is drawn even when it holds nothing.** "shop 0" on `/surfing` is
itself the fact worth seeing, and a section that vanishes when empty makes the
page a different shape every time, which cannot be scanned the same way twice.

**Every bucket is the same fixed height (`--bucket`, 430px) and scrolls inside
itself.** That is what turns this from a page you read downwards into a panel
you scan across: the seven headings line up in a grid, so the counts can be
compared without scrolling, and no one kind can push the others off the screen.

It also retired an earlier rule — "a section past 14 rows takes the full width
and splits its own items into columns" — which existed only to stop `/cafe`
running 65 venues down one column with the other side empty. A fixed height
solves that without handing one kind more of the page than the rest. If a
CSS-multi-column version is ever tried again: it splits a long section across
the fold, and `break-inside: avoid` cannot rescue a section taller than its
column, so the break happens anyway and unpredictably.

Three columns above 1180px, two below it. **Below 820px the buckets grow
instead of scrolling** — seven nested scroll areas on a phone is a trap, where
a drag meaning "scroll the page" lands inside a bucket and goes nowhere. The
scroll areas also set `overscroll-behavior:contain`, or reaching the end of one
bucket starts scrolling the page underneath it.

The empty state lives INSIDE the scroll box rather than beside it, or an empty
kind would be a different height from a full one and the grid would go ragged
again.

**The type page alone widens to 1400px** — `body[data-nav="type"] .page`. Three
columns of listings want the screen, while the masthead reads better narrow, so
`.stand` keeps its own 54ch cap and only the grid below it spreads.

**The row is `.item`, not the board's `.rowline`.** Same gesture — the head is
the button, one class toggles, the body carries what the head could not show —
at a size that fits half a column. Deliberately not a copy: the board's row
also carries an icon gutter, a colour tint and the save pin, and none of those
earn their width here. **No description in the head**, because the thing you
scan for is the name and how it is filed.

**`item()` takes a third argument, and it matters**: the ONE type to leave out,
rather than all of them. On `/cafe` a row that is `bakery · cafe` must still say
bakery — that is the only thing separating it from the other 64, and dropping
the whole list to avoid repeating "cafe" throws it away too.

**Each bucket is outlined, and the kind is set as a heading.** Seven scroll
areas with nothing between them read as one long list that keeps restarting —
the border is what says "this is a box with an end to it", which is the premise
of a fixed height. The kind was a small-caps utility label and read as a field
name; it is the site's serif at 19px in Title Case now, which is the name of a
list rather than the label on a form.

**A row linked to its own place row prints its own name back at itself.**
`Patagonia Torquay` the shop points at `Patagonia Torquay` the place to inherit
a coordinate, so `place` and `name` are the same string. `item()`, `row()` and
index.html's own `whereParts()` all drop `place` when it matches the name —
three copies of one rule, because the board's row template is not shared with
the subject pages.

**`fromRow` had to learn `kind`.** It was dropping the column entirely, so the
first build put all 65 cafes under "no kind". Anything the page reads has to be
in that mapping — the view carrying a column is not enough.

### What was lifted out of index.html, and why it had to be

Three files came out of the one-file page so more than one page could read them.
This is a **lift, not a copy**, and that is the whole point — two live copies of
one fact is how this project put the same festival on two different dates.

- **`notice-vocab.js`** — `suburbOf` and the suburb list, `typesOf`, `GROUPS`,
  `GROUP_OF`, `groupsOf`, `TYPE_PLURAL`, `PLACE_TYPES`/`EVENT_TYPES`, and
  `todayISO`/`daysAway`/`nextDate`. A suburb page that decided for itself what
  counts as "Torquay" would disagree with the board sooner or later. `nextDate`
  in particular has already been wrong once in a way only a test caught (the UTC
  parsing bug) — one copy, one fix.
- **`notice-data.js`** — the connection and `fromRow`. **`scripts/configure.py`
  writes the keys here now, not into `index.html`.** `admin.html` still carries
  its own copy of the URL and anon key; that predates this and was left alone.
- **`notice-page.js`** — `rows()`, `row()`, the date label. Only the two subject
  pages use it.

Load order is `notice-vocab.js` → `notice-data.js` → the page's own script.
`fromRow` reads `GROUP_OF`; classic scripts, no modules, nothing on `window`
by hand.

### The bar

`nav.js` writes the bar into the page rather than each file carrying the markup,
so it is in one place when it changes. **It is the first thing inside `<body>`,
and that is load-bearing**: a classic script there runs before anything below it
is parsed, so the bar is in the document for the first paint. Deferred at the
end of the body it appears late and shoves the page down.

`notice-nav.css` **names no colour** — every value is one of the site's own
tokens, so the bar follows Auto/Light/Dark with the theme pill and never has to
learn the three-state shape. It is `--surface` against the page's `--ground`, so
it reads as raised in both schemes: a shade darker than the page in light, a
shade lighter in dark. Scott chose theme-aware over a hardcoded white bar.

`z-index:70` and not 60. The board's filter pops are 60 and live in the page's
own stacking context, so the bar has to outrank them or the Type menu opens
behind the Suburb one.

**The menus are the vocabulary, not the data.** They list every suburb and every
type, with no counts. A suburb with nothing in it is still a suburb, the count
belongs on the page you land on rather than the menu you leave, and building
them from `listings` would make the bar wait on a fetch before it could draw.

The masthead's top padding dropped from 72px to 44px (26px on mobile) — the bar
is now that space.

### Deliberately not done

- **No baked-in fallback on the subject pages.** index.html ships 160KB of JSON
  so the board is never blank; a Place page says it could not reach the database
  instead. Do not add the copy to three more files.
- **No map on a town page.** It is the obvious next thing and it is real work —
  MapLibre, the water check, the shared-coordinate pin. Not started.
- **The board does not link to these pages yet.** A suburb or a type printed in
  a row is still plain text. Linking them is the natural follow-up.

## Researching listings in bulk — the group prompts

`prompts/by-group.md` holds nine prompts, one per group, written 26 Aug 2026 to
be pasted into a Cowork session with this folder open. Each is a loop: it works
every type in its group thinnest-first, dry-runs, writes, logs to
`prompts/log/<group>.md`, and does not stop to ask between types. They all point
at `prompts/RESEARCH_RULES.md` rather than repeating the rules — one copy.

`scripts/have.py` is what they read first: `have.py <type>` lists what is already
there, `have.py <group>` does every type in a group thinnest-first, and
`have.py places` shows the places table and which rows have a feed.

**The hospitality pass ran first — 71 rows, group 26 → 120.** Discipline held
where it was checked mechanically: everything unverified, every row with a
`source_note`, no `km` invented, three pins left null rather than guessed. Four
things went wrong, and all four were the same shape — *a rule that lived only in
prose*:

- **A road named after a town beat the town.** `suburbOf()` scanned longest-first
  over the whole string, so "561 Cape Otway Road, Moriac" filed the Moriac
  General Store under Cape Otway, 90 km away. It now reads the last
  comma-separated chunk first and falls back to the old scan. Two rows moved,
  nothing else did. **Write `location` ending in the suburb.**
- **`sync.py add` never checked coordinate precision** — only `/admin` did — so a
  three-decimal pin walked in. Both write paths check it now. Note the honest
  exception: a real OSM node can sit on a round number (the 18th Amendment Bar
  is at exactly -38.1480000), and that case goes in through `/admin` with the
  reason in `source_note`.
- **`add`'s duplicate check misses a suffix.** `Common Ground Project` landed
  beside `Common Ground Project – Freshwater Creek`. Merged onto the lower id
  26 Aug 2026, the way the Torquay Farmers Market pair was. Search the
  distinctive word, not the whole name.
- **A Google Maps *search* url got written and logged as "per policy".** It is
  not, and never was. 37 of those are still in the table as a standing defect.

The generalisable bit: **a rule the tooling does not enforce is a rule a research
pass will break**, however plainly the prose states it — and it will report the
break as a decision rather than a mistake. Before the next big pass, put the rule
in `check()`.

**Round two proved that sentence twice over** (26–27 Aug 2026, 95 rows, ids
364–458, every one of the 47 Place-menu towns swept). The two rules that had been
moved into `check()` held perfectly: **no `km` invented, and not one coordinate
under four decimal places.** The `suburbOf` fix held too — all 95 rows land in
the town their address names. The rule still living only in prose was broken
again, harder: **nine Google Maps search urls**, where round one wrote one. So
`check()` refuses those now as well. Cleared 27 Aug 2026, each row's
`source_note` saying what it used to hold.

Round two's own finds are worth keeping:

- **OSM's tags are not a category system.** A pub tagged `tourism=hotel` and a
  cafe tagged `shop=convenience` are invisible to an `amenity` food query — the
  Little River Hotel and Kennett River's Kafe Koala were both found only by
  looking at the town by hand afterwards. `nearby.py`'s KIND_TAGS needs
  `tourism=hotel`, and any sweep of it needs a by-hand pass behind it.
- **OSM is stale in a useful way.** It still listed MoVida Lorne (now Totti's),
  Growlers (now Ela) and The Ridge at Beech Forest (closed). A name that will not
  confirm first-party is often a venue that has changed hands, which is worth
  more than the listing would have been.
- **Anglesea had a pub nobody had listed** — Klein's Anglesea Hotel. The first
  pass filed "no pub in Anglesea" as fact.
- `Love House` (400) supersedes `Captain Moonlite` (355) — same building at the
  Anglesea SLSC, new operator. Two listings for one room; 355 needs removing or
  marking closed through /admin.
- Totti's Lorne (406) shares a coordinate with the Lorne Hotel (313) because it
  is inside it. That is the HOOP Gallery case, not the placeholder case.

Still open from that pass: **19 pre-existing activities carry a pin under four
decimal places** (three at 2dp, one at 1dp), which the 24 Aug sweep missed
because it only looked at the citizen-science rows. Several share a coordinate
exactly, which reads as copy-paste rather than geocoding. Not touched — nulling
19 pins takes them off the map, and that is Scott's call.

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

Scott's own artwork. Five are in so far: `skatepark` → skate, `mountain biking`
→ bike, `cafe` → coffee (from `../Notice.Place/Icons/SVG/`), plus `nature` →
nature and `running` → run (from `../Notice.Place/Icons Test/SVG/`, which is a
two-colour direction still being tried).

**The type split silently broke three of the five and they were repointed**
(26 Aug 2026). `ICON_OF` is keyed on a row's *first* type, and `bike track`
became `mountain biking` while `sport` and `sport-event` were deleted — so
`skatepark`, `cafe` and `nature` were the only ones still drawing. The bike now
also serves `cycling` and the runner serves `running`, which is where the old
`sport-event` runs went. That reaches **72 of 419 rows**, up from 52.

The lesson generalises: every map keyed on a type name — `ICON_OF`, `EXTRA_OF`,
`GROUP_OF`, `TYPE_PLURAL`, `VERB_OF` before it was deleted — fails *silently*
when a type is renamed, because a missing key is just no icon, no group, no
label. There is no test for this. Grep the type name before renaming one.

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
  small-size version before the set reaches all 42 types. The two-colour pair
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

- **`sync.py add` takes `place_id` now** (27 Aug 2026). It was on activities but
  not events, so every event written by hand started unlinked — no pin, no
  curated suburb — and needed a second patch that is easy to forget; that is a
  quiet contributor to the place-less events on this list. Event 154 was the
  last one added the old way. A bad id is refused by number rather than as an
  opaque foreign-key error, and the ids are only fetched when a row actually
  carries one. Adding it to `EVENT_COLS` does not disturb `EVENT_ONLY`, since
  `place_id` is in both column sets — checked: an event with a `place_id` still
  routes to `events`.
- An activity's single `url` is whatever it is — a map pin for some, the venue's own
  site for others. The row labels it by inspection (`isMapLink`), so don't assume the
  slot means "map". 87 of 203 activities carry a website there. `Directions` is built
  separately from `lat`/`lng`. 128 of 272 activities are pinned; the rest are the
  At home entries and the roving ones, which have nowhere to be
- 42 entries use Google Maps *search* URLs rather than pinned coordinates
- **The Gather trio is one thing in three kinds, and it is the clearest example
  of why the kinds exist.** `Gather` (activity 291) is the cafe — a **venue**.
  `Gather Athletics` (activity 461, added 27 Aug 2026) is the running group that
  meets there — a **group**. `Gather Athletics Shop Run` (event 89) is the
  Saturday run itself — a **happening**. All three share place 84's coordinate;
  none of them duplicates it, because 461 links with `place_id`.
  The run's `recurrence = weekly` no longer rests on Scott's word alone: the
  @gatherathletics profile says "every saturday" first-party. Still no `km` on
  any of them.
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
  `cp public/*.html public/*.css public/*.js ~/.cache/notice-preview/`. See "Serving it
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

0. ~~Set the Vercel environment variables~~ **DONE 27 Aug 2026.** `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` and `ADMIN_PASSWORD` are in the Vercel
   project and `/admin` saves — the endpoint answers `wrong_password` to a bad
   one rather than `no_password`, which is the difference between configured
   and not. `GITHUB_TOKEN` is separate and only powers the Run-now button.
1. **The kinds are in and everything is classified; two halves are left.**
   (a) **The four filters** — Go somewhere / What's on / Join in / At home —
   which is what makes `kind` visible to a reader. `ok()` in index.html filters
   on `S.kind`, and `atHomeHidden()` can then go: holding the at-home rows back
   was a patch over not having a kind, and `kind = 'idea'` says it properly.
   (b) **Merging `places` into the listings tables**, which is the destructive
   half and the one that fixes the 32 things existing in both, three of them
   disagreeing about where they are by up to 999 m.
2. Give `The Sound Doctor` (place 32) the right kind, or decide `hall` will do
   — see the Places section. The other 11 unclassified places need a word the
   vocabulary does not have yet (shops, organisations, two walks, a boat ramp).
3. Build place rows for the four dated events whose free text already names a
   real place: `Baines Crescent outlets` (22), `Anglesea Community Hub` (30),
   `Anglesea Community Precinct` (53), `Torquay Common` (77). Each one then
   gets a pin and a tidier name. `name_rules.py` lists all 18 that have a date
   and a time but no venue.
4. **Give the 16 place-less events a place.** Every event is verified now, so
   `sync.py pending` is empty and this is what is actually left. Four only need
   a place row built from the name they already carry (`The Mac`, `Anglesea
   Community Precinct`, `Torquay Common`, `Surf Coast Walk`); six name only a
   suburb and need a real start line; two are genuinely shire-wide; four are
   the `Quiet Club` nights, parked 25 Aug 2026 — their venue is missing from
   the source, not from us (see below).
5. Verify community additions — `python3 scripts/sync.py pending`, then `verify <id>`
   to approve or `reject <id>` to delete. `reject` refuses verified rows and asks
   before deleting; `--yes` skips the prompt.
   `add file.json` (or `-` for stdin) writes a researched entry, one object or a
   list. It checks types, conditions, enums, date shape and URLs against the live
   vocabularies before writing, so a bad field in a batch names itself instead of
   failing an opaque insert. It refuses a name that already exists — pass `--force`
   only when it genuinely is a different thing. `--verified` requires a
   `source_note`; `--dry-run` checks without writing. An event's link is
   `info_url`/`ticket_url`, never `url`.
6. Pin the 42 entries whose `url` is a Google Maps *search* rather than a
   coordinate — each one is a missing pin on the map
7. Promote the Ideas Pipeline into the database
8. A scheduled job that re-checks estimated event dates as real ones get announced
9. **Type icons cover 72 of 419 rows.** Six symbols against 42 types. The set was
   drawn for the old 26 and the split widened the gap — `surfing`, `swimming`,
   `walk`, `night`, `gig` and `at-home` are all big now and all draw the empty
   slot. See the icon section for what the artwork has to solve first (the bike
   does not survive 28px, and only one of an icon's two edges can be true until
   they are all drawn to the same width).
10. **`places.offers` has a value that means nothing.** `tickets` records that the
   row has an `events_url` for the scraper to read — a fact about our plumbing,
   not about the place, and true of every venue that sells a ticket. It is on 2
   of the 7 rows that have one, so it does not even work on its own terms. Delete
   it. `live-music` is worth arguing about on the same grounds: it is true of 38
   places, but a venue with gigs is already proved by having gig rows attached, so
   storing it is a second copy that can go stale.
11. **`Sport` listings from the events feed now arrive with no type.** The source
   says only "Sport" and the vocabulary has running, cycling, swimming, surfing
   and paddling — the feed never says which, so `scrape_events.py` writes nothing
   rather than guessing. Those rows show as *unsorted* and need a person. That is
   the intended behaviour, not a gap, but it means the Monday/Thursday run will
   quietly accumulate untyped sport events if nobody looks.
