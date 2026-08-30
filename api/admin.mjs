// POST /api/admin — the only way an edit reaches the database from a browser.
//
// The back-of-house page (public/admin.html) READS with the anon key, exactly
// like the public site does: everything it shows is already public. Writing is
// different — anon may select and insert but never update or delete
// (supabase/schema.sql), and the service key must never go in the page. So the
// service key lives here, in the function's environment, and this endpoint is
// the whole write surface.
//
// Needs two things in the Vercel project's environment:
//   SUPABASE_URL, SUPABASE_SERVICE_KEY   — the same pair scripts/sync.py uses
//   ADMIN_PASSWORD                       — anything you like; without it this
//                                          endpoint refuses every request
//
// The rules below are the ones scripts/sync.py already enforces, restated here
// because this is a public URL and the page cannot be trusted to have checked.
// A validator that only runs in the browser is decoration.

import crypto from 'node:crypto';

// Which columns may be written, per table. Everything else is refused by name
// rather than silently dropped — a typo that vanishes is how a field ends up
// quietly empty. id/created_at/updated_at are deliberately absent: the first is
// the address, the last two belong to the database's own trigger.
const WRITABLE = {
  activities: new Set(['name','kind','types','tags','ages','cost','location','km','season',
    'duration','description','url','rating','notes','conditions','lat','lng',
    'daypart','added_by','verified','source_note','place_id']),
  events: new Set(['name','types','starts_on','ends_on','time_text','recurrence',
    'venue','location','km','cost','ages','artist','genre','description',
    'ticket_url','info_url','conditions','date_confidence','added_by','verified',
    'source_note','place_id']),
  places: new Set(['name','suburb','address','kind','offers','aliases','website',
    'events_url','ticketing_url','facebook','instagram','lat','lng','source_note',
    'kind_legacy']),
};

const URL_FIELDS = ['url','info_url','ticket_url','website','events_url',
                    'ticketing_url','facebook','instagram'];

const COST_PLACE = ['Free','Cheap','Moderate','Splurge'];
const DAYPART    = ['day','night','both'];
const RECURRENCE = ['none','weekly','fortnightly','monthly','annual'];
const CONFIDENCE = ['high','medium','low'];

