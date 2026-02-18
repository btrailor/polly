# Knowledge Graph Refinement — Implementation Plan

## Status: Ready to Execute

---

## Part 1: Fix Graph Layout (Tight Clustering)

### Task 1: Switch to cose-bilkent + tune params

**File: `electron-app/src/renderer/index.html` line 19**
- Add `<script src="cytoscape-cose-bilkent.js"></script>` after the cytoscape.min.js script tag

**File: `electron-app/src/renderer/app.js` line 17837-17847 (`initGraphPage()`)**
- After the `typeof cytoscape` check, register the plugin:
```js
// Register cose-bilkent layout if available
if (typeof cytoscapeCoseBilkent !== 'undefined') {
  cytoscape.use(cytoscapeCoseBilkent);
}
```

**File: `electron-app/src/renderer/app.js` lines 18138-18156 (`getLayoutConfig()` cose case)**
- Replace the `cose` default layout config with `cose-bilkent`:
```js
case 'cose':
default:
  return {
    name: 'cose-bilkent',
    animate: 'end',
    animationDuration: 500,
    fit: true,
    padding: 80,
    nodeRepulsion: 6500,
    idealEdgeLength: 200,
    edgeElasticity: 0.45,
    nestingFactor: 0.1,
    gravity: 0.25,
    gravityRange: 3.8,
    numIter: 2500,
    tile: true,
    tilingPaddingVertical: 40,
    tilingPaddingHorizontal: 40,
    nodeDimensionsIncludeLabels: true
  };
```

### Task 2: Fix Reset Layout + increase node sizes

**File: `electron-app/src/renderer/app.js` lines 18401-18413 (Reset button handler)**
- Replace the ad-hoc cose config with `getLayoutConfig(graphState.layout || 'cose')`:
```js
document.getElementById('graph-reset')?.addEventListener('click', () => {
  if (cytoscapeInstance) {
    const layout = cytoscapeInstance.layout(getLayoutConfig(graphState.layout || 'cose'));
    layout.run();
  }
});
```

**File: `electron-app/src/renderer/app.js` lines 18177-18178 (node size)**
- Change node size from `12 + (authority * 24)` to `16 + (authority * 32)`:
```js
'width': ele => 16 + (ele.data('authority') * 32),
'height': ele => 16 + (ele.data('authority') * 32),
```

---

## Part 2: Edge Type Legend & Toggles

### Task 3: Add edge type legend + toggles in Filters panel

**File: `electron-app/src/renderer/app.js` lines 18876-18920 (`renderGraphFiltersPanel()`)**

After the Layout section, before Ghost Node Toggle, insert a new "Connection Types" section:

```js
<!-- Connection Types Legend + Toggles -->
<div class="filter-section" style="margin-bottom: 20px;">
  <label style="display: block; font-size: 12px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
    <i data-lucide="cable" style="width: 12px; height: 12px; margin-right: 4px;"></i>
    Connection Types
  </label>
  <div class="edge-type-toggles">
    <label class="edge-type-toggle" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
      <input type="checkbox" class="edge-type-cb" data-edge-type="references" checked>
      <span style="display: inline-block; width: 24px; height: 2px; background: #888888; border-radius: 1px;"></span>
      <span>References (backlinks)</span>
    </label>
    <label class="edge-type-toggle" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
      <input type="checkbox" class="edge-type-cb" data-edge-type="mention" checked>
      <span style="display: inline-block; width: 24px; height: 0; border-top: 2px dashed #45B7D1;"></span>
      <span>Mentions (unlinked)</span>
    </label>
    <label class="edge-type-toggle" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
      <input type="checkbox" class="edge-type-cb" data-edge-type="shared_tag" checked>
      <span style="display: inline-block; width: 24px; height: 0; border-top: 2px dotted #52B788;"></span>
      <span>Shared Tags</span>
    </label>
    <label class="edge-type-toggle" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
      <input type="checkbox" class="edge-type-cb" data-edge-type="relates_to" checked>
      <span style="display: inline-block; width: 24px; height: 0; border-top: 2px dashed #555555;"></span>
      <span>Relates To (entities)</span>
    </label>
    <label class="edge-type-toggle" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
      <input type="checkbox" class="edge-type-cb" data-edge-type="co_occurs_with" checked>
      <span style="display: inline-block; width: 24px; height: 0; border-top: 2px dotted #555555;"></span>
      <span>Co-occurs With</span>
    </label>
  </div>
</div>
```

**Add toggle handlers** (in the same function, after icons init):
```js
// Setup edge type toggle handlers
document.querySelectorAll('.edge-type-cb').forEach(cb => {
  // Restore state from graphState
  const edgeType = cb.dataset.edgeType;
  if (graphState.filters.edgeTypes && !graphState.filters.edgeTypes.includes(edgeType)) {
    cb.checked = false;
  }
  
  cb.addEventListener('change', () => {
    toggleEdgeType(cb.dataset.edgeType, cb.checked);
  });
});
```

**Add new `toggleEdgeType()` function** (after `applyGraphLayout()`):
```js
function toggleEdgeType(edgeType, visible) {
  if (!cytoscapeInstance) return;
  
  // Update graphState
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
  
  // Toggle visibility of matching edges
  cytoscapeInstance.edges().forEach(edge => {
    if (edge.data('relationshipType') === edgeType) {
      if (visible) {
        edge.style('display', 'element');
      } else {
        edge.style('display', 'none');
      }
    }
  });
  
  saveGraphState();
}
```

**Restore edge type visibility on graph init** — in `initGraphCanvas()` after `cytoscapeInstance.one('layoutstop', ...)`, add:
```js
// Restore edge type visibility from saved state
if (graphState.filters.edgeTypes) {
  const allTypes = ['references', 'mention', 'shared_tag', 'relates_to', 'co_occurs_with'];
  allTypes.forEach(type => {
    if (!graphState.filters.edgeTypes.includes(type)) {
      cytoscapeInstance.edges().forEach(edge => {
        if (edge.data('relationshipType') === type) {
          edge.style('display', 'none');
        }
      });
    }
  });
}
```

