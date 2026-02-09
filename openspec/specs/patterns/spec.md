# Patterns & Compression (OpenSpec)

Source of truth for pattern learning and conversation compression (Phases 13a, 2b). Detail: [docs/planning/tiers/TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md), phase 13a/2b docs.

## Pattern Learning (Phase 13a)

- **Storage:** `~/.polly/patterns.json`. Four types: query, code, conceptual, workflow.
- **Behavior:** Learns from interactions; RAG navigation optimization (30–70% faster retrieval). Pattern pruning and decay; compression and quality controls.
- **Implementation:** `core/pattern_learning.py` (~900 lines).

## Compression (Phase 2b)

- **Types:** conversation, pattern, mental_model. Token savings (40–60%); pattern-based context management.
- **Triggers:** Token threshold, message count. Settings UI: compression panel, stats (tokens saved, ratio), user thresholds.
- **Implementation:** `core/compression/compressor.py`.

## Reference

- [docs/planning/phases/phase-11/PHASE11_COMPRESSION_SYSTEM.md](../../../docs/planning/phases/phase-11/PHASE11_COMPRESSION_SYSTEM.md) — Compression UI
- Tier 1 doc for phase 13a/2b summaries
