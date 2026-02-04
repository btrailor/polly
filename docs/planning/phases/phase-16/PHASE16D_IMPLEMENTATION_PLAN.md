# Phase 16d: Complete Native Notes System

**Status:** In Progress  
**Started:** January 31, 2026  
**Target:** 10-14 days to production-ready  
**Priority:** CRITICAL - Foundation for all knowledge features

---

## Overview

Phase 16 (native notes frontend) is 40% complete. We have:
- ✅ Notes browser with file tree
- ✅ Monaco editor
- ✅ Wiki-links with auto-update
- ✅ File watcher for real-time sync
- ✅ Scribe persona creating notes
- ⚠️ **Only 44/110 notes indexed to RAG**
- ⚠️ **Missing: Templates, search UI, versioning, graph view**

This phase completes the foundation so Phase 12a (Knowledge Graph) can build on solid ground.

---

## Scope: What We're Building

### **MUST HAVE (Production-Ready Baseline)**
These are non-negotiable for a solid foundation:

1. ✅ **Complete RAG Indexing** (44/110 → 110/110)
2. ✅ **File Watcher Polish** (reduce logging, add UI status)
3. ✅ **Migration Progress Feedback** (detailed messages)
4. ✅ **Note Template System** (for Scribe + user customization)
5. ✅ **Full-Text Search UI** (hybrid BM25 + semantic)

### **SHOULD HAVE (Enhanced Experience)**
Nice-to-have for better UX:

6. ⏸️ **Migration Pre-flight Check** (preview before migrating)
7. ⏸️ **Tag Browser** (filter notes by tag)
8. ⏸️ **Backlinks Panel** (show incoming references)

### **DEFER (Post-Foundation)**
Save for after Knowledge Graph:

- ❌ Graph View → Phase 12a will build this properly
- ❌ Note Versioning → Nice but not critical
- ❌ Note Statistics Dashboard → Polish feature
- ❌ Export Notes → Can wait
- ❌ Smart Suggestions → AI enhancement

---

## Implementation Plan

### **Week 1: Core Fixes (Days 1-5)**

#### **Day 1: Complete RAG Indexing** (3-4 hours)
**Goal:** Get all 110 notes indexed, not just 44

**Tasks:**
1. Add "Re-index All Notes" button in Settings → Notes tab
2. Implement background indexing with progress tracking
3. Add streaming progress endpoint: `POST /polly/notes/reindex` (SSE)
4. Show progress in UI: "Indexing notes... (67/110)"
5. Test with full vault

**Files:**
- `interfaces/server.py` - New endpoint with progress streaming
- `electron-app/src/renderer/index.html` - Add button
- `electron-app/src/renderer/app.js` - Progress handler

**Success Criteria:**
- ✅ All notes indexed to RAG
- ✅ Progress visible in UI
- ✅ No timeout errors

---

#### **Day 2: File Watcher Polish** (4-5 hours)
**Goal:** Production-ready file watcher with UI visibility

**Part A: Reduce Debug Logging (1 hour)**
1. Add `DEBUG_FILE_WATCHER` env variable
2. Make verbose prints conditional
3. Keep important logger calls

**Part B: File Watcher Status UI (3-4 hours)**
1. Add status indicator in Notes Browser header:
   - 🟢 Green: "Watching for changes (2s ago)"
   - 🟡 Yellow: "Indexing... (3 files)"
   - 🔴 Red: "File watcher stopped"
2. Show stats: "110 notes • 899 chunks indexed"
3. Add API endpoint: `GET /polly/notes/sync/status`
4. Poll status every 5 seconds

**Files:**
- `core/notes_file_watcher.py` - Add status property
- `interfaces/server.py` - Add status endpoint
- `electron-app/src/renderer/notes-manager.js` - Status display
- `electron-app/src/renderer/styles/notes.css` - Status styling

**Success Criteria:**
- ✅ Less verbose console output
- ✅ Real-time status visible to user
- ✅ Know when indexing is happening

---

#### **Day 3: Migration Progress Feedback** (2-3 hours)
**Goal:** Show detailed progress during Obsidian migration

**Tasks:**
1. Add status message display below progress bar
2. Backend sends progress updates:
   - "Scanning Obsidian vault... (0/101 files)"
   - "Copying markdown files... (45/101)"
   - "Copying attachments... (12/23)"
   - "Building index... (67/101)"
   - "Indexing to RAG... (23/101)"
3. Update migration API to stream detailed progress

