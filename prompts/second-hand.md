# second-hand — a type pass, not a group pass

`second-hand` is the 44th type, added 1 Sep 2026, and it has **one row**. The
other nine prompts work a whole group thinnest-first; this one works a single
type from nearly zero, so it is organised by **source** rather than by type.

Read the "Getting the repo" section at the top of
[by-group.md](by-group.md) first — the clone instruction, the no-credentials
rule and `sync.py check` are the same here.

---

```text
Read prompts/RESEARCH_RULES.md and the `second-hand` section of CLAUDE.md, then research
listings for the `second-hand` type. It has one row and the region has dozens of candidates.

Do not re-litigate the name. `second-hand` was chosen over `vintage` (a subset — Savers is a
thrift megastore and Vinnies is a charity shop, neither is vintage) and over `environmental`
(a motive, not a thing, and the type is the word the row prints). Those arguments are settled
in CLAUDE.md. If you think a fifth name is better, put it in the worklog and use second-hand.

═══ WHAT THIS TYPE IS FOR ═══

It says WHAT IS SOLD, not what the row is. So it covers the charity shop, the vintage
boutique, the antique dealer, the council tip shop, the used record and book shop, and the
monthly flea market — things that have nothing else in common and that a person hunting for
a jumper, a bookcase or a record would all look for in one place.

Almost every row will be `kind: "shop"`, which means it is OFF THE NOTICE BOARD by design.
Do not ask whether a row is worth doing on a Saturday — that is the wrong test here. The
test is whether somebody looking for second-hand goods would want to know it exists. Shops
earn their place on the /second-hand page, not on the board.

═══ PHASE 0 — READ FIRST, AND AUDIT TWO ROWS ═══

  python3 scripts/have.py second-hand

Then check the whole table for things already held under another type, because a second-hand
shop may be in the database wearing the wrong word:

  python3 scripts/have.py community | head -40

Two existing rows are almost certainly this type and are your first job. Report them in the
worklog as proposed edits — you cannot write, so name the id, the current types and the
proposed types:

  110  Anglesea Resale Shed (Tip Shop)   kind=shop, types=['community']
       CLAUDE.md calls `community` the weakest type in the database and names THIS row as
       the one it is weakest on. It is the reason the type was created. Read the row, read
       Surf Coast Shire's own page for it, and say what its types should be.

  539  Pop Cultcha                       kind=shop, types=['music']
       A Geelong collectibles and record shop. Its own source_note says the type is a
       placeholder. Decide whether `second-hand` belongs on it and in which position, and
       say why. If its stock is mostly new merchandise, say that instead — this is a
       judgement, not a foregone conclusion.

Anything else you find already in the database that sells second-hand goods goes on the same
list. Do not write a second row for it.

═══ PHASE 1 — THE CHARITY CHAINS ═══

This is the bulk of the type and it is a FINITE, PUBLISHED list, so work it exhaustively
before touching anything else. Every one of these runs a store locator:

  Salvos Stores · Vinnies (St Vincent de Paul Victoria) · Australian Red Cross shops ·
  Savers · Sacred Heart Mission · Anglicare Victoria · Uniting Vic.Tas op shops ·
  Diabetes Victoria · MS Australia · Cancer Council Victoria · Lifeline ·
  RSPCA Victoria op shops · Geelong Animal Welfare Society (GAWS) · Bethany Community
  Support · hospital auxiliary and church parish op shops

**The Savers lesson is the technique for all of them, and it is already proved.** A chain's
marketing site is often a client-rendered app: a plain fetch of savers.com.au/locations
returns a 3KB shell and every guessed store path shows "Oops! That page doesn't exist."
Its **locator subdomain** stores.savers.com.au is server-rendered and carries schema.org
LocalBusiness with address, phone, trading hours and a coordinate.

So: DRIVE THE SITE'S OWN STORE FINDER to get the store URL. Never guess a store path from
the pattern of another one. If a chain's locator will not render to a fetch at all, say so
in the worklog and move on — a chain you could not read is a finding, not a failure.

═══ PHASE 2 — THE INDEPENDENTS ═══

Vintage boutiques, antique dealers, used bookshops, record shops, retro furniture, preloved
kids' clothing, consignment. These have no central list, so they come from the map and from
each town by hand:

  python3 scripts/nearby.py --refresh                    # ONCE, at the start of the pass
  python3 scripts/nearby.py "Geelong" --kinds secondhand

`secondhand` was added to `KIND_TAGS` for this pass and asks Overpass for
`shop=second_hand|charity|antiques|books|music`. An op shop is tagged `charity`.
`books` and `music` are in because a used bookshop and a record shop carry no other tag —
they catch NEW shops too, so every hit needs reading, the same bargain `tourism=hotel` makes
in the food net. `clothes` is deliberately out: it is overwhelmingly new fashion and would
swamp Geelong, which is what `florist` did to the produce sweep.

**The cache is per-category, and the guard is real.** Asking for `secondhand` against a
cache fetched for other kinds exits telling you to `--refresh` rather than reporting a
region with no op shops in it. If you see that message, run the refresh — do not work
around it.

**Read the label derivation before you trust a filter.** That script has silently discarded
whole categories three times (the `--kinds` space form, the arts label bug, a stale cache).
A search tool that returns nothing looks identical to a region that contains nothing. If a
sweep returns zero for a town you know has op shops, the tool is wrong, not the town.

═══ PHASE 3 — COUNCIL TIP SHOPS AND RESALE SHEDS ═══

The Anglesea Resale Shed is one of these and there will be more. Land managers publish them
properly, which makes them the easiest first-party rows in the pass:

  Surf Coast Shire (resource recovery / waste and recycling)
  City of Greater Geelong (resource recovery centres)
  Colac Otway Shire · Golden Plains Shire

Opening hours matter more here than anywhere else in the type — a tip shop is often open two
days a week — so quote them from the council's own page or leave them null.

═══ PHASE 4 — MARKETS ARE EVENTS, NOT SHOPS ═══

A vintage market, flea market, car boot sale or garage-sale trail is a DATED thing and goes
to `events`, not `activities`:

  types: ["market", "second-hand"]      kind: none — an event is always a happening

Every dated row needs a `place_id` or it cannot be plotted, and an event has no coordinate
of its own. Run `python3 scripts/have.py places` and link an existing place where one fits.
Where none does, WRITE THE ADDRESS INTO THE WORKLOG so Scott can build the place row — do
not invent a pin and do not leave the address only in prose. Three passes in a row have hit
this and it is the single most repeated fault in this project's research history.

And do not infer a date from a pattern. "Third Sunday" is not a date. If the organiser has
not published the next one, write the pattern into `notes` and no date at all.

═══ KIND, AND THE ONE THING THIS TYPE GETS FOR FREE ═══

`KIND_OF['second-hand'] = 'shop'` in scripts/classify_kinds.py, so a row typed `second-hand`
ALONE classifies itself correctly and needs no hand decision. That is unusual and it is the
reason the type was allowed to map to a kind at all.

**It stops being free the moment you add a second type.** `PRECEDENCE` is
`idea < group < maker < shop < spot < venue`, so `second-hand · cafe` comes out a VENUE and
`second-hand · music` comes out whatever `music` maps to — the shop is outranked and the row
walks onto the board it was meant to stay off.

So: keep `second-hand` as the only type unless there is a real reason for a second one, set
`kind: "shop"` explicitly on every activity anyway, and **list every multi-type row in the
worklog** so Scott can add a `BY_ID` line for it. A café that also sells vintage stays a café
— that is the rule working, not a mistake.

═══ WHAT NOT TO WRITE ═══

- **Facebook Marketplace, Gumtree, eBay, Depop.** Not places. There is nowhere to stand.
- **A charity's head office** when what you want is its shop. Organiser is not the venue,
  in one more hat.
- **A shop that has closed.** Directories carry dead businesses for years — this project has
  already found Good Cycles and Bike Guru that way. A name that will not confirm as trading
  first-party is usually a business that has stopped being one. Say so and move on.
- **Anything already filed correctly elsewhere.** Repair Café Surf Coast, Repair Cafe
  Bellarine, Landcare, Odonata and the GRLC Seed Library are all in the database under
  `community` or `volunteering` and they are RIGHT there. Reuse and repair are not
  second-hand — they do not share a shelf, which is exactly why `environmental` was refused
  as a name. Do not retype them.
- **Torquay, Devon.** Searches for "op shop Torquay" and "vintage Torquay" both return
  England on the first page. This has caught two previous passes.

═══ WHAT AN HONEST RESULT LOOKS LIKE ═══

**Expect this to be Geelong-heavy and do not correct for it.** Op shops cluster where the
population is — Pakington Street, Belmont, Corio, Newcomb, Ocean Grove — and several Surf
Coast towns will genuinely have none. A pass that comes back with three Lorne op shops has
invented them. Write what is there and let the distribution say what it says.

There is no row target. The chains are a finite list, so finish them; the independents stop
when the sources stop. Never pad.

═══ THE RULES, AS EVERYWHERE ═══

Every row: a first-party `url`, a `source_note` naming the page and the date you read it,
`km` absent, a coordinate of at least four decimal places or none at all, no Google Maps
search link, and a `location` ending in a town `suburbOf()` recognises.

**Pin the way Savers was pinned.** The chain publishes a coordinate; run an independent
structured Nominatim query on the same address; if the two agree at building level, store
the OSM node and say in `source_note` how far apart they were. Savers Geelong is 5.5 m and
that is the strongest pin this project knows how to make. Where they disagree, or where only
one exists, say which one you used and why. Reverse-geocode every pin before you write it —
a coastal point that comes back as bare "Victoria, Australia" is open water.

Validate before handing anything back:

  python3 scripts/sync.py check <file>

═══ HAND BACK ═══

1. The batches as files — activities and events separate.
2. `prompts/log/second-hand.md`, and the worklog is the more valuable half. It must carry:
   - the audit of 110 and 539, and anything else already in the database
   - **the rejection list** — every candidate checked and not written, with the reason.
     This is the part nothing else records and the part that stops the next pass spending
     the same hour.
   - every chain whose locator could not be read, and what it did instead
   - every multi-type row, for its BY_ID line
   - every event with no place_id, with the address to build one from
   - towns that returned nothing, so the gap is a fact rather than a silence
```
