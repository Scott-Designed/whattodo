# The community — worklog

Pass run 31 Aug 2026, volunteering then community, per the loop in the prompt. Repo cloned
fresh from `origin/main`. **Nothing has been written to Supabase** — this session had no
`.env`, so both batches were built and validated with `python3 scripts/sync.py check`, which
runs the same `check()` and the same live vocabularies `add` does. They need one
`--dry-run` each and then the real run. See **Handover**.

Counts at the start, from `scripts/have.py community`:
`reading 104 · kids 88 · workshop 65 · community 32 · volunteering 12` = 222 (before overlap).

**Library rows were left alone,** as instructed. Reading, kids and most of workshop are the
Geelong Regional Libraries import and arrive twice a week on their own. No story time was
added, and nothing on this pass touches a library row.

`python3 scripts/nearby.py --refresh` was run once as the prompt asks and **every Overpass
endpoint refused this address** (connection reset from overpass-api.de, 403 through the
proxy for kumi and private.coffee). It made no difference: the prompt already says OSM has
nothing for this group, and the cached `scripts/osm_cache.json` was not needed either. No
per-town query was attempted afterwards.

---

## volunteering — 12 existing, 20 built

**What was already there.** Read carefully, the 12 are six coastal working-bee groups
(Jan Juc Coast Action, Torquay Coast Action, ANGAIR, SANE, Surfrider, Torquay Landcare),
EstuaryWatch, Bellarine Catchment Network, and the three mountain bike clubs carrying
`volunteering` as a secondary type. **Every "Friends of" group on this coast was missing** —
`ilike '%Friends%'` returned nothing at all.

**Searched.** Surf Coast Shire's own Get-involved page (the council's list of environmental
groups); GORCC's three district volunteer pages — Torquay, Anglesea & Aireys Inlet, and
Fairhaven to Lorne — which are the authority's own register and the single best source in
this group; the Victorian Landcare Gateway for the Corangamite region; the Surf Coast &
Inland Plains network's own site; and then each group's own site where it has one.

**Built (20).** All `kind: "group"`, all `km` absent, and **not one carries a coordinate** —
correct for this kind, and each `source_note` says why rather than leaving it blank:

- **From GORCC Torquay district:** Friends of Taylor Park · Friends of Deep Creek ·
  Friends of Jan Juc Creek · Friends of Cosy Corner
- **From GORCC Anglesea & Aireys Inlet district:** Friends of Aireys Inlet Coastal Reserve ·
  Friends of Anglesea Coast · Friends of the Eagle Rock Marine Sanctuary ·
  Friends of Point Addis · Friends of Eastern Otways
- **From GORCC Fairhaven to Lorne:** LorneCare · Friends of Queens Park Lorne ·
  Friends of Moggs Creek
- **Landcare:** Surf Coast & Inland Plains Landcare Network · Breamlea Coast Action ·
  Connewarre Landcare Group · Bellarine Landcare Group
- **Organisations:** Surf Coast Environment Group · Geelong Sustainability ·
  Repair Café Surf Coast · Rotary Club of Torquay

**No event row was invented for any of them.** Nine of the twenty publish a recurrence —
"first Sunday, 10am", "second Saturday, 10am-12pm" — and that is exactly the inference this
project is named after. The day and time are in `notes`, with the standing warning that a
monthly does not roll forward.

**Two of these fill gaps this file has already recorded.**

- **Surf Coast Environment Group** has been `places` row 81 with a Humanitix feed for weeks
  and had no listing of its own. Same shape as the Surf Coast Mountain Bike Club: a places
  row is not a listing, so the group was invisible on `/volunteering`.
- **Geelong Sustainability** is named in CLAUDE.md as the body that "holds its events in
  other people's rooms and was never registered at all". A group row is the answer to that —
  its events keep landing at whichever venue it hired, which is right.

**Rejected, and why.**
- **Barwon Heads Landcare** — named on the SCIPN site as a member group, but the Landcare
  Gateway slug 404s and it has no page of its own. Nothing first-party to describe. Worth a
  second look by somebody who can ask SCIPN directly.
