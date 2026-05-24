# Extending Pi — Extensions, Skills, Prompt Templates, Themes, Packages

Source: https://pi.dev/docs/latest/extensions, /skills, /prompt-templates, /themes, /packages

---

## 1. Extensions

TypeScript modules that extend Pi's behavior. They subscribe to lifecycle events, register
LLM-callable tools, add commands, bind shortcuts, register providers, and more. **They run with
full system permissions.**

### Discovery

- `~/.pi/agent/extensions/*.ts` (global)
- `.pi/extensions/*.ts` (project)
- `pi -e ./path.ts` (one-off / testing)

### Skeleton

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
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

### Events

- **Session**: `session_start`, `session_shutdown`, `session_before_switch`, `session_before_fork`
- **Agent**: `before_agent_start`, `agent_start`, `agent_end`, `turn_start`, `turn_end`
- **Tools**: `tool_call`, `tool_result`, `tool_execution_start|update|end`
- **Messages**: `message_start`, `message_update`, `message_end`, `input`, `context`
- **Model/thinking**: `model_select`, `thinking_level_select`

### `ExtensionAPI` methods

- **Register**: `registerTool(def)`, `registerCommand(name, opts)`, `registerShortcut(key, opts)`,
  `registerFlag(name, opts)`, `on(event, handler)`.
- **Messaging**: `sendMessage()`, `sendUserMessage()`, `appendEntry()` (persist state in session).
- **Tools**: `getActiveTools()`, `getAllTools()`, `setActiveTools()`, `registerMessageRenderer()`,
  `registerProvider()`.
- **Session**: `setSessionName()`, `getSessionName()`, `setLabel()`, `exec()` (shell).
- **Model**: `setModel()`, `getThinkingLevel()`, `setThinkingLevel()`.

### `ExtensionContext` (`ctx`)

`ctx.ui.*` (dialogs), `ctx.sessionManager`, `ctx.cwd`, `ctx.signal`, `ctx.isIdle()`,
`ctx.getContextUsage()`, `ctx.getSystemPrompt()`. Commands get `ExtensionCommandContext` which adds
`waitForIdle()`, `newSession()`, `fork()`, `switchSession()`, `navigateTree()`.

### Tool definition

```typescript
pi.registerTool({
  name: "tool_name",
  label: "Display Name",
  description: "LLM-visible description",
  promptSnippet: "One-line system prompt entry",
  promptGuidelines: ["Use tool_name when..."],
  parameters: Type.Object({ /* schema */ }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    onUpdate?.({ content: [...] });           // stream updates
    return { content: [...], details: {...}, terminate: true /* optional: skip follow-up */ };
  },
  renderCall(args, theme, context) { ... },
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
// Transform input
pi.on("input", async (event, ctx) => {
  if (event.text.startsWith("?quick "))
    return { action: "transform", text: `Respond briefly: ${event.text.slice(7)}` };
});
// Inject system prompt
pi.on("before_agent_start", async (event, ctx) =>
  ({ systemPrompt: event.systemPrompt + "\nExtra instructions..." }));
```

### UI

```typescript
const choice    = await ctx.ui.select("Pick one:", ["A", "B", "C"]);
const confirmed = await ctx.ui.confirm("Delete?", "Confirm?");
const name      = await ctx.ui.input("Name:", "placeholder");
const text      = await ctx.ui.editor("Edit:", "content");
ctx.ui.notify("Done!", "info");
ctx.ui.setStatus("my-ext", "Processing...");
ctx.ui.setWidget("my-ext", ["Line 1", "Line 2"]);
ctx.ui.setWorkingMessage("Thinking...");
ctx.ui.setTitle("pi - project");
ctx.ui.custom(async (ui, theme) => { /* return custom component */ });
```

### Constraints (rules)

- **Output truncation**: keep tool results ≲50KB / 2000 lines.
- **File mutations**: use `withFileMutationQueue()` for concurrent-safe edits.
- **Errors**: throw — never return error flags.
- **Type safety**: use `StringEnum` from `@earendil-works/pi-ai` for LLM-facing enums.
- **Session replacement**: never reuse an old `ctx` after a session switch.

### State persistence

