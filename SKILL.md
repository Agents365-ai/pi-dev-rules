---
name: pi-dev-rules
description: Authoritative reference and rules for working with Pi (the @earendil-works/pi-coding-agent terminal coding harness) — installing/running it, configuring providers/models/settings/keybindings, managing sessions and compaction, and extending it with extensions, skills, prompt templates, themes, packages, custom providers, and the SDK/RPC/JSON modes. Use whenever the user asks to install, configure, run, automate, script, or extend Pi, write a Pi extension or skill, set up a Pi provider/model, or integrate Pi programmatically.
license: MIT
metadata: {"source":"https://pi.dev/docs/latest","docVersion":"latest","fetched":"2026-07-09"}
---

# Pi Dev Rules

Pi is a **minimal terminal coding harness**: lightweight core, extended through TypeScript
customizations. Package: `@earendil-works/pi-coding-agent`. Maintained by Earendil Inc. (MIT).
This skill mirrors the official docs at https://pi.dev/docs/latest so you can answer Pi questions
and build Pi customizations without re-fetching.

## When to use this skill

- Installing, authenticating, or launching Pi; explaining CLI flags / slash commands.
- Configuring providers, API keys, custom models (`models.json`), or proxies.
- Editing `settings.json`, keybindings, themes; understanding sessions & compaction.
- Understanding the **project-trust security model** and running Pi in containers/sandboxes.
- **Extending Pi**: writing extensions, skills, prompt templates, packages, custom providers, TUI UI.
- Finding/installing a community package from the pi.dev gallery (5,000+ packages).
- Checking Pi's version history / what changed in a recent release.
- Driving Pi programmatically via the SDK, RPC mode, or JSON event-stream mode.
- Setting up Pi on Windows/Termux/tmux/specific terminals, or building it from source.

## Reference index — load the file you need

| File | Covers |
|------|--------|
| `references/cli-and-usage.md` | Install, auth, launching, CLI flags, slash commands, message queue, context files, env vars, sessions, keybindings |
| `references/providers-and-models.md` | Subscription & API-key providers (30+), `auth.json` (+ scoped `env`), cloud providers (Azure/Bedrock/Vertex/Cloudflare), custom models in `models.json`, `compat`, custom-provider extensions |
| `references/settings-and-compaction.md` | `settings.json` schema + example, trust/analytics/retry/transport keys, compaction (auto/manual) and branch summarization |
| `references/extending-pi.md` | Extension API (events, tools, commands, UI), Skills (SKILL.md), Prompt Templates, Themes, Packages |
| `references/tui-components.md` | TUI component system for custom extension/tool UIs (components, overlays, theming, custom editor) |
| `references/security-and-containerization.md` | Project-trust model (`trust.json`, `defaultProjectTrust`), no built-in sandbox, Gondolin micro-VM, Docker, OpenShell |
| `references/session-format.md` | Session JSONL schema — versions, content blocks, message/entry types, tree/context building, SessionManager API |
| `references/programmatic.md` | SDK, RPC mode, JSON event-stream mode |
| `references/platform-setup.md` | Windows, Termux, tmux, per-terminal modified-Enter setup, shell aliases, build-from-source |
| `references/packages-catalog.md` | pi.dev package gallery — how to query/refresh, category counts, top-30, + full `references/pi-packages.csv` (5,001 packages) |
| `references/changelog.md` | pi.dev/news release notes — recent versions, RSS feed, how to fetch latest |

## Cheat sheet

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent   # install (or: curl -fsSL https://pi.dev/install.sh | sh)
export ANTHROPIC_API_KEY=sk-ant-...                               # or run /login in-session
cd /path/to/project && pi                                          # start interactive (may prompt to trust the project)

pi -c                       # continue most recent session
pi -r                       # browse/resume sessions
pi --session <path|id>      # open specific session
pi --fork <path|id>         # fork a session
pi --no-session             # ephemeral (no save)
pi -a / -na                 # trust / don't trust project-local files for this run

pi -p "Summarize this codebase"                 # print mode (non-interactive)
pi @README.md "Summarize this"                  # attach files/images with @
cat file | pi -p "..."                          # pipe stdin
pi --provider openai --model gpt-4o "..."       # pick provider/model
pi --model sonnet:high "..."                    # model:thinkingLevel
pi --tools read,grep,find,ls -p "..."           # allowlist tools (-xt to exclude)
pi --mode json "..." | jq -c 'select(.type=="message_end")'   # JSON stream
pi --mode rpc                                   # JSON-RPC over stdin/stdout

# In-editor: @file (fuzzy), !cmd (run+send), !!cmd (run, hidden), /command, Ctrl+L model, Shift+Tab thinking
# While the agent runs: Enter queues a steering msg, Alt+Enter a follow-up, Esc aborts + restores
```

**Key locations** (global `~/.pi/agent/`, project `.pi/`):
`settings.json`, `auth.json`, `models.json`, `keybindings.json`, `trust.json`, `AGENTS.md`,
`SYSTEM.md`, `extensions/`, `skills/`, `prompts/`, `themes/`, `sessions/`.

## Hard rules

- **Install package name is exactly** `@earendil-works/pi-coding-agent` with `--ignore-scripts`.
- **Project context file is `AGENTS.md`** (Pi also reads `CLAUDE.md`); put it in the project root.
- **Extensions run with full system permissions** — treat them as trusted code; gate dangerous
  ops (`rm`, `sudo`, sensitive paths) with `ctx.ui.confirm` or a `tool_call` block handler.
- **Project trust is an input-loading guard, not a sandbox.** Pi ships no built-in sandbox; a project
  is "trusted" only to decide whether to load its `.pi/` resources (settings/extensions/skills/
  prompts/themes) — decisions live in `~/.pi/agent/trust.json`, governed by `defaultProjectTrust`
  (`ask`/`always`/`never`), overridable per run with `--approve`/`--no-approve`. For untrusted repos
  or unattended runs, isolate with a container/VM (Gondolin/Docker/OpenShell); don't mount host
  `~/.pi/agent` unless the sandbox should see host credentials.
- **In extension/SDK tools: throw on error, never return an error flag.** Limit tool output to
  ~50KB / 2000 lines. Use `StringEnum` (from `@earendil-works/pi-ai`) for LLM-facing enums.
- **Skill `name`**: 1–64 chars, lowercase `a-z 0-9 -`, no leading/trailing or consecutive hyphens;
  `description` ≤1024 chars and must say *when* to load it (a skill with no description won't load).
- **`auth.json` must be `0600`.** Credential priority: CLI `--api-key` → `auth.json` →
  env var → custom-provider keys in `models.json`.
- Project `.pi/settings.json` overrides global; nested objects merge (not replace). Use `pi install -l`
  to write package config to project settings for team sharing.
