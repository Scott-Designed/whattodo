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

  **THE RED BOX WAS KILLED 30 Aug 2026, on Scott's instruction**, and this
  paragraph is the argument against having done it — kept, not deleted, because
  it is the thing to read if these dates start going stale. The count survives
  in the overview's *Waiting on you* stat, which still says "2 moved dates", so
  nothing is silent; what has gone is the shouting and the link straight into
  each event's editor. Nothing else in the interface names WHICH rows moved.

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

## Coast & Bay — registered, not yet automated

`coastandbay.com.au/this-weekend/` — a local publication's what's-on page,
added to the aggregator list 27 Aug 2026 at Scott's request. It shows on the
Automations tab as **not automated**, which is the honest state: nothing reads
it and two things stand in the way.

**1. A Claude session cannot check it.** Its robots.txt names `ClaudeBot` and
disallows the entire site — the Humanitix rule again, and this time for the
whole domain rather than one path. `whattodo-janjuc` falls under `User-agent: *`
which says `Allow: /`, so **the scheduled Action and Scott's own terminal are
fine**; an assistant is not. Nine crawlers are blocked, which is a stock
Cloudflare AI-bot list, not a judgement about this project.

Its Content Signals say `search=yes, ai-train=no, use=reference`. Nothing here
trains anything, and referencing is permitted.

**ANSWERED 28 Aug 2026 — it does publish the feed.** The back-of-house "Test
this source" button ran it and got *"a JSON feed with 3 items"*, with the same
field shape as surfcoastevents (`id, global_id, global_id_lineage, author,
status, date, date_utc…`). So this is **the second real feed this project has
ever had**, and the only thing left is point 2 below: `scrape_events.py` has to
learn to carry more than one source.

    https://coastandbay.com.au/wp-json/tribe/events/v1/events?per_page=3

The check could not come from a Claude session — that site disallows ClaudeBot —
and it did not: it came from the Vercel function, which is neither a browser nor
ClaudeBot, identifies as `whattodo-janjuc`, and reads robots.txt first.

**2. `scrape_events.py` is hardwired to one source, and that is deeper than a
constant.** `SOURCE`/`API` are module-level, but so is the rest: the
`source_note` is written as `surfcoastevents.com.au/<slug>`, `added_by` is the
literal `'surfcoastevents'`, the drift check matches rows with a regex on that
domain, and the header line prints it. **The seen ledger is keyed on `slug`
alone**, so two sites could both publish `spring-market` and the second would be
silently treated as already offered. A second feed means keying provenance and
the ledger by source, not adding a URL.

**Do not register an aggregator in `places`.** `scrape_venues.py` sets
`place_id` to the row it read from, so every event from a Coast & Bay row would
be filed with "Coast & Bay" as its venue — the organiser-is-not-the-venue trap
at its worst. That is exactly why surfcoastevents lives in `scrape_events.py`
instead, and why that scraper deliberately sets no `place_id`.

## The mountain bike clubs, and EntryBoss — 28 Aug 2026

Four clubs added as **groups** at Scott's request. None carries a coordinate:
not one of the four publishes premises or a postal address, and all four are
filed at the park or network they work in rather than at rooms they do not
have — the `Surf Coast Mountain Bike Club` precedent from 27 Aug.

    516  Geelong Mountain Bike Club              You Yangs  mountain biking
    517  Surf Coast Mountain Bike Club           Anglesea   mountain biking · volunteering
    518  You Yangs Mountain Bike Club            You Yangs  mountain biking · volunteering
    519  Forrest Mountain Bike and Cycling Club  Forrest    mountain biking · cycling · volunteering

**GMBC and You Yangs MTB Inc are two different clubs sharing one park**, which
is the kind of thing worth writing down before somebody merges them. GMBC races
in the You Yangs; You Yangs MTB Inc builds and maintains the downhill and XC
trails there and says its ride days "are purely fundraisers".

### A `places` row is not a listing — the fault this exposed

Scott noticed the Surf Coast club was missing from `/mountain-biking`. It had
been in the database since 27 Aug as **place 105**, and that was the whole
problem: **type pages and the board read `listings`, which unions `activities`
and `events`. A `places` row appears on neither.** So a thing can be fully
researched, correctly typed in prose, and completely invisible.

Row 517 links `place_id = 105` rather than repeating the club, so there is still
one copy of the fact. The generalisable check: **after adding a place, ask
whether a reader is ever meant to find it.** If yes, it also needs a listing.

**Event 150 `Trail Working Bee` was the second half of the same complaint** and
a different fault — it was typed `volunteering` alone, so a working bee on a
mountain bike trail network was absent from `/mountain-biking`. It is
`volunteering · mountain biking` now, volunteering still primary because that is
what the row is. `mountain biking` went 12 → 16.

### EntryBoss is readable, and it is the best HTML source this project has found

`entryboss.cc/calendar/gmbc` — the club's fixture calendar. **robots.txt is
entirely commented out**: nothing disallowed, no AI-crawler clause, so a Claude
session and the Action are both fine. Not Humanitix, not Coast & Bay.

The markup is regular and needs no per-venue special case:

    .fixture-row  >  .fixture-date    "Sat, 29 Aug 2026"
                     .fixture-name    <a href="/races/31305">
                     .fixture-course  "GMBC - Drysdale Rd Carpark"

An `<h4>Upcoming</h4>` section is followed by `<h4>Previously</h4>`, so future
events are separable without comparing dates. **Every date prints its weekday**,
which is exactly the checksum `scrape_venues.py` already applies. All nine
upcoming rows passed it. Each `/races/<id>` page then carries the real schedule
(registration 8:30am, race 9:30am), the fee table, and a Google Maps place link
with a building-level coordinate in it.

### The club's own site is WRONG, and the ticketing platform is right

This inverts the rule this file has repeated everywhere else, so it is worth the
detail. `gmbc.com.au` is WordPress running Modern Events Calendar, robots-clean,
with a public `wp-json/wp/v2/mec-events` API and **schema.org JSON-LD `Event`
markup on every event page** — the shape `eventlib.jsonld_events` already parses.
Everything about it says "use this instead of scraping HTML".

**Do not.** Two faults, both silent:

- **`wp/v2/mec-events` gives the POST date, not the event date.** MEC keeps the
  event date in postmeta, which `wp/v2` does not expose, and `mec/v1/events`
  returns `[]`. A scraper reading `date` would file every race on the day its
  page was published. `date_gmt` is the same trap wearing a suffix.
- **The JSON-LD dates are a day late on the Friday races.** Checked across eight
  events 28 Aug 2026. Every Friday night race — the "under lights" ones, which
  carry a nonsense `05:00:00+10:00` start — reads one day after the date in its
  own title, while the weekend events are correct:

        Round 6 at Duckponds   title "Fri 11th September"   JSON-LD 2026-09-12 (Sat)
        Round 5 at Duckponds   title "Fri 4th September"    JSON-LD 2026-09-05 (Sat)
        Round 3 at Duckponds   title "Fri 21st August"      JSON-LD 2026-08-22 (Sat)

  EntryBoss has all three right. **The times are unreliable across the board** —
  the 3 Hour Endurance race shows 18:30 in JSON-LD and registers at 8:30am on
  its own race page.

The weekday checksum is what catches this, and it catches it in the document
that contains both facts: a page whose title says Friday and whose `startDate`
is a Saturday is refuting itself. **A first-party page is authoritative about
intent, not about correctness.** Where a club actually operates from a ticketing
platform, the platform holds the working data and the website is a poster.

### Automating it — the honest state

It is the most automatable source found since surfcoastevents, and **it fits
neither existing scraper without a change**. The eight fixtures below were
therefore written by hand; automating it would have been the larger job and is
still open:

- **`scrape_venues.py` is wrong for it.** Its registry is `places.events_url`
  and it sets `place_id` to the row it read from. GMBC is an **organiser**, so
  registering it would file every race at "Geelong Mountain Bike Club" — the
  Creative Geelong trap, which this file already warns about for aggregators.
  **Do not put the EntryBoss URL in a GMBC `places` row.** The venue is in the
  data instead: `.fixture-course` per row, and a coordinate on the race page —
  the same shape as reading Eventbrite's `location.name` off the events.
- **`scrape_events.py` is hardwired to one source.** `SOURCE`/`API`, the
  `source_note` string, the literal `added_by = 'surfcoastevents'`, the drift
  regex, and **a seen ledger keyed on `slug` alone**. The Coast & Bay note
  already says what this costs: a second feed means keying provenance and the
  ledger by source, not adding a URL. That work is shared between the two, so
  whichever lands first pays for both.

### The eight fixtures are in — events 172-179, 28 Aug 2026

Written by hand, with three `places` rows built for the courses first. Seven of
the eight are on the map. `GMBC Merch 2026 (Winter)` was in the calendar and was
dropped — it is a merchandise order, not a happening, and a scraper needs to
drop those too.

    117  Drysdale Road Carpark (You Yangs Stockyards)  -37.9257642, 144.4425827
    118  Kurrajong Carpark (You Yangs)                 -37.953832,  144.402298
    119  Duckponds (You Yangs)                         -37.963063,  144.409938

**Every course coordinate is the club's own published location.** Two of the
three are **plus codes** off the race pages' map embeds, decoded rather than
looked up — `3CFV+M2` and `2CP5+QX Little River`. That is deterministic maths,
not a geocode, and it was validated before being trusted: race 31305 also links
a Google Maps *place* naming "Drysdale Road Carpark - You Yangs MTB
(Stockyards)", and the decoded plus code lands **6 m** from it. A plus code cell
is 14 m, so two independently published values agree exactly. All three
reverse-geocode to named roads — Stockyards Management Track, Kurrajong Avenue,
Turntable Drive — none to a bare "Victoria, Australia", which is the open-water
signature.

**Duckponds is 200 m from a building Nominatim calls "Former Duck Ponds
Parsonage and School"**, which is what confirms it: the club's own schema.org
markup names the venue "Duckponds School". The published plus code was kept
rather than the heritage building, because the club is publishing where to turn
up, not which building it is. Note the EntryBoss **course label for those races
reads "GMBC - Park Office"**, which matches neither the race titles nor the
location the same page publishes — the location field was trusted over the
label, and a scraper reading `.fixture-course` as the venue would get this wrong.

**The Dirt Girls ride (177) has no `place_id` on purpose.** It meets at Hurst
Rd, Anglesea, and Nominatim returns three separate Hurst Road segments up to
3 km apart — the multi-segment coin toss. The meeting point is free text in
`venue`, the same call as the Apollo Bay Foreshore and Mirambeena Park markets.

**Two existing pins look like placeholders and were left alone.** `You Yangs
MTB Park – Kurrajong` (40) sits 5.5 km from the club's Kurrajong carpark and
carries a coordinate **identical to activity 155's**, the whole regional park;
`– Stockyards` (41) is ~2 km from the Drysdale Rd carpark. Same coordinate on
two rows reads as a park centroid copied twice rather than as a second opinion.
Not touched — moving somebody else's pin on suspicion is how the disagreements
in this database got made. Worth a check.

**Only GMBC is on EntryBoss** — checked against the platform's own club list,
which carries Geelong BMX, Geelong Cycling, Geelong & Surfcoast Cycling and
Colac Cycling but neither of the other MTB clubs. The other three publish to
Facebook and nowhere machine-readable.

