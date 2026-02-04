# Polly: Phase Status Summary

**Last Updated:** January 29, 2026  
**Project Status:** ~62% Complete (Phases 0.5, 1-5, 1.5, 2a, 2b, 11c, 13a, 14, 16, 21 done)  
**Current Phase:** Phases 14 & 21 Complete ✅

---

## 🎯 Current Focus & Next Steps

**Recently Completed:**

**Phase 14 - Mental Models System** ✅ (Jan 29, 2026)
- ✅ Three-tier activation (Domain + Page + Persona)
- ✅ PIL compression achieving 2.3x ratio
- ✅ 12 default mental models across 4 tiers
- ✅ Template system with 5 pre-built templates
- ✅ Settings UI with full CRUD operations
- ✅ Per-conversation override via context menu
- ✅ REST API with 7 endpoints
- ✅ Future-proof for Phase 20 (Mail/Calendar) and Phase 22 (Teaching Mode)
- ✅ 48/51 tests passing (94%)

**Phase 21 - Knowledge Base Deduplication** ✅ (Jan 28, 2026)
- ✅ Semantic similarity detection before note creation
- ✅ "Similar notes found" warning with three action options
- ✅ Prevents knowledge fragmentation
- ✅ DeduplicationEngine with RAG integration
- ✅ UI integrated into Create Note Modal
- ✅ Append, link, and create-anyway workflows

**Next Recommended:** Phase 22 - Teaching Mode (2-3 days)
- NOW UNBLOCKED (Phase 14 complete)
- Specialized "Teaching Mode" persona
- Socratic method integration
- Builds on mental models system

**Alternative Next:** Phase 11 - Multi-Model Router v2 (10-14 days)
- Provider management (OpenAI, Anthropic, GitHub)
- Intelligent routing with confidence-based selection
- Cost tracking and optimization
- Foundation for advanced features

**See:** PHASE14_IMPLEMENTATION_COMPLETE.md and PHASE21_KNOWLEDGE_DEDUPLICATION.md

---

## Quick Status Overview

| Phase | Name | Status | Priority | Effort | Blocks |
|-------|------|--------|----------|--------|--------|
| 1 | UI Foundation | ✅ Complete | - | - | - |
| 2 | GitHub OAuth | ✅ Complete | - | - | - |
| 3 | Obsidian Integration | ✅ Complete | - | - | - |
| 4 | Multi-Conversation System | ✅ Complete | - | - | - |
| 5 | Backend Integration Framework | ✅ Complete | - | - | - |
| **0.5** | **Obsidian-Inspired UI Redesign** | ✅ **Complete (Jan 26)** | **🟡 High (Tier 0)** | **7 days** | **None** |
| **1.5** | **Domain Configuration** | ✅ **Complete (Jan 25)** | **🟡 High (Tier 1)** | **6 days** | **None** |
| **2a** | **RAG Optimization** | ✅ **Complete (Jan 28)** | **🟡 High (Tier 1)** | **3 days** | **Phase 1.5** |
| **2b** | **Pattern Compression** | ✅ **Complete (Jan 28)** | **🟡 High (Tier 1)** | **2 days** | **Phase 13a** |
| **11c** | **Compression UI** | ✅ **Complete (Jan 28)** | **🟡 High (Tier 1)** | **1 day** | **Phase 2b** |
| **13a** | **Pattern Learning Core** | ✅ **Complete (Jan 25)** | **🟡 High (Tier 1)** | **16 days** | **Phase 1.5** |
| **14** | **Mental Models System** | ✅ **Complete (Jan 29)** | **🟡 High (Tier 1)** | **5 days** | **Phase 1.5** |
| **16** | **Native Notes Frontend** | ✅ **Complete (Jan 26)** | **🟡 High (Tier 1)** | **1 day** | **Phase 0.5** |
| **21** | **Knowledge Base Deduplication** | ✅ **Complete (Jan 28)** | **🟡 High (Tier 1)** | **2-3 days** | **Phase 16** |
| **22** | **Teaching Mode** | 📋 **Ready (UNBLOCKED)** | **🟡 High (Tier 1)** | **2-3 days** | **Phase 14** ✅ |
| **13b** | **Pattern Learning UI** | 📋 **Planned** | **🟡 High (Tier 1)** | **7 days** | **Phase 13a** |
| **12a** | **Knowledge Graph - Basic** | 📋 **Planned** | **🟡 High (Tier 1)** | **5-7 days** | **Phase 1.5** |
| **12b** | **Knowledge Graph - Reasoning** | 📋 **Planned** | **🟡 High (Tier 1)** | **1-2 weeks** | **Phase 12a, 16, 17** |
| **11** | **Multi-Model + Intelligent Routing** | 📋 **Planned** | **🟡 High (Tier 1)** | **10-14 days** | **Phase 1.5, 13a** |
| **15** | **MCP Server Integration** | 📋 **Planned** | **🟡 High (Tier 1)** | **5-7 days** | **Phases 13a, 14** |
| **17** | **Code Workspace** | 📋 **Planned** | **🟡 High (Tier 1)** | **3 weeks** | **All Tier 1 phases** |

**Legend:**
- ✅ Complete
- 🚧 In Progress
- 📋 Planned
- ⏸️ Not Started (Optional/Deferred)
- 🟡 High Priority
- 🟢 Medium Priority
- 🟣 Low Priority
- 🔴 Critical

---

## Recommended Implementation Order

### Tier 0: UI Foundation (Current - Complete First)

**Phase 0.5: Obsidian-Inspired UI Redesign (4-5 days remaining)** 🚧 **IN PROGRESS**
- ✅ Day 1 Complete: Layout foundation, three-column grid, ribbon navigation
- ✅ Day 2-3 Complete: Chat system migration with page-specific conversations
- ⏳ Day 4-5: Left sidebar context-specific panels (2-3 days)
- ⏳ Day 6-7: Polish, content migration, empty states (2-3 days)
- **Progress:** 57% complete (Day 1-3 of 7)
- **Blocks:** None - foundational work
- **Detail:** See PHASE0.5_DAY1_COMPLETE.md, SESSION_SUMMARY_JAN26_2026.md, and PHASE_0.5_TO_0.7_ROADMAP.md

**Phase 0.6: Essential Feature Completion (3-5 days)** 📋 **DEFERRED**
- Settings page enhancements
- Knowledge page improvements
- Performance optimization
- **Blocked by:** Phase 0.5
- **Note:** Can be done later as polish sprints

**Phase 0.7: UX Refinement (3-5 days)** 📋 **DEFERRED**
- Micro-interactions and animations
- Command palette (Cmd+K)
- Keyboard shortcuts
- Onboarding flow
- **Blocked by:** Phase 0.6
- **Note:** Can be done later as polish sprints

---

### Tier 1: Core Intelligence (Do After 0.5, 13-16 weeks)

Build in development mode (no signed app needed):

**1. Phase 1.5:** Domain Configuration (6 days) ✅ **COMPLETE (Jan 25)**
- User-definable domains (not hardcoded)
- Zero-config quick start + custom domain paths
- 6 templates, smart recommendations
- Foundation for all other phases

