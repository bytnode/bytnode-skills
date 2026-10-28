---
name: bytnode-api
description: Use when calling the BytNode crypto market-data API (api.bytnode.com) or writing code against it — candles, trades, funding, open interest, basis, liquidations, CVD, order book, options, technical indicators, on-chain, ETF, macro or sentiment data — or when handling its errors (401, 403 history_depth or plan_family, 422, 429), paging its history, sizing requests to a plan, or choosing between its REST API, MCP server, WebSocket and SDKs. Also use whenever a user mentions BytNode, a cb_live_ key or BYTNODE_API_KEY.
---

# Using the BytNode REST API

BytNode serves crypto market data aggregated across the major venues behind one key, one
response envelope and one set of conventions. Everything below holds on every route, so learn it
once. The full route list, units and error codes are in `references/` — search them instead of
guessing a path or a field.

## Pick the channel first

| The user wants… | Use |
|---|---|
| an answer to a market question, inside a chat | the MCP server — see the `bytnode-mcp` skill |
| code, a script, a dashboard, a dataset | REST (this skill) or the official SDKs (`bytnode-sdk`) |
| a backtest or a long history download | REST + the `bytnode-history-backtest` skill |
| live trades, liquidations or order books | the WebSocket (`bytnode-realtime-stream`, Traders plan and up) |

The API is read-only market data: no orders, no account data. It never says which exchange a
number came from (except `/v1/spread/interexchange`): do not promise per-exchange figures.

## Start with discovery — never guess the plan or the pairs

```bash
curl -H "X-API-KEY: $BYTNODE_API_KEY" https://api.bytnode.com/v1/limits   # free, not counted
```

`/v1/limits` returns `plan` (`free`, `traders`, `financial`, `startup`, `enterprise`), the
`families` the key may read (`null` = all), `history` — a list of `{timeframe, window_s}`
(`window_s` in seconds, `null` = unlimited, `0` = not in the plan) — `trades_window_s`,
`liquidations_events_count`, the per-minute `rate` and the monthly `quota` with what is left
(`remaining_count`). Read it before sizing any history request: it is how you avoid a 403
instead of discovering it.

Only the families matter for access: on Free, REST `/v1/funding/next`, `/v1/oi` or `/v1/basis`
work (family `derivatives`); what Free lacks is the `snapshot` family (and with it the MCP's
"current value" mode — see `bytnode-mcp`).

- Pairs: `GET /v1/symbols` (never hard-code the list or its size; it grows). Spot-only
  stablecoin pairs (`USDCUSDT`, `USDTUSDC`) have no futures data.
- What one pair supports: `GET /v1/capabilities?symbol=BTCUSDT`.
- Feed freshness: `GET /v1/status`. Health without a key: `GET /v1/health`.
- Each route's family (what `families` lists) is in `references/routes.generated.md`; which plan
  opens which family, and indicative limits: `references/plans.md`.

`scripts/bytnode_client.py` is a dependency-free Python client (key from `BYTNODE_API_KEY`,
`Retry-After` handling, `next` pagination, typed errors). Use it directly, or copy its loop.

## Requests

- `https://api.bytnode.com` + path. HTTPS only (plain HTTP is a 403 `https_required`).
- Key in `X-API-KEY: <key>` (or `Authorization: Bearer <key>`). Never put a key in a web page.
- Parameters are **strict**: an unknown or repeated one is a 422 with a suggestion
  (`limt` → `limit`); an unknown value of a closed set lists the accepted ones in
  `error.details.accepted`. `symbol`, `asset`, `timeframe`, `series` are case-insensitive.
- `?fields=a,b.c` projects `data` to the fields you need.
- Time bounds are epoch **milliseconds** (13 digits). Seconds are a 422 `invalid_time_range`.

## Responses

Success: `{status: "ok", server_time, data_type, data, …}` plus the effective `symbol`,
`timeframe`, `market`… you asked for. `data` is an **object** (or `null`) on a latest-value route,
a **list** on every `/history` route and event series, **newest first** unless `order=asc`.
`server_time` is when the server answered; every row carries its own `time`.

