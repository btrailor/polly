# Proposal: Phase 2 — Knowledge Skill

## Intent
Give Polly access to the user's personal knowledge base — Obsidian vault, BookLore library, and conversation history — via a unified retrieval service. This is the infrastructure layer that unblocks all Phase 3 cognitive features.

## Scope

**In scope:**
- Obsidian vault adapter (structure-aware chunking, wikilink graph layer)
- BookLore/EPUB adapter (chapter-boundary chunking)
- Conversation history adapter (agent memory files, section-header chunking)
- Shared FAISS HNSW index with hybrid retrieval (dense + sparse + RRF fusion + cross-encoder reranking)
- SQLite wikilink graph store
- Index hooks extension point (ships empty; Phase 3 features register hooks)
- DIRECT / ADJACENT / ABSENT retrieval classification
- Degradation handling (staleness, corruption, embedding failure, OOM)
- `knowledge_search`, `knowledge_graph`, `knowledge_domains`, `knowledge_register_hook`, `knowledge_conversation_history` tool interfaces
- Service contracts for all Phase 3 consumers
- iOS source cards UI + filter chips in chat
- Domain taxonomy reconciliation (iOS MMKV seeds → gateway keyword matching)
- Security acceptance criteria — @security_audit gate required

**Out of scope (Phase 3):**
- `knowledge_analogy` (structural pattern retrieval)
- `knowledge_dream` (distance-band misretrieval)
- Structural pattern tagger, domain-label-enricher, rhetorical-structure-extractor hooks
- OpenClaw session export adapter (full conversation history — memory files sufficient for Phase 2)

## Approach

Single service model (not independent skills). The Knowledge Skill owns the FAISS index and SQLite graph store. All Phase 3 features consume via declared tool interfaces — no feature duplicates index infrastructure.

Pluggable adapter architecture: each source (vault, booklore, conversation) is an adapter with a common interface (crawl, chunk, watch). New sources added by implementing the adapter interface.

Index hooks allow Phase 3 features to register metadata-enrichment passes without requiring full re-index.

## Key decisions already locked (2026-03-25)

- Single service model (@backend)
- 7-layer prompt injection hierarchy; gateway owns layers 3-7 (@backend)
- DIRECT/ADJACENT/ABSENT classification from salvage audit DualValidator/RetrievalClassifier
- Conversation history `## Reasoning` section mandated in Standard SOUL Baseline (@code_architect)
- @backend owns `manifest.json` in Phase 1 export pipeline (COGNITIVE_ARTIFACT.md §4)

## Specs modified by this change

- `knowledge/knowledge-skill.md` — primary spec (complete)
- `knowledge/service-contracts.md` — tool interfaces and cross-feature contracts (complete, @backend §4 pending)
- `agent-system/agent-templates.md` — Standard SOUL Baseline `## Reasoning` section added (complete)
- `ios-app/ios-spec.md` — Source cards UI, filter chips, domain config sync (see tasks)

## Review required

- @security_audit: skill manifest permissions, file system access sandboxing, network constraint enforcement
- @backend: `service-contracts.md §4` config read path caching model (session vs. request scoped for Layer 6)
