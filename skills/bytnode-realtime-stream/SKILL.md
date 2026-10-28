---
name: bytnode-realtime-stream
description: Use when building on BytNode's real-time WebSocket (wss://ws.bytnode.com/ws) — live trades, liquidations or consolidated order books, live candles or tickers built from trades, a browser dashboard, a trading bot feed — or when the stream refuses the handshake (401, 403 plan_websocket), closes with 4003, 4005, 4008 or 4010, goes quiet, loses messages (seq jumps) or must be resumed after a reconnection.
---

# Using the BytNode WebSocket stream

A relay: the trades, liquidations and order books of the major venues, normalised and merged,
pushed on a 100 ms tick. No metrics, no history — what happens from your connection onwards.
The past comes from REST. **REQUIRED BACKGROUND:** `bytnode-api` for keys, units and errors.
Machine description: `https://api.bytnode.com/asyncapi.json`.

## Access, by plan

| | Free | Traders | Financial / Startup |
|---|---|---|---|
| WebSocket | no (403 `plan_websocket` at the handshake) | yes | yes |
| Simultaneous connections (whole account) | — | 3 | 10 / 20 |
| `trades.*`, `orderbook.*` (family microstructure) | — | yes | yes |
| `liquidations.*` (family derivatives) | — | yes | yes |
| REST individual trades to fill a gap (family `trades`) | — | **no** | yes (1 h / 24 h window) |

On Traders the stream works, but individual trades missed during a disconnection cannot be read
back over REST. For a gap minute, `/v1/trades-kline/futures/history?timeframe=1m` (microstructure,
Traders) gives its exact futures volume, buy/sell volume and trade count — but no OHLC; the OHLC of
`/v1/klines` comes from a reference **spot** market, a different candle. Mark such minutes as
partial rather than mixing sources silently.

## Connect — never put the API key in a browser

- **Server side** (Python, Node, a bot): open `wss://ws.bytnode.com/ws` with the header
  `X-API-KEY: <key>` (or `Authorization: Bearer`). `?api_key=` works but leaks into logs.
- **Browser**: your backend calls `POST https://api.bytnode.com/v1/ws/token` with the key and
  returns only `data.token` (`wst_…`, valid **60 s, one connection**, not counted in the quota);
  the page opens `wss://ws.bytnode.com/ws?token=<token>`. Ask a new token for every connection and
  every reconnection. (`wss://api.bytnode.com/ws` is the same stream.)
- Authentication happens at the handshake, before the socket opens: missing/invalid key or used
  token → HTTP 401; plan without the stream → 403; service at capacity → 503 (retry later);
  more than 1 opening per second (burst 10) → 429.
- **A browser never sees those HTTP statuses** (a refused WebSocket is just close `1006`). Detect
  refusals on the token call instead: `POST /v1/ws/token` answers 401 for a bad key and 403
  `plan_websocket` for a plan without the stream, with the usual error body. After the socket
  fails, fetch a new token (which re-checks the key and plan) before reconnecting, and give up
  after a few consecutive failures.

Minimal backend for a browser page (Node 18+, no dependency):

```js
// POST /ws-token → {token}; the key stays in process.env. Bind to localhost or protect this
// endpoint (auth, rate limit): anyone who can call it can open connections on your account.
import http from "node:http";
http.createServer(async (req, res) => {
  if (req.method !== "POST" || req.url !== "/ws-token") { res.writeHead(404).end(); return; }
  const r = await fetch("https://api.bytnode.com/v1/ws/token", {
    method: "POST", headers: { "X-API-KEY": process.env.BYTNODE_API_KEY } });
  const body = await r.json();
  res.writeHead(r.ok ? 200 : r.status, { "Content-Type": "application/json" })
     .end(JSON.stringify(r.ok ? { token: body.data.token } : { error: body.error?.code }));
}).listen(8787, "127.0.0.1");
```

## Subscribe

```json
{"op": "subscribe", "channels": ["trades.futures.BTCUSDT", "liquidations.BTCUSDT"], "depth": 5}
```

- Channels: `trades.futures.<SYM>`, `trades.spot.<SYM>`, `liquidations.<SYM>`,
  `orderbook.futures.<SYM>`, `orderbook.spot.<SYM>`; pairs = the perpetual pairs of
  `GET /v1/symbols` (stablecoin pairs: spot channels only). Case-insensitive.
