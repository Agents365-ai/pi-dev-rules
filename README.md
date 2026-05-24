# pi-dev-rules

A Claude Code / OpenClaw / Pi skill that packages the **latest [Pi](https://pi.dev) documentation**
(`@earendil-works/pi-coding-agent`) as an on-demand reference, so an agent can install, configure,
run, and **extend Pi** without re-fetching the docs.

Mirrors https://pi.dev/docs/latest (fetched 2026-05-24).

## What's inside

- `SKILL.md` — overview, when-to-use, cheat sheet, hard rules, reference index.
- `references/cli-and-usage.md` — install, auth, CLI flags, slash commands, context files, env
  vars, sessions, keybindings.
- `references/providers-and-models.md` — providers, `auth.json`, cloud providers, custom
  `models.json`, custom-provider extensions.
- `references/settings-and-compaction.md` — `settings.json`, auto/manual compaction, branch summaries.
- `references/extending-pi.md` — extensions API, skills (SKILL.md), prompt templates, themes, packages.
- `references/programmatic.md` — SDK, RPC mode, JSON event-stream mode.

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
