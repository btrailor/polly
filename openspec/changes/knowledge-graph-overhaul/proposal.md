# Knowledge Graph & Garden Overhaul — Proposal

**Date**: 2026-03-04  
**Status**: Complete  
**Priority**: P0 — Multiple critical features broken, core page non-functional  
**Scope**: Frontend (primary) + Backend (entity quality, community detection, suggestion persistence)  
**Depends On**: entity-model-unification (✅ complete), knowledge-graph-refinement (partially implemented)  
**Related Specs**: [knowledge-graph spec](../../specs/knowledge-graph/spec.md)

---

## Problem Statement

The Knowledge Graph page has accumulated extensive technical debt across both the Browse view and Garden view. Many features that are marked "✅ Implemented" in the spec are either non-functional, broken, or produce garbage results. The Garden view in particular is in a state that actively undermines user trust.

### Browse View Issues

#### 1. "Explore From Here" Does Nothing Useful

The `exploreFromNode()` function (`app.js:23922`) fetches a 2-hop neighborhood from the backend and adds new nodes/edges to the existing graph. However, it then re-runs the full layout (`cose`) which redistributes **all** nodes — effectively zooming out to show everything, undoing any focus the user tried to achieve.

**What it does**: Adds neighborhood nodes, re-layouts the entire graph → appears to "zoom out to everything"  
**What it should do**: Isolate the selected node and its connections, hide everything else, providing a focused exploration view with a "Back to full graph" button

**Original design intent** (from knowledge-graph-refinement proposal): The explore feature was meant to let users drill into a node's local neighborhood, seeing only the connected subgraph so they can understand that node's relationship context without noise from the rest of the graph.

#### 2. Ghost Node Toggle Broken

The "Show filtered nodes as ghosts" toggle is supposed to keep filtered-out nodes visible at reduced opacity (e.g., 0.15 opacity with no interaction) so users maintain spatial context. Currently, filtering out a domain (e.g., Sigils) with the ghost toggle enabled **completely removes** those nodes — identical behavior to having ghosts disabled.

**Root cause**: The ghost toggle's backend/frontend integration never maps filtered-but-ghost nodes to the `isGhost: true` data attribute, or the Cytoscape style rules for ghost nodes (`opacity: 0.15`, `events: no`) are not applied.

#### 3. Community Cluster Coloring Broken

When "Color by: Community Cluster" is selected, all nodes appear grey. The community detection algorithm (`intelligence.py:120`) runs label propagation and writes `community_id` to the entities table, but:

1. **Communities are seeded by garbage relationships** — The entity extraction creates entities from trivial fragments like "Ini" (from config file mentions of `__init__`), "Dom" (truncated from "domain"), "Set" (Python keyword). These fragment entities form spurious relationships that poison community detection.
2. **Community IDs may not be populated** — If `detect_communities()` was never run or was run before garbage entities existed, `community_id` is NULL for most entities
3. **Frontend may not fetch community data** — The `/polly/graph/nodes` endpoint may not include `community_id` in the response, so the frontend has nothing to color by

The result: Community clusters show garbage groupings like "Django, Flask" and "Ini, Dom" that have nothing to do with the user's actual knowledge structure.

### Garden View Issues

#### 4. Isolated Notes Doesn't Work

The "Isolated Notes" section in the Garden should show notes with 0-2 connections. Despite the user clearly having notes with zero connections, the isolated notes list is empty.

