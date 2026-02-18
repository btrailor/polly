# Knowledge Graph Refinement — Design

**Date**: 2026-02-18  
**Status**: Ready for Implementation  
**Related**: proposal.md, tasks.md

---

## Architecture Overview

This change is purely additive and refinement-focused. No existing functionality is removed or changed in breaking ways. All changes enhance the existing knowledge graph system.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Electron)                       │
├─────────────────────────────────────────────────────────────┤
│  Graph Canvas (Cytoscape.js)                                │
│  ├─ Layout: cose-bilkent (NEW)                             │
│  ├─ Edge type toggles (NEW)                                │
│  ├─ Ghost node toggle (FIXED)                              │
│  └─ Filter state management                                │
├─────────────────────────────────────────────────────────────┤
│  Filters Panel (Lower Panel)                                │
│  ├─ Layout selector (existing)                             │
│  ├─ Edge type legend + toggles (NEW)                       │
│  ├─ Domain filter (ENABLED)                                │
│  ├─ Content type filter (NEW)                              │
│  ├─ Authority threshold (NEW)                              │
│  └─ Ghost toggle (FIXED)                                   │
├─────────────────────────────────────────────────────────────┤
│  Garden View (Sidebar Tab)                                  │
│  ├─ Stats Dashboard (NEW)                                  │
│  ├─ Connection Suggestions (NEW)                           │
│  ├─ Merge Candidates (NEW)                                 │
│  ├─ Isolated Notes (ENHANCED)                              │
│  ├─ Enrichment Queue (NEW)                                 │
│  └─ Prune Tools (NEW)                                      │
├─────────────────────────────────────────────────────────────┤
│  Details Panel (Lower Panel)                                │
│  ├─ Node info + actions (ENHANCED)                         │
│  ├─ Connections list with remove (NEW)                     │
│  ├─ Add connection UI (NEW)                                │
│  └─ Entity list (NEW)                                      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  Existing Endpoints (unchanged)                              │
│  ├─ GET /polly/graph/nodes                                  │
│  ├─ GET /polly/graph/list                                   │
│  └─ POST /polly/graph/backfill                              │
├─────────────────────────────────────────────────────────────┤
│  New Garden Endpoints                                        │
│  ├─ GET /polly/graph/garden/stats                           │
│  ├─ GET /polly/graph/garden/suggestions                     │
│  ├─ POST /polly/graph/garden/enrich                         │
│  ├─ POST /polly/graph/garden/connection                     │
│  ├─ POST /polly/graph/garden/merge                          │
│  └─ DELETE /polly/graph/garden/prune                        │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                Core Data Layer (Python)                      │
├─────────────────────────────────────────────────────────────┤
│  EntityStore (SQLite)                                        │
│  ├─ New methods for garden features                         │
│  ├─ get_mentions_for_source()                               │
│  ├─ move_mentions()                                         │
│  ├─ prune_weak_relationships()                              │
│  ├─ prune_stale_entities()                                  │
│  └─ remove_relationship()                                   │
├─────────────────────────────────────────────────────────────┤
│  Existing Indices (unchanged)                                │
│  ├─ NotesIndex                                              │
│  ├─ BacklinksIndex                                          │
│  ├─ UnlinkedMentionsIndex                                   │
│  └─ TagsIndex                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: Layout Engine Switch

### Problem Analysis

Current layout configuration (app.js:18138-18155):
```js
name: 'cose',
nodeRepulsion: 800000,   // High repulsion but...
idealEdgeLength: 150,    // Short edges and...
gravity: 40,             // STRONG CENTER PULL → causes tight clustering
```

The `gravity: 40` parameter is the culprit. It pulls all nodes toward the center with 40x force, completely negating the repulsion. Combined with short ideal edge length (150) and small node sizes (12-36px), the result is an unreadable cluster.

### Solution: cose-bilkent

Cytoscape-cose-bilkent is a more sophisticated layout algorithm designed for compound graphs with better overlap prevention. Already installed as a dependency, just unused.

**New layout config**:
```js
name: 'cose-bilkent',
animate: 'end',          // Animate only at end (faster)
animationDuration: 500,
fit: true,
padding: 80,             // More breathing room (was 50)
nodeRepulsion: 6500,     // Tuned for spread
idealEdgeLength: 200,    // Longer edges (was 150)
edgeElasticity: 0.45,    // Edge flexibility
nestingFactor: 0.1,      // Low nesting (flat graph)
gravity: 0.25,           // WEAK center pull (was 40!)
gravityRange: 3.8,       // Gravity falloff distance
numIter: 2500,           // More iterations (was 1000)
tile: true,              // Separate disconnected components
tilingPaddingVertical: 40,
tilingPaddingHorizontal: 40,
nodeDimensionsIncludeLabels: true
```

**Node size increase** (for better readability):
- Current: `12 + (authority * 24)` → range 12-36px
- New: `16 + (authority * 32)` → range 16-48px

