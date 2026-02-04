# Phase 16 Planning Session - Complete Summary

**Date:** January 26, 2026  
**Status:** ✅ Planning Complete - Ready for Implementation  
**Timeline:** 5-5.5 weeks (was 3-4 weeks in original spec)

---

## What We Accomplished

We transformed the Phase 16 Native Notes specification from a basic editor implementation into a **production-ready Obsidian migration system** by:

1. **Identified 5 Critical Architectural Gaps** not addressed in original spec
2. **Designed comprehensive migration wizard** with validation and compatibility checks
3. **Mapped all Obsidian features** (15 features across 3 categories)
4. **Created Note Source Management system** to prevent RAG duplication
5. **Defined conversion strategies** for Dataview queries and other incompatible features
6. **Added auto-sync capabilities** via file watcher for RAG updates
7. **Addressed 3 additional architectural issues** (search clarity, domain tracking, attachments)

---

## Documents Created

### 1. `PHASE16_MIGRATION_ANALYSIS.md` (1,268 lines)

**Comprehensive analysis document** - Read this first for full context

Contains:
- Obsidian Feature Compatibility Matrix (Categories A, B, C)
- 5 Critical Architectural Gaps with solutions
- Note Source Management system design
- Enhanced 7-step migration wizard (was 5 steps)
- RAG file watcher implementation
- Missing Obsidian features (embeds, heading links, aliases, callouts)
- 3 Additional architectural issues
- Updated timeline breakdown
- Risk mitigation strategies
- Future enhancements roadmap

### 2. `PHASE16_IMPLEMENTATION_UPDATES.md` (459 lines)

**Quick reference checklist** - Use this during implementation

Contains:
- Timeline comparison table (original vs updated)
- Phase 16a additions (6 items)
- Phase 16b additions (4 items)
- File-by-file modification checklist
- Testing requirements
- Success metrics

### 3. `MASTER_ROADMAP.md` (modified)

**Updated with future enhancements:**
- Added "Notes System Enhancements" section (line ~1622)
- Multi-source notes (v2)
- LaTeX math rendering (v2)
- Mermaid diagrams (v2)
- Advanced query system (v2)

---

## Critical Architectural Decisions

### 1. Single Note Source for v1
- **Decision:** Only ONE note source active at a time (Obsidian OR native, not both)
- **Why:** Prevents RAG duplicate content, simpler implementation
- **Impact:** Multi-source deferred to v2
- **Config:** `~/.polly/config.yaml` → `notes.source: 'obsidian' | 'native'`

### 2. RAG Collection Rename
- **Decision:** Rename `'obsidian'` collection to `'notes'`
- **Why:** Generic name works for any note source
- **Impact:** Existing Obsidian users need one-time re-index
- **File:** `core/rag.py` line 343-360

### 3. Folder = Domain Source of Truth
- **Decision:** Folder location determines domain, frontmatter auto-corrects
- **Why:** Prevents sync issues between folder and frontmatter
- **Impact:** Non-blocking notification on auto-correction
- **Behavior:** Save validates folder matches frontmatter, repairs if needed

### 4. Centralized Attachments Directory
- **Decision:** `~/.polly/notes/_Attachments/{images,files}/`
- **Why:** Prevents duplication, easy backup, clear structure
- **Impact:** Migration rewrites image paths
- **Example:** `![](old/path.png)` → `![](../_Attachments/images/path.png)`

### 5. Dataview Conversion Strategy
- **Decision:** Hybrid approach - user chooses per query
- **Options:** Static content, search link, or remove
- **Why:** Flexible, prevents broken syntax, covers all use cases
- **File:** `core/dataview_converter.py`

### 6. File Watcher for RAG Sync
- **Decision:** Automatic indexing with 2s debounce
- **Why:** Users shouldn't need to manually trigger re-index
- **Tech:** chokidar library watching `~/.polly/notes/`
- **File:** `core/notes_file_watcher.py` or `.ts`

---

## Timeline Breakdown

### Original Estimate: 3-4 weeks
- Phase 16a: 2 weeks (Monaco editor, migration, preview)
- Phase 16b: 1-2 weeks (Wiki-links, backlinks, tags, templates)

### Updated Estimate: 5-5.5 weeks

**Phase 16a: 2.7 weeks (13.5 days)**
- Week 1: Monaco editor + Note Source Management (+2 days)
- Week 2: Migration wizard + Validation + Dataview (+2 days)
- Week 3: Live preview + File watcher + Domain tracking (+1.5 days)

