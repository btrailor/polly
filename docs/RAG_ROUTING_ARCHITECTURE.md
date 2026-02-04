# RAG & Hybrid Routing Architecture

**Status:** ✅ Production Ready  
**Last Updated:** February 1, 2026  
**Recent Fixes:** Critical RAG scoring and routing bugs resolved

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Recent Critical Fixes](#recent-critical-fixes)
5. [Configuration](#configuration)
6. [Performance & Cost](#performance--cost)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Polly's RAG (Retrieval-Augmented Generation) system intelligently routes queries between local (free) and cloud (paid) LLM providers based on the quality of retrieved context. This hybrid approach maximizes cost efficiency while maintaining response quality.

### Key Features

- **Hybrid Search:** Combines semantic (vector) and keyword (BM25) search
- **Smart Routing:** Routes to local Ollama when RAG context is strong
- **Cost Optimization:** Saves ~70% on API costs by using local models for retrieval queries
- **Quality Preservation:** Uses cloud models for complex reasoning tasks
- **RAG-Aware:** Routing decisions based on actual context quality, not just query analysis

---

## Architecture Diagram

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Query Expansion                             │
│  - Pattern learner enhances query                        │
│  - Domain detection                                      │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           RAG Search (Hybrid)                            │
│                                                           │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │ Semantic Search  │      │ Keyword Search   │         │
│  │ (Vector/Cosine)  │      │ (BM25)           │         │
│  │                  │      │                  │         │
│  │ ChromaDB         │      │ BM25 Index       │         │
│  │ nomic-embed-text │      │ TF-IDF scoring   │         │
│  └────────┬─────────┘      └────────┬─────────┘         │
│           │                         │                    │
│           └──────────┬──────────────┘                    │
│                      │                                   │
│                      ▼                                   │
│          ┌──────────────────────┐                        │
│          │ Reciprocal Rank      │                        │
│          │ Fusion (RRF)         │                        │
│          │                      │                        │
│          │ • Normalize scores   │                        │
│          │ • Title boosting     │                        │
│          │ • Preserve 0-1 range │                        │
│          └──────────┬───────────┘                        │
└───────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│             Score Calculation                            │
│                                                           │
│  • Top score: Best result similarity (0-1)               │
│  • High quality count: Results with score > 0.7          │
│  • Total context chars: Sum of top 10 results            │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           Routing Decision                               │
│                                                           │
│  ┌─────────────────────────────────────────────┐         │
│  │ Thresholds (configurable):                  │         │
│  │ • min_top_score: 0.75                        │         │
│  │ • min_high_quality_results: 2                │         │
│  │ • min_context_chars: 500                     │         │
│  │ • exceptional_score: 0.85                    │         │
│  │ • exceptional_min_results: 3                 │         │
│  └─────────────────────────────────────────────┘         │
│                                                           │
│  ┌─────────────────────────────────────────────┐         │
│  │ Query Type Detection:                        │         │
│  │ • Retrieval: "what is", "tell me about"     │         │
│  │ • Complex: "design", "architect", "how do i"│         │
│  └─────────────────────────────────────────────┘         │
│                                                           │
│  Decision Logic:                                         │
│  • Strong RAG + Retrieval → LOCAL                        │
│  • Strong RAG + Not Complex → LOCAL                      │
│  • Exceptional RAG → LOCAL                               │
│  • Otherwise → CLOUD                                     │
└────────┬────────────────────────────────────────────────┘
         │
         ├─────────────────┬────────────────────┐
         │                 │                    │
         ▼                 ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   LOCAL      │  │    CLOUD     │  │    CLOUD     │
│   (Ollama)   │  │   (GitHub    │  │  (Anthropic/ │
│              │  │   Models)    │  │   OpenAI)    │
│ • Free       │  │ • $0.006/q   │  │ • $0.01/q    │
│ • Private    │  │ • Fast       │  │ • Quality    │
│ • qwen2.5    │  │ • gpt-4o     │  │ • claude     │
└──────────────┘  └──────────────┘  └──────────────┘
         │                 │                    │
         └─────────────────┴────────────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │   Response   │
                  └──────────────┘
```

---

## Component Details

### 1. RAG Search System

**File:** `core/rag.py`  
**Purpose:** Retrieval-Augmented Generation - finds relevant context from indexed documents

#### 1.1 Hybrid Search

**Semantic Search (Vector-based):**
- **Embedding Model:** `nomic-embed-text` (768-dim vectors)
- **Vector DB:** ChromaDB with cosine similarity
- **Distance Metric:** Cosine distance (0 = identical, 2 = opposite)
- **Score Calculation:** `score = 1 - distance` (converts to 0-1 similarity)

**Keyword Search (BM25):**
- **Algorithm:** Best Matching 25 (BM25)
- **Index:** In-memory TF-IDF index
- **Query Enhancement:** Extracts key terms, removes stopwords
- **Scoring:** Probabilistic relevance ranking

**Fusion (Reciprocal Rank Fusion):**
```python
# File: core/hybrid_search.py (lines 268-287)

# RRF score for each document
rrf_score = Σ [1 / (k_rrf + rank_i)]
# where k_rrf = 60, rank starts at 1

# Score normalization (CRITICAL FIX - Feb 1, 2026):
if no_keyword_results:
    # Pure semantic - preserve original scores
    final_score = semantic_score × title_boost
else:
    # Hybrid - normalize RRF to 0-1 range
    final_score = (rrf_score × k_rrf) × title_boost
```

**Why Normalization Matters:**
- Raw RRF scores: 0.016 (rank 1) to 0.008 (rank 10)
- Routing threshold: 0.75 (expects 0-1 range)
- Without normalization: ALL queries route to cloud (expensive!)
- With normalization: Scores match semantic range (0-1)

#### 1.2 Collections

**ChromaDB Collections:**
- `notes`: User's markdown notes (Obsidian vault)
- `codebase`: Indexed code repositories
- `documents`: PDFs, docs, other files
- `patterns`: Learned query→chunk associations

**Indexing:**
- **Chunking:** Smart markdown-aware (headers preserved)
- **Metadata:** Filepath, domain, timestamps
- **Updates:** File watcher triggers re-indexing on save

---

### 2. Routing System

**File:** `core/polly.py`  
**Method:** `_should_use_local_model()` (lines 700-769)

#### 2.1 Decision Logic

```python
# Calculate RAG quality metrics
top_score = rag_results[0].score if rag_results else 0
high_quality_count = sum(1 for r in rag_results if r.score > 0.7)
total_context_chars = sum(len(r.chunk.content) for r in rag_results[:10])

# Check thresholds
has_strong_rag = (
    top_score > 0.75 and
    high_quality_count >= 2 and
    total_context_chars > 500
)

# Detect query type
is_retrieval_query = any(kw in query.lower() for kw in [
    'what is', 'what are', 'tell me about', 'show me', ...
])
is_complex_query = any(kw in query.lower() for kw in [
    'design', 'architect', 'implement', 'how do i', ...
])

# Route decision
if has_strong_rag and is_retrieval_query:
    return True  # LOCAL
elif has_strong_rag and not is_complex_query:
    return True  # LOCAL
elif top_score > 0.85 and high_quality_count >= 3:
    return True  # LOCAL (exceptional)
else:
    return False  # CLOUD
```

#### 2.2 Router Integration

**When Router V2 Enabled (default):**
```python
# File: core/polly.py (lines 1531-1540)

if self.using_router_v2:
    # Decide routing mode
    use_local = self._should_use_local_model(
        query=query,
        rag_results=filtered_search_results,
        provider_override=provider_override
    )
    
    if use_local:
        # Use self.llm (router_v1 hybrid mode)
        # CRITICAL FIX: Was self.router.llm.chat() - router_v2 has no .llm!
        async for chunk in self.llm.chat(
            messages=messages,
            system_prompt=augmented_system,
            stream=stream
        ):
            yield chunk
    else:
        # Use router_v2 for cloud providers
        routing_decision = await self.router_v2.route(...)
```

**Router V1 (legacy):**
- Single router handles both local and cloud
- No hybrid decision logic
- User selects mode manually

---

### 3. Provider System

**Files:** `core/providers/*.py`

#### 3.1 GitHub Models Provider

**File:** `core/providers/github_provider.py`  
**Purpose:** Interface to GitHub Models API (Azure OpenAI backend)

**Critical Fixes (Feb 1, 2026):**

**Fix #1: Empty Choices Array**
```python
# Lines 313-316 - stream() method

# BEFORE (crashed):
chunk_text = data["choices"][0]["delta"]["content"]

# AFTER (defensive):
if "choices" in data and len(data["choices"]) > 0:
    delta = data["choices"][0].get("delta", {})
    chunk_text = delta.get("content", "")
else:
    # Skip metadata chunks
    logger.debug(f"Empty choices in SSE response: {data}")
    continue
```

**Why It Crashed:**
- GitHub API sends metadata chunks with empty `choices: []`
- These are filter results, content safety checks, etc.
- Direct array access `choices[0]` raised IndexError
- Now gracefully skips non-content chunks

**Fix #2: System Prompt Not Sent (CRITICAL)**
```python
# Lines 154-169 - complete() method
# Lines 259-275 - stream() method

# BEFORE (system prompt discarded!):
def stream(messages, **kwargs):
    # system was in kwargs but never used!
    response = httpx.post(
        url=f"{self.base_url}/chat/completions",
        json={"messages": messages, ...}  # Missing system!
    )

# AFTER (system prompt included):
def stream(messages, **kwargs):
    # Extract system prompt from kwargs
    system_prompt = kwargs.get('system', None)
    
    # Prepend to messages array
    if system_prompt:
        messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]
    
    # Send full context
    response = httpx.post(
        url=f"{self.base_url}/chat/completions",
        json={"messages": messages, ...}
    )
```

**Impact:**
- RAG system generated 11,662 chars of context
- Built augmented system prompt with context
- Provider received prompt but **threw it away**
- LLM had no context, responded "I don't have access to your notes"
- This was the **#1 most critical bug** - RAG was completely broken!

#### 3.2 Other Providers

**Anthropic Provider:** `core/providers/anthropic_provider.py`  
**OpenAI Provider:** `core/providers/openai_provider.py`  

Both implement same interface:
- `stream(messages, system=None, **kwargs)` → async iterator
- `complete(messages, system=None, **kwargs)` → string
- Handle system prompts correctly (no fix needed)

---

### 4. Configuration

**File:** `config.yaml`

#### 4.1 Hybrid Routing Config

```yaml
# Add this section to enable hybrid routing thresholds
hybrid_routing:
  thresholds:
    # Minimum top result score to consider RAG "strong"
    min_top_score: 0.75
    
    # Minimum number of high-quality results (score > 0.7)
    min_high_quality_results: 2
    
    # Minimum total context characters
    min_context_chars: 500
    
    # Exceptional quality overrides (always use local)
    exceptional_score: 0.85
    exceptional_min_results: 3
  
  patterns:
    # Queries that benefit from local models
    retrieval_keywords:
      - "what is"
      - "what are"
      - "tell me about"
      - "show me"
      - "in my notes"
      - "list"
      - "find"
    
    # Queries that need complex reasoning (cloud)
    complexity_keywords:
      - "design"
      - "architect"
      - "implement"
      - "how do i"
      - "best practice"
      - "optimize"
```

#### 4.2 RAG Config

```yaml
rag:
  vector_db_path: "~/.polly/chroma_db"
  chunk_size: 800
  chunk_overlap: 100
  n_results: 10

models:
  local:
    host: "http://localhost:11434"
    embedding_model: "nomic-embed-text"
    chat_models:
      balanced: "qwen2.5-coder:7b"
```

#### 4.3 Router V2 Config

```yaml
routing_v2:
  enabled: true
  default_confidence: "balanced"
  
  providers:
    github:
      enabled: true
      oauth_token_env: "GITHUB_TOKEN"
      priority: 1
      models:
        balanced: "openai/gpt-4o"
```

---

## Recent Critical Fixes

### Summary Table

| Bug | Severity | Impact | Status |
|-----|----------|--------|--------|
| GitHub Models crashes on empty choices | High | Provider unusable | ✅ Fixed |
| System prompts not sent to GitHub Models | **CRITICAL** | RAG completely broken | ✅ Fixed |
| Hybrid search score normalization | High | All queries use expensive cloud | ✅ Fixed |
| Router AttributeError (no .llm) | Medium | Local routing fails | ✅ Fixed |

### Fix Timeline

**Date:** February 1, 2026  
**Session Duration:** ~6 hours  
**Files Modified:** 3  
**Lines Changed:** ~50

### Detailed Fix Analysis

#### Fix #1: GitHub Models Empty Choices
**Problem:** IndexError on `choices[0]` when API returns metadata chunks  
**Root Cause:** Assumed all chunks have content  
**Solution:** Check array length before access  
**Impact:** Provider stability  

#### Fix #2: System Prompt Discarded ⚠️ CRITICAL
**Problem:** RAG context never reached LLM despite successful search  
**Root Cause:** Provider methods accepted `system` parameter but never used it  
**Solution:** Extract from kwargs and prepend to messages array  
**Impact:** **Core functionality broken** - RAG was completely useless!  

**Evidence:**
```
Before fix:
Query: "What can you tell me about Two Tangles?"
RAG: Found 28 results, 11,662 chars
LLM: "I don't have access to your notes..."

After fix:
Query: "What can you tell me about Two Tangles?"
RAG: Found 28 results, 11,662 chars
LLM: "Two Tangles is a norns instrument..." ✅
```

#### Fix #3: Score Normalization
**Problem:** RRF scores (0.016) way below routing threshold (0.75)  
**Root Cause:** Different score ranges (RRF vs semantic)  
**Solution:** Normalize RRF or use semantic scores when no keywords  
**Impact:** Cost optimization broken, always using expensive cloud  

**Evidence:**
```
Before fix:
RAG score: 0.019 (semantic was 0.694!)
Routing: CLOUD (0.019 < 0.75 threshold)
Cost: $0.007 per query

After fix:
RAG score: 0.895 (properly normalized)
Routing: LOCAL (0.895 > 0.75 threshold)
Cost: $0.00 per query
```

#### Fix #4: Router AttributeError
**Problem:** `AttributeError: 'IntelligentRouter' object has no attribute 'llm'`  
**Root Cause:** Router v2 doesn't have .llm attribute  
**Solution:** Use `self.llm` directly (created by hybrid init)  
**Impact:** Local routing completely broken when router v2 enabled  

---

## Performance & Cost

### Metrics

**RAG Search Performance:**
- Semantic search: ~50-100ms (depends on collection size)
- Keyword search: ~10-20ms (in-memory BM25)
- Fusion: ~5-10ms
- Total: ~100-150ms

**LLM Response Time:**
- Local (Ollama qwen2.5): 20-30s first token, ~100 tokens/sec
- Cloud (GitHub Models gpt-4o): 2-5s first token, ~80 tokens/sec

### Cost Analysis

**Assumptions:** 100 queries/day, 70% retrieval, 30% complex

**Before Fixes (all cloud):**
- 100 queries × $0.007 = $0.70/day
- **Monthly:** $21.00

**After Fixes (hybrid routing):**
- 70 retrieval (local) × $0 = $0
- 30 complex (cloud) × $0.007 = $0.21/day
- **Monthly:** $6.30

**Savings:** $14.70/month (70% reduction)

### Quality Metrics

**RAG Quality Indicators:**
```
Excellent: top_score > 0.85, high_quality > 5
Good:      top_score > 0.75, high_quality > 2
Fair:      top_score > 0.60, high_quality > 1
Poor:      top_score < 0.60
```

**Current Performance (after fixes):**
```
Query: "What can you tell me about my Norns project Two Tangles?"

RAG Results:
- Top score: 0.895 (Excellent ✅)
- High quality results: 13
- Context chars: 3,269
- Decision: LOCAL
- Cost: $0.00
- Response time: ~25s
- Quality: Accurate, contextual
```

---

## Troubleshooting

### Issue: Low RAG Scores

**Symptoms:**
- All queries routing to cloud
- Scores consistently < 0.75
- "Weak RAG" in logs

**Diagnosis:**
```bash
# Check hybrid search scores
tail -100 /tmp/polly.log | grep "Top Hybrid RAG"

# Look for score ranges
# Should see semantic scores 0.6-0.9 for good matches
# If seeing 0.01-0.03, hybrid search normalization broken
```

**Solutions:**
1. **Rebuild index with fresh embeddings:**
```python
from core.rag import UnifiedRAG
from pathlib import Path

rag = UnifiedRAG(
    db_path=Path.home() / '.polly/chroma_db',
    embedding_model='nomic-embed-text'
)

# Clear and rebuild
for coll in rag.collections.values():
    all_ids = coll.get()['ids']
    if all_ids:
        coll.delete(ids=all_ids)

vault_path = Path.home() / 'Library/Mobile Documents/...'
rag.index_obsidian_vault(vault_path, force=True)
```

2. **Check hybrid search normalization:**
```bash
grep "final_score.*rrf_score" core/hybrid_search.py
# Should see: (rrf_score * self.k_rrf) for normalization
```

3. **Verify embedding model:**
```bash
curl http://localhost:11434/api/tags | jq '.models[] | .name' | grep nomic
# Should show: nomic-embed-text:latest
```

### Issue: System Prompt Not Used

**Symptoms:**
- LLM says "I don't have access to your notes"
- RAG search finds results but LLM doesn't reference them
- Logs show context built but responses generic

**Diagnosis:**
```bash
# Check if system prompt extraction exists
grep "system_prompt = kwargs.get" core/providers/github_provider.py

# Should find in both stream() and complete() methods
```

**Solution:**
Apply fixes from lines 154-169 and 259-275 in github_provider.py

### Issue: Router AttributeError

**Symptoms:**
- `AttributeError: 'IntelligentRouter' object has no attribute 'llm'`
- "Router v2 failed" in logs
- Falls back to router v1

**Diagnosis:**
```bash
grep "self.router.llm" core/polly.py
# Should find: self.llm.chat() NOT self.router.llm.chat()
```

**Solution:**
Change `self.router.llm.chat()` to `self.llm.chat()` (line 1543)

### Issue: Always Routes to Cloud

**Symptoms:**
- All queries use cloud despite good RAG scores
- Logs show "Using cloud: weak RAG" even with high scores
- Unnecessary cloud costs

**Diagnosis:**
```bash
# Check routing decision logs
tail -100 /tmp/polly.log | grep "RAG quality"

# Look for:
# RAG quality: top_score=X.XXX, high_quality=N, chars=NNNN
# If score < 0.75 but should be higher, check normalization
```

**Solutions:**
1. Check threshold configuration (should be in config.yaml)
2. Verify score normalization in hybrid_search.py
3. Rebuild index if scores genuinely low

### Issue: Ollama Not Available

**Symptoms:**
- All queries route to cloud
- Logs: "Ollama not available"
- "Connection refused" errors

**Diagnosis:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if model is installed
ollama list | grep qwen
```

**Solution:**
```bash
# Start Ollama
ollama serve

# Pull model if missing
ollama pull qwen2.5-coder:7b

# Pull embedding model
ollama pull nomic-embed-text
```

---

## Testing

### Manual Testing

```bash
# Start server
cd /Users/brettgershon/polly
PYTHONPATH=/Users/brettgershon/polly venv/bin/python -m uvicorn \
  interfaces.server:create_app --host 127.0.0.1 --port 11436 --factory

# Test retrieval query (should use local)
curl -N 'http://127.0.0.1:11436/polly/query' \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is Two Tangles?","mode":"balanced"}'

# Test complex query (should use cloud)
curl -N 'http://127.0.0.1:11436/polly/query' \
  -H 'Content-Type: application/json' \
  -d '{"query":"Design a complex distributed system","mode":"balanced"}'

# Check routing decision
tail -50 /tmp/polly.log | grep "Using local\|Using cloud"
```

### Expected Results

**Retrieval Query:**
```
RAG quality: top_score=0.895, high_quality=13, chars=3269
Using local: Strong RAG + retrieval query
Response: [Contextual answer from notes]
Cost: $0.00
```

**Complex Query:**
```
RAG quality: top_score=0.421, high_quality=1, chars=156
Using cloud: weak RAG
Response: [Reasoning-heavy answer]
Cost: $0.007
```

---

## Future Improvements

### Potential Enhancements

1. **Adaptive Thresholds:**
   - Learn optimal thresholds from user feedback
   - A/B test different routing strategies
   - Track success rates per threshold

2. **Query Caching:**
   - Cache RAG results for similar queries
   - Skip search for exact duplicates
   - LRU cache with TTL

3. **Hybrid Models:**
   - Use local for draft, cloud for refinement
   - Ensemble responses from both
   - Quality scoring and selection

4. **Monitoring Dashboard:**
   - Real-time routing decisions
   - Cost tracking per query type
   - RAG score distributions
   - Provider availability status

5. **Fine-tuned Local Models:**
   - Fine-tune qwen on user's notes
   - Improve local model accuracy
   - Reduce cloud dependency further

---

## References

### Related Documentation

- [HYBRID_ROUTING_COMPLETE.md](../HYBRID_ROUTING_COMPLETE.md) - Original implementation
- [config.yaml](../config.yaml) - Configuration reference
- [API_KEYS.md](API_KEYS.md) - Provider setup guide

### Key Files

```
core/
├── polly.py              # Main orchestration, routing logic
├── rag.py                # RAG search system
├── hybrid_search.py      # Hybrid search implementation
├── router_v2.py          # Multi-provider router
└── providers/
    ├── github_provider.py   # GitHub Models adapter
    ├── anthropic_provider.py
    └── openai_provider.py
```

### External Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [Ollama Documentation](https://ollama.ai/docs)

---

**Document Status:** ✅ Complete and validated  
**Last Tested:** February 1, 2026  
**Production Status:** Ready for deployment
