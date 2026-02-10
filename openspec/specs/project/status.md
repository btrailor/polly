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
| **Spec integration** | Feb 2026 — Knowledge management, DRM, BAD Canvas, knowledge quality specs integrated into OpenSpec |

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

### Spec Integration (Feb 2026) 📋
- **Status:** Specs integrated into OpenSpec. Implementation not started.
- **Scope:** Five specification sets plus comprehensive gap audit — knowledge management & capture, DRM (hybrid discovery, PKI security, Meshtastic resilience), BAD Canvas, knowledge quality/anti-slop, Agent Swarms, plus missing personas, communication, onboarding, data autonomy, and detailed Phase 25–29 plans.
- **Impact:** 11 new domain specs created (knowledge-graph, capture, drm, canvas, publishing, mobile, analytics, agent-swarms, **communication, onboarding, data-autonomy**). 15+ existing specs updated. Roadmap expanded with Tiers 2–5 and detailed Phases 18–29. Personas expanded from 3 to 7 (added Programmer, Librarian, Designer, Administrator). Phase 24 reconceived as Agent Swarms (24a–24e). DRM expanded to 6 phases (36d Cloudflare, 36e Meshtastic). Knowledge graph visualization layer added.
- **OpenSpec:** [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)

### Code Library & Development Philosophy (Feb 2026) 📋
- **Status:** Specs integrated into OpenSpec. Implementation not started.
- **Scope:** Two interconnected systems — (1) Reusable Code Library using Agent Skills format that Polly builds as a byproduct of working: patterns, components, prompts, workflows in `_polly/library/`. (2) Development Philosophy Configuration: guided process for positioning projects on technical spectrums (open/constrained, friendly/powerful, local/cloud, etc.) producing `development-philosophy.md`. Also includes: AI Slop review skill, slash command system (`/library`, `/philosophy`, `/model`, `/cost`), multi-model cost optimization for library operations, and pattern → library promotion pipeline.
- **Impact:** 2 new domain specs created (**code-library, dev-philosophy**). 5 existing specs updated (patterns, personas, design, architecture, overview). New `core/code_library/`, `core/philosophy/`, `core/commands/` packages. New `code-library` ChromaDB collection. Config expanded with `library` and `philosophy` sections. Persona system prompt injection expanded with philosophy context. Estimated 4–7 weeks implementation (5 waves).
- **OpenSpec:** [openspec/changes/code-library-and-dev-philosophy/](../../changes/code-library-and-dev-philosophy/)

### Designer Profile (Feb 2026) 📋
- **Status:** Specs integrated into OpenSpec. Implementation not started.
- **Scope:** Comprehensive expansion of Designer persona — (1) p5.js generative design engine producing custom icons (Lucide-compatible), pattern tiles, feature images, data viz, UI micro-elements. (2) Per-project design system (`_design/` directory with `system.yml` tokens, icon registry, generator scripts). (3) Theme→Generator integration: theme behavior layer properties (`designer.default_composition`, `designer.color_logic`, `designer.turbulence`, `designer.material_awareness`) directly constrain the p5.js pipeline — same request under different themes produces different output. (4) Feature image generation for POSE/Ghost CMS publishing pipeline. (5) Design components, generators, and system templates as code library modules.
- **Impact:** Designer persona expanded from 4 to 5 modes (added Generate). 6 existing specs updated (personas, themes, code-library, publishing, design, architecture). New `core/design/` package. Phase 27 expanded to 27a–27d. Design system as formal per-project artifact. Theme behavior layer gains concrete operational meaning through generator constraints. Estimated 5–8 weeks implementation (3 phases).
- **OpenSpec:** [openspec/changes/designer-profile/](../../changes/designer-profile/)

### Learning & Administrator Profiles (Feb 2026) 📋
- **Status:** Specs integrated into OpenSpec. Implementation not started.
- **Scope:** (1) Learning page center area redesign — move analytics to Review tab, make Active Session default, four center-area states (Active Session, Curriculum View, Practice Space, Review). Banking→problem-posing education principle. (2) Meta-pedagogy system — persona-specific prompt injectors detect improvable prompts and deliver brief contextual coaching. Not error messages; thinking-skill development. Teaches transferable skills: articulating goals, specifying constraints, recognizing what kind of help you need. (3) Competency tracking — per-persona, per-skill tracking (5 levels: 0–4), stored in `_polly/user/prompting-competency.yml`. Coaching fades as mastery grows (progressive scaffolding fade). (4) Persona introductions — natural one-message orientation on first interaction with each persona. (5) Administrator communication modes — Superhuman-informed Triage, Compose, Schedule, Remind modes. Speed is a feature. Sequential flow-based email processing, voice-matched drafts, calendar intelligence, snooze with context. (6) Communication slash commands (`/mail triage`, `/mail compose`, etc.) and cross-persona email integration (Scribe captures actions, Architect gets technical emails, Publisher uses Compose for newsletters).
- **Impact:** Teaching spec expanded with meta-pedagogy section. Onboarding spec gains persona introductions and competency tracking mechanism. Administrator persona expanded from 4 to 8 modes (4 system + 4 communication). Communication spec gains Superhuman-informed UX. UI spec updated for Learning page redesign and communication views. Analytics spec clarified (Review tab, not center stage). New `core/pedagogy/` package. 7 existing specs updated. Phase 22 frontend scope expanded. Phase 20a–20b gain concrete UX design. Estimated 4–6 weeks (Waves 1–2 Learning parallel with Wave 3 Administrator → 3–5 weeks effective).
- **OpenSpec:** [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/)

