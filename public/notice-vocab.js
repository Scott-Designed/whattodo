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
const scanFor = l => {
  for(const s of SUB_BY_LEN){                 /* longest first: Geelong West beats Geelong */
    const t=s.toLowerCase().replace(/[\u2019']/g,'');
    if(new RegExp('(^|[^a-z])'+rxEsc(t)+'([^a-z]|$)').test(l))
      return GEELONG.has(s) ? 'Geelong' : s;
  }
  return null;
};
/* An address ends with the suburb it is in, so read that chunk before scanning
   the whole string. Longest-first is right within a scan and wrong across one:
   "561 Cape Otway Road, Moriac" matched Cape Otway, because a road named after
   a town is a longer string than the town you are actually standing in — and
   that put the Moriac General Store on a page 90km away. Found 26 Aug 2026 in
   the first big research pass, which added three rows with the same shape.

   The whole-string scan stays as the fallback, and has to: it is what reads
   "Torquay Foreshore" and "Anywhere along the Surf Coast Walk", and what
   rescues an address whose last chunk is a postcode or "Victoria". */
function suburbOf(loc){
  const l=String(loc||'').toLowerCase().replace(/[\u2019']/g,'');
  if(!l) return null;
  if(AT_HOME.test(l)) return 'Home';
  if(IN_CAR.test(l))  return 'Car';
  if(l.includes(',')){
    const tail = scanFor(l.split(',').pop().trim());
    if(tail) return tail;
  }
  const whole = scanFor(l);
  if(whole) return whole;
  if(NO_FIXED.test(l)) return 'Surf Coast wide';
  return null;
}
/* the three that are not towns lead the list; the towns follow, alphabetically */
const PLACE_ORDER=['Surf Coast wide','Home','Car',
  ...SUBURBS.filter(x=>!GEELONG.has(x)||x==='Geelong').sort()];

/* A listing carries a list of types and `type` is the first of them — the one the
   row prints and draws an icon for. Two older shapes still reach here with a bare
   string: the built-in copy baked into this file, and anything a visitor adds. So
   read the list through this rather than touching `.types` directly. */
const typesOf = i => i.types?.length ? i.types : (i.type ? [i.type] : []);

/* ── the nine groups ──
   Every one of the 43 types belongs to exactly one group, so a new type has one
   obvious home. This replaced two things at once: the 13 themes, which were a
   second vocabulary keyed on the same word and had gone stale the moment the
   types were renamed, and the 15 verbs, which asked what you felt like doing
   and could only answer from the type anyway.

   The group counts still do not sum to the number of listings, and that is the
   types being a list rather than a fault here: 69 rows carry types from two
   groups. Bells Beach Surf Film Festival is festival, surfing and cinema, so it
   is in The music, The ocean and The arts & culture — which is the whole reason
   any of this was done. 494 across nine groups, 419 rows.

   The line between `landscape` and `outdoors` is being in it versus doing
   something in it. That is why a walk and a glow-worm hunt sit apart from a
   mountain bike trail, and it is the one call here worth arguing with. */
const GROUPS=[['ocean','The ocean'],['landscape','The landscape'],['outdoors','The outdoors'],
  ['hospitality','The hospitality'],['produce','The produce'],['arts','The arts & culture'],
  ['music','The music'],['community','The community'],['home','The home']];

const GROUP_OF={
  beach:'ocean', surfing:'ocean', swimming:'ocean', paddling:'ocean', water:'ocean',

  walk:'landscape', nature:'landscape', night:'landscape',

  running:'outdoors', cycling:'outdoors', 'mountain biking':'outdoors',
  skatepark:'outdoors', 'rock climbing':'outdoors', golf:'outdoors',
  'parks & playgrounds':'outdoors', 'camping ground':'outdoors',

  cafe:'hospitality', bakery:'hospitality', restaurant:'hospitality',
  bar:'hospitality', pub:'hospitality', winery:'hospitality', brewery:'hospitality',

  market:'produce', produce:'produce', 'farm life':'produce', shop:'produce',
  nursery:'produce',

  arts:'arts', 'art gallery':'arts', theatre:'arts', museum:'arts',
  cinema:'arts', cultural:'arts',

  gig:'music', party:'music', comedy:'music', festival:'music',

  community:'community', volunteering:'community', workshop:'community',
  reading:'community',

  'at-home':'home'};

/* A row is in every group its types are in — usually one, sometimes two: a film
   festival is music and arts, a glow-worm walk is landscape only because all
   three of its types live there. The first is what tints the row. */
const groupsOf = i => [...new Set(typesOf(i).map(t=>GROUP_OF[t]).filter(Boolean))];

/* The three entries in PLACE_ORDER that are not towns get a line saying so,
   because "Home" and "Surf Coast wide" are honest answers to Where and are not
   places you drive to. Here rather than in place.html because api/subject.mjs
   puts the same sentence in the page's description — and two copies of a
   sentence is how prose drifts. */
const NOT_A_TOWN = {
  'Home':'Things you can do without leaving the house.',
  'Car':'Things to do on the way, from the passenger seat.',
  'Surf Coast wide':'Things with no single address — they move, or they are the whole coast.'};

/* ── slugs, for the URL ──
   A suburb or a type as a URL segment, derived from the word itself rather
   than stored next to it. A slug column would be a second copy of the
   vocabulary and would go stale the first time a type was renamed — the
   failure this file exists to prevent. Checked 26 Aug 2026: no two of the 50
   places and no two of the 43 types slug the same.

   unslug() is the way back, and it compares slugs rather than tidying the
   segment, so "surf-coast-wide" finds "Surf Coast wide" and "mountain-biking"
   finds "mountain biking" without either being written down twice.

   The nine group names all slug to "the-…" and no type does, so a group page
   could share this namespace later without colliding. */
const slugify = s => String(s == null ? '' : s).toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const unslug = (seg, list) => list.find(x => slugify(x) === slugify(seg)) || null;

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

/* The 43 types, split by whether you are adding a place you go to or a thing
   that is on. This is NOT the database's `types.band` — that groups by subject
   now (the nine GROUPS above). It is only the Add form's two lists.

   Nine types can honestly be either: an exhibition is on for a fortnight, a
   gallery is open all year. They sit under events, because someone filling in
   this form with a date in mind is the case that needs the shorter list. */
const EVENT_TYPES=['gig','comedy','party','reading','festival','workshop',
  'community','market','arts'];
const PLACE_TYPES=['beach','surfing','swimming','paddling','water',
  'walk','running','cycling','mountain biking','skatepark','rock climbing','golf','nature',
  'parks & playgrounds','camping ground','night','at-home',
  'cafe','bakery','restaurant','bar','pub','winery','brewery',
  'shop','produce','farm life','nursery',
  'art gallery','theatre','museum','cinema','cultural','volunteering'];

/* A type is stored lower-case and hyphenated because the database checks it
   against a vocabulary. That is the right shape for a column and the wrong one
   for a heading, so a page that puts a type in an <h1> asks here instead of
   title-casing the raw value and printing "At-home". Plural, because a type
   page is a list of things rather than one of them. */
const TYPE_PLURAL={
  beach:'Beaches', surfing:'Surfing', swimming:'Swimming', paddling:'Paddling',
  water:'On the water', walk:'Walks', running:'Running', cycling:'Cycling',
  'mountain biking':'Mountain biking', skatepark:'Skateparks',
  'rock climbing':'Rock climbing', golf:'Golf', nature:'Nature',
  'parks & playgrounds':'Parks & playgrounds', 'camping ground':'Camping',
  night:'After dark', 'at-home':'At home',
  cafe:'Caf\u00e9s', bakery:'Bakeries', restaurant:'Restaurants', bar:'Bars',
  pub:'Pubs', winery:'Wineries', brewery:'Breweries',
  market:'Markets', shop:'Shops', produce:'Produce', 'farm life':'Farm life',
  nursery:'Nurseries',
  arts:'Arts', 'art gallery':'Galleries', theatre:'Theatres', museum:'Museums',
  cinema:'Cinemas', cultural:'Wadawurrung Country',
  gig:'Gigs', comedy:'Comedy', party:'Parties', reading:'Reading',
  festival:'Festivals', workshop:'Workshops', community:'Community',
  volunteering:'Volunteering'};
const typeLabel = t => TYPE_PLURAL[t] || (t||'').replace(/-/g,' ')
  .replace(/^./,c=>c.toUpperCase());
