# Documentation map — full migration to OpenSpec

All existing project docs are migrated **into** the OpenSpec standard: OpenSpec specs are the source of truth; the docs below are **reference** that feed or support those specs. When behavior changes, update the relevant spec first; then update or archive the referenced doc as needed.

## By OpenSpec domain (spec → reference docs)

| Spec | Purpose | Reference docs (detailed) |
|------|---------|----------------------------|
| [specs/overview/spec.md](specs/overview/spec.md) | System overview | MASTER_ROADMAP (Architecture Summary), docs/planning/tiers/ |
| [specs/project/status.md](specs/project/status.md) | Current status | docs/status/CURRENT.md, docs/status/CHANGELOG.md |
| [specs/project/roadmap.md](specs/project/roadmap.md) | Tiers & phases | MASTER_ROADMAP.md, docs/planning/README.md, docs/planning/tiers/, docs/planning/phases/ |
| [specs/architecture/spec.md](specs/architecture/spec.md) | Stack, flow | MASTER_ROADMAP (Architecture), docs/planning/tiers/TIER_0, TIER_1 |
| [specs/design/spec.md](specs/design/spec.md) | Design philosophy | docs/planning/DESIGN_PHILOSOPHY.md |
| [specs/ui/spec.md](specs/ui/spec.md) | UI, layout, pages | docs/planning/phases/phase-0.5/* (PHASE0.5_OBSIDIAN_INSPIRED_UI, PHASE0.5_UI_DESIGN_SYSTEM) |
| [specs/rag/spec.md](specs/rag/spec.md) | RAG, routing | docs/RAG_ROUTING_ARCHITECTURE.md, README_RAG_DOCS.md, RAG_TROUBLESHOOTING_QUICK_REFERENCE.md |
| [specs/personas/spec.md](specs/personas/spec.md) | Personas | docs/PERSONA_SYSTEM_ARCHITECTURE.md, docs/PERSONA_API.md, docs/planning/phases/phase-11/* |
| [specs/domains/spec.md](specs/domains/spec.md) | Domain config | docs/planning/phases/phase-1.5/* |
| [specs/notes/spec.md](specs/notes/spec.md) | Notes, TOC, templates | docs/planning/phases/phase-16/*, phase-16e/*, phase-16c/*; NATIVE_NOTES_GUIDE.md, NOTES_FUNCTIONALITY_IMPLEMENTATION.md |
| [specs/curriculum/spec.md](specs/curriculum/spec.md) | Curriculum | docs/planning/phases/phase-23/* (PHASE23_CURRICULUM_SYSTEM, PHASE23_QUICK_REFERENCE, TEST_PLAN, etc.) |
| [specs/teaching/spec.md](specs/teaching/spec.md) | Teaching mode | docs/planning/phases/phase-22/* |
| [specs/patterns/spec.md](specs/patterns/spec.md) | Patterns, compression | docs/planning/tiers/TIER_1 (13a, 2b); phase-11/PHASE11_COMPRESSION_SYSTEM |
| [specs/mental-models/spec.md](specs/mental-models/spec.md) | Mental models | docs/planning/phases/phase-14/*; MENTAL_MODELS_USER_GUIDE.md (root) |
| [specs/integrations/spec.md](specs/integrations/spec.md) | Integrations | docs/integration_status.md, filesystem_integration.md, calendar_signed_app_notes.md |
| [specs/security/spec.md](specs/security/spec.md) | Security | docs/SECURITY.md, docs/planning/phases/phase-23.5/* |

## By doc location (role in OpenSpec)

### docs/ (root level)

| Doc | Role | Feeds spec |
|-----|------|------------|
| API_KEYS.md | Reference | security, backend |
| ASYNC_RULES_QUICK_REF.md | Reference | backend |
| PERSONA_SYSTEM_ARCHITECTURE.md | Reference | personas |
| PERSONA_API.md | Reference | personas |
| RAG_ROUTING_ARCHITECTURE.md | Reference | rag |
| README_RAG_DOCS.md, RAG_TROUBLESHOOTING_QUICK_REFERENCE.md | Reference | rag |
| integration_status.md | Reference | integrations |
| filesystem_integration.md, calendar_signed_app_notes.md | Reference | integrations |
| SECURITY.md | Reference | security |
| DEVELOPMENT_CHECKLIST.md | Operations / process | project |
| PHASE16C_IMPLEMENTATION_CHECKLIST.md, PHASE16C_PROGRESS.md | Reference | notes |
| POST_MORTEM_*.md, DASHBOARD_*, PATTERN_*, phase_9_permissions.md, WEB_UI.md | Reference / ops | various |
| DAY*.md | Session / progress notes | project (historical) |

### docs/planning/

| Doc | Role | Feeds spec |
|-----|------|------------|
| README.md | Navigator | project, roadmap |
| DESIGN_PHILOSOPHY.md | Reference | design |
| KNOWN_ISSUES.md | Operations | project (backlog/ops) |
| RESEARCH_QUEUE.md | Backlog / ops | project |
| BACKLOG_INDEX.md | Index to backlog | project |
| BRAIN_DUMP_SUMMARY.md | Reference | project |

### docs/planning/tiers/

| Doc | Role | Feeds spec |
|-----|------|------------|
| TIER_0_FOUNDATION.md, TIER_1_INTELLIGENCE.md, TIER_2_PACKAGING.md | Reference | architecture, project, roadmap |

### docs/planning/phases/phase-*

Each phase folder is the **reference** for the corresponding capability. Summary:

- **phase-0.5** → ui
- **phase-1.5** → domains
- **phase-11** → personas, rag, patterns (compression)
- **phase-14** → mental-models
- **phase-16** → notes
- **phase-16c** → notes (AI note creation)
- **phase-16e** → notes (TOC, templates)
- **phase-21** → notes (dedup)
- **phase-22** → teaching
- **phase-23** → curriculum
- **phase-23.5** → security

### docs/planning/phases/other/

Planned/future phases and investigations. Role: **backlog / planning**. When a phase is started, create an OpenSpec change under `openspec/changes/` and link to the phase doc.

| Category | Examples |
|----------|----------|
| Future phases (24–29) | PHASE24_ORCHESTRATOR_MODE, PHASE25_CODE_ARCHITECTURE_SYSTEM, PHASE26_PROJECT_MANAGEMENT, PHASE27_DESIGNER_PERSONA, PHASE28_OPEN_POLLY_TOOLS, PHASE29_BUILT_IN_BROWSER |
| User profile, data autonomy | PHASE13B_USER_PROFILE_SYSTEM, PHASE19_DATA_AUTONOMY |
| Phase 17 (Code Workspace) / Void | PHASE17_*, VOID_*, VSCODE_* — reference or archived |
| Status summaries | PHASE_STATUS_SUMMARY, PHASE3_COMPLETE_SUMMARY, PHASE_0.5_TO_0.7_ROADMAP |

### docs/status/

| Doc | Role | Feeds spec |
|-----|------|------------|
| CURRENT.md | Detailed reference | specs/project/status.md (authoritative summary) |
| CHANGELOG.md | History | project (completion log) |

### docs/troubleshooting/

| Doc | Role | Feeds spec |
|-----|------|------------|
| COMPRESSION_UI_TROUBLESHOOTING.md, CONVERSATION_RELOAD_FIX.md, DOMAINS_FIX.md, ISSUES_TO_TROUBLESHOOT.md | Operations | patterns, ui, domains |
| todos/NOTES_SYSTEM_TODO.md | Backlog | notes |

### Root-level .md

| Doc | Role | Feeds spec |
|-----|------|------------|
| MASTER_ROADMAP.md | Reference (full roadmap/vision) | project, roadmap, architecture |
| FEATURES_TO_BUILD.md | Backlog | roadmap |
| ROADMAP_ANALYSIS_AND_NEXT_STEPS.md | Backlog / reference | project |
| BRAIN_DUMP_*.md | Reference / braindump | project |
| NATIVE_NOTES_GUIDE.md, NOTES_FUNCTIONALITY_IMPLEMENTATION.md | Reference | notes |
| MENTAL_MODELS_USER_GUIDE.md | Reference | mental-models |
| PHASE17_POC_EXECUTE_NOW.md, START_POC.md | Reference / historical | — |
| Other PHASE*_*.md, *_COMPLETE.md, *_GUIDE.md | Reference | See phase folders above |

### archive/

Historical and superseded docs. Role: **archive**. Keep for history; do not treat as source of truth.

### void-migration/

Void/VSCODE migration and build docs. Role: **reference / archive**. Not part of current product spec; reference only if needed.

---

## How to use this map

1. **When implementing a feature:** Find the OpenSpec spec for that domain (table 1). Use the listed reference docs for detail; keep the spec updated when behavior changes.
2. **When adding a new doc:** Add it to this map under the right spec or "Operations / Backlog".
3. **When changing behavior:** Update the OpenSpec spec first; then update any referenced doc that is still the canonical detail for that behavior.
