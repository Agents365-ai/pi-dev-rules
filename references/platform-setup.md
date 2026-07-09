# Pi — Platform Setup & Development

Source: https://pi.dev/docs/latest/{windows,termux,tmux,terminal-setup,shell-aliases,development}

Terminals strip modifier info differently, so **modified-Enter** (Shift/Ctrl/Alt+Enter) needs
per-terminal setup for steering/follow-up/newline to work. Pi uses the Kitty keyboard protocol where
available and falls back to xterm `modifyOtherKeys`.

## Windows

Pi requires a **bash shell**. It checks, in order:

1. `shellPath` in `~/.pi/agent/settings.json`
2. Git Bash (`C:\Program Files\Git\bin\bash.exe`)
3. `bash.exe` on PATH (Cygwin, MSYS2, WSL)

For most users, [Git for Windows](https://git-scm.com/download/win) is enough. Custom path (note
escaped backslashes):

```json
{ "shellPath": "C:\\cygwin64\\bin\\bash.exe" }
```

(Windows Terminal keybindings live under **Terminal Setup**, not here.)

## Termux (Android)

1. Install **Termux** and **Termux:API** from GitHub or F-Droid (**not** Google Play — deprecated).
2. Install and run Pi:

```bash
pkg update && pkg upgrade
pkg install nodejs termux-api git
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
mkdir -p ~/.pi/agent
pi
```

- Clipboard via `termux-clipboard-set` / `termux-clipboard-get` (needs Termux:API). **Image clipboard
  is not supported** — `ctrl+v` image paste won't work.
- Pi detects Termux via `TERMUX_VERSION` (used for clipboard + TUI redraw handling).
- Run `termux-setup-storage` once for `/storage/emulated/0`. Some native deps are skipped on Android
  ARM64. A tailored `~/.pi/agent/AGENTS.md` documenting Termux paths/commands helps the agent.

## tmux

tmux collapses `Shift/Ctrl+Enter` to plain `Enter` unless extended keys are on. Add to `~/.tmux.conf`:

```tmux
set -g extended-keys on
set -g extended-keys-format csi-u
```

Then fully restart: `tmux kill-server && tmux`. `extended-keys-format csi-u` needs **tmux 3.5+**; on
3.2–3.4 omit the `-format` line (Pi supports the default xterm `modifyOtherKeys` too). Requires a
terminal that supports extended keys (Ghostty, Kitty, iTerm2, WezTerm, Windows Terminal).

| Key | Without extkeys | With `csi-u` |
|-----|-----------------|--------------|
| Enter | `\r` | `\r` |
| Shift+Enter | `\r` | `\x1b[13;2u` |
| Ctrl+Enter | `\r` | `\x1b[13;5u` |
| Alt/Option+Enter | `\x1b\r` | `\x1b[13;3u` |

## Terminal Setup

`PI_HARDWARE_CURSOR=1` (or `showHardwareCursor: true`) shows a hardware cursor (helps CJK IME).

- **Kitty, iTerm2** — work out of the box.
- **Apple Terminal** — Pi enables enhanced key reporting; a local macOS modifier fallback handles
  `Shift+Enter` (same-Mac only, not over SSH).
- **Ghostty** — `~/.config/ghostty/config` (macOS: `~/Library/Application Support/com.mitchellh.ghostty/config`):
  `keybind = alt+backspace=text:\x1b\x7f`. Remove any old `keybind = shift+enter=text:\n` from Claude
  Code (Pi's `Ctrl+J` newline alias keeps Shift+Enter working in tmux).
- **WezTerm** — usually works; to force Kitty protocol set `config.enable_kitty_keyboard = true` in
  `~/.wezterm.lua`. For macOS `Option+Enter` follow-up queueing, map `key='Enter', mods='ALT'` →
  `SendString('\x1b[13;3u')`. On WSL, set `PI_HARDWARE_CURSOR=1` if IME candidates lag.
- **Alacritty** — `~/.config/alacritty/alacritty.toml`, `Option+Enter`:
  `[[keyboard.bindings]] key="Enter" mods="Alt" chars="[13;3u"`. Restart after.
- **VS Code integrated terminal** — 1.109.5+ enables Kitty protocol by default; older needs a
  `keybindings.json` `sendSequence` entry (`shift+enter` → `[13;2u`, `when: terminalFocus`).
- **Windows Terminal** — `settings.json` actions mapping `shift+enter` → `[13;2u` and
  `alt+enter` → `[13;3u` (the latter frees `Alt+Enter` from fullscreen). Fully restart.
- **xfce4-terminal, terminator, IntelliJ terminal** — limited escape support; modified-Enter can't
  be distinguished from Enter (breaks bindings like `submit: ["ctrl+enter"]`). Prefer Kitty-protocol
  terminals (Kitty, Ghostty, WezTerm, iTerm2, Alacritty).

## Shell aliases

Pi runs bash non-interactively (`bash -c`), which doesn't expand aliases. Enable them via
`shellCommandPrefix` in `~/.pi/agent/settings.json` (adjust the rc path to your shell):

```json
{ "shellCommandPrefix": "shopt -s expand_aliases\neval \"$(grep '^alias ' ~/.zshrc)\"" }
```

## Development (build from source)

Repo `earendil-works/pi-mono` (guidelines: `AGENTS.md` at repo root).

```bash
git clone https://github.com/earendil-works/pi-mono
cd pi-mono && npm install && npm run build
/path/to/pi-mono/pi-test.sh          # run from source, keeps caller's cwd
```

**Testing**:

```bash
./test.sh                            # non-LLM tests (no API keys)
npm test                             # all tests
npm test -- test/specific.test.ts    # one test
```

**Project structure**:

```
packages/
  ai/           # LLM provider abstraction
  agent/        # agent loop + message types
  tui/          # terminal UI components
  coding-agent/ # CLI + interactive mode
```

- **Fork / rebrand** via `package.json` `piConfig` (`name`, `configDir` — affects banner, config
  paths, env var names) and the `bin` field:
  ```json
  { "piConfig": { "name": "pi", "configDir": ".pi" } }
  ```
- **Path resolution** — three modes (npm install, standalone binary, tsx from source); always use
  `src/config.ts` for package assets (`getPackageDir()`, `getThemeDir()`), never `__dirname`.
- **Debug** — hidden `/debug` command writes `~/.pi/agent/pi-debug.log` (rendered TUI lines + last
  messages sent to the LLM).
