# Notes System Polish & Enhancement TODO

**Status:** Base functionality complete, needs polish and enhancement  
**Created:** January 31, 2026  
**Priority:** Medium (on hold for now)

---

## Executive Summary

The native knowledge base system is now functional with:
- ✅ Native KB in `~/.polly/notes/`
- ✅ Obsidian migration UI working
- ✅ Real-time file watcher auto-indexing (create/modify/delete)
- ✅ Scribe persona creating notes in native KB
- ✅ Notes Browser showing all notes
- ✅ 110 notes indexed, 899 RAG chunks from 44 files

However, several areas need polish before it's production-ready.

---

## High Priority

### 1. Complete RAG Indexing for All Notes

**Problem:** Only 44 of 110 notes are indexed to RAG (partial timeout during initial migration)

**Solution Options:**
- Add "Re-index All Notes" button in Settings → Notes tab
- Implement background indexing queue for large migrations
- Increase timeout for initial indexing operations
- Show indexing progress in UI (progress bar with file count)

**Estimated Effort:** 2-3 hours

**Files to Modify:**
- `/Users/brettgershon/polly/electron-app/src/renderer/index.html` - Add UI button
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js` - Add click handler
- `/Users/brettgershon/polly/interfaces/server.py` - Add streaming endpoint for progress

---

### 2. Reduce Debug Logging Verbosity

**Problem:** File watcher logs are very verbose (helpful for debugging, but noisy for production)

**Solution:**
- Add `DEBUG_FILE_WATCHER` environment variable
- Make `[FILE WATCHER]` print statements conditional
- Keep logger.info/error calls for important events

**Estimated Effort:** 30 minutes

**Files to Modify:**
- `/Users/brettgershon/polly/core/notes_file_watcher.py` (lines 74-99, 154-408)

**Example:**
```python
DEBUG = os.getenv('DEBUG_FILE_WATCHER', 'false').lower() == 'true'

def _should_process_file(self, path: Path) -> bool:
    if DEBUG:
        print(f"[FILE WATCHER] _should_process_file checking: {path}", flush=True)
    # ... rest of logic
```

---

### 3. File Watcher Status in UI

**Problem:** Users can't see if file watcher is running or if files are being synced

**Solution:** Add real-time sync indicator in Notes Browser
- Green dot: "Watching for changes"
- Yellow spinner: "Indexing..."
- Red dot: "File watcher stopped"
- Show last sync time
- Show pending changes count

**Estimated Effort:** 3-4 hours

**Files to Modify:**
- `/Users/brettgershon/polly/electron-app/src/renderer/notes-manager.js` - Add status display
- `/Users/brettgershon/polly/interfaces/server.py` - Add `/polly/notes/sync/status` endpoint
- `/Users/brettgershon/polly/core/notes_file_watcher.py` - Expose stats via API

**UI Mockup:**
```
┌─────────────────────────────────────┐
│ Notes                         [+]   │
├─────────────────────────────────────┤
│ 🟢 Watching for changes (2s ago)   │
│ 110 notes • 899 chunks indexed     │
├─────────────────────────────────────┤
│ Search notes...                     │
└─────────────────────────────────────┘
```

---

### 4. Migration Progress Feedback

**Problem:** Migration UI shows progress bar but doesn't show what's happening

**Solution:** Add detailed progress messages
- "Scanning Obsidian vault... (0/101 files)"
- "Copying markdown files... (45/101)"
- "Copying attachments... (12/23)"
- "Building index... (67/101)"
- "Indexing to RAG... (23/101)"

**Estimated Effort:** 2 hours

**Files to Modify:**
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js:7520-7587` (startMigration function)
- Add status message display below progress bar

---

## Medium Priority

### 5. Migration Pre-flight Check

**Problem:** Users don't know what will be migrated before starting

**Solution:** Add "Preview Migration" button
- Shows folder structure that will be copied
- Shows file count per folder
- Shows attachment count
- Estimates time and disk space
- Allows folder selection (opt-in/out specific folders)

**Estimated Effort:** 4-5 hours

**New Component:** Migration Preview Modal

---

### 6. Note Template System

**Problem:** Scribe persona uses hardcoded templates; users can't customize note structure

