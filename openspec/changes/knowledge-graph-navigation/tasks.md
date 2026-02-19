# Knowledge Graph Navigation — Tasks

**Last Updated:** February 2026
**Priority:** P1 — Ships after cursor-ui-pattern-migration Phases 1-2
**Estimated Effort:** 2.5–3.5 weeks
**Depends On:** entity-model-unification (✅ Done), cursor-ui-pattern-migration Phases 1-2

---

## Task Overview

| # | Task | Est. | Status | Phase |
|---|------|------|--------|-------|
| 0 | Dead code pruning (~650 lines) | 0.5d | ☐ | Prep |
| 1 | Fix broken existing endpoints and wiring | 1d | ☐ | Prep |
| 2 | Wire entity extraction into note save path | 0.5d | ✅ | Backend |
| 3 | Implement `/polly/graph/list` endpoint | 1.5d | ✅ | Backend |
| 4 | Implement `/polly/graph/nodes` endpoint | 1.5d | ✅ | Backend |
| 5 | Implement `/polly/graph/state` endpoint | 0.5d | ✅ | Backend |
| 6 | Implement missing notes endpoints (search, tags, move, rename, folders, append) | 1.5d | ✅ | Backend |
| 7 | Add graph ribbon button and view container | 0.5d | ✅ | Frontend |
| 8 | Build shared Browse list component (`updateBrowseList()`) | 1.5d | ✅ | Frontend |
| 9 | Build lower collapsible panel component | 1d | ✅ | Frontend |
| 10 | Refactor Notes page sidebar | 1.5d | ✅ | Frontend |
| 11 | Build Graph page (Cytoscape.js canvas + sidebar) | 3d | ✅ | Frontend |
| 12 | Implement navigation wiring (click-to-open, back-to-graph, cross-highlighting) | 1d | ✅ | Frontend |
| 13 | CSS: Replace file-tree styles, add graph + browse + lower panel styles | 1d | ✅ | Frontend |
| 14 | Integration testing and polish | 1.5d | ✅ | Polish |
| 15 | Update OpenSpec specs | 0.5d | 🔄 | Specs |

**Implementation Note (Feb 2026):** Tasks 2–14 were implemented as part of the knowledge-graph-navigation and knowledge-graph-refinement development cycles. The code for all backend endpoints, frontend graph page, Cytoscape.js integration, Browse list, Garden view, filters, and CSS exists and is functional. Tasks 0–1 (prep/cleanup) were not formally executed as separate steps but much of the cleanup happened organically during implementation. Task 15 (spec updates) is in progress.

---

## Phase: Prep (Tasks 0–1)

Clean the codebase before building on it. These tasks have zero functional change — they only remove dead code and fix bugs that exist today.

### Task 0: Dead Code Pruning (~650 lines in notes-manager.js, ~165 lines CSS/HTML)

**Files:** `electron-app/src/renderer/notes-manager.js`, `electron-app/src/renderer/styles/notes.css`, `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/index.html`

**notes-manager.js — delete these functions:**

| Function | Lines | Why Dead |
|----------|-------|----------|
| `setupSidebarViewToggle()` | 1801–1810 | Queries `.sidebar-view-btn` elements that don't exist in DOM. Never executes. |
| `switchSidebarView(viewName)` | 1815–1848 | Only called by `setupSidebarViewToggle()`. Toggles `.notes-sidebar-view` elements that don't exist. |
| `enterEditMode(cursorPos)` | 1061–1080 | References `#notes-editor-view` and `#notes-editor-textarea` — legacy pre-CM6 elements removed from HTML. |
| `exitEditMode()` | 1085–1108 | Same — calls `renderMarkdown()` which also targets missing elements. |
| `calculateCursorPositionFromClick()` | 1113–1204 | 90 lines of DOM-walking for click-to-edit in rendered markdown. Dead with CM6. |
| `renderMarkdown(markdown)` | 640–704 | Targets `#notes-editor-view` which doesn't exist. CM6 live preview replaced this. |
| `scrollToHeading(heading)` | 1009–1034 | Targets `#notes-editor-view`. Replaced by `scrollToLine()` for CM6. |
| `setupWikiLinkHandlers(container)` | 1039–1056 | Only called from `renderMarkdown()`. CM6 handles wiki-links via `onWikiLinkClick`. |
| `showNoteSuggestions()` | 3342–3399 | Legacy textarea wiki-link autocomplete. CM6 has its own. |
| `updateNoteSuggestions()` | 3404–3516 | Same — 110 lines of dead textarea autocomplete. |
| `navigateSuggestions()` | 3521–3539 | Same. |
| `insertSelectedSuggestion()` | 3544–3561 | Same. |
| `insertNoteName()` | 3566–3630 | Same. |
| `hideNoteSuggestions()` | 3635–3642 | Same. |
| `escapeHtml()` (duplicate at line 2621) | 2621–2625 | Exact duplicate of the one at line 1933. |
| `addToRecent(note)` | 2471–2473 | Stub — body is `// TODO`. Called from `openNote()` but does nothing. |

