#!/usr/bin/env python3
"""Propose a kind for every undated listing.

    python3 scripts/classify_kinds.py            # the proposal, writes nothing
    python3 scripts/classify_kinds.py --write    # fill in the rows with no kind
    python3 scripts/classify_kinds.py --write --reclassify   # overwrite every row
    python3 scripts/classify_kinds.py --show venue           # one kind in full

**--write only fills nulls.** A row that already has a kind was either set by
the first run or set by a person afterwards, and this script cannot tell those
apart — so re-running it must not quietly undo somebody's decision. `Gather
Athletics` is a group whose types are `running · community`, which the rules
below would make a spot; it is right because a person said so, and one
re-run without this guard would have thrown that away. Disagreements are still
printed every time, so nothing is hidden — `--reclassify` applies them.

Events are always `happening` and the view says so with a literal, so this
only ever touches `activities`.

What decides a kind, in order, and why the order is the rule:

  1. A HAND DECISION in BY_ID. First, always, and the only thing that can
     overrule the rest. Every entry carries its reason.
  2. `types`. This is the researched field, so it is the one allowed to
     decide. The map below is exhaustive over the 43 types — a type with no
     entry is a bug, not a default, and the script says so rather than
     guessing.
  3. Nothing else. In particular NOT the name.

The name is deliberately excluded. A first pass at this filed `Barwon Club
Hotel` and `Workers Club Geelong` as Groups because their names contain
"Club", and reported it as a decision — which is exactly the failure this
project keeps paying for. Scott's rule: anything with a door defaults to
Venue, and moving a row out of Venue needs research, not a pattern.

A row whose types disagree is resolved by PRECEDENCE, not by the first type:
a row that is both an idea and a place is a place, because it has somewhere to
be. The order is idea < group < maker < shop < spot < venue, weakest first, so
venue wins any tie. `Common Ground Project` is `farm life · cafe · produce` and
comes out a venue, which is right — you can go and eat there; `Wye River
General Store` is `cafe · shop` and stays a venue for the same reason.

Then one correction, and it is the only thing here that reads a column other
than `types`: A SPOT WITH NO ANCHOR IS AN IDEA. `night` and `nature` describe
what a row is about, not whether it is anywhere — so "Milky Way Stargazing" and
"Jan Juc Skatepark" arrive at this point looking identical, both spots, both
with no pin. What separates them is `location`, which is researched:

    Jan Juc Skatepark          "Jan Juc"                 -> a town   -> spot
    Milky Way Stargazing       "Several Surf Coast bea…" -> nowhere  -> idea

That reading is done by `suburbOf` in public/notice-vocab.js, evaluated through
node rather than reimplemented here. It is the same function the site uses to
decide which town page a row belongs to, and a second copy of it would disagree
with the site eventually — the failure this project has paid for twice.

The correction only ever demotes a spot. A venue, shop, group or maker keeps
its kind whatever `location` says, because a door and a contact do not stop
existing when a location string fails to parse.
"""
import os, sys, json, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── the map: every one of the 43 types, and the kind it implies ──
# Exhaustive on purpose. Adding a type means adding a line here, and the
# script refuses to run if one is missing rather than filing it as a venue.
KIND_OF = {
  # outdoors, no door, nobody owns it
  'beach':'spot', 'surfing':'spot', 'swimming':'spot', 'paddling':'spot',
  'water':'spot', 'walk':'spot', 'nature':'spot', 'parks & playgrounds':'spot',
  'skatepark':'spot', 'mountain biking':'spot', 'cycling':'spot',
  'running':'spot', 'rock climbing':'spot', 'camping ground':'spot',
  'night':'spot', 'cultural':'spot', 'farm life':'spot',

  # a door, hours, a price
  'cafe':'venue', 'restaurant':'venue', 'bakery':'venue', 'pub':'venue',
  'bar':'venue', 'brewery':'venue', 'winery':'venue', 'produce':'venue',
  'museum':'venue', 'cinema':'venue', 'theatre':'venue',
  'art gallery':'venue', 'golf':'venue', 'market':'venue', 'arts':'venue',
  # a plant nursery has a door, hours and a till — you visit it and buy plants.
  # It was `group` in the first pass, which put seven of them in with Landcare
  # and the working bees. Being run by volunteers does not stop a thing being a
  # place you go to.
  'nursery':'venue',

  # here so a type page has somewhere to buy the gear
  'shop':'shop',

  # people who run something you join
  'volunteering':'group', 'community':'group',

  # no anchor of any kind
  'at-home':'idea',

  # dated types, which only ever reach an activity by mistake
  'gig':'venue', 'festival':'venue', 'workshop':'group', 'comedy':'venue',
  'party':'venue', 'reading':'group',
}

