---
name: bytnode-history-backtest
description: Use when downloading BytNode history for a backtest, a research dataset, a chart or a model — candles, open interest, funding, basis, CVD, liquidations or order book over days or weeks — or when a history request hits 403 history_depth, returns fewer rows than expected, has gaps, or must be aligned across series without lookahead bias.
---

# Pulling BytNode history for backtests and datasets

A correct dataset depends on three things: what the plan lets you read, reading every page, and
dating each value at the moment it was actually known. **REQUIRED BACKGROUND:** `bytnode-api`
(units, pagination, errors).

## 1. Size the request against the plan — before writing the loader

`GET /v1/limits` (free) gives `history[].window_s` per timeframe. The window slides from now;
paging cannot get past it.

| Need | Rows | Check |
|---|---|---|
| N days of `tf` candles | N × 86400 / step(tf) | N days ≤ window of `tf` |
| settled funding | 3 per day | window of the `4h` line |
| daily series (on-chain, sentiment, macro) | 1 per day | window of `1d` |

If the plan cannot cover the range, **say so before coding** and offer the choices: the range
the plan allows (state its length), a coarser timeframe whose window covers it (e.g. 5m instead of
1m), **accumulating** (a scheduled job that re-reads the window every run and appends to a local
store — after N days you own N days of history; overlap the reads and de-duplicate on `time`), or a
larger plan. Never let a loader silently return a shorter history than asked: a backtest on 3 days
presented as 7 is wrong. Indicative windows: the `bytnode-api` skill's `references/plans.md`.

When the range equals the window exactly (3 days of 1m on a 3-day window), start a couple of
minutes inside it (`since_ms = now − window + 2 min`): by the time the request lands, "now" has
moved. Quota: one request = up to 1,000 rows (`limit=1000`). 7 days of 1m = 10,080 rows ≈ 11 requests;
plan the job against the per-minute rate (Free: 30/min).

## 2. Read every page, forward

```text
GET /v1/klines/history?symbol=ETHUSDT&timeframe=1m&since_ms=<start>&order=asc&limit=1000
→ follow `next` (a ready relative URL) until it is null
```

- `order=asc` requires `since_ms`; bounds are epoch **milliseconds**, `since_ms` inclusive.
- A short or empty page with a `next` is not the end. Stop only on `next: null`.
- De-duplicate on `time` (and on `id` for trades) if you restart a job.
- `scripts/fetch_history.py` does all of this to CSV, checks the plan window first (`--clamp` to
  shrink with a message), drops provisional rows and counts gaps:
  `python scripts/fetch_history.py --route /v1/oi/history --symbol BTCUSDT --timeframe 5m --days 7`.

In pandas (requests):

```python
import os, time, requests, pandas as pd

def history(path, **params):
    """All closed rows of a BytNode /history route, oldest first, indexed by bucket start."""
    s = requests.Session(); s.headers["X-API-KEY"] = os.environ["BYTNODE_API_KEY"]
    url, rows = "https://api.bytnode.com" + path, []
    params = {**params, "order": "asc", "limit": 1000}          # since_ms required with asc
    while url:
        r = s.get(url, params=params, timeout=60)
        if r.status_code in (429, 503) and "quota_exceeded" not in r.text:
            time.sleep(float(r.headers.get("Retry-After", 1))); continue
        r.raise_for_status()                                     # 403 history_depth etc.: fix the request
        page = r.json(); rows += page["data"]
        url, params = (("https://api.bytnode.com" + page["next"]) if page.get("next") else None), None
    df = pd.DataFrame(rows)
    if df.empty: return df
    if "is_closed" in df: df = df[df["is_closed"]]               # keep final rows only
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.drop_duplicates("time").set_index("time").sort_index()
```

## 3. Keep only final rows, detect gaps

- Drop `is_closed: false` (the bucket still settling). Rows can be completed by late trades within
  the hour after they close; for the most recent hour, re-read before training.
- Expected step = the envelope's `step` (`1h`, `8h` for funding…). A jump larger than the step is a
  gap (collection outage, a pair listed later, a few minutes around maintenance): keep it as a gap
  — do not forward-fill prices or volumes silently; mark it. Read `step` on each page rather than
  assuming it equals your `timeframe`.
- Older history can be coarser: a `timeframe` only serves the period where readings are at least
  that fine (e.g. 1m market data starts in mid-2026, daily candles go back to 2017). `step` always
  tells the truth; history depth per family: https://bytnode.com/docs/history.

## 4. Date values when they were known — no lookahead

| Series | `time` means | Known at |
|---|---|---|
| candles, CVD, buy/sell ratio, OI, basis, order book (buckets) | bucket **start** | `time + timeframe` (+ a few seconds) |
| OI per bucket | value at the bucket END | `time + timeframe` |
| settled funding | start of the 8 h period | `period_end_at` / `settled_at` |
| `/v1/funding/next` | the settlement it forecasts | when read (`server_time`) |
| trades, liquidation events | the event | `time` |
| daily on-chain / macro | the day | later — macro inputs lag (`oldest_input_date`), MVRV ~7 days |

So a signal computed from the 14:00 1h candle can only trade at 15:00 or later. When merging
series, index each on its *known-at* time and use a backward as-of join
(`pandas.merge_asof(..., direction="backward")`), never a plain join on `time`.

## 5. Indicators

`POST /v1/indicators` returns only the **latest** values (`limit + warm-up ≤ 1000` candles, no
time bounds, and those candles must fit the plan window): fine to cross-check, not to build a long
backtest series. Compute indicators locally on the downloaded candles, and discard the warm-up
(5 × period for RSI/ATR, 3 × slow for MACD, 14 × period for ADX; all warm-ups are in the
`bytnode-api` skill's `references/indicators.generated.md`). The server uses TA-Lib (RSI = Wilder
smoothing): `talib.RSI(close, 14)` and a pandas Wilder RSI (`ewm(alpha=1/14, adjust=False)` on
gains and losses) agree exactly on a long series. The server's values differ from them by about
0.01–0.02 RSI points (measured on BTCUSDT 1h), because it starts from only `limit + 5 × period`
candles: your longer series is the more converged one. Compare with that tolerance.

## 6. Data notes worth carrying into the dataset

- Candle OHLC comes from one reference spot market; `volume` is spot + perpetual futures, in base
  units (`volume_spot`, `volume_futures` split it). USD volume = volume × close (an estimate).
- `is_volume_estimated: true` flags quantities estimated from USD amounts in older history.
- Values are aggregated across venues: there is no per-exchange series to reproduce one venue.

## Common mistakes

- Writing the loader first and discovering the plan window from a 403 at run time.
- Stopping on an empty page; looping on `before_ms` built by hand instead of following `next`.
- Training on `is_closed: false` rows; joining series on bucket start (lookahead of one bucket).
- Using `POST /v1/indicators` as a historical indicator source.
- Treating base-unit volume or OI as USD.
