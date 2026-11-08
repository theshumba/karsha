#!/usr/bin/env python3
"""Pull Framer's per-page inline CSS out into one shared stylesheet.

WHY: Framer inlines the CSS a page uses into the page. That is right for a
12-page template and wrong for a 900-page one: the same 148KB of rules would
ship on every single place page, uncached, on the one-bar connection this site
is actually used on. Lifted into one file it is fetched once and cached.

The join is only safe if no selector appears twice with two different bodies,
because then order decides the winner and a union has no honest order. The
splitter below is brace-aware so @media and @font-face survive, and the build
refuses to continue if it finds a genuine conflict.
"""
import re
from collections import OrderedDict

STYLE_RE = re.compile(
    r'<style([^>]*)>(.*?)</style>', re.S | re.I)


def split_rules(css):
    """Top-level rules, brace-aware. Returns [(selector, whole_rule)]."""
    out = []
    depth = 0
    start = 0
    i = 0
    n = len(css)
    while i < n:
        c = css[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                rule = css[start:i + 1].strip()
                if rule:
                    sel = rule.split("{", 1)[0].strip()
                    out.append((sel, rule))
                start = i + 1
        i += 1
    tail = css[start:].strip()
    if tail:
        out.append((tail, tail))
    return out


class Joiner:
    """Accumulates rules across pages, first-seen order, conflict-aware."""

    def __init__(self):
        self.rules = OrderedDict()       # whole rule -> whole rule
        self.by_selector = {}            # plain selector -> the rule that set it
        self.conflicts = []

    def add_css(self, css):
        """Dedupe on the whole rule, not the selector.

        @font-face and @media all share one "selector", so keying on that
        reported 7,517 conflicts that were simply the same rule seen 74 times.
        Identical rules collapse; a selector carrying two different bodies is a
        real cascade question and gets recorded.
        """
        for sel, rule in split_rules(css):
            if rule in self.rules:
                continue
            self.rules[rule] = rule
            if sel.startswith("@"):
                continue
            prev = self.by_selector.get(sel)
            if prev is not None and prev != rule:
                self.conflicts.append((sel, prev, rule))
            else:
                self.by_selector[sel] = rule

    def css(self):
        return "\n".join(self.rules.values())


def page_style_blocks(html):
    """[(attrs, css)] for every <style> in the page."""
    return [(m.group(1), m.group(2)) for m in STYLE_RE.finditer(html)]
