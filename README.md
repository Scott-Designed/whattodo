# WhatToDo Jan Juc

A community list of things to do around Jan Juc and the Surf Coast.
Add something on the site and it goes into the database and onto the site for
everyone, immediately.

```
public/index.html            the whole site — one file, no build step
supabase/SETUP_RUN_THIS.sql  ← paste this into the SQL editor. Everything.
supabase/schema.sql          tables, constraints, row level security
supabase/seed.sql            the 181 rows as inserts
supabase/seed_*.csv          the same data as CSV, if you ever want it
scripts/configure.py         paste your Supabase keys into the page
api/enrich.js                Claude drafts missing fields; you approve
scripts/sync.py              seed, export, and moderate
```

## Setup — about ten minutes

**1. Create the project.** At supabase.com: new project, free tier, region
Sydney. Nothing else — do **not** create any tables by hand.

**2. Run one file.** Open the SQL editor, paste the whole of
`supabase/SETUP_RUN_THIS.sql`, press Run. That creates the tables and loads all
181 rows in one go. It is safe to run twice.

> Don't use the Table Editor's *New table* button or the CSV importer. A table
> made that way has only `id` and `created_at`, and the importer then refuses
> the CSV because none of the real columns exist. The SQL file makes the tables
> itself.

Check it worked — the SQL editor should return 150 / 31 / 181 for:

```sql
select (select count(*) from activities) activities,
       (select count(*) from events)     events,
       (select count(*) from listings)   listings;
```

**3. Point the site at it.** Settings → API. Copy the Project URL and the
**anon / public** key — not the service key.

```bash
python3 scripts/configure.py https://xxxx.supabase.co eyJhbGciOi...
```

**4. Deploy.** Drag this folder onto vercel.com/new, or:

```bash
npx vercel --prod
```

Open it. The badge next to the date should read **live**.

**5. Optional — turn on drafting.** In the Vercel project, add an environment
variable `ANTHROPIC_API_KEY`. Redeploy. The **Ask Claude to fill the rest**
button appears in the Add panel.

## How it holds together

The page ships with a full copy of the data baked in, so it renders instantly
and still works if Supabase is down — the badge then reads *offline copy*
rather than pretending to be current. When the database answers, those rows
replace the baked ones.

**Adding.** The form writes straight to `activities` or `events` and the list
reloads. New rows land with `verified = false` and show an **unverified** tag
until someone checks them.

**Row level security.** Anyone may read. Anyone may add — but the policy
refuses any insert that sets `verified = true` or claims `added_by = 'Research'`,
so a submission cannot dress itself up as researched data. Editing and deleting
need the service key, which lives only in `.env` and never reaches the browser.

The anon key in `public/index.html` is meant to be public. That is how Supabase
works: the key identifies the project, the policies do the protecting.

## Drafting — Claude fills the gaps, you approve

Type a name, press **Ask Claude to fill the rest**. `/api/enrich` searches the
web and hands back a proposal: type, suburb, distance, cost, description, link,
conditions, and for events a date and time. The fields fill in marked *drafted*,
with what it found and the sources it used shown underneath.

Nothing is saved by that. The mark clears the moment you edit a field, and
**submitting the form is the write** — so what lands in the database is what you
approved, not what Claude wrote.

The endpoint enforces the research rules server-side rather than trusting the
model: a type outside the vocabulary is dropped, condition tags outside the
vocabulary are stripped, and any `maps.app.goo.gl` link is discarded — those are
fabricated by definition. If the search returned nothing, the panel says to treat
the draft as a guess.

To switch it on, add `ANTHROPIC_API_KEY` to the Vercel project. Without it the
button hides itself and adding works as normal. Roughly a cent or two per draft.

## Do you still need the spreadsheet?

**No.** Use it once to seed the database, then keep it as an archive and stop
editing it. Supabase's table editor is a grid that does everything the sheet did,
and it exports CSV.

Two live copies of the same data is exactly how the Arts Trail ended up in two
sheets with two different dates, one of them wrong.

```bash
python3 scripts/sync.py seed       # only if you skipped SETUP_RUN_THIS.sql
python3 scripts/sync.py export     # dated .xlsx snapshot, for safekeeping
python3 scripts/sync.py pending    # what people added, awaiting a check
python3 scripts/sync.py verify 1043
```

## Still to do

- The four events on estimated dates need confirming as real dates are published
- 42 entries still use Google Maps *search* URLs rather than pinned coordinates
- Distances are approximate driving estimates; Waurn Ponds is known wrong
- Ideas Pipeline (177 rows) is not in the database yet
- Tide, moon and fire-ban conditions have no data source wired up — only the
  weather-derived ones (`dry-ground`, `dry-trails`, `warm`, `low-wind`,
  `clear-sky`, `good-in-rain`) actually evaluate
