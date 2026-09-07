#!/usr/bin/env python3
"""Parks Victoria's Change of Conditions — what is closed in the parks.

Every park page on parks.vic.gov.au carries a server-rendered block of
notices: a site (h4), a title (h3) and a paragraph. There is no feed and no
API behind it — probed 4 Sep 2026 by the nature source pass and again here —
so this reads the thirteen park pages that fall in this region and keeps the
`park_notices` table in step with them. See supabase/PARK_NOTICES.sql for the
wording rule: the public board prints the title and a link, never the
paragraph.

    python3 scripts/scrape_parks.py            # look and report, writes nothing
    python3 scripts/scrape_parks.py --write    # keep park_notices in step

Idempotent against the database, keyed on sha1(park, site, title). A notice
that has gone from a page that was READ SUCCESSFULLY is marked inactive, not
deleted; a park whose page did not answer keeps its notices as they were.

robots.txt on parks.vic.gov.au names no AI crawler (checked 8 Sep 2026), so a
Claude session may run this as well as the Action. Sub-pages under a park
(campgrounds, walks) inherit the park page's block — checked: Lake Elizabeth
and Big Hill carry the Otway page's three items verbatim — so reading the park
page once is the whole of it and produces no duplicates.
"""
import sys, re, html, hashlib, datetime, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eventlib as E

SITE = 'parks.vic.gov.au'
BASE = 'https://www.parks.vic.gov.au/places-to-see/parks/'

# The region's park pages, off the site's own sitemap (466 park URLs, 8 Sep
# 2026; these are the top-level pages that fall between Colac, the You Yangs,
# Werribee and the coast). Point Cook is Melbourne and is left out. A slug
# that stops answering prints as failed rather than as a park with nothing
# closed — a 404 here returns 200 with the generic body, so the test is
# whether the notices block parses, never the status code.
PARKS = [
    ('great-otway-national-park',            'Great Otway National Park'),
    ('you-yangs-regional-park',              'You Yangs Regional Park'),
    ('brisbane-ranges-national-park',        'Brisbane Ranges National Park'),
    ('point-addis-marine-national-park',     'Point Addis Marine National Park'),
    ('serendip-sanctuary',                   'Serendip Sanctuary'),
    ('barwon-bluff-marine-sanctuary',        'Barwon Bluff Marine Sanctuary'),
    ('eagle-rock-marine-sanctuary',          'Eagle Rock Marine Sanctuary'),
    ('marengo-reefs-marine-sanctuary',       'Marengo Reefs Marine Sanctuary'),
    ('point-danger-marine-sanctuary',        'Point Danger Marine Sanctuary'),
    ('port-phillip-heads-marine-national-park', 'Port Phillip Heads Marine National Park'),
    ('steiglitz-historic-park',              'Steiglitz Historic Park'),
    ('werribee-gorge-state-park',            'Werribee Gorge State Park'),
    ('werribee-park',                        'Werribee Park'),
]

# Hand decisions, the BY_ID pattern: (park slug, site as published) -> the
# activity ids a notice under that site attaches to, with the reason. Empty
# today. Park-wide sites ("Great Otway National Park", "Notices Affecting
# Multiple Sites") attach to nothing on purpose — a road closure inland of
# Wye River is not a fact about Wye River Beach, and guessing which rows it
# touches is the fault this project refuses everywhere else.
BY_SITE = {
    # ('great-otway-national-park', 'Wye Road'): [75, 221],   # example shape
}

MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
UNTIL_RE = re.compile(
    r'\b(?:to|until|through|reopen(?:ing|s)?\s+on)\s+(\d{1,2})\s+(' + MONTHS + r')\s+(\d{4})\b', re.I)
ITEM_RE = re.compile(r'<li class="item change-of-conditions__item">(.*?)</li>', re.S)


def plain(s):
    """Their HTML to plain text. Block elements become line breaks, so
    'What to expect:' and its points do not run into one sentence."""
    s = re.sub(r'<br\s*/?>|</(?:p|div|li|h\d)>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t\xa0]+', ' ', s)
    s = re.sub(r'\s*\n\s*', '\n', s)
    return s.strip()


def balanced_div(t, start):
    """The text of the <div ...> that opens at `start`, walking nested divs,
    because the content block holds divs of its own and a regex to the next
    </div> cuts it after the first sentence."""
    i = t.index('>', start) + 1
    depth, j = 1, i
    while depth and j < len(t):
        m = re.compile(r'<div\b|</div>').search(t, j)
        if not m:
            return t[i:]
        depth += 1 if m.group(0).startswith('<div') else -1
        j = m.end()
    return t[i:j - 6]


def items(page):
    """Every notice on a page, as published."""
    out = []
    for m in ITEM_RE.finditer(page):
        it = m.group(1)
        sub = re.search(r'__subtitle">(.*?)</h4>', it, re.S)
        ttl = re.search(r'__title-text">(.*?)</span>', it, re.S)
        lvl = re.search(r'__heading--(\w+)', it)
        b = it.find('class="change-of-conditions__content"')
        body = plain(balanced_div(it, it.rfind('<div', 0, b))) if b >= 0 else ''
        title = plain(ttl.group(1)) if ttl else ''
        if not title:
            continue
        out.append({
            'site':  plain(sub.group(1)) if sub else None,
            'title': title,
            'level': lvl.group(1) if lvl else None,
            'body':  body[:2000],
        })
    return out


def until_of(body):
    """An end date the body states plainly, or None. One distinct date or
    nothing: 'closed from 29 May to 25 September 2026' gives the 25th; a body
    naming two different end dates is a person's job."""
    found = set()
    for d, mo, y in UNTIL_RE.findall(body or ''):
        try:
            found.add(datetime.datetime.strptime(f'{d} {mo} {y}', '%d %B %Y').date())
        except ValueError:
            pass
    return found.pop() if len(found) == 1 else None


