# The music pass — 31 Aug 2026

Registry pass, not a listings pass. **No gigs were added. No rows were written
to Supabase at all** — this group's work is `places`, which no script can write,
so the whole output is three tables for `/admin` plus the faults found on the way.

Group as found: music 73 · festival 22 · comedy 4 · party 4 — 109 rows, 106 events.
Registry as found: **140 places — 32 with `events_url`, 38 website-only, 70 with
nothing**. Matches the 26 Aug survey exactly, so nothing moved in between.

**Found: 11 venues that already carry gigs and now have a readable feed;
26 new `places` rows worth creating; 11 OSM venues in neither table;
6 fixes to existing rows that need no new row at all.**

---

## Before the tables: four faults in the registry itself

These cost nothing to fix and each one is currently costing a feed.

### 1. `The Sound Doctor` is not marked as an organiser, and the code names it

`scrape_venues.py:404` has the fix built and documented:

```python
# Some listings name an organiser where the room should be — The Sewing
# Collective runs its nights somewhere different each time, exactly as The
# Sound Doctor does. ... mark one `kind = 'organiser'` in the venues table
# and it is never mistaken for a room again.
```

Four places carry `kind_legacy = 'organiser'`: Surf Coast Environment Group,
Bellarine Catchment Network, The Book Club Social, The Sewing Collective.
**The Sound Doctor (#32) is not one of them** — it is `kind = 'hall'`,
`kind_legacy = 'Live Music Venue'`, and it has a live Humanitix feed.

So every gig that feed imports is filed with the promoter as its room. The
proof is already in the data: four events sit on Anglesea Memorial Hall (#40)
and all four link to `thesounddoctor.info`. The Sound Doctor's own site says
"📍 Anglesea Memorial Hall" under every listing. It is a promoter with an
address (1B McMillan St) two doors from the hall it books (1A McMillan St).

**Fix: set `kind_legacy = 'organiser'` on #32.** One field.

### 2. Grand Hotel Portarlington has its gig page in the wrong column

Place #17 `website` = `https://www.portarlingtongrandhotel.com.au/whats-on/`
and `events_url` = null.

`have.py` therefore prints it as `site`, and `source_page()` takes the website
branch, which appends `GIG_PATHS` to a URL that is *already* the what's-on page —
`.../whats-on//events`, `.../whats-on//gigs` — and 404s every time before falling
back to the homepage-that-isn't-a-homepage. The page it needs is on the row.

I read it: "Join us every week Fridays to Sundays in the afternoon for live
music", plus dated acts (The Divinyls Story, 15 Aug 2026).

**Fix: move that URL to `events_url`; set `website` to
`https://www.portarlingtongrandhotel.com.au/`.** No new row.

### 3. A bare town name is sitting in an alias list

Place #49 Blackmans Brewery Torquay carries `aliases = ["Blackman's Brewery", "Torquay"]`.

`scrape_venues.py:557` builds `registry[venue_key(alias)] = id`, and
`ensure_venue()` checks `registry` **before** `worth_adding()`:

```python
if key and key in registry: return registry[key], None
name, why = worth_adding(g)          # the "just the suburb" guard is down here
```

So any scraped gig whose `venue_name` normalises to `torquay` is filed at
Blackmans Brewery Torquay, silently. `worth_adding()` has a guard for exactly
this (`"{name}" is just the suburb`) and it never gets reached.

**Fix: drop `"Torquay"` from #49's aliases.** Keep `"Blackman's Brewery"`.

### 4. Two duplicate place rows, one of them a room inside another place

| Keep | Merge away | Why |
|---|---|---|
| #128 Geelong Library and Heritage Centre (The Dome) | #143 `Wurdi Youang,  Level 5, Geelong Library & Heritage Centre` | A room on level 5 of #128. #128 already has a feed; #143 has nothing and holds one event. Merge as an alias. Note the double space in the name. |
| #88 Barwon Bluff (Bluff Road Carpark) | #144 `Barwon Bluff, Barwon Heads (Bluff Road Carpark)` | Same carpark, written twice. Not music, but it is in the way. |

Also **#31 `The Playhouse` (Geelong, theatre, nothing on file) is a room inside
Geelong Arts Centre** — GAC spells it "The Play House", 764 seats, alongside
The Story House (550), The Open House (240) and four studios. It should become
an alias on the Geelong Arts Centre row in HALF TWO, not survive as a venue.

---

## HALF ONE — venues already carrying gigs that nothing reads

24 places hold a music-group event and have no `events_url`. Twelve of those are
a park, a reserve, a street, a school or a beach holding one annual festival —
those are listed at the bottom and are not feed candidates. These are the rooms.

### Apply through /admin

| Name | Suburb | Address | Website | events_url | Platform |
|---|---|---|---|---|---|
| Barwon Club Hotel *(#3, update)* | South Geelong | 509 Moorabool St, South Geelong VIC 3220 | `https://www.barwonclub.com.au/` | `https://barwonclub.oztix.com.au/` | **Oztix** |
| The Sands Torquay *(#95, update)* | Torquay | 2 Sands Boulevard, Torquay VIC 3228 | `https://www.thesandstorquay.com` | `https://www.thesandstorquay.com/whats-on` | own site |
| Oneday Estate *(#24, update)* | Curlewis | 45 Curlewis Rd, Curlewis VIC 3222 | `https://onedayestate.com.au` | `https://onedayestate.com.au/visit-us/events/` | Humanitix (links out) |
| Elephant & Castle Hotel *(#12, update)* | Geelong | 158 McKillop St, Geelong VIC 3220 | `https://elephantandcastle.com.au` | `https://elephantandcastle.com.au/events/` | own site (NowBookIt) |
| Aireys Pub *(#1, update)* | Aireys Inlet | 45 Great Ocean Rd, Aireys Inlet VIC 3231 | `https://www.aireyspub.com.au` | `https://www.aireyspub.com.au/events` | own site, free gigs |
| Mt Duneed Estate *(#23, update)* | Waurn Ponds | 65 Pettavel Rd, Waurn Ponds VIC 3216 | `https://mtduneedestate.com.au/` | `https://mtduneedestate.com.au/whats-on` | own site |
| Grand Hotel Portarlington *(#17, fix)* | Portarlington | 76 Newcombe St, Portarlington VIC 3223 | `https://www.portarlingtongrandhotel.com.au/` | `https://www.portarlingtongrandhotel.com.au/whats-on/` | own site |

**One line each, and why it is worth watching:**

- **Barwon Club Hotel** — the biggest single win in the pass. Eleven gigs in the
  database, every one of them ticketed on Oztix, and the outlet page
  `barwonclub.oztix.com.au` carries about twenty shows out to Feb 2027. Read and
  confirmed: Dear Seattle 4 Sep, The Coolabahs 6 Sep, META4 11 Sep, The Darts
  12 Sep, DRENCHER FESTIVAL 19 Sep. This is a proper Geelong bandroom running
  weekly. **Register the Oztix outlet page, not `barwonclub.com.au/gig-guide/`** —
  that path appeared in search results with a matching title but its host serves a
  redirect-looping robots.txt, so it could not be fetched and should not be pinned.
  The Oztix page fetched clean and `from_oztix()` already knows how to read it.
- **The Sands Torquay** — three events on file and *nothing* in the registry, not
  even a website. Its own `/whats-on` carries the dated shows (Piano Bar 29 Aug,
  Comedy Night with Dave O'Neil 11 Sep) *and* a standing "Family Friendly Live
  Music Sessions" every Sat 5–8pm and Sun 4–7pm. A resort that programmes music
  weekly and was invisible to the registry.
- **Oneday Estate** — three gigs, all ticketing on Humanitix. `/visit-us/events/`
  is the winery's own index and links out to them, so the scraper's Humanitix
  regex fires on links found there without us ever fetching humanitix ourselves.
  A sibling `/visit-us/sunday-sessions/` page also exists.
- **Elephant & Castle** — bands most weekends (Rat Pack 29 Aug, Regular Boys
  30 Aug, Midnight Oil & Cold Chisel tributes 10 Oct). Website was on file, gig
  page was not.
- **Aireys Pub** — gigs are on its own `/events`, not only on Facebook as the
  single DB event's link suggested. Free entry, no ticketing, so this one only
  ever surfaces if the venue page is read.
- **Mt Duneed Estate** — came in through HALF THREE (OSM's "Ceremony Pit") and
  belongs here: an existing place row with nothing on file at all, and a
  `/whats-on` carrying a **Concerts** category with Boyz II Men on it. This is
  the estate that puts large outdoor shows on. Caveat below.
- **Grand Hotel Portarlington** — see fault 2. Live music Fri–Sun every week.

### Rooms that carry gigs but should NOT get an `events_url`

| Venue | Why not |
|---|---|
| **Anglesea Memorial Hall** (#40) | Surf Coast Shire hire-only room, 1A McMillan St. No council programme; bookings via `envibe.surfcoast.vic.gov.au`. Its four gigs are The Sound Doctor's. The feed belongs to the promoter — see fault 1. |
| **Mantra Lorne** (#65) | Hire room. Its two tribute concerts are promoter-run on TryBooking. The resort's own site sells weddings and conferences. `mantralorne.com.au/events/` surfaced in search titled "Local Lorne Events" — a town guide, not its programme; not fetched, not recommended. Promoter unidentified; `dreamsshow.com.au` was checked and positively ruled out (13 dates, all QLD/NSW, no Lorne). |
| **Globe Theatre** (#57) | Surf Coast Shire hire-only. Council page offers it for "parties, meetings, fitness classes, concerts and conferences". No programme published, no own website. |
| **Barwon Heads Hall** (#107) | Hire-only, 79 Hitchcock Ave. Council directory lists activity *types* (monthly market, film nights) with no calendar. Each hirer tickets separately. |
| **Nyaal Banyul Geelong Convention and Event Centre** (#142) | MCEC-operated and entirely B2B — `nyaalbanyul.com.au` is venue-hire sales pages with no public what's-on. Its events will only ever arrive through whoever promotes each show. |
| **4 Pines X Boardriders Torquay** (#96) | Its own venue page lists Taco Trivia, Parma & Pint and happy hour — **no live music**. The group's `/events` index has no per-venue filter, so pinning it would attribute every 4 Pines venue's events to Torquay. Leave null. |

### Not feed candidates — one annual festival at a public space

Lorne Foreshore · Aireys Inlet Primary School · WG Little Reserve · Ocean Grove
Park · Australian National Surfing Museum · Deans Marsh Memorial Reserve ·
Pakington Street · Jan Juc SLSC · Lions Park Winchelsea · Anglesea SLSC ·
Princess Park Queenscliff · Wurdi Youang (merge, fault 4).

The festival owns the page, not the park. Pako Festa, the Mussel Festival, One
Planet, Deans Marsh Festival, Queenscliff Music Festival and the Anglesea Music
Festival each publish their own site; the reserve underneath publishes nothing.
Twelve rows, correctly empty. Logged so the next pass does not re-walk them.

---

## HALF TWO — the 57 listings that can never hold an event

Confirmed the number exactly: 86 activities carry `pub`, `bar`, `brewery`,
`winery`, `theatre` or `music`; 84 have `place_id` null; 27 of those match an
existing `places` row by name or alias; **57 have no place row at all.**

### New `places` rows to create

| Name | Suburb | Address | Website | events_url | kind |
|---|---|---|---|---|---|
| Lorne Theatre | Lorne | 78 Mountjoy Parade, Lorne VIC 3232 | `https://lornetheatre.com.au/` | `https://lornetheatre.ourgoldenage.com.au/live-music` | theatre |
| ↳ *also set* `ticketing_url` | — | — | — | `https://lornetheatre.oztix.com.au/` | — |
| Geelong Arts Centre | Geelong | 50 Little Malop St, Geelong VIC 3220 | `https://geelongartscentre.org.au/` | `https://geelongartscentre.org.au/whats-on/` | theatre |
| Bellarine Arts Centre | Drysdale | 41 Peninsula Dr, Drysdale VIC 3222 | `https://app.geelongcity.vic.gov.au/bellarineartscentre/default.aspx` | `https://app.geelongcity.vic.gov.au/bellarineartscentre/events/default.aspx` | theatre |
| The Esplanade Hotel Queenscliff | Queenscliff | 2 Gellibrand St, Queenscliff VIC 3225 | `https://esplanadequeenscliff.com.au/` | `https://esplanadequeenscliff.com.au/events/live-music/` | pub |
| Mount Moriac Hotel | Moriac | 1115 Princes Hwy, Mount Moriac VIC 3240 | `https://www.mountmoriachotel.com.au/` | `https://www.mountmoriachotel.com.au/experience-the-best-of-local-talent-at-mount-moriac-pub/` | pub |
| Royal Mail Hotel | Birregurra | 49 Main St, Birregurra VIC 3242 | `https://www.theroyalmailbirregurra.com.au/` | `https://www.theroyalmailbirregurra.com.au/live-music` | pub |
| St Leonards Hotel by the Sea | St Leonards | 496 The Esplanade, St Leonards VIC 3223 | `https://stleonardsbythesea.com.au/` | `https://stleonardsbythesea.com.au/events/` | pub |
| Ocean Grove Hotel | Ocean Grove | 175 Bonnyvale Rd, Ocean Grove VIC 3226 | `https://oceangrovehotel.com.au/` | `https://oceangrovehotel.com.au/whats-on/` | pub |
| Lara Hotel | Lara | 10 Hicks St, Lara VIC 3212 | `https://www.larahotel.com.au/` | `https://www.larahotel.com.au/events--specials.html` | pub |
| Bennetts on Bellarine | Bellarine | 2171 Portarlington Rd, Bellarine VIC 3223 | `https://www.bennettsonbellarine.com/` | `https://www.bennettsonbellarine.com/whats-on-1` | winery |
| Leura Park Estate | Curlewis | Curlewis VIC 3222 *(street number not confirmed on their own site)* | `https://leuraparkestate.com.au/` | `https://leuraparkestate.com.au/blogs/news/sunday-live-music-line-up` | winery |
| Alt Rd Wines | Winchelsea | 880 Winchelsea-Deans Marsh Rd | `https://altroad.com.au` | `https://altroad.com.au/whats-on/` | winery |
| Shoestring Playhouse | Torquay | The MAC, 77 Beach Rd, Torquay VIC 3228 | `https://www.ttt.org.au` | `https://www.ttt.org.au/whats-on` | theatre |
| The Blues Train | Queenscliff | departs Queenscliff Railway Station, 20 Symonds St, Queenscliff VIC 3225 | `https://www.thebluestrain.com.au/` | `https://www.thebluestrain.com.au/` | *(see room-vs-organiser)* |
| The Covenant Wine Bar | Ocean Grove | 2/62 The Terrace, Ocean Grove VIC 3226 | `https://thecovenantwinebar.com.au` | null *(see note)* | bar |
| Great Ocean Road Brewing Taphouse | Torquay | 27 Baines Cres, Torquay VIC 3228 | `https://greatoceanroadbrewing.com.au/taphouse/` | null | brewery |
| Das Bierhaus | Geelong | 310 Moorabool St, Geelong VIC 3220 | `https://dasbierhaus.com.au/` | null | bar |
| Noble Rot Wine Store & Bar | Point Lonsdale | 51 Point Lonsdale Rd, Point Lonsdale VIC 3225 | `https://noblerotwine.com.au/` | null | bar |
| Morgans Bar & Grill | Anglesea | 87 Great Ocean Rd, Anglesea VIC 3230 | null | null | bar |
| Love House | Anglesea | Anglesea SLSC, 100 Great Ocean Rd, Anglesea VIC 3230 *(their own site says 3228 — Anglesea is 3230; unresolved)* | `https://www.lovehousedining.com.au` | null | bar |
| The Palais Geelong | Geelong | 297 Moorabool St, Geelong VIC 3220 | `https://www.palaisgeelong.com/` | null | theatre |
| Costa Hall | Geelong | 1 Gheringhap St, Geelong VIC 3220 | `https://geelongartscentre.org.au/venue-hire/costa-hall/` | **null — do not copy GAC's** | hall |
| Deans Marsh Community Hall | Deans Marsh | 10 Pennyroyal Valley Rd, Deans Marsh VIC 3235 | `https://www.surfcoast.vic.gov.au/Experience/Venues-for-Hire/Deans-Marsh-Community-Hall` | null | hall |
| Yellow Gums Performance Space | Jan Juc | Bob Pettitt Reserve, 89–91 Sunset Strip, Jan Juc VIC 3228 | `https://www.surfcoast.vic.gov.au/Experience/Parks-and-reserves-listing/Bob-Pettitt-Reserve` | null | hall |
| Great Ocean Road Brewing (brewery taproom) | South Geelong | 112 Balliang St, South Geelong VIC 3220 | `https://www.greatoceanroadbrewing.com.au` | null | brewery |
| Valhalla Brewing | Geelong | 12–14 Union St, Geelong *(from press, not their own site)* | null | null | brewery |

**One line each, and why it is worth watching:**

- **Lorne Theatre** — the standing example, and it checks out, but not where the
  prompt says. The masthead **"THE OLDEST & LARGEST LIVE VENUE ON THE SURFCOAST —
  MUSIC | THEATRE | FILM"** is on **`lornetheatre.com.au`**, which is a different
  site from `lornetheatre.ourgoldenage.com.au` (the cinema operator Our Golden
  Age's booking front, which is what the listing has on file and which does *not*
  carry that line). Both are live. Address 78 Mountjoy Parade. It is a cinema that
  also programmes live music, which is why it types `["cinema","theatre"]` and still
  belongs here.
  **Correction made on verification:** I first proposed `lornetheatre.oztix.com.au`
  as the `events_url`. It **302s to `/event/d45aa609-…`, a single show** (Diesel,
  20 Nov 2026), because that is the only one on sale — and a single-event link is
  the one thing this pass is not allowed to register. So the `events_url` is the
  venue's own `/live-music` page and the Oztix subdomain goes in **`ticketing_url`**,
  which is exactly the shape #4 Barwon Heads Hotel and #37 Torquay Hotel already use.
  It will list properly once a second show is on sale; until then it must not be pinned.
- **Geelong Arts Centre** — the largest room in the region with a dated public
  programme, and it had no place row at all. Absorbs #31 The Playhouse as an alias.
- **Bellarine Arts Centre** — **the Potato Shed was renamed in Feb 2026** and
  `geelongaustralia.com.au/potatoshed/` now 302s to the new council site. Twelve
  dated shows to Dec 2026 including two straight music ones (Neil Diamond Tribute
  13 Oct, The Chuck Berry Story 10 Nov). The listing's URL is stale.
- **The Esplanade Hotel Queenscliff** — a dedicated `/events/live-music/` page:
  acoustic Fri 7–9pm, local bands Sat from 8pm, acoustic Sun 2–5pm in the beer
  garden. Three nights a week, published, in a town we already cover heavily.
- **Mount Moriac Hotel** — bills itself "Geelong's Destination for Live Music on
  Sunday Afternoons & Friday Evenings" with a named-artist gig list. Read directly.
  Suburb note: `Mount Moriac` is not in `SUBURBS`; **`Moriac` is** — use that.
- **Royal Mail Birregurra / St Leonards / Ocean Grove / Lara** — four pubs with
  their own dated rosters. Lara's events page read stale (February dates on an
  August read), so it may need watching rather than trusting.
- **Bennetts on Bellarine** — named acts nearly every Sat 2–5pm and Sun 1–4pm,
  plus Nicky Bomba. The clearest winery YES in the set.
- **Leura Park Estate** — "18 years of live music at Leura", weekly Sunday session
  with a published line-up. The `events_url` given is a blog post, which is the
  best thing that exists; worth re-checking that it is the permanent home.
- **Alt Rd Wines** — "Live music every Saturday evening throughout the summer
  months". Seasonal, so it will read empty half the year, which is honest.
- **Shoestring Playhouse** — a blackbox room inside The MAC, Torquay; Torquay
  Theatre Troupe programmes it and tickets on Humanitix (`/jumbuck-hotel` seen in
  the page text; **recorded, not fetched**).
- **Great Ocean Road Brewing Taphouse** — YES rests on press (Surf Coast Times:
  "live music on Saturdays"; Visit Great Ocean Road lists Live Music as a
  facility), not on a venue page. Enter it, but the null `events_url` is honest.
- **The Covenant Wine Bar** — "Sunday from 3pm - live music from 3.30pm" is on
  its homepage and the residency is real, but `/what-s-happening` turned out on
  verification to be an **unpopulated skeleton** — an "Upcoming Events" heading
  with nothing under it. Row yes, feed no. (Its own site also splits `www` and
  bare-domain; pick one.)
- **Das Bierhaus / Noble Rot / Morgans / Love House** — all four do music, none
  publishes a listing. Das Bierhaus has a "Live-Music-Geelong" banner and no
  calendar; Noble Rot's evidence is the owner quoted in Forte; Morgans is a Visit
  Great Ocean Road facility line with no site at all; Love House's is on the
  Anglesea SLSC site, not its own. Rows worth having, feeds that do not exist.
- **Costa Hall** — 1,421 seats, Deakin-owned, Geelong Arts Centre-operated,
  ten minutes' walk from the GAC building. Its programme publishes through GAC's
  what's-on. **Do not put GAC's `events_url` on it** — see the shared-pin warning.
- **Deans Marsh Community Hall / Yellow Gums** — real rooms, no programmes.
  Deans Marsh's pavilion was opened by Goanna and has a raised stage; Yellow Gums
  is a council outdoor stage at Bob Pettitt Reserve programmed by Jan Juc Live.
- **The Palais Geelong** — UNCLEAR and entered on that basis: its own site shows
  a "Recent Shows" gallery and a poll asking patrons what they want back. No
  dated programme. Real room, uncertain present tense.
- **Valhalla Brewing** — the weakest row here. Forte says "acoustic sessions on
  Friday nights and Sunday afternoons"; a Whatslively profile says "No upcoming
  gigs"; its own domain serves a bare directory index. Enter it or leave it — I
  would not call it a hard YES.

### Already in `places` under a different spelling — alias, not a new row

| Listing | Existing place | Action |
|---|---|---|
| `Saints & Sailors` | **#29 Saints and Sailors**, Portarlington | add alias `Saints & Sailors`, set the listing's `place_id` |
| `Flying Brick Cider House` | **#14 Flying Brick Cider Co**, Wallington | add alias `Flying Brick Cider House` |
| `Bomboras Beach Bar` *(OSM)* | **#10 Bomboras**, Torquay | add alias `Bomboras Beach Bar` |
| `Portarlington Pub` / `Portarlington Grand Hotel` *(OSM)* | **#17 Grand Hotel Portarlington** | add both aliases; see fault 2 for the URL fix |
| `The Playhouse` **(#31, a place row)** | room inside **Geelong Arts Centre** | fold into the new GAC row as alias `The Play House` |
| `Ceremony Pit` *(OSM)* | **#23 Mt Duneed Estate** | not a venue — the estate's outdoor concert space. No source anywhere trades under that name. |

All four alias cases slipped a two-distinctive-word matcher: `&` vs `and`,
`Co` vs `House`, and a suffix. That is the same near-miss family that produced
`Common Ground Project` twice, one field along, and it is exactly how
`scrape_venues.py` would recreate them on the next run.

Separately, **27 listings match an existing `places` row by name and still have
`place_id` null** — Aireys Pub, Torquay Hotel, Barwon Heads Hotel, Lorne Hotel,
Barwon Club, Bird Rock, Bomboras, Cuda Bar, the 18th Amendment, Piano Bar,
Workers Club, Lambys, Little Creatures, Bells Beach Brewing, Provenance, Oneday,
Bellarine Estate, Bellbrae Estate, Mt Duneed, Blackmans ×2, Grand Hotel
Portarlington, Elephant & Castle, Last One Inn, Great Ocean Road Brewhouse,
Apollo Bay Hotel, The Whiskery. The row exists; only the link is missing. That is
a bulk `place_id` update, not research, and it is the cheapest map coverage
available in the whole database.

### Checked and rejected — a room, but not a music room

Baie Wines · Brown Magpie (cellar door "closed until further notice", newest
post Nov 2021) · McGlashan's Wallington Estate · Jack Rabbit Vineyard ·
Scotchmans Hill · Oakdene Vineyards · Basils Farm · Wolseley Wines *(is at
**Paraparap**, not Bellbrae)* · Austin's *(is at **Sutherlands Creek**, not
Bannockburn)* · Clyde Park Vineyard · Mt Pleasant Rd Brewers *(trivia and happy
hour only)* · Prickly Moses / Otway Estate · White Rabbit Barrel Hall *(Little
Creatures' Geelong events page is trivia, parmi night and run club)* · Wye Beach
Hotel · Inverleigh Hotel *(is at **1 High St**, not East Street)* · Klein's
Anglesea Hotel *(its "Events" nav is an `#events` anchor holding an embedded
Facebook feed; no music text on its own pages)* · Geelong Cellar Door ·
Union Cellars *(was Union Street Wine — **rebranded and moved to 15 Minerva Rd,
Herne Hill**; old domain redirects)* · Bakery Bar & Lounge · Bob Sugar *(DJ
Fridays, not live music)* · Ipsos · **Pop Cultcha — not a venue at all**, it is a
pop-culture retail store typed `music` in the listings, and that type is wrong.

Four could not be judged and are **UNCLEAR, not NO**: Dinny Goonan (JS-only
render, `/about/` 403), Banks Road Vineyard (its own nav links to an `/events/`
that 404s), Forrest Brewing (site says closed for winter, reopens 25 Sep),
Terindah Estate (boilerplate claims live music, lists none). The Barwon Hotel
Winchelsea also stayed UNCLEAR — its host serves a broken robots.txt on every
path and could not be read in four attempts; two weak third-party mentions of
live music exist. Worth a human look.

**`Piping Hot Chicken Shop` looks closed.** It was a genuine original-music room
(Dave Graney, Jeff Lang played there per Songkick, 18 past concerts) but its
domain no longer resolves, Songkick shows zero upcoming and nothing since Apr
2024, and closure posts exist. The listing needs a closed flag or deletion, not
a place row.

**`Pub Trivia Night – Surf Coast` is not a venue and its URL is banned.** Its
`location` is "Several Surf Coast pubs" and its `url` is
`https://www.google.com/maps/search/The+Sands...` — one of the 37 Google Maps
placeholders RESEARCH_RULES says are waiting to be cleared. Flagging, not fixing.

---

## HALF THREE — venues in neither table

`nearby.py --refresh` **failed**: all three Overpass endpoints refused this
address (`Connection reset by peer`, then `403` on both mirrors), which is the
signature the script itself documents. It did not matter — `scripts/osm_cache.json`
is committed and was fetched **31 Aug 2026 12:50**, 2,796 POIs, hours before this
pass. Every town lookup reads the cache, so the net was current. **Do not re-run
`--refresh` to "fix" this.**

Of 155 named pub/bar/brewery/winery/theatre POIs in the cache, 127 have no place
row. Filtering by town first, as instructed: everything at **Werribee, Altona,
Laverton, Tarneit and Hoppers Crossing** is out (direction, not distance — the
bbox reaches them, the region does not); everything the Queenscliff centroid
catches at 10–19 km is across the bay at **Sorrento, Rye and Portsea**, which is
Mornington Peninsula and explicitly out of scope; **Lismore** (47 km) and
**Rokewood** are out. **Meredith** and its Supernatural Amphitheatre sit 30 km
north of Inverleigh, inland toward Ballarat — that is the direction the region
rules exclude, so I have left it out rather than quietly including a famous name.
Flagging it as a judgment call for you rather than deciding it.

### New `places` rows to create

| Name | Suburb | Address | Website | events_url | kind |
|---|---|---|---|---|---|
| The Sphinx Hotel | Geelong *(North Geelong)* | 2 Thompson Rd, North Geelong VIC 3215 | `https://www.sphinxhotel.com.au/` | `https://www.sphinxhotel.com.au/entertainment` | pub |
| Beav's Bar | Geelong | 77–79 Little Malop St, Geelong VIC 3220 | `https://www.beavsbar.com.au/` | `https://www.beavsbar.com.au/whats-on` | bar |
| The Telegraph Hotel | Geelong West | 2 Pakington St, Geelong West VIC 3218 | `https://thetelegraphhotel.com.au/` | null *(see note)* | pub |
| The Grovedale Hotel | Grovedale | 236–258 Torquay Rd, Grovedale VIC 3216 | `https://grovedalehotel.com.au/` | `https://grovedalehotel.com.au/events/` | pub |
| Queen of the West | Geelong West | 126 Pakington St, Geelong West VIC 3218 | `https://queenofthewestgeelong.com.au/` | `https://queenofthewestgeelong.com.au/whats-on/` | pub |
| Belmont Hotel | Belmont | 77 High St, Belmont VIC 3216 | `https://www.belmonthotelgeelong.com.au/` | `https://www.belmonthotelgeelong.com.au/whats-on` | pub |
| The Union Hotel Colac | Colac | 110 Murray St, Colac VIC 3250 | `https://unioncolac.com.au/` | `https://unioncolac.com.au/whats-on/` | pub |
| The Deck Geelong | Geelong | 2–4 Gheringhap St, Geelong VIC 3220 | `https://thedeckgeelong.com.au/` | `https://thedeckgeelong.com.au/whats-on/` | pub |
| Gellibrand River Hotel | Forrest *(is at Gellibrand)* | 20 Old Main Rd, Gellibrand VIC 3239 *(directory, not own site)* | `https://www.gellibrandriverhotel.com.au/` | `https://www.gellibrandriverhotel.com.au/whats-on-1` | pub |
| Fyansford Hotel | Fyansford | 67 Hyland St, Fyansford VIC 3218 | `https://www.thefyansfordhotel.com.au/` | null | pub |

**One line each, and why it is worth watching:**

- **The Sphinx Hotel** — the biggest miss in the whole registry. A dedicated
  showroom (The Luxor) with tribute shows, bands, recording artists and comedy,
  ticketing across **Oztix, Moshtix, Eventbrite and Leap Events**, plus a monthly
  Morning Melodies. Read directly: Isaac Butterfield 3 Sep, Alright Hey 5 Sep. It
  is not in `places`, not in `activities`, and not in any event we hold.
- **Beav's Bar** — the other one. Site titled "Beav's Bar - Live Music -
  Functions - Geelong", and `/whats-on` carries named acts with set times, five
  nights of the week (Michael Hardiman 9.30pm Sat, Luke Biscan 6pm Sun, and so on).
  Read directly. It runs more gigs per week than anything already in the registry.
- **Grovedale / Queen of the West / Belmont** — three Geelong suburban pubs with
  a published weekend gig page. Grovedale: "live music in our rustic laneway-style
  garden bar every Friday and Saturday". Queen of the West states Live Music for
  Fri and Sat and links *through* to a separate Gig Guide — pin `/whats-on/` for
  now, but the Gig Guide itself is the better target if you can find its URL.
  Belmont: "live music and DJs playing in the bar every weekend... until 1am".
- **Telegraph Hotel** — real live-music pub, **but `/live-fridays/` is not a gig
  page.** On verification it holds a single announcement (Cam Henderson and Steve
  Kucina, "Friday 18th August" — a date that is not a Friday in 2026), with no
  recurring schedule and no calendar. Create the row, leave `events_url` null. This
  was in my first draft as a feed and it should not have been.
- **Union Hotel Colac** — "Live entertainment every Saturday" with named acts.
  Colac is in the suburb vocabulary and has almost nothing in the database.
- **The Deck** — real live music, but its `/whats-on` pushes you to Facebook for
  the listings, so the pinned page will read thin. Enter it and expect little.
- **Gellibrand River Hotel** — carries a "Gellibrand River Blues" page of its own
  and a separate blues-and-blueberry festival site. The one genuine Otways find.
  Caveat from verification: `/whats-on-1` is a real page whose only current content
  is a **festival cancellation notice**, so the feed will import nothing until they
  post again. Pin it anyway — it is the right page — but do not expect rows.
  **`Gellibrand` is not in `SUBURBS`** — nearest recognised is Forrest (or Beech
  Forest); per the rules I am saying so rather than letting a road name land it.
- **Fyansford Hotel** — UNCLEAR. It runs Morning Melodies, which is daytime
  cabaret rather than band gigs, and has no gig page. Row worth having, feed no.

### Checked, no evidence of live music — do not re-walk these

Sawyers Arms Tavern (Newtown) · The Cremorne Hotel (Newtown) · Great Western
Hotel (Newtown) · Sir Charles Darling Hotel · Petrel Hotel · Jokers On Ryrie
("Live and Loud on the big screen" is sport) · Malt Shovel Taphouse (age-gated,
nothing found) · Austral Hotel Colac · **The Beach Hotel Jan Juc**, 3–9 Stuart
Ave — our own town's pub, and its site is Tab & Fox Sports, happy hour, steak
night and parma night; setlist.fm has three gigs there in **2004** under the old
name Bells Beach Hotel and nothing since, so it is a NO with a footnote ·
**Movida Lorne** — appears closed, was on the ground floor of the Lorne Hotel;
treat the OSM point as stale · **CentreStage** — OSM tags it `theatre` but it is a
theatre/education/talent company at 22 Princess Hwy, Norlane that stages its
musicals *at Geelong Arts Centre*. Not a venue. The OSM tag is wrong.

---

## The gap: rooms whose organiser is a different thing

The prompt asked for these specifically. Eight, and they are not all the same shape.

1. **Anglesea Memorial Hall / The Sound Doctor** — promoter books a council hall.
   The schema *does* have an answer (`kind_legacy = 'organiser'`) and it is simply
   not applied. Fault 1.
2. **The Blues Train / Bellarine Railway / Queenscliff Railway Station** — the
   sharpest case in the set and the one with no answer. The **room is four
   carriages of a moving train**; the audience rotates through them to see four
   acts. The **programmer** is The Blues Train (est. 1994, office Shop 3, 45 Hesse
   St). The **rail operator** is a third party, Bellarine Railway — which we
   already hold as place #141 Queenscliff Railway Station, aliased "Bellarine
   Railway Queenscliff". The pin is the departure point, 20 Symonds St; the venue
   is not at the pin for most of the evening. A `place_id` can express "where you
   turn up" and cannot express "what you are in". Note also its `/shows/` page
   still lists **2024** dates while the homepage lists Oct–Nov 2026 — pin the
   homepage, not `/shows/`.
3. **Costa Hall / Deakin University / Geelong Arts Centre** — owner, operator and
   programmer are three parties, and the room is not inside the operator's
   building. It needs its own row and GAC's programme; the schema can hold one or
   the other, not both.
4. **Shoestring Playhouse / Torquay Theatre Troupe / The MAC** — a room inside a
   building, programmed by a company, all three with names in use.
5. **Anglesea Performing Arts** — a **company, not a room**. Thirty-plus years,
   performs in Anglesea Memorial Hall. Its site `angleseaperformers.org.au` does
   not resolve. It should never become a `places` row; if anything it is a second
   organiser at the same hall as The Sound Doctor.
6. **Yellow Gums Performance Space / Jan Juc Live** — council stage, community
   programmer, no published calendar from either.
7. **Deans Marsh Community Hall / Deans Marsh Festival** — hire room whose music
   is one annual festival run by a separate committee.
8. **The Sewing Collective (#85) / 70D The Terrace (#100)** — already in the data
   and already half-handled: the Collective is marked `organiser`, 70D is the room,
   and they **share a `website`**, which trips `__shared_site` and makes the room
   unreadable. The existing pattern, showing its own limit.

The shape of the gap: `places` has one row per thing and one `events_url` per row,
so a room can point at exactly one programme. Where the programme belongs to
someone else, we can either file the gigs under the promoter (wrong pin, right
feed) or under the room (right pin, no feed). `kind_legacy = 'organiser'` picks
the second and accepts the loss. Nothing in the schema says *"this promoter's
events happen in that room"* — which for Anglesea Memorial Hall is a fixed,
knowable fact that we are currently throwing away four times a year.

---

## Two traps for whoever applies these

**Never give two places the same `events_url`.** `scrape_venues.py:537` sets
`__shared_pin` when a URL appears on more than one row, and `source_page()` then
returns *nothing for either of them* — silently, with only a back-of-house note.
Right now only the 18 library branches trip it. Three of this pass's findings
would trip it if applied carelessly:

- **Blackmans Brewery Geelong** — its events page is site-wide
  (`blackmansbrewery.com.au/venue-news-and-events/`, one page for both venues) and
  its Humanitix host feed is shared with Torquay. Torquay (#49) already has that
  feed. **Putting it on Geelong (#92) as well kills both.** Leave #92 null, or
  give it only the website.
- **Costa Hall** — do not copy Geelong Arts Centre's `/whats-on/` onto it.
- **Great Ocean Road Brewing** — South Geelong and the Torquay Taphouse share
  `greatoceanroadbrewing.com.au`, which trips `__shared_site` instead. Give the
  Taphouse `…/taphouse/` as its website so the two rows differ.

**Three "Great Ocean Road" venues, two companies.** Do not merge them.
*Great Ocean Road Brewing* runs the **South Geelong** taproom (112 Balliang St,
Fridays only) and the **Torquay Taphouse** (27 Baines Cres) — two different rooms,
one company. **Great Ocean Road Brewhouse**, Apollo Bay (#18, already in `places`)
is a **different company** on a different domain, owned by Otway Brewing Group
(the Prickly Moses people). Its correct site is `greatoceanroadbrewhouse.com.au`,
which is what #18 already holds — do not let it inherit the Brewing domain. The
Brewhouse's own `/whats-on/` does list live music, so #18 is also a HALF ONE
candidate: **`https://www.greatoceanroadbrewhouse.com.au/whats-on/`**.

---

## Data corrections found along the way

| Row | On file | Should be |
|---|---|---|
| Lara Hotel *(listing)* | `thelarahotel.com.au` — does not resolve | `https://www.larahotel.com.au/` |
| St Leonards Hotel *(listing)* | 1381 Murradoc Road | 496 The Esplanade, St Leonards |
| Inverleigh Hotel *(listing)* | East Street (Hamilton Highway) | 1 High Street, Inverleigh |
| The Potato Shed *(listing)* | `geelongaustralia.com.au/potatoshed/` | renamed **Bellarine Arts Centre**, new council URL |
| Union Street Wine *(listing)* | 6 Union Street, Geelong | **Union Cellars**, 15 Minerva Rd, Herne Hill |
| Wolseley Wines *(listing)* | Bellbrae | Paraparap |
| Austin's Wines | Bannockburn | Sutherlands Creek |
| Barwon Club Hotel *(place #3)* | suburb "Geelong" | South Geelong (Oztix and the listing agree) |
| Hop City *(listing)* | 122 Moorabool St | EatClub says 64 Little Malop St — **conflict, not resolved** |
| The Little River Hotel *(listing)* | River Street | third-party says 10–14 Flinders St — **not confirmed from a first-party source** |
| Piping Hot Chicken Shop *(listing)* | active | appears **closed** since ~Apr 2024 |
| Pub Trivia Night – Surf Coast *(listing)* | a `google.com/maps/search/…` url | banned placeholder; should be null |

**Suburbs used above that `SUBURBS` does not recognise**, flagged per the rules
rather than relied on: `Mount Moriac` (use **Moriac**), `North Geelong` and
`Newtown` (use **Geelong** — neither is in the `GEELONG` set either), `Gellibrand`
(use **Forrest**), `Herne Hill`, `Marcus Hill`, `Bambra`, `Paraparap`, `Modewarre`,
`Swan Bay`. None of these should be leaned on to land a listing by accident.

---

## Verification pass

Every URL in the three proposal tables was re-fetched independently after the
tables were written — 72 URLs, no host dead. Three came back wrong and are
corrected above rather than left standing:

| URL | Was proposed as | Actually |
|---|---|---|
| `lornetheatre.oztix.com.au` | Lorne Theatre `events_url` | 302s to a **single event page** — moved to `ticketing_url` |
| `thetelegraphhotel.com.au/live-fridays/` | Telegraph Hotel `events_url` | one stale gig announcement, no calendar — now null |
| `thecovenantwinebar.com.au/what-s-happening` | Covenant `events_url` | empty "Upcoming Events" skeleton — now null |

Two of those three were single-event or non-listing pages, which is the exact
rule this pass was told twice not to break. They only surfaced because the
tables were checked against the live web a second time, which is worth doing
again on whatever the next pass produces.

**Feeds that are real but will read stale or empty**, so nobody is surprised
when the scraper reports nothing: Aireys Pub (Jul/Aug dates), Lara Hotel (Feb
dates on an Aug read), Royal Mail Birregurra (Jun/Jul), Union Colac (Apr/May),
Bennetts on Bellarine (Jan–Mar, off-season), St Leonards ("no upcoming events"
right now), The Deck (pushes to Facebook), Gellibrand River (a cancellation
notice), Alt Rd (summer only). All are correct pins on pages the venue really
maintains; they are just between seasons.

---

## What is left

- **Humanitix was never fetched**, and no Humanitix URL is proposed as an
  `events_url` anywhere above. Two are referred to by name only — The Sound
  Doctor's host feed (already on place #32) and Torquay Theatre Troupe's
  `/jumbuck-hotel` link, seen in the text of `ttt.org.au/whats-on`. That path is
  the scheduled Action's to walk, not this pass's.
- **No URL here was constructed.** Every one was either fetched successfully by me
  or by a researcher, or seen verbatim in a search result — and where it was only
  seen, the log says so. No Google Maps links. Nulls are real nulls.
- **Not researched, deliberately:** every venue in Werribee/Altona/Laverton/
  Tarneit, everything the Queenscliff centroid catches across the bay, and
  Meredith. If Meredith should be in scope, that is a geography-rule decision and
  belongs in `CLAUDE.md`, not in a pass log.
- **The 27 orphan `place_id`s** are the highest-value follow-up in this file and
  need no research at all.
- Unresolved and worth a human five minutes: The Barwon Hotel Winchelsea
  (unreadable host), Hop City's address, Dinny Goonan, Banks Road's broken
  `/events/`, Forrest Brewing (recheck after 25 Sep), Terindah Estate.
