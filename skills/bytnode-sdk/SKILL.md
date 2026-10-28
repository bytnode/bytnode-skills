---
name: bytnode-sdk
description: Use when writing Python or TypeScript/JavaScript code with the official BytNode SDK (package `bytnode`, `from bytnode import Bytnode`, `import { Bytnode } from 'bytnode'`) — installing it, calling routes, paging history with .iter(), getting pandas DataFrames, handling its errors (RateLimitError, PermissionDeniedError…), streaming the WebSocket, or installing the BytNode MCP server with its `bytnode` command.
---

# Using the official BytNode SDKs (Python, TypeScript)

The SDKs are generated from the API contract: every route is a method, every row a typed model,
and they handle pagination, retries, rate limits and the WebSocket. **REQUIRED BACKGROUND:**
`bytnode-api` for what the data means (units, buckets, plan windows) — the SDK does not change it.

## Install — from GitHub releases, not PyPI or npm

The packages are attached to each release of https://github.com/bytnode/bytnode-SDK/releases
(not published on PyPI/npm: `pip install bytnode` installs something else or fails). Take the
latest version `X.Y.Z` from https://github.com/bytnode/bytnode-SDK/releases/latest (or
`gh release view -R bytnode/bytnode-SDK`). Each release carries the Python wheel
(`bytnode-X.Y.Z-py3-none-any.whl`), the Python sdist (`.tar.gz`) and the npm tarball (`.tgz`):

```bash
pip install "bytnode[pandas] @ https://github.com/bytnode/bytnode-SDK/releases/download/vX.Y.Z/bytnode-X.Y.Z-py3-none-any.whl"
npm install https://github.com/bytnode/bytnode-SDK/releases/download/vX.Y.Z/bytnode-X.Y.Z.tgz
export BYTNODE_API_KEY=cb_live_...        # the clients read it
```

Python 3.10+ (sync `Bytnode` and async `AsyncBytnode`); Node 18+, Deno, Bun. If the API serves a
newer contract than the SDK, the SDK warns once; unknown new fields are kept, never break.

## The rule: the URL is the method

| Route | Python | TypeScript |
|---|---|---|
| `GET /v1/klines` | `client.klines("BTCUSDT", "1h")` | `client.klines({ symbol: 'BTCUSDT', timeframe: '1h' })` |
| `GET /v1/klines/history` | `client.klines.history("BTCUSDT", "1h", limit=24)` | `client.klines.history({ symbol, timeframe, limit })` |
| `GET /v1/funding/rate/history` | `client.funding.rate.history("BTCUSDT", since=…)` | `client.funding.rate.history({ symbol, since })` |
| `GET /v1/buy-sell-ratio/spot` | `client.buy_sell_ratio.spot(…)` | `client.buySellRatio.spot({…})` |
| `GET /v1/global` | `client.global_()` | `client.global()` |

Dashes become `_` (Python) or camelCase (TS); a Python keyword gets a trailing `_`. Required
parameters come first (positional in Python); closed values (`timeframe`, `asset`…) are typed.

A response: `.data` (model, list of models, or `None`/`null`), `.unavailable` (why `data` is empty),
`.server_time`, `.rate_limit` / `lastRateLimit`, `.raw`. Dates are `datetime`/`Date` in UTC.
Field names are the API's (`rate_pct`, `oi`, `volume` in base units…).

## History, pagination, pandas

```python
from datetime import datetime, timedelta, timezone
from bytnode import Bytnode

with Bytnode() as client:                                   # closes its connections on exit
    since = datetime.now(timezone.utc) - timedelta(days=5)
    df = client.funding.rate.history.iter("BTCUSDT", since=since).to_pandas()   # every page
```

- `.iter()` follows `next` for you. With `since`, pages are the largest allowed and rows come
  **oldest first**; without, newest first and it stops at the plan window. `.pages()` yields each
  page; `.to_list()` / `toArray()`; `max_items=` caps the rows.
- Time bounds: `datetime`, `date`, ISO string or epoch **milliseconds** (a seconds-looking int is
  refused locally with the millisecond value to use).
- `.to_pandas()` (Python, `bytnode[pandas]`): indexed by `time` (UTC, the bucket/period START),
  ascending; `flatten=True` spreads nested objects.
