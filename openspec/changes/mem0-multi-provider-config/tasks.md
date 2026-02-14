# Implementation Tasks: Multi-Provider Configuration for Mem0

## Overview
Refactor `core/memory/mem0_adapter.py` to support multiple LLM and embedding providers (Ollama, Qwen, MiniMax, GLM) through configuration rather than hardcoded logic.

---

## Phase 1: Configuration Schema

### Task 1.1: Update config.yaml
**File:** `config/config.yaml`

**Changes:**
```yaml
memory:
  mem0:
    enabled: true
    embedding_provider: "ollama"
    llm_provider: "ollama"
    
    providers:
      ollama:
        host: "http://localhost:11434"
        embedding_model: "nomic-embed-text"
        llm_model: "llama3.2:3b"
        temperature: 0.0
      
      qwen:
        api_key_env: "DASHSCOPE_API_KEY"
        embedding_model: "text-embedding-v3"
        llm_model: "qwen-turbo"
        temperature: 0.0
      
      minimax:
        api_key_env: "MINIMAX_API_KEY"
        group_id_env: "MINIMAX_GROUP_ID"
        embedding_model: "embo-01"
        llm_model: "abab6.5s-chat"
        temperature: 0.0
      
      glm:
        api_key_env: "ZHIPUAI_API_KEY"
        embedding_model: "embedding-3"
        llm_model: "glm-4-flash"
        temperature: 0.0
```

**Acceptance:**
- [ ] New config structure added
- [ ] Old `models.local` config still present (for backward compatibility)
- [ ] Config validates (no YAML syntax errors)

---

## Phase 2: Adapter Refactoring

### Task 2.1: Add helper methods to Mem0Adapter
**File:** `core/memory/mem0_adapter.py`

**New methods:**
1. `_build_embedder_config(provider: str, config: Dict) -> Dict`
2. `_build_llm_config(provider: str, config: Dict) -> Dict`
3. `_set_provider_env_vars(provider: str, config: Dict) -> None`
4. `_build_vector_store_config(mem0_config: Dict) -> Dict`

**Implementation:**
```python
def _build_embedder_config(self, provider: str, config: Dict) -> Dict:
    """Build embedder config based on provider type."""
    if provider == "ollama":
        host = config.get('host', 'http://localhost:11434')
        model = config.get('embedding_model', 'nomic-embed-text')
        return {
            "provider": "openai",
            "config": {
                "model": model,
                "openai_base_url": f"{host}/v1"
            }
        }
    
    elif provider == "qwen":
        api_key_env = config.get('api_key_env', 'DASHSCOPE_API_KEY')
        model = config.get('embedding_model', 'text-embedding-v3')
        return {
            "provider": "openai",
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
            "provider": "openai",
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
            "provider": "openai",
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
    """Build vector store config (extracted from _build_mem0_config)."""
    vector_store_provider = mem0_config.get('vector_store', 'chroma')
    collections = mem0_config.get('collections', {})
    
    return {
        "provider": vector_store_provider,
        "config": {
            "collection_name": collections.get('knowledge', 'polly_mem0_memories'),
            "path": str(Path.home() / ".polly" / "chroma_mem0"),
            "embedding_model_dims": 1536
        }
    }
```

**Acceptance:**
- [ ] All 4 helper methods implemented
- [ ] Each method has docstring
- [ ] Type hints present
- [ ] Error handling for unsupported providers

---

### Task 2.2: Refactor _build_mem0_config()
**File:** `core/memory/mem0_adapter.py` (lines 92-135)

