# Proposal: Scalable Memory Layers + Rolling Relevance-Weighted Context

**Date:** 2026-02-18
**Status:** Proposed
**Priority:** P1 — Core intelligence infrastructure
**Tier:** 1 — Core Intelligence
**Scope:** Backend (Python)
**Depends On:** Mem0 Adaptive Memory (complete), Hardened Knowledge Infrastructure (complete)

---

## What

Add a tiered memory architecture (long-term stable, medium-term episodic, short-term working) built on Mem0, paired with a rolling relevance-weighted context assembler that enforces strict token budgets and dynamically scores, decays, and bin-packs context entries across turns. This replaces the current unbounded context concatenation with a system that knows what it's spending, prioritizes what matters now, and persists what matters later.

## Why

### Current State

Polly has multiple independent systems that contribute to the context window: RAG results (`core/rag.py`), mental models (`core/mental_models.py`), entity context (`core/entities/`), pattern engine (`core/patterns/`), conversation compression (`core/compression/`), and Mem0 adaptive memory (`core/memory/mem0_adapter.py`). Each operates as an island:

1. **No context budget.** The system prompt assembly in `core/polly.py:1921-2012` concatenates RAG results, gathered context (mental models + entities + patterns + compression summaries), domain prompts, and conversation history without any token accounting. A typical cloud call can consume 8,000-15,000+ input tokens with no mechanism to enforce a ceiling or make tradeoffs between sections.

2. **Mem0 is disconnected.** The Mem0 adapter is initialized (`polly.py:293-298`) but never called from the main `query()` pipeline. It is not a `ContextContributor` and does not participate in `_gather_context()`. The Scribe persona calls it directly for enrichment preferences; the Professor persona doesn't use it at all. There is no session-end extraction that writes learned facts back to persistent memory.

3. **No memory decay or amplification.** Time is never a factor in any scoring pipeline. A three-month-old episodic fact retrieved via semantic similarity gets the same weight as something explicitly discussed two turns ago. There is no mechanism to promote recurring topics or demote stale ones within a session.

4. **Token counting is approximate.** All token estimation uses `len(text) // 4` rather than a proper tokenizer. This means budget calculations, compression thresholds, and RAG context limits operate on rough guesses.

5. **Flat memory namespacing.** Mem0 memories are scoped by `persona:{name}` only. There is no tier separation (stable vs episodic vs working), no cross-persona shared memory, and no metadata for salience, source type, or reference frequency.

### Problem

These gaps compound. Without a budget, Polly overspends on context for cloud calls and can't make intelligent tradeoffs. Without tiered memory, conversations don't build on prior sessions — Polly has amnesia between sessions except for what's in its RAG-indexed notes. Without decay and amplification, the context window fills with equally-weighted noise rather than foregrounding what the conversation is actually about. Without session-end extraction, insights from conversations evaporate unless the user manually captures them as notes.

### Solution

Two complementary systems:

1. **Tiered Memory Store** — Three Mem0 collections (stable, episodic, working) with structured metadata, session-end extraction that writes back to longer-lived tiers, and time-decay scoring on retrieval. Built on the existing Mem0 adapter rather than replacing it.

2. **Rolling Relevance-Weighted Context Assembler** — A strict token budget allocator that governs all context sections, a composite relevance scorer that factors in retrieval similarity + recency + reference frequency + domain affinity + tier weight, and a per-turn decay/amplification loop that keeps the working set focused on what's active in the conversation.

### Benefits

1. **Predictable context costs.** Strict budget allocation means cloud calls consume a known maximum number of input tokens, with tradeoffs made explicitly rather than by accident.
2. **Cross-session continuity.** Session-end extraction captures stable facts, decisions, and in-progress work to persistent memory. Subsequent sessions surface these automatically via retrieval.
3. **Conversation coherence.** Rolling relevance scoring keeps recurring topics prominent and lets tangential context decay naturally, producing a tighter working set each turn.
4. **Foundation for persona memory.** The tiered architecture provides the infrastructure for persona-specific memory patterns (Professor teaching history, Architect decision logs) as a subsequent phase.
5. **Budget visibility.** Accurate token counting across the pipeline enables meaningful cost tracking and optimization.

## Scope

### Backend (Python)