def key_of(park, site, title):
    return hashlib.sha1(f'{park}|{site or ""}|{title}'.encode()).hexdigest()[:16]


def site_name(site):
    """'Aire River West Campground (Great Otway National Park GORCAPA, ...)'
    -> 'Aire River West Campground'. The bracket is the park hierarchy."""
    return re.sub(r'\s*\(.*$', '', site or '').strip()


def attach(park, site, by_name):
    """Which listings a notice belongs to. Exact normalised name match on the
    site, or a hand line — never fuzzy, never the park's whole contents."""
    hand = BY_SITE.get((park, site_name(site)))
    if hand:
        return list(hand)
    return list(by_name.get(E.norm(site_name(site)), []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    E.load_env()
    today = datetime.date.today().isoformat()

    acts = E.db('GET', '/rest/v1/activities?select=id,name&published=is.true', all_rows=True)
    by_name = {}
    for a in acts:
        by_name.setdefault(E.norm(a['name']), []).append(a['id'])
    names = {a['id']: a['name'] for a in acts}

    have = {r['key']: r for r in E.db('GET', '/rest/v1/park_notices?select=*', all_rows=True)}

    seen, read_ok, failed = {}, [], []
    for slug, name in PARKS:
        url = BASE + slug
        page = E.fetch(url, cap=400_000, timeout=25)
        if page is None:
            failed.append(slug); continue
        # A missing slug returns 200 with the generic page; the block that says
        # "this is a park page" is the notices wrapper itself, present even
        # when empty.
        if 'change-of-conditions' not in page:
            failed.append(slug); continue
        read_ok.append(slug)
        for it in items(page):
            k = key_of(slug, it['site'], it['title'])
            seen[k] = {**it, 'key': k, 'park': slug, 'park_name': name, 'park_url': url,
                       'until': until_of(it['body']),
                       'activity_ids': attach(slug, it['site'], by_name)}

    new = [n for k, n in seen.items() if k not in have]
    kept = [n for k, n in seen.items() if k in have]
    # Only a park that was read may stand a notice down — a page that did not
    # answer says nothing about what it would have shown.
    ended = [r for k, r in have.items()
             if r['active'] and k not in seen and r['park'] in read_ok]
    revived = [r for k, r in have.items() if not r['active'] and k in seen]
    attached = [n for n in seen.values() if n['activity_ids']]
    parkwide = [n for n in seen.values() if not n['activity_ids']]

    if failed and not read_ok:
        print(f'source {SITE} — failed: none of {len(PARKS)} park pages answered')
        sys.exit(1)
    print(f'source {SITE} — {len(read_ok)} of {len(PARKS)} parks read, '
          f'{len(seen)} notices, {len(new)} new, {len(ended)} ended, '
          f'{len(attached)} attached to a listing, {len(parkwide)} unattached'
          + (f', FAILED to read {", ".join(failed)}' if failed else ''))

    print('NOTICES')
    for n in sorted(seen.values(), key=lambda x: (x['park'], x['title'])):
        who = ', '.join(f'a{i} {names.get(i, "?")}' for i in n['activity_ids']) or '—'
        print(f'  {"NEW " if n in new else "    "}{n["park"]} | {n["level"] or "-"} | '
              f'{n["title"]} | site: {site_name(n["site"]) or "-"} | '
              f'until {n["until"] or "-"} | -> {who}')
    if ended:
        print(f'ENDED — {len(ended)} no longer on a page that was read')
        for r in ended:
            print(f'  {r["park"]} | {r["title"]} | first seen {r["first_seen"]}')
    if parkwide:
        print(f'UNATTACHED — {len(parkwide)} name no listing (park-wide, or no row by that name)')
        for n in parkwide:
            print(f'  {n["park"]} | site: {site_name(n["site"]) or "-"} | {n["title"]}')

    if not args.write:
        print('dry run — nothing written; --write to apply')
        return

    note = f'read from {SITE} by scrape_parks.py; title and site are Parks Victoria\'s own words, body kept for the back office only'
    if new:
        E.db('POST', '/rest/v1/park_notices', [{
            'key': n['key'], 'park': n['park'], 'park_name': n['park_name'],
            'park_url': n['park_url'], 'site': n['site'], 'title': n['title'],
            'level': n['level'], 'body': n['body'],
            'until': n['until'].isoformat() if n['until'] else None,
            'activity_ids': n['activity_ids'], 'first_seen': today, 'last_seen': today,
            'active': True, 'source_note': note,
        } for n in new], extra={'Prefer': 'return=minimal'})
    for n in kept:
        # Re-read the body and the date every run: the page is the truth and
        # a person's judgement lives nowhere on this row. The attachments are
        # rewritten too, so a listing added later picks its notice up.
        E.db('PATCH', f'/rest/v1/park_notices?key=eq.{n["key"]}', {
            'last_seen': today, 'active': True, 'body': n['body'], 'level': n['level'],
            'until': n['until'].isoformat() if n['until'] else None,
            'activity_ids': n['activity_ids'],
        }, extra={'Prefer': 'return=minimal'})
    for r in ended:
        E.db('PATCH', f'/rest/v1/park_notices?key=eq.{r["key"]}', {'active': False},
             extra={'Prefer': 'return=minimal'})
    print(f'wrote {len(new)} new, refreshed {len(kept)}, ended {len(ended)}, '
          f'revived {len(revived)}')


if __name__ == '__main__':
    main()
