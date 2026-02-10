# Library — BookLore (OpenSpec)

Source of truth for Polly's ebook library management, reading pipeline, and library-to-knowledge-base integration. Planned as Phase 25 (originally in Brain Dump and Core Framework Refinement Wave 6).

## Overview

BookLore brings the user's ebook library into Polly as a first-class knowledge source. Books are imported, parsed, indexed into RAG, and connected to the knowledge graph — making book content retrievable alongside personal notes, captures, and conversations in a unified knowledge base.

The key design tension: **books must enrich retrieval without drowning out the user's own thinking.** Library content is always weighted below personal notes in RAG results unless the user explicitly searches the library.

---

## Storage

```
~/.polly/library/
├── books/                    # Original ebook files
│   ├── {isbn-or-hash}/      # Per-book directory
│   │   ├── book.epub        # Original file
│   │   ├── metadata.json    # Extracted metadata
│   │   └── chunks/          # Pre-parsed chapter chunks (markdown)
│   └── ...
├── highlights/               # User annotations and highlights
│   └── {book-id}.json
└── exports/                  # E-reader sync staging
```

### Metadata Database

SQLite in `~/.polly/knowledge.db` (shared with knowledge graph):

```sql
CREATE TABLE books (
    id TEXT PRIMARY KEY,         -- ISBN or content hash
    title TEXT NOT NULL,
    authors TEXT,                -- JSON array
    publisher TEXT,
    pub_date TEXT,
    language TEXT,
    format TEXT,                 -- epub, pdf, mobi
    file_path TEXT,              -- Path to original file
    cover_path TEXT,             -- Path to extracted cover image
    domain TEXT,                 -- User-assigned domain
    tags TEXT,                   -- JSON array of user tags
    total_chapters INTEGER,
    total_words INTEGER,
    indexed_at TIMESTAMP,        -- When indexed into RAG
    maturity_stage TEXT DEFAULT '20-Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE book_chapters (
    id TEXT PRIMARY KEY,
    book_id TEXT REFERENCES books(id),
    chapter_number INTEGER,
    title TEXT,
    word_count INTEGER,
    chunk_count INTEGER          -- Number of RAG chunks from this chapter
);

CREATE TABLE book_highlights (
    id TEXT PRIMARY KEY,
    book_id TEXT REFERENCES books(id),
    chapter_id TEXT REFERENCES book_chapters(id),
    content TEXT NOT NULL,        -- Highlighted text
    annotation TEXT,              -- User's note on the highlight
    page_number INTEGER,
    position_start INTEGER,
    position_end INTEGER,
    exported_to_note TEXT,        -- Path to note if exported
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## How Polly Reads Ebooks

### EPUB Parsing Pipeline

EPUB is the primary format. The parsing pipeline extracts structured content for RAG indexing:

```
EPUB file
  │
  ├── 1. Unzip (EPUB is a ZIP archive)
  │     └── Extract XHTML content files, metadata (OPF), TOC (NCX/nav)
  │
  ├── 2. Metadata Extraction
  │     ├── Title, authors, publisher, date, language, ISBN
  │     ├── Cover image extraction
  │     └── Table of contents structure (chapter titles + order)
  │
  ├── 3. Content Extraction (per chapter)
  │     ├── Parse XHTML → clean text (strip HTML tags, preserve structure)
  │     ├── Preserve headings (H1–H6) as structural markers
  │     ├── Preserve block quotes, lists, code blocks
  │     ├── Extract inline images (store separately, reference in chunks)
  │     ├── Handle footnotes/endnotes (inline or append to chapter)
  │     └── Output: clean markdown per chapter
  │
  ├── 4. Chunking (for RAG)
  │     ├── Strategy: chapter-aware semantic chunking
  │     │   - Primary split: by chapter boundaries
  │     │   - Secondary split: by heading boundaries within chapters
  │     │   - Tertiary split: by paragraph if sections exceed max chunk size
  │     ├── Chunk size: 512–1024 tokens (same as note chunking)
  │     ├── Overlap: 64 tokens between consecutive chunks
  │     ├── Each chunk preserves:
  │     │   - book_id, chapter_number, chapter_title
  │     │   - section_heading (if within a subsection)
  │     │   - page_number (estimated from character position)
  │     │   - chunk_index (position within chapter)
  │     └── Output: list of ChunkWithMetadata objects
  │
  ├── 5. Embedding + Indexing
  │     ├── Embed chunks via Ollama (same embedder as notes: nomic-embed-text)
  │     ├── Store in ChromaDB `library` collection (separate from `notes`)
  │     ├── Metadata per chunk: book_id, chapter, section, page, author, domain
  │     └── BM25 index updated for keyword search
  │
  └── 6. Entity Extraction + Graph Integration
        ├── Book-level entities: book (type: book), author (type: person), key concepts
        ├── Chapter-level entities: topics, people, frameworks mentioned
        ├── Relationships: book → authored_by → author, concept → cited_in → book
        ├── Run through Knowledge Quality Pipeline
        └── Graph edges connect book entities to note entities (same concepts)
