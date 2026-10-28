# BytNode MCP tools

> Generated from https://api.bytnode.com/.well-known/mcp/server-card.json (MCP surface **4.1.0**, REST contract 3.0.1) by `tools/generate_references.py`. Do not edit by hand: regenerate.

Endpoint: `https://api.bytnode.com/mcp` (Streamable HTTP). Auth: `X-API-KEY` header or `Authorization: Bearer <key>`; connectors (claude.ai, ChatGPT, Claude Code) sign in with OAuth instead.

## Server instructions (sent to the model at connection)

BytNode MCP 4.1.0: crypto market data aggregated across the major spot and perpetual venues (never named, except spread_interexchange): pairs, options, spot ETFs, macro, on-chain, sentiment. Every response carries mcp_version: if it differs from 4.1.0, your client holds older tool definitions (reconnect it).

READ FIRST
- Units: _pct = percent (58.5 = 58.5 %), _ratio = fraction (0.585 = 58.5 %), _bps, _usd, _s, _count. Prices in the quote currency, quantities in base units; oi_usd = oi x close. describe_fields gives the unit of every column and the thresholds of every label.
- Time: ISO 8601 UTC; a row is dated at the START of its bucket (ranges.to too); a current value is the last CLOSED bucket. Rows come newest first. A regular series ALWAYS gives first_time and step_s, whatever its row count (row i = first_time + i x step_s); events (trades, liquidation events) and tables keep a time column, a block `date` (rows give HH:MM:SS) or one `time` (every row at that instant).
- The get_* tools and rank_pairs answer {mode, data, ...}: data has one key per series; an empty or not applicable series is null, and unavailable says why.
- summary, per series, on the WHOLE series: latest, oldest, min/max with their time, mean, sum and `sums` (flows), by_side (trades, liquidation events) or change (states); candles add high_max/low_min. For a total, an extreme or a change read summary, not the rows; detail="summary" keeps one row per series.
- ranges: what is really covered (row_count of total_row_count, from, to, note). Never conclude on a period without it. unavailable: not_applicable, no_api_key (not collected: NOT a market fact), no_data. warnings: a late feed (never present it as current) or an ignored parameter. freshness.age_s = age of the source feed, not of the row.

MODES: no window = current value (limit=N: the N latest points). since_ms/until_ms (epoch ms, ISO date or '48h' ago) or last='48h' = history, closed buckets only (last='24h': 24 buckets; since_ms='24h': the 23 after it). Without timeframe the server picks about 200 points. FIELDS tags: tf = takes timeframe; now = no dated history; live = live=true adds the open candle; N<=x = max limit (else 1000); a parameter name = only these fields take it. Several fields per call; with several pairs every key is '<pair>/<field>'.

SIZE: 6,000 estimated tokens by default, max_tokens up to 16,000. Beyond it series keep their newest rows and ranges.<key>.missing (several pairs: missing.<field>; ranges, omitted_columns identical for every pair are written once, under '<field>') says how to get the rest, often the max_tokens that fits; read_export(export_id, key, offset) pages the full data (one hour, same key).

PLANS: every plan works but reads only its own data (get_system_info). Free has no snapshot family: ask last='1h' instead of current values. Outside the plan: 403 plan_family or history_depth. api_requests = quota requests used by the call.

ERRORS: isError=true, text "Error (HTTP NNN): ...", structuredContent.error {status, code, message, param?, hint?, retry_after_s?}; wrong_tool: hint names the right tool; 429: retry after the delay. Every code: resource bytnode://schemas/error. Field definitions: describe_fields (free).

## Tools

### `describe_fields`

Full definition of data-tool fields, and of the output keys liquidations_24h, oi_usd, cumulative_net_volume, ranking: columns, unit of each column, label thresholds, dating, tool, timeframes, history depth, extra parameters. Free, no quota.

Parameters:
- `fields` **(required)** (array): Field names.

### `get_macro_data`

US macro: one FRED `series` (macro; without series, the latest of every series), an intraday instrument (macro_intraday, series required), and computed fields with no target. Series: get_system_info catalogs. No window = current value; since_ms/until_ms/last = history. Rows newest first, dated at the START of their bucket (first_time + i x step_s); for a total, an extreme or a change read summary, for the period covered read ranges; null + unavailable = no data; _pct = percent, _ratio = fraction; every unit: describe_fields. timeframe: macro_intraday only. A daily or monthly series is legitimately days or weeks old.

