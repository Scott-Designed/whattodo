#!/usr/bin/env python3
"""Database housekeeping.

    python3 scripts/sync.py seed          # load the CSVs — ONCE, at setup
    python3 scripts/sync.py export        # database -> a dated .xlsx backup
    python3 scripts/sync.py pending       # community additions awaiting a check
    python3 scripts/sync.py verify 1043   # mark one verified
    python3 scripts/sync.py reject 1043   # remove one that isn't real (asks first)

The database is the source of truth. `export` writes a dated snapshot for
safekeeping; nothing reads it back. Edit rows in the Supabase table editor,
not in a spreadsheet.

Needs SUPABASE_URL and SUPABASE_SERVICE_KEY in the environment or a .env file.
The service key bypasses Row Level Security, so it stays out of the browser.
"""
import os, sys, json, csv, pathlib, datetime, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
def load_env():
    f = ROOT/'.env'
    if f.exists():
        for line in f.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k,v=line.split('=',1); os.environ.setdefault(k.strip(), v.strip())
load_env()
URL = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
KEY = os.environ.get('SUPABASE_SERVICE_KEY') or ''
if not URL or not KEY:
    sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_KEY (in the environment or .env).")

def req(method, path, body=None, extra=None):
    r = urllib.request.Request(URL+path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    r.add_header('apikey', KEY); r.add_header('Authorization','Bearer '+KEY)
    r.add_header('Content-Type','application/json')
    for k,v in (extra or {}).items(): r.add_header(k,v)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}\n{e.read().decode()[:400]}")

def arr(v):
    v=(v or '').strip()
    return [x.strip('"') for x in v[1:-1].split(',') if x] if v.startswith('{') else []

def seed():
    for table, f in (('activities','seed_activities.csv'), ('events','seed_events.csv')):
        rows=[]
        for r in csv.DictReader(open(ROOT/'supabase'/f)):
            row={k:(v if v!='' else None) for k,v in r.items()}
            for k in ('tags','ages','season','conditions'):
                if k in row: row[k]=arr(row[k])
            for k in ('km','rating','lat','lng','id'):
                if row.get(k) is not None:
                    row[k]=float(row[k]) if k in ('km','lat','lng') else int(row[k])
            row['verified'] = str(row.get('verified')).lower()=='true'
            rows.append(row)
        for i in range(0,len(rows),100):
            req('POST', f'/rest/v1/{table}', rows[i:i+100],
                {'Prefer':'resolution=merge-duplicates,return=minimal'})
        print(f"pushed {len(rows)} -> {table}")
    # keep identity sequences ahead of the seeded ids
    print("NOTE: run this once in the SQL editor so new inserts don't collide:")
    print("  select setval(pg_get_serial_sequence('activities','id'), (select max(id) from activities));")
    print("  select setval(pg_get_serial_sequence('events','id'),     (select max(id) from events));")

def export():
    from openpyxl import load_workbook
    xl = ROOT/'JanJuc_WhatToDo_Database.xlsx'
    if not xl.exists(): sys.exit(f"Put the spreadsheet at {xl} first.")
    acts = req('GET','/rest/v1/activities?select=*&order=id')
    evs  = req('GET','/rest/v1/events?select=*&order=id')
    wb = load_workbook(xl)
    stamp = datetime.date.today().isoformat()
    out = ROOT/f'JanJuc_WhatToDo_Database.{stamp}.xlsx'
    ws = wb['Activities']
    hdr = {c.value: i+1 for i,c in enumerate(ws[1])}
    by_id = {a['id']: a for a in acts}
    updated = added = 0
    seen=set()
    for r in range(2, ws.max_row+1):
        i = ws.cell(r,1).value
        if i is None: continue
        a = by_id.get(int(i))
        if not a: continue
        seen.add(int(i))
        if ws.cell(r,11).value != a['description']:
            ws.cell(r,11).value = a['description']; updated += 1
    nxt = ws.max_row+1
    for a in acts:
        if a['id'] in seen: continue
        ws.cell(nxt,1).value=a['id']; ws.cell(nxt,2).value=a['name']; ws.cell(nxt,3).value=a['type']
        ws.cell(nxt,6).value=a.get('cost'); ws.cell(nxt,7).value=a.get('location')
        ws.cell(nxt,8).value=a.get('km');   ws.cell(nxt,11).value=a.get('description')
        ws.cell(nxt,12).value=a.get('url'); ws.cell(nxt,13).value=a.get('added_by')
        ws.cell(nxt,15).value=('UNVERIFIED — added on the site' if not a.get('verified') else None)
        ws.cell(nxt,16).value=', '.join(a.get('conditions') or ['any-weather'])
        nxt+=1; added+=1
    wb.save(out)
    print(f"pulled {len(acts)} activities, {len(evs)} events")
    print(f"  {added} new rows appended, {updated} descriptions refreshed")
    print(f"  written to {out.name} (the original is untouched)")

def pending():
    for t in ('activities','events'):
        rows = req('GET', f'/rest/v1/{t}?select=id,name,type,location,added_by,created_at&verified=eq.false&order=created_at.desc')
        print(f"\n{t}: {len(rows)} awaiting a check")
        for r in rows:
            print(f"  {r['id']:>6}  {r['name'][:44]:44} {str(r.get('added_by'))[:14]:14} {str(r.get('created_at'))[:10]}")

def verify(idn):
    for t in ('activities','events'):
        got = req('PATCH', f'/rest/v1/{t}?id=eq.{idn}', {'verified':True},
                  {'Prefer':'return=representation'})
        if got: print(f"verified {t} {idn}: {got[0]['name']}"); return
    print(f"no row with id {idn}")

def reject(idn, assume_yes=False):
    """Delete a community add. Refuses verified rows; confirms unless --yes."""
    for t in ('activities','events'):
        got = req('GET', f'/rest/v1/{t}?id=eq.{idn}&select=id,name,type,location,added_by,verified')
        if not got: continue
        r = got[0]
        if r['verified']:
            sys.exit(f"{t} {idn} '{r['name']}' is verified — un-verify it in Supabase first "
                     f"if you really mean to remove it.")
        print(f"{t} {idn}: {r['name']}")
        print(f"  type {r.get('type')}   location {r.get('location')}   added by {r.get('added_by')}")
        if not assume_yes and input("  delete permanently? [y/N] ").strip().lower() != 'y':
            print("  left alone."); return
        req('DELETE', f'/rest/v1/{t}?id=eq.{idn}')
        print(f"rejected {t} {idn}: {r['name']}")
        return
    print(f"no row with id {idn}")

cmd = sys.argv[1] if len(sys.argv)>1 else ''
if   cmd=='seed': seed()
elif cmd=='export': export()
elif cmd=='pending': pending()
elif cmd=='verify' and len(sys.argv)>2: verify(sys.argv[2])
elif cmd=='reject' and len(sys.argv)>2: reject(sys.argv[2], '--yes' in sys.argv)
else: print(__doc__)
