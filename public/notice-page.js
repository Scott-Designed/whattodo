/* ══ notice-page.js ════════════════════════════════════════════════════
   What a Place page and a Type page have in common: getting the rows, and
   drawing one listing.

   These pages read the database and nothing else. index.html ships with a
   baked-in copy of the data so the board is never blank and still renders if
   Supabase is down — that fallback is 160KB of JSON and belongs on the page
   people actually land on. A subject page says plainly that it could not reach
   the database instead, which is honest and costs nothing to ship.
   ═══════════════════════════════════════════════════════════════════════ */
(function(){
  'use strict';

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,
    function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c] }) }

  /* An event with no date is waiting on information, not finished, so it stays.
     One that has been and gone drops out — the same rule the board applies. */
  function current(i){
    if(!i.ev || !i.date) return true;
    var d = daysAway(nextDate(i));
    return d === null || d >= 0;
  }

  async function rows(){
    var all = await loadRemote();
    return all ? all.filter(current) : null;
  }

  /* ── dating an event ──
     nextDate() rolls a weekly or fortnightly event forward to the occurrence
     that has not happened yet, so a standing Saturday gig reads as this
     Saturday rather than as a date last March. */
  var FMT = {weekday:'short', day:'numeric', month:'short'};
  function whenLabel(i){
    if(!i.ev) return '';
    if(!i.date) return 'Date not set';
    var ds = nextDate(i), d = daysAway(ds);
    if(d === 0) return 'Today';
    if(d === 1) return 'Tomorrow';
    /* A weekly event says how often rather than which date. Its name no longer
       carries the recurrence, so this is the only place it is written — the
       board's whenText() says the same thing the same way. */
    if(i.recur === 'weekly')
      return 'Every ' + new Date(ds + 'T00:00:00').toLocaleDateString('en-AU', {weekday:'long'});
    var txt = new Date(ds + 'T00:00:00').toLocaleDateString('en-AU', FMT);
    return d > 0 && d < 7 ? txt : txt + (d > 300 ? ' ' + ds.slice(0,4) : '');
  }

  /* ── one listing ──
     `skip` is the fact the page has already made its subject, said once at the
     top instead of against every row — that being the whole reason these are
     pages rather than the board with a filter on it.

     'suburb' and not 'where': a town page has already said Torquay, but the
     Torquay Hotel is still the thing you need to read. Dropping both leaves a
     gig with nowhere to be.

     More than one fact can already be established — a Type page groups by town,
     so it has said both — hence a list rather than a single value. */
  function row(i, skip){
    var drop = ',' + (skip || '') + ',';
    var off  = function(k){ return drop.indexOf(',' + k + ',') >= 0 };
    var meta = [];
    /* The raw type, lower case, exactly as the board prints it. typeLabel() is
       plural and belongs in a heading — "Gigs" against one gig reads wrong. */
    if(!off('type')) typesOf(i).forEach(function(t){ meta.push(t) });
    if(!off('where')){
      var place = (i.place || '').trim(), loc = townOf(i.loc);
      /* Two facts that are often the same one twice — "Torquay Hotel" in a row
         whose location reads "Torquay". Where one contains the other, the
         longer is the one that tells you something. And a row linked to its own
         place row carries its own name in `place`, which tells you nothing. */
      if(place && place.toLowerCase() === String(i.name || '').trim().toLowerCase()) place = '';
      if(place && loc){
        var a = place.toLowerCase(), b = loc.toLowerCase();
        if(a.indexOf(b) >= 0 || b.indexOf(a) >= 0) { place = a.length >= b.length ? place : loc; loc = '' }
      }
      if(off('suburb')) loc = '';
      if(place) meta.push(place);
      if(loc) meta.push(loc);
    }
    if(i.cost) meta.push(i.cost);
    /* km is null for anything with nowhere to be, and 0 means Jan Juc itself —
       neither is a distance to print, and 0 must never read as "unknown". */
    if(i.km != null && i.km > 0) meta.push(i.km + ' km');
    if(i.ev && i.time) meta.push(i.time);

    var links = [];
    if(i.ticket) links.push(['Tickets', i.ticket]);
    if(i.info)   links.push(['Details', i.info]);
    if(i.url && i.url !== i.info) links.push([/google\.[a-z.]+\/maps/.test(i.url) ? 'Map' : 'Website', i.url]);
    if(i.lat != null && i.lng != null)
      links.push(['Directions', 'https://www.google.com/maps/dir/?api=1&destination=' + i.lat + ',' + i.lng]);

    return '<div class="row">' +
      '<div class="nm">' + esc(i.name) + '</div>' +
      (i.ev ? '<div class="when">' + esc(whenLabel(i)) + '</div>' : '') +
      (meta.length ? '<div class="meta">' + meta.map(function(m){
        return '<i>' + esc(m) + '</i>' }).join('') + '</div>' : '') +
      (i.desc ? '<div class="desc">' + esc(i.desc) + '</div>' : '') +
      (links.length ? '<div class="lnks">' + links.map(function(l){
        return '<a href="' + esc(l[1]) + '" rel="noopener">' + l[0] + '</a>' }).join('') + '</div>' : '') +
      '</div>';
  }

  /* ── one listing, closed until you ask ──
     The same gesture as the board's row at a size that fits half a column:
     the head is the button, the body carries what the head could not show.
     `skip` works exactly as it does in row() — the facts the page has already
     made its subject are left out.

     The head deliberately shows no description. On a monitoring view the
     thing you are scanning for is the name and how it is filed, and 65 cafes
     each with a paragraph is a page nobody reads to the bottom of. */
  function item(i, skip, dropType){
    var drop = ',' + (skip || '') + ',';
    var off  = function(k){ return drop.indexOf(',' + k + ',') >= 0 };

    var meta = [];
    if(!off('type')){
      /* `dropType` removes ONE type — the page's own — and keeps the rest.
         On /cafe a row that is `bakery · cafe` should still say bakery: that
         is the only thing distinguishing it from the other 64, and dropping
         the whole list to avoid repeating "cafe" throws it away too. */
      var ts = typesOf(i).filter(function(t){ return t !== dropType });
      if(ts.length) ts.forEach(function(t){ meta.push(esc(t)) });
      else if(!typesOf(i).length) meta.push('<span class="unsorted">unsorted</span>');
    }
    if(!off('where')){
      var place = (i.place || '').trim(), loc = townOf(i.loc);
      /* A row linked to its own place row — which is how a shop or a venue
         inherits a coordinate — has the same string in both, so it would print
         its own name back at itself. */
      if(place && place.toLowerCase() === String(i.name || '').trim().toLowerCase()) place = '';
      if(place && loc){
        var a = place.toLowerCase(), b = loc.toLowerCase();
        if(a.indexOf(b) >= 0 || b.indexOf(a) >= 0){ place = a.length >= b.length ? place : loc; loc = '' }
      }
      if(off('suburb')) loc = '';
      if(place) meta.push(esc(place));
      if(loc) meta.push(esc(loc));
    }
    if(i.km != null && i.km > 0) meta.push(i.km + ' km');
    if(i.ev) meta.push('<span class="item-when">' + esc(whenLabel(i)) + '</span>');

    var links = [];
    if(i.ticket) links.push(['Tickets', i.ticket]);
    if(i.info)   links.push(['Details', i.info]);
    if(i.url && i.url !== i.info) links.push([/google\.[a-z.]+\/maps/.test(i.url) ? 'Map' : 'Website', i.url]);
    if(i.lat != null && i.lng != null)
      links.push(['Directions', 'https://www.google.com/maps/dir/?api=1&destination=' + i.lat + ',' + i.lng]);

    var fact = function(label, v){
      return v ? '<p class="dl"><b>' + label + '</b><span>' + esc(v) + '</span></p>' : '' };

    return '<div class="item">' +
      '<button class="item-head" type="button" aria-expanded="false">' +
        '<span class="item-name">' + esc(i.name) + '</span>' +
        (meta.length ? '<span class="item-meta">' + meta.map(function(m){
          return '<i>' + m + '</i>' }).join('') + '</span>' : '') +
      '</button>' +
      '<div class="item-body">' +
        '<p>' + (i.desc ? esc(i.desc)
                        : '<em style="color:var(--ink3)">No description yet.</em>') + '</p>' +
        fact('Good to know', i.notes) +
        fact('Best conditions', (i.cond || []).join(', ')) +
        fact('Suits', (i.ages || []).join(', ')) +
        fact('Cost', i.cost) +
        fact('Time', i.time) +
        (i.ev ? fact('How often', i.recur) : fact('How long', i.dur)) +
        (i.ev ? '' : fact('Season', (i.season || []).join(', '))) +
        (i.rating ? fact('Rating', i.rating + ' / 5') : '') +
        (links.length ? '<div class="lnks">' + links.map(function(l){
          return '<a href="' + esc(l[1]) + '" rel="noopener" target="_blank">' + l[0] + '</a>'
        }).join('') + '</div>' : '') +
      '</div></div>';
  }

  /* One listener on the container rather than one per row — a type page can
     hold 400 of these, and they are re-rendered whenever the page redraws. */
  function wireItems(root){
    root.addEventListener('click', function(e){
      var head = e.target.closest('.item-head');
      if(!head || !root.contains(head)) return;
      var open = head.parentNode.classList.toggle('open');
      head.setAttribute('aria-expanded', String(open));
    });
  }

  var byDate = function(a,b){
    var k = function(i){ return i.date ? (daysAway(nextDate(i)) == null ? 9e5 : daysAway(nextDate(i))) : 9e5 };
    return k(a) - k(b) || a.name.localeCompare(b.name);
  };
  var byName = function(a,b){ return a.name.localeCompare(b.name) };

  var n = function(c, one, many){ return c + ' ' + (c === 1 ? one : many) };

  /* ── which subject this page is about, and its one true address ──
     The URL is flat — /anglesea, /surfing — so the slug is the whole path and
     nothing in it says which of the two pages you are on. It does not need to:
     the page knows what it is, and `seg` is its own name, used only to tell
     "/place/anglesea" (an old link, mid-redirect) from "/anglesea".

     Three shapes reach here, and all three still have to work:
       /anglesea            the flat path, what everything links to now
       /place/anglesea      a link shared before 27 Aug 2026 — Vercel 301s it,
                            but a bookmark can still land here first
       /place?p=Anglesea    older still, served straight off the filesystem

     Whichever way it arrived, the address bar is put back to the flat form.
     replaceState and not assign: no reload, and no second entry in the back
     button for a URL the reader never chose. */
  function subject(seg, param, list, fallback){
    var parts = location.pathname.replace(/\.html$/,'').split('/').filter(Boolean);
    var raw = '';
    if(parts[0] === seg)  raw = parts[1] ? decodeURIComponent(parts[1]) : '';
    else if(parts[0])     raw = decodeURIComponent(parts[0]);
    if(!raw) raw = new URLSearchParams(location.search).get(param) || '';
    if(!raw) return {value: fallback, raw: fallback};
    return {value: unslug(raw, list), raw: raw};
  }

  /* Only ever called once the subject is known to be real. A made-up slug
     keeps the URL the reader typed — rewriting it would hide the mistake the
     page is about to explain. */
  function canonical(value){
    var want = '/' + slugify(value);
    if(location.pathname !== want)
      try{ history.replaceState(null, '', want + location.hash) }catch(e){}
  }

  window.NoticePage = {esc:esc, rows:rows, row:row, whenLabel:whenLabel,
                       byDate:byDate, byName:byName, n:n,
                       subject:subject, canonical:canonical,
                       item:item, wireItems:wireItems};
})();
