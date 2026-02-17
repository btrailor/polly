# Knowledge Graph Navigation — Design

## Navigation Model

### Core Concept: The Graph Is the Knowledge Base

The knowledge graph is not a visualization of the knowledge base — it **is** the knowledge base. Every piece of indexed content (notes, captures, books, conversations, code files, canvases) exists as a node in the graph. Connections between nodes are the organizational structure. The user's experience of "browsing their knowledge" is the experience of navigating this graph.

Two views exist for the same structure:

```
                    ┌─────────────────────────────────────┐
                    │        Entity Graph (SQLite)         │
                    │  nodes = all indexed content         │
                    │  edges = entity connections          │
                    │  metadata = authority, maturity,     │
                    │             domain, type             │
                    └──────────┬────────────┬──────────────┘
                               │            │
                    ┌──────────▼──┐  ┌──────▼──────────────┐
                    │ Graph View  │  │ List View            │
                    │ (Graph page)│  │ (Notes page sidebar) │
                    │ Cytoscape.js│  │ Filtered, sortable   │
                    │ Visual nav  │  │ Text nav             │
                    └─────────────┘  └─────────────────────┘
```

Both views are powered by the same backend: `/polly/graph/list` for the list view, `/polly/graph/nodes` for the graph canvas. Both ship together as a single change.

---

## Graph Page

A first-class page accessible via the `graph` lucide icon in the navigation ribbon.

### Layout (follows cursor-ui-pattern-migration structure)

```
┌─────────┬─────────────────────────────────────┬─────────────────────┐
│ Ribbon  │ Graph Left Sidebar                  │   Chat Panel        │
│         │                                     │                     │
│  ...    │ ┌─────────────────────────────────┐ │                     │
│  graph ←│ │ [Browse]  [Garden]    ← ribbon  │ │   [Agent Tabs]      │
│  ...    │ ├─────────────────────────────────┤ │   [Messages]        │
│         │ │                                 │ │   [Input]           │
│         │ │  (Browse: filtered list of      │ │                     │
│         │ │   graph nodes, same as notes    │ │                     │
│         │ │   sidebar list view)            │ │ Cytoscape.js        │
│         │ │                                 │ │ Graph Canvas        │
│         │ │  (Garden: orphans, merges,      │ │ (main area)         │
│         │ │   maintenance tasks)            │ │                     │
│         │ │                                 │ │                     │
│         │ ├─────────────────────────────────┤ │                     │
│         │ │ ▲ Lower Panel (collapsible)     │ │                     │
│         │ │ ┌───────────────────────────┐   │ │                     │
│         │ │ │ [Filters] [Details]       │   │ │                     │
│         │ │ │                           │   │ │                     │
│         │ │ │ Filters: domain, type,    │   │ │                     │
│         │ │ │   maturity, authority,     │   │ │                     │
│         │ │ │   layout selector,        │   │ │                     │
│         │ │ │   ghost toggle            │   │ │                     │
│         │ │ │                           │   │ │                     │
│         │ │ │ Details: (when node       │   │ │                     │
│         │ │ │   selected) backlinks,    │   │ │                     │
│         │ │ │   tags, TOC, entities     │   │ │                     │
│         │ │ └───────────────────────────┘   │ │                     │
│         │ └─────────────────────────────────┘ │                     │
└─────────┴─────────────────────────────────────┴─────────────────────┘
```

### Sidebar Structure

The graph page sidebar has two layers:

**Top: Ribbon with two tabs**

1. **Browse** — A filtered, sortable list of graph nodes. Identical data and rendering to the Notes page sidebar list view. Clicking an item in the Browse list highlights it in the graph canvas and can open it in the viewer.

2. **Garden** — The anti-slop maintenance view. Shows:
   - Isolated notes (0-2 connections) with bulk actions (link, merge, delete)
   - Suggested merges ("These 3 notes all discuss X")
   - Connection suggestions ("X mentioned in 5 unlinked notes")
   - Maintenance stats (total orphans, last review date)
   - Weekly/monthly digest summary
   - This operationalizes the garden maintenance prompts from the knowledge-graph spec directly in the navigation surface.

