# Architecture Integration Audit — Tasks

**Last Updated:** February 2026  
**Scope:** This task list covers the audit documentation and spec reconciliation only. Implementation tasks live in sibling change folders.

---

## Audit & Documentation (This Folder)

| # | Task | Status |
|---|------|--------|
| 1 | Complete codebase analysis of all 12 systems | ✅ |
| 2 | Document 10 integration findings with evidence | ✅ |
| 3 | Create sibling change folders with proposals | ✅ |
| 4 | Create sibling change folders with designs | ✅ |
| 5 | Create sibling change folders with tasks | ✅ |
| 6 | Update roadmap.md with integration tier | ✅ |
| 7 | Spec reconciliation: add status markers to all specs | ✅ |
| 8 | Update architecture/spec.md with actual data flow | ✅ |
| 9 | Add "Vision" headers to unimplemented specs | ✅ |

---

## Spec Reconciliation — Detailed Steps

### Task 7: Add Status Markers to All Specs

For each spec in `openspec/specs/`, add a status table at the top:

```markdown
## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Basic entity extraction | ✅ Implemented | `learners/graph.py` |
| Authority scoring | 💭 Vision | Spec-only |
| RAG integration | 📐 Designed | In entity-model-unification change |
```

**Specs requiring status markers (prioritized):**
1. `knowledge-graph/spec.md` — heavy mismatch between spec and code
2. `patterns/spec.md` — 9 planned use cases with no implementation
3. `personas/spec.md` — 4 planned personas, theme integration unbuilt
4. `mental-models/spec.md` — constitutional tier not implemented as described
5. `rag/spec.md` — multi-collection and entity-graph retrieval unbuilt
6. `compression/spec.md` — adaptive compression and caching unbuilt
7. `themes/spec.md` — entire system unbuilt
8. `agent-swarms/spec.md` — entire system unbuilt
9. `drm/spec.md` — entire system unbuilt
10. `communication/spec.md` — entire system unbuilt
11. `mobile/spec.md` — entire system unbuilt
12. `publishing/spec.md` — entire system unbuilt
13. `canvas/spec.md` — entire system unbuilt
14. `teaching/spec.md` — frontend incomplete
15. `onboarding/spec.md` — entire system unbuilt
16. `security/spec.md` — Phase 23.5 not started
17. `domains/spec.md` — dynamic configuration unbuilt
18. `analytics/spec.md` — entire system unbuilt
19. `data-autonomy/spec.md` — entire system unbuilt
20. Remaining specs — verify and annotate

### Task 8: Update Architecture Spec

Current `architecture/spec.md` is 80 lines and describes aspirational data flow. Rewrite to:

1. Show actual component diagram (what exists in code)
2. Show actual data flow during `Polly.query()` (the real hot path)
3. Separate "Current Architecture" from "Planned Architecture"
4. List actual storage systems and their schemas
5. Reference the integration audit findings

### Task 9: Add Vision Headers

For each spec where the system has zero implementation, add:

```markdown
> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for [Tier X / Phase Y].
> Other specs should not design integration points against this system until implementation begins.
```

Applies to: `agent-swarms`, `drm`, `mobile`, `communication`, `publishing`, `canvas`, `analytics`, `data-autonomy`, `onboarding`

---

## Implementation Delegation

| Remediation Area | Sibling Change | Priority |
|-----------------|----------------|----------|
| Pattern learner merge | [unified-pattern-engine/](../unified-pattern-engine/) | P0 — Foundation |
| Entity model + knowledge graph | [entity-model-unification/](../entity-model-unification/) | P0 — Foundation |
| Cross-system protocols + learning loops | [integration-contracts/](../integration-contracts/) | P1 — Depends on P0 |
| Library extraction / modularization | [library-extraction/](../library-extraction/) | P2 — Depends on P1 |

---

## Relationship to Existing Changes

This audit subsumes or overlaps with parts of:

- **core-framework-refinement**: Pattern→Routing integration, PIL expansion, SKILL↔Mental Model bridge
  - These are now addressed more comprehensively in `integration-contracts/` and `unified-pattern-engine/`
  - The core-framework-refinement change remains authoritative for: Provider Registry, "Polly" mode routing, Query Decomposition, BookLore, RAG Optimization
  
- **spec-integration-2026-02**: Spec reconciliation
  - Subsumed by Task 7–9 in this document
