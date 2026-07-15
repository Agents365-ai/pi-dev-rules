# Pi — CLI, Usage, Sessions & Keybindings

Source: https://pi.dev/docs/latest/quickstart, /usage, /sessions, /keybindings

## Install & uninstall

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent   # npm (recommended)
curl -fsSL https://pi.dev/install.sh | sh                         # Linux/macOS one-liner
# uninstall: use your package manager's remove for the same package (npm/pnpm/yarn/bun)
```

## Authenticate

- **Subscription login**: run `/login` in-session to auth Claude Pro/Max, ChatGPT Plus/Pro,
  or GitHub Copilot. `/logout` clears credentials. Tokens stored in `~/.pi/agent/auth.json`
  and auto-refresh.
- **API key**: `export ANTHROPIC_API_KEY=sk-ant-...` then `pi` (or `/login` → store an API key
  into `auth.json`, or `--api-key <key>`).

## Launch

```bash
cd /path/to/project
pi
```

On first launch in a project that ships `.pi/` resources or `.agents/skills`, Pi asks whether to
**trust** it (loads project settings/extensions/skills/prompts/themes). See
`security-and-containerization.md` for the trust model.

## Interactive editor

- Four UI areas: startup header (shortcuts, loaded context files, prompt templates, skills,
  extensions), messages, editor, footer. Editor border color shows thinking level.
- `@` — fuzzy-search project files; **Tab** path completion.
- **Shift+Enter** newline (Ctrl+Enter on Windows Terminal); **Ctrl+J** newline alias (works in tmux).
- Paste images **Ctrl+V** (**Alt+V** on Windows) or drag-and-drop.
- `!command` runs shell and sends output to model; `!!command` runs without sending.
- **Ctrl+G** opens `$VISUAL`/`$EDITOR` (or `externalEditor` setting).
- **Ctrl+X** copies the last assistant message (or selected message in `/tree`).

### Message queue (steering & follow-up)

While the agent is running you can keep typing:

- **Enter** — queue a *steering* message (delivered after the current assistant turn / next tool
  boundary; delivery controlled by `steeringMode`).
- **Alt+Enter** — queue a *follow-up* message (delivered after the agent finishes; `followUpMode`).
- **Escape** — abort the run and restore queued messages into the editor.
- **Alt+Up** — pull queued messages back into the editor.

## Slash commands

`/login` `/logout` · `/model` (or Ctrl+L) · `/scoped-models` (enable/disable the Ctrl+P cycle set) ·
`/settings` (thinking level, theme, message delivery, transport) · `/trust` (save project trust
decision) · `/resume` · `/session` (id, tokens, cost) · `/tree` (jump anywhere in session) ·
`/new` · `/name <name>` · `/fork` · `/clone` · `/import <file>` (resume from a JSONL file) ·
`/compact [instructions]` · `/export [file]` (HTML **or** JSONL) · `/copy` (copy last assistant
message; also Ctrl+X) · `/share` (GitHub gist) · `/reload` (re-apply keybindings/resources) · `/hotkeys` ·
`/changelog` · `/skill:<name> [args]` (needs `enableSkillCommands`) · `/quit`.

## Context files

Pi loads `AGENTS.md` or `CLAUDE.md` from: global `~/.pi/agent/AGENTS.md`, parent dirs, and the
current dir. Replace the default system prompt with `~/.pi/agent/SYSTEM.md` (global) or
`.pi/SYSTEM.md` (project), or append via `~/.pi/agent/APPEND_SYSTEM.md` / `.pi/APPEND_SYSTEM.md`.
Disable with `--no-context-files` / `-nc`. Context files load regardless of project trust.

## CLI reference

**Package management**

```bash
pi install <source> [-l]    # -l writes to project .pi/settings.json (team sharing)
pi remove <source> [-l]     # alias: pi uninstall
pi update [source]          # update packages/extensions
pi update self              # update Pi itself (also: pi update pi, --self)
pi update --all             # update everything; --extensions all; --extension <src> one
pi list
pi config
```

**Modes**

- default interactive · `-p`/`--print` print then exit · `--mode json` · `--mode rpc` ·
  `--export <in> [out]` export session to HTML.

**Model options**

- `--provider <name>` (anthropic, openai, google, …)
- `--model <pattern>` — accepts `provider/model`, `model:thinkingLevel`, glob patterns.
- `--thinking <off|minimal|low|medium|high|xhigh|max>`
- `--list-models [search]`, `--models "claude-*,gpt-4o"` (comma-separated patterns for Ctrl+P cycle)
- `--api-key <key>` — key override (highest precedence).

**Session options**

- `-c`/`--continue` · `-r`/`--resume` · `--session <path|id>` · `--fork <path|id>` ·
  `--no-session` (ephemeral) · `--session-dir <dir>` (storage dir; CLI > `PI_CODING_AGENT_SESSION_DIR`
  > settings) · `--name <name>`/`-n` (set session display name at startup) ·
  `--exclude-tools <list>`/`-xt` (disable specific tools while keeping others).

**Tool options**

- `--tools <list>`/`-t` allowlist · `--exclude-tools <list>`/`-xt` disable specific tools ·
  `--no-builtin-tools`/`-nbt` · `--no-tools`/`-nt`.
- Built-in tools: `read, bash, edit, write, grep, find, ls`.

**Resource options**

- `-e`/`--extension <source>` · `--skill <path>` · `--prompt-template <path>` · `--theme <path>`
  (all repeatable, additive).
- Disable discovery: `--no-extensions` · `--no-skills` · `--no-prompt-templates` · `--no-themes` ·
  `--no-context-files`/`-nc`. (`--skill`/`-e` stay additive even with the matching `--no-*`.)

**Trust options**

- `-a`/`--approve` — trust project-local files for this run · `-na`/`--no-approve` — ignore them.

**Other**

- `--system-prompt <text>` · `--append-system-prompt <text>` · `--verbose` (force verbose startup) ·
  `-h`/`--help` · `-v`/`--version`.

**File args**: prefix with `@` to include in the message — `pi @file.md "command"` (images too).

**Examples**

```bash
pi "List all .ts files in src/"
pi -p "Summarize this codebase"
cat README.md | pi -p "Summarize this text"
pi @README.md "Summarize this"
pi @src/app.ts @src/app.test.ts "Review these together"
pi -p @screenshot.png "What's in this image?"
pi --provider openai --model gpt-4o "Help me refactor"
pi --model openai/gpt-4o "Help me refactor"
pi --model sonnet:high "Solve this complex problem"
pi --models "claude-*,gpt-4o"
pi --tools read,grep,find,ls -p "Review the code"
```

## Environment variables

- `PI_CODING_AGENT_DIR` — override config dir.
- `PI_CODING_AGENT_SESSION_DIR` — override session storage.
- `PI_PACKAGE_DIR` — override package dir (Nix/Guix store paths).
- `PI_OFFLINE` — disable network ops.
- `PI_SKIP_VERSION_CHECK` — skip version check.
- `PI_TELEMETRY` — override install/update telemetry (`1/true/yes` or `0/false/no`).
- `PI_CACHE_RETENTION` — set `long` for extended prompt cache.
- `PI_HARDWARE_CURSOR` — show hardware cursor (also `showHardwareCursor` setting).
- `VISUAL` / `EDITOR` — external editor for Ctrl+G (override with `externalEditor` setting).
- `PI_CODING_AGENT_CONFIG_DIR` — alias for `PI_CODING_AGENT_DIR`.

## Sessions

Auto-saved as JSONL under `~/.pi/agent/sessions/`, organized by working dir. Each session is a
**tree**: every entry has an id and parent id. Schema details in `session-format.md`.

- Startup: `pi -c`, `pi -r`, `pi --session <path|id>`, `pi --fork <path|id>`, `pi --no-session`.
- Interactive: `/resume`, `/new`, `/name <name>`, `/session`, `/tree`, `/fork`, `/clone`,
  `/import <file>`, `/export [file]`.
- `/tree`: arrow-key navigation, fold/unfold, label entries, pick any point to continue.
  Selecting a **user/custom** message moves the leaf to its parent, loads the text into the editor,
  and starts a new branch; selecting an **assistant/tool/compaction** entry continues from there with
  an empty editor; selecting root resets to an empty conversation. Switching branches can summarize
  the abandoned path (see compaction reference).
- `/resume` picker: search, **Ctrl+N** named-only filter, **Ctrl+S** toggle sort, **Ctrl+P** toggle
  path display, **Ctrl+R** rename, **Ctrl+D** delete (uses `trash` CLI when available).

## Keybindings

Customize in `~/.pi/agent/keybindings.json`; run `/reload` to apply (no restart). Pre-namespaced
ids migrate automatically. Key format `modifier+key` with modifiers `ctrl/shift/alt` (combinable),
letters/digits, special keys (escape, enter, tab, space, backspace, delete, home, end, pageUp,
pageDown, arrows), f1–f12, and symbol names (backtick, dash, equals, brackets, backslash,
semicolon, quote, comma, period, slash). Each action takes a key or array of keys; user config
overrides defaults. Built-in Emacs and Vim preset examples exist.

```json
{
  "tui.editor.cursorUp": ["up", "ctrl+p"],
  "tui.editor.cursorDown": ["down", "ctrl+n"],
  "tui.editor.deleteWordBackward": ["ctrl+w", "alt+backspace"]
}
```

**Action namespaces**: `tui.editor.*` (cursor/word/line moves, `deleteToLineStart` ctrl+u,
`deleteToLineEnd` ctrl+k, kill-ring `yank` ctrl+y / `yankPop` alt+y, `undo` ctrl+-, `jumpForward`
ctrl+] / `jumpBackward` ctrl+alt+]) · `tui.input.*` (`newLine` shift+enter/ctrl+j, `submit` enter,
`copy` ctrl+c) · `tui.select.*` (up/down/pageUp/pageDown/confirm/cancel) · `app.*`
(`interrupt` escape, `clear` ctrl+c, `exit` ctrl+d, `suspend` ctrl+z, `editor.external` ctrl+g,
`clipboard.pasteImage` ctrl+v/alt+v) · `app.session.*` (`new`/`tree`/`fork`/`resume`,
`togglePath` ctrl+p, `toggleSort` ctrl+s, `rename` ctrl+r, `delete` ctrl+d) · `app.model.*`
(`select` ctrl+l, `cycleForward` ctrl+p, `cycleBackward` shift+ctrl+p) · `app.thinking.*`
(`cycle` shift+tab, `toggle` ctrl+t) · `app.tools.expand` ctrl+o · `app.message.copy` ctrl+x · `app.message.followUp` alt+enter /
`dequeue` alt+up · `app.tree.*` (fold/unfold, `editLabel` shift+l, filter cycles) ·
`app.models.*` (scoped-models selector: `save` ctrl+s, `enableAll` ctrl+a, `clearAll` ctrl+x).
