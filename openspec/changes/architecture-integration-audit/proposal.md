# Architecture Integration Audit — Proposal

**Tier:** Cross-cutting (all tiers)  
**Scope:** Backend + Specs + Architecture  
**Status:** Analysis complete; remediation planned across sibling changes  
**Created:** February 2026

---

## What We're Doing

A comprehensive audit of Polly's architecture to identify and remediate gaps between:

1. **What specs describe** vs **what code implements**
2. **How systems should compose** vs **how they actually interact at runtime**
3. **What is built** vs **what is assumed to exist by other systems**

This audit found 10 critical integration issues across Polly's core systems and proposes a remediation plan spanning four sibling change folders. This document is the master reference.

## Why

Polly has grown organically through 15+ implementation phases. Each phase built real capability, but the connective tissue between systems was deferred. The result:

- Two incompatible pattern learning systems serving overlapping purposes
- Three independent entity extraction pipelines with no shared model
- A knowledge graph that exists structurally but is functionally disconnected from RAG and personas
- Specs that reference unbuilt systems (Agent Swarms, DRM, Themes) as though they're available
- A compression system branded as a "language" (PIL) but implementing only format-string abbreviation
- Mental models that are prompt fragments with no feedback loop
- Personas that operate as islands — not composing with patterns, graph, themes, or each other

These gaps compound. Pattern learning can't inform routing because the two pattern systems don't share a data model. The knowledge graph can't enrich persona responses because there's no integration protocol. Compression output doesn't feed back into entity extraction or pattern learning consistently.

**The risk:** As we build Tiers 2–5 on this foundation, each new system inherits these disconnections and adds its own. The cost of remediation grows exponentially.

## Scope

This audit covers:

### Systems Analyzed
1. Pattern Learning (`learners/patterns.py` + `core/pattern_learning.py`)
2. Knowledge Graph (`learners/graph.py`)
3. Compression System (`core/compression/`)
4. PIL (Polly Internal Language) — mental model compression format
5. Mental Models (`core/mental_models.py`)
6. Personas (`core/personas/`)
7. Domain Engine (`core/domains.py`)
8. RAG System (`core/rag.py`)
9. Routing (`core/router.py`, `core/router_v2.py`)
10. Memory Systems (conversation history, Mem0, compression)
11. Themes (spec-only, no implementation)
12. Agent Swarms (spec-only, no implementation)

### Deliverables
- **This document** — Master findings reference
- **[unified-pattern-engine/](../unified-pattern-engine/)** — Merge two pattern learners, create unified data model
- **[entity-model-unification/](../entity-model-unification/)** — Shared entity model, knowledge graph restructure
- **[integration-contracts/](../integration-contracts/)** — Cross-system protocols, learning loop closure, persona composition
- **[library-extraction/](../library-extraction/)** — Modularization into extractable libraries

### Spec Reconciliation
After implementation, all affected specs will be updated to reflect:
- Actual vs planned status for every system
- Real integration points (not aspirational)
- Clear "Implemented" / "Designed" / "Vision" labels on every feature

## Reference

- Related specs: All specs under `openspec/specs/` (30+ domains)
- Existing change: [core-framework-refinement/](../core-framework-refinement/) (overlapping Pattern→Routing + PIL scope)
- Architecture spec: [openspec/specs/architecture/spec.md](../../specs/architecture/spec.md)
