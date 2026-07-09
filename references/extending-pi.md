# Extending Pi — Extensions, Skills, Prompt Templates, Themes, Packages

Source: https://pi.dev/docs/latest/extensions, /skills, /prompt-templates, /themes, /packages
See also: `tui-components.md` (custom UI), `session-format.md` (entry/message schema).

---

## 1. Extensions

TypeScript modules that extend Pi's behavior. They subscribe to lifecycle events, register
LLM-callable tools, add commands, bind shortcuts, register providers, and more. **They run with
full system permissions.**

### Discovery

- `~/.pi/agent/extensions/*.ts` and `~/.pi/agent/extensions/*/index.ts` (global)
- `.pi/extensions/*.ts` and `.pi/extensions/*/index.ts` (project — requires trust)
- `pi -e ./path.ts` (one-off / testing)

Project extensions require project trust; user/global and CLI `-e` extensions load before trust
resolves and may handle the `project_trust` event.

### Skeleton

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {           // may be `async`; awaited before startup
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  pi.registerTool({
    name: "greet",
    description: "Greet someone by name",
    parameters: Type.Object({ name: Type.String() }),
    async execute(toolCallId, params, signal, onUpdate, ctx) {
      return { content: [{ type: "text", text: `Hello, ${params.name}!` }], details: {} };
    },
  });
}
```

Do **not** start background resources in the factory — defer to `session_start`, clean up in
`session_shutdown`.

### Events

- **Startup**: `project_trust` (first extension to return yes/no owns the decision),
  `resources_discover` (contribute skill/prompt/theme paths; `reason: "startup"|"reload"`).
- **Session**: `session_start` (`reason: "startup"|"reload"|"new"|"resume"|"fork"`),
  `session_info_changed`, `session_before_switch`, `session_before_fork`,
  `session_before_compact` (may supply a custom summary), `session_compact`,
  `session_before_tree` (may supply a custom summary), `session_tree`, `session_shutdown`.
- **Agent**: `before_agent_start`, `agent_start`, `agent_end`.
- **Turn**: `turn_start`, `turn_end`.
- **Messages**: `message_start`, `message_update`, `message_end`.
- **Tools**: `tool_call`, `tool_result`, `tool_execution_start|update|end`.
- **Provider/model**: `before_provider_headers` (mutate outgoing headers in place),
  `before_provider_request` (inspect/replace payload before send),
  `after_provider_response` (`event.status`, `event.headers`, before stream consume),
  `context`, `model_select` (`event.source: "set"|"cycle"|"restore"`), `thinking_level_select`.
- **User interaction**: `user_bash` (`!`/`!!`; can supply operations or a result), `input`.

### `ExtensionAPI` methods

- **Register**: `registerTool(def)`, `registerCommand(name, opts)`, `registerShortcut(key, opts)`,
  `registerFlag(name, opts)`, `registerMessageRenderer()`,
  `registerEntryRenderer(customType, renderer)` (render `custom` session entries),
  `registerProvider()`, `unregisterProvider(name)`, `on(event, handler)`.
- **Messaging**: `sendMessage(text, { triggerTurn?, deliverAs? })` (`deliverAs:
  "steer"|"followUp"|"nextTurn"`), `sendUserMessage(content, { deliverAs? })`
  (`content: string | Content[]`), `appendEntry()` (persist state in session).
- **Tools/model**: `getActiveTools()`, `getAllTools()`, `setActiveTools()`, `setModel(model)`
  (returns boolean), `getThinkingLevel()` (`off|minimal|low|medium|high|xhigh`), `setThinkingLevel()`,
  `getCommands()` (`{ name, description, source, sourceInfo }[]`).
- **Session**: `setSessionName()`, `getSessionName()`, `setLabel()`, `exec()` (shell).
- **Cross-extension bus**: `pi.events.on(event, handler)`, `pi.events.emit(event, data)`.

### `ExtensionContext` (`ctx`)

`ctx.ui.*` (dialogs — see `tui-components.md`), `ctx.sessionManager`, `ctx.cwd`, `ctx.signal`,
`ctx.mode` (`"tui"|"rpc"|"json"|"print"`), `ctx.hasUI`, `ctx.isIdle()`, `ctx.isProjectTrusted()`,
`ctx.abort()`, `ctx.hasPendingMessages()`, `ctx.compact({ customInstructions?, onComplete?, onError? })`,
`ctx.getContextUsage()`, `ctx.getSystemPrompt()`, `ctx.modelRegistry`, `ctx.model`, `ctx.shutdown()`.

Commands get `ExtensionCommandContext`, which adds `waitForIdle()`, `reload()`,
`getSystemPromptOptions()`, `newSession({ parentSession?, setup?, withSession? })`,
`fork(entryId, { position?, withSession? })` (`position: "before"|"at"`),
`switchSession(path, { withSession? })`,
`navigateTree(targetId, { summarize?, customInstructions?, replaceInstructions?, label? })`.

`ctx.sessionManager` surface: `getEntries()`, `getBranch()`, `buildContextEntries()`,
`getLeafId()`, `getSessionFile()`, `getSessionId()`, `getLabel(entryId)` (full API in
`session-format.md`).

### Tool definition

```typescript
pi.registerTool({
  name: "tool_name",
  label: "Display Name",
  description: "LLM-visible description",
  promptSnippet: "One-line system prompt entry",
  promptGuidelines: ["Use tool_name when..."],
  parameters: Type.Object({ /* Typebox schema */ }),
  prepareArguments(args) { return args; },              // optional compat shim, before validation
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    onUpdate?.({ content: [...] });                     // stream updates
    return {
      content: [...],       // sent to LLM
      details: {...},       // rendering & state
      terminate: true,      // optional: skip follow-up LLM call if all tools set this
      // isError is set ONLY by a thrown error; returning it does nothing
    };
  },
  renderCall(args, theme, context) { ... },             // may return TUI components
  renderResult(result, options, theme, context) { ... },
});
```

### Handler patterns

```typescript
// Block a tool call
pi.on("tool_call", async (event, ctx) => {
  if (event.input.command?.includes("rm -rf")) return { block: true, reason: "Dangerous" };
});
// Modify a result
pi.on("tool_result", async (event, ctx) => ({ content: [...], details: {...} }));
// Transform / handle input (event.text, event.images, event.source, event.streamingBehavior)
pi.on("input", async (event, ctx) => {
  if (event.text.startsWith("?quick "))
    return { action: "transform", text: `Respond briefly: ${event.text.slice(7)}` };
  // action: "continue" (default) | "transform" (text/images) | "handled" (block agent, ext handles)
});
// Inject a persisted message and/or system prompt
pi.on("before_agent_start", async (event, ctx) =>
  ({ message: { customType: "note", content: "…", display: true },
     systemPrompt: event.systemPrompt + "\nExtra instructions..." }));
