# Brain Dump Organization Summary

**Date:** January 28, 2026  
**Purpose:** Document where all items from the massive brain dump were organized  
**Total Items Processed:** 40+ questions, ideas, and features

---

## Overview

Your brain dump has been systematically organized across **5 key documents**:

1. **TECHNICAL_QUESTIONS.md** (NEW) - 7 investigation items
2. **FEATURES_TO_BUILD.md** (UPDATED) - 12 new features added
3. **ISSUES_TO_TROUBLESHOOT.md** (UPDATED) - 2 UI issues added
4. **PHASE23_PROJECT_MANAGEMENT.md** (NEW) - Major new phase proposal
5. **MASTER_ROADMAP.md** (UPDATED) - Phase 23 added to Tier 5

---

## 1. TECHNICAL_QUESTIONS.md (NEW DOCUMENT)

**Location:** `/Users/brettgershon/polly/TECHNICAL_QUESTIONS.md`

**7 Questions Requiring Investigation:**

### Q1: Obsidian.py Migration Status
- **Category:** Phase 16 (Native Notes)
- **Question:** Is there an outmoded `Obsidian.py` file after Phase 16 migration?
- **Action:** Search codebase, determine if old integration code can be removed

### Q2: Domain Priority Structure & RAG Retrieval Efficiency ⚠️ CRITICAL
- **Category:** Phase 1.5 + Phase 13
- **Question:** Is domain filtering too restrictive for cross-domain topics? (Monome Norns = Sigils + Signals)
- **Potential Solutions:** Multi-domain tagging, cross-domain confidence boost, softer filtering
- **Test Case:** Query "How do I program Monome Norns in Lua?" should return both Sigils and Signals results

### Q3: Wiki-Link Embed Syntax Differences
- **Category:** Phase 16 (Native Notes)
- **Question:** What's difference between `[[]]` (link) and `![[]]` (embed)? Are embeds supported?
- **Action:** Review Phase 16 wiki-link parsing, document expected behavior

### Q4: Knowledge Base Organization at Scale
- **Category:** Phase 16c + Phase 21
- **Question:** How does Polly keep KB organized as it scales? How to decide when to subcategorize?
- **Proposed Solutions:** Threshold-based subcategorization, semantic clustering, project-based folders

### Q5: Codebase Context Confusion (Aleph vs. aleph-builder)
- **Category:** Phase 17 (Code Workspace)
- **Question:** Why does chat confuse connected codebases with similar names?
- **Proposed Solutions:** Include repo name in metadata, disambiguation UI, conversation context memory

### Q6: Mail Pattern Response Storage & Visibility
- **Category:** Phase 20a (Email Intelligence)
- **Question:** How are learned email replies stored? RAG only? Visible to user? How managed?
- **Proposed Storage:** `~/.polly/email_patterns.json` or `_Templates/Email/` notes

### Q7: Pattern Response Visibility & Management
- **Category:** Phase 13b (Pattern Learning UI)
- **Question:** How are patterns made visible to user? What management actions?
- **Answer:** Phase 13b will add dedicated Patterns page with browser, search, filters, management

---

## 2. FEATURES_TO_BUILD.md (UPDATED - 12 NEW FEATURES)

**Location:** `/Users/brettgershon/polly/FEATURES_TO_BUILD.md`

### High Priority Features (6 added)

**Feature #2: User-Defined Knowledge Base Directory** ⭐ MUST-HAVE
- **Target Phase:** Phase 19 (Data Autonomy) or earlier
- **Requirements:** Dropbox, iCloud, Google Drive, OneDrive, WebDAV compatibility
- **Storage:** User-chosen location (e.g., `~/Dropbox/Polly/`)
- **Benefit:** Full control over data location, survives app updates

**Feature #3: Wiki-Link Note Creation** ⭐ MUST-HAVE
- **Target Phase:** Phase 16 enhancement
- **Behavior:** Click `[[broken link]]` → Modal with folder selection → Create & open note
- **Benefit:** Seamless Obsidian-style note creation workflow