### Task 4: Fix ghost toggle

**File: `electron-app/src/renderer/app.js` lines 18937-18943**

Replace the TODO ghost toggle handler:
```js
const ghostToggle = document.getElementById('graph-show-ghosts');
if (ghostToggle) {
  // Restore saved state
  if (graphState.filters.showGhosts === false) {
    ghostToggle.checked = false;
  }
  
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
}
```

---

## Part 3: Implement Filtered Views

### Task 5: Enable domain filter + add type/authority filters

**File: `electron-app/src/renderer/app.js` `renderGraphFiltersPanel()`**

Replace the disabled domain filter with a functional one:
```js
<!-- Domain Filter -->
<div class="filter-section" style="margin-bottom: 20px;">
  <label style="display: block; font-size: 12px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
    <i data-lucide="folder" style="width: 12px; height: 12px; margin-right: 4px;"></i>
    Domain
  </label>
  <select id="graph-domain-filter" style="width: 100%; padding: 6px 8px; font-size: 12px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary);">
    <option value="">All Domains</option>
    ${Object.keys(graphDomainColors || {}).map(d => `<option value="${escapeHtml(d)}" ${graphState.filters.domain === d ? 'selected' : ''}>${escapeHtml(d)}</option>`).join('')}
  </select>
</div>

<!-- Content Type Filter -->
<div class="filter-section" style="margin-bottom: 20px;">
  <label style="display: block; font-size: 12px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
    <i data-lucide="shapes" style="width: 12px; height: 12px; margin-right: 4px;"></i>
    Content Types
  </label>
  <div class="content-type-toggles">
    ${['note', 'conversation', 'book', 'capture', 'code', 'canvas'].map(type => {
      const checked = !graphState.filters.types || graphState.filters.types.includes(type);
      const icons = { note: 'file-text', conversation: 'message-square', book: 'book-open', capture: 'camera', code: 'code', canvas: 'layout' };
      return `<label style="display: flex; align-items: center; gap: 6px; padding: 3px 0; font-size: 11px; color: var(--text-primary); cursor: pointer;">
        <input type="checkbox" class="content-type-cb" data-content-type="${type}" ${checked ? 'checked' : ''}>
        <i data-lucide="${icons[type]}" style="width: 12px; height: 12px; opacity: 0.6;"></i>
        <span>${type.charAt(0).toUpperCase() + type.slice(1)}s</span>
      </label>`;
    }).join('')}
  </div>
</div>

<!-- Authority Threshold -->
<div class="filter-section" style="margin-bottom: 20px;">
  <label style="display: block; font-size: 12px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
    <i data-lucide="award" style="width: 12px; height: 12px; margin-right: 4px;"></i>
    Min Authority: <span id="authority-value">${(graphState.filters.authority_min || 0).toFixed(1)}</span>
  </label>
  <input type="range" id="graph-authority-filter" min="0" max="1" step="0.1" value="${graphState.filters.authority_min || 0}" style="width: 100%; accent-color: var(--accent-primary);">
</div>
```

**Add handlers for these new filters:**
```js
// Domain filter
const domainSelect = document.getElementById('graph-domain-filter');
if (domainSelect) {
  domainSelect.addEventListener('change', (e) => {
    graphState.filters.domain = e.target.value || null;
    applyGraphFilters();
  });
}

// Content type filters
document.querySelectorAll('.content-type-cb').forEach(cb => {
  cb.addEventListener('change', () => {
    const types = [];
    document.querySelectorAll('.content-type-cb:checked').forEach(checked => {
      types.push(checked.dataset.contentType);
    });
    graphState.filters.types = types;
    applyGraphFilters();
  });
});

// Authority slider
const authoritySlider = document.getElementById('graph-authority-filter');
if (authoritySlider) {
  authoritySlider.addEventListener('input', (e) => {
    document.getElementById('authority-value').textContent = parseFloat(e.target.value).toFixed(1);
  });
  let authorityDebounce;
  authoritySlider.addEventListener('change', (e) => {
    clearTimeout(authorityDebounce);
    authorityDebounce = setTimeout(() => {
      graphState.filters.authority_min = parseFloat(e.target.value) || null;
      applyGraphFilters();
    }, 300);
  });
}
```

### Task 6: Wire all filters with `applyGraphFilters()`

**New function in app.js** (after `applyGraphLayout()`):
```js
let filterDebounce = null;

async function applyGraphFilters() {
  clearTimeout(filterDebounce);
  filterDebounce = setTimeout(async () => {
    // Save current viewport state before re-fetching
    if (cytoscapeInstance) {
      graphState.position = cytoscapeInstance.pan();
      graphState.zoom = cytoscapeInstance.zoom();
    }
    
    saveGraphState();
    
    // Re-initialize graph with new filters (initGraphCanvas reads from graphState.filters)
    await initGraphCanvas();
  }, 300);
}
```

---

## Part 4: Backend Garden Endpoints

### Task 7: `/polly/graph/garden/stats`

**File: `interfaces/server.py`** — Add new endpoint near existing graph endpoints (~line 4200):

