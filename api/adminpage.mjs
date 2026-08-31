// GET /admin — the back of house, behind a password.
//
// Until 31 Aug 2026 the page itself was public and only WRITING was locked.
// Scott asked for the whole thing hidden, which is right: the interface names
// every source, every run and every venue's state, and there is no reason for
// that to be readable by anyone who guesses the URL.
//
// Be clear about what this does and does not protect. The listings, places and
// vocabularies are readable from Supabase with the anon key by anyone who wants
// them — that is what the public site runs on, and no page gate changes it.
// What this hides is the interface. The one genuinely private thing, the email
// inbox, was never exposed to the anon key at all.
//
// admin.html lives in private/ rather than public/ so Vercel does not serve it
// as a static file; this function reads it off disk, the same trick as
// api/subject.mjs. vercel.json's includeFiles is what puts it in the bundle.

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import crypto from 'node:crypto';

const DAYS = 14;                       // how long a login lasts
const COOKIE = 'notice_admin';

// The cookie is <expiry>.<hmac>, signed with ADMIN_PASSWORD. Nothing secret is
// in it — it only says "somebody knew the password, until this date" — and it
// cannot be forged without the password, so the password never travels again
// after the first POST.
const sign = (exp, key) =>
  crypto.createHmac('sha256', key).update(String(exp)).digest('base64url');

function valid(cookie, key) {
  if (!cookie || !key) return false;
  const [exp, mac] = String(cookie).split('.');
  if (!exp || !mac || Number(exp) < Date.now()) return false;
  const want = sign(exp, key);
  // Compare digests, so a wrong cookie cannot be narrowed down by timing.
  const a = Buffer.from(mac), b = Buffer.from(want);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const same = (a, b) => {
  const h = s => crypto.createHash('sha256').update(String(s ?? '')).digest();
  return crypto.timingSafeEqual(h(a), h(b));
};

function loginPage(msg) {
  return `<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Back of house — Notice</title>
<style>
  :root{color-scheme:light dark}
  body{font:16px/1.5 ui-sans-serif,system-ui,sans-serif;display:grid;
       place-items:center;min-height:100svh;margin:0;background:#14170F;color:#EDEDE4}
  form{width:min(320px,88vw);text-align:left}
  h1{font-family:ui-serif,Georgia,serif;font-weight:500;font-size:26px;margin:0 0 4px}
  p{color:#8C8C80;font-size:13px;margin:0 0 20px}
  input,button{width:100%;font:inherit;padding:10px 12px;border-radius:8px;box-sizing:border-box}
  input{background:#1C2016;border:1px solid #333A2A;color:inherit}
  button{margin-top:10px;background:#EDEDE4;color:#14170F;border:0;font-weight:600;cursor:pointer}
  .bad{color:#E8836B;font-size:13px;margin:10px 0 0}
</style>
<form method="POST" action="/admin">
  <h1>Back of house</h1>
  <p>Notice — notice.place</p>
  <input type="password" name="password" placeholder="Password" autofocus
         autocomplete="current-password" required>
  <button type="submit">Unlock</button>
  ${msg ? `<p class="bad">${msg}</p>` : ''}
</form>`;
}

let cached = null;
const page = () => (cached ??=
  readFileSync(join(process.cwd(), 'private', 'admin.html'), 'utf8'));

export default async function handler(req, res) {
  const key = process.env.ADMIN_PASSWORD;
  // No password set means no way in — the same refusal api/admin.mjs makes,
  // rather than falling open.
  if (!key) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(501).send(loginPage(
      'ADMIN_PASSWORD is not set in the Vercel project, so there is no way in.'));
  }

  const cookies = Object.fromEntries(String(req.headers.cookie || '').split(';')
    .map(c => c.trim().split('=').map(decodeURIComponent))
    .filter(p => p.length === 2));

  if (req.method === 'POST') {
    // Vercel parses a urlencoded form body for us; fall back for JSON.
    const given = (req.body && (req.body.password ?? '')) || '';
    if (!given || !same(given, key)) {
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      return res.status(401).send(loginPage('That is not the password.'));
    }
    const exp = Date.now() + DAYS * 86400_000;
    res.setHeader('Set-Cookie',
      `${COOKIE}=${exp}.${sign(exp, key)}; Path=/; Max-Age=${DAYS * 86400}` +
      `; HttpOnly; Secure; SameSite=Lax`);
    // 303 so the browser follows with GET rather than re-posting the password.
    res.setHeader('Location', '/admin');
    return res.status(303).end();
  }

  // Signing out: clear the cookie and fall through to the form.
  if (req.query?.signout) {
    res.setHeader('Set-Cookie',
      `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(loginPage('Signed out.'));
  }

  if (!valid(cookies[COOKIE], key)) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    return res.status(401).send(loginPage(''));
  }

  // Through the gate. The flag tells the page it is already authenticated, so
  // it does not ask for the password a second time to write — /api/admin
  // accepts the same cookie.
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  // Injected INSIDE <head>, not between </head> and <body>: a script placed
  // between them is reparented by the HTML parser, which works but is a
  // needless question to leave open. Either way it runs before the page's own
  // script, which is what COOKIE_AUTH depends on.
  return res.status(200).send(
    page().replace('</head>', '<script>window.ADMIN_COOKIE=1</script></head>'));
}