### Constitutional Epistemology (Feb 2026) 📋
- **Status:** Specs integrated into OpenSpec. Implementation not started.
- **Scope:** Hardcoded epistemological foundation that makes Polly structurally resistant to fascist, racist, and authoritarian logic — through consistently better analysis, not content filtering. Three core principles: (1) Material analysis over essentialism — default to structural/historical analysis when encountering group-attribution arguments. (2) Cui bono as default heuristic — surface who benefits from a given framing. (3) Suspicion of scapegoat narratives — "things are bad because of [outgroup]" triggers deeper structural analysis, not amplification. Derived commitments: horizontal over hierarchical, self-activity over obedience, plural worlds over singular narratives, defamiliarization of naturalized hierarchies. Five conduct rules ensure Polly never moralizes: never label users, lead with curiosity, acknowledge legitimate grievances, reserve naming for analytical contexts, defamiliarize don't denounce. Inoculation pedagogy (teach about harmful ideologies to build resistance). Constitutional mental model tier (always active, non-toggleable). RAG knowledge strategy prioritizing structural analysis sources.
- **Impact:** New `ethics` domain spec. Design principles gain #14 (Constitutional epistemology). Persona prompt hierarchy updated (constitutional layer is deepest, non-negotiable). Mental models gain constitutional tier (Cui Bono, Historical Construction, Structural Analysis). Teaching spec gains inoculation pedagogy. Architecture gains `core/constitutional/` subsystem. 6 existing specs updated. Draws directly from Polly's existing theoretical foundations (Freire, Graeber, Bogost, autonomism, inhabit.global). Not a feature — a foundation. Not configurable — hardcoded.
- **OpenSpec:** [openspec/changes/constitutional-epistemology/](../../changes/constitutional-epistemology/)

---

## In Progress / Pending

| Phase | Status | Notes |
|-------|--------|--------|
| **Core Framework** | 🔄 ~25% | Knowledge Writing done; Provider Registry + Routing pipeline pending |
| **16c** | Backend ready, frontend pending | AI Note Creation; ~4 weeks remaining |
| **22** | Backend 100%, frontend ~40% | Teaching Mode; 1–2 days to finish UI; deferred until after 23.5 |
| **12a** | Ready to start | Knowledge Graph — extended scope per spec integration (see Tier 3) |
| **12b** | After 12a | Knowledge Graph Advanced — extended scope |

---

## Completed Phases (Summary)

**Tier 0 (100%):** 0.5 (UI), 1 (Config), 3 (Server), 4 (Electron), 5 (Secrets)  
**Tier 1 (~82%):** 1.5 (Domains), 2a (RAG), 2b (Compression), 11 (Multi-Model + Personas), 11c (Compression UI), 13a (Patterns), 14 (Mental Models), 16 (Notes), 16c (Scribe/AI notes), 16e (TOC/Templates), 21 (Dedup), 22 (~75%), 23 (Curriculum)

Detailed phase notes and file references remain in [docs/status/CURRENT.md](../../../docs/status/CURRENT.md) (reference). New work should update this status and [roadmap.md](roadmap.md) and, when applicable, [openspec/changes/](../changes/).

---

## Where to Look Next

- **What to build next:** [roadmap.md](roadmap.md) and "Recommended Next Steps" in [docs/status/CURRENT.md](../../../docs/status/CURRENT.md)
- **Core Framework Refinement:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/) — Active cross-cutting change
- **Spec Integration:** [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/) — Feb 2026 spec integration (knowledge mgmt, DRM, canvas, quality)
- **New domain specs:** knowledge-graph, capture, drm, canvas, publishing, mobile, analytics, **code-library, dev-philosophy, ethics** — all under [openspec/specs/](../specs/)
- **Detailed phase specs:** [docs/planning/phases/](../../../docs/planning/phases/)
- **Active OpenSpec changes:** [openspec/changes/](../changes/) — e.g. **Phase 17 (Monaco code workspace):** [phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/); **Code Library & Philosophy:** [code-library-and-dev-philosophy/](../changes/code-library-and-dev-philosophy/); **Designer Profile:** [designer-profile/](../changes/designer-profile/); **Learning & Administrator Profiles:** [learning-and-administrator-profiles/](../changes/learning-and-administrator-profiles/); **Constitutional Epistemology:** [constitutional-epistemology/](../changes/constitutional-epistemology/)
- **Void vs Monaco decision:** [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md)
- **Changelog (completion history):** [docs/status/CHANGELOG.md](../../../docs/status/CHANGELOG.md)