EXAMPLE: 10-year yield: series=DGS10, fields=["macro"]

FIELDS:
- macro: US macro: one `series`, or the latest of every series. [series optional]
- macro_intraday: Intraday candles of a macro instrument. [tf with N or history, needs series]
- macro_net_liquidity: Fed net liquidity, USD (balance sheet - TGA - reverse repo).
- macro_correlations: Correlations between crypto and macro series. [now, 1 point]
- macro_momentum: 30-day and 90-day momentum of the macro series. [now, 1 point]
- macro_risk: Macro risk-on / risk-off score with its signals. [now, 1 point]

Parameters:
- `fields` **(required)** (array) — one of macro, macro_intraday, macro_net_liquidity, macro_correlations, macro_momentum, macro_risk: Fields (FIELDS below).
- `limit` (integer): N latest points per series (default 1).
- `series` (string): FRED series (DGS10) or intraday instrument (PAXGUSDT).
- `timeframe` (string) — one of 1m, 5m, 15m, 1h, 4h, 1d: Step of macro_intraday.
- `since_ms` (string): History start: epoch ms, ISO date or '48h' ago.
- `until_ms` (string): History end.
- `last` (string): History over the last '48h' / '30d' (whole buckets).
- `columns` (array): Columns to keep, e.g. ["close", "volume"].
- `detail` (string) — one of compact, full, summary: summary: one row per series + summary; full: every column.
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_market_indicators`

Technical indicators on the klines of 1 to 10 pairs (OBV, MFI, AD, ADOSC: aggregated spot volume; stablecoin pair: its keys null, unavailable not_applicable). Up to 50, several of a type (rsi_7, rsi_21). data: one series per '<id>@<timeframe>' ('<pair>/<id>@<timeframe>' with several pairs), newest first; indicators.<id>: its type and parameters; limit 1 = the latest CLOSED candle. One quota request per pair.
limit + warmup <= 1000 (warmup: period; ema 3x, rsi/atr/keltner 5x, adx 14x, macd 3x slow + signal, sar 200; the 422 gives the largest period). obv, ad: cumulative, read the slope only.
OUTPUTS: stoch {k, d}; macd {macd, signal, histogram}; bb, keltner, donchian {upper, middle, lower}; ichimoku {tenkan_sen, kijun_sen, senkou_a, senkou_b}; others one value.
EXAMPLE: indicators=[{"id": "rsi_7", "type": "rsi", "period": 7}, {"id": "macd", "type": "macd"}]

Parameters:
- `symbol` **(required)** (array): 1 to 10 pairs, e.g. ["BTCUSDT"].
- `timeframe` **(required)** (string) — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w: Candle step.
- `indicators` **(required)** (array): {id (your unique name), type, ...its own optional parameters, flat}. Defaults: rsi(period=14), ema(period=20), sma(period=20), bb(period=20, std=2.0), atr(period=14), stoch(k=14, d=3, smooth=3), macd(fast=12, slow=26, signal=9), obv(), ad(), adx(period=14), cci(period=20), willr(period=14), mfi(period=14), roc(period=10), donchian(period=20), adosc(fast=3, slow=10), sar(acceleration=0.02, maximum=0.2), keltner(period=20, multiplier=2.0), ichimoku(tenkan=9, kijun=26, senkou=52).
- `limit` (integer): N latest values (default 1).
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_market_overview`

The whole crypto market, no target. No window = current value; since_ms/until_ms/last = history. Rows newest first, dated at the START of their bucket (first_time + i x step_s); for a total, an extreme or a change read summary, for the period covered read ranges; null + unavailable = no data; _pct = percent, _ratio = fraction; every unit: describe_fields. timeframe: global_market only; the indices are daily.

EXAMPLE: dominance over 30 days: fields=["global_market"], timeframe=1d, last="30d"

FIELDS:
- global_market: Total market cap, volume, BTC and ETH dominance. [tf with N or history]
- fear_greed: Crypto Fear & Greed index (0-100) and label, daily.
- fear_greed_cmc: CMC's Fear & Greed index (0-100), not fear_greed.
- altcoin_season: Altcoin Season index (0-100) and yearly range.
- cmc20: CMC20 index level, constituents and 24h change.
- cmc100: CMC100 index level, constituents and 24h change.

