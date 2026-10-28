#!/usr/bin/env python3
"""BytNode WebSocket: live 1-minute candles from trades + liquidations, with reconnection.

    pip install websockets
    BYTNODE_API_KEY=cb_live_... python stream_example.py BTCUSDT [--seconds 120]

Server-side client (the key goes in a header). Shows the four rules that matter: bucket on the
trade's own `time` and close a minute ~2 s late; resubscribe after every reconnection; detect
lost messages from `seq`; never retry a refused handshake.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import time
from datetime import datetime, timezone

import websockets  # pip install websockets (>= 12)

URL = "wss://ws.bytnode.com/ws"
CLOSE_DELAY_S = 2.0  # late trades: up to ~1.5 s


def minute_of(iso: str) -> int:
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()) // 60 * 60


class Candles:
    def __init__(self) -> None:
        self.open: dict[int, dict] = {}
        self.complete_from = 0  # first minute fully observed since the last (re)connection

    def connected(self, now: float) -> None:
        self.complete_from = int(now) // 60 * 60 + 60

    def add(self, trade: dict) -> None:
        m = minute_of(trade["time"])
        c = self.open.get(m)
        p, q = trade["price"], trade["quantity"]
        if c is None:
            self.open[m] = {"open": p, "high": p, "low": p, "close": p, "volume": q,
                            "buy": q if trade["side"] == "buy" else 0.0, "first": trade["time"], "last": trade["time"]}
            return
        c["high"], c["low"], c["volume"] = max(c["high"], p), min(c["low"], p), c["volume"] + q
        if trade["side"] == "buy":
            c["buy"] += q
        if trade["time"] < c["first"]:
            c["open"], c["first"] = p, trade["time"]
        if trade["time"] >= c["last"]:
            c["close"], c["last"] = p, trade["time"]

    def close_due(self, now: float) -> None:
        for m in sorted(self.open):
            if now >= m + 60 + CLOSE_DELAY_S:
                c = self.open.pop(m)
                stamp = datetime.fromtimestamp(m, timezone.utc).strftime("%H:%M")
                flag = "" if m >= self.complete_from else " (partial: connected mid-minute)"
                print(f"candle {stamp}{flag} O {c['open']} H {c['high']} L {c['low']} C {c['close']} "
                      f"V {c['volume']:.4f} (buy {c['buy'] / c['volume']:.1%})")


async def run(symbol: str, seconds: float) -> None:
    key = os.environ["BYTNODE_API_KEY"]
    channels = [f"trades.futures.{symbol}", f"liquidations.{symbol}"]
    candles, last_seq, backoff = Candles(), {}, 0.5
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            async with websockets.connect(URL, additional_headers={"X-API-KEY": key}) as ws:
                await ws.send(json.dumps({"op": "subscribe", "channels": channels}))
                backoff, last_seq = 0.5, {}  # new connection: new seq start, fresh subscription
                candles.connected(time.time())  # minutes before the next full one are incomplete
                while time.time() < deadline:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    except asyncio.TimeoutError:
                        candles.close_due(time.time())
                        continue
                    msg = json.loads(raw)
                    if msg.get("op") == "error":
                        raise SystemExit(f"refused: {msg['error']}")  # fix the request, don't loop
                    if "channel" not in msg:
                        continue  # subscribed / pong
                    ch, seq = msg["channel"], msg["seq"]
                    if ch in last_seq and seq != last_seq[ch] + 1:
                        print(f"! {seq - last_seq[ch] - 1} message(s) lost on {ch}")
                    last_seq[ch] = seq
                    if ch.startswith("trades."):
                        for t in msg["data"]:
                            candles.add(t)
                    else:
                        for liq in msg["data"]:  # side = the liquidated position
                            print(f"liquidation {liq['side']:5} {liq['value_usd']:>12,.0f} USD at {liq['price']}")
                    candles.close_due(time.time())
        except websockets.InvalidStatus as exc:  # 401 / 403 at the handshake: retrying won't help
            raise SystemExit(f"handshake refused: HTTP {exc.response.status_code}") from None
        except websockets.ConnectionClosed as exc:
            if exc.rcvd and exc.rcvd.code == 4003:
                raise SystemExit("4003: connection ceiling of the plan reached") from None
            print(f"disconnected ({exc.rcvd.code if exc.rcvd else '?'}), reconnecting in {backoff:.1f}s")
        await asyncio.sleep(backoff * (0.5 + random.random()))
        backoff = min(backoff * 2, 30)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol", nargs="?", default="BTCUSDT")
    ap.add_argument("--seconds", type=float, default=120)
    a = ap.parse_args()
    asyncio.run(run(a.symbol.upper(), a.seconds))
