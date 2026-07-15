# Pi — Settings & Compaction

Source: https://pi.dev/docs/latest/settings, /compaction

## Settings files

| Location | Scope |
|----------|-------|
| `~/.pi/agent/settings.json` | Global (all projects) |
| `.pi/settings.json` | Project (current directory; requires trust) |

Project overrides global; **nested objects merge** rather than replace.

### Categories & keys

**Model & thinking**: `defaultProvider`, `defaultModel`,
`defaultThinkingLevel` (`off|minimal|low|medium|high|xhigh|max`), `hideThinkingBlock`,
`showCacheMissNotices` (false — show transcript notices for significant prompt-cache misses),
`thinkingBudgets` (custom token allocations per level), `enabledModels` (patterns for the Ctrl+P
cycle set).

**Trust & analytics**: `defaultProjectTrust` (`ask` default | `always` | `never`),
`enableAnalytics` (false), `trackingId` (auto-generated), `enableInstallTelemetry`,
`warnings.anthropicExtraUsage` (true — warn when subscription auth may incur paid usage).

**UI & display**: `theme` (`dark|light|<custom>`), `quietStartup`, `collapseChangelog`,
`doubleEscapeAction` (`tree` default | `fork` | `none`), `treeFilterMode`
(`default` | `no-tools` | `user-only` | `labeled-only` | `all`), `editorPaddingX` (0–3),
`outputPad` (message padding, 0 or 1; default 1), `autocompleteMaxVisible` (3–20),
`showHardwareCursor`, `markdown.codeBlockIndent` (default `" "`).

**Message delivery**: `steeringMode` (`one-at-a-time` default | `all`),
`followUpMode` (`one-at-a-time` default | `all`).

**Editor / shell**: `externalEditor` (Ctrl+G command; default `$VISUAL`/`$EDITOR`/Notepad/nano),
`shellPath` (custom bash path — required on Windows if not auto-found), `shellCommandPrefix`
(prepended to every `bash -c`; used to enable aliases), `npmCommand` (string[], e.g.
`["mise","exec","node@20","--","npm"]`).

**Network / transport**: `httpProxy` (sets `HTTP_PROXY`/`HTTPS_PROXY`), `transport`
(`auto` default | `sse` | `websocket` | `websocket-cached`), `httpIdleTimeoutMs` (300000; 0 disables),
`websocketConnectTimeoutMs` (15000).

**Terminal & images**: `terminal.showImages` (true), `terminal.imageWidthCells` (60),
`terminal.clearOnShrink` (false); `images.autoResize` (true, max 2000×2000), `images.blockImages` (false).

**Retry** (exponential backoff): `retry.enabled` (true), `retry.maxRetries` (3),
`retry.baseDelayMs` (2000 → 2s/4s/8s); provider-level `retry.provider.timeoutMs`,
`retry.provider.maxRetries` (0), `retry.provider.maxRetryDelayMs` (60000).

**Compaction & branch summary**: `compaction` (see below), `branchSummary.reserveTokens` (16384),
`branchSummary.skipPrompt` (false — skip the summarize prompt on `/tree`).

**Resources** (arrays support globs, `!exclude`, `+force-include`, `-force-exclude`; `[]` = none):
`packages`, `extensions`, `skills`, `prompts`, `themes`, `enableSkillCommands`
(true — register skills as `/skill:name`).

### Example

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-20250514",
  "defaultThinkingLevel": "medium",
  "theme": "dark",
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "retry": { "enabled": true, "maxRetries": 3 },
  "enabledModels": ["claude-*", "gpt-4o"],
  "warnings": { "anthropicExtraUsage": true },
  "packages": ["pi-skills"]
}
```

`thinkingBudgets` example: `{ "minimal": 1024, "low": 4096, "medium": 10240, "high": 32768 }`.
`packages` object form: `[ { "source": "pi-skills", "skills": ["brave-search"], "extensions": [] } ]`.

## Compaction & branch summarization

Two summarization mechanisms, same structured format, both track file ops cumulatively:

| Mechanism | Trigger | Purpose |
|-----------|---------|---------|
| Compaction | context exceeds threshold, or `/compact` | summarize old messages to free context |
| Branch summarization | `/tree` navigation | preserve context when switching branches |

### Auto-compaction

Triggers when `contextTokens > contextWindow - reserveTokens`. Process: walk back from newest
message accumulating tokens until `keepRecentTokens` (cut point) → collect messages from previous
boundary to cut point → LLM summarization (prior summaries used iteratively) → append a
`CompactionEntry` with summary + `firstKeptEntryId` → reload using summary + messages from
`firstKeptEntryId` forward.

**Split turns**: if one turn exceeds `keepRecentTokens`, it cuts mid-turn at an assistant message,
making two summaries (history + turn prefix) and merging them.

Manual: `/compact [instructions]` (optional instructions focus the summary).

```json
{ "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 } }
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `enabled` | true | enable auto-compaction (`/compact` still works when false) |
| `reserveTokens` | 16384 | tokens reserved for the LLM response |
| `keepRecentTokens` | 20000 | recent tokens preserved (not summarized) |

`CompactionEntry` interface:
```typescript
interface CompactionEntry<T = unknown> {
  type: "compaction"; id: string; parentId: string; timestamp: number;
  summary: string; firstKeptEntryId: string; tokensBefore: number;
  fromHook?: boolean;                 // true when an extension supplied the summary
  details?: T;                        // e.g. { readFiles, modifiedFiles }
}
```

### Summary format

```
## Goal
## Constraints & Preferences
## Progress
### Done
### In Progress
### Blocked
## Key Decisions
## Next Steps
## Critical Context

<read-files> ... </read-files>
<modified-files> ... </modified-files>
```

### Branch summarization

On `/tree` navigation Pi offers to summarize abandoned work, walking from the old leaf back to the
common ancestor and injecting a `BranchSummaryEntry` into the target branch — preserving context
without replaying the whole branch. Extensions can supply a custom summary via `session_before_tree`
/ `session_before_compact`.

Source files (pi-mono): `packages/coding-agent/src/core/compaction/{compaction,branch-summarization,utils}.ts`;
entry types in `core/session-manager.ts` (`CompactionEntry`, `BranchSummaryEntry`). TS defs:
`node_modules/@earendil-works/pi-coding-agent/dist/`. Full on-disk schema: `session-format.md`.
