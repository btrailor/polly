# Auto-Linking Spec

## Problem

109 notes exist in the graph as **completely isolated nodes** with 0 edges. The backlinks system works correctly but depends on explicit `[[wikilinks]]` in note content. Only 7 of 109 notes contain any wikilinks (5 hub notes + 2 others), and most of those link to notes that don't exist as files. The result: a graph of disconnected dots.

**Root cause:** Notes were imported or created without cross-references. The system has no way to discover connections that aren't explicitly written as `[[...]]`.

**Goal:** Automatically discover and surface connections between notes using signals that already exist in the data — without requiring the user to manually add `[[wikilinks]]` to 100+ notes.

---

## Current State

| Signal | Available? | Used for edges? |
|---|---|---|
| Explicit wikilinks `[[Note B]]` | 7 of 109 notes | Yes (backlinks index) — but index not always built |
| Frontmatter/inline tags | Many notes have tags | No |
| Plain-text mentions of note titles | Unknown, likely common | No |
| Shared domain (folder) | All notes have domains | No |
| RAG embedding similarity | Indexed in ChromaDB | No |
| Extracted entities (spaCy/regex) | Available via entity store | No (was incorrectly used as nodes, now metadata only) |

---

## Design Principles

1. **No LLM calls required.** Auto-linking must work instantly from existing data. LLM-assisted linking is a future enhancement, not a dependency.

2. **Edge types are explicit.** Each auto-linking strategy produces edges with a distinct `type` so the user and the UI can distinguish between a deliberate wikilink and an inferred tag connection.

3. **Backlinks are primary.** Explicit `[[wikilinks]]` are the strongest signal and always shown. Auto-links supplement them, not replace them.

4. **Progressive — not overwhelming.** Start with high-confidence connections. The graph should look useful with 20-50 edges, not noisy with 500.

---

## Linking Strategies (Implementation Order)

### Strategy 1: Fix Backlinks Initialization

**Problem:** `get_backlinks_index()` returns an empty `BacklinksIndex` that never calls `build_backlinks()`. The index only gets populated when `NotesSyncManager.start()` runs — which depends on the notes source being set to 'native' with `auto_index` enabled.

**Fix:** When the graph endpoints need backlinks data, ensure `build_backlinks()` has been called. Add a lazy initialization check: if the backlinks index is empty and notes exist, build it.

**Edge type:** `backlink` (already exists)
**Confidence:** 1.0 (explicit user intent)
**Expected edges:** ~15-30 (from hub note wikilinks that resolve to existing notes)

### Strategy 2: Unlinked Mentions

**Concept:** Scan every note's content for plain-text occurrences of other note names or titles. If note "Docker Deployment" contains the text "Live Performance Rig" without wrapping it in `[[...]]`, that's a real reference that should create a graph edge.

**Algorithm:**
1. Build a lookup of all note names + titles + aliases (from NotesIndex)
2. For each note, read its content and search for occurrences of other note names/titles
3. Match case-insensitively, whole-word boundaries to avoid false positives
4. Exclude self-references and matches inside existing `[[wikilinks]]`
5. Create edges with type `mention`

**Edge type:** `mention`
**Confidence:** 0.8 (strong — the text literally contains the note name)
**Performance:** O(N * M) where N = notes, M = unique note names. For 109 notes this is trivial. For 1000+ notes, use an Aho-Corasick automaton or pre-filter by token overlap.

**Considerations:**
- Short note names (1-2 words) may produce false positives. Apply a minimum character length (e.g., 4+ characters) or require exact case match for short names.
- Frontmatter content should be excluded from scanning (tags, title fields contain note-like strings).
- Code blocks should be excluded.

### Strategy 3: Shared Tags

**Concept:** Two notes sharing the same tag have an intentional topical connection. The user explicitly tagged them with the same concept.

**Algorithm:**
1. Build tag-to-notes mapping (from TagsIndex or frontmatter + inline tags)
2. For each tag with 2+ notes, create edges between all notes sharing that tag
3. Weight by selectivity: a tag shared by 2 notes is more meaningful than a tag shared by 20

