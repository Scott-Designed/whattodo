/* ══ notice-vocab.js ═══════════════════════════════════════════════════
   The words this site sorts by, in one file because more than one page now
   reads them.

   This was lifted out of index.html on 26 Aug 2026, when the suburb and type
   pages arrived. It is deliberately a lift and not a copy: a suburb page that
   decided for itself what counts as "Torquay" would disagree with the board
   sooner or later, and two live copies of one fact is exactly how this project
   put the same festival on two different dates.

   A classic script, no module, no build step — everything here lands on
   `window` and the page's own script can just use it. Load it BEFORE the page
   script, or the const declarations will not exist yet.
   ═══════════════════════════════════════════════════════════════════════ */

/* Where, as a place you could name to someone. `location` is free text and holds
   106 distinct strings — bare suburbs, but also street addresses, regions, routes
   and "Anywhere with a hose" — so the answer is read out of the string rather
   than being the string.

   Four groups, in this order, because the order is what makes them work:
   Home first (or "Anywhere - your backyard" lands in the Anywhere bucket), then
   Car, then a real suburb, then everything left that means "no particular
   place". A Geelong suburb answers as Geelong: nobody planning a Saturday
   distinguishes Grovedale from Waurn Ponds, and eleven suburbs holding one
   listing each is a longer menu that finds less. */
const GEELONG=new Set(['Geelong','Geelong West','South Geelong','Belmont','Grovedale',
  'Waurn Ponds','Norlane','Corio','Fyansford','Ceres']);
const SUBURBS=['Aireys Inlet','Anglesea','Apollo Bay','Armstrong Creek','Barwon Heads',
 'Beech Forest','Bellarine','Bellbrae','Bells Beach','Belmont','Birregurra','Breamlea',
 'Cape Otway','Ceres','Connewarre','Corio','Cumberland River','Curlewis','Deans Marsh',
 'Drysdale','Eastern View','Fairhaven','Forrest','Freshwater Creek','Fyansford','Geelong',
 'Geelong West','Grovedale','Indented Head','Inverleigh','Jan Juc','Kennett River','Lara',
 'Lavers Hill','Leopold','Little River','Lorne','Moggs Creek','Moriac','Mt Duneed','Norlane',
 'Ocean Grove','Point Addis','Point Lonsdale','Portarlington','Queenscliff','Skenes Creek',
 'South Geelong','St Leonards','Torquay','Wallington','Waurn Ponds','Werribee',
 'Winchelsea','Wye River','You Yangs'];
