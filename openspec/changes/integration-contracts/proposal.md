# Integration Contracts — Proposal

**Tier:** 1 (Core Intelligence) — Cross-cutting  
**Scope:** Backend  
**Status:** Designed, not started  
**Created:** February 2026  
**Depends On:** [unified-pattern-engine/](../unified-pattern-engine/), [entity-model-unification/](../entity-model-unification/)  
**Blocks:** [library-extraction/](../library-extraction/)

---

## What We're Doing

Defining and implementing the protocols that let Polly's core systems compose with each other. This is the connective tissue — the thing that turns a collection of independently-built subsystems into a coherent, compounding intelligence.

Specifically:

1. **Cross-system protocols** — Typed interfaces (Python Protocols) that define how systems interact: `PatternConsumer`, `EntityProvider`, `PersonaAware`, `ContextContributor`
2. **Persona composition** — Wire personas to actually use patterns, entities, mental models, and (eventually) themes instead of operating as islands
3. **Routing feedback loop** — Pattern learning feeds routing decisions; routing outcomes feed pattern learning
4. **Conversation synchronization** — Single source of truth for conversations between Electron and Python
5. **Mental model effectiveness tracking** — Measure whether activated mental models improve response quality
6. **Dynamic domain configuration** — Domains configurable at runtime, not hardcoded enums

## Why

Every system in Polly works in isolation. Pattern learning doesn't inform routing. The knowledge graph doesn't enrich persona responses. Mental models are injected but never measured. Compression output doesn't feed back into the knowledge layer. Personas don't learn from their own behavior.

The result is that Polly's systems don't compound. Using the Architect persona doesn't make future Architect sessions smarter. Learning a pattern in one domain doesn't help related domains. The knowledge graph grows but nothing queries it meaningfully.

This change creates the wiring that makes the whole greater than the sum of parts.

## Scope

### In Scope
- Protocol definitions in `core/protocols/`
- Persona↔Pattern integration (personas contribute to and consume patterns)
- Persona↔Entity integration (personas use graph context per-mode)
- Persona↔Mental Model integration (personas select/prioritize models)
- Pattern→Router integration (patterns inform model selection)
- Router→Pattern feedback (routing outcomes become patterns)
- Compression→Entity integration (entities extracted from compressed summaries)
- Conversation synchronization protocol between Electron and Python
- Mental model effectiveness tracking (lightweight)
- Dynamic domain configuration from user config

### Out of Scope
- Persona↔Theme integration (themes system doesn't exist yet)
- Agent Swarms integration (Agent Swarms don't exist yet)
- DRM integration (DRM doesn't exist yet)
- New personas (Programmer, Librarian, Administrator, Designer) — integration only for existing personas

## Reference

- Audit: [architecture-integration-audit/](../architecture-integration-audit/) (Findings #5, #6, #7, #9, #10)
- Depends: [unified-pattern-engine/](../unified-pattern-engine/), [entity-model-unification/](../entity-model-unification/)
- Related: [core-framework-refinement/](../core-framework-refinement/) (Pattern→Routing, SKILL↔Mental Model)
