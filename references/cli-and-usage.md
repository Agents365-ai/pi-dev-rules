# Pi — CLI, Usage, Sessions & Keybindings

Source: https://pi.dev/docs/latest/quickstart, /usage, /sessions, /keybindings

## Install & uninstall

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
# uninstall: use your package manager's remove for the same package (npm/pnpm/yarn/bun)
```

## Authenticate

- **Subscription login**: run `/login` in-session to auth Claude Pro/Max, ChatGPT Plus/Pro
  (Codex), or GitHub Copilot. `/logout` clears credentials. Tokens stored in
  `~/.pi/agent/auth.json` and auto-refresh.
- **API key**: `export ANTHROPIC_API_KEY=sk-ant-...` then `pi`.

## Launch

```bash
cd /path/to/project
pi
```

## Interactive editor

- Four UI areas: startup header (shortcuts, loaded context files, prompt templates, skills,
  extensions), messages, editor, footer. Editor border color shows thinking level.
- `@` — fuzzy-search project files; **Tab** path completion.
- **Shift+Enter** newline (Ctrl+Enter on Windows Terminal). Paste images Ctrl+V / drag.
- `!command` runs shell and sends output to model; `!!command` runs without sending.
- **Ctrl+G** opens `$VISUAL`/`$EDITOR`.

## Slash commands (subset)

`/login` `/logout` · `/model` (or Ctrl+L) · `/settings` (thinking level, theme) ·
`/resume` · `/session` (id, tokens, cost) · `/tree` (jump anywhere in session) ·
`/new` · `/name <name>` · `/fork` · `/clone` · `/compact [instructions]` ·
`/export [file]` (HTML) · `/share` (GitHub gist) · `/reload` (apply keybindings) ·
`/skill:<name> [args]` (needs `enableSkillCommands`).

## Context files

Pi loads `AGENTS.md` or `CLAUDE.md` from: global `~/.pi/agent/AGENTS.md`, parent dirs, and the
current dir. Replace the default system prompt with `.pi/SYSTEM.md`, or append via
`.pi/APPEND_SYSTEM.md`. Disable with `--no-context-files` / `-nc`.

## CLI reference

**Package management**

```bash
pi install <source> [-l]    # -l writes to project .pi/settings.json (team sharing)
pi remove <source> [-l]
pi update [source|self|pi]
pi list
pi config
```

**Modes**

- default interactive · `-p`/`--print` print then exit · `--mode json` · `--mode rpc` ·
  `--export <in> [out]` export session to HTML.

**Model options**

- `--provider <name>` (anthropic, openai, google, …)
- `--model <pattern>` — accepts `provider/model`, `model:thinkingLevel`, glob patterns.
- `--thinking <off|minimal|low|medium|high|xhigh>`
- `--list-models [search]`, `--models "claude-*,gpt-4o"`

**Session options**

- `-c`/`--continue` · `-r`/`--resume` · `--session <path|id>` · `--fork <path|id>` ·
  `--no-session` (ephemeral).

**Tool options**

- `--tools <list>` allowlist · `--no-builtin-tools` · `--no-tools`.
- Built-in tools: `read, bash, edit, write, grep, find, ls`.

**Other**

- `-e`/`--extension <source>` · `--skill <path>` · `--prompt-template <path>` ·
  `--theme <path>` · `--no-context-files`/`-nc` · `--system-prompt <text>` ·
  `-h`/`--help` · `-v`/`--version`.

**File args**: prefix with `@` to include in the message — `pi @file.md "command"`.

**Examples**

```bash
pi "List all .ts files in src/"
pi -p "Summarize this codebase"
cat README.md | pi -p "Summarize this text"
pi --provider openai --model gpt-4o "Help me refactor"
pi --model openai/gpt-4o "Help me refactor"
pi --model sonnet:high "Solve this complex problem"
pi --models "claude-*,gpt-4o"
pi --tools read,grep,find,ls -p "Review the code"
```

## Environment variables

- `PI_CODING_AGENT_DIR` — override config dir.
- `PI_CODING_AGENT_SESSION_DIR` — override session storage.
- `PI_OFFLINE` — disable network ops.
- `PI_SKIP_VERSION_CHECK` — skip version check.
- `VISUAL` / `EDITOR` — external editor for Ctrl+G.

## Sessions

Auto-saved as JSONL under `~/.pi/agent/sessions/`, organized by working dir. Each session is a
**tree**: every message has an id and parent id.

- Startup: `pi -c`, `pi -r`, `pi --session <path|id>`, `pi --fork <path|id>`, `pi --no-session`.
- Interactive: `/resume`, `/new`, `/name <name>`, `/session`, `/tree`, `/fork`, `/clone`,
  `/export [file]`.
- `/tree`: arrow-key navigation, fold/unfold, label entries, pick any point to continue.
  Selecting a user message loads it into the editor for revision; an assistant message continues
  from there. Switching branches can summarize the abandoned path (see compaction reference).
- `/resume` picker: search, filter named-only (Ctrl+N), rename (Ctrl+R), delete (Ctrl+D).

## Keybindings

Customize in `~/.pi/agent/keybindings.json`; run `/reload` to apply (no restart). Pre-namespaced
ids (e.g. `cursorUp`) migrate automatically. Key format `modifier+key` with modifiers
`ctrl/shift/alt` (combinable), letters/digits, special keys (escape, enter, tab, space, backspace,
delete, home, end, pageUp, pageDown, arrows), f1–f12, and symbol names.

```json
{
  "tui.editor.cursorUp": ["up", "ctrl+p"],
  "tui.editor.cursorDown": ["down", "ctrl+n"],
  "tui.editor.deleteWordBackward": ["ctrl+w", "alt+backspace"]
}
```

Each action takes a key or array of keys; user config overrides defaults. Built-in Emacs and Vim
preset examples exist.

Notable defaults: `ctrl+a`/`ctrl+e` line start/end · `alt+b`/`alt+f` word move ·
`ctrl+w`/`alt+backspace` delete word back · `alt+d` delete word fwd · `ctrl+u`/`ctrl+k` to
line start/end · `shift+enter` newline · `enter` submit · `tab` autocomplete ·
`ctrl+c` clear/cancel · `ctrl+d` exit when empty · `ctrl+g` external editor ·
`ctrl+l` model selector · `ctrl+p`/`shift+ctrl+p` cycle models · `shift+tab` cycle thinking ·
`ctrl+t` toggle thinking blocks · `ctrl+o` expand/collapse tool output · `alt+enter` queue
follow-up · `alt+up` restore queued.
