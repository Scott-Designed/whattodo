-- ── 26 types become 42, and a listing can be more than one of them ───────
-- Run in the Supabase SQL editor, or via the Management API (see CLAUDE.md).
--
-- `type` was one word per listing, foreign-keyed to `types`. One word could not
-- hold what the data actually is:
--
--   * `gig` had 75 rows — 18% of everything — and ~20 were not music: four
--     Quiet Clubs, four Wadawurrung sessions, three film screenings, two
--     comedy nights, two canoe paddles, a book club, an AGM.
--   * `sport-event` had 22 — surfing, running, ocean swims, cycling and a
--     triathlon under one word, which is why the Run verb returned every swim.
--   * `cafe` had 21 rows of which four were cafés; the rest were wineries,
--     breweries, a distillery, a chocolaterie and a strawberry farm.
--   * Nothing could be two things. Bells Beach Surf Film Festival is a
--     festival, a surf thing and a film thing, so it was invisible to two of
--     the three searches that should find it.
--
-- So `types` is many values, array-checked against the vocabulary — the same
-- pattern as `conditions` in schema.sql and `offers` in PLACES_TAXONOMY.sql.
-- The first element is the primary: the word the row prints, the icon it draws.
--
-- Nothing is thrown away: the old single value moves to `type_legacy`.

begin;

-- The view reads `activities.type`, which is about to be renamed. Postgres
-- would follow the rename into the view definition and leave it selecting
-- `type_legacy` under the name `type`, which is exactly the quiet wrongness
-- this file exists to end. Drop it now and rebuild it deliberately at the
-- bottom.
drop view if exists listings;

-- ── the band means something different now ───────────────────────────────
-- It was place/community/event, which described where a row came from rather
-- than what it is, and nothing read it — checked across the page, the admin
-- page, both API functions and every script. So it is free to become the seven
-- groups the front end will offer.
--
-- The old check comes off here and the new one goes on at the very bottom.
-- Postgres validates a check against every existing row the moment it is
-- added, and between here and there the table still holds five words with old
-- bands that cannot be deleted until the foreign key is gone.
alter table types drop constraint if exists types_band_check;

-- ── the 42 ───────────────────────────────────────────────────────────────
-- Existing names that survive are updated in place; the 19 new ones inserted.
insert into types (name, band) values
  ('beach','water'),('surfing','water'),('swimming','water'),('paddling','water'),
  ('water','water'),

  ('walk','land'),('running','land'),('cycling','land'),('mountain biking','land'),
  ('skatepark','land'),('rock climbing','land'),('golf','land'),('nature','land'),

  ('parks & playgrounds','places'),('camping ground','places'),('night','places'),
  ('at-home','places'),

  ('cafe','food'),('bakery','food'),('restaurant','food'),('bar','food'),
  ('pub','food'),('winery','food'),('market','food'),('shop','food'),
  ('produce','food'),('farm life','food'),

  ('arts','culture'),('art gallery','culture'),('theatre','culture'),
  ('museum','culture'),('cinema','culture'),('cultural','culture'),

  ('gig','whatson'),('comedy','whatson'),('party','whatson'),('reading','whatson'),
  ('festival','whatson'),('workshop','whatson'),('community','whatson'),

  ('volunteering','involved'),('nursery','involved')
on conflict (name) do update set band = excluded.band;

-- Two words are on their way out but cannot go yet: their rows are split by
-- hand in scripts/retype.py, and until that has run they are still the only
-- thing those 35 listings say. Deleted in the follow-up, not here.
update types set band = 'land'    where name = 'sport';
update types set band = 'whatson' where name = 'sport-event';

-- ── the column ───────────────────────────────────────────────────────────
alter table activities add column if not exists types text[] not null default '{}';
alter table events     add column if not exists types text[] not null default '{}';

-- The renames and the one merge, applied as the backfill rather than as a
-- separate pass — a rename is not a decision anyone needs to review.
create or replace function type_renamed(t text) returns text
language sql immutable as $$
  select case t
    when 'surf'       then 'surfing'
    when 'bike track' then 'mountain biking'
    when 'camping'    then 'camping ground'
    when 'park'       then 'parks & playgrounds'
    when 'playground' then 'parks & playgrounds'
    else t end