Parameters:
- `fields` **(required)** (array) — one of global_market, fear_greed, fear_greed_cmc, altcoin_season, cmc20, cmc100: Fields (FIELDS below).
- `limit` (integer): N latest points per series (default 1).
- `timeframe` (string) — one of 1h, 4h, 1d: Step of global_market.
- `since_ms` (string): History start: epoch ms, ISO date or '48h' ago.
- `until_ms` (string): History end.
- `last` (string): History over the last '48h' / '30d' (whole buckets).
- `columns` (array): Columns to keep, e.g. ["close", "volume"].
- `detail` (string) — one of compact, full, summary: summary: one row per series + summary; full: every column.
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_onchain_data`

Bitcoin and Ethereum on-chain, no target. No window = current value; since_ms/until_ms/last = history. Rows newest first, dated at the START of their bucket (first_time + i x step_s); for a total, an extreme or a change read summary, for the period covered read ranges; null + unavailable = no data; _pct = percent, _ratio = fraction; every unit: describe_fields. timeframe: btc_fees only (others keep their source cadence); `dataset`: the btc_mining history.

EXAMPLE: MVRV over 90 days: fields=["btc_mvrv"], last="90d"

FIELDS:
- btc_network: Difficulty, block height, next adjustment.
- btc_mempool: Mempool size, fees and trend.
- btc_fees: Recommended fees, sat/vB, by urgency. [tf with N or history]
- btc_mining: Mining pool concentration, pool ranking and block rewards. [dataset in history]
- btc_mvrv: MVRV, label, 30-day change (source ~7 days behind).
- btc_nvt: NVT and NVT signal (label: the signal).
- btc_active_addresses: Active addresses, 7- and 30-day averages.
- btc_revenue_per_difficulty: Miner revenue per unit of difficulty, in USD.
- eth_supply: Supply, issuance, burn, net issuance.
- eth_gas: Gas prices (gwei) and block usage.
- eth_staking: Staking ratio, total staked, APR.
- eth_deflation: 24h burn and net issuance (and annualised).
- eth_defi: DeFi TVL, DEX volume, health ratio.
- eth_gas_momentum: Gas trend: 7-day vs 30-day averages.
- eth_squeeze: Supply squeeze index (staking, issuance).
- eth_price_btc: ETH price in BTC and USD, 7-day change.

Parameters:
- `fields` **(required)** (array) — one of btc_network, btc_mempool, btc_fees, btc_mining, btc_mvrv, btc_nvt, btc_active_addresses, btc_revenue_per_difficulty, eth_supply, eth_gas, eth_staking, eth_deflation, eth_defi, eth_gas_momentum, eth_squeeze, eth_price_btc: Fields (FIELDS below).
- `limit` (integer): N latest points per series (default 1).
- `timeframe` (string) — one of 1h, 4h, 1d: Step of btc_fees.
- `since_ms` (string): History start: epoch ms, ISO date or '48h' ago.
- `until_ms` (string): History end.
- `last` (string): History over the last '48h' / '30d' (whole buckets).
- `dataset` (string) — one of concentration, rewards, difficulty, fee_rates: btc_mining history (default concentration).
- `columns` (array): Columns to keep, e.g. ["close", "volume"].
- `detail` (string) — one of compact, full, summary: summary: one row per series + summary; full: every column.
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_options_data`

Options and spot ETFs of ONE asset (BTC or ETH, never a pair). No window = current value; since_ms/until_ms/last = history. Rows newest first, dated at the START of their bucket (first_time + i x step_s); for a total, an extreme or a change read summary, for the period covered read ranges; null + unavailable = no data; _pct = percent, _ratio = fraction; every unit: describe_fields.
- expiries=true: active expiries with, PER EXPIRY, OI calls/puts, put/call, max pain, top strikes, ATM IV (options_summary and options_put_call_ratio are totals).
- options_max_pain: every active expiry, nearest first (limit=N: N nearest); its history needs `expiry`. options_oi_distribution: one `expiry` is much smaller.
- etf_fundamentals: QUARTERLY SEC filings per issuer (no daily flows); `ticker` keeps one.

EXAMPLE: nearest expiry: asset=BTC, expiries=true

