# Knowledge Graph & Quality (OpenSpec)

Source of truth for entity extraction, knowledge graph, authority scoring, anti-slop mechanisms, and unified knowledge retrieval. Extends Phase 12a/12b (Knowledge Graph), overhauls Phase 21 (Deduplication), and supersedes the original LlamaIndex KG task (#24 in Core Framework Refinement).

## Implementation Status

| Feature                                                | Status         | Notes                                                                            |
| ------------------------------------------------------ | -------------- | -------------------------------------------------------------------------------- |
| Entity extraction (spaCy + regex)                      | ✅ Implemented | `core/entities/extractor.py`                                                     |
| EntityStore (SQLite, CRUD, graph ops)                  | ✅ Implemented | `core/entities/store.py`, `~/.polly/entities.db`                                 |
| Authority scoring (recompute_authority)                | ✅ Implemented | Upgraded with PageRank + betweenness (Phase 12b Wave 3)                          |
| EntityContextBuilder (prompt context)                  | ✅ Implemented | `core/entities/context.py`                                                       |
| Graph-aware retrieval (GraphRetriever + authority RRF) | ✅ Implemented | Phase 12b Wave 1: `core/entities/retriever.py`, `core/hybrid_search.py`          |
| Quality controls (isolation, garden digest, batch ops) | ✅ Implemented | Phase 12b Wave 2: garden digest endpoint, batch operations, authority scheduling |
| Community detection (label propagation)                | ✅ Implemented | Phase 12b Wave 3: `core/entities/intelligence.py`                                |
| Centrality metrics (PageRank + betweenness)            | ✅ Implemented | Phase 12b Wave 3: `core/entities/intelligence.py`                                |
| Edge confidence scoring (multi-factor)                 | ✅ Implemented | Phase 12b Wave 3: `core/entities/intelligence.py`                                |
| Path-finding API                                       | ✅ Implemented | Phase 12b Wave 1: `GET /graph/path`                                              |
| "Why this connection?" API                             | ✅ Implemented | Phase 12b Wave 3: `GET /graph/edge/explain`                                      |
| Communities API                                        | ✅ Implemented | Phase 12b Wave 3: `GET /graph/communities`                                       |
| Frontend: community cluster coloring                   | ✅ Implemented | Phase 12b Wave 3: color-by toggle (domain/community)                             |
| Frontend: path highlighting                            | ✅ Implemented | Phase 12b Wave 3: gold path overlay between nodes                                |
| Frontend: edge confidence "Why?" modal                 | ✅ Implemented | Phase 12b Wave 3: multi-factor breakdown + evidence                              |
| Frontend: isolation badges + garden digest             | ✅ Implemented | Phase 12b Wave 2: browse list badges, garden panel                               |
| LlamaIndex KG / SubQuestionQueryEngine                 | 💭 Vision      | Core Framework Refinement Task #24                                               |
| Anti-slop (augmented writing, smart summarization)     | 📐 Designed    | Phase 12c scope                                                                  |

## Overview

The Knowledge Quality system is the connective tissue for all knowledge management in Polly. It extracts entities from content, builds a queryable graph of relationships, scores notes by authority, and provides ongoing maintenance to prevent knowledge fragmentation ("slop").

The system unifies three previously separate approaches:

1. **`core/entities/`** (implemented Feb 2026) — Unified entity model, SQLite storage (`~/.polly/entities.db`), EntityStore with graph operations (traversal, path finding, cross-domain bridges), EntityExtractor (spaCy + technical terms + regex), EntityContextBuilder for prompt context. Replaces the former `learners/graph.py` (archived to `learners/archive/graph_v1.py`).
2. **LlamaIndex KG** (planned, Task #24) — Triple storage (subject-predicate-object), SubQuestionQueryEngine. Remains a valid tool for the entity extraction and graph query layer.
3. **Anti-slop / Recall architecture** (new) — Authority scoring (✅ basic formula in EntityStore.recompute_authority), connection metrics, garden maintenance, augmented writing. The quality and maintenance layer on top of the graph.

The existing `DeduplicationEngine` (Phase 21, `core/notes_dedup.py`) is absorbed as one step in the broader Knowledge Quality Pipeline.

---

## Entity Extraction

### LLM-Based Extraction (Primary)

- **Method:** LLM-based extraction for domain-specific entities (people, concepts, tools, frameworks, projects). Standard NER models miss domain-specific terms; LLM extraction via existing provider system handles entities like "norns," "SuperCollider," "finite games."
- **Why not keyword-only:** The existing `learners/graph.py` uses hardcoded keyword lists (`ENTITY_TYPES`). This misses novel entities and doesn't generalize across user-customized domains. LLM extraction adapts to any domain configuration.
- **Fallback:** If LLM is unavailable (offline, rate-limited), fall back to keyword extraction from `learners/graph.py` + wiki-link parsing. Degraded but functional.

### LlamaIndex Integration (Optional Enhancement)

- **LlamaIndex KG index** provides structured triple extraction (subject-predicate-object) that complements free-form LLM extraction.
- **Use when available:** If LlamaIndex is installed, use its `KnowledgeGraphIndex` for structured triple storage alongside the SQLite entity graph.
- **SubQuestionQueryEngine:** Upgrades query decomposition to route sub-queries across KG, vector (ChromaDB), and keyword (BM25) indices simultaneously.
- **Not a hard dependency:** The knowledge graph works without LlamaIndex using LLM extraction + SQLite.

### Extraction Sources

- Runs on all note saves (new and edited), capture saves, canvas updates, conversation summaries.
- **Library content:** Book chunks, highlights, and annotations extracted during library indexing. Book-level entities (author, title, key concepts) extracted from metadata. See [library spec](../library/spec.md).
- **Output:** Entity nodes with type, name, domain affiliation, and source references.
- **User review:** Suggested entities presented before save completes. User can accept, reject, or add entities. Creates backpressure against thoughtless capture.

## Graph Structure

### Storage: SQLite (Primary)

**Current implementation (Feb 2026):** `core/entities/store.py` uses `~/.polly/entities.db` with tables `entities`, `relationships`, `entity_mentions`. See [entity-model-unification design](../../changes/entity-model-unification/design.md) for the exact schema. Authority scoring is implemented via `recompute_authority()` (mention_count, source_count, relationship count, recency).

**Planned enhancement:** Tables in `~/.polly/knowledge.db` (or merge into entities.db):

```sql
-- Core entities
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- concept, tool, project, person, framework, book, author
    domain TEXT,
    description TEXT,
    aliases TEXT,  -- JSON array
    authority_score REAL DEFAULT 0.0,
    inbound_count INTEGER DEFAULT 0,
    outbound_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationships between entities
CREATE TABLE entity_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id TEXT REFERENCES entities(id),
    target_entity_id TEXT REFERENCES entities(id),
    relationship_type TEXT NOT NULL,  -- references, relates_to, part_of, derived_from, contradicts, supports, authored_by, cited_in
    weight REAL DEFAULT 1.0,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Where entities are mentioned (provenance)
CREATE TABLE entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT REFERENCES entities(id),
    source_type TEXT NOT NULL,  -- note, capture, canvas, conversation, book, highlight
    source_id TEXT NOT NULL,
    context_snippet TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migration from `learners/graph.py`

- Existing JSON-stored entities and relationships migrate to SQLite on first run of new system.
- `learners/graph.py` becomes a compatibility layer that reads/writes to SQLite instead of JSON.
- Co-occurrence tracking moves to `entity_edges` with `relationship_type = 'co_occurs_with'`.

### Relationship Types

| Type             | Meaning                    | Example                              |
| ---------------- | -------------------------- | ------------------------------------ |
| `references`     | Direct mention or citation | Note references a concept            |
| `relates_to`     | Semantic relationship      | Two concepts are related             |
| `part_of`        | Hierarchical containment   | Section is part of a book            |
| `derived_from`   | One thing built on another | A note derived from a book highlight |
| `contradicts`    | Opposing claims            | Two sources disagree                 |
| `supports`       | Reinforcing claims         | Two sources agree                    |
| `authored_by`    | Authorship                 | Book authored by a person            |
| `cited_in`       | Citation relationship      | Concept cited in a book              |
| `co_occurs_with` | Frequently appear together | Auto-detected from co-occurrence     |

## Unified Knowledge Retrieval

The knowledge graph enables retrieval across **all** content sources through a unified query interface:

### Source Types in the Graph

| Source               | Entity Types                         | How Indexed                     |
| -------------------- | ------------------------------------ | ------------------------------- |
| **Notes**            | Concepts, tools, projects, people    | Entity extraction on save       |
| **Library (ebooks)** | Books, authors, concepts, citations  | Extracted during book import    |
| **Captures**         | Concepts, projects, people           | Entity extraction on save       |
| **Canvases**         | Projects, user segments, competitors | Cross-references as graph edges |
| **Conversations**    | Topics, decisions, action items      | Extraction from summaries       |
| **Code**             | Frameworks, patterns, libraries      | Extraction during code indexing |

### RAG Integration: Three-Strategy Retrieval

```
Query
  │
  ├── 1. Semantic Search (ChromaDB) → vector similarity
  ├── 2. Keyword Search (BM25) → term matching
  └── 3. Entity Graph Traversal → relationship-based discovery
        │
        ├── Extract entities from query
        ├── Find matching graph nodes
        ├── Traverse 2-3 hops for related content
        └── Return connected notes/books/captures
  │
  └── Reciprocal Rank Fusion (RRF)
        + Authority score weighting
        + Source-type weighting (configurable)
```

### Source-Type Weighting

Users control how different source types are weighted in retrieval:

```yaml
rag:
  source_weights:
    notes: 1.0 # Personal notes — highest weight (user's own thinking)
    library: 0.3 # Books — lower weight to avoid drowning personal notes
    captures: 0.8 # Recent captures — high relevance
    code: 0.5 # Code files — contextual
    conversations: 0.4 # Chat history — supporting context
```

**Smart routing:** Domain context influences weights. A philosophical query auto-boosts library weight. A code query boosts code weight. User can override with explicit scope: "Search my library for..." or "In my notes about...".

## Connection Metrics & Authority Scoring

- **Inbound connections:** How many other notes/captures/books reference this entity or note.
- **Outbound connections:** How many entities/notes this content references.
- **Authority score:** Computed from inbound count, weighted by referencing source quality. High inbound = authoritative hub.
- **Quality signals:**
  - **Hub notes** (high inbound): Core concepts worth elaborating.
  - **Isolated notes** (0–2 connections): Candidates for review, deletion, or integration.
  - **Bridge notes** (high in + out): Integration points between domains.
- **Book authority:** Books with many concept entities extracted get high authority. Highlights from authoritative books carry that authority to connected notes.
- **RAG integration:** Authority score added as a weight in Reciprocal Rank Fusion scoring. High-authority content boosted in search results.

## Anti-Slop Mechanisms

### Connection Threshold for Visibility

- Notes with 0 connections go to an "Inbox" state requiring review.
- Notes with <2 connections flagged as "potentially isolated."
- Encourages linking or deleting rather than accumulating.

### Garden Maintenance Prompts

- **Weekly/monthly digest:** "You have N isolated notes. Review batch?"
- **Suggested merges:** "These 3 notes all discuss X. Merge?"
- **Connection suggestions:** "X mentioned in N unlinked notes. Connect?"
- **Book connection suggestions:** "Your note on Y relates to Chapter 3 of Z. Link?"
- **Batch operations:** Merge duplicates, delete orphans, elaborate stubs.
- Integrates with review workflows (see [capture spec](../capture/spec.md)).

### Query-Driven Note Generation

- AI generates synthesis on explicit request, not automatically.
- "Show me all discussions about Docker from past month" → generates temporary synthesis.
- "What did Deleuze say about desire across my library?" → synthesizes from book chunks + notes.
- User explicitly saves synthesis as permanent note if valuable.
- Prevents auto-proliferation of AI-generated content.

### Smart Summarization Layers

- **Conversation** → immediate AI summary (short, structured).
- **Weekly** → aggregate summaries of related conversations by domain/entity.
- **Monthly** → synthesis notes across domains.
- Creates navigation hierarchy: detail → context → synthesis.
- Weekly/monthly summaries are themselves notes with entity extraction.

### Version Control for AI Content

- AI summaries/syntheses stored with provenance metadata (model, timestamp, source references).
- User can regenerate, edit, or delete without affecting source material.
- Prevents lock-in to stale AI interpretations.

## Augmented Writing

- During note composition, sidebar shows "potentially related notes" based on entity overlap in real-time.
- **Cross-source discovery:** Related library passages surface alongside related notes. "As you write about X, here's what Y said about it in book Z."
- Surfaces existing knowledge at the moment of creation — prevents duplicates and encourages linking.
- Uses existing right panel UI pattern from Notes editor.
- Debounced entity detection on editor content changes → RAG + graph queries → related content list.

## Knowledge Quality Pipeline

The unified pipeline that runs on every save:

```
Content Save (note/capture/canvas/book-import)
  │
  ├── 1. Entity Extraction → graph nodes + edges
  ├── 2. Similarity Check (existing dedup) → duplicate warning
  ├── 3. Connection Suggestion → link to existing entities
  ├── 4. Authority Update → recalculate inbound/outbound scores
  └── 5. RAG Index Update → incremental indexing (existing)
```

Background (scheduled):

- Isolation detection → flag notes with 0–2 connections
- Garden maintenance → weekly prompts for orphans/merges
- Authority recomputation → periodic full graph analysis
- Summarization layers → weekly/monthly synthesis generation

## Dual Hierarchy: User Tags + Auto-Connections

- **User-created structure:** Folders, domains, wiki-links, manual tags. Intentional organization.
- **Auto-generated structure:** Entity graph with extracted connections. Emergent organization.
- Both coexist. Tags provide familiar navigation; the graph provides discovery. Auto-categorization respects existing tag structure.

## Knowledge Graph Visualization

Interactive visualization of the entity graph using Cytoscape.js.

### Core Features

- **Interactive graph view:** Nodes represent entities (concepts, people, organizations, books). Edges represent connections with type and strength. Zoom, pan, click-to-explore.
- **5 node types:** Concept, Person, Organization, Technology, Domain — each with distinct visual style.
- **4 edge types:** References, Related, Defines, Contradicts — with visual differentiation.
- **Connection metrics visible:** Node size scales with inbound connections (authority). Edge thickness indicates connection strength.
- **Domain coloring:** Nodes colored by domain affiliation. Cross-domain connections visually highlighted.

### Reasoning Transparency

When user clicks a connection, show "Why This Connection?" modal:

- **Confidence score** with multi-factor breakdown: semantic similarity, keyword overlap, structural proximity, temporal proximity, user behavior signals.
- **Evidence:** Specific text passages that generated the connection.
- **User override:** Accept, reject, or adjust connection strength.

### "Explore From Here" Mode

Click any node → expand neighborhood (1–3 hops configurable). Progressive disclosure of the graph — don't show everything at once.

### UI Integration

- Dedicated graph view page (or panel within Notes view).
- Mini-graph widget in note detail view showing immediate connections.
- Search results annotated with graph position.

### Technology

- **Cytoscape.js** for rendering (canvas-based, performant for 1000+ nodes).
- **Layouts:** Force-directed (default), hierarchical (for domain trees), concentric (for ego networks).
- Graph data served from SQLite entity tables via REST API.

Detail: [docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md](../../../docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md).

## Implementation Phases

### Phase 12a-Extended: Foundation (2–3 weeks)

- SQLite graph schema (entities, edges, mentions)
- Migrate `learners/graph.py` data to SQLite
- LLM-based entity extraction on all new notes
- Connection metrics visible in notes UI
- Authority scoring computation
- Absorb dedup engine into quality pipeline

### Phase 12b-Extended: Quality Controls + Graph Intelligence ✅ (March 2026)

- ✅ Wave 1: GraphRetriever (ContextContributor), authority scoring as 3rd RRF signal, path-finding API, config entries, 31 tests
- ✅ Wave 2: Isolated note detection, garden maintenance digest, batch operations, authority scheduling, frontend isolation badges + garden panel, 25 tests
- ✅ Wave 3: Community detection (label propagation), PageRank + betweenness centrality, upgraded authority formula, edge confidence scoring, "Why this connection?" API, communities API, frontend community coloring + path highlighting + edge explain modal, 35 tests
- 91 total tests across `test_graph_retriever.py` (31) and `test_graph_intelligence.py` (60)

### Phase 12c: Active Maintenance (2–3 weeks)

- Augmented writing (related notes during composition)
- Smart summarization layers (weekly/monthly)
- Cross-domain entity relationship visualization (Cytoscape.js from original Phase 12a plan)
- Version control for AI-generated content

### Phase 12d: Library Integration (concurrent with library implementation)

- Book-level entity extraction (author, title, concepts)
- Chapter/section entities linked to book entity
- Highlight-to-note entity bridging
- Source-type weighting in unified retrieval
- Cross-source augmented writing (books + notes)

### Optional: LlamaIndex Enhancement

- Add LlamaIndex KG index for structured triple storage
- Upgrade query decomposition to SubQuestionQueryEngine
- Runs in parallel with SQLite graph (complementary, not replacement)

## Relationship to Existing Systems

| System                  | Integration                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| **`learners/graph.py`** | Migrated to SQLite; becomes compatibility layer                                           |
| **Dedup (Phase 21)**    | Absorbed — `check_similarity()` becomes step 2 in quality pipeline                        |
| **RAG**                 | Authority scoring in RRF; entity-graph as third retrieval strategy; source-type weighting |
| **BacklinksIndex**      | Extended with connection counts; feeds authority scoring                                  |
| **Notes**               | Entity extraction on save; augmented writing panel; maturity + connection metadata        |
| **Library**             | Book entities, author entities, highlight provenance in graph; cross-source retrieval     |
| **Patterns**            | Entity patterns detected across notes; cross-project pattern recognition                  |
| **Canvas**              | Canvas cross-references become graph edges; gap detection uses graph                      |
| **Capture**             | Captures run through quality pipeline on save                                             |
| **Mem0**                | Mem0 graph memory complements entity graph; both feed RAG context                         |
| **LlamaIndex**          | Optional KG index for structured triples; SubQuestionQueryEngine for decomposition        |

## Reference

- Phase 12a/12b planning: [docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md](../../../docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md)
- Existing graph: `learners/graph.py`
- Existing dedup: `core/notes_dedup.py`, [PHASE21_KNOWLEDGE_DEDUPLICATION.md](../../../docs/planning/phases/phase-21/PHASE21_KNOWLEDGE_DEDUPLICATION.md)
- Existing backlinks: `core/backlinks.py`
- LlamaIndex KG task: [core-framework-refinement tasks.md](../../changes/core-framework-refinement/tasks.md) (Task #24)
- Library spec: [library spec](../library/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)
