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
| 2 | Wire entity extraction into note save path | 0.5d | ☐ | Backend |
| 3 | Implement `/polly/graph/list` endpoint | 1.5d | ☐ | Backend |
| 4 | Implement `/polly/graph/nodes` endpoint | 1.5d | ☐ | Backend |
| 5 | Implement `/polly/graph/state` endpoint | 0.5d | ☐ | Backend |
| 6 | Implement missing notes endpoints (search, tags, move, rename, folders, append) | 1.5d | ☐ | Backend |
| 7 | Add graph ribbon button and view container | 0.5d | ☐ | Frontend |
| 8 | Build shared Browse list component (`updateBrowseList()`) | 1.5d | ☐ | Frontend |
| 9 | Build lower collapsible panel component | 1d | ☐ | Frontend |
| 10 | Refactor Notes page sidebar | 1.5d | ☐ | Frontend |
| 11 | Build Graph page (Cytoscape.js canvas + sidebar) | 3d | ☐ | Frontend |
| 12 | Implement navigation wiring (click-to-open, back-to-graph, cross-highlighting) | 1d | ☐ | Frontend |
| 13 | CSS: Replace file-tree styles, add graph + browse + lower panel styles | 1d | ☐ | Frontend |
| 14 | Integration testing and polish | 1.5d | ☐ | Polish |
| 15 | Update OpenSpec specs | 0.5d | ☐ | Specs |

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

### Task 2: Wire Entity Extraction into Note Save Path

**Files:** `interfaces/server.py` (PUT `/polly/notes/update` ~line 3193), `core/entities/extractor.py`, `core/entities/store.py`

Currently, entity extraction only runs during LLM queries (`core/polly.py` query pipeline). The `entity_mentions` table only has `source_type="query"` records. For `/polly/graph/list` to work, entities must be extracted from note content on save.

- [ ] In `PUT /polly/notes/update` handler (server.py ~line 3193), after successful note save, call `entity_extractor.extract_and_store(content, source_type="note", source_id=note_name, domains=[domain])` **non-blocking** (fire-and-forget or background thread)
- [ ] Add `source_type="note"` support to `EntityExtractor.extract_and_store()` if not already handled (extractor.py ~line 50)
- [ ] Verify `entity_mentions` table correctly records note→entity links with `source_type="note"` and `source_id=note_name`
- [ ] Add a one-time backfill mechanism: endpoint or management command that iterates all indexed notes and runs entity extraction on each. This populates the graph for existing notes. (Can be `GET /polly/graph/backfill` or a CLI command.)

**Verification:** After saving a note, query `entity_mentions WHERE source_type='note'` and confirm entities appear.

### Task 3: Implement `/polly/graph/list` Endpoint

**Files:** `interfaces/server.py` (new route), `core/entities/store.py`, `core/notes_index.py`, `core/backlinks.py`, `core/tags_index.py`

This is the primary endpoint that powers both the Notes sidebar and the Graph page Browse tab.

