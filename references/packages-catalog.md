# Pi — Package Gallery Catalog

Source: <https://pi.dev/packages> · Snapshot: **2026-07-16** · **5,250 packages**

The pi.dev package gallery is backed by the **npm registry keyword `pi-package`** (pi.dev's own
`/api` routes are disabled — "reserved for future features"). The gallery shows ~5,005; the extra
handful are git-only packages not published to npm.

- **Full manifest**: [`pi-packages.csv`](./pi-packages.csv) — one row per package, all 5,250, sorted
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

For a human: open `pi-packages.csv` in any spreadsheet, or filter live on <https://pi.dev/packages>
(search by name/description/author, filter by type, sort by downloads / recency / A–Z).

## Breakdown (heuristic types)

| type (heuristic) | count |
| ------------------ | ------- |
| extension | 2,693 |
| package (bundle / uncategorized) | 1,957 |
| skill | 459 |
| theme | 93 |
| prompt | 48 |
| **total** | **5,250** |

## Top 30 by monthly downloads

| Package | Downloads/mo | Description |
| --------- | -------------: | ------------- |
| `@vigolium/piolium` | 250,543 | Multi-phase security audits with specialist sub-agents, isolated context, capped concurrency, resumable state |
| `@hypabolic/pi-hypa` | 200,308 | Keeps noisy tool output out of context; rewrites shell commands through Hypa for deterministic compression |
| `pi-web-access` | 139,172 | Web search, URL fetch, GitHub clone, PDF/YouTube/video analysis (many search backends) |
| `pi-mcp-adapter` | 129,186 | Model Context Protocol (MCP) adapter extension for Pi |
| `context-mode` | 113,882 | MCP plugin that saves ~98% of context; sandboxed code exec, FTS5 knowledge base, intent search |
| `pi-subagents` | 112,546 | Delegate tasks to subagents with chains, parallel execution, TUI |
| `@nitra/cursor` | 40,673 | CLI to download cursor rules into a local repo |
| `@tintinweb/pi-subagents` | 39,580 | Claude Code-style autonomous sub-agents for Pi |
| `bigpowers` | 35,832 | 73 agent skills synthesizing software-engineering discipline |
| `pi-lens` | 31,637 | Real-time code feedback — LSP, linters, formatters, type-checking, structural analysis |
| `@remnic/plugin-pi` | 30,324 | Remnic memory extension for Pi Coding Agent |
| `@plannotator/pi-extension` | 29,548 | Interactive plan review with annotations; code/PR review |
| `@quintinshaw/pi-dynamic-workflows` | 25,328 | Dynamic workflows fanning a task across many subagents |
| `@gotgenes/pi-permission-system` | 24,561 | Permission enforcement for the Pi agent |
| `pi-simplify` | 23,730 | Reviews changed code for clarity/maintainability |
| `@juicesharp/rpiv-ask-user-question` | 22,940 | Structured questionnaire the model can put to you |
| `@dietrichgebert/ponytail` | 22,582 | "Lazy senior dev" mode skill — the best code is the code you never wrote |
| `@ff-labs/pi-fff` | 21,434 | FFF-powered fuzzy file + content search |
| `@mjasnikovs/pi-task` | 20,068 | Deterministic task planning with crash-safe /task pipelines |
| `@juicesharp/rpiv-todo` | 19,993 | Todo list as a live overlay that survives /reload |
| `pi-hermes-memory` | 16,575 | Persistent memory + session search + secret scanning |
| `pi-crew` | 15,802 | Coordinated AI teams, workflows, worktrees, async orchestration |
| `@ayulab/pi-rewind` | 15,556 | `/rewind` checkpoint navigation |
| `gentle-pi` | 15,419 | Senior-architect harness (SDD/OpenSpec, subagents) |
| `@raindrop-ai/pi-agent` | 15,173 | Raindrop observability / tracing for Pi |
| `@narumitw/pi-goal` | 13,593 | Autonomous /goal completion with ordered queues |
| `@ollama/pi-web-search` | 12,495 | Web search/fetch via Ollama APIs |
| `pi-readseek` | 12,177 | Hash-anchored read/edit/grep, structural code maps, structural search |
| `pi-shazam` | 11,823 | Codebase-awareness toolkit — 7 structural analysis tools; MCP |
| `pi-agent-browser-native` | 11,550 | Exposes agent-browser as a native browser-automation tool |

The remaining ~5,220 packages are in [`pi-packages.csv`](./pi-packages.csv). Downloads are npm
monthly figures at snapshot time; re-run the fetch script for current numbers.