### Facebook-only sources say so on the Automations tab

Scott's call, 28 Aug 2026. Three of the four clubs announce rides and working
bees on Facebook alone, and Forrest says it outright — **"follow the club
facebook page for events"**, its own wording. That is a standing weekly job for
a person, and it now reads that way instead of sitting in `untried` looking
like an automation that might yet run.

`SRC_STATE` gains **`fbweekly` — "Facebook — check weekly"**, orange like
`manual` but naming the cadence, because the whole reason for flagging it is
that nobody remembers to look. `sourceRows()` derives it: a place with a
`facebook`, no `events_url` and no `ticketing_url`, whose state is otherwise
`nothing`/`untried`/`nourl`/`dead`. **The guard is the important half** — it is
only ever applied where there is nothing machine-readable to lose, so a venue
that also has a ticketing feed keeps the status that actually matters. The row
links to the Facebook page rather than the website, since that is the page a
person has to open.

Two places rows were created to put the clubs on that list at all — **115 You
Yangs MTB Club, 116 Forrest MTB and Cycling Club**, both `kind = bike-club`,
both with `events_url` deliberately null, matching 105. **Do not put a Facebook
URL in `events_url`.** Nothing can read one: it wants a token and client-side
JS, and Forrest's site is the proof — it embeds a `custom-facebook-feed` plugin
whose container renders empty to a plain fetch. Setting it would also hand
`scrape_venues.py` a club to file events against as though it were the venue.

**A guessed social URL got written and had to be corrected within the minute.**
Place 115's Facebook was first written as `/youyangsmtb`, inferred from the
domain; the club's own site links `facebook.com/YYMBI`. Nothing about the rule
is new — *never invent a URL* is the line this file opens with — but it is worth
recording that it broke on a field that felt too minor to check, which is
exactly where it will break again. The correction is in that row's
`source_note`. Forrest's two were read out of its raw HTML.

**Racing at Forrest is run with GMBC**, so some Forrest events will arrive
through the EntryBoss calendar rather than off Facebook. Worth knowing before
the same race is filed twice from two sources.

## The library calendar — 500 events, 19 branches, imported 27 Aug 2026

`scripts/scrape_library.py` reads Geelong Regional Libraries' **iCal** feed.
Both RSS and iCal come off the same endpoint and differ only by `feedType` in a
base64 payload, and they are not equivalent — read the iCal:

- **iCal has LOCATION and GEO.** The RSS has neither, so the branch is only in
  prose and 481 of 500 items never name one. Every event would be unplaceable.
  GEO also means the pins are the library's own published coordinates, not
  something geocoded here, and every branch publishes one consistent point.
- **iCal's DTSTART is honest UTC.** The RSS `pubDate` says `+0000` while
  carrying local wall time — read as UTC that shifts every event ten hours. The
  `nextDate` bug in a new hat, and nothing would have caught it.
- **UID == the RSS guid**, so the ledger keys the same either way.

**The `days` filter does nothing.** 1, 20 and 90 return the identical 500 items
covering about 20 days; the server caps at 500. So the URL is a rolling window
to poll, not a range to request — and because `days` is *relative* there is no
date in it to expire. A Date-range tab in their UI does not reach the feed at
all: setting one produces a byte-identical URL.

**`kids` was added to the vocabulary first, deliberately.** 215 of the 500 are
story times, and retyping them afterwards is more work than typing them right on
the way in. All five places done — the `types` row (band `whatson`), `GROUP_OF`
(→ community), `TYPE_PLURAL` (*For kids*), `api/enrich.mjs`, `EVENT_TYPES`. The
`/kids` slug was checked against every town slug and every file first.

**Four suburbs were missing and are now in.** Highton and Newcomb joined the
`GEELONG` fold; **Bannockburn** and **Colac** became towns in `SUBURBS` — the
produce pass had already recorded Bannockburn as stranded. Without this a branch
row's suburb resolves to null and its events reach no filter and no town page.

**The importer is idempotent against the DATABASE, not the ledger**, and that is
not a nicety. The first run died on a socket timeout after 307 of 500 one-at-a-
time inserts, and `Seen.save()` only runs at the end — so the ledger was never
written and a naive re-run would have duplicated all 307. It now reads back the
UIDs already in `events` (they are in each `source_note`), writes in batches of
50, and checkpoints the ledger after every batch.

**161 of the 500 landed unsorted**, on purpose: types are proposed only from
what a title actually says. That is the same choice `scrape_events.py` makes for
the feed's 'Sport' category — a person sorts them, nothing is invented.

It is **not on the schedule yet**. `.github/workflows/events.yml` runs the other
two scrapers; adding this one is a step nobody has taken.

## Moshtix, and the Festival blind spot it exposed

**`eventlib.jsonld_events` was dropping every festival, silently.** The test was
`'Event' in @type`, which catches MusicEvent, EducationEvent and SportsEvent —
and `'Event' in 'Festival'` is False. schema.org names three Event subtypes
without the word in them: **Festival**, `Hackathon`, `CourseInstance`. Moshtix
types Spilt Milk and the Queenscliff Music Festival exactly that way, so both
read as zero events on a page that plainly had them. `is_event_type()` handles
the three by name now. This is the same family as the Eventbrite `EducationEvent`
note — a substring test standing in for a type hierarchy.

Two Moshtix venues are registered:

- `Queenscliff Town Hall` (place 138) — 2 gigs, both `high`.
- `Kardinia Park Precinct` (place 139) — Spilt Milk, 19 Dec 2026. Pinned to the
  **named feature**: Moshtix gives 354 Moorabool St, Nominatim has no house
  number there and offers two street segments, but "GMHBA Stadium" resolves as
  `type=stadium`. Ask for the feature by name before its street.

`Queenscliff Music Festival` was already event 33 — verified, dated off qmf.net.au.
Moshtix added only the missing `ticket_url`, with its `_gl=` analytics parameters
stripped. Worth checking before creating anything from a link: this one would
have been a duplicate.

## Why the venue page is read but its links are not

`Queenscliff Town Hall` (place 138, 50 Learmonth St, pinned house-level) was
added 27 Aug 2026 with its Moshtix venue page as `events_url`. It reads: the run
says *"schema.org on the page (2)"* and it imported both gigs at `high`.

**Moshtix is deliberately NOT in `TICKETERS`.** Its event pages do carry clean
JSON-LD, so adding the pattern is a one-liner — and that was tried, and the dry
run caught what it did. A Moshtix **venue** page links to *other venues'* shows,
so following those links off Queenscliff Town Hall proposed twelve gigs at The
Night Cat, Brunswick Ballroom, Howler and The Toff in Town, and offered to
create those rooms. That is this project's own rule broken: a listing must never
claim a ticket link it cannot prove is its own.

Removing the pattern did not disable Moshtix — **it fixed it.** With no ticketer
match the scraper falls back to the venue page's own JSON-LD, which lists only
that venue's events, and gets exactly the right two. The lesson generalises: for
a platform whose venue page is already a correct listing, the own-listing path
is the safe reader and link-following is the unsafe one.

## Verifying — what a machine may claim, and what it may not

**The old rule was "nothing is ever inserted verified".** It was protecting two
different things at once, and Scott pulled it apart on 28 Aug 2026: *"surely a
machine can check these as part of the automation?"* It largely can.

`verified` was conflating **"the machine's checks passed"** — mechanical, and
already performed before any insert — with **"a person judged this belongs on
the board"**, which no scraper can do. Refusing to state the first left a queue
nobody worked, and bulk-accepting it (25 Aug) made the flag mean nothing.

**`scrape_venues.py` now auto-verifies a row when all four hold**, and only then:

- `date_confidence == 'high'` — read off a first-party page **and** the weekday
  printed there matched the date. A page saying "Saturday 17 Sep" when the 17th
  is a Thursday refutes itself and never reaches this point.
- a real `starts_on`,
- a `place_id`, so the venue is a curated row rather than a guess,
- a `source_note`, which says so: *"auto-verified: first-party page, printed
  weekday matched the date, linked to a known place"*.

A `medium` row — a date pulled out of a `<title>` by regex, with no weekday to
check it against — still goes to the queue. So does anything unlinked or
undated. Judgement a machine cannot make (is this worth listing, has it been
cancelled, is the venue attribution right on an ambiguous page) stays a
person's, and the queue is how it is asked for. The Moshtix case is the standing
example: every one of those twelve Melbourne gigs would have passed a mechanical
check.

**Deliberately NOT applied retrospectively.** 527 of the 785 waiting rows would
pass the gate today — but 500 of them are the library import, which is exactly
the set Scott has flagged as needing filtering. They pass every machine test and
fail the judgement test, which is the distinction the gate exists to draw. The
gate is forward-looking only.

### Test this source — a button that runs the check

Every source with a URL has one, and it does the work rather than describing it.
`action: 'probe'` on `/api/admin` fetches the page **server-side** and reports
what a scraper would actually find: a JSON feed and its item count, schema.org
events and how many, links to a known ticketing platform, or nothing
machine-readable.

**Why the server and not the page.** The Vercel function is not a browser, so
CORS cannot block it, and it is not ClaudeBot, so a site that disallows that
crawler — Coast & Bay, Humanitix — is still readable. It identifies as
`whattodo-janjuc`, the same as the scrapers, and reads robots.txt first. That is
how the Coast & Bay question above got answered after sitting open for days.

It refuses private addresses (`localhost`, `10.*`, `192.168.*`, link-local),
because an endpoint that takes a URL from a browser must not become a way to
read things only the server can reach.

**A robots.txt pattern is not a prefix, and treating it as one is a false
refusal.** The first version truncated at the first `*`, so `/*?add-to-cart=`
became `/` and matched every path on the site. Coast & Bay and Patagonia both
came back "robots.txt says no" when both plainly allow the pages we wanted. `*`
is now expanded to `.*` and a trailing `$` anchors the end. **Fail-closed
matching is worse than useless if the pattern is wrong** — it hides a working
source behind a rule the site never wrote.

### Where an event came from

The Events table has a **Source** column and an *Any source / Scraped
automatically / Added by hand* filter. It needed no new data: `added_by` is what
every scraper already stamps on an insert, and it had simply never been shown.
A green ✓ means no person typed it.

**`date_confidence` is not shown on the Events list at all** (removed 28 Aug
2026, Scott's call — it was briefly headed "Date from", which read as though the
cell held a date). It still appears in the **Review** queue, where it is
actually load-bearing: deciding whether to approve a row is the moment the
question matters. On a list you are scanning, it was a column of the word *high*.

**`km` is NOT a flag.** Distance is deliberately left null on every import until
there is a way to compute a driving distance — a standing decision, not an
omission. Flagging it put *no distance 643* at the head of the Events worklist
and *261* on Activities: the largest item on a list of things to fix was the one
thing nobody intends to fix by hand. A worklist that leads with something you
have decided not to do teaches you to ignore the worklist.

**`/admin` is 1640px wide, not the site's 1400.** It is a desktop-only back
office whose tables run to eleven columns; at the site's reading width the
Source column fell off the right edge. The tables also cap their long cells and
sit in their own `overflow-x`, so widening the page was the last thing tried
rather than the first.

