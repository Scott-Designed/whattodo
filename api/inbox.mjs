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

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({error: 'POST only'});

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY)
    return res.status(501).json({error: 'not_configured',
      message: 'Set SUPABASE_URL and SUPABASE_SERVICE_KEY in the Vercel project.'});
  if (!process.env.INBOX_SECRET)
    return res.status(501).json({error: 'no_secret',
      message: 'Set INBOX_SECRET in the Vercel project. Without it this endpoint ' +
               'refuses everything, which is the correct failure for a public URL.'});

  const given = req.headers['x-inbox-secret'] || '';
  if (!ok(given, process.env.INBOX_SECRET))
    return res.status(401).json({error: 'wrong_secret'});

  const b = req.body || {};
  const row = {
    from_addr: String(b.from || '').slice(0, 320) || null,
    to_addr:   String(b.to || '').slice(0, 320) || null,
    subject:   String(b.subject || '').slice(0, 500) || null,
    // The readable version is what a person skims in the queue; `raw` keeps
    // whatever actually arrived, because the message is the evidence for
    // anything later written from it.
    body:      plain(b.text || b.html || '') || null,
    raw:       String(b.raw || b.html || b.text || '').slice(0, CAP) || null,
  };
  if (!row.body && !row.subject)
    return res.status(400).json({error: 'empty', message: 'no subject and no body'});

  const key = process.env.SUPABASE_SERVICE_KEY;
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
