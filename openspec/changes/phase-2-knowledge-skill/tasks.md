# Phase 2: Knowledge Skill

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete  
**Spec source:** `KNOWLEDGE_SKILL.md`, `KNOWLEDGE_SERVICE_CONTRACTS.md`  
**Pre-ship gate:** @security_audit sign-off required

## Goal

Give Polly access to the user's personal knowledge base — Obsidian vault, BookLore library, conversation history — via a unified retrieval service. Unblocks all Phase 3 cognitive features.

## Design

Single service model. One FAISS HNSW index. All Phase 3 features consume via tool interfaces. See `KNOWLEDGE_SKILL.md` for full architecture.

## Tasks

### Gateway — Skill Scaffold
- [ ] Skill directory under `src/skills/knowledge/`
- [ ] `manifest.json`: tool declarations, filesystem permissions, `network: []`
- [ ] Register skill with OpenClaw gateway
- [ ] Stub all 5 tool handlers

### Gateway — Shared Pipeline
- [ ] BGE-large-en embedding pipeline (sentence-transformers, local)
- [ ] BM25 sparse encoder
- [ ] FAISS HNSW index (M=32, ef_construction=200) with persistence
- [ ] RRF fusion (k=60)
- [ ] Cross-encoder re-ranker (ms-marco-MiniLM-L-6-v2) — optional per config
- [ ] DIRECT / ADJACENT / ABSENT retrieval classification
- [ ] SQLite chunk metadata store (`index.db`)
- [ ] Index hooks registry (`hooks.json`, hot-reload) — ships empty

### Gateway — Obsidian Adapter
- [ ] Vault crawler (respects `.vaultignore`)
- [ ] Structure-aware chunker (frontmatter, H1–H3 headers, min 50 token chunks)
- [ ] Wikilink extractor → SQLite `graph.db` (dangling link handling)
- [ ] File watcher (watchdog, 30s debounce, `dirty.json`)
- [ ] Incremental update pipeline
- [ ] `knowledge_graph` tool (BFS/DFS, max 3 hops)

### Gateway — BookLore Adapter
- [ ] EPUB parser (ebooklib)
- [ ] Chapter-boundary chunker
- [ ] Library path config + file watcher

### Gateway — Conversation History Adapter
- [ ] Memory file watcher (all agent `memory/YYYY-MM-DD.md`)
- [ ] Section-header chunker (agent_id, date, section metadata)
- [ ] Index in shared FAISS tagged `source: "conversation"`
- [ ] `knowledge_conversation_history` tool (date + agent + section filters)

### Gateway — Domain Taxonomy
- [ ] Read `polly.knowledge.domain_seeds` from gateway config
- [ ] Keyword-match domain labels to vault notes at ingest
- [ ] `knowledge_domains` tool

### Gateway — Degradation
- [ ] Staleness detection (24h threshold) → amber badge signal
- [ ] Corrupt index → ABSENT fallback + red badge signal
- [ ] Embedding circuit breaker (sparse-only fallback, 60s reset)
- [ ] Watcher restart (exponential backoff, surface after 3 failures)

### iOS — Source Cards UI
- [ ] Knowledge Settings screen: source cards (Obsidian, BookLore)
- [ ] Add Source picker with "coming soon" slots
- [ ] Index progress indicator + last-synced timestamp
- [ ] Staleness/error badges (amber/red + "Rebuild Index" action)
- [ ] Vault path picker
- [ ] BookLore library path picker

### iOS — Chat Integration
- [ ] Filter chip row (All, Vault, Books, Conversations)
- [ ] Filter state → `sources` param in `knowledge_search`
- [ ] Domain config sync: MMKV `polly.domains` → `polly.knowledge.domain_seeds` via config.patch

### iOS Spec Update
- [ ] Add source cards section to `POLLY_IOS_SPEC.md`
- [ ] Add filter chip row spec to chat section
- [ ] Add domain config sync spec to domain system section

### Security Review — @security_audit [REQUIRED BEFORE SHIP]
- [ ] [BLOCKED: needs skill + iOS tasks complete] Manifest permission audit
- [ ] Conversation corpus access controls
- [ ] BookLore/vault path traversal protection
- [ ] Sign-off

### Backend — Pending
- [ ] [BLOCKED: @backend §4 review] Finalize config read path caching (session vs. request scoped, Layer 5/6)
- [ ] `manifest.json` Phase 1 export hook (@backend owns — `COGNITIVE_ARTIFACT.md §4`)

## Done when
All tasks checked. @security_audit sign-off. Filter chips working in chat. Vault + BookLore indexing on device.
