// POST /api/enrich — Claude drafts the missing fields for a listing.
// It NEVER writes to the database. It returns a proposal; the person who
// asked for it edits and submits, and that submission is the write.
//
// Needs ANTHROPIC_API_KEY in the Vercel project's environment.
// Optional: ENRICH_MODEL (default claude-sonnet-5).

const TYPES_PLACE = ['beach','walk','surf','water','bike track','skatepark','sport','park',
  'playground','nature','museum','cafe','cinema','camping','at-home','night',
  'volunteering','nursery','cultural'];
const TYPES_EVENT = ['gig','festival','market','workshop','community','sport-event'];
const CONDITIONS = ['any-weather','low-tide','high-tide','new-moon','full-moon','clear-sky',
  'calm-sea','warm','low-wind','dry-trails','dry-ground','no-fire-ban','geomagnetic-storm',
  'good-in-rain'];

const SYSTEM = `You draft entries for a community activity database centred on Jan Juc,
Victoria, Australia (postcode 3228, Surf Coast). Families use it to decide what to do.

Search the web before answering. Cross-reference at least two sources for any factual claim.

HARD RULES — these matter more than completeness:
- Never invent a URL. Use a real site you actually found, or null. Never invent a
  maps.app.goo.gl short link; they only come from a real device.
- Never state a date as fact without a source. If a date is a pattern rather than an
  announcement ("first Sunday of the month", "end of March every year"), say so in
  reasoning and set date_confidence accordingly.
- Return null for anything you could not establish. A null is useful; a guess is damage.
- Distances are approximate DRIVING distances from Jan Juc, not straight-line.
- Descriptions carry real local detail — parking, tides, what it's actually like — not
  tourist brochure copy. Two or three sentences.

VOCABULARIES — use these exact strings, nothing else:
  place types: ${TYPES_PLACE.join(', ')}
  event types: ${TYPES_EVENT.join(', ')}
  conditions:  ${CONDITIONS.join(', ')}

Conditions describe what the weather/tide/moon must be for this to be worth doing.
"dry-ground" means not raining right now (skateparks, markets, picnics). "dry-trails"
means no rain for 48 hours (MTB, unsealed tracks). "good-in-rain" is the opposite — a
positive signal for indoor things. Don't reach for "any-weather" unless conditions
genuinely make no difference.

Geography: in scope is the Surf Coast, Great Ocean Road, Otways, Geelong, Bellarine and
the You Yangs, roughly within 100km. Out of scope: Phillip Island, Mornington Peninsula,
outer Melbourne. If the subject is out of scope, say so in reasoning.

Reply with ONE JSON object and nothing else.`;

function schemaFor(kind){
  const common = `"name": string, "type": one of the ${kind} types, "location": string
  (suburb or venue), "km": number or null, "cost": "Free"|"Cheap"|"Moderate"|"Splurge",
  "description": string, "url": string or null, "conditions": array of condition strings,
  "reasoning": string (what you found and what you could not confirm),
  "sources": array of {title, url}`;
  return kind === 'event'
    ? `{ ${common}, "starts_on": "YYYY-MM-DD" or null, "time_text": string or null,
         "recurrence": "none"|"weekly"|"fortnightly"|"monthly"|"annual",
         "date_confidence": "high"|"medium"|"low" }`
    : `{ ${common}, "duration": "< 1hr"|"half-day"|"full-day"|"overnight",
         "daypart": "day"|"night"|"both" }`;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({error:'POST only'});
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(501).json({error:'not_configured',
    message:'Set ANTHROPIC_API_KEY in the Vercel project to enable this.'});

  const { kind = 'place', name = '', location = '', hint = '' } = req.body || {};
  if (!name.trim()) return res.status(400).json({error:'name_required'});
  if (!['place','event'].includes(kind)) return res.status(400).json({error:'bad_kind'});

  const ask = `Draft a ${kind === 'event' ? 'community EVENT' : 'PLACE or ACTIVITY'} entry.

What the person typed:
  name: ${name}
  where: ${location || '(not given)'}
  ${hint ? 'extra: ' + hint : ''}

Today is ${new Date().toISOString().slice(0,10)}.
Return exactly this shape:
${schemaFor(kind)}`;

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {'x-api-key': key, 'anthropic-version': '2023-06-01',
                'content-type': 'application/json'},
      body: JSON.stringify({
        model: process.env.ENRICH_MODEL || 'claude-sonnet-5',
        max_tokens: 2000,
        system: SYSTEM,
        tools: [{type:'web_search_20250305', name:'web_search', max_uses: 6,
                 user_location:{type:'approximate', city:'Torquay', region:'Victoria',
                                country:'AU', timezone:'Australia/Melbourne'}}],
        messages: [{role:'user', content: ask}],
      }),
    });
    if (!r.ok) {
      const body = await r.text();
      return res.status(502).json({error:'upstream', status:r.status, detail: body.slice(0,300)});
    }
    const data = await r.json();

    // Collect the assistant's text, and the citations the search actually returned.
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('');
    const cited = [];
    for (const b of data.content || []) {
      for (const c of b.citations || []) {
        if (c.url && !cited.some(x => x.url === c.url)) cited.push({title: c.title, url: c.url});
      }
    }
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) return res.status(502).json({error:'no_json', detail:text.slice(0,300)});

    let proposal;
    try { proposal = JSON.parse(m[0]); }
    catch { return res.status(502).json({error:'bad_json', detail:m[0].slice(0,300)}); }

    // Refuse anything outside the vocabularies rather than letting it reach the database.
    const validTypes = kind === 'event' ? TYPES_EVENT : TYPES_PLACE;
    if (proposal.type && !validTypes.includes(proposal.type)) proposal.type = null;
    if (Array.isArray(proposal.conditions))
      proposal.conditions = proposal.conditions.filter(c => CONDITIONS.includes(c));
    // A URL that no source backs up is exactly the failure this project has had before.
    if (proposal.url && !/^https?:\/\//.test(proposal.url)) proposal.url = null;
    if (/maps\.app\.goo\.gl/.test(proposal.url || '')) proposal.url = null;

    const sources = (proposal.sources || []).concat(cited)
      .filter((s,i,a) => s && s.url && a.findIndex(x => x.url === s.url) === i)
      .slice(0, 8);

    return res.status(200).json({proposal, sources, searched: cited.length > 0});
  } catch (e) {
    return res.status(500).json({error:'failed', detail:String(e).slice(0,200)});
  }
}
