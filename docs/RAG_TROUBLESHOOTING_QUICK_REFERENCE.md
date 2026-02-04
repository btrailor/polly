# RAG & Routing Quick Troubleshooting Guide

**Quick reference for diagnosing and fixing RAG/routing issues**

---

## Symptom Checklist

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| LLM says "no access to notes" | System prompt not sent | Check provider system prompt handling |
| All queries use cloud | Scores too low or normalization broken | Check score ranges, rebuild index |
| Provider crashes | Empty choices array | Add defensive checks |
| AttributeError: no .llm | Wrong router reference | Use `self.llm` not `self.router.llm` |
| Scores always ~0.02 | Score normalization broken | Fix hybrid search RRF normalization |
| No results found | Index empty or wrong vault | Rebuild index, check vault path |

---

## Quick Diagnostics

### Check RAG Score Ranges (should be 0.6-0.9 for matches)

```bash
tail -100 /tmp/polly.log | grep "Top.*RAG.*Score:"
```

**Expected:** Scores like `0.894`, `0.756`, etc.  
**Problem:** Scores like `0.019`, `0.016`, etc. → normalization broken

---

### Check Routing Decisions

```bash
tail -100 /tmp/polly.log | grep "RAG quality:"
```

**Good:**
```
RAG quality: top_score=0.895, high_quality=13, chars=3269
Using local: Strong RAG + retrieval query
```

**Bad:**
```
RAG quality: top_score=0.019, high_quality=0, chars=8700
Using cloud: weak RAG
```

---

### Check System Prompt Delivery

```python
# Add temporary logging to provider
def stream(self, messages, **kwargs):
    system_prompt = kwargs.get('system', None)
    print(f"[DEBUG] System prompt length: {len(system_prompt) if system_prompt else 0}")
```

**Expected:** Length > 1000 (has RAG context)  
**Problem:** Length = 0 or None → prompt not passed or not extracted

---

### Check Ollama Availability

```bash
curl http://localhost:11434/api/tags
ollama list | grep -E "(qwen|nomic)"
```

**Expected:** Both models present  
**Problem:** Connection refused or models missing → install/start Ollama

---

## Common Fixes

### Fix #1: System Prompt Not Sent

**File:** `core/providers/github_provider.py` (or your provider)

```python
def stream(self, messages: List[Dict], **kwargs):
    # Add this at the start
    system_prompt = kwargs.get('system', None)
    if system_prompt:
        messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]
    # ... rest of method
```

Apply to BOTH `stream()` and `complete()` methods.

---

### Fix #2: Score Normalization

**File:** `core/hybrid_search.py`

```python
# In reciprocal_rank_fusion(), around line 287
if not keyword_results:
    result.final_score = result.semantic_score * title_boost
else:
    result.final_score = (rrf_score * self.k_rrf) * title_boost
```

---

### Fix #3: Empty Choices Crash

**File:** `core/providers/github_provider.py`

```python
# In stream() method, when parsing chunks
if "choices" in data and len(data["choices"]) > 0:
    delta = data["choices"][0].get("delta", {})
    chunk_text = delta.get("content", "")
else:
    logger.debug(f"Empty choices: {data}")
    continue
```

---

### Fix #4: Router AttributeError

**File:** `core/polly.py`

```python
# Change from:
async for chunk in self.router.llm.chat(...):

# To:
async for chunk in self.llm.chat(...):
```

---

### Fix #5: Rebuild Index with Fresh Embeddings

```python
from core.rag import UnifiedRAG
from pathlib import Path

rag = UnifiedRAG(
    db_path=Path.home() / '.polly/chroma_db',
    embedding_model='nomic-embed-text',
    use_hybrid_search=True
)

# Clear all collections
for coll in rag.collections.values():
    all_ids = coll.get()['ids']
    if all_ids:
        coll.delete(ids=all_ids)
        print(f"Cleared {len(all_ids)} from {coll.name}")

# Rebuild
vault = Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Organizer'
count = rag.index_obsidian_vault(vault, force=True)
print(f"Indexed {count} notes")
```

