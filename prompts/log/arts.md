# The arts & culture pass — 28 Aug 2026

Group at 55 listings when this started: arts 16 · cinema 13 · museum 10 ·
cultural 9 · art gallery 6 · theatre 1. Worked thinnest first.

**29 rows built and validated; NOT YET WRITTEN.** `sync.py` exits at line 36
without `SUPABASE_URL`/`SUPABASE_SERVICE_KEY`, and it does that *before* it
parses anything, so `--dry-run` is blocked as well as the write. The batches
sit at `/tmp/arts/{theatre,gallery,museum,cinema,arts}.json`. All 29 were run
through `sync.py`'s own `check()` against the live vocabularies using the anon
key — **0 complaints** — and all 29 names checked against the 628 existing
names for exact collisions — none.

    theatre 6 · art gallery 8 · museum 8 · cinema 5 (1 activity + 4 events) · cultural 0 · arts 2

---

## Two tooling faults found first

### 1. `nearby.py --kinds arts` cannot return a museum, a gallery or a public artwork

This is the `--kinds produce` fault wearing a new coat, and it is worse, because
it silently removes exactly what two of this group's six types are made of.

`KIND_TAGS['arts']` correctly asks Overpass for `tourism={museum, gallery,
artwork, attraction}` and `historic={memorial, monument, heritage, museum}`.
The data comes back. Then line 169:

```python
label = t.get('amenity') or t.get('shop') or t.get('craft') or t.get('landuse')
```

never reads `tourism` or `historic`, so every one of those POIs is cached with
`label: None`. Line 280 then drops them:

```python
if p['label'] not in keep:      # None is never in keep
    continue
```

**272 of the 2049 cached POIs are affected** — every museum, every gallery,
every public artwork, every attraction and every memorial in the region. The
sweep reports them as not existing. Anglesea Museum, the Old Cable Station
Museum, Salt and Pepper Gallery, Art Reach Studio, Tin Liz Gallery, Oxide Arts,
the Fat Ladies, Bunjil, the Memorial Arch — none of them can appear in
`nearby.py "<town>" --kinds arts` output today.

The one-line fix, which needs a `--refresh` to take effect because the label is
computed at fetch time and cached:

```python
label = (t.get('amenity') or t.get('shop') or t.get('craft')
         or t.get('landuse') or t.get('tourism') or t.get('historic'))
```

**I did not apply it and did not re-run `--refresh`** — the instruction was one
refresh for the pass. I worked around it by reading `osm_cache.json` directly
and matching the 272 unlabelled POIs to their nearest town, which recovered the
whole set. Worth applying before the next pass touches this group.

The generalisable bit is the same one the produce pass wrote down: **a search
tool that returns nothing looks identical to a region that contains nothing.**
Both faults were a filter quietly discarding rows, and neither printed anything.

### 2. `deansmarshspark.org.au` does not resolve

Surf Coast Shire's own Community Arts Facilities page gives it as SPARK's
website. DNS failure, checked 28 Aug 2026. The Deans Marsh row carries `url:
null` rather than a link that would 404 forever.

---

## theatre — 1 listing, 6 rows built

`have.py theatre` returned exactly one row: The Palais Geelong.

**Swept:** Geelong, Lorne, Winchelsea, Queenscliff, Torquay, Anglesea via
`nearby.py --kinds arts`. Geelong returned 31 names (Costa Hall, McAuley Hall,
The Open House, The Playhouse, The Story House all tagged `theatre`). **Lorne
returned 4, Torquay 3, Queenscliff 1, Anglesea 0, and Winchelsea 0** — while
Winchelsea has a working heritage theatre with a monthly film club in it. The
by-hand check beat the map again, and by more than it did on produce.

The source that did the work is **Surf Coast Shire's Community Arts Facilities
page**, which lists nine rooms with addresses. Nothing on the map would have
found Yellow Gums or the Deans Marsh kiln.

**Added:**

