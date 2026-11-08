#!/usr/bin/env python3
"""Finish what harden.py's quiet_prefetch starts.

harden.py patches only the FIRST CMS range-loader it finds per chunk. This
bundle (toplevel-deps) ships NINE identical loaders (co/wc/vu/mf/Im/Ag/xv/Bb and
the one harden already did). Each range-fetches a blob and throws
"Unexpected response length" off Framer's CDN. /referral uses a reference lookup
(mf -> getModel -> lookupItems) that HARD-crashes the page to height 0; the
markets pages log "Failed to call CollectionUtils method". Same root cause.

This applies harden's exact transform to every REMAINING loader: drop the range
param so the whole file is fetched, and replace the length-check + sequential
re-assembly loop with a single whole-file write at offset 0 (the store is keyed
by absolute offset, so u.read(from,len) still resolves).

Idempotent: a loader with no MARKER left is already done and is skipped.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "throw Error(`Request failed: Unexpected response length`);"
SET = "searchParams.set(`range`,"
DEL = "searchParams.delete(`range`,"
BUF = re.compile(r"=new Uint8Array\([\w$]+\);if\(([\w$]+)\.length!==[\w$]+\)$")
LOOP = re.compile(r"let ([\w$]+)=new ([\w$]+),[\w$]+=0;for\(let .*?\}", re.S)

total = 0
for p in sorted((ROOT / "assets/js").glob("*.mjs")):
    t = p.read_text(encoding="utf-8")
    if MARKER not in t:
        continue
    here = 0
    while MARKER in t:
        i = t.index(MARKER)
        head, tail = t[:i], t[i + len(MARKER):]
        buf = BUF.search(head[-160:])
        loop = LOOP.match(tail)
        if not buf or not loop:
            print(f"  !! {p.name}: loader shape changed near offset {i}, stopping. "
                  f"Re-derive BUF/LOOP from the code around the marker.")
            break
        resp, store, cls = buf.group(1), loop.group(1), loop.group(2)
        tail = f"void 0;let {store}=new {cls};{store}.write(0,{resp});" + tail[loop.end():]
        j = head.rfind(SET)                       # this loader's own range-set
        if j != -1:
            head = head[:j] + DEL + head[j + len(SET):]
        t = head + tail
        here += 1
    p.write_text(t, encoding="utf-8")
    total += here
    print(f"  {p.name}: patched {here} loader(s)")

print(f"Done. {total} CMS loader(s) now read whole files.")
