# The Cowork research prompt

A reusable brief for researching a category of things for **Notice** somewhere
that is not this repo — Cowork, a browser session, a phone. It comes back as
JSON that `scripts/sync.py add` accepts without editing.

**How to use it:** copy everything between the rules below, replace
`<<CATEGORY>>` with what you want researched (`cafes`, `pubs`, `wineries`,
`skateparks`, `galleries`, `markets`), optionally replace `<<AREA>>`, and paste.
Paste the JSON block it returns back here, or save it and run
`python3 scripts/sync.py add that.json --dry-run`.

**Why it is this long.** Every rule in it is one this project has already paid
for — a fabricated maps link, a festival on a date nobody announced, fifty
listings sharing one coordinate in Bass Strait. A shorter prompt gets shorter
answers and more of them are wrong.

---

You are researching listings for **Notice**, a community listings site for Jan
Juc and the Surf Coast in Victoria, Australia. I want a researched list of:

> **<<CATEGORY>>** in <<AREA: the Surf Coast and Bellarine>>

## The region

Torquay and Jan Juc, west along the Great Ocean Road to Anglesea, Aireys Inlet,
Lorne, Wye River, Kennett River, Apollo Bay and Lavers Hill; inland to Moriac,
Winchelsea, Deans Marsh, Birregurra and Forrest; east to Geelong and across the
Bellarine — Ocean Grove, Barwon Heads, Point Lonsdale, Queenscliff, Drysdale,
Portarlington, St Leonards, Indented Head.

## Step 1 — work out which vocabulary the category belongs to, and say so

Three closed lists. Nothing may be invented, and the answer decides the output
shape. Print the match and the shape before you research anything.

**Listing types (26)** — these describe a *listing*, something on the board:

    beach · walk · surf · water · bike track · skatepark · sport · park ·
    playground · nature · museum · cafe · cinema · camping · at-home · night ·
    shop · volunteering · nursery · cultural
    gig · festival · market · workshop · community · sport-event

The last six are dated events; the rest are evergreen.

**Place kinds (31)** — these describe a *venue*, a building or feature that
things happen at:

    beach · park · reserve · foreshore · pier · lookout · campground · farm
    pub · bar · brewery · winery · distillery · cidery · cafe
    hall · theatre · museum · gallery · library · community-centre
    surf-club · sports-ground · showground · playground
    civic · memorial · school · street · carpark · accommodation

Then:

- category is a **listing type** and evergreen → **Shape A**
- category is a **listing type** and dated → **Shape C**
- category is a **place kind only** (pub, winery, brewery, bar, distillery,
  cidery, gallery, hall, theatre, library, surf-club, lookout, pier, reserve,
  foreshore, campground, farm, sports-ground, showground, memorial,
  accommodation…) → **Shape B**
- category is in **both** lists (beach, park, cafe, museum, playground) → ask me
  which I want before researching. A café as somewhere to go is Shape A; a café
  as a room that hosts gigs is Shape B.
- category is in **neither** → stop. Name the nearest thing in each list and ask.
  Do not file it under an approximate type.

## Step 2 — the research rules

These are not style preferences. Each one is a failure this database has
already had.

1. **Never invent a URL.** Give a link only if you actually opened that page and
   it loaded. No guessed domains, no constructed search URLs, and never a
   `maps.app.goo.gl` link — those were fabricated wholesale once and the
   importer now rejects them outright.
2. **Never state a date you have not read on a first-party page.** The
   organiser's own site, the venue's own gig listing, the event's own ticket
   page. One of those is enough on its own. A date worked out from last year's
   pattern is not a date.
3. **Return null rather than guess.** A field you leave out is a good answer. A
   field you fill in from a plausible assumption is the expensive kind of wrong,
   because nothing downstream can tell it apart from a checked fact.
4. **No coordinates. At all.** Do not estimate a lat/lng, do not copy one out of
   a URL, do not give the town centre. Pinning is a separate geocoding pass
   against OpenStreetMap here. Give the **full street address** instead and that
   pass will do the rest.
5. **No distances.** Leave `km` out of every row. Distance from Jan Juc is a
   driving distance and is being computed properly later; a hand-entered one is
   just another guess.
