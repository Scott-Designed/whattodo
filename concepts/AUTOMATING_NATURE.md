# Automating the nature sources — investigated 1 Sep 2026

Every claim below was measured against the live endpoints and the live deploy
on that date. Nothing is built.

---

## The one measurement that decides the shape

**Which of these can a browser fetch directly?** Sent with
`Origin: https://www.notice.place`:

    api.open-meteo.com              Access-Control-Allow-Origin: *
    marine-api.open-meteo.com       Access-Control-Allow-Origin: *
    air-quality-api.open-meteo.com  Access-Control-Allow-Origin: *
    services.swpc.noaa.gov          Access-Control-Allow-Origin: *
    api.inaturalist.org             Access-Control-Allow-Origin: *
    emergency.vic.gov.au            Access-Control-Allow-Origin: *
    data.emergency.vic.gov.au       — none —
    www.cfa.vic.gov.au              — none —

So six of the eight are reachable from `index.html` with no infrastructure at
all, and **the two that are not are both the fire ban** — the one signal that
actually gates a listing. That asymmetry is what the design has to answer.

## …and it still should not be done in the browser

Open-Meteo's free terms: **under 10,000 calls a day, 5,000 an hour, 600 a
minute, non-commercial, CC-BY 4.0.** Notice is free and community-run, so the
licence fits and the attribution is owed.

Three Open-Meteo calls per page load puts a ceiling of about 3,300 page views a
day on the whole site. **The cost scales with traffic, which is exactly the
wrong way round** — the data is identical for every reader, and the busiest day
is when it would break.

## The answer: one function, cached at the edge

    api/conditions.mjs   →   /api/conditions

The browser makes **one** request. The function gathers everything server-side
and returns a single JSON blob.

**Measured, all eight sources in parallel: 1,803 ms, 63 KB.** Well inside a
Vercel function, and the deploy runs in `syd1`, which is the right side of the
planet for these upstreams.

    weather / rain      1797 ms      769 B
    marine / tide       1784 ms    1,865 B
    wind, 8 beaches     1798 ms    3,324 B
    air quality         1799 ms      358 B
    space weather Kp     826 ms   27,925 B
    fire — Central       152 ms    6,887 B
    fire — South West    161 ms    6,315 B
    planned burns       1175 ms   15,973 B

**Edge caching works here, and it was checked rather than assumed.**
`vercel.json` puts `public, max-age=0, must-revalidate` on `/(.*)`, which looks
like it would forbid it — but `/admin` on the live deploy answers
`cache-control: no-store`, which is `adminpage.mjs` setting its own header. A
function's header wins. So `s-maxage=600, stale-while-revalidate=1800` gives
one upstream gather per ten minutes **regardless of how many people are
reading**, and no reader ever waits 1.8 s for it.

    96 gathers a day × 3 Open-Meteo calls = 288 of the 10,000 allowed.

**It reuses `api/_read.mjs`.** `safeUrl`, `getPage` and `robotsAllows` are
already exported there, along with the `whattodo-janjuc` user agent. A second
fetcher in a second file is the `automationCell()` mistake one directory along.

### Per-beach costs one request, not twenty-nine

Open-Meteo takes a comma-separated list of coordinates and returns an array.
Measured:

     29 coords → 29 results, 1,764 ms, 12 KB, 748-char URL
     60 coords → 60 results, 2,089 ms, 25 KB
    120 coords → 120 results, 2,491 ms, 50 KB

So the whole sheltered-beach and offshore feature is **one call**. And it is
worth doing per-point rather than once for the region: measured across the
coast at the same moment, the wind ran 275° at Marengo and 311° at Point
Lonsdale — 36° apart, which is the difference between offshore and cross-shore.

---

## What must NOT go in that function

**iNaturalist species counts.** Wildflowers and fungi move over weeks, and the
query is one call per natural spot. That belongs in the database, written by a
scheduled job — the existing scraper pattern — not fetched per page load.

**Anything a person writes down.** Whale season, fishing runs, meteor showers,
hooded plover nesting, the Fire Danger Period's start date. A calendar checked
once a year is not a failure of automation; it is the correct shape.

So the split is three ways and matches the concept's own conclusion:

    /api/conditions      live, cached 10 min      tide swell wind rain sea
                                                  UV Kp smoke burns fire
    a scheduled job      slow, into the database  wildflower + fungi counts
    a person             a yearly calendar        whale fishing meteors plover

---

## The one blocker, and it is not technical

**The fire ban is the only source with a licence question.** CFA's per-district
RSS is readable and CORS-blocked; its terms say the feeds are *"available for
personal, non-commercial use only"* and point websites at Emergency Management
Victoria's developer feeds instead. Those feeds
(`data.emergency.vic.gov.au/Show?pageId=getFDRTFBJSON`) currently return **a
single newline byte** — `0a`, not `[]` — because it is out of season, so nobody
has seen the populated shape.

Three options, in order of preference:

1. **Email EMV.** They manage third-party access, this is a free community site
   for one shire, and one paragraph settles both questions — may we use the
   RSS, and what does the developer feed look like in season. Same move as the
   Communico email already drafted for the library.
2. **Wait for November** and read the developer feed with real data in it.
3. **Embed CFA's own district widget** as a stopgap. Licensed for embedding,
   zero code, and somebody else's iframe on the page — which this site would
   normally refuse, but it is honest and free for one fire season.

**Do not build a parser against an empty endpoint.** Shipping a scraper that
has never met real data is how a source reads green while returning nothing,
which `run_log.py` has already caught once.

---

## Ordering, if it gets built

1. **`/api/conditions` without the fire half.** Six sources, all
   unambiguous, all CORS-clear anyway, so the function is pure caching and
   request-count discipline. Ship it and read it in the page.
2. **The bearing column.** One number per beach and launch; 29 already
   measured. Nothing else in the whole exploration needs a schema change.
3. **The fire half**, once the licence is settled.
4. **The monthly iNaturalist job**, on the existing Action.

**And run the invariant after any of it**, because a conditions function that
starts writing rows would be the seventh write path:

    select count(*) from listings where published and not verified;   -- must be 0

`/api/conditions` reads and never writes. That is worth stating in the file
itself, because every other function in `api/` that touches Supabase writes.
