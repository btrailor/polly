# Phase 16: Implementation Updates Summary

**Date:** January 26, 2026  
**Related:** PHASE16_NATIVE_NOTES.md, PHASE16_MIGRATION_ANALYSIS.md  
**Impact:** Timeline increases from 3-4 weeks to **5-5.5 weeks**

---

## Quick Reference

This document summarizes what needs to be **added** to the existing Phase 16 specification based on architectural analysis and Obsidian feature preservation requirements.

**Full analysis:** See `PHASE16_MIGRATION_ANALYSIS.md` for detailed rationale and code examples.

---

## Timeline Changes

| Phase | Original | Updated | Change | Reason |
|-------|----------|---------|--------|--------|
| Phase 16a | 2 weeks | 2.7 weeks | +3 days | Note Source Mgmt + File Watcher + Validation + Domain Tracking + Attachments |
| Phase 16b | 1-2 weeks | 2.5 weeks | +3.5 days | Embeds + Heading Links + Aliases + Callouts |
| **Total** | **3-4 weeks** | **5-5.5 weeks** | **+1.5-2.5 weeks** | Production-ready migration |

---

## Phase 16a Additions

### 1. Note Source Management System ⭐ CRITICAL

**What:** System to manage switching between Obsidian and native notes

**Why:** Original spec doesn't address how Obsidian integration and native notes coexist

**When:** Week 1, Days 4-5 (+2 days)

**Files to create:**
- `core/notes_source_manager.py` - Source switching logic
- Add `notes:` section to `~/.polly/config.yaml`

**Files to modify:**
- `core/rag.py` (line 343-360) - Rename `'obsidian'` collection to `'notes'`
- `interfaces/server.py` - Add `/polly/notes/source` endpoints

**Key decision:** Single source for v1 (either Obsidian OR native, not both). Multi-source deferred to future.

### 2. Migration Compatibility Validation

**What:** Scan vault before import, detect incompatibilities (Canvas files, Dataview queries, math notation)

**Why:** Prevent broken imports, set user expectations

**When:** Week 2, Day 3 (+1 day)

**Files to modify:**
- `integrations/obsidian.py` - Add `validateVault()` method

**New wizard step:** Insert "Compatibility Check" between Import Preview and Domain Mapping

### 3. Dataview Query Conversion

**What:** Detect Dataview queries, offer conversion options (static/search link/remove)

**Why:** Dataview queries won't execute in Polly v1

**When:** Week 2, Day 4 (+1 day)

**Files to create:**
- `core/dataview_converter.py` - Query detection and conversion

**New wizard step:** "Dataview Conversion" shown only if queries detected

### 4. RAG File Watcher

**What:** Automatically detect file changes and update RAG collection

**Why:** Without this, users must manually trigger re-indexing

**When:** Week 3, Days 4-5 (+1 day)

**Files to create:**
- `core/notes_file_watcher.py` or `electron-app/src/notes_file_watcher.ts`

**Dependencies:** `chokidar` package for file watching

### 5. Domain Tracking Validation

**What:** Auto-repair frontmatter domain to match folder location (folder = source of truth)

**Why:** Prevent sync issues between folder location and frontmatter

**When:** Week 3, Day 3 (+0.5 days)

**Files to modify:**
- Note save logic - Add validation that checks folder vs frontmatter domain
- Show non-blocking notification if mismatch detected and corrected

**Key decision:** Folder location is always source of truth, frontmatter auto-corrects on save

### 6. Attachments Handling

**What:** Centralized attachments directory structure with path rewriting during migration

**Why:** Prevent duplication, maintain working image links after migration

**When:** Week 2, Days 4-5 (+0.5 days, overlaps with migration)

**Files to modify:**
- `integrations/obsidian.py` - Add attachment copying and link rewriting
- Create `~/.polly/notes/_Attachments/{images,files}/` directory structure

**Migration behavior:** Rewrite `![](old/path.png)` → `![](../_Attachments/images/path.png)`

---

## Phase 16b Additions

### 1. Note Embeds (`![[Note Name]]`)

**What:** Render embedded note content inline in preview

**Why:** Core Obsidian feature, users rely on it

**When:** Week 1, Day 3 (+1 day)

**Files to modify:**
- Monaco preview renderer - Add `processEmbeds()` method before `processWikiLinks()`

**Edge case:** Circular embeds (A embeds B, B embeds A) - Max depth = 3

