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

### `knowledge_search`

```json
{
  "name": "knowledge_search",
  "description": "Search the user's knowledge base (Obsidian vault, BookLore library, and other connected sources) for content relevant to a query.",
  "parameters": {
    "query": "string — the search query",
    "limit": "integer — max results (default: 5, max: 20)",
    "sources": "string[] — optional: filter to specific sources ['vault', 'booklore']",
    "tags": "string[] — optional: filter by tags (vault source only)",
    "use_hyde": "boolean — optional: use HyDE for conceptual queries (default: false)"
  }
}
```

### `knowledge_graph`

```json
{
  "name": "knowledge_graph",
  "description": "Traverse the wikilink graph from a starting vault note.",
  "parameters": {
    "note_path": "string — path to the starting note",
    "hops": "integer — traversal depth (default: 1, max: 3)"
  }
}
```

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
