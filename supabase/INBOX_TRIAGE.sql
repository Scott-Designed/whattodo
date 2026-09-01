-- Triage on the inbox — 1 Sep 2026.
--
-- The inbox stored what arrived and nothing else, so every message was a pile
-- to work rather than a queue to skim: you could not tell the newsletter worth
-- twenty minutes from the one carrying nothing, without opening both.
--
-- `read` holds what the link reader found (pages, candidates, and the free
-- signals sniffed out of the prose). `triage` is derived from it and stored
-- separately ONLY so the list can filter and sort on it — it is never the
-- source of truth, and re-reading a message recomputes both.
--
-- Nothing here interprets a message on the reader's behalf. The states say how
-- much work a message is, never what it means.
alter table inbox add column if not exists read   jsonb;
alter table inbox add column if not exists triage text;

-- The vocabulary, checked, so a typo cannot invent a seventh state that the
-- page then silently never draws — the failure this project has paid for in
-- every other keyed map.
alter table inbox drop constraint if exists inbox_triage_valid;
alter table inbox add constraint inbox_triage_valid check (triage is null or triage in (
  'ready',      -- candidates found and nothing we already hold
  'duplicate',  -- everything in it is already a row
  'needs-you',  -- something real in it that no machine can read: prose, a poster
  'nothing',    -- no links, no dates, no known venue — probably not a listing
  'unread'      -- not looked at yet (the reader failed, or it predates this)
));

create index if not exists inbox_triage_idx on inbox (triage);
