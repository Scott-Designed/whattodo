-- ── the venue gets its own column in `listings` ──────────────────────────
-- Run this whole file in the Supabase SQL editor. PostgREST cannot redefine a
-- view, so this cannot be applied from a script.
--
-- Why: the Where column on the page was printing the suburb and nothing else.
-- "Torquay" does not tell you the gig is at the Torquay Hotel, and the venue
-- name was the only part anybody would have recognised. It was there in the
-- data the whole time — the view was folding it away:
--
--     coalesce(e.location, e.venue) as location
--
-- one column carrying either fact, so the page could never print both. Two
-- facts, two columns. `venue` is the place you walk into, `location` is the
-- suburb it is in, and the page prints the venue with the suburb beneath it.
--
-- For a linked event the venue row wins on suburb: `venues` is curated and
-- geocoded, while `events.location` came off the feed and has drifted (event 20
-- says Torquay for a gig at The Sound Doctor, which is in Anglesea). An
-- unlinked event still has only its own free text, so it keeps using that.
--
-- Activities get the column too — a view union needs the same shape on both
-- sides — but it stays null unless the activity is one of the licensed venues.
-- An activity is usually its own venue, and "Torquay Hotel, Torquay" under the
-- name "Torquay Hotel" is the same fact printed twice.
--
-- DROP then CREATE, not CREATE OR REPLACE: adding a column in the middle of a
-- view is a column-type change as far as Postgres is concerned (42P16). The
-- file runs in one transaction, so the view is never actually absent.

drop view if exists listings;

create view listings as
  select 'a'||a.id as key, a.id, false as is_event, a.name, a.type, a.location,
         case when a.venue_id is not null then av.name end as venue,
         a.km, a.cost, a.ages,
         a.description, a.url, null::text as info_url, null::text as ticket_url,
         a.conditions, a.rating, a.notes, a.duration, a.season, a.daypart,
         null::date as starts_on, null::text as time_text, null::text as recurrence,
         null::text as date_confidence,
         coalesce(a.lat, av.lat)::numeric as lat,
         coalesce(a.lng, av.lng)::numeric as lng,
         a.verified, a.added_by, a.created_at
    from activities a left join venues av on av.id = a.venue_id
  union all
  select 'e'||e.id, e.id, true, e.name, e.type,
         case when e.venue_id is not null then coalesce(ev.suburb, e.location)
              else e.location end,
         coalesce(ev.name, e.venue),
         e.km, e.cost, e.ages,
         e.description, e.info_url, e.info_url, e.ticket_url,
         e.conditions, null::smallint, null::text, null::text, '{}'::text[], 'day',
         e.starts_on, e.time_text, e.recurrence, e.date_confidence,
         ev.lat::numeric, ev.lng::numeric,
         e.verified, e.added_by, e.created_at
    from events e left join venues ev on ev.id = e.venue_id;

-- Dropping the view dropped its grants with it. The page reads as `anon`.
grant select on listings to anon, authenticated;

select count(*) filter (where is_event and venue is not null) as events_with_a_venue,
       count(*) filter (where is_event) as events
  from listings;
