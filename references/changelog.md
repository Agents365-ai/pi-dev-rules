# Pi — Changelog

Source: <https://pi.dev/news> · RSS: `https://pi.dev/news.xml`

A reverse-chronological release-notes feed. Fetched from the RSS feed.

---

**Cadence**: Pi ships releases every 1–3 days. Run `bash scripts/refresh.sh`
to refresh both the package catalog and this changelog.

## Recent releases

| Version | Date | Highlights |
| --------- | ------ | ----------- |
| **0.80.9** | 2026-07-16 | New Features: Kimi K3 and deferred tool loading — Use Kimi K3 across built-in providers, including progressive extension |
| **0.80.8** | 2026-07-16 | New Features: Unified model runtime and provider authentication — ModelRuntime centralizes model configuration, provider |
| **0.80.10** | 2026-07-16 | New Features: Kimi Coding thinking compatibility — Kimi Coding models now use adaptive thinking correctly; K3 exposes it |
| **0.80.7** | 2026-07-14 | Breaking Changes: Removed the openai-responses compat.sendSessionIdHeader flag from models.json. Session-affinity behavi |
| **0.80.6** | 2026-07-09 | New Features: max thinking level - New opt-in thinking level above xhigh, natively supported on GPT-5.6 and adaptive Cla |
| **0.80.4** | 2026-07-09 | New Features: Prompt cache miss visibility - Significant cache misses can be shown in transcripts via showCacheMissNotic |
| **0.80.3** | 2026-06-30 | New Features: Anthropic Claude Sonnet 5 support - Claude Sonnet 5 is available through inherited Anthropic-compatible an |
| **0.80.2** | 2026-06-23 | Changed: Changed inherited pi-ai ApiKeyCredential to use the auth.json-compatible discriminator type: "api_key" and prov |
| **0.80.1** | 2026-06-23 | Release notes for Pi 0.80.1. |
| **0.80.0** | 2026-06-23 | Changed: Added Ctrl+J as a default newline keybinding alongside Shift+Enter.; Fixed: Fixed session names to normalize ne |
| **0.79.10** | 2026-06-22 | New Features: Extension compaction event context - Extension session_before_compact and session_compact events now inclu |
| **0.79.9** | 2026-06-20 | New Features: Chat-template thinking compatibility - OpenAI-compatible custom providers can map Pi thinking levels into  |
| **0.79.8** | 2026-06-19 | New Features: Selective provider base entry points - SDK users can pair @earendil-works/pi-ai/base and @earendil-works/p |
| **0.79.7** | 2026-06-18 | New Features: Automatic theme mode - /settings can choose separate light and dark themes and follow terminal color-schem |
| **0.79.6** | 2026-06-16 | Release notes for Pi 0.79.6. |
| **0.79.5** | 2026-06-16 | New Features: Provider-scoped API key environments - auth.json API key entries can now include env overrides for provide |
| **0.79.4** | 2026-06-15 | New Features: Automatic first-run theme selection - pi detects the terminal background on first run and defaults to the  |
| **0.79.3** | 2026-06-13 | Release notes for Pi 0.79.3. |
| **0.79.2** | 2026-06-12 | New Features: Clearer Bedrock validation guidance - Amazon Bedrock data retention validation errors now link to AWS data |
| **0.79.1** | 2026-06-09 | New Features: Claude Fable 5 - Claude Fable 5 is now available on the Anthropic and Amazon Bedrock providers, with adapt |

---

## Fetch live

```bash
curl -s 'https://pi.dev/news.xml'
```
