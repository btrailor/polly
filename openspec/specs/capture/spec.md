# Capture System (OpenSpec)

Source of truth for multi-modal capture, PARA-inspired organization, maturity lifecycle, and review workflows.

## Overview

The capture system handles how knowledge enters Polly — from quick text to voice memos to image captures. It provides smart routing to domains, maturity lifecycle tracking, and structured review workflows. Desktop Polly provides the full capture experience; the mobile companion (see [mobile spec](../mobile/spec.md)) provides a lightweight capture-focused interface.

---

## Input Methods

- **Quick text:** Minimal friction text entry. Extends existing knowledge writing from chat.
- **Voice-to-text:** Transcription with domain auto-detection. First-class input on mobile companion.
- **Image capture:** Photos with OCR and domain tagging. Desktop: drag-and-drop or paste. Mobile: camera.
- **URL/link:** Automatic metadata extraction (title, description, content archival). Saves page content, not just link.
- **Code snippets:** Syntax-aware capture with language detection. Extends CodeMirror integration.

## Smart Routing

- **Auto-domain suggestion:** Content analysis via LLM classifies captures to domains. Uses existing domain system (`~/.polly/domains.json`).
- **Custom keyword triggers:** User-defined keywords map to domains (e.g., "norns" → Signals, "Docker" → Sigils). Stored in domain configuration.
- **Default domain per capture method:** Configurable (e.g., voice → Scrolls, code → Sigils).
- **Routing uses existing RAG pipeline** for content classification — extends, not replaces, current domain detection.

## Capture Metadata

Every capture includes:

| Field                   | Source                                            |
| ----------------------- | ------------------------------------------------- |
| Timestamp               | Automatic                                         |
| Source type             | voice, text, image, link, code                    |
| Domain tags             | Multiple allowed; auto-suggested + user-confirmed |
| Maturity stage          | Default: 30-Ideas                                 |
| Related project/context | Optional user tagging                             |
| Location                | Optional (mobile companion)                       |

## Organization: PARA-Inspired Structure

Layered on top of existing vault/notes storage as metadata and views, not restructuring physical files:

- **Projects:** Active work with clear outcomes. Maturity: 20-Active.
- **Areas:** Ongoing responsibilities and domains. Maps to existing domain folders.
- **Resources:** Reference material and archives. Maturity: 10-Archive.
- **Ideas:** Seeds and possibilities. Maturity: 30-Ideas.

## Maturity Lifecycle

Shared system used by captures, notes, and canvases:

| Stage          | Meaning                              | Visual                       |
| -------------- | ------------------------------------ | ---------------------------- |
| **30-Ideas**   | Initial captures, unexplored seeds   | Seed icon, muted style       |
| **20-Active**  | Work in progress, current engagement | Active indicator, full style |
| **10-Archive** | Completed or suspended work          | Archive icon, dimmed         |

- **Transitions:** Manual (drag-and-drop, menu) or prompted (review workflows suggest promotions).
- **Storage:** Frontmatter metadata in note files + SQLite index for querying.
- **Batch updates:** Select multiple captures and change maturity stage together.
- **Visual indicators:** Maturity stage visible in notes browser, search results, canvas.

## Review Workflows

Structured modes for processing knowledge (integrates with garden maintenance from [knowledge-graph spec](../knowledge-graph/spec.md)):

| Mode                | Frequency | Purpose                                         |
| ------------------- | --------- | ----------------------------------------------- |
| **Triage**          | As needed | Quick domain/stage assignment for new captures  |
| **Daily review**    | Daily     | Process recent captures into projects           |
| **Weekly review**   | Weekly    | Maturity stage progression + garden maintenance |
| **Domain-specific** | As needed | Filter by single domain for focused work        |
| **Cross-domain**    | As needed | Explore connections between domains             |

- Review modes are views/filters in the UI, not separate pages.
- Weekly review includes garden maintenance prompts (isolated notes, merge suggestions) from knowledge quality system.

## Tagging System

Extends existing domain tags with richer taxonomy:

- **Domain tags:** From domain system (Sigils, Signals, etc.). Already exists.
- **Project tags:** User-defined, linked to active projects/canvases.
- **Concept tags:** Auto-suggested from entity extraction (knowledge graph), user-confirmed.
- **Tag hierarchy:** Up to 3 levels deep. User-created for intentional organization.
- **Tag analytics:** Usage trends, tag co-occurrence, dormant tags.

## Reference Management

- **URL archival:** Save full page content on capture, not just link. Prevent link rot.
- **Citation extraction:** Parse academic references, format citations.
- **Bibliography generation:** By project — aggregate all sources referenced.
- **Related reading suggestions:** RAG-powered, based on entity overlap with existing captures.

## Implementation Phases

### Capture Foundation (2–3 weeks)

- Capture data model and API (extends `/polly/notes/create`)
- Maturity lifecycle metadata on notes
- Quick text + URL capture with metadata
- Triage review mode

### Smart Routing + Input (2–3 weeks)

- Domain auto-detection on captures
- Custom keyword triggers
- Code snippet capture with language detection
- Daily/weekly review workflow UI

### Voice + Image (3–4 weeks)

- Voice-to-text integration (transcription service)
- Image capture with OCR
- Mobile companion capture submission (via DRM or REST)

### Reference + Analytics (2 weeks)

- URL archival (content preservation)
- Tag analytics and hierarchy
- Capture pattern insights

## Relationship to Existing Systems

| System                | Integration                                                          |
| --------------------- | -------------------------------------------------------------------- |
| **Notes**             | Captures become notes with extended metadata (maturity, source type) |
| **Knowledge writing** | Existing chat-to-KB writing becomes one capture path                 |
| **RAG**               | Captures indexed incrementally (existing `index_single_document()`)  |
| **Domains**           | Smart routing uses domain system for classification                  |
| **Knowledge graph**   | Captures run through entity extraction pipeline on save              |
| **Canvas**            | Captures can link to active canvases as source material              |
| **Mobile**            | Mobile companion submits captures to desktop                         |

## Reference

- Existing knowledge writing: `core/knowledge_writer.py`
- Notes system: [notes spec](../notes/spec.md)
- Domain system: [domains spec](../domains/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)
