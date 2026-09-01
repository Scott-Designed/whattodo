/* ══ api/conditions.mjs ═══════════════════════════════════════════════════
   What the natural world is doing on the Surf Coast right now, gathered once
   and handed to every reader from the same cached copy.

   THIS FUNCTION READS AND NEVER WRITES. Every other function in api/ that
   touches Supabase writes something; this one touches Supabase not at all and
   holds no key. If it ever grows a write it becomes the seventh write path
   onto the board, and the invariant to run is the one in CLAUDE.md:
       select count(*) from listings where published and not verified;  -- 0

   ── why a function and not the browser ─────────────────────────────────
   Six of these sources send `Access-Control-Allow-Origin: *`, so the page
   could call them directly. It should not. Open-Meteo's free terms allow
   10,000 calls a day, and three calls per page load would cap the whole site
   at ~3,300 views — a ceiling that TIGHTENS as the site gets busier, which is
   exactly backwards. The data is identical for every reader, so it is fetched
   once per cache window and shared.

   Measured 1 Sep 2026: all sources in parallel, 1.8 s, 63 KB raw.

   ── the cache header is load-bearing ───────────────────────────────────
   vercel.json puts `public, max-age=0, must-revalidate` on /(.*), which looks
   like it forbids this. It does not: a function's own header wins, which is
   checked rather than assumed — /admin on the live deploy answers `no-store`,
   and that is adminpage.mjs setting it. With s-maxage below, the edge serves
   one gather per ten minutes however many people are reading.

   ── one source being down must not take the run with it ────────────────
   Each source is settled independently and reports its own state. The reply
   is always 200 with a `sources` block saying what happened, because a page
   that can draw eight facts should not lose all eight when one host blinks.
   That is the SourceDown lesson from scrape_events.py, one directory along.
   ═══════════════════════════════════════════════════════════════════════ */

import {safeUrl, getPage} from './_read.mjs';

/* Jan Juc — the origin every km is measured from. NOT the value that stood in
   this project until 24 Aug 2026, which was 2.3 km offshore in Bass Strait. */
const HOME = {lat: -38.34456, lng: 144.29517};
/* Bells, for swell and sea temperature: the marine model wants a point in the
   water and the reef is the one everything else is described against. */
const SURF = {lat: -38.3695, lng: 144.2810};

const CACHE = 600;          // seconds at the edge — see the header note above
const SWR   = 1800;         // and how long a stale copy may still be served

/* ── which way a beach faces ───────────────────────────────────────────────
   THIS BELONGS IN A COLUMN AND IS HERE BECAUSE THE COLUMN DOES NOT EXIST.
   `activities` stores a coordinate for every pinned row and nothing about
   which way it points, so offshore/onshore/sheltered cannot be derived from
   the database alone.

   Measured 31 Aug 2026 from OpenStreetMap coastline: OSM draws its coastline
   with land on the left and water on the right of travel, so the seaward
   normal is the segment bearing + 90°, averaged over every segment within
   400 m of the pin. Validated against a fact it was not given — Bells came
   out 136°, making its offshore a north-westerly, which is the classic Bells
   offshore.

   Keyed the way the board keys a saved listing: `e13`/`a90`, because ids
   collide across the two tables. */
const FACES = {
  a218: 12,  a24: 74,  a585: 81,  a209: 85,  a217: 86,  a216: 96,
  a210: 108, a580: 110, a21: 112, a561: 114, a211: 120, a575: 121,
  a221: 124, a579: 125, a3: 128,  a563: 133, a2: 136,   a213: 137,
  a208: 147, a18: 147, a584: 149, a9: 153,   a215: 163, a578: 167,
  a582: 174, a212: 184, a581: 212, a562: 329,
};
/* The coordinate each of those was measured at, so the wind can be asked for
   at the beach rather than for the region. Open-Meteo takes a comma-separated
   list and answers with an array — 28 points is ONE request, measured at
   1.76 s. Worth doing per point: across this coast at one moment the wind ran
   275° at Marengo and 311° at Point Lonsdale, 36° apart, which is the
   difference between offshore and cross-shore. */