- [ ] Delete all functions listed above
- [ ] Remove `editorMode` state property from `constructor()` (line 18) — set to `'view'`, immediately overridden by CM6
- [ ] Remove `setupSidebarViewToggle()` call from `init()` (line ~43–76)
- [ ] Remove `addToRecent(note)` call from `openNote()` (preserve the call site comment if useful)
- [ ] Verify `processNoteEmbeds()` (711–803) and `processCallouts()` (809–867) are not called by CM6 before deleting — only delete if confirmed dead

**notes.css — delete:**
- [ ] Lines 460–513: `.notes-right-sidebar`, `.notes-sidebar-backlinks`, `.notes-sidebar-tags` — right sidebar was removed from HTML (comment at index.html:2087–2088), these 50+ lines have no matching DOM

**main.css — delete:**
- [ ] Lines 2284–2376: `.legacy-right-sidebar` — force-hidden with `display: none !important`, backward compat only

**index.html — delete:**
- [ ] Lines 124–149: Static left sidebar nav-items — immediately overwritten by `updateLeftSidebar()` on first `showView()` call
- [ ] Lines 2284–2377: Legacy right sidebar HTML (already force-hidden)

### Task 1: Fix Broken Existing Endpoints and Wiring

**Files:** `interfaces/server.py`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/notes-manager.js`

These bugs exist today, independent of the graph navigation change. Fix them now so we build on a solid foundation.

- [ ] **Fix `/polly/notes/{note_name}/backlinks` endpoint** (server.py ~line 3257): Currently references `note.links` which doesn't exist on `NoteInfo`. Should use `BacklinksIndex.get_backlinks(note_name)` from `core/backlinks.py`
- [ ] **Fix `/polly/stats` graph data** (server.py ~line 1096): Currently returns `'graph': {'entities': '?', 'relationships': '?'}` (placeholder). Should call `entity_store.get_stats()` to return real counts
- [ ] **Fix refresh button** (app.js ~line 3239): Calls `window.notesManager.loadNotes()` which doesn't exist. Should be `window.notesManager.loadNotesIndex()`
- [ ] **Fix `showError()`** (notes-manager.js line 2449–2452): Should call `showToast(message, 'error')` instead of just `console.error()`
- [ ] **Remove dead `sidebar-ribbon-change` event dispatch** (app.js lines 3154–3157): Event is dispatched but nothing listens for it. Either wire it up or remove it.

---

## Phase: Backend (Tasks 2–6)

Backend work ships first. All new endpoints are additive — no existing endpoints change (except the fixes in Task 1).

### Task 2: Wire Entity Extraction into Note Save Path — ✅ COMPLETE

**Files:** `interfaces/server.py` (PUT `/polly/notes/update` ~line 3193), `core/entities/extractor.py`, `core/entities/store.py`

Currently, entity extraction only runs during LLM queries (`core/polly.py` query pipeline). The `entity_mentions` table only has `source_type="query"` records. For `/polly/graph/list` to work, entities must be extracted from note content on save.

- [x] In `PUT /polly/notes/update` handler (server.py ~line 3291-3309), after successful note save, call entity extraction **non-blocking** (background task)
- [x] Add `source_type="note"` support to `EntityExtractor.extract_and_store()`
- [x] Verify `entity_mentions` table correctly records note→entity links with `source_type="note"` and `source_id=note_name`
- [x] Add backfill mechanism: `POST /polly/graph/backfill` endpoint (server.py:3330)

**Verification:** After saving a note, query `entity_mentions WHERE source_type='note'` and confirm entities appear.

### Task 3: Implement `/polly/graph/list` Endpoint — ✅ COMPLETE

**Files:** `interfaces/server.py` (server.py:3395), `core/entities/store.py`, `core/notes_index.py`, `core/backlinks.py`, `core/tags_index.py`

This is the primary endpoint that powers both the Notes sidebar and the Graph page Browse tab.

**Implemented at server.py:3395** with full filter/sort support, entity enrichment, domain counts, and connection status computation.

- [x] Add route to server.py
- [x] Implement join logic: NoteInfo + EntityStore + BacklinksIndex + TagsIndex
- [x] Implement filter parameters
- [x] Implement sort parameters (authority sort requires entity join)
- [x] Implement `connection_status` computation: hub (>10 connections), bridge (connects 2+ domains with few internal connections), isolated (0–2 connections), normal (everything else)
- [x] Implement `domain_counts` aggregation in response
- [x] Handle edge case: notes with zero entity mentions (newly created, extraction not yet run) — include them with `connection_count: 0`, `connection_status: "isolated"`

**Route definition:**
```python
@app.get("/polly/graph/list")
async def get_graph_list(
    type: str = None,          # comma-separated: "note,conversation"
    domain: str = None,        # matches primary or secondary
    maturity: int = None,      # 10, 20, 30
    sort: str = "recent",      # authority, recent, alpha, created
    connection_status: str = None,  # hub, bridge, isolated, all
    q: str = None,             # text search
    limit: int = 100,
    offset: int = 0
):
```

**Response shape (from design.md):**
```python
{
    "items": [{
        "id": "...",
        "name": "Docker Deployment Guide",
        "type": "note",
        "primary_domain": "sigils",
        "secondary_domains": ["signals"],
        "authority_score": 0.82,
        "connection_count": 17,
        "inbound_count": 12,
        "outbound_count": 5,
        "connection_status": "hub",
        "maturity": 20,
        "tags": ["docker", "deployment"],
        "updated_at": "2026-02-15T...",
        "created_at": "2026-01-10T...",
        "path": "/path/to/notes/sigils/docker.md",
        "preview_snippet": "First 100 chars..."
    }],
    "total_count": 45,
    "domain_counts": {"sigils": 12, "signals": 8}
}
```

- [ ] Add route to server.py
- [ ] Implement join logic: NoteInfo + EntityStore + BacklinksIndex + TagsIndex
- [ ] Implement filter parameters
- [ ] Implement sort parameters (authority sort requires entity join)
- [ ] Implement `connection_status` computation: hub (>10 connections), bridge (connects 2+ domains with few internal connections), isolated (0–2 connections), normal (everything else)
- [ ] Implement `domain_counts` aggregation in response
- [ ] Handle edge case: notes with zero entity mentions (newly created, extraction not yet run) — include them with `connection_count: 0`, `connection_status: "isolated"`

**Verification:** `curl localhost:PORT/polly/graph/list?sort=authority&limit=10` returns enriched note data.

### Task 4: Implement `/polly/graph/nodes` Endpoint — ✅ COMPLETE

**Files:** `interfaces/server.py` (server.py:3628), `core/entities/store.py`

Powers the Cytoscape.js graph canvas. Uses EntityStore's already-built graph operations.

**Implemented at server.py:3628** with full-graph mode, center-node mode, ghost computation, and filter support.

- [x] Add route to server.py
- [x] Implement full-graph mode: query all entities matching filters, all relationships between them
- [x] Implement center-node mode: use `EntityStore.get_related(center_node, max_hops=hops)` for neighborhood exploration
- [x] Implement ghost computation: when filters are active and `include_ghosts=True`, include filtered-out nodes within 1–2 hops of visible nodes with `is_ghost: true`
- [x] Return response shape from design.md: `{ nodes: [...], edges: [...], total_node_count, ghost_count }`
- [x] Add `is_ghost` boolean to each node and edge in response
- [x] Performance: cap ghost computation at reasonable limits

**Route definition:**
```python
@app.get("/polly/graph/nodes")
async def get_graph_nodes(
    type: str = None,          # Content type filter
    domain: str = None,        # Domain filter
    maturity: int = None,
    authority_min: float = None,
    confidence_min: float = None,
    center_node: str = None,   # "Explore From Here" — return N-hop neighborhood
    hops: int = 2,
    include_ghosts: bool = True,
    limit: int = 500,
    offset: int = 0
):
```

- [ ] Add route to server.py
- [ ] Implement full-graph mode: query all entities matching filters, all relationships between them
- [ ] Implement center-node mode: use `EntityStore.get_related(center_node, max_hops=hops)` for neighborhood exploration
- [ ] Implement ghost computation: when filters are active and `include_ghosts=True`, include filtered-out nodes within 1–2 hops of visible nodes with `is_ghost: true`. Use `get_related()` on each visible node, mark any filtered-out neighbors as ghosts.
- [ ] Return response shape from design.md: `{ nodes: [...], edges: [...], total_node_count, ghost_count }`
- [ ] Add `is_ghost` boolean to each node and edge in response
- [ ] Performance: cap ghost computation at reasonable limits (e.g., max 100 ghosts)

**Verification:** `curl localhost:PORT/polly/graph/nodes?center_node=ENTITY_ID&hops=2` returns nodes + edges.

### Task 5: Implement `/polly/graph/state` Endpoint — ✅ COMPLETE

**Files:** `interfaces/server.py` (GET: server.py:4663, POST: server.py:4699)

Simple key-value persistence for graph view state (position, zoom, filters, layout).

- [x] Add POST route — save state
- [x] Add GET route — return state or `null`
- [x] State shape: `{ position: {x, y}, zoom, filters: {domain, type, maturity}, expanded_nodes: [], layout: "force-directed" }`

### Task 6: Implement Missing Notes Endpoints — ✅ COMPLETE

**Files:** `interfaces/server.py`, `core/notes_index.py`, `core/tags_index.py`

All 7 missing endpoints have been implemented:

| Endpoint | Server Location |
|----------|----------------|
| `GET /polly/notes/search` | server.py:4741 |
| `GET /polly/notes/tags` | server.py:4784 |
| `GET /polly/notes/tags/{tag}` | server.py:4817 |
| `POST /polly/notes/move` | server.py:4944 |
| `POST /polly/notes/rename` | server.py:5019 |
| `GET /polly/notes/folders` | server.py:4859 |
| `POST /polly/notes/append` | server.py:4888 |

- [x] `GET /polly/notes/search?q=X&limit=N`
- [x] `GET /polly/notes/tags`
- [x] `GET /polly/notes/tags/{tag}`
- [x] `POST /polly/notes/move`
- [x] `POST /polly/notes/rename`
- [x] `GET /polly/notes/folders`
- [x] `POST /polly/notes/append`

---

## Phase: Frontend (Tasks 7–13)

Frontend work builds on backend endpoints. Tasks 7–9 are reusable infrastructure. Tasks 10–12 are page-specific.

### Task 7: Add Graph Ribbon Button and View Container — ✅ COMPLETE

**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`

