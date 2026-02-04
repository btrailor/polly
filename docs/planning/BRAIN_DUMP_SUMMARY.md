# Brain Dump Organization Summary

**Date:** February 3, 2026  
**Session:** Brain dump of 50+ features/ideas organized into structured planning system  
**Result:** 6 new phase specifications, 20 new features tracked, 18 known issues, 12 research items

---

## Quick Overview

### What Was Created

**7 New Phase Specifications** (Tier 1-2):
- Phase 13b: User Profile System (~12,500 words) - Added Feb 4, 2026
- Phase 24: Orchestrator Mode (~6,000 words)
- Phase 25: Code Architecture System (~5,500 words)
- Phase 26: Project Management (~5,000 words)
- Phase 27: Designer Persona (~5,500 words)
- Phase 28: Open Polly Tools (~5,000 words)
- Phase 29: Built-in Browser (~4,500 words)

**3 Core Planning Documents:**
- `DESIGN_PHILOSOPHY.md` - Progressive Capability model (~4,000 words)
- `RESEARCH_QUEUE.md` - 12 research items (~2,500 words)
- `KNOWN_ISSUES.md` - 18 tracked issues (~3,000 words)

**Feature Tracking:**
- 20 new features added to `FEATURES_TO_BUILD.md` (#19-38)
- Categories: UI/UX, Infrastructure, Project Management, Personas, Plugins, Advanced

---

## Priority Rankings

### Tier 1: Critical Path (Build These First)

#### 1. **Phase 24: Orchestrator Mode** ⭐ HIGHEST PRIORITY
**Effort:** 2-3 weeks  
**Why Critical:**
- **Foundation for everything else** - Required by Phase 27, 28
- Multi-persona coordination unlocks power user features
- Dynamic todo lists (OpenCode-style progress tracking)
- Customizable workflows (Architect → Designer → Programmer)

**Dependencies:** Phase 11c ✅ (complete)

**User Value:**
- No manual persona switching
- Complex projects in one session
- Transparent progress tracking
- Intelligent task routing

**Next Steps After:** Phase 27 (Designer) OR Phase 26 (Project Mgmt)

---

#### 2. **Phase 22 Frontend Completion** ⭐ QUICK WIN
**Effort:** 1-2 days  
**Why Critical:**
- Backend 100% complete (just needs UI)
- Unlock full Socratic teaching capabilities
- Learning dashboard with progress tracking
- High user value for low effort

**Dependencies:** Phase 14 ✅, Phase 23 ✅ (complete)

**User Value:**
- Complete teaching mode experience
- Visual progress tracking
- Mode switching UI

**Next Steps After:** Continue with Phase 24 or fix critical issues

---

#### 3. **Critical Bug Fixes** ⚠️ USER FRICTION
**Effort:** 6-10 hours total  
**Why Critical:**
- Resize handles broken (critical usability issue)
- Context reload jarring UX (high priority)
- Quick wins that improve user experience

**Issues:**
- KNOWN_ISSUES.md #1: Resize handles (2-3 hours)
- KNOWN_ISSUES.md #2: Context reload UX (4-6 hours)

**User Value:**
- Better usability
- Smoother experience
- Reduced friction

---

#### 4. **Phase 13b: User Profile System** 🧠 FOUNDATIONAL
**Effort:** 2-3 weeks  
**Depends On:** Phase 24 (recommended, but can build independently)

**Why Critical:**
- Enables Polly to understand user's unique thinking, preferences, expertise
- Profile-aware responses (appropriate depth, tone, context)
- Foundation for all personalization
- Human-readable markdown (user owns and controls profile)

**User Value:**
- Stop repeating context ("I'm experienced with X")
- Responses match your communication preferences
- Domain-specific expertise recognized
- Profile you can edit directly

**Key Features:**
- 4 bootstrap mechanisms (corpus import, onboarding, progressive, manual)
- Quality scoring (prevents slop/generic content)
- Profile-aware context injection (local + cloud)
- Domain-specific sub-profiles (one-to-one with Phase 1.5 domains)

**Reference:** `PHASE13B_USER_PROFILE_SYSTEM.md`

---

### Tier 2: High Value (Build After Tier 1)

#### 5. **Phase 27: Designer Persona** 🎨
**Effort:** 8-12 weeks  
**Depends On:** Phase 24 ⚠️ (must complete first)

**Why High Priority:**
- Major differentiator (design + code in one tool)
- 4 modes: Vision, Mockup, Critic, System
- Architect → Designer → Programmer workflow
- Theme-as-meta-persona concept

**User Value:**
- Consistent design-to-code workflow
- AI-powered design critique
- Design system management

---

#### 6. **Phase 26: Project Management** 📊
**Effort:** 3-4 weeks  
**Depends On:** Phase 24 ⚠️ (must complete first), Phase 23 ✅

**Why High Priority:**
- Visual project roadmaps
- OmniFocus-style task management
- Dynamic todo lists in chat
- AI-powered planning assistant

**User Value:**
- Visual progress tracking
- Transparent task management
- Intelligent planning assistance

**Research Needed:** HyperTask.ai integration

---

#### 7. **Phase 28: Open Polly Tools** 🔌
**Effort:** 4-6 weeks  
**Depends On:** Phase 24 ⚠️ (must complete first), Phase 11c ✅

**Why High Priority:**
- Community-driven ecosystem
- GitHub-based tool distribution
- 10 core official tools
- Extensibility without forking

**User Value:**
- Extend Polly capabilities
- Community contributions
- Easy sharing and discovery

---

### Tier 3: Medium Priority (Build When Ready)

#### 8. **Phase 25: Code Architecture System** 🏗️
**Effort:** 3-4 weeks  
**Depends On:** Phase 17 (Code Workspace)

**Why Medium Priority:**
- Visual dependency trees
- Impact analysis ("what breaks if I change this?")
- Auto-generated architecture docs
- Developer-focused tool

**Research Needed:** SummonAI Kit integration

---

#### 9. **Phase 16c: AI Note Creation** 📝
**Effort:** 4 weeks  
**Depends On:** Phase 11 ✅ (complete)

**Why Medium Priority:**
- Backend ready (Phase 11 complete)
- High user value
- AI-assisted note generation
- Clarifying questions workflow

---

#### 10. **Phase 12a: Knowledge Graph Basic** 🕸️
**Effort:** 5-7 days  
**Dependencies:** None

**Why Medium Priority:**
- Visual understanding of connections
- Interactive graph visualization
- Click-to-navigate
- Nice-to-have, not critical

---

### Tier 4: Lower Priority (Nice-to-Have)

#### 11. **Phase 29: Built-in Browser** 🌐
**Effort:** 2-3 weeks  
**Depends On:** Phase 17, Phase 27

**Why Lower Priority:**
- Nice-to-have (not essential)
- Embedded Chromium browser
- DevTools for web analysis
- Live preview of generated code

---

## Critical Path Visualization

```
Current State
     ↓
Phase 22 Frontend (1-2 days) ← QUICK WIN
     ↓
Fix Critical Bugs (6-10h) ← QUICK WIN
     ↓
Phase 24: Orchestrator Mode (2-3 weeks) ← FOUNDATION
     ├─→ Phase 13b: User Profile System (2-3 weeks) ← PERSONALIZATION
     │        ↓
     │   [Profile-aware responses across all personas]
     │
     ├─→ Phase 27: Designer Persona (8-12 weeks)
     ├─→ Phase 26: Project Management (3-4 weeks)
     └─→ Phase 28: Open Polly Tools (4-6 weeks)
```

**Key Insight:** Phase 24 (Orchestrator) is the **bottleneck** - it unlocks Phases 27, 26, 28, and enhances Phase 13b.

**Phase 13b Position:** Can be built independently OR after Phase 24 for full integration. Recommended: Build after Phase 24 for profile-aware multi-persona workflows.

---

## Recommended Build Order

### Immediate (This Week)
1. ✅ Phase 22 Frontend (1-2 days) - **QUICK WIN**
2. ✅ Fix resize handles (2-3h) - **QUICK WIN**
3. ✅ Fix context reload UX (4-6h) - **QUICK WIN**

**Outcome:** Complete Tier 1 features, smooth UX

---

### Short-Term (Next 2-4 Weeks)
4. ⭐ Phase 24: Orchestrator Mode (2-3 weeks) - **FOUNDATION**
5. 🧠 Phase 13b: User Profile System (2-3 weeks) - **PERSONALIZATION**

**Outcome:** Unlock all advanced features + personalized responses

---

### Medium-Term (Next 1-3 Months)
6. 🎨 Phase 27: Designer Persona (8-12 weeks) - **DIFFERENTIATOR**
7. 📊 Phase 26: Project Management (3-4 weeks) - **PRODUCTIVITY**
8. 🔌 Phase 28: Open Polly Tools (4-6 weeks) - **EXTENSIBILITY**

**Outcome:** Polly becomes design tool + code editor + knowledge manager + AI assistant

---

### Long-Term (3-6 Months)
9. 🏗️ Phase 25: Code Architecture (3-4 weeks)
10. 📝 Phase 16c: AI Note Creation (4 weeks)
11. 🕸️ Phase 12a: Knowledge Graph (5-7 days)
12. 🌐 Phase 29: Built-in Browser (2-3 weeks)

---

## Design Philosophy Established

**Core Principle:** Progressive Capability
- Tool starts simple, grows with user
- Context reveals complexity
- Default-driven configuration
- Open plugin ecosystem (Phase 28)
- Growth-oriented design

**Key Decisions:**
- Not fully open source, not fully closed
- Open Polly Tools (Phase 28) = hybrid approach
- Core closed, extensions open
- Curated community ecosystem

**Reference:** `docs/planning/DESIGN_PHILOSOPHY.md`

---

## Research Queue Priorities

### High Priority (Required for Phases)
1. **SummonAI Kit** - Code stack analysis (Phase 25 dependency)
2. **HyperTask.ai** - Project management integration (Phase 26 learning)
3. **OpenCode performance** - Preventive analysis (avoid their mistakes)

### Medium Priority (Exploration)
4. Reor.ai - Self-organizing notes
5. Uare.ai - Competitive overlap analysis
6. Kilo Code - Free models (GLM 4.7, MiniMax 2.1)
7. Figma API - Designer persona integration
8. CodeMirror - Chat polish

**Reference:** `docs/planning/RESEARCH_QUEUE.md` (12 items)

---

## Known Issues Summary

**Critical (P0):**
- Resize handles not working

**High Priority (P1):**
- Context reload jarring UX
- Deduplication system needs clarity

**Medium Priority (P2):**
- Domain tagging misclassification
- Learning profile UI too prominent
- Pattern learning clarity
- Compression system clarity

**Total Tracked:** 18 issues

**Reference:** `docs/planning/KNOWN_ISSUES.md`

---

## UI/UX Polish Backlog

**Quick Wins (1-2 days each):**
- Resizable sidebars
- Lucide icons system-wide (partially complete)
- Loading spinner overhaul (cute dots)
- Scroll-to-bottom button
- Mode dropdown with visual indicator
- Excel-style note action chips

**Medium Effort (2-4 days):**
- CodeMirror chat polish
- Floating chat input (OpenCode-style)

**Reference:** `FEATURES_TO_BUILD.md` #19-24

---

## Big Differentiators (What Makes Polly Unique)

### 1. **Orchestrator Mode** (Phase 24)
- Multi-persona coordination
- Customizable workflows
- Dynamic progress tracking
- **Competitor Gap:** No other AI tool does this

### 2. **Designer Persona** (Phase 27)
- Figma-like capabilities
- Architect → Designer → Programmer workflow
- Design + code in one tool
- **Competitor Gap:** v0 by Vercel is cloud-only, not integrated

### 3. **Open Polly Tools** (Phase 28)
- Community-driven ecosystem
- Curated quality tools
- GitHub-based distribution
- **Competitor Gap:** Most AI tools are closed, no extensibility

### 4. **Code Architecture System** (Phase 25)
- Visual dependency trees
- Impact analysis
- Auto-generated docs
- **Competitor Gap:** Most IDEs lack this

### 5. **Progressive Capability**
- Starts simple, grows powerful
- Context reveals complexity
- Default-driven
- **Competitor Gap:** Most tools are either too simple or too complex

---

## Success Metrics

### Short-Term (Phase 24 Complete)
- ✅ Multi-persona workflows working
- ✅ Customizable routings functional
- ✅ Dynamic todo lists in chat
- ✅ User can complete complex project in one session

### Medium-Term (Phases 27, 26, 28 Complete)
- ✅ Designer persona generating UI mockups
- ✅ Project roadmaps visualized
- ✅ Community tools being created
- ✅ Polly = design tool + code editor + knowledge manager

### Long-Term (All Phases Complete)
- ✅ Users choose Polly over Figma + VS Code + Obsidian + ChatGPT
- ✅ Active community contributing tools
- ✅ Polly becomes "the tool" for building software

---

## Files Modified/Created

### Phase Specifications (New)
- `docs/planning/phases/other/PHASE24_ORCHESTRATOR_MODE.md` (~6,000 words)
- `docs/planning/phases/other/PHASE25_CODE_ARCHITECTURE_SYSTEM.md` (~5,500 words)
- `docs/planning/phases/other/PHASE26_PROJECT_MANAGEMENT.md` (~5,000 words)
- `docs/planning/phases/other/PHASE27_DESIGNER_PERSONA.md` (~5,500 words)
- `docs/planning/phases/other/PHASE28_OPEN_POLLY_TOOLS.md` (~5,000 words)
- `docs/planning/phases/other/PHASE29_BUILT_IN_BROWSER.md` (~4,500 words)

### Core Planning Documents (New)
- `docs/planning/DESIGN_PHILOSOPHY.md` (~4,000 words)
- `docs/planning/RESEARCH_QUEUE.md` (~2,500 words)
- `docs/planning/KNOWN_ISSUES.md` (~3,000 words)
- `docs/planning/BRAIN_DUMP_SUMMARY.md` (this file)

### Updated Documents
- `FEATURES_TO_BUILD.md` (added features #19-38)
- `docs/status/CURRENT.md` (added new phases, issues, research references)

---

## Next Session Recommendations

### If You Want Quick Wins (1-2 Days)
1. Complete Phase 22 frontend
2. Fix resize handles
3. Fix context reload UX

**Result:** Tier 1 complete, smooth UX

---

### If You Want To Unlock Everything (2-3 Weeks)
1. Build Phase 24: Orchestrator Mode

**Result:** Foundation for all advanced features

---

### If You Want The "Wow" Factor (8-12 Weeks)
1. Complete Phase 24 first (2-3 weeks)
2. Build Phase 27: Designer Persona (8-12 weeks)

**Result:** Polly becomes design + code tool (major differentiator)

---

### If You Want Community Growth (4-6 Weeks)
1. Complete Phase 24 first (2-3 weeks)
2. Build Phase 28: Open Polly Tools (4-6 weeks)

**Result:** Extensible, community-driven ecosystem

---

## Key Insights from Session

### 1. Phase 24 is the Bottleneck
Everything exciting (Designer, Project Mgmt, Plugins) requires Orchestrator Mode first.

**Action:** Prioritize Phase 24 after quick wins.

---

### 2. Quick Wins Available
Phase 22 frontend and critical bug fixes are ~2 days total effort, high user value.

**Action:** Complete these before starting Phase 24.

---

### 3. Design Philosophy Clarified
"Progressive Capability" model established. Not fully open, not fully closed. Hybrid approach with Open Polly Tools.

**Action:** Use this philosophy to guide all future decisions.

---

### 4. Community Ecosystem is Key
Open Polly Tools (Phase 28) enables growth without losing control of core product.

**Action:** Build plugin system with curated marketplace.

---

### 5. Designer Persona is the Differentiator
Combining design + code in one tool (with AI) is unique in the market.

**Action:** Prioritize Phase 27 after Phase 24.

---

## Context for Continuation

### If Starting a New Session
1. Read this document first (5 min)
2. Review `docs/planning/DESIGN_PHILOSOPHY.md` (10 min)
3. Choose priority: Quick wins OR Foundation (Phase 24) OR Differentiator (Phase 27)
4. Read relevant phase specification
5. Begin implementation

### If Continuing Planning
1. Review `docs/planning/RESEARCH_QUEUE.md` - Start research items
2. Review `docs/planning/KNOWN_ISSUES.md` - Prioritize fixes
3. Refine phase specifications based on research findings
4. Update estimates and timelines

---

**Created:** February 3, 2026  
**Purpose:** One-page reference for brain dump organization results  
**Next Review:** After completing Phase 22 frontend or Phase 24

---

## Quick Reference Table

| Phase | Name | Priority | Effort | Depends On | Why Critical |
|-------|------|----------|--------|------------|--------------|
| 22 Frontend | Teaching Mode UI | ⭐⭐⭐⭐⭐ | 1-2d | Phase 14 ✅ | Backend complete, quick win |
| Critical Bugs | Resize + Context | ⭐⭐⭐⭐⭐ | 6-10h | None | User friction, quick win |
| 24 | Orchestrator Mode | ⭐⭐⭐⭐⭐ | 2-3w | Phase 11c ✅ | Foundation for everything |
| 13b | User Profile System | ⭐⭐⭐⭐⭐ | 2-3w | Phase 24 (rec) | Foundational personalization |
| 27 | Designer Persona | ⭐⭐⭐⭐ | 8-12w | Phase 24 ⚠️ | Major differentiator |
| 26 | Project Management | ⭐⭐⭐⭐ | 3-4w | Phase 24 ⚠️ | Productivity tool |
| 28 | Open Polly Tools | ⭐⭐⭐⭐ | 4-6w | Phase 24 ⚠️ | Extensibility |
| 25 | Code Architecture | ⭐⭐⭐ | 3-4w | Phase 17 | Developer tool |
| 16c | AI Note Creation | ⭐⭐⭐ | 4w | Phase 11 ✅ | High user value |
| 12a | Knowledge Graph | ⭐⭐ | 5-7d | None | Nice-to-have |
| 29 | Built-in Browser | ⭐⭐ | 2-3w | Phase 17, 27 | Nice-to-have |

**Legend:**
- ✅ = Dependency complete
- ⚠️ = Dependency incomplete (blocks this phase)
- ⭐ = Priority (more stars = higher priority)
