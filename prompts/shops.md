# Two passes the type pages are waiting on — shops, and the people

Written 1 Sep 2026, out of a review of all 44 type pages. Both are worked
**by type**, both point at [prompts/RESEARCH_RULES.md](RESEARCH_RULES.md) rather
than repeating it, and both are loops — paste one block into Cowork with this
folder open and let it run.

## Why these two and not another group pass

The nine group passes are done and they filled one chapter each: **places**. A
type page draws a chapter per `kind`, and measured against the four an
"Everything" page promises — Places · What's on · Shops · People — only three
types of eighteen fill all four:

    produce            56 rows    Places 40   On  9   Shops 2   People 5   4/4
    mountain biking    36 rows    Places 14   On  9   Shops 9   People 4   4/4
    cycling            24 rows    Places 10   On  4   Shops 8   People 2   4/4

Those are exactly the three a shop pass has been run on — the produce pass and
the bike-shop pass. **13 of 18 are missing shops. 13 of 18 are missing people.
Only 3 are missing places.**

The whole database holds **24 shops and makers, and 17 of them are bikes or
produce.** `surfing` has three shops on a coast full of them; `music` has one
record store; `reading` has one bookshop. None of that is a fact about surfing,
music or reading. It is a fact about which passes have been run.

**Do not read a thin chapter as evidence the chapter should not exist.** This
project has paid for that sentence three times already — the `--kinds` parser
that silently dropped rows, the stale arts cache that reported every gallery in
the region as non-existent, and the 1000-row PostgREST cap that hid 205 listings
for three days. A search that returns nothing looks exactly like a world
containing nothing.

---

## The thing this pass gets wrong if it gets anything wrong

**A shop can no longer be inferred, and that is permanent.** `shop` was retired
as a *type* on 27 Aug 2026 because it said twice what `kind` already said. The
consequence is in `scripts/classify_kinds.py`: `KIND_OF` has nothing mapping to
the shop kind, so a row typed `surfing` or `reading` — things you go and **do** —
comes out a **spot** under the rules.

So every shop needs **two** things, not one:

1. `"kind": "shop"` written explicitly on the row.
2. **A line in `BY_ID` in `scripts/classify_kinds.py`, with its reason.**

Without the second, `--reclassify` flattens it back to a spot and the row walks
onto the Notice Board, which is precisely what the shop kind exists to prevent.
The bike pass added eight lines in the same commit as its eight rows. Do the
same: hand back the `BY_ID` lines with the batch.

**Shops are held off the board by `OFF_BOARD` in index.html.** A shop earns its
place on a *type page* and nowhere else — so **a shop with no useful type is
invisible**. Type it by what it SELLS.

### Shop or venue — the Chocolaterie rule

Settled by Scott, 27 Aug 2026, and it decides every row here:

> **Would you go for the thing itself?** Then it is a **venue**.
> **Does it exist so a type page has a stockist?** Then it is a **shop**.

Great Ocean Road Chocolaterie is a **venue** — people drive there for its own
sake. `Go Ride A Wave – Torquay` went venue → shop on the same rule: a hire and
lesson counter is a stockist, so it earns `/surfing` and stays off the board.

---

## 1 · The shop pass

> Missing shops today: arts 0 · golf 0 · paddling 0 · skatepark 0 · swimming 0 ·
> walk 0 · music 1 · reading 1 · rock climbing 1 · surfing 2

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then run the shop pass.

Work these ten types, thinnest first: arts, golf, paddling, skatepark, swimming, walk,
music, reading, rock climbing, surfing. Target every honest shop in the region, not a number.
Never pad. If a type genuinely has two shops in the region, two is the answer.

This is a loop. For each type, in order:
  1. `python3 scripts/have.py <type>` — read what is there, names and towns.
  2. Sweep the map, then check the towns by hand behind it. Both halves are needed:
     the bike pass found Torquay's only bike shop by search alone, because it is in
     no map and no directory.
  3. For each candidate: confirm it still trades from a first-party page, get its
     address from that page, geocode it, cross-check, build the row.
  4. Write the batch to the scratch directory and run `python3 scripts/sync.py check <file>`.
  5. Append to prompts/log/shops.md: added, rejected and why, still open.
  6. Next type. Do not ask me between types.

EVERY ROW NEEDS THREE THINGS OR IT IS WRONG:
  - "kind": "shop"                       — explicit, always
  - types listing what it SELLS          — the shop's own categories, in its own words
  - a BY_ID line for classify_kinds.py   — hand these back with the batch, with reasons

  Format for the BY_ID lines, one per row, matching the bike pass:
      <id>: ('shop', 'a surf shop; `surfing` is a thing you DO so the rules make it a spot'),
  You will not know the id until Scott writes the batch. Give them keyed on NAME and
  say so — he fills the ids in.