**Implementation**:
1. Add `<script src="cytoscape-cose-bilkent.js"></script>` to index.html after cytoscape.min.js
2. Register plugin in `initGraphPage()`: `cytoscape.use(cytoscapeCoseBilkent);`
3. Replace cose config in `getLayoutConfig()` with cose-bilkent params
4. Fix Reset button to use same config instead of ad-hoc params

---

## Part 2: Edge Type Legend & Toggles

### Current State

Edges are visually differentiated:
- `references` (backlinks): solid gray #888888
- `mention` (unlinked): dashed blue #45B7D1
- `shared_tag`: dotted green #52B788
- `relates_to`: dashed gray #555555
- `co_occurs_with`: dotted gray #555555

But there's no legend and no control.

### Design

**Filters Panel Addition** (between Layout and Ghost toggle):

```
Connection Types
  ☑ ── References (backlinks)     ← solid line sample, #888888
  ☑ -- Mentions (unlinked)        ← dashed line sample, #45B7D1
  ☑ ·· Shared Tags               ← dotted line sample, #52B788
  ☑ -- Relates To (entities)      ← dashed line sample, #555555
  ☑ ·· Co-occurs With            ← dotted line sample, #555555
```

Each row: checkbox + visual line sample (matching actual edge style) + label

**Interaction**:
- Unchecking a type: `cytoscapeInstance.edges('[relationshipType="X"]').style('display', 'none')`
- Checking a type: `cytoscapeInstance.edges('[relationshipType="X"]').style('display', 'element')`
- State persisted in `graphState.filters.edgeTypes: string[]`

**Implementation**:
```js
function toggleEdgeType(edgeType, visible) {
  if (!cytoscapeInstance) return;
  
  // Update state
  if (!graphState.filters.edgeTypes) {
    graphState.filters.edgeTypes = ['references', 'mention', 'shared_tag', 'relates_to', 'co_occurs_with'];
  }
  if (visible) {
    if (!graphState.filters.edgeTypes.includes(edgeType)) {
      graphState.filters.edgeTypes.push(edgeType);
    }
  } else {
    graphState.filters.edgeTypes = graphState.filters.edgeTypes.filter(t => t !== edgeType);
  }
  
  // Apply style
  cytoscapeInstance.edges().forEach(edge => {
    if (edge.data('relationshipType') === edgeType) {
      edge.style('display', visible ? 'element' : 'none');
    }
  });
  
  saveGraphState();
}
```

---

## Part 3: Filtered Views Implementation

### Domain Filter (Enable)

Currently disabled with "Coming soon" message. Enable by:
1. Populate dropdown from `graphDomainColors` (computed at line 17981)
2. On change: update `graphState.filters.domain`, call `applyGraphFilters()`

```js
<select id="graph-domain-filter">
  <option value="">All Domains</option>
  ${Object.keys(graphDomainColors || {}).map(d => 
    `<option value="${d}" ${graphState.filters.domain === d ? 'selected' : ''}>${d}</option>`
  ).join('')}
</select>
```

### Content Type Filter (New)

Multi-select checkboxes for: note, conversation, book, capture, code, canvas

```js
<div class="content-type-toggles">
  ${['note', 'conversation', 'book', 'capture', 'code', 'canvas'].map(type => {
    const checked = !graphState.filters.types || graphState.filters.types.includes(type);
    return `<label>
      <input type="checkbox" class="content-type-cb" data-content-type="${type}" ${checked ? 'checked' : ''}>
      <i data-lucide="${iconMap[type]}"></i> ${type}s
    </label>`;
  }).join('')}
</div>
```

On change: collect checked types into `graphState.filters.types: string[]`, call `applyGraphFilters()`

### Authority Threshold (New)

Range slider 0.0-1.0 with live value display:

```js
<label>
  Min Authority: <span id="authority-value">0.0</span>
</label>
<input type="range" id="graph-authority-filter" min="0" max="1" step="0.1" value="0">
```

On change (debounced 300ms): `graphState.filters.authority_min = value`, call `applyGraphFilters()`

### Ghost Toggle (Fix)

Replace the TODO with actual implementation:

```js
ghostToggle.addEventListener('change', (e) => {
  const showGhosts = e.target.checked;
  graphState.filters.showGhosts = showGhosts;
  
  if (cytoscapeInstance) {
    cytoscapeInstance.nodes().forEach(node => {
      if (node.data('isGhost')) {
        node.style('display', showGhosts ? 'element' : 'none');
      }
    });
    cytoscapeInstance.edges().forEach(edge => {
      if (edge.data('isGhost')) {
        edge.style('display', showGhosts ? 'element' : 'none');
      }
    });
  }
  
  saveGraphState();
});
```

### Unified Filter Application

```js
let filterDebounce = null;

async function applyGraphFilters() {
  clearTimeout(filterDebounce);
  filterDebounce = setTimeout(async () => {
    // Save viewport before re-fetching
    if (cytoscapeInstance) {
      graphState.position = cytoscapeInstance.pan();
      graphState.zoom = cytoscapeInstance.zoom();
    }
    saveGraphState();
    
    // Re-initialize with new filters (reads from graphState.filters)
    await initGraphCanvas();
  }, 300);
}
```