const BEACH_AT = {
  a218: [-38.111677, 144.652084], a24:  [-38.540000, 143.978600],
  a585: [-38.778803, 143.664707], a209: [-38.424861, 144.178921],
  a217: [-38.170344, 144.720026], a216: [-38.283914, 144.615206],
  a210: [-38.333945, 144.326585], a580: [-38.307155, 144.376483],
  a21:  [-38.326900, 144.325200], a561: [-38.327236, 144.328054],
  a211: [-38.385930, 144.252611], a575: [-38.436467, 144.127651],
  a221: [-38.633761, 143.892088], a579: [-38.342653, 144.319519],
  a3:   [-38.395310, 144.253890], a563: [-38.268497, 144.664277],
  a2:   [-38.368980, 144.282450], a213: [-38.291844, 144.406279],
  a208: [-38.415151, 144.185827], a18:  [-38.347480, 144.306010],
  a584: [-38.573822, 143.948867], a9:   [-38.473310, 144.042430],
  a215: [-38.272501, 144.515006], a578: [-38.345692, 144.311289],
  a582: [-38.273049, 144.657796], a212: [-38.285655, 144.463220],
  a581: [-38.289703, 144.605825], a562: [-38.152716, 144.563588],
};
const KEYS = Object.keys(BEACH_AT);

const COMPASS = ['N','NNE','NE','ENE','E','ESE','SE','SSE',
                 'S','SSW','SW','WSW','W','WNW','NW','NNW'];
const sector  = d => COMPASS[Math.floor(((d + 11.25) % 360) / 22.5)];
/* Smallest angle between two bearings, 0–180. */
const apart   = (a, b) => Math.abs(((a - b + 540) % 360) - 180);

/* A beach is sheltered when the wind comes off the land behind it — that is,
   from roughly the opposite of the way it faces. A paraglider on the same
   coast wants the exact reverse, which is why this returns the relationship
   rather than a verdict. */
function windRelation(faces, from) {
  const off = apart(from, (faces + 180) % 360);
  if (off <= 45)  return 'offshore';
  if (off >= 135) return 'onshore';
  return 'cross';
}

/* Great-circle metres. Used only to say whether a planned burn is near enough
   to matter, so the cheap formula is the right one. */
function metres(a, b, c, d) {
  const R = 6371000, r = Math.PI / 180;
  const p1 = a * r, p2 = c * r, dp = (c - a) * r, dl = (d - b) * r;
  const x = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}


/* ── what is growing, out of iNaturalist ───────────────────────────────────
   The same method the wildflower work used: research-grade observations in a
   bounding box over the last 30 days. It works for plants and fungi because
   THE ORGANISM'S VISIBILITY IS THE PHENOMENON — a flower is only recorded when
   it is out. It does NOT work for animals, and this deliberately carries none:
   Hooded Plover peaks in the records in February and nests from August,
   because February is when people are on the beach.

   Two boxes, because the two seasons are in different country. The orchids are
   the Anglesea heath; the fungi are the Otways.

   THE HONEST CAVEAT, which belongs anywhere this is printed: observation
   counts measure observers as much as they measure flowers. The reason to
   trust the shape anyway is the differential — orchids swing 25x between
   trough and peak where all plants swing 9x, off the same walkers. */
const HEATH = {nelat: -38.28, nelng: 144.40, swlat: -38.58, swlng: 143.95};
const OTWAY = {nelat: -38.15, nelng: 144.55, swlat: -38.90, swlng: 143.40};

/* Twelve monthly totals per taxon, measured once on 31 Aug 2026 and STORED
   rather than re-fetched: it is years of records, it barely moves, and asking
   for it every ten minutes would be three more calls to say the same thing.
   It is what turns a raw count into "in season" or "over" — without it, 63
   fungi records is a number with nothing to compare against. Re-measure it
   yearly; the date it was taken is printed beside it. */
const BASELINE = {
  orchids: {taxon: 47217, box: HEATH, label: 'Orchids', where: 'Anglesea heath',
            months: [164, 100, 121, 381, 208, 232, 321, 949, 2339, 2563, 470, 237]},
  fungi:   {taxon: 47170, box: OTWAY, label: 'Fungi', where: 'The Otways',
            months: [84, 145, 514, 1007, 2857, 2634, 1160, 384, 234, 259, 114, 86]},
  plants:  {taxon: 47126, box: HEATH, label: 'All flowering plants', where: 'Anglesea heath',
            months: [893, 803, 623, 1704, 1385, 977, 1263, 3272, 6210, 7175, 2290, 1434]},
};
const BASELINE_TAKEN = '2026-08-31';

/* Where this month sits against the taxon's own annual peak, and which way it
   is heading. Bands are wide on purpose — this is "is it worth going to look",
   not a phenology model. */
