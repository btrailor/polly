# Design: Phase 2 — Knowledge Skill

## Architecture Overview

```
iOS Client
  └── Source Cards UI (Settings)
  └── Filter Chips (Chat)
  └── Domain Config (MMKV polly.domains → polly.knowledge.domain_seeds)

Gateway
  └── Knowledge Skill (single service)
        ├── Tool Interfaces
        │     knowledge_search / knowledge_graph / knowledge_domains
        │     knowledge_register_hook / knowledge_conversation_history
        │
        ├── Shared Pipeline
        │     ├── FAISS HNSW Index (dense vectors)
        │     ├── BM25 Sparse Index
        │     ├── RRF Fusion
        │     ├── Cross-encoder Re-ranker
        │     └── Retrieval Classifier (DIRECT/ADJACENT/ABSENT)
        │
        ├── Adapters
        │     ├── Obsidian Vault Adapter
        │     │     └── Wikilink Graph Store (SQLite graph.db)
        │     ├── BookLore Adapter
        │     └── Conversation History Adapter (memory/*.md files)
        │
        ├── Index Hooks Registry (hooks.json — empty Phase 2)
        │
        └── File Watchers (dirty-flag, 30s cycle)
              └── dirty.json (per-source dirty registry)
```

## Component Specs

### Shared Pipeline

- **Embedding model:** BGE-large-en (local, via sentence-transformers). User-configurable in skill settings.
- **Sparse encoder:** BM25 (same sentence-transformers pipeline).
- **Fusion:** Reciprocal Rank Fusion (RRF, k=60). No hyperparameter tuning required.
- **Re-ranker:** Cross-encoder (ms-marco-MiniLM-L-6-v2). Runs on top-N from RRF. Optional (configurable).
- **Index format:** FAISS HNSW (M=32, ef_construction=200). Persisted at `~/.openclaw/skills/knowledge/index.faiss`.
- **Metadata store:** SQLite `index.db` — chunk_id, source, path, title, tags, section, etc.

### Wikilink Graph Store

SQLite at `~/.openclaw/skills/knowledge/graph.db`.

```sql
notes(note_id PK, title, path, tags JSON, domain NULLABLE, modified_at)
wikilinks(from_id, to_id NULLABLE, to_title, link_text)
```

Dangling links (to_id = NULL) resolved on next ingest cycle if target note created.

### File Watchers

One watcher per source. Uses `watchdog` (Python). 30-second debounce. On change:
1. Write changed file path to `dirty.json`
2. Ingest worker polls `dirty.json` every 30s
3. Chunk changed file → re-embed → update FAISS + metadata store + graph store
4. Remove from `dirty.json`

### Degradation / Circuit Breaker

| Failure | Response |
|---------|----------|
| Index stale (> 24h) | Amber badge in skill settings. Continue serving stale. |
| Index corrupt | Return ABSENT for all queries. Red badge + "Rebuild Index" action. |
| Embedding failure | Circuit breaker → sparse-only (BM25) fallback. Reset after 60s. |
| Watcher crash | Restart with backoff (1s, 2s, 4s → max 30s). Surface after 3 failures. |
| OOM | Reduce HNSW params. If still OOM, surface error with guidance. |

### Domain Taxonomy

1. iOS: user declares domains in Settings → stored in MMKV `polly.domains`
2. iOS syncs to gateway via `config.patch` as `polly.knowledge.domain_seeds`
3. Knowledge Skill reads seeds at startup → applies keyword matching to vault notes at ingest
4. Phase 3: domain-label-enricher hook runs wikilink cluster analysis → confirms/refines domains

### Prompt Injection Layer Hierarchy (locked)

| Layer | Content | Owner |
|-------|---------|-------|
| 7 | Constitutional epistemology | Gateway (`polly.constitutional.layer`) |
| 6 | EIS flags (Phase 3) | Gateway (`polly.epistemic.flags`) |
| 5 | Theme behavior | Gateway (`polly.ios.aestheticStance`) |
| 4 | Plan context (Phase 2 swarm) | Gateway |
| 3 | Group chat header (Phase 2) | Gateway |
| 2 | Domain context hint | iOS client |
| 1 | Mental model framing + vault note | iOS client |

## Files Created / Modified

| File | Status |
|------|--------|
| `openspec/specs/knowledge/knowledge-skill.md` | Complete |
| `openspec/specs/knowledge/service-contracts.md` | Complete — @backend §4 pending |
| `openspec/specs/agent-system/agent-templates.md` | Updated — `## Reasoning` section, Epistemological Commitments |
| `openspec/specs/ios-app/ios-spec.md` | Needs update — source cards UI, filter chips, domain config sync |

## Security Considerations

- Skill manifest must declare `read:filesystem:{vault_path}` and `read:filesystem:{booklore_path}`
- `network: []` — no network access. Strictly enforced.
- Conversation history corpus is the highest-sensitivity data. Never leaves gateway machine.
- @security_audit review required before Phase 2 ships.