### One row is one line

The Events table was three facts deep in places — date over time, venue over
town, flags under the name — so a row could be 121px and the column could not be
scanned. Each fact now has its own column: **When · Time · How often · Venue ·
Town · Link · Date from · To fix**. All 683 rows are 39px.

**Anything with no natural length limit is cut, with the whole value on the
`title`.** A name, a venue, a `time_text` that is prose in some rows ("34km
8.30am from Queenscliff; 17km about 9.40am from Drysdale"), a list of types.
`white-space:nowrap` alone is not the answer — it stops the wrap and pushes the
table sideways instead, which is what happened first. `td.cap` does both: cut,
ellipsis, tooltip.

The table lives in its own `overflow-x:auto`, so a wide table scrolls itself
rather than the page.

**Link** shows the host and first path segment — enough to tell an Oztix ticket
page from the venue's own site — links out, and carries the full URL on the
tooltip.

### No chips in a table, and no badge that restates its own row

Two passes with Scott on 28 Aug 2026, and the rule that came out of them:

**A badge that repeats its own row is noise.** Places carried `NO KIND` beside a
Kind column reading "—", `NO WEBSITE` beside an Automation of *no website on
file*, `NO PIN` beside a Pinned of *no*. Every flag except `coarse pin`
duplicated a column the row already had. The badges are gone; `coarse pin`
became a third state on Pinned, which is where the only non-duplicated one
belonged. Activities kept `maps search` and `unverified` — nothing else on that
table says either — but as **a "To fix" column of plain words**, not chips.

**A bordered pill inside a cell is a box drawn round a word that already has a
column.** One CSS rule strips every `.tag` inside a `td` to plain coloured text:
the colour is the signal, the box never was. The filter buttons above a table
keep their shape, because those are controls rather than data.

**The tab intros went too**, the same call already made for Automations. What is
left above each table is a heading, a search box and the filter chips.

**There is no Address column, and adding one was a mistake worth recording.**
Scott caught it: Aireys Inlet Primary School has no address, has a pin, and is
on the map. That is not an edge case — **72 of 140 places are pinned without an
address**, 47 because a named feature resolved in OpenStreetMap (a school, a
stadium, a pier answers to its own name) and 25 from the library feed's own
`GEO`. A yes/no Address column marked the majority of the table "no" for a field
that is not required and whose absence means nothing.

What is actually actionable is much smaller, and is a chip now: **`can be
pinned`** — an address on the row and no coordinate made from it, which is a
geocode waiting to happen. There are six. The eight with neither are already
covered by `no pin`.

The general shape: a column that is mostly "no" is either a real crisis or the
wrong question. Check which before shipping it.

### The venue list

**One icon leads the Automation column so the table reads down it**: a **sync**
mark means a machine keeps this venue up to date, a **hand** means a person
does. Both are Lucide (`refresh-cw`, `hand`), taken verbatim from
lucide-static 1.37.0 under its ISC licence and kept as `<symbol>`s with a
`<use>` per row — not redrawn, and not four paths inlined 140 times.

- **sync** — then a green pill naming what reads it (*own listing + Oztix*,
  *Humanitix*), then when it last read. 27 venues.
- **hand** — then *last added 3 days ago*, amber past six months. 79 venues.
- **neither** — *nothing added yet*, for a venue nothing has ever been attached
  to.

**Which icon a row gets is evidence, not a label anyone maintains.** A hand
means it has listings and nothing reads it; the day a feed starts working the
row changes by itself. Church Geelong is the case that prompted it: robots.txt
on its ticketing subdomain is `Disallow: /`, its own site publishes no
structured data, and Scott keeps it current by hand.

**31 places host nothing and have nothing to read** — a playground, a carpark, a
beach — and they are held back by default with a button that counts them and
brings them back. Searching, picking a kind or picking a chip lifts the hold, so
nothing is ever silently absent. Same bargain the board makes with the at-home
listings.

**That hold is EVIDENCE, never a guess from `kind`.** Princess Park is a park
and hosts the Queenscliff Music Festival; the Barwon Heads riverbank hosts a
market. A rule that hid parks would hide both. The test is "has never had an
event **and** has no feed to get one from", which is a fact about the row rather
than an opinion about the category.

The Places tab answers "what reads this venue, and how much is it carrying":
kind, town, the **automation** (state, what reads it, when it last read) and
**events** (upcoming, total, plus any activities linked to it). Sortable by most
events or automated-first. It is the same `sourceRows()` the Automations tab
uses, so the two can never disagree.

### "Needs a person" says which person does what

A status that asks for a human and does not say what they should do is a dead
end — Scott's question, 28 Aug 2026. Every state that asks for you now carries a
one-line **What to do**, first in the source drawer: the exact curl for Coast &
Bay, the API-or-JSON-LD choice for Eventbrite with the count waiting behind it,
the two decisions blocking the library feed. States that need nothing say
nothing.

**Moshtix was mislabelled and it exposed a real hole.** It read as *needs a
person* while working perfectly. Two causes, both fixed: its `AGGREGATORS` entry
still said "none on file yet" from before it had venues, and the platform's
state was derived only from sources whose `via` names it. Moshtix is read
through the **own-listing** path precisely because it is not in `TICKETERS`, so
`via` never says Moshtix and the platform looked untouched. A platform's state
now falls back to its own venues' results.

The general trap: a derived status is only as honest as what it derives from,
and the run log is a snapshot. Both Moshtix venues were registered *after* the
last run, so nothing in the log mentioned them — which is why the honest word
for it is now *not tried yet* rather than *needs a person*.

### The Review tab

`/admin` → **Review**, with a count in the tab. Everything unverified, grouped
by `added_by`, because the useful gesture is nearly always *approve all of
these* rather than one at a time — 500 library rows are one decision, not five
hundred. Each group has an **Approve all**; each row has Approve, Delete, and
its name opens the full editor.

Each row carries what you need to judge it without opening anything: the
**town** (the first question is always "is this even in the region"), the venue
under it, the types or *unsorted*, the date and time, a red **in the past**
where the date has already gone, **no place** where an event has no `place_id`,
the confidence, and a `source ↗` link to the page it was read from.

**`/admin` loads `notice-vocab.js` for that**, rather than reimplementing the
suburb rules. A back office that disagreed with the board about which town a row
is in would be worse than useless. Checked for global collisions before adding
the tag — 26 names against 64, none shared. Note this is why Colac and
Bannockburn resolve at all: they were added to `SUBURBS` for the library
branches, and without that those rows would show no town.

Approving is one request for a whole batch (`action: 'verify'`, a table and a
list of ids, `id=in.(…)`), capped at 600. **It refuses a batch where any row has
no `source_note`** — verifying those would record that somebody looked when
nothing says what they checked, which is the exact failure this file already
notes about the 25 Aug bulk accept.

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

### The Automations tab — rebuilt 28 Aug 2026 after a UX audit

Scott said he was confused by the layout and the amount of body copy. Measured
before touching anything: **736 words of prose on one tab** — seven explanatory
paragraphs plus 460 words inside the table cells. Two and a half paperback
pages, and every word explained *why* rather than showing *what*. CLAUDE.md is
where the why belongs; it had been duplicated into the interface.

What he asked for, and what the tab now is:

- **Almost no prose.** Visible chrome is ~164 words. Everything that used to be
  printed into a cell — how a source is read, its caveats, what to do about it —
  is in a **drawer behind a click**. Nothing was deleted; the `how` and `note`
  fields on `AGGREGATORS` are still the copy, they are just not in the table.
- **One list, not two sections.** Aggregators and venues were two headings, two
  subheads and two paragraphs explaining the difference. They are one table with
  a Kind filter: the distinction is a property of a row, not a reason to split
  the page.
- **One status per row**, not three columns. `AUTOMATED · READING · 3 days ago /
  +2 / 5 all time` was five tokens for one idea; it is a state tag and
  `3 days ago · +2`.
- **Desktop only**, Scott's call — so the tables are tables and no effort goes
  into stacking them on a phone.

The tab went 22,858px → 1,442px. The four-stat overview stayed exactly as it
was: it was the one part that already worked, and it became the model.

**`fbweekly` is a state, not a failure.** A place with a Facebook page and no
`events_url` cannot be read by anything, so it is a standing weekly job for a
person rather than a broken automation. It says *Facebook — check weekly*.

### The venues came off Automations — 30 Aug 2026

Scott's question: *"the Automations tab should just have the aggregators no?
The places are in the places tab, is that duplication?"* It was. The tab listed
147 sources — 8 aggregators plus **every one of the 140 `places` rows** — and a
venue's Status column was the same `sourceRows()` output the Places tab already
prints in its Automation column. One fact, two screens, and a venue with two
homes; the thing this project has paid for repeatedly.

**Automations is the eight aggregators and nothing else now.** That list is
genuinely nowhere else: it is the parser story, hand-written in `AGGREGATORS`,
and it has no row in any table.

**What the venue list was actually for is the worklist under it**, and that
stayed. The state chips are now venue-only counts, biggest first, and pressing
one **hands the set to the Places tab** — `showVenueState()` sets `PFILTER.state`,
clears every other filter and switches tab. `no website on file 75` lands you on
exactly 75 rows, where the town, the address, the event counts and the editor
already are. Two things make that honest:

- **The chip clears the other filters**, or the number on it would not match the
  list it lands you in, which is the whole promise.
- **The quiet hold lifts for it.** Places holds back the 31 that host nothing and
  have nothing to read; a state filter is asking, the same as a search.

**A venue's automation status is on the venue's own editor drawer** —
`automationPanel()`, above the fields. That is where the two things a table cell
could never hold went: the per-state **What to do** line, and the scraper's own
**hint** (*found at / — set events_url to lock it in*). The **Test this source**
button moved with them, so the probe is still one click from a venue.

**The hint is deliberately NOT a sub-line in the Places table.** It was tried and
it is a sentence — *one row is one line* is the rule that table already keeps.
It was also attached to the wrong branch on the first go, under *not automated*,
where a hint can never appear: hints come off a run, so only a source that was
read has one. It rendered nowhere and looked fine.

**`.scrollbox` survived on its own merits.** Its comment said it existed for the
136-row venue list, so deleting that list looked like reason to delete the CSS —
but the Review queue uses it too, and a 500-row library group is exactly the case
it was built for. Grep for a class before removing it on the strength of its
comment.

The Kind filter and the source search went with the venues: eight rows need
neither. `SRCFILTER` is gone entirely. The eight rows now print each
aggregator's own `what` (*Ticketing platform*, *The shire's whole calendar*)
where they all used to say "aggregator".

### Three columns, and the 401 they found

Scott asked for more columns on what was left. The three added are **Runs**,
**Events** and **Still to come**, and the first thing they did was expose a
source that had been failing silently for days.

- **Runs** — *Mon & Thu* / *by hand* / *not built*, off `AGGREGATORS.auto`.
  A different question from Status: Status is what the last run did, Runs is
  whether the thing fixes itself. Geelong Regional Libraries reads perfectly
  and is on no schedule, which Status alone can never say.
- **Events** — how many events in the database came through it. **It needed no
  new data**: every importer writes the page it read into `source_note`, so the
  host IS the provenance. `added_by` is the tidier column and cannot answer
  this — `venue-feed` covers Oztix, Humanitix, TryBooking and Moshtix at once.