// ── the database, as the service key ──────────────────────────────────────
async function db(method, path, body, extra = {}) {
  const key = process.env.SUPABASE_SERVICE_KEY;
  const r = await fetch(process.env.SUPABASE_URL + path, {
    method,
    headers: {apikey: key, Authorization: 'Bearer ' + key,
              'Content-Type': 'application/json', ...extra},
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${r.status} ${text.slice(0, 300)}`);
  return text ? JSON.parse(text) : null;
}

const names = async table =>
  new Set((await db('GET', `/rest/v1/${table}?select=name`)).map(r => r.name));

// ── is it you ─────────────────────────────────────────────────────────────
// Digest both sides first: timingSafeEqual throws on a length mismatch, which
// would leak the password's length through the error rather than the timing.
function passwordOk(given) {
  const want = process.env.ADMIN_PASSWORD || '';
  if (!want) return false;
  const h = s => crypto.createHash('sha256').update(String(s)).digest();
  return crypto.timingSafeEqual(h(given ?? ''), h(want));
}

// ── the rules ─────────────────────────────────────────────────────────────
// Returns a list of complaints. Empty means the patch may be written.
async function complaints(table, patch, current) {
  const bad = [];
  const has = f => Object.prototype.hasOwnProperty.call(patch, f);
  const val = f => (has(f) ? patch[f] : current?.[f]);

  const unknown = Object.keys(patch).filter(k => !WRITABLE[table].has(k));
  if (unknown.length) bad.push(`no such field on ${table}: ${unknown.join(', ')}`);
  if (unknown.length) return bad;          // don't validate a shape we don't know

  if (has('name') && !String(patch.name || '').trim()) bad.push('needs a name');

  // `types` is an array, checked the way `conditions` and `offers` already are.
  // A bare string would reach Postgres as a per-character array, so refuse it
  // here rather than storing {g,i,g}.
  if (table !== 'places' && has('types') && patch.types !== null) {
    if (!Array.isArray(patch.types)) {
      bad.push('types must be a list, even for one type');
    } else {
      const types = await names('types');
      for (const t of patch.types)
        if (!types.has(t)) bad.push(`type '${t}' is not one of the ${types.size} allowed`);
    }
  }
  // `kind` means two different things depending on the table, so this has to
  // dispatch on it: on `places` it is the place taxonomy (pub, hall, beach),
  // on `activities` it is what sort of listing the row is (spot, venue, shop,
  // group, maker, idea). Same word, two vocabularies, one of which would
  // silently accept the other's values if this checked only one.
  if (table === 'places' && has('kind') && patch.kind !== null) {
    const kinds = await names('place_kinds');
    if (!kinds.has(patch.kind)) bad.push(`kind '${patch.kind}' is not a place kind`);
  }
  if (table === 'activities' && has('kind') && patch.kind !== null) {
    const kinds = await names('kinds');
    if (!kinds.has(patch.kind))
      bad.push(`kind '${patch.kind}' is not a listing kind`);
    if (patch.kind === 'happening')
      bad.push(`'happening' is what an event is — a dated thing belongs in the events table`);
  }

  // A maker's address is the one this project can do real harm with: a shaper
  // or a jeweller working from home has a findable home address, and a pin here
  // means "you can stand here". Code cannot tell a self-published address from
  // a dug-up one, so it insists the same edit says where it came from and
  // leaves a person to read it. Only fires when the edit actually touches the
  // kind or the coordinate — the editor sends only what changed, so renaming a
  // maker that already has a pin is untouched by this.
  if (table === 'activities' && (has('kind') || has('lat') || has('lng'))) {
    const makerNow = patch.kind === 'maker';
    const pinNow   = (has('lat') && patch.lat !== null) || (has('lng') && patch.lng !== null);
    if (makerNow && pinNow && !String(patch.source_note || '').trim())
      bad.push(`a maker with a coordinate needs a source_note in the same edit, saying `
             + `where the address came from — it must be one the maker publishes `
             + `themselves, not an ABN record, a geotag or a search result`);
  }
  if (table === 'places' && has('offers') && patch.offers) {
    const offers = await names('place_offers');
    for (const o of patch.offers)
      if (!offers.has(o)) bad.push(`offer '${o}' is not in the vocabulary`);
  }
  if (table !== 'places' && has('conditions') && patch.conditions) {
    const conds = await names('conditions');
    for (const c of patch.conditions)
      if (!conds.has(c)) bad.push(`condition '${c}' is not in the vocabulary`);
  }

  if (table === 'activities') {
    if (has('cost') && patch.cost !== null && !COST_PLACE.includes(patch.cost))
      bad.push(`cost must be one of ${COST_PLACE.join('/')}`);
    if (has('daypart') && !DAYPART.includes(patch.daypart))
      bad.push(`daypart must be ${DAYPART.join('/')}`);
    if (has('rating') && patch.rating !== null &&
        !(Number.isInteger(patch.rating) && patch.rating >= 1 && patch.rating <= 5))
      bad.push('rating must be a whole number 1–5, or empty');
  }
  if (table === 'events') {
    if (has('recurrence') && patch.recurrence !== null && !RECURRENCE.includes(patch.recurrence))
      bad.push(`recurrence must be one of ${RECURRENCE.join('/')}`);
    if (has('date_confidence') && !CONFIDENCE.includes(patch.date_confidence))
      bad.push(`date_confidence must be ${CONFIDENCE.join('/')}`);
    for (const f of ['starts_on','ends_on'])
      if (has(f) && patch[f] && !/^\d{4}-\d{2}-\d{2}$/.test(String(patch[f])))
        bad.push(`${f} must be YYYY-MM-DD`);
  }

  for (const f of URL_FIELDS) {
    if (!has(f) || !patch[f]) continue;
    const u = String(patch[f]);
    if (!/^https?:\/\//i.test(u)) bad.push(`${f} must start with http:// or https://`);
    // Earlier versions of this database were full of these and none of them
    // resolved. They only come off a real device, never out of a model.
    if (/maps\.app\.goo\.gl/.test(u))
      bad.push(`${f} is a maps.app.goo.gl link — those get fabricated, use a real URL`);
  }

  // A coordinate is a claim that you can stand there. Two decimal places is
  // 1.1km wide, which on this coast is often open water — this database has
  // already shipped a placeholder pin 2.3km out to sea. Written out to four
  // places a deliberate round number still passes; a guess usually will not.
  for (const f of ['lat','lng']) {
    if (!has(f) || patch[f] === null || patch[f] === '') continue;
    const raw = String(patch[f]).trim();
    if (!/^-?\d+(\.\d+)?$/.test(raw)) { bad.push(`${f} must be a number`); continue; }
    const dp = (raw.split('.')[1] || '').length;
    if (dp < 4) bad.push(
      `${f} has ${dp} decimal place${dp === 1 ? '' : 's'} — that is a guess, not a ` +
      `coordinate. Geocode it, or write it out to at least four (e.g. -38.3446).`);
  }
  // Both or neither: half a coordinate cannot be drawn.
  const lat = val('lat'), lng = val('lng');
  if ((has('lat') || has('lng')) &&
      ((lat === null || lat === '') !== (lng === null || lng === '')))
    bad.push('lat and lng go together — set both, or clear both');

  if (has('km') && patch.km !== null && patch.km !== '') {
    const n = Number(patch.km);
    if (!Number.isFinite(n) || n < 0) bad.push('km must be a number, or empty');
  }

  if (table !== 'places' && has('place_id') && patch.place_id !== null) {
    const got = await db('GET', `/rest/v1/places?select=id&id=eq.${Number(patch.place_id)}`);
    if (!got.length) bad.push(`there is no place ${patch.place_id}`);
  }

  // Claiming verified without saying where it came from is the flag this
  // project has twice found meaningless. Say what you checked.
  if (table !== 'places' && val('verified') &&
      !String(val('source_note') || '').trim())
    bad.push('verified needs a source_note — say what you actually checked');

  return bad;
}

// Empty strings out of a form are nulls in the database, not empty text — and
// an empty array is how a text[] column is cleared.
function clean(patch) {
  const out = {};
  for (const [k, v] of Object.entries(patch)) {
    out[k] = (typeof v === 'string' && v.trim() === '') ? null
           : (typeof v === 'string' ? v.trim() : v);
  }
  return out;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({error: 'POST only'});

  // The password gates everything. The Supabase keys are checked further down,
  // after the actions that do not touch the database — otherwise pressing Run
  // now reports "set SUPABASE_URL", which is true but has nothing to do with it.
  if (!process.env.ADMIN_PASSWORD)
    return res.status(501).json({error: 'no_password',
      message: 'Set ADMIN_PASSWORD in the Vercel project to enable editing.'});

  const {password, action = 'check', table, id, ids, patch = {}, force = false} = req.body || {};
  if (!passwordOk(password)) return res.status(401).json({error: 'wrong_password'});
  if (action === 'check') return res.status(200).json({ok: true});

  // ── run the scrapers now, as the Action ─────────────────────────────────
  // This is the honest way to read Humanitix on demand. Humanitix's robots.txt
  // permits `whattodo-janjuc` and disallows `ClaudeBot`, so a run driven by an
  // assistant has to pass --skip humanitix and those venues come back "skipped
  // this run". Pressing this dispatches the GitHub Action, which is not Claude
  // and is the same job that runs Mon and Thu — so it reads them normally.
  //
  // Dispatching needs a token; the public API is read-only. Fine-grained PAT
  // with Actions: read and write on this repo, or a classic one with `workflow`.
  if (action === 'dispatch') {
    const token = process.env.GITHUB_TOKEN;
    if (!token) return res.status(501).json({error: 'no_github_token',
      message: 'Set GITHUB_TOKEN in the Vercel project (Actions: read and write) ' +
               'to run the job from here. Until then, press it on GitHub or run ' +
               'the scrapers in a terminal.'});
    const repo = process.env.GITHUB_REPO || 'Scott-Designed/whattodo';
    const r = await fetch(
      `https://api.github.com/repos/${repo}/actions/workflows/events.yml/dispatches`,
      {method: 'POST',
       headers: {Authorization: 'Bearer ' + token,
                 Accept: 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28',
                 'User-Agent': 'whattodo-janjuc',
                 'Content-Type': 'application/json'},
       body: JSON.stringify({ref: 'main'})});
    // 204 No Content is success here; anything else carries a reason.
    if (r.status === 204) return res.status(200).json({ok: true, repo});
    const detail = await r.text();
    return res.status(502).json({error: 'dispatch_failed', status: r.status,
      message: r.status === 403 || r.status === 401
        ? 'GitHub refused the token — it needs Actions: read and write on this repo.'
        : detail.slice(0, 300)});
  }

  // ── test a source, server-side ───────────────────────────────────────────
  // The point of doing it here rather than in the page: this function is not a
  // browser (so CORS cannot block it) and it is not ClaudeBot (so sites that
  // disallow that crawler, like Coast & Bay and Humanitix, are readable). It
  // identifies as whattodo-janjuc, the same as the scrapers, and honours
  // robots.txt before fetching anything.
  if (action === 'probe') {
    const raw = String(req.body?.url || '').trim();
    let u;
    try { u = new URL(raw); } catch { return res.status(400).json({error:'bad_url'}); }
    if (!['http:', 'https:'].includes(u.protocol))
      return res.status(400).json({error:'bad_scheme'});
    // Not a hop into the private network. This endpoint takes a URL from a
    // browser, so it must not become a way to read things only the server can.
    if (/^(localhost$|127\.|10\.|192\.168\.|169\.254\.|0\.|\[?::1)/i.test(u.hostname)
        || /^172\.(1[6-9]|2\d|3[01])\./.test(u.hostname))
      return res.status(400).json({error:'private_address'});

    const UA = 'whattodo-janjuc/1.0 (+https://www.notice.place; community events listing)';
    const get = async (url, ms = 12000) => {
      const stop = AbortSignal.timeout(ms);
      const r = await fetch(url, {headers: {'User-Agent': UA}, signal: stop, redirect: 'follow'});
      return {status: r.status, type: r.headers.get('content-type') || '',
              body: (await r.text()).slice(0, 400_000)};
    };

    const out = {url: u.toString(), checked: []};
    try {
      // robots first, and read it the way eventlib does — only a 401/403 on
      // robots.txt itself counts as a refusal.
      let allowed = true, why = 'robots.txt allows it';
      try {
        const rb = await get(u.origin + '/robots.txt', 8000);
        if ([401, 403].includes(rb.status)) { allowed = false; why = 'robots.txt refused'; }
        else if (rb.status === 200) {
          // the group that applies to us, plus any that names us
          const lines = rb.body.split(/\r?\n/).map(l => l.trim());
          let active = false, dis = [];
          for (const l of lines) {
            const m = /^user-agent:\s*(.+)$/i.exec(l);
            if (m) { active = ['*', 'whattodo-janjuc'].includes(m[1].trim().toLowerCase()); continue; }
            const d = /^disallow:\s*(.*)$/i.exec(l);
            if (d && active && d[1].trim()) dis.push(d[1].trim());
          }
          // A robots pattern is not a prefix. Truncating at the first `*` turns
          // `/*?add-to-cart=` into `/`, which matches every path on the site —
          // that read Coast & Bay and Patagonia as refusing us outright when
          // both plainly allow the pages we wanted. `*` is any run of
          // characters and a trailing `$` anchors the end; everything else is
          // literal.
          const rx = p => new RegExp('^' +
            p.replace(/[.+?^${}()|[\]\\]/g, '\\$&')
             .replace(/\*/g, '.*')
             .replace(/\\\$$/, '$'));
          const path = u.pathname + u.search;
          const hit = dis.find(p => { try { return rx(p).test(path); } catch { return false; } });
          if (hit) { allowed = false; why = `robots.txt disallows ${hit}`; }
        }
      } catch { why = 'robots.txt could not be read — proceeding'; }
      out.robots = why;
      if (!allowed) return res.status(200).json({...out, ok: false, verdict: 'robots.txt says no'});

      const page = await get(u.toString());
      out.status = page.status;
      out.checked.push(`fetched (${page.status}, ${(page.body.length/1024).toFixed(0)}KB)`);
      if (page.status >= 400)
        return res.status(200).json({...out, ok:false, verdict:`the site answered ${page.status}`});

      // 1. a real JSON feed?
      if (/json/i.test(page.type)) {
        try {
          const j = JSON.parse(page.body);
          const arr = Array.isArray(j) ? j : (j.events || j.items || j.data);
          if (Array.isArray(arr) && arr.length) {
            const k = Object.keys(arr[0] || {});
            return res.status(200).json({...out, ok: true,
              verdict: `a JSON feed with ${arr.length} item(s)`,
              detail: `fields on the first one: ${k.slice(0, 10).join(', ')}`});
          }
          return res.status(200).json({...out, ok:false,
            verdict:'valid JSON, but no list of events in it',
            detail: JSON.stringify(j).slice(0, 200)});
        } catch { /* fall through */ }
      }

      // 2. schema.org events in the HTML?
      const blocks = [...page.body.matchAll(
        /<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)];
      let events = 0;
      for (const b of blocks) {
        try {
          const doc = JSON.parse(b[1]);
          const stack = [doc];
          while (stack.length) {
            const o = stack.pop();
            if (Array.isArray(o)) { stack.push(...o); continue; }
            if (!o || typeof o !== 'object') continue;
            stack.push(...Object.values(o).filter(v => v && typeof v === 'object'));
            const ty = [].concat(o['@type'] || []).join(' ');
            const isEvent = /Event/.test(ty) && ty !== 'EventVenue';
            if ((isEvent || /Festival|Hackathon|CourseInstance/.test(ty)) && o.startDate) events++;
          }
        } catch {}
      }
      if (events) return res.status(200).json({...out, ok:true,
        verdict:`${events} schema.org event(s) on the page`,
        detail:'the venue scraper can read this — put it in events_url'});

      // 3. a ticketing platform linked from it?
      const plat = ['oztix','humanitix','trybooking','eventbrite','moshtix']
        .filter(p => page.body.toLowerCase().includes(p + '.com'));
      if (plat.length) return res.status(200).json({...out, ok:true,
        verdict:`links to ${plat.join(', ')}`,
        detail:'the scraper follows those, so this page is worth registering'});

      return res.status(200).json({...out, ok:false,
        verdict:'nothing machine-readable',
        detail:'no JSON feed, no schema.org events, no ticketing links'});
    } catch (e) {
      return res.status(200).json({...out, ok:false,
        verdict:'could not be reached', detail:String(e).slice(0,140)});
    }
  }

  // ── the email inbox ──────────────────────────────────────────────────────
  // Read through here rather than with the anon key, because unlike everything
  // else the back of house shows, an email is not public: it carries whoever
  // sent it and whatever they wrote. The `inbox` table has no anon policy at
  // all, so this is the only way to see it.
  if (action === 'inbox') {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
      return res.status(501).json({error: 'not_configured'});
    const want = ['new', 'filed', 'ignored'].includes(req.body?.status)
      ? `&status=eq.${req.body.status}` : '';
    const rows = await db('GET',
      `/rest/v1/inbox?select=*&order=received_at.desc&limit=200${want}`);
    return res.status(200).json({ok: true, rows});
  }

  // Paste an email in by hand. The domain is on Vercel's nameservers, so the
  // forwarding address is a DNS decision nobody has made yet — and a venue's
  // "here is our September program" email is useful today. Same table, same
  // queue; `from_addr` records that a person put it there.
  if (action === 'inbox_add') {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
      return res.status(501).json({error: 'not_configured'});
    const subject = String(req.body?.subject || '').slice(0, 500).trim();
    const body    = String(req.body?.body || '').slice(0, 60_000).trim();
    if (!subject && !body)
      return res.status(400).json({error: 'empty', message: 'no subject and no body'});
    const [row] = await db('POST', '/rest/v1/inbox',
      {from_addr: String(req.body?.from || '').slice(0, 320).trim() || 'pasted by hand',
       subject: subject || null, body: body || null, raw: body || null},
      {Prefer: 'return=representation'});
    return res.status(200).json({ok: true, row});
  }

  if (action === 'inbox_status') {
    if (!['new', 'filed', 'ignored'].includes(req.body?.status))
      return res.status(400).json({error: 'bad_status'});
    const n = Number(req.body?.id);
    if (!Number.isInteger(n) || n <= 0) return res.status(400).json({error: 'bad_id'});
    // Never deleted on the way past: the message is the evidence for whatever
    // was written from it, the same reason run_log keeps the raw scraper text.
    const [row] = await db('PATCH', `/rest/v1/inbox?id=eq.${n}`,
      {status: req.body.status, note: req.body.note ?? null},
      {Prefer: 'return=representation'});
    return res.status(200).json({ok: true, row});
  }

  // ── approve rows from the review queue ──────────────────────────────────
  // One request for a whole batch: the library import alone is 500 rows and
  // 500 round trips would be absurd. Every row still has to earn it — a
  // verified flag with no source_note is the meaningless flag this project
  // already has a note about.
  if (action === 'verify') {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
      return res.status(501).json({error: 'not_configured'});
    if (!['activities', 'events'].includes(table))
      return res.status(400).json({error: 'bad_table',
        message: 'verify works on activities or events'});
    const list = (Array.isArray(ids) ? ids : []).map(Number)
      .filter(n => Number.isInteger(n) && n > 0);
    if (!list.length)   return res.status(400).json({error: 'no_ids'});
    if (list.length > 600) return res.status(400).json({error: 'too_many',
      message: 'verify at most 600 rows at a time'});

    const inList = `(${list.join(',')})`;
    const rows = await db('GET',
      `/rest/v1/${table}?select=id,name,source_note&id=in.${inList}`);
    const bare = rows.filter(r => !String(r.source_note || '').trim());
    if (bare.length) return res.status(400).json({error: 'no_source_note',
      message: `${bare.length} row(s) have no source_note — verifying those would ` +
               `record that somebody looked when nothing says what they checked.`,
      names: bare.slice(0, 5).map(r => r.name)});

    const done = await db('PATCH', `/rest/v1/${table}?id=in.${inList}`,
                          {verified: true}, {Prefer: 'return=representation'});
    return res.status(200).json({ok: true, verified: done.length});
  }

  // Everything past here reads or writes the database.
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
    return res.status(501).json({error: 'not_configured',
      message: 'Set SUPABASE_URL and SUPABASE_SERVICE_KEY in the Vercel project.'});

  if (!WRITABLE[table]) return res.status(400).json({error: 'bad_table',
    message: `table must be one of ${Object.keys(WRITABLE).join(', ')}`});
  const rowId = Number(id);
  if (!Number.isInteger(rowId) || rowId <= 0)
    return res.status(400).json({error: 'bad_id'});

  try {
    const [current] = await db('GET', `/rest/v1/${table}?select=*&id=eq.${rowId}`);
    if (!current) return res.status(404).json({error: 'no_such_row',
      message: `${table} has no row ${rowId}`});

    if (action === 'update') {
      const body = clean(patch);
      if (!Object.keys(body).length)
        return res.status(400).json({error: 'empty_patch'});

      const bad = await complaints(table, body, current);
      if (bad.length) return res.status(400).json({error: 'invalid', complaints: bad});

      const [row] = await db('PATCH', `/rest/v1/${table}?id=eq.${rowId}`, body,
                             {Prefer: 'return=representation'});
      return res.status(200).json({ok: true, row});
    }

    if (action === 'delete') {
      // The same guard scripts/sync.py's reject has: a verified row is one a
      // person vouched for, so deleting it takes a second, deliberate press.
      if (current.verified && !force)
        return res.status(409).json({error: 'verified',
          message: `${current.name} is verified — deleting it needs a confirm.`});
      await db('DELETE', `/rest/v1/${table}?id=eq.${rowId}`);
      return res.status(200).json({ok: true, deleted: {table, id: rowId, name: current.name}});
    }

    return res.status(400).json({error: 'bad_action',
      message: 'action must be check, update or delete'});
  } catch (e) {
    return res.status(500).json({error: 'failed', detail: String(e).slice(0, 300)});
  }
}