**Feature #4: Notes Templating System**
- **Target Phase:** Phase 16 enhancement
- **Features:** Templates in `_Templates/` folder, variable substitution `{{date}}`, `{{title}}`
- **Benefit:** Consistent note structure, faster creation

**Feature #5: Table of Contents View for Large Notes**
- **Target Phase:** Phase 16 enhancement
- **UI:** Right sidebar panel with clickable heading navigation
- **Benefit:** Navigate long documents easily

**Feature #6: Document-Specific Context in Chat** ⭐ MUST-HAVE
- **Target Phase:** Phase 17 or Phase 11 enhancement
- **UI:** Type `/` in chat → Knowledge base browser → Add documents to context
- **Benefit:** Precise context control, better responses

**Feature #7: Chat Note Creation with Confirmation**
- **Target Phase:** Phase 16c enhancement
- **Change:** Remove persistent button, use confirmation dialogue in chat
- **Benefit:** Cleaner UI, contextual actions

**Feature #8: OmniFocus-Style Todo List with Chat Integration**
- **Target Phase:** Phase 23 (Project Management) or separate
- **Features:** Projects, contexts, defer/due dates, review cycles, chat extraction
- **Integration:** Extract action items from conversations automatically

### Low Priority Features (4 added)

**Feature #9: Auto-Complete for Wiki-Links** (`[[` → `[[]]`)
**Feature #10: Click-to-Position Cursor in Edit Mode**
**Feature #11: Generate Note Templates from Existing Notes** (AI-powered)
**Feature #12: One-Time Purchase Feature Expansions** (Monetization strategy)

---

## 3. ISSUES_TO_TROUBLESHOOT.md (UPDATED - 2 UI ISSUES)

**Location:** `/Users/brettgershon/polly/ISSUES_TO_TROUBLESHOOT.md`

### Issue #2: Unused "Conversations" UI Element in Right Sidebar
- **Status:** Low priority cleanup
- **Problem:** Clickable dropdown arrow does nothing
- **Cause:** Old UI element from previous design
- **Action:** Remove HTML, CSS, event listeners

### Issue #3: Settings UI Update Incomplete
- **Status:** Low priority polish
- **Problem:** Settings page doesn't match Phase 0.5 Obsidian-inspired design
- **Cause:** Built before redesign
- **Action:** Audit and update styling to match new design system

---

## 4. PHASE23_PROJECT_MANAGEMENT.md (NEW MAJOR PHASE)

**Location:** `/Users/brettgershon/polly/PHASE23_PROJECT_MANAGEMENT.md`

**Comprehensive 3-4 week phase proposal covering 10 major strategic ideas from brain dump:**