### 2. Heading Links (`[[Note#Section]]`)

**What:** Support linking to specific sections within notes

**Why:** Common Obsidian pattern for cross-referencing

**When:** Week 1, Day 4 (+0.5 days, overlaps with wiki-links)

**Files to modify:**
- `WikiLinkHandler.processWikiLinks()` - Parse `#` syntax, generate anchors

**Implementation:** Split link text on `#`, slugify heading for anchor

### 3. Aliases (Frontmatter)

**What:** Allow notes to be referenced by multiple names

**Why:** Improves discoverability, prevents broken links when renaming

**When:** Week 1, Day 5 (+1 day)

**Files to modify:**
- Note index structure - Add `aliases: string[]` field
- `findNoteByName()` - Check aliases after checking name
- Autocomplete provider - Suggest aliases

**Example:**
```yaml
---
aliases: [FP, functional-style]
---
```

### 4. Callouts (Custom Rendering)

**What:** Render Obsidian callouts with custom styling

**Why:** Visual parity with Obsidian, commonly used feature

**When:** Week 3, Day 5 (+1 day)

**Files to modify:**
- Monaco preview - Add `marked.js` extension for callout syntax

**Syntax:** `> [!note] Title`

**Types:** note, tip, warning, important, question, success, failure, danger, bug

---

## Config File Changes

### `~/.polly/config.yaml`

**Add new section:**

```yaml
notes:
  source: "native"  # Options: "obsidian" or "native"
  obsidian:
    vault_path: "~/Documents/Obsidian/MyVault"
    enabled: false
  native:
    path: "~/.polly/notes"
    enabled: true
```

---

## RAG Collection Changes

### `core/rag.py` (Line 343-360)

**BEFORE:**
```python
self.collections = {
    'obsidian': self.client.get_or_create_collection(
        name="obsidian_vault",
        ...
    ),
    ...
}
```

**AFTER:**
```python
self.collections = {
    'notes': self.client.get_or_create_collection(  # ← RENAMED
        name="notes",  # ← Generic name
        ...
    ),
    ...
}
```

**Why:** Generic name allows switching between Obsidian and native sources without collection conflict.

---

## Migration Wizard Updates

### Current Flow (5 steps)
1. Detect Vault
2. Import Preview
3. Domain Mapping
4. Import Progress
5. Import Summary

### Updated Flow (7 steps)
1. Detect Vault
2. Import Preview
3. **Compatibility Check** ⭐ NEW
4. **Dataview Conversion** ⭐ NEW (conditional)
5. Domain Mapping
6. Import Progress (updated with conversion status)
7. Import Summary (updated with skipped files info)

---

## New NPM Dependencies

Add to `electron-app/package.json`:

```json
{
  "dependencies": {
    "chokidar": "^3.5.3"  // File watcher
  }
}
```

---

## Testing Requirements

### Phase 16a Testing

1. **Note Source Management**
   - Switch from Obsidian to native (verify RAG clears and re-indexes)
   - Switch from native to Obsidian (verify RAG clears and re-indexes)
   - Config persists between app restarts

2. **Migration Validation**
   - Vault with Canvas files → warns user, skips files
   - Vault with Dataview queries → shows conversion step
   - Vault with math notation → warns user in compatibility check

3. **File Watcher**
   - Create new note → auto-indexes within 5s
   - Edit existing note → re-indexes within 5s
   - Delete note → removes from RAG within 5s
   - Performance: < 5% CPU when idle

### Phase 16b Testing

4. **Note Embeds**
   - `![[Note]]` renders full note content
   - `![[Note|Section]]` renders specific section
   - Missing note shows error placeholder
   - Circular embeds stop at depth 3

5. **Heading Links**
   - `[[Note#Section]]` navigates to section
   - Slugify handles special characters
   - Missing heading scrolls to top of note

6. **Aliases**
   - Autocomplete suggests aliases
   - `[[Alias]]` resolves to correct note
   - Backlinks work with aliases

7. **Callouts**
   - All callout types render correctly
   - Icons match Obsidian
   - Nested content (lists, code) renders

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Migration speed | 500+ notes in < 2 min | Test with large vault |
| File watcher latency | Index change within 5s | Monitor logs during edits |
| Search performance | 1000+ notes, results < 500ms | Performance profiler |
| CPU usage (idle) | < 5% | Activity Monitor |
| Memory usage | < 200MB for 1000 notes | Activity Monitor |
| Zero data loss | 100% notes preserved | Diff before/after |

