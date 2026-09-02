#!/usr/bin/env python3
"""The assertions private/admin.html has to pass. Run it after editing that file.

    python3 scripts/check_admin.py

WHY THIS EXISTS. That file is 4,500 lines of markup, CSS and JavaScript edited
by scripts, and it has now failed the same way three times — a replacement whose
anchors spanned more than the author meant, silently taking code with it:

  - a function inserted INTO the <style> block, because the anchor matched a CSS
    comment hundreds of lines earlier. It parsed clean, shipped nothing, and
    surfaced at runtime as "drawHome is not defined".
  - a rebuild of the tab strip that deleted the six tally spans six functions
    were still writing to.
  - a slice from `const RSORTS` to `function drawReview()` that swallowed
    reviewRows, clock and dupeCell, because a later edit had written them
    BETWEEN those two markers. The page was driven in a browser BEFORE that edit
    and committed after it, so nothing caught it and /admin's Review tab shipped
    broken.

The rule this project already records is *assert on what a replacement REMOVES,
not only that it found something*. Check 4 is that rule made mechanical: it asks
git what the file used to define, and complains only where a name has gone and
something still calls it. A deliberate deletion has no callers left and passes
in silence; the third failure above is caught on the spot.

`node --check` is necessary and nowhere near sufficient — every one of the three
parsed perfectly.
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REL  = 'private/admin.html'
PAGE = ROOT / REL

DECL = re.compile(r'^(?:function\s+([\w$]+)\s*\(|(?:const|let|var)\s+([\w$]+)\s*=)', re.M)


def parts(text):
    """(the stylesheet, the page's own script) — the biggest inline <script>."""
    css = text[text.index('<style>'):text.index('</style>')]
    bodies = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', text, re.S)
    return css, max(bodies, key=len)


def top_level(js):
    """Names this script defines at the left margin. Deliberately only column 0:
    a nested helper is not something another function can lose track of."""
    return {a or b for a, b in DECL.findall(js)}


def committed():
    """The same file as git last saw it, or None outside a repo / on a new file."""
    r = subprocess.run(['git', 'show', f'HEAD:{REL}'],
                       cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    text = PAGE.read_text()
    css, js = parts(text)
    bad, note = [], []

    # 1. No function may live in the stylesheet.
    stray = re.findall(r'function \w+\(', css)
    if stray:
        bad.append(f"{len(stray)} function(s) inside <style>: {stray[:3]}")

    # 2. Every #id the script reaches for exists in the markup.
    ids  = set(re.findall(r'\bid="([\w-]+)"', text))
    used = set(re.findall(r"\$\('#([\w-]+)'\)", text))
    if used - ids:
        bad.append(f"$('#id') with no such id: {sorted(used - ids)}")

    # 3. It parses. node is the only thing that can say so.
    tmp = ROOT / '.admin-check.js'
    tmp.write_text(js)
    try:
        r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
        if r.returncode:
            bad.append('does not parse: ' + (r.stderr.strip().splitlines() or [''])[-1])
    finally:
        tmp.unlink(missing_ok=True)

    # 4. Nothing git knew about has gone while something still calls it.
    old = committed()
    if old is None:
        note.append('not comparing against git — no committed copy of this file')
    else:
        gone = top_level(parts(old)[1]) - top_level(js)
        # A name is only a problem if the page still asks for it. `foo` alone is
        # a deliberate deletion; `foo(` with no `foo` is the bug.
        orphan = sorted(n for n in gone
                        if re.search(r'(?<![.\w$])' + re.escape(n) + r'\s*\(', js))
        if orphan:
            bad.append('defined at HEAD, gone now, still called: ' + ', '.join(orphan))
        elif gone:
            note.append(f"{len(gone)} name(s) removed since HEAD and nothing calls "
                        f"them: {', '.join(sorted(gone))}")

    for n in note: print('note ' + n)
    for b in bad:  print('FAIL ' + b)
    if not bad:
        print('admin.html: stylesheet clean, ids resolve, parses, '
              'nothing called has gone missing')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
