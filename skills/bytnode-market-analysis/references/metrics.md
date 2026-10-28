# Metrics in detail

Each entry: what it measures, where it lives (REST route · MCP field), units and dating, how to
read it, pitfalls. Field definitions are generated in the `bytnode-api` skill
(`references/routes.generated.md`); this file is about interpretation.

## Contents
- Funding · Open interest · Basis · Taker flow and CVD · Liquidations · Liquidation heatmap ·
  Order book · Inter-venue spread · Large trades · Options · Sentiment · Macro · On-chain

## Funding
- **Routes**: `/v1/funding/rate` (last settled 8 h period) and `/history`; `/v1/funding/next`
  (current estimate for the next settlement — what venue UIs call "current funding");
  `/v1/funding/cumulative` (sum over a rolling 24 h). MCP: `funding_rate`, `funding_next`,
  `funding_cumulative`; `rank_pairs(metric="funding_next")`.
- **Units**: `rate_pct` / `estimated_rate_pct` = percent **per 8 h**; `apr_pct` = annualised.
  Aggregated across venues, weighted by open interest. Normalised to 8 h whatever each
  venue's own settlement interval.
- **Dating**: `/funding/rate` `time` = start of the 8 h period, `settled_at` = when it was paid;
  `/funding/next` `time` = the settlement it forecasts.
- **Read**: positive = longs pay shorts. Persistent and rising positive funding with rising OI =
  leveraged long demand ("crowded long"). Deeply negative = crowded short (short-squeeze fuel).
  Compare with the pair's own 7–30 day history and with other pairs.
- **Pitfalls**: 0.01 means 0.01 %, not 1 %. One period is noise; look at the sequence.

## Open interest
- **Routes**: `/v1/oi` (latest), `/v1/oi/history` (per bucket), `/v1/oi/change` (rolling 60 s) and
  `/v1/oi/change/history` (per bucket). MCP: `oi` (rows carry `oi_usd` = oi × close), `oi_change`.
- **Units**: base asset (BTC). USD = oi × price of the same time.
- **Read** (with price over the same window): price ↑ OI ↑ new longs; price ↑ OI ↓ short covering;
  price ↓ OI ↑ new shorts; price ↓ OI ↓ long liquidations / deleveraging. Large OI growth with
  flat price = leverage building, often ahead of a large move.
- **Pitfalls**: `oi_change` on the latest route is one minute, not a day.

## Basis
- **Route**: `/v1/basis` (+ `/history`). MCP `basis`. `basis_pct` = (futures − spot) / spot × 100;
  `basis_value` in the quote currency; futures price OI-weighted across venues.
- **Read**: perpetual basis hovers near 0 (funding keeps it there). A widening positive basis =
  perp premium, leveraged buying; negative = discount, leveraged selling or hedging.
- **Pitfalls**: a few basis points of noise are normal; compare with its history.

## Taker flow and CVD
- **Routes**: `/v1/cvd` (+ `/spot`, `/futures`, `/history`): `buy_volume`, `sell_volume`,
  `net_volume` = buy − sell, base units, per bucket; `cvd_series` = cumulative delta inside the
  bucket (one point per finer step). `/v1/buy-sell-ratio`: `buy_ratio` = buy share (fraction).
  `/v1/trades/avg-size`, `/v1/trades-kline` (counts). MCP `cvd` adds `cumulative_net_volume`
  (running total over the returned rows).
- **Read**: positive `net_volume` = aggressive buyers dominated. Price up with negative delta =
  passive sellers absorbing / short covering; price flat with strong positive delta = absorption by
  sellers. Spot-led vs futures-led flow (compare `/spot` and `/futures`).
- **Pitfalls**: base units; `buy_sell_coverage_ratio` < 1 means part of the volume has no known
  side; `is_volume_estimated: true` flags estimated quantities.

## Liquidations
- **Routes**: `/v1/liquidations/cumulative` (rolling **5 minutes**) and `/history?timeframe=…`
  (per bucket); `/v1/liquidations/big-small-ratio` (counts and USD of large vs small, per bucket);
  `/v1/liquidations/events` (individual, plan-limited count). MCP `liquidations_cumulative`,
  `liquidations_big_small_ratio`, `liquidations_events`.
- **Units**: USD. `long_usd` = long positions liquidated (forced sells), `short_usd` = shorts
  liquidated (forced buys). On events, `side` is the side of the liquidated position.
- **Read**: a spike of long liquidations on a drop = capitulation / flush; repeated short
  liquidations on a rise = short squeeze. Compare a day with the average of the previous week.