---

## Emergency Restart

```bash
# Kill everything
pkill -f "python.*uvicorn"
pkill -f ollama

# Start Ollama
ollama serve &

# Wait for startup
sleep 3

# Start Polly
cd /Users/brettgershon/polly
PYTHONPATH=/Users/brettgershon/polly venv/bin/python -m uvicorn \
  interfaces.server:create_app --host 127.0.0.1 --port 11436 --factory \
  > /tmp/polly.log 2>&1 &

# Wait for startup
sleep 6

# Test
curl 'http://127.0.0.1:11436/health'
```

---

## Validation Tests

### Test 1: RAG Context Delivery

```bash
curl -N 'http://127.0.0.1:11436/polly/query' \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is Two Tangles?","mode":"balanced"}' \
  | head -50
```

**Pass:** Response mentions specific details from notes  
**Fail:** Response says "I don't have access to your notes"

---

### Test 2: Score Ranges

```python
from core.rag import UnifiedRAG
from pathlib import Path

rag = UnifiedRAG(Path.home() / '.polly/chroma_db', 'nomic-embed-text', True)
results = rag.search('test query', n_results=5)

for r in results:
    assert 0 <= r.score <= 1, f"Score out of range: {r.score}"
    print(f"✓ Score {r.score:.3f} in valid range")
```

**Pass:** All scores between 0 and 1  
**Fail:** Scores like 0.019, 0.016 (too low)

---

### Test 3: Local Routing

```bash
# Send retrieval query
curl -N 'http://127.0.0.1:11436/polly/query' \
  -H 'Content-Type: application/json' \
  -d '{"query":"What are my notes about?","mode":"balanced"}' &

# Check routing
sleep 10
tail -50 /tmp/polly.log | grep "Using local\|Using cloud"
```

**Pass:** "Using local: Strong RAG"  
**Fail:** "Using cloud: weak RAG" (for strong context)

---

## Configuration Check

### Verify Thresholds

```bash
grep -A 10 "hybrid_routing:" config.yaml
```

**Should see:**
```yaml
hybrid_routing:
  thresholds:
    min_top_score: 0.75
    min_high_quality_results: 2
    min_context_chars: 500
```

**If missing:** Add to config.yaml

---

### Verify Router V2 Enabled

```bash
grep -A 2 "routing_v2:" config.yaml
```

**Should see:**
```yaml
routing_v2:
  enabled: true
```

---

## Score Range Reference

| Score Range | Quality | Routing |
|-------------|---------|---------|
| 0.85 - 1.00 | Excellent | LOCAL (exceptional) |
| 0.75 - 0.85 | Good | LOCAL (if retrieval) |
| 0.60 - 0.75 | Fair | CLOUD (weak context) |
| 0.00 - 0.60 | Poor | CLOUD (no relevant context) |

**If seeing 0.01-0.03:** Score normalization broken!

---

## When to Rebuild Index

Rebuild if:
- ✅ Scores consistently too low despite relevant content
- ✅ Changed embedding model
- ✅ ChromaDB upgraded
- ✅ Added many new notes
- ✅ Index appears corrupted

Don't rebuild if:
- ❌ Just restarted server
- ❌ Only routing issues (check config first)
- ❌ Provider errors (separate issue)

---

## Emergency Contacts

**Architecture Docs:**
- [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) - Full details
- [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) - Bug history

**Key Files:**
- `core/polly.py` - Main orchestration, routing logic (lines 700-769)
- `core/rag.py` - RAG search system
- `core/hybrid_search.py` - Score fusion (lines 268-287)
- `core/providers/github_provider.py` - System prompt handling

**Logs:**
- `/tmp/polly.log` - Main application log
- Check for: "RAG quality", "Using local/cloud", "Top Hybrid RAG"

---

**Last Updated:** February 1, 2026  
**Status:** Production validated ✅
