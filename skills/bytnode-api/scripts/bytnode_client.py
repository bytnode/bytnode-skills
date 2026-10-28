#!/usr/bin/env python3
"""Minimal BytNode REST client — standard library only, Python 3.9+.

As a library:
    from bytnode_client import Client
    c = Client()                                    # key from BYTNODE_API_KEY
    limits = c.get("/v1/limits")["data"]
    for row in c.paginate("/v1/klines/history", symbol="BTCUSDT", timeframe="1h",
                          since_ms=c.ms_ago(hours=12), order="asc"):
        ...

As a command (prints JSON; --all follows `next` and prints one row per line):
    python bytnode_client.py /v1/limits
    python bytnode_client.py /v1/funding/rate symbol=BTCUSDT
    python bytnode_client.py /v1/oi/history symbol=ETHUSDT timeframe=1h limit=1000 --all
    python bytnode_client.py POST /v1/indicators '{"symbol":"BTCUSDT","timeframe":"1h","limit":3,"indicators":[{"id":"rsi","type":"rsi"}]}'

What it does for you: sends the key in X-API-KEY over HTTPS, waits `Retry-After` on 429/503
(but never sleeps through a spent monthly quota), retries 502/504 and network errors with
backoff, follows `next` until it is null (an empty page with a `next` is NOT the end), and
raises BytNodeError carrying the stable `error.code`, `param` and `details`.
The key is never printed.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator

BASE_URL = "https://api.bytnode.com"


class BytNodeError(Exception):
    """An API error: branch on `.code` (stable), show `.message`, read `.details`."""

    def __init__(self, status: int, body: dict[str, Any] | None, headers: Any = None) -> None:
        err = (body or {}).get("error") or {}
        self.status = status
        self.code: str = err.get("code") or f"http_{status}"
        self.param: str | None = err.get("param")
        self.details: dict[str, Any] = err.get("details") or {}
        self.request_id = headers.get("X-Request-Id") if headers else None
        self.deny_reason = headers.get("X-Deny-Reason") if headers else None
        super().__init__(f"{status} {self.code}: {err.get('message') or body}")


class Client:
    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL,
                 timeout: float = 30, max_retries: int = 4, max_wait_s: float = 60) -> None:
        self.api_key = api_key or os.environ.get("BYTNODE_API_KEY")
        if not self.api_key:
            raise SystemExit("Set BYTNODE_API_KEY (free key: https://bytnode.com/sign-up).")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_wait_s = max_wait_s
        self.last_rate_limit: dict[str, str] = {}

    @staticmethod
    def ms_ago(days: float = 0, hours: float = 0, minutes: float = 0) -> int:
        """Epoch MILLISECONDS for a moment in the past (the API refuses seconds)."""
        return int((time.time() - days * 86400 - hours * 3600 - minutes * 60) * 1000)

    def request(self, method: str, path: str, params: dict[str, Any] | None = None,
                body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = path if path.startswith("http") else self.base_url + path
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(clean, safe="@,")
        data = json.dumps(body).encode() if body is not None else None
        headers = {"X-API-KEY": self.api_key, "Accept": "application/json",
                   "User-Agent": "bytnode-skills-client/1.0"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        attempt = 0
        while True:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                    self.last_rate_limit = {k: v for k, v in resp.headers.items()
                                            if k.lower().startswith("ratelimit")}
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                try:
                    payload = json.loads(exc.read().decode("utf-8"))
                except ValueError:
                    payload = None
                error = BytNodeError(exc.code, payload, exc.headers)
                retry_after = exc.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else None
                retriable = exc.code in (429, 503) and error.code != "quota_exceeded"
                retriable = retriable or exc.code in (502, 504) or (exc.code == 500 and attempt == 0)
                if not retriable or attempt >= self.max_retries:
                    raise error from None
                if wait is None or wait > self.max_wait_s:
                    wait = min(self.max_wait_s, 0.5 * 2 ** attempt) * (0.5 + random.random())
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt >= self.max_retries:
                    raise BytNodeError(0, {"error": {"code": "network_error", "message": str(exc)}}) from None
                wait = min(self.max_wait_s, 0.5 * 2 ** attempt) * (0.5 + random.random())
            attempt += 1
            time.sleep(wait)

    def get(self, path: str, **params: Any) -> dict[str, Any]:
        return self.request("GET", path, params)

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", path, body=body)

    def pages(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        """Every page of a paged route: follows `next` until it is null."""
        page = self.get(path, **params)
        while True:
            yield page
            nxt = page.get("next")
            if not nxt:
                return
            page = self.request("GET", nxt)

    def paginate(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        """Every row of a paged route, in the reading order of the request."""
        for page in self.pages(path, **params):
            yield from page.get("data") or []


def _main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    method = "GET"
    if argv[0].upper() in ("GET", "POST"):
        method, argv = argv[0].upper(), argv[1:]
    path, rest = argv[0], argv[1:]
    follow = "--all" in rest
    rest = [a for a in rest if a != "--all"]
    client = Client()
    try:
        if method == "POST":
            print(json.dumps(client.post(path, json.loads(rest[0] if rest else "{}")), indent=1))
        elif follow:
            params = dict(a.split("=", 1) for a in rest)
            for row in client.paginate(path, **params):
                print(json.dumps(row))
        else:
            params = dict(a.split("=", 1) for a in rest)
            print(json.dumps(client.get(path, **params), indent=1))
    except BytNodeError as err:
        print(json.dumps({"status": err.status, "code": err.code, "param": err.param,
                          "details": err.details, "message": str(err)}, indent=1), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
