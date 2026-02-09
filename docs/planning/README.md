# Planning Documentation Navigator

**Purpose:** Central index for phase documentation and detailed planning.  
**Authoritative project tracking:** Status and roadmap live in **OpenSpec** — use those first for "where we are" and "what's next."  
**Full doc migration:** All docs are migrated into OpenSpec; every doc is mapped to a spec or to backlog/ops in [openspec/DOCUMENTATION_MAP.md](../../openspec/DOCUMENTATION_MAP.md).

**Last Updated:** February 2026

---

## Quick Navigation (OpenSpec-first)

- **Project Status (authoritative):** [openspec/specs/project/status.md](/openspec/specs/project/status.md)
- **Roadmap (authoritative):** [openspec/specs/project/roadmap.md](/openspec/specs/project/roadmap.md)
- **OpenSpec index:** [openspec/INDEX.md](/openspec/INDEX.md)
- **Completion History:** [docs/status/CHANGELOG.md](/docs/status/CHANGELOG.md)
- **Master Roadmap (full reference):** [MASTER_ROADMAP.md](/MASTER_ROADMAP.md)
- **Tier Organization:** [docs/planning/tiers/](#tier-based-organization)
- **Phase Documents:** [docs/planning/phases/](#phase-documentation)
- **Backlog index:** [docs/planning/BACKLOG_INDEX.md](BACKLOG_INDEX.md)

---

## How to Use This Documentation

### Finding What You Need

**"What's the current status?"**  
→ Read [openspec/specs/project/status.md](/openspec/specs/project/status.md)

**"What should I work on next?"**  
→ Check [openspec/specs/project/roadmap.md](/openspec/specs/project/roadmap.md) and "Recommended Next Steps" in [docs/status/CURRENT.md](/docs/status/CURRENT.md)

**"Has Phase X been completed?"**  
→ Check [openspec/specs/project/status.md](/openspec/specs/project/status.md) or [openspec/specs/project/roadmap.md](/openspec/specs/project/roadmap.md); history in [docs/status/CHANGELOG.md](/docs/status/CHANGELOG.md)

**"What does Phase X involve?"**  
→ Navigate to `/docs/planning/phases/phase-XX/` or check the tier documents

**"What phases are in Tier Y?"**  
→ Read `/docs/planning/tiers/TIER_Y_NAME.md`

**"Where's the detailed implementation plan?"**  
→ See [/MASTER_ROADMAP.md](/MASTER_ROADMAP.md) - the complete project roadmap

---

## Tier-Based Organization

Phases are organized into tiers representing different stages of development:

### Tier 0: Foundation & UI ✅ 100% Complete
**Status:** All phases complete  
**Duration:** ~3 weeks  
**Documentation:** `/docs/planning/tiers/TIER_0_FOUNDATION.md` (to be created)

**Phases:**
- Phase 0.5: Obsidian-Inspired UI Redesign ✅
- Phase 1: Configuration System ✅
- Phase 3: Backend Server ✅
- Phase 4: Electron Application ✅
- Phase 5: Secrets Manager ✅

**Impact:** Production-ready desktop application with professional UI

### Tier 1: Core Intelligence 🔄 ~70% Complete
**Status:** 9 of 12-13 phases complete  
**Duration:** ~17-21 weeks total  
**Documentation:** `/docs/planning/tiers/TIER_1_INTELLIGENCE.md` (to be created)

**Completed Phases:**
- Phase 1.5: Domain Configuration ✅
- Phase 2a: RAG Optimization ✅
- Phase 2b: Pattern Compression ✅
- Phase 11: Multi-Model Routing & Agent Personas ✅
  - Phase 11a: Router v2 Core ✅
  - Phase 11b: Provider Adapters ✅
  - Phase 11c: Agent Personas Framework ✅
- Phase 11c: Compression UI ✅
- Phase 13a: Pattern Learning Core ✅
- Phase 14: Mental Models System ✅
- Phase 16: Native Notes Frontend ✅
- Phase 16e: TOC & Templates ✅
- Phase 21: Knowledge Base Deduplication ✅

**In Progress/Pending:**
- Phase 23.5: Security Hardening 🔐 (CRITICAL - planning complete, ready for implementation)
- Phase 16c: AI Note Creation 🔄 (backend ready, frontend pending)
- Phase 22: Teaching Mode 📋 (deferred until after Phase 23.5)
- Phase 12a: Knowledge Graph Basic 📋
- Phase 12b: Knowledge Graph Advanced 📋

**Impact:** Intelligent AI assistant that learns, adapts, and specializes

### Tier 2: Packaging & Permissions 📋 Not Started
**Status:** 0% complete  
**Duration:** ~1 week  
**Documentation:** `/docs/planning/tiers/TIER_2_PACKAGING.md` (to be created)

**Phases:**
- Phase 9: macOS Permissions (2-3 days)
- App Signing/Notarization (2-3 days)
- UI Polish Sprint (1 week)

**Impact:** Production-ready deployment

### Tier 3: Polish & Autonomy 📋 Not Started
**Status:** 0% complete  
**Duration:** ~2-3 weeks  
**Documentation:** `/docs/planning/tiers/TIER_3_POLISH.md` (to be created)

**Phases:**
- Phase 18: Onboarding & Progressive Teaching (1-2 weeks)
- Phase 19: Data Autonomy & Export (5-7 days)

**Impact:** User-friendly onboarding and data ownership

### Tier 4: Advanced Communication 📋 Not Started
**Status:** 0% complete  
**Duration:** ~2-3 weeks  
**Documentation:** `/docs/planning/tiers/TIER_4_COMMUNICATION.md` (to be created)

**Phases:**
- Phase 20a: Email Intelligence (1 week)
- Phase 20b: Calendar & Action Items (1 week)
- Phase 20c: Communication Progressive Autonomy (3-5 days)

**Impact:** Proactive communication assistance

---

## Phase Documentation

### Completed Phases (Detailed Reports)

#### Phase 11: Multi-Model Routing & Agent Personas ✅
**Completion Date:** January 30, 2026  
**Report:** [/PHASE11_COMPLETE.md](/PHASE11_COMPLETE.md)

**Sub-Phases:**
- Phase 11a: Router v2 Core (601 lines)
- Phase 11b: Provider Adapters (3,916 lines)
- Phase 11c: Agent Personas Framework (3,181 lines)

**Key Files:**
- `/core/router_v2.py`
- `/core/providers/*.py`
- `/core/personas/*.py`

#### Phase 16e: TOC & Templates ✅
**Completion Date:** February 1, 2026  
**Report:** [/PHASE16E_COMPLETE.md](/PHASE16E_COMPLETE.md)

**Implementation:**
- TOC sidebar: 150 lines
- Template system: 342 lines backend + frontend

**Key Files:**
- `/electron-app/src/renderer/notes-manager.js:1757-1909`
- `/core/templates/manager.py`
- `/core/templates/template.py`

#### Other Completed Phases
See [/docs/status/CHANGELOG.md](/docs/status/CHANGELOG.md) for complete list and details.

### In Progress/Pending Phases

#### Phase 16c: AI Note Creation 🔄
**Status:** Backend ready, frontend pending  
**Depends On:** Phase 11 ✅ (complete)  
**Estimated Effort:** 4 weeks

**Documentation:**
- Spec: `PHASE16C_AI_NOTE_CREATION.md`
- Implementation Plan: `PHASE16C_OPTION_A_PLAN.md`
- Checklist: `PHASE16C_IMPLEMENTATION_CHECKLIST.md`

**What's Ready:**
- Architect persona (Plan/Build modes) ✅
- Router v2 for model selection ✅
- Template system ✅

**What's Needed:**
- Intent detection for note requests
- API endpoints for persona operations
- Inline Q&A UI for clarifying questions
- Preview modal with edit capabilities
- Save to `_Drafts/` workflow

#### Phase 23.5: Security Hardening 🔐
**Status:** Planning complete, ready for implementation  
**Priority:** CRITICAL (must complete before Phase 24)  
**Depends On:** Phase 23 ✅ (complete)  
**Estimated Effort:** 2-3 weeks

**Documentation:**
- Spec: `PHASE23.5_SECURITY_HARDENING.md`
- Implementation Plan: `PHASE23.5_IMPLEMENTATION_PLAN.md`

**Scope:**
- Capability Broker Pattern for security
- Pyodide sandbox for code execution
- Package allowlist with approval workflow
- Context7 integration for package trust scores
- Content sanitization (prompt injection detection)
- PII detection (warn-only mode)
- API key hardening with context managers

#### Phase 22: Teaching Mode 📋
**Status:** Deferred until after Phase 23.5  
**Depends On:** Phase 14 ✅ (complete), Phase 23.5 🔐 (security)  
**Estimated Effort:** 2-3 days

**Documentation:**
- Spec: `PHASE22_TEACHING_MODE.md`

**Scope:**
- Capture personal mental models through conversation
- Guided teaching workflow
- Integration with existing mental models system
- Domain-specific teaching

#### Phase 12a: Knowledge Graph Basic 📋
**Status:** Ready to start  
**Estimated Effort:** 5-7 days

**Scope:**
- Interactive Cytoscape.js visualization
- 5 node types (Note, Concept, Person, Project, Domain)
- 4 edge types (Links to, Related to, Part of, Mentions)
- Real-time updates from notes
- Click-to-navigate

---

## Phase Naming Conventions

**Phase Numbering:**
- **Phase X:** Major phase (e.g., Phase 11, Phase 16)
- **Phase Xa:** Sub-phase (e.g., Phase 11a, Phase 11b, Phase 11c)
- **Phase X.Y:** Decimal indicates variant/alternative (e.g., Phase 0.5, Phase 1.5)

**Status Indicators:**
- ✅ Complete
- 🔄 In progress
- 📋 Planned but not started
- ❌ Cancelled/deferred
- 🚧 On hold

**Phase Folder Structure:**
```
/docs/planning/phases/
├── phase-01/         # Phase 1: Configuration System
├── phase-03/         # Phase 3: Backend Server
├── phase-04/         # Phase 4: Electron Application
├── phase-05/         # Phase 5: Secrets Manager
├── phase-11/         # Phase 11: Multi-Model Routing (all sub-phases)
├── phase-16/         # Phase 16: Native Notes Frontend
├── phase-16c/        # Phase 16c: AI Note Creation
├── phase-16e/        # Phase 16e: TOC & Templates
├── phase-22/         # Phase 22: Teaching Mode
└── ...
```

---

## Phase Dependencies

**Dependency Chain (Tier 1):**

```
Phase 1 (Config) ──┬──> Phase 5 (Secrets) ──> Phase 11 (Multi-Model)
                   │
                   ├──> Phase 1.5 (Domains) ──┬──> Phase 13a (Patterns)
                   │                           │
                   └──> Phase 3 (Server) ──────┴──> Phase 14 (Mental Models) ──> Phase 22 (Teaching)
                                                │
                                                └──> Phase 16 (Notes) ──┬──> Phase 21 (Dedup)
                                                                        │
                                                                        └──> Phase 16e (TOC/Templates)

Phase 11 (Multi-Model) ──> Phase 16c (AI Note Creation)

Phase 13a (Patterns) + Phase 14 (Mental Models) ──> Phase 12a (Knowledge Graph)
```

**Critical Path:**
1. Foundation (Phases 1, 3, 4, 5) ✅
2. Core Intelligence (Phases 1.5, 13a, 14, 11) ✅
3. Advanced Features (Phases 16c, 22, 12a) 🔄

---

## Investigation Documents

For research and exploration documents that informed phase design:

**Location:** `/docs/planning/investigations/`

**Examples:**
- Architecture decisions
- Technology evaluations
- Performance benchmarks
- Design explorations

---

## Documentation Maintenance

### When Completing a Phase

1. **Update Status Documents:**
   - Add entry to `docs/status/CHANGELOG.md` (top of file)
   - Update `openspec/specs/project/status.md` and `openspec/specs/project/roadmap.md` with completion
   - Update `docs/status/CURRENT.md` with completion (detailed reference)
   - Mark phase as ✅ in relevant tier document

2. **Create Completion Report:**
   - Create `PHASE_XX_COMPLETE.md` in project root
   - Document implementation details, files, metrics
   - Include success criteria verification

3. **Organize Phase Documentation:**
   - Move phase planning docs to `/docs/planning/phases/phase-XX/`
   - Update cross-references
   - Archive obsolete documents

4. **Update This Navigator:**
   - Move phase from "Pending" to "Completed"
   - Update statistics
   - Update dependency chain if needed

### When Starting a Phase

1. **Check Prerequisites:**
   - Verify dependencies (check [openspec/specs/project/status.md](/openspec/specs/project/status.md) and [openspec/specs/project/roadmap.md](/openspec/specs/project/roadmap.md))
   - Review phase specification in `docs/planning/phases/phase-XX/`
   - Check for related completion reports

2. **Create an OpenSpec change:**
   - Create `openspec/changes/<change-name>/` (e.g. `phase-23.5-security-hardening/`)
   - Add `proposal.md`, `design.md`, `tasks.md`
   - Phase directory under `docs/planning/phases/phase-XX/` holds detailed spec (reference)

3. **Track Progress:**
   - Implement per design and tasks
   - Update `openspec/specs/project/status.md` and `openspec/specs/project/roadmap.md` when done
   - Add completion entry to `docs/status/CHANGELOG.md`

---

## Statistics

**Total Phases Defined:** 25+  
**Completed Phases:** 14 major phases  
**In Progress:** 1 phase (Phase 16c)  
**Ready to Start:** 2 phases (Phase 22, Phase 12a)

**Documentation Files:**
- Status documents: 2 (CURRENT.md, CHANGELOG.md)
- Completion reports: 10+
- Phase specifications: 25+
- Total documentation: ~50,000+ words

---

## Related Resources

**Planning Documents:**
- [MASTER_ROADMAP.md](/MASTER_ROADMAP.md) (redirect); full text: [archive/root-docs/MASTER_ROADMAP.md](/archive/root-docs/MASTER_ROADMAP.md)
- [archive/root-docs/FEATURES_TO_BUILD.md](/archive/root-docs/FEATURES_TO_BUILD.md) - Feature backlog
- [archive/root-docs/BRAIN_DUMP_2026-01-31.md](/archive/root-docs/BRAIN_DUMP_2026-01-31.md) - Brainstorming notes

**Troubleshooting:**
- [/docs/troubleshooting/KNOWN_ISSUES.md](/docs/troubleshooting/KNOWN_ISSUES.md) (to be created)
- [/docs/troubleshooting/todos/](/docs/troubleshooting/todos/) - Tracked issues

**User Guides:**
- [MENTAL_MODELS_USER_GUIDE.md](/MENTAL_MODELS_USER_GUIDE.md) - Mental models usage
- [/docs/guides/](/docs/guides/) - Developer and user guides

**Architecture:**
- [PERSONA_SYSTEM_ARCHITECTURE.md](/PERSONA_SYSTEM_ARCHITECTURE.md)
- [RAG_ROUTING_ARCHITECTURE.md](/RAG_ROUTING_ARCHITECTURE.md)
- [/docs/](/docs/) - Various architecture documents

---

## Contributing to Documentation

**Style Guidelines:**
- Use clear, concise language
- Include code examples where relevant
- Date all documents prominently
- Cross-reference related documents
- Use consistent formatting (Markdown)

**File Naming:**
- UPPERCASE for important files (CURRENT.md, CHANGELOG.md)
- Phase docs: `PHASE##_DESCRIPTION.md` or `PHASE##X_DESCRIPTION.md`
- Completion reports: `PHASE##_COMPLETE.md`
- lowercase for supporting files

**Update Frequency:**
- Status documents: After each phase completion
- Changelog: Every phase completion
- This navigator: Monthly or after major changes

---

**Maintained By:** Development team  
**Questions?** Check [/docs/status/CURRENT.md](/docs/status/CURRENT.md) first, then ask!
