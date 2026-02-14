# Proposal: Multi-Provider Configuration for Mem0

## What
Extend Mem0's configuration system to support multiple LLM and embedding providers (Ollama, Qwen/Dashscope, MiniMax, GLM/Zhipu) with provider-agnostic adapter logic.

## Why
**Current state:** Mem0 is configured to work exclusively with local Ollama (after fixes in commits 77b542a, f74a309, 80ce909 on `development` branch):
- Embedder: Uses OpenAI-compatible endpoint pointed at Ollama (`http://localhost:11434/v1`)
- LLM: Uses LiteLLM with hardcoded `ollama/llama3.2:3b` model string
- Environment: Sets `OLLAMA_API_BASE` for LiteLLM routing
- Hardcoded logic in `core/memory/mem0_adapter.py` lines 104-150

**Problem:**
1. **Provider lock-in:** Cannot switch to cloud providers (Qwen, MiniMax, GLM) without code changes
2. **Hardcoded assumptions:** Lines 104-105 assume `models.local.embedding_model`, lines 120-127 assume Ollama
3. **Mixed configuration sources:** Some settings from config.yaml, others hardcoded in adapter
4. **Limited extensibility:** Adding new provider requires editing adapter logic

**Solution:** Make `Mem0Adapter._build_mem0_config()` read provider settings from config.yaml and dynamically construct:
- Embedder configuration based on provider type (ollama, qwen, minimax, glm)
- LLM model strings with provider prefix for LiteLLM (`ollama/`, `dashscope/`, `minimax/`, `zhipuai/`)
- Provider-specific API endpoints and authentication

**Benefits:**
1. **Zero-code provider switching:** Change config.yaml, restart server
2. **Future-proof architecture:** Supports Polly's multi-provider vision
3. **Better separation of concerns:** Configuration vs. implementation
4. **Consistent with existing systems:** RAG and router already support multiple providers

## Scope

### Backend (Python)
- **Modified:** `core/memory/mem0_adapter.py` (lines 92-135)
  - Replace hardcoded `models.local.embedding_model` with configurable provider lookup
  - Build embedder config dynamically based on `memory.mem0.embedding_provider`
  - Build LLM model string dynamically based on `memory.mem0.llm_provider`
  - Support provider-specific environment variables

### Configuration
- **Modified:** `config/config.yaml`
  - Restructure `memory.mem0` section with explicit provider fields:
    ```yaml
    memory:
      mem0:
        enabled: true
        embedding_provider: "ollama"  # ollama, qwen, minimax, glm
        llm_provider: "ollama"         # ollama, qwen, minimax, glm
        providers:
          ollama:
            host: "http://localhost:11434"
            embedding_model: "nomic-embed-text"
            llm_model: "llama3.2:3b"
          qwen:
            api_key_env: "DASHSCOPE_API_KEY"
            embedding_model: "text-embedding-v3"
            llm_model: "qwen-turbo"
          # ... similar for minimax, glm
    ```

### Frontend
- **No changes:** This is purely backend configuration

### Related Phase
- **Phase 1.5 (Core Intelligence):** Enhances existing Mem0 integration
- **Phase 11 (Multi-Provider System):** Aligns with Polly's multi-provider architecture

## Migration Strategy
1. **Phase 1:** Add new config structure to `config.yaml` (backward compatible)
2. **Phase 2:** Refactor `_build_mem0_config()` to read from new config structure
3. **Phase 3:** Test with Ollama (current provider)
4. **Phase 4:** Add provider-specific configurations for Qwen, MiniMax, GLM
5. **Phase 5:** Document provider setup in README

## Success Criteria
1. Mem0 works with Ollama using new config structure (no regression)
2. Can switch to Qwen by changing config.yaml only
3. Can switch to MiniMax by changing config.yaml only
4. Can switch to GLM by changing config.yaml only
5. All provider-specific settings in config.yaml (zero hardcoding)

## Non-Goals
- Changing Mem0's internal API or behavior
- Adding new embedding/LLM providers beyond the 4 listed
- Frontend UI for provider switching (defer to future phase)
- Automatic provider fallback/failover (handled by router)