6. **Never set `verified`.** Everything you return lands unverified and waits
   for a person. Leaving it out is what makes that work.
7. **Always write `source_note`** — where you read it and when, in plain words:
   `"Read torquayhotel.com.au/whats-on, 26 Aug 2026"`. If two sources disagree,
   say both in the note rather than picking one silently. Two sources disagreeing
   is a useful bug report; one source quietly wrong is not.
8. **Say what you could not find.** After the JSON, list anything you looked for
   and could not confirm, and anything you deliberately left out and why. That
   list is as useful as the rows.

## Step 3 — the suburb has to be one of these

`location` (Shape A and C) and `suburb` (Shape B) are read by a matcher that
knows only these names. A street address is fine as long as it ends with one of
them — `"12 Bell St, Torquay"` works, `"Torquay VIC 3228"` works, `"the surf
coast"` does not.

    Aireys Inlet · Anglesea · Apollo Bay · Armstrong Creek · Barwon Heads ·
    Beech Forest · Bellarine · Bellbrae · Bells Beach · Belmont · Birregurra ·
    Breamlea · Cape Otway · Ceres · Connewarre · Corio · Cumberland River ·
    Curlewis · Deans Marsh · Drysdale · Eastern View · Fairhaven · Forrest ·
    Freshwater Creek · Fyansford · Geelong · Geelong West · Grovedale ·
    Indented Head · Inverleigh · Jan Juc · Kennett River · Lara · Lavers Hill ·
    Leopold · Little River · Lorne · Moggs Creek · Moriac · Mt Duneed ·
    Norlane · Ocean Grove · Point Addis · Point Lonsdale · Portarlington ·
    Queenscliff · Skenes Creek · South Geelong · St Leonards · Torquay ·
    Wallington · Waurn Ponds · Werribee · Winchelsea · Wye River · You Yangs

A place outside all of them is outside the region — leave it out and say you did.

## Step 4 — the output

A short table first so I can skim it, then **one fenced `json` block, last, with
nothing after it**. An array of objects, even for a single result. Use exactly
the field names below and **omit any field you do not have** — do not pad with
`null`, `""`, `"unknown"` or `"N/A"`.

### Shape A — an evergreen listing (activities)

```json
[{
  "name": "Bird Rock Cafe",
  "type": "cafe",
  "location": "1 Bell St, Torquay",
  "description": "One or two sentences, plain and specific. What it is and why you would go. No marketing copy.",
  "url": "https://example.com",
  "cost": "Cheap",
  "ages": ["kids", "teens", "adults"],
  "duration": "1-2 hours",
  "season": ["all year"],
  "daypart": "day",
  "conditions": ["any-weather"],
  "tags": ["coffee", "breakfast"],
  "notes": "Anything that does not fit above.",
  "source_note": "Read example.com/about, 26 Aug 2026"
}]
```

- `cost` is exactly one of `Free` · `Cheap` · `Moderate` · `Splurge`, or omitted.
- `daypart` is exactly one of `day` · `night` · `both`, or omitted.
- `conditions` come only from this list — 13 gates and one boost:
  `any-weather` · `low-tide` · `high-tide` · `new-moon` · `full-moon` ·
  `clear-sky` · `calm-sea` · `warm` · `low-wind` · `dry-trails` · `dry-ground` ·
  `no-fire-ban` · `geomagnetic-storm` · `good-in-rain`.
  `dry-trails` means no rain for 48 hours (unsealed tracks); `dry-ground` means
  not raining right now (skateparks, markets, picnics). Use `any-weather` when
  the weather genuinely does not matter, not as a default.
- `tags` and `ages` are free text — keep them short and lower case.

### Shape B — a venue (places)

```json
[{
  "name": "Blackmans Brewery",
  "kind": "brewery",
  "suburb": "Torquay",
  "address": "26 Bell St, Torquay VIC 3228",
  "website": "https://example.com",
  "events_url": "https://example.com/whats-on",
  "ticketing_url": "https://www.oztix.com.au/...",
  "facebook": "https://www.facebook.com/...",
  "instagram": "https://www.instagram.com/...",
  "aliases": ["Blackman's Brewery, Torquay"],
  "offers": ["food", "drinks", "live-music"],
  "source_note": "Read example.com, 26 Aug 2026"
}]
```