**index.html:**
- [x] Add graph button to `#icon-ribbon` (index.html:95, `data-view="graph"`)
- [x] Add graph view container (index.html:2189, `#view-graph`) with Cytoscape.js canvas container div

**app.js:**
- [x] Add `graph` entry to `sidebarRibbonConfigs`
- [x] Add `graph` case to `showView()`
- [x] Add `graph` entry to `sidebarConfigs` in `updateLeftSidebar()`
- [x] Add `graph` case to `updateLeftSidebar()` setTimeout handler block

### Task 8: Build Shared Browse List Component (`updateBrowseList()`) — ✅ COMPLETE

**Files:** `electron-app/src/renderer/notes-manager.js`

Implemented at notes-manager.js:898 (`updateBrowseList()`). Calls `/polly/graph/list` with filter/sort state. Used by both Notes sidebar (`#notes-browse-list`) and Graph page Browse tab (`#graph-browse-list`).

- [x] Write `updateBrowseList(container, options)` method in notes-manager.js
- [x] Implement type icon rendering
- [x] Implement hover metadata display: connection count, authority badge, secondary domain color dots
- [x] Implement sort controls: authority, recent, alpha, created
- [x] Implement filter state management
- [x] Handle empty state
- [x] Handle loading state
- [x] Wire search input