When `data` is `null` or a field is empty, `unavailable` says why: `not_applicable` (e.g. futures
data of a stablecoin), `no_api_key` (BytNode does not collect it — not a market fact), `no_data`.
"No measure" is never "nothing happened": say which one it is.

## Units — read the suffix, every time

| Suffix / field | Meaning | Example |
|---|---|---|
| `_pct` | percent | `rate_pct: 0.0084` = 0.0084 % (not 0.84 %) |
| `_ratio` | a quotient; a share of a whole is a fraction | `buy_ratio: 0.519` = 51.9 % |
| `_bps`, `_pp` | basis points, percentage points | |
| `_usd` | US dollars | |
| `_s`, `_at`, `_count` | seconds, an instant, a count | |
| `volume`, `buy_volume`, `oi`, `quantity`, `net_volume` | **base asset units** (BTC for BTCUSDT), never USD | `oi: 370534` = 370,534 BTC |
| prices (`close`, `basis_value`…) | quote currency (USDT for BTCUSDT) | |

- USD value of a base quantity: multiply by a price of the same time (`volume × close` of the
  same candle; `oi × close`). Say it is an estimate.
- Funding (`rate_pct`, `estimated_rate_pct`) is **per 8 hours**; `apr_pct` is its annualised form.
- A name without a market suffix covers spot + perpetual futures; `_spot` / `_futures` one market.
  Candle prices come from one reference spot market; candle volume is spot + futures.
- Every field's unit is in the route's schema (`x-unit`) and in `references/routes.generated.md`.

## Time — when a value is dated and when it is final

- A **bucket** (candles, CVD, order book, buy/sell ratio, every `/history` row) is dated at its
  **start** and carries `is_closed`. The 14:00 1h candle covers 14:00–14:59:59 and is only known
  after 15:00. Latest-value routes return the last **closed** bucket; a bucket closes a few
  seconds after its end (up to ~20 s if a venue is late). `?live=1` adds the open bucket
  (`is_closed: false`) only on `/v1/klines`, `/v1/cvd`, `/v1/trades-kline` (+ `/spot`, `/futures`),
  `/v1/funding/rate` and `/v1/spread/interexchange`; elsewhere it is a 422.
- A **rolling window** value is dated at the window's END and says its length in `window_s`:
  `/v1/liquidations/cumulative` is the **last 5 minutes** (`window_s: 300`), `/v1/oi/change` the
  last 60 s, `/v1/funding/cumulative` 24 h. For "liquidations over 24 h", sum the 1h rows of
  `/v1/liquidations/cumulative/history?timeframe=1h&limit=24`.
- Point-in-time values (options, on-chain, tokenomics) are dated when the source was read; a daily
  value at midnight UTC. Macro and on-chain series can legitimately be days old.

## History and pagination

**The plan window is a sliding window from now**: rows older than `now − window` cannot be read,
however you page. Depth reached = `limit × timeframe` (or the oldest `since_ms`). If it exceeds the
window → 403 `history_depth` with `details.window_s`, `earliest_ms`, `max_limit`. Without `limit`
and `since_ms`, a page simply stops at the window. `limit × timeframe` equal to the window fits
(24 × 1h on a 1-day window is fine).

Which window applies: the request's `timeframe` (`30m` uses the `1h` line, `1w` the `1d` line);
daily series (on-chain, sentiment, tokenomics, macro daily) the `1d` line; settled funding (8 h
periods) the `4h` line; trades the `trades_window_s`.

Paging, one dialect everywhere:

```python
url, params = "/v1/oi/history", {"symbol": "BTCUSDT", "timeframe": "1h", "limit": 1000}
while url:
    page = get(url, params)          # params only on the first call: `next` already has them
    rows.extend(page["data"])
    url, params = page.get("next"), None
```

- `next` is a ready relative URL, or `null` at the end. A short or even **empty page with a
  `next` is not the end** (a heavy read returns what it has within its time budget).
- Backwards: `before_ms` (exclusive). Forwards: `order=asc` + `since_ms` (required with asc).
  `since_ms`/`until_ms` are inclusive. Trades add `after_id` to resume inside one millisecond.
