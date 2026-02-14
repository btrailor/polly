# Quick Start Guide - Tomorrow Morning

**Goal:** Implement multi-provider support for Mem0 in 3-5 hours

---

## Before You Start

### 1. Check Branch Status
```bash
git status
git branch -a
```

Currently on: `opencode/misty-canyon`  
Fixes are on: `development`

### 2. Decide on Branch Strategy

**Recommendation:** Create a new feature branch from `development`

```bash
# Option 1: New feature branch (RECOMMENDED)
git checkout development
git checkout -b feature/mem0-multi-provider

# Option 2: Work directly on development
git checkout development

# Option 3: Cherry-pick to current branch
git cherry-pick 77b542a f74a309 80ce909
```

### 3. Verify Mem0 Fixes Are Present
```bash
# Check if fixes are present
git log --oneline | grep -i "mem0\|frontmatter\|persona introduction"

# Should see these 3 commits:
# 77b542a fix: configure Mem0 to use local Ollama
# f74a309 fix: sanitize Obsidian Templater syntax
# 80ce909 fix: display persona introduction messages
```

---

## Implementation Steps

### Phase 1: Configuration (15 minutes)

1. **Open** `config/config.yaml`

2. **Find** the `memory.mem0` section

3. **Add** this configuration:
   ```yaml
   memory:
     mem0:
       enabled: true
       embedding_provider: "ollama"  # Start with ollama
       llm_provider: "ollama"        # Start with ollama
       
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

4. **Save** the file

5. **Verify** YAML is valid:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

---

### Phase 2: Refactoring (1-2 hours)

1. **Open** `core/memory/mem0_adapter.py`

2. **Add** these 4 new methods (copy from `tasks.md`):
   - `_build_embedder_config(self, provider: str, config: Dict) -> Dict`
   - `_build_llm_config(self, provider: str, config: Dict) -> Dict`
   - `_set_provider_env_vars(self, provider: str, config: Dict) -> None`
   - `_build_vector_store_config(self, mem0_config: Dict) -> Dict`

   **Tip:** Full code is in `tasks.md` Task 2.1 - copy/paste it!

3. **Replace** the `_build_mem0_config()` method (lines 92-135) with new version

   **Tip:** Full code is in `tasks.md` Task 2.2 - copy/paste it!

4. **Add** import at top if not present:
   ```python
   import os
   from pathlib import Path
   ```

5. **Save** the file

6. **Quick syntax check:**
   ```bash
   python -c "import core.memory.mem0_adapter"
   ```

---

### Phase 3: Testing (1-2 hours)

#### Unit Tests (30 min)

1. **Create/update** `tests/test_mem0_adapter.py`

2. **Add tests** (examples in `tasks.md` Task 3.1):
   - `test_build_embedder_config_ollama()`
   - `test_build_embedder_config_qwen()`
   - `test_build_embedder_config_minimax()`
   - `test_build_embedder_config_glm()`
   - `test_build_llm_config_all_providers()`
   - `test_set_provider_env_vars()`

3. **Run tests:**
   ```bash
   pytest tests/test_mem0_adapter.py -v
   ```

#### Integration Tests (30 min)

1. **Test with Ollama** (no regression):
   ```bash
   # Start Ollama if not running
   ollama serve
   
   # Start Polly server
   python -m interfaces.server
   
   # Test memory operations
   curl -X POST http://localhost:8000/api/memory/add \
     -H "Content-Type: application/json" \
     -d '{"content": "Test memory with Ollama", "user_id": "test"}'
   
   curl http://localhost:8000/api/memory/search?query=test
   ```

2. **Test with Qwen** (if you have API key):
   ```bash
   # Set API key
   export DASHSCOPE_API_KEY="your-key"
   
   # Edit config.yaml:
   # embedding_provider: "qwen"
   # llm_provider: "qwen"
   
   # Restart server and test
   ```

#### Manual Testing (30 min)

1. **Test provider switching:**
   - Start with Ollama
   - Switch to Qwen (edit config, restart)
   - Verify logs show "Using qwen for Mem0 embeddings"
   - Test memory operations
   - Switch back to Ollama

2. **Test error handling:**
   - Set invalid provider name
   - Set missing API key
   - Verify graceful error messages

---

### Phase 4: Documentation (30 minutes)

1. **Update** `openspec/changes/mem0-multi-provider-config/README.md`
   - Already done! Just review and adjust if needed.

2. **Update** `openspec/changes/mem0-adaptive-memory/IMPLEMENTATION_SUMMARY.md`
   - Add section: "Multi-Provider Support"
   - Link to new change proposal

3. **Update status** in `README.md`:
   - Change status from "📝 PLANNED" to "✅ COMPLETE"

---

### Phase 5: Finalization (30 minutes)

1. **Create completion report:**
   ```bash
   # File: openspec/changes/mem0-multi-provider-config/COMPLETION_REPORT.md
   ```

2. **Commit changes:**
   ```bash
   git add config/config.yaml
   git add core/memory/mem0_adapter.py
   git add tests/test_mem0_adapter.py
   git add openspec/changes/mem0-multi-provider-config/
   
   git commit -m "feat: add multi-provider support to Mem0 adapter

   - Add configurable provider selection (ollama, qwen, minimax, glm)
   - Refactor _build_mem0_config() to use dynamic provider builders
   - Add helper methods for embedder, LLM, and env var configuration
   - Maintain backward compatibility with legacy config structure
   - Add unit and integration tests for all providers
   
   See openspec/changes/mem0-multi-provider-config/ for details"
   ```

3. **Test one more time:**
   ```bash
   python -m interfaces.server
   # Verify server starts without errors
   ```

---

## Troubleshooting

### "Config validation failed"
- Check YAML syntax in config.yaml
- Ensure proper indentation (2 spaces)

### "Unsupported provider"
- Check spelling in config.yaml
- Valid values: "ollama", "qwen", "minimax", "glm"

### "API key not found"
- Set environment variable: `export DASHSCOPE_API_KEY="..."`
- Check `api_key_env` matches env var name in config

### "Import error"
- Run: `python -c "import mem0ai"`
- If fails: `pip install mem0ai`

### "Mem0 initialization failed"
- Check logs for specific error
- Verify Ollama is running (if using ollama)
- Verify API key is set (if using cloud provider)

---

## Checklist

### Before Starting
- [ ] Decided on branch strategy
- [ ] Verified Mem0 fixes are present
- [ ] Read proposal.md, design.md, tasks.md

### Phase 1: Configuration
- [ ] Updated config.yaml with new structure
- [ ] Validated YAML syntax
- [ ] Committed config changes

### Phase 2: Refactoring
- [ ] Added 4 helper methods to Mem0Adapter
- [ ] Replaced _build_mem0_config() method
- [ ] Verified no syntax errors

### Phase 3: Testing
- [ ] Unit tests written and passing
- [ ] Integration test with Ollama (no regression)
- [ ] Manual provider switching test
- [ ] Error handling verified

### Phase 4: Documentation
- [ ] README updated
- [ ] Main Mem0 docs updated
- [ ] Status changed to complete

### Phase 5: Finalization
- [ ] Completion report created
- [ ] Changes committed
- [ ] Server starts without errors

---

## Success Criteria

You're done when:

✅ Can switch providers by editing config.yaml only  
✅ All 4 providers work (Ollama tested, others with API keys)  
✅ No regression in Ollama functionality  
✅ All tests pass  
✅ Documentation complete  
✅ Changes committed with good commit message  

---

## Time Tracking

Start time: ____________  

Phase 1 complete: ____________ (Target: +15 min)  
Phase 2 complete: ____________ (Target: +1-2 hours)  
Phase 3 complete: ____________ (Target: +1-2 hours)  
Phase 4 complete: ____________ (Target: +30 min)  
Phase 5 complete: ____________ (Target: +30 min)  

Total time: ____________ (Target: 3-5 hours)

---

## Need Help?

1. **Review design.md** for complete code examples
2. **Review tasks.md** for step-by-step instructions
3. **Check IMPLEMENTATION_SUMMARY.md** for context

All documentation is in:
`openspec/changes/mem0-multi-provider-config/`

---

**Good luck!** 🚀

The planning is done, the code is written in the docs, you just need to copy/paste and test!