TYPES — what it sells, and a warning about generosity:
  Patagonia Torquay carries `surfing · mountain biking · rock climbing · running`,
  taken from the categories its own store page lists. That is honest, and it also puts
  one shop on four type pages. Take the shop's own words, but if a fifth type is you
  reaching, drop it — a padded type page is worse than a thin one.

  A dive shop is `swimming` first if it sells snorkelling gear to families, `water`
  first if it is a scuba operation. An outdoor shop that sells boots and tents is
  `walk` first and `camping ground` second. Pick what someone would search for.

THE ADDRESS — the bike-pass technique, and it is the best this project has:
  Geocode the address off the shop's OWN page, then look up the shop independently in
  OpenStreetMap and measure the gap. Six of seven bike shops agreed within 21 metres and
  two matched `type=bicycle`, the shop itself as a mapped feature. Two published values
  agreeing is a stronger pin than either alone and costs one extra lookup.

  Read the match, never accept it. Forrest Bike Hire matched `type=hotel` and was still
  right — the house number checked out and a guesthouse shares the address. Hendry's
  matched `type=clothes`, a contributor's opinion about the tenancy.

  Four decimal places minimum. No match you trust, no pin — null is honest.

WHAT THE MAP WILL AND WILL NOT GIVE YOU:
  `scripts/nearby.py` has no category for this. Add one — call it `gear` — and put the
  reason in a comment beside it the way `bike` and `ocean` do:

      'gear': {'shop': {'sports', 'outdoor', 'surf', 'scuba_diving', 'watersports',
                        'fishing', 'golf', 'ski', 'swimming_pool', 'music',
                        'musical_instrument', 'books', 'art'},
               'leisure': {'sports_centre', 'climbing'},
               'craft': {'shoemaker', 'sailmaker'}},

  Wide on purpose, the same bargain `tourism=hotel` makes in the food net and `sports`
  makes in the bike net: a surf shop that also sells skate decks gets tagged whatever
  the mapper felt like. The cost of a wrong extra name is one look; the cost of a
  missing one is a gap nobody knows is there.

  The cache guard WILL refuse a `gear` query against a cache fetched for other
  categories, and will tell you what to run. That is correct — it is the fix for the
  arts-pass bug where a stale cache reported every museum and gallery in the region
  as non-existent. Re-fetch; do not work around it.

  Three things the map gets wrong here, all of them already paid for:
  - OSM tags are not a category system. A record shop is `shop=music`; so is a shop
    selling pianos. A surf shop may be `surf`, `sports`, `outdoor` or nothing at all.
  - OSM IS STALE, and usefully so. It still lists closed businesses — Good Cycles in
    Geelong does not exist, Bike Guru in Colac closed in 2021 after eleven years.
    A name that will not confirm first-party is often a shop that has changed hands,
    which is worth more than the listing would have been. Confirm every one.
  - The 2 km sweep radius hides the Geelong suburbs. `town_list()` folds Belmont,
    Grovedale, Highton and Waurn Ponds into "Geelong", and a 2 km circle on the city
    centre reaches none of them — the bike pass would have missed two shops 3.0 km and
    4.9 km out. Read the cache region-wide and assign each hit to its nearest town.

A SHOP THAT PUBLISHES NO ADDRESS IS NORMAL:
  Bike Matters in Torquay has no street address, no map link and no phone anywhere on
  its site — bookings go through an embedded Hubtiger widget, which is why there is a
  booking page and no shopfront. Flowstate is a JS-rendered Shopify storefront whose
  address exists only in a browser-rendered footer. Do not invent one, and do not
  assume the shop is not real. Put it in the log with what you could not find.
  Scott supplying an address by hand is a valid source — record that it came from him
  and not from the site, because those are different strengths of evidence.

WATCH FOR THE WRONG HEMISPHERE. "Bike shop Torquay" returns Devon; "surf shop Victoria"
returns Victoria, British Columbia. Both were on the first page of results for the bike
pass.

TYPES THAT SHOULD STAY EMPTY, and I want this said in the log rather than filled:
  `nature`, `night` and `cultural` have no honest shop chapter. A binoculars retailer is
  not a nature listing. Leave them at zero and say so.
  `second-hand` has its own prompt at prompts/second-hand.md — do not do it here.

HAND BACK: the batch JSON, prompts/log/shops.md, and the BY_ID lines keyed on name.
Nothing is pushed and nothing is written to the database.
```

---

## 2 · The clubs and makers pass

> Missing people today: arts 0 · golf 0 · music 0 · night 0 · rock climbing 0 ·
> skatepark 0 · walk 0 · paddling 1 · reading 1 · surfing 1 · swimming 1

The twin of the pass above, and the harder one — a group has a contact and often
no address at all, which is exactly why it has never been researched.

```text
Read prompts/RESEARCH_RULES.md and CLAUDE.md, then run the clubs and makers pass.

