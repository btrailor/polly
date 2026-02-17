# Knowledge Graph Navigation — Codebase Audit

Comprehensive impact analysis of every file, function, endpoint, data structure, and UI element affected by the knowledge-graph-navigation change. Organized by: **interweave** (modify/extend), **replace** (swap with new), **prune** (dead code to remove), and **create** (new code).

---

## Table of Contents

1. [Frontend: notes-manager.js](#1-frontend-notes-managerjs)
2. [Frontend: app.js](#2-frontend-appjs)
3. [Frontend: index.html](#3-frontend-indexhtml)
4. [Frontend: CSS](#4-frontend-css)
5. [Backend: server.py](#5-backend-serverpy)
6. [Backend: Data Layer](#6-backend-data-layer)
7. [Backend: Entity System](#7-backend-entity-system)
8. [Cross-Change Conflicts (cursor-ui-pattern-migration)](#8-cross-change-conflicts)
9. [Broken Features Found During Audit](#9-broken-features)
10. [Summary Tables](#10-summary-tables)

---

## 1. Frontend: notes-manager.js

**File:** `electron-app/src/renderer/notes-manager.js` (3647 lines)

The NotesManager is a monolith. ~650 lines are dead code. ~300 lines get replaced. ~550 lines get modified. ~1450 lines stay unchanged.

### 1A. REPLACE (swap with new implementation)

| Function | Lines | What It Does | What Replaces It |
|----------|-------|-------------|-----------------|
| `updateFileTree()` | 1304-1468 | Renders folder-grouped file tree or flat sorted list into `#notes-file-tree-container`. Groups by `note.domain`, builds nested HTML via string concatenation, attaches click/dblclick/toggle handlers. **The primary target of this change.** | `updateBrowseList()` — calls `/polly/graph/list`, renders flat filtered list with type icons, graph metadata on hover, no folder grouping |
| Sort logic (inline) | 1400-1430 | Inside `updateFileTree()`: sorts by name-asc/desc, modified-desc, created-desc when `sortMode !== 'folder'` | Extracted to standalone sort logic or moved into `updateBrowseList()`. Sort options expand to include authority, connection_count |
| `setupDragAndDrop(container)` | 1534-1600 | Makes `.file-tree-item` draggable, `.file-tree-folder-header` droppable. On drop, calls `moveNote()`. | Coupled to folder-tree DOM. Either removed entirely (graph nav has no folders to drop into) or reimplemented for list reordering |

### 1B. MODIFY (interweave with new design)

| Function | Lines | What Changes |
|----------|-------|-------------|
| `constructor()` | 6-38 | Remove `sortMode` (replaced by graph list sort). Add state for: graph list filters, lower panel state, active domain filter |
| `init()` | 43-76 | Remove `setupSidebarViewToggle()` call (dead). Add initialization for lower collapsible panel and graph list |
| `loadNotesIndex(domain, limit)` | 106-156 | Keep the fetch to `/polly/notes/index` but change the UI update: instead of calling `updateFileTree()`, call `updateBrowseList()` (or better: switch to calling `/polly/graph/list` for the sidebar, keep `loadNotesIndex()` for internal data only) |
| `setupEventListeners()` | 1209-1299 | Search input target may change. Add-button dropdown stays. Collapsible panel header handlers need updating for new lower panel. Some selectors reference elements that won't exist |
| `startInlineRename(item)` | 1473-1529 | Still needed but must work with new list item DOM structure instead of `.file-tree-item` |
| `updateBacklinksPanel()` | 1705-1748 | Retarget from `#notes-backlinks-panel` to new lower-panel container. Same rendering logic |
| `updateTagsPanel()` | 1753-1796 | Retarget from `#notes-tags-panel` to new lower-panel container. Same rendering logic |
| `updateTOCPanel()` | 1853-1912 | Retarget from `#notes-toc-list` to new lower-panel container. Same rendering logic |
| `renderEmptyTOC(tocList)` | 1917-1928 | Retarget container reference |
| `filterByTag(tag)` | 1973-1989 | Change `updateFileTree()` call to `updateBrowseList()`. Consider: should tag filtering use `/polly/graph/list?tag=X` instead of `/polly/notes/tags/{tag}`? |
| `showFilterIndicator(filter)` | 2454-2468 | May need new container target in redesigned sidebar |
| `updateSearchResults()` | 2410-2447 | Container target may change; integrate with graph list view |
| `showCreateNoteModal(prefillName)` | 2630-2717 | Remove hard-coded `'30-Ideas'` default (line 2660). Use most-recent domain or let user pick |
| `showError(message)` | 2449-2452 | Fix: should call `showToast(message, 'error')` instead of just `console.error()` |

### 1C. KEEP (no changes needed)

| Function | Lines | Why |
|----------|-------|-----|
| `checkNotesSource()` | 81-101 | Backend config, no UI coupling |
| `setupEditor()` | 460-581 | CM6 editor setup, not sidebar-related |
| `setupFallbackEditor()` | 586-635 | Fallback editor, rarely used |
| `openNote(noteName, heading, preserveScroll)` | 191-268 | Core note-opening logic, mostly editor-focused |
| `loadBacklinks(noteName)` | 273-287 | Data fetch, no UI |
| `loadTags()` | 292-308 | Data fetch + UI update (UI part gets MODIFY via `updateTagsPanel`) |
| `reloadAfterSync()` | 405-455 | Sync logic, calls `loadNotesIndex()` which handles updates |
| `saveCurrentNote()` | 2502-2583 | Core save logic |
| `onEditorChange()` | 2483-2497 | Auto-save trigger |
| `updateSaveStatus(status)` | 2588-2619 | Save status display |
| `checkSyncStatus()` | 313-328 | Sync status check |
| `startFileWatcher()` | 333-367 | File watcher setup |
| `startSyncPolling()` | 372-400 | Sync polling |
| `scrollToLine(lineNumber)` | 1942-1968 | CM6 line scroll |
| `updateNoteHeader()` | 2267-2297 | Note header display |
| `setupTitleEditing()` | 2302-2351 | Inline title editing |
| `searchNotes(query, limit)` | 161-183 | Search API call |
| `renameNote(oldName, newTitle)` | 2356-2408 | Core rename logic |
| `moveNote(noteName, targetDomain)` | 1605-1650 | Core move logic |
| `createNote()` | 2835-2924 | Core create logic |
| `showSimilarNotesWarning()` | 2929-2990 | Dedup UI |
| `setupDedupActions()` | 2995-3016 | Dedup wiring |
| `appendToSelectedNote()` | 3021-3068 | Dedup action |
| `createWithLinks()` | 3073-3129 | Dedup action |
| `createAnyway()` | 3134-3177 | Dedup action |
| `showCreateFolderModal()` | 3182-3207 | Folder creation UI |
| `createFolder()` | 3250-3315 | Core folder creation |
| Quick Switcher (all 6 functions) | 1997-2224 | Cmd+O navigation, independent of sidebar |
| `showToast()` | 1655-1700 | General UI utility |
| `cleanup()` | 3320-3337 | Teardown |
| Various editor helpers | 963-1004 | `resolveImagePath`, `slugifyHeading`, `extractSection`, `fetchEmbeddedNote` |

### 1D. PRUNE (~650 lines of dead code)

| Function | Lines | Why It's Dead |
|----------|-------|--------------|
| `setupSidebarViewToggle()` | 1801-1810 | Queries `.sidebar-view-btn` elements that don't exist in DOM. Ribbon tabs use `.notes-ribbon-btn` from app.js. **Never executes.** |
| `switchSidebarView(viewName)` | 1815-1848 | Called only by `setupSidebarViewToggle()` which is dead. Toggles `.notes-sidebar-view` elements that don't exist. |
| `enterEditMode(cursorPos)` | 1061-1080 | References `#notes-editor-view` and `#notes-editor-textarea` — legacy pre-CM6 elements removed from HTML. CM6 is always in edit mode. |
| `exitEditMode()` | 1085-1108 | Same — calls `renderMarkdown()` which also targets missing elements. |
| `calculateCursorPositionFromClick()` | 1113-1204 | 90 lines of complex DOM-walking code for click-to-edit in rendered markdown. Dead with CM6. |
| `renderMarkdown(markdown)` | 640-704 | Targets `#notes-editor-view` which doesn't exist. Was for view/edit toggle. CM6 live preview replaced this. |
| `scrollToHeading(heading)` | 1009-1034 | Targets `#notes-editor-view`. Replaced by `scrollToLine()` for CM6. |
| `setupWikiLinkHandlers(container)` | 1039-1056 | Only called from `renderMarkdown()`. CM6 handles wiki-links via `onWikiLinkClick` callback. |
| `showNoteSuggestions()` | 3342-3399 | Legacy textarea wiki-link autocomplete. CM6 has its own autocomplete. |
| `updateNoteSuggestions()` | 3404-3516 | Same — 110 lines of dead textarea autocomplete. |
| `navigateSuggestions()` | 3521-3539 | Same. |
| `insertSelectedSuggestion()` | 3544-3561 | Same. |
| `insertNoteName()` | 3566-3630 | Same. |
| `hideNoteSuggestions()` | 3635-3642 | Same. |
| `escapeHtml()` (duplicate) | 2621-2625 | Exact duplicate of the one at line 1933. |
| `addToRecent(note)` | 2471-2473 | Stub — body is `// TODO: Track recent notes`. Called from `openNote()` but does nothing. |
| `editorMode` state property | 18 | Set to `'view'` in constructor, immediately overridden to `'edit'` by CM6. View/edit toggle concept is dead. |
| `processNoteEmbeds()` | 711-803 | Only called from `renderMarkdown()` (dead). **Verify:** CM6 live-preview may call this independently — check before deleting. |
| `processCallouts()` | 809-867 | Same — only called from `renderMarkdown()`. Verify CM6 dependency. |

---

## 2. Frontend: app.js

**File:** `electron-app/src/renderer/app.js` (17,516 lines)

### 2A. MODIFY

| Item | Lines | What Changes |
|------|-------|-------------|
| `sidebarRibbonConfigs.notes` | 2996-3004 | **Currently:** `files, backlinks, tags, toc`. **New:** Single `browse` tab. Backlinks/Tags/TOC move to lower panel. |
| `sidebarRibbonConfigs` (add entry) | after 3060 | **Add:** `graph: { containerClass: "graph-ribbon-buttons", btnClass: "graph-ribbon-btn", buttons: [{ id: "browse", ... }, { id: "garden", ... }] }` |
| `showView(view)` | 2898-2975 | Add `graph` case to view-specific loading block (~line 2960): `} else if (view === "graph") { initGraphPage(); }` |
| `updateLeftSidebar()` — notes content | 3301-3332 | **Replace** the sort-select + add-button + `#notes-file-tree-container` with Browse list + lower collapsible panel HTML |
| `updateLeftSidebar()` — add graph entry | after 3411 | Add `graph: { title: "Graph", content: renderGraphSidebar() }` to `sidebarConfigs` |
| `updateLeftSidebar()` — event handlers | 3454-3614 | Add `graph` case in the `setTimeout` handler block for graph sidebar events |
| `setupBrowserRibbonHandlers(view)` | 3203-3250 | Notes browser ribbon: "collapse-all" becomes irrelevant (no folders). "sort" stays. "refresh" fix: calls `loadNotes()` which doesn't exist — should be `loadNotesIndex()`. |
| `createBrowserRibbon(view)` | 3101-3133 | Notes: remove "collapse-all" button (no folders). Keep or modify other buttons for graph-list context. |
| `setupSidebarRibbonHandlers(view)` | 3138-3168 | May need graph-specific handling (like `learning` has `switchLearningSidebarPanel`). The `sidebar-ribbon-change` event is dispatched but **nothing listens for it** — this is currently dead infrastructure. |

### 2B. CREATE (new functions needed in app.js)

| Function | Purpose |
|----------|---------|
| `renderGraphSidebar()` | Returns HTML for graph page left sidebar: Browse tab content, Garden tab content, lower panel with Filters + Details sub-tabs |
| `initGraphPage()` | Initializes Cytoscape.js canvas, loads graph data from `/polly/graph/nodes`, sets up graph event handlers |
| `renderLowerPanel(view, tabs)` | Reusable: renders the lower collapsible panel with sub-ribbon tabs (used by both notes and graph sidebars) |

### 2C. KEEP

| Item | Lines | Why |
|------|-------|-----|
| `createSidebarRibbon(view)` | 3079-3096 | Data-driven from `sidebarRibbonConfigs`, auto-supports new views |
| Ribbon click handlers | 2205-2253 | Dynamic `querySelectorAll(".ribbon-item")`, auto-handles new `data-view="graph"` |
| Nav-item click handlers | 2192-2203 | Same — dynamic |
| `updateRightSidebar(view)` | 3958-4002 | Always shows chat, view-agnostic |
| `toggleLeftSidebar()` | 2336-2354 | View-agnostic collapse/expand |
| `toggleRightSidebar()` | 2356-2374 | View-agnostic |
| All other `render*Sidebar()` functions | various | dashboard, knowledge, patterns, settings — unaffected |

### 2D. PRUNE

| Item | Lines | Why |
|------|-------|-----|
| `sidebar-ribbon-change` event dispatch | 3154-3157 | Event is dispatched but **no code anywhere listens for it**. Either wire it up or remove it. |
| Static nav-items in left sidebar HTML | index.html 124-149 | Immediately overwritten by `updateLeftSidebar()` on first `showView()`. Serve no purpose. |
| Broken refresh button handler | ~3239 | Calls `window.notesManager.loadNotes()` which **doesn't exist**. Method is `loadNotesIndex()`. |

---

## 3. Frontend: index.html

**File:** `electron-app/src/renderer/index.html` (2600+ lines)

### 3A. MODIFY

| Element | Lines | What Changes |
|---------|-------|-------------|
| Navigation ribbon (`#icon-ribbon`) | 69-112 | **Add** new graph button after line 88: `<button class="ribbon-item" data-view="graph" title="Graph"><i data-lucide="git-graph"></i></button>` |

### 3B. CREATE

| Element | Where | What |
|---------|-------|------|
| Graph view container | Before line 2179 (before `</main>`) | `<div class="view hidden" id="view-graph">` — contains Cytoscape.js canvas container, floating "Back to Graph" button |
| Lower panel in notes view | Inside `#view-notes` or dynamically in sidebar | Collapsible bottom panel with Filters/Backlinks/Tags/TOC sub-tabs. **Note:** This may be dynamically generated in JS rather than static HTML. |

### 3C. KEEP

| Element | Lines | Why |
|---------|-------|-----|
| `#view-notes` | 2056-2096 | Notes container, toolbar, editor area — the main content stays; only the sidebar content changes |
| Notes modals (create note, create folder, quick switcher) | various | Modal HTML stays as-is |
| Chat panel | 2181-2235 | Unaffected |
| All other views | various | dashboard, knowledge, patterns, settings, learning, etc. — unaffected |

### 3D. PRUNE

| Element | Lines | Why |
|---------|-------|-----|
| Static left sidebar nav-items | 124-149 | Overwritten on every `showView()` call. Dead HTML. |
| Legacy right sidebar | 2284-2377 | Force-hidden with `display: none !important`. Backward compat only. |

---

## 4. Frontend: CSS

### 4A. notes.css (1123 lines)

**File:** `electron-app/src/renderer/styles/notes.css`

| Lines | Selectors | Classification | Notes |
|-------|-----------|----------------|-------|
| 1-107 | `.notes-container`, `.notes-toolbar`, `.notes-search-*`, `.notes-content` | **KEEP** | Container and toolbar styles |
| 108-223 | `.file-tree-folder`, `.file-tree-item`, `.file-tree-folder-header`, `.file-tree-icon`, `.file-tree-rename-input` | **REPLACE** | All file-tree-specific styles. Will be replaced by graph list item styles. |
| 225-459 | `.notes-editor-*`, heading styles, markdown rendering | **KEEP** | Editor area styling |
| 460-513 | `.notes-right-sidebar`, `.notes-sidebar-backlinks`, `.notes-sidebar-tags` | **PRUNE** | The right sidebar was **removed from HTML** (comment at index.html:2087-2088). These 50+ lines of CSS have no matching DOM. |
| 514-613 | `.notes-backlinks-panel`, `.notes-tags-panel`, `.notes-backlinks-item`, `.notes-tag-item` | **MODIFY** | Keep the item styling but retarget selectors for the new lower panel containers |
| 644-797 | `.notes-sidebar-content`, `.notes-sidebar-view-toggle`, `.sidebar-view-btn`, `.toc-*` | **MODIFY** | View-toggle styles reference the dead `switchSidebarView()` system — update selectors. TOC styles keep but need new container context. |
| 800-895 | `.notes-search-results`, `.notes-empty-state`, `.notes-filter-indicator`, `.notes-loader` | **KEEP** | Search results and states |
| 896-977 | `.notes-menu-item`, `.drag-*`, `.note-embed-*` | **MODIFY** | Drag styles get replaced if drag-and-drop is removed. Menu items and embeds keep. |
| 979-1099 | `.heading-highlight`, `.callout-*` | **KEEP** | Content rendering styles |
| 1101-1123 | `@media` responsive rules | **MODIFY** | References `.notes-sidebar` (may not match current DOM structure) |

### 4B. main.css (4498+ lines)

**File:** `electron-app/src/renderer/styles/main.css`

| Lines | Selectors | Classification | Notes |
|-------|-----------|----------------|-------|
| 220-500 | `.ribbon`, `.left-sidebar`, `.main-content-area`, `.three-column-layout` | **KEEP** | Core layout — graph page reuses this |
| 1137-1206 | `.notes-sidebar-container`, `.code-sidebar-container` | **MODIFY** | Notes sidebar container styles need updating for new structure (Browse list + lower panel) |
| 1207-1346 | `.notes-ribbon-buttons`, `.notes-ribbon-btn`, `.code-ribbon-*`, `.knowledge-ribbon-*`, etc. | **MODIFY** | Add `.graph-ribbon-buttons`, `.graph-ribbon-btn` selectors. Modify `.notes-ribbon-buttons` for single Browse tab. |
| 2284-2376 | `.legacy-right-sidebar` | **PRUNE** | Force-hidden with `display: none !important` |

### 4C. CSS TO CREATE

| What | Purpose |
|------|---------|
| Graph page styles | `.graph-canvas-container`, `.graph-node-tooltip`, `.graph-context-menu`, `.back-to-graph-button` |
| Browse list styles | `.browse-list-item`, `.browse-item-icon`, `.browse-item-metadata`, `.browse-item-hover-details` (shared between Notes sidebar and Graph page) |
| Lower panel styles | `.lower-panel`, `.lower-panel-ribbon`, `.lower-panel-tab`, `.lower-panel-content`, collapse/expand animation |
| Garden tab styles | `.garden-orphans`, `.garden-suggestions`, `.garden-merge-card` |
| Graph ribbon styles | `.graph-ribbon-buttons`, `.graph-ribbon-btn` |
| Ghost node styles | `.graph-node-ghost` (opacity, dotted edges) |

---

## 5. Backend: server.py

**File:** `interfaces/server.py` (~5500 lines)

### 5A. KEEP (unchanged)

| Endpoint | Lines | Why |
|----------|-------|-----|
| `GET /polly/notes/source` | 2602 | Backend config |
| `POST /polly/notes/sync/start` | 2647 | File watcher |
| `POST /polly/notes/sync/stop` | 2699 | File watcher |
| `GET /polly/notes/sync/status` | 2745 | Sync status |
| `GET /polly/notes/reindex` | 2780 | RAG reindexing (SSE) |
| `GET /polly/notes/index` | 2883 | **Explicitly kept** — serves file watcher, RAG indexing, Obsidian migration |
| `POST /polly/notes/create` | 2999 | Note creation with dedup |
| `POST /polly/notes/create-folder` | 3135 | Folder creation |
| `PUT /polly/notes/update` | 3193 | Note save |

### 5B. MODIFY

| Endpoint | Lines | What Changes |
|----------|-------|-------------|
| `GET /polly/notes/{note_name}/backlinks` | 3257 | **Currently broken:** references `note.links` which doesn't exist on `NoteInfo`. Should use `BacklinksIndex` from `core/backlinks.py`. Fix this. |
| `GET /polly/stats` | ~1096 | Currently returns `'graph': {'entities': '?', 'relationships': '?'}` (placeholder). Should actually query `EntityStore.get_stats()` to return real counts. |

### 5C. CREATE (new endpoints)

| Endpoint | Purpose |
|----------|---------|
| `GET /polly/graph/list` | Filtered list of graph-enriched content items. Queries EntityStore + NoteInfo. Powers Notes sidebar and Graph Browse tab. (See design.md for full spec.) |
| `GET /polly/graph/nodes` | Nodes + edges for Cytoscape.js. Supports filtering, center_node + hops, ghost computation. |
| `POST /polly/graph/state` | Save graph view state (position, zoom, filters, layout). |
| `GET /polly/graph/state` | Retrieve last saved graph state. |

### 5D. Frontend references endpoints that DON'T EXIST (broken)

These are called from `notes-manager.js` or `app.js` but have no matching route in `server.py`:

| Called From | Endpoint | Line in Frontend | Status |
|-------------|----------|-----------------|--------|
| notes-manager.js | `GET /polly/notes/search` | 170 | **Missing** — frontend calls it, backend doesn't have it |
| notes-manager.js | `GET /polly/notes/tags` | 294 | **Missing** — `tags_index.py` exists but no API route |
| notes-manager.js | `GET /polly/notes/tags/{tag}` | 1976 | **Missing** — same |
| notes-manager.js | `POST /polly/notes/move` | 1613 | **Missing** — frontend has full move logic, no backend route |
| notes-manager.js | `POST /polly/notes/rename` | 2364 | **Missing** — same |
| notes-manager.js | `GET /polly/notes/folders` | 2648 | **Missing** — used by create-note modal to populate folder dropdown |
| notes-manager.js | `POST /polly/notes/append` | 3032 | **Missing** — used by dedup "append to existing note" flow |
| app.js | `POST /polly/notes/index/build` | 5627 | **Missing** |
| app.js | `POST /polly/notes/migrate-from-obsidian` | 13799 | **Missing** (and related migrate-status, switch-source) |

**Decision needed:** Which of these should be implemented as part of this change vs. tracked separately? The move, rename, and folders endpoints are needed for a functioning Notes page regardless of graph navigation.

---

## 6. Backend: Data Layer

### 6A. NoteInfo Dataclass

**File:** `core/notes_index.py:17-35`

```python
@dataclass
class NoteInfo:
    path: Path
    name: str              # Filename without extension
    aliases: List[str]     # From frontmatter
    title: str             # From frontmatter or first heading
    domain: Optional[str]  # Inferred from folder structure
    tags: List[str]        # From frontmatter only
    created: Optional[datetime]
    modified: Optional[datetime]
    size: int              # File size in bytes
```

**Classification: KEEP (unchanged)**

NoteInfo stays as-is for `/polly/notes/index`. The new `/polly/graph/list` endpoint returns a **different response shape** that joins NoteInfo data with EntityStore data. We do NOT modify NoteInfo itself — the graph enrichment happens at the API layer, not the data class.

### 6B. NotesIndex Class

**File:** `core/notes_index.py:38-519`

| Method | Classification | Notes |
|--------|---------------|-------|
| `build_index(notes_path, recursive)` | **KEEP** | Index building stays for file watcher |
| `_extract_note_info(md_file, root_path)` | **KEEP** | Extraction stays |
| `_extract_frontmatter(content)` | **KEEP** | Frontmatter parsing stays |
| `_extract_first_heading(content)` | **KEEP** | Heading extraction stays |
| `_infer_domain_from_path(md_file, root_path)` | **KEEP** | Domain inference stays (becomes "primary domain") |
| `find_note_by_name(name)` | **KEEP** | Lookup |
| `find_note_by_alias(alias)` | **KEEP** | Lookup |
| `get_all_notes()` | **KEEP** | Used by new `/polly/graph/list` to join with entity data |
| `get_notes_by_domain(domain)` | **KEEP** | Used for primary domain filtering |
| `search_notes(query, limit)` | **KEEP** | Fuzzy search |
| `get_stats()` | **KEEP** | Stats |

### 6C. BacklinksIndex

**File:** `core/backlinks.py` (517 lines)

| Method | Classification | Notes |
|--------|---------------|-------|
| `build_index(notes)` | **KEEP** | Scans wiki-links across all notes |
| `get_backlinks(note_name)` | **MODIFY** | **Currently unused by API** — the `/polly/notes/{name}/backlinks` endpoint tries to use `note.links` instead. Fix the endpoint to use this. |
| `get_outgoing_links(note_name)` | **KEEP** | Needed for connection counting |
| `get_orphaned_notes()` | **KEEP** | Directly powers the Garden view's "Isolated notes" section |
| `get_most_linked_notes()` | **KEEP** | Useful for authority/hub identification |
| Global singleton `get_backlinks_index()` | **KEEP** | |

**Key finding:** BacklinksIndex has rich data (orphans, most-linked, outgoing links) that is **completely unexposed via API**. The `/polly/graph/list` endpoint should use this data.

### 6D. TagsIndex

**File:** `core/tags_index.py` (560 lines)

| Method | Classification | Notes |
|--------|---------------|-------|
| `build_index(notes)` | **KEEP** | Scans frontmatter + inline tags |
| `get_tags_for_note(note_name)` | **KEEP** | Needed for note detail view |
| `get_notes_for_tag(tag)` | **KEEP** | Needed for tag filtering |
| `get_all_tags()` | **KEEP** | Needed for filter dropdowns |
| `get_tag_stats()` | **KEEP** | Tag counts |
| Global singleton `get_tags_index()` | **KEEP** | |

**Key finding:** TagsIndex is also **completely unexposed via API**. Frontend calls `GET /polly/notes/tags` and `GET /polly/notes/tags/{tag}` but those routes don't exist in server.py. The data is there; the routes aren't.

---

## 7. Backend: Entity System

**File:** `core/entities/` (5 files, ~1105 lines total)

### 7A. EntityStore (`store.py`, 538 lines)

**Database:** SQLite at `~/.polly/entities.db`

**Tables:**
- `entities` (id PK, name, entity_type, description, aliases JSON, domains JSON, tags JSON, mention_count, source_count, authority_score, last_seen, created, metadata JSON)
- `relationships` (id auto, source_id, target_id, relationship_type, strength, context, bidirectional, mention_count, created, last_seen. UNIQUE source_id+target_id+relationship_type)
- `entity_mentions` (id, entity_id, source_type, source_id, context, created)

| Method | Classification | Notes |
|--------|---------------|-------|
| `upsert_entity()` | **KEEP** | Core CRUD |
| `upsert_relationship()` | **KEEP** | Core CRUD |
| `get_entity()` / `get_entity_by_name()` | **KEEP** | Lookup |
| `delete_entity()` | **KEEP** | CRUD |
| `record_mention()` | **KEEP** | Tracks source→entity links |
| `search(EntityQuery)` | **MODIFY** | May need extension for the graph list filtering (domain, authority_min, type filter) |
| `get_related(entity_id, max_hops, min_strength)` | **KEEP** | BFS traversal — powers "Explore From Here" and ghost computation |
| `find_path(source_id, target_id)` | **KEEP** | Shortest path — powers "Why This Connection?" |
| `get_cross_domain_bridges(domain_a, domain_b)` | **KEEP** | Powers secondary domain detection |
| `recompute_authority()` | **KEEP** | PageRank-like scoring |
| `get_stats()` | **MODIFY** | Currently returns basic counts. Extend to include: nodes by type, orphan count, avg connections per node |
| `get_top_entities(limit, entity_type)` | **KEEP** | Hub identification |

**Key finding:** EntityStore has rich graph traversal capabilities (`get_related`, `find_path`, `get_cross_domain_bridges`) that are **completely unexposed via API**. This is the core data engine for both new endpoints.

### 7B. EntityExtractor (`extractor.py`, 238 lines)

| Method | Classification | Notes |
|--------|---------------|-------|
| `extract_and_store()` | **MODIFY** | Currently called during queries. Needs to also be called during note saves for save-time suggestions. |
| `extract_entities_only()` | **KEEP** | Preview without storing — used for suggestions UI |

**Key finding:** Entity extraction currently happens during LLM queries (as context building), **not during note saves**. For save-time entity suggestions, we need to wire `extract_and_store()` into the save path.

### 7C. Entity Mentions Gap

The `entity_mentions` table has `source_type` and `source_id` columns, designed to track which content produced which entities. **Currently, mentions are only recorded for "query" source type** — not for notes. To power `/polly/graph/list`, we need mentions recorded for source_type="note" with source_id=note path/name. This requires:

1. Calling `entity_extractor.extract_and_store(content, source_type="note", source_id=note_name)` during note indexing/saving
2. Using `entity_mentions` to join entities↔notes for the graph list response

---

## 8. Cross-Change Conflicts (cursor-ui-pattern-migration)

### HIGH Conflicts

| # | Element | cursor-ui-migration | knowledge-graph-navigation | Resolution |
|---|---------|--------------------|-----------------------------|------------|
| 1 | `sidebarRibbonConfigs.notes` (app.js:2996) | Changes to action buttons: New Note, Templates, Folders, Tags, Search | Changes to single Browse tab | **KGN takes precedence** for Notes sidebar content. CUI defines the container. |
| 2 | `updateFileTree()` (notes-manager.js:1304) | Assumes file tree stays, wraps in new container | Replaces file tree entirely with graph list | **KGN takes precedence.** CUI should not deeply integrate with file tree. |
| 3 | `#notes-file-tree-container` + CSS | Restructures container, preserves tree | Replaces container contents and all `.file-tree-*` CSS | **KGN takes precedence.** CUI should treat Notes sidebar content as a slot. |
| 4 | `updateLeftSidebar()` notes entry (app.js:3301) | Redesigns sidebar HTML with new ribbon buttons | Replaces sidebar HTML with Browse list + lower panel | **KGN takes precedence** for content; CUI for infrastructure. |

### GAPS (KGN needs, CUI doesn't provide)

| # | What | Notes |
|---|------|-------|
| 5 | Lower collapsible panel | KGN needs it for both Notes and Graph sidebars. CUI doesn't define this pattern. Build it as shared infrastructure. |
| 6 | Shared Browse list component | KGN needs a reusable list component across pages. CUI builds per-page content without reuse. |

### COMPATIBLE (no conflict)

| # | What | Notes |
|---|------|-------|
| 7 | Collapsible left sidebar infrastructure | CUI builds it; KGN consumes it |
| 8 | Main content + chat panel split | CUI builds it; KGN uses it for graph canvas |
| 9 | Navigation ribbon | KGN adds a button; CUI restructures existing ones |
| 10 | Status bar, agents sidebar, keyboard shortcuts | Both reuse these |

### Recommended Sequence

1. **cursor-ui-migration Phases 1-2** (layout infrastructure, collapsible sidebar, main content split) — ship first
2. **cursor-ui-migration Task 2.3** (Notes sidebar content) — **defer to knowledge-graph-navigation** or implement as minimal pass-through (wrap existing file tree in new container, don't redesign)
3. **knowledge-graph-navigation** — ships after CUI Phase 1-2 provides container infrastructure
4. **cursor-ui-migration Phases 4-9** (chat panel, agents, settings, polish) — ships after KGN, no conflicts

---

## 9. Broken Features Found During Audit

Issues discovered that exist today, independent of this change:

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 1 | Refresh button calls `loadNotes()` which doesn't exist | app.js ~3239 | **Broken** — should be `loadNotesIndex()` |
| 2 | `/polly/notes/{name}/backlinks` endpoint references `note.links` which doesn't exist on NoteInfo | server.py:3300 | **Broken** — should use `BacklinksIndex` |
| 3 | `/polly/notes/search` endpoint missing | server.py (absent) | **Missing** — frontend calls it at notes-manager.js:170 |
| 4 | `/polly/notes/tags` endpoint missing | server.py (absent) | **Missing** — `TagsIndex` exists but has no API route |
| 5 | `/polly/notes/tags/{tag}` endpoint missing | server.py (absent) | **Missing** — same |
| 6 | `/polly/notes/move` endpoint missing | server.py (absent) | **Missing** — frontend has full move logic but no backend |
| 7 | `/polly/notes/rename` endpoint missing | server.py (absent) | **Missing** — frontend has full rename logic but no backend |
| 8 | `/polly/notes/folders` endpoint missing | server.py (absent) | **Missing** — create-note modal can't populate folder dropdown |
| 9 | `/polly/notes/append` endpoint missing | server.py (absent) | **Missing** — dedup "append" flow can't execute |
| 10 | `/polly/stats` graph data is placeholder `'?'` | server.py:1096 | **Broken** — should call `entity_store.get_stats()` |
| 11 | `showError()` just logs, ignores existing `showToast()` | notes-manager.js:2449 | **Incomplete** |
| 12 | `sidebar-ribbon-change` event dispatched, never listened to | app.js:3154 | **Dead infrastructure** |
| 13 | Entity extraction only runs during queries, not note saves | core/polly.py | **Architecture gap** — entities never extracted from note content |
| 14 | `entity_mentions` only tracks "query" source type, not notes | core/entities/store.py | **Data gap** — can't join entities↔notes |

---

## 10. Summary Tables

### By Action

| Action | Files Affected | Estimated Impact |
|--------|---------------|-----------------|
| **PRUNE** (dead code removal) | notes-manager.js (650 lines), notes.css (50 lines), index.html (25 lines), main.css (90 lines) | ~815 lines removed |
| **REPLACE** | notes-manager.js (300 lines: updateFileTree, sort, drag-and-drop), notes.css (115 lines: file-tree styles) | ~415 lines replaced |
| **MODIFY** | notes-manager.js (550 lines), app.js (200 lines), server.py (50 lines), notes.css (200 lines), main.css (150 lines) | ~1150 lines modified |
| **CREATE** | New graph page JS, new CSS, new API endpoints, new HTML, Browse list component, lower panel component | ~2000-3000 lines new |
| **KEEP** | notes-manager.js (1450 lines), all other views, all editor code, save/sync, quick switcher, CRUD operations | Majority of existing code |

### Files Touched (ordered by impact)

| File | PRUNE | REPLACE | MODIFY | CREATE | Total Impact |
|------|-------|---------|--------|--------|-------------|
| `notes-manager.js` | 650 lines | 300 lines | 550 lines | Browse list logic | **VERY HIGH** |
| `app.js` | 3 items | — | 8 items | 3 new functions | **HIGH** |
| `server.py` | — | — | 2 endpoints | 4 new endpoints | **HIGH** |
| `notes.css` | 50 lines | 115 lines | 200 lines | — | **HIGH** |
| `main.css` | 90 lines | — | 150 lines | Graph + Browse styles | **MEDIUM** |
| `index.html` | 25 lines | — | 1 element | 1 new view container | **MEDIUM** |
| `core/entities/store.py` | — | — | 2 methods | — | **LOW** |
| `core/entities/extractor.py` | — | — | 1 method wiring | — | **LOW** |
| `core/notes_index.py` | — | — | — | — | **NONE** |
| `core/backlinks.py` | — | — | — | — | **NONE** (but data is newly exposed via API) |
| `core/tags_index.py` | — | — | — | — | **NONE** (but data is newly exposed via API) |

### New Dependencies Needed

| Dependency | Purpose | Where |
|------------|---------|-------|
| Cytoscape.js | Graph visualization library | `package.json` (npm) |
| Cytoscape.js layouts plugin(s) | Force-directed, concentric, hierarchical layouts | `package.json` (npm) |
| (optional) cytoscape-cose-bilkent | Better force-directed layout | `package.json` (npm) |

### Existing Code That's Already Built But Unexposed

These capabilities exist in the backend but have **zero API exposure**. This change surfaces them:

| Capability | Location | Exposed By |
|-----------|----------|-----------|
| BFS graph traversal (N-hop neighbors) | `EntityStore.get_related()` | `/polly/graph/nodes?center_node=X&hops=N` |
| Shortest path between entities | `EntityStore.find_path()` | "Why This Connection?" UI |
| Cross-domain bridge detection | `EntityStore.get_cross_domain_bridges()` | Secondary domain computation |
| Authority/PageRank scoring | `EntityStore.recompute_authority()` | Authority-based sort/size in graph |
| Orphaned note detection | `BacklinksIndex.get_orphaned_notes()` | Garden view "Isolated notes" |
| Most-linked note identification | `BacklinksIndex.get_most_linked_notes()` | Hub detection |
| Tag reverse index | `TagsIndex.get_notes_for_tag()` | Tag filtering in Browse list |
| Entity search with type/domain filters | `EntityStore.search()` | `/polly/graph/list` filtering |
