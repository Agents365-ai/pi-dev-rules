# Pi — Programmatic Usage (SDK, RPC, JSON)

Source: https://pi.dev/docs/latest/sdk, /rpc, /json
See also: `session-format.md` (session schema), `tui-components.md` (custom UI).

---

## SDK

```bash
npm install @earendil-works/pi-coding-agent
```

```javascript
import { AuthStorage, createAgentSession, ModelRegistry, SessionManager }
  from "@earendil-works/pi-coding-agent";

const authStorage   = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

const { session } = await createAgentSession({          // returns { session, extensionsResult, modelFallbackMessage? }
  sessionManager: SessionManager.inMemory(),
  authStorage, modelRegistry,
});

session.subscribe((event) => {
  if (event.type === "message_update" &&
      event.assistantMessageEvent.type === "text_delta")
    process.stdout.write(event.assistantMessageEvent.delta);
});

await session.prompt("What files are in the current directory?");
```

**Factories**: `createAgentSession(options)`, `createAgentSessionRuntime(factory, options)`,
`createAgentSessionFromServices(options)`, `createAgentSessionServices(options)`.

**`createAgentSession` options**: `model`, `thinkingLevel` (`off|minimal|low|medium|high|xhigh`),
`scopedModels` (`Array<{model, thinkingLevel}>`), `tools`, `noTools` (`"all"|"builtin"`),
`excludeTools` (`string[]`), `customTools`, `authStorage`, `modelRegistry`, `sessionManager`,
`settingsManager`, `resourceLoader`, `cwd`, `agentDir`.

**AgentSession** — methods: `prompt(text, PromptOptions?)`, `steer(text)`, `followUp(text)`,
`subscribe(listener)`, `setModel(model)`, `setThinkingLevel(level)`, `cycleModel()`,
`cycleThinkingLevel()`, `navigateTree(targetId, options?)`, `compact(customInstructions?)`,
`abortCompaction()`, `abort()`, `dispose()`. Properties: `sessionFile?`, `sessionId`, `agent`,
`model?`, `thinkingLevel`, `messages`, `isStreaming`. `PromptOptions`: `expandPromptTemplates?`,
`images?`, `streamingBehavior?` (`"steer"|"followUp"`), `source?`, `preflightResult?`.

**AgentSessionRuntime** handles session replacement — `newSession()`, `switchSession(path)`,
`fork(entryId, { position? })`, `importFromJsonl(data)`; properties `session`, `services`, `diagnostics`.

**Model selection**
```javascript
import { getModel } from "@earendil-works/pi-ai";
const model = getModel("anthropic", "claude-opus-4-5");
const { session } = await createAgentSession({ model, thinkingLevel: "medium" });
```
`ModelRegistry`: `create(authStorage)`, `inMemory(authStorage)`, `find(provider, modelId)`,
`getAvailable()`; helpers `resolveCliModel({ cliModel, modelRegistry })`,
`resolveModelScopeWithDiagnostics(models, registry)`.

**Tools** — built-ins: `read, bash, edit, write, grep, find, ls`.
```javascript
const { session } = await createAgentSession({ tools: ["read", "bash", "grep"] });
```
Tool creators: `createCodingTools(cwd)`, `createReadOnlyTools(cwd)`,
`create{Read,Bash,Edit,Write,Grep,Find,Ls}Tool(cwd)`.

**Custom tools**
```javascript
import { Type } from "typebox";
import { defineTool } from "@earendil-works/pi-coding-agent";
const myTool = defineTool({
  name: "my_tool", description: "Does something useful",
  parameters: Type.Object({ input: Type.String() }),
  execute: async (_id, params) => ({ content: [{ type: "text", text: `Result: ${params.input}` }], details: {} }),
});
const { session } = await createAgentSession({ customTools: [myTool] });
```

**Extensions & skills**
```javascript
import { DefaultResourceLoader } from "@earendil-works/pi-coding-agent";
const loader = new DefaultResourceLoader({ additionalExtensionPaths: ["/path/to/extension.ts"] });
await loader.reload();
const { session } = await createAgentSession({ resourceLoader: loader });
```
Getters: `getExtensions()`, `getSkills()`, `getPrompts()`, `getThemes()`, `getAgentsFiles()`.
Options include `systemPromptOverride`, `extensionFactories`, `skillsOverride`, `promptsOverride`,
`agentsFilesOverride`, `eventBus` (see `createEventBus()`).

**Session management**
```javascript
SessionManager.inMemory()                  // no persistence
SessionManager.create(process.cwd())       // persistent
SessionManager.continueRecent(process.cwd())
SessionManager.open("/path/to/session.jsonl")
```

**Helpers/constants**: `getAgentDir()`, `getPackageDir()`, `getReadmePath()`, `getDocsPath()`,
`getExamplesPath()`, `CONFIG_DIR_NAME = ".pi"`.

