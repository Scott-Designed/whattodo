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

  const {password, action = 'check', table, id, patch = {}, force = false} = req.body || {};
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