All filter changes call this function. It debounces, saves state, and re-fetches `/polly/graph/nodes` with updated params.

---

## Part 4: Backend Garden Endpoints

### GET /polly/graph/garden/stats

Returns maintenance statistics for the dashboard.

**Query**: None  
**Response**:
```json
{
  "total_notes": 127,
  "total_connections": 543,
  "total_entities": 89,
  "isolated_count": 12,
  "enriched_count": 98,
  "unenriched_count": 29,
  "coverage_pct": 77.2,
  "avg_connections": 4.3,
  "domain_counts": {
    "sigils": 45,
    "signals": 32,
    "scrolls": 28,
    "Uncategorized": 22
  },
  "unenriched_notes": ["note1.md", "note2.md", ...]  // first 20
}
```

**Implementation**:
- Query `NotesIndex.get_all_notes()` for total count
- Query `BacklinksIndex` for connection counts per note
- Query `EntityStore.get_mentions_for_source()` to determine enriched vs. unenriched
- Compute coverage percentage: `enriched / total * 100`

### GET /polly/graph/garden/suggestions

Returns connection suggestions, merge candidates, and enrichment queue.

**Query**: `limit=20` (optional)  
**Response**:
```json
{
  "connection_suggestions": [
    {
      "source_id": "docker-deploy.md",
      "source_name": "Docker Deployment Guide",
      "target_id": "docker-compose.md",
      "target_name": "Docker Compose Setup",
      "reason": "'docker-compose' is mentioned in 'Docker Deployment Guide' but not linked",
      "type": "unlinked_mention",
      "confidence": 0.8
    }
  ],
  "merge_candidates": [
    {
      "notes": ["ai-agents.md", "llm-agents.md"],
      "shared_entity_count": 7,
      "overlap_ratio": 0.73,
      "reason": "Share 7 entities with 73% overlap"
    }
  ],
  "enrichment_candidates": [
    {
      "note_id": "old-note.md",
      "note_name": "Old Note",
      "reason": "No entities extracted yet",
      "domain": "signals"
    }
  ]
}
```

**Implementation**:
- **Connection suggestions**: Query `UnlinkedMentionsIndex`, cross-check with `BacklinksIndex` to exclude already-linked pairs
- **Merge candidates**: Build entity sets per note, find pairs with high Jaccard similarity (>0.5) and absolute overlap (>3 shared entities)
- **Enrichment candidates**: Notes with zero entity mentions in `EntityStore`

### POST /polly/graph/garden/enrich

Triggers entity extraction on specified notes.

**Body**:
```json
{
  "note_ids": ["note1.md", "note2.md"]  // or empty array for "all unenriched"
}
```

**Response**:
```json
{
  "enriched_count": 2,
  "total_entities": 15,
  "results": [
    {
      "note_id": "note1.md",
      "note_name": "Note Title",
      "entities_extracted": 8,
      "entities": [
        {"id": "entity-123", "name": "Docker", "type": "tool", "description": "..."},
        ...
      ]
    }
  ]
}
```

**Implementation**:
1. For each `note_id`, read note content from disk
2. Call `EntityExtractor.extract(content)`
3. For each extracted entity: `EntityStore.upsert_entity()` + `EntityStore.add_mention(entity_id, note_id, "note")`
4. Return list of extracted entities per note

**Limits**: Cap at 50 notes per request to avoid timeouts

### POST /polly/graph/garden/connection

Adds or removes a connection between two notes/entities.

**Body**:
```json
{
  "action": "add",  // or "remove"
  "source_id": "note1.md",
  "target_id": "note2.md",
  "relationship_type": "related_to",  // for "add" only
  "strength": 0.8  // for "add" only
}
```

**Response**:
```json
{
  "status": "created",  // or "removed"
  "relationship": {
    "source": "note1.md",
    "target": "note2.md",
    "type": "related_to",
    "strength": 0.8
  }
}
```

**Implementation**:
- **add**: Create `Relationship` object, call `EntityStore.upsert_relationship()`
- **remove**: Call `EntityStore.remove_relationship()` (soft delete: set strength to 0)

### POST /polly/graph/garden/merge

Merges entity mentions from source notes into a target note.

**Body**:
```json
{
  "source_ids": ["note1.md", "note2.md"],
  "target_id": "note-master.md",
  "append_content": false  // optional: append source content to target
}
```

**Response**:
```json
{
  "status": "merged",
  "merged_entities": 23,
  "target": "note-master.md"
}
```

**Implementation**:
1. For each source: call `EntityStore.move_mentions(source_id, target_id)`
2. Optionally append source content to target note file
3. Update backlinks across the graph (any note linking to source should now link to target)

### DELETE /polly/graph/garden/prune

Removes weak connections, stale entities, or specific items.

**Body**:
```json
{
  "type": "weak_connections",  // or "stale_entities" or "specific"
  "threshold": 0.2,  // for weak_connections
  "ids": []  // for specific
}
```