- The plan window still applies: a range beyond it raises `PermissionDeniedError` with code
  `history_depth` (check `client.limits()` first — free, not counted).

Several pairs into one frame (settled funding is per 8-hour period; `time` = period start —
reindex on `period_end_at` if you want the settlement instant):

```python
frames = {s: client.funding.rate.history.iter(s, since=since).to_pandas()["rate_pct"]
          for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")}
funding = pd.DataFrame(frames)          # one column per pair, % per 8 h
```

## Errors and retries

| Exception (Python / TS) | When | Do |
|---|---|---|
| `InvalidRequestError` | 400/422 | fix from `e.code`, `e.param`, message (lists accepted values) |
| `AuthenticationError`, `MissingAPIKeyError` | 401 / no key | fix the key |
| `PermissionDeniedError` | 403: `plan_family`, `history_depth`, `plan_websocket` | change the request or the plan; `e.details` has the window |
| `RateLimitError` | 429 after the SDK's own waits | `e.is_quota` / `isQuota` true = monthly quota spent: stop |
| `ServerError`, `APIConnectionError`, `APITimeoutError` | 5xx / network, after retries | report with `e.request_id` |
| `StreamError`, `ConnectionLimitError` | WebSocket | see `bytnode-realtime-stream` |

Import them from the package root: `from bytnode import RateLimitError, PermissionDeniedError,
InvalidRequestError, BytnodeError` (TS: `import { RateLimitError, … } from 'bytnode'`). All
inherit from `BytnodeError`; API errors carry `code`, `param`, `details`, `request_id`.
`RateLimitError` adds `retry_after` (seconds) and `is_quota`.

Branch on `e.code`, never on the message. **Built-in retries — do not wrap them in your own retry
loop**: 429 waits `Retry-After` (up to 60 s) then retries; 502/503/504 and network errors back off
with jitter (`max_retries`, default 3); a spent monthly quota fails at once (`is_quota`). Tune with
`Bytnode(timeout=10, max_retries=5)` or per call `request_options={"timeout": 60}` (TS: second
argument `{ timeout, maxRetries, signal }`). A `RateLimitError` that still reaches you with
`is_quota` false means sustained over-rate: slow the job down (fewer parallel calls, pause
`retry_after`) rather than looping. `client.limits().data` gives `plan`, `families`, `rate`
and `quota` (`remaining_count`) before you start.

## Snapshot and indicators

```python
snap = client.snapshot("BTCUSDT", funding_rate=True, basis=True, klines={"1h": 24})   # Traders+
snap.data.klines_1h            # list, newest first

from bytnode import indicators as ind
res = client.indicators("BTCUSDT", "1h", [ind.rsi(14), ind.macd()], limit=200)
res.data.indicators["rsi_14"].values[0]
```

TS: `client.snapshot({ symbol, funding_rate: true, klines: { '1h': 24 } })`, `snap.data?.['klines@1h']`;
`import { ind } from 'bytnode'`.

## Stream

```python
from bytnode import channels as ch
with client.stream(ch.trades("BTCUSDT"), ch.liquidations("BTCUSDT")) as stream:
    for msg in stream:              # reconnects and re-subscribes by itself
        if msg.gap: print(msg.gap, "lost on", msg.channel)
```

TS in a **browser**: never give the client the key — pass `token: async () => (await (await
fetch('/my-backend/ws-token', { method: 'POST' })).json().token)`; your backend calls
`POST /v1/ws/token`. Under Node the key goes in a header automatically.

## Command line

`bytnode check` (key valid? quota left?), `bytnode mcp install cursor|claude-desktop|claude-code|vscode|windsurf`
(adds the MCP server to that client, with a backup), `bytnode mcp config vscode` (prints the snippet).
TS: `npx bytnode …`.

## Common mistakes

- `pip install bytnode` / `npm install bytnode` from the public registries.
- Re-implementing pagination or retries around SDK calls; retrying `RateLimitError` with `is_quota`.
- Reading `rate_pct` as a fraction, or `volume`/`oi` as USD (the SDK keeps the API's units).
- Calling the stream from a browser with the API key.
- Forgetting `with Bytnode() as client` / `client.close()` in long-running scripts.
