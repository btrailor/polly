# Design: Multi-Provider Configuration for Mem0

## Architecture Overview

### Current Architecture (Post-Fix)

```
config.yaml (models.local.*)
    ↓
Mem0Adapter._build_mem0_config()
    ↓ (hardcoded logic)
├─→ Embedder: OpenAI provider @ http://localhost:11434/v1
│   Model: nomic-embed-text
│   
└─→ LLM: LiteLLM provider
    Model: ollama/llama3.2:3b
    Env: OLLAMA_API_BASE=http://localhost:11434
```

**Issues:**
- Lines 104-105: `mem0_config.get('models', {}).get('local', {})` assumes Ollama
- Lines 120-127: Hardcoded `provider: "litellm"`, `model: "ollama/llama3.2:3b"`
- Lines 140-150: Only Ollama configuration path exists

### Proposed Architecture

```
config.yaml (memory.mem0.providers.*)
    ↓
Mem0Adapter._build_mem0_config()
    ↓ (dynamic provider resolution)
    ↓
ProviderConfigBuilder
    ↓ (match provider type)
    ├─→ OllamaConfigBuilder
    │   ├─→ Embedder: OpenAI @ /v1 endpoint
    │   └─→ LLM: LiteLLM (ollama/...)
    │
    ├─→ QwenConfigBuilder
    │   ├─→ Embedder: Dashscope native
    │   └─→ LLM: LiteLLM (dashscope/...)
    │
    ├─→ MiniMaxConfigBuilder
    │   ├─→ Embedder: OpenAI-compatible
    │   └─→ LLM: LiteLLM (minimax/...)
    │
    └─→ GLMConfigBuilder
        ├─→ Embedder: Zhipu native
        └─→ LLM: LiteLLM (zhipuai/...)
```

## Configuration Schema

### New config.yaml Structure

```yaml
memory:
  provider: "mem0"
  mem0:
    enabled: true
    
    # Provider selection
    embedding_provider: "ollama"  # Which provider to use for embeddings
    llm_provider: "ollama"        # Which provider to use for LLM (entity extraction)
    
    # Vector store (unchanged)
    vector_store: "chroma"
    collections:
      knowledge: "polly_mem0_memories"
    
    # Provider-specific configurations
    providers:
      ollama:
        host: "http://localhost:11434"
        embedding_model: "nomic-embed-text"
        llm_model: "llama3.2:3b"
        temperature: 0.0
      
      qwen:
        api_key_env: "DASHSCOPE_API_KEY"  # Environment variable name
        embedding_model: "text-embedding-v3"
        llm_model: "qwen-turbo"
        temperature: 0.0
      
      minimax:
        api_key_env: "MINIMAX_API_KEY"
        group_id_env: "MINIMAX_GROUP_ID"
        embedding_model: "embo-01"  # MiniMax embedding model
        llm_model: "abab6.5s-chat"
        temperature: 0.0
      
      glm:
        api_key_env: "ZHIPUAI_API_KEY"
        embedding_model: "embedding-3"
        llm_model: "glm-4-flash"
        temperature: 0.0
```

### Backward Compatibility

Old config structure will still work (deprecated warning):
```yaml
models:
  local:
    provider: "ollama"
    host: "http://localhost:11434"
    embedding_model: "nomic-embed-text"
```

## Implementation Details

### File: `core/memory/mem0_adapter.py`

#### Changes to `_build_mem0_config()`

**Before (lines 92-135):**
```python
def _build_mem0_config(self) -> Dict[str, Any]:
    mem0_config = self.config.get('memory', {}).get('mem0', {})
    
    # Hardcoded Ollama configuration
    ollama_config = self.config.get('models', {}).get('local', {})
    ollama_host = ollama_config.get('host', 'http://localhost:11434')
    
    mem_config = {
        "version": "v1.1",
        "vector_store": { ... },
        "llm": {
            "provider": "litellm",
            "config": {
                "model": "ollama/llama3.2:3b",  # Hardcoded
                "temperature": 0.0
            }
        }
    }
    
    os.environ.setdefault("OLLAMA_API_BASE", ollama_host)
    return mem_config
```