| row | where | how sourced |
|---|---|---|
| Shoestring Playhouse | The MAC, 77 Beach Rd, Torquay | ttt.org.au + shire arts organisations page |
| The Potato Shed | 41 Peninsula Drive, Drysdale | City of Greater Geelong's own venue site |
| Globe Theatre | 17 Willis St, Winchelsea — `place_id 57` | shire facilities page + growingwinchelsea.com |
| Yellow Gums Performance Space | 89–91 Sunset Strip, Jan Juc | shire facilities page |
| Deans Marsh Community Hall | 10 Pennyroyal Valley Rd, Deans Marsh | shire facilities page |
| Anglesea Performing Arts | Anglesea Memorial Hall — `kind: group` | shire arts organisations page |

Torquay Theatre Troupe's home room is the **Shoestring Playhouse**, inside The
MAC at 77 Beach Rd — the same complex as place 46 (surfing museum) and place 98
(Hoop Gallery). That is the HOOP case, not the placeholder case. The Playhouse
is pinned to the `77, Beach Road` address point rather than the museum node the
other two share, so the three do not stack on one pin.

**Rejected / not written:**

- **Costa Hall, McAuley Hall, The Open House, The Playhouse, The Story House**
  (Geelong, all OSM `amenity=theatre`) — The Playhouse and The Story House are
  rooms *inside* Geelong Arts Centre, which is already listed, so listing them
  would be the 32-duplicates problem by another route. Costa Hall is real and
  separate (Deakin Waterfront, programmed by GPAC) but geelongartscentre.org.au
  has no venues page that resolves — its `/visit/venues/` 404s — so I could not
  source an address first-party. **Left for the next pass.**
- **The Wool Exchange Entertainment Complex** (place 34) — a function and
  entertainment venue, not a theatre with a season. Marginal; left.
- Skip Jack Theatre, Surfcoast Wildmovers, Riverlee Art Studio, Singing For Fun
  (shire arts organisations page) — all are people rather than rooms, with no
  venue of their own and, for three of them, only a mobile number. `group` rows
  are possible but they are contact records, not things to do.

---

## art gallery — 6 listings, 8 rows built

**The single most useful find: `The HOOP Gallery has no listing at all.`** It
has *two* place rows (98 and 102) and two events pointing at it, but the gallery
itself has never been a row. It is the carried-over candidate from the earlier
passes and it is now written, linked to `place_id 98`.

**Added:** Hoop Gallery (Torquay, `place_id 98`) · Salt & Pepper Gallery
(Bellbrae) · Surfcoast Gallery (Torquay) · Eagles Nest Fine Art Gallery (Aireys
Inlet) · Anglesea Art Space (`place_id 41`) · Art Reach Studio Gallery (Beech
Forest) · Oxide Contemporary Arts (Geelong) · Boom Gallery (Geelong West).

Two of the four carried-over candidates are in: **Salt & Pepper Gallery** at 557
Great Ocean Rd and **Art Reach Studio** at Beech Forest. Both were found only by
reading the cache around the broken label filter — neither appears in a
`--kinds arts` sweep. **Bellbrae Clay** is already listed (462). The fourth,
**the HOOP Gallery**, is above.

**Art Reach Studio is deliberately flagged.** Its own domain resolves but
renders client-side and returns no text, so its hours and current trading status
are *not* first-party confirmed — the row says so in `notes` and `source_note`.
It matters out of proportion to its size because the hospitality pass concluded
Beech Forest has no food at all after the Ridge Organic Store closed, and OSM
carries a second node at the same point tagged `amenity=cafe`, which is why the
row carries `cafe` as a second type.

**Existing row needs correcting: `Surf Coast Shire's own Galleries page is
stale.`** It gives Surfcoast Gallery as 4/110 Surf Coast Highway; the gallery's
own site says **2C Gilbert Street**. The row uses Gilbert Street. Worth knowing
the shire page is not authoritative on addresses — it was right about every
gallery's existence and wrong about this one's location.

**Logged, not written** — real galleries, no first-party page reachable:

- **The Lightbox**, 2/7-9 Cylinders Drive, Torquay — shire page, phone only
- **Leighton Edwards Art**, 2/13 Pearl Street, Torquay — shire page, phone only
- **Surfcoastimages Gallery**, 184 Fischer Street, Torquay — surfcoastimages.com.au
- **Moongate Studios**, 90 Elkington Road, Bellbrae — jangeoart2.com
- **The Bellbrae Pottery**, 55 Moores Road, Bellbrae — no website
- **Art Aireys**, 23 Anderson Street, Aireys Inlet — no website
- **The Great Ocean Road Story**, 15 Mountjoy Parade, Lorne — inside the Lorne
  Visitor Information Centre; greatoceanroadstory.com.au
