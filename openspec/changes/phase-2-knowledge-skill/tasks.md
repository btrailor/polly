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
*Phase boundary: watcher + indexing is Phase 2 foundation; query tool is Phase 3 (needs stable adapter first). Decision locked 2026-03-25.*
- [ ] Memory file watcher (all agent `memory/YYYY-MM-DD.md`)
- [ ] Section-header chunker (agent_id, date, section metadata)
- [ ] Index in shared FAISS tagged `source: "conversation"`
- [ ] `knowledge_conversation_history` tool (date + agent + section filters) — **⬛ Phase 3** (move to phase-3-rag-routing)

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

### Write Path Integration (KNOWLEDGE_WRITE_PATH.md Phase 2)
*Phase boundary: Phase 2 vault writes are **user-initiated only** (quick capture promotion, conversation save). Agent write-back (`vault_write` tool) is **Phase 3 only**. Decision locked 2026-03-25.*
- [ ] Promotion pipeline: inbox → organized note (promotion sheet UI: title, domain, tags, folder, maturity, links, preview)
- [ ] `knowledge_dedup` tool implementation — semantic similarity check before write (see contracts §6.1)
- [ ] Dedup defaults: quick-capture/share=0.85, promotion=0.80, conversation-save=0.75, write-back=0.70
- [ ] Wikilink suggestions at promotion time: simple title matching against `knowledge_graph` note index
- [ ] "Save conversation to vault" write path (long-press → Save to Vault)
- [ ] `vault.write_complete` event emission from gateway write path — Knowledge Skill subscribes for incremental index (see contracts §6.2; gateway-changes #10)
- [ ] @backend: implement `vault.write_complete` event in gateway write path

### LLM-Selection Fallback for Low-Confidence FAISS Results (from CLAUDE_CODE_ARCHITECTURE_INSIGHTS.md §3.2)- [ ] When FAISS retrieval returns all results below ABSENT threshold (<0.45), fall back to LLM-based note selection: send note frontmatter/titles to Sonnet, ask it to select top 5 relevant notes by semantic understanding
- [ ] LLM fallback is a complement to FAISS, not a replacement — FAISS is primary path for all normal retrievals
- [ ] @backend owns fallback path; threshold and model configurable in skill manifest

### Session-End Memory Extraction — Forked Agent Pattern (from CLAUDE_CODE_ARCHITECTURE_INSIGHTS.md §3.3)
- [ ] Write path #7 (session-end extraction in `KNOWLEDGE_WRITE_PATH.md`): implement extraction as a forked agent — a copy of the session that shares the prompt cache, sees full conversation context (system prompt, tools, all turns, active SOUL)
- [ ] Do NOT pass conversation as plain input to a separate LLM call — the fork preserves domain context, mental models, and agent SOUL, which inform what facts are worth extracting
- [ ] @backend owns fork mechanism; @code_architect to update `KNOWLEDGE_WRITE_PATH.md §7` with this pattern

## Done when
All tasks checked. @security_audit sign-off. Filter chips working in chat. Vault + BookLore indexing on device. Promotion pipeline functional. Dedup tool live.

---

## Open Question: NAS as FAISS Index Host (from POLLY_WEB_ANALYSIS.md Q1)

Should the FAISS index live on the NAS (high-capacity persistent NAS storage, served from NAS RAM) rather than the Mac Mini (low network latency)? For large vaults (10k+ notes), the NAS storage advantage may outweigh the latency cost. For smaller vaults, Mac Mini is clearly better.

**Decision gate:** @backend to evaluate at Phase 4 planning based on: vault size at that point, update frequency vs. query frequency, measured NAS-to-gateway latency on Brett's LAN. Document decision in `KNOWLEDGE_SKILL.md` before Phase 4 infra work begins. This is not a Phase 2 concern — index lives on Mac Mini until Phase 4.

---

## Skill Runner Compatibility (from IOS_SPEC_AUDIT.md §2.5)

The Knowledge Skill runs on the gateway machine as a Python service (BGE-large-en via sentence-transformers + PyTorch). This requires verifying that OpenClaw's skill runner can invoke Python skills.

**Investigation required before Phase 2 starts (owner: @backend):**

- [ ] Verify: does OpenClaw's skill runner support Python skills natively, or is it Node-only?
- [ ] If Python-native: document the invocation pattern (subprocess? venv? system Python?)
- [ ] If Node-only (likely): spec the sidecar pattern — Knowledge Skill runs as a Python HTTP/stdio sidecar that OpenClaw calls via skill adapter. The `SALVAGE_AUDIT.md` already recommends this pattern for the four stateful systems (curriculum, mental models, DualValidator, RollingContext).
- [ ] Define the minimal viable MVP: `knowledge_search` tool only (no graph layer, no conversation history), FAISS flat index (not HNSW). What's the minimum Python stack to ship that? (Likely: `faiss-cpu`, `sentence-transformers`, `flask` or `fastapi` for HTTP adapter — no PyTorch GPU required on Mac Mini CPU)
- [ ] @backend documents findings in `KNOWLEDGE_SKILL.md` as a new "Skill Runner Compatibility" section before Phase 2 implementation begins

**Fallback position if sidecar is needed:** The HTTP sidecar pattern is well-understood. It does not change the tool signatures (`knowledge_search`, `knowledge_graph`, etc.) — the adapter layer is transparent to agents. Implementation complexity is moderate. Not a blocker — just needs to be designed before coding starts.
