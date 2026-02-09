# Polly Project Status (OpenSpec)

**Authority:** This file is the single source of truth for "where we are now."  
**Last Updated:** February 2026  
**Full history:** [docs/status/CHANGELOG.md](../../../docs/status/CHANGELOG.md)

---

## Quick Summary

| | |
|---|---|
| **Overall** | ~82% Tier 1 complete, production-ready |
| **Completed** | 15.75 major phases (0.5, 1, 1.5, 2a, 2b, 3, 4, 5, 11, 11c, 13a, 14, 16, 16c, 16e, 21, 22 ~75%, 23) |
| **Current priority** | Phase 23.5 (Security Hardening) — CRITICAL before Phase 24 |
| **Next recommended** | Phase 23.5 then Phase 22 frontend (Teaching Mode) |

---

## Current Priority (Active Work)

### Core Framework Refinement 🧠
- **Status:** In progress — Knowledge Writing + Autonomy Metrics implemented; Intelligent Routing pipeline pending
- **OpenSpec:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)
- **Completed:** Knowledge Writer (`core/knowledge_writer.py`), Autonomy Metrics (`core/autonomy_metrics.py`), Incremental RAG indexing, Scribe standalone enrich, AI Features config + settings UI, save-message frontend component, settings API endpoints
- **Next:** Provider Registry, "Polly" mode, OpenRouter adapter, Query Decomposition → Split Routing → Synthesis pipeline

### Phase 23.5: Security Hardening 🔐
- **Status:** Planning complete, ready for implementation
- **Why:** Phase 23 added code execution (unsandboxed); Phase 24+ will add more risk. Harden now.
- **Scope:** Capability Broker, Pyodide sandbox, package allowlist, Context7 trust, content sanitization, API key hardening
- **Effort:** 2–3 weeks
- **OpenSpec:** When started, use [openspec/changes/](../changes/) (e.g. `phase-23.5-security-hardening/`) with proposal, design, tasks.

---

## In Progress / Pending

| Phase | Status | Notes |
|-------|--------|--------|
| **Core Framework** | 🔄 ~25% | Knowledge Writing done; Provider Registry + Routing pipeline pending |
| **16c** | Backend ready, frontend pending | AI Note Creation; ~4 weeks remaining |
| **22** | Backend 100%, frontend ~40% | Teaching Mode; 1–2 days to finish UI; deferred until after 23.5 |
| **12a** | Ready to start | Knowledge Graph Basic; 5–7 days |
| **12b** | After 12a | Knowledge Graph Advanced |

---

## Completed Phases (Summary)

**Tier 0 (100%):** 0.5 (UI), 1 (Config), 3 (Server), 4 (Electron), 5 (Secrets)  
**Tier 1 (~82%):** 1.5 (Domains), 2a (RAG), 2b (Compression), 11 (Multi-Model + Personas), 11c (Compression UI), 13a (Patterns), 14 (Mental Models), 16 (Notes), 16c (Scribe/AI notes), 16e (TOC/Templates), 21 (Dedup), 22 (~75%), 23 (Curriculum)

Detailed phase notes and file references remain in [docs/status/CURRENT.md](../../../docs/status/CURRENT.md) (reference). New work should update this status and [roadmap.md](roadmap.md) and, when applicable, [openspec/changes/](../changes/).

---

## Where to Look Next

- **What to build next:** [roadmap.md](roadmap.md) and "Recommended Next Steps" in [docs/status/CURRENT.md](../../../docs/status/CURRENT.md)
- **Core Framework Refinement:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/) — Active cross-cutting change
- **Detailed phase specs:** [docs/planning/phases/](../../../docs/planning/phases/)
- **Active OpenSpec changes:** [openspec/changes/](../changes/) — e.g. **Phase 17 (Monaco code workspace):** [phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/)
- **Void vs Monaco decision:** [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md)
- **Changelog (completion history):** [docs/status/CHANGELOG.md](../../../docs/status/CHANGELOG.md)
