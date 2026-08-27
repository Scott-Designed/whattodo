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
      (CUR==='whatson'?' aria-current="page"':'') + '>Notice Board</a>' +
    menu('place','Place') +
    menu('type','Type');

  function menu(key,label){
    return '<div class="navmenu">' +
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
        return '<a href="/'+slugify(t)+'"'+
               (on?' aria-current="page"':'')+'>'+esc(typeLabel(t))+'</a>' }).join('');
    }).join('');
  }

  var FILL = {place:fillPlace, type:fillType}, BUILT = {};

  /* ── opening and closing ── */
  function closeAll(except){
    bar.querySelectorAll('[data-menu]').forEach(function(b){
      if(b===except) return;
      b.setAttribute('aria-expanded','false');
      document.getElementById('navpop-'+b.dataset.menu).hidden = true;
    });
  }

  bar.addEventListener('click', function(e){
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
