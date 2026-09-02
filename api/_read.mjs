// api/_read.mjs — reading somebody else's page, and triaging a message.
//
// Vercel does not route a file whose name begins with `_`, so this is a module
// rather than an endpoint. Both /api/inbox (on arrival) and /api/admin (the
// Read links button) import it, which is the point: a message must not be
// triaged one way when it lands and another way when a person presses the
// button. One reader, two callers.
//
// It runs on the SERVER, which is what makes it work at all: the function is
// not a browser, so CORS cannot block it, and it is not ClaudeBot, so a site
// that disallows that crawler — Humanitix, Coast & Bay — is still readable. It
// identifies as the same agent the scrapers use.
//
// NO MODEL IS INVOLVED anywhere in this file. That is deliberate and it is the
// whole reason this path is free: a ticket page publishes schema.org, so a link
// needs no inference. A newsletter keeps its events in prose and cannot be read
// this way at all — `sniffProse` below says how much is in there and refuses to
// guess what.

/* ── reading somebody else's page ───────────────────────────────────────────
   Shared by `probe` (is this source worth registering?) and `inbox_read`
   (what is in the links of this email?). They were one copy inside probe
   until the inbox needed the identical answer, and two would have drifted the
   first time either was touched — the automationCell() lesson, one file along.

   It runs on the SERVER, which is the whole point: the function is not a
   browser, so CORS cannot block it, and it is not ClaudeBot, so a site that
   disallows that crawler — Humanitix, Coast & Bay — is still readable. It
   identifies as the same agent the scrapers use. */
const UA = 'whattodo-janjuc/1.0 (+https://www.notice.place; community events listing)';

/* An endpoint that takes a URL from a browser must not become a way to read
   things only the server can reach. */