- **All or nothing**: one invalid channel (or a family outside the plan) refuses the whole
  message with `{"op": "error", "error": {code, message, param}}` — fix and resend.
- The answer `{"op": "subscribed", "channels": [...]}` lists **every** active channel of the
  connection (a state, not an acknowledgement). `unsubscribe` is symmetrical.
- `depth` (1–5 levels per side, default 5) applies to every order book of the connection; each
  `subscribe` resets it. An order book sends its current state immediately on subscription.
- `"mode": "batch"` in the subscribe groups all pending frames into one message per send: fewer
  messages, same content — use it when you follow many channels.
- `{"op": "ping"}` → `{"op": "pong"}`. The server also pings every 20 s at the protocol level;
  standard libraries answer it, a hand-written client must (else close 1011).

## Messages

Every pushed message: `{channel, server_time, seq, data}`.

- **Trades**: `data` = list of `{time, id, side, price, quantity, value_usd}`, oldest first
  within the message. `side` = the **taker** side (`buy` = a buyer lifted the offer).
  `quantity` in base units, `value_usd = price × quantity`. `id` = the same id as REST
  `/v1/trades/*`: use it to deduplicate when you merge REST backfill with the stream (the stream
  itself never repeats an `id`). Rows with the same time, price and size but different `id`s are
  distinct executions of one taker order — keep them.
- **Liquidations**: `data` = list of `{time, price, quantity, side, value_usd}`. `side` = the
  **liquidated position** (`long` = a long was liquidated). No `id`. Not every venue publishes
  liquidations: a quiet channel is not a failure, and totals are a floor.
- **Order book**: `data = {bids: [[price, quantity]…], asks: […], avg_mid_price, avg_spread_bps}`.
  A consolidated **depth** around `avg_mid_price` (venue books re-centred on the mean mid, then
  merged on a price grid) — liquidity by distance from mid, not executable prices. Use
  `avg_mid_price` as the reference price and `avg_spread_bps` as the typical venue spread. Each
  message replaces the previous one.

## Build on event time, not arrival time

- Bucket trades on `data[].time`. Order is guaranteed **within** a message only; a later message
  can carry a trade up to ~1.5 s older. **Close a live candle ~2 s after its end**, then freeze it.
- Volume = sum of `quantity` (or `value_usd`), never the row count (some venues split orders down
  to 1 satoshi).
- The 100 ms tick is a ceiling: under load messages arrive further apart; a silence of a few
  seconds is not a stall. Liquidations can arrive seconds late: window on their `time`.

## Losses, reconnection, limits

- `seq` is monotonic per channel from an arbitrary start. A jump between two consecutive messages
  = messages dropped (your client was too slow: the per-client queue holds ~512 frames). On an
  event channel the lost events are gone; on an order book the next state replaces everything.
- **Reconnect** with backoff (0.5 s doubling to 30 s, with jitter), get a new token if browser,
  and **send `subscribe` again** — subscriptions do not survive. Treat the first message after a
  reconnection as a new start for `seq`. No replay: backfill missed trades with
  `/v1/trades/futures` or `/v1/trades/spot` + `since_ms` (Financial and up), dedup on `id`.
- Close codes: **4003** connection ceiling of the plan (don't retry: close another connection);
  **4005** client too slow (10 overflows in a row: consume faster, use `batch`, fewer channels);
  **4008** more than 20 client messages per second; **4010** session expired after 6 h (reconnect —
  rights are re-checked); **1011** ping timeout. Never retry a 401/403 handshake unchanged.

The official SDKs (`bytnode-sdk` skill) do the reconnection, re-subscription, gap counting and
browser tokens for you. Runnable Python example: `scripts/stream_example.py`.

## Common mistakes

- Shipping the API key to the browser (in JS or in the WebSocket URL).
- Forgetting to re-subscribe after a reconnection; reusing a used token.
- Bucketing on arrival time or closing the candle at :00 exactly (late trades fall out).
- Reading trade `side` and liquidation `side` with the same convention (taker vs liquidated position).
- Counting trades as activity; treating the order book as executable venue prices.
- Expecting a replay, or REST trade backfill on Traders.