$$;

update activities set types = array[type_renamed(type)] where type is not null;
update events     set types = array[type_renamed(type)] where type is not null;

-- every type must be in the vocabulary — conditions_valid(), reused
create or replace function types_valid(tags text[]) returns boolean
language sql immutable as $$
  select coalesce(bool_and(t in (select name from types)), true) from unnest(tags) t
$$;
alter table activities drop constraint if exists activities_types_valid;
alter table activities add  constraint activities_types_valid check (types_valid(types));
alter table events     drop constraint if exists events_types_valid;
alter table events     add  constraint events_types_valid check (types_valid(types));

-- ── retire the single column ─────────────────────────────────────────────
-- The foreign key has to go before the old words can be deleted from the
-- vocabulary. Found by catalogue rather than by guessing its name.
do $$
declare c text;
begin
  for c in
    select conname from pg_constraint
     where conrelid = 'activities'::regclass and contype = 'f'
       and conkey = array[(select attnum from pg_attribute
                            where attrelid='activities'::regclass and attname='type')]
  loop execute format('alter table activities drop constraint %I', c); end loop;
  for c in
    select conname from pg_constraint
     where conrelid = 'events'::regclass and contype = 'f'
       and conkey = array[(select attnum from pg_attribute
                            where attrelid='events'::regclass and attname='type')]
  loop execute format('alter table events drop constraint %I', c); end loop;
end $$;

alter table activities rename column type to type_legacy;
alter table events     rename column type to type_legacy;

-- RELAX_FIELDS.sql already dropped this, but a NOT NULL surviving here would
-- break every insert the moment nothing writes the old column any more.
alter table activities alter column type_legacy drop not null;
alter table events     alter column type_legacy drop not null;

delete from types where name in ('surf','bike track','camping','park','playground');

-- Every remaining word now carries one of the seven new bands, so the check
-- can go on and be validated.
alter table types add constraint types_band_check check (band in
  ('water','land','places','food','culture','whatson','involved'));

create index if not exists activities_types_idx on activities using gin (types);
create index if not exists events_types_idx     on events     using gin (types);

-- ── the view carries both ────────────────────────────────────────────────
-- `types` is the truth; `type` is its first element, so admin.html and anything
-- else still reading one word keeps working until it is moved over.
drop view if exists listings;

create view listings as
  select 'a'||a.id as key, a.id, false as is_event, a.name,
         a.types, a.types[1] as type, a.location,
         case when a.place_id is not null then ap.name end as place,
         case when a.place_id is not null then ap.kind end as place_kind,
         a.km, a.cost, a.ages,
         a.description, a.url, null::text as info_url, null::text as ticket_url,
         a.conditions, a.rating, a.notes, a.duration, a.season, a.daypart,
         null::date as starts_on, null::text as time_text, null::text as recurrence,
         null::text as date_confidence,
         coalesce(a.lat, ap.lat)::numeric as lat,
         coalesce(a.lng, ap.lng)::numeric as lng,
         a.verified, a.added_by, a.created_at
    from activities a left join places ap on ap.id = a.place_id
  union all
  select 'e'||e.id, e.id, true, e.name,
         e.types, e.types[1],
         case when e.place_id is not null then coalesce(ep.suburb, e.location)
              else e.location end,
         coalesce(ep.name, e.venue),
         ep.kind,
         e.km, e.cost, e.ages,
         e.description, e.info_url, e.info_url, e.ticket_url,
         e.conditions, null::smallint, null::text, null::text, '{}'::text[], 'day',
         e.starts_on, e.time_text, e.recurrence, e.date_confidence,
         ep.lat::numeric, ep.lng::numeric,
         e.verified, e.added_by, e.created_at
    from events e left join places ep on ep.id = e.place_id;

grant select on listings to anon, authenticated;

commit;

select (select count(*) from types)                            as vocabulary,
       (select count(*) from activities where types = '{}')     as activities_untyped,
       (select count(*) from events     where types = '{}')     as events_untyped,
       (select count(*) from listings)                          as listings;