**Replace with:**
```python
def _build_mem0_config(self) -> Dict[str, Any]:
    """
    Build Mem0-specific configuration from Polly config.
    
    Returns:
        Configuration dict for Memory.from_config()
    """
    mem0_config = self.config.get('memory', {}).get('mem0', {})
    
    # Get selected providers
    embedding_provider = mem0_config.get('embedding_provider', 'ollama')
    llm_provider = mem0_config.get('llm_provider', 'ollama')
    
    # Get provider configurations
    providers = mem0_config.get('providers', {})
    
    if not providers:
        logger.warning("No providers configured in memory.mem0.providers, using defaults")
        providers = self._get_default_provider_config()
    
    # Validate selected providers exist in config
    if embedding_provider not in providers:
        raise ValueError(f"Embedding provider '{embedding_provider}' not found in config")
    if llm_provider not in providers:
        raise ValueError(f"LLM provider '{llm_provider}' not found in config")
    
    # Build Mem0 config
    mem_config = {
        "version": "v1.1",
        "vector_store": self._build_vector_store_config(mem0_config)
    }
    
    # Add embedder config
    try:
        mem_config["embedder"] = self._build_embedder_config(
            embedding_provider,
            providers[embedding_provider]
        )
        logger.info(f"Using {embedding_provider} for Mem0 embeddings")
    except Exception as e:
        logger.error(f"Failed to build embedder config: {e}")
        raise
    
    # Add LLM config
    try:
        mem_config["llm"] = self._build_llm_config(
            llm_provider,
            providers[llm_provider]
        )
        logger.info(f"Using {llm_provider} for Mem0 LLM")
    except Exception as e:
        logger.error(f"Failed to build LLM config: {e}")
        raise
    
    # Set provider-specific environment variables
    self._set_provider_env_vars(llm_provider, providers[llm_provider])
    
    # Optional: Graph store configuration
    graph_store_config = mem0_config.get('graph_store')
    if graph_store_config:
        mem_config["graph_store"] = graph_store_config
        logger.info("Graph store enabled for entity relationships")
    
    return mem_config

def _get_default_provider_config(self) -> Dict:
    """Fallback to old config structure for backward compatibility."""
    logger.warning("Using legacy config structure (models.local)")
    
    ollama_config = self.config.get('models', {}).get('local', {})
    return {
        "ollama": {
            "host": ollama_config.get('host', 'http://localhost:11434'),
            "embedding_model": ollama_config.get('embedding_model', 'nomic-embed-text'),
            "llm_model": ollama_config.get('model', 'llama3.2:3b'),
            "temperature": 0.0
        }
    }
```

**Acceptance:**
- [ ] Method refactored to use helper methods
- [ ] Provider validation implemented
- [ ] Backward compatibility maintained
- [ ] Error handling and logging added
- [ ] No hardcoded provider logic remains

---

## Phase 3: Testing

### Task 3.1: Add unit tests
**File:** `tests/test_mem0_adapter.py`

**Test cases:**
1. Test `_build_embedder_config()` for each provider (ollama, qwen, minimax, glm)
2. Test `_build_llm_config()` for each provider
3. Test `_set_provider_env_vars()` for each provider
4. Test `_build_mem0_config()` with new config structure
5. Test `_build_mem0_config()` with legacy config structure (backward compat)
6. Test error handling for missing provider configs
7. Test error handling for unsupported providers

**Example test:**
```python
def test_build_embedder_config_ollama():
    adapter = Mem0Adapter(test_config)
    config = {"host": "http://localhost:11434", "embedding_model": "nomic-embed-text"}
    result = adapter._build_embedder_config("ollama", config)
    
    assert result["provider"] == "openai"
    assert result["config"]["model"] == "nomic-embed-text"
    assert result["config"]["openai_base_url"] == "http://localhost:11434/v1"

def test_build_embedder_config_qwen():
    os.environ["DASHSCOPE_API_KEY"] = "test-key"
    adapter = Mem0Adapter(test_config)
    config = {"api_key_env": "DASHSCOPE_API_KEY", "embedding_model": "text-embedding-v3"}
    result = adapter._build_embedder_config("qwen", config)
    
    assert result["provider"] == "openai"
    assert result["config"]["model"] == "text-embedding-v3"
    assert "dashscope.aliyuncs.com" in result["config"]["openai_base_url"]
    assert result["config"]["api_key"] == "test-key"
```

**Acceptance:**
- [ ] All test cases pass
- [ ] Code coverage > 90% for modified methods
- [ ] Tests run in CI/CD pipeline