```

### PDF Parsing

PDFs lack the structural metadata of EPUB. Parsing is best-effort:

```
PDF file
  │
  ├── 1. Text Extraction (PyPDF2 or pdfplumber)
  │     ├── Page-by-page text extraction
  │     ├── Handle multi-column layouts (heuristic detection)
  │     └── OCR fallback for scanned pages (optional, Tesseract)
  │
  ├── 2. Structure Detection
  │     ├── Heading detection via font size/weight heuristics
  │     ├── Chapter boundary detection (page breaks + heading patterns)
  │     └── Table of contents extraction (if present in bookmarks)
  │
  ├── 3. Chunking
  │     ├── Chapter-aware if structure detected
  │     ├── Page-based fallback (chunk per 2-3 pages)
  │     └── Same metadata schema as EPUB chunks
  │
  └── 4-6. Same as EPUB (embedding, indexing, entity extraction)
```

### MOBI/KFX Parsing

Convert to EPUB first (via Calibre's `ebook-convert` if available), then parse as EPUB. If conversion unavailable, extract text via fallback parser.

### Chunk Metadata Schema

Every library chunk in ChromaDB carries:

```json
{
  "source_type": "library",
  "book_id": "isbn-978-...",
  "book_title": "A Thousand Plateaus",
  "book_author": "Gilles Deleuze, Félix Guattari",
  "chapter_number": 3,
  "chapter_title": "10,000 B.C.: The Geology of Morals",
  "section_heading": "Double Articulation",
  "page_number": 45,
  "chunk_index": 7,
  "domain": "scrolls",
  "total_chunks_in_chapter": 24,
  "word_count": 487
}
```

This metadata enables:
- "What does Deleuze say about X?" → filter by author
- "In chapter 3 of A Thousand Plateaus..." → filter by book + chapter
- "Show me all philosophy passages about desire" → filter by domain + keyword
- Citation generation with page numbers

## RAG Integration: Unified Knowledge Retrieval

### Collection Architecture

Library content lives in a **separate ChromaDB collection** (`library`) from notes (`notes`) and code (`code`). This prevents library content from diluting personal note retrieval and allows independent control.

```
ChromaDB Collections:
  ├── notes      (personal notes, captures)
  ├── code       (code files, GitHub repos)
  └── library    (ebook content)
```

### Retrieval Modes

| Mode | Behavior | When Used |
|---|---|---|
| **Notes-only** | Search `notes` collection only | Default for most queries |
| **Notes + Library** | Search both, merge with library weight 0.3 | When domain suggests books are relevant |
| **Library-only** | Search `library` collection only | Explicit: "Search my library for..." |
| **Full Knowledge Base** | All collections, domain-weighted | Explicit: "Search everything about..." |

### Smart Routing for Library Inclusion

Rather than always searching the library (expensive, risks drowning notes), Polly decides when to include library results:

```python
def should_include_library(query: str, domain: str, entities: list) -> bool:
    """Decide whether to search library for this query."""
    
    # Explicit library request
    if "library" in query.lower() or "book" in query.lower():
        return True
    
    # Domain-based: philosophical, theoretical, academic queries
    if domain in library_heavy_domains:  # User-configurable
        return True
    
    # Entity-based: query mentions an author or book title in the graph
    for entity in entities:
        if entity.type in ('author', 'book'):
            return True
    
    # Citation pattern: "What did X say about Y?"
    if citation_pattern_detected(query):
        return True
    
    return False  # Default: don't search library
```

### Authority Scoring for Library Content

Library content participates in the knowledge graph's authority scoring:
- **Books** get authority from how many user notes reference their concepts.
- **Highlights** get authority from being explicitly marked by the user.
- **Book concepts** that also appear in the user's notes get boosted authority (the user has engaged with this idea).
- A passage from a book the user has heavily annotated ranks higher than one from an unread book.

## Knowledge Graph Integration

### Book-Level Entities

When a book is imported, the following entities are created:

```
Book Entity:  "A Thousand Plateaus" (type: book)
Author Entity: "Gilles Deleuze" (type: person)
Author Entity: "Félix Guattari" (type: person)

Edges:
  "A Thousand Plateaus" → authored_by → "Gilles Deleuze"
  "A Thousand Plateaus" → authored_by → "Félix Guattari"
```

### Concept Bridging

When entity extraction finds concepts in book content that match existing note entities:

```
Book chunk mentions "rhizome" → entity: "Rhizome" (type: concept)
User note "My Rhizome Thinking" → entity: "Rhizome" (type: concept)

Auto-generated edges:
  "Rhizome" → cited_in → "A Thousand Plateaus"
  "My Rhizome Thinking" → references → "Rhizome"
  
