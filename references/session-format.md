# Pi — Session Format

Source: https://pi.dev/docs/latest/session-format

Sessions are **JSONL** — one JSON object per line, each with a `type` field. Entries form a **tree**
via `id` / `parentId` (in-place branching; no new file per branch).

## On-disk location

```
~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl
```

`<path>` is the working directory with `/` replaced by `-`. Delete by removing `.jsonl` files, or
interactively via `/resume` → select → `Ctrl+D` → confirm (uses `trash` CLI when available).

## Version history (header `version`)

- **v1** — linear entry sequence (legacy; auto-migrated on load).
- **v2** — tree structure with `id`/`parentId` linking.
- **v3** (current) — renamed the `hookMessage` role → `custom` (extension unification).

Existing sessions auto-migrate to v3 on load. Source: `packages/coding-agent/src/core/session-manager.ts`,
`.../messages.ts`, `packages/ai/src/types.ts`, `packages/agent/src/types.ts` (repo
`earendil-works/pi-mono`).

## Content blocks

```typescript
interface TextContent     { type: "text"; text: string; }
interface ImageContent    { type: "image"; data: string; mimeType: string; }  // data = base64
interface ThinkingContent { type: "thinking"; thinking: string; }
interface ToolCall        { type: "toolCall"; id: string; name: string; arguments: Record<string, unknown>; }
```

## Message types

Base (pi-ai):

```typescript
interface UserMessage {
  role: "user"; content: string | (TextContent | ImageContent)[]; timestamp: number;
}
interface AssistantMessage {
  role: "assistant"; content: (TextContent | ThinkingContent | ToolCall)[];
  api: string; provider: string; model: string; usage: Usage;
  stopReason: "stop" | "length" | "toolUse" | "error" | "aborted";
  errorMessage?: string; timestamp: number;
}
interface ToolResultMessage {
  role: "toolResult"; toolCallId: string; toolName: string;
  content: (TextContent | ImageContent)[]; details?: any; isError: boolean; timestamp: number;
}
interface Usage {
  input; output; cacheRead; cacheWrite; totalTokens;
  cost: { input; output; cacheRead; cacheWrite; total };
}
```

Extended (pi-coding-agent):

```typescript
interface BashExecutionMessage {
  role: "bashExecution"; command; output; exitCode: number | undefined;
  cancelled; truncated; fullOutputPath?; excludeFromContext?; timestamp;  // excludeFromContext=true for "!!"
}
interface CustomMessage {
  role: "custom"; customType: string; content: string | (TextContent | ImageContent)[];
  display: boolean; details?: any; timestamp;
}
interface BranchSummaryMessage    { role: "branchSummary"; summary; fromId; timestamp; }
interface CompactionSummaryMessage{ role: "compactionSummary"; summary; tokensBefore; timestamp; }

type AgentMessage = UserMessage | AssistantMessage | ToolResultMessage | BashExecutionMessage
  | CustomMessage | BranchSummaryMessage | CompactionSummaryMessage;
```

## Entry types (distinct from message roles)

```typescript
interface SessionEntryBase {
  type: string; id: string;         // 8-char hex
  parentId: string | null; timestamp: string;   // ISO
}
```

- **SessionHeader** `{"type":"session","version":3,"id":"uuid","timestamp":"…","cwd":"…"}` — no
  id/parentId; optional `"parentSession":"/path/…jsonl"` when created via `/fork`, `/clone`, or
  `newSession({ parentSession })`.
- **SessionMessageEntry** `type:"message"`, field `message: AgentMessage`.
- **ModelChangeEntry** `type:"model_change"`, `provider`, `modelId`.
- **ThinkingLevelChangeEntry** `type:"thinking_level_change"`, `thinkingLevel`.
- **CompactionEntry** `type:"compaction"`, `summary`, `firstKeptEntryId`, `tokensBefore`; optional
  `details` (`{ readFiles, modifiedFiles }`), `fromHook`.
- **BranchSummaryEntry** `type:"branch_summary"`, `fromId`, `summary`; optional `details`,
  `fromHook`. Created when switching branches via `/tree`.
- **CustomEntry** `type:"custom"`, `customType`, `data` — extension state, **not** in LLM context;
  render with `pi.registerEntryRenderer`.
- **CustomMessageEntry** `type:"custom_message"`, `customType`, `content`, `display`, optional
  `details` — extension message that **does** participate in LLM context.
- **LabelEntry** `type:"label"`, `targetId`, `label` (set `label` undefined to clear).
- **SessionInfoEntry** `type:"session_info"`, `name` — set via `/name`, `--name`/`-n`, or
  `pi.setSessionName()`.

## Tree & context building

- First entry has `parentId: null`; the leaf is the current position; branching adds children off an
  earlier entry.
- `buildContextEntries()` walks leaf→root honoring compaction (includes the compaction entry, then
  `firstKeptEntryId`→compaction, then post-compaction; keeps non-message entries for rendering).
- `buildSessionContext()` converts entries → LLM messages: `message`→stored `AgentMessage`,
  `compaction`→`compactionSummary`, `branch_summary`→`branchSummary`, `custom_message`→`CustomMessage`,
  `custom`→(no context message); extracts current model + thinking level from the full path.

## SessionManager API

- **Static**: `create(cwd, sessionDir?)`, `open(path, sessionDir?)`, `continueRecent(cwd, sessionDir?)`,
  `inMemory(cwd?)`, `forkFrom(sourcePath, targetCwd, sessionDir?)`, `list(cwd, sessionDir?, onProgress?)`,
  `listAll(onProgress?)`.
- **Session mgmt**: `newSession({ parentSession? })`, `setSessionFile(path)`, `createBranchedSession(leafId)`.
- **Append** (each returns the new entry ID): `appendMessage`, `appendThinkingLevelChange(level)`,
  `appendModelChange(provider, modelId)`, `appendCompaction(summary, firstKeptEntryId, tokensBefore,
  details?, fromHook?)`, `appendCustomEntry(customType, data?)`, `appendSessionInfo(name)`,
  `appendCustomMessageEntry(customType, content, display, details?)`, `appendLabelChange(targetId, label)`.
- **Tree nav**: `getLeafId()`, `getLeafEntry()`, `getEntry(id)`, `getBranch(fromId?)`, `getTree()`,
  `getChildren(parentId)`, `getLabel(id)`, `branch(entryId)`, `resetLeaf()`,
  `branchWithSummary(entryId, summary, details?, fromHook?)`.
- **Context/info**: `buildContextEntries()`, `buildSessionContext()`, `getEntries()`, `getHeader()`,
  `getSessionName()`, `getCwd()`, `getSessionDir()`, `getSessionId()`, `getSessionFile()`, `isPersisted()`.

## Example JSONL

```jsonl
{"type":"session","version":3,"id":"…uuid…","timestamp":"2026-01-01T00:00:00.000Z","cwd":"/home/me/proj"}
{"type":"message","id":"a1b2c3d4","parentId":null,"timestamp":"…","message":{"role":"user","content":"hi","timestamp":1}}
{"type":"message","id":"e5f6a7b8","parentId":"a1b2c3d4","timestamp":"…","message":{"role":"assistant","content":[{"type":"text","text":"hello"}],"provider":"anthropic","model":"claude-sonnet-4","stopReason":"stop","usage":{},"timestamp":2}}
```

Parse by switching on `entry.type` (`session`, `message`, `compaction`, `branch_summary`, `custom`,
`custom_message`, `label`, `model_change`, `thinking_level_change`).