**Response**:
```json
{
  "status": "pruned",
  "pruned_count": 15,
  "type": "weak_connections"
}
```

**Implementation**:
- **weak_connections**: `EntityStore.prune_weak_relationships(threshold)`
- **stale_entities**: `EntityStore.prune_stale_entities()` (entities with 0 mentions)
- **specific**: Loop through `ids`, call `EntityStore.delete_entity(id)` for each

---

## Part 5: Garden UI Redesign

### Current State

`loadGardenView()` renders:
1. Isolated notes list (from `/polly/graph/list?connection_status=isolated`)
2. Graph data status + backfill button

### New Design

Garden content container with 6 sections (scrollable):

```
┌────────────────────────────────────────┐
│ Stats Dashboard                        │
│ ┌────────┬────────┬────────┬────────┐ │
│ │ 127    │ 543    │ 89     │ 77.2%  │ │
│ │ Notes  │ Conns  │ Entities │ Cov  │ │
│ └────────┴────────┴────────┴────────┘ │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░ Coverage bar      │
├────────────────────────────────────────┤
│ Suggested Connections           [12]   │
│ ┌────────────────────────────────────┐ │
│ │ ○ "docker-compose" mentioned in    │ │
│ │   "Docker Guide" but not linked    │ │
│ │   [Link] [Dismiss]                 │ │
│ └────────────────────────────────────┘ │
├────────────────────────────────────────┤
│ Merge Candidates                [3]    │
│ ┌────────────────────────────────────┐ │
│ │ ⬡ "AI Agents" + "LLM Agents"       │ │
│ │   Share 7 entities (73% overlap)   │ │
│ │   [Merge] [Dismiss]                │ │
│ └────────────────────────────────────┘ │
├────────────────────────────────────────┤
│ Isolated Notes              [Enrich All]│
│ (existing list, enhanced with actions) │
├────────────────────────────────────────┤
│ Enrichment Queue            [Enrich All]│
│ (unenriched notes from stats.unenriched)│
├────────────────────────────────────────┤
│ ▶ Prune Tools                          │
│   (collapsible, hidden by default)     │
└────────────────────────────────────────┘
```

### Section 1: Stats Dashboard

Render 4 stat cards + coverage bar:

```js
async function loadGardenStats() {
  const resp = await fetch('http://127.0.0.1:11436/polly/graph/garden/stats');
  const data = await resp.json();
  
  document.getElementById('garden-stats').innerHTML = `
    <div class="garden-stats-grid">
      <div class="garden-stat-card">
        <div class="garden-stat-value">${data.total_notes}</div>
        <div class="garden-stat-label">Notes</div>
      </div>
      <div class="garden-stat-card">
        <div class="garden-stat-value">${data.total_connections}</div>
        <div class="garden-stat-label">Connections</div>
      </div>
      <div class="garden-stat-card">
        <div class="garden-stat-value">${data.total_entities}</div>
        <div class="garden-stat-label">Entities</div>
      </div>
      <div class="garden-stat-card">
        <div class="garden-stat-value">${data.coverage_pct}%</div>
        <div class="garden-stat-label">Coverage</div>
      </div>
    </div>
    <div class="garden-coverage-bar">
      <div class="garden-coverage-fill" style="width: ${data.coverage_pct}%;"></div>
    </div>
  `;
}
```

### Section 2: Connection Suggestions

Render list of suggestions with accept/dismiss buttons:

```js
async function loadGardenSuggestions() {
  const resp = await fetch('http://127.0.0.1:11436/polly/graph/garden/suggestions?limit=20');
  const data = await resp.json();
  
  document.getElementById('suggestion-count').textContent = data.connection_suggestions.length;
  
  let html = '';
  data.connection_suggestions.forEach(sugg => {
    html += `
      <div class="garden-suggestion-item">
        <i data-lucide="link" style="width: 14px; height: 14px; opacity: 0.5;"></i>
        <div class="garden-suggestion-info">
          <div style="font-size: 11px; font-weight: 500;">${escapeHtml(sugg.source_name)} → ${escapeHtml(sugg.target_name)}</div>
          <div class="garden-suggestion-reason">${escapeHtml(sugg.reason)}</div>
        </div>
        <div class="garden-suggestion-actions">
          <button class="garden-btn-accept" onclick="acceptSuggestion('${sugg.source_id}', '${sugg.target_id}', 'references')">Link</button>
          <button class="garden-btn-dismiss" onclick="dismissSuggestion('${sugg.source_id}', '${sugg.target_id}')">Dismiss</button>
        </div>
      </div>
    `;
  });
  
  document.getElementById('garden-suggestions').innerHTML = html || '<p style="font-size: 11px; color: var(--text-secondary); padding: 8px;">No suggestions</p>';
}
```

**acceptSuggestion()**: Calls `POST /polly/graph/garden/connection` with `action: "add"`, refreshes graph, removes suggestion from list

**dismissSuggestion()**: Stores dismissal in localStorage (key: `dismissed-suggestions`), removes from list