**After (proposed):**
```python
def _build_mem0_config(self) -> Dict[str, Any]:
    mem0_config = self.config.get('memory', {}).get('mem0', {})
    
    # Get selected providers
    embedding_provider = mem0_config.get('embedding_provider', 'ollama')
    llm_provider = mem0_config.get('llm_provider', 'ollama')
    
    # Get provider configurations
    providers = mem0_config.get('providers', {})
    
    # Build base config
    mem_config = {
        "version": "v1.1",
        "vector_store": self._build_vector_store_config(mem0_config)
    }
    
    # Build embedder config
    mem_config["embedder"] = self._build_embedder_config(
        embedding_provider, 
        providers.get(embedding_provider, {})
    )
    
    # Build LLM config
    mem_config["llm"] = self._build_llm_config(
        llm_provider,
        providers.get(llm_provider, {})
    )
    
    # Set provider-specific environment variables
    self._set_provider_env_vars(llm_provider, providers.get(llm_provider, {}))
    
    return mem_config

def _build_embedder_config(self, provider: str, config: Dict) -> Dict:
    """Build embedder config based on provider type."""
    if provider == "ollama":
        host = config.get('host', 'http://localhost:11434')
        model = config.get('embedding_model', 'nomic-embed-text')
        return {
            "provider": "openai",  # Ollama's OpenAI-compatible endpoint
            "config": {
                "model": model,
                "openai_base_url": f"{host}/v1"
            }
        }
    
    elif provider == "qwen":
        api_key_env = config.get('api_key_env', 'DASHSCOPE_API_KEY')
        model = config.get('embedding_model', 'text-embedding-v3')
        return {
            "provider": "openai",  # Dashscope is OpenAI-compatible
            "config": {
                "model": model,
                "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": os.environ.get(api_key_env)
            }
        }
    
    elif provider == "minimax":
        api_key_env = config.get('api_key_env', 'MINIMAX_API_KEY')
        model = config.get('embedding_model', 'embo-01')
        return {
            "provider": "openai",  # MiniMax is OpenAI-compatible
            "config": {
                "model": model,
                "openai_base_url": "https://api.minimax.chat/v1",
                "api_key": os.environ.get(api_key_env)
            }
        }
    
    elif provider == "glm":
        api_key_env = config.get('api_key_env', 'ZHIPUAI_API_KEY')
        model = config.get('embedding_model', 'embedding-3')
        return {
            "provider": "openai",  # Zhipu is OpenAI-compatible
            "config": {
                "model": model,
                "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key": os.environ.get(api_key_env)
            }
        }
    
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")

def _build_llm_config(self, provider: str, config: Dict) -> Dict:
    """Build LLM config based on provider type."""
    model = config.get('llm_model')
    temperature = config.get('temperature', 0.0)
    
    # LiteLLM model string format: {provider}/{model}
    provider_prefixes = {
        "ollama": "ollama",
        "qwen": "dashscope",
        "minimax": "minimax",
        "glm": "zhipuai"
    }
    
    prefix = provider_prefixes.get(provider)
    if not prefix:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    return {
        "provider": "litellm",
        "config": {
            "model": f"{prefix}/{model}",
            "temperature": temperature
        }
    }

def _set_provider_env_vars(self, provider: str, config: Dict):
    """Set provider-specific environment variables for LiteLLM."""
    if provider == "ollama":
        host = config.get('host', 'http://localhost:11434')
        os.environ.setdefault("OLLAMA_API_BASE", host)
    
    elif provider == "qwen":
        api_key_env = config.get('api_key_env', 'DASHSCOPE_API_KEY')
        if api_key_env in os.environ:
            os.environ.setdefault("DASHSCOPE_API_KEY", os.environ[api_key_env])
    
    elif provider == "minimax":
        api_key_env = config.get('api_key_env', 'MINIMAX_API_KEY')
        group_id_env = config.get('group_id_env', 'MINIMAX_GROUP_ID')
        if api_key_env in os.environ:
            os.environ.setdefault("MINIMAX_API_KEY", os.environ[api_key_env])
        if group_id_env in os.environ:
            os.environ.setdefault("MINIMAX_GROUP_ID", os.environ[group_id_env])
    
    elif provider == "glm":
        api_key_env = config.get('api_key_env', 'ZHIPUAI_API_KEY')
        if api_key_env in os.environ:
            os.environ.setdefault("ZHIPUAI_API_KEY", os.environ[api_key_env])

def _build_vector_store_config(self, mem0_config: Dict) -> Dict:
    """Build vector store config (unchanged logic)."""
    vector_store_provider = mem0_config.get('vector_store', 'chroma')
    collections = mem0_config.get('collections', {})
    
    return {
        "provider": vector_store_provider,
        "config": {
            "collection_name": collections.get('knowledge', 'polly_mem0_memories'),
            "path": str(Path.home() / ".polly" / "chroma_mem0"),
            "embedding_model_dims": 1536  # TODO: Make configurable per provider
        }
    }
```

