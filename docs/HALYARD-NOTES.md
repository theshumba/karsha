# Halyard mirror, notes

Source: https://convex-motivation-500539.framer.app (a paid Framer template,
"Halyard", by Solo Foundry). This is a pristine, de-Framered static mirror. No
rebrand yet: every name, number, team member and logo on screen is still the
template's placeholder content.

## What the mirror is

- 76 pages: home, markets, trade, wallet, earn, launchpad, card, pay,
  institutions, security, fees, api, status, learn, blog, help, about, team,
  careers, press, referral, app, contact, signup, login, legal, plus nested
  market, earn, launchpad, careers, help, learn and blog detail pages.
- Pixel diff against the live site: 76 of 76 routes under 0.9%, heights matching
  exactly, 0 console errors, 0 failed requests.

## Fixes made to the raw mirror

The mirror tooling missed three things that broke the site off Framer. All found
by rendering every page in a real browser and fixed:

1. The smooth-scroll library (`lenis`) was never downloaded, so every page threw
   on load. Pulled it from source.
2. Eleven card and team photos were saved under mangled names and 404'd. Re-downloaded.
3. Eight of the nine crypto-data loaders still asked for byte-ranges only
   Framer's own servers answer, which crashed `/referral` to a blank page and
   errored every markets page. Patched all of them to read whole files, the same
   way the hardening script fixes the first one. (`docs/patch-cms-loaders.py`.)

## Author chrome removed

The template author (Solo Foundry) pinned their own links to every page: a
footer credit to solofoundryhq.com, a Lemon Squeezy "buy this template" checkout
and a framer.link store link. All hidden.

## Known quirk, inherited from the template, not a mirror fault

The footer legal links (Privacy, Terms, Cookies) and a few others (Status, App,
Team) do not navigate when clicked: they land back on the home page. The live
template does exactly the same thing, so the mirror is faithful. Every one of
those pages renders correctly when opened by its own URL. If this becomes a real
site these footer links need fixing, since broken Privacy and Terms links are a
compliance problem on a finance site.

## Owner-gated before this goes live as a real site

- It is a crypto exchange template full of invented proof: fake team, fake
  reserve and volume figures, a fake `api.halyard.exchange` endpoint, placeholder
  token launches. None of it is true and all of it needs replacing or removing in
  the rebrand pass.
- Which venture this is for, the brand, the real copy and real numbers.
- The template licence: this is a paid template. Using it commercially needs the
  licence bought from Solo Foundry.
