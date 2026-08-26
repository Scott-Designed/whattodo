#!/usr/bin/env python3
"""Paste your Supabase credentials into public/notice-data.js.

    python3 scripts/configure.py https://xxxx.supabase.co eyJhbGciOi...

The anon key is public by design — Row Level Security is what protects the
data. Never put the SERVICE key in this file; it belongs in .env only.
"""
import sys, pathlib, re
if len(sys.argv)!=3:
    print(__doc__); sys.exit(1)
url, anon = sys.argv[1].rstrip('/'), sys.argv[2].strip()
if 'service_role' in anon:
    sys.exit("That looks like the SERVICE key. Use the anon/public key — the service key\n"
             "would let anyone with the page delete your database.")
p = pathlib.Path(__file__).resolve().parent.parent / 'public' / 'notice-data.js'
h = p.read_text()
h2 = re.sub(r'const SUPABASE_URL = "[^"]*";',  f'const SUPABASE_URL = "{url}";',  h, count=1)
h2 = re.sub(r'const SUPABASE_ANON = "[^"]*";', f'const SUPABASE_ANON = "{anon}";', h2, count=1)
if h2 == h: sys.exit("Could not find the config block in public/notice-data.js.")
p.write_text(h2)
print(f"Configured {p}\n  url  {url}\n  anon {anon[:12]}…{anon[-4:]}")
