#!/usr/bin/env python3
"""Turn a hardened Framer mirror into a plain static shell.

Three things happen here and nothing else. Content comes later, so this pass can
be checked with a pixel diff against the live template: if the shell is right,
the site still looks exactly like Listora.

  1. staticise   drop the Framer runtime, reveal the appear animations
  2. css         lift the per-page inline CSS into one shared stylesheet
  3. paths       make src and srcset root-absolute like harden.py did for href

WHY (2) MATTERS HERE AND DID NOT MATTER FOR THE TEMPLATE: Framer inlines the
CSS a page uses into that page, about 148KB of it. That is fine across 12 pages
and absurd across 900, on a site whose brief says every kilobyte is a real cost
because it is used on one bar of signal. Lifted out, it is 457KB fetched once.

WHY (3): harden.py made hrefs root-absolute but left asset paths relative with a
../ depth per page. This build writes pages at depths the template never had
(/place/oh/slug/), so a relative asset path would resolve to nothing. Root
absolute is safe because the site is served from a domain root, which is already
required by the hrefs.

  python3 docs/lift-css.py            # rewrite every page in place
  python3 docs/lift-css.py --report   # print sizes, change nothing

Needs cssjoin.py beside it. Run it AFTER detach.py and harden.py and BEFORE the
content pass, then pixel-diff against live: if the shell is right the site still
looks exactly like the template.
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "docs"))

from cssjoin import Joiner, split_rules          # noqa: E402
from staticise import staticise                  # noqa: E402

SHARED_CSS = "assets/css/wcih-framer.css"

# Which inline blocks get lifted. The other two stay put on purpose:
#   data-framer-breakpoint-css  is page-specific and tiny
#   data-framer-html-style      sets the page background, and it DIFFERS by page
#                               (light pages vs the dark 404), so a union would
#                               give every page the last one seen.
LIFT = ("data-framer-font-css", "data-framer-css-ssr-minified")

STYLE_RE = re.compile(r"<style([^>]*)>(.*?)</style>", re.S | re.I)


def routes():
    cfg = json.loads((ROOT / "clone.json").read_text())
    out = []
    for route in cfg["pages"]:
        rel = urllib.parse.unquote(route.strip("/"))
        path = ROOT / ((rel + "/index.html") if rel else "index.html")
        if path.exists():
            out.append((route, path))
    return out


def lifted(attrs):
    return any(k in attrs for k in LIFT)


def collect_css(pages):
    """Fonts first, then component rules, matching each page's own order."""
    fonts, comps = Joiner(), Joiner()
    for _, html in pages:
        for m in STYLE_RE.finditer(html):
            attrs, css = m.group(1), m.group(2)
            if "data-framer-font-css" in attrs:
                fonts.add_css(css)
            elif "data-framer-css-ssr-minified" in attrs:
                comps.add_css(css)
    return fonts, comps


def strip_lifted(html):
    """Remove the lifted style blocks, leaving a marker at the first one."""
    seen = [False]

    def sub(m):
        if not lifted(m.group(1)):
            return m.group(0)
        if not seen[0]:
            seen[0] = True
            return f'<link rel="stylesheet" href="/{SHARED_CSS}"/>'
        return ""

    return STYLE_RE.sub(sub, html)


# ---- inline style hoisting -------------------------------------------------
# Framer writes the same style attribute over and over: 33,609 attributes across
# the 74 template pages, but only 298 distinct values, 4.0MB of markup. Applied
# to a 900-page site that is 40MB of duplicated text. Hoisted into classes it is
# 47KB in the shared stylesheet.
#
# An inline style beats every class rule, so the hoisted rule has to win the
# cascade the same way. It is written last in the file and its selector repeats
# the class five times, which gives specificity 0,5,0: higher than anything
# Framer generates, and still losing to !important exactly as an inline style
# would.
# A whole opening tag, attributes intact. The first version of this matched only
# the part of the tag BEFORE style=, so when Framer wrote style before class the
# hoisted class was appended as a SECOND class attribute and the browser kept the
# first, silently dropping framer-text from three headings per page. Match the
# whole tag or do not match it.
TAG_RE = re.compile(r"""<([a-zA-Z][\w:.-]*)((?:[^>"']|"[^"]*"|'[^']*')*)>""")
STYLE_IN_ATTRS = re.compile(r'\s*style="([^"]*)"')
CLASS_IN_ATTRS = re.compile(r'\sclass="([^"]*)"')