- **Big vs small** (`/v1/liquidations/big-small-ratio`, per bucket): `big_count` / `big_usd` vs
  `small_count` / `small_usd` around a fixed USD threshold, `big_small_ratio` = big USD / small USD.
  A high ratio = a few large positions were forced out (whales, or one cascade); a low ratio =
  many small retail liquidations. It has no long/short split: pair it with `long_usd` /
  `short_usd` of `/v1/liquidations/cumulative/history` over the same buckets.
- **Pitfalls**: not every venue publishes liquidations: totals are a floor, not the whole market.

## Liquidation heatmap
- **Route**: `/v1/heatmap/clusters` (+ `/history`). `density_up/down` (score), `dist_up_ratio` /
  `dist_down_ratio` (fraction of price), `attraction_* = density / dist²`.
- **Read**: the cluster above holds estimated short liquidation levels, the one below long levels.
  A strong, close cluster can act as a magnet. It is a model estimate, not resting orders.

## Order book
- **Routes**: `/v1/orderbook` (+ `/spot`, `/futures`, `/history`): per bucket, the book at the END
  of the bucket, `ranges` from ±0.25 % to ±10 % of mid with bids/asks quantity (base) and USD.
- **Read**: imbalance = (bids − asks)/(bids + asks) per range; tight ranges matter for short-term
  moves, wide ranges for support/resistance depth. Thin books amplify moves.

## Inter-venue spread
- **Route**: `/v1/spread/interexchange`: `max_spread_bps` between venues, `high_venue`,
  `low_venue`, per-venue `premium_bps`. The ONLY route that names venues.
- **Read**: a widening spread signals stress or a venue-specific flow (premium on one venue).

## Large trades
- **Route**: `/v1/trades/large` (futures trades above `min_usd`, default 100,000). `side` = taker.
- **Read**: clusters of large aggressive trades in one direction; sum `value_usd`, don't count rows.

## Options (BTC, ETH)
- **Routes**: `/v1/options/summary`, `/put-call-ratio`, `/iv` (+ `/iv/klines`), `/max-pain`,
  `/oi/distribution`, `/expiry`, `/greeks`, `/volume`. MCP `get_options_data(asset=…)`.
- `put_call_ratio` = puts per call on open interest (`put_call_label`: < 0.7 `bullish`, > 1
  `bearish`). `iv_atm_30d_pct` = ATM implied vol at constant 30-day maturity, annualised %.
  `max_pain_strike_usd` per expiry (expiries at 08:00 UTC).
- **Read**: rising IV = market pricing bigger moves; high put/call = hedging demand; large OI at a
  strike near expiry can pin price. Compare IV with realised volatility of the candles.
- **Front vs 30-day IV**: `nearest_expiry` ATM IV above the 30-day IV = an event or the expiry
  itself priced at the front (term structure inverted); below = calm front. Max pain: compare it
  with the options `underlying_price_usd`, and only care within a day or two of that expiry, when
  its OI is large relative to the total.

## Sentiment
- `/v1/fear-greed` (alternative.me, since 2018) and `/v1/fear-greed/cmc` (CoinMarketCap): 0–100,
  `label` `extreme_fear` … `extreme_greed`, daily. Two different indices: name the one you cite.
- `/v1/altcoin-season`: 0–100 (≥ 75 altcoin season, ≤ 25 bitcoin season), 1-year range.
- `/v1/indices/cmc20`, `/cmc100`: index level and constituents. `/v1/global`: total market cap,
  volume, BTC/ETH dominance (percent).
- **Read**: extremes are contrarian signals at best; mid-range values say little.

## Macro
- `/v1/macro/risk`: `score` = share of risk-on signals × 100, `label`, `signals` with conditions;
  `oldest_input_date` bounds its freshness. `/v1/macro/net-liquidity`: Fed balance sheet − TGA −
  reverse repo, USD (weekly inputs). `/v1/macro/correlations`, `/momentum`, `/v1/macro?series=…`
  (FRED ids such as DGS10, CPIAUCSL, WALCL; catalogue: `/v1/macro/series`), `/v1/macro/intraday/history` (e.g. PAXGUSDT gold proxy).
- **Read**: rising net liquidity and risk-on regime are tailwinds for crypto historically; weekly
  and monthly inputs move slowly — do not over-read day-to-day changes.

## On-chain
- Bitcoin: `/v1/btc/mvrv` (valuation; source ~7 days behind), `/nvt`, `/active-addresses`,
  `/mempool`, `/fees`, `/mining`, `/network`. Ethereum: `/v1/eth/supply`, `/staking`, `/gas`,
  `/defi`, `/deflation`, `/squeeze`.
- **Read**: slow-moving context for valuation and network usage; never for intraday calls.
