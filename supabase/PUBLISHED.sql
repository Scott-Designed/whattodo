-- A publish gate, 1 Sep 2026 — Scott's ask, on registering visitgeelongbellarine:
-- "I would like for events not to appear until they have been published by me."
--
-- WHY THIS IS NOT `verified`. It looks like the flag for this and it cannot be,
-- for a reason that only became true on 28 Aug 2026: `scrape_venues.py` now
-- AUTO-VERIFIES a row when four mechanical checks pass — first-party page, the
-- printed weekday matched the date, a real starts_on, a linked place. So
-- `verified` is partly machine-set, and gating the board on it would publish
-- exactly the rows a person most wants to look at first. The two flags mean
-- genuinely different things and both are worth having:
--
--     verified   somebody (or a mechanical check) established this is TRUE
--     published  a person decided this belongs on the board
--
-- CLAUDE.md already records that `verified` was conflating two meanings and that
-- the 25 Aug bulk accept left it saying very little. Loading a third meaning onto
-- it would have finished the job.
--
-- DEFAULT TRUE, and the backfill is the whole point: every one of the 1246 rows
-- on the site today stays on it. Nothing disappears on deploy. Only a writer that
-- explicitly says `published: false` is held back, which today is one scraper.
--
-- Run in the Supabase SQL editor, or through the Management API.

alter table activities add column if not exists published boolean not null default true;
alter table events     add column if not exists published boolean not null default true;

comment on column activities.published is
  'On the board. False means a person has not released it yet — a scraper may write false, only a person writes true.';
comment on column events.published is
  'On the board. False means a person has not released it yet — a scraper may write false, only a person writes true.';

-- The board reads `listings`, so the flag has to reach it or the column is
-- invisible to the only thing that needs it. Appended at the end: CREATE OR
-- REPLACE VIEW may add columns but may not reorder or retype the existing ones.
create or replace view listings as
 SELECT 'a'::text || a.id AS key, a.id, false AS is_event, a.name, a.types,
    a.types[1] AS type, a.location,
    CASE WHEN a.place_id IS NOT NULL THEN ap.name  ELSE NULL::text END AS place,
    CASE WHEN a.place_id IS NOT NULL THEN ap.kind  ELSE NULL::text END AS place_kind,
    a.km, a.cost, a.ages, a.description, a.url,
    NULL::text AS info_url, NULL::text AS ticket_url,
    a.conditions, a.rating, a.notes, a.duration, a.season, a.daypart,
    NULL::date AS starts_on, NULL::text AS time_text, NULL::text AS recurrence,
    NULL::text AS date_confidence,
    COALESCE(a.lat, ap.lat)::numeric AS lat,
    COALESCE(a.lng, ap.lng)::numeric AS lng,
    a.verified, a.added_by, a.created_at, a.kind, ak.family,
    a.published
   FROM activities a
     LEFT JOIN places ap ON ap.id = a.place_id
     LEFT JOIN kinds ak ON ak.name = a.kind
UNION ALL
 SELECT 'e'::text || e.id AS key, e.id, true AS is_event, e.name, e.types,
    e.types[1] AS type,
    CASE WHEN e.place_id IS NOT NULL THEN COALESCE(ep.suburb, e.location)
         ELSE e.location END AS location,
    COALESCE(ep.name, e.venue) AS place, ep.kind AS place_kind,
    e.km, e.cost, e.ages, e.description,
    e.info_url AS url, e.info_url, e.ticket_url, e.conditions,
    NULL::smallint AS rating, NULL::text AS notes, NULL::text AS duration,
    '{}'::text[] AS season, 'day'::text AS daypart,
    e.starts_on, e.time_text, e.recurrence, e.date_confidence,
    ep.lat::numeric AS lat, ep.lng::numeric AS lng,
    e.verified, e.added_by, e.created_at,
    'happening'::text AS kind, 'time'::text AS family,
    e.published
   FROM events e
     LEFT JOIN places ep ON ep.id = e.place_id;

-- An index, because the board's every read filters on it and this table only grows.
create index if not exists activities_published_idx on activities (published) where not published;
create index if not exists events_published_idx     on events     (published) where not published;