**2. Phase 13a:** Pattern Learning Core (16 days) ✅ **COMPLETE (Jan 25)**
- Activated dormant system (445 lines)
- 4 pattern types: query, code, conceptual, workflow
- Compression and storage system

**3. Phase 2a:** RAG Optimization (3 days) ✅ **COMPLETE (Jan 28)**
- Metadata tracking for RAG queries
- Performance improvements
- Better relevance filtering

**4. Phase 2b:** Pattern Compression (2 days) ✅ **COMPLETE (Jan 28)**
- Conversation compression system
- Token savings and context management
- Integration with pattern learning

**5. Phase 11c:** Compression UI (1 day) ✅ **COMPLETE (Jan 28)**
- Settings UI for compression
- Statistics dashboard
- User controls

**6. Phase 14:** Mental Models System (5 days) ✅ **COMPLETE (Jan 29)**
- Three-tier activation (Domain + Page + Persona)
- 12 default models across 4 tiers
- Template system, CRUD UI, per-conversation override
- PIL compression (2.3x ratio)
- REST API with 7 endpoints
- **Foundation for Phase 22 (Teaching Mode)**

**7. Phase 16:** Native Notes Frontend (1 day) ✅ **COMPLETE (Jan 26)**
- Beautiful notes browser with file tree
- Wiki-links, backlinks, auto-save
- Quick switcher, drag-and-drop

**8. Phase 21:** Knowledge Base Deduplication (2-3 days) ✅ **COMPLETE (Jan 28)**
- Semantic similarity detection before note creation
- "Similar notes found" warning UI
- Three workflows: append, create with links, or create anyway
- Prevents knowledge fragmentation

**9. Phase 22:** Teaching Mode (2-3 days) 📋 **READY TO START**
- **Phase 14 dependency satisfied ✅**
- Specialized "Teaching Mode" mental model
- Socratic pedagogy integration
- Mode switcher UI

**10. Phase 12a:** Knowledge Graph - Basic (5-7 days) 📋 **PLANNED**
- Interactive Cytoscape.js graph
- 5 node types, 4 edge types

**11. Phase 12b:** Knowledge Graph - Reasoning Transparency (1-2 weeks) ⭐ **ENHANCED**
- Edge confidence scores (0.0-1.0)
- Multi-factor analysis (semantic, keyword, temporal, user behavior)
- "Why this connection?" modal UI
- Connection pattern learning

**12. Phase 11:** Multi-Model + Intelligent Routing (10-14 days) ⭐ **ENHANCED**
- Three-layer confidence system
- Adaptive thresholds, meta-query generation
- Token budget management, draft notes queue

**13. Phase 13b:** Pattern Learning UI (7 days)
- Visual pattern browser
- Manual pattern creation
- Pattern editing and management

**14. Phase 15:** MCP Server Integration (5-7 days)
- Model Context Protocol support
- External tool integration
- **Depends on:** Phases 13a ✅, 14 ✅

**15. Phase 16c:** Polly Enhancements (5-7 days) ⭐ **NEW**
- AI note creation, domain auto-tagging
- Proactive connection suggestions
- Auto-organization mode
- Draft notes review queue

**10. Phase 15:** MCP Server Integration (5-7 days)
- Expose Polly to OpenCode/Cursor/Claude Desktop
- Zero fork maintenance
- Enhanced with patterns & mental models

**11. Phase 17:** Code Workspace (3 weeks) ⭐ **NEW**
- Integrated development environment
- 9 languages, terminal, Git UI
- Context-aware chat panel

### Tier 2: Packaging & Permissions (After Tier 1, 1 week)

Do when features are stable and ready for signed app:

**1. App Signing/Notarization** (2-3 days)
- Build signed macOS app bundle

**2. Phase 9:** macOS Permissions (2-3 days)
- Enable Calendar, Reminders, FileSystem integrations

### Tier 3: Polish & Autonomy Awareness (After Tier 2, 2-3 weeks)

Build user-facing polish and data autonomy:

**1. Phase 18:** Onboarding & Progressive Teaching (1-2 weeks) ⭐ **NEW**
- First-run wizard (zero-config vs. custom domains)
- Progressive feature revelation
- Autonomy dashboard (5 metrics)
- Adaptive tutorial system

**2. Phase 19:** Data Autonomy & Export (5-7 days) ⭐ **NEW**
- Knowledge graph export (JSON, GraphML, CSV)
- Notes export (Markdown, JSON, HTML)
- Self-hosted setup guides (Docker, manual, K8s)
- Full offline mode
- Import/restore with rollback

### Tier 4: Advanced Communication (After Tier 2, 2-3 weeks)

Optional Jace.ai-like features with progressive autonomy:

**1. Phase 20a:** Email Intelligence (1 week) ⭐ **NEW**
- IMAP integration (Gmail, Outlook, iCloud)
- Email categorization and smart summaries
- Action item extraction
- Noise filtering
- Privacy-first (local processing default)

**2. Phase 20b:** Calendar & Action Items (1 week) ⭐ **NEW**
- Meeting analysis and pre-meeting context
- Action item extraction from emails/meetings
- Calendar intelligence (prep reminders, conflicts)
- Meeting notes integration

**3. Phase 20c:** Communication Progressive Autonomy (3-5 days) ⭐ **NEW**
- Pattern → local rule conversion
- Communication autonomy dashboard
- Graduated independence (AI → rules)
- Privacy report (local vs. cloud processing)

---

## Detailed Phase Breakdown

### ✅ **Phases 1-5: COMPLETE** (Foundation is solid)

#### Phase 1: UI Foundation
- **Status:** ✅ Complete
- **What Works:** Tabbed navigation, integration cards, brutalist styling
- **Document:** `PHASE1_TESTING.md`

#### Phase 2: GitHub OAuth & Credentials
- **Status:** ✅ Complete
- **What Works:** OAuth flow, Keychain storage, persistent connection
- **Documents:** `PHASE2_SETUP.md`, `PHASE2_FIXED.md`

#### Phase 3: Obsidian Integration
- **Status:** ✅ Complete (95% - minor UI testing remains)
- **What Works:** Folder/tag suggestions, related notes, conversation-to-note, templates
- **Current Index:** 3,508 chunks from 75 files
- **Documents:** `PHASE3_COMPLETE_SUMMARY.md`, `PHASE3_UI_TESTING.md`

#### Phase 4: Multi-Conversation System
- **Status:** ✅ Complete
- **What Works:** 6 categories, star/pin, auto-cleanup, LLM auto-titling, 500 conversation limit
- **Current:** 1 conversation in database
- **Document:** Fully documented in `MASTER_ROADMAP.md` (lines 217-365)

#### Phase 5: Backend Integration Framework
- **Status:** ✅ Complete
- **What Works:** Base integration classes, state persistence, GitHub & Context7 integrations
- **Current Index:** 17 GitHub repos synced
- **Documents:** `PHASE5_COMPLETE.md`, `PHASE5_TEST.md`

---

### 🎨 **Phase 0.5: UI Design System Foundation** - **TIER 0 (OPTIONAL)**

