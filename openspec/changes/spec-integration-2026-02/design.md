# Design: Spec Integration

## Architecture Impact

### New Subsystems

1. **Knowledge Quality Pipeline** (`core/knowledge_quality/`)
   - Entity extraction (LLM-based for domain-specific entities)
   - Graph storage (SQLite — nodes + edges tables, no new dependency)
   - Connection metrics (inbound/outbound counts, authority scoring)
   - Garden maintenance (scheduled analysis, orphan detection, merge suggestions)
   - Absorbs existing `core/notes_dedup.py` as one step in the pipeline

2. **Capture System** (`core/capture/`)
   - Multi-modal input pipeline (voice-to-text, image+OCR, URL metadata, code detection)
   - Smart routing (content → domain classification via LLM)
   - Capture metadata (timestamp, source type, domain tags, maturity stage)
   - Mobile companion submits captures via DRM or REST

3. **BAD Canvas** (`core/canvas/`)
   - Canvas data model (SQLite storage, JSON zone content)
   - Gap detection engine (validation rules + RAG queries)
   - Cross-canvas pattern recognition (extends pattern learning)
   - Architect persona gains canvas-aware Plan mode

4. **Publishing Pipeline** (`core/publishing/`)
   - POSE workflow (Draft → Review → Schedule → Publish)
   - Ghost CMS integration
   - Social thread generation, newsletter compilation
   - Scribe persona gains publishing mode

5. **Distributed Reasoning Mesh** (`core/drm/`)
   - Node identity + capability manifests (extended: tunnel_url, network_type, geography)
   - Three-layer hybrid discovery: mDNS (LAN) + Cloudflare Tunnels (internet) + Meshtastic (LoRa resilience)
   - Cloudflare Workers coordination service for remote peer registry
   - Ed25519 PKI security: mesh membership tokens (long-lived) + JWT task authorization (short-lived)
   - `trusted-peers.yaml` as signed mesh constitution with revocation
   - Task distribution protocol (HTTP/2 + gRPC + HTTPS via tunnels)
   - Work assignment algorithm (capability + load + locality + network-type scoring)
   - Result aggregation (first-response, consensus, ensemble, reduce)
   - Meshtastic gateway nodes: bridge LoRa mesh ↔ IP network (coordination only, not data)
   - Exit strategy: Cloudflare is convenience not dependency; coordination self-hostable

6. **Mobile Companion** (separate repo/app)
   - Lightweight DRM node focused on capture + chat
   - Voice input as first-class citizen
   - Submits tasks to desktop/NAS nodes

7. **Agent Swarms / Nexus** (`core/swarms/`)
   - Agent interface specification (capability declarations, input/output schemas)
   - Nexus coordination layer (task classification, agent matching, workflow composition)
   - Workflow templates (YAML-based, built-in and custom)
   - Execution graph management (DAG, parallel/sequential, merge strategies)
   - Execution context brokering (extends Capability Broker)
   - Progressive disclosure UI (Level 1–4)
   - Persona-to-agent adapter (existing personas wrapped as agents)
   - Replaces original Phase 24 CrewAI Orchestrator with Polly-native architecture

### Existing System Extensions

| System                    | Extension                                                                                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **RAG**                   | Entity-graph retrieval as third strategy; authority scoring in RRF                                                                                     |
| **Notes**                 | Maturity lifecycle metadata; augmented writing sidebar; version history                                                                                |
| **Domains**               | Cross-domain visualization; capture routing rules; domain intersection tracking                                                                        |
| **Personas**              | Architect: canvas-aware Plan mode. Scribe: publishing mode. Professor: domain onboarding curriculum                                                    |
| **Dedup (Phase 21)**      | Absorbed into Knowledge Quality Pipeline — becomes one step alongside entity extraction, connection suggestion, authority update                       |
| **Personas (Phase 11)**   | Personas wrapped as agents with formal capability declarations. Modes become standalone agent capabilities. Nexus replaces planned Orchestrator toggle |
| **Security (Phase 23.5)** | Capability Broker extended to broker agent execution contexts (scoped access to GitHub, Obsidian, Ghost CMS, filesystem, etc.)                         |
| **Integrations**          | Ghost CMS, automation hooks (webhooks, Shortcuts), email ingestion                                                                                     |
| **UI**                    | Canvas page, analytics page, capture view, augmented writing panel, visualization views                                                                |
| **Security**              | DRM Ed25519 PKI token system (replaces mTLS plan), mesh membership + task JWT, execution context brokering for Agent Swarms                            |