Store state in tool-result `details` so it survives branching; rebuild on `session_start`:

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
| `compatibility` | No | environment requirements |
| `metadata` | No | custom key-value pairs |
| `allowed-tools` | No | pre-approved tools (experimental) |
| `disable-model-invocation` | No | hide from system prompt when true |

### Loading locations (order)

- Global: `~/.pi/agent/skills/` and `~/.agents/skills/`
- Project: `.pi/skills/` and `.agents/skills/` (up to repo root)
- Packages: `skills/` dirs or `pi.skills` in package.json
- Settings: `skills` array
- CLI: `--skill <path>` (repeatable, additive)

In `~/.pi/agent/skills/` and `.pi/skills/`, root `.md` files become individual skills; everywhere,
directories containing `SKILL.md` are discovered recursively.

### Skill commands

`/skill:name` (load+execute), `/skill:name args` (args append as user input). Enable via `/settings`
or `enableSkillCommands`.

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
(1-indexed) · `${@:N:L}` L args from N.

**Locations**: `~/.pi/agent/prompts/*.md`, `.pi/prompts/*.md`, package `prompts/` or `pi.prompts`,
settings `prompts` array, `--prompt-template <path>` (repeatable). Discovery is **non-recursive**.

**Usage**: type `/name` (autocomplete shows description + arg hint); `/component Button "click handler"`.

---

## 4. Themes

JSON with `name` (required, unique), optional `vars`, and `colors` (**all 51 tokens required**).

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

**Token groups (51)**: Core UI (accent, border, borderAccent, borderMuted, success, error, warning,
muted, dim, text, thinkingText) · Backgrounds (selectedBg, userMessageBg/Text, customMessageBg/
Text/Label, toolPendingBg, toolSuccessBg, toolErrorBg, toolTitle, toolOutput) · Markdown (mdHeading,
mdLink, mdLinkUrl, mdCode, mdCodeBlock, mdCodeBlockBorder, mdQuote, mdQuoteBorder, mdHr,
mdListBullet) · Diffs (toolDiffAdded/Removed/Context) · Syntax (syntaxComment, syntaxKeyword,
syntaxFunction, syntaxVariable, syntaxString, syntaxNumber, syntaxType, syntaxOperator,
syntaxPunctuation) · Thinking levels (thinkingOff/Minimal/Low/Medium/High/Xhigh) · bashMode ·
optional export (pageBg, cardBg, infoBg).

**Value formats**: hex `#ff0000`, 256-color index 0–255, `vars` reference, or `""` for terminal default.

---

## 5. Packages

Bundle extensions, skills, prompt templates, and themes for sharing via npm or git.

```bash
pi install npm:@foo/bar@1.0.0
pi install git:github.com/user/repo@v1
pi install https://github.com/user/repo
pi install /absolute/path        # or ./relative/path (added to settings, not copied)
pi install npm:@foo/bar -l       # -l → project .pi/settings.json (team sharing)
pi install <source> -e           # -e → temporary, single run
pi remove npm:@foo/bar
pi list
pi update
```

**Sources**: npm `npm:@scope/pkg@1.2.3` (versioned = pinned, skipped on update; installs to
`~/.pi/agent/npm/` or `.pi/npm/`) · git `git:github.com/user/repo@v1` / HTTPS / SSH (pinned to
tag/commit; cloned to `~/.pi/agent/git/<host>/<path>` or `.pi/git/...`) · local paths.

**Create** — add a `pi` manifest to `package.json`:

```json
{
  "name": "my-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

`pi-package` keyword enables gallery discovery. Paths support globs and `!` exclusions. Without a
manifest, Pi auto-discovers: `extensions/` (.ts/.js), `skills/` (recursive `SKILL.md`), `prompts/`
(.md), `themes/` (.json).

**Dependencies**: runtime deps in `dependencies`; core Pi packages as `peerDependencies` with `"*"`
(don't bundle); other Pi packages must be bundled and referenced via `node_modules/` paths.

**Filtering** (settings object form): `!pattern` exclude, `+path` force-include, `-path` force-exclude.

```json
{ "source": "npm:my-package",
  "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
  "skills": [], "prompts": ["prompts/review.md"] }
```

**Gallery media**: `"pi": { "video": "...mp4", "image": "...png" }` (MP4 video takes precedence).
