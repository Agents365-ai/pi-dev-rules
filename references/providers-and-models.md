# Pi — Providers & Custom Models

Source: https://pi.dev/docs/latest/providers, /models, /custom-provider

Pi knows all available models per provider; the list updates with every Pi release.

## Subscription providers (OAuth via `/login`)

- **ChatGPT Plus/Pro (Codex)** — requires ChatGPT Plus/Pro; officially endorsed by OpenAI.
- **Claude Pro/Max (Anthropic)** — third-party harness usage draws from "extra usage", billed
  per token, not against plan limits.
- **GitHub Copilot** — press Enter for github.com or enter a GitHub Enterprise Server domain.
  If "model not supported": enable it in VS Code (Copilot Chat → model selector → Enable).

`/logout` clears credentials. Tokens stored in `~/.pi/agent/auth.json`, auto-refresh on expiry.

## API-key providers

Set an env var, or store in `~/.pi/agent/auth.json` (chmod `0600`). **`auth.json` wins over env vars.**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "openai":    { "type": "api_key", "key": "sk-..." },
  "deepseek":  { "type": "api_key", "key": "sk-..." },
  "google":    { "type": "api_key", "key": "..." }
}
```

| Provider | Env var | `auth.json` key |
|----------|---------|-----------------|
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic` |
| OpenAI | `OPENAI_API_KEY` | `openai` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek` |
| Google Gemini | `GEMINI_API_KEY` | `google` |
| Mistral | `MISTRAL_API_KEY` | `mistral` |
| Groq | `GROQ_API_KEY` | `groq` |
| Cerebras | `CEREBRAS_API_KEY` | `cerebras` |
| xAI | `XAI_API_KEY` | `xai` |
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter` |
| Together AI | `TOGETHER_API_KEY` | `together` |
| Hugging Face | `HF_TOKEN` | `huggingface` |
| Fireworks | `FIREWORKS_API_KEY` | `fireworks` |

### `key` field formats

```json
{ "type": "api_key", "key": "!security find-generic-password -ws 'anthropic'" }  // shell cmd, stdout cached
{ "type": "api_key", "key": "!op read 'op://vault/item/credential'" }            // shell cmd
{ "type": "api_key", "key": "MY_ANTHROPIC_KEY" }                                 // env var reference
{ "type": "api_key", "key": "sk-ant-..." }                                       // literal
```

### Credential resolution order

1. CLI `--api-key` flag → 2. `auth.json` → 3. environment variable →
4. custom provider keys from `models.json`.

## Cloud providers

**Azure OpenAI**
```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com
export AZURE_OPENAI_API_VERSION=2024-02-01
export AZURE_OPENAI_DEPLOYMENT_NAME_MAP=gpt-4=my-gpt4,gpt-4o=my-gpt4o
```

**Amazon Bedrock**
```bash
export AWS_PROFILE=your-profile          # or AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY, or AWS_BEARER_TOKEN_BEDROCK
export AWS_REGION=us-west-2
pi --provider amazon-bedrock --model us.anthropic.claude-sonnet-4-20250514-v1:0
export AWS_BEDROCK_FORCE_CACHE=1         # for application inference profiles
```

**Cloudflare AI Gateway**
```bash
export CLOUDFLARE_API_KEY=...; export CLOUDFLARE_ACCOUNT_ID=...; export CLOUDFLARE_GATEWAY_ID=...
pi --provider cloudflare-ai-gateway --model "claude-sonnet-4-5"
```

**Cloudflare Workers AI**
```bash
export CLOUDFLARE_API_KEY=...; export CLOUDFLARE_ACCOUNT_ID=...
pi --provider cloudflare-workers-ai --model "@cf/moonshotai/kimi-k2.6"
```

**Google Vertex AI**
```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1
# or: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

## Custom models — `~/.pi/agent/models.json`

Reloads when you open `/model` (no restart). Provider-based structure.

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        {
          "id": "llama3.1:8b",
          "name": "Llama 3.1 8B (Local)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000,
          "cost": { "input": 0, "output": 0 }
        }
      ]
    }
  }
}
```

**API types**: `openai-completions` (most compatible), `openai-responses`,
`anthropic-messages`, `google-generative-ai`.

**Provider fields**: `baseUrl`, `api`, `apiKey`, `headers`, `authHeader` (auto Bearer when true),
`models`, `modelOverrides` (customize built-ins).

**Model fields**: `id` (required) · `name` (default=id) · `reasoning` (false) ·
`input` (`["text"]` or `["text","image"]`) · `contextWindow` (128000) · `maxTokens` (16384) ·
`cost` (per-million; zeros).

`apiKey` resolution: `"!command"` (shell stdout, executed at request time — **no built-in TTL /
stale reuse / recovery**), env var name, or literal.

**Compatibility** (limited OpenAI-compatible servers), provider- or model-level:
```json
"compat": { "supportsDeveloperRole": false, "supportsReasoningEffort": false }
```

**Thinking level mapping** (reasoning models): omitted = supported w/ default; string = specific
value; `null` = unsupported.
```json
"thinkingLevelMap": { "off": null, "minimal": null, "low": null, "medium": null, "high": "high", "xhigh": "max" }
```

**Override built-in provider** (route through a proxy; built-in models stay available):
```json
{ "providers": { "anthropic": { "baseUrl": "https://my-proxy.example.com/v1" } } }
```

## Custom-provider extensions

Use `pi.registerProvider()` in an extension for proxies, self-hosted, OAuth/SSO, or non-standard APIs.

```javascript
pi.registerProvider("anthropic", { baseUrl: "https://proxy.example.com" });   // override
pi.registerProvider("my-provider", {                                          // new
  name: "My Provider", baseUrl: "https://api.example.com",
  apiKey: "MY_API_KEY", api: "openai-completions", models: [/* ... */]
});
pi.unregisterProvider("my-llm");                                              // remove
```

**API types**: `anthropic-messages`, `openai-completions`, `openai-responses`,
`mistral-conversations`, `google-generative-ai`, `bedrock-converse-stream`.

**OAuth callbacks**: `onAuth` (browser redirect), `onDeviceCode` (device code), `onPrompt`
(manual input). Store refresh/access token + expiry in `~/.pi/agent/auth.json`.

**Custom streaming** (`streamSimple()`): create an `AssistantMessageEventStream`, push `"start"`,
stream content blocks (text/thinking/tool-calls) with delta events tracked by index, finish with
`"done"` or `"error"`.

**Context overflow**: normalize provider errors in a `message_end` handler so auto-compaction/retry
kick in:
```javascript
pi.on("message_end", (event, ctx) => {
  if (message.errorMessage?.match(YOUR_PATTERN))
    return { message: { ...message, errorMessage: `context_length_exceeded: ${errorMessage}` } };
});
```
