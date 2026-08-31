# Nature as "what's on" — fire, and wildflowers

Explored 31 Aug 2026. Nothing built. Every URL below was fetched that day and the
result is recorded verbatim; the two that are dead are recorded as dead.

Part of a wider exploration (seasons, tide, swell, wind, moon, stars). These two
were taken first because they are the two ends of the idea: **fire is a season
that closes things, wildflowers are a season that opens them.**

---

## The premise the database already agrees with

`conditions` has 14 tags. **Seven evaluate. Seven have never done anything.**
`met()` in index.html returns `null` for a tag it does not know, and `suits()`
filters nulls out — so an unwired tag is silently inert. No error, no gap on
screen, no way to tell it apart from a row with no conditions at all.

Counted against the live database, 1079 listings:

    EVALUATES                          INERT
    any-weather   476                  calm-sea            40
    good-in-rain  223                  low-tide            18
    dry-ground    139                  new-moon             7
    warm           47                  no-fire-ban          5
    dry-trails     32                  full-moon            2
    low-wind       27                  geomagnetic-storm    1
    clear-sky      19                  high-tide            1

So the vocabulary was written as a nature-driven board from the beginning, and
half of it was never plugged in. This is not a new idea to be invented — it is an
existing idea to be finished.

`no-fire-ban` is on five rows, and they are the right five:

    a102  Backyard Bonfire / Fire Pit Night   Home
    a12   Backyard Camping                    Home
    a65   Blanket Leaf Picnic Area            Lorne (hinterland)
    a78   Bimbi Park – Camp under Koalas      Cape Otway
    e11   Full Moon Bonfire                   Jan Juc

Note e11 carries `no-fire-ban` **and** `full-moon` — two inert tags on one row.
That row is the whole concept in miniature and it currently filters on neither.

---

## Fire

### The region straddles two fire districts, and that decides the design

Victoria is divided into nine fire weather districts. A Total Fire Ban and a Fire
Danger Rating are declared **per district**, not per town. This region is in two
of them, read off the feeds themselves:

    Central     SURF COAST · GREATER GEELONG · GOLDEN PLAINS · BOROUGH OF QUEENSCLIFFE
    South West  COLAC OTWAY

So Torquay, Jan Juc, Anglesea, Aireys Inlet, Lorne, Winchelsea and Deans Marsh are
on one feed, and Apollo Bay, Wye River, Kennett River, Forrest, Beech Forest and
Lavers Hill are on another. **A single site-wide "fire ban today" banner would be
wrong for a third of the listings** — and wrong in the direction that matters,
since the Otways rows are the camping and picnic ones.

The five `no-fire-ban` rows above already span the split: Blanket Leaf is Surf
Coast Shire, Bimbi Park is Colac Otway.

**The cost this implies:** the site's vocabulary is towns (`SUBURBS`), the feed's
vocabulary is municipalities. Town → LGA → district is a lookup that does not
exist yet. It is small and it is fixed — the shire boundaries do not move — but
it has to be written down, and `suburbOf` is where it belongs.

### What is actually readable

**`https://www.cfa.vic.gov.au/cfa/rssfeed/central-firedistrict_rss.xml`**
**`https://www.cfa.vic.gov.au/cfa/rssfeed/southwest-firedistrict_rss.xml`**

Both 200, both plain RSS 2.0, no key. Each carries six items:

- **Five days** — today plus four forecast days. Each says, in words:
  *"Today, Mon, 31 Aug 2026 is not currently a day of Total Fire Ban"*, and
  *"Central: NO RATING"*.
- **A sixth item, "Fire restrictions by municipality"** — every council in the
  district with a yes/no. Today all 26 Central councils read
  *"SURF COAST: No - restrictions may apply"*.

That sixth item is the **fire season** half, and it is the surprise: one document
answers both questions. "Is today a ban day" and "are we in the Fire Danger
Period" arrive together, per council, refreshed continuously.

`robots.txt` on cfa.vic.gov.au is `User-agent: *` and nothing else — fully open,
no AI-crawler clause. A Claude session and the scheduled Action can both read it.
Not Humanitix, not Coast & Bay.

### The licence says the RSS is not for a website

CFA's own terms, on /rss-feeds:

> CFA RSS feeds are protected by copyright laws and are available for personal,
> non-commercial use only. (See below for data feeds for third party developers.)

and, if used anyway: *"The links back to CFA included in the feed must be
displayed when used in a website."*

So the RSS is the readable one and the developer feeds are the licensed one.
Named on the same page, managed by Emergency Management Victoria:

    XML   https://data.emergency.vic.gov.au/Show?pageId=getFDRTFBXML
    JSON  https://data.emergency.vic.gov.au/Show?pageId=getFDRTFBJSON

