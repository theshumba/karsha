# Karsha, working notes

Brand Karsha (swap with `python3 docs/rebrand.py <Name>` on a clean tree, then
`docs/copy-map.py`, and change `CFG.brand` plus the title in `platform/index.html`).

## What exists

- The Halyard template, rebranded. Home hero, stat strip, footer risk line, the Earn "60 days notice"
  line and page titles now describe savings, spot trading, futures and leveraged accounts.
- `/login` and `/signup` on the site now open the platform.
- `/platform/` is a working trading platform in one file: sign up and log in, overview, markets,
  spot trading (market and limit, swing and day), futures (long and short, stop loss, take profit,
  liquidation), a leveraged account switch (5x standard, 20x enabled), savings with a 60 day
  withdrawal notice and daily interest, wallet, activity, settings. Live prices and charts come from the
  free Binance market data endpoint (CoinGecko as fallback). Chart library is vendored in
  `platform/lwc.js` (TradingView Lightweight Charts, Apache 2.0).
- All terms (fees, leverage caps, notice days, savings rates) sit in `CFG` at the top of the script.

## Simulated, not real

Balances, deposits and withdrawals are simulated and stored in the visitor's browser only. Accounts
are not shared between devices and there is no server. Real customer money needs a regulated
custodian, a backend with real authentication, and UK FCA registration or an approved promoter before
the site markets crypto, leverage or savings yield to UK customers. Flip `CFG.simulated` once that is real.

## Still template copy (owner-gated)

Rest of the 76 pages still say what the template says. Known problems to rewrite or remove:
- Earn page and the six earn product pages: invented rates (up to 14.2%), lock terms and "backed by"
  claims. Platform placeholders are 4.0% / 1.5% / 2.5% and are not sourced.
- Home price ticker and hero chart show template prices, not live prices.
- About, Team, Press, Careers, Security, Fees, Status, API, Launchpad, Card, Pay, Institutions:
  invented team, reserve and volume figures, audit and licence claims, a fake `.example` API domain.
- FAQ and blog posts mention "2.1 million accounts", "140 countries", self-custody.
- Footer Privacy, Terms and Cookies links land on the home page (inherited from the template).
- Template licence must be bought from Solo Foundry before this goes live commercially.
