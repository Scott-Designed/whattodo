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
  'Waurn Ponds','Norlane','Corio','Fyansford','Ceres','Highton','Newcomb']);
const SUBURBS=['Aireys Inlet','Anglesea','Apollo Bay','Armstrong Creek','Barwon Heads',
 'Bannockburn','Beech Forest','Bellarine','Bellbrae','Bells Beach','Belmont',
 'Birregurra','Breamlea',
 'Cape Otway','Ceres','Colac','Connewarre','Corio','Cumberland River','Curlewis',
 'Deans Marsh',
 'Drysdale','Eastern View','Fairhaven','Forrest','Freshwater Creek','Fyansford','Geelong',
 'Geelong West','Grovedale','Highton','Indented Head','Inverleigh','Jan Juc',
 'Kennett River','Lara',
 'Lavers Hill','Leopold','Little River','Lorne','Moggs Creek','Moriac','Mt Duneed','Norlane',
 'Newcomb','Ocean Grove','Point Addis','Point Lonsdale','Portarlington','Queenscliff',
 'Skenes Creek',
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
  /* `Mt Duneed` is how SUBURBS spells it and `Mount Duneed` is how the
     businesses there spell it, so the literal scan missed every address a
     research pass would actually write. Normalised rather than added as a
     second SUBURBS entry, which would put one town in the Place menu twice. */
  const l=String(loc||'').toLowerCase().replace(/[\u2019']/g,'')
                         .replace(/\bmount\b/g,'mt');
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
/* The town to PRINT for a location. suburbOf answers "which town is this in",
   which the filters want; this answers "what should the Where column say".

   A researched venue writes `location` as a full street address ending in the
   suburb — the documented convention — so printing it raw put "1A Harding
   Street, Portarlington" into a column two words wide. Only a location with a
   comma is collapsed, and only to a town suburbOf actually recognises, so a
   description keeps its own words: "Anywhere outdoors" is a better answer than
   'Surf Coast wide'.

   It lives here rather than in a page because three pages print a Where column
   and this project has already paid for the same rule existing in more than one
   copy. Keep it DOM-free — api/subject.mjs evaluates this file in a sandbox. */
function townOf(loc){
  var raw = String(loc == null ? '' : loc).trim();
  if(raw.indexOf(',') < 0) return raw;
  var t = suburbOf(raw);
  return (t && ['Home','Car','Surf Coast wide'].indexOf(t) < 0) ? t : raw;
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

  market:'produce', produce:'produce', 'farm life':'produce',
  nursery:'produce',

  arts:'arts', 'art gallery':'arts', theatre:'arts', museum:'arts',
  cinema:'arts', cultural:'arts',

  music:'music', party:'music', comedy:'music', festival:'music',

  community:'community', volunteering:'community', workshop:'community',
  reading:'community', kids:'community',

  'at-home':'home'};

/* A row is in every group its types are in — usually one, sometimes two: a film
   festival is music and arts, a glow-worm walk is landscape only because all
   three of its types live there. The first is what tints the row. */
/* Which icon a type gets. Only the types listed here draw one — the rest keep an
   empty slot, so this can be filled in a type at a time. Values are symbol ids
   without the `i-` prefix. */
const ICON_OF={
  'art gallery':'frame',
  arts:'palette',
  'at-home':'house',
  bakery:'croissant',
  bar:'martini',
  beach:'parasol',
  brewery:'hop',
  cafe:'coffee',
  'camping ground':'tent',
  cinema:'film',
  comedy:'laugh',
  community:'users',
  cultural:'shell',
  cycling:'bike',
  'farm life':'tractor',
  festival:'ferris-wheel',
  music:'guitar',
  golf:'flag-triangle-right',
  kids:'blocks',
  market:'store',
  'mountain biking':'bike',
  museum:'landmark',
  nature:'leaf',
  night:'moon-star',
  nursery:'sprout',
  paddling:'sailboat',
  'parks & playgrounds':'trees',
  party:'party-popper',
  produce:'apple',
  pub:'beer',
  reading:'book-open',
  restaurant:'utensils',
  'rock climbing':'mountain',
  running:'sport-shoe',
  skatepark:'hand-metal',
  surfing:'waves',
  swimming:'waves-ladder',
  theatre:'drama',
  volunteering:'heart-handshake',
  walk:'footprints',
  water:'droplet',
  winery:'wine',
  workshop:'hammer'};

/* skatepark is `hand-metal`, chosen by Scott: Lucide has no skateboard, and the
   thrown horns is what the culture actually signs with. Every type has an icon
   now, so the empty slot the layout keeps is unused — keep it anyway, it is
   what stops a new type shifting every name in the list. */

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

/* ── the hours a listing runs, read out of its free-text time ──
   `time_text` is what the organiser published, so it is prose and not a field.
   618 of the 683 events carry a plain range ("10:30am–11:15am"); the rest say
   things like "Plates from 9am, race 10am", "Sept–Oct holidays" or "Sat & Sun".
   This reads what it can and returns null for the rest. An ON NOW badge drawn
   on hours that were inferred is the fabricated-data failure this project has
   already paid for twice, so nothing here fills a gap in.

   `to` is null when only a start was published, and that is NOT an end. Sorting
   may use a start on its own; the badge may not, because a gig that started at
   8pm is not evidence that it is still going at midnight.

   Two things the data actually demands:
   - the opening time often carries no am/pm and borrows the closing one —
     "2–5pm" is the afternoon, not two in the morning.
   - a full stop is a colon here: "7.30pm" and "8.30am" are both in the table. */
const T_DASH  = '(?:–|—|-|to)';
const T_CLOCK = '(\\d{1,2})(?:[:.](\\d{2}))?\\s*(am|pm)?';
const T_RANGE = new RegExp(T_CLOCK + '\\s*' + T_DASH + '\\s*' + T_CLOCK, 'i');
const T_ONE   = new RegExp('(\\d{1,2})(?:[:.](\\d{2}))?\\s*(am|pm)', 'i');
/* No meridiem, no clock time. "34km 8.30am from Queenscliff" holds three
   numbers and one of them is the hour; requiring am/pm is what tells them
   apart without a list of units to exclude. */
const t_clock = (h, m, ap) => {
  if(!ap) return null;
  return (+h % 12) + (/pm/i.test(ap) ? 12 : 0) + (m ? +m/60 : 0);
};
function timeSpan(t, sunset){
  const s = String(t ?? '').trim()
    .replace(/\bmidnight\b/ig, '12am').replace(/\b(noon|midday)\b/ig, '12pm');
  if(!s) return null;
  if(/\ball[- ]day\b/i.test(s)) return {from:0, to:24};

  const r = T_RANGE.exec(s);
  if(r){
    const from = t_clock(r[1], r[2], r[3] || r[6]);   /* borrow forwards only */
    const to   = t_clock(r[4], r[5], r[6]);
    if(from!=null && to!=null) return {from, to: to<from ? to+24 : to};
  }
  const one = T_ONE.exec(s);
  if(one) return {from: t_clock(one[1], one[2], one[3]), to:null};

  /* the words, which a few rows use on their own — "from sunset", "sunset" */
  if(/sunset|dusk|after dark|evening/i.test(s))
    return Number.isFinite(sunset) ? {from:sunset, to:null} : null;
  if(/dawn|sunrise/i.test(s)) return {from:6.5, to:null};
  return null;
}

/* The board is about one coastline, so "now" is Melbourne's now wherever the
   reader is sitting. The date and the hour have to come off the same clock, or
   a reader in London gets today's Surf Coast events matched against their own
   afternoon. Note todayISO above is deliberately the VIEWER's day — it answers
   a different question (which dates to show), and this one answers "is this on
   at this minute", so it does its own reading. */
function melbourneNow(){
  const p = new Intl.DateTimeFormat('en-CA', {timeZone:'Australia/Melbourne',
      year:'numeric', month:'2-digit', day:'2-digit',
      hour:'2-digit', minute:'2-digit', hour12:false})
    .formatToParts(new Date()).reduce((o,x)=>(o[x.type]=x.value, o), {});
  return {iso:`${p.year}-${p.month}-${p.day}`, hour:(+p.hour % 24) + (+p.minute)/60};
}

/* Is this happening at this minute? Only ever true where the published time
   gives BOTH ends. Three things it therefore cannot answer, all deliberately:
   a start with no end, a listing with no time at all, and a festival running
   across days — `listings` carries no ends_on, so 19–20 Sep is one date here. */
function onNow(i, now, sunset){
  if(!i || !i.ev || !i.date || !now) return false;
  if(nextDate(i) !== now.iso) return false;
  const sp = timeSpan(i.time, sunset);
  if(!sp || sp.to == null) return false;
  return now.hour >= sp.from && now.hour < sp.to;
}

/* The 43 types, split by whether you are adding a place you go to or a thing
   that is on. This is NOT the database's `types.band` — that groups by subject
   now (the nine GROUPS above). It is only the Add form's two lists.

   Nine types can honestly be either: an exhibition is on for a fortnight, a
   gallery is open all year. They sit under events, because someone filling in
   this form with a date in mind is the case that needs the shorter list. */
const EVENT_TYPES=['music','comedy','party','reading','festival','workshop',
  'community','market','arts','kids'];
const PLACE_TYPES=['beach','surfing','swimming','paddling','water',
  'walk','running','cycling','mountain biking','skatepark','rock climbing','golf','nature',
  'parks & playgrounds','camping ground','night','at-home',
  'cafe','bakery','restaurant','bar','pub','winery','brewery',
  'produce','farm life','nursery',
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
  night:'After dark', 'at-home':'At home', kids:'For kids',
  cafe:'Caf\u00e9s', bakery:'Bakeries', restaurant:'Restaurants', bar:'Bars',
  pub:'Pubs', winery:'Wineries', brewery:'Breweries',
  market:'Markets', produce:'Produce', 'farm life':'Farm life',
  nursery:'Nurseries',
  arts:'Arts', 'art gallery':'Galleries', theatre:'Theatres', museum:'Museums',
  cinema:'Cinemas', cultural:'Wadawurrung Country',
  music:'Music', comedy:'Comedy', party:'Parties', reading:'Reading',
  festival:'Festivals', workshop:'Workshops', community:'Community',
  volunteering:'Volunteering'};
const typeLabel = t => TYPE_PLURAL[t] || (t||'').replace(/-/g,' ')
  .replace(/^./,c=>c.toUpperCase());

/* ══ one thing, several places ══════════════════════════════════════════════
   Geelong Regional Libraries publish Toddler Time as one row per branch, so a
   Saturday morning on the board was five identical lines differing only in the
   branch name. 142 of the 686 events are in that shape today, across 56
   clusters, and every one of them is the library. The board draws such a set
   once and says where underneath.

   Three things this is careful about:

   - The key is the EFFECTIVE date. `nextDate` rolls a weekly event forward, so
     grouping on the stored `starts_on` would split a standing Tuesday cluster
     the week it rolls.
   - Only DATED things cluster. Two cafes with the same name are two cafes; two
     events with one name, one date and one published time are one thing in
     several rooms.
   - Grouping happens AFTER the filter, never before. Filter to Torquay and a
     five-branch cluster is a single Torquay row again, which is the honest
     answer and falls out for free.

   DOM-free, like the rest of this file — api/subject.mjs evaluates it in a
   node:vm sandbox. ════════════════════════════════════════════════════════ */
function clusterKey(i){
  if(!i.ev || !i.date) return null;
  return [String(i.name||'').trim().toLowerCase(), nextDate(i),
          String(i.time||'').trim().toLowerCase()].join('\u001f');
}
/* An ordered list of groups, each group an array. A cluster takes the position
   of its first member, so whatever the sort said still holds. */
function clusterRows(list){
  const at=new Map(), out=[];
  for(const i of list){
    const k=clusterKey(i), seen=k?at.get(k):null;
    if(seen){ seen.push(i); continue }
    const cell=[i]; out.push(cell); if(k) at.set(k,cell);
  }
  return out;
}

/* What a set of place names have in common, if anything. Five branches share
   the word "Library" and nothing else, so the row can say what they are; two
   unrelated venues share nothing and the row says "2 places" instead. Never a
   word only some of them carry. */
const PLACE_STOP=new Set(['the','and','for','with']);
const placeWords = n => String(n||'').toLowerCase().replace(/[()]/g,' ')
  .split(/[^a-z']+/).filter(w=>w.length>2 && !PLACE_STOP.has(w));
function commonPlaceWord(names){
  const bag=names.map(placeWords);
  if(bag.length<2 || bag.some(w=>!w.length)) return '';
  const shared=[...new Set(bag[0].filter(w=>bag.every(ws=>ws.includes(w))))];
  if(!shared.length) return '';
  /* More than one word can be shared — every Geelong branch carries "geelong"
     as well as "library". An organisation's own noun is the one that TRAILS a
     branch name, so score each by how far through the names it falls. */
  const score=w=>bag.reduce((s,ws)=>s+ws.indexOf(w)/Math.max(ws.length-1,1),0);
  return shared.sort((a,b)=>score(b)-score(a))[0];
}
const pluralWord = w => /y$/.test(w) ? w.slice(0,-1)+'ies'
                      : /(s|x|ch|sh)$/.test(w) ? w+'es' : w+'s';
const placeNames = g => [...new Set(g.map(i=>String(i.place||'').trim()).filter(Boolean))];
/* "5 libraries", or "5 places" when the names have nothing in common. */
function placesLabel(g){
  const names=placeNames(g), w=commonPlaceWord(names);
  return (names.length||g.length)+' '+(w?pluralWord(w):'places');
}
/* The branch, without the word the row has already said. Only a TRAILING match
   is cut — taking a word out of the middle of a name makes a phrase nobody
   wrote, so "Geelong Library and Heritage Centre (The Dome)" cannot lose its
   "Library" that way. What it can do is fall back on the short name the place
   publishes for itself in brackets: it is called The Dome, by everyone. */
function shortPlace(name, word){
  const full=String(name||'');
  if(!word) return full;
  const esc=w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const cut=full.replace(new RegExp('\\s+'+esc(word)+'\\s*$','i'),'').trim();
  if(cut && !new RegExp('\\b'+esc(word)+'\\b','i').test(cut)) return cut;
  const brack=full.match(/\(([^)]{2,30})\)\s*$/);
  return brack ? brack[1].trim() : (cut || full);
}
