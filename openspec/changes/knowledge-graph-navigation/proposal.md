# Knowledge Graph Navigation — Proposal

**Tier:** 3 (Knowledge Platform)
**Scope:** Frontend + Backend API
**Status:** Designed, not started
**Created:** February 2026
**Depends On:** [entity-model-unification/](../entity-model-unification/) (completed), Phase 12a-ext (Knowledge Graph foundation)
**Blocks:** Nothing (can be built incrementally alongside existing Notes page)

---

## What We're Doing

Elevating the knowledge graph from an analytical visualization tool to the **primary navigation model** for Polly's knowledge base. The graph becomes a first-class page and the organizational substrate that connects all content — notes, captures, books, conversations, code, canvases. The existing Notes file tree is reconceived as a filtered, list-dressed view of the same graph structure.

This change reconciles two things that are currently separate in the specs:
1. The **Notes page** (folder-based file tree navigation)
2. The **Knowledge Graph page** (planned as a separate Cytoscape.js visualization)

After this change, these are two views of the same underlying structure — one visual (graph), one textual (filtered list) — with the graph as the source of truth for organization.

## Why

### Current State

The knowledge-graph spec describes a comprehensive system: entity extraction, SQLite graph structure, authority scoring, anti-slop mechanisms, augmented writing, Cytoscape.js visualization. The entity foundation (`core/entities/`) is implemented.

But the specs treat the graph as an **analytical tool** — a page you visit to visualize connections. Meanwhile, the Notes page remains a conventional folder-based file tree. The two experiences are disconnected: you browse notes in folders, and separately, you visit a graph page to see how things connect.

This contradicts design principle #7: "Emergence over prescription — organization emerges from connection patterns, not folder hierarchies."

### What's Wrong

1. **The graph page and the notes page are separate destinations.** A user who discovers a connection in the graph can't act on it (open, edit, link) without leaving the graph and navigating the file tree.

2. **The file tree reflects file system structure, not knowledge structure.** Domain folders are an intentional hierarchy, but they don't surface emergent connections, authority, or isolation.

3. **The Knowledge Quality Pipeline produces data that has no navigation surface.** Entity extraction, connection metrics, and authority scoring run on save — but these signals aren't visible in how users navigate content.

4. **Recall-inspired architecture is designed but orphaned.** The Recall-inspired concepts (auto-connections, dual hierarchy, card structure, connection thresholds) are fully specified in the knowledge-graph spec but have no UI design for how users interact with them during navigation.

### What We Get

- **One navigation model** where all indexed content (notes, books, captures, conversations, code) is discoverable through connections, not just folder paths
- **The file tree becomes a filtered graph view** — same data, list presentation, with graph metadata progressively disclosed
- **The graph page becomes the primary exploration surface** — click any node to open it in the viewer, with a floating back-button to return to graph position
- **Knowledge quality signals become navigation cues** — authority, isolation, hub/bridge status inform how users encounter their content
- **Foundation for augmented writing, garden maintenance, and all other Knowledge Quality features** — they have a navigation context to live in

## Architecture: Recall-Inspired Principles

This proposal operationalizes the Recall-inspired architecture that was documented during knowledge graph planning but not fully incorporated into the UI/navigation specs:

### 1. Automatic Entity Extraction + Graph Structure

Content is organized by extracted entities and their connections, not by folder placement. When new content arrives, entity extraction identifies concepts, people, tools, and frameworks, and automatically links to existing matching nodes. Folder/domain placement becomes one signal among many, not the primary organizational axis.

### 2. Dual Hierarchy: User Tags + Auto-Connections

Both coexist. User-created structure (folders, domains, wiki-links, manual tags) provides intentional organization. Auto-generated entity connections provide emergent organization. The auto-categorization respects existing structure — if the user has a "Machine Learning" domain, new ML content routes there rather than creating competing categories.

### 3. Freeform Capture, Structured Integration (Model C)

Users write freely. The system proposes structure on save: entity extraction, connection suggestion, metadata inference. The structured path is the path of least resistance without blocking the unstructured path. Save-time suggestions are **non-blocking** — they appear as a notification or sidebar hint, not a modal that interrupts flow.

### 4. Maturity-Gated Structure

Structure scales with note maturity:
- **30-Ideas:** Freeform. No required fields. Auto-generated frontmatter (title, date, domain, extracted entities) wraps the content silently.
- **20-Active:** System prompts for structure. "Add key concepts?" "Link to related project?" Gentle nudges toward connection.
- **10-Archive:** Full card treatment. Structured summary, confirmed entities, authority assessment. The note has earned its structure through use.

### 5. System-Driven + Manual Graph (Hybrid)