**Likely cause**: The garden digest endpoint (`/polly/graph/garden/digest`) queries the entity store for isolation, but if notes haven't been through entity extraction, they have no entity record and therefore don't appear in the isolation query (they're invisible to the entity store, not "isolated" within it).

#### 5. Entities Display is Unreadable

The "Isolated Entities" section truncates entity names with `...` and provides no additional context. Users can't read what the entities are, don't understand what an "entity" means in this context, and get zero actionable information.

**Issues**:

- Truncation makes content unreadable
- No explanation of what entities are
- No actions available on entities
- No expansion/tooltip to see full text

#### 6. Merge Candidates Are Garbage

Merge candidates are filled with nonsensical suggestions like:

- "Dom" merge to "Domain" (fragment from truncated extraction)
- "Set" merge to "Massachusetts" (substring match, not semantic similarity)
- "Ini" merge to "Initialize" (config file noise)

**Root cause**: Entity extraction creates entities from trivial fragments, common words, and code artifacts. The merge candidate algorithm uses string similarity (possibly Jaccard on character n-grams, per `_keyword_overlap()` in `intelligence.py:400`) which matches substrings rather than semantic meaning. "Set" and "Massachusetts" share characters s-e-t, triggering a false merge candidate.

#### 7. Suggestion Persistence Broken

- **Dismissing suggestions doesn't persist** — When you click X on a suggestion, `item.remove()` removes the DOM element but doesn't call any backend endpoint to record the dismissal. The next time the Garden loads, the same suggestion reappears.
- **Accepting suggestions gives no confirmation** — When you accept a connection or merge, the item fades out (opacity transition) but there's no success toast or clear indication the action completed. The next app restart shows the same suggestion again if the backend acceptance didn't actually persist (possible API failure silently caught).
- **No `dismissed_suggestions` state** — There is no table, local storage key, or API endpoint tracking which suggestions have been dismissed.

#### 8. Garden Maintenance Always Returns 0

"Prune weak links," "Remove stale entities," and "Enrich notes" always report 0 items processed because:

- **Prune weak links** (`weak_threshold=0.3`): If all relationships have default strength 0.5 (set during entity extraction), none are below 0.3
- **Remove stale entities** (`stale_days=180`): If the app is less than 180 days old, no entities are stale
- **Enrich notes**: If `enrichment_candidates` is empty (the query returns 0 candidates), the batch enrich has nothing to process

The thresholds are hardcoded and not calibrated to the user's actual data.

#### 9. Garden Health Sidebar Layout

The Garden Health display in the left sidebar requires horizontal scrolling to view fully. Side-scrolling in a sidebar is a poor UX pattern. The content overflows because it's rendered with fixed-width inline styles that don't respect the sidebar's width constraints.

**Desired**: The sidebar should either be resizable, or (more importantly) the content should wrap/reflow to fit the available width. Stats should stack vertically if needed rather than requiring horizontal scroll.

---

## Goals

1. **Fix "Explore From Here"** — isolate the selected node's subgraph, hide unrelated nodes, provide back navigation
2. **Fix ghost node toggle** — filtered nodes appear at reduced opacity when ghost mode is enabled
3. **Fix community cluster coloring** — clean up garbage entities first, then re-run community detection with meaningful results
4. **Fix isolated notes** — detect notes not in the entity store as truly isolated
5. **Make entity display readable** — full names, explanations, expandable details, actions
6. **Fix merge candidates** — filter out fragment entities, use semantic similarity not character overlap
7. **Persist suggestion state** — dismissed suggestions stay dismissed, accepted suggestions show confirmation and don't reappear
8. **Fix maintenance tools** — calibrate thresholds to actual data, show meaningful results
9. **Fix sidebar layout** — responsive content that doesn't require horizontal scroll
10. **Comprehensive Garden redesign** — make the Garden useful, clear, and beautiful

---

## Non-Goals

- Adding new entity extraction methods (LLM-based extraction is Phase 12c)
- 3D graph visualization
- Real-time collaborative graph editing
- Rebuilding the Cytoscape.js integration from scratch
- Library/book entity integration (Phase 12d)

---

## Success Criteria

1. "Explore From Here" shows only the selected node + its direct/2-hop connections; a "Back to full graph" button restores the complete view
2. Ghost toggle works: filtered nodes visible at 15% opacity, non-interactive, maintaining spatial context
3. Community coloring produces 3-10 meaningful clusters that correspond to the user's knowledge domains/topics
4. Isolated notes section includes ALL notes with 0 entity connections, including notes never processed by entity extraction
5. Entity display shows full name (no truncation), type badge, mention count, and expandable details
6. Merge candidates exclude fragment entities (< 3 chars, common programming keywords). Similarity uses semantic comparison, not character overlap
7. Dismissed suggestions persist across sessions. Accepted suggestions show success confirmation and don't reappear
8. Maintenance tools process real items: prune shows count before confirming, thresholds adapt to data
9. Sidebar content reflows without horizontal scrolling at any reasonable sidebar width (≥200px)
10. Garden view is organized into clear, labeled sections with consistent styling and useful information density

---

## User Stories

**As a user exploring a specific node**, I want "Explore From Here" to show me only that node's neighborhood so I can understand its connections without distraction from the rest of the graph.

**As a user filtering domains**, I want filtered nodes to appear as ghosts so I maintain spatial awareness of the full graph structure while focusing on specific domains.

**As a user viewing community clusters**, I want clusters that reflect actual topic groupings in my knowledge, not random word fragments.

**As a user maintaining my knowledge garden**, I want to dismiss bad suggestions permanently and see clear confirmation when I accept good ones.

**As a user with many notes**, I want the Garden to show me actionable maintenance tasks — notes that need connections, entities that should be merged, weak links that could be pruned — with accurate counts, not zeros.

---

## Technical Approach

### Phase 1: Entity Quality Cleanup (Backend — Foundation for Everything)

Before fixing any frontend features, the entity store needs garbage cleanup:

**1a. Entity validation and pruning:**

- Add entity validation rules to `EntityExtractor`:
  - Minimum name length: 3 characters (removes "Ini", "Dom", "Set")
  - Exclude common programming keywords: `set`, `get`, `int`, `str`, `list`, `dict`, `map`, `for`, `if`, etc.
  - Exclude single common English words below a significance threshold
  - Require entities to have at least 1 mention from actual note content (not config/code files)
- Add `POST /polly/graph/garden/cleanup` endpoint that:
  1. Identifies and removes garbage entities matching the above rules
  2. Re-runs community detection after cleanup
  3. Returns count of removed entities

**1b. Merge candidate algorithm improvement:**

- Replace character-overlap similarity with a multi-factor score:
  1. **Normalized edit distance** (Levenshtein) — catches true typo variants ("Sigils" / "Sigisl")
  2. **Semantic check** — if both entities have descriptions, compare them; if one is a substring of another (e.g., "ML" and "Machine Learning"), flag as likely merge
  3. **Alias check** — check if one entity's name appears in another's aliases
  4. **Context overlap** — check if both entities appear in the same notes (co-occurrence > random chance)
- Set a minimum confidence of 0.6 for merge candidates (current threshold too low)
- Exclude pairs where both entities are common words

### Phase 2: Browse View Fixes (Frontend)

**2a. Fix "Explore From Here":**

- When triggered, instead of adding nodes to existing graph:
  1. Store current graph state (node positions, visibility)
  2. Hide ALL nodes except the selected node + its neighborhood (1-2 hops)
  3. Apply a local layout (concentric, with selected node at center)
  4. Show a "Back to full graph" button/breadcrumb
  5. Clicking "Back" restores the saved state
- Consider adding a depth control: "1 hop" / "2 hops" toggle during exploration

**2b. Fix ghost node toggle:**

- When filters are applied with ghost mode ON:
  1. Nodes matching filters: visible, fully interactive (opacity 1.0)
  2. Nodes NOT matching filters: visible at opacity 0.15, `pointer-events: none`, greyed label
  3. Edges between ghost nodes: hidden
  4. Edges between a visible node and a ghost node: visible at opacity 0.1
- Implementation: Use Cytoscape style classes rather than removing/adding elements
  ```javascript
  cy.style()
    .selector(".ghost-node")
    .style({
      opacity: 0.15,
      events: "no",
      label: "", // or keep label but at very low opacity
    })
    .update();
  ```
- When filters change, toggle `.ghost-node` class instead of removing elements from the graph

**2c. Fix community cluster coloring:**

- After entity cleanup (Phase 1), re-run `detect_communities()`
- Ensure `/polly/graph/nodes` response includes `community_id` for each node
- Frontend: maintain a `communityColors` palette (10-15 distinct colors)
- When "Color by: Community" selected, map `community_id` → color
- Nodes with `community_id: null` get a neutral grey
- Add community labels as an overlay legend (e.g., "Cluster 1: Sigils, Norns, SuperCollider")

### Phase 3: Garden View Overhaul (Frontend + Backend)

**3a. Fix isolated notes detection:**

- Modify the garden digest endpoint to query BOTH:
  1. Notes in the entity store with 0-2 connections (current behavior)
  2. Notes in the file index that have NO entity store record at all (truly unprocessed notes)
- Merge both lists, deduplicate, sort by creation date (newest first)
- Each isolated note shows: title, domain, creation date, "Enrich" button (triggers entity extraction)

**3b. Make entity display readable:**

- Remove truncation (`...`) — show full entity name
- Each entity item shows:
  - Full name (bold)
  - Type badge (concept, tool, person, project, etc.)
  - Mention count
  - Source notes (first 2-3, expandable)
- Add tooltip with description if available
- Add clear section header: "Entities are concepts, tools, people, and topics extracted from your notes. Isolated entities have no connections to other entities."
- Make entity items clickable → opens entity detail view or navigates to graph centered on that entity

**3c. Fix merge candidates (display):**

- Show only merge candidates from the improved algorithm (Phase 1b)
- Each candidate shows:
  - Full names of both entities
  - Confidence score with visual indicator
  - Reason for merge suggestion (shown in full, not truncated)
  - "These entities appear in the same X notes" context
  - Preview of what the merge would do
- Accept/Dismiss buttons with clear labels

**3d. Persist suggestion state:**

**Backend:**

- Add `dismissed_suggestions` table to `entities.db`:
  ```sql
  CREATE TABLE IF NOT EXISTS dismissed_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suggestion_type TEXT NOT NULL,  -- 'connection', 'merge', 'enrichment'
    suggestion_key TEXT NOT NULL,   -- unique key (e.g., "entity_a_id:entity_b_id" for merge)
    dismissed_at TEXT NOT NULL,
    UNIQUE(suggestion_type, suggestion_key)
  );
  ```
- Add `POST /polly/graph/garden/suggestion/dismiss` endpoint
- Modify suggestion generation queries to exclude dismissed suggestions
- Add `accepted_suggestions` table similarly for tracking what was accepted

**Frontend:**

- When user clicks X (dismiss): call dismiss endpoint, then remove DOM element
- When user clicks ✓ (accept): call accept endpoint, show success toast ("Connection created!" / "Entities merged!"), animate item out, store in accepted log
- On Garden load: suggestions exclude dismissed and accepted items

**3e. Fix maintenance tools:**

- **Prune weak links**: Before confirming, query the backend for count of relationships below threshold. Show: "Found 12 connections below 0.3 strength. Prune them?" If count is 0, show: "All connections are above the threshold. Try raising it?" Offer a slider for the threshold (0.1–0.5, default 0.3)
- **Remove stale entities**: Same pattern — query count first. Offer a days slider (30–365, default 90 instead of 180). Show: "Found 8 entities with no mentions in the last 90 days"
- **Enrich notes**: Query for unenriched note count. Show: "Found 15 notes without entity extraction. Enrich them?" If 0: "All notes are enriched!"
- All three should show actual counts before the action, not just after

**3f. Fix sidebar layout:**

- Replace inline `style` attributes with CSS classes
- Garden health stats: use CSS Grid with `auto-fit` columns that wrap at narrow widths:
  ```css
  .garden-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 8px;
  }
  ```
- `overflow-x: hidden` on sidebar container
- Consider making sidebar resizable (CSS `resize: horizontal` or a drag handle) — but prioritize responsive reflow first
- All text in sidebar wraps (`word-wrap: break-word; overflow-wrap: break-word`)
- Test at sidebar widths of 200px, 250px, 300px, 400px

### Phase 4: Garden Visual Redesign

Reorganize the Garden into clear, well-labeled sections with consistent component patterns:

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  🌱 Knowledge Garden                                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Health Overview                                   │   │
│  │ [Notes: 47] [Entities: 312] [Coverage: 73%]      │   │
│  │ [Connections: 891] [Avg Authority: 0.45]          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 📋 Suggestions                    [Connections]   │   │
│  │                     [Merges] [Enrichment]         │   │
│  │                                                   │   │
│  │  Note A ↔ Note B                                  │   │
│  │  "Both discuss SuperCollider synthesis"            │   │
│  │  Confidence: 82%        [Accept] [Dismiss]        │   │
│  │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─        │   │
│  │  ...more suggestions...                           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 🏝️ Isolated Notes (5)                             │   │
│  │                                                   │   │
│  │  Note Title          Domain    [Enrich] [View]    │   │
│  │  Another Note        Signals   [Enrich] [View]    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 🔧 Maintenance                                    │   │
│  │                                                   │   │
│  │  [Prune Weak Links (12 found)]                    │   │
│  │  [Remove Stale Entities (8 found)]                │   │
│  │  [Enrich Unenriched Notes (15 found)]             │   │
│  │  [Clean Up Garbage Entities (23 found)]           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

- Consistent card-based sections with clear headers
- Counts shown inline so user knows what to expect before clicking
- Collapsible sections (expanded by default, remembers state)
- Use proper CSS components, not inline styles
- Responsive — works at any container width

---

## Risks & Mitigations

**Risk**: Entity cleanup removes legitimate short-name entities (e.g., "AI", "ML", "JS")  
**Mitigation**: Maintain a whitelist of known-good short entities. Only remove entities below 3 chars that aren't on the whitelist. User can undo cleanup within 30 days (soft delete to trash table).

**Risk**: Community detection still produces poor clusters after cleanup  
**Mitigation**: If label propagation produces < 3 meaningful communities, fall back to domain-based clustering (entities grouped by their primary domain). Show "Communities approximate — based on domain grouping" label.

**Risk**: Suggestion persistence table grows without bound  
**Mitigation**: Auto-expire dismissed suggestions after 90 days. Limit table to 1000 rows with FIFO cleanup.

**Risk**: "Explore From Here" state management creates layout bugs  
**Mitigation**: Store/restore is a snapshot of positions, not a complex state machine. Worst case: "Back to full graph" triggers a full re-layout (slow but correct). Add timeout safeguard.

**Risk**: Sidebar resizing creates z-index/overlap issues with main content  
**Mitigation**: Start with responsive reflow only. Add resize handle as a follow-up if reflow alone isn't sufficient. Test thoroughly at various widths.

---

## Timeline Estimate

- Phase 1 (Entity cleanup + merge algorithm): 8 hours
- Phase 2 (Browse view fixes — explore, ghost, community): 8 hours
- Phase 3 (Garden fixes — isolation, entities, suggestions, maintenance, sidebar): 12 hours
- Phase 4 (Garden visual redesign): 6 hours
- CSS + Polish + Testing: 4 hours

**Total: ~38 hours** (5-6 working days)

---

## Related Work

- Knowledge Graph spec: [openspec/specs/knowledge-graph/spec.md](../../specs/knowledge-graph/spec.md)
- Knowledge Graph refinement: [openspec/changes/knowledge-graph-refinement/](../knowledge-graph-refinement/)
- Knowledge Graph advanced (12b): [openspec/changes/knowledge-graph-advanced/](../knowledge-graph-advanced/)
- Entity model unification: [openspec/changes/entity-model-unification/](../entity-model-unification/)
- Frontend graph code: `electron-app/src/renderer/app.js` (lines ~23000-25500)
- Backend entity store: `core/entities/store.py`
- Backend intelligence: `core/entities/intelligence.py`
- Backend garden endpoints: `interfaces/server.py` (lines ~4900-5200)
- Garden CSS: `electron-app/src/renderer/styles/main.css` (lines ~6861-7319)

---

## Open Questions

1. **Should "Explore From Here" be a separate view or an overlay on the main graph?** → Proposed: overlay with stored state + back button. Easier to implement, less disorienting for users.

2. **Should garbage entity cleanup run automatically on startup?** → No — run once manually via "Clean Up Garbage Entities" button, then prevent garbage creation with validation rules on new extractions.

3. **Should community detection re-run automatically after entity changes?** → Yes, but debounced — at most once per hour, triggered by entity count changes > 5%.

4. **For merge candidates, should we use embedding similarity if available?** → Yes — if ChromaDB embeddings exist for entity descriptions, use cosine similarity as the primary signal. Fall back to edit distance + co-occurrence if embeddings aren't available.

5. **Should the Garden have a "health score" (0-100) displayed prominently?** → Yes — composite score from: coverage %, isolation rate, merge candidate count, average authority. Gives users an at-a-glance understanding of knowledge graph health.

6. **Should we add an "Entity Inspector" view accessible from the Garden?** → Defer — useful but not critical. Focus on fixing what's broken first. Entity details accessible via graph node click in Browse view.