**Files:**
- `interfaces/server.py` - Enhanced migration endpoint
- `electron-app/src/renderer/app.js` - Progress message display

**Success Criteria:**
- ✅ User knows what's happening during migration
- ✅ Can see which step is slow
- ✅ Better user confidence

---

#### **Day 4-5: Note Template System** (8-10 hours)
**Goal:** Flexible, user-customizable note templates

**Architecture:**
```
~/.polly/templates/
  default.md           # Fallback template
  meeting.md           # Meeting notes
  practice.md          # Practices & exercises
  concept.md           # Concept definitions
  howto.md            # How-to guides
  custom/             # User templates
    [user-defined].md
```

**Part A: Backend System (4-5 hours)**
1. Create `core/note_templates.py`:
   - `load_templates()` - Scan templates directory
   - `render_template(name, vars)` - Replace `{{vars}}`
   - `get_default_template(domain)` - Domain-specific defaults
2. Template variables:
   - `{{title}}` - Note title
   - `{{date}}` - Current date (ISO 8601)
   - `{{time}}` - Current time
   - `{{domain}}` - Domain name
   - `{{tags}}` - Comma-separated tags
   - `{{author}}` - User name
3. Add API endpoints:
   - `GET /polly/templates` - List templates
   - `GET /polly/templates/:name` - Get template
   - `POST /polly/templates` - Create template
   - `PUT /polly/templates/:name` - Update template
   - `DELETE /polly/templates/:name` - Delete template

**Part B: Integration (2-3 hours)**
1. Update Scribe persona to use templates:
   - Check for `{{domain}}.md` template first
   - Fall back to `default.md`
   - Render with note variables
2. Update Notes Browser "New Note" modal:
   - Add template selector dropdown
   - Preview template before creation

**Part C: UI for Template Management (2-3 hours)**
1. Add Templates tab in Settings
2. List all templates with edit/delete actions
3. Template editor modal with:
   - Name input
   - Markdown editor with live preview
   - Variable helper (insert `{{var}}` snippets)
   - Save/Cancel buttons

**Files to Create:**
- `core/note_templates.py` (~300 lines)
- `~/.polly/templates/default.md`
- `~/.polly/templates/meeting.md`
- `~/.polly/templates/practice.md`
- `~/.polly/templates/concept.md`

**Files to Modify:**
- `core/personas/implementations/scribe.py` - Use templates
- `interfaces/server.py` - Template endpoints (~150 lines)
- `electron-app/src/renderer/index.html` - Templates tab
- `electron-app/src/renderer/app.js` - Template management UI

**Success Criteria:**
- ✅ Scribe uses templates when creating notes
- ✅ Users can customize templates in Settings
- ✅ Templates support variables
- ✅ New notes use appropriate template for domain

---

### **Week 2: Enhanced Features (Days 6-10)**

#### **Day 6-7: Full-Text Search UI** (8-10 hours)
**Goal:** Dedicated search interface for notes

**Architecture:**
- **Hybrid search:** BM25 (keyword) + RAG (semantic)
- **Filters:** Domain, tags, date range, folder
- **Results:** Snippet with highlights, relevance score
- **Performance:** < 500ms for 1000+ notes

**Part A: Backend Search (4-5 hours)**
1. Add `POST /polly/notes/search` endpoint:
   - Accept: query, filters (domain, tags, date_range, folder)
   - BM25 search on title + content
   - RAG semantic search
   - Merge results with RRF (Reciprocal Rank Fusion)
   - Return: snippets with highlights, scores
2. Optimize for large note collections:
   - Use existing BM25 index from notes_index.py
   - Limit to top 50 results
   - Cache frequent queries

**Part B: Search UI (4-5 hours)**
1. Add Search view in Notes page (new tab or modal)
2. Search input with:
   - Autocomplete for tags
   - Filter dropdowns (domain, tags, date)
   - Sort options (relevance, date, title)
3. Results list:
   - Title with domain badge
   - Snippet (150 chars) with highlighted query terms
   - Relevance score (0-100)
   - Click to open note
4. Keyboard shortcuts:
   - Cmd+F to focus search
   - Arrow keys to navigate results
   - Enter to open selected result

**Files:**
- `interfaces/server.py` - Search endpoint (~100 lines)
- `core/notes_index.py` - Enhance search method
- `electron-app/src/renderer/notes-manager.js` - Search UI (~200 lines)
- `electron-app/src/renderer/styles/notes.css` - Search styling