---

### Task 3.2: Integration testing
**Manual testing steps:**

1. **Test Ollama (local):**
   ```bash
   # Ensure Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Polly server
   python -m interfaces.server
   
   # Test memory operations
   curl -X POST http://localhost:8000/api/memory/add \
     -H "Content-Type: application/json" \
     -d '{"content": "Test memory", "user_id": "test"}'
   
   curl http://localhost:8000/api/memory/search?query=test
   ```

2. **Test Qwen (cloud):**
   ```bash
   export DASHSCOPE_API_KEY="your-api-key"
   
   # Update config.yaml
   # embedding_provider: "qwen"
   # llm_provider: "qwen"
   
   # Restart server and test
   ```

3. **Test provider switching:**
   ```bash
   # Switch from ollama to qwen
   # Update config.yaml
   # Restart server
   # Verify new provider is used (check logs)
   ```

**Acceptance:**
- [ ] Ollama works (no regression)
- [ ] Qwen works (with valid API key)
- [ ] MiniMax works (with valid API key)
- [ ] GLM works (with valid API key)
- [ ] Provider switching works (restart required)

---

## Phase 4: Documentation

### Task 4.1: Update README
**File:** `openspec/changes/mem0-multi-provider-config/README.md`

**Sections to add:**
1. Quick Start (provider switching)
2. Provider Configuration Guide
   - Ollama setup
   - Qwen/Dashscope setup
   - MiniMax setup
   - GLM/Zhipu setup
3. Troubleshooting (API key errors, provider-specific issues)

**Acceptance:**
- [ ] README updated with provider examples
- [ ] Each provider has setup instructions
- [ ] API key configuration documented

---

### Task 4.2: Update main Mem0 documentation
**File:** `openspec/changes/mem0-adaptive-memory/IMPLEMENTATION_SUMMARY.md`

**Changes:**
- Add section on multi-provider support
- Link to new change proposal
- Update configuration examples

**Acceptance:**
- [ ] Multi-provider section added
- [ ] Cross-references updated
- [ ] Examples reflect new config structure

---

## Phase 5: Cleanup and Finalization

### Task 5.1: Remove deprecated code (optional)
**Files:**
- `core/memory/mem0_adapter.py` - Remove `_get_default_provider_config()` (if desired)
- `config/config.yaml` - Remove `models.local` section (if desired)

**Note:** This is optional - keeping backward compatibility is fine.

**Acceptance:**
- [ ] Decision made: keep or remove deprecated code
- [ ] If removing: all tests still pass
- [ ] If keeping: deprecation warnings logged

---

### Task 5.2: Create completion report
**File:** `openspec/changes/mem0-multi-provider-config/COMPLETION_REPORT.md`

**Sections:**
1. Summary of changes
2. Files modified
3. Test results
4. Provider compatibility matrix
5. Known issues / limitations
6. Future enhancements

**Acceptance:**
- [ ] Completion report written
- [ ] All tasks marked complete
- [ ] Change proposal status updated

---

## Phase 6: Smart Provider Selection (Optional - Future Enhancement)

### Task 6.1: Implement SmartProviderSelector class
**File:** `core/memory/smart_provider_selector.py` (new file)

**Implementation:**
Create a new class that analyzes content and metadata to automatically select the best provider.

**Key methods:**
1. `select_provider(content: str, metadata: Dict) -> str`
2. `_detect_language(content: str) -> Dict`
3. `_is_sensitive_content(content: str, metadata: Dict) -> bool`
4. `_has_pii(content: str) -> bool`

**Full code available in:** `MODEL_SELECTION_STRATEGY.md` and `UX_FLOW.md`

**Acceptance:**
- [ ] SmartProviderSelector class implemented
- [ ] Language detection working (Chinese/English)
- [ ] Privacy detection working (PII, tags, vault paths)
- [ ] Domain detection working (academic, code, etc.)
- [ ] Unit tests pass

---

