# Phase 16 Quick Reference Card

**Timeline:** 5-5.5 weeks | **Status:** ✅ Planning Complete | **Date:** Jan 26, 2026

---

## Documents to Read (In Order)

1. **`PHASE16_PLANNING_COMPLETE.md`** ← Start here
   - Executive summary of entire planning session
   - All key decisions and rationale
   - Complete checklist and timeline

2. **`PHASE16_MIGRATION_ANALYSIS.md`** ← Read for full context
   - Detailed analysis of all architectural gaps
   - Complete Obsidian feature compatibility matrix
   - Implementation details and code examples

3. **`PHASE16_IMPLEMENTATION_UPDATES.md`** ← Use during coding
   - File-by-file modification checklist
   - Quick reference for what changed vs original spec
   - Testing requirements

4. **`PHASE16_NATIVE_NOTES.md`** ← Original spec (reference only)
   - Original requirements (unmodified)
   - Still valid, but incomplete without analysis docs

---

## Critical Decisions (One-Liner Summary)

| Decision | Answer |
|----------|--------|
| **Note source strategy** | Single source only (Obsidian OR native) for v1 |
| **RAG collection name** | Rename `'obsidian'` → `'notes'` |
| **Domain source of truth** | Folder location (frontmatter auto-corrects) |
| **Attachments location** | `~/.polly/notes/_Attachments/{images,files}/` |
| **Dataview handling** | User chooses: static/search link/remove |
| **File sync** | Auto-index via chokidar file watcher (2s debounce) |
| **Category B features** | All 9 included in Phase 16b |
| **Math/Mermaid** | v1 limitation (defer to v2) |
| **Timeline** | 5-5.5 weeks (was 3-4 weeks) |

---

## What Changed vs Original Spec (+9.5 days)

### Phase 16a Additions (+3 days)
1. ✅ Note Source Management system (+2 days)
2. ✅ Migration compatibility validation (+1 day)
3. ✅ Dataview query conversion (+1 day, overlaps with migration)
4. ✅ RAG file watcher (+1 day)
5. ✅ Domain tracking validation (+0.5 days)
6. ✅ Attachments handling (+0.5 days, overlaps with migration)

### Phase 16b Additions (+3.5 days)
1. ✅ Note embeds `![[Note]]` (+1 day)
2. ✅ Heading links `[[Note#Section]]` (+0.5 days)
3. ✅ Aliases (frontmatter) (+1 day)
4. ✅ Callouts `> [!note]` (+1 day)

---

## New Files to Create (8 total)

### Python Backend (3 files)
```
core/notes_source_manager.py          # Source switching logic
core/dataview_converter.py            # Dataview query detection/conversion
core/notes_file_watcher.py            # File watcher (if Python impl)
```

### TypeScript Frontend (2 files)
```
electron-app/src/notes_file_watcher.ts    # File watcher (if TS impl)
electron-app/src/components/MigrationWizard.tsx  # UI components
```

### Config (1 file)
```
~/.polly/config.yaml                   # Add 'notes:' section
```

### Directories (2 directories)
```
~/.polly/notes/_Attachments/images/
~/.polly/notes/_Attachments/files/
```

---

## Existing Files to Modify (7 files)

### Python Backend
```
core/rag.py (line 343-360)             # Rename 'obsidian' → 'notes'
interfaces/server.py                   # Add /polly/notes/source endpoints
integrations/obsidian.py               # Add validateVault(), attachments
```

### TypeScript Frontend
```
Monaco editor integration              # Embeds, heading links, callouts
Wiki-link handler                      # Parse [[Note#Section]] syntax
Note save logic                        # Domain validation
marked.js                              # Add callouts extension
```

---

## Migration Wizard (7 Steps)

| Step | New? | Purpose |
|------|------|---------|
| 1. Welcome & Source Selection | Original | Choose vault |
| 2. **Compatibility Check** | ⭐ NEW | Warn about limitations |
| 3. Import Preview | Original | Review files |
| 4. Domain Mapping | Original | Map folders → domains |
| 5. **Dataview Conversion** | ⭐ NEW | Convert queries (conditional) |
| 6. Import Progress | Enhanced | Copy + rewrite links |
| 7. Completion | Enhanced | RAG indexing |

---

## Search Types (3 Distinct)

| Type | Tech | Speed | Scope |
|------|------|-------|-------|
| **Quick Switcher** (Cmd+O) | In-memory fuzzy | < 50ms | Filenames only |
| **Notes Search** | RAG semantic | < 500ms | Note content |
| **Global Search** (v2) | RAG cross-collection | < 1s | All collections |

---

## Obsidian Features (27 total)

### ✅ Category A: Works Out of Box (6)
Standard Markdown, Code Blocks, Task Lists, Images, Tables, Standard Links

### ✅ Category B: Implemented (9)
Wiki-links, Embeds, Heading links, Aliases, Backlinks, Tags, Frontmatter, Templates, Callouts

### 🔄 Special: Converted (7 Dataview features)
Tables, Lists, Task queries, Calendar, Pages, File, Group

