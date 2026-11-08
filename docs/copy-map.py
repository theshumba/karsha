"""Exact-string copy swaps for the Karsha brief (savings, spot, futures, leverage, 60 day notice).
Applied to every page and script. Idempotent. Run after rebrand.py.
Anything not listed here is still template copy: see docs/KARSHA-NOTES.md."""
import os
B = "Karsha"
PAIRS = [
 # hero
 ("The exchange that shows the *real* price.", "Earn, trade and grow in *one* account."),
 ("The exchange that shows the <em>real</em> price.", "Earn, trade and grow in <em>one</em> account."),
 ("The exchange that shows the real price.", "Earn, trade and grow in one account."),
 ("Crypto exchange · Web3 wallet", "High yield savings · Futures · Trading"),
 (f"{B} is a crypto exchange and Web3 wallet: trade 200+ assets at the real price, hold your keys, earn on what you keep.",
  f"{B} gives you high yield savings, swing and day trading, and futures with optional leverage, all in one account."),
 # fabricated registration claim: removed, not reworded
 (f"{B} Markets Ltd is registered as a virtual asset service provider. Crypto assets are volatile; you may lose what you put in.",
  "Crypto assets are volatile and leverage multiplies losses. You may lose some or all of the money you put in."),
 (f"{B} Markets Ltd is registered as a virtual asset service provider.", ""),
 # page titles
 (f"{B} | Crypto Exchange, Web3 Wallet, DeFi &amp; Token Launch", f"{B} | High Yield Savings, Futures &amp; Trading"),
 (f"{B} | Crypto Exchange, Web3 Wallet, DeFi & Token Launch", f"{B} | High Yield Savings, Futures & Trading"),
 # stat strip: invented figures replaced with facts about the product itself
 ('="$2.4B"', '="60 days"'), ('>$2.4B<', '>60 days<'), ('`$2.4B`', '`60 days`'),
 ('="200+"', '="12"'), ('>200+<', '>12<'), ('`200+`', '`12`'),
 ('="140"', '="20x"'), ('>140<', '>20x<'), ('`140`', '`20x`'),
 ('="99.99%"', '="24/7"'), ('>99.99%<', '>24/7<'), ('`99.99%`', '`24/7`'),
 ('>24h volume<', '>savings withdrawal notice<'), ('>assets listed<', '>markets to trade<'),
 ('>countries<', '>maximum leverage<'), ('>uptime, 12 months<', '>markets, always open<'),
 (':24h volume;', ':savings withdrawal notice;'), (':assets listed;', ':markets to trade;'),
 (':countries;', ':maximum leverage;'), (':uptime, 12 months`', ':markets, always open`'),
 ("Audited Q3 2026", "Interest accrues daily"), ("Spot and perpetuals", "Spot and futures"),
 ("Licensed in 31 of them", "Leveraged accounts available"), ("Status page, every minute", "Live market prices"),
 ("Trading desk · 24/7", "Trading · 24/7"),
 ("Real price.|*Your* keys.", "Clear terms.|*Your* account."),
 (" shows the price the market is paying, not a spread dressed up as one.", " shows you the live market price, the fee and the withdrawal notice before you commit."),
 ("assets, hold your own keys and earn on what you keep.", "assets, earn on your savings, and open futures when you are ready."),
 ("Prices refresh every second", "Illustrative home page. Live prices are in the platform."),
 ("200+ assets · Proof of reserves · 24/7 support", "12 markets · Spot and futures · Prices around the clock"),
 # earn: the 60 day clause
 ("Withdraw any time, no notice", "60 days notice to withdraw"),
 ("Backed by over-collateralised lending", "Interest accrues daily"),
]
SKIP = {".git", ".mirror-cache", "verify-shots", "docs", "platform"}
EXT = (".html", ".mjs", ".js", ".json")
n = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith(EXT): continue
        p = os.path.join(root, f)
        s = open(p, encoding="utf-8", errors="surrogateescape").read(); o = s
        for a, b in PAIRS: s = s.replace(a, b)
        if s != o:
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(s); n += 1
print("files changed:", n)
