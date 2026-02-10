# Entity Model Unification — Proposal

**Tier:** 1 (Core Intelligence) → 3 (Knowledge Platform)  
**Scope:** Backend  
**Status:** Designed, not started  
**Created:** February 2026  
**Depends On:** Nothing (can parallel with unified-pattern-engine)  
**Blocks:** [integration-contracts/](../integration-contracts/), [library-extraction/](../library-extraction/), Phase 12a-ext (Knowledge Graph)

---

## What We're Doing

Creating a shared entity model and unified extraction pipeline that consolidates three independent entity systems into one coherent knowledge layer.

1. **Shared `Entity` data model** — one model used by knowledge graph, pattern engine, Mem0, and all future consumers
2. **Unified extraction pipeline** — one extraction path (spaCy + LLM fallback) instead of three independent extractors
3. **Knowledge graph restructure** — migrate from JSON with hardcoded entity lists to SQLite with proper graph operations
4. **Entity-aware RAG** — knowledge graph entities influence retrieval ranking

## Why

### Three Systems, Three Entity Models

**System A** — `KnowledgeGraph` (`learners/graph.py`):
- `Entity(id, name, entity_type, description, domains, aliases, metadata)`
- Regex matching against ~30 hardcoded terms
- JSON file storage
- Only system that feeds into query prompt context

**System B** — `PatternLearner` (`learners/patterns.py`):
- No formal Entity model — concepts are strings extracted by spaCy
- 500+ technical term whitelist
- Stored as pattern metadata, not as first-class entities
- Best extraction quality but entities aren't reusable

**System C** — `Mem0Adapter` (`core/memory/mem0_adapter.py`):
- Entities extracted by Mem0's internal LLM pipeline
- Relationship mapping
- Stored in Mem0's vector store
- Best at relationship discovery but isolated from graph and patterns

### What's Wrong

- "Python" is independently identified by all three systems with no deduplication
- The knowledge graph has the worst extraction (regex) but is the only one injecting context into prompts
- spaCy extraction in the pattern learner produces the best concept candidates but they never reach the knowledge graph
- Mem0 discovers relationships between entities but these never enrich the knowledge graph
- The spec describes authority scoring, anti-slop quality, and graph traversal — none of which exist

### What We Get

- One entity lives in one place, enriched by multiple extractors
- Graph context in prompts is backed by real NLP extraction, not regex
- Entity relationships from Mem0 flow into the graph
- Foundation for Phase 12a-ext (Knowledge Graph + Quality Pipeline)
- Foundation for entity-aware RAG (Tier 3)
- Clean `Entity` model that BookLore, Capture, Canvas can use when they're built

## Scope

### In Scope
- `core/entities/models.py` — shared `Entity`, `Relationship`, `EntityType` models
- `core/entities/store.py` — SQLite-backed entity store (replaces JSON)
- `core/entities/extractor.py` — unified extraction pipeline (spaCy primary, LLM optional)
- `core/entities/graph.py` — graph operations on SQLite (traversal, path finding, context building)
- Migration from `learners/graph.py` JSON format
- Integration with knowledge graph prompt context in `polly.py`
- Integration hooks for pattern engine entity references

### Out of Scope
- Full Phase 12a-ext (authority scoring, quality pipeline) — this is foundation only
- Visualization (Cytoscape.js) — deferred to Phase 12a-ext
- BookLore, Capture, Canvas entity integration — deferred to Tier 3
- Mem0 bidirectional sync — deferred to integration-contracts

## Reference

- Audit: [architecture-integration-audit/](../architecture-integration-audit/) (Findings #2, #3)
- Current: `learners/graph.py`, entity extraction in `learners/patterns.py`, `core/memory/mem0_adapter.py`
- Spec: [openspec/specs/knowledge-graph/spec.md](../../specs/knowledge-graph/spec.md)
- Related: [unified-pattern-engine/](../unified-pattern-engine/) (Pattern.entity_refs field)
