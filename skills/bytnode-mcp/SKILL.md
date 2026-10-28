---
name: bytnode-mcp
description: Use when answering crypto market questions through the BytNode MCP server (tools such as get_pair_brief, get_pair_data, get_options_data, get_market_overview, get_macro_data, get_onchain_data, get_market_indicators, rank_pairs, read_export, get_system_info, describe_fields), when connecting that server to Claude, ChatGPT, Cursor or another MCP client, or when a BytNode MCP call fails, is cut by its token budget, or is refused for the plan (plan_family, history_depth, wrong_tool).
---

# Using the BytNode MCP server

The MCP server (`https://api.bytnode.com/mcp`, Streamable HTTP, read-only) exposes BytNode's
market data to agents through 11 tools. Each data call becomes REST requests made with the
user's own key, so the user's plan applies. Full tool definitions, parameters and the server's own
instructions: `references/tools.generated.md`.

## Connecting

- **Connectors** (claude.ai, ChatGPT, Claude Desktop, Claude Code): add the URL
  `https://api.bytnode.com/mcp`; the client opens an OAuth sign-in on bytnode.com — no key to paste.
  Claude Code: `claude mcp add --transport http bytnode https://api.bytnode.com/mcp`, then `/mcp`
  to sign in.
- **With a key** (Cursor, VS Code, scripts): send it as `X-API-KEY` (or `Authorization: Bearer`):

  ```json
  { "mcpServers": { "bytnode": { "type": "http", "url": "https://api.bytnode.com/mcp",
                                  "headers": { "X-API-KEY": "cb_live_…" } } } }
  ```
  Claude Code: `claude mcp add --transport http bytnode https://api.bytnode.com/mcp --header "X-API-KEY: $BYTNODE_API_KEY"`.
  With the Python SDK installed: `bytnode mcp install cursor` (or `claude-desktop`, `claude-code`,
  `vscode`, `windsurf`).
- Every response carries `mcp_version`. If it differs from the version the tools were listed
  with, the client holds stale definitions: reconnect.

## First call: what may this key read?

Call `get_system_info` with no argument (free, not counted). It returns the plan, its `families`,
the history window per timeframe and the rate/quota left. Decide from it, not from memory:

- **Free plan has no `snapshot` family, so every "current value" request is refused** — a data
  tool called without a window, and `get_pair_brief`. Ask a short history instead: `last="1h"`
  (latest closed buckets), and read `summary.latest`. Fields that only have a current value
  (`funding_next`, `price_change`, `options_summary`, tagged `[now]`) cannot be read on Free
  through the data tools — say so; `rank_pairs` (below) still gives `funding_next` and
  `price_change_pct`, because it reads their own routes, not the snapshot.
