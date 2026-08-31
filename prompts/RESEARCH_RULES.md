# Research rules — read this before any listings pass

The nine group prompts in `prompts/by-group.md` all point here so there is one
copy of these rules and not nine. Read `CLAUDE.md` too; this file is the short
version of the parts a research pass actually touches.

## What you are producing

Rows for the Supabase database, written with `scripts/sync.py add`. Two tables:

- **`activities`** — evergreen places you can go to any week. Fields:
  `name, types, tags, ages, cost, location, km, season, duration, description,
  url, rating, notes, conditions, lat, lng, daypart, added_by, verified, source_note`
- **`events`** — dated things. Fields:
  `name, types, starts_on, ends_on, time_text, recurrence, venue, location, km,
  cost, ages, artist, genre, description, ticket_url, info_url, conditions,
  date_confidence, added_by, verified, source_note`

An event's link is `info_url` or `ticket_url` — **never `url`**, which is
silently dropped. `sync.py` picks the table by which fields are present, so a
row with `starts_on` goes to `events`.

**An event has no `lat`/`lng` of its own. Its pin comes from `place_id`.**
Write an event without one and it is on the list and invisible on the map, with
nothing to tell you — the produce pass wrote twelve markets that way, 28 Aug
2026, and none of them could be plotted. So for every event:

1. `python3 scripts/have.py places` and look for the venue. If it is there, put
   its id in `place_id` and you are done — the `listings` view coalesces the
   coordinate through.
2. If it is not there, say so in the log with the venue's full address, so a
   places row can be built. **You cannot write `places` from a script.**
3. `venue` is free text for the ones that genuinely name no single place —
   "Various venues", "Rotates — check website". Those stay unpinned on purpose.

An **activity** is the other way round: it carries its own `lat`/`lng`, and
`place_id` is only for the case where a `places` row for it already exists
(Patagonia, Gather Athletics). Linking beats a second copy that can drift.

Write a batch as a JSON list to the scratch directory, then:

```bash
python3 scripts/sync.py add /tmp/batch.json --dry-run
```

then the same command without `--dry-run`. Rows land `verified = false` and
`added_by = 'Research'`, so `python3 scripts/sync.py pending` is Scott's review
queue. Do not pass `--verified` unless he has said to.

`add` refuses a name that already exists. It does **not** catch a near-miss, and
the first big pass proved it: `Common Ground Project` went in beside
`Common Ground Project – Freshwater Creek`, one venue listed twice, because a
suffix is enough to slip past the check. **Search on the distinctive word, not
the whole name** — one `ilike` per candidate on the word nobody else uses —
before you write anything.

A listing plus a `places` row for the same venue is fine and normal; that is the
Gather pattern, two different tables. **Two listings is not that.**

## The 43 types, and the nine groups

`public/notice-vocab.js` is the list. A row carries **a list** of types and the
**first one is the primary** — the word the row prints, the icon it draws, the
colour it tints. `["festival","surfing","cinema"]` is a real row. Put the type
that best answers "what is this thing" first.

Only those 43 words. `sync.py` checks them against the `types` table and refuses
anything else. If a listing genuinely has no home in the vocabulary, note it in
the worklog rather than forcing it into the nearest type.

## The region

Surf Coast and Bellarine, plus Geelong, plus the Otways and Great Ocean Road
spine — Cape Otway, Beech Forest, Kennett River, Lavers Hill, Forrest, Apollo
Bay. **Direction matters more than distance.** Something 100 km inland toward
Ballarat is out even though Lavers Hill at 90 km is in.

`location` is free text but it must contain a suburb `suburbOf()` recognises, or
the listing lands in no place page at all. The list is `SUBURBS` in
`public/notice-vocab.js`. Every Geelong suburb answers as Geelong.

**End the string with the suburb**, always — `"561 Cape Otway Road, Moriac"`, in
that order. `suburbOf()` reads the last comma-separated chunk first for exactly
this reason: before that fix, a road named after a town beat the town you were
standing in, and the Moriac General Store filed itself 90 km away under Cape
Otway. Write an address whose last chunk is a postcode or "Victoria" and you are
back on the old whole-string scan, which is where that trap lives.

If a place's real suburb is not in the vocabulary (Bambra, Modewarre, Marcus
Hill, Bannockburn), **say so in the log** and give it the nearest town that is.
Do not rely on a road name to land it there by accident.

## The rules this project has already paid for