**Status:** Planning Complete  
**Priority:** 🟢 **MEDIUM (Optional but recommended)**  
**Effort:** 4-6 days  
**Document:** `PHASE0.5_UI_DESIGN_SYSTEM.md`

#### Why Optional But Recommended

**Establishes professional UI patterns** before building 13-16 weeks of new features (Tier 1).

**Benefits:**
- Consistency by default (all new UIs use same components)
- Avoids massive rework later
- Professional aesthetic from start
- Guides future development

**Why can wait:**
- Brutalist design is functional
- Can apply incrementally during Tier 1
- Not blocking any features

**Recommendation:** Do in parallel with Phase 1.5 (different files, minimal conflicts).

#### What It Does

**Framework Setup:**
- Install Shadcn/ui + Tailwind CSS
- Configure theme (colors, fonts, dark mode)
- Set up CSS variables for theming

**Component Library:**
- Install 12+ Shadcn components (button, card, input, dialog, tabs, etc.)
- Build 4+ custom Polly components (IntegrationCard, ChatMessage, StatusIndicator, EmptyState)
- Document all components in DESIGN_SYSTEM.md

**Design System Documentation:**
- Color system (primary blue, accent orange, slate neutrals)
- Typography (Inter UI, JetBrains Mono code)
- Spacing guidelines (4px base unit)
- Usage guidelines and patterns

**Update High-Visibility Components:**
- Navigation/header
- Integration cards (Phase 5)
- Settings panel
- Tab navigation

**Storage:** `DESIGN_SYSTEM.md`, `src/components/ui/`

#### Implementation

**Day 1:** Framework setup & configuration (Shadcn/ui + Tailwind)  
**Day 2:** Core component library - Part 1 (install Shadcn components)  
**Day 3:** Core component library - Part 2 (build custom Polly components)  
**Day 4:** Document design system (DESIGN_SYSTEM.md)  
**Day 5:** Update high-visibility components  
**Day 6:** Polish & testing (cross-browser, accessibility, dark mode)  

#### Success Criteria

- ✅ Shadcn/ui + Tailwind installed and configured
- ✅ Dark mode works perfectly
- ✅ 12+ Shadcn components + 4+ custom components
- ✅ DESIGN_SYSTEM.md is complete
- ✅ Navigation, integration cards, settings updated
- ✅ Ready to build Phases 1.5-17 with consistent UI

#### UI Polish Sprint (After Tier 1)

After completing Tier 1, spend **1 week** updating remaining Phases 1-5 UIs:
- Chat interface (Phase 4) → `ChatMessage` component
- Conversation list → consistent styling
- All modals → `Dialog` component
- Forms → consistent inputs

**Result:** Professional, consistent UI before packaging (Tier 2) and onboarding (Tier 3).

---

### 🆕 **Phase 1.5: Domain Configuration System** - **FOUNDATION**

**Status:** Planning Complete  
**Priority:** 🟡 **HIGH (Start of Tier 1)**  
**Effort:** 5 days  
**Document:** `PHASE1.5_DOMAIN_CONFIGURATION.md`

#### Why Foundation

**Enables All Other Phases:** Every Tier 1 phase depends on the domain system established here.

- Phase 11: Domain-aware confidence scoring
- Phase 13: Domain-based pattern learning
- Phase 14: Domain-tagged mental models
- Phase 16: Domain folder structure for notes
- Phase 17: Domain context in code workspace

#### What It Does

**User-Definable Domains:**
- Create custom knowledge organization (not hardcoded)
- 6 domain templates: Software Dev, Research, Creative Writing, Personal, Academic, Polly Creator
- Properties: name, description, color, icon, folderPath, ragWeight (0-1), autoTagRules[]

**Smart Recommendations:**
- AI suggests auto-tag keywords based on domain purpose
- RAG weight optimization for retrieval priority
- Domain mapping from existing vault structure
- Obsidian vault analysis and clustering

**First-Run Experience:**
- Guided wizard for setup
- Template selection
- Vault import with domain suggestions
- Behavioral learning improves over time

**Storage:** `~/.polly/domains.json`

**Folder Structure:**
- Numbered by default: `01-Concepts/`, `02-Patterns/` (user-configurable)
- Special folders: `_Drafts/` (review queue), `_Templates/` (note templates)

#### Implementation

**Day 1-2:** Core domain system
- Domain data model (JSON schema)
- Domain manager class (CRUD operations)
- Validation and persistence

**Day 3:** Smart recommendations
- AI analysis of domain purpose → auto-tag suggestions
- RAG weight calculator based on query patterns
- Domain relationship mapper

**Day 4:** First-run wizard
- Template selection UI
- Obsidian vault analyzer
- Domain creation flow

**Day 5:** Settings integration
- Domain management panel
- Edit/delete/reorder domains
- Testing & polish

#### Success Criteria

- ✅ Users can define custom domains
- ✅ 6 templates available and functional
- ✅ AI recommendations are helpful and accurate
- ✅ First-run wizard is intuitive
- ✅ All other phases can access domain configuration

---

### ⚠️ **Phase 9: macOS Permission Handling** - **TIER 2 (After Intelligence)**

**Status:** Planning Complete  
**Priority:** Medium (do after Tier 1)  
**Effort:** 2-3 days  
**Dependencies:** Requires signed app bundle  
**Document:** See `MASTER_ROADMAP.md` (Phase 9 section)

#### Why Critical

**Blocks 3 Complete Integrations:**

1. **Calendar** (`/integrations/calendar.py` - 200+ lines)
   - EventKit integration built and tested
   - Requires Calendar permission
   - Enables: Event search, calendar context in conversations

2. **Reminders** (`/integrations/reminders.py` - 150+ lines)
   - EventKit integration built and tested
   - Requires Reminders permission
   - Enables: Reminder tracking, task management

3. **File System** (`/integrations/filesystem.py` + `filesystem_llm.py` - 900+ lines)
   - Full file operations built and tested
   - Requires Full Disk Access
   - Enables: File organization, Finder tags, natural language file operations

**Total:** ~1,400 lines of working code waiting for permissions

#### What Needs to Be Built

- Permission status checking (Calendar, Reminders, Full Disk Access)
- Permission request flow (EventKit system dialog)
- Full Disk Access guidance UI (open System Settings)
- Integration enable/disable based on permissions
- Graceful error handling

#### Implementation

**Day 1:** Permission Manager backend (`/integrations/permissions.py`)  
**Day 2:** API endpoints and server integration  
**Day 3:** Frontend UI and testing

#### Success Criteria

- ✅ Calendar permission grantable through Polly UI
- ✅ Reminders permission grantable through Polly UI
- ✅ Full Disk Access guided setup works
- ✅ All 3 integrations auto-enable when permissions granted

#### Why Highest ROI

- **3 major features unlocked**
- **Only 2-3 days of work**
- **Code already complete and tested**
- **High user value (calendar, reminders, files)**

---

### 🟡 **Phases 11-17: Intelligence Enhancements** - **HIGH PRIORITY**

All planning complete, ready to implement after Phase 1.5.

#### Phase 11: Multi-Model + Intelligent Routing (ENHANCED)