- **Surf Life Saving club patrol membership** — every club is already a `places` row and
  `Nippers` (289) covers the junior side. A row called "volunteer patrolling" would be an
  abstraction, not a thing you can join at an address.
- **CFA and SES brigades** — not attempted. They are real volunteering and they are on the
  prompt's source list, but a brigade's contact route is a recruitment page per district
  rather than per brigade, and getting that wrong sends somebody to the wrong station. Left
  for a pass that can check them one at a time.
- **Rubbish Rangers (Aireys Inlet, Anglesea, Torquay)** and **Plastic Wise Torquay /
  Winchelsea** — real, listed on the council's page, but Facebook-only with no page this
  session could read to write an honest description. The council listing is a valid `url`
  under the rules, so these are cheap for the next pass; they are not guesses, just unread.

**Notes on particular rows.**
- **Bellarine Landcare Group** is deliberately separate from activity 140,
  `Bellarine Landcare Nursery – Drysdale`. The nursery is the shopfront and a venue —
  CLAUDE.md settled that when the seven nurseries came out of `group` — and the group is the
  thing you join. Filed under Drysdale, not its Mannerim office, for the reason below.
- **Repair Café Surf Coast** is the group; event 4 is its 13 September session. It is not
  `Repair Cafe Bellarine – Ocean Grove` (132), which is a different organisation.
- **Rotary Club of Torquay** meets at a hired venue (The Lakehouse, Kithbrooke Park) and is
  not pinned there. Organiser is not the venue.
- **`scipn.org.au`, the address on the Victorian Landcare Gateway, does not resolve.**
  `scipn.com.au` is live and is what the row carries — as does existing row 129.

---

## community — 32 existing, 16 built

**What was already there, once the library rows are set aside.** Of the 32, eleven are dated
one-off events, two are library programme rows, and the genuinely evergreen community
listings are a handful: two community gardens, the Art House, the Tip Shed, the Dome, the
choir, two Repair Cafés, Nippers and the run crew. **There was no neighbourhood house in the
database at all** — not one of the five Surf Coast Shire houses, none on the Bellarine.
`ilike '%Community House%'` matched one `places` row and no listing; `'%Neighbourhood%'`
matched four at-home ideas about walking around your own street.

**Searched.** Surf Coast Shire's own community houses page; the Neighbourhood Houses Barwon
"find a centre" directory (the sector's own register, which covers Greater Geelong, the
Bellarine, Surf Coast and Colac Otway); then each house's own site. Then the Australian and
Victorian Men's Shed Associations; U3A; toy libraries; and the Anglesea Community House
community directory, which is the best single index of Anglesea groups anywhere.

**Built (16).**

- **Neighbourhood and community houses (9):** Torquay Community House · Anglesea Community
  House · Winchelsea Community House · Lorne Community House · Marrar Woorn Neighbourhood
  House (Apollo Bay) · Queenscliffe Neighbourhood House · SpringDale Neighbourhood Centre
  (Drysdale) · Ocean Grove Neighbourhood House · Leopold Community & Learning Centre
- **Groups (5):** Deans Marsh Community Cottage · Torquay Community Men's Shed ·
  Ocean Grove & District Men's Shed · U3A SurfCoast · Anglesea Community Garden
- **Toy libraries (2):** Surf Coast Toy Library (Torquay) · Ocean Grove Toy Library

**A term timetable is not an event.** Every house here runs to school terms, so all nine are
activities with the timetable and hours in `notes`, exactly as the prompt asks. Not one
dated row was written from a house's programme.

**Coordinates.** Eight rows carry a pin; every one of them was geocoded, reverse-geocoded
and lands on a `house_number` + `road` + `town` — no administrative polygon, nothing in the
water, nothing under four decimal places. Two are the strongest kind of match, where OSM
names the building itself: **Lorne Community House** and **Springdale Neighbourhood
Centre**. Each `source_note` records which kind of match it was.

**Four rows are deliberately unpinned, and the reasons differ:**

