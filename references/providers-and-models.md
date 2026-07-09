# Pi — Providers & Custom Models

Source: https://pi.dev/docs/latest/providers, /models, /custom-provider
Canonical env-var / auth.json-key list: `packages/ai/src/env-api-keys.ts` (`envMap`).

Pi knows all available models per provider; the list updates with every Pi release.

## Subscription providers (OAuth via `/login`)

- **ChatGPT Plus/Pro** — requires ChatGPT Plus/Pro; officially endorsed by OpenAI.
- **Claude Pro/Max (Anthropic)** — third-party harness usage draws from "extra usage", billed
  per token, not against plan limits (`warnings.anthropicExtraUsage` toggles the warning).
- **GitHub Copilot** — press Enter for github.com or enter a GitHub Enterprise Server domain.
  If "model not supported": enable it in VS Code (Copilot Chat → model selector → Enable).

`/logout` clears credentials. Tokens (API key **or** OAuth token) stored in `~/.pi/agent/auth.json`,
auto-refresh on expiry.

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
| Azure OpenAI Responses | `AZURE_OPENAI_API_KEY` | `azure-openai-responses` |
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
| NVIDIA NIM | `NVIDIA_API_KEY` | `nvidia` |
| Ant Ling | `ANT_LING_API_KEY` | `ant-ling` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` | `vercel-ai-gateway` |
| Cloudflare AI Gateway | `CLOUDFLARE_API_KEY` (+ ACCOUNT_ID, GATEWAY_ID) | `cloudflare-ai-gateway` |
| Cloudflare Workers AI | `CLOUDFLARE_API_KEY` (+ ACCOUNT_ID) | `cloudflare-workers-ai` |
| ZAI Coding Plan (Global) | `ZAI_API_KEY` | `zai` |
| ZAI Coding Plan (China) | `ZAI_CODING_CN_API_KEY` | `zai-coding-cn` |
| OpenCode Zen | `OPENCODE_API_KEY` | `opencode` |
| OpenCode Go | `OPENCODE_API_KEY` | `opencode-go` |
| Kimi For Coding | `KIMI_API_KEY` | `kimi-coding` |
| MiniMax | `MINIMAX_API_KEY` | `minimax` |
| MiniMax (China) | `MINIMAX_CN_API_KEY` | `minimax-cn` |
| Xiaomi MiMo | `XIAOMI_API_KEY` | `xiaomi` |
| Xiaomi MiMo Token Plan (CN/AMS/SGP) | `XIAOMI_TOKEN_PLAN_{CN,AMS,SGP}_API_KEY` | `xiaomi-token-plan-{cn,ams,sgp}` |

### `key` field formats

```json
{ "type": "api_key", "key": "!security find-generic-password -ws 'anthropic'" }  // shell cmd, stdout cached (process lifetime)
{ "type": "api_key", "key": "!op read 'op://vault/item/credential'" }            // shell cmd
{ "type": "api_key", "key": "${KEY_PREFIX}_${KEY_SUFFIX}" }                       // env-var interpolation inside a literal
{ "type": "api_key", "key": "MY_ANTHROPIC_KEY" }                                 // bare uppercase = env var reference
{ "type": "api_key", "key": "sk-ant-..." }                                       // literal
{ "type": "api_key", "key": "$$literal-dollar" }                                 // "$$" → literal "$"
{ "type": "api_key", "key": "$!literal-bang" }                                   // "$!" → literal "!" (skips cmd exec)
```

### Provider-scoped `env` (auth.json)

An `"env"` object inside a credential is applied **before process env vars** when resolving the key,
provider/model headers, and provider config (Cloudflare account IDs, Azure settings, Vertex
project/location, Bedrock settings, `PI_CACHE_RETENTION`, `HTTP_PROXY`/`HTTPS_PROXY`).

```json
{
  "cloudflare-ai-gateway": {
    "type": "api_key",
    "key": "$CLOUDFLARE_API_KEY",
    "env": {
      "CLOUDFLARE_API_KEY": "...",
      "CLOUDFLARE_ACCOUNT_ID": "account-id",
      "CLOUDFLARE_GATEWAY_ID": "gateway-id"
    }
  }
}
```

### Credential resolution order

1. CLI `--api-key` flag → 2. `auth.json` (incl. provider-scoped `env`) → 3. environment variable →
4. custom provider keys from `models.json`.

## Cloud providers

**Azure OpenAI**
```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_BASE_URL=https://your-resource.ai.azure.com   # or *.cognitiveservices/*.openai.azure.com; root → /openai/v1
# or instead of base URL:
export AZURE_OPENAI_RESOURCE_NAME=your-resource
export AZURE_OPENAI_API_VERSION=2024-02-01
export AZURE_OPENAI_DEPLOYMENT_NAME_MAP=gpt-4=my-gpt4,gpt-4o=my-gpt4o
```

**Amazon Bedrock**
```bash
export AWS_PROFILE=your-profile   # or AWS_ACCESS_KEY_ID+AWS_SECRET_ACCESS_KEY, AWS_BEARER_TOKEN_BEDROCK,
                                  # ECS task roles (AWS_CONTAINER_CREDENTIALS_*), or IRSA (AWS_WEB_IDENTITY_TOKEN_FILE)