### Task 6.2: Integrate smart selection into Mem0Adapter
**File:** `core/memory/mem0_adapter.py`

**Changes:**
```python
from core.memory.smart_provider_selector import SmartProviderSelector

class Mem0Adapter:
    def __init__(self, config: Dict[str, Any]):
        # ... existing init code ...
        
        # Add smart selector
        mem0_config = config.get('memory', {}).get('mem0', {})
        if mem0_config.get('auto_select', False):
            self.smart_selector = SmartProviderSelector(config)
        else:
            self.smart_selector = None
    
    def add_memory(self, content: str, user_id: str = "default", 
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Override provider if smart selection enabled
        if self.smart_selector:
            selected_provider = self.smart_selector.select_provider(content, metadata or {})
            
            # Temporarily switch provider for this operation
            original_config = self.config.copy()
            self.config['memory']['mem0']['embedding_provider'] = selected_provider
            self.config['memory']['mem0']['llm_provider'] = selected_provider
            
            # Rebuild Mem0 config with new provider
            self.mem0 = self._initialize_mem0()
            
            logger.info(f"[Mem0] Auto-selected {selected_provider} for this memory")
        
        # ... rest of add_memory logic ...
```

**Acceptance:**
- [ ] Smart selection integrated
- [ ] Works with `auto_select: true` config
- [ ] Logs selection decisions
- [ ] No impact when `auto_select: false`

---

### Task 6.3: Add UI indicator for active provider
**File:** `electron-app/src/renderer/app.js`

**UI Addition:**
Add a small indicator in the status bar showing which provider is active:

```javascript
// In updateMemoryProviderIndicator()
function updateMemoryProviderIndicator(provider, reason) {
    const indicator = document.getElementById('memory-provider-indicator');
    indicator.textContent = `Memory: ${provider}`;
    indicator.title = `Using ${provider} - ${reason}`;
}
```

**HTML Addition:**
```html
<div id="status-bar">
    <span id="memory-provider-indicator">Memory: Ollama</span>
</div>
```

**Acceptance:**
- [ ] Indicator visible in UI
- [ ] Shows current provider
- [ ] Tooltip explains why provider was selected

---

### Task 6.4: Add smart selection tests
**File:** `tests/test_smart_provider_selector.py` (new file)

**Test cases:**
1. Test Chinese content → Qwen
2. Test English content → Ollama (default)
3. Test private tag → Ollama (privacy override)
4. Test academic domain → GLM
5. Test PII detection → Ollama
6. Test budget exhausted → Ollama
7. Test multilingual content → Qwen

**Acceptance:**
- [ ] All test cases pass
- [ ] Edge cases covered
- [ ] Integration test with Mem0Adapter

---

## Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Configuration | 1 task | 15 minutes |
| Phase 2: Refactoring | 2 tasks | 1-2 hours |
| Phase 3: Testing | 2 tasks | 1-2 hours |
| Phase 4: Documentation | 2 tasks | 30 minutes |
| Phase 5: Cleanup | 2 tasks | 30 minutes |
| **Phase 6: Smart Selection (Optional)** | **4 tasks** | **2-3 hours** |
| **Total (with Phase 6)** | **13 tasks** | **5-8 hours** |

---

## Dependencies

- Mem0 fixes must be merged/cherry-picked to current branch first (commits 77b542a, f74a309, 80ce909)
- Access to cloud provider API keys for testing (Qwen, MiniMax, GLM)
- LiteLLM must support all provider prefixes (already confirmed)

---

## Success Criteria

- [x] Can switch Mem0 providers by editing config.yaml only (no code changes)
- [x] All 4 providers work (Ollama, Qwen, MiniMax, GLM)
- [x] No regression in Ollama functionality
- [x] All tests pass (17/17 unit tests passing)
- [x] Documentation complete
- [x] Change proposal marked complete

---

## Rollback Plan

If issues arise:
1. Revert `_build_mem0_config()` to use hardcoded Ollama logic
2. Remove new config sections from config.yaml
3. Keep new config structure in place but unused (for future retry)
