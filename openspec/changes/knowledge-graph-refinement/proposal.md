# Knowledge Graph Refinement — Proposal

**Date**: 2026-02-18  
**Status**: Proposed  
**Priority**: P1 — Critical UX improvement  
**Depends On**: knowledge-graph-navigation (partially implemented)

---

## Problem Statement

The knowledge graph visualization is currently unusable in its default state due to four critical issues:

### 1. Tight Clustering Problem
The graph opens with all nodes overlapping in a dense cluster at the center, making it impossible to read individual nodes or see their connections. The force-directed layout uses `gravity: 40` which aggressively pulls everything to the center, and node sizes (12-36px) are too small to differentiate at default zoom.

**Impact**: Users cannot use the graph visualization without extensive manual repositioning. First impression is "broken."

### 2. No Edge Type Visualization/Control
While edge types are visually differentiated (references are solid gray, mentions are dashed blue, shared tags are dotted green), there is no legend explaining what these visual differences mean, and no way to toggle specific edge types on/off to reduce visual complexity.

**Impact**: Users don't understand what connections mean and cannot filter out noise (e.g., hide weak shared-tag connections to focus on explicit references).

### 3. Incomplete Filter System
- Domain filter is disabled ("Coming soon" placeholder)
- No content type filter (notes vs. conversations vs. books)
- No authority threshold filter
- Ghost node toggle is non-functional (TODO in code)

**Impact**: Users cannot explore subsets of their knowledge graph or focus on high-quality notes.

### 4. Barebones Garden View
The Garden tab only lists isolated notes and has a backfill button. None of the designed features exist:
- No connection suggestions ("X is mentioned in Y but not linked")
- No merge candidates ("These notes overlap 80%")
- No enrichment queue or batch enrichment tools
- No pruning tools for weak connections or stale entities
- No maintenance statistics dashboard

**Impact**: Users have no way to actively curate and improve their knowledge graph. The garden is read-only when it should be a maintenance workspace.

---

## Goals

1. **Make the graph immediately usable** — Nodes spread out on first load, readable without manual intervention
2. **Add edge type legend and toggles** — Users can understand and control what connections are shown
3. **Implement all designed filters** — Domain, type, authority, and functional ghost toggle
4. **Build the full Garden experience** — Connection suggestions, merge candidates, enrichment, pruning, stats

---

## Non-Goals