**Bottom: Collapsible lower panel (slides up from bottom of sidebar)**

A context-sensitive detail panel with its own sub-ribbon. Content changes based on what is selected:

- **Filters tab** — Domain filter, content type filter, maturity filter, authority range, layout selector (force-directed / hierarchical / concentric), "Show filtered as ghosts" toggle. These filters apply to both the Browse list above and the graph canvas.

- **Details tab** — Appears when a node is selected. Shows:
  - Backlinks (notes linking to this item)
  - Tags
  - TOC (if the selected item is a note with headings)
  - Extracted entities
  - Inbound/outbound connection breakdown
  - Maturity stage with transition controls

The lower panel is collapsed by default. User drags or clicks to expand it. It persists its collapsed/expanded state.

### Graph Rendering

- **Primary nodes (notes):** Larger, brighter. Default shape: circle. Size scales with authority score.
- **Secondary nodes (conversations, books, captures, code):** Smaller, distinct shapes per type. Dimmer by default. Expand on hover or click.
  - Conversations: diamond
  - Books/library: hexagon
  - Captures: triangle
  - Code files: square
  - Canvases: rounded rectangle
- **Edges:** Thickness indicates connection strength. Color/style indicates relationship type (solid = references, dashed = relates_to, dotted = co_occurs_with). Cross-domain edges visually highlighted.
- **Domain coloring:** Nodes colored by primary domain affiliation.
- **Labels:** Node labels visible at medium zoom. At low zoom, only high-authority nodes show labels. At high zoom, all labels visible.

### Filtered Node Ghosting (Graph View Only)

When filters are applied in the graph canvas, filtered-out nodes are not fully hidden. Instead, they appear as **proximity-limited ghosts**:

- Filtered-out nodes within **1-2 hops** of visible (non-filtered) nodes remain rendered at low opacity (~0.15). Their edges become thin dotted lines at even lower opacity.
- Filtered-out nodes **beyond 2 hops** from any visible node are hidden entirely. This prevents the graph from being overwhelmed with ghosts while preserving nearby spatial context.
- Hovering a ghosted node temporarily restores it to full visibility with a tooltip.
- Clicking a ghosted node opens it normally (same as clicking any node).
- Ghosting applies **only to the graph canvas**, not to the list views. The Browse list and Notes sidebar simply filter items in/out — standard list filtering behavior.
- Ghosting is toggleable via "Show filtered as ghosts" in the Filters panel (default: on).

### Node Interaction

1. **Hover:** Show tooltip with node name, type, domain, connection count, authority indicator.
2. **Click:** Full transition to item viewer. Graph state (position, zoom, filters) saved to session. Floating "Back to Graph" button appears in viewer.
3. **Right-click:** Context menu — Open in viewer, Expand neighbors, Show connections, Copy link, Add to pinned.
4. **"Explore From Here":** Click node → expand 1-3 hop neighborhood. Progressive disclosure — don't render the entire graph at once.

### "Back to Graph" Navigation

When a user clicks a node and transitions to the item viewer:

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│   ┌──────────────────────────────────────────────────────┐   │
│   │  Item Viewer (note editor, book reader, etc.)        │   │
│   │                                                      │   │
│   │  [Content of the clicked node]                       │   │
│   │                                                      │   │
│   │                                                      │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                               │
│   ┌─────────────────────┐                                    │
│   │ ← Back to Graph     │  ← Floating button, bottom-left   │
│   └─────────────────────┘    or configurable position        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

- Button restores exact graph position, zoom level, active filters, and expanded neighborhoods.
- Graph state stored in sessionStorage per graph session.
- If the user navigates away from the viewer to another page (e.g., Settings), the graph state is still preserved until the session ends.
- If the user navigated to the item from the list view (Notes page) instead of the graph, the back button returns to the list view at the same scroll position.