```python
@app.get("/polly/graph/garden/stats")
async def get_garden_stats():
    """Get maintenance statistics for the garden view."""
    try:
        notes_index = polly.notes_index
        backlinks_index = polly.backlinks_index
        entity_store = polly.entity_store
        
        all_notes = notes_index.get_all_notes() if notes_index else []
        total_notes = len(all_notes)
        
        # Count connections
        total_connections = 0
        isolated_count = 0
        connection_counts = []
        
        if backlinks_index:
            for note in all_notes:
                backlinks = backlinks_index.get_backlinks(note.name) or []
                count = len(backlinks)
                connection_counts.append(count)
                total_connections += count
                if count <= 2:
                    isolated_count += 1
        
        # Entity stats
        total_entities = 0
        if entity_store:
            try:
                stats = entity_store.get_stats()
                total_entities = stats.get('entity_count', 0)
            except:
                pass
        
        # Enrichment tracking
        enriched_count = 0
        unenriched = []
        if entity_store:
            for note in all_notes:
                mentions = entity_store.get_mentions_for_source(note.name, "note") if hasattr(entity_store, 'get_mentions_for_source') else []
                if mentions:
                    enriched_count += 1
                else:
                    unenriched.append(note.name)
        
        # Domain distribution
        domain_counts = {}
        for note in all_notes:
            domain = note.domain or 'Uncategorized'
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        avg_connections = sum(connection_counts) / len(connection_counts) if connection_counts else 0
        
        return {
            "total_notes": total_notes,
            "total_connections": total_connections,
            "total_entities": total_entities,
            "isolated_count": isolated_count,
            "enriched_count": enriched_count,
            "unenriched_count": len(unenriched),
            "coverage_pct": round((enriched_count / total_notes * 100) if total_notes > 0 else 0, 1),
            "avg_connections": round(avg_connections, 1),
            "domain_counts": domain_counts,
            "unenriched_notes": unenriched[:20]  # First 20 for UI
        }
    except Exception as e:
        logger.error(f"Failed to get garden stats: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
```

### Task 8: `/polly/graph/garden/suggestions`

```python
@app.get("/polly/graph/garden/suggestions")
async def get_garden_suggestions(limit: int = 20):
    """Get connection suggestions and merge candidates."""
    try:
        notes_index = polly.notes_index
        backlinks_index = polly.backlinks_index
        unlinked_mentions_index = polly.unlinked_mentions_index
        entity_store = polly.entity_store
        
        suggestions = {
            "connection_suggestions": [],
            "merge_candidates": [],
            "enrichment_candidates": []
        }
        
        all_notes = notes_index.get_all_notes() if notes_index else []
        
        # Connection suggestions: notes with unlinked mentions
        if unlinked_mentions_index:
            for note in all_notes[:limit * 2]:  # Check more than limit
                mentions = unlinked_mentions_index.get_mentions_in(note.name) if hasattr(unlinked_mentions_index, 'get_mentions_in') else []
                for mention in mentions:
                    if len(suggestions["connection_suggestions"]) >= limit:
                        break
                    # Check if already linked via backlinks
                    existing_backlinks = backlinks_index.get_backlinks(mention.get('target', '')) if backlinks_index else []
                    already_linked = any(bl.get('source') == note.name for bl in existing_backlinks) if existing_backlinks else False
                    if not already_linked:
                        suggestions["connection_suggestions"].append({
                            "source_id": note.name,
                            "source_name": note.title or note.name,
                            "target_id": mention.get('target', ''),
                            "target_name": mention.get('target', ''),
                            "reason": f"'{mention.get('target', '')}' is mentioned in '{note.title or note.name}' but not linked",
                            "type": "unlinked_mention",
                            "confidence": 0.8
                        })
        
        # Merge candidates: notes with very similar names or overlapping entities
        if entity_store:
            note_entities = {}
            for note in all_notes:
                try:
                    mentions = entity_store.get_mentions_for_source(note.name, "note") if hasattr(entity_store, 'get_mentions_for_source') else []
                    if mentions:
                        note_entities[note.name] = set(m.entity_id if hasattr(m, 'entity_id') else m.get('entity_id', '') for m in mentions)
                except:
                    pass
            
            # Find pairs with high entity overlap
            note_names = list(note_entities.keys())
            for i in range(len(note_names)):
                if len(suggestions["merge_candidates"]) >= limit:
                    break
                for j in range(i + 1, len(note_names)):
                    entities_a = note_entities[note_names[i]]
                    entities_b = note_entities[note_names[j]]
                    if entities_a and entities_b:
                        overlap = entities_a & entities_b
                        union = entities_a | entities_b
                        if len(overlap) >= 3 and len(overlap) / len(union) > 0.5:
                            suggestions["merge_candidates"].append({
                                "notes": [note_names[i], note_names[j]],
                                "shared_entity_count": len(overlap),
                                "overlap_ratio": round(len(overlap) / len(union), 2),
                                "reason": f"Share {len(overlap)} entities with {round(len(overlap) / len(union) * 100)}% overlap"
                            })
        
        # Enrichment candidates: notes with no or stale entity extraction
        for note in all_notes:
            if len(suggestions["enrichment_candidates"]) >= limit:
                break
            has_entities = note.name in (note_entities if 'note_entities' in dir() else {})
            if not has_entities:
                suggestions["enrichment_candidates"].append({
                    "note_id": note.name,
                    "note_name": note.title or note.name,
                    "reason": "No entities extracted yet",
                    "domain": note.domain
                })
        
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get garden suggestions: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
```

### Task 9: `/polly/graph/garden/enrich`

