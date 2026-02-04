# Phase 21 Architecture Update: Migration to Native Notes

**Date:** January 28, 2026  
**Status:** Specification Updated - Ready for Implementation  
**Issue Found:** Original spec was designed for deprecated Obsidian integration  
**Solution:** Completely redesigned for Phase 16 native notes system

---

## Problem Identified

The original Phase 21 specification (dated earlier) was written for the **Obsidian integration** architecture which has since been replaced by the **native Polly notes system** (Phase 16, completed Jan 26, 2026).

**Key Issues:**
- Referenced `/integrations/obsidian.py` and `obsidian.create_note()` method
- Used old Obsidian-based endpoints and preview system
- Assumed dependency on Obsidian vault structure
- Did not leverage NotesIndex or native notes infrastructure

---

## Architecture Changes

### OLD Architecture (Obsolete)

```
User creates note → Obsidian integration
                          ↓
                  obsidian.create_note()
                          ↓
                  obsidian_dedup.py checks similarity
                          ↓
                  Shows preview modal with similar notes
                          ↓
                  Obsidian integration writes to vault
```

**Files:**
- `/integrations/obsidian_dedup.py` (NEW, never created)
- `/integrations/obsidian.py` (modify create_note method)
- `/electron-app/src/renderer/app.js` (old app.js)
- Old Obsidian preview modal

### NEW Architecture (Native Notes)

```
User clicks "Create Note" → Create Note Modal in notes-manager.js
                                      ↓
                          POST /polly/notes/create (check_duplicates=true)
                                      ↓
                          DeduplicationEngine.check_similarity()
                                      ↓
                          RAG search in 'notes' collection
                                      ↓
                          NotesIndex lookups for metadata
                                      ↓
                          Returns {status: "similar_found", similar_notes: [...]}
                                      ↓
                          notes-manager.js shows warning in modal
                                      ↓
                          User chooses: Append | Link | Create Anyway
                                      ↓
           POST /polly/notes/append | POST /polly/notes/create (bypass)
```

**Files:**
- `/core/notes_dedup.py` (NEW - core system, not integration)
- `/interfaces/server.py` (modify `/polly/notes/create`, add `/polly/notes/append`)
- `/core/polly.py` (initialize dedup engine)
- `/electron-app/src/renderer/notes-manager.js` (native notes UI)
- Create Note Modal (already exists in Phase 16)

---

## Key Architectural Decisions

### 1. Core System vs Integration

**Decision:** Place dedup engine in `/core/notes_dedup.py`, NOT `/integrations/obsidian_dedup.py`

**Rationale:**
- Deduplication is a core Polly feature, not integration-specific
- Works with any note source (native, Obsidian, future sources)
- Lives alongside other core systems (RAG, NotesIndex, BacklinksIndex)
- Not coupled to external tool (Obsidian)

### 2. Endpoint-Based vs Method-Based

**Decision:** Integrate at HTTP endpoint level (`/polly/notes/create`)

**Rationale:**
- Cleaner separation of concerns
- Works with existing note creation flow
- Frontend (notes-manager.js) already uses this endpoint
- No need to modify low-level file I/O logic
- Easier to add `check_duplicates` parameter

### 3. Modal-Based UI vs Preview Modal

**Decision:** Use existing Create Note Modal, not separate preview modal

**Rationale:**
- Phase 16 already has Create Note Modal in notes UI
- Users already familiar with this flow
- No need for separate modal system
- Inline warning feels more natural than preview step
- Consistent with native notes UX

### 4. Synchronous vs Async Check

**Decision:** Synchronous check in endpoint before file creation

**Rationale:**
- Simple request/response flow
- No need for async state management
- Duplicate check is fast enough (< 500ms)
- User explicitly triggers check by clicking "Create Note"
- No race conditions

---

## Component Responsibilities

### `/core/notes_dedup.py`
- **Purpose:** Semantic similarity detection engine
- **Dependencies:** RAG system, NotesIndex
- **Exports:** DeduplicationEngine class, get_dedup_engine()
- **Responsibilities:**
  - Search RAG 'notes' collection for similar content
  - Extract snippets from matched notes
  - Return sorted list of SimilarNote objects
  - Generate wikilinks for similar notes
  - Error handling and graceful degradation