# weakest first — the last one standing wins a row with several types.
# venue above shop is what keeps `cafe · shop` a venue: if you can sit down,
# you would go for its own sake, and that is the venue test.
PRECEDENCE = ['idea', 'group', 'maker', 'shop', 'spot', 'venue']

# suburbOf() answers with one of these when a row is not anywhere in
# particular. Anything else is a real town, and a real town is an anchor.
NOWHERE = {'Home', 'Car', 'Surf Coast wide', None}

# ── hand decisions ──
# Each one is a row the rules get wrong, with the reason. The rules propose;
# these are where a person has already accepted or overruled.
BY_ID = {
  # `community · swimming · beach` — spot beats group on precedence, so the
  # rules make this a spot and then demote it to an idea because "Surf Coast
  # surf clubs" is nowhere in particular. Both steps are right in general and
  # wrong here: Nippers is run by the volunteer clubs at Jan Juc, Torquay,
  # Anglesea and Lorne, and you enrol a child in it. That is a group.
  # Left as a hand decision rather than reordering PRECEDENCE, because it is
  # the ONLY row in 438 carrying both a group type and a spot type — a rule
  # change here would be fitted to one row.
  289: ('group', 'Nippers is run by the surf clubs and you enrol in it'),

  # The three rows added by hand on 27 Aug 2026, all of which the rules would
  # make spots — a maker, a shop and a group whose types are all activity types
  # that outrank their kind on PRECEDENCE. `types` says what a row is ABOUT and
  # cannot say what it IS when the two disagree, which is the whole reason
  # `kind` is a column rather than something derived.
  459: ('maker', 'a surfboard shaper — types say surfing, which is the subject'),
  460: ('shop',  'a shop that stocks gear for five activities, not five spots'),
  461: ('group', 'a running group — running·community, and you join it'),

  # `community` makes a group, which is right for a Landcare branch and wrong
  # for a building. A library is somewhere you walk into.
  288: ('venue', 'the Dome is a reading room, not a group you join'),
}

# ── plumbing ──
def env():
    e = {}
    p = ROOT / '.env'
    if p.exists():
        for line in p.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                e[k.strip()] = v.strip().strip('"').strip("'")
    for k in ('SUPABASE_URL', 'SUPABASE_SERVICE_KEY'):
        e.setdefault(k, os.environ.get(k, ''))
    if not e.get('SUPABASE_URL') or not e.get('SUPABASE_SERVICE_KEY'):
        sys.exit('SUPABASE_URL and SUPABASE_SERVICE_KEY must be in .env')
    return e

E = env()
H = {'apikey': E['SUPABASE_SERVICE_KEY'],
     'Authorization': 'Bearer ' + E['SUPABASE_SERVICE_KEY'],
     'Content-Type': 'application/json',
     'User-Agent': 'whattodo-janjuc/1.0 (classify_kinds)'}

def get(path):
    r = urllib.request.Request(E['SUPABASE_URL'] + '/rest/v1/' + path, headers=H)
    return json.load(urllib.request.urlopen(r, timeout=60))

def patch(table, rid, body):
    r = urllib.request.Request(
        E['SUPABASE_URL'] + '/rest/v1/' + table + '?id=eq.' + str(rid),
        data=json.dumps(body).encode(), headers={**H, 'Prefer': 'return=minimal'},
        method='PATCH')
    urllib.request.urlopen(r, timeout=60).read()