**Success Criteria:**
- ✅ Find notes by keyword (BM25)
- ✅ Find notes by concept (semantic)
- ✅ Filter by domain/tags/date
- ✅ Fast (< 500ms)
- ✅ Highlights query terms

---

#### **Day 8-9: Migration Pre-flight Check** (6-8 hours)
**Goal:** Preview migration before starting

**Part A: Backend Preview (3-4 hours)**
1. Add `GET /polly/notes/migration/preview` endpoint:
   - Scan Obsidian vault
   - Count markdown files per folder
   - Count attachments
   - Estimate disk space
   - Estimate time (based on file count)
   - Return folder tree with counts

**Part B: Preview Modal (3-4 hours)**
1. Add "Preview Migration" button in Settings
2. Modal shows:
   - Folder tree with checkboxes (opt-in/out)
   - File counts: "123 markdown files, 45 attachments"
   - Disk space: "~15 MB"
   - Estimated time: "~2-3 minutes"
   - Warning about overwriting existing files
3. "Start Migration" button proceeds to actual migration

**Files:**
- `interfaces/server.py` - Preview endpoint (~80 lines)
- `electron-app/src/renderer/app.js` - Preview modal
- `electron-app/src/renderer/index.html` - Modal HTML

**Success Criteria:**
- ✅ Users see what will be migrated
- ✅ Can exclude folders
- ✅ Know disk space required
- ✅ Better migration confidence

---

#### **Day 10: Tag Browser** (4-5 hours)
**Goal:** Browse notes by tag

**Part A: Backend (2 hours)**
1. Add `GET /polly/notes/tags` endpoint:
   - List all tags with counts
   - Support nested tags (`#learning/python`)
   - Return: `[{tag: "learning", count: 23, subtags: [...]}]`

**Part B: UI (2-3 hours)**
1. Add Tags panel in Notes Browser sidebar:
   - Tag cloud (size = count)
   - Hierarchical list for nested tags
   - Click tag to filter notes
2. Tag filtering:
   - Show only notes with selected tag
   - Multi-tag selection (AND logic)
   - Clear filters button

**Files:**
- `interfaces/server.py` - Tags endpoint (~50 lines)
- `electron-app/src/renderer/notes-manager.js` - Tag browser (~150 lines)
- `electron-app/src/renderer/styles/notes.css` - Tag styling

**Success Criteria:**
- ✅ See all tags with counts
- ✅ Click tag to filter notes
- ✅ Support nested tags
- ✅ Tag cloud visualization

---

#### **Day 11 (Optional): Backlinks Panel** (4-5 hours)
**Goal:** Show incoming references to current note

**Part A: Backend (2 hours)**
1. Add `GET /polly/notes/:id/backlinks` endpoint:
   - Find all notes linking to this note
   - Return: note title, snippet of link context
   - Use existing backlinks index

**Part B: UI (2-3 hours)**
1. Add Backlinks panel in note preview:
   - Show below note content
   - List of notes linking here
   - Click to navigate
2. Update when note renamed (wiki-links updated)

**Files:**
- `interfaces/server.py` - Backlinks endpoint (~40 lines)
- `electron-app/src/renderer/notes-manager.js` - Backlinks panel
- `electron-app/src/renderer/styles/notes.css` - Panel styling

**Success Criteria:**
- ✅ See which notes link to current note
- ✅ Click to navigate
- ✅ Updates when links change

---

## Testing Plan

### **Functional Tests (Days 12-13)**

**Test Suite 1: RAG Indexing**
- Create 100 test notes
- Trigger re-index
- Verify all notes indexed
- Query RAG for each note
- Measure indexing time

**Test Suite 2: File Watcher**
- Create/modify/delete notes manually
- Verify watcher detects changes
- Check RAG updates automatically
- Test with rapid changes (10 notes in 5 seconds)
- Verify debouncing works

**Test Suite 3: Templates**
- Create note with each template
- Verify variables render correctly
- Test custom templates
- Test Scribe with templates
- Edit/delete templates

**Test Suite 4: Search**
- Keyword search (BM25)
- Semantic search (RAG)
- Filter by domain
- Filter by tags
- Filter by date range
- Verify result ranking

**Test Suite 5: Migration**
- Test with small vault (10 notes)
- Test with large vault (1000+ notes)
- Test with special characters
- Test with nested folders
- Test pre-flight preview accuracy

---

### **Performance Tests (Day 14)**

