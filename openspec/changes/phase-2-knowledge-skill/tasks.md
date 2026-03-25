# Tasks: Phase 2 — Knowledge Skill

## Gateway — Skill Scaffold
- [ ] 1.1 Create skill directory structure under `src/skills/knowledge/`
- [ ] 1.2 Write skill manifest (`manifest.json`): tool declarations, filesystem permissions, `network: []`
- [ ] 1.3 Register skill with OpenClaw gateway
- [ ] 1.4 Stub all 5 tool handlers (knowledge_search, knowledge_graph, knowledge_domains, knowledge_register_hook, knowledge_conversation_history)

## Gateway — Shared Pipeline
- [ ] 2.1 Integrate sentence-transformers BGE-large-en embedding pipeline
- [ ] 2.2 Implement BM25 sparse encoder (unified pipeline)
- [ ] 2.3 Build FAISS HNSW index (M=32, ef_construction=200) with persistence
- [ ] 2.4 Implement RRF fusion (k=60)
- [ ] 2.5 Integrate cross-encoder re-ranker (ms-marco-MiniLM-L-6-v2) — optional per config
- [ ] 2.6 Implement DIRECT/ADJACENT/ABSENT retrieval classification (score thresholds: ≥0.75 DIRECT, 0.45–0.75 ADJACENT, <0.45 ABSENT)
- [ ] 2.7 Build chunk metadata store (SQLite `index.db`)
- [ ] 2.8 Implement index hooks registry (`hooks.json` hot-reload, `IndexHook` interface) — ships empty

## Gateway — Obsidian Adapter
- [ ] 3.1 Vault crawler (respects `.vaultignore`)
- [ ] 3.2 Structure-aware chunker: frontmatter extraction, H1-H3 section boundaries, minimum 50 token chunks
- [ ] 3.3 Wikilink extractor → SQLite `graph.db` (notes + wikilinks tables, dangling link handling)
- [ ] 3.4 File watcher (watchdog, 30s debounce, dirty.json registry)
- [ ] 3.5 Incremental update pipeline (dirty-flag → re-chunk → re-embed → update index + graph)
- [ ] 3.6 `knowledge_graph` tool: BFS/DFS traversal with hop limit (max 3), returns NoteNode[] + WikilinkEdge[]

## Gateway — BookLore Adapter
- [ ] 4.1 EPUB parser (ebooklib)
- [ ] 4.2 Chapter-boundary chunker
- [ ] 4.3 BookLore library path config in skill settings
- [ ] 4.4 File watcher for BookLore library directory

## Gateway — Conversation History Adapter
- [ ] 5.1 Memory file watcher (all agent `memory/YYYY-MM-DD.md` files)
- [ ] 5.2 Section-header chunker (`##` boundaries, metadata: agent_id, date, section)
- [ ] 5.3 Index conversation chunks in shared FAISS index tagged `source: "conversation"`
- [ ] 5.4 `knowledge_conversation_history` tool: date-range + agent-id + section filtering

## Gateway — Domain Taxonomy
- [ ] 6.1 Read `polly.knowledge.domain_seeds` from gateway config on startup
- [ ] 6.2 Apply user-declared domain keyword matching to vault notes at ingest time
- [ ] 6.3 `knowledge_domains` tool: returns merged domain list with note_count

## Gateway — Degradation Handling
- [ ] 7.1 Staleness detection (24h threshold, configurable) → amber badge signal
- [ ] 7.2 Index corruption detection (FAISS load exception) → ABSENT fallback + red badge signal
- [ ] 7.3 Embedding circuit breaker (CLOSED→OPEN→HALF-OPEN, 60s reset, sparse-only fallback)
- [ ] 7.4 Watcher restart with exponential backoff (1s/2s/4s, max 30s, surface after 3 failures)

## iOS Client — Source Cards UI
- [ ] 8.1 Knowledge Skill source cards in Settings (Obsidian, BookLore)
- [ ] 8.2 Add Source picker with "coming soon" slots for future adapters
- [ ] 8.3 Index progress indicator (syncing state, last-synced timestamp)
- [ ] 8.4 Staleness/error badge display (amber = stale, red = failed, "Rebuild Index" action)
- [ ] 8.5 Vault path picker (file system browser or path input)
- [ ] 8.6 BookLore library path picker

## iOS Client — Chat Integration
- [ ] 9.1 Filter chip row in chat UI (All, Vault, Books, Conversations)
- [ ] 9.2 Filter chip state → `sources` param passed to `knowledge_search`
- [ ] 9.3 Domain config sync: MMKV `polly.domains` → gateway `polly.knowledge.domain_seeds` via config.patch

## Security Review — @security_audit
- [ ] 10.1 [BLOCKED: requires 8.1-8.6 + 1.1-1.3 complete] Skill manifest permission audit — filesystem access scope, network constraint enforcement
- [ ] 10.2 Conversation history access controls — ensure corpus is not accessible via any network-facing interface
- [ ] 10.3 BookLore/vault path traversal protection — skill must not be able to read outside declared paths
- [ ] 10.4 Sign off before Phase 2 ships to users

## Backend — Pending
- [ ] 11.1 [BLOCKED: awaiting @backend §4 review] Finalize config read path caching model for Layer 5/6 injection (session-scoped vs. request-scoped)
- [ ] 11.2 manifest.json Phase 1 export hook (per COGNITIVE_ARTIFACT.md §4 — @backend owns this)

## iOS Spec Update
- [ ] 12.1 Add Knowledge Skill source cards section to `ios-app/ios-spec.md`
- [ ] 12.2 Add filter chip row spec to chat section of `ios-app/ios-spec.md`
- [ ] 12.3 Add domain config sync spec to domain system section of `ios-app/ios-spec.md`