**Status:** Planning Complete  
**Priority:** High  
**Effort:** 10-14 days (enhanced from original 7-10 days)  
**Document:** `PHASE11_MULTI_MODEL_ENHANCED.md`

**What It Does:**
- **Original Phase 11:** Basic multi-model selection (manual switching)
- **Enhanced Phase 11:** Intelligent confidence-based routing + knowledge gap filling

**Three-Layer Confidence System:**
1. **Pre-flight check (RAG quality):** <40% → skip local, go cloud
2. **Output analysis (response quality):** <60% → generate meta-query for cloud
3. **Historical learning (patterns):** Adaptive thresholds (60%/70% → 40%/60%)

**Key Features:**
- Meta-query generation: Cloud generates comprehensive notes when local knowledge insufficient
- Token budget management: Track usage across providers (Anthropic, OpenAI, Copilot)
- Draft notes review queue: All AI-generated notes go to `~/.polly/notes/_Drafts/` for user review
- Adaptive learning: System learns when to trust local models over time
- Transparency: Show confidence scores and routing decisions

**Storage:** `~/.polly/token_usage.json` (monthly rollover)

**Why Enhanced:**
- Saves money by maximizing local model usage
- Automatically fills knowledge gaps
- Prevents low-quality content in knowledge base
- Learns optimal thresholds over time

**Timeline:**
- Week 1 (5 days): Three-layer confidence system, pre-flight/output analysis
- Week 2 (5-9 days): Token management, draft notes queue, adaptive thresholds, UI/testing

#### Phase 12: Knowledge Graph Visualization (ENHANCED)

**Status:** Planning Complete  
**Priority:** High  
**Effort:** 2.5-3.5 weeks (enhanced from original 5-7 days)  
**Document:** `PHASE12_KNOWLEDGE_GRAPH.md`

**What It Does:**
- Interactive Cytoscape.js graph of all knowledge
- 5 node types: notes, code, concepts, conversations, repos
- 4 edge types: links, imports, similarity, relationships
- "Chat with Context" action
- **NEW: Reasoning Transparency** (1-2 weeks additional)

**Two Sub-Phases:**

**Phase 12a: Basic Graph (5-7 days)**
- Interactive Cytoscape.js visualization
- 5 node types, 4 edge types
- Basic filters and search
- "Chat with Context" action

**Phase 12b: Reasoning Transparency (1-2 weeks)**
- **Edge Confidence Scores:** Every connection has 0.0-1.0 confidence
- **Multi-Factor Analysis:**
  - Semantic similarity (0-1)
  - Keyword overlap (0-1)
  - Temporal proximity (0-1)
  - User behavior (clicks, navigation) (0-1)
  - Weighted composite score
- **"Why this connection?" Modal:**
  - Shows all 4 factors with individual scores
  - Explains why Polly thinks these nodes are related
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

**Storage:** Edge metadata includes `confidence`, `factors`, `created_at`, `user_feedback`

**Why High Priority:**
- Reveals unexpected connections in knowledge
- **Shows Polly's reasoning (transparency = trust)**
- Visualizes Polly's understanding
- Aligns with systems thinking philosophy
- User can understand and improve connection quality

**Marketing Alignment:**
- "See how you think"
- "Transparent reasoning, not black box"
- "Polly shows its work"

#### Phase 13a: Pattern Learning System - Core Intelligence Layer

**Status:** Planning Complete  
**Priority:** Tier 1 (High Priority)  
**Effort:** 30 days (16 days implementation + 14 days documentation)  
**Document:** `PHASE13A_PATTERN_LEARNING_CORE.md` (~3,200 lines)

**What It Does:**
- Transforms pattern learning into RAG navigation system (30-70% faster retrieval)
- 3 pattern types: Query→Chunk, Domain→Collection, Conceptual (refined)
- spaCy-based concept extraction (500+ technical terms, 700+ stopwords)
- Pattern quality controls: automatic pruning, decay, usefulness tracking
- 9 ancillary use cases fully specified (implemented in respective phases)

**Why Tier 1:**
- RAG efficiency critical as knowledge base scales (4K → 40K+ docs)
- Foundation for domain detection (Phase 1.5), autonomous tasks (Phase 3), routing (Phase 11)
- "Knowledge that compounds" - system gets smarter over time

**Key Deliverables:**
- Core pattern system (Query→Chunk, Domain→Collection, Conceptual)
- Pattern APIs for other systems
- RAG timing metrics (permanently enabled)
- Full specifications for 9 ancillary integrations

**Dependencies:**
- Phase 1.5 domain keywords (optional, enhances quality)

**Provides To:**
- Phase 1.5: Domain auto-detection enhancement
- Phase 3: Autonomous workflow learning
- Phase 6, 10, 11, 12, 18, 20: Various pattern-driven features

---

#### Phase 13b: Pattern Learning UI & Testing

**Status:** Planning Complete  
**Priority:** Tier 1 (High Priority)  
**Effort:** 7 days  
**Document:** `PHASE13B_PATTERN_LEARNING_UI.md` (~960 lines)

**What It Does:**
- Learning frequency controls (smarter triggers)
- Pattern visualization UI (browser with search/filter/sort)
- RAG efficiency metrics dashboard
- Pattern management interface (delete, export, clear)
- Comprehensive testing suite

**Why Tier 1:**
- Provides visibility and control over learned patterns
- Validates RAG speedup claims (testing)
- User trust through transparency

**Key Deliverables:**
- Pattern browser UI component
- Metrics dashboard with real-time stats
- Pattern management actions
- RAG speed benchmark tests

**Dependencies:**
- Phase 13a must be complete

---
**What It Does:**
- Activates dormant pattern learning system (445 lines exist, never turned on)
- 4 pattern types: query, code, conceptual, workflow
- Learns organizational habits, coding styles, mental models
- Suggests patterns proactively

**Why High Priority:**
- System is already built but not working (storage never created)
- Enables Polly to learn from all interactions
- Foundation for personalization

#### Phase 14: Mental Models System

**Status:** ✅ Complete (January 29, 2026)  
**Priority:** High  
**Actual Effort:** 5 days  
**Document:** `PHASE14_MENTAL_MODELS.md`, `PHASE14_IMPLEMENTATION_COMPLETE.md`

**What Was Built:**
- Three-tier activation system (Domain + Page + Persona)
- 12 default mental models across 4 tiers (expanded from 5)
- Template system with 5 pre-built templates
- Settings UI with full CRUD operations
- Per-conversation override via context menu
- PIL compression achieving 2.3x ratio
- REST API with 7 endpoints
- Complete user documentation

**Key Features:**
- **Automatic Activation:** Top 3-5 models per query based on context
- **Compression:** Models compress to PIL format saving ~60% tokens
- **Customization:** Unlimited custom models with templates
- **Flexibility:** Per-conversation manual override
- **Future-Proof:** Pre-configured for Phase 20 (Mail/Calendar) and Phase 22 (Teaching Mode)

**Test Results:**
- 48/51 tests passing (94%)
- Integration verified end-to-end
- Minor failures are scoring variations (non-critical)

