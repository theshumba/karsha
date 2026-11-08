"""Brand swap. Change BRAND and rerun on a pristine tree (git tag pristine or reset)."""
import os, re, sys
BRAND = sys.argv[1] if len(sys.argv) > 1 else "Karsha"
DOMAIN = BRAND.lower() + ".example"
SKIP = {".git", ".mirror-cache", "verify-shots", "docs"}
EXT = (".html", ".mjs", ".js", ".json", ".css", ".txt", ".xml")
n = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith(EXT): continue
        p = os.path.join(root, f)
        s = open(p, encoding="utf-8", errors="surrogateescape").read()
        o = s
        s = s.replace("halyard.exchange", DOMAIN)
        s = re.sub(r"Halyard(?!-card)", BRAND, s)
        s = s.replace("HALYARD_KEY", BRAND.upper() + "_KEY")
        if s != o:
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(s); n += 1
print("files changed:", n)