### ⏸️ Category C: v1 Limitations (3)
Math notation, Mermaid diagrams, Canvas files

### 📊 Future: v2+ (2)
Advanced queries, Graph view

---

## Timeline Breakdown

```
Phase 16a: 2.7 weeks (13.5 days)
├─ Week 1: Monaco + Note Source Mgmt
├─ Week 2: Migration + Validation + Dataview
└─ Week 3: Preview + File Watcher + Domain

Phase 16b: 2.5 weeks (12.5 days)
├─ Week 1: Wiki-links + Embeds + Heading + Aliases
├─ Week 2: Backlinks + Tags + Quick Switcher
└─ Week 3: Frontmatter + Templates + Callouts

Total: 5-5.5 weeks
```

---

## Implementation Order (By Week)

### Week 1: Foundation
- [ ] Monaco editor integration
- [ ] Create `notes_source_manager.py`
- [ ] Modify `core/rag.py` collection name
- [ ] Add `/polly/notes/source` API

### Week 2: Migration
- [ ] Build migration wizard UI
- [ ] Add `validateVault()` method
- [ ] Create `dataview_converter.py`
- [ ] Implement attachments handling

### Week 3: Polish Phase 16a
- [ ] Live preview with marked.js
- [ ] Domain validation on save
- [ ] File watcher (chokidar)
- [ ] RAG auto-indexing

### Week 4: Core Features
- [ ] Wiki-links `[[Note]]`
- [ ] Embeds `![[Note]]`
- [ ] Heading links `[[Note#Section]]`
- [ ] Aliases in frontmatter

### Week 5: Discovery
- [ ] Backlinks panel
- [ ] Tags system
- [ ] Quick Switcher (Cmd+O)

### Week 6: Final Features
- [ ] Frontmatter editor UI
- [ ] Templates system
- [ ] Callouts `> [!note]`

---

## Testing Checklist

### Unit Tests (7 components)
- [ ] Note Source Manager
- [ ] Dataview Converter (all 7 types)
- [ ] Domain Validator
- [ ] File Watcher (debounce)
- [ ] Wiki-link Parser (4 syntaxes)
- [ ] Callouts Extension (6 types)
- [ ] Attachments Path Rewriting

### Integration Tests (5 scenarios)
- [ ] End-to-end migration (100 notes)
- [ ] RAG collection rename
- [ ] File watcher → RAG sync
- [ ] Attachments display correctly
- [ ] Search types work independently

### Performance Tests (4 benchmarks)
- [ ] Quick Switcher < 50ms (1000 notes)
- [ ] RAG Search < 500ms
- [ ] File watcher handles 10 rapid edits
- [ ] Migration imports 1000 notes < 2 min

---

## Config Changes Required

Add to `~/.polly/config.yaml`:

```yaml
notes:
  source: 'native'  # or 'obsidian'
  directory: '~/.polly/notes'
  vault_path: null  # Set when source = 'obsidian'
  auto_index: true  # Enable file watcher
  domain_validation: true  # Auto-repair frontmatter
```

Modify in `core/rag.py`:

```python
# Line 343-360: Change collection name
collection_name = 'notes'  # was 'obsidian'
```

---

## Risk Mitigation Summary

| Risk | Mitigation |
|------|-----------|
| Data loss | Never modify original vault, only copy |
| RAG duplicates | Single source enforcement + clear config |
| Broken links | Attachment path rewriting + validation |
| Performance | Progress indicators + async + debounce |
| User confusion | Compatibility check + clear docs |

---

## Success Metrics

- ✅ 95%+ notes import without errors
- ✅ All attachments maintain working links
- ✅ No RAG duplicate content
- ✅ Quick Switcher < 50ms
- ✅ Search results < 500ms
- ✅ All 9 Category B features work
- ✅ Wiki-links resolve 99%+ of time

---

## When to Use Each Document

| Situation | Document |
|-----------|----------|
| Need exec summary | `PHASE16_PLANNING_COMPLETE.md` |
| Need full context | `PHASE16_MIGRATION_ANALYSIS.md` |
| Implementing code | `PHASE16_IMPLEMENTATION_UPDATES.md` |
| Quick lookup | `PHASE16_QUICK_REFERENCE.md` (this file) |
| Original requirements | `PHASE16_NATIVE_NOTES.md` |

---

## Open Questions (Answer Before Coding)

1. **File watcher:** Python or TypeScript? → **Recommend TypeScript**
2. **RAG indexing:** Direct call or queue? → **Recommend direct + debounce**
3. **Dataview default:** Static, link, or remove? → **Recommend static**
4. **Compatibility block:** Block or warn? → **Recommend warn**

---

## Deferred to v2+

- Multi-source notes (Obsidian + native simultaneously)
- LaTeX math rendering (KaTeX)
- Mermaid diagrams (mermaid.js)
- Advanced query system (Dataview replacement)
- Drag-and-drop attachments
- Canvas support (v3+)

---

**Ready to implement:** ✅ Yes  
**Planning complete:** January 26, 2026  
**Next action:** Begin Phase 16a Week 1

---

*For detailed information, see `PHASE16_PLANNING_COMPLETE.md`*
