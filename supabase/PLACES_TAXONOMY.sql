-- ── venues become places, and a place can be more than one thing ─────────
-- Run in the Supabase SQL editor, or via the Management API (see CLAUDE.md).
--
-- Two problems with `venues.kind`, both visible in the data before this ran:
--
--   1. It was not a kind. 40 of 79 rows said "event venue", which records how
--      the row was created, not what the place is — it covered beaches, a
--      cenotaph, a library, a street, a carpark and a resort. 8 were blank.
--      The ~30 real values came off a music-venue spreadsheet, so the whole
--      vocabulary was a music-industry one applied to a coastline.
--
--   2. It was already two axes fighting over one column. `Hotel`, `Winery` and
--      `Beach` say what a place IS. `Live Music Venue` and `Entertainment
--      Venue` say what HAPPENS there. A single text column cannot hold both,
--      which is why the Torquay Hotel — a pub, a restaurant and a live music
--      room — could only be filed as `Hotel`.
--
-- So: `kind` is one value, what the place is, foreign-keyed like `types`.
-- `offers` is many values, what you can do there, array-checked like
-- `conditions`. The two existing vocabulary patterns in this schema, reused.
--
-- Nothing is thrown away: the old free text moves to `kind_legacy`.
--
-- Note on `hotel`: in Australia it is usually a pub. Every "Hotel" in the
-- music sheet — Torquay, Lorne, Apollo Bay, Barwon Club, Elephant & Castle —
-- is a pub, and the one that is actually accommodation (Mantra Lorne) was
-- never labelled one. So there is no `hotel` kind. Pubs are `pub`, places you
-- sleep are `accommodation`, and `offers` carries the rest.

alter table venues rename to places;
alter table events     rename column venue_id to place_id;
alter table activities rename column venue_id to place_id;
alter index if exists events_venue_idx     rename to events_place_idx;
alter index if exists activities_venue_idx rename to activities_place_idx;
alter policy venues_read on places rename to places_read;

-- what a place IS — exactly one
create table if not exists place_kinds (
  name text primary key,
  band text not null check (band in ('outdoors','food-drink','culture','sport','civic','stay'))
);
insert into place_kinds (name, band) values
  ('beach','outdoors'),('park','outdoors'),('reserve','outdoors'),('foreshore','outdoors'),
  ('pier','outdoors'),('lookout','outdoors'),('campground','outdoors'),('farm','outdoors'),
  ('pub','food-drink'),('bar','food-drink'),('brewery','food-drink'),('winery','food-drink'),
  ('distillery','food-drink'),('cidery','food-drink'),('cafe','food-drink'),
  ('hall','culture'),('theatre','culture'),('museum','culture'),('gallery','culture'),
  ('library','culture'),('community-centre','culture'),
  ('surf-club','sport'),('sports-ground','sport'),('showground','sport'),('playground','sport'),
  ('civic','civic'),('memorial','civic'),('school','civic'),('street','civic'),('carpark','civic'),
  ('accommodation','stay')
on conflict (name) do nothing;

-- what you can DO there — any number, including none
create table if not exists place_offers (name text primary key);
insert into place_offers (name) values
  ('live-music'),('food'),('drinks'),('coffee'),('tickets'),('market-stalls'),
  ('function-hire'),('playground'),('toilets'),('parking'),('accessible'),('dog-friendly')
on conflict (name) do nothing;

alter table places rename column kind to kind_legacy;
alter table places add column if not exists kind   text references place_kinds(name);
alter table places add column if not exists offers text[] not null default '{}';

create or replace function offers_valid(tags text[]) returns boolean
language sql immutable as $$
  select coalesce(bool_and(t in (select name from place_offers)), true) from unnest(tags) t
$$;
alter table places drop constraint if exists places_offers_valid;
alter table places add  constraint places_offers_valid check (offers_valid(offers));

alter table place_kinds  enable row level security;
alter table place_offers enable row level security;
drop policy if exists place_kinds_read  on place_kinds;
drop policy if exists place_offers_read on place_offers;
create policy place_kinds_read  on place_kinds  for select using (true);
create policy place_offers_read on place_offers for select using (true);

-- The view's column is `place` now, and it carries the kind alongside it so
-- the page can label a row without a second request.
drop view if exists listings;

create view listings as
  select 'a'||a.id as key, a.id, false as is_event, a.name, a.type, a.location,
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
  select 'e'||e.id, e.id, true, e.name, e.type,
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

grant select on listings    to anon, authenticated;
grant select on places      to anon, authenticated;
grant select on place_kinds to anon, authenticated;
grant select on place_offers to anon, authenticated;

select (select count(*) from places) as places,
       (select count(*) from place_kinds) as kinds,
       (select count(*) from place_offers) as offers;