### Task 9: Build Lower Collapsible Panel Component — ✅ COMPLETE

**Files:** `electron-app/src/renderer/app.js`, CSS files

Reusable collapsible panel implemented. Used by both Notes sidebar and Graph sidebar for Filters/Details/Backlinks/Tags/TOC tabs.

- [x] Write `renderLowerPanel(view, tabs)` in app.js
- [x] Implement collapse/expand
- [x] Persist collapsed/expanded state per view
- [x] Implement tab switching within the panel
- [x] Wire tab content rendering

### Task 10: Refactor Notes Page Sidebar — ✅ COMPLETE

**Files:** `electron-app/src/renderer/notes-manager.js`, `electron-app/src/renderer/app.js`

Notes sidebar now uses graph-enriched Browse list (`updateBrowseList()`) instead of file tree. Lower panel provides Filters/Backlinks/Tags/TOC tabs.

- [x] Modify `constructor()`: updated filter state for browse list
- [x] Modify `init()`: initialization for lower panel and browse list
- [x] Modify `loadNotesIndex()`: calls `updateBrowseList()` instead of `updateFileTree()`
- [x] Retarget `updateBacklinksPanel()` to lower panel
- [x] Retarget `updateTagsPanel()` to lower panel
- [x] Retarget `updateTOCPanel()` to lower panel
- [x] App.js sidebar configs updated for Browse list + lower panel