export AWS_REGION=us-west-2
pi --provider amazon-bedrock --model us.anthropic.claude-sonnet-4-20250514-v1:0
export AWS_BEDROCK_FORCE_CACHE=1  # application inference profiles whose ARN lacks the model name
# Bedrock proxy: AWS_ENDPOINT_URL_BEDROCK_RUNTIME, AWS_BEDROCK_SKIP_AUTH, AWS_BEDROCK_FORCE_HTTP1
```

**Cloudflare AI Gateway** — uses `CLOUDFLARE_API_KEY` as `cf-aig-authorization`; routes to OpenAI
(`/openai`, native IDs e.g. `gpt-5.1`), Anthropic (`/anthropic`, e.g. `claude-sonnet-4-5`), Workers
AI (`/compat`, prefixed `workers-ai/@cf/...`). Upstream-auth modes: Workers AI, Unified billing,
Stored BYOK, Inline BYOK (needs an extra upstream `Authorization` header via models.json override).
```bash
export CLOUDFLARE_API_KEY=...; export CLOUDFLARE_ACCOUNT_ID=...; export CLOUDFLARE_GATEWAY_ID=...
pi --provider cloudflare-ai-gateway --model "claude-sonnet-4-5"
```

**Cloudflare Workers AI** (auto-sets `x-session-affinity` for prefix-cache discounts)
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

Reloads when you open `/model` (no restart). Provider-based structure. Custom models are
**upserted by ID**: a matching `id` replaces the built-in; a new `id` appends. Use `modelOverrides`
to tweak a built-in without redefining the provider.

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
`models`, `modelOverrides` (override built-ins: `name`, `reasoning`, `input`, `cost` partial,
`contextWindow`, `maxTokens`, `headers`, `compat`), provider-level `compat`.

**Model fields**: `id` (required) · `name` (default=id) · `reasoning` (false) ·
`input` (`["text"]` or `["text","image"]`) · `contextWindow` (128000) · `maxTokens` (16384) ·
`cost` (per-million; zeros) · per-model `baseUrl`/`headers` override.

`apiKey` resolution: `"!command"` (shell stdout, executed at request time — **no built-in TTL /
stale reuse / recovery**), env var name, or literal.

**Compatibility** (`compat`, provider- or model-level) — for limited OpenAI/Anthropic-compatible
servers:
```json
"compat": { "supportsDeveloperRole": false, "supportsReasoningEffort": false }
```
Other `compat` fields incl. (openai-completions) `supportsUsageInStreaming`, `maxTokensField`
(`max_completion_tokens`|`max_tokens`), `thinkingFormat`, `supportsStrictMode`, `supportsStore`,
`requiresToolResultName`, `cacheControlFormat`, `supportsLongCacheRetention`, `openRouterRouting`,
`vercelGatewayRouting`; (anthropic-messages) `supportsEagerToolInputStreaming`,
`sendSessionAffinityHeaders`, `supportsCacheControlOnTools`, `forceAdaptiveThinking`,
`allowEmptySignature`. `thinkingFormat` values: `reasoning_effort`/`openai`, `openrouter`,
`deepseek`, `together`, `zai`, `qwen`, `chat-template`, `qwen-chat-template`, `string-thinking`,
`ant-ling`.

**Thinking level mapping** (reasoning models): omitted = supported w/ default; string = specific
value; `null` = unsupported.
```json
"thinkingLevelMap": { "off": null, "minimal": null, "low": null, "medium": null, "high": "high", "xhigh": "max" }
```

**Override built-in provider** (route through a proxy; built-in models stay available):
```json
{ "providers": { "anthropic": { "baseUrl": "https://my-proxy.example.com/v1" } } }
```

**Per-model override with routing**:
```json
{ "providers": { "openrouter": { "modelOverrides": {
  "anthropic/claude-sonnet-4": {
    "name": "Claude Sonnet 4 (Bedrock Route)",
    "compat": { "openRouterRouting": { "only": ["amazon-bedrock"] } }
  } } } } }
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
`openai-codex-responses`, `azure-openai-responses`, `mistral-conversations`,
`google-generative-ai`, `google-vertex`, `bedrock-converse-stream`.

**OAuth** (`OAuthConfig`: `name`, `login()`, `refreshToken()`, `getApiKey()`, optional
`modifyModels(models, credentials)`). Callbacks:
```typescript
interface OAuthLoginCallbacks {
  onAuth(params: { url: string }): void;                                   // browser redirect
  onDeviceCode(params: { userCode; verificationUri; intervalSeconds?; expiresInSeconds? }): void;
  onPrompt(params: { message: string }): Promise<string>;                  // manual input
  onSelect(params: { message; options: { id; label }[] }): Promise<string | undefined>;
}
```
Store `OAuthCredentials` (`refresh`, `access`, `expires` ms) in `~/.pi/agent/auth.json`.

**Custom streaming** (`streamSimple()`): create an `AssistantMessageEventStream`, push `"start"`,
stream content blocks (text/thinking/tool-calls) with delta events tracked by `contentIndex`/`partial`,
finish with `"done"` (`reason: "stop"|"length"|"toolUse"`) or `"error"`.

**Context overflow**: normalize provider errors in a `message_end` handler so auto-compaction/retry
kick in (guard against double-tagging):
```javascript
pi.on("message_end", (event, ctx) => {
  const m = event.message;
  if (m.role !== "assistant" || m.stopReason !== "error") return;
  if (m.errorMessage?.includes("context_length_exceeded")) return;
  if (!MY_OVERFLOW_PATTERN.test(m.errorMessage ?? "")) return;
  return { message: { ...m, errorMessage: `context_length_exceeded: ${m.errorMessage}` } };
});
```

Example extension: `examples/extensions/custom-provider-gitlab-duo`.
