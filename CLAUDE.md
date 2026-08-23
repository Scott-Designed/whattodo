# WhatToDo Jan Juc — working notes

A community listings site for Jan Juc and the Surf Coast, Victoria. Live at
**https://whattodo-nu.vercel.app** (Vercel project `whattodo`).

## Shape of it

```
public/index.html     the entire site — one file, no build step, no framework
api/enrich.mjs        Vercel function: Claude drafts missing fields, user approves
supabase/             schema, seed data, setup SQL
scripts/              configure.py (keys into the page), sync.py (seed/export/moderate)
```

Deploy is a push to `main` — GitHub `Scott-Designed/whattodo` is connected to the
Vercel project, which builds every push. There is no build step; Vercel just
serves `public/` and the function in `api/`. `npx vercel --prod` still works if
you need to force a deploy without a commit.

## The database is the source of truth

Supabase project ref `xpnsrtylcqjcoqitskwy`. Two tables — `activities` (evergreen
places) and `events` (dated things) — plus a `listings` view that unions them into
one shape for the page. 150 + 31 at seed.

The spreadsheet `JanJuc_WhatToDo_Database.xlsx` seeded this and is now an archive.
**Do not edit it and do not sync from it.** Two live copies is how the same festival
ended up in both sheets with two different dates, one of them wrong.

## Conventions that are enforced, not just documented

- **25 types**, foreign-keyed to the `types` table. An unknown type is rejected by
  the database, not just by the form. `null` is allowed and means "not sorted yet".
- **14 condition tags**, checked by `conditions_valid()`. Thirteen are gates;
  `good-in-rain` is a boost — it never hides anything, it promotes on a wet day.
- `dry-trails` = no rain for 48h (MTB, unsealed tracks). `dry-ground` = not raining
  right now (skateparks, markets, picnics). These are deliberately separate.
- Community additions land `verified = false`. RLS refuses any insert that sets
  `verified = true` or `added_by = 'Research'` — a submission cannot dress itself up
  as researched data.

## Research rules — this project has been burned before

- **Never invent a URL.** Earlier versions of the database were full of fabricated
  `maps.app.goo.gl` links. `api/enrich.mjs` strips them server-side.
- **Never state a date without a source.** The Surf Coast Arts Trail sat in the
  database on the wrong date for months. Events carry `date_confidence`
  (high/medium/low) and the site shows "est." on anything below high.
- Cross-reference two sources. Return null rather than guess.
- Distances are approximate DRIVING distances from Jan Juc, not straight-line —
  the Great Ocean Road makes those differ by 40%.

## Known outstanding

- 42 entries use Google Maps *search* URLs rather than pinned coordinates
- Four events sit on estimated dates: Bells Beach Surf Film Festival, Deans Marsh
  Festival, Geelong Pride Film Festival, One Planet Festival
- Ideas Pipeline (177 rows, in the old spreadsheet) is not in the database
- Tide, moon and fire-ban conditions have no data source wired up. Only the
  weather-derived tags actually evaluate: dry-ground, dry-trails, warm, low-wind,
  clear-sky, good-in-rain
- `Ashmore Arts` and any other community adds need checking and verifying
- Distances unverified; Waurn Ponds known wrong

## Gotchas already paid for

- Vercel functions: `.mjs`, or a `package.json` with `"type": "module"`. A bare
  `.js` using `export default` silently fails to deploy and the route 404s.
- Don't create Supabase tables in the Table Editor — run the SQL. A hand-made table
  has only `id` and `created_at` and the CSV importer then refuses everything.
- The site ships with a baked-in copy of the data so it renders instantly and still
  works if Supabase is down. The badge by the date says `live` / `offline copy` /
  `built-in copy`. Don't remove that fallback.
- Sunset is computed in-page (no API) for the When filter. Verified against
  WillyWeather: 22 Aug 2026 gives sunrise 6:59, sunset 5:52pm.

## Next things worth doing

1. Verify community additions — `python3 scripts/sync.py pending`
2. Pin the 42 unpinned map URLs, which unblocks a map view
3. Promote the Ideas Pipeline into the database
4. A scheduled job that re-checks estimated event dates as real ones get announced
