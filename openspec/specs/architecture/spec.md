# Architecture (OpenSpec)

Source of truth for Polly's system architecture. Detailed diagrams and tier breakdown: [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) (Architecture Summary), [docs/planning/tiers/](../../../docs/planning/tiers/).

## Stack

- **Backend:** Python 3 — `core/`, `interfaces/`, `learners/`, `integrations/`. REST server: `interfaces/server.py`. Config: `config/config.yaml`, `config/approved_packages.yaml`, `config/security_policy.yaml`.
- **Frontend:** Electron app in `electron-app/` — Node.js, CodeMirror 6, no React. Main: `src/main/main.js`; preload: `preload.js`; renderer: `src/renderer/app.js`, `index.html`.
- **Data:** SQLite (conversations, electron-store), ChromaDB (embeddings), `~/.polly/` (domains, patterns, mental models, templates, curricula), vault/notes.

## High-Level Flow

- User → Electron → IPC/REST → Python server → RAG + router + personas → LLM providers; response back to UI.
- RAG: hybrid search (ChromaDB + BM25), domain-aware; router: three-tier confidence (Fast/Balanced/Thorough), multi-provider.
- Personas (Architect, Scribe, Professor) and curriculum/teaching systems live in `core/` and `learners/`.

## New Components (Core Framework Refinement)

- **`core/knowledge_writer.py`** — Chat-to-KB writing orchestrator (gap detection, quick/scribe/message save, incremental RAG index)
- **`core/autonomy_metrics.py`** — Progressive autonomy tracking (knowledge writes + routing decisions in SQLite)
- **`electron-app/src/renderer/components/save-message-form.js`** — Frontend component for saving messages to KB
- **Config:** `config.yaml` → `ai_features` section (knowledge suggestions, autonomy dashboard)
- **Planned:** `core/provider_registry.py`, `core/providers/openrouter_provider.py`, query decomposition engine, synthesis layer
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Reference

- [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) — Architecture Summary, Current Status
- [docs/planning/tiers/TIER_0_FOUNDATION.md](../../../docs/planning/tiers/TIER_0_FOUNDATION.md), [TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md)
