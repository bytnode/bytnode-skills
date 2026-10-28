# Plans, families and budgets

> Indicative, as published on 2026-10-28 (https://bytnode.com/pricing). **The key's own
> `GET /v1/limits` is the truth** — read it rather than this table when you have a key.

## Families

Every metered route belongs to one family (`x-family` in the contract, `Family:` in
`routes.generated.md`). `/v1/limits` → `families` lists the ones the key may read (`null` = all).

| Family id | What |
|---|---|
| `price_volume` | candles, price change, global market (`/v1/global`), `/v1/symbols`, `/v1/status`, `/v1/capabilities` |
| `derivatives` | funding, open interest, basis, liquidations (cumulative, big/small, events, heatmap) |
| `indicators` | `POST /v1/indicators` |
| `macro` | FRED series, intraday macro, net liquidity, correlations, momentum, risk |
| `microstructure` | CVD, order book, buy/sell ratio, trade candles, average trade size, inter-venue spread |
| `options` | BTC and ETH options |
| `snapshot` | `/v1/snapshot` (and, on the MCP, every "current value" request) |
| `trades` | individual spot and futures trades, large trades, per-second trade candles (raw ticks) |
| `onchain` | Bitcoin network and valuation, Ethereum |
| `sentiment` | Fear & Greed (two indices), Altcoin Season, CMC20, CMC100 |
| `etf` | US spot ETF fundamentals (SEC filings) |
| `tokenomics` | supply, market cap, FDV |

`/v1/health`, `/v1/limits` and `POST /v1/ws/token` are never counted in the quota.

## Plans (indicative)

| | Free | Traders | Financial | Startup |
|---|---|---|---|---|
| `plan` id | `free` | `traders` | `financial` | `startup` |
| Price (billed yearly) | 0 | 6.95 USD/mo | 19.95 USD/mo | 99.95 USD/mo |
| Requests / month | 10,000 | 200,000 | 2,000,000 | 20,000,000 |
| Requests / minute | 30 | 60 | 300 | 600 |
| Families | price_volume, derivatives, indicators, macro | + microstructure, options, snapshot | all | all |
| WebSocket connections | none | 3 | 10 | 20 |
| History `1m` | 1 hour | 1 day | 3 days | 7 days |
| History `5m` / `15m` | 4 hours | 3 days | 7 days | 30 days |
| History `1h` (and `30m`) | 1 day | 7 days | 30 days | 90 days |
| History `4h` | 7 days | 30 days | 72 days | unlimited |
| History `1d` (and `1w`) | 30 days | unlimited | unlimited | unlimited |
| Raw trades (ticks) | — | — | 1 hour | 1 day |
| Liquidation events | last 100 | last 500 | last 1,000 | last 10,000 |
| Commercial use | no | no | yes | yes, + redistribution in your product |

Enterprise: by contract. Monthly billing costs more than the yearly rates above.

## How the window is applied

- Sliding from now: on Free, a 1h row older than 24 h is unreadable, whatever the paging.
- Depth reached = `limit × timeframe`, or the oldest `since_ms` — compared to the window (a 2-minute
  clock tolerance applies). Over it: 403 `history_depth` with `details.window_s`,
  `details.earliest_ms`, `details.max_limit`.
- Routes without a `timeframe` are judged on the line of their cadence: daily series on `1d`,
  settled funding (one row per 8 h) on `4h`, trades on the ticks window, the rest on `1h`.
- Without `limit` and `since_ms`, a page stops at the window instead of failing.

## Budgeting the quota

- One request = one page of up to 1,000 rows (the max `limit` of most history routes). 30 days of
  1h candles = 720 rows = 1 request; 7 days of 1m candles = 10,080 rows ≈ 11 requests.
- Ask for the largest page the route allows; prefer the coarsest timeframe that answers the question.
- The snapshot reads up to 52 fields in ONE request (Traders and up): cheaper than one call per field.
- `POST /v1/indicators` computes up to 50 indicators in one request.
- Free at 30 requests/minute: a 60-request job takes at least two minutes; pace it instead of
  hammering into 429s.