**Phase 16b: 2.5 weeks (12.5 days)**
- Week 1: Wiki-links + Embeds + Heading links + Aliases (+2.5 days)
- Week 2: Backlinks + Tags + Quick switcher
- Week 3: Frontmatter + Templates + Callouts (+1 day)

**Additions:**
- Note Source Management: +2 days
- Migration validation & Dataview: +2 days
- File watcher: +1 day
- Domain tracking: +0.5 days
- Attachments: +0.5 days
- Embeds + Heading links + Aliases: +2.5 days
- Callouts: +1 day
- **Total added: +9.5 days ≈ +2 weeks**

---

## Implementation Checklist

### Phase 16a: Core Infrastructure

**Week 1: Monaco Editor + Note Source Management**
- [ ] Integrate Monaco editor (Days 1-3)
- [ ] Create `core/notes_source_manager.py` (Day 4)
- [ ] Modify `core/rag.py` - rename collection to `'notes'` (Day 4)
- [ ] Add `/polly/notes/source` API endpoints (Day 5)
- [ ] Add `notes:` section to config.yaml (Day 5)

**Week 2: Migration Wizard + Validation**
- [ ] Build migration wizard UI (Days 1-2)
- [ ] Add `validateVault()` to `integrations/obsidian.py` (Day 3)
- [ ] Insert "Compatibility Check" wizard step (Day 3)
- [ ] Create `core/dataview_converter.py` (Day 4)
- [ ] Add "Dataview Conversion" wizard step (Day 4)
- [ ] Implement attachments copying + link rewriting (Days 4-5)
- [ ] Create `~/.polly/notes/_Attachments/` directories (Day 5)

**Week 3: Live Preview + File Watcher**
- [ ] Implement live preview with marked.js (Days 1-2)
- [ ] Add domain tracking validation on save (Day 3)
- [ ] Create file watcher (chokidar) (Days 4-5)
- [ ] Integrate RAG auto-indexing with 2s debounce (Day 5)

### Phase 16b: Obsidian Feature Parity

**Week 1: Wiki-links + Advanced Linking**
- [ ] Implement basic wiki-links `[[Note Name]]` (Days 1-2)
- [ ] Add note embeds `![[Note Name]]` (Day 3)
- [ ] Add heading links `[[Note#Section]]` (Day 4)
- [ ] Implement aliases in frontmatter + autocomplete (Day 5)

**Week 2: Discovery Features**
- [ ] Build backlinks panel (Days 1-2)
- [ ] Implement tags system (Days 3-4)
- [ ] Create Quick Switcher (Cmd+O) (Day 5)

**Week 3: Metadata + Templates**
- [ ] Frontmatter editor UI (Days 1-2)
- [ ] Templates system (Days 3-4)
- [ ] Callouts rendering (marked.js extension) (Day 5)

---

## Files to Create (New)

**Python Backend:**
1. `core/notes_source_manager.py` - Source switching logic
2. `core/dataview_converter.py` - Query detection/conversion
3. `core/notes_file_watcher.py` - File watcher (if Python implementation)

**TypeScript Frontend (electron-app):**
1. `electron-app/src/notes_file_watcher.ts` - File watcher (if TS implementation)
2. Migration wizard components (UI)

**Config:**
1. Add `notes:` section to `~/.polly/config.yaml`

**Directories:**
1. `~/.polly/notes/_Attachments/images/`
2. `~/.polly/notes/_Attachments/files/`

---

## Files to Modify (Existing)

**Python Backend:**
1. `core/rag.py` (line 343-360) - Rename `'obsidian'` → `'notes'`
2. `interfaces/server.py` - Add `/polly/notes/source` endpoints
3. `integrations/obsidian.py` - Add `validateVault()`, attachments handling

**TypeScript Frontend:**
1. Monaco editor integration - Add embeds, heading links, callouts
2. Wiki-link handler - Parse `[[Note#Section]]` syntax
3. Note save logic - Add domain validation
4. Preview renderer - Process embeds before wiki-links
5. Frontmatter parser - Support aliases
6. Quick switcher - Include aliases in search
7. marked.js - Add callouts extension

---

## Search Architecture (3 Types)

### 1. Quick Switcher (Cmd+O)
- **Tech:** In-memory fuzzy filename match (fuse.js)
- **Speed:** < 50ms
- **Scope:** Filenames only (not content)
- **Use case:** Fast note navigation

