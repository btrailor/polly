# Vault RAG Skill
## Polly Spec | Last updated: 2026-03-25

> *Polly's identity is "AI that knows your work." Without this skill, agents are generic chat. With it, they're operating on your actual knowledge graph.*

---

## Problem Statement

The original Polly app ran a Python backend server that handled semantic retrieval over the user's Obsidian vault. In the iOS-first OpenClaw architecture, that Python backend is gone. Phase 1 vault integration is client-side only — the user manually selects a note and it's prepended to a message. That's augmentation, not retrieval.

This leaves a core capability gap: agents cannot proactively surface what the user knows. They can't answer "what have I written about X?", connect a current conversation to past work, or reason across the vault. This skill fills that gap.

**This is not a Phase 3 aspirational feature. This is what makes Polly Polly.**

---

## Architecture

### Where It Runs

The Vault RAG Skill runs on the **gateway machine** alongside OpenClaw — not on the iPhone. It is implemented as an OpenClaw skill installed by the user via the Skills Marketplace (Phase 2). The iOS client never calls it directly. Agents tool-call it as needed.

```
iPhone (Polly iOS)
    ↓ sends message
OpenClaw Gateway
    ↓ agent decides to retrieve
Vault RAG Skill (running on gateway machine)
    ↓ reads from
Obsidian vault (local filesystem)
    ↓ returns ranked results
Agent incorporates into response
    ↓
iPhone receives response
```

### No Cloud. No Python Server.

The skill runs entirely on the gateway machine. All embeddings are computed locally using sentence-transformers. No API calls to embedding services. No data leaves the machine. The vault stays local.

---

## Retrieval Architecture

### Primary: Hybrid Retrieval (Dense + Sparse + RRF Fusion)

**Why hybrid, not pure dense:**
Obsidian notes are fragments, not documents. A note might be 3 bullet points, a half-finished idea, a name and phone number, or a project title with no body. Dense retrieval alone (semantic similarity) fails on short/sparse content — not enough signal. Sparse (keyword) retrieval handles those cases. Hybrid covers both.

**Stack:**
- **Dense:** FAISS index with SBERT embeddings (`all-MiniLM-L6-v2` — fast, small, local)
- **Sparse:** BM25 via `rank_bm25` (pure Python, zero additional dependencies)
- **Fusion:** Reciprocal Rank Fusion (RRF) — combines dense and sparse rankings without requiring score normalization

```python
# RRF fusion (k=60 standard)
def rrf_score(rank, k=60):
    return 1 / (k + rank)

final_score = rrf_score(dense_rank) + rrf_score(sparse_rank)
```

### Chunking: Structure-Aware, Not Fixed-Size

Obsidian notes have structure that naive chunking destroys. The indexer preserves:

- **Frontmatter** (title, tags, aliases, date) indexed as filterable metadata — not chunked into body text
- **Headers** (H1–H3) used as chunk boundaries — each section is a semantic unit
- **Wikilinks** (`[[note title]]`) extracted and stored as a separate adjacency structure (see Graph Layer below)
- **Tags** (#tag) indexed as metadata for filtered retrieval
- **Minimum chunk size:** 50 tokens. Notes shorter than this are indexed as a single unit.

### Secondary: Wikilink Graph Layer

Standard RAG ignores the `[[wikilink]]` graph — the most valuable signal in an Obsidian vault. The skill maintains a separate adjacency structure:

```
note_id → [linked_note_ids]
```

This enables relationship queries that FAISS cannot answer:
- "What notes connect to this one?"
- "What is this note part of?"
- "Show me everything linked from my weekly review for March 10"

GraphRAG (microsoft/graphrag) is the reference implementation for this layer. Due to its indexing cost, the graph layer is **opt-in** — users with large, well-linked vaults can enable it. Default install uses FAISS + BM25 only.

### Optional: HyDE (Hypothetical Document Embeddings)

For deep conceptual queries ("what have I written about the nature of expertise?"), HyDE improves retrieval by generating a hypothetical answer first, then retrieving against that embedding rather than the raw query.

**Not default** — adds ~500ms latency. Activated when the agent determines the query is conceptual rather than factual.

---

## Index Freshness

Obsidian vaults change constantly. A stale index is a broken feature.

### File Watcher

The skill registers a filesystem watcher on the vault root on startup. Events:

| Event | Action |
|-------|--------|
| File created | Add to index queue |
| File modified | Mark as dirty, re-index on next cycle |
| File deleted | Remove from FAISS index + BM25 corpus |
| File renamed | Remove old, add new |

### Incremental Updates (Not Full Rebuilds)

FAISS supports incremental add/remove. Full rebuilds are only triggered:
- On first install (initial index build)
- On explicit user request ("Rebuild vault index")
- After a FAISS version migration

Dirty-flag tracking: a `~/.openclaw/skills/vault-rag/dirty.json` file tracks files changed since last index. On each watcher cycle (default: 30s), dirty files are re-indexed and the flag cleared.

### Initial Index Build

On first install, the skill crawls the vault and builds the full index. For large vaults (10k+ notes) this may take several minutes. Progress is reported via a gateway event that Polly surfaces as a status message:

```
Vault RAG: indexing your vault (2,847 / 10,432 notes)...
```

The skill is functional for already-indexed notes immediately — it doesn't wait for full completion.

---

## Tool Interface

The skill registers two tools on the gateway:

### `vault_search`

```json
{
  "name": "vault_search",
  "description": "Search the user's Obsidian vault for notes relevant to a query. Returns ranked note excerpts with titles, paths, and relevance scores.",
  "parameters": {
    "query": "string — the search query",
    "limit": "integer — max results to return (default: 5, max: 20)",
    "tags": "string[] — optional: filter to notes with these tags",
    "use_hyde": "boolean — optional: use HyDE for conceptual queries (default: false)"
  }
}
```

### `vault_graph`

```json
{
  "name": "vault_graph",
  "description": "Traverse the wikilink graph from a starting note. Returns connected notes up to N hops away.",
  "parameters": {
    "note_path": "string — path to the starting note",
    "hops": "integer — graph traversal depth (default: 1, max: 3)"
  }
}
```

---

## Permissions Manifest

Per §8.8.2, the skill declares:

```json
{
  "name": "vault-rag",
  "version": "1.0.0",
  "description": "Semantic search over your Obsidian vault. Agents can find and surface relevant notes during conversation.",
  "permissions": {
    "files": ["read:vault"],
    "network": []
  }
}
```

**`network: []`** — this skill makes zero outbound network calls. All embeddings are local. This is a hard constraint, not a default.

---

## Security Model

Per §8.8 and @security_audit review:

### Vault Path Confinement
The skill runner enforces that `read:vault` means files within the declared vault directory only. Path traversal (`../../etc/passwd`) and symlink escapes are blocked at the gateway layer. The skill cannot read outside the approved root regardless of what the skill code requests.

### Index File Security
The FAISS index and BM25 corpus are stored in `~/.openclaw/skills/vault-rag/index/` — sandboxed workspace, not readable by other skills. The index is treated as vault-sensitivity content.

### Network Sandboxing Gate
**The vault RAG skill cannot be released until gateway-level network sandboxing is verified.** A skill with `network: []` that can make outbound calls anyway is a silent data-exfil risk. @security_audit sign-off required before this skill ships.

### Permission-Expanding Updates
Any skill update that adds permissions (e.g., adding a `network` domain) triggers the full install re-approval flow with the new permission highlighted in amber. Silent permission expansion is blocked by the update flow (§8.8 update protocol).

### Security Acceptance Criteria (@security_audit gate)
- [ ] Vault path confinement verified with path traversal test suite
- [ ] Index stored in sandboxed workspace, verified not accessible to other skills
- [ ] `network: []` enforcement verified — skill cannot make outbound calls
- [ ] Permission-expanding update flow tested and confirmed
- [ ] @security_audit sign-off

---

## Implementation Checklist

### Phase 2 — Core Skill

- [ ] Skill scaffold (manifest, gateway registration, tool declarations)
- [ ] Vault crawler (respects `.gitignore`-style `.vaultignore` if present)
- [ ] Structure-aware chunker (frontmatter, headers, wikilinks, tags)
- [ ] SBERT embedding pipeline (local, `all-MiniLM-L6-v2`)
- [ ] FAISS index (incremental add/remove)
- [ ] BM25 corpus (`rank_bm25`)
- [ ] RRF fusion
- [ ] `vault_search` tool
- [ ] File watcher + dirty-flag incremental updates
- [ ] Initial index progress reporting
- [ ] Security acceptance criteria (above) — @security_audit gate

### Phase 2 — Graph Layer (opt-in)

- [ ] Wikilink adjacency structure
- [ ] `vault_graph` tool
- [ ] GraphRAG integration (optional, for users who enable it)

### Phase 3 — Enhancements

- [ ] HyDE mode for conceptual queries
- [ ] Notion vault backend (alternative to Obsidian filesystem)
- [ ] PDF ingestion via `boof` skill integration
- [ ] Domain-aware retrieval (filter by domain tags configured in §11.2)

---

## Open Questions

1. **Embedding model:** `all-MiniLM-L6-v2` is the default recommendation (fast, 384-dim, good for short texts). Should we offer a higher-quality option (`all-mpnet-base-v2`, 768-dim) for users who prioritize quality over speed? Recommend: make this a skill setting, default to MiniLM.

2. **Vault size limits:** No hard limit planned — FAISS handles millions of vectors. But initial index build time scales linearly. Should we warn users with large vaults (>10k notes) about expected build time?

3. **Multi-vault support:** Some users have multiple Obsidian vaults. Phase 2: single vault only. Phase 3+: configurable vault list.

---

*The vault is the user's mind, externalized. RAG over it is the feature that makes every other Polly capability meaningful.*