**Benchmark 1: Large Note Collection**
- Create 1000 test notes
- Measure file tree render time (< 500ms)
- Measure search time (< 500ms)
- Measure indexing time (< 2min for all)

**Benchmark 2: Real-time Sync**
- Create 10 notes rapidly
- Measure time to index (< 5s)
- Verify no dropped events
- Check memory usage

**Benchmark 3: Migration**
- Migrate 500-note vault
- Measure total time
- Verify progress accuracy
- Check error handling

---

## Success Criteria

### **Production-Ready Checklist**

**Core Functionality:**
- [ ] All notes indexed to RAG (110/110, not 44/110)
- [ ] File watcher running reliably
- [ ] Real-time sync working (create/edit/delete detected)
- [ ] Templates system functional
- [ ] Scribe uses templates
- [ ] Full-text search working

**User Experience:**
- [ ] File watcher status visible in UI
- [ ] Migration shows detailed progress
- [ ] Search UI intuitive and fast
- [ ] Tag browser working
- [ ] No confusing error messages

**Performance:**
- [ ] < 500ms search latency
- [ ] < 2 min to index 1000 notes
- [ ] < 5s to detect and index new note
- [ ] File tree renders < 500ms for 1000 notes

**Stability:**
- [ ] Zero crashes during 24-hour test
- [ ] File watcher recovers from errors
- [ ] No memory leaks
- [ ] Handles corrupted notes gracefully

**Documentation:**
- [ ] User guide updated
- [ ] API documentation complete
- [ ] Template system documented
- [ ] Troubleshooting guide

---

## Risk Mitigation

### **Risk 1: RAG Indexing Timeout**
**Mitigation:**
- Batch indexing (10 notes at a time)
- Show progress after each batch
- Allow user to pause/resume
- Increase timeout to 5 minutes

### **Risk 2: File Watcher Instability**
**Mitigation:**
- Add auto-restart on crash
- Log all errors to file
- Health check endpoint
- Manual restart button in UI

### **Risk 3: Template Complexity**
**Mitigation:**
- Start with simple variables only
- Add advanced features later (loops, conditionals)
- Provide 5-6 good default templates
- Clear documentation

### **Risk 4: Search Performance**
**Mitigation:**
- Use existing BM25 index (already fast)
- Limit to top 50 results
- Cache frequent queries
- Add pagination if needed

---

## Deliverables

### **Code:**
1. Complete RAG indexing system with UI
2. Polished file watcher with status indicator
3. Migration with detailed progress feedback
4. Note template system (backend + UI)
5. Full-text search UI
6. Tag browser
7. Migration pre-flight check
8. Backlinks panel (optional)

### **Documentation:**
1. Phase 16d completion report
2. Updated user guide
3. Template system guide
4. API documentation
5. Troubleshooting guide

### **Tests:**
1. Functional test suite (5 suites)
2. Performance benchmarks
3. Integration tests

---

## Timeline Summary

**Week 1: Core Fixes (5 days)**
- Day 1: Complete RAG indexing
- Day 2: File watcher polish
- Day 3: Migration progress
- Day 4-5: Template system

**Week 2: Enhanced Features (5 days)**
- Day 6-7: Full-text search UI
- Day 8-9: Migration pre-flight
- Day 10: Tag browser
- Day 11: Backlinks panel (optional)

**Week 3: Testing & Documentation (4 days)**
- Day 12-13: Functional tests
- Day 14: Performance tests

**Total: 14 days** (can compress to 10 days if we skip optional features)

---

## After Phase 16d

Once complete, we'll have a **rock-solid notes foundation** that enables:

**Phase 12a: Knowledge Graph** (Week 4-5)
- Visual graph of note connections
- Entity/relationship extraction
- Interactive visualization
- Foundation for reasoning transparency

**Phase 12b: Reasoning Transparency** (Week 6-7)
- "Why this connection?" explanations
- Trace reasoning paths through graph
- Confidence scores for relationships

Then we can tackle **Phase 11: Multi-Model Routing** (Week 8-12).

---

## Questions Before Starting

1. **Scope:** Do we want all features (14 days) or just Must-Haves (7-8 days)?

2. **Templates:** Should Scribe templates be domain-specific or note-type-specific?

3. **Search:** BM25 + semantic hybrid, or just semantic (RAG only)?

4. **Backlinks:** Must-have or nice-to-have?

5. **Testing:** How thorough? (Quick smoke tests vs full test suite)

---

**Ready to start Phase 16d? I recommend beginning with Day 1: Complete RAG Indexing. Should I proceed?**