### 1. Standardized Project Workflows
- Documentation-first philosophy
- Project types: Code, Writing, Creative, Research, Custom
- Standard structure: `PROJECT.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `BUILD.md`, `DECISIONS.md`

### 2. Project-Specific Pattern Learning
- Build commands, test commands, deploy commands
- Architecture patterns (key file locations, naming conventions)
- Project context (tech stack, APIs, integrations)
- Storage: `~/Polly/Projects/{name}/.polly/patterns.json`

### 3. Plan/Build Modes for Code Workspace
- **Plan Mode:** Asks questions, refuses to code until spec is complete
- **Build Mode:** Executes implementation following plan
- **Threshold:** Must reach planning completeness before building
- **Philosophy:** "You don't build a rough idea, you plan until it is a detailed vision"

### 4. Always-Current Project Overview
- `PROJECT.md` automatically updated with architectural changes
- High-level summary stays synchronized with reality
- New AI sessions start with current context

### 5. Architectural Change Awareness
- Detects file moves, refactors, major module changes
- Prompts to update documentation
- Creates ADRs (Architecture Decision Records) for major changes
- Example: "Settings moved from sidebar to header" → Update docs + Create ADR

### 6. Compression & Memory System
- "Polly shorthand" for efficient context compression
- 10:1 to 100:1 compression ratio
- Extends conversation memory without hitting token limits
- Patterns stored in compressed format
- Storage: `.polly/compressed_context.json`

### 7. Context-Aware RAG Filtering
- Code Workspace prioritizes codebases, ignores calendar
- Calendar prioritizes events, ignores code
- Efficiency: Skip irrelevant collections, faster retrieval
- Integration with Phase 0.5 page context tracking

### 8. Dashboard as Daily Briefing
- Today's focus (active projects, tasks, meetings)
- Recent activity (conversations, notes, commits)
- Pattern insights ("You often work on Aleph Monday mornings")
- Knowledge updates (new documents, connections)
- Action items (from emails, meetings, conversations)

### 9. Project Maturity Framework
- 5 dimensions: Planning, Implementation, Documentation, Testing, Deployment
- 0-5 scale for each dimension
- Weighted average maturity score
- Guides development priorities (document before building new features)

### 10. Slack-Like Project Interface
- Project list sidebar with maturity scores
- Tabs: Overview, Files, Sessions, Tasks, Build, Chat
- Project-specific context always available
- Channel-based organization for projects

**Effort:** 3-4 weeks (Week 1-2: Core system, Week 3: Plan/Build modes, Week 4: UI)

**Dependencies:** Phase 1.5, 13, 16, 17

**Target Users:** Professional developers, teams, complex projects

---

## 5. MASTER_ROADMAP.md (UPDATED - PHASE 23 ADDED)

**Location:** `/Users/brettgershon/polly/MASTER_ROADMAP.md`

**Change:** Added Phase 23 to Tier 5 (Optional Enhancements)

**Section:** Lines ~1427+ (Tier 5)

**Entry:**
```
#### Phase 23: Project Management & Documentation-First Workflows (3-4 weeks) ⭐ NEW
- Comprehensive project management with documentation-first philosophy
- Project-specific pattern learning
- Plan/Build modes
- Always-current PROJECT.md
- Architectural change awareness
- Compression & memory system
- Context-aware RAG filtering
- Dashboard as daily briefing
- Project maturity framework
- Slack-like project interface

