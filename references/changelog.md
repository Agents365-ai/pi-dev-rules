# Pi — Changelog

Source: https://pi.dev/news · RSS: `https://pi.dev/news.xml`

A reverse-chronological release-notes feed, paginated at 20 entries per page. The live page
has a "Release notes" / "RSS Feed" toggle. For the full history, scrape all pages
(`?page=1` through `?page=13` as of 2026-07-16; oldest entry currently ~v0.75.5 from May 2026).

**Cadence**: Pi ships releases every 1–3 days. Re-fetch this page weekly to keep the digest
current. Run `bash scripts/refresh.sh` (regenerates both the package catalog and prompts for a
changelog update).

## Recent releases (since May 2026 — ~10 weeks)

| Version | Date | Highlights |
|---------|------|-----------|
| **0.80.7** | 2026-07-14 | `sessionAffinityFormat` replaces `sendSessionIdHeader`; cache-friendly dynamic tool loading for Anthropic/OpenAI Responses; `Ctrl+X` copies last assistant message; Fable 5 `xhigh`/`max` thinking across provider catalogs |
| 0.80.6 | 2026-07-09 | Opt-in `max` thinking level above `xhigh` (GPT-5.6, adaptive Claude); input-based pricing tiers for long-context cost accounting; `~` expansion for `shellPath` |
| 0.80.4 | 2026-07-09 | `showCacheMissNotices`; project-local config via `pi config -l`; extension hooks: `agent_settled`, `before_provider_headers`, `InlineExtension`; GPT-5.6 metadata, Copilot Claude Sonnet 5, zstd Codex SSE transport |
| **0.80.3** | 2026-06-30 | Claude Sonnet 5, `outputPad` setting, `externalEditor` setting, richer RPC session commands, extension session metadata, modern Azure Foundry endpoints |
| 0.80.2 | 2026-06-23 | `ApiKeyCredential` discriminator → `type: "api_key"`; `ExecutionEnvExecOptions` → `ShellExecOptions` |
| 0.80.1 | 2026-06-23 | Fixes Bedrock profile resolution; Fireworks Anthropic-compat requests; Together MiniMax M2.7 reasoning toggles |
| **0.80.0** | 2026-06-23 | Ctrl+J as default newline binding; ZAI provider label rename; old `pi-ai` global API → compat entrypoint |
| 0.79.10 | 2026-06-22 | `reason`/`willRetry` on extension compaction events; `pi update` installs exact checked versions |
| 0.79.9 | 2026-06-20 | Chat-template thinking for OpenAI-compat providers (e.g. DeepSeek via vLLM); GLM-5.2 routing/thinking |
| 0.79.8 | 2026-06-19 | Selective provider base entry points; Mistral prompt caching; post-compaction token estimates; OpenRouter Fusion alias |
| 0.79.7 | 2026-06-18 | Auto light/dark theme switching; `pi update` self-only by default (`--all` for packages); new extension exports; Warp inline images |
| 0.79.6 | 2026-06-16 | Fixes HTTP dispatcher fetch-override; OpenCode DeepSeek V4 thinking-off params |
| **0.79.5** | 2026-06-16 | Provider-scoped `env` in `auth.json`; global `httpProxy` setting; Vercel AI Gateway attribution headers |
| 0.79.4 | 2026-06-15 | Auto light/dark first-run terminal-background detection; SHA256SUMS for standalone binaries |
| 0.79.3 | 2026-06-13 | Fixes OpenAI Codex context window → 272k-token observed limit (billing hazard fix) |
| 0.79.2 | 2026-06-12 | Experimental first-run setup (`PI_EXPERIMENTAL=1`); AWS Bedrock data-retention docs |
| **0.79.1** | 2026-06-09 | Claude Fable 5; `${1:-default}` prompt-template values; configurable `defaultProjectTrust`; extension autocomplete triggers |
| **0.79.0** | 2026-06-08 | **Project trust** gating for local inputs; extension-controlled trust decisions; cache-hit footer; richer SDK/RPC exports |
| 0.78.1 | 2026-06-04 | Ant Ling + NVIDIA NIM providers; MiniMax-M3; `ctx.mode`/`ctx.getSystemPromptOptions()` for extensions |
| **0.78.0** | 2026-05-29 | `--name`/`-n` session naming; OSC 8 file hyperlinks in tool titles; new export helpers |
| **0.77.0** | 2026-05-28 | Claude Opus 4.8; `--exclude-tools`/`-xt`; Codex device-code login; streaming-aware input events |
| **0.76.0** | 2026-05-27 | `--session-id` for automation; `excludeFromContext` for RPC bash; bounded provider retries; cross-platform terminal editing |
| 0.75.5 | 2026-05-23 | Collapsed `read` tool cards; async file ops on Windows; adaptive thinking for custom Anthropic-compat providers |

## Fetch live

```bash
# Latest release notes page:
curl -s 'https://pi.dev/news' | grep -E '<h2|<time|version|release'

# RSS feed (XML, all entries):
curl -s 'https://pi.dev/news.xml'

# Paginate (20 per page, page N):
curl -s 'https://pi.dev/news?page=N'
```

Use WebFetch for agent-friendly extraction: `WebFetch("https://pi.dev/news", prompt="...")`. The RSS
feed (`/news.xml`) is the most machine-readable form.
