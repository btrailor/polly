# Unified Pattern Engine — Proposal

**Tier:** 1 (Core Intelligence) — Cross-cutting  
**Scope:** Backend  
**Status:** Designed, not started  
**Created:** February 2026  
**Depends On:** Nothing (can start immediately)  
**Blocks:** [integration-contracts/](../integration-contracts/), [library-extraction/](../library-extraction/)

---

## What We're Doing

Merging Polly's two independent pattern learning systems into a single `PatternEngine` with:

1. **One `Pattern` data model** — replaces both `learners/patterns.Pattern` and `core/pattern_learning.Pattern`
2. **One `PatternEngine` class** — replaces both `PatternLearner` implementations
3. **Pluggable storage backends** — JSON for fast lookup, Mem0/ChromaDB for semantic search, both active simultaneously
4. **Clean consumer API** — typed interface that RAG, routing, domains, and personas code against
5. **PIL rename** — rename "Polly Internal Language" to "Compact Format" to accurately describe what it does

## Why

### The Current Problem

Polly has two `PatternLearner` classes with different data models:

**`learners/patterns.py`** — 3000+ lines, spaCy concept extraction, domain priorities, code patterns, JSON storage  
**`core/pattern_learning.py`** — ~400 lines, simple CRUD, Mem0 semantic search

In `core/polly.py`, both are instantiated and merged at runtime via an anonymous duck-typed class:

```python
wrap = type("_Mem0Pattern", (), {
    "name": p.description[:60],
    "pattern_type": p.type,
    ...
})()
```

This means:
- Patterns learned in `learners/` never reach Mem0's semantic index
- Patterns learned in Mem0 never benefit from spaCy concept extraction
- The bridge is fragile — any field name change breaks it silently
- No tests can cover the anonymous class behavior
- Two decay/pruning algorithms operating independently

### What We Get

- Single pattern system that has both rich extraction AND semantic search
- One place to add new pattern types (workflow, aesthetic, ethical)
- Clean interface for all consumers (RAG, routing, personas, domains)
- Testable, typed, documented
- Foundation for pattern→routing integration (Finding #7 in audit)
- Foundation for persona-aware pattern learning (Finding #6 in audit)

## Scope

### In Scope
- New unified `Pattern` data model in `core/patterns/models.py`
- New `PatternEngine` in `core/patterns/engine.py`
- Storage backends: `JSONBackend`, `Mem0Backend` in `core/patterns/storage/`
- Migration of all `learners/patterns.py` capabilities (concept extraction, domain priorities, code patterns, query patterns)
- Migration of all `core/pattern_learning.py` capabilities (Mem0 semantic search)
- Update all consumers in `core/polly.py` to use new API
- Rename PIL references to "Compact Format" where they refer to the field-abbreviation encoding
- Archive old pattern files (keep for reference, don't delete)

### Out of Scope
- New pattern types (deferred to integration-contracts)
- Pattern→routing feedback loop (deferred to integration-contracts)
- Persona-aware patterns (deferred to integration-contracts)
- Library extraction (deferred to library-extraction)

## Reference

- Audit: [architecture-integration-audit/](../architecture-integration-audit/) (Finding #1, #8)
- Current implementations: `learners/patterns.py`, `core/pattern_learning.py`
- Consumers: `core/polly.py`, `core/rag.py`, `core/domains.py`
- Spec: [openspec/specs/patterns/spec.md](../../specs/patterns/spec.md)