```

`event.systemPromptOptions` = `{ customPrompt, selectedTools, toolSnippets, promptGuidelines,
appendSystemPrompt, cwd, contextFiles, skills }`. Typed helpers: `isToolCallEventType("bash", event)`,
`isBashToolResult(event)` from `@earendil-works/pi-coding-agent`.

### UI (subset — full API in `tui-components.md`)

```typescript
const choice    = await ctx.ui.select("Pick one:", ["A", "B", "C"]);
const confirmed = await ctx.ui.confirm("Delete?", "Confirm?");
const name      = await ctx.ui.input("Name:", "placeholder");
const text      = await ctx.ui.editor("Edit:", "content");
ctx.ui.notify("Done!", "info");                          // "info" | "warning" | "error"
ctx.ui.setStatus("my-ext", "Processing...");
ctx.ui.setWorkingMessage("Thinking...");                 // also setWorkingIndicator({frames,intervalMs})
ctx.ui.setWidget("my-ext", ["Line 1", "Line 2"], { placement: "belowEditor" });
ctx.ui.setEditorText("prefill");
ctx.ui.setTitle("pi - project");
ctx.ui.custom(async (tui, theme, keybindings, done) => { /* return a Component */ });
```

### Utilities / exports

- Truncation: `truncateHead`, `truncateTail`, `truncateLine`, `DEFAULT_MAX_BYTES`, `DEFAULT_MAX_LINES`.
- Tool builders: `createReadTool`, `createBashTool`, `createLocalBashOperations`.
- Concurrency: `withFileMutationQueue(absPath, fn)` for concurrent-safe edits.
- Enums: `StringEnum` from `@earendil-works/pi-ai` for LLM-facing enums.
- `CONFIG_DIR_NAME` (`.pi`) — rebranding-safe config-dir constant; use `join(ctx.cwd, CONFIG_DIR_NAME, …)`.

### Constraints (rules)

- **Output truncation**: keep tool results ≲50KB / 2000 lines.
- **Errors**: throw — never return error flags.
- **Session replacement**: never reuse an old `ctx` after a session switch.

### State persistence

Store state in tool-result `details` (or `appendCustomEntry`) so it survives branching; rebuild on
`session_start`:

```typescript
pi.on("session_start", async (_event, ctx) => {
  for (const entry of ctx.sessionManager.getBranch())
    if (entry.type === "message" && entry.message.toolName === "my_tool") {
      // reconstruct from entry.message.details
    }
});
```

---

## 2. Skills

Three-stage system: (1) at startup Pi scans skill locations, extracting name + description;
(2) those appear in the system prompt as XML (Agent Skills spec); (3) when a task matches, the
agent loads the full `SKILL.md` and follows it, referencing scripts/assets via **relative paths**.
Progressive disclosure: only descriptions are always in context.

### Directory

```
my-skill/
├── SKILL.md       # required: frontmatter + instructions
├── scripts/       # helper scripts
├── references/    # detailed docs
└── assets/        # templates/resources
```

### `SKILL.md`

```
---
name: my-skill
description: What this skill does and when to use it.
---