`robots.txt` there disallows only `/admin`, `/errorpages`, `/META-INF`,
`/templates`, `/WEB-INF`, `/wsviewer`. Nothing in the way.

### …and the licensed feed cannot say "no"

**Both developer feeds return a single newline byte.** Not `[]`, not an empty
document — `0a`. Checked twice, XML and JSON.

That is this project's own standing lesson turning up inside a source: *a query
that silently returns less than you asked for is indistinguishable from a world
containing less.* A bare newline cannot tell "there are no fire bans anywhere in
Victoria today" from "the endpoint moved" or "the service is down". The RSS, which
we are not licensed to put on a website, is the one that states the negative.

Presumably it fills out in season. **Nobody here has seen it populated**, and it
should not be built against until somebody has — November is the first honest
chance. Assuming its shape from the empty case is how a scraper ships a parser
that has never met real data.

Two ways past it, both cheap:

- **Ask EMV.** They manage third-party access and this is a free community site
  for one shire. A one-paragraph email settles whether the RSS may be used, or
  gets the developer feed's in-season shape documented. Same move as the
  Communico OAuth email already drafted for the library.
- **The official widget.** CFA publishes embeddable per-district iframes ("Fire
  District Widgets") that are the same data, licensed for embedding, zero code.
  It is somebody else's box on the page, which this site would normally refuse —
  but as a stopgap during the first fire season it is honest and it is free.

### Dead ends, recorded so nobody re-walks them

- `cfa.vic.gov.au/cfa/rssfeed/todaystotalfirebans_rss.xml` — **404**. This is the
  URL most of the internet still cites. It is gone.
- `emergency.vic.gov.au/public/osom-geojson.json` — **200, and it is the wrong
  feed.** 22 live incidents and warnings (fires, planned burns, a flood advice).
  It carries what is *burning*, not what is *banned*. Useful for a different
  question and not this one.
- **BOM's `api.weather.bom.gov.au` forbids it in its own response.** Every payload
  carries `"copyright": "This application programming interface (API) is owned by
  the Bureau of Meteorology. You must not use, copy or share it."` It has fire
  danger per location and it is off the table. Worth knowing, because it is the
  first thing anyone reaches for.
- CFA's own Total Fire Bans page and Fire Restriction Dates page are ASP.NET with
  the table drawn client-side. The static HTML has the nav and no data. So the
  **start date** of a Fire Danger Period is not scrapeable, only its current
  state via the RSS municipality item.

### What it would mean on the board

Three different things, and they are worth keeping apart:

1. **A gate.** `no-fire-ban` finally gates. Five rows today, and it would be
   right — you genuinely cannot light the fire pit.
2. **A day banner.** A Total Fire Ban day is the single most legitimate "what's on
   today" this coast has. It is not a filter, it is a fact about the day, and it
   belongs where the date and the sunset already are. Per district, so a reader
   in Apollo Bay is told about South West.
3. **A season.** The Fire Danger Period runs roughly five months and changes what
   the place is for. That is the answer to the original question — *redefining
   what's on* — better than either of the above. "The coast is in the fire danger
   period" is as real a season as school holidays, and nothing on the site says it.

Number 3 is the interesting one and the cheapest: it is one boolean per council,
already in the feed, and it needs no new filter to be worth printing.

---

## Wildflowers

### The heath is the best wildflower ground in Victoria and the site barely says so

Five rows in the database touch it:

    a150  Anglesea Heath – Wildflower & Echidna Spotting   spot     nature
    e30   ANGAIR Wildflower & Art Weekend    19 Sep 2026   happening festival·nature·arts
    e116  Orchids in the Park – Barwon Heads  23 Sep 2026  happening nature·walk
    a125  ANGAIR Working Bees                              group    volunteering
    a138  ANGAIR Plant Propagation Centre                  venue    nursery

That is one spot, two dated things and a group — for a heathland that carries over
a hundred orchid species. There is no `wildflower` type, and the rows above are
filed under `nature`, `walk` and `festival`.

### The season is measurable, not a claim

iNaturalist's public API, research-grade observations only, in a box covering the
Anglesea heath and the coast from Torquay to Lorne
(`nelat -38.28 nelng 144.40 swlat -38.58 swlng 143.95`):

    Orchidaceae — 8,085 observations, by month of year
      Jan  164   Jul  321
      Feb  100   Aug  949   ███████████████
      Mar  121   Sep 2339   ██████████████████████████████████████
      Apr  381   Oct 2563   ████████████████████████████████████████
      May  208   Nov  470
      Jun  232   Dec  237

    All plants — 28,029 observations, same shape, Sep 6,210 / Oct 7,175

**The honest caveat is that observation counts measure observers as much as
flowers** — ANGAIR's September show brings people out with cameras, and September
is exactly the peak. But orchids swing 25× between trough and peak while all
plants swing 9×, and both curves come off the same walkers. That differential is
the flowering signal separating itself from the effort signal. It is evidence, not
proof, and it should be described that way if it is ever printed.

There is a stricter source in the same API: iNaturalist's **plant phenology
annotation** (`term_id=12`, value 13 = Flowering) — an explicit "this plant was in
flower", not an inference from a date. It peaks in September too (607 of 1,999).
It is thin: only about 7% of observations carry it. Real, and not enough on its own.

### And it is live — this is the thing worth building

Last 28 days to 31 Aug 2026, same box, research grade:
**147 species, 857 observations.** The top of the list, unedited:

     45  Mayfly Orchid          Acianthus caudatus
     39  Leopard Orchid         Diuris pardina
     37  tall greenhood         Pterostylis melagramma
     36  Nodding Greenhood      Pterostylis nutans
     32  dwarf greenhood        Pterostylis nana
     23  Common Heath           Epacris impressa
     22  Red-banded Greenhood   Pterostylis sanguinea
     19  Red Beaks              Pyrorchis nigricans
     17  Blue Fairy Orchid      Pheladenia deformis
     17  Waxlip Orchid          Glossodia major

That is *what is out on the heath this week*, dated, attributed, checkable, and
free. It is a "what's on" with no organiser, no venue and no ticket — which is
precisely the redefinition the question was asking for. A row that today reads
*Anglesea Heath – Wildflower & Echidna Spotting* could read
*Anglesea Heath · 147 species recorded this month · Mayfly Orchid, Leopard Orchid,
Common Heath*.

`api.inaturalist.org` is a documented public API, not a scrape. inaturalist.org's
robots.txt sets `Content-Signal: search=yes, ai-train=no, use=reference` — the same
shape as Coast & Bay, and the same reading: nothing here trains anything and
referencing is permitted. Every observation carries its observer and its licence,
and both would have to be shown.

Second source if one is wanted: the **Atlas of Living Australia** biocache
(`biocache-ws.ala.org.au/ws/occurrences/search`), 37.8M Victorian records, works
from here, no key.

### ANGAIR is a listing and is not a source

`places` has no ANGAIR row. The society is in the database twice as a listing
(a125 group, a138 venue) and nothing reads it — which is the
"a places row is not a listing" fault running the other way: a group with a live,
robots-open calendar that no automation has ever been pointed at.

`angair.org.au/robots.txt` is Yoast default — `Disallow:` empty, everything
allowed, no AI clause. The site publishes guided walks, bird walks, working bees,
plant propagation mornings and the Wildflower & Art Show, with dated
`?occurrence=YYYY-MM-DD` URLs in the page.

**But it runs Modern Events Calendar, and this project has already paid for that
plugin once.** CLAUDE.md records the GMBC finding; both halves were re-confirmed
against ANGAIR on 31 Aug 2026:

    wp-json/mec/v1/events         →  []            (exactly as predicted)
    wp-json/wp/v2/mec-events      →  the POST date, not the event date

All three events read back `2026-08-29` — the day somebody typed them in. A
scraper trusting `date` would file the whole ANGAIR calendar on one wrong day.

So ANGAIR is readable and its API is a trap. The route is the `?occurrence=` URLs
in the HTML, which carry the real dates. That is a known-shape job, not a new one.

### What it would mean

- **A `wildflower` type**, or the season stays buried under `nature`. Five places
  as usual: the `types` row, `GROUP_OF` (→ The landscape), `TYPE_PLURAL`,
  `api/enrich.mjs`, `PLACE_TYPES`/`EVENT_TYPES`. Worth checking `/wildflower`
  against every town and type slug first.
- **A season on a spot, printed, not filtered.** The heath does not stop existing
  in February; it stops being the reason to drive there. `season` is already a
  column and already a `text[]`.
- **Live species on the row.** One iNat call, cached, per pinned natural spot.
  This is the genuinely new thing and it is small.
- **ANGAIR as a source.** A group whose whole year is the wildflower season, with
  an open calendar nobody reads.

---

## What this suggests about the wider question

Both halves came out the same way, and it is worth saying plainly:

**The interesting nature data is not a filter, it is a season and a day.** The
filter framing — "hide what does not suit today" — is what `conditions` was built
for, and it is the least of what these sources can do. Seven tags have sat inert
for months and nobody has missed them, because a gate that hides things is not
what anyone opens a listings site to get.

What has no home on the site at all is the sentence: *it is fire danger period*,
*the orchids are out*, *it is a king tide on Saturday*. Those are what's on. They
have no organiser, no venue and no ticket, and the schema has nowhere to put them
— which is the same gap this project already recorded for "an organiser worth
watching that is not a room".

That is the thing to decide before anything is built.
