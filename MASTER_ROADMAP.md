# Polly Master Roadmap & Planning Document

**Last Updated:** February 1, 2026 (Phase 11 & 16e Complete - Documentation Reorganization)  
**Project:** Polly - Edge-Native Personal AI System  
**Status:** Active Development (~70% Complete - Tier 0: 100%, Tier 1: ~70%)

---

## 📌 IMPORTANT: Documentation Has Been Reorganized

**For current project status, see:**
- **[docs/status/CURRENT.md](docs/status/CURRENT.md)** - Single source of truth for project status
- **[docs/status/CHANGELOG.md](docs/status/CHANGELOG.md)** - Chronological completion history
- **[docs/planning/README.md](docs/planning/README.md)** - Navigate all planning documentation

**For detailed phase information:**
- **[docs/planning/tiers/](docs/planning/tiers/)** - Tier-based organization (TIER_0, TIER_1, TIER_2)
- **[docs/planning/phases/](docs/planning/phases/)** - Individual phase specifications

**This document provides the overall roadmap and vision. For up-to-date status, always check `docs/status/CURRENT.md` first.**

---

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Project Overview](#project-overview)
3. [Architecture Summary](#architecture-summary)
4. [Current Status](#current-status)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Detailed Phase Plans](#detailed-phase-plans)
7. [Dependencies & Risk Management](#dependencies--risk-management)
8. [Future Enhancements](#future-enhancements)
9. [Reference](#reference)

---

## Quick Start Guide

### What To Do Next

**FIRST: Check Current Status**
→ Read [docs/status/CURRENT.md](docs/status/CURRENT.md) for up-to-date project status

**If you're ready to start implementing:**

1. **Review completed work** - Tier 0 (100%), Tier 1 (~70%) complete
2. **Choose next phase** - See recommendations in [docs/status/CURRENT.md](docs/status/CURRENT.md)
3. **Read phase documentation** - Find specs in [docs/planning/phases/](docs/planning/phases/)
4. **Track progress** - Use the todo system to stay organized
5. **Test incrementally** - Verify each phase works before moving to the next

### Recommended Next Steps

See [docs/status/CURRENT.md](docs/status/CURRENT.md) for current recommendations.

Quick links to likely next phases:
- **Phase 22:** Teaching Mode (2-3 days) - [docs/planning/phases/phase-22/](docs/planning/phases/phase-22/)
- **Phase 16c:** AI Note Creation (4 weeks) - [docs/planning/phases/phase-16c/](docs/planning/phases/phase-16c/)
- **Phase 12a:** Knowledge Graph Basic (5-7 days) - [docs/planning/phases/other/](docs/planning/phases/other/)

### Implementation Priority

**For detailed tier information, see:**
- [docs/planning/tiers/TIER_0_FOUNDATION.md](docs/planning/tiers/TIER_0_FOUNDATION.md)
- [docs/planning/tiers/TIER_1_INTELLIGENCE.md](docs/planning/tiers/TIER_1_INTELLIGENCE.md)
- [docs/planning/tiers/TIER_2_PACKAGING.md](docs/planning/tiers/TIER_2_PACKAGING.md)

**TIER 0: Design System Foundation** ← ✅ 100% COMPLETE (Jan 26, 2026)

See [docs/planning/tiers/TIER_0_FOUNDATION.md](docs/planning/tiers/TIER_0_FOUNDATION.md) for details.

- **Phase 0.5:** Obsidian-Inspired UI Redesign ✅
- **Phase 1:** Configuration System ✅
- **Phase 3:** Backend Server ✅
- **Phase 4:** Electron Application ✅
- **Phase 5:** Secrets Manager ✅

**TIER 1: Core Intelligence** ← 🔄 ~70% COMPLETE

See [docs/planning/tiers/TIER_1_INTELLIGENCE.md](docs/planning/tiers/TIER_1_INTELLIGENCE.md) for details.

**Completed (9 phases):**
1. **Phase 1.5:** Domain Configuration ✅
2. **Phase 2a:** RAG Optimization ✅
3. **Phase 2b:** Pattern Compression ✅
4. **Phase 11:** Multi-Model Routing & Agent Personas ✅
   - Phase 11a: Router v2 Core ✅
   - Phase 11b: Provider Adapters ✅
   - Phase 11c: Agent Personas Framework ✅
5. **Phase 11c:** Compression UI ✅
6. **Phase 13a:** Pattern Learning Core ✅
7. **Phase 14:** Mental Models System ✅
8. **Phase 16:** Native Notes Frontend ✅
9. **Phase 16e:** TOC & Templates ✅
10. **Phase 21:** Knowledge Base Deduplication ✅

**In Progress / Pending (3-4 phases):**
1. **Phase 16c:** AI Note Creation 🔄 (backend ready, frontend pending, 4 weeks)
2. **Phase 22:** Teaching Mode 📋 (fully unblocked, 2-3 days)
3. **Phase 12a:** Knowledge Graph - Basic 📋 (ready to start, 5-7 days)
8. **Phase 12b:** Knowledge Graph - Reasoning Transparency (1-2 weeks)
9. **Phase 11:** Multi-Model + Intelligent Routing (5 weeks - see PHASE11_MULTI_MODEL_ENHANCED_V2.md)
   - Phase 11a: Core Routing + Primary Providers (2 weeks)
   - Phase 11b: Extended Providers + Safety (2 weeks)
   - Phase 11c: Orchestration + Compression (1 week)
10. **Phase 16:** Native Notes Frontend (1 day) - ✅ COMPLETE (Jan 26, 2026)
11. **Phase 16c:** Scribe Persona + Skill System (3-4 weeks) - ✅ COMPLETE (Jan 31, 2026)
12. **Phase 16d:** Notes System Polish (ON HOLD - see NOTES_SYSTEM_TODO.md)
13. **Phase 16e:** TOC Sidebar + Template System (3-4 days) - 🚧 IN PROGRESS (Feb 1, 2026)
13. **Phase 17:** Librarian Persona (2-3 weeks)
14. **Phase 18:** Programmer Persona (2-3 weeks)
15. **Phase 19:** Architect Persona Refactor (2 weeks)
16. **Phase 20:** Professor Persona (2-3 weeks)
17. **Phase 21-Orchestrator:** Orchestrator Mode Toggle (1 week)
18. **Phase 22-Administrator:** Administrator Persona (2 weeks)
19. **Phase 23+:** User Extensibility (4-6 weeks) - YAML personas, custom skills, marketplace
20. **Phase 15:** MCP Server (5-7 days)
21. **Phase 17-Code:** Code Workspace (3 weeks)

**BETWEEN TIER 1 & 2: UI Polish Sprint (1 week)**

After Tier 1 is complete, before packaging:
- Update remaining UIs to match design system
- Smooth transitions, micro-interactions, consistency pass

**TIER 2: Packaging & Permissions (1 week)**

After Tier 1 is complete:
- App Signing/Notarization (2-3 days)
- Phase 9: macOS Permissions (2-3 days)

**TIER 3: Polish & Autonomy Awareness (2-3 weeks)** ← RECOMMENDED

After Tier 2:
- Phase 18: Onboarding & Progressive Teaching (1-2 weeks)
- Phase 19: Data Autonomy & Export (5-7 days)

**TIER 4: Advanced Communication (2-3 weeks)** ← OPTIONAL

After Tier 2 (parallel with Tier 3):
- Phase 20a: Email Intelligence (1 week)
- Phase 20b: Calendar & Action Items (1 week)
- Phase 20c: Communication Progressive Autonomy (3-5 days)

**See [Implementation Roadmap](#implementation-roadmap) for details.**

---

## Project Overview

### Vision

Polly is an edge-first AI system designed to deeply understand you through your domains, learn your patterns, execute efficiently by routing between local and cloud models, and work across all your devices.

### Core Principles

- **Continuation over completion** - The system evolves with you
- **Instruments over tracks** - Generative tools that create new possibilities
- **Constraint as meaning-creation** - Boundaries that enable rather than limit
- **Autonomous infrastructure** - You own the stack, no platform lock-in

### Marketing Positioning

**For full marketing strategy, see:** `MARKETING_POSITIONING.md`

Polly's technical architecture directly supports key marketing themes:

#### Core Themes

**1. "Your work doesn't fit in boxes"**
- **Technical:** Phase 1.5 enables user-defined polymathic domains (not rigid categories)
- **Audience:** Cross-domain thinkers, polymaths, researchers, creative professionals
- **Differentiator:** vs. Notion/Obsidian's rigid folder structures

**2. "Stop organizing. Start working."**
- **Technical:** Phase 1.5 (zero-config auto-filing), Phase 16c (auto-organization mode)
- **Audience:** ADHD users, people overwhelmed by organization systems
- **Differentiator:** vs. Obsidian (requires manual organization)

**3. "Knowledge that compounds"**
- **Technical:** Phase 11 (progressive autonomy), Phase 18 (autonomy dashboard), Phase 20c (pattern → rule conversion)
- **Message:** "System gets smarter as you use it, eventually handling routine tasks autonomously"
- **Differentiator:** vs. ChatGPT/Claude (stateless, always the same)

**4. "See how you think"**
- **Technical:** Phase 12 (knowledge graph with reasoning transparency)
- **Message:** "Visualize connections, understand why Polly makes decisions"
- **Differentiator:** vs. AI black boxes (transparent reasoning)

**5. "Your data. Your freedom."**
- **Technical:** Phase 19 (complete data export, self-hosting, offline mode)
- **Audience:** Privacy-conscious professionals, data sovereignty advocates
- **Differentiator:** vs. ChatGPT/Claude (cloud-locked, no export)

**6. "Build capability, don't rent it"**
- **Technical:** Phase 20c (communication autonomy), Phase 11 (local model preference)
- **Message:** "Learn patterns → create rules → become independent of AI (and costs)"
- **Differentiator:** vs. Jace.ai (permanent AI dependency)

#### Target Audiences

1. **Polymaths/Cross-Domain Workers:** Researchers, creative professionals, entrepreneurs
2. **ADHD/Neurodivergent Users:** Need low-friction systems, auto-organization
3. **Privacy-Conscious Professionals:** Lawyers, healthcare, finance, security researchers
4. **AI-Savvy Early Adopters:** Developers, data scientists, power users
5. **Knowledge Workers Drowning in Tools:** Need consolidation, single source of truth

#### Phase-Marketing Alignment

| Phase | Marketing Theme | Tagline |
|-------|----------------|---------|
| 1.5 | "Your work doesn't fit in boxes" | Zero-config quick start OR custom polymathic domains |
| 11 | "Knowledge that compounds" | Progressive autonomy: local models get smarter over time |
| 12 | "See how you think" | Transparent reasoning: "Why this connection?" |
| 16 | "Stop organizing. Start working." | AI-powered auto-organization and note creation |
| 18 | "Polly teaches you as you teach Polly" | Progressive feature revelation, autonomy dashboard |
| 19 | "Your data. Your freedom." | Complete data export, self-hosting, offline mode |
| 20 | "Build capability, don't rent it" | Email/calendar patterns become local rules |

#### Anti-Messages (What We're NOT Saying)

- ❌ "Organize your life" (we're not another productivity guilt trip)
- ❌ "AI does everything for you" (we build your capability, not dependency)
- ❌ "One tool to rule them all" (we integrate, not replace everything)
- ❌ "Effortless" (learning Polly takes effort, but compounds over time)
- ❌ "Enterprise-ready" (we're for individuals, not corporations)

### Domains System

**Important:** As of Phase 1.5, domains are now **user-configurable**. Users can define their own domain structure to match their workflow.

**Default/Template Domains (Examples):**

| Domain | Focus | File Patterns |
|--------|-------|---------------|
| **Sigils** 🔐 | Code, infrastructure, automation, security | `.py`, `.rs`, `.go`, `docker-compose.yaml` |
| **Signals** 📡 | Audio programming, synthesis, communication | `.scd`, `.lua`, `norns/`, `supercollider/` |
| **Scrolls** 📜 | Writing, pedagogy, documentation | `.md`, `vault/`, `essays/` |
| **Glyphs** ✨ | Visual work, design, UI | `.fig`, `.sketch`, `design/` |
| **Grids** 🗂️ | Systems thinking, frameworks, data | `frameworks/`, `models/`, tagged notes |

**Note:** Users can customize domains via Phase 1.5's domain configuration system. Six templates are provided including Software Development, Research, Creative Writing, Personal Knowledge, Academic/Student, and Polly Creator.

---

## Architecture Summary

```
┌────────────────────────────────────────────────────────────────┐
│                         POLLY CORE                              │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │   Domains   │  │   Pattern   │  │    Intelligent Router   ││
│  │   Engine    │  │   Learner   │  │   (Local ↔ Cloud)       ││
│  │  (Phase 1.5)│  │  (Phase 13) │  │   (Phase 11 Enhanced)   ││
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘│
│         │                │                      │              │
│         └────────────────┴──────────────────────┘              │
│                          │                                      │
│              ┌───────────▼───────────┐                         │
│              │   Unified RAG Layer   │                         │
│              │   ┌─────────────────┐ │                         │
│              │   │ Obsidian Vault  │ │                         │
│              │   │ GitHub Repos    │ │                         │
│              │   │ Context7 Docs   │ │                         │
│              │   │ Pattern Memory  │ │                         │
│              │   │ Mental Models   │ │                         │
│              │   │ Native Notes    │ │ (Phase 16)              │
│              │   └─────────────────┘ │                         │
│              └───────────────────────┘                         │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                    CONVERSATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Multi-Conversation System (SQLite)                       │ │
│  │ • 5 Domain Categories + Uncategorized                    │ │
│  │ • Star/Pin Protection                                    │ │
│  │ • Auto-cleanup (60-day retention)                        │ │
│  │ • LLM Auto-titling                                       │ │
│  │ • Search & Filtering                                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                    KNOWLEDGE LAYER (NEW)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Knowledge Graph (Phase 12)                               │ │
│  │ • Interactive Visualization (Cytoscape.js)               │ │
│  │ • 5 Node Types: Notes, Code, Concepts, Convos, Repos    │ │
│  │ • 4 Edge Types: Links, Imports, Similarity, Relations   │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Native Notes System (Phase 16)                           │ │
│  │ • Monaco Editor with Markdown                            │ │
│  │ • Wiki-links, Backlinks, Tags                            │ │
│  │ • Domain Auto-tagging                                    │ │
│  │ • AI Note Creation                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Code Workspace (Phase 17)                                │ │
│  │ • Monaco Editor (9 languages)                            │ │
│  │ • Integrated Terminal                                    │ │
│  │ • Git Operations UI                                      │ │
│  │ • Context-aware Chat Panel                               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                       INTERFACES                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Electron │  │  FastAPI │  │  MCP     │  │   IPC/REST   │  │
│  │   App    │  │  Server  │  │  Server  │  │   Bridge     │  │
│  │          │  │          │  │(Phase 15)│  │              │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Current Status

### Completed Features (Phases 1-5)

**✅ Phase 1: UI Foundation**
- Tabbed navigation system
- Integration cards with brutalist design
- Settings persistence
- Responsive design

**✅ Phase 2: GitHub OAuth & Credentials**
- macOS Keychain integration
- OAuth flow with browser window
- Secure token storage
- Persistent connection status

**✅ Phase 3: Obsidian Integration**
- Smart folder/tag suggestions
- Related notes discovery (RAG-powered)
- Conversation-to-note creation
- Daily note templates
- **Current index:** 1,152 chunks from 75 files
- **Recent enhancements (Jan 24, 2026):**
  - Fixed markdown chunker to preserve section structure (subsections stay with parent headers)
  - Fixed integration keyword matching (word boundaries to prevent false positives)
  - Fixed related notes similarity threshold (0.7 → 0.01 for hybrid search RRF scores)
  - Added filepath deduplication for related notes
  - Enhanced RAG instructions for domain-specific queries (e.g., Practices & Exercises)
  - Improved chunk quality: full PRACTICE sections with all exercises (~1000-1200 chars each)

**✅ Phase 4: Multi-Conversation System**
- SQLite-based storage
- 6 categories (5 domains + uncategorized)
- Star/pin protection
- Auto-cleanup (60-day retention)
- LLM auto-titling
- Search & filtering

**✅ Phase 5: Backend Integration Framework**
- Base integration classes
- State persistence
- GitHub integration (17 repos synced)
- Context7 integration
- **Total indexed:** ~4,000+ documents

**✅ Hybrid Local/Cloud Routing** (✅ COMPLETE - Jan 28, 2026)
- **Document:** `HYBRID_ROUTING_COMPLETE.md`
- **What It Does:**
  - Intelligent routing between local Ollama (free) and cloud providers (paid)
  - RAG quality-based decision making (5 configurable thresholds)
  - User-facing Settings UI with threshold sliders
  - Three quick presets: Aggressive Local, Balanced, Conservative Cloud
  - Real-time usage statistics (local vs cloud queries, cost saved)
  - Config persistence to `~/.polly/config.yaml`
- **Implementation:**
  - Backend routing logic: `core/polly.py` (+180 lines)
  - Config save method: `core/config.py` (+10 lines)
  - API endpoints: `interfaces/server.py` (+110 lines)
    - GET `/routing/settings` - Retrieve configuration
    - POST `/routing/settings` - Update configuration
    - GET `/routing/stats` - Usage statistics
  - Settings UI: `electron-app/src/renderer/` (+440 lines)
- **Value:** 40-70% cost reduction by routing to local when RAG context is strong
- **Status:** ✅ Complete, tested, ready for user testing
- **Note:** This is NOT Phase 11 (Multi-Provider Routing). This is a simpler threshold-based system that decides local vs cloud. Phase 11 will decide WHICH cloud provider.

**🚧 Phase 1.5: Domain Configuration System** (✅ COMPLETE - Jan 25, 2026)
- **Completed (Days 1-2, Jan 24, 2026):**
  - ✅ Domain config system (`core/domain_config.py` - 440 lines)
  - ✅ Migration to `~/.polly/domains.json`
  - ✅ Updated `core/domains.py` and `learners/patterns.py`
  - ✅ All 3,405 patterns preserved
  - ✅ 8/8 end-to-end tests passing
  - ✅ Documentation: `PHASE1.5_MIGRATION_COMPLETE.md`
- **Completed (Days 3-4, Jan 24-25, 2026):**
  - ✅ Settings UI for domain management
  - ✅ Domain editor modal
  - ✅ Server API endpoints (6 endpoints)
- **Completed (Day 5, Jan 25, 2026):**
  - ✅ Use Case 2: Pattern-Boosted Domain Detection (146% boost!)
  - ✅ Test suite (`test_use_case_2.py` - 4 scenarios)
  - ✅ Documentation: `USE_CASE_2_COMPLETE.md`
- **Completed (Day 6, Jan 25, 2026):**
  - ✅ First-run detection (`is_first_run()`)
  - ✅ Quick-start domains (3 domains)
  - ✅ Template system (`core/domain_templates.py` - 4 templates)
  - ✅ CLI wizard (`setup_wizard.py` - interactive tool)
  - ✅ Documentation: `PHASE1.5_DAY6_COMPLETE.md`
- **Deferred:**
  - ⏸️ UI wizard (React/Electron) - deferred to Phase 18 (Onboarding)
  - ⏸️ AI keyword suggestions - deferred to Phase 18

**✅ Phase 16: Native Notes Frontend** (✅ COMPLETE - Jan 26, 2026)
- Beautiful notes browser with file tree
- Monaco editor with markdown
- Wiki-links with automatic reference updates
- Backlinks panel and tags
- Quick switcher (Cmd+O)
- Drag-and-drop organization
- Auto-save with status indicators
- **Document:** `PHASE16_COMPLETE.md`

**✅ Phase 16c: Native Knowledge Base + Scribe Persona** (✅ COMPLETE - Jan 31, 2026)
- **Documents:** 
  - `NOTES_SYSTEM_TODO.md` - Polish tasks on hold
  - Session summary in conversation history
- **What Was Built:**
  - ✅ Fixed native KB notes indexing (path filtering bug)
  - ✅ Fixed Obsidian auto-connect on startup
  - ✅ Implemented migration UI (always visible in Settings)
  - ✅ Completed test migration (101 files from Obsidian)
  - ✅ Fixed console warnings (Python skill manager, JS file watcher)
  - ✅ Initialized notes sync manager on server startup
  - ✅ **Fixed file watcher event detection (CRITICAL BUG)**
    - File watcher was filtering out ALL files due to path checking bug
    - Now works perfectly: create/modify/delete detection
    - Real-time auto-indexing to RAG (2-second debounce)
    - 110 notes indexed, 899 RAG chunks from 44 files
- **Current System State:**
  - Notes source: `native` (using `~/.polly/notes/`)
  - File watcher: Running and monitoring for changes
  - Migration: 107 notes migrated from Obsidian
  - RAG: Auto-updates when notes change
- **What's On Hold (Phase 16d):**
  - Complete RAG indexing (44/110 files - remaining 66 need manual re-index)
  - Debug logging reduction
  - File watcher UI status indicator
  - Migration progress feedback
  - Template system
  - Backlinks graph view
  - Tag browser
  - Note versioning
  - Full-text search UI
  - See `NOTES_SYSTEM_TODO.md` for complete list

### Implemented But Disabled (Awaiting Phase 9)

**⏸️ Calendar Integration** (`/integrations/calendar.py`)
- EventKit implementation complete
- Requires Calendar permission
- Will be enabled in Phase 9

**⏸️ Reminders Integration** (`/integrations/reminders.py`)
- EventKit implementation complete
- Requires Reminders permission
- Will be enabled in Phase 9

**⏸️ File System Integration** (`/integrations/filesystem.py`, `filesystem_llm.py`)
- Full file operations complete (~900 lines)
- Finder tags, NL file operations
- Requires Full Disk Access
- Will be enabled in Phase 9

**Total:** ~1,400 lines of working code waiting for permissions

### Planned Features (Phases 1.5-20)

See [Implementation Roadmap](#implementation-roadmap) below for full details.

**NEW PHASES (Tier 0):**
- **Phase 0.5:** UI Design System Foundation (4-6 days) - Shadcn/ui + Tailwind setup, component library

**NEW PHASES (Tier 1):**
- **Phase 1.5:** Domain Configuration System (6 days) - User-definable domains + zero-config
- **Phase 11 Enhanced:** Multi-Model + Intelligent Routing (10-14 days) - Confidence-based routing
- **Phase 12 Enhanced:** Knowledge Graph + Reasoning Transparency (2.5-3.5 weeks) - "Why this connection?"
- **Phase 16:** Native Note Management (3.5-4.5 weeks) - Obsidian replacement with auto-organization
- **Phase 17:** Code Workspace (3 weeks) - Integrated development environment

**NEW PHASES (Tier 3):**
- **Phase 18:** Onboarding & Progressive Teaching (1-2 weeks) - First-run wizard + autonomy dashboard
- **Phase 19:** Data Autonomy & Export (5-7 days) - Complete export + self-hosting + offline mode

**NEW PHASES (Tier 4):**
- **Phase 20a:** Email Intelligence (1 week) - Privacy-first email categorization
- **Phase 20b:** Calendar & Action Items (1 week) - Meeting analysis + action extraction
- **Phase 20c:** Communication Progressive Autonomy (3-5 days) - Pattern → rule conversion

**EXISTING PHASES (Enhanced Planning):**
- **Phase 11:** Multi-Model Selection (original) → merged into Phase 11 Enhanced
- **Phase 12:** Knowledge Graph Visualization (original 5-7 days) → enhanced to 2.5-3.5 weeks
- **Phase 13:** Pattern Learning Overhaul (1-2 weeks)
- **Phase 14:** Mental Models System (3-5 days)
- **Phase 15:** MCP Server Integration (5-7 days)
- **Phase 9:** macOS Permission Handling (2-3 days) - deferred to Tier 2

---

## Implementation Roadmap

### Overview

The roadmap is organized into **tiers** based on priority and dependencies:

- **Tier 0: Design System Foundation** (4-6 days) - Optional: Establish UI patterns before building
- **Tier 1: Core Intelligence** (13-16 weeks) - Build Polly's knowledge system
- **UI Polish Sprint** (1 week) - Update remaining UIs to match design system
- **Tier 2: Packaging & Permissions** (1 week) - Enable macOS integrations
- **Tier 3: Polish & Autonomy Awareness** (2-3 weeks) - Onboarding + data sovereignty
- **Tier 4: Advanced Communication** (2-3 weeks) - Email/calendar intelligence
- **Tier 5: Optional Enhancements** (varies) - Nice-to-have improvements
- **Tier 6: Future** (3-4 weeks) - iOS mobile app

**Total Timeline (All Tiers 0-4):** 19-24 weeks

### TIER 0: Design System Foundation (7 days) - ✅ COMPLETE (Jan 26, 2026)

**Alternative Implementation:** Instead of the planned Shadcn/ui + Tailwind approach documented in `PHASE0.5_UI_DESIGN_SYSTEM.md`, an Obsidian-inspired custom CSS implementation was delivered with enhanced features.

#### Phase 0.5: Obsidian-Inspired UI Redesign (7 days) - ✅ COMPLETE

**Document:** `PHASE0.5_COMPLETE.md`

**See Also:** `PHASE0.5_OBSIDIAN_APPROACH.md` - Architecture decision document

**Status:** ✅ 100% Complete (Jan 26, 2026)

**What Was Built:**

**Day 1: Icon Ribbon + Three-Column Layout** ✅
- Vertical icon ribbon with 12 page buttons (Dashboard, Calendar, Mail, Code, Projects, Knowledge, Notes, Learning, Search, Patterns, Domains, Settings)
- Three-column layout: left sidebar (280px), center content (flex), right sidebar (320px)
- Collapsible sidebars with keyboard shortcuts (Cmd+B, Cmd+/)
- Titlebar controls for sidebar toggling
- Dark Obsidian theme with orange accent (#f0903b)

**Day 2-3: Chat System Migration (Page-Specific Conversations)** ✅
- Database schema enhancement: `page_context` column + index
- Automatic migration system (runs on app start, safe for existing databases)
- Page-specific conversation filtering (12 page contexts)
- Visual page badges with 12 color themes
- Active chat header shows current page context
- Backend receives `page_context` for future RAG filtering

**Day 4-5: Left Sidebar Panels (Context-Specific Content)** ✅
- Dashboard sidebar: Quick links + recent 5 conversations
- Knowledge sidebar: Domain filter + action buttons + quick access tree
- Patterns sidebar: Time range filter + category filter + export button
- Settings sidebar: Navigation tabs
- Event handlers for all sidebar actions

**Day 6: Right Sidebar Polish (Stats & Actions)** ✅
- Dashboard right sidebar: System stats + quick actions
- Knowledge right sidebar: RAG stats (Obsidian: 1,290 chunks, Codebase: 489 chunks)
- Patterns right sidebar: Pattern statistics + type breakdown
- Global stats object (`window.pollyStats`) for single source of truth
- Stat cards with color-coded borders matching page themes

**Day 7: Final Testing & Bug Fixes** ✅
- Fixed null reference errors (added checks for all DOM elements)
- Fixed missing event listener warnings (null checks + informative warnings)
- Fixed connection refused on startup (retry logic: 3 attempts, 3s intervals)
- Fixed stats data format (normalized to `window.pollyStats`)
- Zero JavaScript console errors in production

**Files Modified:**
- `electron-app/src/main/db/schema.sql` - Added `page_context` column + index
- `electron-app/src/main/conversation-manager.js` - Migration system, CRUD methods
- `electron-app/src/renderer/app.js` - ~800 lines added (navigation, sidebars, stats, helpers)
- `electron-app/src/renderer/index.html` - Three-column layout, page filter, chat header
- `electron-app/src/renderer/styles/ribbon.css` - New file, vertical icon ribbon
- `electron-app/src/renderer/styles/three-column.css` - New file, ~150 lines (layout, sidebars, stat cards)
- `electron-app/src/renderer/styles/chat-sidebar.css` - Page badge styles with 12 color themes

**Database Changes:**
```sql
ALTER TABLE conversations ADD COLUMN page_context TEXT DEFAULT NULL;
CREATE INDEX idx_conversations_page_context ON conversations(page_context);
```

**Implementation vs. Original Plan:**

**Original Plan (PHASE0.5_UI_DESIGN_SYSTEM.md):**
- Shadcn/ui + Tailwind CSS setup
- Component library approach
- Design system documentation
- 4-6 days

**What Was Built:**
- Custom Obsidian-inspired CSS (no external UI libraries)
- Three-column layout with icon ribbon
- Page-specific conversation system (bonus feature)
- Context-aware sidebars (bonus feature)
- Real-time stats integration (bonus feature)
- 7 days

**Why Obsidian Approach:**
- ✅ No dependency on external UI libraries
- ✅ Fully custom, matches Obsidian aesthetic exactly
- ✅ More features than originally planned
- ✅ Zero npm package overhead
- ✅ Complete control over styling
- ✅ Production-ready with zero console errors

**Benefits Delivered:**
- Page-specific conversation organization (natural extension of multi-page nav)
- Context-aware sidebars maximize screen utility
- Real-time stats from backend (single source of truth)
- Automatic database migration (safe for existing installations)
- Instant filtering with zero network latency

**Marketing Alignment:**
- Obsidian-inspired aesthetic appeals to knowledge workers
- Professional dark theme with personality (orange accent)
- Familiar navigation patterns reduce learning curve

**Next Steps After Phase 0.5:**
- All future UIs should follow Obsidian-inspired patterns
- Three-column layout established as foundation
- Icon ribbon navigation is the standard
- Stats integration pattern documented for reuse

---

### TIER 1: Core Intelligence (13-16 weeks)

**Goal:** Build Polly's core knowledge organization, intelligence, and development capabilities.

**Why This First:** All these features work in development mode without requiring a signed app bundle. This allows rapid iteration and testing before committing to app signing.

#### Phase 1.5: Domain Configuration System (6 days) - ✅ COMPLETE (Jan 25, 2026)

**Document:** `PHASE1.5_DOMAIN_CONFIGURATION.md`

**See Also:**
- `PHASE1.5_MIGRATION_COMPLETE.md` - Days 1-2 completion report
- `PHASE1.5_QUICK_REFERENCE.md` - Quick reference guide
- `USE_CASE_2_COMPLETE.md` - Day 5 completion report (Pattern-Boosted Detection)
- `PHASE1.5_DAY6_COMPLETE.md` - Day 6 completion report (First-Run Wizard)

**Status: Backend 100% Complete ✅ (UI wizard deferred to Phase 18)**

**✅ Completed (Jan 24-25, 2026):**

**Days 1-2: Foundation (Jan 24)**
- ✅ Domain configuration system (`core/domain_config.py` - 440 lines)
- ✅ Migration from hardcoded domains to `~/.polly/domains.json`
- ✅ Updated `core/domains.py` to load from config with fallback
- ✅ Updated `learners/patterns.py` to use config keywords
- ✅ All 8 end-to-end tests passing
- ✅ 3,405 patterns preserved and working
- ✅ Automatic backups on config changes
- ✅ Validation and normalization
- ✅ Zero breaking changes to production data

**Days 3-4: Settings UI + Backend API (Jan 24-25)**
- ✅ 6 server API endpoints in `interfaces/server.py`:
  - ✅ GET `/polly/domains/config` - List all domains
  - ✅ POST `/polly/domains` - Create domain
  - ✅ PUT `/polly/domains/:id` - Update domain
  - ✅ DELETE `/polly/domains/:id` - Delete domain (safety checks)
  - ✅ POST `/polly/domains/reorder` - Reorder domains
  - ✅ POST `/polly/domains/folder-numbering` - Toggle numbering
- ✅ Comprehensive API tests (8/8 passing)
- ✅ Snake_case Python ↔ camelCase JSON conversion
- ✅ RAG weight auto-normalization
- ✅ Duplicate name/ID validation
- ✅ Settings → Domains tab in UI
- ✅ Folder numbering toggle
- ✅ Domain list with drag-to-reorder
- ✅ Domain editor modal:
  - ✅ Name/description inputs (validated)
  - ✅ Icon picker (16 emoji options)
  - ✅ Color picker (20 color palette)
  - ✅ RAG weight slider with auto-normalize
  - ✅ Keyword tag editor (add/remove chips)
- ✅ Full CRUD operations wired to backend
- ✅ Drag-and-drop reordering
- ✅ Error handling and validation
- ✅ CSS styling (brutalist design matching app)

**Day 5: Pattern-Boosted Domain Detection (Jan 25)**
- ✅ **Use Case 2 Implementation:** Pattern-boosted domain detection
- ✅ Enhanced `core/domains.py` with pattern integration (+150 lines):
  - ✅ `_get_pattern_domain_boosts()` - Domain→Collection pattern boosting
  - ✅ `_get_conceptual_pattern_boosts()` - Query expansion with conceptual patterns
  - ✅ `record_successful_detection()` - Learning loop
  - ✅ `set_pattern_learner()` - Pattern learner attachment
- ✅ Integrated with `core/polly.py` query engine (+8 lines)
- ✅ Test suite: `test_use_case_2.py` (4 comprehensive scenarios)
- ✅ **Test Results:** 146% confidence boost achieved (exceeds 15-25% target)
- ✅ Documentation: `USE_CASE_2_COMPLETE.md`

**Day 6: First-Run Wizard (Jan 25)**
- ✅ **Backend Implementation Complete:**
  - ✅ `is_first_run()` function in `core/domain_config.py`
  - ✅ `create_quick_start_domains()` - 3 basic domains (Work, Personal, Learning)
  - ✅ Template system: `core/domain_templates.py` (~700 lines)
    - ✅ Software Development template (5 domains)
    - ✅ Academic Research template (5 domains)
    - ✅ Creative Work template (5 domains)
    - ✅ Business template (5 domains)
  - ✅ CLI wizard: `setup_wizard.py` (~350 lines)
    - ✅ Interactive mode with menus
    - ✅ Quick setup mode (`--quick`)
    - ✅ Template mode (`--template <id>`)
    - ✅ List templates (`--list-templates`)
    - ✅ Optional folder creation
  - ✅ All components tested and working
- ✅ Documentation: `PHASE1.5_DAY6_COMPLETE.md`

**⏸️ Deferred to Phase 18 (Onboarding):**
- UI wizard (React/Electron graphical wizard)
- AI keyword suggestions based on existing content
- Obsidian vault analysis for domain suggestions
- Dashboard dynamic color rendering

**What It Does:**
- User-definable domains (not hardcoded) ✅
- Full domain management UI (create/edit/delete/reorder) ✅
- Pattern-boosted domain detection (15-25% confidence boost) ✅
- First-run wizard with quick-start and templates ✅
- **Quick Start:** 3 basic domains (Work, Personal, Learning) ✅
- **Template System:** 4 pre-configured templates with 5 domains each ✅
  - Software Development
  - Academic Research
  - Creative Work
  - Business
- CLI setup wizard for domain configuration ✅
- Settings panel for ongoing management ✅

**Storage:** `~/.polly/domains.json` ✅

**Key Features:**
- Domains have: name, description, color, icon, folderPath, ragWeight (0-1), autoTagRules[] ✅
- Folder numbering: `01-Concepts/`, `02-Patterns/` (optional, user-configurable) ✅
- Special folders: `_Drafts/` (review queue), `_Templates/` (note templates) (Phase 16)
- Pattern learning integration: domain detection uses learned patterns for 15-25% boost ✅
- Full UI for domain management with validation ✅
- Drag-to-reorder with visual feedback ✅
- CLI wizard for first-run setup ✅

**Why Essential:** Foundation for all other phases - provides domain system used by Phases 11, 12, 13, 14, 16, 17

**Marketing Alignment:** "Your work doesn't fit in boxes" + "Stop organizing. Start working."

**Migration Notes:**
- Existing Sigils/Signals/Scrolls/Glyphs/Grids preserved exactly
- All colors, icons, keywords migrated from hardcoded structure
- Fallback to hardcoded domains if config deleted
- See `PHASE1.5_MIGRATION_COMPLETE.md` for full details

---

#### Phase 13a: Pattern Learning System - Core Intelligence Layer ✅ COMPLETE

**Document:** `PHASE13A_PATTERN_LEARNING_CORE.md` (~3,200 lines)

**See Also:** `docs/PHASE13_PROGRESS.md` - Progress tracking document

**Status:** ✅ COMPLETE (Jan 25, 2026) - All 16 days implemented and tested

**What It Does:**
- Transforms pattern learning into a **RAG navigation system** for 30-70% faster retrieval
- Learns 3 pattern types focused on efficiency:
  - **Query→Chunk Patterns:** Learn which documents answer queries well → boost them immediately (30-50% speedup)
  - **Domain→Collection Priorities:** Learn which sources are relevant per domain → skip irrelevant collections (20-40% speedup)
  - **Conceptual Patterns (Refined):** Learn concept connections for query expansion with strict quality filters (10-20% better relevance)
- Uses spaCy for accurate concept extraction (500+ technical terms, 700+ stopwords)
- Pattern quality controls: automatic pruning, decay, usefulness tracking (permanently enabled)
- RAG timing metrics and pattern usefulness scores (for measurement & validation)
- **9 Ancillary Use Cases** (fully specified for implementation in respective phases):
  1. Proactive Context Loading (Phase 20): Pre-warm cache before queries
  2. Domain Auto-Detection Enhancement (Phase 1.5): ⭐ CRITICAL - boost detection confidence 15-25%
  3. Autonomous Workflow Learning (Phase 3): Remember project-specific build processes
  4. Multi-Model Router Optimization (Phase 11): Route based on learned success patterns
  5. Session Context Persistence (Phase 20): Resume conversations with relevant context
  6. Smart Notification Filtering (Phase 6): Surface only topics user cares about
  7. Intelligent Command Suggestions (Phase 10): Suggest commands based on patterns
  8. Knowledge Gap Detection (Phase 18): Identify poorly-answered topics
  9. Concept-Based Obsidian Linking (Phase 12): Suggest note links from patterns

**Implementation Complete:**
- ✅ Days 1-2: Pattern Storage v2.0
- ✅ Days 3-4: spaCy Concept Extraction
- ✅ Days 5-8: Query→Chunk Pattern Learning (30-50% RAG speedup)
- ✅ Days 9-11: Domain→Collection Priorities (20-40% RAG speedup, integrated)
- ✅ Days 12-13: Conceptual Pattern Refinement (10-20% better relevance)
- ✅ Days 14-15: Pattern Quality Controls (automatic pruning, decay)
- ✅ Day 16: Pattern Enhancement APIs (6 query methods, 4 public APIs)

**Files Modified:**
- `learners/patterns.py` - +1,168 lines (now ~2,380 lines total)
- `core/rag.py` - +60 lines (collection filtering integration)
- `core/polly.py` - +180 lines (query expansion, pattern recording)

**Tests:** 41 test suites, 100% passing ✅

**Storage:** `~/.polly/patterns.json` (200-400 high-quality patterns, auto-pruned, version 2.0)

**Why Essential:** As knowledge base scales (4K → 40K+ docs), RAG becomes slower. Patterns provide efficient lookup paths to the right documents without searching everything. System learns what works and gets faster over time - "knowledge that compounds."

**Marketing Alignment:** Embodies "Knowledge that compounds, not dependency that scales" - system remembers, learns, improves permanently

**Next Steps:** Implement ancillary use cases during their natural phases (e.g., Use Case 2 in Phase 1.5 Day 5)

---

#### Phase 13b: Pattern Learning UI & Testing (7 days)

**Document:** `PHASE13B_PATTERN_LEARNING_UI.md` (~960 lines)

**Prerequisites:** Phase 13a must be complete

**What It Does:**
- Learning frequency controls (5+ messages, domain-only, 3-day re-learning delay)
- Batch learning mode (manual trigger)
- Pattern visualization UI (browser with search/filter/sort)
- RAG efficiency metrics dashboard (real-time speedup estimates)
- Pattern management interface (delete, export, clear with backup)
- Comprehensive testing suite (RAG speed benchmarks, pattern quality verification)

**Why Essential:** Provides visibility, control, and validation of pattern learning system

---

#### Phase 21: Knowledge Base Deduplication (2-3 days)

**Document:** `PHASE21_KNOWLEDGE_DEDUPLICATION.md`

**What It Does:**
- Semantic similarity detection before note creation (70%+ threshold)
- "Similar notes found" warning UI with snippets and similarity scores
- Three action options:
  - **Append to Selected Note:** Add content to existing note with separator
  - **Create with Links:** Auto-generate wikilinks to related notes
  - **Create New Note Anyway:** Bypass warning and create
- User-configurable similarity threshold (50-95%)
- Performance: <500ms duplicate check
- Graceful fallback when RAG unavailable

**Storage:** Configuration in `~/.polly/config.yaml`

**Why Essential:** Prevents knowledge fragmentation, encourages note consolidation, reduces duplicate content over time

**Why Early in Tier 1:** Low complexity, high value, prevents problems before knowledge base grows large

**Marketing Alignment:** "Stop organizing. Start working." - Polly keeps your knowledge base clean automatically

---

#### Phase 14: Mental Models System (5 days) - ✅ COMPLETE

**Document:** `PHASE14_MENTAL_MODELS.md`  
**Implementation Plan:** `PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md`  
**User Guide:** `MENTAL_MODELS_USER_GUIDE.md`

**Status:** ✅ Implementation Complete (January 29, 2026)  
**Actual Effort:** 5 days  
**Test Results:** 48/51 tests passing (94% pass rate)

**Completed Features:**
- ✅ **Three-Tier Activation System:**
  - Domain-level: Content-based (sigils, signals, scrolls, glyphs, grids)
  - Page-level: Context-based (learning, code, mail, calendar, etc.)
  - Persona-level: Mode-based (architect/plan, teacher/socratic, etc.)
- ✅ **Unified PIL Compression:**
  - Polly Internal Language achieving 2.3x compression ratio
  - Extends existing conversation compressor
  - Symbol system (>, ↻, →, ⇄, ?, !)
- ✅ **12 Default Models:**
  - Tier 1: Core Philosophy (Infinite Games, Instruments Over Tracks, Constraint as Meaning)
  - Tier 2: Learning & Thinking (Freire, Reverse Engineering, Socratic Method)
  - Tier 3: Systems & Technical (Systems Thinking, First Principles, Design Thinking)
  - Tier 4: Communication (Inbox Zero, Async-First, Time Blocking) - **FUTURE-PROOF for Phase 20**
- ✅ **Template System:** 5 starter templates for easy custom model creation
- ✅ **Per-Conversation Override:** Context menu for manual model selection with localStorage persistence
- ✅ **Settings UI:** Full CRUD operations, color-coded tags, animated toggles
- ✅ **REST API:** 7 endpoints for programmatic access
- ✅ **Future-Proof Design:** Works with Pages/Personas not yet built (Phase 20, 22)

**Storage:** `~/.polly/mental_models.yaml`

**Code Metrics:**
- Backend: ~1,700 lines (core + API + tests)
- Frontend: ~1,500 lines (HTML + CSS + JS)
- Total: ~3,200 lines
- API Endpoints: 7 new REST endpoints
- Test Coverage: 48/51 passing (94%)

**Implementation Summary:**
- Day 1-2: Core system + PIL compression + REST API + Integration (✅)
- Day 3: Settings UI with CRUD operations (✅)
- Day 4: Per-conversation override + visual indicators (✅)
- Day 5: Integration testing + documentation (✅)

**Impact:** Foundation for Phase 22 (Teaching Mode), supports Phase 20 (Mail/Calendar) mental models before those features exist, aligns with core project philosophy

---

#### Phase 22: Teaching Mode (2-3 days)

**Document:** `PHASE22_TEACHING_MODE.md`

**Prerequisites:** Phase 14 (Mental Models) must be complete

**What It Does:**
- Specialized "Teaching Mode" mental model with Socratic pedagogy
- Mode switcher UI (toggle in conversation header)
- Progressive difficulty adjustment based on user responses
- Checks understanding before proceeding (asks user to explain concepts back)
- References prior knowledge from conversation history
- Learning path tracking:
  - Records topics learned with mastery levels (1-5)
  - Spaced repetition review suggestions
  - Learning statistics dashboard
- Automatic structured learning note creation:
  - Key concepts and principles
  - Understanding and insights
  - Related topics to explore next
  - Practice exercises
- Mode persists per conversation

**Storage:** 
- `~/.polly/learning.json` - Learning topics and progress
- Learning notes in Obsidian vault with #learning tag

**Why After Phase 14:** Built on mental models system, uses mental model injection for Socratic instructions

**Why Early in Tier 1:** Low complexity (extends existing system), high user value, differentiates Polly from "quick answer" AIs

**Marketing Alignment:** "Polly teaches you as you teach Polly" - Learning as dialogue, not transmission

---

#### Phase 12a: Knowledge Graph - Basic (5-7 days)

**Document:** `PHASE12_KNOWLEDGE_GRAPH.md`

**What It Does:**
- Interactive Cytoscape.js visualization
- 5 node types: notes, code files, concepts, conversations, repos
- 4 edge types: links, imports, similarity, relationships
- Domain-based filtering
- Click to zoom, hover info
- Force-directed layout

**Data Scale:** 100-500 nodes initially (scales to thousands)

**Why Split:** Build basic graph first, enhance after Phase 16 adds native notes

---

#### Phase 11: Multi-Model Intelligent Routing (5 weeks)

**Document:** `PHASE11_MULTI_MODEL_ENHANCED_V2.md` (NEW - supersedes original)

**Related Documents:**
- `PHASE11_PROVIDER_SPECIFICATIONS.md` - Detailed API specs for 8 providers
- `PHASE11_GROK_SAFETY.md` - Grok safety filter specification (MANDATORY)
- `PHASE11_SECRETS_MANAGEMENT.md` - Cross-platform encrypted API key storage
- `PHASE11_AGENT_PERSONAS.md` - Agent persona framework (Architect Plan/Build modes)
- `PHASE11_COMPRESSION_SYSTEM.md` - Conversation compression for extended context

**What It Does:**
- **8 Cloud AI Providers:** Anthropic (Claude), OpenAI (GPT), GitHub Copilot, OpenRouter, Google AI (Gemini), Mistral AI, Grok (xAI), Perplexity
- **Three-Tier Routing:** Fast (Haiku, GPT-3.5), Balanced (Sonnet 4, GPT-4), Thorough (Opus 4, GPT-4o)
- **Grok Safety Filters:** Mandatory content filtering for conspiracy theories, extremist content, misinformation
- **Cross-Platform Secrets:** Encrypted API key storage using native keychains (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- **Agent Personas:** Architect persona with Plan/Build modes for structured task execution
- **Budget Management:** Daily/monthly token limits, cost tracking, provider fallback chains
- **Conversation Compression:** 50-100x token reduction for extended context retention

**Sub-Phases:**

**Phase 11a: Core Routing + Primary Providers (2 weeks)**
- Multi-provider infrastructure
- Anthropic, OpenAI, GitHub Copilot integration
- Three-tier confidence routing
- Budget tracking and limits
- Settings UI for provider management

**Phase 11b: Extended Providers + Safety (2 weeks)**
- OpenRouter, Google AI, Mistral AI, Perplexity integration
- Grok integration with mandatory safety filters
- Provider fallback chains
- User consent flow for Grok
- Safety dashboard and monitoring

**Phase 11c: Orchestration + Compression (1 week)**
- Cost optimization system
- Basic conversation compression (50x ratio)
- Architect persona with Plan/Build modes
- Full integration testing
- Documentation and examples

**Timeline:** 5 weeks total
**Next Phase:** Phase 16c (AI Note Creation)

---

#### Phase 16: Native Notes Frontend (1 day) - ✅ COMPLETE (Jan 26, 2026)

**Document:** `PHASE16_COMPLETE.md`

**See Also:** `PHASE16_NATIVE_NOTES.md` (original plan)

**Status:** ✅ 100% Complete (Jan 26, 2026)

**Implementation Approach:**

Instead of the original 3-phase plan (Phase 16a/b/c spanning 3.5-4.5 weeks), we took a pragmatic approach: build a functional notes interface that works seamlessly with existing Obsidian vaults.

**What Was Built:**

1. **Beautiful Notes Browser** ✅
   - File tree with hierarchical folder structure
   - Sort modes: By Folder, Name (A-Z/Z-A), Recently Modified, Recently Created
   - 86 notes indexed across 9 folders
   - Left sidebar with file tree, right sidebar with backlinks/tags

2. **Markdown Editor with Dual Modes** ✅
   - View mode: Beautiful rendered markdown (using marked.js)
   - Edit mode: Raw markdown in textarea
   - Click anywhere to edit, click away to save
   - Wiki-links rendered as clickable links

3. **Wiki-Link System** ✅
   - Click wiki-links to navigate between notes
   - Broken links show creation modal with pre-filled name
   - Backlinks panel shows incoming references
   - Supports: `[[Note]]`, `[[Note|Display]]`, `[[Note#Heading]]`, `![[Embed]]`

4. **Auto-Save Functionality** ✅
   - 2-second debounced auto-save while typing
   - Immediate save on blur (clicking away from editor)
   - Visual status indicator: ● Unsaved → ⏳ Saving... → ✓ Saved
   - Error handling with ✗ Error state

5. **Quick Switcher (Cmd+O)** ✅
   - Keyboard-driven fuzzy search modal
   - Searches title, name, domain, aliases
   - Multi-token support ("sig prac" matches "Sigils Practice")
   - Arrow keys to navigate, Enter to open, Esc to close
   - Returns top 50 results with smart scoring

6. **Note/Folder Creation** ✅
   - Single "+" button in sidebar with dropdown menu
   - New Note: Modal with name, folder selection, optional content
   - New Folder: Modal with name input, sanitizes to folder format
   - Both auto-refresh file tree after creation

7. **Drag-and-Drop Organization** ✅
   - Drag notes between folders visually
   - Visual feedback: opacity changes, cursor changes, folder highlighting
   - Toast notifications during move
   - Automatic file tree refresh after move
   - Prevents dropping on same folder

8. **Editable Titles** ✅
   - **In note header:** Click title or edit icon to enter edit mode
   - **In file tree:** Double-click note name to edit inline
   - Enter to save, Escape to cancel, blur to save
   - Renames file and updates frontmatter title

9. **Automatic Wiki-Link Updates** ✅
   - When renaming a note, ALL wiki-link references across entire vault are automatically updated
   - Handles all formats: `[[old]]` → `[[new]]`, `[[old|text]]` → `[[new|text]]`, `[[old#Section]]` → `[[new#Section]]`
   - Preserves display text and headings
   - Shows reference count in success toast: "Renamed to 'New-Name' (updated 3 references)"
   - Rebuilds backlinks index after completion

**Files Modified:**

**Backend:**
- `interfaces/server.py` (Lines 1451-2024) - 8 new endpoints:
  - `GET /polly/notes/source` - Get notes source (Obsidian/native)
  - `GET /polly/notes/index` - List all notes with metadata
  - `POST /polly/notes/index/build` - Rebuild notes index
  - `GET /polly/notes/folders` - List all folders
  - `POST /polly/notes/create` - Create new note
  - `POST /polly/notes/create-folder` - Create new folder
  - `PUT /polly/notes/update` - Update note content
  - `POST /polly/notes/move` - Move note between folders
  - `POST /polly/notes/rename` - Rename note + update all wiki-links
- `core/backlinks.py` - Enhanced wiki-link parsing

**Frontend:**
- `electron-app/src/renderer/index.html` - Notes view structure + 3 modals
- `electron-app/src/renderer/notes-manager.js` - 1,800+ lines, complete implementation
- `electron-app/src/renderer/app.js` - Sidebar "+" button and dropdown
- `electron-app/src/renderer/styles/notes.css` - 663 lines of styling
- `electron-app/src/renderer/styles/main.css` - Quick switcher styles

**Why This Approach:**

✅ **Pragmatic:** Works with existing Obsidian vaults  
✅ **Fast:** 1 day vs 3.5-4.5 weeks planned  
✅ **Feature-Rich:** All core features plus unique enhancements  
✅ **Production-Ready:** Fully tested, polished UX  
✅ **Unique Features:** Automatic wiki-link updates (Obsidian doesn't have this!)

**Performance:**
- 86 notes indexed in ~40ms
- 99 wiki-links tracked
- Sub-100ms for most operations
- Real-time UI updates

**Testing:** All features manually tested and verified working

**Benefits Delivered:**
- Seamless notes management within Polly
- No context switching to external apps
- Foundation for Phase 11 (Draft Notes), Phase 12 (Knowledge Graph), Phase 17 (Code Workspace)
- Beautiful dark theme matching Polly's Obsidian-inspired design

**What's Next:**
- Phase 11 can now save draft notes directly to vault
- Phase 16c will add AI-powered note creation with templates
- Phase 12 can link graph nodes to notes
- Phase 17 can create code notes from workspace

---

#### Phase 16c: Scribe Persona + Skill System (3-4 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Complete architecture, ~35,000 words)

**Prerequisites:** Phase 16 (Native Notes Frontend) ✅

**Status:** 📋 PLANNING COMPLETE (Jan 30, 2026) ← NEXT TO IMPLEMENT

**What It Does:**
- **Scribe Persona:** Transform conversations into structured notes with 4 modes (Capture/Organize/Enrich/Edit)
- **Skill System:** On-demand knowledge packages (templates, rules, guides) for personas
- **Lazy-Loading PersonaManager:** Load only metadata at startup, full prompts on-demand
- **Question/Answer Flow:** Radio button questions (OpenCode style) with "Type your own" option
- **Auto [[wiki-links]]:** Automatic linking to existing notes during Enrich mode
- **Note Preview Modal:** Edit/Preview/Raw tabs before saving
- **Chat UI Redesign:** Consolidated model dropdown + persona dropdown + orchestrator toggle
- **Foundation for 6-Persona System:** Establishes architecture for all future personas

**Week Breakdown:**

**Week 1: Foundation (5 days)**
- Day 1-3: Refactor PersonaManager for lazy-loading (metadata vs full prompts)
- Day 4-5: Implement SkillManager (discovery, loading, caching)

**Week 2: Scribe Persona (5 days)**
- Day 6-7: Create Scribe YAML definition + write 3 skills:
  - `template-guide` - All available note templates
  - `wiki-linking` - Auto-linking rules (threshold 0.85+)
  - `domain-structure` - Vault organization
- Day 8-10: Implement Scribe persona (4 modes: Capture/Organize/Enrich/Edit)

**Week 3: Frontend (5 days)**
- Day 11-13: Chat UI redesign
  - Consolidated model dropdown (remove separate provider/model selects)
  - Persona dropdown with mode selector
  - Orchestrator mode toggle (OFF by default)
- Day 14-15: Question form + preview modal components
  - Radio button questions with "Type your own" option
  - Preview modal with Edit/Preview/Raw tabs

**Week 4: Integration & Testing (3 days)**
- Day 16: Template system + auto-linking algorithm
- Day 17: Integration testing (all 4 modes)
- Day 18: End-to-end testing + documentation

**Configuration:**
```yaml
personas:
  orchestrator_mode: false  # Toggle for automatic collaboration
  default_persona: librarian
  scribe:
    enabled: true
    auto_link_threshold: 0.85
    question_style: radio_buttons

skills:
  directory: ~/.polly/skills/
  auto_load: false  # Lazy-load on demand
```

**User Experience:**
1. User: "Save this conversation as a note"
2. Scribe (Capture mode): Analyzes conversation, extracts concepts
3. Scribe (Organize mode): Presents radio button questions:
   - "What type of note?" (Meeting / Concept / How-To / Research / Type your own)
   - "Which domain?" (Signals / Scrolls / Glyphs / Type your own)
4. User answers questions
5. Scribe (Enrich mode): Generates markdown with auto [[wiki-links]]
6. Preview modal appears (Edit/Preview/Raw tabs)
7. User saves to vault with smart folder suggestion

**Architecture Details:**

**PersonaManager (Lazy-Loading):**
```python
# Startup: Load only metadata
personas = [
  {"slug": "librarian", "name": "Librarian", "modes": ["search", "catalog", "connect", "curate"]},
  {"slug": "scribe", "name": "Scribe", "modes": ["capture", "organize", "enrich", "edit"]},
  # ... (4 more personas)
]

# On activation: Load full prompt
def activate_persona(slug, mode):
    prompt_path = f"core/personas/definitions/{slug}.yaml"
    load_full_prompt(prompt_path, mode)
```

**Skill System:**
```yaml
# ~/.polly/skills/wiki-linking/SKILL.md
---
name: wiki-linking
category: note-taking
personas: [scribe, librarian]
version: 1.0
---

# Wiki-Linking Rules

## When to Create Links
- Semantic similarity >= 0.85 with existing notes
- Concept appears in at least 2 contexts
- Not already linked in this note

## Link Formats
- `[[Note Name]]` - Standard link
- `[[Note Name|Display]]` - Custom display text
- `[[Note#Heading]]` - Link to section
```

**Files to Create:**
- `core/personas/manager.py` (refactored for lazy-loading)
- `core/personas/definitions/scribe.yaml` (Scribe persona definition)
- `core/personas/implementations/scribe.py` (Scribe Python implementation)
- `core/personas/orchestrator.py` (OrchestratorManager for collaboration)
- `core/skills/base.py` (Skill and SkillMetadata classes)
- `core/skills/manager.py` (SkillManager for lazy-loading)
- `vault/.polly/skills/template-guide/SKILL.md`
- `vault/.polly/skills/wiki-linking/SKILL.md`
- `vault/.polly/skills/domain-structure/SKILL.md`
- `electron-app/src/renderer/components/question-form.js`
- `electron-app/src/renderer/components/preview-modal.js`
- `electron-app/src/renderer/styles/persona-ui.css`

**Files to Modify:**
- `core/personas/base.py` (add skill integration)
- `interfaces/server.py` (already has 6 persona endpoints from Phase 11c)
- `electron-app/src/renderer/app.js` (Chat UI updates)
- `electron-app/src/renderer/index.html` (UI structure)
- `electron-app/src/renderer/styles/chat-sidebar.css` (UI styling)

**Success Criteria:**
- ✅ User can save conversation as note
- ✅ Questions presented as radio buttons with "Type your own"
- ✅ Generated note has auto [[wiki-links]] (threshold 0.85+)
- ✅ Preview modal works perfectly (Edit/Preview/Raw)
- ✅ Note saves to correct folder
- ✅ Chat UI is cleaner (consolidated dropdowns)
- ✅ Orchestrator mode toggle functional (OFF by default)
- ✅ PersonaManager loads metadata only at startup
- ✅ Skills load on-demand when persona needs them

**Timeline:** 3-4 weeks
**Next Phase:** Phase 16d (Notes System Polish) OR Phase 17 (Librarian Persona)

---

#### Phase 16d: Notes System Polish & Enhancement (ON HOLD)

**Document:** `NOTES_SYSTEM_TODO.md`

**Prerequisites:** Phase 16c (Scribe Persona + Skill System) ✅

**Status:** ⏸️ ON HOLD - Base functionality complete, polish deferred

**What's Working Now:**
- ✅ Native KB in `~/.polly/notes/`
- ✅ Obsidian migration UI working
- ✅ Real-time file watcher auto-indexing (create/modify/delete)
- ✅ Scribe persona creating notes in native KB
- ✅ Notes Browser showing all notes
- ✅ 110 notes indexed, 899 RAG chunks from 44 files

**What Needs Polish (See `NOTES_SYSTEM_TODO.md` for full details):**

**High Priority (8-12 hours):**
1. Complete RAG indexing for all notes (currently 44/110 files)
2. Reduce debug logging verbosity (conditional based on env var)
3. File watcher status in UI (green/yellow/red dot with sync time)
4. Migration progress feedback (detailed status messages)

**Medium Priority (20-30 hours):**
5. Migration pre-flight check (preview before migrating)
6. Note template system (user-customizable templates per domain)
7. Backlinks and graph view (visualize connections)
8. Tag browser (browse by tag, tag cloud)
9. Note history/versioning (last 10 versions with diff view)
10. Full-text search UI (hybrid BM25 + semantic with filters)

**Low Priority / Nice-to-Have (30+ hours):**
11. Daily note feature
12. Note statistics dashboard
13. Export notes (PDF, HTML, Markdown archive)
14. Smart note suggestions (related notes, tags, avoid duplicates)
15. Collaboration features (sharing, comments)
16. Mobile app sync

**Technical Debt (15-20 hours):**
17. Unit tests for file watcher
18. Integration tests for migration
19. Performance optimization for 1000+ notes
20. Error recovery (auto-restart, retry, checkpoints)

**Documentation (6-8 hours):**
21. User guide (getting started, migration, best practices)
22. API documentation

**Known Issues to Fix:**
- BM25 index error with <5 notes
- File watcher on network drives
- Special characters in filenames
- Obsidian auto-connect on settings page load

**Why On Hold:**
- Base functionality is solid and production-ready
- Other features (personas, graph, etc.) take priority
- Can be tackled incrementally as user feedback comes in

**Quick Wins (< 2 hours each):**
- Add "Re-index All Notes" button
- Reduce debug logging verbosity
- Fix BM25 error with small datasets
- Add daily note creation shortcut
- Show note count in Notes Browser header
- Add "Last modified" sort option
- Add keyboard shortcut for new note (Cmd+N)

**Timeline:** TBD (when ready to resume)
**Next Phase:** Phase 17 (Librarian Persona)

---

#### Phase 17: Librarian Persona (2-3 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Librarian Persona)

**Prerequisites:** Phase 16c (Scribe Persona + Skill System) ✅

**What It Does:**
- **Librarian Persona:** DEFAULT persona for knowledge organization & search with 4 modes (Search/Catalog/Connect/Curate)
- **Router Capabilities:** Acts as intelligent router to other personas based on query intent
- **eBook Management:** Index, catalog, and export eBooks to Supernote
- **Advanced Search UI:** Filter by domain, time range, tags, similarity threshold
- **Metadata Editor:** Bulk tag assignment, classification, folder organization

**Week Breakdown:**

**Week 1: Core Modes (5 days)**
- Day 1-3: Search & Catalog modes implementation
  - Enhanced RAG search with domain filtering
  - Tag assignment and classification UI
  - Folder suggestion system
- Day 4-5: Connect mode implementation
  - Link discovery algorithm
  - Concept mapping visualization
  - Backlink analysis enhancement

**Week 2: Curate Mode & Skills (5 days)**
- Day 6-8: Curate mode (eBook focus)
  - eBook indexing (EPUB, PDF, MOBI)
  - Metadata extraction and cataloging
  - Supernote export integration
- Day 9-10: Write 4 Librarian skills:
  - `classification-rules` - Tagging and categorization
  - `ebook-formats` - Supported formats and metadata
  - `search-operators` - Advanced RAG syntax
  - `domain-mapping` - Vault structure guide

**Week 3: Router & Polish (5 days)**
- Day 11-13: Intent-based routing
  - Query analysis for persona suggestions
  - "Try Scribe" / "Ask Professor" suggestions
  - Orchestrator integration (when toggle ON)
- Day 14-15: UI polish, testing, documentation

**Success Criteria:**
- ✅ Librarian is default persona on app start
- ✅ Search mode filters by domain, tags, date
- ✅ Catalog mode can bulk assign tags
- ✅ Connect mode suggests [[wiki-links]]
- ✅ Curate mode indexes eBooks correctly
- ✅ Router suggests appropriate personas
- ✅ 4 Librarian skills loaded on-demand

**Timeline:** 2-3 weeks
**Next Phase:** Phase 18 (Programmer Persona)

---

#### Phase 18: Programmer Persona (2-3 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Programmer Persona)

**Prerequisites:** Phase 17 (Librarian Persona) ✅

**What It Does:**
- **Programmer Persona:** Code writing & debugging with 4 modes (Code/Debug/Refactor/Explain)
- **Code-Aware Context:** Loads relevant codebase chunks from GitHub RAG
- **Test Generation:** Auto-generate test cases from code
- **Inline Explanations:** Comment generation for complex code

**Week Breakdown:**

**Week 1: Core Modes (5 days)**
- Day 1-3: Code & Debug modes
  - Code generation with template support
  - Error analysis and debugging suggestions
  - Test case generation
- Day 4-5: Refactor mode
  - Code analysis and optimization
  - Pattern detection from Phase 13a
  - Refactoring suggestions

**Week 2: Explain Mode & Skills (5 days)**
- Day 6-8: Explain mode
  - Code-to-documentation generation
  - Inline comment insertion
  - README generation
- Day 9-10: Write 3 Programmer skills:
  - `coding-standards` - Project style conventions
  - `testing-patterns` - Test structure best practices
  - `debugging-workflow` - Systematic debugging approach

**Week 3: Integration & Testing (5 days)**
- Day 11-13: Collaboration with Architect
  - Request design before major features
  - Design approval workflow
- Day 14-15: Full testing, documentation

**Success Criteria:**
- ✅ Programmer generates code correctly
- ✅ Debug mode analyzes errors effectively
- ✅ Refactor mode uses learned patterns
- ✅ Explain mode generates clear docs
- ✅ Collaborates with Architect when appropriate
- ✅ 3 Programmer skills loaded on-demand

**Timeline:** 2-3 weeks
**Next Phase:** Phase 19 (Architect Persona Refactor)

---

#### Phase 19: Architect Persona Refactor (2 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Architect Persona)

**Prerequisites:** Phase 18 (Programmer Persona) ✅

**What It Does:**
- **Refactor Existing Architect:** Remove code generation, focus on planning/design
- **3 Refined Modes:** Analyze/Design/Review (removed Build mode → moved to Programmer)
- **Design Document Generation:** Create markdown architecture docs (NOT code)
- **Diagram Support:** Text-based diagrams (component specs, data flow)
- **Risk Analysis:** Identify design risks and constraints

**Week Breakdown:**

**Week 1: Mode Refactoring (5 days)**
- Day 1-2: Remove Build mode, refactor to planning-only
- Day 3-5: Enhance Analyze/Design/Review modes
  - Requirements gathering and analysis
  - Architecture document generation
  - Design review and critique

**Week 2: Skills & Collaboration (5 days)**
- Day 6-8: Write 3 Architect skills:
  - `design-patterns` - Common architectural patterns
  - `system-constraints` - Performance/scalability considerations
  - `review-checklist` - Design review criteria
- Day 9-10: Collaboration integration
  - Architect → Programmer handoff workflow
  - Design approval process

**Success Criteria:**
- ✅ Architect no longer generates code
- ✅ Analyze mode gathers requirements
- ✅ Design mode creates markdown docs
- ✅ Review mode provides feedback
- ✅ Seamless handoff to Programmer
- ✅ 3 Architect skills loaded on-demand

**Timeline:** 2 weeks
**Next Phase:** Phase 20 (Professor Persona)

---

#### Phase 20: Professor Persona (2-3 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Professor Persona)

**Prerequisites:** Phase 19 (Architect Persona Refactor) ✅

**What It Does:**
- **Professor Persona:** Teaching & learning with 4 modes (Explain/Socratic/Curriculum/Quiz)
- **Pedagogy Integration:** Uses Mental Models (Phase 14) for teaching approaches
- **Learning Path Creation:** Structured sequences with prerequisites
- **Understanding Assessment:** Test comprehension before proceeding
- **Learning Note Generation:** Auto-save learning sessions to vault

**Week Breakdown:**

**Week 1: Core Modes (5 days)**
- Day 1-3: Explain & Socratic modes
  - Clear explanations with examples
  - Socratic dialogue system (questions → insights)
  - Analogy generation
- Day 4-5: Curriculum mode
  - Learning path creation
  - Prerequisite mapping
  - Content sequencing

**Week 2: Quiz Mode & Skills (5 days)**
- Day 6-8: Quiz mode
  - Question generation from content
  - Answer evaluation and feedback
  - Difficulty adjustment
- Day 9-10: Write 4 Professor skills:
  - `pedagogical-methods` - Teaching approaches (Socratic, Freire, explain-by-example)
  - `learning-paths` - How to structure sequences
  - `assessment-types` - Quiz/assessment formats
  - `concept-prerequisites` - Dependency mapping

**Week 3: Integration & Testing (5 days)**
- Day 11-13: Collaboration & note generation
  - Uses Librarian to find learning materials
  - Uses Scribe to save learning notes
  - Learning progress tracking
- Day 14-15: Full testing, documentation

**Success Criteria:**
- ✅ Explain mode generates clear explanations
- ✅ Socratic mode asks guiding questions
- ✅ Curriculum mode creates learning paths
- ✅ Quiz mode tests understanding
- ✅ Learning notes saved automatically
- ✅ 4 Professor skills loaded on-demand

**Timeline:** 2-3 weeks
**Next Phase:** Phase 21-Orchestrator (Orchestrator Mode Toggle)

---

#### Phase 21-Orchestrator: Orchestrator Mode Toggle (1 week)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Orchestrator Mode Toggle)

**Prerequisites:** All 5 personas complete (Phases 16c, 17, 18, 19, 20) ✅

**What It Does:**
- **Orchestrator Mode:** User-controlled toggle for automatic persona collaboration
- **Manual Mode (Default):** User explicitly switches personas
- **Orchestrator Mode (Toggle ON):** Personas collaborate automatically (transparent to user)
- **Safety Rules:** Max 3 collaborative switches per query, prevent infinite loops
- **Collaboration Logging:** Track all collaborations for transparency
- **Settings UI:** Toggle with clear explanation and examples

**Week Breakdown:**

**Day 1-2: Core System**
- OrchestratorManager implementation
- Collaboration request protocol
- Context passing between personas
- Maximum depth enforcement (3 switches)

**Day 3-4: UI & Visualization**
- Settings toggle with description
- Chat collaboration indicators ("🔀 Collaborating with...")
- Collaboration history view
- Logging and transparency

**Day 5: Testing & Polish**
- Test all persona collaborations
- Edge cases (loops, failures)
- Documentation and examples

**Success Criteria:**
- ✅ Toggle OFF = manual mode (default)
- ✅ Toggle ON = automatic collaboration
- ✅ User sees all collaborations in chat
- ✅ Max 3 switches enforced
- ✅ No infinite loops possible
- ✅ Collaboration history viewable

**Timeline:** 1 week
**Next Phase:** Phase 22-Secretary (Secretary Persona)

---

#### Phase 22-Secretary: Secretary Persona (2 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Secretary Persona)

**Prerequisites:** Phase 21-Orchestrator (Orchestrator Mode) ✅

**What It Does:**
- **Secretary Persona:** Scheduling, communication, task management with 4 modes (Schedule/Compose/Triage/Remind)
- **Calendar Integration:** EventKit for calendar access (requires Phase 9 permissions)
- **Email Intelligence:** Draft emails with tone matching
- **Task Prioritization:** Eisenhower matrix, urgency detection
- **Reminder System:** Smart follow-ups and notifications

**Week Breakdown:**

**Week 1: Core Modes (5 days)**
- Day 1-3: Schedule & Compose modes
  - Calendar operations (read/create/update events)
  - Time blocking suggestions
  - Email drafting with templates
- Day 4-5: Triage mode
  - Task prioritization algorithm
  - Urgency detection
  - Priority framework (Eisenhower)

**Week 2: Remind Mode & Skills (5 days)**
- Day 6-7: Remind mode
  - Reminder creation
  - Follow-up tracking
  - Notification scheduling
- Day 8-10: Write 3 Secretary skills + testing:
  - `calendar-templates` - Common meeting types
  - `email-templates` - Professional email formats
  - `priority-framework` - Task prioritization rules

**Success Criteria:**
- ✅ Schedule mode manages calendar
- ✅ Compose mode drafts emails
- ✅ Triage mode prioritizes tasks
- ✅ Remind mode creates reminders
- ✅ Collaborates with Librarian/Scribe
- ✅ 3 Secretary skills loaded on-demand

**Timeline:** 2 weeks
**Next Phase:** Phase 23+ (User Extensibility)

---

#### Phase 23+: User Extensibility (4-6 weeks)

**Document:** `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (Section: Future - User Extensibility)

**Prerequisites:** All 6 core personas complete (Phases 16c-22) ✅

**What It Does:**
- **User-Defined Personas:** YAML-based persona creation (KILO-inspired)
- **Custom Skills:** Users can write skill files
- **Persona Marketplace:** Community sharing platform
- **Persona Editor UI:** Graphical editor for personas
- **Skill Editor UI:** Graphical editor for skills
- **Import/Export:** Share personas via files

**Week Breakdown:**

**Week 1-2: YAML Persona System (10 days)**
- Day 1-5: YAML persona definition format
  - Name, description, modes specification
  - Prompt template system
  - Skill requirements
- Day 6-10: Persona loader and validator
  - Load user personas from `~/.polly/personas/`
  - Validation and error handling
  - Merge with core personas

**Week 3-4: Editors & Marketplace (10 days)**
- Day 11-15: Persona Editor UI
  - Graphical persona creation
  - Mode configuration
  - Prompt editing
- Day 16-20: Skill Editor UI + Marketplace
  - Skill file creation
  - Import/export functionality
  - Community marketplace (Phase 2)

**Success Criteria:**
- ✅ Users can create personas via YAML
- ✅ Custom personas load correctly
- ✅ Persona editor functional
- ✅ Skill editor functional
- ✅ Import/export working

**Timeline:** 4-6 weeks
**Next Phase:** Persona Marketplace (Community Platform)

---

#### Phase 12b: Knowledge Graph - Reasoning Transparency (1-2 weeks)

**Document:** `PHASE12_KNOWLEDGE_GRAPH.md` (continued)

**What It Adds:**
- **Edge Confidence Scores:** Every connection has 0.0-1.0 confidence score
- **Multi-Factor Analysis:**
  - Semantic similarity (0-1)
  - Keyword overlap (0-1)
  - Temporal proximity (0-1)
  - User behavior (clicks, navigation) (0-1)
  - Weighted composite score
- **"Why this connection?" Modal:**
  - Shows all 4 factors with individual scores
  - Explains why Polly thinks nodes are related
  - Source evidence (text snippets, timestamps)
  - User can adjust factor weights
- **"Explore from here" Mode:**
  - Click node → show connections sorted by confidence
  - Filter by minimum confidence threshold
  - See weakest connections (potential surprises)
- **Connection Pattern Learning:**
  - Track which connections user finds useful
  - Learn optimal confidence thresholds per domain
  - Suggest new connections based on patterns
- **Visual Indicators:**
  - Edge thickness = confidence (thicker = higher)
  - Edge color gradient (red = low, yellow = medium, green = high)
  - Dashed lines for low-confidence connections (<0.4)
- Native notes integration (nodes from Phase 16)
- Code workspace files (nodes from Phase 17)
- Enhanced edge detection (Phase 16 wiki-links, Phase 17 imports)
- "Open in Editor" actions for notes and code
- Real-time graph updates as files change

**Why This Phase:** Shows Polly's reasoning (transparency = trust). Requires Phase 16 and Phase 17 for full integration.

**Marketing Alignment:** "See how you think" - transparent reasoning, not black box

---

#### Phase 15: MCP Server Integration (5-7 days)

**Document:** `PHASE15_MCP_SERVER.md`

**See Also:**
- `PHASE15_INTEGRATION_COMPLETE.md` - Integration completion report
- `PHASE15_SUMMARY.md` - Summary of implementation

**What It Does:**
- Implements Model Context Protocol server
- Exposes all Polly knowledge to external AI tools (OpenCode, Cursor, Claude Desktop, Zed)
- MCP resources: Obsidian notes, GitHub code, Context7 docs, patterns (Phase 13), mental models (Phase 14)
- MCP tools:
  - `search_knowledge(query, sources, limit)` - Semantic search
  - `get_code_context(repo, patterns)` - Repository + learned patterns
  - `get_user_patterns(type)` - Coding patterns from Phase 13
  - `get_mental_model(name, context)` - Apply mental model to problem
- Zero fork maintenance (standard protocol)

**Why This Placement:** Best when patterns and mental models are already learned (Phases 13-14 complete)

**Benefits:**
- ✅ No OpenCode fork needed
- ✅ Works with any MCP-compatible client
- ✅ Enhanced by learned patterns and mental models
- ✅ Future-proof standard protocol

---

#### Phase 17: Code Workspace (3 weeks)

**Document:** `PHASE17_CODE_WORKSPACE.md`

**What It Does:**
- Integrated development environment for 80% of coding tasks
- Monaco editor with 9 languages: Python, JavaScript, TypeScript, C, C++, C#, Lua, Rust, Go
- File tree with Git status indicators
- Integrated terminal (xterm.js)
- Git operations UI (stage, commit, push, pull, visual diff)
- Chat panel with full code context (current file + related files from Phase 12 graph)
- Model routing: Copilot (completion), Claude (refactoring), Local (explanations)
- RAG-powered code search (GitHub repos + local + notes)
- Language/library support via Context7 (downloadable docs)

**Week 1 (5-7 days):** Core editor
- Monaco editor with 9 languages
- File tree with Git status
- Integrated terminal
- Git operations UI

**Week 2 (5-7 days):** Polly integration
- Chat panel with code context
- Model routing (task-based)
- RAG code search
- Context7 language docs

**Week 3 (5-7 days):** Advanced features
- Code actions: "Explain this", "Find similar patterns", "Refactor using mental model", "Save as note"
- Multi-file context (auto-include related files, up to 8k tokens)
- Pattern-aware suggestions (Phase 13 patterns as inline completions)
- Code → Note creation (generates explanation + code block + domain suggestion)

**80/20 Philosophy:**
- 80% in Polly: Quick edits, exploration, learning, prototyping
- 20% in external IDE (via Phase 15 MCP): Debugging, extensions, performance profiling

**Why Last in Tier 1:** Requires all previous phases for maximum value (domains, patterns, mental models, notes, graph, intelligent routing)

---

### UI POLISH SPRINT (1 week) - Between Tier 1 & Tier 2

**When to do this:** After Tier 1 is complete, before packaging (Tier 2).

**Why now:** Ensures professional, consistent UI before:
1. Packaging for distribution (first impressions matter)
2. Tier 3 onboarding (Phase 18 - users see polished UI from start)

**What This Sprint Does:**

Update all remaining Phases 1-5 UIs to match design system established in Phase 0.5:

**Day 1-2: Chat Interface Refresh (Phase 4)**
- Update message bubbles with `ChatMessage` component
- Consistent code blocks and syntax highlighting
- Smooth streaming animation
- Better visual hierarchy

**Day 3: Integration Cards (Phase 3, 5)**
- Apply `IntegrationCard` component consistently
- Update Obsidian, GitHub, Context7 cards
- Consistent status indicators and stats display

**Day 4: Settings & Configuration**
- Update all settings panels
- Consistent form layouts
- Better credential management UI

**Day 5: Navigation & Layout**
- Polish header/navigation
- Sidebar refinement (if applicable)
- Consistent transitions

**Day 6-7: Micro-interactions & Testing**
- Loading states (skeletons, spinners)
- Hover/focus states
- Empty states
- Error states
- Cross-browser testing
- Accessibility verification

**Result:**
- ✅ Entire app uses design system consistently
- ✅ Professional aesthetic throughout
- ✅ Ready for packaging and distribution
- ✅ Onboarding (Phase 18) shows polished UI

**Note:** If you did Phase 0.5 and applied design system incrementally during Tier 1, this sprint is shorter (2-3 days instead of 7).

---

### TIER 2: Packaging & Permissions (1 week)

**When to do this:** After Tier 1 is complete and features are stable.

**Why wait:** Every rebuild during Tier 1 development would require re-signing and re-requesting permissions. Better to build features in dev mode, then package once.

#### App Signing/Notarization (2-3 days)

**What It Does:**
- Build signed macOS app bundle
- Developer ID certificate setup
- Notarize with Apple
- Create stable release build

**Why Required:** macOS permission dialogs only work in signed apps

---

#### Phase 9: macOS Permission Handling (2-3 days)

**Document:** `PHASE9_MACOS_PERMISSIONS.md`

**What It Does:**
- Permission status checking (Calendar, Reminders, Full Disk Access)
- Permission request UI (triggers system dialogs)
- Full Disk Access guidance (opens System Settings)
- Enable 3 complete integrations:
  - **Calendar** (200+ lines, complete)
  - **Reminders** (150+ lines, complete)
  - **FileSystem** (900+ lines, complete)
- Graceful error handling

**Total Code Activated:** ~1,400 lines

**Why After Tier 1:** Requires stable signed app bundle. Permissions persist across launches, but rebuilding during development is disruptive.

---

### TIER 3: Polish & Autonomy Awareness (2-3 weeks)

**When to do this:** After Tier 2 (packaging + permissions) is complete.

**Why important:** These phases improve user adoption, demonstrate progressive autonomy (core marketing theme), and provide data sovereignty (competitive differentiator).

#### Phase 18: Onboarding & Progressive Teaching (1-2 weeks)

**Document:** `PHASE18_ONBOARDING.md`

**What It Does:**
- First-run wizard with dual-path choice:
  - **Path 1: Zero-Config Quick Start** (auto-creates Work/Personal/Learning domains)
  - **Path 2: Custom Domains** (full Phase 1.5 configuration)
- Progressive feature revelation (Week 1: basics, Week 2: patterns, Week 3: mental models)
- Adaptive tutorial system that fades with mastery
- **Autonomy Dashboard:** 5 core metrics showing progressive learning:
  1. Token Usage Trend (local vs. cloud ratio)
  2. RAG Hit Rate (% queries answered locally)
  3. Pattern Learning Progress (# patterns per domain)
  4. Time Since Last Cloud Query (per topic/domain)
  5. Knowledge Compound Score (30-day rolling metric)
- Usage pattern detection and proactive feature suggestions

**Why Tier 3:**
- Improves user adoption and reduces learning curve
- Shows progressive autonomy (core marketing message)
- Enables zero-config for casual users
- Builds confidence in Polly's capabilities

**Marketing Alignment:**
- "Polly teaches you as you teach Polly"
- "Progressive autonomy, not permanent dependency"
- "Start simple, grow sophisticated"

---

#### Phase 19: Data Autonomy & Export (5-7 days)

**Document:** `PHASE19_DATA_AUTONOMY.md`

**What It Does:**
- **Knowledge Graph Export:**
  - JSON format (full data, programmatic access)
  - GraphML format (Gephi, yEd, Cytoscape)
  - CSV format (spreadsheets, analysis)
- **Notes Export:**
  - Markdown files (portable, preserves structure)
  - JSON format (with metadata, frontmatter, tags)
  - HTML format (standalone browsing)
- **Full System Backup:**
  - Complete `.polly/` directory archive
  - Verification system (checksums, integrity)
  - One-click restore with rollback safety
- **Self-Hosted Setup Guides:**
  - Docker Compose (recommended, includes Qdrant + Ollama + Polly)
  - Manual setup (systemd, Nginx, security hardening)
  - Kubernetes (Helm charts, production deployment)
- **Offline Mode:**
  - Full core functionality without internet
  - Local models only (Ollama)
  - Sync when connection restored
- **Import/Restore:**
  - Import from JSON/GraphML/Markdown
  - Merge strategies (replace/merge/skip)
  - Rollback if import fails

**Why Tier 3:**
- Core differentiation: "Your data. Your freedom."
- Anti-platform-lock-in positioning
- Privacy-conscious user appeal
- Professional user requirement (data sovereignty)

**Marketing Alignment:**
- "Your data. Your freedom."
- "Build capability, don't rent it"
- "Own your intelligence"

---

### TIER 4: Advanced Communication (2-3 weeks)

**When to do this:** After Tier 2 is complete. Can run in parallel with Tier 3.

**Why different:** These are Jace.ai-like features but with progressive autonomy (patterns become local rules, not permanent AI dependency). Privacy-first architecture (local processing default).

**Target audience:** Professionals drowning in email, privacy-conscious users, ADHD users struggling with communication overload.

#### Phase 20a: Email Intelligence (1 week)

**Document:** `PHASE20_INTELLIGENT_COMMUNICATION.md`

**What It Does:**
- IMAP integration (Gmail, Outlook, iCloud)
- Email categorization (Important, FYI, Social, Newsletters, Spam, Needs Response)
- Smart summaries (thread summarization, action extraction)
- Noise filtering (newsletter consolidation, social grouping)
- **Privacy-first:** Local processing by default (Ollama), cloud fallback only for complex analysis

**Storage:** `~/.polly/email/` (metadata only, no full email storage)

---

#### Phase 20b: Calendar & Action Items (1 week)

**Document:** `PHASE20_INTELLIGENT_COMMUNICATION.md`

**What It Does:**
- Meeting analysis (pre-meeting context, participant lookup, talking points)
- Action item extraction from emails and meetings
- Draft task creation in Reminders.app
- Calendar intelligence (prep reminders, travel time, conflict detection)
- Meeting notes integration (Phase 16)

**Requires:** Phase 9 (permissions) must be complete first

---

#### Phase 20c: Communication Progressive Autonomy (3-5 days)

**Document:** `PHASE20_INTELLIGENT_COMMUNICATION.md`

**What It Does:**
- **Pattern → Local Rule Conversion:**
  - After 5-10 repetitions, suggest converting to local rule (no AI needed)
  - Example: "Always categorize emails from sarah@example.com as Important" → local rule
- **Communication Autonomy Dashboard:**
  - % emails handled by local rules (vs. AI analysis)
  - % meetings with auto-generated context
  - Action item completion rate
  - Time saved (estimated)
- **Graduated Independence:**
  - Week 1: AI analyzes everything
  - Week 2-3: Patterns emerge, suggest rules
  - Week 4+: Most communication handled by rules, AI only for edge cases
- **Privacy Report:**
  - Show exactly what data sent to cloud (if any)
  - Token usage for email/calendar
  - Local-first percentage (target: >90%)

**Why Tier 4:**
- Jace.ai-like features (not core differentiator yet)
- Requires Phase 9 (permissions) complete
- Nice-to-have vs. must-have
- More complex integrations

**Why Different from Jace.ai:**
- **Jace.ai:** Permanent AI dependency, cloud-only, opaque reasoning
- **Polly:** Progressive autonomy, local-first, transparent pattern learning, user controls rules

**Marketing Alignment:**
- "Build capability, don't rent it"
- "Progressive autonomy, not permanent dependency"
- "Privacy-first by design"
- "Jace.ai for people who want to own their systems"

---

### TIER 5: Optional Enhancements (4-7 weeks total)

These improve existing features but aren't essential. Include major strategic features for power users and teams.

#### Phase 23: Project Management & Documentation-First Workflows (3-4 weeks) ⭐ **NEW**

**Document:** `PHASE23_PROJECT_MANAGEMENT.md`

**What It Does:**
- Comprehensive project management with documentation-first philosophy
- Standardized project workflows (code, writing, creative, research)
- Project-specific pattern learning (build commands, architecture, vocabulary)
- Plan/Build modes for Code Workspace (resist building until well-planned)
- Always-current PROJECT.md (automatically updated with architectural changes)
- Architectural change awareness (prompts to update docs when code changes)
- Compression & memory system ("Polly shorthand" for context preservation)
- Context-aware RAG filtering (Code doesn't see calendar, Calendar doesn't see code)
- Dashboard as daily briefing (aggregates insights across all domains)
- Project maturity framework (5 dimensions: planning, implementation, docs, testing, deployment)
- Slack-like project interface (channel-based organization for projects)

**Key Philosophy:**
"You don't build a rough idea, you plan until it is a detailed vision."

**Week Breakdown:**
- Week 1-2: Core project system, templates, project-specific pattern learning
- Week 3: Plan/Build modes for Code Workspace
- Week 4: UI (Slack-like interface), Dashboard briefing, Context-aware RAG

**Why Tier 5:**
- Advanced feature for power users
- Requires Phases 1.5, 13, 16, 17 complete
- Nice-to-have for individual users, essential for teams/professional use
- Large scope (3-4 weeks)

**Target Users:**
- Professional developers managing complex projects
- Teams needing structured workflows
- Users developing Polly itself (solve our own pain point)
- Anyone managing multiple codebases (firmware, web, mobile, etc.)

**Marketing Alignment:**
- "Build capability, don't rent it" - Integrated project management, not another SaaS
- "Knowledge that compounds" - Project patterns improve development speed over time
- "Stop organizing. Start working." - Standardized workflows remove decision fatigue

**Integration Points:**
- Phase 1.5: Projects belong to domains
- Phase 13: Project-specific pattern learning
- Phase 16: Project documentation as notes
- Phase 17: Plan/Build modes in Code Workspace
- Phase 20: Project-related emails and meetings

**Storage:** `~/.polly/projects/{name}/`

**Open Questions:**
- Cross-user family integration for shared projects?
- Figma integration for design files in PROJECT.md?
- How granular should tracking be? (file-level vs function-level)

---

#### Phase 6: Enhanced GitHub Integration (3-5 days)

**Document:** `PHASE6_GITHUB_ENHANCEMENTS.md`

**Optional improvements:**
- Incremental sync (only fetch changed repos)
- Parallel README fetching (10x faster)
- Code search within repos
- Commit history indexing

**When to do:** If GitHub sync is too slow or deeper code search needed

---

#### Phase 7: Advanced Calendar Features (5-7 days)

**Document:** `PHASE7_CALENDAR_FEATURES.md`

**Requires:** Phase 9 first

**Note:** Most features from Phase 7 are now covered by Phase 20b. This phase is only for additional advanced features not covered there.

**Optional improvements beyond Phase 20b:**
- Multi-account support (iCloud + Google + Exchange simultaneously)
- Advanced calendar visualization
- Calendar analytics and insights

**When to do:** If Phase 20b calendar features aren't enough

---

#### Phase 8: New Integrations (varies, 1-2 weeks each)

**Document:** `PHASE8_NEW_INTEGRATIONS.md`

**Options:**
- Browser History
- Apple Notes
- Photos
- Music
- Slack (if not covered by Phase 20)

**Note:** Email integration is now Phase 20a. Calendar advanced features are Phase 20b.

**When to do:** If specific integration needed

---

### TIER 6: Future (3-4 weeks)

#### Phase 10: iOS Mobile App (3-4 weeks)

**Document:** `PHASE10_IOS_MOBILE.md`

**What It Does:**
- SwiftUI iOS companion app
- Sync via Tailscale
- Quick capture (voice, photos, text)
- Conversation access on mobile
- Voice input/output

**When to do:** After desktop app is stable (Tiers 1-2 complete, optionally Tiers 3-4)

---

## Detailed Phase Plans

### Summary of All Phases

| Phase | Name | Status | Duration | Document |
|-------|------|--------|----------|----------|
| 1 | UI Foundation | ✅ Complete | - | `PHASE1_TESTING.md` |
| 2 | GitHub OAuth | ✅ Complete | - | `PHASE2_SETUP.md` |
| 3 | Obsidian Integration | ✅ Complete | - | `PHASE3_COMPLETE_SUMMARY.md` |
| 4 | Multi-Conversation System | ✅ Complete | - | In MASTER_ROADMAP |
| 5 | Backend Integration Framework | ✅ Complete | - | `PHASE5_COMPLETE.md` |
| **1.5** | **Domain Configuration** | ✅ **Complete** | **6 days** | **`PHASE1.5_DOMAIN_CONFIGURATION.md`** |
| 6 | Enhanced GitHub | ⏸️ Optional (Tier 5) | 3-5 days | `PHASE6_GITHUB_ENHANCEMENTS.md` |
| 7 | Advanced Calendar | ⏸️ Optional (Tier 5) | 5-7 days | `PHASE7_CALENDAR_FEATURES.md` |
| 8 | New Integrations | 📋 Optional (Tier 5) | 1-2 weeks each | `PHASE8_NEW_INTEGRATIONS.md` |
| 9 | macOS Permissions | 📋 Planned (Tier 2) | 2-3 days | `PHASE9_MACOS_PERMISSIONS.md` |
| 10 | iOS Mobile App | 📋 Future (Tier 6) | 3-4 weeks | `PHASE10_IOS_MOBILE.md` |
| **11** | **Multi-Model + Intelligent Routing** | 📋 **Planned (Tier 1)** | **10-14 days** | **`PHASE11_MULTI_MODEL_ENHANCED.md`** |
| **12** | **Knowledge Graph + Reasoning** | 📋 **Planned (Tier 1)** | **2.5-3.5 weeks** | **`PHASE12_KNOWLEDGE_GRAPH.md`** |
| **13a** | **Pattern Learning (Core)** | ✅ **Complete** | **16 days** | **`PHASE13A_PATTERN_LEARNING_CORE.md`** |
| **13b** | **Pattern Learning (UI)** | 📋 Planned (Tier 1) | **5-7 days** | **`PHASE13A_PATTERN_LEARNING_CORE.md`** |
| 14 | Mental Models | 📋 Planned (Tier 1) | 3-5 days | `PHASE14_MENTAL_MODELS.md` |
| 15 | MCP Server | 📋 Planned (Tier 1) | 5-7 days | `PHASE15_MCP_SERVER.md` |
| **16** | **Native Note Management** | 📋 **Planned (Tier 1)** | **3.5-4.5 weeks** | **`PHASE16_NATIVE_NOTES.md`** |
| **17** | **Code Workspace** | 📋 **Planned (Tier 1)** | **3 weeks** | **`PHASE17_CODE_WORKSPACE.md`** |
| **18** | **Onboarding & Progressive Teaching** | 📋 **Planned (Tier 3)** | **1-2 weeks** | **`PHASE18_ONBOARDING.md`** |
| **19** | **Data Autonomy & Export** | 📋 **Planned (Tier 3)** | **5-7 days** | **`PHASE19_DATA_AUTONOMY.md`** |
| **20a** | **Email Intelligence** | 📋 **Planned (Tier 4)** | **1 week** | **`PHASE20_INTELLIGENT_COMMUNICATION.md`** |
| **20b** | **Calendar & Action Items** | 📋 **Planned (Tier 4)** | **1 week** | **`PHASE20_INTELLIGENT_COMMUNICATION.md`** |
| **20c** | **Communication Progressive Autonomy** | 📋 **Planned (Tier 4)** | **3-5 days** | **`PHASE20_INTELLIGENT_COMMUNICATION.md`** |
| **21** | **Knowledge Base Deduplication** | 📋 **Planned (Tier 1)** | **2-3 days** | **`PHASE21_KNOWLEDGE_DEDUPLICATION.md`** |
| **22** | **Teaching Mode** | 📋 **Planned (Tier 1)** | **2-3 days** | **`PHASE22_TEACHING_MODE.md`** |

### Key Phase Summaries

#### Phase 1.5: Domain Configuration System (✅ COMPLETE)

**Status:** Backend 100% complete (Jan 25, 2026). UI wizard deferred to Phase 18.

**Key Innovation:** Makes Polly adaptable to any workflow by allowing user-defined knowledge domains.

**Implemented Features:**
- ✅ **Backend System:** Full domain config system with `~/.polly/domains.json`
- ✅ **Settings UI:** Complete domain management interface with CRUD operations
- ✅ **Pattern Integration:** Use Case 2 - Pattern-boosted domain detection (146% boost)
- ✅ **Quick Start:** 3 basic domains (Work, Personal, Learning)
- ✅ **Template System:** 4 pre-configured templates (Software Dev, Research, Creative, Business)
- ✅ **CLI Wizard:** Interactive command-line setup tool
- ✅ **First-Run Detection:** Automatic detection and setup guidance

**Deferred to Phase 18:**
- UI wizard (React/Electron graphical wizard)
- AI keyword suggestions
- Obsidian vault analysis

**Enables:** All other phases rely on this domain system (Phases 11, 12, 13, 14, 16, 17)

**Documentation:**
- `PHASE1.5_MIGRATION_COMPLETE.md` - Days 1-2
- `USE_CASE_2_COMPLETE.md` - Day 5
- `PHASE1.5_DAY6_COMPLETE.md` - Day 6

**Marketing Alignment:** "Your work doesn't fit in boxes" + "Stop organizing. Start working."

---

#### Phase 11: Multi-Model + Intelligent Routing (ENHANCED)

**Key Innovation:** Confidence-based routing automatically chooses local vs cloud based on knowledge quality.

**Three-Layer Confidence:**
1. Pre-flight (RAG quality): Skip local if <40% confidence
2. Output analysis: Generate meta-query if local output <60% quality
3. Historical learning: Adapt thresholds based on success patterns

**Token Management:**
- Track usage across all providers
- Monthly budgets with rollover
- Automatic fallback when limits reached

**Draft Notes Queue:**
- AI-generated notes go to `_Drafts/` folder
- User reviews, edits, then moves to proper domain
- Prevents knowledge base pollution with low-quality content

---

#### Phase 16: Native Note Management (NEW)

**Key Innovation:** Replaces Obsidian entirely - one app for everything.

**Three Sub-Phases:**
- 16a: Core editor (Monaco, file ops, one-time import) - 2 weeks
- 16b: Power features (wiki-links, backlinks, tags, templates) - 1-2 weeks
- 16c: Polly enhancements (AI creation, auto-tagging, proactive suggestions, auto-organization) - 5-7 days

**Key Phase 16c Features:**
- Proactive connection suggestions while writing (real-time wiki-link recommendations)
- Auto-organization mode (automatically file notes into correct domains with confidence-based prompting)
- AI note creation from conversations
- Domain auto-tagging using Phase 1.5 rules
- Graph integration

**Important Decision:** One-time Obsidian import only (not bidirectional). Users migrate to Polly, simplifying architecture significantly.

**Marketing Alignment:** "Stop organizing. Start working." - auto-organization removes friction

---

#### Phase 17: Code Workspace (NEW)

**Key Innovation:** 80% of development happens in Polly with full context, 20% in external IDE.

**Three Weeks:**
- Week 1: Core editor (Monaco, terminal, Git UI)
- Week 2: Polly integration (chat, routing, RAG search)
- Week 3: Advanced features (code actions, patterns, note creation)

**9 Built-in Languages:**
Python, JavaScript, TypeScript, C, C++, C#, Lua, Rust, Go

**Context-Aware:** Chat panel auto-includes current file + related files from knowledge graph (up to 8k tokens)

---

#### Phase 18: Onboarding & Progressive Teaching (NEW - TIER 3)

**Key Innovation:** Teaches users gradually while demonstrating progressive autonomy (core marketing message).

**Dual-Path First-Run:**
- **Zero-Config Quick Start:** Auto-creates Work/Personal/Learning domains, auto-filing intelligence
- **Custom Domains:** Full Phase 1.5 configuration with templates

**Progressive Feature Revelation:**
- Week 1: Core chat interface, basic RAG
- Week 2: Domain auto-tagging, pattern learning
- Week 3: Mental models, knowledge graph
- Adaptive: Accelerates if user demonstrates mastery

**Autonomy Dashboard (5 Metrics):**
1. Token Usage Trend (local vs. cloud)
2. RAG Hit Rate (% queries answered locally)
3. Pattern Learning Progress
4. Time Since Last Cloud Query (per topic)
5. Knowledge Compound Score (30-day rolling)

**Marketing Alignment:** "Polly teaches you as you teach Polly" - shows progressive autonomy in action

---

#### Phase 19: Data Autonomy & Export (NEW - TIER 3)

**Key Innovation:** Complete data freedom - export everything, self-host, work offline. Zero platform lock-in.

**Export Formats:**
- **Knowledge Graph:** JSON (full data), GraphML (Gephi/yEd), CSV (analysis)
- **Notes:** Markdown (portable), JSON (metadata), HTML (browsing)
- **Full Backup:** Complete `.polly/` archive with verification + rollback

**Self-Hosted Options:**
- Docker Compose (recommended): Pre-configured with Qdrant + Ollama
- Manual setup: systemd, Nginx, security hardening
- Kubernetes: Helm charts for production

**Offline Mode:**
- Full core functionality without internet
- Local models only (Ollama)
- Sync when connection restored

**Marketing Alignment:** "Your data. Your freedom." - competitive differentiator vs. cloud-locked AI services

---

#### Phase 20: Intelligent Communication (NEW - TIER 4, 3 SUB-PHASES)

**Key Innovation:** Jace.ai-like features BUT with progressive autonomy (patterns become local rules, not permanent AI dependency).

**Phase 20a: Email Intelligence (1 week)**
- IMAP integration (Gmail, Outlook, iCloud)
- Email categorization (Important, FYI, Social, Newsletters, Spam, Needs Response)
- Smart summaries, action extraction, noise filtering
- **Privacy-first:** Local processing default (Ollama), cloud fallback only for complex analysis

**Phase 20b: Calendar & Action Items (1 week)**
- Meeting analysis (pre-meeting context, participant lookup, talking points)
- Action item extraction from emails/meetings
- Draft task creation in Reminders.app
- Calendar intelligence (prep reminders, conflict detection)

**Phase 20c: Communication Progressive Autonomy (3-5 days)**
- **Pattern → Local Rule Conversion:** After 5-10 repetitions, convert to rule (no AI needed)
- **Communication Autonomy Dashboard:** Show % handled by rules vs. AI
- **Graduated Independence:** Week 1 (AI analyzes all) → Week 4+ (rules handle most, AI only for edge cases)
- **Privacy Report:** Show exactly what was sent to cloud (target: <10%)

**Why Different from Jace.ai:**
- Jace.ai: Permanent AI dependency, cloud-only, opaque
- Polly: Progressive autonomy, local-first, transparent, user controls rules

**Marketing Alignment:** "Build capability, don't rent it" - vs. Jace.ai's permanent subscription model

---

## Dependencies & Risk Management

### Phase Dependencies

```
Phase 1.5 (Domains) ← FOUNDATION
  ├── Enables: Phase 11 (domain suggestions)
  ├── Enables: Phase 13 (domain-aware patterns)
  ├── Enables: Phase 14 (domain-based mental models)
  ├── Enables: Phase 16 (domain folders)
  └── Enables: Phase 17 (domain-aware code context)

Phase 13 (Patterns) + Phase 14 (Mental Models)
  └── Enhance: Phase 15 (MCP exposes patterns/models)

Phase 16 (Native Notes)
  ├── Required by: Phase 12b (graph enhancement)
  └── Required by: Phase 17 (code → note)

Phase 17 (Code Workspace)
  ├── Requires: All previous Tier 1 phases
  └── Required by: Phase 12b (graph enhancement)

Phase 9 (Permissions)
  ├── Requires: Signed app bundle (Tier 2)
  ├── Enables: Calendar integration
  ├── Enables: Reminders integration
  └── Enables: FileSystem integration
```

### Risk Management

#### Risk 1: Timeline Overruns

**Risk:** Phases take longer than estimated  
**Impact:** Medium (user stated "timeline isn't important")  
**Likelihood:** Medium  
**Mitigation:**
- Track velocity daily
- Adjust scope if behind
- Phases are independent - can pause and resume

#### Risk 2: Obsidian Import Complexity

**Risk:** One-time import may not capture all Obsidian features  
**Impact:** Medium (users may lose some data)  
**Likelihood:** Low (markdown is straightforward)  
**Mitigation:**
- Clear documentation of what's imported
- Support for re-running import
- Manual file copy as fallback

#### Risk 3: Pattern Learning Storage Issues

**Risk:** Pattern storage gets corrupted  
**Impact:** Low (patterns can be re-learned)  
**Likelihood:** Low (simple JSON)  
**Mitigation:**
- Automatic backups (.backup files)
- Validation on load
- Easy to recreate

#### Risk 4: Monaco Editor Performance

**Risk:** Large files may slow down Monaco  
**Impact:** Medium (poor UX)  
**Likelihood:** Low (Monaco handles large files well)  
**Mitigation:**
- Virtual scrolling (built into Monaco)
- File size warnings (>1MB)
- Fallback to simple textarea

#### Risk 5: Confidence Thresholds Too Aggressive

**Risk:** System may skip local models when they'd work fine  
**Impact:** Medium (wastes cloud tokens)  
**Likelihood:** Medium  
**Mitigation:**
- Conservative initial thresholds (60%/70%)
- User can override per-query
- Dashboard shows routing decisions
- Thresholds adjustable in settings

---

## Future Enhancements

### Beyond Phase 17

**Conversation System:**
- LLM-based automatic categorization
- Conversation export (markdown, PDF, JSON)
- Conversation merge/split
- Conversation analytics and insights

**Integration Expansions:**
- More Context7 libraries
- GitHub: code search, commit history, contributor insights
- FileSystem: copy/delete operations, duplicate detection
- New: Email, Slack, Browser History, Apple Notes, Photos, Music

**Core System:**
- Real-time collaboration (multi-device sync)
- Voice input/output (Whisper + TTS)
- Web interface (via Tailscale)
- Plugin system for third-party integrations

**Notes System Enhancements:**
- Multi-source notes support (use Obsidian + native notes simultaneously)
  - Multiple vaults indexing with source prefixes (e.g., 'notes_personal', 'notes_work')
  - UI toggle to enable/disable sources
  - Unified search across enabled sources
  - RAG collection management per source
  - Config: `notes.sources` array with type/path/enabled per source
  - Example use case: Keep personal Obsidian vault separate from work notes
- LaTeX math rendering (KaTeX) in markdown preview
- Mermaid diagram rendering in markdown preview
- Advanced Dataview-like query system for native notes
  - Query language for frontmatter + content filtering
  - Live-updating query results embedded in notes
  - AI-powered smart queries ("show unreviewed notes about React")

**Developer Experience:**
- API documentation (OpenAPI/Swagger)
- Automated testing framework
- Performance monitoring
- Debug mode with verbose logging

**User Experience:**
- Onboarding flow with interactive tutorial
- Full keyboard shortcuts
- Themes (dark mode, custom colors)
- Accessibility (screen reader, high contrast)
- Multi-language (i18n)
- Full data export/backup

---

## Reference

### Key Files

#### Planning Documents

```
/MASTER_ROADMAP.md                        # This file (merged roadmap)
/PHASE_STATUS_SUMMARY.md                  # Phase status overview
/MARKETING_POSITIONING.md                 # Marketing strategy & positioning
/DESIGN_SYSTEM.md                         # UI design system documentation

# Tier 0
/PHASE0.5_UI_DESIGN_SYSTEM.md            # UI Design System (NEW)

# Tier 1 - Completed Phases
/PHASE1_TESTING.md                        # Phase 1: UI Foundation
/PHASE2_SETUP.md                          # Phase 2: GitHub OAuth
/PHASE2_FIXED.md                          # Phase 2: Supplementary fixes
/PHASE3_COMPLETE_SUMMARY.md              # Phase 3: Obsidian Integration
/PHASE3_UI_TESTING.md                    # Phase 3: UI testing notes
/PHASE5_COMPLETE.md                       # Phase 5: Backend Framework
/PHASE5_TEST.md                           # Phase 5: Testing notes

# Tier 1 - Planned Phases
/PHASE1.5_DOMAIN_CONFIGURATION.md        # Domain system (NEW)
/PHASE1.5_MIGRATION_COMPLETE.md          # Phase 1.5: Migration report
/PHASE1.5_QUICK_REFERENCE.md             # Phase 1.5: Quick reference
/PHASE11_MULTI_MODEL_ENHANCED.md         # Intelligent routing (ENHANCED)
/PHASE11_MULTI_MODEL.md                  # Original version (superseded by ENHANCED)
/PHASE12_KNOWLEDGE_GRAPH.md              # Knowledge graph + reasoning transparency
/PHASE13_PATTERN_LEARNING.md             # Pattern learning
/docs/PHASE13_PROGRESS.md                # Phase 13: Progress tracking
/PHASE14_MENTAL_MODELS.md                # Mental models
/PHASE15_MCP_SERVER.md                   # MCP server
/PHASE15_INTEGRATION_COMPLETE.md         # Phase 15: Integration report
/PHASE15_SUMMARY.md                      # Phase 15: Summary
/PHASE16_NATIVE_NOTES.md                 # Native notes (NEW)
/PHASE17_CODE_WORKSPACE.md               # Code workspace (NEW)

# Tier 2
/PHASE9_MACOS_PERMISSIONS.md             # macOS Permissions

# Tier 3
/PHASE18_ONBOARDING.md                   # Onboarding & Progressive Teaching (NEW)
/PHASE19_DATA_AUTONOMY.md                # Data Autonomy & Export (NEW)

# Tier 4
/PHASE20_INTELLIGENT_COMMUNICATION.md    # Email/Calendar Intelligence (NEW)

# Tier 5
/PHASE6_GITHUB_ENHANCEMENTS.md           # Enhanced GitHub (optional)
/PHASE7_CALENDAR_FEATURES.md             # Advanced Calendar (optional)
/PHASE8_NEW_INTEGRATIONS.md              # New Integrations (optional)

# Tier 6
/PHASE10_IOS_MOBILE.md                   # iOS Mobile App (future)

# Deprecated/Superseded
# PHASE11_MULTI_MODEL.md - Original version, superseded by PHASE11_MULTI_MODEL_ENHANCED.md
```

#### Conversation System

```
/electron-app/src/main/conversation-manager.js  # Core logic (595 lines)
/electron-app/src/main/db/schema.sql            # Database schema
/electron-app/src/renderer/app.js               # Frontend UI
~/Library/Application Support/polly/conversations.db  # SQLite database
```

#### Integration System

```
/integrations/base.py           # Base architecture
/integrations/github.py         # GitHub integration
/integrations/context7.py       # Context7 integration
/integrations/obsidian.py       # Obsidian base
/integrations/obsidian_smart.py # Smart features (530 lines)
/integrations/calendar.py       # Calendar (disabled, awaiting Phase 9)
/integrations/reminders.py      # Reminders (disabled, awaiting Phase 9)
/integrations/filesystem.py     # File System (disabled, 446 lines)
/interfaces/server.py           # FastAPI endpoints
```

#### Frontend (Electron)

```
/electron-app/src/renderer/index.html      # UI structure
/electron-app/src/renderer/app.js          # Application logic
/electron-app/src/renderer/styles/main.css # Styling
/electron-app/src/main/main.js             # Main process + IPC
/electron-app/src/main/preload.js          # IPC bridge
```

#### Pattern Learning (Dormant)

```
/learners/patterns.py           # Pattern learning system (445 lines, needs activation)
~/.polly/patterns.json          # Storage (will be created in Phase 13)
```

### Configuration & State

```
~/.polly/domains.json                           # Domain configuration (Phase 1.5)
~/.polly/patterns.json                          # Learned patterns (Phase 13)
~/.polly/mental_models.yaml                     # Mental models (Phase 14)
~/.polly/token_usage.json                       # Token tracking (Phase 11)
~/.polly/notes/                                 # Native notes storage (Phase 16)
~/.polly/notes/_Drafts/                         # Draft notes queue (Phase 11)
~/.polly/notes/_Templates/                      # Note templates (Phase 16)
~/.polly/integrations_state.json                # Integration state
~/Library/Application Support/polly/            # App data directory
~/Library/Application Support/polly/conversations.db  # Conversations
macOS Keychain → Service: "Polly"               # Credentials
```

### Current Metrics

**Data Indexed:**
- Obsidian: 3,508 chunks (75 files)
- Codebase: 178 chunks (26 files)
- GitHub: 17 repos synced
- Context7: React library + more
- **Total:** ~4,000+ searchable documents

**Conversations:**
- Currently: 1 conversation
- Capacity: 500 conversations
- Categories: 6 (5 domains + uncategorized)

**Integration Status:**
- ✅ Working: GitHub, Context7, Obsidian (3)
- ⏸️ Ready (needs Phase 9): Calendar, Reminders, FileSystem (3)
- 🔜 Future: Email, Slack, Browser History, etc.

### Development Timeline

**Completed (2024-2025):**
- ✅ Phases 1-5 complete

**Current (Q1 2026):**
- 🔄 Planning and documentation (Phases 1.5, 11, 16, 17)

**Next (Q1-Q2 2026):**
- 🔜 TIER 1: Core Intelligence (12.5-15.5 weeks)
  - Phase 1.5 → 13 → 14 → 12a → 11 → 16a → 16b → 16c → 12b → 15 → 17
- 🔜 TIER 2: Packaging & Permissions (1 week)
  - App Signing → Phase 9

**Future (Q2 2026+):**
- Optional: Phases 6-8 (enhancements)
- Future: Phase 10 (iOS mobile)

### Estimated Completion

**Minimum Viable (Tier 1 only):** 12.5-15.5 weeks  
**With Permissions (Tier 1 + 2):** 13.5-16.5 weeks  
**With Optional (Tier 1 + 2 + some Tier 3):** 15-20 weeks  
**Complete with Mobile (All tiers):** 18-24 weeks

**Note:** User stated "Timeline isn't important to me. We just keep hammering on this until we have it working well." Focus on quality over speed.

---

## Getting Started

### For New Contributors

1. **Read this document** - Understand full scope and architecture
2. **Review phase documents** - Deep dive into specific phases
3. **Check current status** - See `PHASE_STATUS_SUMMARY.md`
4. **Start with Phase 1.5** - Foundation for everything else

### For Users

1. **Install dependencies:** `npm install` (in electron-app/)
2. **Start the app:** `npm run dev`
3. **Complete setup wizard**
4. **Connect integrations:** GitHub, Context7, Obsidian
5. **Start exploring!**

### For Developers

**Current Priority:** Implement Tier 1 phases in order

**Testing:**
- Run Electron app: `npm run dev` (in electron-app/)
- Test backend: Python scripts in `/scripts/`
- Check database: `sqlite3 ~/Library/Application Support/polly/conversations.db`

**Next Action:** Begin Phase 1.5 implementation (see `PHASE1.5_DOMAIN_CONFIGURATION.md`)

---

**Last Updated:** January 23, 2026  
**Version:** 2.0 (Merged Roadmap)  
**Status:** ~70% Complete - Ready for Tier 1 Implementation  
**Next Phase:** Phase 1.5 (Domain Configuration System)