### 2. Notes Search
- **Tech:** RAG semantic search in `'notes'` collection
- **Speed:** < 500ms
- **Scope:** Note content + titles
- **Use case:** Find notes by meaning/context

### 3. Global Search (Future v2)
- **Tech:** RAG search across all collections
- **Speed:** < 1s
- **Scope:** Notes + conversations + documents
- **Use case:** Cross-domain semantic search

---

## Feature Compatibility Matrix (Summary)

### Category A: Works Out of Box (6 features)
✅ Standard Markdown, Code Blocks, Task Lists, Images, Tables, Standard Links

### Category B: Special Handling Required (9 features)
**Included in Phase 16b:**
1. ✅ Wiki-links `[[Note Name]]`
2. ✅ Note embeds `![[Note Name]]`
3. ✅ Heading links `[[Note#Section]]`
4. ✅ Aliases (frontmatter `aliases: [...]`)
5. ✅ Backlinks panel
6. ✅ Tags `#tag` or `tags: [...]`
7. ✅ Frontmatter editing
8. ✅ Templates
9. ✅ Callouts `> [!note]`

### Category C: Documented Limitations for v1 (3 features)
⏸️ Math notation (LaTeX/KaTeX) - defer to v2
⏸️ Mermaid diagrams - defer to v2
⏸️ Canvas files - not supported, warned during migration

### Special Case: Dataview Queries (7 features)
🔄 Converted during migration (3 options: static/search link/remove)

---

## Migration Wizard (7 Steps)

Enhanced from original 5 steps:

1. **Welcome & Source Selection**
   - Choose Obsidian vault or folder
   - Explain one-time import

2. **Compatibility Check** ⭐ NEW
   - Scan vault for incompatibilities
   - Warn about Canvas, math, Mermaid
   - Show feature counts

3. **Import Preview**
   - Show files to be imported
   - Display folder structure
   - Confirm selection

4. **Domain Mapping**
   - Map folders → domains
   - Auto-suggest based on names
   - Allow manual override

5. **Dataview Conversion** ⭐ NEW (conditional)
   - Only shown if queries detected
   - Choose conversion per query
   - Preview converted output

6. **Import Progress**
   - Copy files with progress bar
   - Rewrite attachment links
   - Show current file being processed

7. **Completion & Next Steps**
   - Show import summary
   - Trigger RAG indexing
   - Guide to next steps

---

## Testing Requirements

### Unit Tests
- [ ] Note Source Manager - switch sources, config validation
- [ ] Dataview Converter - all 7 query types detected, 3 conversions work
- [ ] Domain Validator - folder/frontmatter sync, auto-repair
- [ ] File Watcher - debounce works, handles rapid changes
- [ ] Wiki-link Parser - basic, embeds, heading links, aliases
- [ ] Callouts Extension - all 6 types render correctly

### Integration Tests
- [ ] End-to-end migration - 100 note vault imports successfully
- [ ] RAG collection rename - existing users can re-index
- [ ] File watcher + RAG - changes reflected in search within 3s
- [ ] Attachments - images display correctly after migration
- [ ] Search types - Quick Switcher vs RAG search work independently

### Performance Tests
- [ ] Quick Switcher < 50ms for 1000 notes
- [ ] Notes Search < 500ms for typical query
- [ ] File watcher handles 10 rapid edits without overwhelming RAG
- [ ] Migration imports 1000 notes in < 2 minutes

---

## Success Metrics

### Migration Success
- [ ] 95%+ of notes import without errors
- [ ] All attachments maintain working links
- [ ] No RAG duplicate content detected
- [ ] Users understand incompatibilities before import

### Feature Parity
- [ ] All 9 Category B features work correctly
- [ ] Wiki-links resolve 99%+ of the time
- [ ] Backlinks panel shows all references
- [ ] Tags autocomplete and filter work

### Performance
- [ ] Quick Switcher feels instant (< 50ms)
- [ ] Search results appear quickly (< 500ms)
- [ ] No lag when editing notes
- [ ] File watcher doesn't impact system performance

### User Experience
- [ ] Migration wizard feels guided and safe
- [ ] Compatibility warnings prevent surprises
- [ ] Domain mapping feels intuitive
- [ ] Notes look visually similar to Obsidian

---

## Risk Mitigation

### Risk: Data Loss During Migration
**Mitigation:** Never modify original Obsidian vault, only copy

