---
name: bytnode-market-analysis
description: Use when interpreting crypto market data from BytNode — funding rates, open interest, basis, CVD and taker flow, liquidations, order book depth, liquidation heatmap, options (put/call, max pain, implied volatility), fear & greed, altcoin season, macro risk or net liquidity — to describe positioning, crowding, squeeze risk, sentiment or the state of a pair or of the whole market, from API responses, MCP tool results or a saved JSON file.
---

# Reading the market with BytNode data

BytNode numbers are aggregated across the major venues and come with exact units and timestamps.
A good read states **what the data says, in its units, at its time**, compares it with a baseline,
and separates observation from interpretation. It never gives trading advice.

**REQUIRED BACKGROUND:** the units and timing rules of the `bytnode-api` skill. The three that
break analyses most often are repeated here.

## Three traps to clear before any interpretation

1. **Units.** `_pct` is already a percent: funding `rate_pct: 0.0084` = **0.0084 % per 8 h**
   (≈ 9.2 % a year, see `apr_pct`), not 0.84 %. `_ratio` shares are fractions (`buy_ratio: 0.519`
   = 51.9 %). `oi`, `volume`, `buy_volume`, `net_volume` are in **base units** (BTC), never USD:
   convert with a price of the same time and say it is converted.
2. **Windows.** Check `window_s` / `timeframe` / `step` before naming a period.
   `/v1/liquidations/cumulative` is the **last 5 minutes**; `/v1/oi/change` the last minute; a 1h
   bucket dated 14:00 covers 14:00–15:00. Never call a 5-minute figure "today".
3. **Freshness.** Compare every row's `time` with `server_time`. On-chain, macro and ETF series are
   days old by nature; a market feed minutes old is stale (check `/v1/status` or MCP `warnings`).
   `is_closed: false` is provisional.

## Workflow

1. **Frame**: which asset(s), which horizon (intraday / days / weeks), which question.
2. **Gather** the minimum set (see Recipes). One call where possible: MCP `get_pair_brief`, or
   `/v1/snapshot` on REST (Traders+); otherwise the individual routes.
3. **Normalise**: units → percent / USD, every figure with its time.
4. **Compare with a baseline**: the same metric's own history (7–30 days via `/history` or MCP
   `summary`), and other pairs (`rank_pairs`). A level means little alone; a change or an
   extreme relative to its history means something.
5. **Combine** signals (positioning + flow + price), note agreements and contradictions.
6. **Report** in the format below, including what is missing.

## How to read each metric (summary — details in `references/metrics.md`)

| Metric | Neutral / reference | Reads as |
|---|---|---|
| Funding (`rate_pct`, per 8 h) | ≈ 0.01 %/8 h (≈ 11 % APR) is the common venue default | well above and rising = longs paying to stay long (crowded long); negative = shorts paying |
| Open interest (`oi`, base units) | its own trend | price ↑ + OI ↑ = new longs; price ↑ + OI ↓ = short covering; price ↓ + OI ↑ = new shorts; price ↓ + OI ↓ = long liquidation / deleveraging |
| Basis (`basis_pct`, perp − spot) | ≈ 0 on perpetuals | positive = perp premium (leveraged demand); negative = discount |
| Taker flow (`net_volume`, `buy_ratio`) | `buy_ratio` 0.5 | aggressive buying/selling; divergence with price = absorption |
| Liquidations (`long_usd`, `short_usd`) | its own history | `long_usd` = LONG positions liquidated (price fell into them) |
| Heatmap (`attraction_up/down`, `dist_*_ratio`) | — | estimated liquidation clusters that may attract price; an estimate, not orders |
| Order book (`ranges`) | bids ≈ asks | resting liquidity near the mid; imbalance = (bids − asks)/(bids + asks) |
| Put/call (`put_call_ratio`, OI) | `put_call_label`: < 0.7 bullish, > 1 bearish | puts per call; hedging demand |
| ATM IV (`iv_atm_30d_pct`) | its own history | expected volatility, annualised % |
| Max pain (`max_pain_strike_usd`) | — | strike where option buyers lose most at expiry; weak pull, mainly near expiry |
| Fear & Greed (`value` 0–100, `label`) | 50 | `extreme_fear` … `extreme_greed`; contrarian at extremes |
| Altcoin Season (`value` 0–100) | — | ≥ 75 altcoin season, ≤ 25 bitcoin season |
| Macro risk (`score`, `label`) | 50 | share of risk-on signals; check `oldest_input_date` |

Reference levels are rules of thumb, not BytNode definitions: present them as such.

## Report format

```
**<ASSET> — <one-line read>** (data as of <latest row time, UTC>)

| Signal | Value | Read |
|---|---|---|
| Funding | 0.0084 %/8 h (9.2 % APR), next est. 0.0072 % | mildly positive, easing |
| … | … | … |

Positioning: … Flow: … Liquidations: … Sentiment/macro: …
What would change this read: …
Not covered / caveats: <missing data, stale feeds, estimated USD conversions, 5-min windows…>
```

Lead with the conclusion, then the evidence. Quantify ("OI +2.1 % in 24 h, to 370,500 BTC ≈
29.9 bn USD at 80,650"), never "OI is high". Say "the data is consistent with…", not "price will…".

**When the data is incomplete** (one snapshot, no history, a family outside the plan): give the
read the data supports, mark each missing piece explicitly ("no OI history: cannot say whether
leverage is building"), lower the confidence of the conclusion, and name the call that would fill
the gap. A level without its own history gets "no baseline available", not a verdict.

**Several prices in one capture are normal**: the last trade (`/v1/price-change`), the basis spot
(venue prices at the basis instant), the options underlying (the options venues' index) and a
candle close differ by a few basis points and seconds. Quote the one that matches the metric
(OI × candle close, max pain vs the options underlying) and say which.

## Recipes

- **State of a pair**: price change (1h/4h/1d), funding settled + next, OI and its 24 h change,
  basis, last closed 1h CVD and buy ratio, liquidations over 24 h (sum of 1h rows), fear & greed.
  MCP: `get_pair_brief`. REST: `/v1/snapshot?symbol=…&price_change=1&funding_rate=1&funding_next=1&basis=1&oi@1h=24&cvd@1h=24&liquidations_cumulative=1&fear_greed=1`
  (liquidations over 24 h: `/v1/liquidations/cumulative/history?timeframe=1h&limit=24`).
- **Crowding / squeeze risk**: funding vs its 30-day history and vs other pairs (`rank_pairs`
  `funding_next`); OI trend; basis; heatmap attraction above vs below. Crowded long + rising OI +
  liquidation cluster below = long-squeeze risk (and the mirror for shorts).
- **Market regime**: total market cap and BTC dominance (`/v1/global`), fear & greed (both
  indices), altcoin season, macro risk and net liquidity trend, BTC options IV and put/call.
- **Screening**: `rank_pairs` on `funding_next`, `oi_usd`, `volume_usd_24h`, `price_change_pct`,
  `rsi` — then drill into the outliers.

## Common mistakes

- Any of the three traps above.
- Reading `long_usd` as "longs opened" (it is longs liquidated).
- Comparing a perp's funding with a different period length (all BytNode funding is per 8 h).
- Judging a level without its history; calling one 1h bucket a trend.
- Attributing a number to an exchange (data is aggregated; only `/v1/spread/interexchange` names venues).
- Filling a missing field with a guess: say it is missing and why (`unavailable`).
- Recommending a trade, a target or a position size.
