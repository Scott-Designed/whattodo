-- Only a name is required now. Everything else can arrive later.
alter table activities alter column type drop not null;
alter table events     alter column type drop not null;

-- The vocabulary still applies to any type that IS given — null just means
-- "not sorted yet", it does not mean "anything goes".
select (select count(*) from activities) activities,
       (select count(*) from events)     events,
       (select count(*) from activities where type is null) unsorted;
