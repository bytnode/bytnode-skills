# BytNode REST routes

> Generated from https://api.bytnode.com/openapi.json (contract **3.0.1**) by `tools/generate_references.py`. Do not edit by hand: regenerate.

140 routes. Base URL `https://api.bytnode.com`, key in `X-API-KEY`. `family` is the identifier `GET /v1/limits` lists in `families` (`null` there = every family). Search this file for a path or a field name.

## Contents

- [System](#system) (6)
- [Snapshot](#snapshot) (1)
- [Market: prices & volumes](#market-prices--volumes) (6)
- [Order flow](#order-flow) (33)
- [Derivatives](#derivatives) (11)
- [Liquidations](#liquidations) (7)
- [Tokenomics & sentiment](#tokenomics--sentiment) (14)
- [Macro](#macro) (10)
- [ETF](#etf) (2)
- [Options](#options) (17)
- [Bitcoin network](#bitcoin-network) (8)
- [Ethereum](#ethereum) (16)
- [On-chain Bitcoin](#on-chain-bitcoin) (8)
- [Technical indicators](#technical-indicators) (1)

## System

### GET /v1/capabilities

What a symbol supports. Family: `price_volume`.

Which raw feeds were active over the last 24 h for `symbol` (required), and which derived metrics are available, blocked (with the missing feeds) or not applicable (stablecoins have no futures).

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=asset_class`.

`data`: object or null.
  - `asset_class` (string): `crypto` or `stablecoin` (spot only, no futures metrics).
  - `feeds_active_last_24h` (object): Per source feed, under its `/v1/status` name (`trades_spot`, `trades_kline_futures_seconds`, `oi`, `funding_rate`, `klines_1m`...): whether…
  - `computed_metrics_available` (array): Derived metrics available for the symbol.
  - `computed_metrics_blocked` (object): Derived metrics unavailable, with the missing feeds.
  - `feeds_not_applicable` (array): Feeds that do not exist for this symbol (the futures feeds of a spot-only stablecoin), under their `/v1/status` names.
  - `stablecoin_note` (string): Spot-only stablecoin: why its futures feeds and derived metrics do not apply.
  - `computed_metrics_not_applicable` (object): Derived metrics that do not apply (stablecoins have no futures).

### GET /v1/health

Service health. Not counted in the quota. Never counted.

Liveness of the API and its database (`data.database`).

`data`: object or null.
  - `database` (string): `connected` when the service reaches its database.

### GET /v1/limits

Your plan's limits. Not counted in the quota. Never counted.

What your key may do, read from the plan that served THIS request: `plan`, the data `families` it includes (`null` = all), the history window per `timeframe` (`window_s`, in seconds, `null` = unlimited), the window of individual trades (`trades_window_s`), the number of individual liquidations (`liquidations_events_count`), and the per-minute `rate` and monthly `quota` with what is left (`remaini…

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=plan,families`.

`data`: object or null.
  - `plan` (string): Your plan: `free`, `traders`, `financial`, `startup` or `enterprise` (`legacy` for an internal unmetered key: every limit below is then uns…
  - `families` (array, nullable): Data families your plan includes (`price_volume`, `derivatives`, `microstructure`, `trades`, `snapshot`, `indicators`, `macro`, `options`,…
  - `history` (array): History window per timeframe, one object per timeframe the API serves.
  - `trades_window_s` (integer, nullable, seconds): How far back individual trades (`/v1/trades/spot`, `/futures`, `/large`) may be read, in seconds; `0` = not in your plan (family `trades`),…
  - `liquidations_events_count` (integer, nullable, count): How many of the most recent individual liquidations `/v1/liquidations/events` may return, counted from the latest: 100 (Free), 500 (Traders…
  - `rate` (object, nullable): The per-minute rate, as a token bucket; `null` = unlimited or unmetered key.
  - `quota` (object, nullable): The monthly quota; `null` = unlimited or unmetered key.

### GET /v1/status

Freshness of every feed. Family: `price_volume`.

One row per public feed, for EVERY data family (market, derivatives, options, on-chain, macro, ETF, tokenomics, sentiment): its name, its family, the public `routes` it supplies, its age and staleness threshold (1.5 × the feed's expected interval; a monthly macro series or a quarterly ETF filing legitimately has an age of weeks).

`data`: object or null.
  - `computed_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): When the status was measured: the OLDEST of its measurements (each data family is measured on its own, cached up to 5 minutes for market fe…
  - `state` (string): `ok`, or `degraded` when at least one feed is stale or failed its check.
  - `feed_count` (integer, count): Public feeds checked.
  - `stale_feed_count` (integer, count): Feeds older than their threshold.
  - `error_feed_count` (integer, count): Feeds that could not be checked.
  - `max_age_s` (number, seconds): Age of the oldest feed.
  - `feeds` (array): One row per public feed.

### GET /v1/symbols

List the served trading pairs. Family: `price_volume`.

The served pairs: USDT-margined perpetual markets (the largest crypto assets by market capitalisation that the venues list as perpetuals) plus two spot-only stablecoin pairs (USDCUSDT, USDTUSDC).

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=symbol,base_asset`.

`data`: list (newest first unless `order=asc`).
  - `symbol` (string): Trading pair, e.g. `BTCUSDT`.
  - `base_asset` (string): Base asset of the pair.
  - `name` (string): Human-readable name.
  - `quote_asset` (string): Quote currency of the pair (`USDT` for BTCUSDT, `USDC` for USDTUSDC): the currency of its prices.
  - `markets` (array): Markets served for the pair: `spot` and `futures` (USDT-margined perpetual), or `spot` only for the two stablecoin pairs (their `/futures`…

### POST /v1/ws/token

Issue a short-lived WebSocket token. Not counted in the quota. Never counted.

For a BROWSER (or any client you do not trust with your API key): your server calls this route with its key in the `X-API-KEY` header and hands the browser only the token, which opens the stream at `wss://ws.bytnode.com/ws?token=…`.

`data`: object or null.
  - `token` (string, nullable): The WebSocket token (`wst_…`): pass it as `?token=` when opening `wss://ws.bytnode.com/ws` (or `wss://api.bytnode.com/ws`).
  - `expires_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant after which the token no longer opens a connection.
  - `expires_in_s` (integer, nullable, seconds): Lifetime of the token from its issue, in seconds (60).
  - `url` (string, nullable): The stream URL with the token already in it, ready to open.

## Snapshot

### GET /v1/snapshot

Many fields for one symbol in one request. Family: `snapshot`.

52 fields for one symbol in a single call (41 plain, 11 multi-timeframe): prices, flow, derivatives, liquidations, macro, on-chain, options.

Parameters: `symbol` plus one query key per field — see `snapshot.generated.md`.

`data`: object or null.
  - `altcoin_season` (object, nullable): Altcoin Season Index.
  - `basis` (object, nullable): Futures-spot basis (latest value).
  - `btc_active_addresses` (object, nullable): Bitcoin active addresses.
  - `btc_fees` (object, nullable): Recommended Bitcoin fees.
  - `btc_mempool` (object, nullable): Bitcoin mempool.
  - `btc_mining` (object, nullable): Mining pool concentration.
  - `btc_mvrv` (object, nullable): Bitcoin MVRV.
  - `btc_network` (object, nullable): Bitcoin network state.
  - `btc_nvt` (object, nullable): Bitcoin NVT.
  - `btc_revenue_per_difficulty` (object, nullable): Bitcoin revenue per difficulty.
  - `cmc100` (object, nullable): CoinMarketCap 100 Index and its constituents.
  - `cmc20` (object, nullable): CoinMarketCap 20 Index and its constituents.
  - `eth_defi` (object, nullable): Ethereum DeFi.
  - `eth_deflation` (object, nullable): ETH deflation.
  - `eth_gas` (object, nullable): Ethereum gas.
  - `eth_gas_momentum` (object, nullable): Gas momentum.
  - `eth_price_btc` (object, nullable): ETH price in BTC.
  - `eth_squeeze` (object, nullable): ETH supply squeeze index.
  - `eth_staking` (object, nullable): ETH staking.
  - `eth_supply` (object, nullable): ETH supply and burn.
  - `fear_greed` (object, nullable): Crypto Fear & Greed Index.
  - `fear_greed_cmc` (object, nullable): CMC Crypto Fear & Greed Index.
  - `funding_cumulative` (object, nullable): Funding summed over 24 h.
  - `funding_next` (object, nullable): Next funding forecast.
  - `funding_rate` (object, nullable): Latest settled funding window.
  - `global` (object, nullable): Total crypto market cap and dominance.
  - `heatmap_clusters` (object, nullable): Liquidation heatmap clusters.
  - `liquidations_cumulative` (object, nullable): Liquidations long/short USD over the last 5 minutes (latest value).
  - `liquidations_events` (object, nullable): Individual liquidations (N latest events, at most your plan's count).
  - `macro_correlations` (object, nullable): BTC correlation with DXY, S&P 500, gold, VIX.
  - `macro_momentum` (object, nullable): Macro momentum score.
  - `macro_net_liquidity` (object, nullable): US net liquidity.
  - `macro_risk` (object, nullable): Risk-on / risk-off score.
  - `macro_series` (object, nullable): Latest value of every FRED series.
  - `oi_change` (object, nullable): Open interest change (latest value).
  - `options_summary` (object, nullable): Options market summary for the symbol's asset.
  - `price_change` (object, nullable): Price change over 1m to 1w, in percent.
  - `tokenomics` (object, nullable): Supply, market cap, FDV.
  - `trades_futures` (object, nullable): Individual futures trades (N trades), bounded by your plan's tick window.
  - `trades_kline_futures_seconds` (object, nullable): Futures trades aggregated per second (N seconds).
  - `trades_spot` (object, nullable): Individual spot trades (N trades), bounded by your plan's tick window.
  - `buy_sell_ratio@1m` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@5m` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@15m` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@30m` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@1h` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@4h` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `buy_sell_ratio@1d` (object): Buy/sell volume ratio per bucket (`buy_sell_ratio@<tf>=N`: the N latest closed buckets).
  - `cvd@1m` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@5m` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@15m` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@30m` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@1h` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@4h` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `cvd@1d` (object): CVD per bucket (`cvd@<tf>=N`: the N latest closed buckets).
  - `klines@1m` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@5m` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@15m` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@30m` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@1h` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@4h` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@1d` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `klines@1w` (object): OHLCV candles (`klines@<tf>=N`: the N latest closed candles).
  - `liquidations_big_small_ratio@1m` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@5m` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@15m` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@30m` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@1h` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@4h` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `liquidations_big_small_ratio@1d` (object): Big vs small liquidations per bucket (`liquidations_big_small_ratio@<tf>=N`: the N latest closed buckets with liquidations).
  - `oi@1m` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@5m` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@15m` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@30m` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@1h` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@4h` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `oi@1d` (object): Total open interest per closed bucket (`oi@<tf>=N`: the N latest buckets).
  - `orderbook@1m` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@5m` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@15m` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@30m` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@1h` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@4h` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `orderbook@1d` (object): Order book depth by price range per closed bucket (book at the end of the bucket), spot + futures (`orderbook@1m=1` = a list with the lates…
  - `spread_interexchange@1m` (object): Inter-venue spread per bucket.
  - `spread_interexchange@5m` (object): Inter-venue spread per bucket.
  - `spread_interexchange@15m` (object): Inter-venue spread per bucket.
  - `spread_interexchange@30m` (object): Inter-venue spread per bucket.
  - `spread_interexchange@1h` (object): Inter-venue spread per bucket.
  - `spread_interexchange@4h` (object): Inter-venue spread per bucket.
  - `spread_interexchange@1d` (object): Inter-venue spread per bucket.
  - `trades_avg_size@1m` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@5m` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@15m` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@30m` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@1h` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@4h` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_avg_size@1d` (object): Average trade size per bucket (`trades_avg_size@<tf>=N`: the N latest closed buckets).
  - `trades_kline@1m` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@5m` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@15m` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@30m` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@1h` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@4h` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline@1d` (object): Trade candles, spot + futures (N latest closed buckets).
  - `trades_kline_futures@1m` (object): Trade candles, futures only.
  - `trades_kline_futures@5m` (object): Trade candles, futures only.
  - `trades_kline_futures@15m` (object): Trade candles, futures only.
  - `trades_kline_futures@30m` (object): Trade candles, futures only.
  - `trades_kline_futures@1h` (object): Trade candles, futures only.
  - `trades_kline_futures@4h` (object): Trade candles, futures only.
  - `trades_kline_futures@1d` (object): Trade candles, futures only.
  - `trades_kline_spot@1m` (object): Trade candles, spot only.
  - `trades_kline_spot@5m` (object): Trade candles, spot only.
  - `trades_kline_spot@15m` (object): Trade candles, spot only.
  - `trades_kline_spot@30m` (object): Trade candles, spot only.
  - `trades_kline_spot@1h` (object): Trade candles, spot only.
  - `trades_kline_spot@4h` (object): Trade candles, spot only.
  - `trades_kline_spot@1d` (object): Trade candles, spot only.
  - `available_fields` (array): Catalogue (`?symbol=` alone): the single-value fields your plan includes.
  - `available_multi_tf_fields` (array): Catalogue: the fields requested per timeframe, as `<field>@<tf>=<depth>`.
  - `multi_tf_syntax` (string): Catalogue: how to request a multi-timeframe field.
  - `timeframes` (array): Catalogue: the timeframes a multi-timeframe field accepts by default.
  - `timeframes_by_field` (object): Catalogue: the fields whose timeframes differ from `timeframes`.
  - `max_depth` (object): Catalogue: the largest depth each field accepts (a larger one: 422 `depth_too_large`).

## Market: prices & volumes

### GET /v1/klines

Latest OHLCV candle. Family: `price_volume`.

The latest CLOSED candle of `timeframe` (required: `1m` to `1w`): the first row of `/v1/klines/history`, an object, served as soon as its volumes are final (about 5 seconds after a 1m candle ends).

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w. Candle size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` or `1w` (weekly candles start on Monday 00:00 UTC).
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,open`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest CLOSED candle of `timeframe` (the first row of `/v1/klines/history`); with `?live=1`, of the candle in progress.
  - `open` (number, quote currency (USDT for BTCUSDT)): Opening price of the candle.
  - `high` (number, quote currency (USDT for BTCUSDT)): Highest price of the candle.
  - `low` (number, quote currency (USDT for BTCUSDT)): Lowest price of the candle.
  - `close` (number, quote currency (USDT for BTCUSDT)): Closing price of the candle (last price for the open candle).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Volume traded on the SPOT market, summed across venues, base asset units.
  - `buy_volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume on the SPOT market, across venues.
  - `sell_volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume on the SPOT market, across venues.
  - `is_volume_spot_estimated` (boolean, nullable): `true` when the spot quantities of this candle were ESTIMATED from USD amounts and the candle's typical price (high + low + close) / 3 (dat…
  - `volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Volume traded on PERPETUAL FUTURES, summed across venues, in base asset units.
  - `buy_volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume on PERPETUAL FUTURES, across venues.
  - `sell_volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume on PERPETUAL FUTURES, across venues.
  - `is_volume_futures_estimated` (boolean, nullable): `true` when `volume_futures` was ESTIMATED from USD amounts and the candle's typical price; `false` = measured.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/klines/history

OHLCV candles. Family: `price_volume`.

Candles of `timeframe` (required: `1m` to `1w`) that have ENDED: the candle in progress is never served.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w. Candle size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` or `1w` (weekly candles start on Monday 00:00 UTC).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,open`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `open` (number, quote currency (USDT for BTCUSDT)): Opening price of the candle.
  - `high` (number, quote currency (USDT for BTCUSDT)): Highest price of the candle.
  - `low` (number, quote currency (USDT for BTCUSDT)): Lowest price of the candle.
  - `close` (number, quote currency (USDT for BTCUSDT)): Closing price of the candle (last price for the open candle).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Volume traded on the SPOT market, summed across venues, base asset units.
  - `buy_volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume on the SPOT market, across venues.
  - `sell_volume_spot` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume on the SPOT market, across venues.
  - `is_volume_spot_estimated` (boolean, nullable): `true` when the spot quantities of this candle were ESTIMATED from USD amounts and the candle's typical price (high + low + close) / 3 (dat…
  - `volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Volume traded on PERPETUAL FUTURES, summed across venues, in base asset units.
  - `buy_volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume on PERPETUAL FUTURES, across venues.
  - `sell_volume_futures` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume on PERPETUAL FUTURES, across venues.
  - `is_volume_futures_estimated` (boolean, nullable): `true` when `volume_futures` was ESTIMATED from USD amounts and the candle's typical price; `false` = measured.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/price-change

Price change over 1m to 1w. Family: `price_volume`.

Rolling price change in percent over eight windows, from the LATEST PRICE: the last trade of the symbol's reference spot market, i.e. the close of `/v1/klines?live=1` (`time` is the instant of that trade).

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,price`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of the latest trade of the reference spot market (`price` is that trade's price, the close of `/v1/klines?live=1`); if it has not t…
  - `price` (number, quote currency (USDT for BTCUSDT)): Price.
  - `changes_pct` (object): Price change over each window, keyed by window (`1m` … `1w`), in percent.

### GET /v1/trades/futures

Individual futures trades. Family: `trades`.

Perpetual futures executions ("trades") across venues, one row per trade, most recent first — the same trades, with the same `id`, as the WebSocket channel `trades.futures`.

Parameters:
- `limit` — integer (min 1, max 10000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `after_id` — string. Resume right after this trade: the `id` of the last trade received, with its `time` as `since_ms` (order=asc) or `until_ms` (order=desc).
- `order` — one of asc, desc. Range reading: `desc` (most recent first, the default) or `asc`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,id`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Execution instant of the trade, as stated by the venue (milliseconds).
  - `id` (string): Opaque, stable identifier of the trade (16 hex characters): the same trade always has the same `id`, so it can be used to deduplicate or re…
  - `side` (string): Trades: `buy` or `sell` (aggressor side).
  - `price` (number, quote currency (USDT for BTCUSDT)): Price.
  - `quantity` (number, base asset quantity (BTC for BTCUSDT)): Quantity traded or liquidated, in base asset units.
  - `value_usd` (number, USD): Notional value: price × quantity, in the pair's quote currency (USDT for BTCUSDT), taken as USD.

### GET /v1/trades/large

Large individual trades. Family: `trades`.

Individual perpetual futures trades above `min_usd` (default 100,000 USD), all venues.

Parameters:
- `min_usd` — number (min 1000) — default `100000`. Minimum notional in USD (default 100000, minimum 1000).
- `limit` — integer (min 1, max 10000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `after_id` — string. Resume right after this trade: the `id` of the last trade received, with its `time` as `since_ms` (order=asc) or `until_ms` (order=desc).
- `order` — one of asc, desc. Range reading: `desc` (most recent first, the default) or `asc`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,id`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Execution instant of the trade, as stated by the venue (milliseconds).
  - `id` (string): Opaque, stable identifier of the trade (16 hex characters): the same trade always has the same `id`, so it can be used to deduplicate or re…
  - `side` (string): Trades: `buy` or `sell` (aggressor side).
  - `price` (number, quote currency (USDT for BTCUSDT)): Price.
  - `quantity` (number, base asset quantity (BTC for BTCUSDT)): Quantity traded or liquidated, in base asset units.
  - `value_usd` (number, USD): Notional value: price × quantity, in the pair's quote currency (USDT for BTCUSDT), taken as USD.

### GET /v1/trades/spot

Individual spot trades. Family: `trades`.

Spot executions ("trades") across venues, one row per trade, most recent first — the same trades, with the same `id`, as the WebSocket channel `trades.spot`.

Parameters:
- `limit` — integer (min 1, max 10000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `after_id` — string. Resume right after this trade: the `id` of the last trade received, with its `time` as `since_ms` (order=asc) or `until_ms` (order=desc).
- `order` — one of asc, desc. Range reading: `desc` (most recent first, the default) or `asc`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,id`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Execution instant of the trade, as stated by the venue (milliseconds).
  - `id` (string): Opaque, stable identifier of the trade (16 hex characters): the same trade always has the same `id`, so it can be used to deduplicate or re…
  - `side` (string): Trades: `buy` or `sell` (aggressor side).
  - `price` (number, quote currency (USDT for BTCUSDT)): Price.
  - `quantity` (number, base asset quantity (BTC for BTCUSDT)): Quantity traded or liquidated, in base asset units.
  - `value_usd` (number, USD): Notional value: price × quantity, in the pair's quote currency (USDT for BTCUSDT), taken as USD.

## Order flow

### GET /v1/buy-sell-ratio

Buy/sell volume ratio. Family: `microstructure`.

Taker buy share of volume (`buy_ratio`, a fraction) of the latest CLOSED bucket of `timeframe` (required), all venues: the first row of `/v1/buy-sell-ratio/history` for the same `timeframe`, and the same buy and sell volumes as `/v1/cvd` for that bucket.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/buy-sell-ratio/history` for the same `timeframe`.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, nullable, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/buy-sell-ratio/futures

Buy/sell volume ratio, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/buy-sell-ratio/history` for the same `timeframe`.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, nullable, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/buy-sell-ratio/futures/history

Buy/sell ratio history, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd/history` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/buy-sell-ratio/history

Buy/sell ratio history. Family: `microstructure`.

One row per closed bucket of `timeframe` (required): the taker buy and sell volumes of the WHOLE bucket — the same volumes as `/v1/cvd/history` for the same market and bucket — and the buy share of their sum.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd/history` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/buy-sell-ratio/spot

Buy/sell volume ratio, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/buy-sell-ratio/history` for the same `timeframe`.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, nullable, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/buy-sell-ratio/spot/history

Buy/sell ratio history, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,buy_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `buy_ratio` (number, nullable, fraction (0.585 = 58.5 %)): buy_volume / (buy_volume + sell_volume).
  - `sample_count` (integer, count): Number of points of the CVD series behind the bucket — the `sample_count` of `/v1/cvd/history` for the same bucket.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd

Cumulative volume delta per bucket. Family: `microstructure`.

Net taker delta of the latest closed bucket, with its path inside the bucket (`cvd_series`: one point per minute up to 1h, per 5 minutes in 4h, per 15 minutes in 1d), aggregated across venues.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd/futures

Cumulative volume delta per bucket, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd/futures/history

Cumulative volume delta history, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd/history

Cumulative volume delta history. Family: `microstructure`.

Same as `/v1/cvd`, one row per closed bucket.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd/spot

Cumulative volume delta per bucket, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/cvd/spot/history

Cumulative volume delta history, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `cvd_series` (array, nullable, base asset quantity (BTC for BTCUSDT)): Cumulative volume delta inside the bucket, one point per step of finer candles (1 minute up to `1h`, 5 minutes in `4h`, 15 minutes in `1d`)…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `sample_count` (integer, nullable, count): Number of points in `cvd_series`; 1 when `cvd_series` is `null` (the bucket's candle alone).
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/orderbook

Order book depth by price range, per bucket. Family: `microstructure`.

Liquidity resting within ±0.25 to ±10 % of the mid price (eight ranges), bids and asks, in coins and USD, summed across venues, for the latest CLOSED bucket of `timeframe` (required; `1m` = the latest closed minute).

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/orderbook/futures

Order book depth by price range, per bucket, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/orderbook/futures/history

Order book depth by price range, history, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/orderbook/history

Order book depth by price range, history. Family: `microstructure`.

Same as `/v1/orderbook`, one row per closed bucket; `timeframe` is required.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/orderbook/spot

Order book depth by price range, per bucket, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/orderbook/spot/history

Order book depth by price range, history, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the depth is the photo of the order book at the END of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ranges` (array): One entry per price range around the mid price, from the tightest (±0.25 %) to the widest (±10 %).

### GET /v1/spread/interexchange

Inter-venue price spread. Family: `microstructure`.

Each venue's premium versus the volume-weighted reference price over the bucket, and the widest gap between two venues.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ref_price` (number, quote currency (USDT for BTCUSDT)): Reference price: the volume-weighted average price across venues over the bucket.
  - `weighting` (string): How venues are combined: `oi` (open-interest weighted) or `volume` (volume weighted).
  - `max_spread_bps` (number, basis points (1 bp = 0.01 %)): Gap between the highest and the lowest venue price, relative to ref_price.
  - `high_venue` (string): Venue with the highest price over the bucket.
  - `high_price` (number, quote currency (USDT for BTCUSDT)): Its volume-weighted price over the bucket.
  - `low_venue` (string): Venue with the lowest price over the bucket.
  - `low_price` (number, quote currency (USDT for BTCUSDT)): Its volume-weighted price over the bucket.
  - `venues` (array): Per-venue prices and premiums (`[{venue, price, premium_bps}]`).

### GET /v1/spread/interexchange/history

Inter-venue spread history. Family: `microstructure`.

Same as `/v1/spread/interexchange`, one row per closed bucket.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,is_closed`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `ref_price` (number, quote currency (USDT for BTCUSDT)): Reference price: the volume-weighted average price across venues over the bucket.
  - `weighting` (string): How venues are combined: `oi` (open-interest weighted) or `volume` (volume weighted).
  - `max_spread_bps` (number, basis points (1 bp = 0.01 %)): Gap between the highest and the lowest venue price, relative to ref_price.
  - `high_venue` (string): Venue with the highest price over the bucket.
  - `high_price` (number, quote currency (USDT for BTCUSDT)): Its volume-weighted price over the bucket.
  - `low_venue` (string): Venue with the lowest price over the bucket.
  - `low_price` (number, quote currency (USDT for BTCUSDT)): Its volume-weighted price over the bucket.
  - `venues` (array): Per-venue prices and premiums (`[{venue, price, premium_bps}]`).

### GET /v1/trades-kline

Trade candle, spot + futures combined. Family: `microstructure`.

The trades of the latest closed bucket aggregated into a candle ("trades kline"): trade count, volume, buy/sell volume, net volume, average size and rate, all venues, spot and futures.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades-kline/futures

Trade candle, futures only. Family: `microstructure`.

Same as `/v1/trades-kline`, perpetual futures only.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades-kline/futures/history

Trade candles history, futures only. Family: `microstructure`.

Same as `/v1/trades-kline/futures`, one row per closed bucket.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades-kline/futures/seconds

Trades aggregated per second. Family: `trades`.

Every PERPETUAL FUTURES trade of every venue summed per second: volume, trade count, taker buy and sell, and `is_closed` (a second is final 21 s after it ends: a venue can still deliver a late trade before; a trade delivered later still is added afterwards, so the seconds of a minute always add up to its trades).

Parameters:
- `limit` — integer (min 1, max 1000) — default `100`. Number of seconds to return (one row per second with trades).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `order` — one of asc, desc. Range reading: `desc` (most recent first, the default) or `asc`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,volume`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the second the row covers.
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…

### GET /v1/trades-kline/history

Trade candles history, combined. Family: `microstructure`.

Same as `/v1/trades-kline`, one row per closed bucket.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades-kline/spot

Trade candle, spot only. Family: `microstructure`.

Same as `/v1/trades-kline`, spot venues only.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades-kline/spot/history

Trade candles history, spot only. Family: `microstructure`.

Same as `/v1/trades-kline/spot`, one row per closed bucket.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,trade_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `trade_count` (integer, count): Number of trades.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `buy_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) buy volume, base asset units, aggregated across venues.
  - `sell_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Aggressive (taker) sell volume, base asset units, aggregated across venues.
  - `net_volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): buy_volume - sell_volume over the row, base asset units.
  - `buy_sell_coverage_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the volume (in USD) whose buy/sell split is known.
  - `trade_rate` (number, trades per second): Average number of trades per second over the bucket.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size

Average trade size. Family: `microstructure`.

Average trade size (volume / number of trades, all venues) of the latest CLOSED bucket of `timeframe` (required): the first row of `/v1/trades/avg-size/history` for the same `timeframe` (`time` = its start, `is_closed: true`).

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/trades/avg-size/history` for the same `timeframe`.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, nullable, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size/futures

Average trade size, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/trades/avg-size/history` for the same `timeframe`.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, nullable, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size/futures/history

Average trade size history, perpetual futures only. Family: `microstructure`.

Perpetual futures market only.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`, the value aggregating the bucket's minutes; the row covers `time` to `time` + the envelope's `step` (ex…
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size/history

Average trade size history. Family: `microstructure`.

Trade candles of the market of the path: one row per closed bucket of `timeframe`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`, the value aggregating the bucket's minutes; the row covers `time` to `time` + the envelope's `step` (ex…
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size/spot

Average trade size, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` — the first row of `/v1/trades/avg-size/history` for the same `timeframe`.
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, nullable, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/trades/avg-size/spot/history

Average trade size history, spot only. Family: `microstructure`.

Spot market only.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,avg_trade_size`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`, the value aggregating the bucket's minutes; the row covers `time` to `time` + the envelope's `step` (ex…
  - `avg_trade_size` (number, nullable, base asset quantity (BTC for BTCUSDT)): Average trade size, base asset units (NOT dollars: multiply by the price for a notional).
  - `volume` (number, nullable, base asset quantity (BTC for BTCUSDT)): Traded volume over the row, base asset units (BTC for BTCUSDT, NOT dollars), aggregated across venues, over the market(s) the route covers:…
  - `trade_count` (integer, count): Number of trades.
  - `is_volume_estimated` (boolean, nullable): `true` when some base-asset quantities of this row were ESTIMATED from USD amounts (history where a source reported amounts but not quantit…
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Derivatives

### GET /v1/basis

Futures-spot basis. Family: `derivatives`.

Perpetual futures price versus spot, OI-weighted across venues (each venue weighted by its latest open interest within 10 minutes).

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,basis_value`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the venue prices used (each venue's last futures and spot trades, at most 2 minutes old).
  - `basis_value` (number, quote currency (USDT for BTCUSDT)): Futures price - spot price, in the quote currency (USDT for BTCUSDT), like the two prices.
  - `basis_pct` (number, percent (58.5 = 58.5 %)): (futures - spot) / spot, in percent.
  - `futures_price` (number, quote currency (USDT for BTCUSDT)): Perpetual futures price, open-interest weighted across venues.
  - `spot_price` (number, quote currency (USDT for BTCUSDT)): Spot price across venues at the instant of the row, paired with the futures price of the same instant.

### GET /v1/basis/history

Basis history. Family: `derivatives`.

One row per closed bucket of `timeframe` (required).

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,basis_value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`; the value is the LAST one of the bucket's minutes.
  - `basis_value` (number, quote currency (USDT for BTCUSDT)): Futures price - spot price, in the quote currency (USDT for BTCUSDT), like the two prices.
  - `basis_pct` (number, percent (58.5 = 58.5 %)): (futures - spot) / spot, in percent.
  - `futures_price` (number, quote currency (USDT for BTCUSDT)): Perpetual futures price, open-interest weighted across venues.
  - `spot_price` (number, quote currency (USDT for BTCUSDT)): Spot price across venues at the instant of the row, paired with the futures price of the same instant.
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/funding/cumulative

Funding over the last 24 h. Family: `derivatives`.

Sum of the last three settled 8-hour windows (`rolling_24h_rate_pct`, a ROLLING 24-hour window) and its annualised rate.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,window_start_at`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value over a rolling window: the END of the 24-hour window, i.e. the settlement that closes the last 8-hour period summed.
  - `window_start_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the 24-hour window summed (inclusive).
  - `window_s` (integer, nullable, seconds): Length of the window, in seconds (86400 = 24 hours).
  - `rolling_24h_rate_pct` (number, percent (58.5 = 58.5 %)): Sum of the last three settled 8-hour funding rates — a ROLLING 24-hour window — in percent.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `sample_count` (integer, count): Number of 8-hour funding windows summed.

### GET /v1/funding/cumulative/history

Rolling 24 h funding history. Family: `derivatives`.

One row every 8 hours, each covering the 24 hours before it: consecutive rows OVERLAP by 16 hours, so never add them up — sum `rate_pct` of `/v1/funding/rate/history` for a total over a period.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,window_start_at`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): END of each 24-hour window (the settlement that closes its last 8-hour period).
  - `window_start_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the 24-hour window summed (inclusive).
  - `window_s` (integer, nullable, seconds): Length of the window, in seconds (86400 = 24 hours).
  - `rolling_24h_rate_pct` (number, percent (58.5 = 58.5 %)): Sum of the last three settled 8-hour funding rates — a ROLLING 24-hour window — in percent.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `sample_count` (integer, count): Number of 8-hour funding windows summed.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/funding/next

Next funding forecast. Family: `derivatives`.

Each venue's forecast of its next settlement, normalised to 8 h and OI-weighted.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,estimated_rate_pct`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the next funding settlement the forecast is for.
  - `estimated_rate_pct` (number, percent (58.5 = 58.5 %)): Venue forecast of the NEXT funding settlement, in percent per 8 h (0.01 = 0.01 %), normalised to 8 h, OI-weighted.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `is_past` (boolean): `true` if the forecast settlement instant is already past (the next forecast is not published yet).

### GET /v1/funding/rate

Latest settled funding rate. Family: `derivatives`.

The last fully settled 8-hour funding window, normalised to 8 h and weighted by the open interest of each venue at that time.

Parameters:
- `live` — boolean — default `False`. `1` or `true` to return the CURRENT, still-open period computed on the fly (`is_closed: false`).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,period_end_at`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the 8-hour funding period.
  - `period_end_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): End of the 8-hour funding period (exclusive): the instant of the settlement that pays it.
  - `settled_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of the last settlement counted in the window: `period_end_at` for a complete settled window; `null` for the window in progress (`?l…
  - `rate_pct` (number, percent (58.5 = 58.5 %)): Settled funding rate of the 8-hour period, in percent (0.01 = 0.01 % per 8 h), normalised to 8 h and open-interest weighted across venues.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/funding/rate/history

Settled funding history. Family: `derivatives`.

One row per settled 8-hour window (`time` = start of the period), with `period_end_at` and `settled_at`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,period_end_at`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the 8-hour funding period.
  - `period_end_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): End of the 8-hour funding period (exclusive): the instant of the settlement that pays it.
  - `settled_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of the last settlement counted in the window: `period_end_at` for a complete settled window; `null` for the window in progress (`?l…
  - `rate_pct` (number, percent (58.5 = 58.5 %)): Settled funding rate of the 8-hour period, in percent (0.01 = 0.01 % per 8 h), normalised to 8 h and open-interest weighted across venues.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/oi

Open interest. Family: `derivatives`.

Current total open interest of the perpetual futures, summed across venues (base asset units): for each venue its latest reading, then the sum.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the latest reading summed (the same as `/v1/oi/change`).
  - `oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest across venues, base asset units.

### GET /v1/oi/change

Open interest change. Family: `derivatives`.

Change of total open interest over the last minute, summed across venues: `oi` (now), `previous_oi`, `oi_change`, `oi_change_pct`.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement; the change covers the minute before it.
  - `oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest across venues, base asset units.
  - `previous_oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest at the start of the window (`window_start_at`).
  - `oi_change` (number, base asset quantity (BTC for BTCUSDT)): oi - previous_oi, base asset units.
  - `oi_change_pct` (number, percent (58.5 = 58.5 %)): Relative open interest change, percent.
  - `window_start_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the ROLLING window the value covers (inclusive).
  - `window_s` (integer, nullable, seconds): Length of that rolling window, in whole seconds: it runs from `window_start_at` to `time` (excluded).

### GET /v1/oi/change/history

Open interest change history. Family: `derivatives`.

One row per closed bucket of `timeframe` (required), on the same totals as `/v1/oi/history`: same buckets, same `oi`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`, the value aggregating the bucket's minutes; the row covers `time` to `time` + the envelope's `step` (ex…
  - `oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest across venues, base asset units.
  - `previous_oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest at the start of the window (`window_start_at`).
  - `oi_change` (number, base asset quantity (BTC for BTCUSDT)): oi - previous_oi, base asset units.
  - `oi_change_pct` (number, percent (58.5 = 58.5 %)): Relative open interest change, percent.
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/oi/history

Total open interest history. Family: `derivatives`.

Open interest summed across futures venues, per closed bucket of `timeframe` (required): for each venue, its latest reading at the END of the bucket — `oi` is the value at the end, like a close.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `oi` (number, base asset quantity (BTC for BTCUSDT)): Total open interest across venues, base asset units.
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Liquidations

### GET /v1/heatmap/clusters

Liquidation heatmap clusters. Family: `derivatives`.

The most attractive cluster of estimated liquidation levels above and below the price, projected from open interest changes and the leverage mix.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,density_up`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `density_up` (number, dimensionless score): Estimated liquidation density of the most attractive cluster ABOVE the price (short positions).
  - `dist_up_ratio` (number, fraction (0.585 = 58.5 %)): Distance from the price to the cluster above, as a fraction of the price (0.037 = 3.7 % higher).
  - `density_down` (number, dimensionless score): Estimated liquidation density of the most attractive cluster BELOW the price (long positions).
  - `dist_down_ratio` (number, fraction (0.585 = 58.5 %)): Distance from the price to the cluster below, as a fraction of the price.
  - `attraction_up` (number, dimensionless score): density_up / dist_up_ratio²: how strongly the cluster above pulls the price.
  - `attraction_down` (number, dimensionless score): density_down / dist_down_ratio²: how strongly the cluster below pulls the price.

### GET /v1/heatmap/clusters/history

Liquidation clusters history. Family: `derivatives`.

One row per closed bucket of `timeframe` (required).

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,density_up`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`; the value is the LAST one of the bucket's minutes.
  - `density_up` (number, dimensionless score): Estimated liquidation density of the most attractive cluster ABOVE the price (short positions).
  - `dist_up_ratio` (number, fraction (0.585 = 58.5 %)): Distance from the price to the cluster above, as a fraction of the price (0.037 = 3.7 % higher).
  - `density_down` (number, dimensionless score): Estimated liquidation density of the most attractive cluster BELOW the price (long positions).
  - `dist_down_ratio` (number, fraction (0.585 = 58.5 %)): Distance from the price to the cluster below, as a fraction of the price.
  - `attraction_up` (number, dimensionless score): density_up / dist_up_ratio²: how strongly the cluster above pulls the price.
  - `attraction_down` (number, dimensionless score): density_down / dist_down_ratio²: how strongly the cluster below pulls the price.
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/liquidations/big-small-ratio

Big vs small liquidations. Family: `derivatives`.

Liquidations of 100,000 USD or more versus smaller ones over the latest CLOSED bucket of `timeframe` (required) that had liquidations — the first row of `/v1/liquidations/big-small-ratio/history` for the same `timeframe` (`time` = its start, `is_closed: true`): counts, USD and `big_small_ratio`.

Parameters:
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,big_count`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest closed bucket of `timeframe` that had at least one liquidation — the first row of `/v1/liquidations/big-small-ratio/his…
  - `big_count` (integer, count): Liquidations of 100,000 USD or more.
  - `big_usd` (number, USD): Notional of liquidations of 100,000 USD or more.
  - `small_count` (integer, count): Liquidations below 100,000 USD.
  - `small_usd` (number, USD): Notional of liquidations below 100,000 USD.
  - `big_small_ratio` (number, nullable, big / small): big_usd / small_usd: the notional of liquidations of 100,000 USD or more DIVIDED BY that of the smaller ones (8.2 = the big ones weigh 8.2…
  - `sample_count` (integer, nullable, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/liquidations/big-small-ratio/history

Big vs small liquidations history. Family: `derivatives`.

One row per closed bucket of `timeframe` (required).

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,big_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket of `timeframe`, the value aggregating the bucket's minutes; the row covers `time` to `time` + the envelope's `step` (ex…
  - `big_count` (integer, count): Liquidations of 100,000 USD or more.
  - `big_usd` (number, USD): Notional of liquidations of 100,000 USD or more.
  - `small_count` (integer, count): Liquidations below 100,000 USD.
  - `small_usd` (number, USD): Notional of liquidations below 100,000 USD.
  - `big_small_ratio` (number, nullable, big / small): big_usd / small_usd: the notional of liquidations of 100,000 USD or more DIVIDED BY that of the smaller ones (8.2 = the big ones weigh 8.2…
  - `sample_count` (integer, count): Minutes of the bucket that had at least one liquidation.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/liquidations/cumulative

Liquidations over the last 5 minutes. Family: `derivatives`.

Longs and shorts liquidated, USD, all venues, over the last closed 5-minute ROLLING window, aligned on the minute: `time` is its END, `window_start_at` its start, `window_s` its length.

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,long_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value over a rolling window: the END of the 5-minute window, aligned on the minute.
  - `long_usd` (number, USD): Long positions liquidated, USD.
  - `short_usd` (number, USD): Short positions liquidated, USD.
  - `total_usd` (number, USD): Total, USD.
  - `window_start_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the ROLLING window the value covers (inclusive).
  - `window_s` (integer, nullable, seconds): Length of that rolling window, in whole seconds: it runs from `window_start_at` to `time` (excluded).

### GET /v1/liquidations/cumulative/history

Cumulative liquidations history. Family: `derivatives`.

One row per closed bucket of `timeframe` (required): the longs and shorts liquidated during the WHOLE bucket, USD, all venues (0 when none).

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` **(required)** — one of 1m, 5m, 15m, 30m, 1h, 4h, 1d. Required: `1m`, `5m`, `15m`, `30m`, `1h`, `4h` or `1d`.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,long_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket.
  - `long_usd` (number, USD): Long positions liquidated, USD.
  - `short_usd` (number, USD): Short positions liquidated, USD.
  - `total_usd` (number, USD): Total, USD.
  - `sample_count` (integer, count): Number of source points in the bucket (one-minute points with data).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/liquidations/events

Individual liquidations. Family: `derivatives`.

Forced liquidations across futures venues, one row per event, most recent first.

Parameters:
- `limit` — integer (min 1, max 10000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `min_usd` — number (min 0). Optional minimum notional in USD: only liquidations of at least this size are returned.
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,side`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of the liquidation, as stated by the venue (milliseconds).
  - `side` (string): `long` (a long position was liquidated: forced sell) or `short` (forced buy).
  - `price` (number, quote currency (USDT for BTCUSDT)): Price.
  - `quantity` (number, base asset quantity (BTC for BTCUSDT)): Quantity traded or liquidated, in base asset units.
  - `value_usd` (number, USD): Notional value: price × quantity, in the pair's quote currency (USDT for BTCUSDT), taken as USD.

## Tokenomics & sentiment

### GET /v1/altcoin-season

Altcoin Season Index. Family: `sentiment`.

CoinMarketCap's Altcoin Season Index, from 0 (bitcoin season) to 100 (altcoin season), with the altcoin market capitalisation and the 1-year high and low.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.

`data`: object or null.
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `value` (integer, nullable, score from 0 to 100): Altcoin Season Index (CoinMarketCap): how many of the top altcoins outperformed BTC over the last 90 days.
  - `year_low` (integer, nullable, score from 0 to 100): Lowest value of the index over the last year.
  - `year_high` (integer, nullable, score from 0 to 100): Highest value of the index over the last year.
  - `year_low_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Day of that lowest value, at midnight UTC.
  - `year_high_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Day of that highest value, at midnight UTC.
  - `altcoin_market_cap_usd` (number, nullable, USD): Total market capitalisation of the altcoins (excluding BTC).

### GET /v1/altcoin-season/history

Altcoin Season history. Family: `sentiment`.

One point per day, at midnight UTC.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (integer, nullable, score from 0 to 100): Altcoin Season Index (CoinMarketCap): how many of the top altcoins outperformed BTC over the last 90 days.
  - `altcoin_market_cap_usd` (number, nullable, USD): Total market capitalisation of the altcoins (excluding BTC).
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/fear-greed

Crypto Fear & Greed Index. Family: `sentiment`.

Daily index from 0 (extreme fear) to 100 (extreme greed).

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (integer, score from 0 to 100): Crypto Fear & Greed Index (alternative.me).
  - `label` (string): Label of the value, from alternative.me's scale: `extreme_fear`, `fear`, `neutral`, `greed` or `extreme_greed` (snake_case, like every labe…

### GET /v1/fear-greed/cmc

CMC Fear & Greed Index. Family: `sentiment`.

CoinMarketCap's Crypto Fear & Greed Index, from 0 (extreme fear) to 100 (extreme greed): a different index from `/v1/fear-greed`, refreshed during the day.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.

`data`: object or null.
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `value` (integer, nullable, score from 0 to 100): CMC Crypto Fear & Greed Index (CoinMarketCap), a different index from `/v1/fear-greed` (alternative.me).
  - `label` (string, nullable): Label of the value, from CoinMarketCap's scale: `extreme_fear`, `fear`, `neutral`, `greed` or `extreme_greed` (snake_case, like every label…

### GET /v1/fear-greed/cmc/history

CMC Fear & Greed history. Family: `sentiment`.

One point per day, at midnight UTC.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (integer, nullable, score from 0 to 100): CMC Crypto Fear & Greed Index (CoinMarketCap), a different index from `/v1/fear-greed` (alternative.me).
  - `label` (string, nullable): Label of the value, from CoinMarketCap's scale: `extreme_fear`, `fear`, `neutral`, `greed` or `extreme_greed` (snake_case, like every label…
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/fear-greed/history

Fear & Greed history. Family: `sentiment`.

One point per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (integer, score from 0 to 100): Crypto Fear & Greed Index (alternative.me).
  - `label` (string): Label of the value, from alternative.me's scale: `extreme_fear`, `fear`, `neutral`, `greed` or `extreme_greed` (snake_case, like every labe…
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/global

Total crypto market. Family: `price_volume`.

Total market capitalisation, 24 h volume and dominance of BTC, ETH and the rest.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,market_cap_total_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant the source states for its measurement (often the last millisecond of its minute, `…:59.999Z`).
  - `market_cap_total_usd` (number, USD): Total crypto market capitalisation.
  - `volume_total_usd` (number, USD): Total traded volume, USD.
  - `btc_dominance_pct` (number, percent (58.5 = 58.5 %)): Bitcoin share of the total market cap.
  - `eth_dominance_pct` (number, percent (58.5 = 58.5 %)): Ether share of the total market cap.
  - `others_dominance_pct` (number, percent (58.5 = 58.5 %)): Share of every other asset.
  - `active_cryptocurrency_count` (integer, count): Number of tracked crypto assets.

### GET /v1/global/history

Total crypto market history. Family: `price_volume`.

Most recent first, or oldest first with `order=asc`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` — one of 1h, 4h, 1d. Optional row step: `1h`, `4h` or `1d` — the LAST reading of each closed bucket, dated at the start of the bucket (the bucket in progress is not served).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,market_cap_total_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The instant the source states for each measurement.
  - `market_cap_total_usd` (number, USD): Total crypto market capitalisation.
  - `volume_total_usd` (number, USD): Total traded volume, USD.
  - `btc_dominance_pct` (number, percent (58.5 = 58.5 %)): Bitcoin share of the total market cap.
  - `eth_dominance_pct` (number, percent (58.5 = 58.5 %)): Ether share of the total market cap.
  - `others_dominance_pct` (number, percent (58.5 = 58.5 %)): Share of every other asset.
  - `active_cryptocurrency_count` (integer, count): Number of tracked crypto assets.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/indices/cmc100

CoinMarketCap 100 Index. Family: `sentiment`.

Value of the CMC100 index (the 100 largest crypto assets), its 24 h change and its constituents with their weight.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.

`data`: object or null.
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `value` (number, nullable, index points): CoinMarketCap 100 Index: the 100 largest crypto assets, weighted by market capitalisation.
  - `constituents` (array): The assets of the index, with their weight.
  - `change_24h_pct` (number, nullable, percent (58.5 = 58.5 %)): Change of the index over the last 24 hours.

### GET /v1/indices/cmc100/history

CoinMarketCap 100 Index history. Family: `sentiment`.

One value per day, at midnight UTC.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (number, nullable, index points): CoinMarketCap 100 Index: the 100 largest crypto assets, weighted by market capitalisation.
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/indices/cmc20

CoinMarketCap 20 Index. Family: `sentiment`.

Value of the CMC20 index (the 20 largest crypto assets), its 24 h change and its constituents with their weight.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.

`data`: object or null.
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `value` (number, nullable, index points): CoinMarketCap 20 Index: the 20 largest crypto assets, weighted by market capitalisation.
  - `constituents` (array): The assets of the index, with their weight.
  - `change_24h_pct` (number, nullable, percent (58.5 = 58.5 %)): Change of the index over the last 24 hours.

### GET /v1/indices/cmc20/history

CoinMarketCap 20 Index history. Family: `sentiment`.

One value per day, at midnight UTC.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `value` (number, nullable, index points): CoinMarketCap 20 Index: the 20 largest crypto assets, weighted by market capitalisation.
  - `is_closed` (boolean, nullable): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/tokenomics

Supply, market cap and FDV. Family: `tokenomics`.

Circulating, total and max supply, with market cap and FDV derived from the latest price at request time (pegged at 1 for stablecoins, FDV null).

Parameters:
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,circulating_supply`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `circulating_supply` (number, nullable, coins): Coins in circulation.
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `max_supply` (number, nullable, coins): Hard cap on supply.
  - `price_usd` (number, USD): Price used for market_cap_usd and fdv_usd: the close of the latest closed one-minute candle (the USDT price of the pair, read as USD), refr…
  - `priced_at` (string, nullable, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of `price_usd` (the row's `time` is the instant of the supply data).
  - `market_cap_usd` (number, nullable, USD): circulating_supply × current price, in USD, derived at request time.
  - `fdv_usd` (number, nullable, USD): Fully diluted valuation: max_supply (or total_supply if uncapped) × price.

### GET /v1/tokenomics/history

Supply and market cap history. Family: `tokenomics`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `symbol` **(required)**. Trading pair, e.g. `BTCUSDT`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,price_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `price_usd` (number, USD): Daily closing price used for the derived values.
  - `circulating_supply` (number, nullable, coins): Coins in circulation.
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `max_supply` (number, nullable, coins): Hard cap on supply.
  - `market_cap_usd` (number, nullable, USD): circulating_supply × current price, in USD, derived at request time.
  - `fdv_usd` (number, nullable, USD): Fully diluted valuation: max_supply (or total_supply if uncapped) × price.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Macro

### GET /v1/macro

Latest value of one macro series. Family: `macro`.

Latest value of ONE FRED series (`series` required); the latest value of every series is `/v1/macro/series`.

Parameters:
- `series` **(required)** — string. FRED series id (e.g. `DGS10`).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,category`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day of the observation, at midnight UTC.
  - `category` (string): Series category.
  - `name` (string): Human-readable name of the series.
  - `frequency` (string): Publication frequency of the source (`daily`, `weekly`, `monthly`).
  - `units` (string): Unit of `value` as published by the source.
  - `value` (number, see `units`): Latest value of the series, in the unit given by `units`.

### GET /v1/macro/correlations

BTC correlation with macro. Family: `macro`.

Rolling Pearson correlation of BTC daily returns with the dollar index, the S&P 500, gold and the VIX, over 30 and 90 days.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oldest_input_date`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the last date used by the window (at the top level, the most recent of all windows; see `oldest_input_date`).
  - `oldest_input_date` (string, calendar date (YYYY-MM-DD)): Date of the OLDEST input the value uses (a monthly series lags a daily one): the value cannot be fresher than this input.
  - `method` (string): How the value is computed.
  - `correlations` (object): Pearson correlation from -1 to 1, per macro series and window, with `sample_count` = number of common days.

### GET /v1/macro/history

Macro series history. Family: `macro`.

Values of one series at its native frequency.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `series` **(required)** — string. FRED series id, e.g. `DGS10`, `CPIAUCSL`, `WALCL`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,value`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day of the observation, at midnight UTC.
  - `value` (number, see the series `units`): Value of the series on the day of `time`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/macro/intraday/history

Intraday macro candles. Family: `macro`.

OHLCV candles of one instrument, most recent first (`data` is the list of candles; `series` and `timeframe` are recalled in the envelope).

Parameters:
- `since_ms` — integer. Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer. Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `series` **(required)** — string. The `series` returned by `GET /v1/macro/intraday/series` (e.g. `PAXGUSDT`), in any case.
- `timeframe` **(required)** — one of 1m, 5m, 15m, 1h, 4h, 1d. Candle size, required.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,open`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket the row covers: a 1h bucket at 14:00 covers 14:00:00 to 14:59:59.999.
  - `open` (number, series unit): Open.
  - `high` (number, series unit): High.
  - `low` (number, series unit): Low.
  - `close` (number, series unit): Close.
  - `volume` (number, nullable, see `volume_kind`): Volume reported by the source for this instrument (not the whole market).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/macro/intraday/series

Intraday macro instruments. Family: `macro`.

Instruments with intraday candles (FX, dollar index, gold, oil, US yields, VIX...), the timeframes each serves, their history depth and last candle.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=series,source`.

`data`: list (newest first unless `order=asc`).
  - `series` (string): Series identifier (the value of the `series` parameter).
  - `source` (string): Upstream source.
  - `instrument_code` (string): Code of the instrument at the source (informative; use `series` in requests).
  - `category` (string): Series category.
  - `name` (string): Human-readable name of the series.
  - `units` (string): Unit of `value` as published by the source.
  - `volume_kind` (string): What `volume` measures for this instrument (`broker` = the source's own flow, not the whole market).
  - `timeframes` (array): Timeframes natively collected for the series.
  - `history_start_date` (string, calendar date (YYYY-MM-DD)): First day of available history.
  - `last_candle_at` (object): Last candle available, per timeframe.

### GET /v1/macro/momentum

Macro momentum score. Family: `macro`.

A -100 to +100 score of macro tailwind for crypto (money supply, Fed balance sheet, dollar) over 30 and 90 days, with each input's contribution.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oldest_input_date`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the date of the most recent input.
  - `oldest_input_date` (string, calendar date (YYYY-MM-DD)): Date of the OLDEST input the value uses (a monthly series lags a daily one): the value cannot be fresher than this input.
  - `scale` (string): Reading scale of the score.
  - `30d` (object): Momentum score over the last 30d, from -100 to +100.
  - `90d` (object): Momentum score over the last 90d, from -100 to +100.

### GET /v1/macro/net-liquidity

US net liquidity. Family: `macro`.

Fed balance sheet minus Treasury General Account minus overnight reverse repo, in USD, with its components: the latest row of the history (daily grid of the reverse repo; the weekly WALCL and TGA values are the latest known on that day, dated by `walcl_date` / `tga_date`).

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_liquidity_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `net_liquidity_usd` (number, nullable, USD): Fed balance sheet (WALCL) - Treasury General Account (TGA) - overnight reverse repo (ON RRP), in USD.
  - `walcl_usd` (number, nullable, USD): Fed total assets (WALCL), as known on that day.
  - `tga_usd` (number, nullable, USD): Treasury General Account (WTREGEN), as known on that day.
  - `rrp_usd` (number, USD): Overnight reverse repo (RRPONTSYD) of that day.
  - `walcl_date` (string, calendar date (YYYY-MM-DD)): Observation day of the WALCL value used (weekly series).
  - `tga_date` (string, calendar date (YYYY-MM-DD)): Observation day of the TGA value used (weekly series).

### GET /v1/macro/net-liquidity/history

Net liquidity history. Family: `macro`.

Most recent first, or oldest first with `order=asc`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,net_liquidity_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `net_liquidity_usd` (number, nullable, USD): Fed balance sheet (WALCL) - Treasury General Account (TGA) - overnight reverse repo (ON RRP), in USD.
  - `walcl_usd` (number, nullable, USD): Fed total assets (WALCL), as known on that day.
  - `tga_usd` (number, nullable, USD): Treasury General Account (WTREGEN), as known on that day.
  - `rrp_usd` (number, USD): Overnight reverse repo (RRPONTSYD) of that day.
  - `walcl_date` (string, nullable, calendar date (YYYY-MM-DD)): Observation day of the WALCL value used (weekly series).
  - `tga_date` (string, nullable, calendar date (YYYY-MM-DD)): Observation day of the TGA value used (weekly series).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/macro/risk

Risk-on / risk-off score. Family: `macro`.

Five signals (VIX, dollar trend, 10Y-2Y curve, S&P 500 vs its 50-day average, gold trend) and the share that are risk-on, from 0 to 100.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oldest_input_date`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the date of the most recent signal.
  - `oldest_input_date` (string, calendar date (YYYY-MM-DD)): Date of the OLDEST input the value uses (a monthly series lags a daily one): the value cannot be fresher than this input.
  - `score` (number, score from 0 to 100): Share of risk-on signals × 100.
  - `label` (string): `risk_on` (score above 50), `risk_off` (below 50) or `neutral` (exactly 50).
  - `risk_on_signal_count` (integer, count): Signals currently risk-on.
  - `available_signal_count` (integer, count): Signals that could be evaluated (data available).
  - `signal_count` (integer, count): Signals in the model.
  - `signals` (object): Each signal: its `condition` and whether it is risk-on now (`is_risk_on`).
  - `context` (object): The raw inputs used by the signals.

### GET /v1/macro/series

Macro series catalogue. Family: `macro`.

Every active FRED series with its category, unit, frequency and latest value.

Parameters:
- `category` — string. Filter by category, e.g. `rates`, `inflation`, `liquidity`, `commodities`.
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,series`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day of the latest observation of the series, at midnight UTC.
  - `series` (string): Series identifier (the value of the `series` parameter).
  - `category` (string): Series category.
  - `name` (string): Human-readable name of the series.
  - `frequency` (string): Publication frequency of the source (`daily`, `weekly`, `monthly`).
  - `units` (string): Unit of `value` as published by the source.
  - `value` (number, see `units`): Latest value of the series, in the unit given by `units`.

## ETF

### GET /v1/etf/fundamentals

ETF fundamentals per issuer. Family: `etf`.

Latest SEC EDGAR anchor per spot ETF: shares outstanding, NAV, net assets and coins held.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,ticker`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The balance-sheet date of the filing — the day the holdings, NAV and net assets are measured (end of the quarter for a 10-Q), at midnight U…
  - `ticker` (string): ETF ticker.
  - `issuer` (string): ETF issuer.
  - `shares_outstanding` (number, shares): ETF shares outstanding.
  - `nav_per_share_usd` (number, USD): Net asset value per share.
  - `net_assets_usd` (number, USD): Net assets (AUM).
  - `form` (string): SEC form type of the filing (`10-Q`, `10-K`...).
  - `filed_date` (string, calendar date (YYYY-MM-DD)): Filing date at the SEC.
  - `filing_url` (string): Link to the filing on SEC EDGAR.
  - `holdings` (number, nullable, units of the asset (BTC for asset=BTC, ETH for asset=ETH)): Crypto held by the fund, in units of the asset.
  - `is_holdings_estimated` (boolean): `true` if the holdings are derived from net assets / price rather than read in the filing.

### GET /v1/etf/fundamentals/history

ETF fundamentals history. Family: `etf`.

One row per filing and issuer.

Parameters:
- `ticker` — string. ETF ticker (e.g. `IBIT`, `FBTC`).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to read, most recent first by default.
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,ticker`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The balance-sheet date of the filing — the day the holdings, NAV and net assets are measured (end of the quarter for a 10-Q), at midnight U…
  - `ticker` (string): ETF ticker.
  - `issuer` (string): ETF issuer.
  - `shares_outstanding` (number, shares): ETF shares outstanding.
  - `nav_per_share_usd` (number, USD): Net asset value per share.
  - `net_assets_usd` (number, USD): Net assets (AUM).
  - `form` (string): SEC form type of the filing (`10-Q`, `10-K`...).
  - `filed_date` (string, calendar date (YYYY-MM-DD)): Filing date at the SEC.
  - `filing_url` (string): Link to the filing on SEC EDGAR.
  - `holdings` (number, nullable, units of the asset (BTC for asset=BTC, ETH for asset=ETH)): Crypto held by the fund, in units of the asset.
  - `is_holdings_estimated` (boolean, nullable): `true` if the holdings are derived from net assets / price rather than read in the filing.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Options

### GET /v1/options/expiry

Per-expiry breakdown. Family: `options`.

Every active expiry: open interest, put/call ratio, max pain, top call and put strikes, the ATM IV of that expiry.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,expiry_at`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `expiry_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Expiry instant (08:00 UTC).
  - `time_to_expiry_s` (number, seconds): Time left before expiry, in seconds.
  - `oi_call_usd` (number, nullable, USD): Call open interest, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest, USD.
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `max_pain_strike_usd` (number, USD): Strike at which option holders lose the most at expiry (max pain).
  - `top_call_strike_usd` (number, USD): Strike with the largest call open interest.
  - `top_put_strike_usd` (number, USD): Strike with the largest put open interest.
  - `iv_atm_pct` (number, percent (58.5 = 58.5 %)): At-the-money implied volatility of THIS expiry, annualised, in percent (55.2 = 55.2 %).
  - `put_call_label` (string): `bullish` (put_call_ratio < 0.7), `neutral`, or `bearish` (put_call_ratio > 1).

### GET /v1/options/greeks

Aggregated greeks. Family: `options`.

Delta, gamma, theta and vega of open options, recomputed under one convention and OI-weighted, so they add up across venues.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,delta`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `delta` (number, delta): Aggregated delta of open options, OI-weighted (per unit of underlying).
  - `gamma` (number, delta per USD): Change of delta for a 1 USD move of the underlying, OI-weighted.
  - `theta` (number, USD per day): Time decay per day, OI-weighted.
  - `vega` (number, USD per volatility point): Value change for +1 point of implied volatility, OI-weighted.
  - `coverage` (object): `oi_coverage_ratio`: share of the open interest covered by the venues that answered (1.0 = all).

### GET /v1/options/iv

ATM implied volatility (30 days). Family: `options`.

At-the-money implied volatility at a constant 30-day maturity, aggregated across venues, in percent: interpolated in total variance between the two expiries around 30 days.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,iv_atm_30d_pct`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `iv_atm_30d_pct` (number, percent (58.5 = 58.5 %)): At-the-money implied volatility at a constant 30-day maturity, annualised, in percent (55.2 = 55.2 %).

### GET /v1/options/iv/klines

Latest 30-day ATM IV candle. Family: `options`.

The latest CLOSED candle of the 30-day ATM implied volatility (`timeframe` required), in percent: `open_pct`, `high_pct`, `low_pct`, `close_pct`.

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,open_pct`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the latest CLOSED bucket; the candle summarises its options snapshots.
  - `open_pct` (number, percent (58.5 = 58.5 %)): 30-day ATM IV at the start of the bucket.
  - `high_pct` (number, percent (58.5 = 58.5 %)): Highest 30-day ATM IV.
  - `low_pct` (number, percent (58.5 = 58.5 %)): Lowest 30-day ATM IV.
  - `close_pct` (number, percent (58.5 = 58.5 %)): 30-day ATM IV at the end of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/iv/klines/history

30-day ATM IV candles. Family: `options`.

OHLC of the 30-day ATM implied volatility per bucket, in percent (`open_pct`...

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,open_pct`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the value is the LAST options snapshot of the bucket.
  - `open_pct` (number, percent (58.5 = 58.5 %)): 30-day ATM IV at the start of the bucket.
  - `high_pct` (number, percent (58.5 = 58.5 %)): Highest 30-day ATM IV.
  - `low_pct` (number, percent (58.5 = 58.5 %)): Lowest 30-day ATM IV.
  - `close_pct` (number, percent (58.5 = 58.5 %)): 30-day ATM IV at the end of the bucket.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/max-pain

Max pain per expiry. Family: `options`.

Max pain strike of every active expiry, with the time left (`time_to_expiry_s`), put/call ratio and open interest.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,expiry_at`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `expiry_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Expiry instant (08:00 UTC).
  - `time_to_expiry_s` (number, seconds): Time left before expiry, in seconds.
  - `max_pain_strike_usd` (number, USD): Strike at which option holders lose the most at expiry (max pain).
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `oi_call_usd` (number, nullable, USD): Call open interest, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest, USD.

### GET /v1/options/max-pain/history

Max pain history of one expiry. Family: `options`.

How the max pain of ONE expiry moved.

Parameters:
- `expiry` **(required)** — string. REQUIRED.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,max_pain_strike_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The instant of the options snapshot the max pain was computed on (one row per snapshot, about every minute; no `timeframe`).
  - `max_pain_strike_usd` (number, USD): Strike at which option holders lose the most at expiry (max pain).
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/oi

Options open interest. Family: `options`.

Calls and puts, in USD and in coins.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi_total_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `oi_total_usd` (number, USD): Total open interest, USD.
  - `oi_call_usd` (number, nullable, USD): Call open interest, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest, USD.
  - `oi_call` (number, base asset quantity (BTC for BTCUSDT)): Call open interest, in coins (base asset).
  - `oi_put` (number, base asset quantity (BTC for BTCUSDT)): Put open interest, in coins (base asset).
  - `coverage` (object): `oi_coverage_ratio`: share of the open interest covered by the venues that answered (1.0 = all).

### GET /v1/options/oi/change

Options open interest change. Family: `options`.

Change of call and put open interest over a rolling `timeframe`: from the snapshot `window_start_at` (at least `timeframe` earlier) to the latest one (`time`).

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,window_start_at`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `window_start_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Instant of the reference snapshot: the latest one at least `timeframe` before `time`.
  - `window_s` (integer, nullable, seconds): Actual distance between the two snapshots, in whole seconds (`timeframe` or a little more: snapshots arrive every minute).
  - `oi_change_call_usd` (number, nullable, USD): Change of call open interest from `window_start_at` to `time`, USD.
  - `oi_change_put_usd` (number, nullable, USD): Change of put open interest from `window_start_at` to `time`, USD.
  - `oi_change_total_usd` (number, nullable, USD): Change of total open interest from `window_start_at` to `time`, USD.

### GET /v1/options/oi/change/history

Options OI change history. Family: `options`.

Per bucket.

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi_change_call_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the value is the LAST options snapshot of the bucket.
  - `oi_change_call_usd` (number, nullable, USD): Change of call open interest from `window_start_at` to `time`, USD.
  - `oi_change_put_usd` (number, nullable, USD): Change of put open interest from `window_start_at` to `time`, USD.
  - `oi_change_total_usd` (number, nullable, USD): Change of total open interest from `window_start_at` to `time`, USD.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/oi/distribution

Open interest per strike. Family: `options`.

Latest open interest per (expiry, strike), calls and puts separately.

Parameters:
- `expiry` — string. Restrict to one expiry: `YYYY-MM-DD`, or the `expiry_at` date-time as served (`2026-10-30T08:00:00.000Z`).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,expiry_at`.

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `expiry_at` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Expiry instant (08:00 UTC).
  - `strike_usd` (number, USD): Strike price.
  - `oi_call_usd` (number, nullable, USD): Call open interest at this strike, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest at this strike, USD.

### GET /v1/options/oi/history

Options open interest history. Family: `options`.

Per bucket.

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,oi_total_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the value is the LAST options snapshot of the bucket.
  - `oi_total_usd` (number, USD): Total open interest, USD.
  - `oi_call_usd` (number, nullable, USD): Call open interest, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest, USD.
  - `oi_call` (number, base asset quantity (BTC for BTCUSDT)): Call open interest, in coins (base asset).
  - `oi_put` (number, base asset quantity (BTC for BTCUSDT)): Put open interest, in coins (base asset).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/put-call-ratio

Put/call ratio. Family: `options`.

Put/call open interest ratio (`put_call_ratio`) and its reading (`put_call_label`).

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,put_call_ratio`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `put_call_label` (string): `bullish` (put_call_ratio < 0.7), `neutral`, or `bearish` (put_call_ratio > 1).

### GET /v1/options/put-call-ratio/history

Put/call ratio history. Family: `options`.

Per bucket.

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,put_call_ratio`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the value is the LAST options snapshot of the bucket.
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `put_call_label` (string): `bullish` (put_call_ratio < 0.7), `neutral`, or `bearish` (put_call_ratio > 1).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/options/summary

Options market summary. Family: `options`.

Open interest and volume (calls/puts, USD), put/call ratio and signal, 30-day ATM IV and the nearest expiry, aggregated across options venues.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,underlying_price_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `underlying_price_usd` (number, USD): Index (spot) price of the underlying, from the options venues.
  - `oi_total_usd` (number, USD): Total open interest, USD.
  - `oi_call_usd` (number, nullable, USD): Call open interest, USD.
  - `oi_put_usd` (number, nullable, USD): Put open interest, USD.
  - `volume_total_usd` (number, USD): Total traded volume, USD.
  - `volume_call_usd` (number, USD): Call volume, USD.
  - `volume_put_usd` (number, USD): Put volume, USD.
  - `put_call_ratio` (number, nullable, puts / calls): Put/call open interest ratio (a quotient, not a share: 1.2 = 1.2 puts per call).
  - `put_call_label` (string): `bullish` (put_call_ratio < 0.7), `neutral`, or `bearish` (put_call_ratio > 1).
  - `iv_atm_30d_pct` (number, percent (58.5 = 58.5 %)): At-the-money implied volatility at a constant 30-day maturity, annualised, in percent (55.2 = 55.2 %).
  - `nearest_expiry` (object): The next expiry: its instant, the time left, max pain, put/call ratio, ATM IV.
  - `coverage` (object): `oi_coverage_ratio`: share of the open interest covered by the venues that answered (1.0 = all).

### GET /v1/options/volume

Options volume. Family: `options`.

Calls and puts traded, USD.

Parameters:
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,volume_total_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the options snapshot (all venues read together).
  - `volume_total_usd` (number, USD): Total traded volume, USD.
  - `volume_call_usd` (number, USD): Call volume, USD.
  - `volume_put_usd` (number, USD): Put volume, USD.
  - `coverage` (object): `oi_coverage_ratio`: share of the open interest covered by the venues that answered (1.0 = all).

### GET /v1/options/volume/history

Options volume history. Family: `options`.

Per bucket.

Parameters:
- `timeframe` **(required)** — one of 5m, 15m, 30m, 1h, 4h, 1d. Bucket size, required: `5m`, `15m`, `30m`, `1h`, `4h` or `1d` (`1m` is not served on options).
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `asset` **(required)** — one of BTC, ETH. Asset, e.g. `BTC` or `ETH` (no quote currency), in any case (`eth` works; the envelope gives the canonical form).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,volume_total_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Start of the bucket; the value is the LAST options snapshot of the bucket.
  - `volume_total_usd` (number, USD): Total traded volume, USD.
  - `volume_call_usd` (number, USD): Call volume, USD.
  - `volume_put_usd` (number, USD): Put volume, USD.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Bitcoin network

### GET /v1/btc/fees

Recommended Bitcoin fees. Family: `onchain`.

Fee rates for each confirmation target (sat/vB): the rounded rates under the same names as the history, the unrounded ones as `<name>_precise_sat_vb`, and the fee pressure (`fastest_economy_ratio` and its label).

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,fastest_fee_sat_vb`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `fastest_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for the next block.
  - `half_hour_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for confirmation within ~30 minutes.
  - `hour_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for confirmation within ~1 hour.
  - `economy_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for a low-priority confirmation.
  - `minimum_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Minimum relay fee rate.
  - `fastest_fee_precise_sat_vb` (number, satoshis per virtual byte (sat/vB)): `fastest_fee_sat_vb`, unrounded.
  - `half_hour_fee_precise_sat_vb` (number, satoshis per virtual byte (sat/vB)): `half_hour_fee_sat_vb`, unrounded.
  - `hour_fee_precise_sat_vb` (number, satoshis per virtual byte (sat/vB)): `hour_fee_sat_vb`, unrounded.
  - `economy_fee_precise_sat_vb` (number, satoshis per virtual byte (sat/vB)): `economy_fee_sat_vb`, unrounded.
  - `minimum_fee_precise_sat_vb` (number, satoshis per virtual byte (sat/vB)): `minimum_fee_sat_vb`, unrounded.
  - `fee_pressure` (object): `fastest_economy_ratio` = fastest / economy fee rate, and its `label`: `normal` (<= 2), `elevated` (> 2), `congested` (> 5).

### GET /v1/btc/fees/history

Bitcoin fees history. Family: `onchain`.

Most recent first, or oldest first with `order=asc`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `timeframe` — one of 1h, 4h, 1d. Optional row step: `1h`, `4h` or `1d` — the LAST reading of each closed bucket, dated at the start of the bucket (the bucket in progress is not served).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,fastest_fee_sat_vb`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Without `timeframe`: the instant of the reading.
  - `fastest_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for the next block.
  - `half_hour_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for confirmation within ~30 minutes.
  - `hour_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for confirmation within ~1 hour.
  - `economy_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Fee rate for a low-priority confirmation.
  - `minimum_fee_sat_vb` (integer, satoshis per virtual byte (sat/vB)): Minimum relay fee rate.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/btc/mempool

Bitcoin mempool. Family: `onchain`.

Pending transactions, virtual size, total fees, fee histogram and the 1 h / 4 h / 24 h trend.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,tx_count`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `tx_count` (integer, count): Unconfirmed transactions in the mempool.
  - `vsize` (integer, virtual bytes): Total virtual size of the mempool.
  - `total_fee_sats` (integer, satoshis): Total fees waiting in the mempool.
  - `fee_histogram` (array): `[fee_rate, vsize]` pairs: how much virtual size (virtual bytes) waits at each fee rate (sat/vB).
  - `trend` (object): Mempool size change over 1 h, 4 h and 24 h, and its `label` (`filling`, `draining`, `stable`).

### GET /v1/btc/mempool/history

Mempool history. Family: `onchain`.

Most recent first, or oldest first with `order=asc`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,tx_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `tx_count` (integer, count): Unconfirmed transactions in the mempool.
  - `vsize` (integer, virtual bytes): Total virtual size of the mempool.
  - `total_fee_sats` (integer, satoshis): Total fees waiting in the mempool.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/btc/mining

Mining pool concentration. Family: `onchain`.

Share of the largest pools, pool ranking and the latest block reward in sats and USD, with the BTC price AT THAT BLOCK (`latest_reward.btc_price_usd`, with its `block_height` and `time`) — not the current price (see `/v1/klines`).

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `concentration` (object): Mining pool concentration over the last period.
  - `latest_reward` (object): Average block reward (subsidy + fees) of the latest blocks, in satoshis and USD.
  - `pools` (array): Pools ranked by blocks mined: `name`, `slug`, `block_count`, `rank`, `share_pct`.

### GET /v1/btc/mining/history

Mining history. Family: `onchain`.

One series selected by `dataset`.

Parameters:
- `dataset` — one of concentration, rewards, difficulty, fee_rates. Which mining series to return: `concentration` (pool shares), `rewards` (block rewards), `difficulty` or `fee_rates`.
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,total_block_count`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `total_block_count` (integer, count): Blocks in the period.
  - `top1_share_pct` (number, percent (58.5 = 58.5 %)): Share of blocks mined by the largest pool.
  - `top3_share_pct` (number, percent (58.5 = 58.5 %)): Share of blocks mined by the three largest pools.
  - `pool_count` (integer, count): Number of pools that mined at least one block.
  - `label` (string): Centralisation risk from the top-3 pool share: `healthy` (<= 40 %), `moderate` (> 40 %), `high_risk` (> 50 %).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…
  - `block_height` (integer, nullable, block height): Height of a block: the latest block on `/v1/btc/network`; the reward sample in `latest_reward`; the block where a difficulty adjustment too…
  - `avg_reward_sats` (integer, nullable, satoshis): Average block reward.
  - `avg_reward_usd` (number, nullable, USD): Average block reward in USD.
  - `btc_price_usd` (number, nullable, USD): BTC price in USD at the time of the row: the current price on `/v1/eth/price-btc`, the price at the block of the reward in `latest_reward`…
  - `difficulty` (number, nullable, difficulty units): Network mining difficulty (on a difficulty-adjustment row, the difficulty after it).
  - `previous_difficulty` (number, nullable, difficulty units): Difficulty before the adjustment.
  - `difficulty_change_pct` (number, nullable, percent (58.5 = 58.5 %)): Expected difficulty change at the next adjustment (`/v1/btc/mining/history?dataset=difficulty`: the change applied at that adjustment).
  - `adjustment_multiplier` (number, nullable, dimensionless ratio): `difficulty / previous_difficulty` (1.05 = a 5 % rise).
  - `fee_rate_p0_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): Lowest fee rate paid in the blocks (0th percentile).
  - `fee_rate_p10_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): 10th percentile of the fee rates paid in the blocks.
  - `fee_rate_p25_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): 25th percentile of the fee rates paid in the blocks.
  - `fee_rate_p50_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): Median fee rate paid in the blocks.
  - `fee_rate_p75_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): 75th percentile of the fee rates paid in the blocks.
  - `fee_rate_p90_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): 90th percentile of the fee rates paid in the blocks.
  - `fee_rate_p100_sat_vb` (integer, nullable, satoshis per virtual byte (sat/vB)): Highest fee rate paid in the blocks.

### GET /v1/btc/network

Bitcoin network state. Family: `onchain`.

Height, difficulty and progress of the current period under the same names as the history, plus the 24 h block time and the details of the next difficulty adjustment.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,difficulty`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `difficulty` (number, nullable, difficulty units): Network mining difficulty (on a difficulty-adjustment row, the difficulty after it).
  - `block_height` (integer, block height): Height of a block: the latest block on `/v1/btc/network`; the reward sample in `latest_reward`; the block where a difficulty adjustment too…
  - `progress_pct` (number, percent (58.5 = 58.5 %)): Progress through the current 2016-block difficulty period.
  - `difficulty_change_pct` (number, percent (58.5 = 58.5 %)): Expected difficulty change at the next adjustment (`/v1/btc/mining/history?dataset=difficulty`: the change applied at that adjustment).
  - `block_time` (object): Average block time over 24 h (`avg_24h_s`), its deviation from the 600 s target, and a `label`.
  - `next_adjustment` (object): Next difficulty adjustment: progress, expected change, date, remaining blocks and time.

### GET /v1/btc/network/history

Network history. Family: `onchain`.

Most recent first, or oldest first with `order=asc`.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,difficulty`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `difficulty` (number, nullable, difficulty units): Network mining difficulty (on a difficulty-adjustment row, the difficulty after it).
  - `block_height` (integer, block height): Height of a block: the latest block on `/v1/btc/network`; the reward sample in `latest_reward`; the block where a difficulty adjustment too…
  - `progress_pct` (number, percent (58.5 = 58.5 %)): Progress through the current 2016-block difficulty period.
  - `difficulty_change_pct` (number, percent (58.5 = 58.5 %)): Expected difficulty change at the next adjustment (`/v1/btc/mining/history?dataset=difficulty`: the change applied at that adjustment).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Ethereum

### GET /v1/eth/defi

Ethereum DeFi. Family: `onchain`.

TVL, DEX volume, TVL / market cap and the 30-day trend.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,tvl_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `tvl_usd` (number, USD): Total value locked in Ethereum DeFi.
  - `dex_volume_24h_usd` (number, USD): DEX volume over 24 h.
  - `dex_volume_7d_usd` (number, USD): DEX volume over 7 days.
  - `eth_market_cap_usd` (number, USD): ETH market capitalisation.
  - `defi_health_ratio` (number, fraction (0.585 = 58.5 %)): tvl_usd / eth_market_cap_usd.
  - `defi_health_change_30d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of `defi_health_ratio` (TVL / ETH market cap) over 30 days, percent.
  - `label` (string): 30-day trend of `defi_health_ratio` (TVL / ETH market cap): `growing`, `declining` or `stable`.

### GET /v1/eth/defi/history

DeFi history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,tvl_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `tvl_usd` (number, USD): Total value locked in Ethereum DeFi.
  - `dex_volume_24h_usd` (number, USD): DEX volume over 24 h.
  - `dex_volume_7d_usd` (number, USD): DEX volume over 7 days.
  - `eth_market_cap_usd` (number, USD): ETH market capitalisation.
  - `defi_health_ratio` (number, fraction (0.585 = 58.5 %)): tvl_usd / eth_market_cap_usd.
  - `defi_health_change_30d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of `defi_health_ratio` (TVL / ETH market cap) over 30 days, percent.
  - `label` (string, nullable): 30-day trend of `defi_health_ratio` (TVL / ETH market cap): `growing`, `declining` or `stable`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/deflation

ETH deflation. Family: `onchain`.

24 h burn versus issuance and the annualised net supply change.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,burn_24h`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `burn_24h` (number, nullable, ETH): ETH burnt over the last 24 h.
  - `net_issuance_24h` (number, nullable, ETH): New ETH issued minus ETH burnt over 24 h.
  - `net_issuance_annualized_pct` (number, nullable, percent (58.5 = 58.5 %)): Net issuance annualised, as a percent of supply.
  - `label` (string): `deflationary` (24 h net issuance < 0) or `inflationary`.

### GET /v1/eth/deflation/history

Deflation history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,burn_24h`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `burn_24h` (number, nullable, ETH): ETH burnt over the last 24 h.
  - `net_issuance_24h` (number, nullable, ETH): New ETH issued minus ETH burnt over 24 h.
  - `net_issuance_annualized_pct` (number, nullable, percent (58.5 = 58.5 %)): Net issuance annualised, as a percent of supply.
  - `label` (string, nullable): `deflationary` (24 h net issuance < 0) or `inflationary`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/gas

Ethereum gas. Family: `onchain`.

Gas prices (gwei), base fee, block usage and congestion.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,safe_gas_price_gwei`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `safe_gas_price_gwei` (number, gwei): Gas price for a low-priority transaction.
  - `propose_gas_price_gwei` (number, gwei): Gas price for a standard transaction.
  - `fast_gas_price_gwei` (number, gwei): Gas price for a fast transaction.
  - `base_fee_gwei` (number, gwei): EIP-1559 base fee (burnt).
  - `gas_used_ratio` (number, fraction (0.585 = 58.5 %)): Block gas used / gas target over recent blocks.
  - `label` (string): Congestion: `low` (gas_used_ratio < 0.5), `normal`, or `high` (> 0.8).

### GET /v1/eth/gas-momentum

Gas momentum. Family: `onchain`.

7-day versus 30-day base fee average: rising or falling demand for block space.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,base_fee_gwei`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `base_fee_gwei` (number, gwei): EIP-1559 base fee (burnt).
  - `gas_used_ratio` (number, fraction (0.585 = 58.5 %)): Block gas used / gas target over recent blocks.
  - `gas_sma_7d_gwei` (number, gwei): 7-day simple moving average of the base fee.
  - `gas_sma_30d_gwei` (number, gwei): 30-day simple moving average of the base fee.
  - `sma_7d_vs_30d_pct` (number, percent (58.5 = 58.5 %)): (7-day simple moving average - 30-day simple moving average) / 30-day average, percent.
  - `label` (string): `high_demand` (gas_used_ratio > 0.8 and sma_7d_vs_30d_pct > 0), `low_demand` (< 0.5 and sma_7d_vs_30d_pct < 0), otherwise `normal`.

### GET /v1/eth/gas-momentum/history

Gas momentum history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,base_fee_gwei`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `base_fee_gwei` (number, gwei): EIP-1559 base fee (burnt).
  - `gas_used_ratio` (number, fraction (0.585 = 58.5 %)): Block gas used / gas target over recent blocks.
  - `gas_sma_7d_gwei` (number, gwei): 7-day simple moving average of the base fee.
  - `gas_sma_30d_gwei` (number, gwei): 30-day simple moving average of the base fee.
  - `sma_7d_vs_30d_pct` (number, percent (58.5 = 58.5 %)): (7-day simple moving average - 30-day simple moving average) / 30-day average, percent.
  - `label` (string): `high_demand` (gas_used_ratio > 0.8 and sma_7d_vs_30d_pct > 0), `low_demand` (< 0.5 and sma_7d_vs_30d_pct < 0), otherwise `normal`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/gas/history

Gas history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,safe_gas_price_gwei`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `safe_gas_price_gwei` (number, gwei): Gas price for a low-priority transaction.
  - `propose_gas_price_gwei` (number, gwei): Gas price for a standard transaction.
  - `fast_gas_price_gwei` (number, gwei): Gas price for a fast transaction.
  - `base_fee_gwei` (number, gwei): EIP-1559 base fee (burnt).
  - `gas_used_ratio` (number, fraction (0.585 = 58.5 %)): Block gas used / gas target over recent blocks.
  - `label` (string): Congestion: `low` (gas_used_ratio < 0.5), `normal`, or `high` (> 0.8).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/price-btc

ETH price in BTC. Family: `onchain`.

The ETH price in BTC (`eth_price_btc`), with both USD prices, its 7-day change and which asset outperforms.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,eth_price_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `eth_price_usd` (number, USD): ETH price.
  - `btc_price_usd` (number, USD): BTC price in USD at the time of the row: the current price on `/v1/eth/price-btc`, the price at the block of the reward in `latest_reward`…
  - `eth_price_btc` (number, BTC): ETH price in BTC (ETH price / BTC price).
  - `change_7d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of the value over 7 days, percent.
  - `label` (string): 7-day momentum of ETH/BTC: `eth_outperform` (> 0), `btc_outperform` (< 0) or `neutral`.

### GET /v1/eth/price-btc/history

ETH price in BTC history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,eth_price_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `eth_price_usd` (number, USD): ETH price.
  - `btc_price_usd` (number, USD): BTC price in USD at the time of the row: the current price on `/v1/eth/price-btc`, the price at the block of the reward in `latest_reward`…
  - `eth_price_btc` (number, BTC): ETH price in BTC (ETH price / BTC price).
  - `change_7d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of the value over 7 days, percent.
  - `label` (string, nullable): 7-day momentum of ETH/BTC: `eth_outperform` (> 0), `btc_outperform` (< 0) or `neutral`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/squeeze

ETH supply squeeze index. Family: `onchain`.

0-100 index combining the staked share and net issuance.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,staking_ratio`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `staking_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the ETH supply staked.
  - `net_issuance_annualized_pct` (number, nullable, percent (58.5 = 58.5 %)): Net issuance annualised, as a percent of supply.
  - `squeeze_index` (number, nullable, score from 0 to 100): Supply squeeze index: combines the staked share and net issuance.
  - `label` (string): `low` (< 33), `moderate` (>= 33), `high` (>= 66).

### GET /v1/eth/squeeze/history

Supply squeeze history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,staking_ratio`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `staking_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the ETH supply staked.
  - `net_issuance_annualized_pct` (number, nullable, percent (58.5 = 58.5 %)): Net issuance annualised, as a percent of supply.
  - `squeeze_index` (number, nullable, score from 0 to 100): Supply squeeze index: combines the staked share and net issuance.
  - `label` (string, nullable): `low` (< 33), `moderate` (>= 33), `high` (>= 66).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/staking

ETH staking. Family: `onchain`.

Share of ETH staked, total staked and the staking APR.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,staking_ratio`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `staking_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the ETH supply staked.
  - `total_staked` (number, nullable, ETH): ETH staked (beacon chain).
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.

### GET /v1/eth/staking/history

Staking history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,staking_ratio`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `staking_ratio` (number, nullable, fraction (0.585 = 58.5 %)): Share of the ETH supply staked.
  - `total_staked` (number, nullable, ETH): ETH staked (beacon chain).
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `apr_pct` (number, percent (58.5 = 58.5 %)): Annualised rate in percent.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/eth/supply

ETH supply and burn. Family: `onchain`.

Supply, staking, burnt fees, withdrawals, 24 h burn and net issuance.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,execution_issuance_cumulative`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): Point-in-time value: the instant of the measurement (when the source was read).
  - `execution_issuance_cumulative` (number, ETH): Cumulative execution-layer issuance (genesis + proof-of-work rewards before the Merge), as published by Etherscan.
  - `consensus_rewards_cumulative` (number, ETH): Cumulative consensus-layer issuance (staking rewards) since the Beacon Chain launch.
  - `burnt_fees_cumulative` (number, ETH): ETH burnt since EIP-1559 (cumulative).
  - `withdrawn_cumulative` (number, ETH): ETH withdrawn from staking (cumulative).
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `burn_24h` (number, nullable, ETH): ETH burnt over the last 24 h.
  - `net_issuance_24h` (number, nullable, ETH): New ETH issued minus ETH burnt over 24 h.
  - `label` (string): `deflationary` (24 h net issuance < 0), `inflationary` (> 0) or `neutral`.

### GET /v1/eth/supply/history

ETH supply history. Family: `onchain`.

One row per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,execution_issuance_cumulative`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day, at midnight UTC; the value is the LAST measurement of that day.
  - `execution_issuance_cumulative` (number, ETH): Cumulative execution-layer issuance (genesis + proof-of-work rewards before the Merge), as published by Etherscan.
  - `consensus_rewards_cumulative` (number, ETH): Cumulative consensus-layer issuance (staking rewards) since the Beacon Chain launch.
  - `burnt_fees_cumulative` (number, ETH): ETH burnt since EIP-1559 (cumulative).
  - `withdrawn_cumulative` (number, ETH): ETH withdrawn from staking (cumulative).
  - `total_supply` (number, nullable, coins): Total coins issued (circulating + locked), net of burns.
  - `burn_24h` (number, nullable, ETH): ETH burnt over the last 24 h.
  - `net_issuance_24h` (number, nullable, ETH): New ETH issued minus ETH burnt over 24 h.
  - `label` (string, nullable): `deflationary` (24 h net issuance < 0), `inflationary` (> 0) or `neutral`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## On-chain Bitcoin

### GET /v1/btc/active-addresses

Bitcoin active addresses. Family: `onchain`.

Daily active addresses, 7- and 30-day averages and momentum.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,active_addresses`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `active_addresses` (number, count): Addresses active on the day.
  - `active_addresses_sma_7d` (number, count): 7-day simple moving average of active_addresses.
  - `active_addresses_sma_30d` (number, count): 30-day simple moving average of active_addresses.
  - `sma_7d_vs_30d_pct` (number, percent (58.5 = 58.5 %)): (7-day simple moving average - 30-day simple moving average) / 30-day average, percent.
  - `label` (string): 7-day vs 30-day average: `accelerating` (> +5 %), `decelerating` (< -5 %) or `stable`.

### GET /v1/btc/active-addresses/history

Active addresses history. Family: `onchain`.

One point per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,active_addresses`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `active_addresses` (number, count): Addresses active on the day.
  - `active_addresses_sma_7d` (number, count): 7-day simple moving average of active_addresses.
  - `active_addresses_sma_30d` (number, count): 30-day simple moving average of active_addresses.
  - `sma_7d_vs_30d_pct` (number, percent (58.5 = 58.5 %)): (7-day simple moving average - 30-day simple moving average) / 30-day average, percent.
  - `label` (string): 7-day vs 30-day average: `accelerating` (> +5 %), `decelerating` (< -5 %) or `stable`.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/btc/mvrv

Bitcoin MVRV. Family: `onchain`.

Market value / realised value with its zone and 30-day momentum.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,mvrv`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `mvrv` (number, dimensionless ratio): Market value / realised value.
  - `label` (string): `undervalued` (<= 1), `fair` (> 1), `elevated` (> 2.5), `overvalued` (> 3.5).
  - `change_30d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of the value over 30 days, percent.

### GET /v1/btc/mvrv/history

MVRV history. Family: `onchain`.

One point per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,mvrv`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `mvrv` (number, dimensionless ratio): Market value / realised value.
  - `label` (string): `undervalued` (<= 1), `fair` (> 1), `elevated` (> 2.5), `overvalued` (> 3.5).
  - `change_30d_pct` (number, nullable, percent (58.5 = 58.5 %)): Relative change of the value over 30 days, percent.
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/btc/nvt

Bitcoin NVT. Family: `onchain`.

Network value to transactions ratio and its 90-day NVT Signal, derived on demand.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,nvt`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `nvt` (number, dimensionless ratio): Market cap / daily on-chain transaction volume (NVT ratio).
  - `nvt_signal` (number, dimensionless ratio): NVT smoothed over 90 days (NVT Signal), less noisy.
  - `label` (string): Zone of the NVT Signal: `undervalued` (<= 45), `fair` (> 45), `overvalued` (> 100), `bubble` (> 150).

### GET /v1/btc/nvt/history

NVT history. Family: `onchain`.

One point per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,nvt`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `nvt` (number, dimensionless ratio): Market cap / daily on-chain transaction volume (NVT ratio).
  - `nvt_signal` (number, dimensionless ratio): NVT smoothed over 90 days (NVT Signal), less noisy.
  - `label` (string): Zone of the NVT Signal: `undervalued` (<= 45), `fair` (> 45), `overvalued` (> 100), `bubble` (> 150).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

### GET /v1/btc/revenue-per-difficulty

Bitcoin revenue per difficulty. Family: `onchain`.

Miner revenue per unit of difficulty (`revenue_per_difficulty_usd`) against its 30-day average, and its reading: `healthy`, `stress` or `capitulation`.

Parameters:
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,revenue_per_difficulty_usd`.

`data`: object or null.
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `revenue_per_difficulty_usd` (number, USD per unit of difficulty): Miners' daily revenue (USD) divided by the network difficulty of the day: revenue per unit of work.
  - `revenue_per_difficulty_sma_30d_usd` (number, USD per unit of difficulty): 30-day simple moving average of revenue_per_difficulty_usd.
  - `label` (string): `healthy` (at or above its 30-day average), `stress` (below it), `capitulation` (below 70 % of it — historically near BTC bottoms).

### GET /v1/btc/revenue-per-difficulty/history

Revenue per difficulty history. Family: `onchain`.

One point per day.

Parameters:
- `since_ms` — integer (min 0). Lower time bound, INCLUSIVE, in epoch MILLISECONDS (13 digits).
- `until_ms` — integer (min 0). Upper time bound, INCLUSIVE to the millisecond, in epoch milliseconds.
- `limit` — integer (min 1, max 1000) — default `100`. Number of rows to return, in the reading order (most recent first by default).
- `fields` — string. Comma-separated projection of `data` (dot notation for nested keys): `fields=time,revenue_per_difficulty_usd`.
- `before_ms` — integer (min 0). Upper time bound, EXCLUSIVE, in epoch milliseconds: rows strictly before it.
- `order` — one of asc, desc. Reading order: `desc` (most recent first, the default) or `asc` (oldest first, reading forward from `since_ms`, which is then required).

`data`: list (newest first unless `order=asc`).
  - `time` (string, ISO 8601 UTC, milliseconds (2026-09-28T14:00:00.000Z)): The day the value refers to, at midnight UTC.
  - `revenue_per_difficulty_usd` (number, USD per unit of difficulty): Miners' daily revenue (USD) divided by the network difficulty of the day: revenue per unit of work.
  - `revenue_per_difficulty_sma_30d_usd` (number, USD per unit of difficulty): 30-day simple moving average of revenue_per_difficulty_usd.
  - `label` (string): `healthy` (at or above its 30-day average), `stress` (below it), `capitulation` (below 70 % of it — historically near BTC bottoms).
  - `is_closed` (boolean): `true` = the row is final; `false` = provisional: the latest bucket while it still settles (a few seconds after its end, e.g. a candle whos…

## Technical indicators

### POST /v1/indicators

Compute technical indicators. Family: `indicators`.

POST a JSON body: `symbol`, `timeframe`, `limit` (values per indicator, 1 to 1000, default 1) and `indicators`, a list of `{id, type, <parameters flat>}` — e.g. `{"id": "rsi_14", "type": "rsi", "period": 14}`.

JSON body: see `indicators.generated.md`.

`data`: object or null.
  - `indicators` (object): One result per indicator of the request, keyed by the `id` you gave it.
