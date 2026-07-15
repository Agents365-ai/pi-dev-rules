# Pi — Development (Build from Source)

Source: https://pi.dev/docs/latest/development

## Setup

Clone and build from the monorepo:

```bash
git clone https://github.com/earendil-works/pi-mono
cd pi-mono
npm install
npm run build
```

Run from source (from any directory — Pi keeps the caller's cwd):

```bash
/path/to/pi-mono/pi-test.sh
```

## Forking / rebranding

Configure via `package.json` under a `piConfig` key:

```json
{
  "piConfig": {
    "name": "pi",
    "configDir": ".pi"
  }
}
```

Changing `name`, `configDir`, and `bin` affects the CLI banner, config paths, and environment
variable names.

## Path resolution

Three execution modes: npm install, standalone binary, tsx from source. Always use
`src/config.ts` for package assets — import `getPackageDir` and `getThemeDir` from `"./config.js"`.
Never use `__dirname` directly for package assets.

## Debug

**`/debug`** (hidden slash command) writes to `~/.pi/agent/pi-debug.log` and captures:
- Rendered TUI lines with ANSI codes
- Last messages sent to the LLM

## Testing

| Command | Purpose |
|---------|---------|
| `./test.sh` | Run non-LLM tests (no API keys needed) |
| `npm test` | Run all tests |
| `npm test -- test/specific.test.ts` | Run a specific test file |

## Project structure

```
packages/
  ai/           # LLM provider abstraction
  agent/        # Agent loop and message types
  tui/          # Terminal UI components
  coding-agent/ # CLI and interactive mode
```

- **`ai/`** — abstraction layer for LLM providers
- **`agent/`** — core agent loop and message type definitions
- **`tui/`** — terminal user interface components
- **`coding-agent/`** — the CLI binary and interactive mode entry point

The monorepo includes an `AGENTS.md` with additional guidelines for contributors.