```python
@app.post("/polly/graph/garden/enrich")
async def enrich_notes(body: dict):
    """Trigger entity extraction on specified notes."""
    try:
        note_ids = body.get("note_ids", [])
        entity_extractor = polly.entity_extractor
        entity_store = polly.entity_store
        notes_index = polly.notes_index
        
        if not entity_extractor or not notes_index:
            return JSONResponse(status_code=500, content={"error": "Entity extractor not available"})
        
        # If no specific notes, enrich all
        if not note_ids:
            all_notes = notes_index.get_all_notes()
            note_ids = [n.name for n in all_notes]
        
        results = []
        for note_id in note_ids[:50]:  # Cap at 50 to avoid timeouts
            try:
                note_info = notes_index.get_note(note_id)
                if not note_info:
                    continue
                
                # Read note content
                content = ""
                if hasattr(note_info, 'path') and note_info.path:
                    import os
                    if os.path.exists(note_info.path):
                        with open(note_info.path, 'r') as f:
                            content = f.read()
                
                if not content:
                    continue
                
                # Extract entities
                entities = entity_extractor.extract(content)
                
                # Store entities
                stored_entities = []
                for entity in entities:
                    try:
                        entity_store.upsert_entity(entity)
                        entity_store.add_mention(entity.id, note_id, "note")
                        stored_entities.append({
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                            "description": entity.description or ""
                        })
                    except Exception as store_err:
                        logger.warning(f"Failed to store entity {entity.name}: {store_err}")
                
                results.append({
                    "note_id": note_id,
                    "note_name": note_info.title or note_info.name,
                    "entities_extracted": len(stored_entities),
                    "entities": stored_entities
                })
            except Exception as note_err:
                logger.warning(f"Failed to enrich note {note_id}: {note_err}")
                results.append({
                    "note_id": note_id,
                    "error": str(note_err)
                })
        
        return {
            "enriched_count": len([r for r in results if 'error' not in r]),
            "total_entities": sum(r.get('entities_extracted', 0) for r in results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to enrich notes: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
```

### Task 10: `/polly/graph/garden/connection`

```python
@app.post("/polly/graph/garden/connection")
async def manage_connection(body: dict):
    """Add or remove a connection between notes."""
    try:
        action = body.get("action")  # "add" or "remove"
        source_id = body.get("source_id")
        target_id = body.get("target_id")
        relationship_type = body.get("relationship_type", "related_to")
        strength = body.get("strength", 0.8)
        
        if not action or not source_id or not target_id:
            return JSONResponse(status_code=400, content={"error": "action, source_id, and target_id required"})
        
        entity_store = polly.entity_store
        if not entity_store:
            return JSONResponse(status_code=500, content={"error": "Entity store not available"})
        
        from core.entities.models import Relationship, RelationshipType
        
        if action == "add":
            rel_type = RelationshipType(relationship_type) if relationship_type in [rt.value for rt in RelationshipType] else RelationshipType.RELATED_TO
            relationship = Relationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=rel_type,
                strength=strength,
                context=f"Manually created via garden",
                bidirectional=True,
                mention_count=1
            )
            entity_store.upsert_relationship(relationship)
            return {"status": "created", "relationship": {"source": source_id, "target": target_id, "type": relationship_type, "strength": strength}}
        
        elif action == "remove":
            # Soft delete: set strength to 0
            entity_store.remove_relationship(source_id, target_id)
            return {"status": "removed", "source": source_id, "target": target_id}
        
        else:
            return JSONResponse(status_code=400, content={"error": f"Unknown action: {action}"})
    
    except Exception as e:
        logger.error(f"Failed to manage connection: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
```

### Task 11: Merge + Prune endpoints

```python
@app.post("/polly/graph/garden/merge")
async def merge_notes(body: dict):
    """Merge entity mentions from source notes into target."""
    try:
        source_ids = body.get("source_ids", [])
        target_id = body.get("target_id")
        append_content = body.get("append_content", False)
        
        if not source_ids or not target_id:
            return JSONResponse(status_code=400, content={"error": "source_ids and target_id required"})
        
        entity_store = polly.entity_store
        notes_index = polly.notes_index
        
        merged_entities = 0
        for source_id in source_ids:
            if source_id == target_id:
                continue
            # Move entity mentions from source to target
            if entity_store and hasattr(entity_store, 'move_mentions'):
                count = entity_store.move_mentions(source_id, target_id)
                merged_entities += count
            
            # Optionally append source content to target
            if append_content and notes_index:
                source_note = notes_index.get_note(source_id)
                target_note = notes_index.get_note(target_id)
                if source_note and target_note and hasattr(source_note, 'path') and hasattr(target_note, 'path'):
                    import os
                    if os.path.exists(source_note.path) and os.path.exists(target_note.path):
                        with open(source_note.path, 'r') as f:
                            source_content = f.read()
                        with open(target_note.path, 'a') as f:
                            f.write(f"\n\n---\n\n## Merged from {source_id}\n\n{source_content}")
        
        return {"status": "merged", "merged_entities": merged_entities, "target": target_id}
    except Exception as e:
        logger.error(f"Failed to merge notes: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/polly/graph/garden/prune")
async def prune_knowledge(body: dict):
    """Prune weak connections and stale entities."""
    try:
        prune_type = body.get("type")  # "weak_connections", "stale_entities", "specific"
        ids = body.get("ids", [])
        threshold = body.get("threshold", 0.2)
        
        entity_store = polly.entity_store
        if not entity_store:
            return JSONResponse(status_code=500, content={"error": "Entity store not available"})
        
        pruned_count = 0
        
        if prune_type == "weak_connections":
            # Remove relationships below strength threshold
            pruned_count = entity_store.prune_weak_relationships(threshold) if hasattr(entity_store, 'prune_weak_relationships') else 0
        elif prune_type == "stale_entities":
            # Remove entities with 0 mentions
            pruned_count = entity_store.prune_stale_entities() if hasattr(entity_store, 'prune_stale_entities') else 0
        elif prune_type == "specific":
            for item_id in ids:
                try:
                    entity_store.delete_entity(item_id)
                    pruned_count += 1
                except:
                    pass
        
        return {"status": "pruned", "pruned_count": pruned_count, "type": prune_type}
    except Exception as e:
        logger.error(f"Failed to prune: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
```

---

## Part 5: Garden View UI (Complete Redesign)

### Task 12-17: Redesign `loadGardenView()` and `renderGraphSidebar()`

**File: `electron-app/src/renderer/app.js`**

The Garden tab content in `renderGraphSidebar()` (currently simple HTML) needs to be redesigned as a scrollable container with multiple sections. Replace the current garden HTML structure with:

```js
// In renderGraphSidebar(), the garden panel content becomes:
<div id="garden-content" class="garden-view-content" style="overflow-y: auto; height: 100%; padding: 0;">
  <!-- Stats Dashboard -->
  <div id="garden-stats" class="garden-section" style="padding: 12px;">
    <div class="garden-stats-grid">
      <!-- Populated by loadGardenStats() -->
      <div class="garden-stat-loading" style="text-align: center; padding: 16px; color: var(--text-secondary); font-size: 11px;">
        Loading stats...
      </div>
    </div>
  </div>
  
  <!-- Connection Suggestions -->
  <div class="garden-section" style="padding: 0 12px 12px;">
    <div class="garden-section-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0;">
      <h4 style="font-size: 12px; font-weight: 600; color: var(--text-primary); margin: 0;">
        <i data-lucide="link" style="width: 12px; height: 12px; margin-right: 4px;"></i>
        Suggested Connections
      </h4>
      <span id="suggestion-count" class="garden-badge" style="font-size: 10px; background: var(--bg-tertiary); padding: 2px 6px; border-radius: 8px; color: var(--text-secondary);">0</span>
    </div>
    <div id="garden-suggestions" style="max-height: 200px; overflow-y: auto;">
      <!-- Populated by loadGardenSuggestions() -->
    </div>
  </div>
  
  <!-- Merge Candidates -->
  <div class="garden-section" style="padding: 0 12px 12px;">
    <div class="garden-section-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0;">
      <h4 style="font-size: 12px; font-weight: 600; color: var(--text-primary); margin: 0;">
        <i data-lucide="git-merge" style="width: 12px; height: 12px; margin-right: 4px;"></i>
        Merge Candidates
      </h4>
      <span id="merge-count" class="garden-badge" style="font-size: 10px; background: var(--bg-tertiary); padding: 2px 6px; border-radius: 8px; color: var(--text-secondary);">0</span>
    </div>
    <div id="garden-merges" style="max-height: 200px; overflow-y: auto;">
      <!-- Populated by loadGardenSuggestions() -->
    </div>
  </div>
  
  <!-- Isolated Notes (enhanced) -->
  <div class="garden-section" style="padding: 0 12px 12px;">
    <div class="garden-section-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0;">
      <h4 style="font-size: 12px; font-weight: 600; color: var(--text-primary); margin: 0;">
        <i data-lucide="unplug" style="width: 12px; height: 12px; margin-right: 4px;"></i>
        Isolated Notes
      </h4>
      <button id="garden-enrich-all-isolated" class="garden-action-btn" style="font-size: 10px; padding: 2px 8px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-secondary); cursor: pointer;">
        Enrich All
      </button>
    </div>
    <div id="garden-isolated-notes" style="max-height: 250px; overflow-y: auto;">
      <!-- Populated by loadGardenIsolatedNotes() -->
    </div>
  </div>
  
  <!-- Enrichment Queue -->
  <div class="garden-section" style="padding: 0 12px 12px;">
    <div class="garden-section-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0;">
      <h4 style="font-size: 12px; font-weight: 600; color: var(--text-primary); margin: 0;">
        <i data-lucide="sparkles" style="width: 12px; height: 12px; margin-right: 4px;"></i>
        Enrichment Queue
      </h4>
      <button id="garden-enrich-all" class="garden-action-btn" style="font-size: 10px; padding: 2px 8px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-secondary); cursor: pointer;">
        Enrich All
      </button>
    </div>
    <div id="garden-enrichment-queue" style="max-height: 200px; overflow-y: auto;">
      <!-- Populated by loadGardenEnrichmentQueue() -->
    </div>
  </div>
  
  <!-- Prune Tools (collapsible) -->
  <div class="garden-section" style="padding: 0 12px 12px;">
    <details class="garden-prune-details">
      <summary style="font-size: 12px; font-weight: 600; color: var(--text-primary); cursor: pointer; padding: 8px 0; list-style: none; display: flex; align-items: center; gap: 4px;">
        <i data-lucide="scissors" style="width: 12px; height: 12px;"></i>
        Prune Tools
        <i data-lucide="chevron-right" class="prune-chevron" style="width: 12px; height: 12px; margin-left: auto; transition: transform 0.2s;"></i>
      </summary>
      <div style="padding: 8px 0;">
        <button id="garden-prune-weak" class="garden-action-btn-full" style="display: block; width: 100%; text-align: left; padding: 8px 10px; margin-bottom: 6px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 11px;">
          <strong>Remove Weak Connections</strong>
          <br><span style="font-size: 10px; color: var(--text-secondary);">Prune relationships with strength &lt; 0.2</span>
        </button>
        <button id="garden-prune-stale" class="garden-action-btn-full" style="display: block; width: 100%; text-align: left; padding: 8px 10px; margin-bottom: 6px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 11px;">
          <strong>Remove Stale Entities</strong>
          <br><span style="font-size: 10px; color: var(--text-secondary);">Delete entities with no active mentions</span>
        </button>
      </div>
    </details>
  </div>
  
  <!-- Graph Data Status (backfill) -->
  <div class="garden-section" style="padding: 0 12px 16px;">
    <div id="graph-data-status" style="margin-bottom: 8px;"></div>
    <button id="graph-backfill-btn" style="display: none; width: 100%; padding: 8px; font-size: 12px; background: var(--accent-primary); color: white; border: none; border-radius: 6px; cursor: pointer;">
      Populate Graph from Notes
    </button>
  </div>
</div>
```

**New functions to implement:**