- **Upcoming** — of those, the ones not yet past. 500 library events of which
  467 are ahead is a different fact from 500 that have all gone, and it is the
  half that says whether a source is still worth having.

**Two headings were wrong for one turn and both were Scott's catch.** It shipped
as *Still to come*, which does not say what it counts, and the venue count went
under **Reads via** — a heading written when that cell held *own listing +
Oztix*, which is HOW a source is read. It now holds a count of what it COVERS,
and the heading never moved with the data. They are **Venues** and **Upcoming**,
and the cell stopped carrying its own header: "6 venues" under a column called
Venues is the badge-that-repeats-its-row rule again. Three plain counts side by
side read as numbers or not at all. The drawer keeps the names.

The venue rows on the Places tab still say *TryBooking* / *own listing* in their
Automation cell — that is genuinely how, and `via` still means how there.

**EVENTBRITE IS 401ing AND HAS BEEN READING AS GREEN.** Three of its four
organisers — Creative Geelong Makers Hub, Mt Rothwell, Torquay Bowls Club —
answer `401` every run, so nothing has ever been imported through the API.
`EVENTBRITE_TOKEN` in the GitHub Action is missing or expired. Set it with
`gh secret set EVENTBRITE_TOKEN` from a terminal, never the web form.

**Why nobody saw it: `source_state()` in `run_log.py` DEFAULTS TO SUCCESS.**
Anything a scraper printed that was not one of five known failure phrases came
out `read` — green, "reading". *"Eventbrite API failed — Eventbrite 401 for
organiser 28043893657"* matched none of them. There is a `failed` state now, and
a `manual` for a line asking for a token. **Anything added to the scrapers'
vocabulary of failure has to be added here too**, or it is silently a success.

The fix only takes effect from the next run, because the state word is baked
into `run_log.json`. So `repair()` in admin.html re-reads the run's own
sentence — which is in the log verbatim — and upgrades a stored `read` that
says *failed* or *error*. **Delete it once the logs have rolled over.**

An aggregator whose venues disagree now takes the error: one venue reading is
not a working platform when the other three are 401ing, and an error is nearly
always platform-level — a rejected token, a changed API — rather than per-venue.

**Two AGGREGATORS entries were stale prose and the Runs column turned one into
a visible lie.** Eventbrite still said "deliberately not scraped" two days after
the API was wired up, so it printed *not built* beside a Status of *reading*.
Coast & Bay still said the feed was "unconfirmed" after the Test button
confirmed it. A column that cross-checks hand-written prose against live data is
worth having for that alone.

### A site-based aggregator has venues too — they are in its events

Scott: *"geelong regional libraries should be considered an aggregator, it's an
RSS feed and has lots of venues."* It was already in `AGGREGATORS`; what it was
missing was the venue count, because it was the only source whose venues are
not written down anywhere. A platform's venues are the `places` rows carrying
its URL. **A site's venues are in what it brought in** — 500 events across 19
branches, every one with a `place_id`, because the iCal carries LOCATION and GEO.

**`places` and the event-derived list must stay apart, and folding them together
broke three rows before it was caught.** `places` is the registry and it is what
`state` and `last read` are derived from — so adding the 19 branches made each
branch's own website read, by `scrape_venues`, count as the FEED reading:
Geelong Regional Libraries claimed *reading · 30 min ago · +18* when the feed
has not run since the import, and Surf Coast Events grew from nothing to 21
venues. Organiser-is-not-the-venue in one more hat.

`via` reads the registry for a platform and the events for a site; nothing else
changed. Note a site's `places` holds the feed's own log entry, which is what
carries its history and is not a venue — Surf Coast Events read *1 venue* and
meant itself, which is why the row's `places` field is now empty for a site and
`branches` holds the real list.

Its label said "a real RSS feed" and is now "one calendar feed": **it reads the
iCal**, and the reason is three paragraphs of this file.

### Every date is Australian and carries its year

Scott, 30 Aug 2026. `melb()` gained `year:'numeric'` — *Mon, 31 Aug 2026 ·
7:17 am* — and `dmy()` turns a stored `YYYY-MM-DD` into *29 Aug 2026* for the
Events list, the Review queue and the drift alarm, which all printed the raw
ISO string. A back office is read months after the fact, beside dates running
into next year, so the year is what stops a row being misread.

**`dmy` splits the string rather than passing it to `Date()`.** A stored date is
a DAY, not an instant; `new Date('2026-08-29')` is UTC midnight and prints the
28th at +10. That is the `nextDate` bug, which this project has already paid for
once. The editor's own `<input type="date">` fields stay ISO — that is the value
format HTML requires, and the browser renders them in the reader's locale.

**Two traps when editing this file with a script.** Both were hit in one
sitting: replacing a range that starts at one function and ends at a later
marker silently swallowed the whole sources module, which had been written
between them; and rebuilding the tab's markup left `</section></section>`,
because the slice-end marker already carried the closing tag. Assert on what a
replacement removes, not only on what it finds.

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

## The email inbox — a source that answers back

Built 30 Aug 2026, because the automation ceiling is not the parsers. **18
sources have a website with nothing machine-readable and 63 have no website at
all** — those are not going to grow a feed. They will email a person. So this is
the one route that scales for them, and it works by asking rather than parsing.

    inbox                 Supabase table: received_at, from_addr, to_addr,
                          subject, body, raw, status, event_id, note
    api/inbox.mjs         POST endpoint — receives a message, stores it
    tools/email-worker.js Cloudflare Email Worker — the sender
    /admin  → Inbox tab   the queue, and a paste box

**The table has no anon policy, and that is the one deliberate difference from
everything else here.** Every other thing the back of house shows is already
public — the listings, the places, the vocabularies — so the page reads them
with the anon key. An email is not: it carries whoever sent it and whatever they
wrote. It is read through `api/admin.mjs` with the service key, so the Inbox tab
needs the password even to *look*, which no other tab does.

**Nothing in the path interprets the message.** The endpoint stores what
arrived; a person turns it into a listing. That separation is the whole design —
an inbound endpoint that wrote events directly would be a public form with no
review, which is the one thing this project's write path has never allowed. The
message's own markup is stripped for the readable `body` and never evaluated,
and `raw` keeps what actually came in, because the email is the evidence for
whatever gets written from it. Same rule as `run_log`'s raw scraper text.

**The endpoint refuses everything without `INBOX_SECRET`**, which is the correct
failure for a public URL: an open one is a spam target within a day. It answers
`501 no_secret` when unconfigured and `401` to a wrong one, compared
timing-safely on digests like `ADMIN_PASSWORD`.

### The address does not exist yet, and the reason is DNS

**`notice.place` is on Vercel's nameservers** (`ns1/ns2.vercel-dns.com`, checked
30 Aug 2026) and has **no MX records at all**. Cloudflare Email Routing — the
free, no-third-party, no-volume-limit answer, and what `tools/email-worker.js`
is written for — needs the whole zone on Cloudflare. That is a nameserver move
on a live site, so it is Scott's call and was not done unprompted.

Two routes, and the tradeoff is the only thing to decide:

- **Move the zone to Cloudflare.** Free forever, no third party in the mail
  path, and the worker is already written. Cost: re-adding the Vercel records
  (`A 76.76.21.21`, `CNAME cname.vercel-dns.com`) at Cloudflare, and the site is
  down if they are wrong. Reversible.
- **Keep Vercel DNS, add MX pointing at an inbound-parse service.** No
  nameserver move and no risk to the site. Cost: an account, and that company
  sees the mail — which is cheap here, since the mail is venues sending gig
  listings. **This is the route Scott chose, 31 Aug 2026**, on noticing the
  obvious thing: Vercel does DNS, not mail, so it can point mail somewhere but
  cannot receive it — and pointing is all that is needed.

  **Postmark**, because it allows **custom headers on the webhook**, so the
  `x-inbox-secret` header works with no change. MX `@` → `inbound.postmarkapp.com`, priority 10.
  **SendGrid Inbound Parse was rejected**: it POSTs `multipart/form-data`,
  which Vercel does not parse into `req.body`, so it would need a body parser
  this project does not have.

  **The MX goes on the apex**, so the address is `events@notice.place` — the
  one you would print on the site. A subdomain would leave the rest of the
  domain free for a mailbox one day, at the cost of `events@inbox.notice.place`,
  which nobody would ever type. The apex claims all mail for the domain, so if
  Scott ever wants `scott@notice.place` this has to move first — one MX record,
  not a one-way door.

`INBOX_SECRET` goes in **two** places with the same value — the Vercel project,
and the sender (Postmark's webhook custom header, or `wrangler secret put` on
the Cloudflare worker).

**The endpoint reads three shapes and that is deliberate.** Postmark capitalises
its fields (`From`, `TextBody`, `RawEmail`), the Cloudflare worker sends
lowercase, and the secret arrives as either an `x-inbox-secret` header or basic
auth in the URL. Reading all of them means switching sender later is a DNS
change and nothing else — neither shape is the "real" one.

**Until then the Inbox tab works anyway, via "Paste an email".** That is not a
placeholder: a venue's "here is our September program" email is useful today,
and it goes into the same table and the same queue with `from_addr` recording
that a person put it there. The forwarding address is an upgrade to the front of
this path, not the path itself.

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

**Read through the API since 28 Aug 2026** — Scott has a token. `eventlib`
gained `eventbrite_org_id()` and `eventbrite_events()`, and `scrape_venues.py`
reads an organiser through the API at step 2b, before any link-following.

**Needs `EVENTBRITE_TOKEN` in the environment**, and nowhere else — never in a
place row, never in the page, never in a log line. Two homes:

    gh secret set EVENTBRITE_TOKEN        # the scheduled Action; the one that matters
    echo 'EVENTBRITE_TOKEN=…' >> .env     # only to run it from a terminal

Set it from the terminal, not the web form — this project has already put the
text of a shell command into a secret that way, and the failure surfaced three
layers later as `unknown url type`.

**First real run: 401 on all three** (30 Aug 2026). The secret was set and
reached the job — the log shows `EVENTBRITE_TOKEN: ***` — and Eventbrite
rejected it. A 401 is about the token itself, so re-running never fixes it. The
usual cause is the wrong one of Eventbrite's four credentials: it must be the
**private token** from eventbrite.com/platform/api-keys, not the API key, the
public token or an OAuth client secret. A trailing newline from a prompt does it
too, which is why the token is now `.strip()`ed before use.

One command settles it, and needs no run:

    curl -s -H "Authorization: Bearer <token>" https://www.eventbriteapi.com/v3/users/me/

A good token returns your Eventbrite user; a bad one returns `NOT_AUTHORIZED`.

**Without the token those rows say so** — *"Eventbrite — set EVENTBRITE_TOKEN to
read it"* — rather than reading as no events, which is the difference between a
source that is empty and one that is not being asked.

Three things the implementation gets right and a naive one would not:

- **`start.local`, not `start.utc`.** The API gives both; the local one is the
  wall time at the venue, which is what a listing should print. Using UTC would
  shift every Melbourne event by ten or eleven hours — the `nextDate` bug again.
