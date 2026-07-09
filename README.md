# pi-dev-rules

A Claude Code / OpenClaw / Pi skill that packages the **latest [Pi](https://pi.dev) documentation**
(`@earendil-works/pi-coding-agent`) as an on-demand reference, so an agent can install, configure,
run, and **extend Pi** without re-fetching the docs.

Mirrors https://pi.dev/docs/latest (fetched 2026-07-09).

## What's inside

- `SKILL.md` — overview, when-to-use, cheat sheet, hard rules, reference index.
- `references/cli-and-usage.md` — install, auth, CLI flags, slash commands, message queue, context
  files, env vars, sessions, keybindings.
- `references/providers-and-models.md` — providers (30+), `auth.json` (+ scoped `env`), cloud
  providers, custom `models.json`, `compat`, custom-provider extensions.
- `references/settings-and-compaction.md` — `settings.json` (trust/analytics/retry/transport),
  auto/manual compaction, branch summaries.
- `references/extending-pi.md` — extensions API, skills (SKILL.md), prompt templates, themes, packages.
- `references/tui-components.md` — TUI component system for custom extension/tool UIs.
- `references/security-and-containerization.md` — project-trust model, no built-in sandbox, Gondolin
  micro-VM, Docker, OpenShell.
- `references/session-format.md` — session JSONL schema, message/entry types, SessionManager API.
- `references/programmatic.md` — SDK, RPC mode, JSON event-stream mode.
- `references/platform-setup.md` — Windows, Termux, tmux, per-terminal setup, shell aliases,
  build-from-source.

## Install

| Platform | Path |
|----------|------|
| Claude Code (global) | `~/.claude/skills/pi-dev-rules/` |
| Claude Code (project) | `.claude/skills/pi-dev-rules/` |
| OpenClaw (global) | `~/.openclaw/skills/pi-dev-rules/` |
| Pi (global) | `~/.pi/agent/skills/pi-dev-rules/` |
| Pi (project) | `.pi/skills/pi-dev-rules/` |

```bash
cp -r pi-dev-rules ~/.claude/skills/      # example: Claude Code, global
```

## Updating

Re-fetch the pages under https://pi.dev/docs/latest and regenerate the `references/` files; bump
`metadata.fetched` in `SKILL.md`.

## License

MIT (docs content © Earendil Inc.).