### Section 3: Merge Candidates

Similar rendering:

```js
data.merge_candidates.forEach(merge => {
  html += `
    <div class="garden-suggestion-item">
      <i data-lucide="git-merge"></i>
      <div class="garden-suggestion-info">
        <div style="font-size: 11px; font-weight: 500;">${merge.notes.map(escapeHtml).join(' + ')}</div>
        <div class="garden-suggestion-reason">${escapeHtml(merge.reason)}</div>
      </div>
      <div class="garden-suggestion-actions">
        <button class="garden-btn-accept" onclick="showMergeDialog(${JSON.stringify(merge.notes)})">Merge</button>
        <button class="garden-btn-dismiss" onclick="dismissMerge(${JSON.stringify(merge.notes)})">Dismiss</button>
      </div>
    </div>
  `;
});
```

**showMergeDialog()**: Opens modal to choose target note, confirm merge, optionally append content

### Section 4: Enhanced Isolated Notes

Current implementation stays but add per-item action buttons:

```js
data.items.forEach(item => {
  html += `
    <div class="garden-isolated-item" data-item-id="${item.id}">
      <i data-lucide="${getTypeIcon(item.type)}"></i>
      <div class="garden-isolated-info">
        <div>${escapeHtml(item.name)}</div>
        <div style="font-size: 10px; color: var(--text-secondary);">${item.connection_count || 0} connections</div>
      </div>
      <div class="garden-item-actions">
        <button onclick="enrichNote('${item.id}')" title="Enrich"><i data-lucide="sparkles"></i></button>
        <button onclick="deleteNote('${item.id}')" title="Delete"><i data-lucide="trash-2"></i></button>
      </div>
    </div>
  `;
});
```

### Section 5: Enrichment Queue

List of unenriched notes from stats:

```js
async function loadGardenEnrichmentQueue() {
  const statsResp = await fetch('http://127.0.0.1:11436/polly/graph/garden/stats');
  const stats = await statsResp.json();
  
  let html = '';
  stats.unenriched_notes.forEach(noteId => {
    html += `
      <div class="garden-isolated-item" data-item-id="${noteId}">
        <i data-lucide="file-text"></i>
        <div class="garden-isolated-info">
          <div style="font-size: 11px;">${escapeHtml(noteId)}</div>
          <div style="font-size: 10px; color: var(--text-secondary);">Not enriched</div>
        </div>
        <button class="garden-btn-accept" onclick="enrichNote('${noteId}')">Enrich</button>
      </div>
    `;
  });
  
  document.getElementById('garden-enrichment-queue').innerHTML = html;
}
```

**"Enrich All" button**: Calls `POST /polly/graph/garden/enrich` with `note_ids: []` (empty = all unenriched), shows progress toast

### Section 6: Prune Tools

Expandable `<details>` section:

```html
<details class="garden-prune-details">
  <summary>
    <i data-lucide="scissors"></i> Prune Tools
    <i data-lucide="chevron-right" class="prune-chevron"></i>
  </summary>
  <div>
    <button onclick="pruneWeak()">Remove Weak Connections (< 0.2)</button>
    <button onclick="pruneStale()">Remove Stale Entities (0 mentions)</button>
  </div>
</details>
```

**pruneWeak()**: Calls `DELETE /polly/graph/garden/prune` with `type: "weak_connections"`, shows confirmation dialog first

**pruneStale()**: Calls same endpoint with `type: "stale_entities"`

---

## Part 6: Connection Management UI

### Details Panel Redesign

When a node is selected (tap event), switch lower panel to Details tab and populate:

```js
function renderGraphDetailsPanel(nodeData) {
  content.innerHTML = `
    <div style="padding: 12px;">
      <!-- Node header -->
      <div style="display: flex; gap: 8px; margin-bottom: 12px;">
        <div style="width: 10px; height: 10px; border-radius: 50%; background: ${domainColor};"></div>
        <div>
          <div style="font-weight: 600;">${nodeData.label}</div>
          <div style="font-size: 10px; opacity: 0.7;">${nodeData.type} · ${nodeData.domain} · Authority: ${nodeData.authority.toFixed(2)}</div>
        </div>
      </div>
      
      <!-- Actions -->
      <div style="display: flex; gap: 6px; flex-wrap: wrap;">
        <button onclick="openNote('${nodeData.id}')">Open</button>
        <button onclick="exploreFromNode('${nodeData.id}')">Explore</button>
        <button onclick="enrichNote('${nodeData.id}')">Enrich</button>
        <button onclick="startConnectionMode('${nodeData.id}')">Connect</button>
      </div>
      
      <!-- Connections list -->
      <div style="margin-top: 12px;">
        <h4>Connections (${nodeData.connectionCount})</h4>
        <div id="detail-connections-list">Loading...</div>
      </div>
      
      <!-- Entities list -->
      <div style="margin-top: 12px;">
        <h4>Extracted Entities</h4>
        <div id="detail-entities-list">Loading...</div>
      </div>
    </div>
  `;
  
  loadNodeConnections(nodeData.id);
  loadNodeEntities(nodeData.id);
}
```

