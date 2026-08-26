/* ══ api/subject.mjs ═══════════════════════════════════════════════════
   Serves /place/<slug> and /type/<slug> with their metadata already in the
   HTML, rather than written in by JavaScript after the page has loaded.

   Why this exists. Google renders JavaScript, so search was never the
   problem — link previews are. iMessage, Slack, WhatsApp, Facebook and
   Twitter read the raw HTML and stop. Every town and every type was
   therefore being shared as "Place — Notice" with no description, which is
   the same card 93 times.

   Why a function and not 93 generated files. This project has no build step
   and the intention is that it never gets one. A file per subject would also
   be a second copy of the page shell, which would drift from place.html the
   first time either was touched. So the page stays one file, and this reads
   it and edits the head on the way past.

   What it does NOT do: query the database. A count in the description would
   read better, but it would put a Supabase call in front of every page view
   and give the page a way to fail that it does not currently have. The count
   is already on the page itself, where the reader is.
   ═══════════════════════════════════════════════════════════════════════ */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import vm from 'node:vm';

/* The host the request actually arrived on, not a constant. notice.place 308s
   to www.notice.place, so a hardcoded apex would make every canonical and
   og:url point at a redirect — naming a page's own address as somewhere it is
   not. Falls back only if the header is missing. */
function site(req){
  const host = (req.headers && req.headers.host) || 'www.notice.place';
  return 'https://' + host;
}

/* Read once per cold start, not once per request. */
const cache = {};
function file(name){
  if(!(name in cache)) cache[name] = readFileSync(join(process.cwd(), 'public', name), 'utf8');
  return cache[name];
}

/* The vocabulary is a classic browser script, so it cannot be imported — but
   it is pure data and functions with nothing of the DOM in it, so it runs
   as-is in a sandbox. That keeps ONE copy of the suburb list, the type labels
   and the slug rules, which is the whole reason notice-vocab.js exists. */
let V = null;
function vocab(){
  if(V) return V;
  const box = vm.createContext({});
  vm.runInContext(file('notice-vocab.js'), box);
  V = vm.runInContext(
    '({PLACE_ORDER, PLACE_TYPES, EVENT_TYPES, NOT_A_TOWN, slugify, unslug, typeLabel})', box);
  return V;
}

const esc = s => String(s == null ? '' : s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

/* What each kind of page is called and says, in one place so the two branches
   cannot drift apart. */
function describe(kind, slug){
  const {PLACE_ORDER, PLACE_TYPES, EVENT_TYPES, NOT_A_TOWN, unslug, typeLabel} = vocab();
  if(kind === 'place'){
    const name = unslug(slug, PLACE_ORDER);
    if(!name) return null;
    return {
      page:  'place.html',
      title: name,
      desc:  NOT_A_TOWN[name] ||
             `What's on in ${name}, and what's there anyway — from Notice, a community list for Jan Juc and the Surf Coast.`
    };
  }
  const type = unslug(slug, PLACE_TYPES.concat(EVENT_TYPES));
  if(!type) return null;
  const label = typeLabel(type);
  return {
    page:  'type.html',
    title: label,
    desc:  `${label} around Jan Juc and the Surf Coast, town by town — everywhere it is, grouped by where it is.`
  };
}

/* No og:image yet. A card with no picture beats a card pointing at a picture
   that does not exist, and the site has no artwork made for the 1200x630 slot. */
function head(d, url){
  return [
    `<meta name="description" content="${esc(d.desc)}">`,
    `<link rel="canonical" href="${esc(url)}">`,
    `<meta property="og:site_name" content="Notice">`,
    `<meta property="og:type" content="website">`,
    `<meta property="og:url" content="${esc(url)}">`,
    `<meta property="og:title" content="${esc(d.title)} — Notice">`,
    `<meta property="og:description" content="${esc(d.desc)}">`,
    `<meta name="twitter:card" content="summary">`,
    `<meta name="twitter:title" content="${esc(d.title)} — Notice">`,
    `<meta name="twitter:description" content="${esc(d.desc)}">`
  ].join('\n');
}

export default function handler(req, res){
  const q = req.query || {};
  const kind = q.kind === 'type' ? 'type' : 'place';
  const slug = String(q.slug || '');
  const param = kind === 'place' ? 'p' : 't';

  try{
    const d = describe(kind, slug);

    /* A slug for a town or a type that does not exist is a 404, not a page
       that quietly renders. The body is still the real page — it explains
       itself and offers the list — but the status tells a crawler the truth
       rather than leaving it to guess at a soft 404. */
    if(!d){
      const html = file(kind + '.html');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.status(404).send(html.replace(/<meta name="robots"[^>]*>/, '') 
        .replace('</head>', '<meta name="robots" content="noindex">\n</head>'));
      return;
    }

    const url  = `${site(req)}/${kind}/${slug}`;
    const html = file(d.page)
      .replace(/<title>[\s\S]*?<\/title>/, `<title>${esc(d.title)} — Notice</title>`)
      .replace('</head>', head(d, url) + '\n</head>');

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(200).send(html);
  }catch(e){
    /* If this function is broken the page must still open. Falling back to the
       query-string form gives up the metadata and keeps the site. */
    res.setHeader('Location', `/${kind}?${param}=${encodeURIComponent(slug)}`);
    res.status(302).end();
  }
}