function safeUrl(raw) {
  let u;
  try { u = new URL(String(raw || '').trim()); } catch { return {error: 'bad_url'}; }
  if (!['http:', 'https:'].includes(u.protocol)) return {error: 'bad_scheme'};
  if (/^(localhost$|127\.|10\.|192\.168\.|169\.254\.|0\.|\[?::1)/i.test(u.hostname)
      || /^172\.(1[6-9]|2\d|3[01])\./.test(u.hostname)) return {error: 'private_address'};
  return {u};
}

/* The 400 KB cap keeps a runaway page from filling the function's memory, and
   it is the right default for HTML. It is WRONG for a JSON endpoint, which it
   corrupts rather than shortens: iNaturalist answers a four-record cetacean
   query with 492 KB, and the cut landed mid-object, so JSON.parse threw
   "Unexpected end of JSON input" and the source read as down.

   So the cap is a parameter now — the default is unchanged, so probe and
   inbox_read behave exactly as before — and the result says when it fired.
   A body that was silently shortened is the failure this project keeps
   paying for: it looks like a world containing less. */
async function getPage(url, ms = 12000, cap = 400_000) {
  const r = await fetch(url, {headers: {'User-Agent': UA},
                              signal: AbortSignal.timeout(ms), redirect: 'follow'});
  const full = await r.text();
  return {status: r.status, type: r.headers.get('content-type') || '',
          body: full.slice(0, cap), truncated: full.length > cap};
}

/* Read robots the way eventlib does — only a 401/403 on robots.txt ITSELF is a
   refusal, because plenty of firewalls answer a bot with 403 and the parser
   would otherwise read that as "forbidden from the entire site". */
async function robotsAllows(u) {
  try {
    const rb = await getPage(u.origin + '/robots.txt', 8000);
    if ([401, 403].includes(rb.status)) return {ok: false, why: 'robots.txt refused'};
    if (rb.status !== 200) return {ok: true, why: 'no robots.txt'};
    const lines = rb.body.split(/\r?\n/).map(l => l.trim());
    let active = false; const dis = [];
    for (const l of lines) {
      const m = /^user-agent:\s*(.+)$/i.exec(l);
      if (m) { active = ['*', 'whattodo-janjuc'].includes(m[1].trim().toLowerCase()); continue; }
      const d = /^disallow:\s*(.*)$/i.exec(l);
      if (d && active && d[1].trim()) dis.push(d[1].trim());
    }
    /* A robots pattern is not a prefix. Truncating at the first `*` turns
       `/*?add-to-cart=` into `/`, which matches every path on the site — that
       read Coast & Bay and Patagonia as refusing us when both plainly allow
       the pages we wanted. `*` is any run of characters, a trailing `$`
       anchors the end, everything else is literal. */
    const rx = p => new RegExp('^' + p.replace(/[.+?^${}()|[\]\\]/g, '\\$&')
                                      .replace(/\*/g, '.*').replace(/\\\$$/, '$'));
    const path = u.pathname + u.search;
    const hit = dis.find(p => { try { return rx(p).test(path); } catch { return false; } });
    return hit ? {ok: false, why: `robots.txt disallows ${hit}`}
               : {ok: true, why: 'robots.txt allows it'};
  } catch { return {ok: true, why: 'robots.txt could not be read — proceeding'}; }
}

/* Every object in every ld+json block, flattened. Nested @graph and arrays are
   the normal shape, not the edge case. */
function ldNodes(html) {
  const out = [];
  for (const b of html.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    let doc; try { doc = JSON.parse(b[1]); } catch { continue; }
    const stack = [doc];
    while (stack.length) {
      const o = stack.pop();
      if (Array.isArray(o)) { stack.push(...o); continue; }
      if (!o || typeof o !== 'object') continue;
      out.push(o);
      stack.push(...Object.values(o).filter(v => v && typeof v === 'object'));
    }
  }
  return out;
}

/* schema.org names three Event subtypes without the word in them — Festival,
   Hackathon, CourseInstance — and `'Event' in 'Festival'` is false, which is
   how every festival was silently dropped until Aug 2026. EventVenue is a
   place, not an event, and has to be excluded by name. */
const typeOf = o => [].concat(o['@type'] || []).join(' ');
const isEventType = ty => (/Event/.test(ty) && !/EventVenue/.test(ty))
                          || /Festival|Hackathon|CourseInstance/.test(ty);

/* A stored date is a DAY, not an instant. `startDate` carries the venue's own
   offset, so the date a reader cares about is the one written in the string —
   parsing it into a Date and formatting back is the nextDate bug, which shifts
   every Melbourne evening onto the following morning in UTC. Split, never
   parse. */
const dayOf  = s => (String(s || '').match(/^(\d{4}-\d{2}-\d{2})/) || [])[1] || null;
const clockOf = s => {
  const m = String(s || '').match(/T(\d{2}):(\d{2})/);
  if (!m) return null;
  const h = +m[1], ap = h < 12 ? 'am' : 'pm';
  return `${((h + 11) % 12) + 1}${m[2] === '00' ? '' : ':' + m[2]}${ap}`;
};
/* The weekday the extracted date actually falls on, built from the string's own
   parts through Date.UTC for the same reason. Printed so a person can check it
   against whatever weekday the poster or the email claimed — the checksum
   scrape_venues.py applies, done by eye because an email has no field to hold
   its own claim. */
const WD = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
function weekdayOf(iso) {
  const p = String(iso || '').split('-').map(Number);
  if (p.length !== 3 || p.some(isNaN)) return null;
  return WD[new Date(Date.UTC(p[0], p[1] - 1, p[2])).getUTCDay()];
}

/* streetAddress frequently already ends in the suburb — Humanitix gives
   "Lake Lorne, Drysdale VIC 3222, Australia" — so appending addressLocality
   again printed the town twice. Add it only when it is genuinely missing. */
function joinAddr(a) {
  if (!a || typeof a !== 'object') return null;
  const street = String(a.streetAddress || '').replace(/\s+/g, ' ').trim();
  const town = String(a.addressLocality || '').trim();
  if (!street) return town || null;
  return (town && !new RegExp('\\b' + town.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i').test(street))
    ? `${street}, ${town}` : street;
}

const textOf = v => typeof v === 'string' ? v
  : (v && typeof v === 'object') ? String(v.name || v.text || '') : '';

/* One schema.org Event -> the shape the Add form and `create` already take.
   Anything it cannot establish stays null: a guess here becomes a row. */
function eventFromLd(o, from) {
  const start = o.startDate;
  if (!start || !dayOf(start)) return null;
  const loc = o.location || {};
  const addr = loc.address || {};
  const venue = textOf(loc.name) || null;
  const suburb = typeof addr === 'object'
    ? (addr.addressLocality || null) : null;
  const street = typeof addr === 'object' ? joinAddr(addr) : null;
  const offer = [].concat(o.offers || [])[0] || {};
  return {
    what: 'event',
    name: textOf(o.name).trim().slice(0, 200) || null,
    starts_on: dayOf(start),
    ends_on: o.endDate && dayOf(o.endDate) !== dayOf(start) ? dayOf(o.endDate) : null,
    weekday: weekdayOf(dayOf(start)),
    time_text: clockOf(start) ? (clockOf(o.endDate) && dayOf(o.endDate) === dayOf(start)
      ? `${clockOf(start)}–${clockOf(o.endDate)}` : clockOf(start)) : null,
    venue, suburb, address: street || null,
    description: String(o.description || '').replace(/\s+/g, ' ').trim().slice(0, 600) || null,
    cost: offer.price === 0 || offer.price === '0' ? 'Free' : null,
    info_url: String(o.url || from).slice(0, 500),
    schema_type: typeOf(o) || null,
  };
}

/* A LocalBusiness/Store is the OTHER half of what arrives — most of what a
   newsletter names is a business, not a happening, and this project has no
   other route that finds one. */
function placeFromLd(o, from) {
  const addr = o.address || {};
  if (typeof addr !== 'object' || !addr.streetAddress) return null;
  const geo = o.geo || {};
  const lat = Number(geo.latitude), lng = Number(geo.longitude);
  return {
    what: 'activity',
    name: textOf(o.name).trim().slice(0, 200) || null,
    address: joinAddr(addr),
    suburb: addr.addressLocality || null,
    phone: addr.telephone || o.telephone || null,
    /* A coordinate under four decimal places is a kilometre-wide claim, and on
       this coast that is usually open water. Offered only when the source's own
       number is precise enough to be worth checking; a person still geocodes. */
    lat: Number.isFinite(lat) && String(geo.latitude).split('.')[1]?.length >= 4 ? lat : null,
    lng: Number.isFinite(lng) && String(geo.longitude).split('.')[1]?.length >= 4 ? lng : null,
    hours: String(o.openingHours || '').slice(0, 200) || null,
    description: String(o.description || '').replace(/\s+/g, ' ').trim().slice(0, 600) || null,
    url: String(o.url || from).slice(0, 500),
    schema_type: typeOf(o) || null,
  };
}


/* ── what is in the prose, without a model ──────────────────────────────────
   The link reader covers a ticket page and cannot touch a NEWSLETTER, whose
   events are sentences. Measured on a real one — The Geelong Gist carries
   schema.org `Article` and `BreadcrumbList` and no `Event` at all.

   So this does not extract; it DETECTS. It answers "is this worth twenty
   minutes of yours", which is a question regex can honestly answer, and leaves
   "what are the events" to a person. Naming a date is not claiming one. */
const MONTHS = 'january|february|march|april|may|june|july|august|september|october'
             + '|november|december|jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec';
const DATE_RE = new RegExp('\\b(?:'
  + `\\d{1,2}(?:st|nd|rd|th)?\\s+(?:${MONTHS})`      // 5th September
  + `|(?:${MONTHS})\\s+\\d{1,2}(?:st|nd|rd|th)?`     // September 5
  + '|\\d{4}-\\d{2}-\\d{2}'                          // 2026-09-05
  + '|\\d{1,2}/\\d{1,2}/\\d{2,4}'                    // 5/9/2026
  + ')\\b', 'gi');

export function sniffProse(text, places) {
  const s = String(text || '');
  const dates = [...new Set((s.match(DATE_RE) || []).map(d => d.trim()))];
  /* Match against the registry we already have rather than trying to recognise
     a venue from nothing. Short names are skipped — "Gather" and "Bloom" are
     real place rows and also ordinary words, and a false venue is worse than a
     missing one because it makes a quiet message look urgent. */
  const low = s.toLowerCase();
  const venues = [];
  for (const p of places || []) {
    for (const nm of [p.name, ...(p.aliases || [])]) {
      const n = String(nm || '').trim();
      if (n.length < 7) continue;
      if (low.includes(n.toLowerCase()) && !venues.includes(p.name)) venues.push(p.name);
    }
  }
  return {dates, venues};
}

/* How much work is this message? The states say how much, never what it means —
   nothing here decides whether a thing is worth listing, which is the judgement
   the queue exists to ask a person for. */
export function triageOf(r) {
  const live = (r.candidates || []).filter(c => !c.gate);
  if (live.some(c => !c.already)) return 'ready';
  if (live.length) return 'duplicate';               // every one of them we hold
  const sig = r.signals || {};
  if ((r.links || 0) > 0 || (sig.dates || []).length || (sig.venues || []).length)
    return 'needs-you';                              // something real, unreadable
  return 'nothing';
}

/* One message, read end to end. `db` is passed in so each caller uses its own —
   /api/inbox has one, /api/admin has one, and neither should grow a second. */
export async function readMessage(msg, db, {cap = 6} = {}) {
  /* Decode quoted-printable BEFORE matching, never after: `raw` is the full
     MIME message, so a long URL is split across a soft line break and every `=`
     in its query string is written `=3D`. Matching first finds two broken
     halves of a link nobody can open. Same rule as linksIn() in the page. */
  const src = String(msg.raw || msg.body || '')
    .replace(/=\r?\n/g, '')
    .replace(/=([0-9A-F]{2})/gi, (_, h) => String.fromCharCode(parseInt(h, 16)));
  const seen = new Set(), links = [];
  for (const m of src.matchAll(/https?:\/\/[^\s"'<>()\]]+/g)) {
    const u = m[0].replace(/[.,;:]+$/, '');
    /* Unsubscribe, tracking pixels and the sender's own chrome are most of the
       links in a newsletter and none of them is a listing. */
    if (/unsubscribe|list-manage|\.(png|jpe?g|gif|svg|css|js)($|\?)|\/(privacy|terms)/i.test(u)) continue;
    if (!seen.has(u)) { seen.add(u); links.push(u); }
  }

  const took = links.slice(0, cap);
  const out = {at: new Date().toISOString(), links: links.length, read: took.length,
               skipped: Math.max(0, links.length - cap),   // never a silent cap
               pages: [], candidates: []};

  for (const link of took) {
    const {u, error} = safeUrl(link);
    if (error) { out.pages.push({url: link, verdict: error}); continue; }
    try {
      const rob = await robotsAllows(u);
      if (!rob.ok) { out.pages.push({url: link, verdict: rob.why}); continue; }
      const page = await getPage(u.toString());
      if (page.status >= 400) {
        out.pages.push({url: link, verdict: `answered ${page.status}`}); continue; }
      const nodes = ldNodes(page.body);
      const evs = nodes.filter(o => isEventType(typeOf(o)) && o.startDate)
                       .map(o => eventFromLd(o, u.toString())).filter(Boolean);
      /* Deliberately NOT bare `Place`: on a ticket page that is the event's own
         VENUE, and proposing it as a business to create is the
         organiser-is-not-the-venue trap in a third hat. A venue reaches us
         through the event's `venue` field, where it gets matched against the
         registry instead of invented. */
      const biz = nodes.filter(o => /LocalBusiness|Store|Restaurant|Brewery|Winery/.test(typeOf(o))
                                    && !isEventType(typeOf(o)))
                       .map(o => placeFromLd(o, u.toString())).filter(Boolean);
      for (const c of [...evs, ...biz]) if (c.name) out.candidates.push({...c, from: u.toString()});
      out.pages.push({url: link, verdict: evs.length || biz.length
        ? `${evs.length} event(s), ${biz.length} business(es)`
        : 'nothing machine-readable — prose, so it needs a person'});
    } catch (e) {
      out.pages.push({url: link, verdict: 'could not be reached: ' + String(e).slice(0, 90)});
    }
  }

  const places = await db('GET', '/rest/v1/places?select=id,name,aliases');
  out.signals = sniffProse([msg.subject, msg.body].filter(Boolean).join('\n'), places);

  /* The free gates, and they run BEFORE anybody researches anything because
     they kill most candidates for nothing. */
  const today = new Date().toLocaleDateString('en-CA', {timeZone: 'Australia/Melbourne'});
  const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const dates = [...new Set(out.candidates.map(c => c.starts_on).filter(Boolean))];
  /* Same day is the only scope worth checking: one story time at five branches
     is not a duplicate, and the board already clusters those. */
  const sameDay = dates.length
    ? await db('GET', '/rest/v1/events?select=id,name,starts_on,venue,place_id,published'
               + `&starts_on=in.(${dates.join(',')})`) : [];

  for (const c of out.candidates) {
    if (c.starts_on && c.starts_on < today) { c.gate = 'already past'; continue; }
    if (c.what === 'event' && !c.starts_on) { c.gate = 'no date published'; continue; }

    /* Match the venue against name PLUS every alias, and against each
       comma-separated part on its own — a trailing suburb is what usually stops
       a match ("Blackman's Brewery, Torquay"). */
    if (c.venue) {
      const want = norm(c.venue);
      const parts = c.venue.split(',').map(norm).filter(Boolean);
      const hit = places.find(p => {
        const names = [p.name, ...(p.aliases || [])].map(norm);
        return names.includes(want) || names.some(nm => parts.includes(nm));
      });
      if (hit) { c.place_id = hit.id; c.place_name = hit.name; }
      else c.needs_place = true;
    }

    /* Name AND date, never name alone — dropping on a bare name match is what
       swallowed every later night of a recurring gig in scrape_venues.py and
       reported the gap as a duplicate rather than as anything missing.
       `published` is deliberately NOT filtered: both halves of the one real
       duplicate this database has had were held rows, so a check that reads
       only the live board finds neither. */
    const mine = norm(c.name);
    const clash = sameDay.filter(e => e.starts_on === c.starts_on
      && (norm(e.name) === mine || norm(e.name).includes(mine) || mine.includes(norm(e.name))));
    if (clash.length) c.already = clash.map(e => ({id: e.id, name: e.name,
      starts_on: e.starts_on, venue: e.venue, published: e.published}));
  }

  out.triage = triageOf(out);
  return out;
}

/* What /api/admin's `probe` needs — it asks a different question of the same
   page ("is this source worth registering?"), so it reads the parts rather than
   calling readMessage. Exported here in one place so there is one list. */
export {safeUrl, getPage, robotsAllows, ldNodes, isEventType, typeOf};
