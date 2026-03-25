# Knowledge Skill
## Polly Spec | Status: Planned | Last updated: 2026-03-25 | @security_audit path-permission sign-off: ✅

> *Polly's identity is "AI that knows your work." Without this skill, agents are generic chat. With it, they're operating on your actual knowledge — your notes, your books, your reading.*

---

## Problem Statement

The original Polly app ran a Python backend that handled semantic retrieval over the user's Obsidian vault. In the iOS-first OpenClaw architecture, that backend is gone. Phase 1 vault integration is client-side only — the user manually selects a note and it prepends to the message. That's augmentation, not retrieval.

This leaves a core capability gap: agents cannot proactively surface what the user knows. They can't answer "what have I written about X?", connect a current conversation to past reading, or reason across multiple knowledge sources.

**This is not a Phase 3 aspirational feature. This is what makes Polly Polly.**

---

## Architecture

### One Skill. Multiple Sources.

The Knowledge Skill is a single installable OpenClaw skill with a **pluggable adapter architecture**. It ships with two source adapters:

- **Obsidian Vault** (Phase 2) — reads markdown files from a local vault directory
- **BookLore Library** (Phase 2) — reads EPUBs from a self-hosted BookLore library

All sources feed into a **single shared FAISS HNSW index**, tagged by source. One install, one permission screen, one retrieval pipeline.

```
iPhone (Polly iOS)
    ↓ sends message
OpenClaw Gateway
    ↓ agent decides to retrieve
Knowledge Skill (running on gateway machine)
    ↓ queries
Unified HNSW Index (FAISS)
    chunks tagged by source: vault | booklore | ...
    ↓ backed by
Obsidian vault (filesystem) + BookLore library (filesystem)
    ↓ returns ranked results
Agent incorporates into response
    ↓
iPhone receives response
```

### No Cloud. No Python Server.

Runs entirely on the gateway machine. All embeddings are local via sentence-transformers. No API calls. No data leaves the machine.

### Where It Runs

Gateway machine alongside OpenClaw. Installed via Skills Marketplace (Phase 2). The iOS client never calls it directly — agents tool-call it.

---

## Source Adapters

### Adapter Interface

Each adapter implements:

```python
class KnowledgeAdapter:
    def crawl(self) -> Iterator[RawDocument]      # Initial index build
    def watch(self) -> Iterator[ChangeEvent]       # Incremental updates
    def chunk(self, doc: RawDocument) -> List[Chunk]  # Source-specific chunking
    def metadata(self, doc: RawDocument) -> dict   # Title, author, tags, path, source
```

Chunks are normalized before hitting the shared pipeline — source differences are contained inside the adapter.

---

### Adapter: Obsidian Vault

**Input:** Markdown files on the local filesystem

**Chunking strategy — structure-aware, not fixed-size:**

Obsidian notes are fragments. A note might be 3 bullet points, a half-finished idea, or a title with no body. The adapter preserves structure:

- **Frontmatter** (title, tags, aliases, date) → filterable metadata, not body text
- **Headers** (H1–H3) → chunk boundaries; each section is a semantic unit
- **Wikilinks** (`[[note title]]`) → extracted into adjacency structure (graph layer — see below)
- **Tags** (#tag) → metadata for filtered retrieval
- **Minimum chunk size:** 50 tokens — notes shorter than this are one chunk

**Metadata per chunk:**
```json
{
  "source": "vault",
  "path": "~/Documents/MyVault/Projects/Polly.md",
  "title": "Polly",
  "tags": ["project", "ios"],
  "section": "Architecture"
}
```

**Graph layer (wikilink extraction):**

At chunk ingest time, the Obsidian adapter also extracts wikilinks from each note into a separate graph store. This runs alongside vector embedding — same ingest pass, different output destination.

```python
# Pseudocode — runs during crawl(), not chunk()
def extract_links(doc: RawDocument) -> List[WikilinkEdge]:
    links = re.findall(r'\[\[([^\]]+)\]\]', doc.content)
    return [WikilinkEdge(from_id=doc.id, to_title=link, link_text=link) for link in links]
```

Graph store: SQLite (`~/.openclaw/skills/knowledge/graph.db`). Schema:

```sql
CREATE TABLE notes (
    note_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    path TEXT NOT NULL,
    tags TEXT,          -- JSON array
    domain TEXT,        -- Practice Layer domain label (Phase 3, nullable Phase 2)
    modified_at INTEGER
);

CREATE TABLE wikilinks (
    from_id TEXT NOT NULL,
    to_id TEXT,         -- NULL if target note doesn't exist yet (dangling link)
    to_title TEXT NOT NULL,
    link_text TEXT,
    FOREIGN KEY (from_id) REFERENCES notes(note_id)
);

CREATE INDEX idx_wikilinks_from ON wikilinks(from_id);
CREATE INDEX idx_wikilinks_to ON wikilinks(to_id);
```

Dangling links (wikilinks pointing to notes that don't exist) are stored with `to_id = NULL` — resolved on next ingest if the target note is created.

The graph store is updated incrementally alongside the FAISS index — same dirty-flag mechanism, same watcher cycle.

**Informed by:** `core/entities/store.py` from salvage audit (SQLite-backed graph operations), `core/entities/intelligence.py` (community detection, centrality) — Phase 3 extension of this layer.

---

### Adapter: BookLore Library

**Input:** EPUBs from a self-hosted BookLore library directory

**Why EPUBs are actually good for RAG:**
Unlike Obsidian's fragments, EPUBs are well-structured. Chapters are natural chunk boundaries. Metadata (title, author, publisher) is embedded in the EPUB manifest. Better signal density than vault notes.

**Implementation:**
- Python `ebooklib` library parses EPUB structure
- Chapter boundaries used as primary chunk boundaries
- HTML content stripped to plain text
- Paragraph-level sub-chunking within chapters (max 512 tokens per chunk)
- BookLore library directory watched for new/changed EPUBs

**Metadata per chunk:**
```json
{
  "source": "booklore",
  "path": "/opt/booklore/library/The_Pragmatic_Programmer.epub",
  "title": "The Pragmatic Programmer",
  "author": "David Thomas, Andrew Hunt",
  "chapter": "Chapter 3: The Basic Tools",
  "chunk_index": 2
}
```

**BookLore path config:**
The user provides the BookLore library directory path in skill settings. The skill declares `read:filesystem:/path/to/library` in its manifest — path is user-configured at install time, not hardcoded.

---

### Adapter: Conversation History (Phase 3)

**Input:** OpenClaw session store + agent memory files

Multiple Phase 3 features need to search across past conversations — not vault notes, but what was argued, decided, and inferred in chat sessions. The Epistemic Immune System needs rhetorical structure. The Metacognitive Dashboard needs mental model usage. Temporal Intelligence needs position extraction. Oral History needs the full longitudinal arc.

Daily memory summaries (`memory/YYYY-MM-DD.md`) are too compressed for this — they capture conclusions, not the inferential shape of how those conclusions were reached.

**What gets indexed:**

The conversation adapter reads from two sources:

1. **Agent memory files** — `memory/YYYY-MM-DD.md` from all agents. The Standard SOUL Baseline's `## Reasoning` section provides structured inferential content; the other sections provide goal/decision/fact context.
2. **OpenClaw session exports** (Phase 3+) — requires OpenClaw to expose session data in a readable format. Not required for Phase 3 initial launch; memory files alone are sufficient for the first iteration.

**Why `## Reasoning` matters:** The SOUL baseline's memory write format includes a `## Reasoning` section specifically to give this adapter structured inferential content. A memory file with `## Reasoning` populated is dramatically more useful to the Epistemic Immune System than one with only `## Decisions made`. Every agent that writes memory writes inferential history.

**Chunking strategy:**

Memory files are chunked by section header. Each `##` section becomes a chunk with metadata:

```json
{
  "source": "conversation",
  "agent_id": "string — which agent wrote this",
  "date": "YYYY-MM-DD",
  "section": "## Reasoning | ## Decisions made | ## Goal | ...",
  "path": "agents/the-strategist/memory/2026-03-25.md"
}
```

**Ingest trigger:** Memory files are watched like vault files — same dirty-flag watcher, same 30s cycle. New memory files written by agents are indexed within one cycle.

**Privacy note:** Conversation history is the most sensitive corpus in the system. It stays on the gateway machine. It is not shared with any skill or feature that reads from a network source. The `network: []` constraint applies to this adapter with particular strictness — no conversation data ever leaves the machine.

---

### Index Hooks (Extension Point)

The indexing pipeline supports registered hooks — additional passes that run per-chunk at index time. Phase 2 ships with zero hooks. Phase 3 features register hooks to add metadata without requiring a full re-index.

**Hook interface:**

```python
class IndexHook:
    hook_id: str          # unique identifier, e.g. "structural-pattern-tagger"
    sources: List[str]    # which sources this hook applies to: ['vault', 'booklore', 'conversation']
    run_async: bool       # True: runs in background after ingest; False: blocks ingest
    
    def process(self, chunk: Chunk, metadata: dict) -> dict:
        """
        Receives a chunk and its existing metadata.
        Returns a dict of additional metadata fields to merge.
        """
        ...
```

**Hook registry:** `~/.openclaw/skills/knowledge/hooks.json` — list of registered hook configurations. The Knowledge Skill reads this on startup and re-reads it when the file changes (hot-reload).

**Phase 3 hooks that will register:**
- `structural-pattern-tagger` — LLM classification pass adding `structural_patterns: string[]` to vault chunks (Structural Analogy)
- `domain-label-enricher` — derives domain labels from wikilink cluster membership (Practice Layer)
- `rhetorical-structure-extractor` — identifies argument structure in conversation chunks (Epistemic Immune System)

**Why this matters for Phase 1:** The hook extension point must be designed now. Adding a classification pass at Phase 3 without it means re-indexing the entire corpus — potentially thousands of notes and books — to add metadata that could have been computed incrementally. The hook interface is cheap to add in Phase 2 and expensive to retrofit later.

---

## Retrieval Architecture

### Primary: Hybrid Retrieval (Dense + Sparse + RRF Fusion)

**Stack:**
- **Dense:** FAISS HNSW index (`IndexHNSWFlat` — faster at scale than flat L2, minimal accuracy loss) with embeddings from `BAAI/bge-large-en` (1024-dim, top MTEB benchmark, Apache-2.0). Lightweight alternative: `Qwen/Qwen3-Embedding-0.6B` (compact, competitive). Configurable.
- **Sparse:** SBERT Sparse Encoder (unified pipeline — one library handles both legs)
- **Fusion:** Reciprocal Rank Fusion (RRF) — no score normalization required

```python
def rrf_score(rank, k=60):
    return 1 / (k + rank)

final_score = rrf_score(dense_rank) + rrf_score(sparse_rank)
```

### Secondary: Wikilink Graph Layer (Vault only, opt-in)

The Obsidian adapter maintains a separate `[[wikilink]]` adjacency structure. Enables relationship queries FAISS can't answer: "what connects to this note?", "what's this part of?". GraphRAG (microsoft/graphrag) is the reference implementation. Opt-in due to indexing cost.

### Optional: Query Expansion

LLM rewrites the query before retrieval — expands abbreviations, adds synonyms, clarifies intent. Adds ~100ms. Default: off; user-configurable.

### Optional: Re-ranking

Two-stage retrieval: FAISS retrieves top-20 candidates, Cross-Encoder (`Qwen/Qwen3-Reranker-0.6B`) re-ranks to top-5. More accurate final ranking. Default: on.

### Optional: HyDE (Hypothetical Document Embeddings)

Generates a hypothetical answer first, retrieves against that embedding. Better for deep conceptual queries. Adds ~500ms. Default: off; agent-activated per query.

---

## Index Freshness

### File Watchers

Both adapters register filesystem watchers on startup:

| Event | Action |
|-------|--------|
| File created | Add to index queue |
| File modified | Mark dirty, re-index next cycle |
| File deleted | Remove from HNSW index + sparse index |
| File renamed | Remove old, add new |

Dirty-flag tracking: `~/.openclaw/skills/knowledge/dirty.json`. Watcher cycle default: 30s.

### Incremental Updates

Full rebuilds only on: first install, explicit user request, FAISS version migration.

### Initial Build Progress

```
Knowledge: indexing Obsidian vault (2,847 / 10,432 notes)...
Knowledge: indexing BookLore library (142 / 380 books)...
```

Skill is functional for already-indexed content immediately.

---

## Tool Interface

Four tools ship with the Knowledge Skill. `knowledge_search` and `knowledge_graph` are Phase 2. `knowledge_analogy` and `knowledge_dream` are Phase 3.

Agent access to `knowledge_analogy` and `knowledge_dream` is governed by the `allowed_modes` field in each agent's manifest. See `DREAM_LOGIC.md` §5 for the selectivity spec.

---

### `knowledge_search`

Hybrid retrieval (dense + sparse + RRF fusion). The primary tool — covers the majority of agent retrieval needs.

```json
{
  "name": "knowledge_search",
  "description": "Search the user's knowledge base (Obsidian vault, BookLore library, and other connected sources) for content relevant to a query. Uses hybrid dense+sparse retrieval with RRF fusion and optional cross-encoder re-ranking.",
  "parameters": {
    "query": "string — the search query",
    "limit": "integer (optional) — max results (default: 5, max: 20)",
    "sources": "string[] (optional) — filter to specific sources: ['vault', 'booklore']",
    "tags": "string[] (optional) — filter by tags (vault source only)",
    "use_hyde": "boolean (optional) — use HyDE (Hypothetical Document Embeddings) for deep conceptual queries; adds ~500ms (default: false)"
  },
  "returns": {
    "results": "SearchResult[]"
  }
}
```

**`SearchResult` schema:**
```json
{
  "chunk_id": "string",
  "source": "string — 'vault' | 'booklore'",
  "title": "string — note or book title",
  "path": "string — filesystem path",
  "section": "string (vault only) — header section the chunk is from",
  "chapter": "string (booklore only) — chapter the chunk is from",
  "tags": "string[] (vault only)",
  "author": "string (booklore only)",
  "text": "string — chunk content",
  "score": "float — RRF fusion score (higher = more relevant)"
}
```

### `knowledge_graph`

```json
{
  "name": "knowledge_graph",
  "description": "Traverse the wikilink graph from a starting vault note. Vault source only; requires wikilink graph layer (opt-in).",
  "parameters": {
    "note_path": "string — path to the starting note (e.g. '~/Documents/MyVault/Projects/Polly.md')",
    "hops": "integer — traversal depth (default: 1, max: 3)"
  },
  "returns": {
    "nodes": "NoteNode[] — each node: { note_id, note_title, path, tags, domain }",
    "edges": "WikilinkEdge[] — each edge: { from_id, to_id, link_text }",
    "root": "string — note_id of the starting note"
  }
}
```

### `knowledge_analogy`

Structural analogy retrieval — finds notes whose *relational structure* matches the current context, not surface vocabulary. LLM-based structural pattern classification at index time; vocabulary mapping generated at retrieval time. Phase 3 feature. See `STRUCTURAL_ANALOGY.md` for full architecture.

```json
{
  "name": "knowledge_analogy",
  "description": "Find notes from the vault that share structural patterns with the current context — cross-domain analogies based on relational shape, not vocabulary. Uses LLM-classified structural pattern tags. Only available to agents with 'analogy' in allowed_modes.",
  "parameters": {
    "context": "string — the problem or situation currently being worked on",
    "source_domain": "string (optional) — constrain source to this domain (Practice Layer taxonomy)",
    "target_domain": "string (optional) — constrain target to this domain",
    "patterns": "string[] (optional) — filter to specific structural pattern IDs (e.g. ['feedback-loop', 'threshold-behavior'])",
    "limit": "integer (optional) — max results (default: 3)"
  },
  "returns": {
    "results": "AnalogyResult[]"
  }
}
```

**`AnalogyResult` schema:**
```json
{
  "note_id": "string",
  "note_title": "string",
  "domain": "string — Practice Layer domain label",
  "matched_patterns": "string[] — structural pattern IDs that drove the match",
  "pattern_confidence": "float — confidence that the matched patterns apply (0.0–1.0)",
  "vocabulary_mapping": "string[] — cross-domain term mappings, format: 'Your [source concept] = their [target concept]'",
  "mapping_confidence": "float — confidence that the vocabulary mapping holds (0.0–1.0)"
}
```

### `knowledge_dream`

Structured misretrieval — deliberately targets the FAISS distance band 0.5–0.7, the uncanny valley between obvious relevance and noise. Returns connections that exist but have not yet been named. Agent behavior is **inverted**: results are surfaced *without* explanation. See `DREAM_LOGIC.md` for full architecture and agent selectivity rules.

```json
{
  "name": "knowledge_dream",
  "description": "Retrieve notes in the FAISS distance band 0.5–0.7 relative to the current context — non-arbitrary connections that haven't been consciously made. The agent MUST NOT explain why results are relevant. Surface the collision and stop. Only available to agents with 'dream' in allowed_modes.",
  "parameters": {
    "context": "string — what is currently being thought about (anchors the distance band)",
    "distance_min": "float (optional) — lower bound of distance band (default: 0.5)",
    "distance_max": "float (optional) — upper bound of distance band (default: 0.7)",
    "exclude_domain": "string (optional) — exclude results from this domain (Practice Layer taxonomy) to force cross-domain collisions",
    "limit": "integer (optional) — max results (default: 3, spec maximum — Dream Logic is a collision generator, not a result list)"
  },
  "returns": {
    "results": "DreamResult[]"
  }
}
```

**`DreamResult` schema:**
```json
{
  "note_id": "string",
  "note_title": "string",
  "domain": "string — Practice Layer domain label",
  "distance": "float — FAISS distance score (will be in range [distance_min, distance_max])",
  "collision_context": "null — always null; the agent does not generate explanation"
}
```

**Agent behavior contract for `knowledge_dream`:**
The calling agent MUST present the result title and a brief excerpt, prefaced with something equivalent to: *"I don't know why this is relevant. Do you?"* The agent does not explain. The agent does not withhold an explanation it has — it genuinely has none to give. Interpretation belongs to Brett. An agent that explains a dream result has defeated the purpose of Dream Logic.

---

## Degradation Paths and Retrieval Confidence

### Retrieval Classification: DIRECT / ADJACENT / ABSENT

Every retrieval result carries a confidence classification that shapes how agents communicate what they know. This classification is not optional — it is an epistemological signal that must reach the agent.

**Classification tiers:**

| Tier | Meaning | FAISS score range | Agent behavior |
|------|---------|-------------------|----------------|
| `DIRECT` | High-confidence match — the query is well-represented in the index | score ≥ 0.75 | Agent can assert with confidence. "Your notes on X say..." |
| `ADJACENT` | Partial match — related content, not exact | 0.45 ≤ score < 0.75 | Agent should qualify. "Your notes don't address X directly, but Y is related..." |
| `ABSENT` | No meaningful match — query is not represented in the corpus | score < 0.45 | Agent must be honest. "I didn't find anything on X in your knowledge base. This is my general knowledge, not something from your notes." |

The classification is added to the `SearchResult` schema:

```json
{
  "chunk_id": "string",
  "source": "string",
  "title": "string",
  ...existing fields...,
  "score": "float — RRF fusion score",
  "retrieval_tier": "DIRECT | ADJACENT | ABSENT"
}
```

For `ABSENT` results, the tool returns an empty results array with a top-level `retrieval_tier: "ABSENT"` field rather than returning low-confidence chunks.

**Informed by:** `core/hardened/classifier.py` (DualValidator, RetrievalClassifier) from salvage audit. The DIRECT/ADJACENT/ABSENT distinction was hard-won in the original codebase and must be preserved.

---

### Failure Modes and Fallbacks

| Failure | Detection | Fallback |
|---------|-----------|---------|
| **Index stale** | `dirty.json` last-processed timestamp > staleness threshold (configurable, default 24h) | Surface staleness warning in skill status card. Continue serving from stale index — stale retrieval beats no retrieval. Log: `knowledge: index stale since [timestamp], serving cached results` |
| **Index corrupt** | FAISS load exception on startup | Return `ABSENT` classification for all queries. Surface error in skill status card: "Knowledge index needs rebuilding." Offer "Rebuild Index" action. Do not silently serve empty results. |
| **Embedding model failure** | Exception during embed() call | Circuit breaker: mark embedding service unhealthy. Fall back to sparse-only retrieval (BM25). Surface degraded-mode indicator. Reset circuit breaker after 60s. |
| **File watcher failure** | Watcher thread exits unexpectedly | Log and restart watcher with exponential backoff (1s, 2s, 4s, max 30s). Surface watcher-error indicator in skill settings after 3 failed restarts. |
| **Out of memory** | OOM on FAISS load | Reduce HNSW ef_construction. If still OOM, surface error: "Knowledge index too large for available memory — try reducing your vault size or rebuilding with a lighter model." |

**Circuit breaker pattern (embedding):**
```
CLOSED → [embed fails] → OPEN → [60s] → HALF-OPEN → [test embed]
    ↑                                                      |
    └──────────────────[success]───────────────────────────┘
```

**Staleness indicator:** Skill status card shows last-synced timestamp. If stale, amber badge. If corrupt/failed, red badge with "Rebuild" action. These states surface in the skill settings screen (§ UI Integration above), not in the main chat UI — don't interrupt the conversation with index hygiene.

---

### Domain Taxonomy Reconciliation

The iOS client and the Knowledge Skill have two different views of domains, and they must be reconciled:

- **iOS (Phase 1):** User-declared domains — name, color, icon, keyword list. Stored in MMKV `"polly.domains"`. Client-side auto-detection via keyword matching.
- **Knowledge Skill (Phase 3):** Emergent domains discovered from vault structure — wikilink cluster analysis, note density, cross-link patterns.

These are not competing approaches. They are a bootstrap→validate pipeline:

1. **Phase 1:** iOS domains seed the taxonomy. The `polly.domains` MMKV value is synced to the gateway via `config.patch` as `polly.knowledge.domain_seeds`.
2. **Phase 2:** The Knowledge Skill reads `polly.knowledge.domain_seeds` as the initial domain list. Vault notes are tagged with user-declared domain labels based on keyword matching (same logic as client-side, server-side).
3. **Phase 3:** The domain-label-enricher index hook runs cluster analysis on the wikilink graph. It identifies whether vault structure confirms, refines, or contradicts the user-declared domains. Discrepancies surface as suggestions: "Your notes tagged 'Systems' and 'Code' are heavily interlinked — consider merging these domains or creating a bridge domain."

The user-declared domains are never silently overridden. The graph analysis enriches them.

---

### Skill Settings: Knowledge Sources

Source management lives inside the skill's settings screen — not the main app Settings. Source cards:

```
┌─────────────────────────────────┐
│ 📓 Obsidian Vault          ✅  │
│ ~/Documents/MyVault             │
│ 14,832 chunks · synced 2m ago   │
│                          [Edit] │
├─────────────────────────────────┤
│ 📚 BookLore Library        ✅  │
│ /opt/booklore/library           │
│ 8,201 chunks · synced 1h ago    │
│                          [Edit] │
├─────────────────────────────────┤
│  + Add Knowledge Source         │
└─────────────────────────────────┘
```

Each card expands to show: path config, sync schedule, last sync timestamp, chunk count, include/exclude toggle, "Rebuild Index" action.

**Add Source picker:** "Obsidian Vault" | "BookLore" | (coming soon: Notion, PDF folder, ...)

### Chat UI: Source Filter Chips

When the Knowledge skill is active, a filter chip row appears above the input:

```
[ All Sources ]  [ Vault ]  [ Books ]
```

Lightweight — there but not prominent. Power users will want it; others ignore it.

---

## Permissions Manifest

```json
{
  "name": "knowledge",
  "version": "1.0.0",
  "description": "Semantic search over your personal knowledge base — Obsidian vault, BookLore library, and more.",
  "permissions": {
    "files": [
      "read:vault",
      "read:filesystem:{booklore_library_path}"
    ],
    "network": []
  }
}
```

`{booklore_library_path}` is resolved at install time from user config — not hardcoded. The permissions UI must handle arbitrary declared paths gracefully (@security_audit note: this is a new permission category beyond the hardcoded vault case).

**`network: []`** — zero outbound calls. Hard constraint.

---

## Security Model

### Path Confinement
The skill runner enforces declared paths only. Path traversal and symlink escapes blocked at gateway layer regardless of skill code.

### Index Sandboxing
Index stored in `~/.openclaw/skills/knowledge/index/` — sandboxed, not readable by other skills.

### Network Sandboxing Gate
**Cannot ship until @security_audit verifies `network: []` enforcement.** A skill that can silently make outbound calls is a data-exfil risk.

### Permission-Expanding Updates
Any update adding permissions triggers full re-approval flow with new permission highlighted in amber.

### Security Acceptance Criteria
- [ ] Vault path confinement verified with path traversal test suite
- [ ] BookLore path confinement verified (arbitrary user-configured path)
- [ ] **Arbitrary path permissions — five constraints (@security_audit sign-off 2026-03-25):**
  - [ ] Paths normalized to absolute at install time, stored as resolved
  - [ ] Prefix-strict enforcement with trailing slash — no parent-path reads
  - [ ] Path change = new permission grant, biometric re-auth required
  - [ ] Plain-language path display in UI ("You chose this location")
  - [ ] Freeform manual path entry shows explicit warning callout
- [ ] Index sandboxed and not accessible to other skills
- [ ] `network: []` enforcement verified — no outbound calls possible
- [ ] Permission-expanding update flow tested
- [ ] @security_audit final sign-off

---

## Implementation Checklist

### Phase 2 — Core Skill

**Shared pipeline:**
- [ ] Skill scaffold (manifest, gateway registration, tool declarations)
- [ ] Shared HNSW index with source metadata tagging
- [ ] SBERT embedding pipeline (local, BGE-large-en default)
- [ ] SBERT sparse encoder (unified pipeline)
- [ ] RRF fusion
- [ ] Cross-encoder re-ranking
- [ ] `knowledge_search` tool with source filter support
- [ ] File watcher infrastructure + dirty-flag incremental updates
- [ ] Index progress reporting
- [ ] **Index hooks extension point** (`hooks.json` registry, `IndexHook` interface — Phase 2 ships with zero hooks; hooks registered by Phase 3 features)
- [ ] **Retrieval confidence classification** (DIRECT / ADJACENT / ABSENT tiers — added to `SearchResult` schema)
- [ ] **Degradation handling:** staleness detection, index-corrupt fallback, embedding circuit breaker, watcher restart with backoff
- [ ] Security acceptance criteria — @security_audit gate

**Obsidian adapter:**
- [ ] Vault crawler (respects `.vaultignore` if present)
- [ ] Structure-aware chunker (frontmatter, headers, wikilinks, tags)
- [ ] **Wikilink graph store** (SQLite `graph.db` — notes + wikilinks tables, dangling link handling, incremental updates on dirty-flag cycle)
- [ ] `knowledge_graph` tool

**BookLore adapter:**
- [ ] EPUB parser (`ebooklib`)
- [ ] Chapter-boundary chunking
- [ ] BookLore library path config + file watcher
- [ ] Manifest permission: `read:filesystem:{path}`

**Conversation history adapter (Phase 2 foundation — full feature Phase 3):**
- [ ] Memory file watcher (`memory/YYYY-MM-DD.md` from all agents)
- [ ] Section-header chunking with agent/date/section metadata
- [ ] Indexed alongside vault + booklore in shared HNSW index, tagged `source: "conversation"`

**Domain taxonomy:**
- [ ] Read `polly.knowledge.domain_seeds` from gateway config (synced from iOS `polly.domains` via config.patch)
- [ ] Apply user-declared domain labels to vault notes at ingest time via keyword matching

**UI:**
- [ ] Source cards (settings screen)
- [ ] Add Source picker (Obsidian, BookLore; others: coming soon)
- [ ] Filter chip row in chat UI (add "Conversations" filter chip)
- [ ] Index progress status surface
- [ ] Staleness/error indicators (amber/red badge in skill settings)

### Phase 2 — Graph Layer (opt-in)

- [ ] GraphRAG integration for wikilink graph

### Phase 3 — Enhancements

- [ ] HyDE mode
- [ ] Query expansion (opt-in)
- [ ] `knowledge_analogy` tool
  - [ ] Structural pattern taxonomy (~15 core patterns)
  - [ ] LLM classification pass at index time (async, dirty-flag schedule) — registered as `structural-pattern-tagger` index hook
  - [ ] Domain label derivation from wikilink cluster — registered as `domain-label-enricher` index hook
  - [ ] Vocabulary mapping generation at retrieval time
  - [ ] `allowed_modes: ['analogy']` gating in agent manifest schema
- [ ] `knowledge_dream` tool
  - [ ] FAISS distance-band query (k=200 initial search, filter to 0.5–0.7 band)
  - [ ] Domain exclusion (`exclude_domain` filter)
  - [ ] `allowed_modes: ['dream']` gating in agent manifest schema
  - [ ] Agent behavior contract enforcement: no explanation, collision only
- [ ] Conversation history adapter — full feature
  - [ ] OpenClaw session export adapter (requires OpenClaw session data exposure)
  - [ ] `rhetorical-structure-extractor` index hook (Epistemic Immune System consumer)
  - [ ] Mental model usage extraction (Metacognitive Dashboard consumer)
- [ ] Domain taxonomy enrichment — cluster analysis pass on wikilink graph (Phase 3 domain-label-enricher hook)
- [ ] FLARE (forward-looking active retrieval — per FlashRAG benchmarks, arXiv:2405.13576)
- [ ] Iter-RetGen (iterative retrieval-generation — multi-hop queries)
- [ ] Notion adapter (evaluate LlamaHub Notion loader first — check freshness, incremental indexing support, metadata fidelity before adopting)
- [ ] PDF folder adapter (evaluate LlamaHub PDF loader)
- [ ] Google Drive adapter (LlamaHub loader maintained by Google — higher trust)
- [ ] YouTube transcript adapter
> **LlamaHub note:** Loaders vary in maintenance quality. Before adopting any as a dependency: check last commit date, open issues, and LlamaIndex API version compatibility (v0.x vs v0.10+ — breaking change). Ref: https://llamahub.ai
- [ ] Multi-vault support (multiple Obsidian vaults)
- [ ] Domain-aware retrieval (filter by domain tags configured in §11.2)

---

## Open Questions

All resolved:

1. **Embedding model as skill setting** — Yes. BGE-large-en default (quality), Qwen3-Embedding-0.6B as lightweight option. Exposed as a skill setting.
2. **Large vault/library build time warning** — Yes. Warn users with >10k notes or large EPUB libraries about expected initial build time.
3. **BookLore filesystem vs API** — Filesystem for Phase 2. Simpler, no outbound calls, fits zero-network trust model. API adapter deferred to Phase 3+.

---

*The knowledge base is the user's mind, externalized. This skill is what makes every other Polly capability meaningful.*
