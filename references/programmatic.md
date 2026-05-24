# Pi — Programmatic Usage (SDK, RPC, JSON)

Source: https://pi.dev/docs/latest/sdk, /rpc, /json

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

const { session } = await createAgentSession({
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

**AgentSession**: `prompt(text)`, `steer(text)`, `followUp(text)`, `subscribe(listener)`,
`setModel(model)`, `abort()`. **AgentSessionRuntime** handles session replacement (new/switch/fork).

**Model selection**
```javascript
import { getModel } from "@earendil-works/pi-ai";
const model = getModel("anthropic", "claude-opus-4-5");
const { session } = await createAgentSession({ model, thinkingLevel: "medium" });
```

**Tools** — built-ins: `read, bash, edit, write, grep, find, ls`.
```javascript
const { session } = await createAgentSession({ tools: ["read", "bash", "grep"] });
```

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

**Session management**
```javascript
SessionManager.inMemory()                  // no persistence
SessionManager.create(process.cwd())       // persistent
SessionManager.continueRecent(process.cwd())
SessionManager.open("/path/to/session.jsonl")
```

**Events**: `message_update` (text/thinking deltas), `tool_execution_start`, `agent_end`, …

**Run modes**: `InteractiveMode` (full TUI), `runPrintMode` (single-shot), `runRpcMode`
(JSON-RPC subprocess). Each needs an `AgentSessionRuntime` first.

**Settings**
```javascript
import { SettingsManager } from "@earendil-works/pi-coding-agent";
const settingsManager = SettingsManager.inMemory({ compaction: { enabled: false }, retry: { maxRetries: 2 } });
const { session } = await createAgentSession({ settingsManager });
```

**API keys** — priority: runtime overrides → `auth.json` → env vars → fallback resolver.
```javascript
authStorage.setRuntimeApiKey("anthropic", "sk-temp-key");
```

---

## RPC mode

```bash
pi --mode rpc [--provider ... --model ... --no-session --session-dir ...]
```

JSON Lines over stdin/stdout. Commands → stdin (one JSON object per line); responses are JSON with
`type: "response"`; events stream to stdout as JSON lines. Each command may carry an `id` for
correlation.

**Framing**: split on `\n` only, strip trailing `\r`; do **not** use generic readers that treat
Unicode separators as newlines.

**Commands**
- Prompting: `prompt` (text + optional images, streaming control), `steer` (queue mid-run,
  delivered after tool calls), `follow_up` (queue for after completion), `abort`.
- State: `get_state`, `get_messages`, `set_session_name`.
- Model: `set_model`, `cycle_model`, `get_available_models`, `set_thinking_level`.
- Execution: `bash` (run + add to context), `compact`, `set_auto_compaction`.

**Events**: `agent_start|end`, `turn_start|end`, `message_update`, `tool_execution_*`,
`queue_update`, `compaction_*`.

**Extension UI protocol**: `select`, `confirm`, `input`, `editor` (need a response with matching
`id`); fire-and-forget: `notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`.

**Message types**: `UserMessage` `{"role":"user","content":"...","timestamp":...}`,
`AssistantMessage` (text + thinking + tool calls + usage), `ToolResultMessage`,
`BashExecutionMessage` (from RPC `bash`, not LLM tool calls).

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

**Event types**: session-level (`queue_update`, `compaction_start|end`, `auto_retry_start|end`),
`agent_start|end`, `turn_start|end` (turn_end includes tool results), `message_start|update|end`,
`tool_execution_start|update|end`.

**Message types**: `UserMessage`, `AssistantMessage`, `ToolResultMessage`, plus
`BashExecutionMessage`, `CustomMessage`, `BranchSummaryMessage`, `CompactionSummaryMessage`.

```bash
pi --mode json "List files" 2>/dev/null | jq -c 'select(.type == "message_end")'
```