**Why This Was High Priority:**
- Aligns with project philosophy (infinite games, constraint as meaning)
- High user value (personalized reasoning)
- Foundation for Phase 22 (Teaching Mode) ✅ Now unblocked
- Quick to implement (5 days as estimated)

**Total Code:** ~3,200 lines (1,700 backend + 1,500 frontend)

---

#### Phase 16: Native Note Management (NEW - 3 SUB-PHASES)

**Status:** Planning Complete  
**Priority:** High  
**Effort:** 3.5-4 weeks total  
**Document:** `PHASE16_NATIVE_NOTES.md`

**What It Does:**
- Replaces Obsidian with native note management inside Polly
- Monaco editor with full markdown support
- **One-time import** from Obsidian (NOT bidirectional sync)
- All note features users love, plus Polly enhancements

**Three Sub-Phases:**

**Phase 16a: Core Note Management (2 weeks)**
- Monaco editor with syntax highlighting
- File operations (create, rename, delete, move)
- Folder structure using Phase 1.5 domains
- Full-text search
- One-time Obsidian import
- Live markdown preview

**Phase 16b: Power Features (1-2 weeks)**
- Wiki-links `[[Note Name]]` with autocomplete
- Backlinks panel (shows notes linking to current)
- Tag system `#tag` with browser
- Quick switcher (Cmd+O fuzzy search)
- Frontmatter editing
- Templates with variables

**Phase 16c: Polly Enhancements (3-5 days)**
- Domain auto-tagging using Phase 1.5 rules
- AI note creation from conversations ("Save to Notes")
- Draft notes review queue integration (Phase 11)
- Direct graph → editor navigation (Phase 12)
- Code → Note creation (Phase 17)

**Storage:** `~/.polly/notes/` with domain folders, `_Drafts/`, `_Templates/`, `attachments/`

**Important Decision:** One-time Obsidian import only (not bidirectional). Users migrate to Polly, simplifying architecture.

**Why High Priority:**
- Makes Polly fully self-contained (no external dependencies)
- Seamless integration with all Polly features
- AI-powered note creation unique to Polly
- Single app for everything

---

#### Phase 17: Code Workspace (NEW)

**Status:** Planning Complete  
**Priority:** High  
**Effort:** 3 weeks  
**Document:** `PHASE17_CODE_WORKSPACE.md`

**What It Does:**
- Integrated development environment for 80% of coding tasks
- Monaco editor with 9 built-in languages: Python, JavaScript, TypeScript, C, C++, C#, Lua, Rust, Go
- Integrated terminal (xterm.js)
- Git operations UI (stage, commit, push, pull, visual diff)
- Context-aware chat panel (auto-includes current file + related files from Phase 12 graph)

**Three Weeks:**

**Week 1 (5-7 days): Core Editor**
- Monaco editor with 9 languages
- File tree with Git status indicators
- Integrated terminal
- Git operations UI (visual diff, stage/commit)

**Week 2 (5-7 days): Polly Integration**
- Chat panel with full code context
- Model routing: Copilot (completion), Claude (refactoring), Local (explanations)
- RAG-powered code search (GitHub repos + local + notes)
- Language/library support via Context7 (downloadable docs)

**Week 3 (5-7 days): Advanced Features**
- Code actions: "Explain this", "Find similar patterns", "Refactor using mental model", "Save as note"
- Multi-file context (auto-include related files from graph, up to 8k tokens)
- Pattern-aware suggestions (Phase 13 learned patterns as inline completions)
- Code → Note creation (generates explanation + code block + domain suggestion)

**80/20 Philosophy:**
- 80% in Polly: Quick edits, exploration, learning, prototyping
- 20% in external IDE (via Phase 15 MCP): Debugging, extensions, profiling

**Why High Priority:**
- Full context always available (knowledge graph + patterns + mental models)
- Seamless code → note workflow
- Learning-focused (not just editing)
- Integration with all Tier 1 phases

---

#### Phase 18: Onboarding & Progressive Teaching (NEW - TIER 3)

**Status:** Planning Complete  
**Priority:** Medium (Tier 3)  
**Effort:** 1-2 weeks  
**Document:** `PHASE18_ONBOARDING.md`

**What It Does:**
- First-run wizard with dual-path choice (zero-config vs. custom domains)
- Progressive feature revelation system
- Adaptive tutorial system that fades with mastery
- Autonomy dashboard showing 5 core metrics
- Usage pattern detection

**First-Run Wizard:**
- **Path 1: Zero-Config Quick Start** (for new users)
  - Auto-creates Work/Personal/Learning domains
  - Auto-filing intelligence based on content analysis
  - Progressive domain suggestions after 25-50 notes
  - Can upgrade to custom domains anytime

- **Path 2: Custom Domains** (for power users)
  - Full Phase 1.5 domain configuration
  - Template selection and customization
  - Obsidian vault import with domain mapping

**Progressive Feature Revelation:**
- Week 1: Core chat interface, basic RAG
- Week 2: Domain auto-tagging, pattern learning introduction
- Week 3: Mental models toggle, knowledge graph preview
- Adaptive: Accelerates if user demonstrates mastery

**Autonomy Dashboard:**
Five core metrics showing progressive learning:
1. **Token Usage Trend:** Local vs. cloud ratio over time (target: increase local)
2. **RAG Hit Rate:** % of queries answered from local knowledge (target: >70%)
3. **Pattern Learning Progress:** # of learned patterns per domain
4. **Time Since Last Cloud Query:** Per topic/domain (shows growing independence)
5. **Knowledge Compound Score:** Rolling 30-day metric of knowledge accumulation

**Tutorial System:**
- Context-sensitive tooltips (fade after 3 dismissals)
- Interactive walkthroughs for complex features
- Video tutorials (optional, links to external)
- Help panel with searchable docs

**Implementation:**
- Days 1-3: First-run wizard with dual-path choice
- Days 4-6: Progressive feature revelation system
- Days 7-9: Autonomy dashboard (5 metrics)
- Days 10-12: Tutorial system and help panel

**Why Tier 3:**
- Improves user adoption and reduces learning curve
- Shows progressive autonomy (core marketing message)
- Enables zero-config quick start for casual users
- Builds confidence in Polly's learning capabilities

**Marketing Alignment:**
- "Polly teaches you as you teach Polly"
- "Progressive autonomy, not permanent dependency"
- "Start simple, grow sophisticated"

---

#### Phase 19: Data Autonomy & Export (NEW - TIER 3)

**Status:** Planning Complete  
**Priority:** Medium (Tier 3)  
**Effort:** 5-7 days  
**Document:** `PHASE19_DATA_AUTONOMY.md`

**What It Does:**
- Complete data export (knowledge graph, notes, conversations, patterns)
- Self-hosted server setup guides
- Full offline mode with core functionality
- Import/restore system with rollback safety
- Zero platform lock-in

**Export System:**

**1. Knowledge Graph Export:**
- JSON format (full data, programmatic access)
- GraphML format (Gephi, yEd, Cytoscape)
- CSV format (spreadsheets, custom analysis)
- Includes nodes, edges, metadata, timestamps

