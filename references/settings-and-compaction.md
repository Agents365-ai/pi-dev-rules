# Pi — Settings & Compaction

Source: https://pi.dev/docs/latest/settings, /compaction

## Settings files

| Location | Scope |
|----------|-------|
| `~/.pi/agent/settings.json` | Global (all projects) |
| `.pi/settings.json` | Project (current directory) |

Project overrides global; **nested objects merge** rather than replace.

### Categories

**Model & thinking**: `defaultProvider`, `defaultModel`,
`defaultThinkingLevel` (`off|minimal|low|medium|high|xhigh`), `hideThinkingBlock`,
`thinkingBudgets` (custom token allocations per level).

**UI & display**: `theme` (`dark|light|<custom>`), `quietStartup`, `collapseChangelog`,
`enableInstallTelemetry`, `doubleEscapeAction` (`tree|fork|none`), `treeFilterMode`,
`editorPaddingX` (0–3), `autocompleteMaxVisible` (3–20), `showHardwareCursor`.

**Advanced**: `compaction`, `retry` (exponential backoff), message delivery (steering/follow-up),
terminal & image prefs, shell (custom shell path, npm config), session dir, model cycling
(`enabledModels` patterns for Ctrl+P).

### Example

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-20250514",
  "defaultThinkingLevel": "medium",
  "theme": "dark",
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "enabledModels": ["claude-*", "gpt-4o"],
  "packages": ["pi-skills"]
}
```

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

On `/tree` navigation Pi offers to summarize abandoned work, walking from old leaf back to the
common ancestor to preserve context without replaying the whole branch.

Source files (pi-mono): `packages/coding-agent/src/core/compaction/{compaction,branch-summarization,utils}.ts`;
entry types in `core/session-manager.ts` (`CompactionEntry`, `BranchSummaryEntry`). TS defs:
`node_modules/@earendil-works/pi-coding-agent/dist/`.
