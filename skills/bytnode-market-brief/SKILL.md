---
name: bytnode-market-brief
description: Use when asked for a crypto market brief, daily or morning report, market recap, newsletter section or "what happened in crypto" summary built from BytNode data — whether the data must first be fetched (REST or MCP) or is already provided as JSON.
---

# Writing a market brief from BytNode data

A brief is a fixed-shape, dated, sourced summary a reader can scan in two minutes. Every number
carries its unit and its time; what is missing is said, not invented; nothing is advice.
**REQUIRED BACKGROUND:** `bytnode-market-analysis` (how to read each metric) and `bytnode-api`
(units, windows).

## 1. Gather (skip what the user already provided)

Minimum set, in as few calls as the plan allows (`/v1/limits` or MCP `get_system_info` first):

| Section | MCP | REST |
|---|---|---|
| Market | `get_market_overview(fields=["global_market","fear_greed","fear_greed_cmc","altcoin_season"])` | `/v1/global`, `/v1/fear-greed`, `/v1/fear-greed/cmc`, `/v1/altcoin-season` |
| BTC, ETH (+ pairs the user follows) | `get_pair_brief(symbol=["BTCUSDT","ETHUSDT"])` (Traders+) | `/v1/snapshot?symbol=…&price_change=1&funding_rate=1&funding_next=1&basis=1&oi@1h=24&cvd@1h=24` |
| 24 h liquidations | `get_pair_data(fields=["liquidations_cumulative"], timeframe="1h", last="24h", detail="summary")` | `/v1/liquidations/cumulative/history?timeframe=1h&limit=24` (sum) |
| Movers | `rank_pairs(metric="price_change_pct", window="1d")` asc and desc; `rank_pairs(metric="funding_next")` | `/v1/price-change` per pair |
| Options (BTC, ETH) | `get_options_data(asset="BTC", fields=["options_summary"])` | `/v1/options/summary?asset=BTC` |
| Macro | `get_macro_data(fields=["macro_risk","macro_net_liquidity"])` | `/v1/macro/risk`, `/v1/macro/net-liquidity` |

On Free (no snapshot, no current values on the MCP), use short histories (`last="1h"`) and say
the brief is built on the last closed hour. Skip a section the plan does not open, and say so.

## 2. Check before writing

- **As-of**: the latest data `time`, in UTC. If the user says "morning" but the data is from the
  afternoon, write the real time in the header rather than pretending.
- **Windows**: which figures are 24 h, which are one hour, which are 5 minutes or 1 minute
  (`/v1/liquidations/cumulative` = 5 min; `/v1/oi/change` = 1 min). Never label a short window "24 h".
- **Units**: funding % per 8 h (with APR), base-unit volumes and OI (USD conversions labelled).
- **Staleness**: macro and on-chain inputs are days old by nature — give their date.

## 3. Write — use `assets/brief_template.md`

Keep the section order and headings so successive briefs compare. Adapt the rows to the data:
drop a row or column the data cannot fill (e.g. ETH when only BTC was provided) and list it under
Data gaps; add rows for useful data the template lacks (order book imbalance, large vs small
liquidations). The "Change" columns need a baseline: fetch it (`/v1/global/history?timeframe=1d&limit=2`,
the pair's `/history`) or write "—". Rules:
- Lead line: the one thing that matters today, with its number.
- One table per section, one short "read" line under it; no paragraph longer than three lines.
- Comparisons over levels: "funding eased from 0.0084 % to 0.0072 % per 8 h", "liquidations 2.4× the
  7-day daily average" — if no baseline was fetched, say "no baseline".
- **Data gaps** section always present: what was not available or not fetched, and why.
- Close with "Data: BytNode (bytnode.com), as of <time> UTC. Not investment advice."
- 300–500 words of prose (tables not counted) for a daily brief unless asked otherwise.

## Common mistakes

- An undated brief, or "this morning" on afternoon data.
- Mixing windows (a 5-minute liquidation figure in a "24 h" table).
- Inventing the missing pieces (24 h change, ETH data) instead of listing them as gaps.
- Buy/sell calls, price targets, "expect a bounce".
- A wall of numbers with no read: every table needs its one-line interpretation.