const SUB_BY_LEN=[...SUBURBS].sort((a,b)=>b.length-a.length);
const rxEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const AT_HOME=/^home\b|backyard|neighbourhood/;
const IN_CAR=/\bin the car\b/;
const NO_FIXED=/anywhere|any beach|surf coast|bellarine wide/;
function suburbOf(loc){
  const l=String(loc||'').toLowerCase().replace(/[\u2019']/g,'');
  if(!l) return null;
  if(AT_HOME.test(l)) return 'Home';
  if(IN_CAR.test(l))  return 'Car';
  for(const s of SUB_BY_LEN){                 /* longest first: Geelong West beats Geelong */
    const t=s.toLowerCase().replace(/[\u2019']/g,'');
    if(new RegExp('(^|[^a-z])'+rxEsc(t)+'([^a-z]|$)').test(l))
      return GEELONG.has(s) ? 'Geelong' : s;
  }
  if(NO_FIXED.test(l)) return 'Surf Coast wide';
  return null;
}
/* the three that are not towns lead the list; the towns follow, alphabetically */
const PLACE_ORDER=['Surf Coast wide','Home','Car',
  ...SUBURBS.filter(x=>!GEELONG.has(x)||x==='Geelong').sort()];

const DRINK_KINDS=new Set(['pub','bar','brewery','winery','distillery','cidery']);
/* A listing carries a list of types and `type` is the first of them — the one the
   row prints and draws an icon for. Two older shapes still reach here with a bare
   string: the built-in copy baked into this file, and anything a visitor adds. So
   read the list through this rather than touching `.types` directly. */
const typesOf = i => i.types?.length ? i.types : (i.type ? [i.type] : []);

const THEME_OF={beach:['beach'],surf:['beach'],water:['beach'],walk:['walks'],park:['walks'],
  skatepark:['wheels'],'bike track':['wheels'],nature:['wildlife'],nursery:['wildlife'],
  cafe:['eat'],shop:['eat'],market:['eat','whatson'],cultural:['culture'],museum:['culture'],cinema:['culture'],
  night:['dark'],camping:['camp'],volunteering:['involved'],community:['involved','whatson'],
  workshop:['involved','whatson'],'at-home':['home'],playground:['play'],sport:['play'],
  gig:['whatson'],festival:['whatson'],'sport-event':['whatson']};

/* ── when an event next happens ──
   Shared rather than copied because this function has already been wrong once,
   in a way only a test caught: parsing the stored date as local time and
   formatting it with toISOString() shifts it back a day at +10, so every rolled
   Saturday gig landed on a Friday. One copy, one fix. */
const todayISO=(()=>{const d=new Date();return new Date(d.getTime()-d.getTimezoneOffset()*6e4).toISOString().slice(0,10)})();
const daysAway=ds=>ds?Math.round((new Date(ds+'T00:00:00')-new Date(todayISO+'T00:00:00'))/864e5):null;
/* A weekly or fortnightly event whose stored date has passed has not finished —
   it happens again on the same weekday, seven or fourteen days on. Roll it forward
   so it keeps showing, otherwise a standing Saturday gig silently ages out of the
   site the Sunday after it was entered.
   Monthly and annual are deliberately NOT rolled. Adding a month or a year moves
   the weekday, so "third Sunday" would quietly become "the 20th" — a date nobody
   published, which is exactly how this database got a festival wrong before. Those
   need a person to set the next starts_on. */
function nextDate(i){
  if(!i || !i.ev || !i.date) return i && i.date || null;
  const step = i.recur==='weekly' ? 7 : i.recur==='fortnightly' ? 14 : 0;
  const d = daysAway(i.date);
  if(d===null || d>=0 || !step) return i.date;
  const hops = Math.ceil(-d/step);
  /* Parse and format in UTC. Parsing as local and formatting with toISOString
     shifts the result back a day in +10, so every rolled gig landed on Friday. */
  return new Date(Date.parse(i.date+'T00:00:00Z')+hops*step*864e5)
           .toISOString().slice(0,10);
}

/* The 26 types, split the way the database's `types.band` splits them: a place
   you go to, or a thing that is on. The Add form offers these two lists, and
   the Type menu groups by the same two, so they live here rather than in either
   page. Adding a type still means the four places CLAUDE.md lists — this is one
   of them moving house, not a fifth. */
const PLACE_TYPES=['beach','walk','surf','water','bike track','skatepark','sport','park','playground',
  'nature','museum','cafe','cinema','camping','at-home','night','volunteering','nursery','cultural'];
const EVENT_TYPES=['gig','festival','market','workshop','community','sport-event'];

/* A type is stored lower-case and hyphenated because the database checks it
   against a vocabulary. That is the right shape for a column and the wrong one
   for a heading, so a page that puts a type in an <h1> asks here instead of
   title-casing the raw value and printing "Sport-event". Plural, because a type
   page is a list of things rather than one of them. */
const TYPE_PLURAL={
  beach:'Beaches', walk:'Walks', surf:'Surf spots', water:'On the water',
  'bike track':'Bike tracks', skatepark:'Skateparks', sport:'Sport',
  park:'Parks', playground:'Playgrounds', nature:'Nature', museum:'Museums',
  cafe:'Caf\u00e9s', shop:'Shops', cinema:'Cinemas', camping:'Camping',
  'at-home':'At home', night:'After dark', volunteering:'Volunteering',
  nursery:'Nurseries', cultural:'Culture', gig:'Gigs', festival:'Festivals',
  market:'Markets', workshop:'Workshops', community:'Community',
  'sport-event':'Sport events'};
const typeLabel = t => TYPE_PLURAL[t] || (t||'').replace(/-/g,' ')
  .replace(/^./,c=>c.toUpperCase());