Target Users: Professional developers, teams, complex projects
Marketing: "Build capability, don't rent it" - Integrated, not SaaS
```

---

## Additional Context Enhancements

Several ideas from brain dump enhance existing phases (already documented in their respective phase files):

### Phase 11 Enhancements (PHASE11_COMPRESSION_SYSTEM.md)
- Compression strategy already documented
- Shorthand for efficient memory management
- Pattern compression integration

### Phase 13 Enhancements (PHASE13A_PATTERN_LEARNING_CORE.md, PHASE13B_PATTERN_LEARNING_UI.md)
- Per-project pattern utilization
- Compressed pattern storage format
- Pattern visibility in UI

### Phase 17 Enhancements (PHASE17_CODE_WORKSPACE.md)
- Plan/Build modes integration
- Context-aware code chat
- Project-specific patterns active

### Phase 20 Enhancements (PHASE20_INTELLIGENT_COMMUNICATION.md)
- Mail pattern response caching
- Pattern visibility and management
- Email intelligence storage strategy

---

## Items Deferred or Requiring Further Discussion

### 1. Cross-User Family Integration
- **Mentioned in:** Brain dump, Phase 23 open questions
- **Status:** Needs requirements gathering
- **Questions:** 
  - What does "family integration" mean? (Shared projects? Separate workspaces?)
  - Multi-user sync strategy?
  - Privacy/permissions model?
- **Recommendation:** Create separate design document after Tier 1 complete

### 2. Figma Integration for Code Persona
- **Mentioned in:** Brain dump QoL improvements
- **Status:** Needs scoping
- **Questions:**
  - What should Figma integration do? (Link to designs in PROJECT.md?)
  - Code generation from designs?
  - Design file versioning?
- **Recommendation:** Could be Phase 24 or extension of Phase 23

### 3. Research Airflow and Motion.ai
- **Mentioned in:** Brain dump strategic ideas
- **Status:** Research task, not implementation
- **Action:** Add to research backlog for future inspiration
- **Recommendation:** Review before implementing Phase 23

---

## Summary Statistics

**Total Items Organized:** 40+

**Breakdown by Type:**
- 7 Technical Questions → TECHNICAL_QUESTIONS.md
- 12 Features (8 must-have, 4 QoL) → FEATURES_TO_BUILD.md
- 2 UI Issues → ISSUES_TO_TROUBLESHOOT.md
- 15 Strategic Ideas → PHASE23_PROJECT_MANAGEMENT.md (10 features)
- 6 Enhancements to existing phases → Existing phase documents

**Documents Modified:** 5
**Documents Created:** 3 new (TECHNICAL_QUESTIONS.md, PHASE23_PROJECT_MANAGEMENT.md, BRAIN_DUMP_SUMMARY.md)

**Priority Breakdown:**
- 🔴 Critical: 1 (Q2: Domain filtering RAG issue)
- 🟡 High: 6 must-have features + Phase 23
- 🟢 Medium: 7 items
- 🟣 Low: 6 items

---

## Next Steps

### Immediate Actions (This Week)

1. **Investigate Q2 (Domain Filtering RAG)** ⚠️ CRITICAL
   - Test query: "How do I program Monome Norns in Lua?"
   - Check if results span both Sigils and Signals
   - Determine if multi-domain tagging needed

2. **Review PHASE23_PROJECT_MANAGEMENT.md**
   - Decide if Phase 23 should be Tier 5 (optional) or earlier (essential)
   - Consider if Polly development itself needs this phase now

3. **Prioritize Must-Have Features**
   - User-defined KB directory (Phase 19 or earlier?)
   - Document-specific context in chat (Phase 17 enhancement?)
   - Wiki-link note creation (Phase 16 quick enhancement?)

### Short-Term Actions (Next 2-4 Weeks)

4. **Answer Remaining Technical Questions**
   - Q1: Obsidian.py migration status
   - Q3: Wiki-link embed syntax
   - Q5: Codebase context confusion

5. **Plan Phase 16 Enhancements**
   - Wiki-link note creation
   - Table of contents view
   - Click-to-position cursor
   - Auto-complete for `[[` and `![[`

6. **Consider Phase 23 Early Implementation**
   - If developing Polly itself is painful without it, consider moving to Tier 1
   - Alternative: Implement lightweight version during Tier 1 development

### Long-Term Actions (After Tier 1 Complete)

7. **Implement Phase 23** (if Tier 5)
   - Full 3-4 week implementation
   - Solves documentation and project management pain points

8. **Research Deferred Items**
   - Cross-user family integration requirements
   - Figma integration scope
   - Airflow and Motion.ai learnings

9. **Polish & Cleanup**
   - Fix UI issues (#2, #3)
   - Implement QoL improvements

---

## How to Use This Document

**When you want to:**

- **Investigate a technical question** → See TECHNICAL_QUESTIONS.md
- **Implement a planned feature** → See FEATURES_TO_BUILD.md
- **Fix a known issue** → See ISSUES_TO_TROUBLESHOOT.md
- **Understand project management vision** → See PHASE23_PROJECT_MANAGEMENT.md
- **See overall roadmap** → See MASTER_ROADMAP.md
- **Remember what was in brain dump** → This document (BRAIN_DUMP_SUMMARY.md)

---

**All brain dump items have been systematically organized. Nothing was lost or forgotten.**

**Status:** ✅ Complete - Brain dump fully processed and organized  
**Last Updated:** January 28, 2026