### `/interfaces/server.py`
**Modified:** `/polly/notes/create` endpoint
- **New Parameter:** `check_duplicates: bool = True`
- **New Response:** `{status: "similar_found", similar_notes: [...]}`
- **Logic:**
  1. Parse request parameters
  2. If check_duplicates=true, call dedup engine
  3. If similar notes found, return them (don't create yet)
  4. If no similar notes or check=false, create note normally
  5. Return standard success response

**New Endpoint:** `/polly/notes/append`
- **Purpose:** Append content to existing note
- **Parameters:** path, content, separator
- **Logic:** Read existing content, append with separator, write back

### `/core/polly.py`
**Modified:** `__init__` method
- Initialize dedup engine after RAG and NotesIndex
- Pass RAG and NotesIndex instances to dedup engine
- Store as global singleton via `init_dedup_engine()`

### `/electron-app/src/renderer/notes-manager.js`
**Modified:** `createNoteFromModal()` function
- Call `/polly/notes/create` with `check_duplicates: true`
- Check response status for "similar_found"
- If found, call `showSimilarNotesWarning()` instead of closing modal
- Store proposed note data in global state

**New Function:** `showSimilarNotesWarning()`
- Render similar notes as radio button cards
- Show three action buttons
- Scroll warning into view
- First item selected by default

**New Event Handlers:**
- `btn-append-to-similar` → POST `/polly/notes/append`
- `btn-link-to-similar` → Generate wikilinks, POST `/polly/notes/create` (bypass)
- `btn-create-anyway` → POST `/polly/notes/create` (bypass)

### `/electron-app/src/renderer/index.html`
**Modified:** Create Note Modal
- Add `#similar-notes-warning` section (initially hidden)
- Add `#similar-notes-list` container
- Add three action buttons with icons
- Maintain existing form structure

### `/electron-app/src/renderer/styles/main.css`
**New Styles:**
- `.similar-notes-warning` - Yellow border, secondary background
- `.similar-note-card` - Hover and selected states
- `.similarity-badge` - Color-coded by percentage (high/medium/low)
- `.similar-note-header` - Flex layout for radio + title + badge
- `.similar-note-snippet` - Muted text for content preview
- `.similar-note-path` - Monospace domain/name display

---

## Data Flow Example

### Scenario: User Creates Note Similar to Existing Note

**Step 1:** User fills Create Note Modal
```
Name: "Continuation Over Completion"
Domain: "02-Signals"
Content: "The goal is to keep the game going, not to win..."
```

**Step 2:** User clicks "Create Note" button

**Step 3:** Frontend sends request
```javascript
POST /polly/notes/create
{
  "name": "Continuation Over Completion",
  "domain": "02-Signals",
  "content": "The goal is to keep the game going, not to win...",
  "check_duplicates": true
}
```

**Step 4:** Backend checks for duplicates
```python
dedup_engine = get_dedup_engine()
similar_notes = dedup_engine.check_similarity(
    content="The goal is to keep the game going, not to win...",
    title="Continuation Over Completion",
    similarity_threshold=0.70,
    max_results=5
)
```

**Step 5:** RAG search finds matches
```python
# RAG searches 'notes' collection with query:
# "Continuation Over Completion\n\nThe goal is to keep the game going..."

# Returns results:
[
  SearchResult(score=0.87, doc=Document(content="# Infinite Games..."))
]
```

**Step 6:** NotesIndex provides metadata
```python
note_info = notes_index.find_note_by_path("/path/to/infinite_games.md")
# Returns: NoteInfo(name="infinite_games", title="Infinite Games", domain="02-Signals")
```

**Step 7:** Backend returns similar notes
```json
{
  "status": "similar_found",
  "similar_notes": [
    {
      "path": "/full/path/to/infinite_games.md",
      "name": "infinite_games",
      "title": "Infinite Games",
      "domain": "02-Signals",
      "similarity": 0.87,
      "snippet": "Playing to keep the game going rather than to win. Focuses on continuation over completion..."
    }
  ],
  "proposed_note": {
    "name": "continuation_over_completion",
    "title": "Continuation Over Completion",
    "domain": "02-Signals",
    "content": "..."
  }
}
```

**Step 8:** Frontend shows warning
```javascript
showSimilarNotesWarning(result.similar_notes);
// Renders warning with radio buttons for each similar note
// Shows three action buttons
```

**Step 9:** User selects "Append to Selected"

**Step 10:** Frontend sends append request
```javascript
POST /polly/notes/append
{
  "path": "/full/path/to/infinite_games.md",
  "content": "The goal is to keep the game going, not to win...",
  "separator": "\n\n---\n\n"
}
```

**Step 11:** Backend appends content
```python
existing = note_path.read_text()
new_content = existing + "\n\n---\n\n" + content
note_path.write_text(new_content)
```

**Step 12:** Frontend refreshes and opens updated note
```javascript
await refreshNotesList();
loadNoteContent("/full/path/to/infinite_games.md");
```

---

## Benefits of New Architecture

### 1. **Cleaner Separation**
- Dedup engine is independent of note storage implementation
- Works with native notes, Obsidian, or future sources
- No tight coupling to specific integration

### 2. **Better UX**
- Inline warning in familiar Create Note Modal
- No extra preview step
- Immediate visual feedback
- Action buttons directly in modal

### 3. **Leverages Existing Infrastructure**
- Uses Phase 16 notes system
- Uses NotesIndex for metadata
- Uses RAG for semantic search
- No new infrastructure needed

### 4. **More Maintainable**
- Core system, not integration-specific
- Clear responsibilities per component
- Standard HTTP endpoint pattern
- Easy to test and debug

### 5. **Future-Proof**
- Works with any note source manager
- Compatible with future Phase 16 enhancements
- Can be extended with pattern learning (Phase 13)
- Can be visualized in knowledge graph (Phase 12)

---

## Migration from Original Spec

### What Changed

| Original Spec | New Spec |
|--------------|----------|
| `/integrations/obsidian_dedup.py` | `/core/notes_dedup.py` |
| Obsidian integration dependency | RAG + NotesIndex dependency |
| `obsidian.create_note()` method | `/polly/notes/create` endpoint |
| `/electron-app/src/renderer/app.js` | `/electron-app/src/renderer/notes-manager.js` |
| Old preview modal | Create Note Modal |
| Async method `await check_similarity()` | Sync method `check_similarity()` |
| `/polly/obsidian/create-note` endpoint | `/polly/notes/create` endpoint |
| `/polly/obsidian/append-note` endpoint | `/polly/notes/append` endpoint |

### What Stayed the Same

- **User experience flow:** Same warning UI, same three actions
- **Similarity detection logic:** RAG search with 70% threshold
- **Snippet extraction:** 200-char snippets from matched content
- **Wikilink generation:** `[[note_name]]` format
- **CSS styling:** Same visual design
- **Performance target:** < 500ms for duplicate check
- **Error handling:** Graceful degradation if RAG unavailable

---

## Implementation Timeline (Unchanged)

**Day 1 (6-8 hours):** Backend engine and endpoint integration
- Create `/core/notes_dedup.py`
- Modify `/polly/notes/create` endpoint
- Add `/polly/notes/append` endpoint
- Initialize in `/core/polly.py`
- Test with API calls

**Day 2 (6-8 hours):** Frontend UI and event handlers
- Add warning section to Create Note Modal HTML
- Modify `createNoteFromModal()` in notes-manager.js
- Add `showSimilarNotesWarning()` function
- Add three event handlers (append, link, create-anyway)
- Add CSS styles
- Test end-to-end flow

**Day 3 (4-6 hours):** Polish and testing
- Add error handling
- Add edge case handling
- Add config.yaml settings
- Comprehensive testing
- Documentation

**Total: 2-3 days** (same as original estimate)

---

## Ready for Implementation

The Phase 21 specification has been completely updated to work with the native Polly notes system. All architectural decisions have been made, and the implementation plan is clear.

**Next Step:** Begin Day 1 implementation by creating `/core/notes_dedup.py`.

**Files Modified:**
- ✅ `PHASE21_KNOWLEDGE_DEDUPLICATION.md` - Fully updated spec
- ✅ `PHASE21_ARCHITECTURE_UPDATE.md` - This document

**Ready to proceed:** YES ✅
