# Architecture (OpenSpec)

Source of truth for Polly's system architecture. **Current Architecture** describes what exists in code today; **Planned Architecture** describes target subsystems. Detailed tiers: [docs/planning/tiers/](../../../docs/planning/tiers/), [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md).

---

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Current architecture (stack, query flow, storage) | ✅ Implemented | This spec |
| Integration contracts (ContextContributor, _gather_context) | ✅ Implemented | `core/protocols/`, `core/polly.py` |
| Planned subsystems (Agent Swarms, DRM, Canvas, etc.) | 💭 Vision | See Planned Architecture below |

---

## Stack (Current)

- **Backend:** Python 3 — `core/`, `interfaces/`, `learners/`, `integrations/`. REST server: `interfaces/server.py`. Config: `config/config.yaml`, `config/approved_packages.yaml`, `config/security_policy.yaml`.
- **Frontend:** Electron app in `electron-app/` — Node.js, CodeMirror 6, no React. Main: `src/main/main.js`; preload: `preload.js`; renderer: `src/renderer/app.js`, `index.html`.
- **Mobile:** Companion app (technology TBD) — not implemented; spec only.
- **Data (actual):** SQLite (`~/.polly/entities.db`, `~/.polly/usage.db`, Electron conversations), ChromaDB (`~/.polly/chroma/`), file system (`~/.polly/`, vault/notes). See [Data Stores](#data-stores-current) below.

---

## Current Architecture: Component Diagram

What exists in code today:

```
User → Electron (app.js) → REST (server.py) → Polly.query()
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                             │                                            │
         ▼                                             ▼                                            ▼
   DomainEngine                              UnifiedRAG                                    _gather_context()
   (detect domains)                          (hybrid search + optional compression)       (ContextContributor)
   core/domains.py                           core/rag.py                                   core/polly.py
         │                                             │                                            │
         │                                             │              ┌─────────────────────────────┼─────────────────────────────┐
         │                                             │              │                             │                             │
         │                                             │              ▼                             ▼                             ▼
         │                                             │       MentalModelManager            EntityContextBuilder           PatternEngine
         │                                             │       (priority 60)                 (priority 40)                   (priority 20)
         │                                             │       core/mental_models.py         core/entities/context.py         core/patterns/
         │                                             │              │                             │                             │
         │                                             │              └─────────────────────────────┼─────────────────────────────┘
         │                                             │                                            │
         │                                             │                                            ▼
         │                                             │                                    CompressionManager
         │                                             │                                    (priority 10, conversation summary)
         │                                             │                                    core/compression/
         │                                             │                                            │
         └────────────────────────────────────────────┴────────────────────────────────────────────┘
                                                      │
                                                      ▼
                                              Build augmented prompt
                                                      │
                                                      ▼
                                              IntelligentRouterV2
                                              (tier selection, LiteLLM or legacy adapters)
                                              core/router_v2.py, core/providers/
                                                      │
                                                      ▼
                                              LLM (Anthropic, OpenAI, etc.) → stream response
                                                      │
                                                      ▼
                                              _record_routing_outcome() → PatternEngine (ROUTING_OUTCOME)
                                              Optional: KnowledgeWriter (save to KB), AutonomyMetrics
```

---

## Current Architecture: Query Hot Path (`Polly.query()`)

Actual data flow when a user sends a message:

1. **Resolve persona** — From `persona_manager` if not passed.
2. **Detect domains** — `domains.detect_domains(query, context)` → list of domain IDs; optionally `detect_domains_with_scores`.
3. **Notify persona-aware systems** — `_notify_persona_context(persona, persona_mode)` → PatternEngine, EntityContextBuilder, MentalModelManager (integration-contracts).
4. **RAG retrieval** — `rag.search(search_query, domain_names, n_results, ...)` → hybrid search (ChromaDB + BM25), optional LLMLingua compression → `rag_context` string.
5. **Gather context** — `_gather_context(query, domain_names, persona=..., mode=...)`:
   - Mental models (priority 60): `mental_model_manager.build_context(...)`.
   - Entity context (priority 40): `entity_context.build_context(...)`.
   - Pattern engine (priority 20): `pattern_engine.build_context(...)`.
   - Compression (priority 10): `compression_manager.build_context(...)` (conversation summary if available).
   - Sorted by priority, concatenated.
6. **Build augmented prompt** — Domain prompt + integration note + RAG context + gathered context + practices/instruction overrides.
7. **Route** — `router_v2.route(...)` or direct provider; LiteLLM adapter or legacy per-provider adapters; tier (Fast/Balanced/Thorough), optional provider override.
8. **LLM call** — Async completion (streaming); response chunks yielded to caller.
9. **Post-response** — `_record_routing_outcome(response_metadata, ...)` → PatternEngine learns ROUTING_OUTCOME; optional KnowledgeWriter save; AutonomyMetrics.

Reference: `core/polly.py` — `query()` (≈1207), `_gather_context()` (≈738), `_record_routing_outcome()` (≈811).

---

## Data Stores (Current)

| Store | Purpose | Location | Notes |
|-------|---------|----------|--------|
| SQLite (conversations) | Chat history, compression state | Electron app | Per-app |
| SQLite (entities.db) | Entity graph (EntityStore) | `~/.polly/entities.db` | core/entities/store.py |
| SQLite (usage.db) | Autonomy metrics, budget tracking | `~/.polly/usage.db` | core/autonomy_metrics.py, core/budget_manager.py |
| ChromaDB | RAG embeddings (notes, code, etc.) | `~/.polly/chroma/` | core/rag.py; optional code-library collection |
| File system | Notes, patterns (JSON), mental models, curricula, templates, domain_config | `~/.polly/`, vault/ | core/domains.py, core/patterns/storage/, core/mental_models.py |
| Mem0 (optional) | Adaptive memory (knowledge, patterns, persona) | ChromaDB or configurable | core/memory/mem0_adapter.py; opt-in via config |

Planned (not yet implemented): `knowledge.db` (canvases, captures, publications), DRM state (`~/.polly/drm/`), library files (`~/.polly/library/`). See roadmap and domain specs.

---

## Integration Contracts (Current)

Cross-system behavior is formalized via `core/protocols/`:

- **ContextContributor** — `build_context(query, domains, persona, mode, **kwargs) -> str`; `context_priority: int`. Implemented by: MentalModelManager (60), EntityContextBuilder (40), PatternEngine (20), CompressionManager (10). Polly calls `_gather_context()` which collects and merges by priority.
- **PersonaAware** — `set_active_persona(persona_name, mode)`. Implemented by: PatternEngine, EntityContextBuilder, MentalModelManager. Polly calls `_notify_persona_context()` after domain detection.
- **PatternConsumer** — Router (via Polly) records ROUTING_OUTCOME patterns via `_record_routing_outcome()`; pattern-informed routing uses PatternEngine search.
- **Conversation sync** — Electron sends last N messages to `POST /polly/conversation/sync` so Python's conversation buffer matches the active thread (compression/learning).

See [integration-contracts](../../changes/integration-contracts/design.md) and [architecture-integration-audit](../../changes/architecture-integration-audit/).

---

## Planned Architecture (Vision)

The following subsystems are specified but not implemented. Do not design integration points against them until implementation begins.

### Multi-Agent (Agent Swarms / Nexus)

- Complex tasks: User → Nexus (task decomposition, agent selection) → Agent execution → Merge → Response.
- Three-tier routing stack: Nexus (which agents?) → DRM Router (which node?) → Router v2 (which model?).
- Agents declare capabilities, input/output schemas, execution context requirements.
- Nexus composes workflows from agent pool.
- Execution contexts brokered via Capability Broker (Phase 23.5 extension).

Spec: [agent-swarms](../agent-swarms/spec.md). Phase 24a–24e in roadmap.

### Distributed (DRM)

- Query → DRM Router (which node?) → Node Router (which model/provider?) → LLM → Response.
- Three discovery layers: mDNS (LAN), Cloudflare Tunnels (internet), Meshtastic (LoRa). Ed25519 PKI, `trusted-peers.yaml`.
- Mobile companion submits tasks to capable peers.

Spec: [drm](../drm/spec.md). Phases 36–36e in roadmap.

### Other Planned Subsystems

| Subsystem | Location (planned) | Spec |
|-----------|--------------------|------|
| Knowledge Quality Pipeline | `core/knowledge_quality/` | [knowledge-graph](../knowledge-graph/spec.md) |
| Capture System | `core/capture/` | [capture](../capture/spec.md) |
| BAD Canvas | `core/canvas/` | [canvas](../canvas/spec.md) |
| Publishing Pipeline | `core/publishing/` | [publishing](../publishing/spec.md) |
| Library / BookLore | `core/library/`, `integrations/library.py` | [library](../library/spec.md) |
| Code Library | `core/code_library/` | [code-library](../code-library/spec.md) |
| Design Engine | `core/design/` | [design](../design/spec.md), [personas](../personas/spec.md) |
| Meta-Pedagogy | `core/pedagogy/` | [teaching](../teaching/spec.md), [onboarding](../onboarding/spec.md) |
| Constitutional Epistemology | `core/constitutional/` | [ethics](../ethics/spec.md) |
| Development Philosophy | `core/philosophy/` | [dev-philosophy](../dev-philosophy/spec.md) |
| Slash Commands | `core/commands/` | [code-library](../code-library/spec.md) |
| Distributed Reasoning Mesh | `core/drm/` | [drm](../drm/spec.md) |

---

## New Components (Core Framework Refinement — Current)

- **`core/knowledge_writer.py`** — Chat-to-KB writing (gap detection, quick/scribe/message save, incremental RAG index).
- **`core/autonomy_metrics.py`** — Autonomy tracking (knowledge writes + routing decisions in usage.db).
- **`core/providers/litellm_adapter.py`** — Unified provider adapter (LiteLLM); optional via `routing_v2.use_litellm`.
- **`core/compression/llmlingua_strategy.py`** — LLMLingua RAG context compression.
- **`core/memory/mem0_adapter.py`** — Mem0 adaptive memory (optional).
- **`electron-app/src/renderer/components/save-message-form.js`** — Save message to KB UI.
- **Config:** `config.yaml` → `ai_features`, `memory`, `compression`, `litellm_config.yaml`.

Planned in same change: Provider Management UI, "Polly" mode in UI, Query Decomposition, Split Routing, Synthesis. See [core-framework-refinement](../../changes/core-framework-refinement/).

---

## Architecture Map (Narrative + Graphical)

- **[docs/ARCHITECTURE_MAP.md](../../../docs/ARCHITECTURE_MAP.md)** — Narrative map of critical tools, features they serve, query hot path, integration contracts, and Mermaid diagrams.
- **[docs/architecture-tools-features-map.svg](../../../docs/architecture-tools-features-map.svg)** — Graphical map: tools ↔ features and data stores.

---

## Reference

- [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) — Architecture summary, status
- [docs/planning/tiers/](../../../docs/planning/tiers/) — Tier breakdown
- [architecture-integration-audit](../../changes/architecture-integration-audit/) — Audit and spec reconciliation
- [integration-contracts](../../changes/integration-contracts/) — Protocol definitions and implementation