### Data Storage Additions

All local-first, extending existing SQLite + ChromaDB + file patterns:

- **Entity graph:** SQLite tables (`entities`, `entity_edges`, `entity_mentions`) in `~/.polly/knowledge.db`
- **Canvas data:** SQLite table (`canvases`, `canvas_zones`) in `~/.polly/knowledge.db`
- **Capture queue:** SQLite table (`captures`) in `~/.polly/knowledge.db`
- **Maturity metadata:** Added to existing note frontmatter + SQLite index
- **DRM state:** `~/.polly/drm/` — peer registry, task queue, node identity, `trusted-peers.yaml`
- **DRM keys:** `~/.polly/keys/` — Ed25519 keypairs for mesh authentication
- **Publishing state:** SQLite tables (`publications`, `drafts`) in `~/.polly/knowledge.db`
- **Analytics:** SQLite tables extending existing `usage.db`
- **Agent Swarms:** SQLite tables (`swarm_executions`, `swarm_agent_runs`, `swarm_templates`, `agents`) in `~/.polly/knowledge.db`

### Dependency Order

```
Phase 23.5 (Security) ─── prerequisite for everything below
    │
    ├── Knowledge Graph + Quality Pipeline (extends Phase 12a)
    │       │
    │       ├── Anti-Slop mechanisms (garden maintenance, authority scoring)
    │       ├── Augmented writing (real-time related notes)
    │       └── Dedup overhaul (absorb Phase 21 into pipeline)
    │
    ├── Agent Swarms / Nexus
    │       │
    │       ├── Phase 24a: Nexus Foundation (agent interface, registry, single-agent routing)
    │       ├── Phase 24b: Multi-Agent Workflows (templates, execution graphs, merge)
    │       ├── Phase 24c: Execution Contexts (extends Capability Broker)
    │       ├── Phase 24d: Template UI + Progressive Disclosure
    │       └── Phase 24e: Advanced (DRM integration, pattern learning, Level 3-4 config)
    │
    ├── Capture System
    │       │
    │       ├── PARA + Maturity Lifecycle
    │       └── Review Workflows
    │
    ├── BAD Canvas (depends on: entity graph, RAG, domains)
    │
    ├── Publishing Pipeline (depends on: notes maturity, Scribe persona)
    │
    ├── DRM Phase 1-2 (independent infrastructure)
    │       │
    │       ├── DRM Phase 3-4 (depends on: intelligent routing pipeline)
    │       ├── DRM Phase 5: Remote Mesh (Cloudflare Tunnels + Ed25519 PKI; after Phase 2)
    │       ├── DRM Phase 6: Meshtastic Gateway (LoRa resilience; after Phase 2)
    │       └── Mobile Companion (thin DRM node)
    │
    └── Analytics + Insights (depends on: maturity tracking, entity graph, capture metadata)
```

## Design Principles (Additions)

Added to existing Progressive Capability, Context Reveals Complexity, Intelligent Defaults:

- **Capture over perfection** — Get it in fast, refine later
- **Signal over noise** — Every feature should increase knowledge quality, not just quantity
- **Emergence over prescription** — Let patterns surface from connections, don't force structure
- **Continuation over completion** — Support ongoing work, not just finished products
- **Reverse engineering** — Start with desired outcome (published work), build backward