**2. Notes Export:**
- Markdown files (portable, human-readable)
- JSON format (with frontmatter, metadata, tags)
- HTML format (standalone browsing)
- Preserves folder structure and wiki-links

**3. Full System Backup:**
- Complete `.polly/` directory archive
- Includes: domains.json, patterns.json, mental_models/, conversations/
- Verification system (checksums, integrity validation)
- One-click restore with rollback safety

**Self-Hosted Setup:**

**Option 1: Docker Compose (Recommended)**
- Pre-configured docker-compose.yml
- Includes Qdrant, Ollama, Polly server
- SSL/TLS via Caddy or Traefik
- Tailscale for secure remote access

**Option 2: Manual Setup**
- Step-by-step installation guide
- systemd service files
- Nginx reverse proxy config
- Firewall rules and security hardening

**Option 3: Kubernetes**
- Helm charts for production deployment
- Horizontal scaling config
- Persistent volume claims
- Ingress controller setup

**Offline Mode:**
- Full core functionality without internet
- Local models only (Ollama)
- All features except cloud model fallback
- Sync when connection restored

**Import/Restore:**
- Import knowledge graph from JSON/GraphML
- Import notes from Markdown/Obsidian vault
- Full system restore from backup
- Merge strategy (replace vs. merge vs. skip)
- Rollback to previous state if import fails

**Implementation:**
- Days 1-2: Export system (knowledge graph, notes, conversations)
- Days 3-4: Self-hosted setup guides and Docker Compose
- Day 5: Offline mode implementation
- Days 6-7: Import/restore system with rollback

**Why Tier 3:**
- Core differentiation: "Your data. Your freedom."
- Anti-platform-lock-in positioning
- Privacy-conscious user appeal
- Professional user requirement (data sovereignty)

**Marketing Alignment:**
- "Your data. Your freedom."
- "Build capability, don't rent it"
- "Own your intelligence"
- Competitive advantage vs. ChatGPT/Claude (cloud-locked)

---

#### Phase 20: Intelligent Communication (NEW - TIER 4, 3 SUB-PHASES)

**Status:** Planning Complete  
**Priority:** Low (Tier 4)  
**Effort:** 2-3 weeks total  
**Document:** `PHASE20_INTELLIGENT_COMMUNICATION.md`

**What It Does:**
- Email and calendar intelligence with privacy-first architecture
- Progressive autonomy: Patterns become local rules (not permanent AI dependency)
- Communication autonomy dashboard
- Competitive positioning: "Jace.ai for people who want to own their systems"

**Three Sub-Phases:**

---

**Phase 20a: Email Intelligence (1 week)**

**Email Parsing & Analysis:**
- IMAP integration (Gmail, Outlook, iCloud)
- Local processing by default (Ollama models)
- Cloud fallback only for complex analysis
- No email content sent to cloud unless user explicitly requests

**Email Categorization:**
- 6 categories: Important, FYI, Social, Newsletters, Spam, Needs Response
- Confidence scoring (0.0-1.0)
- User feedback loop improves accuracy
- Pattern learning: "All emails from X go to Y"

**Smart Summaries:**
- Thread summarization (long conversations)
- Action item extraction
- Key decision highlights
- Attachment analysis (file type, relevance)

**Noise Filtering:**
- Newsletter consolidation (daily digest)
- Social media notification grouping
- Promotional email suppression
- VIP sender priority

**Implementation:**
- Days 1-2: IMAP integration, email parsing
- Days 3-4: Categorization system with confidence scoring
- Day 5: Smart summaries and action extraction
- Days 6-7: Noise filtering and testing

**Storage:** `~/.polly/email/` (metadata only, no full email storage)

---

**Phase 20b: Calendar & Action Items (1 week)**

**Meeting Analysis:**
- EventKit + Google Calendar integration
- Pre-meeting context generation (who, what, why, related notes)
- Meeting participant lookup (email → GitHub profile → past interactions)
- Suggested talking points from knowledge graph

**Action Item Extraction:**
- Parse email for commitments ("I'll send you X by Friday")
- Extract meeting action items from context
- Create draft tasks in Reminders.app
- Deadline tracking with smart notifications

**Calendar Intelligence:**
- Meeting prep reminders (15 min before, with context)
- Travel time calculation (using macOS Maps)
- Conflict detection and suggestions
- Time blocking recommendations

**Meeting Notes:**
- Auto-create note in domain (Phase 16 integration)
- Pre-populate with attendees, agenda, related context
- Post-meeting: "What did we decide?" prompt
- Link to action items and follow-ups

**Implementation:**
- Days 1-2: Calendar integration and meeting analysis
- Days 3-4: Action item extraction and task creation
- Day 5: Calendar intelligence (prep, conflicts, time blocking)
- Days 6-7: Meeting notes integration and testing

---

**Phase 20c: Communication Progressive Autonomy (3-5 days)**

**Pattern → Local Rule Conversion:**
- "Always categorize emails from sarah@example.com as Important" → local rule (no AI needed)
- "Monday morning meetings need 30-min prep time" → calendar rule
- "Project X emails should link to note Project_X.md" → auto-filing rule
- After 5-10 pattern repetitions, suggest converting to local rule

**Communication Autonomy Dashboard:**
- % of emails handled by local rules (vs. AI analysis)
- % of meetings with auto-generated context
- Action item completion rate
- Time saved (estimated, based on automation)

**Graduated Independence:**
- Week 1: AI analyzes everything
- Week 2-3: Patterns emerge, AI suggests rules
- Week 4+: Most communication handled by rules, AI only for edge cases

**Privacy Report:**
- Show exactly what data was sent to cloud (if any)
- Token usage for email/calendar features
- Local-first percentage (target: >90%)

**Implementation:**
- Days 1-2: Pattern → rule conversion system
- Days 3-4: Communication autonomy dashboard
- Day 5: Privacy report and testing

---

**Why Tier 4 (Not Tier 1):**
- More complex integrations (email, calendar require permissions)
- Jace.ai-like features (not core differentiator yet)
- Requires Phase 9 (permissions) to be complete
- Nice-to-have vs. must-have

**Why Different from Jace.ai:**
- **Jace.ai:** Permanent AI dependency (always processes every email)
- **Polly:** Progressive autonomy (learns patterns → creates local rules → becomes independent)
- **Jace.ai:** Cloud-only processing
- **Polly:** Local-first, cloud fallback only when needed
- **Jace.ai:** Opaque reasoning
- **Polly:** Transparent pattern learning, user controls rules

**Marketing Alignment:**
- "Build capability, don't rent it"
- "Progressive autonomy, not permanent dependency"
- "Privacy-first by design"
- "Jace.ai for people who want to own their systems"

**Target Users:**
- Professionals drowning in email
- People who want email intelligence WITHOUT cloud dependency
- Users with sensitive communications (lawyers, healthcare, finance)
- ADHD users who struggle with email overload

**Dependencies:**
- Phase 9 (macOS Permissions) - Must be complete first
- Phase 11 (Multi-Model Routing) - For local-first processing
- Phase 13 (Pattern Learning) - For pattern → rule conversion

---