### Risk: RAG Duplication
**Mitigation:** Single source enforcement, clear config, migration clears old collection

### Risk: Broken Links After Migration
**Mitigation:** Attachment path rewriting, validation before import

### Risk: Performance Issues with Large Vaults
**Mitigation:** Progress indicators, async processing, debounced file watcher

### Risk: User Confusion About Missing Features
**Mitigation:** Compatibility check step, clear documentation of v1 limitations

---

## Deferred to Future (Post-v1)

### Multi-Source Notes (v2)
- Obsidian + native simultaneously
- Source priority for duplicates
- Per-collection RAG search

### LaTeX Math Rendering (v2)
- KaTeX library integration
- Inline `$...$` and block `$$...$$`
- Editor preview support

### Mermaid Diagrams (v2)
- Mermaid.js library
- Flowcharts, sequence diagrams, etc.
- Live preview rendering

### Advanced Query System (v2)
- Polly-native query language
- Live-updating query results
- Similar to Dataview but native

### Canvas Support (v3+)
- Infinite canvas for visual thinking
- Complex feature, significant effort
- Low priority vs other features

---

## Open Questions for Implementation

### 1. File Watcher Implementation Language
**Question:** Python or TypeScript for file watcher?

**Options:**
- Python (`watchdog` library) - Backend process
- TypeScript (`chokidar`) - Frontend process

**Recommendation:** TypeScript - frontend already manages Monaco, easier to coordinate

### 2. RAG Indexing on File Change
**Question:** Should file watcher call RAG directly or queue changes?

**Options:**
- Direct call - simpler, immediate
- Queue with batch processing - more efficient for rapid changes

**Recommendation:** Direct call with debounce (2s) - handles 95% of use cases

### 3. Dataview Default Conversion
**Question:** What's the default conversion option if user skips step?

**Options:**
- Static content (safest)
- Search link (preserves intent)
- Remove (cleanest)

**Recommendation:** Static content - preserves information, no broken syntax

### 4. Compatibility Check Blocking
**Question:** Should migration block if critical issues found?

**Options:**
- Block entirely (safest)
- Warn but allow (flexible)
- Auto-fix issues (complex)

**Recommendation:** Warn but allow - users can make informed decision

---

## Next Steps

### Before Implementation Begins:
1. ✅ Review planning documents (this file, PHASE16_MIGRATION_ANALYSIS.md)
2. ✅ Confirm architectural decisions with team/stakeholders
3. ✅ Verify timeline is acceptable (5-5.5 weeks)
4. ✅ Ensure all open questions are answered

### When Ready to Start:
1. Create feature branch `feature/phase-16-native-notes`
2. Begin with Phase 16a Week 1 (Monaco editor + Note Source Management)
3. Use `PHASE16_IMPLEMENTATION_UPDATES.md` as implementation checklist
4. Mark off items as completed
5. Run tests incrementally (don't batch at end)

### During Implementation:
- Reference `PHASE16_MIGRATION_ANALYSIS.md` for detailed context
- Update timeline if estimates were off
- Document any new issues discovered
- Keep test coverage high (aim for 80%+)

---

## Document Status

| Document | Lines | Status | Purpose |
|----------|-------|--------|---------|
| `PHASE16_NATIVE_NOTES.md` | 2,109 | Original spec (unmodified) | Original requirements |
| `PHASE16_MIGRATION_ANALYSIS.md` | 1,268 | ✅ Complete | Comprehensive analysis |
| `PHASE16_IMPLEMENTATION_UPDATES.md` | 459 | ✅ Complete | Implementation checklist |
| `PHASE16_PLANNING_COMPLETE.md` | This file | ✅ Complete | Executive summary |
| `MASTER_ROADMAP.md` | Updated | ✅ Complete | Future enhancements |

**Total planning output:** ~4,000 lines of analysis and documentation

---

## Summary

This planning session identified **critical architectural gaps** that would have caused:
- Duplicate content in RAG
- Broken features after migration
- Poor user experience
- Technical debt

By addressing these issues upfront, we've created a **production-ready implementation plan** that:
- Safely migrates Obsidian users
- Preserves all critical features
- Provides clear upgrade path
- Establishes solid foundation for v2 enhancements

**Timeline impact:** +1.5-2.5 weeks is acceptable given the quality improvements and risk mitigation.

**Ready for implementation:** Yes ✅

---

*Planning completed: January 26, 2026*  
*Next session: Begin Phase 16a implementation*
