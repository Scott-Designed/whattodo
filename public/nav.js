/* ══ nav.js ════════════════════════════════════════════════════════════
   Draws the bar and works its two menus. One file, four pages.

   It writes itself into the page rather than being pasted into each file's
   markup, so the bar is in one place when it changes. Load it as the FIRST
   thing inside <body>, not deferred at the end: a classic script there runs
   before anything below it has been parsed, so the bar is in the document
   before the first paint and nothing jumps down to make room for it.

   The menus are the vocabulary, not the data. A suburb with nothing in it is
   still a suburb, the counts belong on the page you land on rather than in the
   menu you leave, and building them from `listings` would mean this file
   waiting on a fetch before it could draw — three reasons pointing one way.
   PLACE_ORDER and TYPE_PLURAL come from notice-vocab.js, so nothing here is a
   second copy of either list.
   ═══════════════════════════════════════════════════════════════════════ */
(function(){
  'use strict';

  function esc(s){ return String(s).replace(/[&<>"]/g,
    function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c] }) }

  /* Which nav item is the page you are on. The page says so itself, on its
     <body>, because the URL no longer can: /anglesea and /surfing are both a
     bare slug, and telling them apart needs the vocabulary — which loads after
     this file, since the bar is drawn before the first paint. A page knowing
     its own name needs nothing and cannot be wrong. */
  var CUR = document.body.dataset.nav || 'board';
  /* Everything and the Notice Board are the same file — index.html serving two
     paths — so the <body> attribute cannot tell them apart and the path has to.
     A literal path needs no vocabulary, so this is safe here even though the
     vocabulary loads after this file. */
  if(CUR === 'board' && location.pathname.replace(/\/+$/,'') === '/noticeboard')
    CUR = 'whatson';

  /* Which subject, for lighting one row inside a menu. Read late, inside the
     fill functions, so slugify() exists by then. Three shapes still arrive:
     the flat path, an old /place/<slug> mid-redirect, and an older ?p=. */
  function currentSlug(param){
    var parts = location.pathname.replace(/\.html$/,'').split('/').filter(Boolean);
    var raw = (parts[0] === 'place' || parts[0] === 'type')
      ? (parts[1] ? decodeURIComponent(parts[1]) : '')
      : (parts[0] ? decodeURIComponent(parts[0]) : '');
    return slugify(raw || new URLSearchParams(location.search).get(param) || '');
  }

  /* ── the bar ── */
  var bar = document.createElement('nav');
  bar.className = 'nav';
  bar.setAttribute('aria-label','Main');
  bar.innerHTML =
    '<a class="mark" href="/">Notice</a>' +
    '<a class="navlink" data-nav="about" href="/about"' +
      (CUR==='about'?' aria-current="page"':'') + '>About</a>' +
    '<a class="navlink" data-nav="board" href="/"' +
      (CUR==='board'?' aria-current="page"':'') + '>Everything</a>' +
    '<a class="navlink" data-nav="whatson" href="/noticeboard"' +
      (CUR==='whatson'?' aria-current="page"':'') + '>Noticeboard</a>' +
    menu('place','Place') +
    menu('type','Type') +
    savedPill() +
    burger();

  /* ── the pin count, in the bar ──
     What you have kept is a fact about the reader, not about one page, so it
     travels with the bar. On the board it is the button that holds the list
     down to what you saved (index.html wires it); anywhere else it is a link
     to the board with that view already on. The count is read straight from
     localStorage, the one place the saved list lives. */
  function savedPill(){
    var n = 0;
    try{ n = JSON.parse(localStorage.getItem('notice.saved')||'[]').length }catch(e){}
    var onBoard = CUR==='board' || CUR==='whatson';
    var inner = '<span class="ic" aria-hidden="true">\uD83D\uDCCC</span><b>'+n+'</b>';
    var cls = 'navlink savedpill'+(n?'':' empty');
    return onBoard
      ? '<button type="button" id="savedbtn" class="'+cls+'" aria-pressed="false"'
        +' aria-label="Saved listings">'+inner+'</button>'
      : '<a id="savedbtn" href="/?saved" class="'+cls+'" aria-label="Saved listings">'+inner+'</a>';
  }

  /* ── the hamburger ──
     About, Place, Type and the theme switcher sit behind this, at every
     width since 7 Sep 2026. The bar keeps what a reader actually presses: the
     wordmark, Everything, Noticeboard, the pin count, and this. The About /
     Place / Type links are still drawn and hidden by CSS, so putting them back
     on a wide screen is one rule. Lucide `menu` (ISC), verbatim. */
  function burger(){
    return '<div class="navmenu burger">' +
      '<button class="navlink burger" type="button" data-menu="more"' +
        ' aria-expanded="false" aria-haspopup="true" aria-controls="navpop-more" aria-label="Menu">' +
        '<svg class="navic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"' +
        ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg></button>' +
      '<div class="navpop right full" id="navpop-more" hidden></div></div>';
  }

  function menu(key,label){
    return '<div class="navmenu '+key+'">' +
      '<button class="navlink" type="button" data-menu="'+key+'"' +
        ' aria-expanded="false" aria-haspopup="true" aria-controls="navpop-'+key+'"' +
        (CUR===key?' aria-current="page"':'') + '>' +
        label + '<i class="car" aria-hidden="true"></i></button>' +
      '<div class="navpop right" id="navpop-'+key+'" hidden></div></div>';
  }

  document.body.insertAdjacentElement('afterbegin', bar);

  /* ── what is in each menu ── */
  function fillPlace(box){
    /* PLACE_ORDER leads with the three that are not towns, so the menu splits
       there rather than at an alphabetical point. */
    var towns = PLACE_ORDER.filter(function(x){
      return x!=='Surf Coast wide' && x!=='Home' && x!=='Car' });
    var out = '<div class="grp">Towns</div>' + towns.map(link).join('') +
              '<div class="grp">Not one town</div>' +
              ['Surf Coast wide','Home','Car'].map(link).join('');
    function link(x){
      var on = CUR==='place' && currentSlug('p')===slugify(x);
      return '<a href="/'+slugify(x)+'"'+
             (on?' aria-current="page"':'')+'>'+esc(x)+'</a>' }
    box.innerHTML = out;
  }

  function fillType(box){
    /* Split on the band the type belongs to. `TYPE_BANDS` is not a new
       vocabulary — it is the two arrays the Add form already offers, which is
       the same split the database's `types.band` records. */
    var groups = [['Places to go', PLACE_TYPES], ['What’s on', EVENT_TYPES]];
    box.innerHTML = groups.map(function(g){
      return '<div class="grp">'+g[0]+'</div>' + g[1].map(function(t){
        var on = CUR==='type' && currentSlug('t')===slugify(t);
        /* iconFor comes from notice-icons.js, which every page loads. A type
           with no icon returns '' and the row simply has none — the label
           still lines up, because the slot is drawn either way. */
        var ic = (typeof iconFor==='function') ? iconFor(t) : '';
        return '<a href="/'+slugify(t)+'"'+
               (on?' aria-current="page"':'')+'><i class="tslot" aria-hidden="true">'+
               ic+'</i>'+esc(typeLabel(t))+'</a>' }).join('');
    }).join('');
  }

  /* The hamburger's panel: the three plain links, then Place and Type as
     rows that open in place. The town and type lists are the same fill
     functions the desktop menus use, so there is one list of each. */
  function fillMore(box){
    function plain(key,href,label){
      return '<a href="'+href+'"'+(CUR===key?' aria-current="page"':'')+'>'+label+'</a>' }
    function sec(key,label){
      return '<button class="navsec" type="button" data-sec="'+key+'" aria-expanded="false"' +
        ' aria-controls="sec-'+key+'"'+(CUR===key?' aria-current="page"':'')+'>' +
        label+'<i class="car" aria-hidden="true"></i></button>' +
        '<div class="secbox" id="sec-'+key+'" hidden></div>' }
    box.innerHTML = plain('about','/about','About') + plain('board','/','Everything') +
      plain('whatson','/noticeboard','Noticeboard') + sec('place','Place') + sec('type','Type') +
      themeRow();
  }

  /* ── light / dark / follow the system ──
     Lives here since 7 Sep 2026 so every page has it, in the menu. The
     stylesheets already have the three-state shape — bare :root is light, the
     prefers-color-scheme block is guarded with :not([data-theme="light"]), and
     [data-theme="dark"] overrides both — so this only sets or clears one
     attribute on <html>. Auto is a real third state: clearing the key means
     "follow the system". A change is announced as `notice:theme`, which is how
     the board retints its basemap. */
  var THEMEKEY='notice.theme';
  function themeRow(){
    var m = document.documentElement.dataset.theme || 'auto';
    return '<div class="grp">Theme</div>' +
      '<div class="navtheme" role="group" aria-label="Colour scheme">' +
      ['auto','light','dark'].map(function(x){
        return '<button type="button" data-mode="'+x+'" aria-pressed="'+(x===m)+'">' +
               x[0].toUpperCase()+x.slice(1)+'</button>' }).join('') + '</div>';
  }
  function setTheme(m){
    if(m==='auto') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = m;
    /* private browsing refuses to write: the choice holds for this visit */
    try{ m==='auto' ? localStorage.removeItem(THEMEKEY) : localStorage.setItem(THEMEKEY,m) }catch(e){}
    bar.querySelectorAll('[data-mode]').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.mode===m)) });
    document.dispatchEvent(new CustomEvent('notice:theme',{detail:m}));
  }

  var FILL = {place:fillPlace, type:fillType, more:fillMore}, BUILT = {};

  /* ── opening and closing ── */
  function closeAll(except){
    bar.querySelectorAll('[data-menu]').forEach(function(b){
      if(b===except) return;
      b.setAttribute('aria-expanded','false');
      document.getElementById('navpop-'+b.dataset.menu).hidden = true;
    });
  }

  bar.addEventListener('click', function(e){
    var th = e.target.closest('[data-mode]');
    if(th){ e.stopPropagation(); setTheme(th.dataset.mode); return; }
    /* a Place / Type row inside the hamburger opens in place */
    var s = e.target.closest('[data-sec]');
    if(s){
      e.stopPropagation();
      var box = document.getElementById('sec-'+s.dataset.sec);
      var was = s.getAttribute('aria-expanded')==='true';
      if(!was && !BUILT['sec-'+s.dataset.sec]){ FILL[s.dataset.sec](box); BUILT['sec-'+s.dataset.sec]=1 }
      s.setAttribute('aria-expanded', String(!was));
      box.hidden = was;
      return;
    }
    var b = e.target.closest('[data-menu]');
    if(!b) return;
    e.stopPropagation();
    var pop = document.getElementById('navpop-'+b.dataset.menu);
    var open = b.getAttribute('aria-expanded')==='true';
    closeAll(b);
    if(!open && !BUILT[b.dataset.menu]){ FILL[b.dataset.menu](pop); BUILT[b.dataset.menu]=1 }
    b.setAttribute('aria-expanded', String(!open));
    pop.hidden = open;
    /* The board closes its own filter pops on any document click, and this
       handler stops that click reaching it — so say so directly. */
    if(typeof closeAllMulti==='function') closeAllMulti();
  });

  document.addEventListener('click', function(){ closeAll() });
  document.addEventListener('keydown', function(e){
    if(e.key==='Escape'){ closeAll() } });
})();