**Solution:** Implement template system
- Default templates for each domain (Sigils, Signals, Scrolls, Glyphs, Grids)
- User-customizable templates via Settings
- Template variables: `{{title}}`, `{{date}}`, `{{tags}}`, `{{domain}}`
- Scribe uses appropriate template when creating notes

**Estimated Effort:** 6-8 hours

**Files to Create:**
- `/Users/brettgershon/polly/core/note_templates.py`
- `/Users/brettgershon/polly/.polly/templates/` directory

**Files to Modify:**
- `/Users/brettgershon/polly/core/scribe.py` - Use templates instead of hardcoded format
- Add Templates tab in Settings UI

---

### 7. Backlinks and Graph View

**Problem:** Wiki-links `[[like-this]]` are parsed but not visualized

**Solution:** Implement backlinks panel and graph view
- Backlinks panel in note preview (shows notes linking to current note)
- Graph view showing connections between notes
- Click node to navigate to note
- Filter by domain/tags

**Estimated Effort:** 10-12 hours (significant UI work)

**Dependencies:**
- D3.js or similar for graph visualization
- Backlinks already parsed in notes_index.py (needs API endpoint)

---

### 8. Tag Browser

**Problem:** Tags are indexed but there's no UI to browse by tag

**Solution:** Add tag browser view
- List all tags with count
- Click tag to filter notes
- Tag cloud visualization
- Tag hierarchy support (nested tags like `#learning/python`)

**Estimated Effort:** 3-4 hours

**Files to Modify:**
- Add Tags tab in Notes view
- Add `/polly/notes/tags` API endpoint

---

### 9. Note History / Versioning

**Problem:** No way to see previous versions of notes or undo changes

**Solution:** Implement simple versioning
- Save snapshot on every significant edit
- Keep last 10 versions per note
- Show diff view between versions
- Restore previous version

**Estimated Effort:** 8-10 hours

**Storage:** `~/.polly/notes/.history/` (hidden from main index)

---

### 10. Full-Text Search UI

**Problem:** Notes can be searched via RAG but no dedicated search UI

**Solution:** Add dedicated search view
- Hybrid search: BM25 (exact match) + semantic (RAG)
- Filter by domain, tags, date
- Show snippets with highlights
- Search within specific folder

**Estimated Effort:** 5-6 hours

---

## Low Priority / Nice-to-Have

### 11. Daily Note Feature

Quick-create daily notes with automatic date-based naming.

**Estimated Effort:** 2 hours

---

### 12. Note Statistics Dashboard

Show insights:
- Most linked notes
- Most tagged notes  
- Notes created per day (chart)
- Domain distribution (pie chart)
- Word count trends

**Estimated Effort:** 4-5 hours

---

### 13. Export Notes

Export notes to:
- PDF
- HTML (static site)
- Markdown archive (zip)
- Notion import format
- Obsidian vault format

**Estimated Effort:** 6-8 hours

---

### 14. Smart Note Suggestions

When creating/editing notes, suggest:
- Related notes to link
- Relevant tags to add
- Similar existing notes (avoid duplicates)

**Estimated Effort:** 5-6 hours

---

### 15. Collaboration Features

**Long-term vision:**
- Share notes with others
- Real-time collaborative editing
- Comments and annotations
- Publish notes to web

**Estimated Effort:** 20+ hours (major feature)

---

### 16. Mobile App Sync

Sync notes with iOS/Android mobile app (Phase 10)

**Estimated Effort:** 15+ hours

---

## Technical Debt / Code Quality

### 17. Unit Tests for File Watcher

Add comprehensive tests for:
- Event detection (create/modify/delete)
- Debouncing logic
- Path filtering
- Callback execution
- Error handling

**Estimated Effort:** 4-5 hours

**Files to Create:**
- `/Users/brettgershon/polly/tests/test_notes_file_watcher.py`

---

### 18. Integration Tests for Migration

Test migration with various vault structures:
- Nested folders
- Special characters in filenames
- Large files (>1MB)
- Binary attachments
- Symlinks
- Canvas files

**Estimated Effort:** 3-4 hours

---

### 19. Performance Optimization

