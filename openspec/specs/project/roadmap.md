# Polly Roadmap (OpenSpec)

**Authority:** This file is the OpenSpec source of truth for tiers and phase plan.  
**Status:** See [status.md](status.md). **Detail:** [docs/planning/phases/](../../../docs/planning/phases/), [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) (reference).

---

## Tiers Overview

| Tier | Name | Progress | Notes |
|------|------|----------|--------|
| **0** | Foundation & UI | ✅ 100% | Phases 0.5, 1, 3, 4, 5 |
| **1** | Core Intelligence | ~82% | 15+ phases done; 23.5, 16c, 22, 12a/12b remaining |
| **2** | Packaging & Permissions | 📋 Not started | Phase 9, signing, UI polish |
| **3** | Polish & Autonomy | 📋 Not started | Phase 18 onboarding, Phase 19 data autonomy |
| **4** | Advanced Communication | 📋 Not started | Phase 20a/b/c email, calendar, autonomy |

Tier docs: [docs/planning/tiers/](../../../docs/planning/tiers/).

---

## Phase List (Status)

### Tier 0 ✅
| Phase | Name | Status |
|-------|------|--------|
| 0.5 | Obsidian-Inspired UI | ✅ |
| 1 | Configuration System | ✅ |
| 3 | Backend Server | ✅ |
| 4 | Electron Application | ✅ |
| 5 | Secrets Manager | ✅ |

### Tier 1
| Phase | Name | Status | OpenSpec / Notes |
|-------|------|--------|-------------------|
| 1.5 | Domain Configuration | ✅ | |
| 2a | RAG Optimization | ✅ | |
| 2b | Pattern Compression | ✅ | |
| 11 | Multi-Model Routing & Personas | ✅ | 11a, 11b, 11c |
| 11c | Compression UI | ✅ | |
| 13a | Pattern Learning Core | ✅ | |
| 14 | Mental Models | ✅ | |
| 16 | Native Notes Frontend | ✅ | |
| 16c | AI Note Creation | 🔄 | Backend done, frontend pending |
| 16e | TOC & Templates | ✅ | |
| 21 | Knowledge Base Deduplication | ✅ | |
| 22 | Teaching Mode | 🔄 ~75% | Backend done; frontend 1–2 days |
| 23 | Curriculum Learning System | ✅ | All 6 sub-phases |
| **23.5** | **Security Hardening** | 📋 Next | Use [openspec/changes/](../changes/) when starting |
| 12a | Knowledge Graph Basic | 📋 | 5–7 days |
| 12b | Knowledge Graph Advanced | 📋 | After 12a |

### Cross-Cutting: Core Framework Refinement
| Component | Status | OpenSpec / Notes |
|-----------|--------|-------------------|
| Knowledge Writing | ✅ | `core/knowledge_writer.py`, settings API, frontend |
| Autonomy Metrics | ✅ | `core/autonomy_metrics.py`, dashboard API |
| Incremental RAG Index | ✅ | `rag.index_single_document()` |
| AI Features Config + UI | ✅ | `config.yaml`, settings toggles |
| Provider Registry | 📋 | `core/provider_registry.py` (designed, not coded) |
| "Polly" Routing Mode | 📋 | UI + routing pipeline (designed, not coded) |
| OpenRouter Gateway | 📋 | `core/providers/openrouter_provider.py` (designed) |
| Query Decomposition | 📋 | Core differentiator — not started |
| Split Routing + Synthesis | 📋 | Depends on decomposition |
| Pattern → Routing | 📋 | Not started |
| PIL Expansion | 📋 | Not started |
| SKILL ↔ Mental Model | 📋 | Not started |
| Orchestrator | 📋 | Not started |
| BookLore Library | 📋 | Not started |
| RAG Optimization | 📋 | Not started |

Change folder: [changes/core-framework-refinement/](../changes/core-framework-refinement/)

### Tier 2+
| Phase | Name | Status | OpenSpec / Notes |
|-------|------|--------|-------------------|
| 9 | macOS Permissions | 📋 | |
| 17 | Code Workspace (Monaco) | 📋 | [changes/phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/); Void/Cursor design reference only |
| 24 | Orchestrator Mode | 📋 | Blocked by 23.5 |
| 13b | User Profile System | 📋 | |
| 25–29 | Code Arch, PM, Designer, Plugins, Browser | 📋 | |

Full phase descriptions and dependencies: [docs/planning/README.md](../../../docs/planning/README.md), [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md).

---

## Backlog & Reference Docs

- **Feature backlog:** [archive/root-docs/FEATURES_TO_BUILD.md](../../../archive/root-docs/FEATURES_TO_BUILD.md)
- **Roadmap analysis:** [archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md](../../../archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md)
- **Brain dumps / planning:** [archive/root-docs/BRAIN_DUMP_2026-01-31.md](../../../archive/root-docs/BRAIN_DUMP_2026-01-31.md), [planning/investigations/](../../../planning/investigations/), [archive/](../../../archive/)
- **Design philosophy:** [docs/planning/DESIGN_PHILOSOPHY.md](../../../docs/planning/DESIGN_PHILOSOPHY.md)

When starting a phase, create an OpenSpec change under [openspec/changes/](../changes/) (e.g. `phase-23.5-security-hardening/`) with `proposal.md`, `design.md`, `tasks.md`, then implement and update [status.md](status.md) and this roadmap.

**Phase 17 (Code Workspace):** Monaco path is the chosen approach (no VSCode/Void fork). See [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md) for decision and audit runbook; active change: [changes/phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/).