- **Shire Hall Tea Rooms**, Winchelsea (place 78 exists) and **SPARK**, Deans
  Marsh — listed by the shire as exhibition spaces
- **James Street Gallery** and **Shearers Arms Gallery**, Geelong — OSM named
  `tourism=gallery` nodes, nothing else found
- **Wyndham Art Gallery**, 177 Watton Street, Werribee — OSM named node;
  wyndham.vic.gov.au returned 403. Werribee is in `SUBURBS` but is the far edge
  of the region, so this one is a judgement call for Scott as much as a sourcing
  problem.

**Tin Liz Gallery — left out on a coordinate conflict, and it is worth
recording.** OSM has a named `tourism=gallery` node at Andersons Road, Mannerim,
Drysdale (-38.1957654, 144.6159718), plus a second, `Little Tin Local Gallery`,
2m away. But quiddityplace.com.au says Tin Liz Gallery is one of its tenants,
alongside Oakdene's cellar door and the Hidden Frog restaurant — and Quiddity
Place is on Grubb Road, Wallington, several kilometres from the OSM node. Two
sources placing one gallery in two towns is exactly the "two rows disagreeing"
signal this project treats as a bug report. **Unsure, so left out.**

---

## cultural — 9 listings, 0 rows. This is a finding, not a gap.

Worked strictly to the brief: Wadawurrung Traditional Owners Aboriginal
Corporation, Parks Victoria, or a council page written with Traditional Owners,
and only where the source says the place is open to visitors.

**Nothing qualified, and here is each door I tried:**

- **wadawurrung.org.au** — the corporation's own site describes its statutory
  role under the Aboriginal Heritage Act and its services to organisations. It
  names no visitor-facing site, tour or centre. Its **Book Online** page returns
  office addresses and a phone number and nothing bookable.
- **The Wadawurrung Cultural Education Sessions sell through Humanitix**, which
  this project must not fetch — their robots.txt permits `whattodo-janjuc` and
  disallows `ClaudeBot`. So a Claude session structurally cannot add sessions
  beyond the four already in the database. **The scheduled Action can.** Those
  four (events 112, 115, 117, 118) all already carry a `place_id`, so there is
  no place-less-event problem in this type.
- **Parks Victoria, You Yangs Regional Park** — acknowledges the park as "part
  of an Aboriginal cultural landscape in the traditional Country of the
  Wadawurrung People" and names exactly one visitable feature, the **Bunjil
  Geoglyph Day Visitor Area**.
- **Surf Coast Shire's Aboriginal heritage page** — carries an Acknowledgement
  of Country and names no site at all.

**Bunjil Geoglyph was deliberately filed under `arts`, not `cultural`.** Parks
Victoria's own page for that site says it is "a spectacular stone structure, in
the shape of a wedge tailed eagle" made by artist **Andrew Rogers** to
commemorate the 2006 Melbourne Commonwealth Games, and says nothing about a
Wadawurrung connection to the geoglyph itself. Filing a 2006 artwork by a named
non-Indigenous artist as a Wadawurrung cultural site would be me writing
significance the source does not claim, which is the one thing the brief says
not to do. It is a genuine destination and it is now listed — under the type
that is true.

Everything else the searches surfaced (Buckley's Cave, assorted "Aboriginal
heritage of the Surf Coast" pages) came from tourism sites and was not opened.

---

## museum — 10 listings, 8 rows built

Sourced by putting nine candidates through a first-party check. Every row's
hours and admission are quoted from the operating body's own page, or marked
"not stated" and left null.

**Added:** Queenscliffe Historical Museum · Old Court House Museum (Drysdale) ·
Geelong Sports Museum · The Heights Heritage House and Garden · Anglesea Museum
· Lara Heritage and History Museum · Old Cable Station Museum (Apollo Bay) ·
Museum of Play and Art (Geelong).

Three carry an explicit honesty flag rather than a guess:

- **Anglesea Museum, Lara Museum and MoPA publish no opening hours at all** on
  their own sites. `cost` and hours are null and `notes` says so. Not filled in
  from a review site.
- **Old Cable Station Museum's own site blocks crawlers** (robots.txt fetch
  fails on every attempt). Its hours — Sat 2–5pm, Sun 10am–1pm, $10/$5 — come
  from the museum's **self-authored profile on Victorian Collections**, a
  museum-managed platform, not a review site. That is one step short of
  first-party and the `source_note` says which.