- **Anglesea Community House** — because the venue is already `places` row 42, pinned from
  the same address on 24 Aug. The row links through `place_id: 42` instead of carrying a
  second copy that can drift. This is the cheapest kind of map coverage there is.
- **Marrar Woorn Neighbourhood House** — OSM has no house number on Pengilley Avenue. Both a
  plain and a structured Nominatim query return only the street way, whose bounding box is
  about 420 m long, and reverse-geocoding that midpoint lands on number 14 while the house
  publishes number 6. **A street-midpoint pin was written and then removed** during the
  verification step. Null is honest.
- **Ocean Grove Toy Library** — the Boorai Centre has no OSM match, and Shell Road runs
  several kilometres out to Marcus Hill, so a centreline would be a kilometre-scale guess.
- **Deans Marsh Community Cottage** — see below. This one is the organiser-is-not-the-venue
  trap and it nearly caught this pass.

**Deans Marsh Community Cottage has no pin on purpose.** The Surf Coast Shire directory
gives its address as 10 Pennyroyal Valley Road, which is the **Deans Marsh Community Hall** —
activity 495 and `places` 167, already pinned. Nothing first-party separates the cottage
building from the hall, and its own site lists events at both the hall and The Store. Pinning
the organisation at the hall would have put a second row on an existing coordinate and
claimed a building this pass cannot see.

**Two men's sheds carry a pin even though they are groups**, which is a deviation worth
Scott's eye. The rule is that a group usually has no coordinate because it hires its rooms;
a men's shed occupies premises it publishes as its own address — 18 Price Street, Torquay
(behind the Old Police Station) and 17 Smithton Grove, Ocean Grove. Both `source_note`s say
this explicitly. **If the rule is meant to be absolute, null those two and nothing else
changes.**

**Rejected, and why.**
- **Portarlington Neighbourhood House** — its own site still carries a COVID-era notice
  saying it is "temporarily closed pending Department of Health & Human Services approval to
  reopen". It leases Parks Hall from the council, so the address is a hired room as well.
  Current status needs a person, not a research pass.
- **Forrest & District Neighbourhood House** — the page on forrestvictoria.com is dated
  February 2018 and carries no address, hours or contact. Real house, unreadable source.
- **The nine Greater Geelong houses** — Geelong West, Grovedale, South Barwon, Vines Road,
  Cloverdale, Rosewall, Norlane, Whittington, Lara — all listed with addresses on the
  Neighbourhood Houses Barwon directory and all in region. Left for a following pass rather
  than written thin: this one worked the coast first, as the prompt asks. **Two of them need
  a location decision** — Whittington and Hamlyn Heights are not in `SUBURBS`, so they have
  to be written as `"…, Geelong"` to land anywhere. Checked: that string does resolve.
- **U3A Geelong** — real and in region, but U3A SurfCoast is the local one and a second U3A
  adds a Geelong row rather than a Surf Coast one. Cheap for the next pass.
