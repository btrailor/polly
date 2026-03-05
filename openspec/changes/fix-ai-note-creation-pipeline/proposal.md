# Fix AI Note Creation Pipeline — Proposal

**Date**: 2026-03-04  
**Status**: ✅ Complete  
**Priority**: P1 — Critical workflow broken  
**Scope**: Backend + Frontend  
**Depends On**: None  
**Related Specs**: [notes spec](../../specs/notes/spec.md), [knowledge-graph spec](../../specs/knowledge-graph/spec.md)

---

## Problem Statement

When creating notes through the AI "Enrich with Scribe" feature in the conversation window, three critical issues prevent the workflow from being useful:

### Issue 1: Template Selection Not Triggered

When a note is created via the Scribe enrichment path, the template selection step is completely bypassed. The `scribe_save()` → `enrich_standalone()` pipeline jumps straight to enrichment without presenting the user with template options. Templates exist in `vault/.polly/templates/` and are loaded by `core/templates/manager.py`, but the `enrich_standalone()` method in `core/personas/implementations/scribe.py:570` builds a "simplified enrich prompt" that ignores templates entirely:

```python
# Build a simplified enrich prompt (no template required)
enrich_prompt = f"""You are Polly's Scribe..."""
```

The comment literally says "no template required" — this was an intentional shortcut during initial implementation that was never revisited.

**Impact**: Notes created via Scribe all have the same generic structure regardless of type. A "Meeting Notes" note should use the meeting template; a "Project Plan" should use the project template. Without template selection, users get unstructured markdown blobs.

### Issue 2: Notes Not Indexed into Knowledge Base

When a note is created through the AI conversation flow, it is not immediately indexed into the knowledge base. The `_save_note()` method in `knowledge_writer.py` attempts RAG indexing via `rag.index_single_document()`, but:

1. The note may not be indexed if the RAG instance is not properly initialized or available during the save
2. The notes index (used by the notes browser page) is separate from the RAG index and is not updated after AI note creation
3. Users navigate to the Notes page expecting to find their newly created note, but it doesn't appear until a full re-index or app restart

**Impact**: Users create notes via AI, believe they saved successfully (they see a success toast), then cannot find the note when browsing. This erodes trust in the system.

### Issue 3: Poor Note Naming

Notes created via AI are named using `_generate_title_from_content()` (knowledge_writer.py:856), which simply:

1. Looks for the first markdown heading
2. Falls back to the first sentence of content
3. Truncates to 60 characters

This produces titles like "Can you help me understand how..." or "I need information about the..." — these are the user's query phrasing, not descriptive knowledge titles. The titles are long, start with filler words, and don't reflect the actual topic.

**Impact**: The Notes page fills with poorly named notes that are hard to scan and identify. Users must open each note to understand its content.

---

## Goals

1. **Integrate template selection into the Scribe enrichment flow** — present template picker before enrichment, pass selected template to the enrichment prompt
2. **Ensure immediate indexing** — after AI note creation, update both the RAG index and the notes browse index so the note appears everywhere instantly
3. **Generate intelligent note titles** — use LLM to generate a concise, topic-focused title rather than truncating the first sentence
4. **Refine note templates** — audit existing templates for quality and add missing common types

---

## Non-Goals

- Redesigning the Scribe persona's broader capabilities
- Adding real-time collaborative editing during note creation
- Changing the note file format (Markdown + YAML frontmatter stays)
- Rebuilding the PreviewModal component

---

## Success Criteria

1. When creating a note via "Enrich with Scribe," a template picker appears with available templates + a "Blank" option
2. The selected template's structure, AI hints, and variables are passed to the Scribe enrichment prompt
3. After note creation via any AI path (quick save or Scribe), the note appears in the Notes browse page within 2 seconds without requiring refresh
4. Note titles are 3-7 words, topic-focused, and never start with "Can you," "I need," "Help me," or similar query phrasing
5. Template gallery shows at least 5 well-designed templates: Blank, Meeting Notes, Project Plan, Research Note, Concept Exploration, Daily Reflection

---

## User Stories

**As a user creating a note from a conversation**, I want to choose a template that fits my note type so the AI structures the content appropriately.

**As a user who just created a note via AI**, I want to immediately find that note in my Notes page so I know it was saved and can continue working on it.

**As a user browsing my notes**, I want titles that tell me what the note is about at a glance, not titles that repeat my original question.

---

## Technical Approach

### Phase 1: Template Selection in Scribe Flow

**Frontend (conversation panel / save dialog):**

- When user triggers "Enrich with Scribe" from conversation, show a template picker overlay/step before calling the Scribe API
- Fetch available templates from `GET /api/settings/templates` (exists or create)
- Display templates as selectable cards with icon, name, and description
- Include a "Blank" option (no template, current behavior)
- Pass selected template ID to the `POST /api/settings/knowledge/save-scribe` request

**Backend (`settings_api.py`):**

- Add `template_id` parameter to `ScribeSaveRequest`
- Pass template to `KnowledgeWriter.scribe_save()` → `Scribe.enrich_standalone()`

**Backend (`knowledge_writer.py`):**

- Accept optional `template` parameter in `scribe_save()`
- Load template content from `TemplateManager` if template ID provided
- Pass template structure and AI hints to `enrich_standalone()`

**Backend (`scribe.py`):**

