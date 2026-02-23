# Context Engine Improvement Specs

**Series:** Redis 2026 Context Engine Audit  
**Created:** February 2026  
**Motivation:** Redis's 2026 AI predictions identify context engineering — not reasoning — as the make-or-break capability for AI platforms in 2026. Simple RAG is insufficient. This series audits Polly's context systems against that standard and specifies targeted improvements.

---

## Specs in This Series

| # | Spec | Priority | Status | Core Problem Solved |
|---|------|----------|--------|---------------------|
| 01 | [Semantic Cache Layer](./01-semantic-cache.md) | P1 — Highest ROI | ✅ Implemented (Phase A) | No caching exists between query intake and LLM call. Every query pays full cost. |
| 02 | [Per-Item Granularity Context Assembly](./02-per-item-context-assembly.md) | P2 — Budget precision | 💭 Planned | Contributors return text blobs; bin-packing can't select individual items. |
| 03 | [Persist RollingContext Across Sessions](./03-rolling-context-persistence.md) | P3 — Cross-session continuity | 💭 Planned | RollingContext working set dies at session end; every session starts cold. |
| 04 | [Semantic Compression Trigger](./04-semantic-compression-trigger.md) | P4 — Preserve valuable conversations | 💭 Planned | Compression fires on message count/age, not semantic redundancy. |
| 05 | [Pattern Boost Calibration & Negative Patterns](./05-pattern-boost-calibration.md) | P5 — Better retrieval learning | 💭 Planned | 1.1–1.5x boost too weak to influence ranking; no negative evidence mechanism. |
| 06 | [Context Quality Observability](./06-context-quality-observability.md) | P6 — Enable iteration | ✅ Implemented | No persistent metrics on context system performance. Can't optimise blind. |
| 07 | [Mental Model Compression Validation](./07-mental-model-compression-validation.md) | P7 — Validate Compact Format | 💭 Planned | Symbol substitution unvalidated for small local models (qwen2.5:7b). |
| 08 | [BM25 Index Persistence](./08-bm25-index-persistence.md) | P8 — Cold-start latency | 💭 Planned | BM25 index rebuilds from scratch every session startup. |

---

## Dependency Graph

Some specs build on or are enhanced by others:

```
01 (Semantic Cache)
    └── feeds → 06 (Observability: cache_hit_rate metric)

02 (Per-Item Granularity)
    └── enables → 03 (RollingContext: per-item decay is more meaningful at item granularity)
    └── enables → 06 (Observability: items_returned/items_selected per contributor)

03 (RollingContext Persistence)
    └── depends on → 02 (persistence is more valuable when decay operates at item granularity)

04 (Semantic Compression Trigger)
    └── uses → embed_fn from UnifiedRAG (already available)
    └── feeds → 06 (Observability: SRS at compression time)

05 (Pattern Boost)
    └── feeds → 06 (Observability: pattern_boosted / pattern_penalised counts)

06 (Observability)
    └── enables → 07 (A/B data for mental model format validation)
    └── enables → all other specs (provides measurement for success criteria)

07 (Mental Model Validation)
    └── depends on → 06 (requires context_turns table with mm_format, mm_reference_rate)

08 (BM25 Persistence)
    └── independent — no dependencies, no dependents
```

**Recommended implementation order:** 06 first (observability unlocks measurement for everything else), then 01, then 02 → 03, then 04, 05, 07, 08 in parallel.

---

## What Polly Already Has (Context for Readers)

Polly's context engine is architecturally ahead of the simple RAG model Redis critiques. Before implementing these specs, understand what is already in place:

- **Budget-aware context assembly** (`core/context/budget_allocator.py`) — 3-pass priority allocation with minimums, target percentages, and hard caps
- **RollingContext** (`core/context/rolling_context.py`) — per-turn decay, amplification on reference, greedy bin-packing with look-ahead
- **RelevanceScorer** (`core/context/relevance_scorer.py`) — 5-factor composite scoring: retrieval similarity, recency, reference frequency, domain affinity, tier weight
- **Hybrid search** (`core/hybrid_search.py`) — semantic + BM25 + RRF fusion with title boosting
- **Three-tier memory** (`core/memory/tiers.py`) — STABLE / EPISODIC / WORKING with Mem0 backend
- **Pattern learning** (`core/patterns/engine.py`) — QueryChunkPattern and DomainPriorityPattern with confidence decay
- **Mental models** (`core/mental_models.py`) — 20+ models with three-tier activation scoring and Compact Format compression
- **Wave 3 pipeline** — query decomposition → split routing → synthesis (all enabled in `config/config.yaml`)

These specs are refinements of a solid foundation, not rewrites.

---

## Related OpenSpecs

- [Compression spec](../compression/spec.md) — existing compression system (spec-04 extends this)
- [Patterns spec](../patterns/spec.md) — existing pattern system (spec-05 extends this)
- [RAG spec](../rag/spec.md) — existing RAG system (specs 01, 05, 08 extend this)
- [Mental Models spec](../mental-models/spec.md) — existing mental model system (spec-07 extends this)
