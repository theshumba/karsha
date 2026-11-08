#!/usr/bin/env python3
"""Rename percent-encoded directories to their decoded UTF-8 names.

mirror.py writes a route containing a non-ASCII character to disk using the
percent-encoded form as a literal directory name (categories/caf%C3%A9s), while
every link in the HTML points at the decoded form (/categories/cafés). A static
host decodes the request before looking on disk, so the page 404s everywhere.

Caught on the Listora mirror: /categories/cafés was the single broken route,
63.9% pixel diff and the only route with console errors.
"""
import os, sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
renamed = []

for p in sorted(ROOT.rglob('*'), key=lambda x: -len(x.parts)):
    if '.mirror-cache' in p.parts or '.git' in p.parts or 'docs' in p.parts:
        continue
    if '%' not in p.name:
        continue
    decoded = unquote(p.name)
    if decoded == p.name:
        continue
    target = p.with_name(decoded)
    if target.exists():
        print(f'  skip, target exists: {target.relative_to(ROOT)}')
        continue
    p.rename(target)
    renamed.append((p.name, decoded))

for old, new in renamed:
    print(f'  {old}  ->  {new}')
print(f'{len(renamed)} path(s) renamed')
sys.exit(0)
