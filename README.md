# BytNode skills

Agent skills that teach an AI agent (Claude, Codex, Cursor, the BytNode-AI app…) to use
[BytNode](https://bytnode.com), the crypto market-data API — correctly, the first time.

BytNode serves aggregated market data on the largest crypto pairs: candles and trades, order flow,
derivatives (funding, open interest, basis, liquidations), options, technical indicators, on-chain,
spot ETFs, macro and sentiment — over REST, a real-time WebSocket and a native MCP server. These
skills carry what an agent needs to know and would otherwise get wrong: units, bucket timing,
pagination, plan limits, error recovery, and how to read the numbers.

| Skill | Use it when the agent… |
|---|---|
| [`bytnode-api`](skills/bytnode-api/SKILL.md) | calls the REST API or writes code against it (the foundation: auth, discovery, units, time, pagination, errors) |
| [`bytnode-mcp`](skills/bytnode-mcp/SKILL.md) | answers questions through the BytNode MCP server's tools |
| [`bytnode-market-analysis`](skills/bytnode-market-analysis/SKILL.md) | interprets funding, open interest, basis, CVD, liquidations, options, sentiment or macro |
| [`bytnode-history-backtest`](skills/bytnode-history-backtest/SKILL.md) | downloads history for a backtest, a dataset or a chart |
| [`bytnode-realtime-stream`](skills/bytnode-realtime-stream/SKILL.md) | builds on the WebSocket stream (trades, liquidations, order books) |
| [`bytnode-sdk`](skills/bytnode-sdk/SKILL.md) | uses the official Python or TypeScript SDK |
| [`bytnode-market-brief`](skills/bytnode-market-brief/SKILL.md) | writes a market report or daily brief from BytNode data |

## Install

**Claude Code** (plugin marketplace):

```
/plugin marketplace add bytnode/bytnode-skills
/plugin install bytnode@bytnode
```

**Claude Code, by hand**: copy the folders of `skills/` into `~/.claude/skills/` (every project)
or `.claude/skills/` (one project).

**Claude.ai / Claude Desktop**: zip a skill folder (e.g. `skills/bytnode-api/`) and upload it under
Settings → Capabilities → Skills.

**Codex and other agents** that read the Agent Skills format: copy the folders into
`.agents/skills/` (or the folder your agent reads).

**BytNode-AI app**: copy the folders into `~/.bytnode-ai/skills/`.

Then give the agent a key: `export BYTNODE_API_KEY=cb_live_…` (free at
[bytnode.com/sign-up](https://bytnode.com/sign-up)). MCP connectors (claude.ai, ChatGPT, Claude
Code) sign in with OAuth and need no key.

## How the skills stay true

Everything that can drift — routes, parameters, units, error codes, snapshot fields, indicators,
MCP tools — lives in `references/*.generated.md`, generated from the public contract
(`https://api.bytnode.com/openapi.json`) and the MCP server card. `CONTRACT.json` records the
contract version they were generated from. The skills never hard-code a pair count or a price:
they tell the agent to ask the API (`/v1/symbols`, `/v1/limits`).

```bash
python tools/generate_references.py          # regenerate from the live contract
python tools/generate_references.py --check  # CI: fail if a generated file is stale
```

`evals/` holds the test tasks used to check each skill (run with and without the skill) and real
captured responses in `evals/fixtures/`.

## License

MIT for the skills. The data you fetch with them is governed by your BytNode subscription.