**Events** (`session.subscribe`): `message_start|update|end` (text/thinking deltas),
`tool_execution_start|update|end`, `turn_start|end`, `agent_start|end`, `queue_update`,
`compaction_start|end`, `auto_retry_start|end`.

**Run modes**: `InteractiveMode` (full TUI; opts `{ migratedProviders, modelFallbackMessage?,
initialMessage?, initialImages?, initialMessages? }` + `.run()`), `runPrintMode(runtime,
{ mode: "text"|"json", initialMessage, initialImages?, messages? })`, `runRpcMode(runtime)`.
Each needs an `AgentSessionRuntime` first.

**Settings**
```javascript
import { SettingsManager } from "@earendil-works/pi-coding-agent";
const settingsManager = SettingsManager.inMemory({ compaction: { enabled: false }, retry: { maxRetries: 2 } });
const { session } = await createAgentSession({ settingsManager });
```
Also `SettingsManager.create(cwd?, agentDir?)`, `applyOverrides(overrides)`, `flush()`, `drainErrors()`.

**API keys** — priority: runtime overrides → `auth.json` → env vars → fallback resolver.
```javascript
authStorage.setRuntimeApiKey("anthropic", "sk-temp-key");
```

---

## RPC mode

```bash
pi --mode rpc [--provider ... --model ... --name ... --no-session --session-dir ...]
```

JSON Lines over stdin/stdout. Commands → stdin (one JSON object per line); responses are JSON with
`type: "response"`; events stream to stdout as JSON lines. Each command may carry an `id` for
correlation.

**Framing**: split on `\n` only, strip trailing `\r`; do **not** use generic readers that treat
Unicode separators as newlines.

**Commands**
- Prompting: `prompt` (text + optional images, streaming control), `steer` (queue mid-run,
  delivered after tool calls), `follow_up` (queue for after completion), `abort`.
- Sessions: `new_session`, `switch_session`, `fork`, `clone`, `get_fork_messages`,
  `get_entries` (cursor-based), `get_tree`, `get_session_stats`, `set_session_name`, `export_html`.
- State: `get_state`, `get_messages`, `get_last_assistant_text`, `get_commands`.
- Model: `set_model`, `cycle_model`, `get_available_models`, `set_thinking_level`, `cycle_thinking_level`.
- Delivery: `set_steering_mode` (`all`|`one-at-a-time`), `set_follow_up_mode`.
- Execution: `bash` (run + add to context), `abort_bash`, `compact`, `set_auto_compaction`,
  `set_auto_retry`, `abort_retry`.

**Events**: `agent_start|end`, `turn_start|end`, `message_start|update|end`, `tool_execution_*`,
`queue_update`, `compaction_*`, `auto_retry_start|end`, `extension_error`
(`extensionPath`, `event`, `error`). `message_update` delta discriminators: `start`,
`text_start|delta|end`, `thinking_start|delta|end`, `toolcall_start|delta|end`, `done`
(`reason: stop|length|toolUse`), `error` (`reason: aborted|error`).

**Extension UI protocol**: requests `{"type":"extension_ui_request","id","method"}`; responses
`{"type":"extension_ui_response","id","value"|"confirmed"|"cancelled"}`. Interactive: `select`,
`confirm`, `input`, `editor`. Fire-and-forget: `notify`, `setStatus`, `setWidget`
(`widgetPlacement: aboveEditor|belowEditor`), `setTitle`, `set_editor_text`.

**Message types**: `UserMessage` `{"role":"user","content":"...","timestamp":...}`,
`AssistantMessage` (text + thinking + tool calls + usage), `ToolResultMessage`,
`BashExecutionMessage` (from RPC `bash`, not LLM tool calls). Full `Model` and `Attachment`
(`id,type,fileName,mimeType,size,content,extractedText,preview`) objects are documented on the page.

**Error**: `{"type":"response","command":"...","success":false,"error":"description"}`.

```python
send({"type": "prompt", "message": "Hello!"})
for event in read_events():
    if event.get("type") == "message_update":
        delta = event.get("assistantMessageEvent", {})
        if delta.get("type") == "text_delta":
            print(delta["delta"], end="")
```

---

## JSON event-stream mode

```bash
pi --mode json "Your prompt"
```

Outputs all session events as JSON lines to stdout. First line is a session header:

```json
{"type":"session","version":3,"id":"uuid","timestamp":"...","cwd":"/path"}
```

**Event types**: session-level (`queue_update`, `compaction_start|end` — `end` includes `result`,
`aborted`, `willRetry`, `errorMessage` —, `auto_retry_start|end`), `agent_start|end`,
`turn_start|end` (turn_end includes tool results), `message_start|update|end`,
`tool_execution_start|update|end`.

**Message types**: `UserMessage`, `AssistantMessage`, `ToolResultMessage`, plus
`BashExecutionMessage`, `CustomMessage`, `BranchSummaryMessage`, `CompactionSummaryMessage`
(see `session-format.md`).

```bash
pi --mode json "List files" 2>/dev/null | jq -c 'select(.type == "message_end")'
```