Optimize for large note collections (1000+ notes):
- Lazy loading in Notes Browser
- Virtual scrolling for long lists
- Incremental RAG indexing (chunk batching)
- Index caching
- Debounce search input

**Estimated Effort:** 6-8 hours

---

### 20. Error Recovery

Improve error handling:
- File watcher crashes → auto-restart
- RAG indexing failure → retry with exponential backoff
- Corrupted notes → skip and log error
- Out of disk space → show warning
- Migration interrupted → resume from checkpoint

**Estimated Effort:** 5-6 hours

---

## Documentation Needs

### 21. User Guide

Write comprehensive user documentation:
- Getting started with native notes
- Migrating from Obsidian
- Scribe persona workflow
- Wiki-linking best practices
- Folder structure recommendations
- Tag conventions
- Troubleshooting common issues

**Estimated Effort:** 4-5 hours

---

### 22. API Documentation

Document notes-related API endpoints:
- `/polly/notes/*` endpoints
- Request/response schemas
- Error codes
- Rate limits
- Examples with curl

**Estimated Effort:** 2-3 hours

---

## Known Issues to Fix

### Issue 1: File Watcher on Network Drives

**Problem:** Watchdog may not work reliably on network-mounted drives

**Solution:** Detect network drives and fall back to polling mode

---

### Issue 2: BM25 Index Error with <5 Notes

**Problem:** `ZeroDivisionError` when too few notes for BM25

**Solution:** Add minimum note count check before BM25 indexing

---

### Issue 3: Special Characters in Filenames

**Problem:** Some special characters may cause issues in URLs or file paths

**Solution:** Sanitize filenames on creation, URL-encode when necessary

---

### Issue 4: Obsidian Auto-Connect on Settings Page Load

**Problem:** Opening Settings → Notes tab may trigger Obsidian connection check

**Solution:** Make integration status check lazy (only on user action)

---

## Architecture Considerations

### Future: Plugin System for Note Processors

Allow plugins to:
- Add custom note types
- Transform notes during indexing
- Add custom metadata extractors
- Implement custom search algorithms

---

### Future: Cloud Sync Option

Sync `~/.polly/notes/` to cloud storage:
- Dropbox
- Google Drive
- iCloud
- S3-compatible services

---

## Prioritization Guidelines

When resuming work on notes system:

1. **User-facing bugs** → Fix immediately
2. **Core functionality gaps** (like full RAG indexing) → High priority
3. **UX polish** (status indicators, progress feedback) → Medium priority
4. **Advanced features** (versioning, graph view) → Low priority
5. **Documentation** → Ongoing, parallel to feature work

---

## Quick Wins (< 2 hours each)

If you have a short session and want to make progress:

1. ✅ Add "Re-index All Notes" button
2. ✅ Reduce debug logging verbosity  
3. ✅ Fix BM25 error with small datasets
4. ✅ Add daily note creation shortcut
5. ✅ Show note count in Notes Browser header
6. ✅ Add "Last modified" sort option
7. ✅ Add keyboard shortcut for new note (Cmd+N)

---

## Metrics to Track

Once polished, track these metrics to measure success:

- Notes created per day/week
- Migration completion rate (% of users who complete migration)
- File watcher uptime / crash rate
- Average time to index new note
- Search query response time
- User retention (% returning to Notes feature)

---

## Related Documentation

- [PHASE16_COMPLETE.md](PHASE16_COMPLETE.md) - Original native notes implementation
- [NATIVE_NOTES_GUIDE.md](NATIVE_NOTES_GUIDE.md) - User guide for native notes
- [PHASE16C_AI_NOTE_CREATION.md](PHASE16C_AI_NOTE_CREATION.md) - Scribe persona specs
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - Overall system status

---

## Contact

When resuming work on this system, first:

1. ✅ Read this document thoroughly
2. ✅ Check server logs: `tail -f /tmp/polly-server.log`
3. ✅ Verify file watcher status: `curl -s http://localhost:11436/polly/stats | jq '.rag.notes'`
4. ✅ Test basic operations (create/edit/delete note)
5. ✅ Review any new user feedback or bug reports

---

**Last Updated:** January 31, 2026  
**Next Review:** When ready to resume notes system work
