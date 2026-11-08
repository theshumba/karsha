"""RETIRED. This replaced pages with stubs; the full site was restored on request. Kept for reference only."""
"""Prepares the tree for publishing. Idempotent.
 - pages that asserted facts that are not true of Karsha become honest "coming soon" stubs
 - every kept page gets the Karsha stylesheet, the language toggle, a favicon and noindex
Originals stay in git history."""
import os, re
KEEP = {"index.html", "login/index.html", "signup/index.html"}
SKIP = {".git", ".mirror-cache", "verify-shots", "docs", "platform", "assets"}
STUB = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Karsha</title><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/karsha.css"></head><body style="margin:0;background:#0b0c10"><div class="kr-stub">
<header><a class="lg" href="/"><img src="/assets/karsha-mark.svg" width="28" height="28" alt="">Karsha</a></header>
<main><h1>%(h)s</h1><p>%(p)s</p><div class="row"><a class="b p" href="/platform/">Open the platform</a><a class="b" href="/">Back to home</a></div></main></div>
<script src="/assets/karsha-i18n.js"></script></body></html>"""
INJECT = ('<meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/karsha.css">'
          '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">')
SCRIPT = '<script defer src="/assets/karsha-i18n.js"></script>'
stubs = kept = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith(".html"): continue
        p = os.path.normpath(os.path.join(root, f))
        if p in KEEP:
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            if "karsha-i18n.js" not in s:
                s = re.sub(r'<link[^>]*rel="icon"[^>]*>', "", s)
                s = s.replace("</head>", INJECT + "</head>", 1).replace("</body>", SCRIPT + "</body>", 1)
                open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)
            kept += 1
        elif p == "404.html":
            open(p, "w").write(STUB % {"h": "Page not found", "p": "That page does not exist. You can go back to the home page or open the platform."}); stubs += 1
        else:
            open(p, "w").write(STUB % {"h": "This page is being built", "p": "Karsha is opening in stages. The platform is open now: savings, spot trading and futures at live prices."}); stubs += 1
open("robots.txt", "w").write("User-agent: *\nDisallow: /\n")
print("stubs", stubs, "kept", kept)
