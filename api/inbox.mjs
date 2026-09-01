// POST /api/inbox — a venue emails its listings and they land in the queue.
//
// The 18 sources that read "nothing machine-readable" are not going to grow a
// feed. They will keep sending a person an email, so this is the route that
// actually scales for them: it works by asking rather than parsing.
//
// Nothing here interprets the message. It stores what arrived, and a person
// (or Autofill) turns it into a listing in the back of house. That separation
// is the point — an inbound endpoint that tried to write events directly would
// be a public form with no review, which is the one thing this project's
// write path has never allowed.
//
// Needs in the Vercel project:
//   SUPABASE_URL, SUPABASE_SERVICE_KEY   — the inbox table has no anon policy
//   INBOX_SECRET                         — the shared secret the sender proves
//
// The sender is a Cloudflare Email Worker (see CLAUDE.md). It POSTs JSON and
// sets `x-inbox-secret`. Without the secret this endpoint refuses everything:
// it is a public URL, and an open one would be a spam target within a day.

import crypto from 'node:crypto';
import {readMessage} from './_read.mjs';

const CAP = 60_000;          // one email's worth; a newsletter is not an event

function ok(given, want) {
  if (!want) return false;
  const h = s => crypto.createHash('sha256').update(String(s ?? '')).digest();
  return crypto.timingSafeEqual(h(given), h(want));
}

// Their markup is data, never instructions, and nothing here evaluates it.
// Same rule the scrapers follow when they strip a third party's HTML.
function plain(s, limit = CAP) {
  // JS has no inline (?is) — those are Python's, and carrying the pattern over
  // from eventlib.py made this file fail to parse at all.
  return String(s || '')
    .replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

// Which place did this come from? The sender's domain against the place's own
// website, and **only when exactly one place matches**. 18 library branches
// share grlc.vic.gov.au, so a domain is not an identity — an ambiguous one is
// left null for a person to pick in the back of house rather than filed at
// whichever branch sorted first.
//
// A miss is normal and costs nothing: plenty of venues send through Mailchimp
// or a personal address, and those get linked by hand. This only saves the
// easy ones.
function domainOf(addr) {
  const at = String(addr || '').lastIndexOf('@');
  if (at < 0) return '';
  return addr.slice(at + 1).trim().toLowerCase().replace(/[>\s]+$/, '').replace(/^www\./, '');
}

async function matchPlace(from, db) {
  const d = domainOf(from);
  if (!d) return null;
  const places = await db(`/rest/v1/places?select=id,website&website=not.is.null`);
  const hits = places.filter(p => {
    try {
      const h = new URL(p.website).hostname.toLowerCase().replace(/^www\./, '');
      // A subdomain counts — mail.venue.com.au is still the venue — but only
      // as a suffix, or "notvenue.com" would match "venue.com".
      return h === d || d.endsWith('.' + h) || h.endsWith('.' + d);
    } catch { return false; }
  });
  return hits.length === 1 ? hits[0].id : null;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({error: 'POST only'});

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
    return res.status(501).json({error: 'not_configured',
      message: 'Set SUPABASE_URL and SUPABASE_SERVICE_KEY in the Vercel project.'});
  if (!process.env.INBOX_SECRET)
    return res.status(501).json({error: 'no_secret',
      message: 'Set INBOX_SECRET in the Vercel project. Without it this endpoint ' +
               'refuses everything, which is the correct failure for a public URL.'});

  // Two ways to present the secret, because senders differ. Postmark allows
  // custom headers on a webhook, so the header is the tidy route; basic auth
  // in the URL is the fallback for a sender that does not. Both are only ever
  // read over HTTPS.
  const auth = String(req.headers.authorization || '');
  const basic = auth.startsWith('Basic ')
    ? Buffer.from(auth.slice(6), 'base64').toString().split(':').pop()
    : '';
  const given = req.headers['x-inbox-secret'] || basic || '';
  if (!ok(given, process.env.INBOX_SECRET))
    return res.status(401).json({error: 'wrong_secret'});

  // Every sender names these fields differently and none of them is wrong.
  // Postmark capitalises (From, TextBody, RawEmail); the Cloudflare worker in
  // tools/ sends lowercase. Read both rather than making one of them the
  // "real" shape, or changing sender means changing this endpoint.
  const b = req.body || {};
  const pick = (...ks) => { for (const k of ks) if (b[k]) return b[k]; return ''; };
  const row = {
    from_addr: String(pick('from', 'From') || b.FromFull?.Email || '').slice(0, 320) || null,
    to_addr:   String(pick('to', 'To', 'OriginalRecipient')).slice(0, 320) || null,
    subject:   String(pick('subject', 'Subject')).slice(0, 500) || null,
    // The readable version is what a person skims in the queue; `raw` keeps
    // whatever actually arrived, because the message is the evidence for
    // anything later written from it.
    body:      plain(pick('text', 'TextBody', 'html', 'HtmlBody')) || null,
    raw:       String(pick('raw', 'RawEmail', 'html', 'HtmlBody', 'text', 'TextBody')).slice(0, CAP) || null,
  };
  if (!row.body && !row.subject)
    return res.status(400).json({error: 'empty', message: 'no subject and no body'});

  const key = process.env.SUPABASE_SERVICE_KEY;
  const read = async path => {
    const q = await fetch(process.env.SUPABASE_URL + path,
      {headers: {apikey: key, Authorization: 'Bearer ' + key}});
    return q.ok ? q.json() : [];
  };
  // The shape readMessage() expects. Same credentials, one more argument.
  const dbq = async (method, path, body) => {
    const q = await fetch(process.env.SUPABASE_URL + path, {method,
      headers: {apikey: key, Authorization: 'Bearer ' + key,
                'Content-Type': 'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body)});
    return q.ok ? q.json() : [];
  };
  // Best effort, and never fatal: a message that cannot be matched is still a
  // message, and losing it because a lookup failed would be the worse bug.
  try { row.place_id = await matchPlace(row.from_addr, read); } catch { }

  /* Read the links NOW, so the queue is already triaged by the time anybody
     looks. Free — there is no model anywhere in readMessage — and it is the
     difference between a pile to work and a list to skim.

     THE BUDGET IS LOAD-BEARING. Postmark gives an inbound webhook about ten
     seconds and RETRIES on a timeout, so being slow here does not mean a late
     answer, it means the same message stored twice. Three links at five
     seconds each is the common case (one link) comfortably read; anything
     slower lands `unread` and the Read links button picks it up, which is a
     worse outcome than being read and a much better one than a duplicate.

     Never fatal, for the same reason the place match is not: a message that
     could not be read is still a message, and losing it to a failed lookup
     would be the worse bug by far. */
  try {
    const read = await Promise.race([
      readMessage(row, dbq, {cap: 3}),
      new Promise(ok => setTimeout(() => ok(null), 8000)),
    ]);
    if (read) { row.read = read; row.triage = read.triage; }
    else row.triage = 'unread';
  } catch { row.triage = 'unread'; }

  const r = await fetch(process.env.SUPABASE_URL + '/rest/v1/inbox', {
    method: 'POST',
    headers: {apikey: key, Authorization: 'Bearer ' + key,
              'Content-Type': 'application/json', Prefer: 'return=representation'},
    body: JSON.stringify(row),
  });
  const text = await r.text();
  if (!r.ok) return res.status(502).json({error: 'store_failed', detail: text.slice(0, 200)});

  const [saved] = JSON.parse(text);
  return res.status(200).json({ok: true, id: saved.id});
}