### ⏸️ **Phases 6-8: Optional Enhancements** - **LOW PRIORITY**

These improve existing features but aren't essential.

#### Phase 6: Enhanced GitHub Integration

**Status:** Not Started  
**Priority:** Low  
**Effort:** 3-5 days  
**Document:** `PHASE6_GITHUB_ENHANCEMENTS.md`

**What It Adds:**
- Incremental sync (faster)
- Parallel README fetching (10x speed)
- Code search within repos
- Commit history indexing

**Why Optional:** Current GitHub integration already works well

#### Phase 7: Advanced Calendar Features

**Status:** Not Started  
**Priority:** Low  
**Effort:** 5-7 days  
**Dependencies:** Phase 9 (must be done first)  
**Document:** `PHASE7_CALENDAR_FEATURES.md`

**What It Adds:**
- Multi-account support (iCloud + Google simultaneously)
- Natural language queries ("What meetings do I have tomorrow?")
- Event creation from chat
- Meeting notes integration with Obsidian

**Why Optional:** Basic calendar (Phase 9) provides core functionality

#### Phase 8: New Integrations

**Status:** Planning  
**Priority:** Low  
**Effort:** Varies (1-2 weeks per integration)  
**Document:** `PHASE8_NEW_INTEGRATIONS.md`

**Options:**
- Email (IMAP/Gmail API)
- Slack
- Browser History
- Apple Notes
- Photos
- Music

**Why Optional:** Current integrations cover most needs

---

### 📋 **Phase 10: iOS Mobile App** - **FUTURE**

**Status:** Planning  
**Priority:** Low  
**Effort:** 3-4 weeks  
**Document:** `PHASE10_IOS_MOBILE.md`

**What It Does:**
- SwiftUI iOS companion app
- Sync via Tailscale
- Quick capture (voice, photos, text)
- Conversation access on the go
- Voice input/output

**Why Future:**
- Desktop is primary interface
- Mobile is nice-to-have
- Significant effort (3-4 weeks)
- Focus on desktop features first

---

## Current Codebase Health

### What's Working Well

**Integrations:**
- ✅ Obsidian (3,508 chunks indexed)
- ✅ GitHub (17 repos synced)
- ✅ Context7 (React library + more)
- ⏸️ Calendar (built, needs Phase 9)
- ⏸️ Reminders (built, needs Phase 9)
- ⏸️ FileSystem (built, needs Phase 9)

**Conversation System:**
- ✅ 6 categories (5 domains + uncategorized)
- ✅ Star/pin protection
- ✅ Auto-cleanup (60-day retention)
- ✅ LLM auto-titling
- ✅ Search & filtering

**RAG System:**
- ✅ ~4,000+ searchable documents
- ✅ Semantic search working
- ✅ Multiple collections (Obsidian, code, GitHub)

**Router:**
- ✅ 3 providers (Ollama, Anthropic, OpenAI)
- ✅ AUTO/LOCAL/CLOUD modes
- ⚠️ Simplistic routing (Phase 11 will improve)

### What Needs Work

**Pattern Learning:**
- ⚠️ System exists (445 lines) but dormant
- ❌ Storage never gets created
- ❌ Patterns don't persist
- **Fix:** Phase 13 (1-2 weeks)

**Permissions:**
- ❌ Can't enable Calendar, Reminders, FileSystem
- ❌ No permission request UI
- **Fix:** Phase 9 (2-3 days) - **Do after Tier 1, requires signed app**

**Model Selection:**
- ⚠️ Only 3 providers
- ⚠️ No confidence-based routing
- ⚠️ No knowledge gap filling
- **Fix:** Phase 11 Enhanced (10-14 days)

**Note Management:**
- ⚠️ Depends on external Obsidian
- ❌ No native note editor
- ❌ No AI note creation
- **Fix:** Phase 16 (3.5-4 weeks)

**Development Environment:**
- ❌ No code workspace
- ❌ Context switching between IDE and Polly
- ❌ No code → note workflow
- **Fix:** Phase 17 (3 weeks)

---

## Dependencies & Blockers

### Current Blockers

**No critical blockers!** All Tier 1 phases can start immediately.

**Phase 1.5 is the foundation** - Should be done first, but not technically blocking (other phases will be less useful without it)

**Phase 9 (Permissions) requirements:**
- Signed app bundle (do after Tier 1 features are stable)
- Blocks: Calendar, Reminders, FileSystem integrations (already built, just disabled)

### Phase Dependencies

```
Phase 1.5 (Domains) ← FOUNDATION
  ├── Recommended first (all other phases benefit)
  ├── Enables: Phase 11 (domain-aware routing)
  ├── Enables: Phase 13 (domain-based patterns)
  ├── Enables: Phase 14 (domain mental models)
  ├── Enables: Phase 16 (domain folder structure)
  └── Enables: Phase 17 (domain code context)

Tier 1 Intelligence Phases (do after Phase 1.5)
  ├── Phase 13: Pattern Learning (requires Phase 1.5 domains)
  ├── Phase 14: Mental Models (requires Phase 1.5 domains)
  ├── Phase 12a: Knowledge Graph Basic (requires Phase 1.5)
  ├── Phase 11: Multi-Model Enhanced (requires Phases 1.5)
  ├── Phase 16a/b/c: Native Notes (requires Phases 1.5, 11 for drafts)
  ├── Phase 12b: Knowledge Graph Enhanced (requires Phases 16, 17)
  ├── Phase 15: MCP Server (enhanced by Phases 13, 14)
  └── Phase 17: Code Workspace (requires all previous Tier 1)

Tier 2 (do after Tier 1 stable)
  ├── App Signing/Notarization
  └── Phase 9: macOS Permissions
        ├── Enables: Calendar
        ├── Enables: Reminders
        ├── Enables: FileSystem
        └── Unblocks: Phase 7 (Advanced Calendar)

Phase 10 (iOS Mobile)
  ├── Should wait for: Tier 1 + Tier 2 complete
  └── Should wait for: Stable desktop app
```

---

## Estimated Timeline

### Option 1: With UI Design System (Recommended)

**Phase 0.5: UI Design System (4-6 days)**
- Can do in parallel with Phase 1.5 or right after
- Establishes professional UI foundation

**Tier 1: Core Intelligence (13-16 weeks)**
- Build all features using design system
- Apply components consistently as you go

**UI Polish Sprint: (1 week)**
- Update remaining Phases 1-5 UIs
- Final consistency pass

**Tier 2: Packaging & Permissions (1 week)**
- App signing + macOS permissions

**Total: 15-18 weeks (with professional UI throughout)**

---

### Option 2: Without UI Design System (Faster start, more rework later)

**Tier 1: Core Intelligence (13-16 weeks)**
- Build with brutalist UI
- Focus on features

**UI Overhaul Sprint: (2-3 weeks)**
- Update ALL UIs at once (more work than Option 1)

**Tier 2: Packaging & Permissions (1 week)**

**Total: 16-20 weeks (but onboarding sees old UI)**

---

### Minimum Viable Start (2-3 weeks)

