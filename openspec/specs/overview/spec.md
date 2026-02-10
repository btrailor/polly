# Polly — System Overview (OpenSpec)

This spec is the OpenSpec source of truth for current system behavior. Project tracking (status and roadmap) is OpenSpec-driven.

## What Polly Is

- **Polly** is an edge-native personal AI system designed for polymathic practice across interconnected domains.
- **Desktop app:** Electron + Python backend — full-featured knowledge management, AI chat, publishing, learning.
- **Mobile companion:** Lightweight capture + chat app; acts as a thin DRM node.
- **Distributed:** Multiple Polly instances cooperate via the Distributed Reasoning Mesh (DRM) protocol.
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
- **Spec Integration (Feb 2026)** — [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/) — Knowledge management, DRM, BAD Canvas, knowledge quality/anti-slop
- **Aesthetic Theme Engine** — [openspec/changes/aesthetic-theme-engine/](../../changes/aesthetic-theme-engine/) — Artist-derived theme system: 7 themes (Reas, Fidenza, Ghost Box, Martens, Jetset, Riley, Albers), UI presentation + persona behavior, composability
- **Code Library & Dev Philosophy** — [openspec/changes/code-library-and-dev-philosophy/](../../changes/code-library-and-dev-philosophy/) — Reusable code library (Agent Skills format), development philosophy configuration (guided spectrum positioning), AI Slop review, slash commands, multi-model cost routing
- **Designer Profile** — [openspec/changes/designer-profile/](../../changes/designer-profile/) — p5.js generative design engine, per-project design systems (`_design/`), Lucide-compatible icon generation, theme→generator constraint mapping, feature image pipeline for POSE
- **Learning & Administrator Profiles** — [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/) — Learning page center area redesign, meta-pedagogy prompt injectors, competency tracking, Superhuman-informed Administrator communication modes (Triage/Compose/Schedule/Remind)
- **Constitutional Epistemology** — [openspec/changes/constitutional-epistemology/](../../changes/constitutional-epistemology/) — Hardcoded epistemological foundation (material analysis, cui bono, scapegoat suspicion). Foundation, not filter. Shapes how all personas think. Non-configurable.

## Spec Domains (full set)

Current behavior is specified by domain in `openspec/specs/`:

### Core Systems
- **project** — [status](../project/status.md), [roadmap](../project/roadmap.md)
- **architecture** — Stack, backend/frontend, data flow
- **design** — Design philosophy and principles
- **ui** — Design system, layout, pages
- **themes** — [Aesthetic Theme Engine](../themes/spec.md): artist-derived theme system for UI presentation and AI persona behavior (7 themes, composability, cross-domain ripple)
- **ethics** — [Constitutional epistemology](../ethics/spec.md): hardcoded epistemological foundation (material analysis over essentialism, cui bono, scapegoat suspicion). Foundation, not filter. Non-configurable.
- **security** — Current and planned (Phase 23.5)

### Intelligence
- **rag** — RAG, hybrid search, routing, autonomy metrics
- **personas** — Architect, Scribe, Professor (+ planned: Programmer, Librarian, Designer with generative p5.js pipeline, Administrator)
- **agent-swarms** — Configurable multi-agent workflows, Nexus coordination, execution contexts
- **domains** — User domain configuration
- **patterns** — Pattern learning, compression, pattern → library promotion
- **mental-models** — Mental models system
- **compression** — LLMLingua + LLM summary compression
- **code-library** — Reusable code modules (Agent Skills format), pattern extraction, AI Slop review, multi-model routing
- **dev-philosophy** — Development philosophy configuration, guided spectrum positioning, persona integration

### Knowledge Management
- **notes** — Native notes, TOC, templates, knowledge writing from chat
- **knowledge-graph** — Entity extraction, graph structure, authority scoring, anti-slop, unified retrieval, visualization
- **library** — BookLore ebook management, EPUB/PDF parsing, library RAG, highlight-to-note pipeline
- **capture** — Multi-modal capture, PARA organization, maturity lifecycle, review workflows
- **canvas** — BAD Canvas for structured project planning
- **publishing** — POSE publishing pipeline (Ghost CMS, social, newsletter)
- **analytics** — Knowledge patterns, quality metrics, reflective features

### Learning
- **curriculum** — Curriculum learning system
- **teaching** — Teaching mode, learning tracker
- **onboarding** — First-run wizard, progressive feature revelation, adaptive tutorials

### Communication
- **communication** — Email intelligence, calendar features, progressive communication autonomy

### Infrastructure
- **drm** — Distributed Reasoning Mesh (peer-to-peer, Cloudflare Tunnels, Meshtastic resilience)
- **mobile** — Mobile companion app (capture + chat)
- **integrations** — GitHub, Context7, Obsidian, Ghost CMS, etc.
- **data-autonomy** — Export, self-hosting, offline mode, anti-lock-in

All existing docs are mapped to these specs in [openspec/DOCUMENTATION_MAP.md](../../DOCUMENTATION_MAP.md).

## Conventions

- Specs and changes live under `openspec/specs/` and `openspec/changes/`.
- Use OpenSpec workflow: create changes with proposals, design, tasks, and spec deltas; implement; then update specs and archive.
