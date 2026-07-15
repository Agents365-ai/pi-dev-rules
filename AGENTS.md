# AGENTS.md

pi-dev-rules packages the latest [Pi](https://pi.dev) documentation
(`@earendil-works/pi-coding-agent`) as an on-demand reference for coding agents, so they can
install, configure, run, and extend Pi without re-fetching the docs.

Full usage and install instructions: see [README.md](README.md) (English) /
[README_CN.md](README_CN.md) (中文). This file orients a coding agent working in this repo.

## Using pi-dev-rules from an agent

- **Claude Code / OpenClaw / Pi / ClawHub**: the skill auto-loads from `SKILL.md`. The
  description triggers on any Pi-related question — install, configure, providers, models,
  extensions, skills, themes, packages, SDK, RPC, JSON streaming, sessions, compaction,
  security, keybindings, platform setup.
- **Codex CLI / Copilot / Cursor / Windsurf / Aider / other agents**: point your agent at
  `SKILL.md` as the entry point. It indexes 12 reference files under `references/` by topic
  — load only the file(s) you need:
  - `cli-and-usage.md` — install, auth, CLI flags, slash commands, sessions, keybindings
  - `providers-and-models.md` — 30+ providers, `auth.json`, custom `models.json`
  - `settings-and-compaction.md` — `settings.json`, auto/manual compaction
  - `extending-pi.md` — extensions API, skills, prompt templates, themes, packages
  - `tui-components.md` — TUI component system
  - `security-and-containerization.md` — project-trust model, containerization
  - `session-format.md` — JSONL session schema
  - `programmatic.md` — SDK, RPC mode, JSON event-stream mode
  - `platform-setup.md` — Windows, Termux, tmux, shell aliases
  - `development.md` — building from source, monorepo structure
  - `packages-catalog.md` — pi.dev gallery (5,500 packages); use grep on `pi-packages.csv`
  - `changelog.md` — recent pi.dev/news release notes

## Working on this repo

- Refresh scripts under `scripts/`: `refresh.sh` (full refresh), `fetch-pi-packages.py`
  (package catalog CSV). Run weekly.
- `SKILL.md` is the primary skill definition (Claude Code / OpenClaw / Pi native format).
- `AGENTS.md` (this file) is the cross-agent portability layer; keep it thin.
- License: MIT (docs content © Earendil Inc.). `version` in `SKILL.md` frontmatter is the
  source of truth for the release tag.
