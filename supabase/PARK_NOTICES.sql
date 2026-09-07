-- Park notices — what Parks Victoria says is closed, 8 Sep 2026
--
-- Every park page on parks.vic.gov.au carries a server-rendered "Change of
-- Conditions" block: a site, a title, a paragraph. There is no feed and no
-- API behind it, so scripts/scrape_parks.py reads the thirteen park pages in
-- this region on the Mon/Thu Action and keeps this table in step with them.
--
-- THE WORDING RULE, decided with Scott 8 Sep 2026. Parks Victoria publishes
-- no licence statement anywhere on its site, so its text is State copyright
-- by default. A closure is a FACT and a fact with a link is not a copyright
-- question; a paragraph copied onto another site is. So:
--
--   title, site      their own words — a label for the fact, shown publicly
--   body             their paragraph, plain text — FOR THE BACK OFFICE ONLY,
--                    so a person can read what the notice says. The public
--                    board never prints it.
--   park_url         the link a reader follows to read it from them
--   until            a date read out of the body where the text states one
--                    plainly ("closed from 29 May to 25 September 2026");
--                    null when it does not, never inferred
--
-- The board prints "Parks Victoria notice: <title> — until <date>, read it at
-- <park>" and nothing else of theirs.
--
-- `key` is sha1(park, site, title), so a notice re-read on Thursday is the
-- same row. `active` is turned off when a park page that was read
-- successfully no longer carries the notice; it is never deleted, because a
-- closure that has lifted is a fact worth keeping and reversible if the
-- page was simply mid-edit.
--
-- `activity_ids` is which listings the notice attaches to: an exact
-- normalised match on the site's name, or a hand line in the script. Park-
-- wide notices ("Wye Road Closure" under "Great Otway National Park") attach
-- to nothing and are reported every run.

create table if not exists park_notices (
  id           bigserial primary key,
  key          text not null unique,
  park         text not null,             -- the slug on parks.vic.gov.au
  park_name    text not null,
  park_url     text not null,
  site         text,                      -- the h4: which part of the park
  title        text not null,             -- the h3: what the notice is
  level        text,                      -- 'warning' or null; their heading class
  body         text,                      -- their paragraph, back office only
  until        date,                      -- only when the body states one
  activity_ids integer[] not null default '{}',
  first_seen   date not null default current_date,
  last_seen    date not null default current_date,
  active       boolean not null default true,
  source_note  text
);

create index if not exists park_notices_active on park_notices (active) where active;

alter table park_notices enable row level security;

-- Readable with the anon key, like listings and places: these are Parks
-- Victoria's public notices. Nothing but the service key writes.
drop policy if exists "anon reads park notices" on park_notices;
create policy "anon reads park notices" on park_notices
  for select to anon using (true);