**New files:**
- `core/context/token_counter.py` (~100 lines) — Token counting service wrapping `tiktoken` + local estimator
- `core/context/budget_allocator.py` (~200 lines) — Strict section-based token budget allocation
- `core/context/relevance_scorer.py` (~150 lines) — Composite relevance scoring with configurable weights
- `core/context/rolling_context.py` (~250 lines) — Per-turn decay/amplification and bin-packing selection
- `core/memory/tiers.py` (~200 lines) — Tiered memory definitions, metadata schema, tier-aware read/write
- `core/memory/retriever.py` (~250 lines) — Tiered retrieval with time-decay, domain filtering, ContextContributor
- `core/memory/extractor.py` (~300 lines) — Session-end extraction pipeline with tiered model routing

**Modified files:**
- `core/polly.py` — Refactor `_gather_context()` and context assembly in `query()` to use budget allocator and rolling context; add session-end extraction trigger; register memory retriever as ContextContributor
- `core/memory/__init__.py` — Update factory to expose tiered memory and retriever
- `core/memory/mem0_adapter.py` — Add tier-aware collection management and metadata schema
- `core/compression/manager.py` — Accept token budget parameter in `build_context()`
- `core/mental_models.py` — Accept token budget parameter in `build_context()`
- `core/config.py` — Add `memory` and `context_budget` sections to DEFAULT_CONFIG
- `config.yaml` — Add `memory` and `context_budget` configuration sections
- `core/hardened/classifier.py` — Wire into main query path (existing TODO at `polly.py:1869`)
- `core/mental_models.py` — Fix `"teacher"` → `"professor"` persona name mismatch in default models

### Frontend (Electron)
- No frontend changes in this phase. Memory configuration is backend-only via `config.yaml`.

### Dependencies
- `tiktoken` — OpenAI tokenizer library (new pip dependency, ~2MB)
- All other dependencies already present (Mem0, ChromaDB, Ollama)

## Non-Goals

- **Persona-specific memory patterns.** This change builds the tiered infrastructure. Professor teaching history, Architect decision logs, and other persona-specific read/write loops are a follow-up change that builds on this foundation.
- **Cross-persona memory sharing policies.** The tier structure supports shared namespaces, but defining which personas can read/write which tiers is deferred.
- **Memory management UI.** No Electron UI for browsing, editing, or deleting memories. Backend + config only.
- **Context distillation.** Already specced as a separate change (`context-distillation-layer`). Complements this work but is independent — distillation compresses content, this change decides what content to include.
- **Semantic response cache.** Already specced separately (`semantic-response-cache`). Orthogonal.
- **Entity graph retrieval.** Specced in the RAG spec as future work. Would enhance the retriever but is not required for this phase.

## Success Criteria

1. Every cloud-routed query stays within the configured token budget (no unbounded concatenation).
2. Facts stated by the user in one session are retrievable in subsequent sessions without manual note-taking.
3. Context entries that are discussed repeatedly in a conversation score higher than entries not referenced in 5+ turns.
4. Session-end extraction correctly identifies new stable facts vs decisions vs in-progress status and writes to appropriate tiers.
5. All existing ContextContributors (mental models, entities, patterns, compression) continue to function, now governed by budget allocation.
6. Token counting accuracy within 5% of actual model tokenization for cloud providers.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Session-end extraction produces noisy/wrong facts | Degrades long-term memory quality over time | Deduplication against existing stable memory; extraction confidence thresholds; tiered model routing (cloud for complex sessions) |
| Strict budget starves important context sections | Worse response quality despite budget discipline | Configurable min/max per section; guaranteed minimums for system prompt and conversation history; monitor and tune |
| Relevance decay prunes something the user needs | User has to re-state context | Conservative decay rate (0.85/turn); 5-turn eviction threshold; amplification on re-reference resets decay |
| tiktoken adds dependency overhead | Larger install, potential compatibility issues | Lazy-load tiktoken; fall back to `len(text)//4` if import fails; tiktoken is a well-maintained, widely-used package |

## Roadmap Reference

This is a **Tier 1 (Core Intelligence)** cross-cutting change that sits alongside the existing Core Framework Refinement work. It directly addresses the "Persona Memory for Enrichment" item (#24, currently ~25%) in Wave 4 by providing the tiered memory infrastructure that persona-specific memory needs.

It also complements two specced but unimplemented changes:
- **Context Distillation Layer** — Distillation compresses content after this change selects what to include. They stack.
- **Semantic Response Cache** — Cache hits skip the entire memory/context pipeline. Cache misses benefit from better context assembly.

Depends on completed work:
- **Mem0 Adaptive Memory** (complete) — Provides the storage backend this change builds on.
- **Hardened Knowledge Infrastructure** (complete) — The `RetrievalClassifier` (DIRECT/ADJACENT/ABSENT) is wired into the retriever's scoring in this change.
- **Integration Contracts** (complete) — The `ContextContributor` protocol this change extends.
