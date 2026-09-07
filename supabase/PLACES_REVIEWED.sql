-- 7 Sep 2026. A place a machine creates is not a place a person has looked at.
-- The feed scrapers may now build a `places` row from the venue a feed publishes
-- (name, street, town, postcode, geocoded here) and every one of those lands
-- reviewed = false, so it sits in the /admin review queue beside the event it
-- carries. Everything already in the table was built or checked by a person,
-- hence the default. Only /admin ever sets it true.
alter table places add column if not exists reviewed boolean not null default true;
comment on column places.reviewed is 'false = created by a scraper and not yet looked at by a person; only /admin sets it true';

-- And who made it, the way events and activities already say. Null means a
-- person, which is everything before this date; a scraper writes its own key
-- ('coastandbay', 'surfcoastevents') so the review queue can group by source.
alter table places add column if not exists added_by text;