**loadNodeConnections()**: Query graph edges for this node, render list with remove buttons

```js
async function loadNodeConnections(nodeId) {
  const edges = cytoscapeInstance.edges().filter(e => 
    e.data('source') === nodeId || e.data('target') === nodeId
  );
  
  let html = '';
  edges.forEach(edge => {
    const otherNodeId = edge.data('source') === nodeId ? edge.data('target') : edge.data('source');
    const otherNode = cytoscapeInstance.getElementById(otherNodeId);
    
    html += `
      <div class="detail-connection-item">
        <span class="detail-edge-indicator" style="background: ${getEdgeColor(edge.data('relationshipType'))};"></span>
        <span style="font-size: 11px;">${escapeHtml(otherNode.data('label'))}</span>
        <span style="font-size: 10px; opacity: 0.6; margin-left: 4px;">${edge.data('relationshipType')}</span>
        <button class="detail-remove-btn" onclick="removeConnection('${edge.data('source')}', '${edge.data('target')}')">
          <i data-lucide="x"></i>
        </button>
      </div>
    `;
  });
  
  document.getElementById('detail-connections-list').innerHTML = html;
}
```

### Drag-to-Link (Connection Mode)

**"Connect" button handler**:

```js
function startConnectionMode(sourceId) {
  connectionMode = { active: true, sourceId };
  
  // Visual feedback on source node
  const sourceNode = cytoscapeInstance.getElementById(sourceId);
  sourceNode.style('border-color', '#00ff88');
  sourceNode.style('border-width', 4);
  
  showToast('Click another node to create a connection (Esc to cancel)', 'info');
  
  // Add temporary click handler
  const connectHandler = (evt) => {
    const targetNode = evt.target;
    const targetId = targetNode.data('id');
    if (targetId === sourceId) return;
    
    showConnectionDialog(sourceId, targetId, targetNode.data('label'));
    endConnectionMode();
    cytoscapeInstance.off('tap', 'node', connectHandler);
  };
  
  cytoscapeInstance.on('tap', 'node', connectHandler);
  
  // Esc to cancel
  document.addEventListener('keydown', function escHandler(e) {
    if (e.key === 'Escape') {
      endConnectionMode();
      cytoscapeInstance.off('tap', 'node', connectHandler);
      document.removeEventListener('keydown', escHandler);
      showToast('Connection cancelled', 'info');
    }
  });
}
```

**showConnectionDialog()**: Modal with relationship type dropdown + strength slider

```js
function showConnectionDialog(sourceId, targetId, targetName) {
  const dialog = document.createElement('div');
  dialog.className = 'graph-connection-dialog';
  dialog.innerHTML = `
    <h3>Create Connection</h3>
    <p>Connect to: <strong>${targetName}</strong></p>
    <label>Relationship Type</label>
    <select id="conn-type-select">
      <option value="related_to">Related To</option>
      <option value="references">References</option>
      <option value="uses">Uses</option>
      <option value="implements">Implements</option>
      <option value="part_of">Part Of</option>
      <option value="extends">Extends</option>
      <option value="depends_on">Depends On</option>
      <option value="inspires">Inspires</option>
      <option value="teaches">Teaches</option>
      <option value="contradicts">Contradicts</option>
    </select>
    <label>Strength</label>
    <input type="range" id="conn-strength" min="0.1" max="1.0" step="0.1" value="0.8">
    <div>
      <button id="conn-cancel">Cancel</button>
      <button id="conn-create">Create</button>
    </div>
  `;
  
  // Modal overlay
  const overlay = document.createElement('div');
  overlay.className = 'graph-dialog-overlay';
  
  document.body.append(overlay, dialog);
  
  dialog.querySelector('#conn-create').addEventListener('click', async () => {
    const type = dialog.querySelector('#conn-type-select').value;
    const strength = parseFloat(dialog.querySelector('#conn-strength').value);
    
    await createConnection(sourceId, targetId, type, strength);
    
    dialog.remove();
    overlay.remove();
  });
  
  // Cancel handlers
  dialog.querySelector('#conn-cancel').addEventListener('click', () => {
    dialog.remove();
    overlay.remove();
  });
  overlay.addEventListener('click', () => {
    dialog.remove();
    overlay.remove();
  });
}
```

**createConnection()**: Calls backend, adds edge visually

```js
async function createConnection(sourceId, targetId, type, strength) {
  try {
    const resp = await fetch('http://127.0.0.1:11436/polly/graph/garden/connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add', source_id: sourceId, target_id: targetId, relationship_type: type, strength })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    
    showToast('Connection created', 'success');
    
    // Add edge to graph
    cytoscapeInstance.add({
      data: {
        id: `${sourceId}-${targetId}-${type}`,
        source: sourceId,
        target: targetId,
        weight: strength,
        relationshipType: type,
        isGhost: false
      }
    });
  } catch (err) {
    showToast('Failed to create connection: ' + err.message, 'error');
  }
}
```