- **Playgroups** — searched, nothing written. The playgroups here run *inside* the community
  houses (Torquay's is a Torquay Community House programme), so a separate row would be a
  second listing for one thing. Recorded rather than written.
- **Anglesea Community Garden** was written; the council's other gardens — Danawa, Lorne,
  Winchelsea — were not, for lack of a first-party page this session could read.
  **"Community Garden 3231" on the council's list is the Aireys Inlet Community Garden**,
  activity 112, already held under a different name.

---

## Findings for a person — none of these were touched

1. **Activity 112, `Aireys Inlet Community Garden`, carries a Google Maps *search* url.**
   `https://www.google.com/maps/search/Aireys+Inlet+Community+Garden+Victoria`. It is one of
   the 37 standing defects this file records, and it is in this group, so it is named here.
2. **Activity 543, `Bellarine Catchment Network`, lands in no place page.** Its `location` is
   `"865 Swan Bay Road, Mannerim"`, and Mannerim is not in `SUBURBS` — `suburbOf()` returns
   null, checked through `notice-vocab.js` itself. Drysdale is the nearest town in the
   vocabulary; the new Bellarine Landcare Group row is filed there for the same reason.
3. **Activity 140, `Bellarine Landcare Nursery – Drysdale`, looks pinned in the wrong place.**
   It sits at `-38.1744, 144.5706`, which is Drysdale's High Street — about 50 m from the
   SpringDale Neighbourhood Centre this pass just geocoded. Bellarine Landcare's own site
   gives the nursery as **Belchers Road, Drysdale**, whose street centreline is
   `-38.1946, 144.5536`, **2.4 km south-west**. Not corrected here: Belchers Road is a
   centreline, not the nursery gate, so this is a report and not a replacement coordinate.
4. **Activities 124 and 129 share one coordinate exactly.** `Torquay Coast Action – Working
   Bees` and `Torquay Landcare Group` are both at `-38.3364, 144.3239`. Torquay Landcare
   publishes only a PO box; its working sites are across the hinterland. That reads as
   copy-paste rather than geocoding — the pattern the 24 Aug sweep was chasing.
5. **The Anglesea Twilight Market's organiser is the Anglesea Community House.** The produce
   prompt asks what that market actually is; ACH names it as one of its own. Its recurrence
   is still unset in the events table.
6. **The Deans Marsh Festival's organiser is the Deans Marsh Community Cottage**, along with
   Run the Marsh, the markets and the dog trials.
7. **Repair Café Surf Coast publishes its remaining 2026 dates first-party** — Sunday
   13 September, 4 October, 8 November, 6 December, 10am–1pm at the Aireys Inlet Community
   Hall, last repairs 12:30pm. Event 4 holds 13 September. The other three were **not**
   written, because three rows named "Repair Café" is a duplicate problem and the dates
   belong to a decision about how a monthly series is stored, not to this pass. The Anglesea
   Community House page for the same event still shows a 2024 calendar and 10am–2pm; the
   group's own site is the one to trust.

## `places` candidates — `/admin` work, no script can do it

- **Place 42, `Anglesea Community House`, has no `website` and no `events_url`.** Its site is
  `https://anglesea.org.au/`, which carries both an events calendar and the town's community
  directory. This is the one registration on this pass that is clearly worth making.
- **Repair Café Surf Coast** is an organiser, not a room — the Sound Doctor case. If it is
  registered it wants its own `places` row with `kind_legacy = 'organiser'` and
  `events_url = https://repaircafesurfcoast.tech/`, **not** an `events_url` on place 39, the
  Aireys Inlet Community Hall, which hosts other things.
- **Nine houses and centres now have a listing but no `places` row** — Torquay, Winchelsea,
  Lorne, Marrar Woorn, Queenscliffe, SpringDale, Ocean Grove NH, Leopold, plus the two men's
  sheds. Only worth adding where something will actually host events.

**No claim is made here about whether any of those pages is machine-readable.**
`eventlib.fetch` returns empty for every URL from this session's container, including
`example.com` — the egress is blocked, not the sites. The music pass's rule applies and was
followed: verify a URL with the fetcher that will actually read it, which means somebody
running this on a normal connection before any `events_url` is set.

---

## Handover

Two batches, both validated, neither written:

    python3 scripts/sync.py add /tmp/wt/volunteering.json --dry-run   # 20 rows
    python3 scripts/sync.py add /tmp/wt/community.json    --dry-run   # 16 rows

`sync.py check` passes on both — 36 rows, 36 to `activities`, 0 to `events`, no name clash
against the live tables. Every row: `added_by` defaults to Research, `verified` unset, a
`source_note` naming a page and the date it was read, no `km`, no coordinate under four
decimal places, no Google Maps search url, and a `location` ending in a town `suburbOf()`
recognises — all 36 checked through `notice-vocab.js` itself, not a second copy of the list.

Next in this group, in order of value: the nine Greater Geelong neighbourhood houses; the
Facebook-only Rubbish Rangers and Plastic Wise groups off the council's page; U3A Geelong;
CFA and SES by district; Barwon Heads Landcare via SCIPN.