function seasonOf(months, monthIndex) {
  const peak = Math.max(...months);
  const now  = months[monthIndex];
  const prev = months[(monthIndex + 11) % 12];
  const share = peak ? now / peak : 0;
  const state = share >= 0.7 ? 'peak' : share >= 0.35 ? 'in season' : 'out of season';
  const peakMonth = months.indexOf(peak);
  return {state, share: Math.round(share * 100),
          rising: now > prev,
          peak_month: ['Jan','Feb','Mar','Apr','May','Jun',
                       'Jul','Aug','Sep','Oct','Nov','Dec'][peakMonth]};
}

const iso = d => d.toISOString().slice(0, 10);

/* ── one source, settled on its own ────────────────────────────────────────
   Returns the parsed value AND a report. The report is what /admin draws, so
   a source that fails is visible rather than silently absent — the failure
   mode run_log.py already had to be taught about, where anything that was not
   a known failure phrase came out green. */
async function source(id, url, parse, ms = 12000) {
  const t0 = Date.now();
  const bad = safeUrl(url);
  if (bad.error) return {id, ok: false, state: 'bad_url', error: bad.error, ms: 0};
  try {
    const r = await getPage(url, ms);
    const took = Date.now() - t0;
    if (r.status !== 200)
      return {id, ok: false, state: 'http', error: 'HTTP ' + r.status,
              ms: took, bytes: r.body.length};
    const value = parse(r.body);
    return {id, ok: true, state: 'read', ms: took, bytes: r.body.length, value};
  } catch (e) {
    return {id, ok: false, state: 'down', ms: Date.now() - t0,
            error: String(e && e.message || e).slice(0, 120)};
  }
}

const J = b => JSON.parse(b);
const q = o => Object.entries(o).map(([k, v]) => k + '=' + encodeURIComponent(v)).join('&');
const OM = 'https://api.open-meteo.com/v1/forecast?';
const TZ = 'Australia/Melbourne';

/* ── the tide, out of the marine model's sea level ─────────────────────────
   `sea_level_height_msl` is hourly, and it is a real lunar tide rather than a
   surge field: measured over twelve days the mean interval between high
   waters was 12.32 h, against 12.42 for the lunar M2 constituent and 12.00
   for anything solar or artefactual, and the range grew from 1.5 m to 2.37 m
   as the spring–neap cycle came round.

   BECAUSE IT IS HOURLY THE TIMES ARE GOOD TO ABOUT HALF AN HOUR. This returns
   the hour, and the page must say "low tide around 7pm" and never print a
   tide time to the minute. It is a model, not a gauge, and not a tide table. */
function turningPoints(times, level) {
  const out = [];
  for (let i = 1; i < level.length - 1; i++) {
    const a = level[i - 1], b = level[i], c = level[i + 1];
    if (b >= a && b > c) out.push({kind: 'high', at: times[i], m: b});
    else if (b <= a && b < c) out.push({kind: 'low', at: times[i], m: b});
  }
  return out;
}

