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

The seven skills follow the open [Agent Skills](https://agentskills.io) format (one folder per
skill, a `SKILL.md` inside), so the same files work in every agent below. Install all of them:
each skill is only loaded when a task needs it.

### Claude Code

Plugin marketplace (recommended — one command to update later):

```
/plugin marketplace add bytnode/bytnode-skills
/plugin install bytnode@bytnode
```

Update: `/plugin marketplace update bytnode`. Or, from a terminal, with the
[`skills` CLI](https://github.com/vercel-labs/skills) (Node.js 18+):

```bash
npx skills add bytnode/bytnode-skills -a claude-code -g    # -g: every project (~/.claude/skills)
                                                           # without -g: this project (.claude/skills)
```

### Codex (CLI, IDE extension, desktop app)

From a terminal:

```bash
npx skills add bytnode/bytnode-skills -a codex -g          # -g: ~/.agents/skills, every repo
                                                           # without -g: .agents/skills of this repo
```

Or ask Codex itself, at its prompt, with the built-in installer (it writes to `~/.codex/skills`).
Give it the path of each skill — a URL to the whole `skills/` folder is refused:

```
$skill-installer install from the repo bytnode/bytnode-skills the paths skills/bytnode-api skills/bytnode-mcp skills/bytnode-market-analysis skills/bytnode-history-backtest skills/bytnode-realtime-stream skills/bytnode-sdk skills/bytnode-market-brief
```

One skill: `$skill-installer install https://github.com/bytnode/bytnode-skills/tree/main/skills/bytnode-api`.

Codex picks up new skills automatically; type `/skills` to check, restart Codex if one is missing.

### Any other coding agent

Cursor, Gemini CLI, GitHub Copilot, OpenCode, Windsurf, Cline, Goose, Kiro, Roo Code and
[70+ others](https://github.com/vercel-labs/skills/blob/main/docs/agents.md):

```bash
npx skills add bytnode/bytnode-skills                      # detects your agents and asks where
npx skills add bytnode/bytnode-skills -a cursor -a gemini-cli -g   # or name them
npx skills add bytnode/bytnode-skills --list               # see the skills without installing
npx skills add bytnode/bytnode-skills --skill bytnode-api  # only one skill
npx skills update -g                                       # update later
```

Without Node.js, copy the folders yourself into the skills folder your agent reads
(`.agents/skills/` in a project is read by Codex, Cursor, Gemini CLI, Copilot, OpenCode and most
others; Claude Code reads `.claude/skills/`):

```bash
git clone --depth 1 https://github.com/bytnode/bytnode-skills
mkdir -p ~/.agents/skills && cp -r bytnode-skills/skills/* ~/.agents/skills/
```

```powershell
git clone --depth 1 https://github.com/bytnode/bytnode-skills
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force bytnode-skills\skills\* "$HOME\.agents\skills\"
```

**BytNode-AI app**: copy the folders into `~/.bytnode-ai/skills/` (same commands, other folder).

### Chat assistants (claude.ai, Claude Desktop, ChatGPT, Gemini, Mistral…)

**Claude (claude.ai, desktop app)**: zip one skill folder per upload, then *Settings → Capabilities
→ Skills → Upload skill* (code execution must be on; the menu can sit under *Customize* depending on
your plan). Start with `bytnode-mcp` and `bytnode-market-analysis`.

```bash
cd bytnode-skills/skills && zip -r bytnode-mcp.zip bytnode-mcp      # macOS, Linux
```

```powershell
cd bytnode-skills\skills; Compress-Archive bytnode-mcp bytnode-mcp.zip   # Windows
```

**Any other chatbot** (no skill upload): paste the content of the `SKILL.md` you need into the
custom instructions of a project or custom assistant, and attach its `references/` files as
knowledge files. For live data, also add the BytNode MCP server as a connector:
`https://api.bytnode.com/mcp` (sign-in with OAuth on bytnode.com, no key to paste).

### Then give the agent data access

- REST, SDK, WebSocket: a key in the environment, `export BYTNODE_API_KEY=cb_live_…`
  (PowerShell: `$env:BYTNODE_API_KEY="cb_live_…"`), free at
  [bytnode.com/sign-up](https://bytnode.com/sign-up).
- MCP connectors (claude.ai, ChatGPT, Claude Code): add `https://api.bytnode.com/mcp`; they sign
  in with OAuth, no key. See the [`bytnode-mcp`](skills/bytnode-mcp/SKILL.md) skill.

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