- A field outside the plan → `plan_family`; a period beyond the window → `history_depth`. The
  window rule: `N buckets × timeframe ≤ window`; equal fits (24 × 1h on Free's 1-day window,
  `last="7d"` of settled funding on Free's 7-day `4h` line).
- Options and snapshot open at Traders; on-chain, sentiment, ETF and tokenomics at Financial.

## Pick the tool by target

| Question about… | Tool | Notes |
|---|---|---|
| the state of 1–10 pairs, fast | `get_pair_brief` | fixed shape: price change, next funding, basis, OI (+`oi_usd`), last 1h CVD, 24 h liquidations, fear & greed. Not on Free. |
| anything else on a pair (candles, trades, order flow, funding, OI, liquidations, tokenomics) | `get_pair_data` | `symbol` + `fields`; up to 10 pairs, keys become `PAIR/field` |
| comparing all pairs on one metric | `rank_pairs` | `oi_usd`, `volume_usd_24h`, `funding_next`, `price_change_pct`, `rsi`: ONE quota request for all pairs; `limit` default 10, max 100; works on every plan (it uses the derivatives / price / indicators routes) |
| BTC or ETH options, spot ETFs | `get_options_data` | `asset` (BTC/ETH, never a pair); `expiries=true` for per-expiry detail |
| whole market: cap, dominance, fear & greed, altcoin season, CMC20/100 | `get_market_overview` | no target |
| US macro, net liquidity, risk-on/off | `get_macro_data` | series catalogue via `get_system_info(catalogs=["macro_series"])` |
| Bitcoin / Ethereum on-chain | `get_onchain_data` | no target |
| RSI, MACD, Bollinger… (19 types) | `get_market_indicators` | `indicators=[{"id","type",…}]`, up to 50 |
| the unit or meaning of a field | `describe_fields` | free, no quota |
| the rest of a cut response | `read_export` | free, same key, export lives 1 hour |

A field asked from the wrong tool is refused with `wrong_tool` and a `hint` naming the right one.

## Modes of a data tool

- **No window** → current value (latest closed bucket); `limit=N` → the N latest points.
- **History** → `last="48h"` / `"30d"` (whole closed buckets), or `since_ms` / `until_ms`
  (epoch ms, ISO date, or `"48h"` ago). Without `timeframe`, the server picks ~200 points.
- `detail="summary"` keeps one row per series plus the summary (with `sums` for flows) — use it
  for totals and extremes. `detail`, `columns`, `timeframe` and the window apply to every field
  of the call; split the call when fields need different settings.
- `columns=[…]` keeps only the columns you need; `max_tokens` (default 6,000, up to 16,000).

## Reading a response

- `data` has one key per series (`klines@1h`, `BTCUSDT/funding_next`). An empty or not-applicable
  series is `null` and `unavailable` says why (`no_api_key` = not collected — not a market fact).
- Rows are **newest first**. A regular series has no `time` column: row *i* is dated
  `first_time + i × step_s` (`step_s` is negative). Events keep a `time` column.
- For a total, an extreme or a change, read `summary` (`latest`, `oldest`, `min`/`max` with their
  time, `mean`, `sum`, `sums` for flows such as `long_usd` / `short_usd`), not the rows.
- `ranges` says what was really covered (`row_count` of `total_row_count`, `from`, `to`): never
  state a conclusion about a period without checking it. `ranges.<key>.missing` explains a cut.
- `warnings`: a late feed (do not present it as current) or an ignored parameter.
  `freshness.age_s` is the age of the source feed.
- Units are those of the REST API: `_pct` = percent (`0.0084` = 0.0084 %), `_ratio` = fraction,
  quantities in base units (BTC), `oi_usd` = oi × close. Funding is per 8 h, `apr_pct` annualised.
- `api_requests` = quota requests the call used.

## Recipes

- **Is funding crowded? (any plan)** — `get_pair_data(symbol=["BTCUSDT"], fields=["funding_rate"],
  last="7d")` for the settled trend (+ `funding_next` without window on Traders+), then
  `rank_pairs(metric="funding_next", limit=100)` to read BTC's next estimate and place it among
  all pairs (works on Free).
- **Liquidations over 24 h, longs vs shorts** — `get_pair_data(symbol=["BTCUSDT"],
  fields=["liquidations_cumulative"], timeframe="1h", last="24h", detail="summary")` → read
  `summary.sums.long_usd` / `short_usd` (long = longs liquidated) and check `ranges`.
- **State of a pair on Free** — `get_pair_data(fields=["klines","funding_rate","oi","basis"],
  timeframe="1h", last="1h")` instead of `get_pair_brief`.
- **Big response** — narrow with `columns`, `detail="summary"` or a coarser `timeframe` first;
  then `read_export(export_id, key, offset)` until `next_offset` is null.

## Errors

A failed call is `isError: true`, text `Error (HTTP NNN): …`, and `structuredContent.error` with
`code` (`invalid_symbol`, `plan_family`, `history_depth`, `rate_limited`, `quota_exceeded`,
`wrong_tool`, `unknown_parameter`…), `hint`, `retry_after_s`. Follow the hint; wait
`retry_after_s` on `rate_limited`; never retry a plan refusal or a spent quota — tell the user which
plan opens it.

## Common mistakes

- Calling `get_pair_brief` or a current value on Free (refused): ask `last="1h"`.
- Passing a pair to `get_options_data` (it takes `asset`), or `fields` to `get_pair_brief`.
- Concluding from the rows shown when the response was cut: check `ranges` and `missing`.
- Reading `0.0084` funding as 0.84 %, or `oi` as dollars (use `oi_usd`).
- One `get_pair_data` call per pair to compare 50 pairs: use `rank_pairs` (one request).
- Presenting a `warnings` late feed as live.