**Weeks 1-2:**
- Phase 0.5: UI Design System (4-6 days) - OPTIONAL
- Phase 1.5: Domain Configuration (6 days)
- Phase 13: Pattern Learning (1-2 weeks)

**Week 3:**
- Phase 14: Mental Models (3-5 days)

**Result:** Foundation + core intelligence features in place (+ design system if included)

---

### Full Tier 1 Implementation (13-16 weeks)

**Recommended order:**
1. Phase 1.5: Domain Configuration (6 days)
2. Phase 13: Pattern Learning (1-2 weeks)
3. Phase 14: Mental Models (3-5 days)
4. Phase 12a: Knowledge Graph - Basic (5-7 days)
5. Phase 12b: Knowledge Graph - Reasoning Transparency (1-2 weeks)
6. Phase 11: Multi-Model + Intelligent Routing (10-14 days)
7. Phase 16a: Core Note Management (2 weeks)
8. Phase 16b: Power Features (1-2 weeks)
9. Phase 16c: Polly Enhancements (5-7 days)
10. Phase 15: MCP Server (5-7 days)
11. Phase 17: Code Workspace (3 weeks)

**If doing Phase 0.5:** Do in parallel with Phase 1.5 or right after

**Result:** Complete intelligence + knowledge system + development environment

---

### With UI Polish Sprint + Tier 2 (15-18 weeks)

Add after Tier 1:
- UI Polish Sprint (1 week) - Update remaining UIs
- App Signing/Notarization (2-3 days)
- Phase 9: macOS Permissions (2-3 days)

**Result:** Professional UI + all core features + 3 macOS integrations enabled

---

### With Tier 3: Polish & Autonomy (17-21 weeks)

Add Tier 3 after UI Polish Sprint + Tier 2:
- Phase 18: Onboarding & Progressive Teaching (1-2 weeks)
- Phase 19: Data Autonomy & Export (5-7 days)

**Result:** Professional onboarding experience + complete data sovereignty

---

### With Tier 4: Advanced Communication (19-24 weeks)

Add Tier 4 after Tier 2 (can run parallel with Tier 3):
- Phase 20a: Email Intelligence (1 week)
- Phase 20b: Calendar & Action Items (1 week)
- Phase 20c: Communication Progressive Autonomy (3-5 days)

**Result:** Full communication intelligence with privacy-first progressive autonomy

---

### With Optional Enhancements (21-29 weeks)

Add optional phases after core tiers:
- Phase 6: Enhanced GitHub (3-5 days)
- Phase 7: Advanced Calendar (5-7 days)
- Phase 8: Choose 1-2 new integrations (1-2 weeks each)

---

## What To Do Next

### Immediate Next Steps

1. **Read Phase 1.5 document:** `PHASE1.5_DOMAIN_CONFIGURATION.md`
2. **Implement Phase 1.5** (6 days)
   - Foundation for all other Tier 1 phases
   - User-definable domains, zero-config quick start, smart recommendations
3. **Continue with Tier 1 phases:**
   - Recommended order: 13 → 14 → 12a → 12b → 11 → 16a → 16b → 16c → 15 → 17
   - 13-16 weeks of intelligence building
4. **Package and sign app** (Tier 2, after Tier 1 stable)
5. **Implement Phase 9** to enable macOS integrations (Calendar, Reminders, FileSystem)
6. **Polish and autonomy** (Tier 3, optional but recommended)
   - Phase 18: Onboarding experience
   - Phase 19: Data export and self-hosting
7. **Advanced communication** (Tier 4, optional)
   - Phase 20a/b/c: Email and calendar intelligence

### Priority Guidance

**Start with:** Phase 1.5 (foundation - 6 days)  
**Then build:** Tier 1 intelligence features (~13 weeks)  
**Then package:** App signing and permissions (Tier 2 - 1 week)  
**Then polish:** Onboarding and data autonomy (Tier 3 - 2-3 weeks, optional)  
**Then enhance:** Communication intelligence (Tier 4 - 2-3 weeks, optional)

### Phase 10 (iOS)

- Wait until desktop app is stable (Tier 1 complete)
- Revisit after Tier 1 and optionally Tier 2 complete
- Not urgent - desktop is primary interface

---

## Summary

**Current Status:** 50% complete, solid foundation (Phases 1-5 done)  
**Next Phase:** Phase 1.5 (6 days) - Domain Configuration (foundation)  
**Tier 1 Priority:** Phases 1.5, 13, 14, 12, 11, 16, 15, 17 (13-16 weeks) - Core intelligence  
**Tier 2 Later:** App Signing + Phase 9 (1 week) - Enable macOS integrations  
**Tier 3 Polish:** Phases 18, 19 (2-3 weeks) - Onboarding + data autonomy  
**Tier 4 Advanced:** Phase 20a/b/c (2-3 weeks) - Communication intelligence  
**Optional:** Phases 6-8 (varies) - Nice-to-have improvements  
**Future:** Phase 10 (3-4 weeks) - iOS mobile app  

**Recommended Path:** 
- Phase 1.5 → Tier 1 (Phases 13, 14, 12a/b, 11, 16a/b/c, 15, 17) → Tier 2 (Signing + Phase 9) → Tier 3 (Phases 18, 19) → Tier 4 (Phase 20a/b/c) → Optional Phases 6-8 → Future Phase 10

**New Phases Added:**
- ⭐ Phase 1.5: Domain Configuration (user-definable domains + zero-config)
- ⭐ Phase 11 Enhanced: Intelligent routing with confidence system
- ⭐ Phase 12 Enhanced: Reasoning transparency (edge confidence, "why this connection?")
- ⭐ Phase 16: Native Note Management (Obsidian replacement, 3 sub-phases, proactive suggestions)
- ⭐ Phase 17: Code Workspace (integrated development environment)
- ⭐ Phase 18: Onboarding & Progressive Teaching (Tier 3)
- ⭐ Phase 19: Data Autonomy & Export (Tier 3)
- ⭐ Phase 20: Intelligent Communication - 3 sub-phases (Tier 4)

**Timeline Update:** 
- **Tier 1:** 13-16 weeks (core intelligence)
- **Tier 2:** +1 week (packaging + permissions)
- **Tier 3:** +2-3 weeks (polish + autonomy)
- **Tier 4:** +2-3 weeks (communication)
- **Total with all tiers:** 18-23 weeks

**Marketing Alignment:**
- "Your work doesn't fit in boxes" → Phase 1.5 (polymathic domains)
- "Stop organizing. Start working." → Phase 16c (auto-organization)
- "Knowledge that compounds" → Phase 11 (progressive autonomy)
- "See how you think" → Phase 12 (reasoning transparency)
- "Your data. Your freedom." → Phase 19 (data export, self-hosting)
- "Polly teaches you as you teach Polly" → Phase 18 (progressive revelation)
- "Build capability, don't rent it" → Phase 20c (communication autonomy)

---

**Last Updated:** January 24, 2026  
**Next Action:** Start Phase 1.5 (Domain Configuration System)  
**Primary Document:** `MASTER_ROADMAP.md` (merged roadmap, single source of truth)  
**Marketing Document:** `MARKETING_POSITIONING.md` (complete marketing strategy)