## Provider-Specific Details

### Ollama (Local)
- **Embedder:** Uses OpenAI-compatible endpoint (`/v1`)
- **LLM:** LiteLLM with `ollama/` prefix
- **Auth:** None (local service)
- **Env vars:** `OLLAMA_API_BASE`

### Qwen/Dashscope (Cloud)
- **Embedder:** OpenAI-compatible endpoint
- **LLM:** LiteLLM with `dashscope/` prefix
- **Auth:** API key via environment variable
- **Env vars:** `DASHSCOPE_API_KEY`
- **Docs:** https://help.aliyun.com/zh/dashscope/

### MiniMax (Cloud)
- **Embedder:** OpenAI-compatible endpoint
- **LLM:** LiteLLM with `minimax/` prefix
- **Auth:** API key + Group ID via environment variables
- **Env vars:** `MINIMAX_API_KEY`, `MINIMAX_GROUP_ID`
- **Docs:** https://platform.minimaxi.com/document

### GLM/Zhipu (Cloud)
- **Embedder:** OpenAI-compatible endpoint
- **LLM:** LiteLLM with `zhipuai/` prefix
- **Auth:** API key via environment variable
- **Env vars:** `ZHIPUAI_API_KEY`
- **Docs:** https://open.bigmodel.cn/dev/api

## Testing Strategy

### Unit Tests
1. Test `_build_embedder_config()` for each provider
2. Test `_build_llm_config()` for each provider
3. Test `_set_provider_env_vars()` for each provider
4. Test backward compatibility with old config structure

### Integration Tests
1. Initialize Mem0 with Ollama config
2. Initialize Mem0 with Qwen config (mocked)
3. Initialize Mem0 with MiniMax config (mocked)
4. Initialize Mem0 with GLM config (mocked)

### Manual Testing Checklist
- [ ] Ollama: Add memory, search memory
- [ ] Qwen: Add memory, search memory (requires API key)
- [ ] MiniMax: Add memory, search memory (requires API key)
- [ ] GLM: Add memory, search memory (requires API key)
- [ ] Switch providers mid-session (restart required)

## Migration Path

### Step 1: Add new config structure (backward compatible)
- Add `memory.mem0.providers` section to config.yaml
- Keep existing `models.local` section for now

### Step 2: Refactor adapter (feature flag)
- Add `use_new_config` flag to `memory.mem0`
- Implement new config builders
- Fallback to old logic if flag is false

### Step 3: Test with Ollama
- Enable `use_new_config: true`
- Verify no regression in Ollama functionality

### Step 4: Add cloud provider configs
- Add Qwen, MiniMax, GLM sections
- Test with API keys

### Step 5: Remove old config (deprecation)
- Remove `models.local` fallback
- Remove `use_new_config` flag
- Update documentation

## Open Questions

1. **Embedding dimensions:** Different models have different dimensions (Ollama: 768, OpenAI: 1536). Should this be configurable per provider?
2. **Cost tracking:** Should we add cost calculation for cloud providers?
3. **Fallback logic:** Should Mem0 fallback to local provider if cloud provider fails?
4. **Model validation:** Should we validate that specified models exist for each provider?

## References

- Mem0 Embedder Providers: `venv/lib/python3.13/site-packages/mem0/embeddings/`
- Mem0 LLM Providers: `venv/lib/python3.13/site-packages/mem0/llms/`
- LiteLLM Provider List: https://docs.litellm.ai/docs/providers
- Current Mem0 Config: `core/memory/mem0_adapter.py:92-135`
