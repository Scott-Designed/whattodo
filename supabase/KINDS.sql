-- ══ Seven kinds of listing ═════════════════════════════════════════════
-- Agreed with Scott 27 Aug 2026. See the "Seven kinds of listing" section
-- in CLAUDE.md for the reasoning; this file is only the mechanism.
--
-- `activities` vs `events` is undated vs dated, not activity vs place — the
-- table names came off the seed spreadsheet. So one table holds Bells Beach,
-- Anglesea Bakery, a surf school and Backyard Cricket. `kind` is the fact
-- that was missing.
--
--   FAMILY  KIND         COUNT                 WHAT IT IS
--   place   spot           178   no door, no hours, nobody owns it
--           venue          287   a door, hours, a price
--           shop            15   a door, hours, and it is here so a type page
--                                has somewhere to buy the gear
--   people  group           22   you join in
--           maker            6   you buy from them
--   time    happening      491   it has a date
--   idea    idea            57   no anchor of any kind
--                        -----
--                         1056   listings in total
--
-- Counts read from the live database 31 Aug 2026, and they MOVE — shop and
-- maker were both 0 when this file was written four days earlier, and the
-- happening count halved the same morning as a session pruned library story
-- times. Re-count before quoting; do not trust the numbers above as current.
--
--   select coalesce(kind,'unset') k, count(*) from activities group by 1
--   union all select 'happening', count(*) from events;
--
-- SHOP IS ITS OWN KIND, decided 27 Aug 2026 after being tried as a flag on
-- venue. It shares every property with venue — a door, hours, a pin, it can
-- host a happening — because both are in the `place` family, and the family is
-- where those properties live. What it buys over a flag is that anything
-- needing to separate shops out asks one column instead of inspecting a list
-- of types, which is what makes it usable in contexts that do not exist yet.
--
-- Bakeries are VENUES, decided explicitly: a bakery you can sit outside is a
-- cafe that sells bread. Shop means the row is here so `/surfing` has a
-- stockist, not that the row is dull. Great Ocean Road Chocolaterie is a venue
-- for the same reason — people drive there for its own sake.
--
-- This migration is deliberately ADDITIVE. It adds a column and appends two to
-- the view; it rewrites no existing row and removes no existing fact. The destructive half —
-- merging the 32 things that exist in both `activities` and `places` — is a
-- separate job, and is the one that fixes the 999 m Blackman's disagreement.
--
-- Run it in the Supabase SQL editor, or from here via the Management API.

begin;

-- ── the vocabulary ──
-- `family` is what a kind can DO, and it is why the families exist rather than
-- being prose: a place can carry a coordinate and host a happening, a person
-- may have neither. Anything that needs to ask "can this hold a pin?" asks the
-- family, not a list of kind names it would have to keep in step.
create table if not exists kinds (
  name   text primary key,
  family text not null check (family in ('place','people','time','idea'))
);

insert into kinds (name, family) values
  ('spot','place'), ('venue','place'), ('shop','place'),
  ('group','people'), ('maker','people'),
  ('happening','time'),
  ('idea','idea')
on conflict (name) do nothing;

alter table kinds enable row level security;
drop policy if exists kinds_read on kinds;
create policy kinds_read on kinds for select using (true);

-- ── the column ──
-- Nullable on purpose. Null means "nobody has classified this yet", which is a
-- question; a wrong kind is an answer nobody checked. Same reasoning as
-- places.kind, which still has 14 honest nulls.
alter table activities add column if not exists kind text references kinds(name);

-- shop was briefly a boolean here. It is a kind now; drop the column rather
-- than leave a false-everywhere flag for somebody to find and wonder about.
-- The view has to go first — it reads the column, and Postgres refuses to drop
-- a column something depends on.
drop view if exists listings;
alter table activities drop constraint if exists activities_shop_is_venue;
alter table activities drop column if exists shop;

-- ── the view ──
-- `kind` and `family` appended at the end of both branches; every existing
-- column is byte-for-byte what it was. Dropped and recreated rather than
-- replaced, because the shop column above had to go and CREATE OR REPLACE VIEW
-- can only append. Nothing in SQL depends on this view — only the page and the
-- scripts, which read it over PostgREST.
--
-- Events are always `happening`, so that branch carries a literal rather than a
-- column: there is no such thing as an event without a date, and a column would
-- be a value free to drift away from a fact.
create view listings as
 SELECT 'a'::text || a.id AS key,
    a.id,
    false AS is_event,
    a.name,
    a.types,
    a.types[1] AS type,
    a.location,
        CASE
            WHEN a.place_id IS NOT NULL THEN ap.name
            ELSE NULL::text
        END AS place,
        CASE
            WHEN a.place_id IS NOT NULL THEN ap.kind
            ELSE NULL::text
        END AS place_kind,
    a.km,
    a.cost,
    a.ages,
    a.description,
    a.url,
    NULL::text AS info_url,
    NULL::text AS ticket_url,
    a.conditions,
    a.rating,
    a.notes,
    a.duration,
    a.season,
    a.daypart,
    NULL::date AS starts_on,
    NULL::text AS time_text,
    NULL::text AS recurrence,
    NULL::text AS date_confidence,
    COALESCE(a.lat, ap.lat)::numeric AS lat,
    COALESCE(a.lng, ap.lng)::numeric AS lng,
    a.verified,
    a.added_by,
    a.created_at,
    a.kind,
    ak.family
   FROM activities a
     LEFT JOIN places ap ON ap.id = a.place_id
     LEFT JOIN kinds  ak ON ak.name = a.kind
UNION ALL
 SELECT 'e'::text || e.id AS key,
    e.id,
    true AS is_event,
    e.name,
    e.types,
    e.types[1] AS type,
        CASE
            WHEN e.place_id IS NOT NULL THEN COALESCE(ep.suburb, e.location)
            ELSE e.location
        END AS location,
    COALESCE(ep.name, e.venue) AS place,
    ep.kind AS place_kind,
    e.km,
    e.cost,
    e.ages,
    e.description,
    e.info_url AS url,
    e.info_url,
    e.ticket_url,
    e.conditions,
    NULL::smallint AS rating,
    NULL::text AS notes,
    NULL::text AS duration,
    '{}'::text[] AS season,
    'day'::text AS daypart,
    e.starts_on,
    e.time_text,
    e.recurrence,
    e.date_confidence,
    ep.lat::numeric AS lat,
    ep.lng::numeric AS lng,
    e.verified,
    e.added_by,
    e.created_at,
    'happening'::text AS kind,
    'time'::text AS family
   FROM events e
     LEFT JOIN places ep ON ep.id = e.place_id;

commit;