### Task 11: Build Graph Page (Cytoscape.js Canvas + Sidebar) — ✅ COMPLETE

**Files:** `electron-app/src/renderer/app.js`, `electron-app/src/renderer/index.html`, `package.json`

Complete Graph page with Cytoscape.js canvas, sidebar (Browse + Garden tabs), filters panel, details panel, and Garden view with maintenance tools.

**Key implementations:**
- [x] Cytoscape.js + cytoscape-cose-bilkent dependencies added
- [x] `renderGraphSidebar()` — Browse tab + Garden tab (app.js:17593)
- [x] `initGraphPage()` — Cytoscape.js init, data fetch, state restore, event handlers (app.js:17819)
- [x] `renderGraphFiltersPanel()` — Domain, type, maturity, edge type toggles, ghost toggle (app.js:18964)
- [x] `renderGraphDetailsPanel()` — Node details on selection (app.js:19320)
- [x] Node visual encoding: shape by type, size by authority, color by domain
- [x] Edge rendering: thickness by strength, style by relationship type
- [x] Node hover tooltips, click handlers, right-click context menus
- [x] "Explore From Here" neighborhood expansion
- [x] Canvas pan/zoom with debounced state save
- [x] Filter change → re-fetch with ghost node support
- [x] Ghost nodes at opacity 0.15 with dotted edges
- [x] Garden view with 6 sections: stats, suggestions, enrich, connection, merge, prune (app.js:19337+)
- [x] `loadGardenStats()` (app.js:19344), `loadGardenSuggestions()` (app.js:19432)
- [x] Garden maintenance actions: prune, enrich, merge, connection (app.js:19663-19867)
- [x] Layout options: cose-bilkent (default), concentric, hierarchical
- [x] 6 Garden API endpoints: stats, suggestions, enrich, connection, merge, prune

### Task 12: Implement Navigation Wiring — ✅ COMPLETE

**Files:** `electron-app/src/renderer/app.js`, `electron-app/src/renderer/notes-manager.js`

Bidirectional navigation between graph, list, and item views is wired up.

- [x] Click-to-open from graph: Node click → save graph state → open item
- [x] "Back to Graph" button: floating button returns to graph with restored state
- [x] Click-to-open from list: Browse list item click → open note
- [x] Cross-highlighting: active note highlighted in graph
- [x] Graph state management via `graphState` object (app.js:17880)
- [x] List-to-graph highlight: selecting note in Browse list centers graph on corresponding node

### Task 13: CSS — ✅ COMPLETE

**Files:** `electron-app/src/renderer/styles/notes.css`, `electron-app/src/renderer/styles/main.css`

Graph page CSS, browse list styles, lower panel styles, garden tab styles, and ghost node styling all implemented in main.css:7175+.

- [x] Browse list styles
- [x] Lower panel styles
- [x] Graph page styles (canvas container, tooltips, context menus)
- [x] Garden tab styles
- [x] Ghost node Cytoscape.js styling
- [x] Edge type legend and toggle CSS

---

## Phase: Polish (Task 14)

### Task 14: Integration Testing and Polish — ✅ COMPLETE

**Files:** All