- Update `enrich_standalone()` to accept optional template
- When template is provided, inject template structure into the enrichment prompt:

  ```
  **Template:** {template.name}
  **Structure:** {template.markdown_content}
  **AI Hints:** {template.get_ai_hints()}

  Follow this template's structure while enriching the content.
  Fill in template variables with relevant information from the content.
  ```

**Backend (`server.py` or `settings_api.py`):**

- Add `GET /api/settings/templates` endpoint to list available templates with metadata
- Returns `[{ id, name, icon, description, category }]`

### Phase 2: Immediate Note Indexing

**Backend (`knowledge_writer.py` — `_save_note()`):**

- After file write, ensure RAG indexing succeeds or is queued:
  1. Call `rag.index_single_document()` — if it fails, queue for retry
  2. Emit a `note_created` event (or call directly) to refresh the notes file index
- Add a new method `_notify_notes_index(note_path, metadata)` that:
  1. Triggers the notes file watcher to pick up the new file
  2. OR directly calls the notes index update endpoint

**Backend (`server.py`):**

- Add `POST /polly/notes/refresh-index` to force a notes index refresh for a specific path
- The `_save_note()` method calls this after successful file write

**Frontend (`notes-manager.js`):**

- After receiving success from any note creation API call, trigger a notes list refresh
- Add listener for a `note-created` event that triggers `loadNotesIndex()` automatically
- Consider websocket/SSE notification for real-time index updates (stretch goal)

### Phase 3: Intelligent Note Naming

**Backend (`knowledge_writer.py`):**

- Replace `_generate_title_from_content()` with `_generate_smart_title()`:
  1. If content is from a conversation query, extract the topic (not the question phrasing)
  2. Use a lightweight LLM call with a focused prompt:

     ```
     Generate a concise knowledge base note title (3-7 words) for this content.
     The title should name the TOPIC, not describe the action.

     BAD: "How to set up Django models"
     GOOD: "Django Model Configuration"

     BAD: "Can you explain quantum computing"
     GOOD: "Quantum Computing Fundamentals"

     Content: {first 500 chars of content}

     Title:
     ```

  3. Fallback (no LLM available): extract key nouns/concepts via simple NLP, construct a noun-phrase title
  4. Never start with: "Can you," "I need," "Help me," "How to," "What is," "Discussion about"

- Add title validation: reject titles > 60 chars, titles that are questions, titles with filler words at start
- Add `conversation_context` parameter — if the note originated from a conversation, use the conversation's messages for better topic understanding

### Phase 4: Template Refinement

**Templates (`vault/.polly/templates/`):**

- Audit existing templates for:
  - Clear section structure
  - Useful AI hints in frontmatter
  - Appropriate default tags and domain mappings
  - Variable placeholders that the enrichment can fill
- Ensure at least these templates exist and are well-crafted:
  1. **Blank** (no structure, free-form)
  2. **Meeting Notes** (date, attendees, agenda, decisions, action items)
  3. **Project Plan** (overview, goals, phases, timeline, risks)
  4. **Research Note** (topic, key findings, sources, open questions, connections)
  5. **Concept Exploration** (definition, examples, relationships, applications)
  6. **Daily Reflection** (date, highlights, learnings, gratitude, tomorrow)
  7. **Book/Article Notes** (title, author, key ideas, quotes, synthesis)

---

## Risks & Mitigations

**Risk**: Template selection adds friction to the save flow  
**Mitigation**: Default to "Blank" with one-click selection. Remember last-used template per domain. Template picker can be skipped with a "quick save" button.

**Risk**: LLM title generation adds latency to note creation  
**Mitigation**: Generate title asynchronously after note is saved. Show a placeholder title immediately, update when LLM responds. Use fast tier.

**Risk**: RAG indexing fails silently on new notes  
**Mitigation**: Add explicit success/failure tracking. Queue failed indexing for retry. Show a small indicator on the note if not yet indexed.

**Risk**: Template enrichment produces worse results than freeform  
**Mitigation**: Template AI hints guide the LLM but don't over-constrain. The "Blank" option always available. A/B test template vs. freeform quality.

---

## Timeline Estimate

- Phase 1 (Template selection): 6 hours
- Phase 2 (Immediate indexing): 3 hours
- Phase 3 (Smart naming): 3 hours
- Phase 4 (Template refinement): 3 hours

**Total: ~15 hours** (2 working days)

---

## Related Work

- Knowledge Writer: `core/knowledge_writer.py`
- Scribe Persona: `core/personas/implementations/scribe.py`
- Template Manager: `core/templates/manager.py`, `core/templates/template.py`
- Notes Spec: [openspec/specs/notes/spec.md](../../specs/notes/spec.md)
- Settings API: `interfaces/settings_api.py` (save-quick, save-scribe endpoints)
- Notes Manager: `electron-app/src/renderer/notes-manager.js`

---

## Open Questions

1. Should template selection persist per domain? (e.g., "Sigils" domain defaults to "Concept Exploration") → **Yes, store preference in config**
2. Should notes created without a template be retroactively restructured? → **No, only applies to new notes going forward**
3. Should the template picker also appear for Quick Save (non-Scribe) path? → **No initially — Quick Save is meant to be fast. Add later if requested.**
4. How should the title generation handle non-English content? → **Same prompt, LLM handles multilingual. Fallback to first-sentence truncation for unsupported languages.**