---

## Notes Page: File Tree Transition

### Current Implementation

The Notes sidebar is driven by `GET /polly/notes/index`, which returns `NoteInfo` objects with file-system metadata (`name`, `title`, `path`, `domain`, `tags`, `modified`, `created`). The `updateFileTree()` method in `notes-manager.js` renders two modes:

- **Folder view** (default): Groups notes by `note.domain` (the folder on disk), renders collapsible domain sections
- **Flat view**: Sorts all notes by name/modified/created

The sidebar has a 4-tab ribbon: Files, Backlinks, Tags, TOC.

### New Implementation

The Notes sidebar switches from the `/polly/notes/index` endpoint to `/polly/graph/list`, which returns graph-enriched data. The folder tree is replaced by a filtered, sortable list of graph nodes.

#### Sidebar Structure (Notes Page)

```
┌─────────────────────────────────┐
│ [Browse]              ← ribbon  │
│  (single tab — the filtered     │
│   graph list, same component    │
│   as the Graph page Browse tab) │
├─────────────────────────────────┤
│ [Search]                        │
│ New Note button                 │
│                                 │
│ ● Note Title Alpha              │
│ ● Note Title Beta               │
│ ◆ Conversation: Docker          │
│ ● Note Title Gamma              │
│ ...                             │
│                                 │
├─────────────────────────────────┤
│ ▲ Lower Panel (collapsible)     │
│ ┌─────────────────────────────┐ │
│ │ [Filters] [Backlinks] [Tags]│ │
│ │ [TOC]                       │ │
│ │                             │ │
│ │ Backlinks: (for selected    │ │
│ │   note) linked notes list   │ │
│ │                             │ │
│ │ Tags: tag list for selected │ │
│ │   note, click to filter     │ │
│ │                             │ │
│ │ TOC: heading outline for    │ │
│ │   selected note             │ │
│ │                             │ │
│ │ Filters: domain, type,     │ │
│ │   maturity, sort            │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

**Key changes from current:**

1. The top ribbon collapses from 4 tabs (Files, Backlinks, Tags, TOC) to 1 tab (Browse). Backlinks, Tags, and TOC move to the **lower collapsible panel** as sub-tabs — they are context-sensitive to the selected note, not alternative navigation views.

2. The file tree (folder grouping by `note.domain` on disk) is replaced by a flat filtered list powered by `/polly/graph/list`. Domain grouping is now a filter, not a folder structure.

3. Filters live in the lower panel alongside the note-specific views (Backlinks, Tags, TOC). The lower panel slides up from the bottom of the sidebar and is collapsible.

4. The Browse list component is **shared** between the Notes page sidebar and the Graph page Browse tab. Same component, same data source, same rendering. The Graph page just has more sidebar content (the Garden tab and graph-specific filter options like layout selector and ghost toggle).

### Domain Resolution

Notes have both a **primary domain** and **secondary domain connections**:

- **Primary domain:** Set by the user — either from the folder the note lives in on disk, or from frontmatter `domain:` field. This is the user's intentional categorization.
- **Secondary domains:** Inferred from entity connections. If a note about Docker is connected to entities that also appear in Signals-domain notes, it gains a secondary connection to Signals.

**Rules:**

1. A note appears **once** in an unfiltered list, under its primary domain.
2. When filtering by a specific domain, the note appears if it has **either** a primary or secondary connection to that domain.
3. In the list, each note shows its primary domain color. Small secondary domain indicators (colored dots matching other domain colors) hint at cross-domain connections — visible on hover (progressive disclosure).
4. The user can change a note's primary domain by editing frontmatter or moving the file on disk. Secondary domains are system-managed and update automatically as entity connections change.
5. Notes with **no domain** (no folder, no frontmatter, no entity connections to domain-affiliated entities) appear under an "Uncategorized" group and are flagged in the Garden view as candidates for connection.

### Multi-Domain Notes in List View

When no domain filter is active:
```
● Docker Deployment Guide          Jan 15    ← primary domain: Sigils
  (hover: 8 connections · bridge · ●● )      ← ●● = secondary domain dots
                                                (Signals, Scrolls)