### Right-Click Edge Menu

```js
cy.on('cxttap', 'edge', (evt) => {
  const edge = evt.target;
  const data = edge.data();
  
  const menu = document.createElement('div');
  menu.className = 'graph-context-menu';
  menu.style.cssText = `position: fixed; left: ${evt.originalEvent.clientX}px; top: ${evt.originalEvent.clientY}px;`;
  
  const typeLabel = {
    references: 'Reference',
    mention: 'Mention',
    shared_tag: 'Shared Tag',
    relates_to: 'Relates To',
    co_occurs_with: 'Co-occurs'
  }[data.relationshipType] || data.relationshipType;
  
  menu.innerHTML = `
    <div class="ctx-header">${typeLabel} · Strength: ${data.weight.toFixed(1)}</div>
    <button class="graph-ctx-item" data-action="remove">Remove Connection</button>
    <button class="graph-ctx-item" data-action="strengthen">Strengthen (+0.2)</button>
    <button class="graph-ctx-item" data-action="weaken">Weaken (-0.2)</button>
  `;
  
  document.body.appendChild(menu);
  
  menu.addEventListener('click', async (e) => {
    const action = e.target.dataset.action;
    if (!action) return;
    
    if (action === 'remove') {
      await removeConnection(data.source, data.target);
      edge.remove();
    } else if (action === 'strengthen') {
      const newStrength = Math.min(1.0, data.weight + 0.2);
      await updateConnectionStrength(data.source, data.target, data.relationshipType, newStrength);
      edge.data('weight', newStrength);
    } else if (action === 'weaken') {
      const newStrength = Math.max(0.1, data.weight - 0.2);
      await updateConnectionStrength(data.source, data.target, data.relationshipType, newStrength);
      edge.data('weight', newStrength);
    }
    
    menu.remove();
  });
  
  // Close on click outside
  setTimeout(() => {
    document.addEventListener('click', function closeMenu(e) {
      if (!menu.contains(e.target)) {
        menu.remove();
        document.removeEventListener('click', closeMenu);
      }
    });
  }, 0);
});
```

---

## CSS Requirements

New styles needed in `main.css`:

```css
/* Garden Stats */
.garden-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.garden-stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 10px;
  text-align: center;
}

.garden-stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.garden-stat-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.garden-coverage-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  margin-top: 8px;
}

.garden-coverage-fill {
  height: 100%;
  background: var(--accent-primary);
  transition: width 0.5s ease;
}

/* Garden Suggestions */
.garden-suggestion-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  margin-bottom: 6px;
  background: var(--bg-secondary);
}

.garden-suggestion-item:hover {
  background: var(--bg-tertiary);
}

.garden-btn-accept {
  padding: 3px 8px;
  font-size: 10px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.garden-btn-dismiss {
  padding: 3px 8px;
  font-size: 10px;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 4px;
  cursor: pointer;
}

/* Connection Dialog */
.graph-connection-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10000;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 20px;
  min-width: 300px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

.graph-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
}

/* Edge type toggles */
.edge-type-toggles label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  cursor: pointer;
}

.edge-type-toggles label:hover {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

/* Detail panel connections */
.detail-connection-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  font-size: 11px;
  border-radius: 4px;
}

.detail-connection-item:hover {
  background: var(--bg-tertiary);
}

.detail-connection-item:hover .detail-remove-btn {
  opacity: 1;
}

.detail-remove-btn {
  opacity: 0;
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-error);
  cursor: pointer;
  transition: opacity 0.15s;
}

.detail-edge-indicator {
  width: 16px;
  height: 2px;
  border-radius: 1px;
  flex-shrink: 0;
}

/* Graph context menu */
.graph-context-menu {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  padding: 4px;
  min-width: 160px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.graph-ctx-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 10px;
  border: none;
  background: none;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 12px;
  border-radius: 4px;
}

.graph-ctx-item:hover {
  background: var(--bg-tertiary);
}
```

---

## EntityStore Method Requirements

Several backend endpoints need EntityStore methods that may not exist yet. Check `core/entities/store.py` and add if missing:

1. **`get_mentions_for_source(source_id: str, source_type: str) -> List[EntityMention]`**
   - Query: `SELECT * FROM entity_mentions WHERE source_id = ? AND source_type = ?`
   - Used by: stats endpoint, enrichment queue

2. **`move_mentions(source_id: str, target_id: str) -> int`**
   - Update: `UPDATE entity_mentions SET source_id = ? WHERE source_id = ?`
   - Returns count of moved mentions
   - Used by: merge endpoint

3. **`prune_weak_relationships(threshold: float) -> int`**
   - Delete: `DELETE FROM relationships WHERE strength < ?`
   - Returns count of deleted relationships
   - Used by: prune endpoint

4. **`prune_stale_entities() -> int`**
   - Delete entities with zero mentions: `DELETE FROM entities WHERE id NOT IN (SELECT entity_id FROM entity_mentions)`
   - Returns count of deleted entities
   - Used by: prune endpoint

