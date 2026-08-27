/* ══ notice-data.js ════════════════════════════════════════════════════
   The connection, and the one place the `listings` view is turned into the
   shape a page renders.

   Lifted out of index.html on 26 Aug 2026, when the suburb and type pages
   arrived and needed the same rows. `fromRow` in particular has to be shared:
   it is where `types` becomes a list, where a row's groups are worked out and
   where the view's two old column names are still absorbed. A second copy of
   that would drift, and a page quietly disagreeing with the board about what a
   row says is the failure this project keeps paying for.

   A classic script — everything lands on `window`. Load it AFTER
   notice-vocab.js (it reads GROUP_OF) and BEFORE the page's own script.
   scripts/configure.py writes the two keys below.
   ═══════════════════════════════════════════════════════════════════════ */

/* ══ backend ═══════════════════════════════════════════════════════════════
   Paste your Supabase project URL and anon key here (scripts/configure.py
   does it for you). The anon key is meant to be public — Row Level Security
   in supabase/schema.sql is what actually protects the data: anyone may read
   and add, nobody may edit or delete without the service key.
   Leave blank and the page runs from the baked-in copy below, read-only. */
const SUPABASE_URL = "https://xpnsrtylcqjcoqitskwy.supabase.co";
const SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwbnNydHlsY3FqY29xaXRza3d5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODczNzI1MzcsImV4cCI6MjEwMjk0ODUzN30.Jf2hG4g55IZamv_5OECQK5rBz6o_a4lZRo3Mthp62KE";
const REMOTE = /^https?:\/\/[^\s]+$/.test(SUPABASE_URL) && !SUPABASE_URL.includes('__SUPABASE')
               && SUPABASE_ANON.length > 10 && !SUPABASE_ANON.includes('__SUPABASE');
const sbHeaders = () => ({apikey:SUPABASE_ANON, Authorization:'Bearer '+SUPABASE_ANON,
                          'Content-Type':'application/json'});
let REMOTE_OK = false;

/* listings view -> the shape this page renders */
function fromRow(r){
  const cond = r.conditions || [];
  /* `types` while the view still called it `type`. A row that is a festival and a
     surf thing and a film thing says so; the first one is what the row prints. */
  const types = r.types?.length ? r.types : (r.type ? [r.type] : []);
  const groups = [...new Set(types.map(t=>GROUP_OF[t]).filter(Boolean))];
  return {
    id:r.id, key:r.key, ev:r.is_event, name:r.name, types, type:types[0]??null, loc:r.location,
    /* `venue` while the view still called it that; the table is `places` now */
    place:r.place ?? r.venue, placeKind:r.place_kind,
    /* what sort of thing this is — spot, venue, shop, group, maker,
       happening, idea — and the family it belongs to. Null on a row
       nobody has classified, which is a question, not a default. */
    kind:r.kind ?? null, family:r.family ?? null,
    km:r.km===null?null:Number(r.km), cost:r.cost, ages:r.ages||[], desc:r.description,
    url:r.url, info:r.info_url, ticket:r.ticket_url, cond, rating:r.rating,
    notes:r.notes, dur:r.duration, season:r.season||[], dbDaypart:r.daypart,
    date:r.starts_on, time:r.time_text, recur:r.recurrence, conf:r.date_confidence,
    lat:r.lat, lng:r.lng, verified:r.verified, by:r.added_by, created:r.created_at,
    added: r.verified===false, groups,
  };
}
async function loadRemote(){
  if(!REMOTE) return null;
  try{
    const r=await fetch(SUPABASE_URL+'/rest/v1/listings?select=*',{headers:sbHeaders()});
    if(!r.ok) throw new Error(r.status);
    const rows=await r.json();
    if(!Array.isArray(rows)||!rows.length) throw new Error('empty');
    REMOTE_OK=true;
    return rows.map(fromRow);
  }catch(e){ REMOTE_OK=false; return null; }
}