- **Never invent a URL.** A `maps.app.goo.gl` link is refused outright — earlier
  versions of this database were full of fabricated ones. If a place has no
  website, leave `url` null. An Instagram or Facebook page is a real url.
  **A Google Maps search link is not a placeholder and there is no policy that
  permits one.** The first pass wrote one and said "per policy" in its log; there
  are already 37 of those in the database waiting to be cleared, and each one is
  a missing pin. Null is the honest value.
- **Never state a date without a source.** A first-party page — the venue's own
  gig listing, the organiser's own site, the event's own ticket page — is enough
  on its own for `date_confidence: "high"`. An aggregator, a news story or a
  worked-out recurrence ("third Sunday") is `medium` and needs a second source.
  **Return null rather than guess.**
- **A coordinate means "you can stand here".** Geocode it, never estimate:

  ```bash
  curl -s -A 'whattodo-janjuc' 'https://nominatim.openstreetmap.org/search?format=json&q=28+Hodgson+Street,+Ocean+Grove,+Victoria,+Australia'
  ```

  Max **1 request per second** and a real User-Agent. Then check three things:
  - **Four decimal places minimum.** 0.01° is 1.1 km, which on this coast is
    often open water. Fewer than four is a guess, not a coordinate. `sync.py add`
    refuses these now, as `/admin` always has. The one real exception is a
    genuine match that happens to land on a round number — OSM has the 18th
    Amendment Bar at exactly `-38.1480000` — and the way to write one of those is
    to say so in `source_note` and put it in through `/admin`.
  - **`type: "administrative"` means you got a boundary, not a place.** "Bells
    Beach" resolves to a polygon whose centre is 2.6 km from the beach.
  - **A coastal point that reverse-geocodes to bare "Victoria, Australia"** —
    no road, no suburb in the `address` object — has nothing under it, which
    here means the sea.

  No match you can trust? Leave `lat`/`lng` null. A null pin is honest.
  Record what Nominatim actually matched in `source_note` — building, street,
  or name-and-suburb are three different facts.
- **Never write `km`** — with exactly one exception. Standing decision, 25 Aug
  2026: distance stays null until driving distance can be computed
  automatically. Hand-entering them is how a hundred more guesses get in.

  **The exception is `at-home`, where `km` MUST be 0.** `sortFn` reads
  `(a.km ?? 999)`, so a null sends the row below every real place in the region
  on the default Closest-first sort — the group was rendering as two halves at
  opposite ends of the list with nothing between them. `km = 0` means *here*,
  which is exactly what an at-home listing is. Fixed on 23 rows, 31 Aug 2026.
- **Never infer an accessibility claim.** A wrong one sends someone to a place
  that cannot take them.
- `cost` on an activity is `Free`/`Cheap`/`Moderate`/`Splurge` or null.
  `daypart` is `day`/`night`/`both`. `conditions` come from the 14:
  `any-weather, low-tide, high-tide, new-moon, full-moon, clear-sky, calm-sea,
  warm, low-wind, dry-trails, dry-ground, no-fire-ban, geomagnetic-storm,
  good-in-rain`. Be conservative — `dry-trails` is no rain for 48h, `dry-ground`
  is not raining now, and they are deliberately different.
- `source_note` says where it came from, in a sentence a person can check.
  Every row you write gets one, whether or not it is verified.

## Description and notes

`description` is two to four sentences of the thing itself — what it is, why
someone would go, what is specifically true of it. Not marketing copy lifted off
the venue's own page, and not a paraphrase that says nothing ("a great spot for
the whole family"). `notes` is the practical tail: hours, parking, the bit that
would otherwise make someone turn up on the wrong day.

## Places, and the automations

`places` is the registry the venue scraper reads. **A venue with an `events_url`
gets read twice a week forever**; a hand-entered gig goes stale the day after it
happens. So when a research pass turns up a venue that publishes its own gigs or
sells tickets, the durable move is a `places` row with `events_url` filled in —
not a fistful of dated rows. Register the **organiser** page, never a single
`/e/` event link.

You cannot write `places` with `sync.py`. Put candidates in the worklog with
their URLs and say so in your summary; Scott adds them through `/admin`.

**Do not run the Humanitix path.** Humanitix's robots.txt permits
`whattodo-janjuc` but disallows `ClaudeBot`, so an assistant must not fetch it on
Scott's behalf. `--skip humanitix` when you are driving.

## The worklog

Every pass keeps one, at `prompts/log/<group>.md`, so the loop can be stopped and
picked up again. Append as you go — one heading per type, and under it: what you
searched, what you added, what you rejected and why, and what is left. A
candidate you decided against is worth more than a blank line; it stops the next
pass spending the same hour.
