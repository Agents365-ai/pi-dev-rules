# Pi — Package Gallery Catalog

Source: https://pi.dev/packages · Snapshot: **2026-07-09** · **5,001 packages**

The pi.dev package gallery is backed by the **npm registry keyword `pi-package`** (pi.dev's own
`/api` routes are disabled — "reserved for future features"). The gallery shows ~5,005; the extra
handful are git-only packages not published to npm.

- **Full manifest**: [`pi-packages.csv`](./pi-packages.csv) — one row per package, all 5,001, sorted
  by monthly downloads. Columns: `name, type, downloads_monthly, version, author, description,
  install, repository, npm, updated`.
- **Refresh** (list changes daily): `bash scripts/refresh.sh` — regenerates the CSV and prompts for a
  changelog update. **Recommended cadence: weekly** (npm churn is fast but a weekly snapshot keeps
  this skill current without constant PRs). Or run just the CSV: `python3 scripts/fetch-pi-packages.py`
  (no API key needed).

> `type` is a **heuristic** derived from npm keywords/description (npm search doesn't expose the
> gallery's real category, which comes from each package's `pi` manifest). Treat `name`,
> `downloads_monthly`, `description`, `install`, and `repository` as exact; treat `type` as a hint.

## Install any package

```bash
pi install npm:<name>            # e.g. pi install npm:pi-web-access
pi install npm:<name> -l         # -l → project .pi/settings.json (team sharing)
pi install npm:<name> -e         # -e → temporary, single run
pi remove npm:<name>
```

Git/HTTPS sources also work (`pi install git:github.com/user/repo@v1`). See `extending-pi.md` §5.

## Query the manifest

For an agent (exact/greppable — don't load the whole CSV into context):

```bash
grep -i 'memory'      references/pi-packages.csv          # search name+description
awk -F, 'NR==1||$2=="skill"' references/pi-packages.csv   # filter by heuristic type
# top 20 by downloads (CSV is already sorted desc):
sed -n '1,21p'        references/pi-packages.csv
# structured queries with python:
python3 -c "import csv;[print(r['name'],r['downloads_monthly']) for r in csv.DictReader(open('references/pi-packages.csv')) if 'web' in r['description'].lower()]"
```

For a human: open `pi-packages.csv` in any spreadsheet, or filter live on https://pi.dev/packages
(search by name/description/author, filter by type, sort by downloads / recency / A–Z).

## Breakdown (heuristic types)

| type (heuristic) | count |
|------------------|-------|
| extension | 2,536 |
| package (bundle / uncategorized) | 1,882 |
| skill | 446 |
| theme | 91 |
| prompt | 46 |
| **total** | **5,001** |

## Top 30 by monthly downloads

| Package | Downloads/mo | Description |
|---------|-------------:|-------------|
| `@hypabolic/pi-hypa` | 201,821 | Keeps noisy tool output out of context; rewrites shell commands through Hypa for deterministic compression |
| `pi-web-access` | 128,018 | Web search, URL fetch, GitHub clone, PDF extraction, YouTube/video understanding (many search backends) |
| `context-mode` | 113,283 | MCP plugin that saves ~98% of context; sandboxed code exec, FTS5 knowledge base, intent search |
| `pi-mcp-adapter` | 109,130 | Model Context Protocol (MCP) adapter extension for Pi |
| `pi-subagents` | 101,841 | Delegate tasks to subagents with chains, parallel execution, TUI |
| `@tintinweb/pi-subagents` | 37,414 | Claude Code-style autonomous sub-agents for Pi |
| `@juicesharp/rpiv-ask-user-question` | 35,210 | Structured questionnaire the model can put to you |
| `@nitra/cursor` | 34,926 | CLI to download cursor rules into a local repo |
| `@ayulab/pi-rewind` | 32,349 | `/rewind` checkpoint navigation |
| `@juicesharp/rpiv-todo` | 29,231 | Todo list as a live overlay that survives `/reload` |
| `@plannotator/pi-extension` | 28,494 | Interactive plan review with annotations; code/PR review |
| `pi-lens` | 27,256 | Real-time code feedback — LSP, linters, formatters, type-checking |
| `bigpowers` | 26,963 | 73 agent skills synthesizing software-engineering discipline |
| `@quintinshaw/pi-dynamic-workflows` | 23,611 | Dynamic workflows fanning a task across many subagents |
| `@ff-labs/pi-fff` | 23,348 | FFF-powered fuzzy file + content search |
| `@gotgenes/pi-permission-system` | 21,194 | Permission enforcement for the Pi agent |
| `@mjasnikovs/pi-task` | 21,146 | Deterministic task planning with crash-safe pipelines |
| `pi-simplify` | 19,900 | Reviews changed code for clarity/maintainability |
| `@remnic/plugin-pi` | 17,405 | Remnic memory extension |
| `pi-hermes-memory` | 15,011 | Persistent memory + session search + secret scanning |
| `@ollama/pi-web-search` | 14,590 | Web search/fetch via Ollama APIs |
| `@raindrop-ai/pi-agent` | 13,757 | Raindrop observability / tracing for Pi |
| `glimpseui` | 12,630 | Native micro-UI for scripts/agents (cross-platform WebView) |
| `pi-agent-browser-native` | 12,318 | Exposes agent-browser as a native browser-automation tool |
| `@dietrichgebert/ponytail` | 12,049 | "Lazy senior dev" mode skill |
| `pi-crew` | 12,013 | Coordinated AI teams, workflows, worktrees, async orchestration |
| `gentle-pi` | 11,760 | Senior-architect harness (SDD/OpenSpec, subagents) |
| `pi-landstrip` | 11,420 | Landlock-based sandboxing with permission prompts |
| `superpowers-zh` | 11,192 | Chinese-enhanced "superpowers" skills (+4 original) |
| `pi-shazam` | 10,920 | Codebase-awareness toolkit — 7 structural analysis tools; MCP |

The remaining ~4,970 packages are in [`pi-packages.csv`](./pi-packages.csv). Downloads are npm
monthly figures at snapshot time; re-run the fetch script for current numbers.
