#!/usr/bin/env python3
"""Remove the template author's own Google Analytics from the mirror.

detach.py strips Framer's built-in beacon, but a template author can paste their
own gtag snippet into Framer's custom head/body code, and that survives. On the
Listora mirror every one of the 75 pages was still reporting pageviews to the
author's property G-EP7Z8ZCV9W from localhost. Always check for this after detach.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    # the loader tag
    re.compile(r'<script[^>]*src="https?://www\.googletagmanager\.com/[^"]*"[^>]*>\s*</script>', re.I),
    # any inline gtag bootstrap block
    re.compile(r'<script\b(?![^>]*\bsrc=)[^>]*>(?:(?!</script>).)*?\bgtag\s*\((?:(?!</script>).)*?</script>', re.I | re.S),
    # google tag manager container form
    re.compile(r'<script\b(?![^>]*\bsrc=)[^>]*>(?:(?!</script>).)*?googletagmanager\.com(?:(?!</script>).)*?</script>', re.I | re.S),
    re.compile(r'<noscript>\s*<iframe[^>]*googletagmanager\.com[^>]*>\s*</iframe>\s*</noscript>', re.I | re.S),
    # the leftover HTML comment
    re.compile(r'<!--\s*Global site tag \(gtag\.js\)[^>]*?-->', re.I),
]

changed = removed = 0
for f in sorted(ROOT.rglob('*.html')):
    if '/docs/' in str(f) or '/.mirror-cache/' in str(f):
        continue
    s = orig = f.read_text(encoding='utf-8', errors='ignore')
    for p in PATTERNS:
        s, n = p.subn('', s)
        removed += n
    if s != orig:
        f.write_text(s, encoding='utf-8')
        changed += 1

leftover = 0
for f in ROOT.rglob('*.html'):
    if '/docs/' in str(f) or '/.mirror-cache/' in str(f):
        continue   # the download cache is gitignored and never shipped
    t = f.read_text(encoding='utf-8', errors='ignore')
    leftover += t.count('googletagmanager') + t.count('G-EP7Z8ZCV9W')

print(f'{changed} pages cleaned, {removed} tags removed')
print(f'references to googletagmanager / the GA id remaining: {leftover}')
sys.exit(1 if leftover else 0)
