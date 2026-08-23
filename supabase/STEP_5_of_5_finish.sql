-- WhatToDo Jan Juc — final step: check the counts and set the id sequences.

select setval(pg_get_serial_sequence('activities','id'), coalesce((select max(id) from activities), 1));
select setval(pg_get_serial_sequence('events','id'),     coalesce((select max(id) from events), 1));

select (select count(*) from activities) as activities,
       (select count(*) from events)     as events,
       (select count(*) from listings)   as listings;