Entity extraction output + auto-connections are the base layer. The graph works even if the user never manually links anything. But manual wiki-links add intentional connections the AI might miss, and are encouraged. Both layers are visible in the graph.

---

## Scope

### In Scope

1. **Graph page** — New top-level page (lucide `graph` icon in ribbon). Cytoscape.js visualization of the full entity graph. Nodes for all indexed content types. Full transition to item viewer on node click, with floating back-to-graph button preserving graph position/zoom.

2. **Graph left sidebar** — Page-specific sidebar with graph controls (layout selector, filter by content type, filter by domain, search, zoom controls). Further sidebar contents to be brainstormed.

3. **File tree as filtered graph list** — The existing Notes file tree is reconceived as a list view of graph nodes, filtered by connections. Domain filters replace folder navigation. Graph metadata (connection count, authority, hub/bridge/isolated status) progressively disclosed on hover/selection.

4. **Node type visual hierarchy** — Notes are primary nodes (larger, brighter). Other content types (conversations, books, captures, code) are secondary — smaller nodes, distinct shapes/colors, expand on interaction.

5. **Non-blocking save-time suggestions** — When content is saved, entity extraction runs and suggested connections appear as a non-blocking notification (e.g., "3 connections found"). User can review later or ignore.

6. **Maturity-gated structure prompts** — Ideas-stage notes get silent auto-metadata. Active notes get gentle structure suggestions. Archive notes get full card treatment.

7. **Back-to-graph navigation** — Floating button visible whenever a user navigated to content from the graph. Returns to exact graph position/zoom state.

### Out of Scope

- Cytoscape.js rendering implementation details (covered in existing Phase 12 planning)
- Backend entity extraction changes (already designed in knowledge-graph spec)
- Mobile/responsive graph layout (defer to mobile spec)
- Graph sharing or collaboration features
- "Explore From Here" mode details (already designed in knowledge-graph spec)
- Augmented writing panel (already designed; will integrate with this navigation model when built)

## Backend vs Frontend

**Primarily frontend** with API additions:

- **Frontend:** New Graph page component, Cytoscape.js integration, file tree refactor to graph-filtered list, navigation state management (graph position persistence), progressive disclosure of graph metadata, save-time suggestion notifications.
- **Backend API additions:** Graph data endpoint (nodes + edges for Cytoscape.js), filtered node list endpoint (for list view), graph position/state persistence.
- **Backend logic:** No changes to entity extraction, Knowledge Quality Pipeline, or authority scoring — those are already designed/implemented.

## Relationship to Other Work

| Change/Spec | Relationship |
|---|---|
| **knowledge-graph spec** | This change operationalizes the visualization and navigation sections. The spec's backend design (entity extraction, authority scoring, anti-slop, quality pipeline) remains authoritative. This change adds the navigation/UX layer. |
| **notes spec** | Notes remain the primary content type. The Notes page file tree is refactored but not removed — it becomes a filtered graph list. Editor, TOC, templates, auto-save are unchanged. |
| **ui spec** | The planned "Knowledge Graph" page is realized here. The planned "Connection Metrics in Notes" and "Augmented Writing Panel" integrate with this navigation model. |
| **cursor-ui-pattern-migration** | The graph page follows the same layout patterns: left sidebar + main content + chat panel. The Notes page sidebar content changes (from folder tree to filtered graph list) but the layout structure is compatible. |
| **capture spec** | Captures enter the graph through the existing Knowledge Quality Pipeline. They appear as secondary nodes in the graph. |
| **design spec** | Directly implements principle #7 (emergence over prescription) and principle #3 (capture over perfection). |

## Design Reference

- **Recall.ai** — Auto-connection architecture, knowledge cards, dual hierarchy, connection metrics, augmented browsing. Primary inspiration for the organizational model.
- **Obsidian Graph View** — Visual reference for node rendering, but Polly's graph is navigational (not just analytical).
- **Roam Research** — Daily notes + graph sidebar as alternative to folder navigation.
- **Cursor** — Layout patterns for the page structure (left sidebar, main content, chat panel).

## Open Questions

1. **Graph left sidebar contents** — Beyond filters and layout controls, what else belongs here? Recent nodes? Pinned nodes? Saved graph views/filters?
2. **Graph URL state** — Should the graph position/zoom/filter state be reflected in the URL for shareability and browser back/forward?
3. **Performance threshold** — At what node count does the graph need pagination, clustering, or level-of-detail rendering? The spec says Cytoscape.js handles 1000+ nodes, but UX may degrade earlier.
4. **Default graph view** — When a user first opens the graph page, what do they see? Full graph? Their most recent domain? High-authority nodes only?
5. **Transition from current Notes page** — Is this a gradual migration (graph features added to existing Notes page) or a one-time transition (new Graph page replaces Notes page)?
