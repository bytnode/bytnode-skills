#!/usr/bin/env python3
"""Download a BytNode history route to CSV, within the key's plan — standard library only.

    python fetch_history.py --symbol BTCUSDT --timeframe 1h --days 30
    python fetch_history.py --route /v1/oi/history --symbol ETHUSDT --timeframe 5m --days 3 --out eth_oi.csv
    python fetch_history.py --route /v1/funding/rate/history --symbol SOLUSDT --days 7
    python fetch_history.py --symbol BTCUSDT --timeframe 1m --days 7 --clamp   # shrink to the plan window

What it does: reads GET /v1/limits (free) and refuses up front a range the plan cannot serve
(or, with --clamp, shrinks it and says so); reads forward (order=asc + since_ms, limit=1000)
following `next` until it is null; drops rows with is_closed=false; de-duplicates on `time`;
reports gaps against the expected step; writes one CSV (nested values as JSON), oldest first.
Key from BYTNODE_API_KEY, never printed. Exit code 2 = the plan cannot serve the request.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.bytnode.com"
STEP_S = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800}
# The plan window used by routes without a timeframe (see the bytnode-api skill).
WINDOW_LINE = {"/v1/funding/rate/history": "4h"}
ROUTE_STEP_S = {"/v1/funding/rate/history": 8 * 3600}


def call(url: str, key: str, tries: int = 5) -> dict:
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"X-API-KEY": key, "User-Agent": "bytnode-fetch-history/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8") or "{}")
            code = (body.get("error") or {}).get("code")
            if exc.code in (429, 503) and code != "quota_exceeded" and attempt < tries - 1:
                time.sleep(float(exc.headers.get("Retry-After") or 2 ** attempt))
                continue
            if exc.code in (502, 504) and attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            err = body.get("error") or {}
            raise SystemExit(f"API error {exc.code} {err.get('code')}: {err.get('message')} {err.get('details') or ''}")
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)
    raise SystemExit("unreachable")


def window_s(limits: dict, line: str) -> float | None:
    for row in limits.get("history") or []:
        if row.get("timeframe") == line:
            return row.get("window_s")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Download a BytNode history route to CSV.")
    ap.add_argument("--route", default="/v1/klines/history")
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--timeframe", help="required by bucketed routes (1m … 1w)")
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--out", help="CSV path (default: <symbol>_<route>_<tf>.csv)")
    ap.add_argument("--clamp", action="store_true", help="shrink the range to the plan window instead of failing")
    args = ap.parse_args()

    key = os.environ.get("BYTNODE_API_KEY")
    if not key:
        raise SystemExit("Set BYTNODE_API_KEY (free key: https://bytnode.com/sign-up).")

    limits = call(f"{BASE}/v1/limits", key)["data"]
    line = args.timeframe or WINDOW_LINE.get(args.route, "1h")
    line = {"30m": "1h", "1w": "1d"}.get(line, line)
    allowed = window_s(limits, line)
    wanted = args.days * 86400
    if allowed is not None and wanted > allowed:
        msg = (f"plan '{limits.get('plan')}' keeps {allowed / 86400:g} day(s) of {line} history; "
               f"{args.days:g} day(s) requested.")
        if not args.clamp:
            print(msg + " Use --clamp, a coarser --timeframe, or a larger plan.", file=sys.stderr)
            return 2
        print(msg + " Clamped to the window.", file=sys.stderr)
        wanted = allowed - 120  # stay inside the window (2-minute margin)

    since_ms = int((time.time() - wanted) * 1000)
    params = {"symbol": args.symbol, "since_ms": since_ms, "order": "asc", "limit": 1000}
    if args.timeframe:
        params["timeframe"] = args.timeframe
    url = f"{BASE}{args.route}?{urllib.parse.urlencode(params)}"

    rows: dict[str, dict] = {}
    requests = 0
    while url:
        page = call(url, key)
        requests += 1
        for row in page.get("data") or []:
            if row.get("is_closed") is False:
                continue  # provisional bucket: never train on it
            rows[row["time"]] = row
        nxt = page.get("next")
        url = f"{BASE}{nxt}" if nxt else None

    ordered = [rows[t] for t in sorted(rows)]
    step = STEP_S.get(args.timeframe or "", ROUTE_STEP_S.get(args.route))
    gaps = 0
    if step and len(ordered) > 1:
        stamps = [datetime.fromisoformat(r["time"].replace("Z", "+00:00")).timestamp() for r in ordered]
        gaps = sum(1 for a, b in zip(stamps, stamps[1:]) if b - a > step * 1.5)

    out = args.out or f"{args.symbol}_{args.route.strip('/').replace('/', '_')}_{args.timeframe or 'native'}.csv"
    columns: list[str] = []
    for row in ordered:
        columns += [c for c in row if c not in columns]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in ordered:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()})

    first = ordered[0]["time"] if ordered else "-"
    last = ordered[-1]["time"] if ordered else "-"
    print(f"{len(ordered)} closed rows, {first} -> {last}, {gaps} gap(s), {requests} request(s) -> {out}",
          file=sys.stderr)
    print(f"generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