class StyleHoist:
    def __init__(self):
        self.index = {}

    def name(self, value):
        if value not in self.index:
            self.index[value] = "wq%d" % len(self.index)
        return self.index[value]

    def apply(self, html):
        def sub(m):
            tag, attrs = m.group(1), m.group(2)
            found = STYLE_IN_ATTRS.search(attrs)
            if not found or not found.group(1).strip():
                return m.group(0)
            cls = self.name(found.group(1))
            attrs = attrs[:found.start()] + attrs[found.end():]
            if CLASS_IN_ATTRS.search(attrs):
                attrs = CLASS_IN_ATTRS.sub(
                    lambda c: ' class="%s %s"' % (c.group(1), cls), attrs, count=1)
            else:
                closing = ""
                if attrs.rstrip().endswith("/"):
                    attrs, closing = attrs.rstrip()[:-1], "/"
                attrs = attrs.rstrip() + ' class="%s"' % cls + closing
            return "<%s%s>" % (tag, attrs)

        return TAG_RE.sub(sub, html)

    def css(self):
        out = []
        for value, cls in self.index.items():
            sel = "".join("." + cls for _ in range(5))
            out.append("%s{%s}" % (sel, value.rstrip(";")))
        return "\n".join(out)


# The depth prefix is optional: at the site root Framer writes a bare
# assets/images/x.jpg with no ./ in front of it, so a pattern that required one
# left every asset path on the home page relative.
ASSET_ATTR = re.compile(r'(\s(?:src|href)=")((?:\.{1,2}/)*)(assets/[^"]*)"')
SRCSET = re.compile(r'(\ssrcset=")([^"]*)"')
REL_ASSET = re.compile(r"(?<![/\w.])(?:\.{1,2}/)*(assets/)")


def absolutise_assets(html):
    html = ASSET_ATTR.sub(lambda m: f'{m.group(1)}/{m.group(3)}"', html)

    def fix_srcset(m):
        fixed = REL_ASSET.sub(r"/\1", m.group(2))
        return m.group(1) + fixed + '"'

    html = SRCSET.sub(fix_srcset, html)
    # url(../../assets/...) inside remaining inline styles
    html = re.sub(r"url\((\"|\')?(?:\.{1,2}/)+assets/", r"url(\1/assets/", html)
    return html


def shellify(html, hoist=None):
    html = absolutise_assets(strip_lifted(staticise(html)))
    if hoist is not None:
        html = hoist.apply(html)
    return html


def main():
    report = "--report" in sys.argv
    pages = [(route, path, path.read_text()) for route, path in routes()]
    stat = [(r, p, staticise(h)) for r, p, h in pages]
    fonts, comps = collect_css([(r, h) for r, _, h in stat])
    css = fonts.css() + "\n" + comps.css()

    hoist = StyleHoist()
    before = sum(len(h) for _, _, h in pages)
    out = [(p, hoist.apply(absolutise_assets(strip_lifted(h)))) for _, p, h in stat]
    after = sum(len(h) for _, h in out)
    css = css + "\n" + hoist.css()

    print(f"pages            {len(pages)}")
    print(f"shared stylesheet {len(css):,} bytes  "
          f"({len(fonts.rules)} font rules, {len(comps.rules)} component rules)")
    print(f"style values     {len(hoist.index)} distinct, hoisted to classes")
    print(f"html total       {before:,} -> {after:,} "
          f"({100 * after / before:.0f}%)")
    if comps.conflicts:
        print(f"selector conflicts kept both ways: {len(comps.conflicts)}")
    if report:
        return

    target = ROOT / SHARED_CSS
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(css)
    for path, html in out:
        path.write_text(html)
    print(f"wrote {SHARED_CSS} and {len(out)} pages")


if __name__ == "__main__":
    main()