```

When filtering by "Signals" (secondary domain):
```
● Docker Deployment Guide          Jan 15    ← appears because of secondary
                                                connection to Signals
● Audio Networking Setup           Jan 12    ← primary domain is Signals
```

### What Happens to updateFileTree()

The `updateFileTree()` method in `notes-manager.js` is replaced by a new `updateBrowseList()` method that:

1. Calls `/polly/graph/list` instead of `/polly/notes/index`
2. Renders a flat filtered list (no folder grouping) with type icons, titles, and subtle metadata
3. Applies filters from the lower panel (domain, type, maturity, sort)
4. Handles progressive disclosure (hover for connection count, status, secondary domains)
5. Shares rendering logic with the Graph page Browse tab (ideally the same component or function)

The `/polly/notes/index` endpoint is **not removed**. It continues to serve the file watcher, RAG indexing, Obsidian migration, and any other system that needs file-system-level note data.

---

## Save-Time Suggestions (Non-Blocking)

When a user saves any content, the Knowledge Quality Pipeline runs. The entity extraction and connection suggestion steps produce results that appear as a non-blocking notification:

```
┌──────────────────────────────────────────────────────────┐
│  Note Editor                                              │
│                                                          │
│  [User's note content...]                                │
│                                                          │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 3 connections found · 2 entities extracted         │  │
│  │ [Review]                            [Dismiss]      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- **Non-blocking:** Note saves immediately regardless. Suggestions are informational.
- **"Review" expands:** Shows extracted entities (accept/reject each) and suggested connections (accept/reject each). One-click bulk accept.
- **"Dismiss" hides:** Suggestions are not lost — they're stored and can be reviewed later via the node's detail view in the lower panel, or during garden maintenance.
- **Frequency control:** If user consistently dismisses, reduce frequency (show only for high-confidence suggestions). Configurable in settings.

---

## Maturity-Gated Structure

Structure requirements scale with note maturity stage:

### 30-Ideas (Seed Stage)

- **Auto-generated frontmatter:** System silently adds `title`, `date`, `domain` (inferred), `entities` (extracted) to frontmatter on save. User never has to think about it.
- **No required fields.** Body is entirely freeform.
- **Graph integration:** Node appears in graph with auto-extracted connections. Works even with zero manual effort.

### 20-Active (Working Stage)

When a note transitions to Active (manually or via review workflow prompt):

- **Gentle structure suggestions:** "This note discusses 5 concepts. Add key concept tags?" / "Link to related project?" / "3 similar notes exist — view them?"
- **Suggestions are non-blocking.** The note transitions to Active regardless.
- **Augmented writing activates:** The sidebar shows related notes during editing (when augmented writing is implemented).

### 10-Archive (Settled Stage)

When a note transitions to Archive:

- **Full card treatment.** System generates a structured summary if one doesn't exist. Proposes: confirmed entities, connection review, authority assessment.
- **Still non-blocking** — but the system is more persistent. "This note has no summary. Generate one?"
- **The note has earned its structure** through use and maturity. Structure is a natural consequence of the note's lifecycle, not a prerequisite for creation.

---

## Graph Quality: Hybrid Model

The graph is useful "for free" through automatic entity extraction, but manual linking makes it richer:

### Automatic Layer (System-Driven)

- Entity extraction on every save (spaCy + LLM)
- Co-occurrence detection (entities appearing in the same document)
- Semantic similarity connections (via RAG embeddings)
- Authority scoring from connection patterns
- Domain classification from content analysis

### Manual Layer (User-Driven)

- Wiki-links (`[[Note Name]]`) create explicit edges
- Manual tags create explicit connections to tag entities
- User-confirmed entity suggestions strengthen auto-connections
- User-rejected suggestions prune false connections
- Drag-and-drop linking in graph view (future)

### How They Interact

- Auto-connections have a `confidence` score (0.0–1.0). User-confirmed connections get confidence = 1.0.
- Graph visualization can filter by confidence threshold (e.g., "show only connections above 0.7").
- User rejections reduce confidence to 0.0 and hide the connection (not delete — can be re-evaluated).
- Over time, user behavior trains the system on what constitutes a meaningful connection in this user's knowledge base.

---

## API Design

### Strategy

Two new endpoints serve the graph navigation layer. The existing `/polly/notes/index` is **unchanged** — it continues to serve file-system consumers (file watcher, RAG indexing, Obsidian migration).

The new endpoints query the EntityStore (SQLite) for graph metadata and join with NoteInfo for file metadata. The EntityStore already has `entity_mentions` linking entities to source content (notes, conversations, books, etc.) with `source_type` and `source_id`. Authority scores, inbound/outbound counts are already computed.

### `/polly/graph/nodes` — Graph Canvas Data

Returns nodes and edges for Cytoscape.js rendering.

```
GET /polly/graph/nodes
  ?type=note,conversation,book    # Content type filter (comma-separated)
  &domain=sigils                  # Domain filter (primary or secondary)
  &maturity=20                    # Maturity stage filter
  &authority_min=0.3              # Minimum authority score
  &confidence_min=0.5             # Minimum edge confidence
  &center_node=entity-id-123     # For "Explore From Here" — return N-hop neighborhood
  &hops=2                        # Hop depth for center_node (default: 2)
  &include_ghosts=true           # Include proximity-limited ghost nodes
  &limit=500                     # Max nodes
  &offset=0

Response: {
  nodes: [{
    id: "entity-id-123",
    name: "Docker Deployment Guide",
    type: "note",                    // note, conversation, book, capture, code, canvas
    primary_domain: "sigils",
    secondary_domains: ["signals"],
    authority_score: 0.82,
    inbound_count: 12,
    outbound_count: 5,
    maturity: 20,
    updated_at: "2026-02-15T...",
    is_ghost: false                  // true for proximity-limited ghost nodes
  }],
  edges: [{
    source: "entity-id-123",
    target: "entity-id-456",
    relationship_type: "references",
    weight: 0.9,
    confidence: 0.85,
    is_ghost: false
  }],
  total_node_count: 1234,
  ghost_count: 45
}
```

### `/polly/graph/list` — Filtered List Data

Returns a flat list of content items enriched with graph metadata. Powers both the Notes page sidebar and the Graph page Browse tab.

```
GET /polly/graph/list
  ?type=note                      # Content type filter
  &domain=sigils                  # Domain filter (matches primary or secondary)
  &maturity=20                    # Maturity stage filter
  &sort=authority                 # Sort: authority, recent, alpha, created
  &connection_status=hub          # Filter: hub, bridge, isolated, all
  &q=docker                      # Text search (title, entities)
  &limit=100
  &offset=0

Response: {
  items: [{
    id: "entity-id-123",
    name: "Docker Deployment Guide",
    type: "note",
    primary_domain: "sigils",
    secondary_domains: ["signals"],
    authority_score: 0.82,
    connection_count: 17,
    inbound_count: 12,
    outbound_count: 5,
    connection_status: "hub",       // hub, bridge, isolated, normal
    maturity: 20,
    tags: ["docker", "deployment"],
    updated_at: "2026-02-15T...",
    created_at: "2026-01-10T...",
    path: "/Users/.../notes/sigils/docker.md",  // For file-based items
    preview_snippet: "First 100 chars..."
  }],
  total_count: 45,
  domain_counts: { "sigils": 12, "signals": 8, ... }
}
```

### `/polly/graph/state` — Graph View State Persistence

```
POST /polly/graph/state
  {
    position: { x: 120.5, y: -45.2 },
    zoom: 1.5,
    filters: { domain: "sigils", type: ["note"], maturity: null },
    expanded_nodes: ["entity-id-123", "entity-id-456"],
    layout: "force-directed"
  }

GET /polly/graph/state
  → Returns last saved graph state (or null if none)
```

---

## Relationship to Existing Specs

### Spec Updates Required

| Spec | Update Needed |
|---|---|
| **ui/spec.md** | Knowledge Graph page moves from "Planned" to designed with navigation model. Notes page sidebar description updated to filtered graph list with lower collapsible panel. Add "Back to Graph" floating button pattern. |
| **notes/spec.md** | Add "Graph-Filtered Navigation" section describing how the sidebar works. Update Knowledge Cards to describe maturity-gated structure. Add non-blocking save suggestions. Remove file-tree as primary navigation description. |
| **knowledge-graph/spec.md** | Add "Navigation Model" section. Update "Dual Hierarchy" to describe filtered list view and primary/secondary domain resolution. Add "Maturity-Gated Structure" section. Add "Garden View" section. Update "UI Integration" under visualization. Add ghosting behavior. Reference this change. |
| **design/spec.md** | Add Recall.ai as a named inspiration for the navigation model. |
| **capture/spec.md** | Note that captures appear as secondary nodes in the graph. |

### Spec Sections That Remain Authoritative (No Changes)

- Entity extraction pipeline (knowledge-graph spec)
- Graph structure / SQLite schema (knowledge-graph spec)
- Authority scoring (knowledge-graph spec)
- Anti-slop mechanisms (knowledge-graph spec)
- Knowledge Quality Pipeline (knowledge-graph spec)
- Augmented writing (knowledge-graph spec) — will integrate with this navigation model
- RAG integration (knowledge-graph spec, rag spec)
- Cytoscape.js technology choice and rendering details (knowledge-graph spec, Phase 12 planning doc)
- Reasoning transparency / "Why This Connection?" (knowledge-graph spec)
- "Explore From Here" mode (knowledge-graph spec)

---

## Implementation: Shipping Together

The graph page and the Notes sidebar refactor ship as a single change. Users get the full experience at once — the graph visualization and the graph-filtered list are two views of the same system, and shipping one without the other would create a disjointed experience.

### Prerequisites (must be working before this change)

- Entity extraction running on all saves (partially implemented in `core/entities/extractor.py`)
- EntityStore with graph operations (implemented in `core/entities/store.py`)
- Authority scoring (implemented in `EntityStore.recompute_authority()`)
- `entity_mentions` table populated with source_type and source_id for all indexed content

### Implementation Sequence

1. **Backend: `/polly/graph/list` endpoint** — Query EntityStore + NoteInfo, return enriched list. This unblocks both frontend views.
2. **Backend: `/polly/graph/nodes` endpoint** — Query EntityStore for nodes + edges with filtering, ghost computation. This unblocks the graph canvas.
3. **Backend: `/polly/graph/state` endpoint** — Simple sessionStorage-like persistence.
4. **Frontend: Shared Browse list component** — Renders the filtered graph list. Used by both the Notes sidebar and the Graph page Browse tab.
5. **Frontend: Notes sidebar refactor** — Replace `updateFileTree()` with `updateBrowseList()`. Add lower collapsible panel with Filters/Backlinks/Tags/TOC sub-tabs.
6. **Frontend: Graph page** — New page with Cytoscape.js canvas, sidebar (Browse + Garden tabs), lower panel (Filters + Details), floating back button.
7. **Frontend: Navigation wiring** — Click-to-open transitions, back-to-graph state management, list-to-graph cross-highlighting.

### Performance

- Cytoscape.js handles 1000+ nodes, but UX defaults to progressive disclosure ("Explore From Here") rather than rendering everything
- List view uses virtual scrolling for large collections
- `/polly/graph/nodes` supports `center_node` + `hops` for progressive graph loading
- Graph state (position, zoom) stored in sessionStorage, not recomputed on every page load
- Ghost nodes are computed server-side (within N hops of filtered nodes) to avoid sending the full graph to the client