- A 504 `upstream_timeout` on one heavy page: lower `limit` and retry.

## Errors — branch on `error.code`, never on the message

`{status: "error", error: {code, message, param?, details?}}`. Plan refusals also carry the code in
the `X-Deny-Reason` header.

| Code | Do |
|---|---|
| `invalid_symbol`, `invalid_timeframe`, `unknown_parameter`, `invalid_parameter`… (422) | fix from `details.suggestion` / `details.accepted`; do not retry unchanged |
| `invalid_time_range` | milliseconds, `since ≤ until`, no `before_ms` with `until_ms` |
| `history_depth` (403) | shorten to `details.max_limit` / `earliest_ms`, or a coarser timeframe |
| `plan_family` (403) | the family is not in the plan: say which plan opens it, don't retry |
| `missing_api_key` / `invalid_api_key` (401) | key absent / wrong or revoked |
| `rate_limited` (429) | wait `Retry-After` seconds (= `details.retry_after_s`), then retry |
| `quota_exceeded` (429) | monthly quota spent: stop, do not loop (`Retry-After` = next month) |
| `edge_rate_limited` (429) | > 20 req/s from one IP: wait 1 s |
| `service_unavailable` (503), `internal_error` (500) | back off and retry; quote `X-Request-Id` if it persists |
| `upstream_timeout` (504) | smaller `limit` or range |

All codes: `references/errors.generated.md`. Responses with a metered key carry `RateLimit` and
`RateLimit-Policy` headers (policies `rate` and `quota`).

## Snapshot and indicators (two special syntaxes)

- `GET /v1/snapshot?symbol=BTCUSDT&funding_rate=1&basis=1&klines@1h=24&cvd@1h=24` — many fields
  in one request (Traders plan and up). Plain field = its latest-value object; `name@tf=N` = always
  a list of the N latest closed buckets. `?symbol=` alone lists the fields your plan includes. A
  failed field becomes an `error` object and `is_partial: true`. Fields: `references/snapshot.generated.md`.
- `POST /v1/indicators` with JSON `{symbol, timeframe, limit, indicators: [{id, type, …params flat}]}`
  — 19 indicators computed server-side (TA-Lib; RSI/ATR use Wilder smoothing) on the same
  candles, results keyed by your `id`, newest first. Only the latest values (`limit + warm-up ≤
  1000` candles; no time bounds), and the candles read count against the plan window:
  `(limit + warm-up) × timeframe` must fit it (Free's 1-hour `1m` window cannot hold an RSI 14,
  whose warm-up is 70 candles — use `5m` or `1h`). Types, warm-ups and parameters:
  `references/indicators.generated.md`.

## Common mistakes

- Reading `rate_pct: 0.0084` as 0.84 %, or `oi`/`volume` as dollars.
- Treating `/v1/liquidations/cumulative` as a daily total (it is 5 minutes).
- Requesting 30 days of 1h data on a plan with a 1-day 1h window, instead of reading `/v1/limits`.
- Stopping pagination on an empty page, or building the next URL by hand instead of following `next`.
- Using the open bucket (`is_closed: false`) as if it were final; using a candle's `time` as the
  moment its close was known (it is known at `time + timeframe`).
- Retrying a 403 or a `quota_exceeded`; sleeping on 429 without reading `Retry-After`.
- Sending epoch seconds; hard-coding the number of pairs.

## Reference files

- `references/routes.generated.md` — every route: family, parameters, `data` fields with units.
- `references/errors.generated.md` — every error code.
- `references/snapshot.generated.md`, `references/indicators.generated.md` — the two special syntaxes.
- `references/plans.md` — families and indicative limits per plan, quota budgeting.
- `scripts/bytnode_client.py` — runnable client (`python bytnode_client.py /v1/limits`).

Machine-readable sources (no key): `https://api.bytnode.com/openapi.json` (OpenAPI 3.1, the
truth), `/openapi-lite.json`, `/asyncapi.json`; docs `https://bytnode.com/docs`.
