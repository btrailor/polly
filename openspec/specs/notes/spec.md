# Notes (OpenSpec)

Source of truth for native notes, TOC, and templates (Phases 16, 16e). Detail: [docs/planning/phases/phase-16/](../../../docs/planning/phases/phase-16/), [docs/planning/phases/phase-16e/](../../../docs/planning/phases/phase-16e/).

## Native Notes (Phase 16)

- **Storage:** Vault (e.g. Obsidian-compatible or `~/.polly/notes/`). File tree, create/edit/rename/delete.
- **Editor:** Monaco-style markdown; view/edit modes. Wiki-links `[[Note Name]]` with navigation and auto-update on rename.
- **Features:** Backlinks panel, tags, quick switcher (Cmd+O), drag-and-drop organization, auto-save. Domain-based folder organization; RAG indexing with file watcher.

### Auto-save and change detection

- **Trigger:** Content changes in the editor (CodeMirror 6 or fallback) schedule a debounced save after a short idle delay (default 2s).
- **Change detection:** Before performing the save, the client compares the current editor content to the last successfully saved content (normalized for comparison). If they are equal, no PUT is sent: the timeout is cleared, the UI is updated to "Saved", and the operation ends. This avoids redundant writes when the user types then undoes, or when content is unchanged for other reasons.
- **Normalization:** For comparison only, line endings are normalized (`\r\n` and `\r` → `\n`). No trimming of trailing newlines, so changes to line endings are still treated as real changes.
- **State:** `lastSavedContent` is set when a note is opened (from the loaded file content) and after each successful save. It is not trimmed or otherwise altered beyond line-ending normalization.
- **Implementation:** `electron-app/src/renderer/notes-manager.js` — `lastSavedContent`, `_normalizeContentForCompare()`, and the early-return in `saveCurrentNote()` when content is unchanged.

- **Deduplication (Phase 21):** Similar-notes warning on create; append/link/create-anyway workflows. Being absorbed into broader Knowledge Quality Pipeline — see [knowledge-graph spec](../knowledge-graph/spec.md).

## TOC & Templates (Phase 16e)

- **TOC:** Collapsible table of contents in notes view; heading detection (H1–H6); click-to-navigate.
- **Templates:** Gallery and manager (create, edit, delete). Template variables. Storage: `vault/.polly/templates/`. Defaults: Meeting Notes, Project Plan, Daily Journal.

## AI Note Creation (Phase 16c)

- **Status:** Backend ready (personas, router, templates); frontend pending. Intent detection, Q&A UI, preview modal, save to `_Drafts/`.

## Knowledge Writing from Chat (Core Framework Refinement)

- **Status:** ✅ Implemented — full stack (backend, API, frontend)
- **Backend:** `core/knowledge_writer.py` — `KnowledgeWriter` class orchestrates all chat-to-KB writes. Gap detection (heuristic, no LLM), quick save (structured markdown), Scribe-assisted save (wiki-linking via `enrich_standalone()`), per-message save (context menu).
- **Common path:** All writes converge on `_save_note()` → dedup check → file write → incremental RAG index (`rag.index_single_document()`) → record metric.
- **API:** `POST /api/settings/knowledge/save-quick`, `save-scribe`, `save-message`
- **Frontend:** Right-click context menu on assistant messages → "Save to KB". `SaveMessageForm` component. AI suggestion rendering (`renderKnowledgeSuggestion()`).
- **Config:** `config.yaml` → `ai_features.knowledge_suggestions` (enabled, style, min_gap_score)
- **Settings UI:** AI Features section with toggles for knowledge suggestions and autonomy dashboard
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Planned Extensions

### Maturity Lifecycle

Notes gain maturity metadata (30-Ideas / 20-Active / 10-Archive) stored as frontmatter + SQLite index. Shared system with captures and canvases. See [capture spec](../capture/spec.md).

### Entity Extraction on Save

All note saves (new and edited) run through the Knowledge Quality Pipeline: entity extraction → similarity check → connection suggestion → authority update. See [knowledge-graph spec](../knowledge-graph/spec.md).

### Augmented Writing

During composition, sidebar shows related notes based on entity overlap in real-time. Prevents duplicates and encourages linking at the moment of creation.

### Version History

Edit history for all notes. Rollback to previous versions. Compare side-by-side. AI-generated content tracked with provenance metadata.

### Knowledge Cards

Structured note archetypes with required fields. A "conversation summary" card: date, participants, key decisions, extracted concepts. An "idea seed" card: core claim, supporting evidence, open questions. Templates enforce signal over noise.

## Reference

- [PHASE16_NATIVE_NOTES.md](../../../docs/planning/phases/phase-16/PHASE16_NATIVE_NOTES.md), [PHASE16_COMPLETE.md](../../../docs/planning/phases/phase-16/PHASE16_COMPLETE.md)
- [PHASE16E_COMPLETE.md](../../../docs/planning/phases/phase-16e/PHASE16E_COMPLETE.md), [PHASE16E_TOC_TEMPLATES.md](../../../docs/planning/phases/phase-16e/PHASE16E_TOC_TEMPLATES.md)
- [PHASE16C_AI_NOTE_CREATION.md](../../../docs/planning/phases/phase-16c/PHASE16C_AI_NOTE_CREATION.md)
- Knowledge quality: [knowledge-graph spec](../knowledge-graph/spec.md)
- Capture system: [capture spec](../capture/spec.md)