export default async function handler(req, res) {
  const started = Date.now();

  const beachLat = KEYS.map(k => BEACH_AT[k][0]).join(',');
  const beachLng = KEYS.map(k => BEACH_AT[k][1]).join(',');

  const jobs = [
    source('weather', OM + q({
      latitude: HOME.lat, longitude: HOME.lng,
      current: 'temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,cloud_cover',
      daily: 'precipitation_sum,uv_index_max',
      past_days: 2, forecast_days: 3, timezone: TZ}), J),

    source('marine', 'https://marine-api.open-meteo.com/v1/marine?' + q({
      latitude: SURF.lat, longitude: SURF.lng,
      current: 'wave_height,wave_period,swell_wave_height,swell_wave_direction,'
             + 'swell_wave_period,wind_wave_height,sea_surface_temperature',
      hourly: 'sea_level_height_msl', forecast_days: 3, timezone: TZ}), J),

    // 28 beaches, one request. See the note on BEACH_AT.
    source('beaches', OM + q({
      latitude: beachLat, longitude: beachLng,
      current: 'wind_speed_10m,wind_direction_10m,wind_gusts_10m', timezone: TZ}), J, 15000),

    source('air', 'https://air-quality-api.open-meteo.com/v1/air-quality?' + q({
      latitude: HOME.lat, longitude: HOME.lng,
      current: 'pm2_5,pm10', timezone: TZ}), J),

    // Kp comes back as ~360 one-minute rows and only the last one is wanted.
    // Trimmed here so the reply stays small; the raw size is in the report.
    source('space', 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json', J),

    source('burns', 'https://emergency.vic.gov.au/public/osom-geojson.json', J, 15000),

    /* iNaturalist. Its robots signals read search=yes, ai-train=no,
       use=reference — nothing here trains anything and referencing is what
       this is. Every observation carries an observer and a licence, and both
       have to be shown wherever the species names are.

       These move over WEEKS, so a ten-minute cache is generous to the point of
       waste — 432 calls a day against iNaturalist's 10,000. A second endpoint
       on a six-hour window would be tidier and is not worth a second thing to
       monitor until something else needs one. */
    ...Object.entries(BASELINE).map(([id, b]) =>
      source('nature.' + id, 'https://api.inaturalist.org/v1/observations/species_counts?' + q({
        taxon_id: b.taxon, quality_grade: 'research',
        d1: iso(new Date(Date.now() - 30 * 864e5)), d2: iso(new Date()),
        nelat: b.box.nelat, nelng: b.box.nelng,
        swlat: b.box.swlat, swlng: b.box.swlng}), J, 20000)),

  ];

  const reports = await Promise.all(jobs);
  const got = Object.fromEntries(reports.map(r => [r.id, r.ok ? r.value : null]));

  /* ── shape the reply ────────────────────────────────────────────────────
     Every block is null-safe on its own, because a source that failed must
     cost only its own block. */
  const out = {at: new Date().toISOString(), gathered_ms: Date.now() - started,
               cache_seconds: CACHE,
               /* Three different places answer this reply and it used to name
                  none of them, which teaches a reader that one number covers
                  the coast. It does not: the air is measured at Jan Juc, the
                  sea at Bells, and Kp is planet-wide. */
               taken_at: {
                 weather: {name: 'Jan Juc', lat: HOME.lat, lng: HOME.lng},
                 sea:     {name: 'Bells Beach', lat: SURF.lat, lng: SURF.lng},
                 air:     {name: 'Jan Juc', lat: HOME.lat, lng: HOME.lng},
                 space:   {name: 'planet-wide', lat: null, lng: null},
                 beaches: {name: 'each beach, individually', lat: null, lng: null},
               }};

  const w = got.weather;
  if (w) {
    const rain = w.daily?.precipitation_sum || [];
    out.weather = {
      temp: w.current.temperature_2m, raining: w.current.precipitation > 0.1,
      wind_kmh: w.current.wind_speed_10m, wind_from: w.current.wind_direction_10m,
      wind_sector: sector(w.current.wind_direction_10m),
      cloud: w.current.cloud_cover,
      uv_max: (w.daily?.uv_index_max || [])[2] ?? null,
      // The 48-hour figure the board already fetches and reads in one
      // direction only: it closes the MTB trails and OPENS the waterfalls.
      rain_48h: rain.slice(0, 2).reduce((a, b) => a + (b || 0), 0),
    };
  }

  const m = got.marine;
  if (m) {
    out.sea = {
      wave_m: m.current.wave_height, wave_s: m.current.wave_period,
      swell_m: m.current.swell_wave_height, swell_s: m.current.swell_wave_period,
      swell_from: m.current.swell_wave_direction,
      wind_wave_m: m.current.wind_wave_height,      // the calm-sea reading
      sea_temp: m.current.sea_surface_temperature,
    };
    const t = m.hourly?.time || [], lv = m.hourly?.sea_level_height_msl || [];
    if (t.length) {
      const now = new Date().toISOString().slice(0, 13);
      out.tide = {
        note: 'hourly model — good to about half an hour, never print a minute',
        next: turningPoints(t, lv).filter(p => p.at.slice(0, 13) >= now).slice(0, 4),
      };
    }
  }

  const b = got.beaches;
  if (Array.isArray(b) && b.length === KEYS.length) {
    out.beaches = KEYS.map((k, i) => {
      const c = b[i].current, from = c.wind_direction_10m, faces = FACES[k];
      return {key: k, faces, faces_sector: sector(faces),
              wind_kmh: c.wind_speed_10m, wind_from: from, wind_sector: sector(from),
              gust_kmh: c.wind_gusts_10m, relation: windRelation(faces, from)};
    }).sort((x, y) => apart(x.wind_from, (x.faces + 180) % 360)
                    - apart(y.wind_from, (y.faces + 180) % 360));
  }

  if (got.air) out.air = {pm2_5: got.air.current.pm2_5, pm10: got.air.current.pm10};

  if (Array.isArray(got.space) && got.space.length) {
    const last = got.space[got.space.length - 1];
    out.space = {kp: last.kp_index, at: last.time_tag,
                 aurora_watch: Number(last.kp_index) >= 6};
  }

  if (got.burns?.features) {
    out.burns = got.burns.features
      .filter(f => ['Planned Burn', 'Fire'].includes(f.properties?.category1))
      .filter(f => f.geometry?.type === 'Point')
      .map(f => ({
        what: f.properties.category1, where: f.properties.location || null,
        status: f.properties.status || null, size: f.properties.sizeFmt || null,
        km: Math.round(metres(HOME.lat, HOME.lng,
                              f.geometry.coordinates[1], f.geometry.coordinates[0]) / 100) / 10,
      }))
      .filter(x => x.km <= 120)          // the region, plus a margin for smoke
      .sort((a, c) => a.km - c.km);
  }


  /* One entry per taxon: what is out now, and where that sits in its own year.
     A raw count with nothing to compare against says very little — 63 fungi
     records is either a dead feed or the end of the season, and only the
     baseline can tell them apart. */
  const month = Number(new Date().toLocaleDateString('en-CA',
                  {timeZone: TZ, month: '2-digit'})) - 1;
  out.growing = Object.entries(BASELINE).map(([id, b]) => {
    const g = got['nature.' + id];
    const season = seasonOf(b.months, month);
    if (!g) return {id, label: b.label, where: b.where, season, species: null,
                    records: null, top: []};
    return {
      id, label: b.label, where: b.where, season,
      species: g.total_results,
      records: (g.results || []).reduce((n, r) => n + r.count, 0),
      top: (g.results || []).slice(0, 6).map(r => ({
        n: r.count,
        name: r.taxon.preferred_common_name || r.taxon.name,
        latin: r.taxon.name})),
    };
  });
  out.growing_note = {
    window: '30 days', source: 'iNaturalist, research grade',
    baseline_taken: BASELINE_TAKEN,
    caveat: 'Observation counts measure observers as much as flowers. Orchids '
          + 'swing 25x between trough and peak where all plants swing 9x, off '
          + 'the same walkers, which is the flowering signal separating itself '
          + 'from the effort.',
  };

  /* ── fire is deliberately NOT fetched ──────────────────────────────────
     CFA's per-district RSS is readable and CORS-blocked, and its own terms
     say the feeds are "available for personal, non-commercial use only",
     pointing websites at Emergency Management Victoria's developer feeds
     instead. Those return a single newline byte out of season, so nobody has
     seen the populated shape.

     Building a parser against an empty endpoint is how a source reads green
     while returning nothing, which run_log.py has already caught once. So
     this reports the block rather than guessing at it, and /admin prints the
     reason and what to do. Turning it on is a licence decision, not a code
     change. */
  out.fire = {
    state: 'blocked',
    why: 'CFA licenses its RSS for personal, non-commercial use and points '
       + 'websites at EMV. The EMV developer feed returns an empty body out '
       + 'of season, so its real shape is unknown.',
    todo: 'Email Emergency Management Victoria — they manage third-party '
        + 'access. Ask whether a free community site may read the district '
        + 'RSS, and what getFDRTFBJSON returns in season. Or wait for '
        + 'November and read it with data in it.',
    districts: {Central: ['Surf Coast', 'Greater Geelong', 'Golden Plains',
                          'Borough of Queenscliffe'],
                'South West': ['Colac Otway']},
  };

  /* The report, last, so the monitor reads one place. Never the raw bodies —
     the Kp feed alone is 28 KB and only its final row is wanted. */
  out.sources = reports.map(r => ({
    id: r.id, ok: r.ok, state: r.state, ms: r.ms,
    bytes: r.bytes ?? null, error: r.error || null,
  }));
  out.ok = reports.every(r => r.ok);

  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  // Overrides vercel.json's blanket max-age=0. Checked against the live
  // deploy: a function's own Cache-Control wins.
  // `max-age=0` is for the BROWSER and `s-maxage` is for the edge. Vercel
  // consumes s-maxage for its own cache and forwards the rest, so without the
  // max-age the client sees a bare `public` and may hold a copy indefinitely
  // on its own heuristic — measured on the deploy, which is the only place
  // this is observable. Confirmed working: x-vercel-cache HIT with a rising
  // age, so one upstream gather serves everybody for CACHE seconds.
  res.setHeader('Cache-Control',
                `public, max-age=0, s-maxage=${CACHE}, stale-while-revalidate=${SWR}`);
  // Open-Meteo is CC-BY 4.0 and the attribution is owed somewhere a person
  // can find it. The page carries it too; this is the machine-readable half.
  res.setHeader('X-Data-Sources',
                'open-meteo.com (CC-BY 4.0); NOAA SWPC; emergency.vic.gov.au');
  // The board reads this cross-origin from www.notice.place in some previews.
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.status(200).json(out);
}
