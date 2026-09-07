-- 7 Sep 2026. listings carries ends_on so a two-day show can print its span
-- and a festival running across days counts as on today. CREATE OR REPLACE
-- may only append columns, which is why it is last on both halves.
create or replace view listings as
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
    ak.family,
    a.published,
    NULL::date AS ends_on
   FROM activities a
     LEFT JOIN places ap ON ap.id = a.place_id
     LEFT JOIN kinds ak ON ak.name = a.kind
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
    'time'::text AS family,
    e.published,
    e.ends_on
   FROM events e
     LEFT JOIN places ep ON ep.id = e.place_id;