- **`expand=venue`**, so each event carries the room it happens in. That is the
  whole reason the API beats the page here: the organiser is not the venue, and
  all nine Creative Geelong events name the Makers Hub rather than Creative
  Geelong Inc.
- **It pages.** The API caps a page at 50 and reports `has_more_items`; an
  organiser with more would otherwise be silently truncated.

`API_INSTEAD` still holds `Eventbrite`, but its meaning has changed: it now
stops the link-following branch touching a loose `/e/` page found on somebody's
website, because the API needs an organiser id and a stray ticket link does not
carry one.

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

### The produce pass — 38 rows, 28 Aug 2026

12 market events (156–167) and 26 activities (465–490). market 13→25, produce
17→42, nursery 7→10, farm life 6→9. **Every mechanical rule held**: no `km`, no
coordinate under four places, no Google Maps search url, every row sourced, all
38 landing in the town their address names, and all 26 activities carrying an
explicit `kind: "venue"` — which matters, because `KIND_OF` maps `farm life` to
*spot* and Lomas Orchards would otherwise have been classified as one.

Three tooling faults it found, all now fixed:

- **`nearby.py --kinds produce` silently did the wrong thing.** The parser read
  only `--kinds=produce` while the docstring showed the space form, so a sweep
  run exactly as documented fell back to `food` AND swallowed `produce` as part
  of the town name. No error. Both forms work now. *Silently wrong is the worst
  failure a search tool can have.*
- **`season` is a `text[]` and nothing said so.** A free-text season failed with
  a raw Postgres `22P02` **after three rows of the batch were already written**.
  `check()` validates it now — `any/spring/summer/autumn/winter` — so it fails
  before anything is written.
- **`shop=florist` was in the produce sweep** and contributed nine Geelong flower
  shops, a quarter of that town's misses. Removed.

**The by-hand town check beat the map, and not narrowly.** Grubb Road, Wallington
is an unmapped farm-gate strip — Lomas Orchards, Van Loon's Nursery, Wattle Grove
Honey, Wallington's Local Pantry — and `nearby.py` returned *zero* for Wallington.
Drysdale's four OSM names were all servos and bottle shops while the real town
holds Tuckerberry Hill, Bellarine Smokehouse and the Bellarine Farm Gate market.
**OSM maps shopfronts, not farm gates.** The `otwayharvesttrail.org.au` guide and
`bellarinefarmgate.com.au` between them found most of what the map missed and are
worth treating as an annual import.

Findings worth not re-researching:

- **Event 14, Night Markets (Geelong After Dark), is dead.** The festival ran
  2014–2019 and did not return; `geelongafterdark.com.au` has been taken over by
  an auto-generated news portal, so **do not cite that domain**. The Johnstone
  Park night market was the Nightjar Festival, whose operator has moved to
  Torquay. Nobody publishes anything at Johnstone Park on 2026-11-07.
- **Event 21, Community Market at the Anglesea SLSC, does not exist.** Neither
  the club's site nor Anglesea Community House — the row's own `info_url` —
  mentions a market there.
- **There is no visitable olive grove on the Bellarine**, no cherry farm and no
  apple u-pick. The only u-pick is strawberries at Lomas and berries at
  Tuckerberry Hill.
- **No recurrence word fits "first and third Friday"** (Anglesea Twilight Market)
  or "every two months". They are null, which reads as *unknown* when it means
  *no word for this*.
- `SUBURBS` strands a whole u-pick cluster at **Gellibrand** — Otway Blueberries,
  The Little Organic Paddock, Glen Loch Apple Farm, Country Dahlias — plus
  Murroon and Bannockburn, where two dated first-party Golden Plains markets sit.

**The twelve new markets were written with no `place_id`, so none could be
plotted.** An event has no coordinate of its own — it inherits one from its
place — and nothing in the tooling says so out loud, which is why this was the
third pass in a row to hit the same class of fault. Three were linked to
existing pinned rows on 28 Aug 2026 (156→70 Princess Park, 160→77 WG Little
Reserve, 162→21 Little Creatures Brewery); **the other nine need `places` rows
built and geocoded**, which cannot be done from `sync.py`:

    159 Wallington Primary School      163 Barwon Heads Riverbank, Ewing Blyth Dr
    161 Mirambeena Park, Armstrong Ck  164 Portarlington Senior Citizens Hall
    157 Apollo Bay Youth Club          165 South Geelong Primary School
    158 Apollo Bay Foreshore           166 Little Malop Street Central
                                       167 Point Lonsdale Primary School

**Six more were built and linked 28 Aug 2026** — places 109–114: Apollo Bay
Youth Club, Wallington Primary School, Portarlington Senior Citizens Hall, South
Geelong Primary School, Little Malop Street Mall, Point Lonsdale Primary School.
9 of the 12 markets are on the map now.

**The three left are left on purpose, and the reason is the rule.** Every one of
those six pins is a *named OSM feature* — a house number, a school polygon, a
pedestrian mall. The street queries were rejected: "65 Wallington Road" returned
two segments **4.5 km apart**, Little Malop Street three up to **1.2 km** apart,
Ewing Blyth Drive two **600 m** apart. Apollo Bay Foreshore, Mirambeena Park and
the Barwon Heads riverbank have no named feature at all, and the reserves
Nominatim offers instead are a different reserve from the one each market names
— Barwon Heads Community Park is 1.5 km from Ewing Blyth Drive. Each of the
three carries the reason in its own `source_note`.

The generalisable bit, which cost an hour to learn: **ask for the feature by
name before you ask for its street.** A school, a park and a mall are named
things in OSM and resolve to the grounds; the same place asked for as an address
resolves to a road centreline that is a coin toss between segments.

`RESEARCH_RULES.md` now tells a pass to check `have.py places` for every event
and to log the address when there is no row. That is the rule; it is still prose,
so expect it to be broken until `check()` can warn on a dated row with neither a
`place_id` nor a venue string that names no single place.

Six market rows need /admin: id 6 (Belmont Market — hours out by an hour at both
ends, wrong name, Maps-search url), 14 (delete), 21 (delete), 40 (Drysdale — time
is "Sunday morning"), 88 (Winchelsea — venue moved to the Leisure Time Centre),
22 (Baines Crescent — a permanent outlet precinct, not an event).

### The arts pass — 29 rows, 28 Aug 2026

theatre 1→7, art gallery 6→14, museum 10→18, cinema 13→19, arts 16→20. Group
55→87. Every mechanical rule held again, and every one of the four events
carries a `place_id` — the first pass where the place-less-event trap was
avoided rather than discovered.

**It found the worst bug `nearby.py` has had, and it was mine.** `label` was
read as `amenity or shop or craft or landuse` — a second list that had to be
kept in step with `KIND_TAGS` and was not. Adding the arts category asked
Overpass for `tourism` and `historic`, got the data back, and cached all **272**
of them with `label: None`, so the filter dropped every one. Every museum,
gallery, public artwork and memorial in the region reported as not existing.
The label is derived from `ALL_TAGS` now, so a new tag key cannot go missing.

**That is the third time a filter in that script has silently discarded rows**
(the `--kinds` space form, the stale-cache category, this). The generalisable
sentence, which the produce pass wrote first: *a search tool that returns
nothing looks identical to a region that contains nothing.*

**`cultural` gained zero rows and that is the correct answer, not a gap.**
Worked strictly to the brief — Wadawurrung Traditional Owners Aboriginal
Corporation, Parks Victoria, or a council page written with Traditional Owners,
and only where the source says the place is open to visitors. wadawurrung.org.au
names no visitor-facing site; the shire's Aboriginal heritage page names none
either; the Wadawurrung Cultural Education Sessions sell through Humanitix,
which a Claude session must not fetch (the Action can). **Bunjil Geoglyph was
deliberately filed `arts`, not `cultural`**: Parks Victoria's own page calls it
a 2006 work by artist Andrew Rogers for the Commonwealth Games and makes no
Wadawurrung claim about the geoglyph, so filing it as a cultural site would be
writing significance the source does not.

**Surf Coast Shire's Community Arts Facilities page is the source that did the
work** — nine rooms with addresses, and nothing on the map would have found
Yellow Gums or the Deans Marsh kiln. Winchelsea returned 0 from the sweep while
having a working heritage theatre with a monthly film club in it.

Corrections needing /admin, in order of seriousness:

1. **Event 7, Surf Coast Arts Trail, is corrupt.** `starts_on 2027-08-07`,
   `ends_on 2026-10-12` — the end is ten months before the start. The real 2026
   Trail ran 1–2 August 2026 and is over; no 2027 dates are published. Its
   `info_url` points at surfcoastarts.com rather than surfcoastartstrail.com.au.
   **This is the event this project's whole date rule is named after.**
2. **Events 30 and 51 are one festival** — ANGAIR Wildflower & Art Weekend and
   Angair Wildflower & Arts Show, both 2026-09-19. Merge onto 30, keeping 30's
   first-party url, 51's `place_id` and 51's `ends_on`.
3. **Places 98 and 102 are a duplicate** — both the HOOP Gallery. Needs the
   three-step alias merge; the new gallery listing links 98.
4. `Geelong Arts Centre` carries `art gallery` and not `theatre`; `Lorne
   Theatre` carries `cinema` only though its own masthead says music/theatre/
   film; `Geelong Gallery` is typed `museum` and is the region's public gallery.

**The clearest vocabulary gap the project has found: a monument or landmark.**
The Great Ocean Road Memorial Arch is a genuine stop and there is no honest type
for it — not `arts` (a commemorative structure is not an artwork), not
`cultural` (that means Wadawurrung Country), not `museum`, not `walk`. The same
gap swallows the Cliff Young statue, both lighthouses as objects, and ~40 war
memorials. Not forced into a type.