5. **`remove_relationship(source_id: str, target_id: str)`**
   - Soft delete: `UPDATE relationships SET strength = 0 WHERE source_id = ? AND target_id = ?`
   - Used by: connection endpoint (remove action)

6. **`get_stats() -> Dict`**
   - Returns: `{"entity_count": ..., "relationship_count": ..., "mention_count": ...}`
   - Used by: stats endpoint

---

## Testing Strategy

### Unit Testing

For backend endpoints:
- Mock EntityStore, NotesIndex, BacklinksIndex responses
- Test each endpoint with valid/invalid inputs
- Verify response schemas match design

For frontend functions:
- Mock fetch responses
- Test filter state updates
- Test Cytoscape interactions (add/remove edges)

### Integration Testing

1. **Layout Test**: Load graph with 50+ nodes, verify nodes are spread out (no overlapping labels at zoom=1.0 for authority>0.6)
2. **Edge Toggle Test**: Toggle off "shared_tag" edges, verify they disappear; toggle on, verify they reappear
3. **Filter Test**: Set domain filter to "signals", verify only signals nodes remain
4. **Garden Stats Test**: Verify stats dashboard shows accurate counts
5. **Connection Suggestion Test**: Accept a suggestion, verify connection appears in graph
6. **Merge Test**: Merge two notes, verify entity mentions move to target
7. **Enrich Test**: Enrich an unenriched note, verify entities extracted
8. **Prune Test**: Prune weak connections, verify count matches deleted relationships
9. **Connection Management Test**: Add connection via Details panel, verify edge appears; remove via right-click menu, verify edge disappears

### Manual Testing Checklist

- [ ] Graph opens with readable node layout (no tight cluster)
- [ ] Edge legend shows all 5 types correctly
- [ ] Toggling edge types hides/shows them
- [ ] Domain filter populates and filters correctly
- [ ] Authority slider filters nodes by threshold
- [ ] Ghost toggle hides/shows ghost nodes
- [ ] Stats dashboard shows accurate data
- [ ] Connection suggestions are actionable (link/dismiss)
- [ ] Merge candidates can be merged
- [ ] Isolated notes list shows correct items
- [ ] Enrichment queue shows unenriched notes
- [ ] Enriching a note extracts entities
- [ ] Prune tools remove weak/stale items
- [ ] Details panel populates on node select
- [ ] "Connect" button enters connection mode
- [ ] Connection dialog creates connections
- [ ] Right-click edge menu removes/modifies edges
- [ ] All actions persist (refresh page, state restored)

---

## Performance Considerations

### Frontend
- **Layout computation**: cose-bilkent is O(n²) but acceptable for <500 nodes. For larger graphs, use progressive disclosure ("Explore From Here" mode)
- **Edge toggle**: Style updates are instant (no layout re-run needed)
- **Filter debouncing**: 300ms debounce prevents excessive API calls during slider dragging

### Backend
- **Garden suggestions**: Limit to 20 items by default. Compute on-demand (not cached)
- **Enrichment**: Cap at 50 notes per request. Background task for larger batches
- **Merge**: Entity mention moves are bulk SQL updates (fast)
- **Prune**: Batch deletes (single query per type)

---

## Migration & Rollback

### Migration
- No database schema changes
- No breaking changes to existing APIs
- All changes are additive or refinements

### Rollback
- If cose-bilkent causes issues: revert to tuned `cose` params (just change layout name in config)
- If backend endpoints fail: frontend gracefully handles 500 errors (shows error state)
- If garden UI is buggy: hide Garden tab in sidebar config (one-line change)

---

## Documentation Updates

After implementation, update:

1. **openspec/specs/knowledge-graph/spec.md**
   - Add "Garden View" section describing maintenance tools
   - Add "Connection Management" section for UI interactions
   - Update "Visualization" section with layout details

2. **openspec/changes/knowledge-graph-navigation/design.md**
   - Reference this change as "Graph Refinement" follow-up
   - Note that Garden features are now implemented

3. **README.md** (if user-facing docs exist)
   - Add garden view usage guide
   - Add connection management guide

---

## Success Metrics

1. **Graph readability**: 0 overlapping labels for authority>0.6 nodes at default zoom
2. **User engagement**: Garden tab visited within first 5 minutes of graph usage
3. **Connection quality**: Average connection strength increases over time (users pruning weak, adding strong)
4. **Coverage improvement**: Graph coverage % increases after enrichment feature launch
5. **User feedback**: "Graph is now usable" sentiment in feedback

---

## Future Enhancements (Out of Scope)

- Drag-and-drop node repositioning (manual layout overrides)
- Custom layout algorithms (circular, hierarchical by domain)
- Connection confidence visualization (edge thickness = confidence × strength)
- Temporal graph view (connections over time)
- Export graph as image/JSON
- Community detection (auto-cluster related notes)
- Graph diff (visualize changes between two time points)

These can be follow-up changes once the core refinement is validated.
