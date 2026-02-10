# Archived provider adapters (legacy)

These per-provider adapters are **kept for reference** when `routing_v2.use_litellm` is `false`. When `use_litellm` is `true`, Polly uses the unified **LiteLLM** adapter (`core/providers/litellm_adapter.py`) for all providers.

- `anthropic_provider.py` — AnthropicAdapter (Claude)
- `openai_provider.py` — OpenAIAdapter (GPT)
- `github_provider.py` — GitHubModelsAdapter
- `grok_provider.py` — GrokAdapter (xAI)
- `perplexity_provider.py` — PerplexityAdapter
- `gemini_provider.py` — GeminiAdapter
- `mistral_provider.py` — MistralAdapter

Imports: use `from core.providers import AnthropicAdapter, ...` or `from core.providers.archive.anthropic_provider import AnthropicAdapter`.