---

## Documentation Updates Needed

### 1. Update PHASE16_NATIVE_NOTES.md

**Sections to add/update:**

- **Overview**: Update "One-time migration" principle to explain source management
- **Phase 16a, Week 1**: Add Days 4-5 (Note Source Management)
- **Phase 16a, Week 2**: Add Day 3 (Compatibility Check), Day 4 (Dataview Conversion)
- **Phase 16a, Week 3**: Add Days 4-5 (File Watcher)
- **Phase 16b, Week 1**: Add Days 3-5 (Embeds, Heading Links, Aliases)
- **Phase 16b, Week 3**: Add Day 5 (Callouts)
- **Timeline**: Update from 3-4 weeks to 5 weeks

### 2. Create User Documentation

When Phase 16 ships, create:

- **Migration Guide**: Step-by-step Obsidian → Polly migration
- **Feature Compatibility Matrix**: What works, what doesn't, workarounds
- **Dataview Conversion Guide**: How to convert Dataview queries to Polly alternatives
- **Config Reference**: `notes:` section options

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File watcher impacts performance | Medium | High | Debounce, batch operations, < 5% CPU target |
| Large vaults timeout during import | Low | High | Stream progress, chunked imports, cancel/resume |
| Dataview conversion inaccurate | Medium | Medium | Preview before commit, allow manual edit |
| Circular embeds cause infinite loop | Low | High | Max depth = 3, detect cycles |
| RAG re-index blocks app | Low | Medium | Background operation, show progress |

---

## Open Questions for Implementation

1. **Attachment directory structure:** Where to store images/files in native notes?
   - Suggested: `~/.polly/notes/_Attachments/{images,files}/`

2. **Dataview static conversion:** How to execute Dataview queries during migration?
   - Option A: Parse query, build results manually
   - Option B: Skip static conversion, only offer search links
   - **Recommendation:** Option B for v1 (simpler)

3. **File watcher error handling:** What if RAG indexing fails?
   - Retry 3 times, log error, show notification
   - Don't block file operations

4. **Callout types:** Support all Obsidian types or subset?
   - **Recommendation:** Support all types (simple icon mapping)

---

## Integration Points

### With Phase 1.5 (Domain Configuration)
- Domain folders used for native notes storage
- Domain selection in migration wizard

### With Phase 2 (RAG)
- RAG collection renaming (`'obsidian'` → `'notes'`)
- File watcher triggers RAG re-indexing

### With Phase 11 (Draft Notes)
- Draft notes stored in `_Drafts` folder
- Appear in notes tree view

### With Phase 12 (Knowledge Graph)
- Graph nodes link to note editor
- Wiki-links create graph edges

---

## Future Considerations (Post-v1)

### Multi-Source Notes (v1.1+)

Allow multiple note sources simultaneously:

```yaml
notes:
  sources:
    - type: native
      path: ~/.polly/notes
      enabled: true
    - type: obsidian
      vault_path: ~/Documents/Obsidian/Personal
      enabled: true
```

**Complexity:** Medium (3-5 days)  
**Dependencies:** RAG collection prefixing, UI toggle for sources

### LaTeX Math Rendering (v1.2+)

Add KaTeX integration for math notation.

**Complexity:** Low (1-2 days)  
**Dependencies:** `katex` npm package

### Mermaid Diagrams (v1.2+)

Add mermaid.js integration for diagrams.

**Complexity:** Low (1-2 days)  
**Dependencies:** `mermaid` npm package

### Advanced Query System (v2.0+)

Build Dataview-like query system for Polly.

**Complexity:** High (1-2 weeks)  
**Dependencies:** Query language parser, live result rendering

---

## Summary

**What changed:** Added 4 major features to Phase 16a/16b based on architectural analysis

**Why:** Ensure production-ready Obsidian migration with feature preservation

**Time impact:** +1-2 weeks (3-4 weeks → 5 weeks)

**Files affected:** 8 new files, 4 modified files, 1 config update

**Next steps:** 
1. Review this document
2. Update PHASE16_NATIVE_NOTES.md with additions
3. Begin implementation in order: 16a Week 1 → 16a Week 2 → 16a Week 3 → 16b

---

**Document Status:** ✅ Complete  
**Ready for:** Implementation planning and spec updates