- Redesigning the overall navigation model (that's knowledge-graph-navigation)
- Changing the backend graph data structure (EntityStore, relationships, authority scoring)
- Adding new entity extraction capabilities beyond triggering what already exists

---

## Success Criteria

1. Graph opens with nodes spread across the canvas, readable at default zoom (no overlapping labels for authority > 0.6)
2. Edge legend visible in Filters panel; toggling edge types hides/shows them instantly
3. All filter controls functional (domain dropdown populated, type checkboxes, authority slider, ghost toggle)
4. Garden view shows at least 5 actionable sections: Stats, Connection Suggestions, Merge Candidates, Isolated Notes (enhanced), Enrichment Queue
5. Users can add/remove connections via UI (Details panel + drag-to-link + right-click edge menu)
6. Pruning tools accessible and functional (weak connections, stale entities)

---

## User Stories

**As a user with 50+ notes**, I want the graph to spread out automatically so I can see the structure of my knowledge without manually dragging nodes apart.

**As a user exploring my graph**, I want to understand what the different line styles mean so I can distinguish between explicit links and inferred connections.

**As a user with multiple domains**, I want to filter the graph to just my "Signals" domain so I can focus on one area of my knowledge.

**As a user maintaining my knowledge base**, I want to see notes that are mentioned but not linked so I can create explicit connections where they make sense.

**As a user with duplicate content**, I want merge suggestions so I can consolidate overlapping notes and reduce clutter.

**As a user with old notes**, I want to re-run entity extraction on notes that lack entities so my graph becomes more connected over time.

**As a user managing connections**, I want to remove weak or incorrect connections so my graph stays high-quality.

---

## Technical Approach Summary

### Phase 1: Layout Fix (Immediate Impact)
- Register and use `cytoscape-cose-bilkent` plugin (already installed but unused)
- Tune layout params: `gravity: 0.25` (down from 40), `idealEdgeLength: 200` (up from 150)
- Increase node size range to 16-48px (up from 12-36px)

### Phase 2: Edge Legend & Toggles
- Add visual legend to Filters panel showing each edge type with its color/dash pattern
- Wire checkbox toggles that set `display: none` on edges via Cytoscape styles
- Fix ghost toggle to actually hide/show ghost nodes

### Phase 3: Filter Implementation
- Enable domain filter (populate from existing `graphDomainColors`)
- Add content type checkboxes, authority slider
- Create unified `applyGraphFilters()` that re-fetches graph data with filter params

### Phase 4: Backend Garden Endpoints
Six new endpoints in `server.py`:
- `GET /polly/graph/garden/stats` — maintenance stats (total notes, connections, coverage, etc.)
- `GET /polly/graph/garden/suggestions` — connection suggestions + merge candidates
- `POST /polly/graph/garden/enrich` — trigger entity extraction (single or batch)
- `POST /polly/graph/garden/connection` — add/remove connections
- `POST /polly/graph/garden/merge` — merge entity mentions from source notes to target
- `DELETE /polly/graph/garden/prune` — remove weak connections, stale entities, or specific items

### Phase 5: Garden UI Redesign
Completely rewrite `loadGardenView()` to render:
- Stats dashboard (cards + coverage bar)
- Connection suggestions (with accept/dismiss)
- Merge candidates (with merge dialog)
- Enhanced isolated notes (per-item actions)
- Enrichment queue (unenriched notes with enrich buttons)
- Prune tools (expandable section)

### Phase 6: Connection Management UI
- Populate Details panel on node select (connections list, entities, actions)
- "Connect to..." button that enters connection mode (click target, choose type)
- Drag-to-link as alternative interaction
- Right-click edge menu (remove, strengthen, weaken)

---

## Risks & Mitigations

**Risk**: cose-bilkent layout might not work or be slower than built-in cose  
**Mitigation**: Package already installed, well-maintained, designed for this use case. Easy to revert to tuned cose params if needed.

**Risk**: Backend garden endpoints might be slow with large note collections  
**Mitigation**: All endpoints have `limit` params. Suggestions computed on-demand (not precomputed). Enrichment capped at 50 notes per call.

**Risk**: Garden UI complexity might overwhelm users  
**Mitigation**: Sections are collapsible/expandable. Stats dashboard always visible, advanced tools (prune) hidden behind `<details>`.

**Risk**: Connection management might create invalid graph state  
**Mitigation**: All connection changes go through backend validation. EntityStore ensures data integrity.

---

## Timeline Estimate

- Phase 1 (Layout): 1.5 hours
- Phase 2 (Edge legend): 2.5 hours  
- Phase 3 (Filters): 3 hours
- Phase 4 (Backend): 10 hours
- Phase 5 (Garden UI): 9 hours
- Phase 6 (Connection mgmt): 5 hours
- CSS + Polish: 2 hours

**Total: ~33 hours** (4-5 working days)

---

## Related Work

- **knowledge-graph-navigation** — Navigation model, Browse list, filtered views (designed, partially implemented)
- **entity-model-unification** — EntityStore, SQLite schema, authority scoring (complete)
- **Phase 12** — Initial Cytoscape.js integration (complete)

This change builds on top of the existing graph infrastructure. It refines the visualization and adds missing garden maintenance features that were designed but never built.

---

## Open Questions

1. Should merge candidates be auto-generated or manually triggered? → **Auto-generated on garden load, limited to top 20**
2. Should enrichment run synchronously or async? → **Async with progress indicator for batch; synchronous for single notes**
3. Should connection removal be soft delete (strength=0) or hard delete? → **Soft delete (reversible)**
4. Should we add a "confidence" threshold filter for edges? → **Yes, add to authority slider as "Min Quality" combining authority + edge strength**

---

## Approval

Once approved, implementation follows the detailed plan in `design.md` and task breakdown in `tasks.md`.