# ── the decision ──
def suburbs_for(locations):
    """suburbOf() for a batch of location strings, straight out of the site's
    own vocabulary. One copy of the rule, not two."""
    import subprocess
    js = ("const fs=require('fs'),vm=require('vm');const b=vm.createContext({});"
          "vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),b);"
          "const f=vm.runInContext('suburbOf',b);"
          "const inp=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));"
          "const o={};for(const s of inp)o[s]=f(s);"
          "process.stdout.write(JSON.stringify(o))")
    tmp = ROOT / '.suburbs.in.json'
    tmp.write_text(json.dumps(sorted(locations)))
    try:
        out = subprocess.run(
            ['node', '-e', js, str(ROOT / 'public' / 'notice-vocab.js'), str(tmp)],
            capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            sys.exit('could not read suburbOf from notice-vocab.js:\n' + out.stderr[:400])
        return json.loads(out.stdout)
    finally:
        tmp.unlink(missing_ok=True)

def decide(row, suburb):
    """(kind, why) for one activity. `suburb` is suburbOf(row.location)."""
    if row['id'] in BY_ID:
        k, why = BY_ID[row['id']]
        return k, 'by hand: ' + why

    types = row.get('types') or []
    if not types:
        return None, 'no types — nothing to read'

    kinds = []
    for t in types:
        if t not in KIND_OF:
            return None, 'type %r is not in KIND_OF' % t
        kinds.append(KIND_OF[t])

    kind = max(kinds, key=PRECEDENCE.index)
    why = '·'.join(types) + ' -> ' + '/'.join(dict.fromkeys(kinds))

    # the one correction, and it only ever demotes a spot
    if kind == 'spot' and suburb in NOWHERE:
        return 'idea', why + ', but "%s" is nowhere -> idea' % (row.get('location') or '')
    return kind, why

def main():
    write = '--write' in sys.argv
    redo  = '--reclassify' in sys.argv
    show = sys.argv[sys.argv.index('--show') + 1] if '--show' in sys.argv else None

    # a type the map has never heard of is a bug, and it should stop the run
    # rather than be quietly filed as a venue
    known = {t['name'] for t in get('types?select=name')}
    missing = known - set(KIND_OF)
    if missing:
        sys.exit('KIND_OF is missing %d type(s): %s'
                 % (len(missing), ', '.join(sorted(missing))))
    stale = set(KIND_OF) - known
    if stale:
        print('note: KIND_OF has %d type(s) the database no longer uses: %s\n'
              % (len(stale), ', '.join(sorted(stale))))

    rows = get('activities?select=id,name,types,kind,lat,km,location&order=id')
    subs = suburbs_for({r.get('location') or '' for r in rows})

    out, unknown = [], []
    for r in rows:
        kind, why = decide(r, subs.get(r.get('location') or ''))
        (unknown if kind is None else out).append(
            (r, why) if kind is None else (r, kind, why))

    tally = {}
    for r, kind, why in out:
        tally[kind] = tally.get(kind, 0) + 1

    print('%d activities read.\n' % len(rows))
    for k in reversed(PRECEDENCE):
        print('   %-10s %4d' % (k, tally.get(k, 0)))
    if unknown:
        print('   %-10s %4d   NEEDS A PERSON' % ('(none)', len(unknown)))
    print()

    if unknown:
        print('── rows the rules will not answer')
        for r, why in unknown:
            print('   %-6s %-42s %s' % (r['id'], r['name'][:42], why))
        print()

    # the correction firing is worth reading every time: it is the only place
    # this script overrules the researched type, so a wrong one here is a wrong
    # kind nobody would otherwise see
    demoted = [(r, why) for r, k, why in out if 'is nowhere' in why]
    print('── spot demoted to idea because it is nowhere in particular (%d)' % len(demoted))
    for r, why in demoted:
        print('   %-6s %-40s %s' % (r['id'], r['name'][:40], (r.get('location') or '')[:34]))
    print()

    # kind and coordinate disagreeing is a data question, not a kind question:
    # a spot with no pin needs geocoding, an idea with one needs the pin removed
    odd = [(r, k) for r, k, w in out
           if (k == 'idea' and r['lat'] is not None)
           or (k == 'spot' and r['lat'] is None)]
    if odd:
        print('── kind and coordinate disagree — a data job, not a kind job (%d)' % len(odd))
        for r, k in odd[:15]:
            print('   %-6s %-40s %-6s %s' % (
                r['id'], r['name'][:40], k,
                'has a pin' if r['lat'] is not None else 'no pin'))
        if len(odd) > 15:
            print('   … and %d more' % (len(odd) - 15))
        print()

    if show:
        rows_ = [(r, w) for r, k, w in out if k == show]
        print('── every %s (%d)' % (show, len(rows_)))
        for r, w in rows_:
            print('   %-6s %-44s %s' % (r['id'], r['name'][:44], w))
        print()

    differs = [(r, k) for r, k, w in out if r.get('kind') != k]
    fresh   = [(r, k) for r, k in differs if not r.get('kind')]
    settled = [(r, k) for r, k in differs if r.get('kind')]

    if settled:
        print('── already has a kind, and the rules disagree (%d)' % len(settled))
        print('   These are left alone unless you pass --reclassify. A kind that is')
        print('   already set may have been set by a person.')
        for r, k in settled:
            print('   %-6s %-40s %-8s -> %s' % (r['id'], r['name'][:40], r['kind'], k))
        print()

    changed = differs if redo else fresh
    print('%d row(s) with no kind would be filled.' % len(fresh))
    if redo: print('--reclassify: %d row(s) would be overwritten too.' % len(settled))

    if not write:
        print('\nDry run. Read the above, then re-run with --write.')
        return

    n = 0
    for r, k in changed:
        patch('activities', r['id'], {'kind': k})
        n += 1
        if n % 100 == 0:
            print('   %d/%d' % (n, len(changed)))
    print('wrote %d row(s).' % n)

if __name__ == '__main__':
    main()