- `kind` is one of the 31 place kinds, or omitted. There is deliberately **no
  `hotel` kind** — in Australia a hotel is usually a pub, so a pub is `pub` and
  somewhere you sleep is `accommodation`.
- `offers` come only from: `live-music` · `food` · `drinks` · `coffee` ·
  `tickets` · `market-stalls` · `function-hire` · `playground` · `toilets` ·
  `parking` · `accessible` · `dog-friendly`.
  **Never claim `accessible` unless the venue's own page says so** — a wrong
  accessibility claim sends someone to a building that cannot take them.
- `events_url` is the page that lists what is on. If the venue sells through a
  ticketing platform, give the **organiser or venue page**, never a single
  event: an `/e/` link dies the night it is over, the `/o/` page keeps working.
- `aliases` are the other names a source calls it — the trailing-suburb version,
  the trading name, the organiser's name. These are what stop a scraper creating
  a duplicate next week, so they are worth collecting.
- The **organiser is not the venue.** If a listing is sold by "Creative Geelong
  Inc" at "Creative Geelong Makers Hub", the venue is the Hub. Put the
  organiser's name in `aliases`.

### Shape C — a dated event (events)

```json
[{
  "name": "Torquay Farmers Market",
  "type": "market",
  "starts_on": "2026-09-05",
  "time_text": "8:30am-1pm",
  "recurrence": "weekly",
  "venue": "Surf Coast Shire Offices carpark",
  "location": "Torquay",
  "description": "One or two sentences.",
  "info_url": "https://example.com",
  "ticket_url": "https://example.com/tickets",
  "cost": "Free",
  "date_confidence": "high",
  "source_note": "Read example.com/markets, 26 Aug 2026"
}]
```

- **An event's link is `info_url` or `ticket_url`. There is no `url` field** —
  writing one gets the row rejected.
- `starts_on` is `YYYY-MM-DD`, always. No other date format is accepted.
- `recurrence` is one of `none` · `weekly` · `fortnightly` · `monthly` ·
  `annual`. If it recurs on a named day, put that in `time_text`
  (`"Saturdays, 8:30am-1pm"`) — there is nowhere else for the day to live.
- `date_confidence` is `high` only when you read the date on a first-party page,
  `medium` for a curated calendar or aggregator, `low` for anything inferred.
  A date you inferred from a pattern is `low` and needs saying so in the note.
- `name` carries the thing; `venue` and `location` carry the place. Do not write
  "Open Mic Night - Torquay Hotel" when `venue` already says Torquay Hotel — on
  a phone the repeat is what pushes the actual event off the edge.

## Step 5 — do not offer me something already there

Before you finalise, read what the database already holds and drop anything that
is a duplicate under any spelling. It is a public read-only endpoint, no login:

    https://xpnsrtylcqjcoqitskwy.supabase.co/rest/v1/listings?select=name,type,location&limit=1000&apikey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwbnNydHlsY3FqY29xaXRza3d5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODczNzI1MzcsImV4cCI6MjEwMjk0ODUzN30.Jf2hG4g55IZamv_5OECQK5rBz6o_a4lZRo3Mthp62KE

For venues, the same with `places?select=name,suburb,kind,aliases`.

If you cannot reach it, say so and hand me the list anyway — the importer checks
for name clashes again on the way in. Flag anything you suspect is a
near-duplicate under a different spelling rather than dropping it silently.

---

## After it comes back

    python3 scripts/sync.py add cowork.json --dry-run   # validate, write nothing
    python3 scripts/sync.py add cowork.json             # write, unverified
    python3 scripts/sync.py pending                     # what is waiting
    python3 scripts/sync.py verify <id>                 # accept one

`add` checks types and conditions against the **live** vocabularies, so a bad
field names itself instead of failing an opaque insert. It refuses a name that
already exists; `--force` only when it genuinely is a different thing.

Shape B has no `sync.py` path yet — places are written through `/admin` or SQL.
Geocode afterwards; nothing here should carry a coordinate it did not earn.
