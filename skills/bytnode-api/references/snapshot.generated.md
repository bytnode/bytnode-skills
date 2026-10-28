# Snapshot fields

> Generated from https://api.bytnode.com/openapi.json (contract **3.0.1**) by `tools/generate_references.py`. Do not edit by hand: regenerate.

52 fields for one symbol in a single call (41 plain, 11 multi-timeframe): prices, flow, derivatives, liquidations, macro, on-chain, options. Each query key is a field and its value a depth: `funding_rate=1` (or `=true`). Multi-timeframe fields take `@tf`: `klines@1h=24`, `cvd@1h=24`; `klines` also takes `1w`. Every field has the name of its route, and ONE type whatever the depth: a field WITHOUT a timeframe is the response of its latest-value route, an object (depth 1, or `true`; 422 `depth_too_large` above, naming its `/history` route) — except the event series `trades_spot`, `trades_futures`, `trades_kline_futures_seconds` and `liquidations_events`, always a list of their latest N rows; a field WITH `@tf` is ALWAYS a list, the latest N rows of its `/history` at that timeframe (`cvd@1h=1` is a list of one row). `max_depth` gives each ceiling. The timeframe is case-insensitive like everywhere (`cvd@1H`), except `1M`. A market field serves all markets (the route without `/spot` or `/futures`). Call it with only `symbol` to get, under `data`, `available_fields` (fields without a timeframe), `available_multi_tf_fields`, `multi_tf_syntax`, `timeframes`, `timeframes_by_field` and `max_depth`. An empty field carries `unavailable` (`not_applicable`, `no_api_key` or `no_data`) so 'no measure' is never mistaken for 'nothing happened'. Response: `symbol`, `data` (an object keyed by field name) and `is_partial` (true if a field failed: that field is then an `error` object with `code` and `message`, with the codes of the error catalogue).

## Fields without a timeframe (41)

Syntax `name=1` (or `true`); an event series takes `name=N`.

- `altcoin_season`: Altcoin Season Index.
- `basis`: Futures-spot basis (latest value).
- `btc_active_addresses`: Bitcoin active addresses.
- `btc_fees`: Recommended Bitcoin fees.
- `btc_mempool`: Bitcoin mempool.
- `btc_mining`: Mining pool concentration.
- `btc_mvrv`: Bitcoin MVRV.
- `btc_network`: Bitcoin network state.
- `btc_nvt`: Bitcoin NVT.
- `btc_revenue_per_difficulty`: Bitcoin revenue per difficulty.
- `cmc100`: CoinMarketCap 100 Index and its constituents.
- `cmc20`: CoinMarketCap 20 Index and its constituents.
- `eth_defi`: Ethereum DeFi.
- `eth_deflation`: ETH deflation.
- `eth_gas`: Ethereum gas.
- `eth_gas_momentum`: Gas momentum.
- `eth_price_btc`: ETH price in BTC.
- `eth_squeeze`: ETH supply squeeze index.
- `eth_staking`: ETH staking.
- `eth_supply`: ETH supply and burn.
- `fear_greed`: Crypto Fear & Greed Index.
- `fear_greed_cmc`: CMC Crypto Fear & Greed Index.
- `funding_cumulative`: Funding summed over 24 h.
- `funding_next`: Next funding forecast.
- `funding_rate`: Latest settled funding window.
- `global`: Total crypto market cap and dominance.
- `heatmap_clusters`: Liquidation heatmap clusters.
- `liquidations_cumulative`: Liquidations long/short USD over the last 5 minutes (latest value).
- `liquidations_events`: Individual liquidations (N latest events, at most your plan's count).
- `macro_correlations`: BTC correlation with DXY, S&P 500, gold, VIX.
- `macro_momentum`: Macro momentum score.
- `macro_net_liquidity`: US net liquidity.
- `macro_risk`: Risk-on / risk-off score.
- `macro_series`: Latest value of every FRED series.
- `oi_change`: Open interest change (latest value).
- `options_summary`: Options market summary for the symbol's asset.
- `price_change`: Price change over 1m to 1w, in percent.
- `tokenomics`: Supply, market cap, FDV.
- `trades_futures`: Individual futures trades (N trades), bounded by your plan's tick window.
- `trades_kline_futures_seconds`: Futures trades aggregated per second (N seconds).
- `trades_spot`: Individual spot trades (N trades), bounded by your plan's tick window.

## Multi-timeframe fields (11)

Syntax `name@tf=N`: always a list of the N latest closed buckets.

- `buy_sell_ratio@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `cvd@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `klines@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
- `liquidations_big_small_ratio@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `oi@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `orderbook@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `spread_interexchange@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `trades_avg_size@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `trades_kline@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `trades_kline_futures@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
- `trades_kline_spot@tf` — tf in 1m, 5m, 15m, 30m, 1h, 4h, 1d