Work these nine types thinnest first: arts, golf, music, rock climbing, walk, paddling,
reading, surfing, swimming. Same loop as the shop pass: read what is there with
have.py, search, source, build, check, log, next.

TWO KINDS, AND THEY ARE NOT THE SAME THING:
  "kind": "group"  — you JOIN IN. A boardriders club, a masters swimming squad, a
                     bushwalking club, a book club, an art society, a choir.
  "kind": "maker"  — you BUY FROM THEM. A shaper, a luthier, a potter, a jeweller.

  Both need a BY_ID line in scripts/classify_kinds.py for the same reason the shops do:
  `surfing` and `reading` are things you DO, so PRECEDENCE makes them spots. Hand the
  lines back keyed on name.

  The one existing hand decision is `Nippers` (289) — `community · swimming · beach`,
  where spot beats group and then the no-anchor correction demotes it to an idea. Both
  steps right in general, both wrong there. Expect more of that shape here.

A GROUP DOES NOT GET A PIN UNLESS IT PUBLISHES PREMISES:
  This is the rule the community pass got right across 25 rows and it is the one to
  keep. The group is not the reserve it works on; the club is not the hall it hires.
  Every Friends-of group, every Landcare branch, Rotary and U3A were left unpinned
  with the reason on the row. Two Men's Sheds ARE pinned, and their notes say why —
  they publish their own premises rather than hiring a room.

  Boardriders clubs and surf life saving clubs are the interesting case: an SLSC has a
  clubhouse on the beach and publishes it, so it pins. A boardriders club usually meets
  at a break and has a PO box, so it does not.

A MAKER GETS A PIN ONLY IF THEY PUBLISH A VISITABLE ADDRESS THEMSELVES:
  Not an ABN record, not an Instagram geotag, not a search result. A maker working from
  home HAS a home address and a research pass WILL find it and WILL report finding it
  as a success. The precedent is Shyama Buttonshaw — pinned, because 100 Addiscott Rd is
  in his own site's footer AND Scott supplied it independently. What his site does not do
  is invite a visitor: no studio hours, no "by appointment". The "face-to-face
  consultation at his studio" line in search results is NobodySurf's editorial, not his.

  That is why the rule asks for a source_note rather than deciding in code — the note is
  where the difference gets written down. `check()` enforces it: a maker with a
  coordinate must carry a source_note in the same write.

DO NOT INVENT EVENT ROWS FROM A PATTERN.
  Fourteen groups in the community pass publish a monthly working bee — "second Saturday
  at 10am". The pass recorded each pattern in `notes` and created NO dated row from any
  of them. Do the same. A group earns its place on a type page as reference; whether it
  has a published date this month is a different question. Working a date out from
  "third Saturday" is the Surf Coast Arts Trail failure, which is the one this whole
  project is named after avoiding.

WHERE THESE ACTUALLY LIVE:
  Surfing Victoria and Surf Life Saving Victoria list affiliated clubs. Swimming Victoria
  and Masters Swimming Australia list squads. Bushwalking Victoria lists walking clubs.
  Golf clubs are usually the VENUE already in the database — check before adding a group
  that duplicates a course. Most of the rest announce themselves on Facebook alone, which
  is fine as a first-party source for the club's own existence and contact.

  DO NOT put a Facebook URL in a places `events_url`. Nothing can read one — it wants a
  token and client-side JS — and it would hand scrape_venues.py a club to file events
  against as though it were the venue.

`any-weather` IS NOT A DEFAULT AND I WILL BE CHECKING.
  The ocean pass wrote it on 34 of 41 rows and its own log said it wrote none. The
  community pass wrote it on all 20 volunteering rows. It is 54 rows across two passes
  and the convention in the table is against it: `met()` returns TRUE for it, so it reads
  as "suits any weather" rather than "no opinion", which is plainly wrong for a coastal
  working bee. Leave conditions empty unless the source justifies one.

HAND BACK: the batch JSON, prompts/log/people.md, and the BY_ID lines keyed on name.
```

---

## What to expect

The bike pass is the benchmark: **8 shops, 7 of them cross-checked against an
independent OSM node, six agreeing within 21 metres.** It took one session and it
took `mountain biking` from 17 rows to 33 across the day.

`surfing` should be the biggest single win here — it is the defining pursuit of
this coast and it has three shops and one shaper on file. If that pass does not
return a dozen, something is wrong with the search rather than with the coast.