- **Lara Museum's street number disagrees with OSM.** Its own site says 2–10
  Canterbury Road West (cnr Forest Road South); the OSM node named "Lara
  Heritage and History Museum" carries an address tag of 110. The pin is the
  named node; the `location` string is the museum's own number.

**Rejected:**

- **Portarlington Mill** — the National Trust's own page says "Portarlington
  Mill is currently closed" and "temporarily closed until further notice".
  A visitable-museum row would be wrong. **Not written.** This is the Ridge at
  Beech Forest lesson holding: a name that will not confirm as open is often a
  place that has stopped being one.
- **B-24 Liberator Museum** and **RAAF Museum Point Cook** (Werribee /
  Point Cook, both in the OSM sweep) — wrong direction, outer Melbourne. Out.
- **Nura Gallery / Nepean Historical Society** — 10.5km from Queenscliff but
  across the heads at Sorrento, which is Mornington Peninsula. Out.

Note Queenscliff now holds **four** museums between them — Maritime, Fort
Queenscliff, Marine & Freshwater Discovery Centre, and the Historical Museum
added here — within a few streets. Worth a "museum town" angle on the place page
some day.

---

## cinema — 13 listings, 5 rows built (1 activity, 4 events)

**Added activity:** Winchelsea Movie Club (`kind: group`, `place_id 57`).

**Added events, all with a `place_id` and all weekday-checksummed:**

| event | date | place |
|---|---|---|
| Winchelsea Movie Club – The Book Thief | 2026-09-17 | 57 Globe Theatre |
| Anglesea Movie Club – Living | 2026-09-11 | 80 Anglesea Memorial Hall |
| Anglesea Movie Club – The Princess Bride | 2026-10-16 | 80 |
| Anglesea Movie Club – The Sapphires | 2026-11-20 | 80 |