# My Skill
## Setup
## Usage
```

### Frontmatter fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | 1–64 chars, lowercase `a-z 0-9 -` only |
| `description` | Yes | ≤1024 chars; determines when the skill loads |
| `license` | No | name or file ref |
| `compatibility` | No | environment requirements (≤500 chars) |
| `metadata` | No | custom key-value pairs |
| `allowed-tools` | No | pre-approved tools (experimental) |
| `disable-model-invocation` | No | hide from system prompt when true |

### Loading locations (order)

- Global: `~/.pi/agent/skills/` and `~/.agents/skills/`
- Project: `.pi/skills/` and `.agents/skills/` (searched in cwd and ancestors up to repo/fs root)
- Packages: `skills/` dirs or `pi.skills` in package.json
- Settings: `skills` array
- CLI: `--skill <path>` (repeatable, additive — stays active even with `--no-skills`)

In `~/.pi/agent/skills/` and `.pi/skills/`, root `.md` files become individual skills; everywhere,
directories containing `SKILL.md` are discovered recursively.

### Skill commands

`/skill:name` (load+execute), `/skill:name args` (args appended as `User: <args>`). Enable via
`/settings` or `enableSkillCommands`.

### Name rules

1–64 chars; lowercase letters/numbers/hyphens; no leading/trailing or consecutive hyphens.
Valid: `pdf-processing`, `data-analysis`. Invalid: `PDF-Processing`, `-pdf`, `pdf--processing`.

### Best practices

Descriptions must say *when* to load — "Extracts text and tables from PDFs, fills forms, merges
PDFs" beats "Helps with PDFs". Pi warns on most spec violations but is permissive; a skill with no
description won't load; name collisions warn and keep the first discovered.

---

## 3. Prompt templates

Markdown + optional YAML frontmatter. Filename (minus `.md`) is the command name (`review.md` → `/review`).

```
---
description: Review staged git changes
argument-hint: <required> [optional]
---
Review the staged changes (`git diff --cached`). Focus on:
- Bugs and logic errors
- Security issues
```

**Variables**: `$1`,`$2`… positional · `$@` / `$ARGUMENTS` all args joined · `${@:N}` from N
(1-indexed) · `${@:N:L}` L args from N · `${1:-default}` arg 1 or a default when empty.

**Locations**: `~/.pi/agent/prompts/*.md`, `.pi/prompts/*.md`, package `prompts/` or `pi.prompts`,
settings `prompts` array, `--prompt-template <path>` (repeatable). Discovery is **non-recursive**.
Disable with `--no-prompt-templates`. If `description` is omitted, the first non-empty line is used.

**Usage**: type `/name` (autocomplete shows description + arg hint); `/component Button "click handler"`.

---

## 4. Themes

JSON with `name` (required, unique, no `/`), optional `vars`, and `colors` (**all 51 tokens required**).
Hot-reloads on file edit; first run auto-detects terminal background.

```json
{
  "$schema": "https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json",
  "name": "my-theme",
  "vars": { "blue": "#0066cc", "gray": 242 },
  "colors": { /* 51 tokens */ }
}
```

**Locations**: built-in `dark`/`light`, `~/.pi/agent/themes/*.json`, `.pi/themes/*.json`, package
`themes/` or `pi.themes`, settings array, `--theme <path>` (repeatable). Disable with `--no-themes`.

**Token groups (51 required)**: Core UI (accent, border, borderAccent, borderMuted, success, error,
warning, muted, dim, text, thinkingText) · Backgrounds (selectedBg, userMessageBg/Text,
customMessageBg/Text/Label, toolPendingBg, toolSuccessBg, toolErrorBg, toolTitle, toolOutput) ·
Markdown (mdHeading, mdLink, mdLinkUrl, mdCode, mdCodeBlock, mdCodeBlockBorder, mdQuote,
mdQuoteBorder, mdHr, mdListBullet) · Diffs (toolDiffAdded/Removed/Context) · Syntax (syntaxComment,
syntaxKeyword, syntaxFunction, syntaxVariable, syntaxString, syntaxNumber, syntaxType, syntaxOperator,
syntaxPunctuation) · Thinking levels (thinkingOff/Minimal/Low/Medium/High/Xhigh) · bashMode.
**Optional HTML-export tokens** (beyond the 51): `export.pageBg`, `export.cardBg`, `export.infoBg`.

**Value formats**: hex `#ff0000`, 256-color index 0–255 (0–15 ANSI / 16–231 RGB cube /
232–255 grayscale), `vars` reference, or `""` for terminal default.

---

## 5. Packages

Bundle extensions, skills, prompt templates, and themes for sharing via npm or git.

```bash
pi install npm:@foo/bar@1.0.0
pi install git:github.com/user/repo@v1
pi install ssh://git@github.com/user/repo@v1     # or scp-style git:git@github.com:user/repo
pi install https://github.com/user/repo@v1
pi install /absolute/path        # or ./relative/path (added to settings, not copied)
pi install npm:@foo/bar -l       # -l → project .pi/settings.json (team sharing)
pi install <source> -e           # -e → temporary, single run
pi remove npm:@foo/bar
pi list
pi update [--all|--extensions|--extension <src>|--self|--force]
```

**Sources**: npm `npm:@scope/pkg@1.2.3` (versioned = pinned, skipped on update; installs to
`~/.pi/agent/npm/` or `.pi/npm/`) · git `git:github.com/user/repo@v1` / HTTPS / SSH / scp-style
(pinned to tag/commit; cloned to `~/.pi/agent/git/<host>/<path>` or `.pi/git/...`) · local paths.
`-l` writes install/remove to project settings; default is user settings.

**Create** — add a `pi` manifest to `package.json`:

```json
{
  "name": "my-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"],
    "video": "https://example.com/demo.mp4",
    "image": "https://example.com/screenshot.png"
  }
}
```

`pi-package` keyword enables gallery discovery (MP4 `video` takes precedence over `image`). Paths
support globs and `!` exclusions. Without a manifest, Pi auto-discovers: `extensions/` (.ts/.js),
`skills/` (recursive `SKILL.md`), `prompts/` (.md), `themes/` (.json).

**Dependencies**: runtime deps in `dependencies`; core Pi packages as `peerDependencies` with `"*"`
(don't bundle); third-party/other Pi packages go in `bundledDependencies` and are referenced via
`node_modules/` paths.

**Filtering** (settings object form): `!pattern` exclude, `+path` force-include, `-path`
force-exclude, `[]` (empty array) = load none of that resource type.

```json
{ "source": "npm:my-package",
  "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
  "skills": [], "prompts": ["prompts/review.md"] }
```
