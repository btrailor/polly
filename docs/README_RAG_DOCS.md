# Documentation Index - RAG & Routing System

**Complete reference for Polly's RAG and Hybrid Routing implementation**

---

## Quick Start

**New to the system?** Start here:
1. [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) - Read "Overview" and "Architecture Diagram" sections
2. [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) - Bookmark for when things break
3. [Configuration](#configuration-guide) - Set up your system

**Debugging an issue?** Go straight to:
- [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) - Fast diagnosis and fixes

**Understanding recent changes?** Check:
- [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) - Recent critical bug fixes

---

## Document Hierarchy

```
docs/
├── 📘 RAG_ROUTING_ARCHITECTURE.md
│   └── Complete system architecture (40+ pages)
│       ├── Overview & diagrams
│       ├── Component details
│       ├── Recent fixes
│       ├── Configuration
│       ├── Performance & cost analysis
│       └── Troubleshooting (detailed)
│
├── 📕 POST_MORTEM_rag_routing_fixes.md
│   └── Critical bug fix history (Feb 1, 2026)
│       ├── Timeline of discovery
│       ├── Detailed analysis of 4 critical bugs
│       ├── Root cause analysis
│       ├── Impact analysis (before/after)
│       └── Prevention checklist
│
├── 📗 RAG_TROUBLESHOOTING_QUICK_REFERENCE.md
│   └── Quick reference card (2 pages)
│       ├── Symptom checklist
│       ├── Common fixes
│       ├── Validation tests
│       └── Emergency restart
│
└── 📙 README_RAG_DOCS.md (this file)
    └── Navigation guide
```

---

## Documentation by Use Case

### 🎯 I want to...

#### Understand how it works
→ [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md)
- Read: "Overview", "Architecture Diagram", "Component Details"

#### Fix a broken system
→ [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md)
- Start with "Symptom Checklist"
- Jump to relevant "Quick Fix"

#### Configure thresholds
→ [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md)
- Section: "Configuration" → "Hybrid Routing Config"

#### Understand recent changes
→ [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md)
- Read: "Executive Summary", "Bug #1-4"

#### Add a new provider
→ [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md)
- Section: "Provider System"
- Then: [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) → "Prevention Checklist"

#### Optimize costs
→ [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md)
- Section: "Performance & Cost"
- Adjust thresholds in config

#### Debug low scores
→ [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md)
- Check: "Score Ranges", "Common Fixes #2"

#### Rebuild the index
→ [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md)
- Section: "Common Fixes #5"

---

## Key Concepts

### RAG (Retrieval-Augmented Generation)
**What:** Search your notes, inject relevant context into LLM prompts  
**Why:** Gives LLM knowledge of your personal notes/docs  
**Learn More:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "RAG Search System"

### Hybrid Search
**What:** Combines semantic (vector) + keyword (BM25) search  
**Why:** Better than either alone - catches different types of matches  
**Learn More:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Hybrid Search"

### Smart Routing
**What:** Automatically choose local (free) vs cloud (paid) based on context quality  
**Why:** Saves ~70% on costs while maintaining quality  
**Learn More:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Routing System"

### Score Normalization
**What:** Ensuring scores are in 0-1 range for threshold comparisons  
**Why:** Different scoring methods (semantic vs RRF) have different ranges  
**Learn More:** [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) → "Bug #2"

---

## Configuration Guide

### Minimum Required Config

Add to `config.yaml`:

```yaml
# RAG configuration
rag:
  vector_db_path: "~/.polly/chroma_db"
  chunk_size: 800
  chunk_overlap: 100
  n_results: 10

# Hybrid routing thresholds
hybrid_routing:
  thresholds:
    min_top_score: 0.75              # Minimum score to consider RAG "strong"
    min_high_quality_results: 2      # Minimum good results needed
    min_context_chars: 500           # Minimum context length
    exceptional_score: 0.85          # Score for "exceptional" override
    exceptional_min_results: 3       # Results for exceptional

  patterns:
    retrieval_keywords:              # Use local for these
      - "what is"
      - "tell me about"
      - "show me"
      - "in my notes"
    
    complexity_keywords:             # Use cloud for these
      - "design"
      - "architect"
      - "how do i"
      - "best practice"

# Router v2 (multi-provider)
routing_v2:
  enabled: true
  default_confidence: "balanced"

# Models
models:
  local:
    host: "http://localhost:11434"
    embedding_model: "nomic-embed-text"
    chat_models:
      balanced: "qwen2.5-coder:7b"
```

**Full config reference:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Configuration"

---

## File Location Map

### Core System Files

```
core/
├── polly.py                    # Main orchestration
│   ├── query() method          # Entry point
│   ├── _should_use_local_model() (lines 700-769)  # Routing logic
│   └── Hybrid router integration
│
├── rag.py                      # RAG search system
│   ├── UnifiedRAG class        # Main interface
│   ├── Hybrid search integration
│   └── Index management
│
├── hybrid_search.py            # Hybrid search implementation
│   ├── HybridSearcher class
│   ├── reciprocal_rank_fusion() (lines 268-287)  # ⚠️ Score normalization
│   └── BM25 keyword search
│
├── router_v2.py                # Multi-provider router
│   └── IntelligentRouterV2 class
│
└── providers/
    ├── github_provider.py      # GitHub Models adapter
    │   ├── stream() (lines 259-275)  # ⚠️ System prompt fix
    │   └── complete() (lines 154-169)  # ⚠️ System prompt fix
    ├── anthropic_provider.py
    └── openai_provider.py
```

**⚠️ = Recent critical fixes (Feb 1, 2026)**

---

## Common Issues & Solutions

| Issue | Document | Section |
|-------|----------|---------|
| Low RAG scores (0.01-0.03) | [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) | "Score Normalization" |
| "No access to notes" | [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) | "System Prompt Not Sent" |
| Always routes to cloud | [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) | "Score Ranges" |
| Provider crashes | [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) | "Empty Choices Crash" |
| AttributeError: no .llm | [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) | "Router AttributeError" |
| Understanding RRF scoring | [Architecture](RAG_ROUTING_ARCHITECTURE.md) | "Hybrid Search" |
| Cost optimization | [Architecture](RAG_ROUTING_ARCHITECTURE.md) | "Performance & Cost" |
| Adding new provider | [Post-Mortem](POST_MORTEM_rag_routing_fixes.md) | "Prevention Checklist" |

---

## Testing & Validation

### Quick Health Check

```bash
# 1. Check server
curl http://127.0.0.1:11436/health

# 2. Test retrieval query (should use local)
curl -N 'http://127.0.0.1:11436/polly/query' \
  -H 'Content-Type: application/json' \
  -d '{"query":"What are my notes about?","mode":"balanced"}' | head -20

# 3. Check routing decision
tail -50 /tmp/polly.log | grep "Using local\|Using cloud"
```

**Expected:** "Using local: Strong RAG + retrieval query"

**Full test suite:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Testing"

---

## Historical Context

### Before February 1, 2026
- RAG system appeared to work
- Search found documents correctly
- System prompts were built
- BUT: Context never reached LLMs
- Result: "I don't have access to your notes"

### After February 1, 2026
- ✅ System prompts properly delivered
- ✅ Scores normalized correctly
- ✅ Routing decisions accurate
- ✅ 70% cost savings via local routing
- ✅ No crashes or errors

**Full timeline:** [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) → "Timeline of Discovery"

---

## Performance Benchmarks

**RAG Search:**
- Semantic: 50-100ms
- Keyword: 10-20ms
- Fusion: 5-10ms
- **Total: ~100-150ms**

**LLM Response:**
- Local (Ollama): 20-30s first token
- Cloud (GitHub): 2-5s first token

**Costs (100 queries/day):**
- Before: $21/month (all cloud)
- After: $6.30/month (hybrid)
- **Savings: $14.70/month (70%)**

**Full analysis:** [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Performance & Cost"

---

## Next Steps

### For First-Time Setup
1. Read [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Overview"
2. Configure your system (see "Configuration Guide" above)
3. Start Ollama: `ollama serve`
4. Pull models: `ollama pull qwen2.5-coder:7b && ollama pull nomic-embed-text`
5. Start Polly server
6. Test with validation commands (see "Testing & Validation" above)

### For Troubleshooting
1. Identify symptom from [Quick Ref](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) → "Symptom Checklist"
2. Apply corresponding "Quick Fix"
3. Run validation test
4. If still broken, see [Architecture](RAG_ROUTING_ARCHITECTURE.md) → "Troubleshooting" (detailed)

### For Development
1. Review [POST_MORTEM_rag_routing_fixes.md](POST_MORTEM_rag_routing_fixes.md) → "Prevention Checklist"
2. Understand component interactions in [Architecture](RAG_ROUTING_ARCHITECTURE.md) → "Component Details"
3. Check score ranges and thresholds before changing code
4. Test full pipeline, not just individual components

---

## Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| RAG_ROUTING_ARCHITECTURE.md | ✅ Complete | Feb 1, 2026 |
| POST_MORTEM_rag_routing_fixes.md | ✅ Complete | Feb 1, 2026 |
| RAG_TROUBLESHOOTING_QUICK_REFERENCE.md | ✅ Complete | Feb 1, 2026 |
| README_RAG_DOCS.md (this file) | ✅ Complete | Feb 1, 2026 |

**Production Status:** All systems operational ✅

---

## Contact & Support

**Issues?** Check [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](RAG_TROUBLESHOOTING_QUICK_REFERENCE.md) first

**Architecture Questions?** See [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md)

**Bug Reports:** Include:
- Symptom description
- Relevant log excerpts
- Score ranges (from logs)
- Configuration (anonymize API keys)

**Feature Requests:** See [RAG_ROUTING_ARCHITECTURE.md](RAG_ROUTING_ARCHITECTURE.md) → "Future Improvements"

---

**Last Updated:** February 1, 2026  
**System Status:** Production Ready ✅
