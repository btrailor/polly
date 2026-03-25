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
- **Wikilinks** (`[[note title]]`) → extracted into adjacency structure (graph layer)
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

## UI Integration

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
- [ ] Security acceptance criteria — @security_audit gate

**Obsidian adapter:**
- [ ] Vault crawler (respects `.vaultignore` if present)
- [ ] Structure-aware chunker (frontmatter, headers, wikilinks, tags)
- [ ] Wikilink adjacency structure
- [ ] `knowledge_graph` tool

**BookLore adapter:**
- [ ] EPUB parser (`ebooklib`)
- [ ] Chapter-boundary chunking
- [ ] BookLore library path config + file watcher
- [ ] Manifest permission: `read:filesystem:{path}`

**UI:**
- [ ] Source cards (settings screen)
- [ ] Add Source picker (Obsidian, BookLore; others: coming soon)
- [ ] Filter chip row in chat UI
- [ ] Index progress status surface

### Phase 2 — Graph Layer (opt-in)

- [ ] GraphRAG integration for wikilink graph

### Phase 3 — Enhancements

- [ ] HyDE mode
- [ ] Query expansion (opt-in)
- [ ] `knowledge_analogy` tool
  - [ ] Structural pattern taxonomy (~15 core patterns)
  - [ ] LLM classification pass at index time (async, dirty-flag schedule)
  - [ ] Domain label derivation from wikilink cluster
  - [ ] Vocabulary mapping generation at retrieval time
  - [ ] `allowed_modes: ['analogy']` gating in agent manifest schema
- [ ] `knowledge_dream` tool
  - [ ] FAISS distance-band query (k=200 initial search, filter to 0.5–0.7 band)
  - [ ] Domain exclusion (`exclude_domain` filter)
  - [ ] `allowed_modes: ['dream']` gating in agent manifest schema
  - [ ] Agent behavior contract enforcement: no explanation, collision only
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
