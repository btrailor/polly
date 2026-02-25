# Proposal: Context Distillation Layer

## What
Add a context distillation layer that compresses RAG results, gathered context, and conversation history through a local Ollama model before sending to expensive cloud LLMs. This reduces input token consumption on every cloud-routed call while preserving semantic quality.

This is **Phase 1** of a four-phase Copilot integration and token conservation plan.

## Why
**Current state:** When Polly routes a query to a cloud provider (Anthropic, OpenAI, Gemini, etc.), the full system prompt includes:
- Formatted RAG results (up to 10-20 search results, each potentially thousands of characters)
- Gathered context (mental models, entity context, pattern engine, compression summaries)
- Domain-specific prompt injections
- Conversation history (up to 20 exchanges before compression triggers)
- Constitutional epistemology layer and persona prompts

A typical cloud call can easily consume **8,000-15,000 input tokens** — most of which is context, not the user's actual query.

**Problem:**
1. **Excessive input tokens:** RAG results often contain redundant or low-value chunks that inflate cost
2. **Context dilution:** More context doesn't always mean better answers — large contexts can confuse models
3. **No pre-processing:** Context goes directly from RAG to cloud LLM with no intermediate filtering or summarization
4. **Existing compression is limited:** LLMLingua (BERT-based) compresses individual chunks but doesn't perform semantic distillation — it removes tokens algorithmically, not intelligently
5. **Local models underutilized:** Ollama models (llama3.2:3b, llama3.1:7b) sit idle during cloud calls when they could be compressing context

**Solution:** A distillation layer that:
- Takes the assembled context (RAG results + gathered context) after formatting
- Passes it through a fast local Ollama model (llama3.2:3b) with a distillation prompt
- Produces a compressed summary that preserves key facts, code snippets, and actionable information
- Replaces the raw context in the system prompt before cloud routing
- Tracks compression ratios and token savings in AutonomyMetrics

**Benefits:**
1. **40-60% input token reduction:** Distilling 8K tokens of context to 3-4K tokens (configurable ratio)
2. **Improved response quality:** Distilled context is denser and more focused — less noise for the cloud model
3. **Near-zero marginal cost:** Ollama models run locally with no per-token charges
4. **200-400ms overhead:** Local inference on llama3.2:3b is fast (~200ms for distillation of typical context)
5. **Stacks with Phase 0 cache:** Cache hits skip distillation entirely; cache misses get distilled before cloud call
6. **Uses existing infrastructure:** Ollama is already running for local routing; no new dependencies

## Scope

### Backend (Python)
- **New file:** `core/context_distiller.py` (~200 lines) — ContextDistiller class with singleton pattern
- **New file:** `core/compression/ollama_strategy.py` (~150 lines) — OllamaDistillStrategy implementing existing compression interface
- **Modified:** `core/polly.py` — Distillation step between context assembly (~L2011) and router call (~L2140)
- **Modified:** `core/compression/compressor.py` — Register `"ollama_distill"` strategy alongside `"llmlingua"` and `"llm_summary"`
- **Modified:** `core/compression/manager.py` — Add distillation-specific configuration and method
- **Modified:** `core/config.py` — Add `context_distillation` to DEFAULT_CONFIG
- **Modified:** `config.yaml` — Add `context_distillation:` configuration section
- **Modified:** `core/autonomy_metrics.py` — Track distillation stats (tokens saved, compression ratios)
- **Modified:** `interfaces/server.py` — Add `GET /polly/distillation/stats` endpoint
- **Modified:** `interfaces/settings_api.py` — Add distillation settings endpoints

### Frontend (Electron)
- **Modified:** `electron-app/src/renderer/index.html` — Distillation toggle + ratio slider in AI Features section
- **Modified:** `electron-app/src/renderer/app.js` — Load/save distillation settings

### No New Dependencies
- Uses existing Ollama connection (already running for local routing)
- Implements existing `CompressionResult` interface from `core/compression/llmlingua_strategy.py`
- No new pip packages required

## Four-Phase Roadmap Context

| Phase | Name | Purpose | Status |
|-------|------|---------|--------|
| 0 | Semantic Response Cache | System-wide query dedup + token savings tracking | Specced |
| **1** | **Context Distillation Layer** | **Local Ollama compresses context before cloud calls** | **This proposal** |
| 2 | GitHub Copilot Completions API | Native FIM for inline code completion | Planned |
| 3 | Programmer Persona + Code Routing | Modes: complete/explain/refactor/generate/debug/review | Planned |

Phase 1 sits between Phase 0 (cache) and Phase 2 (Copilot). On a cache miss, the context distillation layer reduces the tokens sent to cloud models. When Copilot FIM is added in Phase 2, distillation can also compress the code context window before sending to Copilot.

## Non-Goals
- Replacing LLMLingua compression (LLMLingua handles per-chunk compression; distillation handles assembled context)
- Distilling local Ollama responses (local calls are already cheap)
- Distilling the user's query (queries are short and must be preserved verbatim)
- Distilling persona/constitutional prompts (these are fixed-length and carefully authored)
- Running distillation on cache hits (Phase 0 cache already returns the complete response)