**Edge type:** `shared_tag`
**Confidence:** 0.6 (intentional but indirect — the user tagged both notes, didn't link them)
**Weight formula:** `1.0 / log2(count_of_notes_with_this_tag)` — rare tags create stronger edges

**Considerations:**
- Very common tags (e.g., 10+ notes) create too many edges. Cap at N edges per tag or reduce weight significantly.
- Multiple shared tags between the same pair of notes should strengthen the edge, not create duplicates. Merge into one edge with combined weight.

---

## Edge Data Model

All edges returned by `/polly/graph/nodes` use this structure:

```json
{
  "source": "note_name_a",
  "target": "note_name_b",
  "type": "backlink | mention | shared_tag",
  "strength": 1.0,
  "is_ghost": false,
  "metadata": {
    "tag": "docker",
    "context": "...mentioned Live Performance Rig in paragraph 3..."
  }
}
```

### Edge Type Visual Encoding (Frontend)

| Type | Line Style | Color | Opacity |
|---|---|---|---|
| `backlink` | Solid | White/bright | 0.8 |
| `mention` | Dashed | Blue | 0.6 |
| `shared_tag` | Dotted | Green | 0.4 |

These map to existing Cytoscape style selectors — `references` (solid), `relates_to` (dashed), `co_occurs_with` (dotted).

---

## Implementation Plan

### Step 1: Fix Backlinks Initialization

**File:** `interfaces/server.py` (graph endpoints)

In `get_graph_nodes()` and `get_graph_list()`, after getting the backlinks index, check if it has been built. If not, trigger `build_backlinks()` with the notes path.

```python
backlinks_idx = get_backlinks_index(notes_idx)
if not backlinks_idx._last_build:
    notes_path = Path(polly.config.get('knowledge_base', {}).get('path', '')) / 'notes'
    backlinks_idx.build_backlinks(notes_path)
```

### Step 2: Unlinked Mentions Module

**New file:** `core/unlinked_mentions.py`

```python
class UnlinkedMentionsIndex:
    """Detects plain-text references to note names in note content."""
    
    def __init__(self, notes_index: NotesIndex):
        self.notes_index = notes_index
        self._mentions: Dict[str, List[Mention]] = {}  # target_name -> [Mention]
    
    def build(self, notes_path: Path):
        """Scan all notes for unlinked mentions of other note names."""
        # 1. Collect all note names, titles, aliases (min 4 chars)
        # 2. For each note, read content
        # 3. Strip frontmatter, code blocks, existing [[wikilinks]]
        # 4. Search for note name occurrences (case-insensitive, word boundary)
        # 5. Store as Mention(source_name, target_name, line, context)
    
    def get_mentions_of(self, note_name: str) -> List[Mention]:
        """Get all notes that mention this note name in their text."""
    
    def get_mentions_from(self, note_name: str) -> List[Mention]:
        """Get all note names mentioned in this note's text."""
```

### Step 3: Shared Tags Edge Builder

**In:** `interfaces/server.py` (or a helper module)

Build shared-tag edges when constructing the graph response. Uses TagsIndex (already built by NotesSyncManager) or falls back to reading tags from NotesIndex.

```python
def build_shared_tag_edges(notes: List[NoteInfo], tags_idx: TagsIndex) -> List[dict]:
    """Create edges between notes sharing the same tags."""
    tag_to_notes = {}
    for note in notes:
        for tag in tags_idx.get_note_tags(note.name):
            tag_to_notes.setdefault(tag, []).append(note.name)
    
    edges = []
    seen = set()
    for tag, note_names in tag_to_notes.items():
        if len(note_names) < 2 or len(note_names) > 10:  # Skip very common tags
            continue
        weight = 1.0 / max(1, log2(len(note_names)))
        for i, a in enumerate(note_names):
            for b in note_names[i+1:]:
                key = tuple(sorted([a, b]))
                if key not in seen:
                    seen.add(key)
                    edges.append({"source": a, "target": b, "type": "shared_tag", "strength": weight})
    return edges
```

### Step 4: Wire Into Graph Endpoints

Update `/polly/graph/nodes` to combine all three edge sources:

```python
# 1. Backlink edges (existing)
edges = build_backlink_edges(notes, backlinks_idx)

# 2. Unlinked mention edges
mentions_idx = get_unlinked_mentions_index(notes_idx)
edges += build_mention_edges(notes, mentions_idx)

# 3. Shared tag edges
tags_idx = get_tags_index(notes_idx)
edges += build_shared_tag_edges(notes, tags_idx)

# Deduplicate: if same pair has both backlink + mention, keep backlink only
edges = deduplicate_edges(edges)
```

---

## Future Extensions (Not in This Implementation)

### Embedding Similarity (Tier 2)
Use RAG vector similarity to find semantically similar notes. Create `similar_to` edges for pairs above a cosine threshold (e.g., 0.85). Expensive to compute for all pairs — run as a background job or on-demand.

### LLM Wikilink Suggestions (Tier 3)  
A "Suggest Links" action in the Garden view that asks the LLM to propose `[[wikilinks]]` for a note given the list of all note titles. User approves before insertion. Creates real backlinks, not inferred edges.

### Conversation Linking
Conversations contain full message text that references notes, topics, and decisions. Entity extraction on conversation content + shared entity edges would connect conversations to relevant notes. Requires running extraction on conversation messages.

---

## Success Criteria

After implementation:
- Graph shows **meaningful connections** between notes (target: 30-100 edges for 109 notes)
- Hub notes are visibly connected to their referenced notes (backlinks working)
- Notes that discuss the same topics are connected even without explicit wikilinks
- Edge types are visually distinguishable in the graph
- No false positives that make the graph noisy or confusing
- Graph loads in under 2 seconds for 100-500 nodes
