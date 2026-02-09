# Polly — System Overview (OpenSpec)

This spec is the OpenSpec source of truth for current system behavior. Project tracking (status and roadmap) is OpenSpec-driven.

## What Polly Is

- **Polly** is an edge-native personal AI system (desktop Electron app + Python backend).
- **Status (now):** [openspec/specs/project/status.md](../project/status.md)
- **Roadmap (tiers/phases):** [openspec/specs/project/roadmap.md](../project/roadmap.md)
- **Detailed reference:** [docs/status/CURRENT.md](../../../docs/status/CURRENT.md), [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md), [docs/planning/](../../../docs/planning/)

## Architecture (Current)

- **Backend:** Python 3 (core/, interfaces/, learners/, integrations/). Server in interfaces/server.py; config in config/.
- **Frontend:** Electron app in electron-app/ (Node.js, CodeMirror 6, no React).
- **Data:** SQLite (electron-store, better-sqlite3), ChromaDB for embeddings, local files.
- **AI:** LLM calls via backend; RAG, curriculum, and persona systems in core/.

## Active Changes

- **Core Framework Refinement** — [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/) — Progressive autonomy: Knowledge Writing (✅), Autonomy Metrics (✅), Provider Registry (planned), Intelligent Routing pipeline (planned), BookLore (planned)

## Spec domains (full set)

Current behavior is specified by domain in `openspec/specs/`:

- **project** — [status](../project/status.md), [roadmap](../project/roadmap.md)
- **architecture** — Stack, backend/frontend, data flow
- **design** — Design philosophy and principles
- **ui** — Design system, layout, pages
- **rag** — RAG, hybrid search, routing, autonomy metrics
- **personas** — Architect, Scribe, Professor
- **domains** — User domain configuration
- **notes** — Native notes, TOC, templates, knowledge writing from chat
- **curriculum** — Curriculum learning system
- **teaching** — Teaching mode, learning tracker
- **patterns** — Pattern learning, compression
- **mental-models** — Mental models system
- **integrations** — GitHub, Context7, Obsidian, etc.
- **security** — Current and planned (Phase 23.5)

All existing docs are mapped to these specs in [openspec/DOCUMENTATION_MAP.md](../../DOCUMENTATION_MAP.md).

## Conventions

- Specs and changes live under `openspec/specs/` and `openspec/changes/`.
- Use OpenSpec workflow: create changes with proposals, design, tasks, and spec deltas; implement; then update specs and archive.
