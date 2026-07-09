# Pi — TUI Components

Source: https://pi.dev/docs/latest/tui

Extensions and custom tools render interactive UIs through Pi's TUI component system. Primitives
come from `@earendil-works/pi-tui`; higher-level helpers and `ExtensionAPI` come from
`@earendil-works/pi-coding-agent`.

## Core interfaces

```typescript
interface Component {
  render(width: number): string[];      // each line must not exceed `width`
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;                    // called on theme change; rebuild pre-baked colors here
}
```

The TUI appends SGR + OSC resets after each line, so **styling must be reapplied per line**. After
state changes inside `handleInput`, call `tui.requestRender()`.

`Focusable` adds IME/cursor support (`CURSOR_MARKER`):

```typescript
import { CURSOR_MARKER, type Component, type Focusable } from "@earendil-works/pi-tui";
class MyInput implements Component, Focusable {
  focused = false;
  render(width: number): string[] {
    const marker = this.focused ? CURSOR_MARKER : "";
    return [`> ${beforeCursor}${marker}\x1b[7m${atCursor}\x1b[27m${afterCursor}`];
  }
  invalidate() {}
}
```

Container components must propagate `focused` to child `Input`s.

## Built-in components (`@earendil-works/pi-tui`)

- `Text(content, paddingX?, paddingY?, bgFn?)` — `.setText(s)`
- `Box(paddingX, paddingY, bgFn?)` — `.addChild()`, `.setBgFn()`
- `Container` — `.addChild()`, `.removeChild()`, `.clear()`
- `Spacer(n)`
- `Markdown(content, paddingX, paddingY, theme)` — `.setText()`
- `Image(base64, "image/png", theme, { maxWidthCells, maxHeightCells })` — terminals: Kitty, iTerm2,
  Ghostty, WezTerm, Warp
- `SelectList(items: SelectItem[], maxHeight, options?)` — `options` has `selectedPrefix`,
  `selectedText`, `description`, `scrollInfo`, `noMatch` (each `(t)=>string`); `.onSelect`, `.onCancel`
- `SettingsList(items: SettingItem[], maxHeight, theme, onValueChange, onClose, options?)` —
  `options: { enableSearch }`
- `Editor` — main input editor (Focusable)
- `Input` — text field (Focusable)

Types: `SelectItem = { value, label, description? }`; `SettingItem = { id, label, currentValue,
values: string[] }`.

## Helpers (`@earendil-works/pi-coding-agent`)

- `DynamicBorder((s) => theme.fg("accent", s))`
- `BorderedLoader(tui, theme, message)` — `.signal: AbortSignal`, `.onAbort`
- `CustomEditor` — base class to extend for custom editors (e.g. vim mode)
- `getMarkdownTheme()`, `getSettingsListTheme()`

## Utilities (`@earendil-works/pi-tui`)

- `matchesKey(data, key)`, `Key` class — `Key.enter/escape/tab/space/backspace/delete/home/end/
  up/down/left/right`; `Key.ctrl("c")`, `Key.shift("tab")`, `Key.alt("left")`, `Key.ctrlShift("p")`.
  `matchesKey(data, "escape")` also accepts a bare string.
- `visibleWidth(str)`, `truncateToWidth(str, width, ellipsis?)`, `wrapTextWithAnsi(str, width)`.

## `ctx.ui` / `pi.ui` API

```typescript
ctx.ui.custom(component, options?)        // → handle { close(), requestRender() }
ctx.ui.notify(message, type)              // "info" | "warning" | "error"
ctx.ui.setStatus(id, content?)            // footer status entry; undefined clears
ctx.ui.setWorkingMessage(text)            // or setWorkingIndicator({ frames, intervalMs })
ctx.ui.setWidget(id, content?, options?)  // options.placement: "aboveEditor" | "belowEditor"
ctx.ui.setFooter(renderer?)               // (tui, theme, footerData) => Component
ctx.ui.setEditorComponent(factory?)       // (tui, theme, keybindings) => CustomEditor
ctx.ui.setEditorText(text)
ctx.ui.theme                              // theme object
```

`custom()` factory signature: `(tui, theme, keybindings, done) => Component`. In tools, use
`pi.ui.custom(...)` inside `execute()`. `footerData` exposes `getGitBranch()` / `onBranchChange()`.

### Overlays

```typescript
ctx.ui.custom<T>(factory, { overlay: true, overlayOptions?, onHandle? });
```

`overlayOptions`: `width`/`minWidth`/`maxHeight` (number|string), `anchor` (`"center"`,
`"top-left"`, `"top-center"`, `"right-center"`, … 9 positions), `offsetX`/`offsetY`, `row`/`col`,
`margin` (number | `{top,right,bottom,left}`), `visible: (termW, termH) => boolean`.
`onHandle(handle)` → `handle.focus()`, `handle.unfocus({ target? })`, `handle.setHidden(bool)`,
`handle.hide()`. Overlay components are **disposed on close** — create fresh instances (re-call
`custom()` to re-show; don't cache the component).

## Theming

`theme.fg(color, text)`, `theme.bg(color, text)`, `theme.bold(text)`. Foreground keys mirror the
theme tokens (`text, accent, muted, dim, success, error, warning, border*, userMessageText,
tool*, mdHeading…, syntax*, thinking*, bashMode`); background keys: `selectedBg, userMessageBg,
customMessageBg, toolPendingBg, toolSuccessBg, toolErrorBg`. On theme change the TUI calls
`invalidate()` on all components — components that pre-bake theme colors must rebuild there. Always
use the theme from the callback, never an imported one.

## Custom-tool render hooks

`renderCall(...)` and `renderResult(result, options, theme, context)` may return TUI components:

```typescript
renderResult: (result) => new Text(theme.fg("success", "Done!"), 0, 0)
// or: new Markdown(result.details.markdown, 0, 0, getMarkdownTheme())
```

## Custom entry renderer

`pi.registerEntryRenderer(customType, renderer)` renders `custom` session entries in interactive mode.

## Patterns on the docs page

Worked examples: a custom `SelectList` command; `BorderedLoader` with abort; `SettingsList`;
`setStatus` / `setWorkingIndicator`; `setWidget` (array and renderer-function forms); `setFooter`
with git-branch data; and a full **`VimEditor extends CustomEditor`** (normal/insert modes) wired
via `ctx.ui.setEditorComponent` — the flagship example.

## Debug

- `PI_TUI_WRITE_LOG=/tmp/tui-ansi.log npx tsx packages/tui/test/chat-simple.ts` captures raw ANSI.
- Cache `render()` output keyed on width; clear the cache in `invalidate()`.
