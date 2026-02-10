# Library Extraction — Proposal

**Tier:** Cross-cutting (long-term)  
**Scope:** Backend + Package structure  
**Status:** Designed, not started  
**Created:** February 2026  
**Depends On:** [unified-pattern-engine/](../unified-pattern-engine/), [entity-model-unification/](../entity-model-unification/), [integration-contracts/](../integration-contracts/)  
**Blocks:** Nothing (final step)

---

## What We're Doing

Identifying and extracting Polly's core systems into modular, independently-usable Python packages. Each library has:

1. **Clean public API** — well-typed, documented, no Polly-specific assumptions
2. **Independent installability** — pip-installable with its own dependencies
3. **Polly as the integration layer** — Polly becomes a thin orchestrator that composes these libraries

## Why

### For Polly
- **Cleaner architecture**: Each system has enforced boundaries. No more cross-module imports that bypass interfaces.
- **Easier testing**: Libraries can be tested in isolation without spinning up the full Polly stack.
- **Faster development**: New contributors can work on one library without understanding the full codebase.
- **Dependency clarity**: Each library declares its own dependencies instead of one monolithic `requirements.txt`.

### For the Ecosystem
- **Reusable components**: The intelligent router, pattern engine, and knowledge graph are useful outside Polly.
- **Open source value**: Individual libraries are more approachable for contributions than a full application.
- **Composability**: Other projects can use `polly-routing` without importing `polly-compression`.

### The Timing is Right
After the P0 (unified-pattern-engine, entity-model-unification) and P1 (integration-contracts) changes, each system will have:
- A clean interface (Protocol-based contracts)
- Clear boundaries (no duck-typed bridges)
- Defined integration points (not ad-hoc imports)

This is the natural moment to draw package boundaries.

## Scope

### Libraries to Extract (Priority Order)

1. **`polly-routing`** — Multi-provider intelligent LLM routing
2. **`polly-patterns`** — Pattern learning and retrieval engine
3. **`polly-compression`** — Conversation and context compression
4. **`polly-entities`** — Knowledge graph and entity management
5. **`polly-personas`** — Persona framework with mode system

### What Stays in Polly Core
- `core/polly.py` — Orchestrator (composes all libraries)
- `core/config.py` — Polly-specific configuration
- `interfaces/` — API server, CLI
- `electron-app/` — Frontend
- `integrations/` — Third-party integrations
- Domain engine — too Polly-specific to generalize
- Knowledge writer — orchestration, not a library

### Approach: Packages in Monorepo
The libraries stay in the Polly repository as internal packages (not published to PyPI initially). They're extracted as subdirectories with their own `__init__.py` and can later be split into separate repos if desired.

```
polly/
├── libs/
│   ├── polly-routing/
│   │   ├── polly_routing/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── providers/
│   │   │   └── budget.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── polly-patterns/
│   ├── polly-compression/
│   ├── polly-entities/
│   └── polly-personas/
├── core/
│   ├── polly.py         # Imports from libs/
│   ├── config.py
│   └── ...
```

## Reference

- Audit: [architecture-integration-audit/](../architecture-integration-audit/) (modularization recommendations)
- Depends: All P0 and P1 changes must complete first