**Query logic:**
1. Start with all notes from `NotesIndex.get_all_notes()` — provides `name`, `title`, `path`, `domain` (primary), `tags`, `created`, `modified`
2. Join with `entity_mentions` WHERE `source_type='note'` to get entity connections per note
3. For each note, compute: `connection_count` (inbound + outbound from `BacklinksIndex`), `authority_score` (from connected entities' authority), `connection_status` (hub/bridge/isolated/normal based on connection patterns)
4. Compute `secondary_domains` via `EntityStore.get_cross_domain_bridges()` — domains connected through shared entities
5. Apply filters: `type`, `domain` (matches primary OR secondary), `maturity`, `connection_status`, `q` (text search)
6. Apply sort: `authority`, `recent` (modified), `alpha` (title), `created`

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

### Task 4: Implement `/polly/graph/nodes` Endpoint

**Files:** `interfaces/server.py` (new route), `core/entities/store.py`

Powers the Cytoscape.js graph canvas. Uses EntityStore's already-built graph operations.

**Leverages existing (unexposed) methods:**
- `EntityStore.get_related(entity_id, max_hops, min_strength)` — BFS traversal for `center_node` + `hops` mode
- `EntityStore.search(EntityQuery)` — for filtering by type/domain
- `EntityStore.recompute_authority()` — authority scores already computed

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

### Task 5: Implement `/polly/graph/state` Endpoint

**Files:** `interfaces/server.py` (2 new routes)

Simple key-value persistence for graph view state (position, zoom, filters, layout). Stored in SQLite or flat JSON file.

```python
@app.post("/polly/graph/state")
async def save_graph_state(body):
    # body: { position, zoom, filters, expanded_nodes, layout }

@app.get("/polly/graph/state")
async def get_graph_state():
    # Returns last saved state or null
```

- [ ] Add POST route — save state to `~/.polly/graph_state.json` or a new SQLite table
- [ ] Add GET route — return state or `null`
- [ ] State shape: `{ position: {x, y}, zoom, filters: {domain, type, maturity}, expanded_nodes: [], layout: "force-directed" }`

### Task 6: Implement Missing Notes Endpoints

**Files:** `interfaces/server.py`, `core/notes_index.py`, `core/tags_index.py`

These endpoints are called by the frontend but don't exist in the backend (audit.md Section 9). They're needed for a functioning Notes page regardless of graph navigation.

| Endpoint | Frontend Caller | Line |
|----------|----------------|------|
| `GET /polly/notes/search` | `notes-manager.js searchNotes()` | 170 |
| `GET /polly/notes/tags` | `notes-manager.js loadTags()` | 294 |
| `GET /polly/notes/tags/{tag}` | `notes-manager.js filterByTag()` | 1976 |
| `POST /polly/notes/move` | `notes-manager.js moveNote()` | 1613 |
| `POST /polly/notes/rename` | `notes-manager.js renameNote()` | 2364 |
| `GET /polly/notes/folders` | `notes-manager.js showCreateNoteModal()` | 2648 |
| `POST /polly/notes/append` | `notes-manager.js appendToSelectedNote()` | 3032 |

- [ ] `GET /polly/notes/search?q=X&limit=N` — delegate to `NotesIndex.search_notes(query, limit)` (already implemented in core)
- [ ] `GET /polly/notes/tags` — delegate to `TagsIndex.get_all_tags()` (already implemented in core)
- [ ] `GET /polly/notes/tags/{tag}` — delegate to `TagsIndex.get_notes_for_tag(tag)` (already implemented in core)
- [ ] `POST /polly/notes/move` — move file on disk, update `NotesIndex`, update `BacklinksIndex`
- [ ] `POST /polly/notes/rename` — rename file on disk, update all wiki-link references, update indexes
- [ ] `GET /polly/notes/folders` — return list of domain folders from notes root
- [ ] `POST /polly/notes/append` — append content to an existing note file

**Note:** Move and rename are the most complex — they need to update file references across all notes that link to the moved/renamed note.

---

## Phase: Frontend (Tasks 7–13)

Frontend work builds on backend endpoints. Tasks 7–9 are reusable infrastructure. Tasks 10–12 are page-specific.

### Task 7: Add Graph Ribbon Button and View Container

**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`

Minimal wiring to make the Graph page addressable. No content yet.

**index.html:**
- [ ] Add graph button to `#icon-ribbon` (after line 88): `<button class="ribbon-item" data-view="graph" title="Graph"><i data-lucide="git-graph"></i></button>`
- [ ] Add graph view container before `</main>` (before line 2179): `<div class="view hidden" id="view-graph"></div>` with a Cytoscape.js canvas container div inside

**app.js:**
- [ ] Add `graph` entry to `sidebarRibbonConfigs` (after line 3060): `graph: { containerClass: "graph-ribbon-buttons", btnClass: "graph-ribbon-btn", buttons: [{ id: "browse", ... }, { id: "garden", ... }] }`
- [ ] Add `graph` case to `showView()` (line 2898–2975): `else if (view === "graph") { initGraphPage(); }`
- [ ] Add `graph` entry to `sidebarConfigs` in `updateLeftSidebar()` (after line 3411): `graph: { title: "Graph", content: renderGraphSidebar() }`
- [ ] Add `graph` case to `updateLeftSidebar()` setTimeout handler block (line 3454–3614) for graph sidebar event wiring

**Verification:** Clicking the graph ribbon icon shows an empty graph page with sidebar structure.

### Task 8: Build Shared Browse List Component (`updateBrowseList()`)

**Files:** `electron-app/src/renderer/notes-manager.js`

This is the component that **replaces** `updateFileTree()` (notes-manager.js lines 1304–1468). It renders a flat filtered list of graph-enriched content items. Used by both the Notes sidebar and the Graph page Browse tab.

**What `updateBrowseList()` does:**
1. Calls `GET /polly/graph/list` with current filter/sort state
2. Renders a flat list (no folder grouping) into a target container
3. Each item shows: type icon (● circle for notes, ◆ diamond for conversations, etc.), title, subtle date
4. On hover: progressive disclosure — connection count, authority indicator, secondary domain dots
5. Click: opens the item (calls `openNote()` for notes, navigates to relevant view for other types)
6. Supports keyboard navigation (arrow keys, Enter to open)

**Implementation:**
- [ ] Write `updateBrowseList(container, options)` method in notes-manager.js — takes a target container element and options (filters, sort, onItemClick callback)
- [ ] Implement type icon rendering: circle (●) for notes, diamond (◆) for conversations, hexagon for books, triangle for captures, square for code
- [ ] Implement hover metadata display: connection count, authority badge, secondary domain color dots
- [ ] Implement sort controls: authority, recent, alpha, created (replaces the old `sortMode` from `updateFileTree()`)
- [ ] Implement filter state management: domain, type, maturity, connection_status — stored in `this.browseFilters`
- [ ] Handle empty state: "No items match filters" with reset-filters action
- [ ] Handle loading state: skeleton items or spinner
- [ ] Wire search input (notes-manager.js `setupEventListeners()` line 1209–1299): search queries pass through to `/polly/graph/list?q=X`

**Replaces:**
- `updateFileTree()` (lines 1304–1468) — delete after `updateBrowseList()` is working
- Sort logic (lines 1400–1430) — subsumed by `/polly/graph/list?sort=X`
- `setupDragAndDrop()` (lines 1534–1600) — delete (no folders to drag into)

### Task 9: Build Lower Collapsible Panel Component

**Files:** `electron-app/src/renderer/app.js` (new `renderLowerPanel()` function), CSS files

A reusable collapsible panel that slides up from the bottom of a sidebar. Used by both the Notes sidebar (Filters/Backlinks/Tags/TOC tabs) and the Graph sidebar (Filters/Details tabs).

**Structure:**
```html
<div class="lower-panel" data-collapsed="true">
  <div class="lower-panel-header">
    <div class="lower-panel-handle">▲</div>  <!-- click or drag to expand -->
  </div>
  <div class="lower-panel-ribbon">
    <button class="lower-panel-tab active" data-tab="filters">Filters</button>
    <button class="lower-panel-tab" data-tab="backlinks">Backlinks</button>
    <!-- ... -->
  </div>
  <div class="lower-panel-content">
    <!-- tab content rendered here -->
  </div>
</div>
```

- [ ] Write `renderLowerPanel(view, tabs)` in app.js — returns HTML string for the panel. `view` determines context ("notes" or "graph"), `tabs` is array of `{id, label}`.
- [ ] Implement collapse/expand: click header toggles, drag handle resizes panel height
- [ ] Persist collapsed/expanded state per view in localStorage
- [ ] Implement tab switching within the panel (sub-ribbon)
- [ ] Wire tab content rendering: each tab calls a render function (e.g., `updateBacklinksPanel()`, `updateTagsPanel()`, `updateTOCPanel()` — already exist in notes-manager.js, just need retargeting)

### Task 10: Refactor Notes Page Sidebar

**Files:** `electron-app/src/renderer/notes-manager.js`, `electron-app/src/renderer/app.js`

Replace the folder-based file tree with the graph-filtered Browse list and add the lower collapsible panel.

**notes-manager.js changes:**

- [ ] **Modify `constructor()` (lines 6–38):** Remove `sortMode`. Add `browseFilters: { domain: null, type: null, maturity: null, sort: 'recent', connectionStatus: null }`, `lowerPanelState: { collapsed: true, activeTab: 'filters' }`, `activeDomainFilter: null`
- [ ] **Modify `init()` (lines 43–76):** Remove `setupSidebarViewToggle()` call (already deleted in Task 0). Add initialization for lower panel and browse list
- [ ] **Modify `loadNotesIndex()` (lines 106–156):** Keep the fetch to `/polly/notes/index` for internal data. Change UI update: call `updateBrowseList()` instead of `updateFileTree()`
- [ ] **Modify `startInlineRename()` (lines 1473–1529):** Update to work with new `.browse-list-item` DOM structure instead of `.file-tree-item`
- [ ] **Retarget `updateBacklinksPanel()` (lines 1705–1748):** Render into lower panel container instead of `#notes-backlinks-panel`
- [ ] **Retarget `updateTagsPanel()` (lines 1753–1796):** Render into lower panel container instead of `#notes-tags-panel`
- [ ] **Retarget `updateTOCPanel()` (lines 1853–1912):** Render into lower panel container instead of `#notes-toc-list`
- [ ] **Retarget `renderEmptyTOC()` (lines 1917–1928):** Update container reference
- [ ] **Modify `filterByTag()` (lines 1973–1989):** Change `updateFileTree()` call to `updateBrowseList()`. Consider routing through `/polly/graph/list?tag=X`
- [ ] **Modify `showCreateNoteModal()` (lines 2630–2717):** Remove hard-coded `'30-Ideas'` default (line 2660). Use most-recent domain or let user pick.
- [ ] **Delete `updateFileTree()`** (lines 1304–1468) — replaced by `updateBrowseList()` from Task 8
- [ ] **Delete `setupDragAndDrop()`** (lines 1534–1600) — no folders to drag into

**app.js changes:**

- [ ] **Modify `sidebarRibbonConfigs.notes`** (lines 2996–3004): Change from `[files, backlinks, tags, toc]` to single `[browse]` tab. Backlinks/Tags/TOC move to lower panel.
- [ ] **Modify `updateLeftSidebar()` notes content** (lines 3301–3332): Replace sort-select + add-button + `#notes-file-tree-container` with Browse list container + lower collapsible panel HTML (using `renderLowerPanel("notes", [{id:"filters",...}, {id:"backlinks",...}, {id:"tags",...}, {id:"toc",...}])`)
- [ ] **Modify `createBrowserRibbon()` for notes** (lines 3101–3133): Remove "collapse-all" button (no folders). Keep sort and refresh.
- [ ] **Fix `setupBrowserRibbonHandlers()` for notes** (lines 3203–3250): Fix refresh to call `loadNotesIndex()`. Remove collapse-all handler.

**Verification:** Notes sidebar shows graph-enriched flat list instead of file tree. Lower panel has Filters/Backlinks/Tags/TOC tabs. All existing notes operations (create, edit, save, rename) still work.

### Task 11: Build Graph Page (Cytoscape.js Canvas + Sidebar)

**Files:** `electron-app/src/renderer/app.js` (new functions), `electron-app/src/renderer/index.html`, `package.json`

The largest task. Builds the entire Graph page.

**Dependencies:**
- [ ] Add `cytoscape` to `package.json` dependencies (npm install cytoscape)
- [ ] Add `cytoscape-cose-bilkent` for improved force-directed layout (optional but recommended)

**app.js — new functions:**

- [ ] **`renderGraphSidebar()`** — Returns HTML for graph page left sidebar: Browse tab content (reuses `updateBrowseList()`), Garden tab content, lower panel with Filters + Details sub-tabs (uses `renderLowerPanel("graph", [{id:"filters",...}, {id:"details",...}])`)
- [ ] **`initGraphPage()`** — Main initialization:
  1. Initialize Cytoscape.js instance in `#graph-canvas-container`
  2. Fetch graph data from `/polly/graph/nodes` (default: no center_node, all nodes up to limit)
  3. Restore last graph state from `/polly/graph/state` (position, zoom, filters)
  4. Render nodes with visual encoding: shape by type, size by authority, color by domain
  5. Render edges: thickness by strength, style by relationship type (solid/dashed/dotted)
  6. Set up event handlers (see below)

**Graph event handlers:**
- [ ] **Node hover:** Show tooltip (name, type, domain, connection count, authority)
- [ ] **Node click:** Save graph state to `/polly/graph/state`, transition to item viewer. Show "Back to Graph" floating button.
- [ ] **Node right-click:** Context menu (Open, Explore From Here, Show connections, Copy link)
- [ ] **"Explore From Here":** Call `/polly/graph/nodes?center_node=ID&hops=2`, merge new nodes into canvas
- [ ] **Canvas pan/zoom:** Standard Cytoscape.js interaction. Save position on significant change (debounced).
- [ ] **Filter changes:** When filters change in lower panel, re-fetch `/polly/graph/nodes` with new filters, update ghost nodes

**Graph rendering rules (from design.md):**
- [ ] Notes: circle, larger, brighter
- [ ] Conversations: diamond, smaller, dimmer
- [ ] Books: hexagon
- [ ] Captures: triangle
- [ ] Code files: square
- [ ] Canvases: rounded rectangle
- [ ] Node size scales with `authority_score` (0.0–1.0 → min–max radius)
- [ ] Edge thickness scales with `weight`
- [ ] Edge style: solid = references, dashed = relates_to, dotted = co_occurs_with
- [ ] Domain coloring: each domain gets a consistent color from a palette
- [ ] Labels: visible at medium zoom, only high-authority at low zoom, all at high zoom
- [ ] Ghost nodes: opacity 0.15, dotted edges at lower opacity. Hover restores full visibility.

**Garden tab content:**
- [ ] Isolated notes (0–2 connections) — data from `/polly/graph/list?connection_status=isolated`
- [ ] Maintenance stats (total orphans, last review date)
- [ ] Suggested merges and connection suggestions — placeholder for now, powered by entity extraction quality metrics later

**Layout options (in Filters tab):**
- [ ] Force-directed (default) — `cose-bilkent` or `cose`
- [ ] Concentric — high-authority nodes at center
- [ ] Hierarchical — tree layout by domain

**Verification:** Graph page renders with nodes and edges. Clicking a node opens it. "Back to Graph" button returns to graph with preserved state. Filters work. "Explore From Here" expands neighborhoods.

### Task 12: Implement Navigation Wiring

**Files:** `electron-app/src/renderer/app.js`, `electron-app/src/renderer/notes-manager.js`

Wire up the bidirectional navigation between graph, list, and item views.

- [ ] **Click-to-open from graph:** Node click in graph canvas → save graph state to sessionStorage (position, zoom, filters, expanded nodes) → call `showView('notes')` or relevant view → open the item → show floating "Back to Graph" button
- [ ] **"Back to Graph" button:** Floating button appears whenever user arrived from graph. Click → `showView('graph')` → restore graph state from sessionStorage → center on previously-clicked node
- [ ] **Click-to-open from list:** Browse list item click in Notes sidebar → open note (existing `openNote()` flow). No "Back to Graph" needed.
- [ ] **Cross-highlighting:** When a note is open in the editor and the user switches to the Graph page, the corresponding node should be highlighted/centered in the graph canvas
- [ ] **Graph state in sessionStorage:** Store `{ position, zoom, filters, expanded_nodes, layout, source_node }` per graph session. Clear on app restart.
- [ ] **List-to-graph highlight:** When user selects a note in the Browse list on the Graph page, highlight and center that node in the canvas

### Task 13: CSS — Replace File-Tree Styles, Add Graph + Browse + Lower Panel Styles

**Files:** `electron-app/src/renderer/styles/notes.css`, `electron-app/src/renderer/styles/main.css`

**notes.css — replace:**
- [ ] Delete lines 108–223: All `.file-tree-folder`, `.file-tree-item`, `.file-tree-folder-header`, `.file-tree-icon`, `.file-tree-rename-input` styles
- [ ] Modify lines 514–613: Keep `.notes-backlinks-item`, `.notes-tag-item` styling but retarget selectors for lower panel containers
- [ ] Modify lines 644–797: Remove `.notes-sidebar-view-toggle`, `.sidebar-view-btn` (dead system). Keep `.toc-*` styles but add lower panel container context.
- [ ] Modify lines 896–977: Remove `.drag-*` styles if drag-and-drop is deleted. Keep `.notes-menu-item`, `.note-embed-*`.
- [ ] Modify lines 1101–1123: Update `@media` responsive rules for new sidebar structure

**main.css — add/modify:**
- [ ] Modify lines 1137–1206: Update `.notes-sidebar-container` for new structure (Browse list + lower panel)
- [ ] Modify lines 1207–1346: Add `.graph-ribbon-buttons`, `.graph-ribbon-btn` selectors alongside existing ribbon styles

**New CSS to create:**
- [ ] **Browse list styles:** `.browse-list-item`, `.browse-item-icon` (with type-specific colors), `.browse-item-title`, `.browse-item-date`, `.browse-item-metadata` (hover reveal), `.browse-item-hover-details`, `.browse-item-domain-dots` (secondary domain indicators), `.browse-item.active` (selected state)
- [ ] **Lower panel styles:** `.lower-panel`, `.lower-panel-header`, `.lower-panel-handle`, `.lower-panel-ribbon`, `.lower-panel-tab`, `.lower-panel-content`, collapse/expand animation (CSS transition on max-height or transform)
- [ ] **Graph page styles:** `.graph-canvas-container` (full height/width), `.graph-node-tooltip`, `.graph-context-menu`, `.back-to-graph-button` (floating, bottom-left, z-index above content)
- [ ] **Garden tab styles:** `.garden-orphans`, `.garden-suggestions`, `.garden-stats`
- [ ] **Ghost node styles:** `.graph-node-ghost` — handled by Cytoscape.js styling API, not CSS. Define in JS: `{ opacity: 0.15, 'border-style': 'dotted' }`

---

## Phase: Polish (Task 14)

### Task 14: Integration Testing and Polish

**Files:** All

- [ ] Test full flow: open app → click Graph → see nodes → click node → editor opens → "Back to Graph" returns to same state
- [ ] Test Notes sidebar: search, filter by domain, filter by tag, sort by authority, open note, backlinks panel, tags panel, TOC panel
- [ ] Test Browse list shared behavior: same data in Notes sidebar and Graph Browse tab
- [ ] Test edge cases: empty graph (no entities extracted yet), single note, note with zero connections
- [ ] Test ghost nodes: apply filter → verify ghosts appear at low opacity within 1–2 hops → verify toggle hides them
- [ ] Test performance: 100+ notes, 500+ nodes — verify graph renders without lag
- [ ] Test state persistence: close and reopen graph → verify position/zoom/filters restored
- [ ] Test lower panel: collapse/expand, tab switching, content updates when note selection changes
- [ ] Test cross-change compatibility: verify cursor-ui-pattern-migration layout infrastructure still works (collapsible sidebar, main content split)
- [ ] Fix any broken notes operations: create, save, rename, move (especially after `updateFileTree()` removal)

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