Still open: Costa Hall (real venue, no first-party address — GPAC's `/visit/
venues/` 404s); Tin Liz Gallery (OSM puts it at Mannerim, quiddityplace.com.au
puts it on Grubb Road, Wallington — two sources, two towns); Apollo Bay cinema
(robots.txt blocks five attempts, needs a browser); eleven Surf Coast galleries
with no reachable first-party page.

## The bike shop pass — 8 shops, 28 Aug 2026

Activities 520-527, all `kind = shop`. `mountain biking` went 17 → 33 across
the day's work.

    520  Trailhead Bike Co.          67 Great Ocean Road, Anglesea
    521  Forrest Bike Hire           16 Grant Street, Forrest
    522  Bike Matters                11/12, 31 Baines Crescent, Torquay
    523  De Grandi Cycle Works       36 Mercer Street, Geelong
    524  Hendry's Geelong            Shop 3/170 Torquay Road, Grovedale
    525  Hendry's Ocean Grove        1/83 The Parade, Ocean Grove
    526  Bicycle Superstore Geelong  33-35 Pakington Street, Geelong West
    527  Bicycle Centre Belmont      119 High Street, Belmont

**`nearby.py` gained a `bike` category** — `shop=bicycle|sports|outdoor` plus
`craft=bicycle`. The wide net is deliberate, the same argument as
`tourism=hotel` in the food net: a shop selling bikes beside surfboards gets
tagged `sports`, and a one-man repair place is often `craft=bicycle` with no
shop tag. `amenity=bicycle_repair_station` is deliberately excluded — that is a
tool stand bolted to a post, and it would put fake retailers on a type page.

**The cache guard earned its keep on the first run**: asking for `bike` against
a cache fetched for `arts, food, produce` exited with what to run instead,
rather than reporting the region as empty. That is the arts-pass bug, fixed and
now proven.

### Six of seven addresses agree with OSM to within 21 m

Each shop was geocoded from the address on its **own site**, then cross-checked
against the independent OSM node: 0 m, 1 m, 5 m, 11 m, 12 m, 21 m. Two matched
`type=bicycle` — the shop itself as a mapped feature, which is the best case
this project has had. Worth keeping as a technique: **first-party address plus
an independent map node is a stronger pin than either alone**, and it costs one
extra lookup.

Two matches needed reading rather than accepting, which is the standing rule:

- **Forrest Bike Hire matched `type=hotel`.** It is still right — the match
  carries `house_number 16, Grant Street` and the Forrest Guesthouse shares the
  address. The house number is what was checked, not the tag.
- **Hendry's Grovedale matched `type=clothes`**, a contributor's opinion about
  the tenancy. Same treatment.

### What the map could not do, and what it got wrong

**The 2 km sweep radius hides the Geelong suburbs.** `town_list()` folds
Belmont, Grovedale, Highton, Waurn Ponds and the rest into "Geelong", and a 2 km
circle on the city centre reaches none of them — `Bicycle Centre Belmont` is
3.0 km out and `Hendry's` 4.9 km. Both would have been missed. **Read the cache
region-wide and assign each POI to its nearest town** rather than trusting
`--all`; that is what found them. This is a real limitation of `--all`, not a
one-off.

**Two OSM rows were wrong in opposite directions, and both needed a person:**

- **`Good Cycles` in Geelong does not exist.** Its own site lists one location,
  Melbourne CBD. OSM is stale — the same lesson as MoVida Lorne and The Ridge.
- **`Bike Guru` in Colac closed in 2021**, after 11 years, announced by the
  business itself. Directories still carry it, and they **disagree about its
  address** (247 vs 39A Murray Street), which is its own warning.

**Torquay's own bike shop is in neither OSM nor any directory.** Bike Matters
was found by search alone. Its site advertises a Geelong studio as *coming
soon*, which is deliberately not listed: a page announcing a future opening is
not evidence of one, the Sustainable House Day call again.

**Its address came from Scott, because the business does not publish one.**
Checked properly before asking: the home page, the Torquay booking page and the
raw HTML of both carry no street address, no map link and no phone. Bookings go
through an embedded **Hubtiger** widget (`bookings.hubtiger.com`), which is why
there is a booking page and no shopfront details — worth knowing, because a shop
on that platform will look address-less to any scraper. Scott supplied
**11/12, 31 Baines Crescent, Torquay** on 28 Aug 2026, and that geocodes to a
Nominatim `type=house` match on number 31 which reverse-geocodes back to the
same address, so the pin is building level. A person handing over a fact is a
source, the same way a link a person pastes is not an invented URL — but the
row's `source_note` says it was Scott and not the site, because those are
different strengths of evidence.

Note Baines Crescent is the same street as event 22, the *Baines Crescent
outlets* — a light-industrial estate that is a permanent retail precinct rather
than an event, and still on the /admin list to be dealt with.

**Colac is unresolved.** Three names turn up — Bike Guru (closed), "The Bike
Shop", and Colac Bicycles & Repairs — and not one has a reachable first-party
page. Nothing was written rather than citing a directory.

**Watch for Torquay, UK.** Several searches for "bike shop Torquay" return
Devon, and "bike shop Victoria" returns Victoria, BC. Both were in the first
page of results here.

### These twelve rows are hand decisions, and the classifier would undo them

All twelve of the day's rows — four clubs and eight shops — were added to
`BY_ID` in `classify_kinds.py` in the same commit. **Every one would otherwise
come out a `spot`**: `mountain biking`, `cycling` and `volunteering` are all
things you go and DO, and `PRECEDENCE` ranks spot above both group and shop. It
is the 459-461 case again, twelve times over, and it is why that file says
adding a shop means adding a line.

**`classify_kinds.py` could not run to confirm it — FIXED 30 Aug 2026.** Its
exhaustiveness guard exited with *"KIND_OF is missing 1 type(s): kids"*: a
`kids` type and several hundred library events landed after that script was
written and nothing had taught it the word. The guard was behaving correctly;
the script was blocked, so `BY_ID` was verified by parsing the file instead and
**nobody saw the disagreement report for three days** — the twelve bike-pass
hand decisions among them.

`'kids':'venue'` is in `KIND_OF` now, filed with the dated types that only ever
reach an activity by mistake: a room that runs story times is a library, which
is a venue. With the script running again the standing report is four rows, and
**all four are the rules being crude rather than the rows being wrong**:

    496  Anglesea Performing Arts   group -> venue     a company you join
    513  Winchelsea Movie Club      group -> venue     a club you join
    514  Bunjil Geoglyph            spot  -> venue     `arts` maps to venue
    515  Geelong Bollards           spot  -> venue     `arts` maps to venue

The last two are the monument-and-landmark vocabulary gap this file already
records, showing up as a kind disagreement. Nothing to change; left alone, which
is what the script does without `--reclassify`.

**Read the exit code, not the output.** This blocker was briefly reported as
fixed on the strength of `python3 scripts/classify_kinds.py | sed …` printing
nothing alarming — but `$?` after a pipe is *sed's* status, so a script that
exited 1 on line one looked like a clean run. That is the same trap this file
already records for `tee` in GitHub Actions, and it is worth knowing it catches
people twice. Redirect to a file and check `$?`, or use `set -o pipefail`.

## Roadside stalls and the beekeepers — 5 rows, 30 Aug 2026

Sent by Scott as links through the day, each with his own classification. Two
stalls and three honey producers; `produce` 42 → 46, `nursery` 10 → 11.

    528  Islaindi          shop   nursery · produce  Cape Otway Road, Winchelsea
    529  Fyansford Honey   shop   produce            20 Carroll Road, Fyansford
    530  Edmonds Honey     maker  produce            5 Lower Duneed Rd, Mount Duneed
    531  Surfcoast Bees    maker  produce            Surf Coast
    532  Coastal Nectar    maker  produce            Surf Coast

**A roadside stall is a Shop.** `produce` and `nursery` are things a place
GROWS, so the rules make these venues — and nobody drives to an honesty box for
its own sake. They are stockists, which is the Chocolaterie rule, so they earn
a place on `/produce` and `/nursery` and stay off the board. All five are in
`BY_ID`, because a shop can no longer be inferred and a maker never could.

**None of the three beekeepers gets a pin, and one of them is the interesting
case.** Surfcoast Bees leaves its address fields blank and invites nobody;
Coastal Nectar tells you to ask its stockists. Both are the maker rule working
as written. **Edmonds Honey is different: Scott supplied the address himself**
(5 Lower Duneed Rd, Mount Duneed) after the site was checked at `/`, `/contact`
and `/about` and published no street address, phone or postcode. That is the
Bike Matters precedent — a person handing over a fact is a source — so the
address is recorded and the `source_note` says it came from Scott and not the
site.

**It still has no coordinate, and that is a second decision.** Nominatim has no
house number on Lower Duneed Road: it returns two `type=secondary` road
segments **900 m apart in two different localities** (Mount Duneed and
Armstrong Creek), which is the multi-segment coin toss, and neither the
business name nor the name-plus-suburb resolves to any named feature. An
address you can post to is not the same fact as a point you can stand on.

**Fyansford Honey is the best-pinned row of the five**, by the bike-shop
technique: the directory publishes -38.1460091,144.3029375 and a structured
Nominatim query on its address independently matches `type=house` **14 m**
away. The OSM node is stored, and it reverse-geocodes back to 20 Carroll Road.
Islaindi has no street number anywhere, so it keeps the directory's own
road-level point — which reverse-geocodes to Cape Otway Road, Winchelsea, and
is the honest answer for a thing that genuinely is on the roadside.

**The directory these two came from is not a source and is not being pursued** —
Scott's call, 30 Aug 2026. A listing there is weaker evidence than a first-party
page, which is why both rows say so in their `source_note`. The two stalls stay;
nothing reads that site.

### `Mount Duneed` did not resolve, and `Mt Duneed` was already a town

`SUBURBS` spells it **`Mt Duneed`**; every business there writes **`Mount
Duneed`**; `scanFor` matches literals, so `suburbOf` returned null and the row
would have reached no filter and no town page.

Fixed in `suburbOf` by normalising `\bmount\b` → `mt` alongside the existing
apostrophe strip — **not** by adding a second `SUBURBS` entry, which would put
one town in the Place menu twice, and **not** by folding it into `GEELONG`,
which would have quietly moved a standing town into the city. Mt Duneed still
appears once in the menu and every other town still resolves to itself.

The generalisable bit: a vocabulary that stores one spelling silently drops
every other one, and the symptom is a row with no town rather than an error.

## 205 listings were invisible on the live site — FIXED 30 Aug 2026

**PostgREST caps a response at `db-max-rows`, which is 1000 on Supabase, and it
does not tell you.** You get `200 OK` and a short array. `notice-data.js` asked
for `/rest/v1/listings?select=*` in one request and trusted what came back.

The library import took `listings` past 1000 on 27 Aug 2026. From that moment
the board was drawing **1000 of 1205 rows**, the badge still said `live`, and
the tally said *871 things pinned* — a number that looked entirely plausible
because nobody knows what it should be. Three days, no error, nothing in the
console.

**It surfaced by luck.** Two events written on 30 Aug were the newest rows and
therefore the ones cut, and they were both dated that day, so the check was
"why is today's event missing from the board" rather than "is the board
complete". Five other events dated the same day rendered fine, which is what
ruled out a date bug and pointed at the fetch. Had those two rows been older
they would have displaced two others and the count would still have been wrong.

`fetchAll()` in `notice-data.js` pages with `limit`/`offset` and stops when a
page comes back short, which is the only end-of-data signal PostgREST offers.
`admin.html`'s `sb()` does the same — `events` is past 700 and climbing with
every library import, so the only screen that can edit a row was one good week
from hiding the newest ones.

Two things to keep hold of:

- **`PAGE` may be at most 1000.** Ask for more and the cap silently gives you
  1000 back, the loop never sees a short page, and it never ends.
- **A short array is not an empty one.** The old code only treated a *zero*
  length response as a failure, which is why truncation sailed past the
  `throw new Error('empty')` guard that was sitting right there.

The generalisable sentence, which this file has now written three times in
different clothes — the `--kinds` parser, the stale arts cache, this: **a query
that silently returns less than you asked for is indistinguishable from a world
containing less.** Anything reading a growing table has to page or assert a
count.

**The built-in fallback copy in `index.html` is separately stale** — it says
"as at 26 Aug 2026" and 419 rows, against 1205 now. It is only shown when
Supabase is unreachable, so it is not urgent, but it is no longer a fallback so
much as a museum. Regenerating it is its own job and nobody has done it.

## The Event Inbox pull of 30 Aug 2026 — 14 items, 19 rows

The second inbox pull, and much the largest. Seven photographs, six links and a
newspaper clipping; Scott sent five more links in the chat while it was running.

**Photographs of a phone screen are now a normal capture**, not an exception —
four of the seven were Instagram profiles or a business's own web page shot in
Safari, and the address, the hours and the market days were all legible in
them. An Instagram bio is the business's own publication, so it is first-party
for its own address. That is how `Alt Rd Wines` got 880 Winchelsea–Deans Marsh
Road, which its website does not publish at all.

    533 Church Geelong          venue  gig·theatre·comedy   (place 140)
    534 Alt Rd Wines            venue  winery·restaurant
    535 Mt Pleasant Rd Brewers  venue  brewery·bar
    536 Hop City                venue  bar
    537 GOR Brewing             venue  brewery              112 Balliang St
    538 GOR Brewing Taphouse    venue  brewery·bar·rest.    27 Baines Cres
    539 Pop Cultcha             shop   arts                 (type is a placeholder)
    540 Pop Cultcha Gallery     venue  art gallery          no pin
    541 Good Blooms Flower Farm maker  produce              no pin
    542 Ghazeepore Greens       maker  produce              no pin
    543 Bellarine Catchment Net group  volunteering·nature  (place 82)
    544 Happy Hour Run Crew     group  running·community
    683 Trivia Arvo             happening  community·cinema (place 7)
    684 Happy Hour Run          happening  weekly, Sundays

**`Great Ocean Road Brewing` is NOT `Great Ocean Road Brewhouse`.** The
Brewhouse (activity 309, place 18) is at Apollo Bay on
greatoceanroadbrewhouse.com.au; the Brewing company is South Geelong plus a
Torquay taphouse on greatoceanroadbrewing.com.au. This was first written up as
a conflict in an existing row before the domains were compared. Two businesses,
similar names, and a merge waiting to happen if nobody writes it down.

**`Bellarine Catchment Network` is the "a places row is not a listing" fault
again** — place 82, with a Humanitix `events_url`, fully known to the scraper
and invisible to every reader since the places table was built. Exactly the
Surf Coast Mountain Bike Club case from 28 Aug, two days later. **After adding a
place, ask whether a reader is ever meant to find it.**

**Sketch and Scribe Festival (event 73) had the wrong end date.** The row said
5 Sep – 17 Oct at `medium` from surfcoastevents; the festival's own site says
**5 Sep – 11 Oct**. Corrected, confidence raised to `high`, and `info_url`
repointed off the aggregator. It was `verified = true`, which records only that
the bulk queue was accepted on 25 Aug. **A duplicate capture exposed a wrong
date for the third time** — the Torquay Farmers Market and the Oneday Estate
address were the others.

**Church Geelong is registered as a source and cannot be read.** robots.txt
allows everything and names no AI crawler, but there is no Events Calendar
plugin, no event post type in `wp/v2/types`, and the only JSON-LD is Yoast
`WebPage`/`WebSite` boilerplate. Its 14 gigs to December are hand-built HTML.
`events_url` is set to the homepage so it shows on the Automations tab in its
honest state, which is *nothing to read*.

**Two things were deliberately not written.** `feverup.com/en/geelong/candlelight`
is a **ticketing aggregator** whose Candlelight concerts happen in other
people's rooms, so a `places` row for it would file every concert at "Fever" —
the Coast & Bay trap. And `theroadsidestalls.com.au` is not being pursued at
all — Scott's call; the two stalls already taken from it stay.

**Pop Cultcha has no honest type, and that is the shop-type retirement biting.**
A collectibles and record shop is not `arts`, and `arts` is what it has. The
same vocabulary gap as monuments and landmarks. Its `source_note` says the type
is a placeholder.

**Nothing published a coordinate it should not have.** Six pins are building
level and cross-checked; six rows have none, each with the reason written down —
Church Geelong (OSM's only "71" is on Little Ryrie Street, a different road),
Pop Cultcha Gallery (no house number, two road segments 140 m apart), the two
market growers and the run crew (no premises), and Bellarine Catchment Network
(no house number on Swan Bay Road, and the road returned is in Marcus Hill).

## Two running events, and a past one kept on purpose — 30 Aug 2026

    685  Bellarine Rail Trail Run   Sun 23 Aug 2026  annual  place 141  ALREADY HAPPENED
    686  Geelong Running Festival   19-20 Sep 2026   annual  place 142

    141  Queenscliff Railway Station                        -38.264327, 144.661633
    142  Nyaal Banyul Geelong Convention and Event Centre    -38.142490, 144.358628

**685 is in the past and that is the point.** Scott's instruction: keep a record
so next year's edition can be tracked against it. It is the 22nd running, so
`recurrence = annual` is well evidenced — and `nextDate` deliberately does NOT
roll annual forward, so the row sits in the past rather than inventing a 2027
date. **Do not infer one.** The site announces no 2027 date, and working the
next edition out from the last is precisely the Surf Coast Arts Trail failure.
Somebody has to read a published date off brtrun.com.au.

`brtrun.com.au` is worth knowing: BRT is the **Bellarine Rail Trail**, the run
is Queenscliff to Drysdale and back, and the organisers are firm that it is
"a group training run and NOT a race". Contact Brett Coleman, 0438 434 260.

**686 is the INAUGURAL Geelong Running Festival**, which its own news page says
outright. So `annual` there is Scott's designation of intent, not a commitment
the organiser has published, and the row's `source_note` says so. Safe for the
same reason: annual is never rolled forward.

**Queenscliff Railway Station had to be found through Overpass, not Nominatim.**
Nominatim returns *nothing* for that name, and "Bellarine Railway" returns two
`narrow_gauge` LINE segments 4 km apart — the track, not the station. Querying
`railway=station|halt` in a bbox found the real node (operator: Geelong Steam
Preservation Society), along with Drysdale, Swan Bay and Lakers Siding. **When
Nominatim has no feature by name, ask Overpass for the tag.** `kind` is null:
`place_kinds` has no word for a railway station.

The convention centre is the "ask for the feature by name" rule paying off
again — by name it resolves `type=conference_centre` with a house number; its
street, which is how the festival publishes it, resolves to a road centreline.

### `have.py` was silently showing 1000 of 1207 listings

Found because the two events above did not appear in `have.py running` a minute
after being written. **PostgREST caps a response at 1000 rows however large the
`limit` is, and it does it silently** — no error, no flag, just a short list.
The query said `limit=2000`, the table held 1207, and 207 rows were invisible.

That is the worst failure this particular tool can have, because
`RESEARCH_RULES.md` tells a pass to run `have.py` FIRST to decide what is
missing — so a hidden row gets researched and written a second time, which is
how duplicates are made. `running` read 13 and was really 16.

`get()` pages with `Range` now and callers ask for `all_rows=True`. **The lesson
is the one nearby.py has already taught three times: a filter that drops rows
without saying so is worse than one that fails.**

### Then every other read was audited — four more, two already wrong

This is the **third** independent discovery of the same cap in one day: the
board and `/admin` (commit 1029fb1, `notice-data.js` + `admin.html`), then
`have.py`, then a grep of every `rest/v1` read in the repo. Do that grep before
assuming a script is fine.

    nearby.py listed_names()   listings  1207  ALREADY WRONG — was reading 1000
    retype.py                  listings  1207  ALREADY WRONG — was reading 1000
    scrape_library.py          grlc evts  500  time bomb, and the worst failure
    sync.py export()           acts/evts  524/683  time bomb

**`nearby.py` was the dangerous one of the two already broken.** Its
"already listed" check went blind to 207 rows, so it would report things the
database already holds as gaps to go and research — the duplicate-making
direction, in the tool a research pass runs first.

**`scrape_library.py`'s is the worst failure mode**, though it had not fired
yet. That read is the *idempotency* check — the one added after a run died at
307 of 500 with the ledger unwritten — so a short read means re-importing events
that are already there. `limit=5000` was doing nothing, and grlc events sat at
500, one import from crossing the cap.

`eventlib.db` takes `all_rows=True` now and pages; `retype.req` and
`nearby.listed_names` do their own. **`sync.py`'s duplicate check was never
exposed** — it is a filtered `name=ilike` query, not a full-table read — but
`export()` writes the spreadsheet from a full read and is fixed with the rest.

**The general rule for this repo: a `limit=` above 1000 is a lie.** It reads as
a deliberate ceiling and is silently ignored, which is why three of these sat
unnoticed. Page, or filter server-side.

### And `sync.py pending` has been broken since the multi-type migration

Found running the paging fix: `pending`, `verify`, `reject` and `export` all
still selected the **`type`** column that `TYPES_MULTI.sql` replaced with the
`types` array. Every one answered a raw PostgREST 400 —
*"column activities.type does not exist"*. `add` and `check` were updated at the
time; these four were not, and nothing has run them since.

Fixed — they read `types` and print it joined with `·`. Worth noticing WHY it
went unseen for so long: this file has been saying "the moderation queue is
empty because everything was verified in bulk", which was true on 25 Aug and has
not been true for days. **It is 785 rows now** — 248 activities and 537 events,
of which 500 are the library import — and the tool that shows them has been
answering 400 the whole time. A tool nobody runs is a tool nobody notices is
broken, and a note saying "this is empty" is what stops people running it.

### The `listings` view has no `ends_on`

Noticed writing 686, which runs 19-20 September. `events.ends_on` is set and
correct, but the view does not carry it, so the page cannot show that a listing
spans days and prints the start date alone. Not fixed — it is a view change and
nobody has asked for multi-day display. Worth knowing before someone re-derives
a festival's end date from somewhere else.

## Soonest first now orders the day, and ON NOW says what is happening

Scott's ask, 30 Aug 2026: *"look to the opening hours to better order the day"*,
and a badge beside `unverified`.

**Distance was doing the whole job inside a day, and it has nothing to say about
a Tuesday.** `sortFn`'s `when` branch keyed on `daysAway` alone and broke every
tie on `km`, so a day's events came out ordered by their drive from Jan Juc.
That is 56 rows sharing the time 4pm–5pm and 55 more sharing 10:30am–11am — most
of the board — arranged by a number nobody was asking about. The key is
`daysAway + dayPos(i)` now, a fraction of a day, so a day reads in the order you
would live it.

### `timeSpan` — one parser, in notice-vocab.js

`time_text` is what an organiser published, so it is prose and not a field.
**618 of 683 events carry a plain range** ("10:30am–11:15am"); 43 carry a start
alone; the rest say things like "Plates from 9am, race 10am", "Sat & Sun" or
"Sept–Oct holidays". `timeSpan` reads **661 of the 683** and returns null for
the rest — every miss checked, and every one is a string with no clock in it.

Three things the real data demanded, none of them obvious from the schema:

- **The opening time often carries no am/pm and borrows the closing one.**
  "2–5pm" is the afternoon. Borrowing is forwards only; "10:30am–11:15am" says
  both ends itself.
- **A full stop is a colon here** — "7.30pm" and "8.30am" are both in the table.
- **Requiring am/pm is what tells an hour from a number.** "34km 8.30am from
  Queenscliff; 17km about 9.40am from Drysdale" holds three numbers and one
  hour, and a meridiem separates them without a list of units to exclude.

**`to` is null when only a start was published, and that is NOT an end.**
Sorting may use a start alone; the badge may not, because a gig that started at
8pm is not evidence that it is still going at midnight. Nothing fills the gap
in — an ON NOW drawn on hours that were inferred is the fabricated-data failure
this file opens with.

**It replaced `startHour`, which had been sitting in index.html unused.** Once
Soonest first and the badge both needed it there was no version of keeping it
that did not end in two parsers disagreeing about what "2–5pm" means. It also
had to answer the closing time, which that one never did.

### Where a listing sits inside its day

`dayPos` in index.html. The hour of the start, over 24 — except for two things
that are the **absence** of a fact rather than a late hour, which take reserved
positions at the very end of the day (23.96 and 23.97 hours, both under 24 or
they would tip into tomorrow's midnight and outrank a real 12:01am):

- **no hours published** — not evidence of a midnight start.
- **finished today** — an event that ended at eleven this morning is still a
  thing that was on today, so it stays inside today, under everything still to
  come. That is what makes the order useful when you open the board at three in
  the afternoon. Only TODAY can be finished; every other day is read in full.
  It keeps its own hour inside that last slot, so the tail still reads seven,
  nine, eleven rather than falling back on distance.

**A start with no published end never sinks, and that is deliberate.** At 2:30pm
the 6am Happy Hour Run still sorts above the 11am market that is genuinely on.
Mildly odd, and the honest answer: the alternative is inventing a duration, and
the same rule would bury a "from 7am" festival that is still running. The row
prints its own time, so nothing is being claimed.

### The badge

`onNow(i, now, sunset)` in notice-vocab.js. **Only ever true where the published
time gives both ends**, so **608 of the 683 events are eligible**. Three things
it therefore cannot answer, all on purpose: a start with no end, a listing with
no time at all, and a **festival running across days — `listings` carries no
`ends_on`**, so 19–20 Sep is one date here. That last one is the standing item
in the paging section, now with a second reason to fix it.

**`melbourneNow()` reads its own clock, and has to.** The date and the hour must
come off the same one or a reader in London gets today's Surf Coast events
matched against their own afternoon. Note `todayISO` beside it is deliberately
the VIEWER's day — it answers which dates to show, a different question.

Drawn as a filled green pill where `unverified` is an outlined square — same
size and setting, opposite everything else, so the two read as a pair on a row
carrying both. **`--live` is a token in all three theme states**, because a
green dark enough to carry white text in the light scheme goes muddy against
`#14170F`. The white on it IS a literal: both greens are chosen to take it, and
`var(--ink)` flips to near-white in one scheme and near-black in the other.

**It is computed at paint and does not tick.** Same convention as the date line
in the masthead, which is stamped at load. A `setInterval` re-render is the
obvious fix and is the wrong one — a re-render shuts every open row on the page.

**A doubled gap was found doing this.** `.c-name` set `gap:8px` AND both badges
set `margin-left:8px`, so the spacing was 16px. Nobody noticed with one badge;
two cost the name 32px of a column it already clips in. The **margin** is the
one that survives, not the gap — below 700px `.c-name` becomes a plain block and
a gap stops applying, which is exactly where the badges ran into the name.

**Still cramped between 700 and 1180px.** The name column is tight there before
any badge, and a second one costs it about five characters. Accepted: the badge
is worth more than the tail of a name, and the band is a split window rather
than a phone or a desktop.

**The subject pages do not draw it yet.** `place.html` and `type.html` render
through `notice-page.js`, which has its own `row()`/`item()`. The parser is
already shared, so adding it there is one condition in each — the town page's
What's on is where it would earn its place next.

## One thing in several places — 30 Aug 2026

Scott's ask, off a screenshot of five near-identical rows: *"if an event has the
same name and time but appears at multiple locations, can it just appear once
and say Library, with the locations in smaller text underneath?"*

Yes, and it is now what the board does. **552 rows for 640 things** on the
default view — 88 lines that were saying the same sentence five times.

**The shape of the problem, measured first: 142 of the 686 events are in 56
clusters** sharing a name, a date and a published time across different
branches, and **every one of them is the library**. Toddler Time on a Monday is
five rows differing only in the branch.

### The rule

Same **name** + same **effective date** + same **published time** = one line.
Three things it is careful about, all in `notice-vocab.js` beside `nextDate`:

- **The key is the effective date.** `nextDate` rolls a weekly event forward, so
  keying on the stored `starts_on` would split a standing Tuesday cluster the
  week it rolls.
- **Only dated things cluster.** Two cafes with one name are two cafes. Two
  events with one name, one date and one clock time are one thing in several
  rooms.
- **Clustering happens AFTER `ok()`, never before.** Narrow to Torquay and the
  five-branch row is a single Torquay row again — checked, it is. That falls out
  for free and it is the only version that cannot lie: a collapsed row never
  stands for something the filter has excluded.

**It is deliberately not a library rule.** Nothing tests `added_by`, a place
kind or a name. Three dawn services at one hour in three towns would collapse
the same way and should — the row claims "this name, this time, at these
places", which is exactly what the data says. It does not claim one organiser.

### What the Where column says

`placesLabel` prints **"5 libraries"**, and the branches go underneath in the
same small type the suburb used. The noun is derived, never assumed:
`commonPlaceWord` intersects the words of the place names and prints the shared
one — five branches share *library* and nothing else. **With no shared word it
says "3 places"**, which is the honest fallback and the reason two unrelated
venues can never be given a name that only one of them carries.

**More than one word can be shared** — every Geelong branch carries *geelong* as
well as *library*. The tie is broken by position: an organisation's own noun
trails a branch name, so each candidate is scored by how far through the names
it falls. That is the whole of the cleverness and it is worth keeping small.

`shortPlace` drops the word the row has already said — but **only a trailing
match**, because cutting a word out of the middle of a name makes a phrase
nobody wrote. `Geelong Library and Heritage Centre (The Dome)` therefore cannot
lose its Library that way, and falls back on **the short name the place
publishes for itself in brackets**: *The Dome*, which is what everyone calls it.

The sub-line clips like every other column and carries the **full branch list on
its `title`**, so nothing is hidden, only shortened.

### What the open row has to keep

**Collapsing the line must not lose the fact that these are different
buildings.** The detail draws a `.branches` list: each branch by name, its town
where the name does not already say it (*Colac Library* is in Colac), its own
`info_url` — every library event has a different one — and its own Directions
from its own coordinate. The single-row **Address** line is suppressed on a
cluster, because one member's address is not the set's.

### Three things that had to move with it

- **`VISIBLE` is still the flat list, so the map keeps every pin.** Clustering is
  a list-view transform and nothing else. 640 visible, 609 pinned, unchanged.
- **The tally still counts things, not lines.** *640 things pinned* above 552
  rows is the honest way round — the row itself says how many places it stands
  for, and the map's count agrees with the tally rather than with the list.
- **The pin saves the whole set.** `data-k` carries every member's key, `kept`
  means all of them, and pressing an all-saved row clears it. `toggleSaved(k)`
  became `setSaved(keys, on)` — one thing on the board should be one thing on
  your list.

### Not done

**The subject pages do not cluster.** `place.html` and `type.html` render
through `notice-page.js`, which has its own `row()`/`item()`; `/kids` and the
Geelong town page are where it would earn its place next. The helpers are in
`notice-vocab.js` precisely so that is a call, not a second copy — and they are
DOM-free, because `api/subject.mjs` evaluates that file in a `node:vm` sandbox.

## `gig` became `music` — 30 Aug 2026

Scott's call, made while retyping Pop Cultcha: a record shop cannot be a `gig`.
`gig` describes an evening out, so it could never hold the things that are
*about* music without being a performance — a record shop, and in time an
instrument shop or a teacher. `music` reads correctly on a type page for both.

**64 rows moved** (62 events, 2 activities), and the rename ran as one
statement through the Management API — `insert 'music'`, then
`array_replace(types,'gig','music')` on both tables, then `delete 'gig'`.
`array_replace` preserves position, which matters more than it looks: **the
first element is the primary**, so a per-row rewrite that rebuilt the list
could silently re-order 64 rows and change the word each one prints.
`types_valid()` is a live check, so the insert has to come first and the delete
last.

**This is the rename this file has been warning about, and the warning was
right.** Every map keyed on a type name fails *silently* — a missing key is
just no icon, no group, no label, no error. Nine live sites had to move:

    notice-vocab.js   GROUP_OF · ICON_OF · EVENT_TYPES · TYPE_PLURAL
    index.html        NIGHTABLE · EXTRA_OF
    api/enrich.mjs    TYPES_EVENT
    classify_kinds.py KIND_OF
    scrape_events.py · scrape_venues.py · scrape_library.py   what they assign
    name_rules.py     the word a bare one-word name gains

**`ICON_OF` is the one that proves the point.** `gig:'guitar'` is a real icon
drawing on 56 rows of the board. Miss that key and 56 rows quietly lose their
icon with nothing anywhere to say so. Grep the type name — do not trust a
mental list of the five places, because the five places are about *adding* a
type and a rename touches more.

**`name_rules.py` was the one that should NOT be a straight substitution.** Its
map is type → the word appended to a name too bare to stand alone, and the word
is still *Gig*: "Ceramics Workshop", not "Ceramics Music". The key moved to
`music`; the value stayed `Gig`.

**A dead `ICON_OF` key turned up while checking, and it was mine** — `shop`
still mapped to `shopping-bag` three days after `shop` was retired as a type.
Four of the five maps were updated that day and `ICON_OF` was not, because it
is not one of the five and nothing looks at it. Harmless, and removed. The
lesson is that the five-places list is necessary and not sufficient: **the real
rule is `grep`.**

`/gig` now 404s and `/music` serves. `music` was checked against every town
slug, every other type slug, every file in `public/`, and `RESERVED` in
`api/subject.mjs` before anything moved.

**Pop Cultcha (539) is typed `music`**, replacing the `arts` placeholder it was
written with the same day. Its `kind` was already `shop`, so it stays off the
board and earns its place on `/music`, which is where somebody hunting records
would look.

**The baked-in fallback was renamed too** — 109 occurrences inside the `DATA`
blob in `index.html`. That is not hand-editing a record, it is the same
mechanical substitution a regeneration would perform, and without it the
offline copy would carry a type the vocabulary no longer knows. The blob is
still stale by about 800 rows; that is a separate job.

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
- **The moderation queue is NOT empty any more — 785 rows** (30 Aug 2026): 248
  activities and 537 events, 500 of them the library import. It was emptied in
  bulk on 25 Aug and has refilled since. `sync.py pending` was answering 400 for
  most of that time (see the paging section above), so nothing was visible.

  The 25 Aug clearance was all 101 at once, on Scott's instruction, and each of
  those rows' `source_note` says so in those words. A `verified` flag on one of
  them records that Scott accepted the queue, not that anyone read that row's
  own page — treat it as weaker evidence than a flag set one row at a time, and
  do not let it stop you questioning a date. `Ashmore Arts` (169) and `The Fives` (168) are both
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
9. **Type icons now cover 41 of the 43 types** — this entry used to say "six
   symbols" and was years out of date by the standards of this project. Only
   `skatepark` and `kids` draw the empty slot: skatepark deliberately, because
   Lucide has no skateboard and an unrelated glyph is worse than none (the
   reason is in `notice-vocab.js` beside the map), and `kids` because it
   arrived with the library import and nobody has picked one. The artwork notes
   in the icon section still stand for Scott's own hand-drawn set (the bike
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
