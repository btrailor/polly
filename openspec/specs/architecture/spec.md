# Architecture (OpenSpec)

Source of truth for Polly's system architecture. Detailed diagrams and tier breakdown: [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) (Architecture Summary), [docs/planning/tiers/](../../../docs/planning/tiers/).

## Stack

- **Backend:** Python 3 — `core/`, `interfaces/`, `learners/`, `integrations/`. REST server: `interfaces/server.py`. Config: `config/config.yaml`, `config/approved_packages.yaml`, `config/security_policy.yaml`.
- **Frontend:** Electron app in `electron-app/` — Node.js, CodeMirror 6, no React. Main: `src/main/main.js`; preload: `preload.js`; renderer: `src/renderer/app.js`, `index.html`.
- **Mobile:** Companion app (technology TBD) — lightweight capture + chat client, thin DRM node.
- **Data:** SQLite (conversations, electron-store, knowledge graph, captures, canvases, publications), ChromaDB (embeddings), `~/.polly/` (domains, patterns, mental models, templates, curricula), vault/notes.

## High-Level Flow

### Desktop (Single Node)
- User → Electron → IPC/REST → Python server → RAG + router + personas → LLM providers; response back to UI.
- RAG: hybrid search (ChromaDB + BM25) + entity graph, domain-aware; router: three-tier confidence (Fast/Balanced/Thorough), multi-provider.
- Personas (Architect, Scribe, Professor) and curriculum/teaching systems live in `core/` and `learners/`.
- Knowledge quality pipeline: entity extraction → similarity check → connection suggestion → authority update → RAG index.

### Multi-Agent (Swarms)
- Complex tasks: User → Nexus (task decomposition, agent selection) → Agent execution → Merge → Response.
- Three-tier routing stack: Nexus (which agents?) → DRM Router (which node?) → Router v2 (which model?).
- Agents declare capabilities, input/output schemas, execution context requirements.
- Nexus composes workflows from agent pool: parallel branches, sequential dependencies, intervention points.
- Execution contexts brokered via Capability Broker (Phase 23.5 extension).

### Distributed (DRM)
- Query → DRM Router (which node?) → Node Router (which model/provider?) → LLM → Response.
- DRM adds a node-routing tier above existing model/provider routing.
- **Three discovery layers:** mDNS (LAN), Cloudflare Tunnels (internet), Meshtastic (LoRa radio resilience). All optional and composable.
- Capability-aware task assignment with network-type scoring (local preferred for latency-sensitive).
- **Security:** Ed25519 PKI token system — mesh membership (long-lived) + task authorization JWT (short-lived, 5-min expiry). `trusted-peers.yaml` as mesh constitution.
- Mobile companion submits tasks to capable peers via tunnel or local network.
- Agent Swarm parallel tasks distributed across DRM nodes using existing capability scoring.

## Data Stores

| Store | Purpose | Location |
|---|---|---|
| SQLite (conversations) | Chat history, conversation compression | Electron app |
| SQLite (knowledge.db) | Entity graph, canvases, captures, publications | `~/.polly/knowledge.db` |
| SQLite (usage.db) | Autonomy metrics, budget tracking | `~/.polly/usage.db` |
| ChromaDB | Embeddings for RAG hybrid search (collections: notes, code, library) | `~/.polly/chroma/` |
| File system | Notes, patterns, mental models, curricula, templates | `~/.polly/`, vault/ |
| Library files | Ebook files (EPUB, PDF, MOBI), parsed chapters, covers | `~/.polly/library/` |
| DRM state | Peer registry, task queue, node identity, `trusted-peers.yaml` | `~/.polly/drm/` |
| DRM keys | Ed25519 keypairs for mesh authentication | `~/.polly/keys/` |

## New Components (Core Framework Refinement)

- **`core/knowledge_writer.py`** — Chat-to-KB writing orchestrator (gap detection, quick/scribe/message save, incremental RAG index)
- **`core/autonomy_metrics.py`** — Progressive autonomy tracking (knowledge writes + routing decisions in SQLite)
- **`electron-app/src/renderer/components/save-message-form.js`** — Frontend component for saving messages to KB
- **Config:** `config.yaml` → `ai_features` section (knowledge suggestions, autonomy dashboard)
- **Planned:** `core/provider_registry.py`, `core/providers/openrouter_provider.py`, query decomposition engine, synthesis layer
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Planned Subsystems

| Subsystem | Location | Spec |
|---|---|---|
| Knowledge Quality Pipeline | `core/knowledge_quality/` | [knowledge-graph](../knowledge-graph/spec.md) |
| Agent Swarms / Nexus | `core/swarms/` | [agent-swarms](../agent-swarms/spec.md) |
| Capture System | `core/capture/` | [capture](../capture/spec.md) |
| BAD Canvas | `core/canvas/` | [canvas](../canvas/spec.md) |
| Publishing Pipeline | `core/publishing/` | [publishing](../publishing/spec.md) |
| Library / BookLore | `core/library/`, `integrations/library.py` | [library](../library/spec.md) |
| Code Library | `core/code_library/` | [code-library](../code-library/spec.md) |
| Design Engine | `core/design/` | [personas — Designer](../personas/spec.md), [design](../design/spec.md) |
| Meta-Pedagogy | `core/pedagogy/` | [teaching](../teaching/spec.md), [onboarding](../onboarding/spec.md) |
| Constitutional Epistemology | `core/constitutional/` | [ethics](../ethics/spec.md), [personas](../personas/spec.md) |
| Development Philosophy | `core/philosophy/` | [dev-philosophy](../dev-philosophy/spec.md) |
| Slash Commands | `core/commands/` | [code-library](../code-library/spec.md), [dev-philosophy](../dev-philosophy/spec.md) |
| Distributed Reasoning Mesh | `core/drm/` | [drm](../drm/spec.md) |

## Reference

- [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) — Architecture Summary, Current Status
- [docs/planning/tiers/TIER_0_FOUNDATION.md](../../../docs/planning/tiers/TIER_0_FOUNDATION.md), [TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md)