FIELDS:
- options_summary: Options overview: OI, volume, put/call, ATM IV, nearest expiry. [now, 1 point]
- options_oi: Open interest, calls and puts, USD. [tf with N or history]
- options_oi_change: OI change, calls and puts, USD. [tf with N or history]
- options_oi_distribution: Open interest by strike, per expiry. [expiry, now, 1 point]
- options_volume: Volume, calls and puts, USD. [tf with N or history]
- options_put_call_ratio: Put/call ratio (open interest) and label. [tf with N or history]
- options_iv: ATM 30-day implied volatility (%). [tf with N or history]
- options_iv_klines: Candles of the ATM 30-day implied volatility (%). [tf with N or history]
- options_max_pain: Max pain strike of each active expiry. [history needs expiry]
- options_greeks: Aggregated greeks: delta, gamma, theta, vega. [now, 1 point]
- etf_fundamentals: Spot ETF filings per issuer: shares, NAV, net assets, holdings. [ticker in history]

Parameters:
- `asset` **(required)** (string) — one of BTC, ETH: The asset.
- `fields` (array) — one of options_summary, options_oi, options_oi_change, options_oi_distribution, options_volume, options_put_call_ratio, options_iv, options_iv_klines, options_max_pain, options_greeks, etf_fundamentals: Fields (FIELDS below).
- `limit` (integer): N latest points per series (default 1).
- `expiries` (boolean): Adds the active expiries.
- `timeframe` (string) — one of 5m, 15m, 30m, 1h, 4h, 1d: Step of the history.
- `since_ms` (string): History start: epoch ms, ISO date or '48h' ago.
- `until_ms` (string): History end.
- `last` (string): History over the last '48h' / '30d' (whole buckets).
- `expiry` (string): Expiry YYYY-MM-DD.
- `ticker` (string): ETF issuer (IBIT) of etf_fundamentals.
- `columns` (array): Columns to keep, e.g. ["close", "volume"].
- `detail` (string) — one of compact, full, summary: summary: one row per series + summary; full: every column.
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_pair_brief`

The state of 1 to 10 pairs in ONE call, fixed shape: price_change, funding_next, the latest basis, oi (with oi_usd) and cvd of the last closed 1h bucket, liquidations_24h {from, to (start of the first and of the last 1h bucket), long_usd, short_usd, total_usd, bucket_count} and fear_greed (Financial plan). About one quota request per pair, plus one. Anything else: get_pair_data.

Parameters:
- `symbol` **(required)** (array): 1 to 10 pairs, e.g. ["BTCUSDT"].

### `get_pair_data`

A trading pair, or up to 10 compared: price, candles, trades, order flow, derivatives, tokenomics. No window = current value; since_ms/until_ms/last = history. Rows newest first, dated at the START of their bucket (first_time + i x step_s); for a total, an extreme or a change read summary, for the period covered read ranges; null + unavailable = no data; _pct = percent, _ratio = fraction; every unit: describe_fields. oi is read at the END of its bucket; price_change 1d = rolling 24 h.

EXAMPLES
- State: symbol=["BTCUSDT"], fields=["klines","funding_next","oi","cvd"], timeframe=1h, limit=24
- Liquidations 48 h, long/short: fields=["liquidations_cumulative"], last="48h", detail="summary"
- Buyers vs sellers, last 1000 trades: fields=["trades_futures"], limit=1000, detail="summary"

FIELDS:
- klines: OHLCV candles (OHLC: reference spot market; volume: spot + futures). [tf, live]
- price_change: Current price (last trade) and its rolling % change, 1m to 1w. [now, 1 point]
- trades_spot: Individual spot trades, most recent first. [now, N<=10000]
- trades_futures: Individual perpetual futures trades, most recent first. [now, N<=10000]
- trades_large: Futures trades above `min_usd`, most recent first. [min_usd, now, N<=10000]
- trades_kline_futures_seconds: Perpetual futures trades aggregated per second. [now]
- oi: Open interest per bucket, base units and USD (oi_usd). [tf]
- funding_next: Next estimated funding (8h equivalent, %) and APR: what venues show as current. [now, 1 point]
- funding_rate: Settled funding of each period (8h equivalent, %) and APR.
- funding_cumulative: Funding summed over a rolling 24h, and APR.
- basis: Futures/spot basis, % and price (positive = contango). [tf]
- oi_change: Open interest change per bucket, absolute and in %. [tf]
- liquidations_events: Individual liquidations: side, price, quantity, USD. [min_usd, now, N<=10000]
- liquidations_cumulative: USD liquidated per bucket, long and short positions. [tf]
- liquidations_big_small_ratio: Large vs small liquidations per bucket: counts, USD, ratio. [tf]
- heatmap_clusters: Liquidation cluster density and distance above/below price. [tf]
- orderbook: Order book depth (bids, asks, imbalance) by distance from mid. [tf, market]
- cvd: Volume delta per bucket (net, buy, sell, base units) and its running total cumulative_net_volume. [tf, market, live]
- spread_interexchange: Price spread between venues, bps (the only field naming venues). [tf, live]
- buy_sell_ratio: Buy share of the traded volume per bucket. [tf, market]
- trades_avg_size: Average trade size per bucket (base units). [tf, market]
- trades_kline: Trade candles, spot + futures: count, buy, sell, net volume. [tf, live, N<=1440]
- trades_kline_spot: Trade candles, spot: count, buy, sell, net volume. [tf, live, N<=1440]
- trades_kline_futures: Trade candles, futures: count, buy, sell, net volume. [tf, live, N<=1440]
- tokenomics: Supply (circulating, total, max), market cap, FDV (USD).

Parameters:
- `symbol` **(required)** (array): 1 to 10 pairs, e.g. ["BTCUSDT"].
- `fields` **(required)** (array) — one of klines, price_change, trades_spot, trades_futures, trades_large, trades_kline_futures_seconds, oi, funding_next, funding_rate, funding_cumulative, basis, oi_change, liquidations_events, liquidations_cumulative, liquidations_big_small_ratio, heatmap_clusters, orderbook, cvd, spread_interexchange, buy_sell_ratio, trades_avg_size, trades_kline, trades_kline_spot, trades_kline_futures, tokenomics: Fields (FIELDS below).
- `limit` (integer): N latest points per series (default 1).
- `timeframe` (string) — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w: Step of tf fields (default 1h, history: ~200 points). 1w: klines.
- `live` (boolean): Adds the open candle (live fields).
- `since_ms` (string): History start: epoch ms, ISO date or '48h' ago.
- `until_ms` (string): History end.
- `last` (string): History over the last '48h' / '30d' (whole buckets).
- `min_usd` (number): USD threshold: trades_large (default 100000), liquidations_events.
- `market` (string) — one of all, spot, futures: Of cvd, buy_sell_ratio, trades_avg_size, orderbook.
- `columns` (array): Columns to keep, e.g. ["close", "volume"].
- `detail` (string) — one of compact, full, summary: summary: one row per series + summary; full: every column.
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `get_system_info`

Your plan (families, history depth, rate, quota; null = unlimited), always returned and free; on demand the served pairs, data freshness and catalogs.
include: symbols (spot-only pairs have no futures data), freshness (freshness_fields: per field). catalogs: macro_series, macro_intraday_series, symbol_capabilities (the `series` of get_macro_data; symbol_capabilities needs `symbol`). Each part or catalog: one request.

Parameters:
- `include` (array) — one of symbols, freshness: Parts to add.
- `freshness_fields` (array): Fields whose freshness you want.
- `catalogs` (array) — one of macro_series, macro_intraday_series, symbol_capabilities: Catalogs to add.
- `symbol` (string): Pair of symbol_capabilities.
- `category` (string): Filter of macro_series.

### `rank_pairs`

Every pair ranked by ONE metric, top `limit`, ONE quota request: oi_usd, volume_usd_24h (spot + futures, last 24 closed hours, USD), funding_next (next estimated funding: estimated_rate_pct, 8h rate in %, and apr_pct), price_change_pct (over `window`, default 1d), rsi (RSI 14, last closed candle of `timeframe`, default 4h). Values at most 60 s old; pairs without the metric are in `excluded`. Example, most negative funding: metric=funding_next, order=asc

Parameters:
- `metric` **(required)** (string) — one of oi_usd, volume_usd_24h, funding_next, price_change_pct, rsi: Metric.
- `order` (string) — one of desc, asc: desc = largest first.
- `limit` (integer): Pairs returned.
- `window` (string) — one of 1h, 4h, 1d, 1w: price_change_pct only (default 1d).
- `timeframe` (string) — one of 1h, 4h, 1d: rsi only (default 4h).
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).

### `read_export`

The rest of a response cut by its size budget, page by page, same format, free. key: as in its data (default the first); offset: first row (0 = newest; the cut response's ranges.<key>.row_count). next_offset null = end. One hour, same API key.

Parameters:
- `export_id` **(required)** (string): export.export_id of the cut response.
- `key` (string): Series key (default the first).
- `offset` (integer): First row (0 = newest).
- `max_tokens` (integer): Response budget, estimated tokens (default 6000).
