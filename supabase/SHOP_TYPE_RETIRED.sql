-- `shop` retired as a TYPE — 27 Aug 2026, Scott's call.
--
-- It had become a second copy of a fact the row already carried. Three rows
-- were `kind = 'shop'` AND `types = {shop, ...}`, which is one fact in two
-- columns; on The Running Company it was also the PRIMARY type, so the row
-- printed "shop" — the least informative word available — instead of
-- "running", which is what separates it from Patagonia.
--
-- The seven others were `kind = 'venue'` with `shop` in their types, where it
-- meant "this venue also sells goods". That fact now has nowhere to live in
-- `types`. If it is wanted back, it belongs in `places.offers` (a `retail`
-- value), which is the column for what a place DOES rather than what it IS.
--
-- Ten rows were stripped first, then the vocabulary row deleted; none was left
-- with an empty types list and no event carried it. 43 types -> 42.
--
--   a36  Great Ocean Road Chocolaterie   produce · shop      -> produce
--   a110 Anglesea Resale Shed (Tip Shop) shop · community    -> community
--   a290 Bellarine Wholefoods            shop · produce      -> produce
--   a336 Aireys Inlet General Store      cafe · shop         -> cafe
--   a341 Moriac General Store            cafe · shop         -> cafe
--   a442 Wye River General Store         cafe · shop         -> cafe
--   a443 Kafe Koala General Store        cafe · shop         -> cafe
--   a460 Patagonia Torquay               shop · surfing · …  -> surfing · …
--   a462 Bellbrae Clay                   arts · workshop · shop -> arts · workshop
--   a463 The Running Company Torquay     shop · running      -> running
--
-- `shop` as a KIND is untouched and is still one of the seven. This file
-- supersedes the ('shop','food') seed line in TYPES_MULTI.sql, which is left
-- as the record of what was actually run that day.

update activities set types = array_remove(types, 'shop') where 'shop' = any(types);
update events     set types = array_remove(types, 'shop') where 'shop' = any(types);
delete from types where name = 'shop';