Graph enables: "Your note on rhizome thinking relates to Chapter 1 of A Thousand Plateaus"
```

### Highlight-to-Note Pipeline

When users create highlights:
1. Highlight stored in `book_highlights` table.
2. Entity extraction runs on highlight text.
3. If user annotates the highlight, annotation becomes a capture linked to the highlight.
4. "Export to note" creates a note with:
   - Highlight text as block quote
   - Source citation (book, chapter, page)
   - Wiki-links to related notes (via entity graph)
   - `derived_from` edge in graph connecting note → highlight → book

### Cross-Source Discovery

The entity graph enables queries that span books and notes:

- "What connections exist between my notes and Deleuze's work?" → graph traversal from author entity to all connected note entities
- "Which of my ideas have support in my library?" → find note entities that share edges with book entities
- "What have I read but never written about?" → book entities with no outbound edges to note entities (garden maintenance prompt)

## E-Reader Integration (Future)

- **Supernote:** USB/WiFi upload, highlight sync via annotation files.
- **Remarkable:** reMarkable Cloud API for document sync.
- **Kindle:** `My Clippings.txt` import for highlights/annotations.
- Highlight import creates `book_highlights` entries → entity extraction → graph integration.

## UI

### Library Page
New page in ribbon navigation:
- **Book browser:** Grid/list view with covers, filter by domain/author/tag.
- **Book detail:** Metadata, chapter list, highlights, related notes (via graph).
- **Import:** Drag-and-drop EPUB/PDF/MOBI. Batch import from folder.
- **Reading view (optional):** Basic in-app reader with highlight/annotation capability.

### Library in Search
- Library results appear in global search with source attribution ("From: A Thousand Plateaus, Ch. 3, p. 45").
- Toggle: "Include library in search" (persistent setting per session or global).
- Library-specific search: "Search library: desire and becoming"

### Library in Augmented Writing
- During note composition, related library passages surface alongside related notes in the right panel.
- Clicking a library result inserts a block quote with citation.

## Implementation Phases

### Phase 25a: Book Management (1–2 weeks)
- EPUB parsing pipeline (unzip, metadata, content extraction, chunking)
- PDF parsing (text extraction, structure detection)
- SQLite metadata tables (books, chapters)
- Import API endpoint
- Basic book browser UI

### Phase 25b: Library RAG (1–2 weeks)
- Separate ChromaDB `library` collection
- Embed and index book chunks with full metadata
- BM25 index for library
- Smart routing: when to include library in retrieval
- Source-type weighting in unified RAG
- Library search API

### Phase 25c: Knowledge Graph Integration (1–2 weeks)
- Book-level and chapter-level entity extraction
- Concept bridging between books and notes
- Authority scoring for library content
- Cross-source augmented writing (books + notes in sidebar)
- Garden maintenance: "Books you've read but never referenced"

### Phase 25d: Highlights & Annotations (1 week)
- Highlight storage and management
- Highlight-to-note export with citations
- E-reader highlight import (Kindle Clippings, Supernote)
- Highlight entity extraction and graph integration

### Phase 25e: E-Reader Sync (1 week, future)
- Supernote upload/sync
- Remarkable Cloud integration
- Reading progress tracking

## Performance Considerations

### Scale
- **Target:** 100–500 books (personal library scale).
- **Chunks per book:** ~200–500 (average 80,000 words, 512-token chunks).
- **Total library chunks:** 20,000–250,000.
- **ChromaDB handles this:** Tested to millions of documents. Separate collection keeps library queries isolated.
- **BM25 index:** Rebuilt incrementally per book. Sub-second for library-scale.

### Indexing Time
- **EPUB parsing:** 1–5 seconds per book.
- **Embedding:** 30–120 seconds per book (depends on model, GPU).
- **Entity extraction:** 5–30 seconds per book (LLM call for key concepts, bulk extraction).
- **Total per book:** ~1–3 minutes. Background task, non-blocking.
- **Batch import:** Queue system for importing entire library. DRM-distributable to NAS.

### Retrieval Latency
- **Library-only search:** Same as notes search (~100–500ms).
- **Combined search:** Two parallel collection queries + merge (~200–700ms).
- **Graph-enhanced:** +50–100ms for entity graph traversal.

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **RAG** | Separate `library` collection; unified retrieval with source-type weighting |
| **Knowledge graph** | Books, authors, concepts as entities; concept bridging to notes |
| **Notes** | Highlight-to-note export; cross-reference via graph |
| **Domains** | Books assigned to domains; domain influences library retrieval weight |
| **Capture** | Annotations on books become captures |
| **Maturity lifecycle** | Books track reading status (Ideas/Active/Archive) |
| **Augmented writing** | Library passages surface during note composition |
| **DRM** | Book indexing distributable to NAS node (compute-heavy) |
| **Compression** | LLMLingua compression on library chunks before LLM context injection |
| **Scribe** | Scribe assists with highlight synthesis and book note creation |

## Reference

- Original design: [archive/root-docs/BRAIN_DUMP_2026-01-31.md](../../../archive/root-docs/BRAIN_DUMP_2026-01-31.md) (Feature 1: Library Mode)
- Core Framework tasks: [core-framework-refinement tasks.md](../../changes/core-framework-refinement/tasks.md) (Tasks #27–28)
- Knowledge graph: [knowledge-graph spec](../knowledge-graph/spec.md)
- RAG system: [rag spec](../rag/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)
