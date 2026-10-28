"""Generate the reference files of the skills from BytNode's public machine-readable files.

    python tools/generate_references.py                      # fetch the live files
    python tools/generate_references.py --openapi path.json --server-card card.json
    python tools/generate_references.py --check              # fail if a generated file is stale

Nothing in `references/*.generated.md` is written by hand: routes, parameters, units, error
codes, snapshot fields, indicators and MCP tools all come from the contract
(https://api.bytnode.com/openapi.json) and the MCP server card
(https://api.bytnode.com/.well-known/mcp/server-card.json). A number copied by hand drifts at
the first release; a generated one cannot. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
OPENAPI_URL = "https://api.bytnode.com/openapi.json"
CARD_URL = "https://api.bytnode.com/.well-known/mcp/server-card.json"


def load(source: str | None, url: str) -> dict[str, Any]:
    if source:
        return json.loads(pathlib.Path(source).read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "bytnode-skills-generator/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 (fixed https URL)
        return json.loads(resp.read().decode("utf-8"))


class Spec:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.schemas: dict[str, Any] = spec["components"]["schemas"]

    def resolve(self, node: Any) -> Any:
        while isinstance(node, dict) and "$ref" in node:
            node = self.schemas[node["$ref"].split("/")[-1]]
        return node

    def unwrap(self, node: Any) -> tuple[Any, bool]:
        """(schema without its null alternative, nullable)."""
        node = self.resolve(node)
        nullable = False
        for key in ("anyOf", "oneOf"):
            if isinstance(node, dict) and key in node:
                parts = [p for p in node[key] if self.resolve(p).get("type") != "null"]
                nullable = len(parts) < len(node[key])
                if len(parts) == 1:
                    return self.resolve(parts[0]), nullable
        return node, nullable

    def enum_of(self, node: Any) -> list[str] | None:
        node = self.resolve(node)
        if not isinstance(node, dict):
            return None
        if "enum" in node:
            return [str(v) for v in node["enum"]]
        for key in ("anyOf", "oneOf"):
            for part in node.get(key, []):
                values = self.enum_of(part)
                if values:
                    return values
        return None


def first_sentence(text: str, limit: int = 220) -> str:
    text = " ".join((text or "").split())
    guarded = text.replace("e.g.", "e@@g@@").replace("i.e.", "i@@e@@")
    match = re.match(r"(.+?[.!?])(\s|$)", guarded)
    out = (match.group(1) if match else guarded).replace("@@", ".")
    return out if len(out) <= limit else out[: limit - 1].rstrip() + "…"


def header(title: str, source: str, version: str) -> str:
    return (
        f"# {title}\n\n"
        f"> Generated from {source} (contract **{version}**) by `tools/generate_references.py`. "
        "Do not edit by hand: regenerate.\n\n"
    )


# ── routes ────────────────────────────────────────────────────────────────────────────────


def describe_param(spec: Spec, p: dict[str, Any]) -> str:
    schema, _ = spec.unwrap(p.get("schema", {}))
    bits = [f"`{p['name']}`" + (" **(required)**" if p.get("required") else "")]
    enum = spec.enum_of(p.get("schema", {}))
    if enum and p["name"] != "symbol":
        shown = ", ".join(enum[:12]) + (f", … ({len(enum)} values)" if len(enum) > 12 else "")
        bits.append(f"one of {shown}")
    elif isinstance(schema, dict) and schema.get("type"):
        rng = []
        if "minimum" in schema:
            rng.append(f"min {schema['minimum']}")
        if "maximum" in schema:
            rng.append(f"max {schema['maximum']}")
        bits.append(schema["type"] + (f" ({', '.join(rng)})" if rng else ""))
    if isinstance(schema, dict) and "default" in schema:
        bits.append(f"default `{schema['default']}`")
    return " — ".join(bits) + (f". {first_sentence(p.get('description', ''), 160)}" if p.get("description") else "")


def data_fields(spec: Spec, response_schema: Any) -> tuple[str, list[str]]:
    envelope = spec.resolve(response_schema)
    data = envelope.get("properties", {}).get("data", {})
    node, nullable = spec.unwrap(data)
    shape = "object" + (" or null" if nullable else "")
    if node.get("type") == "array":
        shape = "list (newest first unless `order=asc`)"
        node, _ = spec.unwrap(node.get("items", {}))
    lines = []
    for name, prop in (node.get("properties") or {}).items():
        sub, null = spec.unwrap(prop)
        unit = prop.get("x-unit") or sub.get("x-unit") or ""
        typ = sub.get("type", "object") if isinstance(sub, dict) else "?"
        if isinstance(typ, list):
            null = null or "null" in typ
            typ = "/".join(t for t in typ if t != "null")
        desc = first_sentence(prop.get("description") or sub.get("description") or "", 140)
        lines.append(
            f"  - `{name}` ({typ}{', nullable' if null else ''}{', ' + unit if unit else ''})"
            + (f": {desc}" if desc else "")
        )
    return shape, lines


def routes_md(spec: Spec) -> str:
    version = spec.spec["info"]["version"]
    out = [header("BytNode REST routes", "https://api.bytnode.com/openapi.json", version)]
    by_tag: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}
    for path, ops in spec.spec["paths"].items():
        for method, op in ops.items():
            if method in ("get", "post"):
                by_tag.setdefault((op.get("tags") or ["Other"])[0], []).append((method.upper(), path, op))
    out.append(
        f"{sum(len(v) for v in by_tag.values())} routes. Base URL `https://api.bytnode.com`, key in "
        "`X-API-KEY`. `family` is the identifier `GET /v1/limits` lists in `families` "
        "(`null` there = every family). Search this file for a path or a field name.\n\n"
        "## Contents\n\n"
    )
    order = [t["name"] for t in spec.spec.get("tags", [])]
    by_tag = dict(sorted(by_tag.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 99))
    for tag in by_tag:
        anchor = re.sub(r"[^a-z0-9 -]", "", tag.lower()).replace(" ", "-")
        out.append(f"- [{tag}](#{anchor}) ({len(by_tag[tag])})\n")
    for tag, routes in by_tag.items():
        out.append(f"\n## {tag}\n")
        for method, path, op in sorted(routes, key=lambda r: r[1]):
            out.append(f"\n### {method} {path}\n\n{op.get('summary', '')}. ")
            fam = op.get("x-family")
            out.append(f"Family: `{fam}`." if fam else "Not counted in the quota.")
            if op.get("x-metered") is False:
                out.append(" Never counted.")
            out.append("\n\n" + first_sentence(op.get("description", ""), 400) + "\n")
            params = [spec.resolve(p) for p in op.get("parameters", [])]
            if params and path != "/v1/snapshot":
                out.append("\nParameters:\n")
                for p in params:
                    out.append(f"- {describe_param(spec, p)}\n")
            elif path == "/v1/snapshot":
                out.append("\nParameters: `symbol` plus one query key per field — see `snapshot.generated.md`.\n")
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if body:
                out.append("\nJSON body: see `indicators.generated.md`.\n" if "indicators" in path else "\nJSON body.\n")
            ok = op.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {})
            if ok.get("schema"):
                shape, fields = data_fields(spec, ok["schema"])
                out.append(f"\n`data`: {shape}.\n")
                if fields:
                    out.append("\n".join(fields) + "\n")
    return "".join(out)


# ── errors ────────────────────────────────────────────────────────────────────────────────


def errors_md(spec: Spec) -> str:
    version = spec.spec["info"]["version"]
    api_error = spec.schemas["ApiError"]["properties"]["error"]["properties"]["code"]["description"]
    out = [header("BytNode error codes", "https://api.bytnode.com/openapi.json", version)]
    out.append(
        "Every error is `{status: \"error\", server_time, error: {code, message, param?, details?}}` "
        "(the WebSocket sends the same object under `op: \"error\"`). Branch on `error.code`; show "
        "`error.message`; read `error.details` (`suggestion`, `accepted`, `retry_after_s`, "
        "`window_s`, `earliest_ms`, `max_limit`…) for what to change. A code not listed here is a "
        "newer one: treat it as a generic error.\n\n## Codes\n\n"
    )
    for line in api_error.splitlines():
        if line.startswith("- `"):
            out.append(line + "\n")
    out.append("\n## By HTTP status\n\n")
    for name, resp in spec.spec["components"]["responses"].items():
        out.append(f"- **{name}**: {resp.get('description', '')}\n")
    return "".join(out)


# ── snapshot ──────────────────────────────────────────────────────────────────────────────


def snapshot_md(spec: Spec) -> str:
    version = spec.spec["info"]["version"]
    op = spec.spec["paths"]["/v1/snapshot"]["get"]
    plain, multi = [], {}
    for p in (spec.resolve(x) for x in op["parameters"]):
        name = p["name"]
        if name in ("symbol", "fields"):
            continue
        if "@" in name:
            base, tf = name.split("@")
            multi.setdefault(base, []).append(tf)
        else:
            plain.append((name, first_sentence(p.get("description", ""), 160)))
    out = [header("Snapshot fields", "https://api.bytnode.com/openapi.json", version)]
    out.append(" ".join(op["description"].split()) + "\n\n")
    out.append(f"## Fields without a timeframe ({len(plain)})\n\nSyntax `name=1` (or `true`); an event series takes `name=N`.\n\n")
    for name, desc in plain:
        out.append(f"- `{name}`" + (f": {desc}" if desc else "") + "\n")
    out.append(f"\n## Multi-timeframe fields ({len(multi)})\n\nSyntax `name@tf=N`: always a list of the N latest closed buckets.\n\n")
    for name, tfs in multi.items():
        out.append(f"- `{name}@tf` — tf in {', '.join(tfs)}\n")
    return "".join(out)


# ── indicators ────────────────────────────────────────────────────────────────────────────

# The contract names each type only by its code; the human names never change.
INDICATOR_NAMES = {
    "ad": "Accumulation/Distribution line", "adosc": "Chaikin A/D oscillator",
    "adx": "Average Directional Index", "atr": "Average True Range", "bb": "Bollinger Bands",
    "cci": "Commodity Channel Index", "donchian": "Donchian channel",
    "ema": "Exponential moving average", "ichimoku": "Ichimoku cloud",
    "keltner": "Keltner channel", "macd": "MACD", "mfi": "Money Flow Index",
    "obv": "On-Balance Volume", "roc": "Rate of change", "rsi": "Relative Strength Index",
    "sar": "Parabolic SAR", "sma": "Simple moving average", "stoch": "Stochastic oscillator",
    "willr": "Williams %R",
}


def indicators_md(spec: Spec) -> str:
    version = spec.spec["info"]["version"]
    op = spec.spec["paths"]["/v1/indicators"]["post"]
    definition = spec.schemas["IndicatorDefinition"]
    out = [header("Technical indicators (POST /v1/indicators)", "https://api.bytnode.com/openapi.json", version)]
    out.append(" ".join(op["description"].split()) + "\n\n")
    out.append(f"## The {len(definition['oneOf'])} types\n\n")
    for ref in definition["oneOf"]:
        schema = spec.resolve(ref)
        props = schema.get("properties", {})
        typ = (props.get("type", {}).get("const") or (props.get("type", {}).get("enum") or ["?"])[0])
        params = []
        for name, prop in props.items():
            if name in ("id", "type", "parameters"):
                continue
            prop = spec.resolve(prop)
            bits = [f"`{name}`"]
            if "default" in prop:
                bits.append(f"default {prop['default']}")
            rng = [f"{k} {prop[k]}" for k in ("minimum", "maximum", "exclusiveMinimum") if k in prop]
            if rng:
                bits.append(", ".join(rng))
            params.append(" ".join(bits))
        title = INDICATOR_NAMES.get(typ, typ)
        desc = " ".join(schema.get("description", "").split()).replace(f"`{typ}` indicator. ", "")
        out.append(f"- **`{typ}`** ({title})" + (f": {desc}" if desc else "") + (f" Parameters: {'; '.join(params)}." if params else " No parameter.") + "\n")
    return "".join(out)


# ── MCP tools ─────────────────────────────────────────────────────────────────────────────


def mcp_md(card: dict[str, Any], contract: str) -> str:
    out = [
        f"# BytNode MCP tools\n\n> Generated from https://api.bytnode.com/.well-known/mcp/server-card.json "
        f"(MCP surface **{card.get('version', '?')}**, REST contract {contract}) by "
        "`tools/generate_references.py`. Do not edit by hand: regenerate.\n\n"
        f"Endpoint: `{card.get('remotes', [{}])[0].get('url', 'https://api.bytnode.com/mcp')}` "
        "(Streamable HTTP). Auth: `X-API-KEY` header or `Authorization: Bearer <key>`; "
        "connectors (claude.ai, ChatGPT, Claude Code) sign in with OAuth instead.\n\n"
        "## Server instructions (sent to the model at connection)\n\n"
    ]
    out.append(card.get("instructions", "").strip() + "\n\n## Tools\n")
    for tool in card.get("tools", []):
        out.append(f"\n### `{tool['name']}`\n\n{tool.get('description', '').strip()}\n\nParameters:\n")
        schema = tool.get("inputSchema", {})
        required = set(schema.get("required", []))
        for name, prop in schema.get("properties", {}).items():
            enum = prop.get("enum") or (prop.get("items") or {}).get("enum")
            typ = prop.get("type", "")
            line = f"- `{name}`" + (" **(required)**" if name in required else "") + (f" ({typ})" if typ else "")
            if enum:
                line += " — one of " + ", ".join(map(str, enum))
            if prop.get("description"):
                line += f": {' '.join(prop['description'].split())}"
            out.append(line + "\n")
    return "".join(out)


# ── main ──────────────────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--openapi", help="local openapi.json (default: the live contract)")
    ap.add_argument("--server-card", help="local MCP server-card.json (default: the live one)")
    ap.add_argument("--check", action="store_true", help="exit 1 if a generated file would change")
    args = ap.parse_args()

    spec = Spec(load(args.openapi, OPENAPI_URL))
    card = load(args.server_card, CARD_URL)
    version = spec.spec["info"]["version"]
    files = {
        SKILLS / "bytnode-api/references/routes.generated.md": routes_md(spec),
        SKILLS / "bytnode-api/references/errors.generated.md": errors_md(spec),
        SKILLS / "bytnode-api/references/snapshot.generated.md": snapshot_md(spec),
        SKILLS / "bytnode-api/references/indicators.generated.md": indicators_md(spec),
        SKILLS / "bytnode-mcp/references/tools.generated.md": mcp_md(card, version),
        ROOT / "CONTRACT.json": json.dumps(
            {"contract_version": version, "mcp_version": card.get("version"), "routes": len(spec.spec["paths"])},
            indent=2,
        )
        + "\n",
    }
    stale = []
    for path, text in files.items():
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != text:
            stale.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    if args.check and stale:
        print("stale generated files (run tools/generate_references.py):", *stale, sep="\n  ")
        return 1
    print(f"contract {version}, MCP {card.get('version')}: {len(stale)} file(s) {'stale' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