1. `loadGardenStats()` — Calls `GET /polly/graph/garden/stats`, renders stat cards
2. `loadGardenSuggestions()` — Calls `GET /polly/graph/garden/suggestions`, renders connection suggestions + merge candidates
3. `loadGardenIsolatedNotes()` — Enhanced version of current `loadGardenView()` with per-item action buttons
4. `loadGardenEnrichmentQueue()` — Shows unenriched notes with enrich buttons
5. `enrichNote(noteId)` — Calls `POST /polly/graph/garden/enrich`, shows results inline
6. `createConnection(sourceId, targetId, type)` — Calls `POST /polly/graph/garden/connection`
7. `mergeNotes(sourceIds, targetId)` — Calls `POST /polly/graph/garden/merge`
8. `pruneKnowledge(type, threshold)` — Calls `DELETE /polly/graph/garden/prune`

---

## Part 6: Node Details Panel & Connection Management

### Task 18: Populate Details panel on node select

**File: `electron-app/src/renderer/app.js` — Rewrite `renderGraphDetailsPanel()`**

When a node is selected via tap event, switch the lower panel to the Details tab and populate it:

```js
function renderGraphDetailsPanel(nodeData) {
  const content = document.querySelector('.lower-panel[data-view="graph"] .lower-panel-content');
  if (!content) return;
  
  if (!nodeData) {
    content.innerHTML = `
      <div class="lower-panel-empty">
        <i data-lucide="info" style="width: 20px; height: 20px; opacity: 0.3; margin-bottom: 8px;"></i>
        <p style="font-size: 12px; color: var(--text-secondary);">Select a node to see details</p>
      </div>
    `;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    return;
  }
  
  const domainColor = graphDomainColors[nodeData.domain] || '#666';
  
  content.innerHTML = `
    <div style="padding: 12px;">
      <!-- Header -->
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        <div style="width: 10px; height: 10px; border-radius: 50%; background: ${domainColor};"></div>
        <div>
          <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">${escapeHtml(nodeData.label)}</div>
          <div style="font-size: 10px; color: var(--text-secondary);">${escapeHtml(nodeData.type)} · ${escapeHtml(nodeData.domain || 'No domain')} · Authority: ${(nodeData.authority || 0).toFixed(2)}</div>
        </div>
      </div>
      
      <!-- Actions -->
      <div style="display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;">
        <button onclick="if(window.notesManager) { window.notesManager.openNote('${escapeHtml(nodeData.id)}'); showView('notes'); }" style="font-size: 10px; padding: 4px 8px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary); cursor: pointer;">
          <i data-lucide="external-link" style="width: 10px; height: 10px;"></i> Open
        </button>
        <button onclick="exploreFromNode('${escapeHtml(nodeData.id)}')" style="font-size: 10px; padding: 4px 8px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary); cursor: pointer;">
          <i data-lucide="expand" style="width: 10px; height: 10px;"></i> Explore
        </button>
        <button onclick="enrichNote('${escapeHtml(nodeData.id)}')" style="font-size: 10px; padding: 4px 8px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary); cursor: pointer;">
          <i data-lucide="sparkles" style="width: 10px; height: 10px;"></i> Enrich
        </button>
        <button id="detail-add-connection-btn" style="font-size: 10px; padding: 4px 8px; background: var(--accent-primary); border: none; border-radius: 4px; color: white; cursor: pointer;">
          <i data-lucide="plus" style="width: 10px; height: 10px;"></i> Connect
        </button>
      </div>
      
      <!-- Connections -->
      <div style="margin-bottom: 12px;">
        <h4 style="font-size: 11px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">
          Connections (${nodeData.connectionCount || 0})
        </h4>
        <div id="detail-connections-list" style="max-height: 200px; overflow-y: auto;">
          <!-- Populated by loadNodeConnections() -->
          <div style="font-size: 11px; color: var(--text-secondary); padding: 4px 0;">Loading...</div>
        </div>
      </div>
      
      <!-- Entities -->
      <div>
        <h4 style="font-size: 11px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">
          Extracted Entities
        </h4>
        <div id="detail-entities-list" style="max-height: 150px; overflow-y: auto;">
          <div style="font-size: 11px; color: var(--text-secondary); padding: 4px 0;">Loading...</div>
        </div>
      </div>
    </div>
  `;
  
  if (typeof lucide !== 'undefined') lucide.createIcons();
  
  // Load connections and entities asynchronously
  loadNodeConnections(nodeData.id);
  loadNodeEntities(nodeData.id);
  
  // Setup "Connect" button
  document.getElementById('detail-add-connection-btn')?.addEventListener('click', () => {
    startConnectionMode(nodeData.id);
  });
}
```

Wire into existing node tap handler at `setupGraphEventHandlers()`:
```js
cy.on('tap', 'node', (evt) => {
  // ... existing code ...
  
  // Update details panel (don't navigate away immediately - show details)
  // The node click currently navigates to the note - we should also populate details
  const detailsTab = document.querySelector('.lower-panel-tab[data-tab="details"]');
  if (detailsTab) {
    // Expand lower panel if collapsed and switch to details tab
    const panel = detailsTab.closest('.lower-panel');
    if (panel && panel.dataset.collapsed === 'true') {
      panel.dataset.collapsed = 'false';
    }
    detailsTab.click();
  }
  renderGraphDetailsPanel(data);
});
```

### Task 19: Drag-to-link

Add a connection mode to the graph:

```js
let connectionMode = { active: false, sourceId: null };

function startConnectionMode(sourceId) {
  connectionMode = { active: true, sourceId };
  
  // Visual feedback
  if (cytoscapeInstance) {
    const sourceNode = cytoscapeInstance.getElementById(sourceId);
    if (sourceNode.length > 0) {
      sourceNode.style('border-color', '#00ff88');
      sourceNode.style('border-width', 4);
    }
  }
  
  // Show instruction toast
  showToast('Click another node to create a connection, or press Esc to cancel', 'info');
  
  // Add temporary click handler for target selection
  const connectHandler = (evt) => {
    const targetNode = evt.target;
    const targetId = targetNode.data('id');
    
    if (targetId === sourceId) return; // Can't connect to self
    
    // Show connection type dialog
    showConnectionDialog(sourceId, targetId, targetNode.data('label'));
    
    // Clean up
    endConnectionMode();
    cytoscapeInstance.off('tap', 'node', connectHandler);
  };
  
  cytoscapeInstance.on('tap', 'node', connectHandler);
  
  // Esc to cancel
  const escHandler = (e) => {
    if (e.key === 'Escape') {
      endConnectionMode();
      cytoscapeInstance.off('tap', 'node', connectHandler);
      document.removeEventListener('keydown', escHandler);
      showToast('Connection cancelled', 'info');
    }
  };
  document.addEventListener('keydown', escHandler);
}

function endConnectionMode() {
  if (connectionMode.sourceId && cytoscapeInstance) {
    const sourceNode = cytoscapeInstance.getElementById(connectionMode.sourceId);
    if (sourceNode.length > 0) {
      sourceNode.style('border-color', '#ffffff');
      sourceNode.style('border-width', 2);
      sourceNode.style('border-opacity', 0.3);
    }
  }
  connectionMode = { active: false, sourceId: null };
}

function showConnectionDialog(sourceId, targetId, targetName) {
  // Simple modal/dialog for choosing relationship type
  const dialog = document.createElement('div');
  dialog.className = 'graph-connection-dialog';
  dialog.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10000; background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: 8px; padding: 20px; min-width: 300px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);';
  dialog.innerHTML = `
    <h3 style="margin: 0 0 12px; font-size: 14px; color: var(--text-primary);">Create Connection</h3>
    <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">Connect to: <strong>${escapeHtml(targetName)}</strong></p>
    <label style="font-size: 11px; color: var(--text-primary); display: block; margin-bottom: 4px;">Relationship Type</label>
    <select id="conn-type-select" style="width: 100%; padding: 6px; margin-bottom: 12px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
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
    <label style="font-size: 11px; color: var(--text-primary); display: block; margin-bottom: 4px;">Strength</label>
    <input type="range" id="conn-strength" min="0.1" max="1.0" step="0.1" value="0.8" style="width: 100%; margin-bottom: 12px;">
    <div style="display: flex; gap: 8px; justify-content: flex-end;">
      <button id="conn-cancel" style="padding: 6px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-primary); border-radius: 4px; color: var(--text-primary); cursor: pointer; font-size: 12px;">Cancel</button>
      <button id="conn-create" style="padding: 6px 12px; background: var(--accent-primary); border: none; border-radius: 4px; color: white; cursor: pointer; font-size: 12px;">Create</button>
    </div>
  `;
  
  // Overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999;';
  
  document.body.appendChild(overlay);
  document.body.appendChild(dialog);
  
  dialog.querySelector('#conn-cancel').addEventListener('click', () => {
    dialog.remove();
    overlay.remove();
  });
  
  overlay.addEventListener('click', () => {
    dialog.remove();
    overlay.remove();
  });
  
  dialog.querySelector('#conn-create').addEventListener('click', async () => {
    const type = dialog.querySelector('#conn-type-select').value;
    const strength = parseFloat(dialog.querySelector('#conn-strength').value);
    
    try {
      const resp = await fetch('http://127.0.0.1:11436/polly/graph/garden/connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'add', source_id: sourceId, target_id: targetId, relationship_type: type, strength })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      
      showToast('Connection created', 'success');
      
      // Add edge to graph visually
      if (cytoscapeInstance) {
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
      }
    } catch (err) {
      showToast('Failed to create connection: ' + err.message, 'error');
    }
    
    dialog.remove();
    overlay.remove();
  });
}
```

### Task 20: Right-click edge context menu

In `setupGraphEventHandlers()`, add:
```js
cy.on('cxttap', 'edge', (evt) => {
  const edge = evt.target;
  const data = edge.data();
  
  const menu = document.createElement('div');
  menu.className = 'graph-context-menu';
  menu.style.cssText = `position: fixed; left: ${evt.originalEvent.clientX}px; top: ${evt.originalEvent.clientY}px; z-index: 10000; background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: 6px; padding: 4px; min-width: 160px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);`;
  
  const typeLabel = {
    references: 'Reference (backlink)',
    mention: 'Mention (unlinked)',
    shared_tag: 'Shared Tag',
    relates_to: 'Relates To',
    co_occurs_with: 'Co-occurs With'
  }[data.relationshipType] || data.relationshipType;
  
  menu.innerHTML = `
    <div style="padding: 6px 10px; font-size: 11px; color: var(--text-secondary); border-bottom: 1px solid var(--border-primary);">
      ${escapeHtml(typeLabel)} · Strength: ${(data.weight || 0).toFixed(1)}
    </div>
    <button class="graph-ctx-item" data-action="remove-edge" style="display: block; width: 100%; text-align: left; padding: 8px 10px; border: none; background: none; color: var(--text-primary); cursor: pointer; font-size: 12px; border-radius: 4px;">
      <i data-lucide="trash-2" style="width: 12px; height: 12px; margin-right: 6px;"></i>
      Remove Connection
    </button>
    <button class="graph-ctx-item" data-action="strengthen" style="display: block; width: 100%; text-align: left; padding: 8px 10px; border: none; background: none; color: var(--text-primary); cursor: pointer; font-size: 12px; border-radius: 4px;">
      <i data-lucide="trending-up" style="width: 12px; height: 12px; margin-right: 6px;"></i>
      Strengthen
    </button>
    <button class="graph-ctx-item" data-action="weaken" style="display: block; width: 100%; text-align: left; padding: 8px 10px; border: none; background: none; color: var(--text-primary); cursor: pointer; font-size: 12px; border-radius: 4px;">
      <i data-lucide="trending-down" style="width: 12px; height: 12px; margin-right: 6px;"></i>
      Weaken
    </button>
  `;
  
  document.body.appendChild(menu);
  if (typeof lucide !== 'undefined') lucide.createIcons();
  
  // Handle actions
  menu.addEventListener('click', async (e) => {
    const action = e.target.closest('[data-action]')?.dataset.action;
    if (!action) return;
    
    if (action === 'remove-edge') {
      try {
        await fetch('http://127.0.0.1:11436/polly/graph/garden/connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'remove', source_id: data.source, target_id: data.target })
        });
        edge.remove();
        showToast('Connection removed', 'success');
      } catch (err) {
        showToast('Failed to remove connection', 'error');
      }
    } else if (action === 'strengthen') {
      const newStrength = Math.min(1.0, (data.weight || 0.5) + 0.2);
      try {
        await fetch('http://127.0.0.1:11436/polly/graph/garden/connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'add', source_id: data.source, target_id: data.target, relationship_type: data.relationshipType, strength: newStrength })
        });
        edge.data('weight', newStrength);
        showToast(`Strengthened to ${newStrength.toFixed(1)}`, 'success');
      } catch (err) {
        showToast('Failed to strengthen connection', 'error');
      }
    } else if (action === 'weaken') {
      const newStrength = Math.max(0.1, (data.weight || 0.5) - 0.2);
      try {
        await fetch('http://127.0.0.1:11436/polly/graph/garden/connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'add', source_id: data.source, target_id: data.target, relationship_type: data.relationshipType, strength: newStrength })
        });
        edge.data('weight', newStrength);
        showToast(`Weakened to ${newStrength.toFixed(1)}`, 'success');
      } catch (err) {
        showToast('Failed to weaken connection', 'error');
      }
    }
    
    menu.remove();
  });
  
  // Close on click outside
  const closeMenu = (e) => {
    if (!menu.contains(e.target)) {
      menu.remove();
      document.removeEventListener('click', closeMenu);
    }
  };
  setTimeout(() => document.addEventListener('click', closeMenu), 0);
});
```