All four dates are printed on the organiser's own page, so `date_confidence:
high`. Every printed weekday checks out against the 2026 calendar. Two are worth
noting:

- **17 September is a Thursday in 2026 and a Wednesday in 2025**, which is a
  free currency check on the Growing Winchelsea page — it could only have been
  written for this year.
- **11 September 2026 is the *second* Friday**, while the Anglesea club's stated
  pattern is the third. Recorded as printed, not corrected. The club moved that
  one; guessing 18 September would have been the Arts Trail failure in miniature.

The Anglesea Movie Club's full Feb–Nov 2026 season is published as a PDF on
Anglesea Community House's site. Only the three remaining dates were written —
the seven that have already happened were not.

**Findings, no row:**

- **Torquay has no cinema.** Asked and answered: no first-party site exists, and
  every "Torquay cinema" search result is Torquay, Devon. The **Surf Coast Film
  Society**, which nominally covers Torquay, states on its own page "THE FILM
  SOCIETY IS CURRENTLY ON A BREAK" with "Dates for 2021 TBC!" — dormant, and it
  screened at the Anglesea Fire Station community room anyway. **Do not list.**
  Surf Coast Times has covered a proposed Torquay cinema that was never built.
- **Apollo Bay is unresolved for a mechanical reason, not an absence.** Great
  Ocean Road Cinemas — the same operator as the Lorne Theatre — maintains
  `greatoceanroadcinemas.com.au/apollo-bay/`, but five fetch attempts all failed
  on robots.txt. The venue is very likely live. **Needs a browser check by a
  person**; the widely-quoted "21 Great Ocean Road" address is third-party only
  and was not written.
- **Barwon Heads Film Society** (already listed, a108's neighbour) has no
  website — only a robots-blocked Facebook page. The Federation of Victorian
  Film Societies directory confirms it is a current member, contact Alex
  Kuebler, format DVD, but publishes no venue, day or fee. Nothing addable.
- **Queenscliff Film Festival** (formerly Bellarine Lighthouse Film Festival),
  Queenscliff Town Hall, 50 Learmonth St — **both its own site and the Borough's
  page are stale**. The festival site's latest dates are June 2024, its About
  page cites August 2023, and the council page describes the 2022 edition. No
  2026 edition is published anywhere first-party. **Not written** — an annual
  festival needs a real published next date, and this is precisely the pattern
  that put the Arts Trail in the database on the wrong date for months.
- **Village Cinemas Geelong** and **Reading Cinemas Waurn Ponds** are both
  already listed and both confirmed still trading via their operators' own
  sites. Neither address could be read first-party — both sites are JavaScript
  SPAs that render nothing to a fetcher — so nothing was changed on either row.

---

## arts — 16 listings, 2 rows built

The thickest type in the group, so the bar was higher. Two public artworks that
are genuine destinations rather than street furniture:

- **Bunjil Geoglyph**, You Yangs Regional Park, Little River — see `cultural`
  above for why it is filed here. Parks Victoria publishes the coordinate.
- **Geelong Bollards**, Waterfront, Geelong — 100+ painted bollards by Jan
  Mitchell running Rippleside Park → Waterfront → Limeburners Point, with the
  council's own 30-minute self-guided Waterfront Bollards Trail. Pinned at
  Steampacket Gardens with the reason in `source_note`, because a linear trail
  has no single standing point.

**Public artwork considered and left out**, judged by whether someone would walk
to it: the Fat Ladies (Lorne), Geelong Camera Obscura (Highton), Cliff Young and
the Gum Boot (Beech Forest), the 2006 Commonwealth Games Fish (Apollo Bay), the
Arthur Streeton Memorial (Moriac), and roughly forty Geelong sculptures and war
memorials in the recovered OSM set. The first three are real destinations and I
wanted to write them — **no first-party source could be found for any of them**,
only hobbyist and tourism pages, so they are leads rather than rows.

---

## Corrections to existing rows — none of these can be done from `sync.py`

1. **`Event 7, Surf Coast Arts Trail, is corrupt.`** `starts_on: 2027-08-07`,
   `ends_on: 2026-10-12` — **the end date is ten months before the start date.**
   `recurrence: annual`, which never rolls forward. The real 2026 Trail ran
   **Saturday 1 – Sunday 2 August 2026, 10am–4pm, free**, per both
   surfcoastartstrail.com.au and the shire's own event page — so it is over, and
   no 2027 dates are published anywhere. Its `info_url` also points at
   surfcoastarts.com rather than the Trail's own surfcoastartstrail.com.au.
   Nothing was guessed. **This is the event this project's whole date rule is
   named after, and it is wrong in the database right now.**
2. **Events 30 and 51 are the same festival.** `ANGAIR Wildflower & Art Weekend`
   (30) and `Angair Wildflower & Arts Show` (51), both 2026-09-19. Id 30 has the
   better `info_url` (angair.org.au, first-party) but no `place_id` and no
   `ends_on`; id 51 has `place_id 80` and `ends_on 2026-09-20`. Merge onto the
   lower id the way the Torquay Farmers Market pair was, keeping 30's url, 51's
   place_id and 51's end date.
3. **Places 98 and 102 look like a duplicate** — `The HOOP Gallery` and
   `The HOOP Gallery - Torquay Multi-Arts Centre`, both Torquay. The new gallery
   listing links 98. Merging needs the three-step alias treatment.
4. **`Geelong Arts Centre` (a listing) carries `art gallery` and not `theatre`.**
   It is the region's principal performing arts centre, 50 Little Malop Street,
   and `theatre` had exactly one listing before this pass. Add `theatre`, first.
5. **`Lorne Theatre` carries `cinema` only.** Its own site's masthead reads "THE
   OLDEST & LARGEST LIVE VENUE ON THE SURFCOAST — MUSIC | THEATRE | FILM", and
   it is open 10am–9.30pm daily. Add `theatre`.
6. **`Geelong Gallery` is typed `museum`.** It is the region's public art
   gallery — OSM has it as `tourism=gallery` at 55 Little Malop Street. Add
   `art gallery`.

---

## Places rows needed (cannot be written from a script)

Every event added in this pass has a `place_id`. These are the venues that need
a `places` row before *their* events can be plotted, with the address to build
it from:

| venue | address | why |
|---|---|---|
| **Bellbrae Clay** | 590 Great Ocean Road, Bellbrae | `bellbraeclay.com/booknow` is a live first-party workshop list — **7 dated sessions and prices** confirmed 28 Aug 2026 (below). Activity 462 exists and carries its own coordinate; CLAUDE.md flags repointing it at a place row as Scott's call. Needs the `www.` |
| **Lorne Theatre** | 78 Mountjoy Parade, Lorne | its own site carries a dated live programme (DIESEL "By Request", **Fri 20 Nov 2026, 7pm**). `events_url` here is the durable move rather than hand-entering gigs |
| **Geelong Arts Centre** | 50 Little Malop Street, Geelong | the region's main programme. Place 31 is `The Playhouse`, a room *inside* it, not the centre |
| **The Potato Shed** | 41 Peninsula Drive, Drysdale | council-run, publishes its own season — 9 shows dated Aug–Oct 2026 were on the page |
| **Queenscliffe Historical Museum** | 49–55 Hesse Street, Queenscliff | monthly talks, next **25 Sep 2026, 10.30am–12pm**, "100 Years of Golf at Point Lonsdale" |
| **Shoestring Playhouse** | The MAC, 77 Beach Road, Torquay | Torquay Theatre Troupe's season. Note tickets are on **Humanitix**, so a Claude session cannot read the dates — the Action can |
| **Boom Gallery** | 41 Pakington Street, Geelong West | publishes its own exhibition opening dates |

**Bellbrae Clay's seven sessions, as printed 28 Aug 2026** — every weekday
checks out against the 2026 calendar. Not written, because they would be seven
unpinned events:

    Sat 12 Sep  Platters, Plates, Bowls   $120
    Sun 13 Sep  Mugs, Jugs, Vases         $120
    Tue 22 Sep  Kids Holiday Play          $85  (sold out)
    Thu 24 Sep  Mugs & Monsters            $85
    Tue 29 Sep  Family Fun                 $85
    Thu  1 Oct  Kids Holiday Play          $85
    Sun  4 Oct  Make Something Sunday     $120
    Fridays     Walk-In Fridays 2–6pm      $50

---

## What the 42-type vocabulary had no word for

- **A monument or landmark.** The **Great Ocean Road Memorial Arch** at Eastern
  View is one of the region's genuine stops and there is no honest type for it.
  It is not `arts` (it is a commemorative structure, not an artwork), not
  `cultural` (that means Wadawurrung Country here), not `museum`, not `walk`.
  The same gap swallows the Cliff Young statue at Beech Forest, the Split Point
  and Point Lonsdale lighthouses as objects rather than sites, and around forty
  war memorials in the OSM set. **Not forced into a type. This is the clearest
  vocabulary gap the pass found.**
- **An organiser that is not a room.** CLAUDE.md already records this for The
  Sound Doctor and Geelong Sustainability; this group adds **Surf Coast Arts**
  (surfcoastarts.com), **Growing Winchelsea**, and the **Torquay Theatre
  Troupe**, all of which programme real things in other people's buildings.
- **A festival that is a whole-region trail** rather than an event at a venue.
  The Surf Coast Arts Trail is 300 artists across 65 spaces in a dozen towns; it
  is currently `festival · arts` with `venue: "Various venues – Surf Coast"`,
  which is honest and unmappable.
- Minor: **`art gallery` vs `arts` held up well.** The one place it strained was
  Oxide Contemporary Arts, an art *school* with a gallery attached — written as
  `workshop · art gallery`, which reads correctly on both pages.

## Still open

- Costa Hall, Geelong — real theatre venue, no first-party address found
- Tin Liz Gallery — two sources, two towns, unresolved
- The eleven Surf Coast galleries logged above with no reachable first-party page
- Apollo Bay cinema — needs a person with a browser
- Whether Werribee is in scope for this project in practice, not just in `SUBURBS`
