-- Nothing reaches the board unapproved — 1 Sep 2026, Scott's rule.
--
--   "Anything that comes from an automation, doesn't get published as
--    'unverified' on site. Anything from scrapers goes in for review, and
--    doesn't go on site until I approve."
--
-- PUBLISHED.sql built the gate and only one source used it. This closes it over
-- everything, and the second half of the sentence is why it has to reach the
-- public Add form too: while a stranger's submission can still publish itself,
-- there are unverified rows on the site and the rule is simply not true.
--
-- Two changes, and the second is the one that makes it enforceable.

-- 1. Hold every row nobody has approved. 41 today: 28 from scrapers, 13 written
--    by hand and never checked off. Nothing is deleted and nothing is edited —
--    they are all still in `listings`, they are in the Review queue, and one
--    press each puts them back.
update activities set published = false where verified = false and published;
update events     set published = false where verified = false and published;

-- 2. RLS. The public Add form is going to send `published: false`, and a form
--    is a request rather than a guarantee: this is a public endpoint and the
--    page cannot be trusted to have run its own rules. The policy already
--    refuses a submission that dresses itself up as verified or as Research;
--    it now refuses one that dresses itself up as published.
--
--    This is the rule the project keeps learning: a rule the tooling does not
--    enforce is a rule that gets broken, and it will be reported as a decision
--    rather than as a mistake.
drop policy if exists "public add" on activities;
create policy "public add" on activities for insert to anon
  with check (verified = false and published = false
              and added_by is distinct from 'Research');

drop policy if exists "public add" on events;
create policy "public add" on events for insert to anon
  with check (verified = false and published = false
              and added_by is distinct from 'Research');