---

## Part 7: CSS Additions

### Task 21: New styles

**File: `electron-app/src/renderer/styles/main.css`**

Add after existing graph styles (~line 7434):

```css
/* Garden Stats Dashboard */
.garden-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 4px;
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
  line-height: 1.2;
}

.garden-stat-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.garden-coverage-bar {
  width: 100%;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 8px;
}

.garden-coverage-fill {
  height: 100%;
  background: var(--accent-primary);
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* Garden Section */
.garden-section {
  border-bottom: 1px solid var(--border-primary);
}

.garden-section:last-child {
  border-bottom: none;
}

/* Garden Suggestion Items */
.garden-suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  margin-bottom: 6px;
  background: var(--bg-secondary);
  transition: background 0.15s;
}

.garden-suggestion-item:hover {
  background: var(--bg-tertiary);
}

.garden-suggestion-info {
  flex: 1;
  min-width: 0;
}

.garden-suggestion-reason {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
  line-height: 1.3;
}

.garden-suggestion-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.garden-btn-accept,
.garden-btn-dismiss {
  padding: 3px 8px;
  font-size: 10px;
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all 0.15s;
}

.garden-btn-accept {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.garden-btn-accept:hover {
  opacity: 0.9;
}

.garden-btn-dismiss {
  background: transparent;
  color: var(--text-secondary);
}

.garden-btn-dismiss:hover {
  background: var(--bg-tertiary);
}

/* Garden Isolated Item (enhanced) */
.garden-isolated-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.garden-isolated-item:hover {
  background: var(--bg-tertiary);
}

.garden-isolated-item:hover .garden-item-actions {
  opacity: 1;
}

.garden-item-actions {
  opacity: 0;
  display: flex;
  gap: 4px;
  margin-left: auto;
  transition: opacity 0.15s;
}

/* Enrichment results inline */
.garden-enrich-results {
  padding: 8px;
  margin-top: 4px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 11px;
}

.garden-entity-tag {
  display: inline-block;
  padding: 2px 6px;
  margin: 2px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 3px;
  font-size: 10px;
  color: var(--text-primary);
}

/* Edge type toggles */
.edge-type-toggles label:hover {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

/* Connection dialog */
.graph-connection-dialog select:focus,
.graph-connection-dialog input:focus {
  outline: 1px solid var(--accent-primary);
}

/* Prune details open state */
.garden-prune-details[open] .prune-chevron {
  transform: rotate(90deg);
}

/* Node detail connections */
.detail-connection-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  font-size: 11px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
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
  padding: 2px 4px;
  background: none;
  border: none;
  color: var(--text-error);
  cursor: pointer;
  font-size: 10px;
  transition: opacity 0.15s;
}

.detail-edge-indicator {
  width: 16px;
  height: 2px;
  border-radius: 1px;
  flex-shrink: 0;
}

/* Graph context menu hover */
.graph-ctx-item:hover {
  background: var(--bg-tertiary);
}
```

---

## EntityStore Methods Needed

Several backend endpoints need EntityStore methods that may not exist. Check and add:

1. `entity_store.get_mentions_for_source(source_id, source_type)` — returns entity mentions for a given source note
2. `entity_store.move_mentions(source_id, target_id)` — moves entity mentions from one source to another
3. `entity_store.prune_weak_relationships(threshold)` — removes relationships below strength threshold
4. `entity_store.prune_stale_entities()` — removes entities with zero mentions
5. `entity_store.remove_relationship(source_id, target_id)` — soft-deletes a relationship
6. `entity_store.get_stats()` — returns entity/relationship/mention counts

Check `core/entities/store.py` to see which already exist and implement missing ones.

---

## Implementation Order

1. Tasks 1-2 (layout fix) — immediate visual improvement
2. Tasks 3-6 (edge legend + filters) — make graph navigable  
3. Tasks 7-11 (backend endpoints) — enable garden features
4. Tasks 12-17 (garden UI) — full garden experience
5. Tasks 18-20 (details panel + connection management) — interactive graph management
6. Task 21 (CSS) — style everything
7. Task 22 (integration testing) — verify everything works together