- [x] Test full flow: open app → click Graph → see nodes → click node → editor opens → "Back to Graph" returns to same state
- [x] Test Notes sidebar: search, filter by domain, filter by tag, sort by authority, open note, backlinks panel, tags panel, TOC panel
- [x] Test Browse list shared behavior: same data in Notes sidebar and Graph Browse tab
- [x] Test edge cases: empty graph, single note, note with zero connections
- [x] Test ghost nodes: apply filter → verify ghosts appear at low opacity → verify toggle hides them
- [x] Test performance: 100+ notes, 500+ nodes
- [x] Test state persistence: close and reopen graph → verify position/zoom/filters restored
- [x] Test lower panel: collapse/expand, tab switching, content updates
- [x] Test cross-change compatibility
- [x] Verify notes operations: create, save, rename, move

---

## Phase: Specs (Task 15)

### Task 15: Update OpenSpec Specs

**Files:** `openspec/specs/ui/spec.md`, `openspec/specs/notes/spec.md`, `openspec/specs/knowledge-graph/spec.md`, `openspec/specs/design/spec.md`, `openspec/specs/capture/spec.md`

Update specs to reflect implemented reality (per design.md "Spec Updates Required" section):

- [ ] **ui/spec.md:** Knowledge Graph page moves from "Planned" to implemented. Notes page sidebar description updated. Add "Back to Graph" floating button pattern. Add lower collapsible panel pattern.
- [ ] **notes/spec.md:** Add "Graph-Filtered Navigation" section. Update Knowledge Cards for maturity-gated structure. Add non-blocking save suggestions. Remove file-tree as primary navigation description.
- [ ] **knowledge-graph/spec.md:** Add "Navigation Model" section. Update "Dual Hierarchy" for filtered list + primary/secondary domains. Add "Maturity-Gated Structure", "Garden View", ghosting behavior. Reference this change.
- [ ] **design/spec.md:** Add Recall.ai as a named design inspiration.
- [ ] **capture/spec.md:** Note that captures appear as secondary nodes in the graph.

---

## Verification Criteria

1. **Graph page renders** with real entity data — nodes, edges, domain colors, authority-based sizing
2. **Browse list** in Notes sidebar shows graph-enriched data from `/polly/graph/list` — not the old file tree
3. **Same data** appears in Notes sidebar Browse list and Graph page Browse tab
4. **Lower panel** works in both Notes and Graph sidebars — collapsible, tab-switching, content updating
5. **Click-to-open** from graph canvas transitions to item viewer with "Back to Graph" button
6. **"Back to Graph"** restores exact graph state (position, zoom, filters, expanded neighborhoods)
7. **Filters** work: domain, type, maturity, connection_status — in both list and graph views
8. **Ghost nodes** appear at low opacity within 1–2 hops of visible nodes when filters active
9. **Entity extraction** runs on note save — `entity_mentions` table has `source_type='note'` records
10. **All existing notes operations** still work: create, save, rename, search, quick switcher
11. **~815 lines** of dead code removed (Task 0)
12. **9 broken/missing endpoints** fixed or implemented (Tasks 1 + 6)
13. **No regressions** in cursor-ui-pattern-migration layout infrastructure

---

## Cross-Change Coordination Notes

**cursor-ui-pattern-migration (CUI) must ship Phases 1–2 first:**
- CUI provides: collapsible sidebar infrastructure, main content + chat panel split, sidebar content router
- KGN consumes: sidebar container for graph page, main content area for graph canvas

**CUI Task 2.3 (Notes Page Left Sidebar) should be minimal:**
- CUI should wrap existing notes sidebar content in new container, NOT redesign it
- KGN Task 10 will replace the content entirely with Browse list + lower panel

**4 HIGH conflicts (audit.md Section 8):**
1. `sidebarRibbonConfigs.notes` — KGN takes precedence for content
2. `updateFileTree()` — KGN replaces entirely
3. `#notes-file-tree-container` + CSS — KGN replaces
4. `updateLeftSidebar()` notes entry — KGN takes precedence for content, CUI for infrastructure

---

## Total Estimated Time

**Approximately 60–80 hours** (2.5–3.5 weeks for one developer)

Backend (Tasks 2–6): ~5.5 days
Frontend (Tasks 7–13): ~9.5 days
Prep + Polish + Specs: ~4 days
