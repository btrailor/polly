# Technical Questions & Investigation Items

**Project:** Polly - Edge-Native Personal AI System  
**Purpose:** Track questions that need investigation, research, or clarification  
**Last Updated:** January 28, 2026

---

## Active Questions

### 1. Obsidian.py Migration Status
**Category:** Phase 16 (Native Notes)  
**Priority:** Medium  
**Status:** 🟡 Needs Investigation

**Question:**
Is there an `Obsidian.py` file that is now outmoded given our migration to Polly native notes?

**Context:**
- Phase 16 completed January 26, 2026
- Native notes system now handles note management
- Need to verify if old Obsidian integration code can be removed or deprecated

**Investigation Steps:**
1. Search codebase for `obsidian.py` or `Obsidian.py`
2. Check if it's still imported/used anywhere
3. Determine if it's needed for backward compatibility
4. Document what functionality it provided vs. Phase 16

**Related Files:**
- `core/obsidian.py` (if exists)
- `integrations/obsidian.py` (Phase 3 integration)
- Phase 16 native notes implementation

---

### 2. Domain Priority Structure & RAG Retrieval Efficiency ✅ SOLVED
**Category:** Phase 1.5 (Domains) + Phase 13 (Pattern Learning)  
**Priority:** High  
**Status:** 🟢 Complete - Issue Solved with Universal Fixes  
**Investigation Date:** January 29, 2026  
**Implementation Date:** January 29, 2026

**Question:**
Is domain priority structure restricting RAG retrieval? For example, "Monome Norns" is sometimes tagged as "Sigils" (code) and sometimes "Signals" (audio) and most of the time both. Is our domain filtering in pattern learning and RAG retrieval making finding things on this topic more difficult?

**Answer: YES - Issue confirmed and SOLVED**

**Test Results:**
- Initial: 50% of Norns queries detected only one domain
- **After fixes: 100% of Norns queries detect both relevant domains** ✅

**Root Cause:**
1. Keyword-only matching missed cross-domain topics
2. Technology mentions (Lua, Python) not recognized
3. User intent (programming, design) not detected
4. Aggressive collection skipping for low-priority domains

**Implementation Status:**

✅ **IMPLEMENTED (Jan 29, 2026):** Softened Collection Skipping
- File: `core/rag.py` lines 743-761
- Never skip collections for multi-domain queries (2+ domains)
- Lowered skip threshold: 0.5 → 0.3
- Test results: All 5 test cases pass

✅ **IMPLEMENTED (Jan 29, 2026):** Technology Pattern Matching
- File: `core/domains.py` lines 418-525
- Detects technology mentions (Lua, Python, React, Docker, SuperCollider, etc.)
- Boosts domains whose patterns match those technologies (+0.2 per tech, max +0.3)
- Supports 18+ technologies
- Test results: Improved detection from 50% → 62%

✅ **IMPLEMENTED (Jan 29, 2026):** Intent-Based Detection
- File: `core/domains.py` lines 527-686
- Detects user intent (programming, analysis, design, writing, learning, audio)
- Boosts domains matching detected intent (+0.15 per intent, max +0.25)
- Supports 6 intent types with 30+ patterns
- Test results: Improved detection from 62% → 100%

**Impact:**
- ✅ **100% success rate** for Norns cross-domain queries
- ✅ **Universal:** Works for ANY domain configuration
- ✅ **No hardcoding:** Uses domain characteristics, not specific names
- ✅ **Tested:** Comprehensive test suites for all fixes

**Examples:**
- "How do I program Monome Norns in Lua?" → ✅ Detects Sigils + Signals
- "Norns SuperCollider engine development" → ✅ Detects Sigils + Signals  
- "Create a Norns app with audio" → ✅ Detects Sigils + Signals
- "Analyze genomic data in Python" → ✅ Would boost DataScience domains
- "Build a React component" → ✅ Detects code domains

**Files:**
- `test_collection_skipping.py` - Tests collection skipping (5 tests, all pass)
- `test_technology_matching.py` - Tests tech detection (comprehensive suite)
- `test_intent_detection.py` - Tests intent detection (22/23 pass, 100% on Norns)
- `planning/investigations/domain_filtering_rag_investigation.md` - Full report
- `planning/investigations/universal_cross_domain_solution.md` - Solution design
- `planning/investigations/TECHNOLOGY_MATCHING_IMPLEMENTATION.md` - Tech matching details

**Result:** ✅ COMPLETE - Problem solved universally for all users!

See `planning/investigations/domain_filtering_rag_investigation.md` for full details.

---

### 3. Wiki-Link Embed Syntax Differences
**Category:** Phase 16 (Native Notes)  
**Priority:** Medium  
**Status:** 🟡 Needs Documentation

**Question:**
What's the difference between `![[]]` and `[[]]` in Obsidian and Polly's embed structuring?

**Context:**
- Obsidian uses:
  - `[[Note Name]]` - Link to note (navigate on click)
  - `![[Note Name]]` - Embed note content inline
  - `![[Image.png]]` - Embed image inline
- Polly Phase 16 currently handles `[[]]` links
- Need to clarify if `![[]]` embeds are supported

**Investigation Steps:**
1. Review Phase 16 wiki-link parsing code
2. Check if `![[]]` syntax is detected/rendered
3. Document expected behavior for embeds vs links
4. Decide if embeds should be Phase 16d enhancement or in scope

**Related Files:**
- `core/backlinks.py` (wiki-link parsing)
- `electron-app/src/renderer/notes-manager.js` (line ~400-500, wiki-link rendering)
- `PHASE16_COMPLETE.md`

**Expected Behavior:**
- `[[Note]]` → Clickable link (navigate to note)
- `![[Note]]` → Embed note content inline (read-only view)
- `![[Image.png]]` → Embed image inline
- `![[Note#Section]]` → Embed specific section

---

### 4. Knowledge Base Organization at Scale
**Category:** Phase 16c (AI Note Creation) + Phase 21 (Deduplication)  
**Priority:** High  
**Status:** 🟡 Architectural Question

**Question:**
As Polly generates a knowledge base, how will she keep that knowledge base reliably organized and accessible? As a domain grows beyond what is reasonable to not subcategorize, how would Polly decide how to manage its files?

**Context:**
- Polly can generate notes via Phase 16c (AI Note Creation)
- Over time, could generate hundreds/thousands of notes
- Need strategy for preventing disorganization
- Phase 21 addresses deduplication, but not overall organization

**Concerns:**
- Without careful tuning, knowledge base could become "overwhelmingly disarrayed"
- Users create their own domains, so can't hardcode organization rules
- Need smart subcategorization strategy as domains grow

**Investigation Areas:**

**1. Automatic Subcategorization:**
- When does a domain need subcategories? (threshold: 50 notes? 100 notes?)
- How to detect natural clusters within domain?
- Should Polly suggest subcategories or create them automatically?

**2. AI-Driven Organization:**
- Use embedding similarity to cluster related notes
- Suggest folder structure based on semantic groupings
- Learn organizational patterns from user behavior

**3. Phase 1.5 Integration:**
- Domain folder paths already support nesting: `~/Polly/Sigils/Projects/Aleph/`
- Could auto-create project-specific subfolders
- Pattern learning could detect organizational habits

**Proposed Solutions:**
- **Option 1:** Threshold-based subcategorization (suggest subfolders after N notes)
- **Option 2:** Semantic clustering (group notes by embedding similarity)
- **Option 3:** Project-based organization (detect project mentions, create subfolders)
- **Option 4:** User-defined templates for organization rules

**Related Phases:**
- Phase 16c: AI Note Creation (needs organization logic)
- Phase 21: Knowledge Base Deduplication (prevents duplicates, not chaos)
- Phase 13: Pattern Learning (learn organizational habits)

**Related Files:**
- `PHASE16C_AI_NOTE_CREATION.md`
- `PHASE21_KNOWLEDGE_DEDUPLICATION.md`
- `PHASE1.5_DOMAIN_CONFIGURATION.md`

---

### 5. Codebase Context Confusion (Aleph vs. aleph-builder)
**Category:** Phase 17 (Code Workspace)  
**Priority:** Medium  
**Status:** 🟡 Context Management Issue

**Question:**
Why does chat get confused by connected codebases and GitHub repositories when querying about "Aleph"? It finds "aleph-builder" instead of the intended project.

**Context:**
- Multiple repositories/codebases can be connected
- Similar names can cause ambiguity
- RAG retrieval may not have enough context to disambiguate

**Investigation Steps:**
1. Test query: "How does Aleph work?" - What does it return?
2. Check if RAG metadata includes repository/project name
3. Review how connected codebases are indexed
4. Check if domain context helps disambiguation

**Proposed Solutions:**
- **Option 1:** Include repository name in chunk metadata for disambiguation
- **Option 2:** When multiple matches, show disambiguation UI: "Which Aleph? (aleph-project, aleph-builder)"
- **Option 3:** Use conversation context to remember which project user is working on
- **Option 4:** Pattern learning to remember user's preferred interpretation

**Related Phases:**
- Phase 17: Code Workspace (context-aware code chat)
- Phase 13: Pattern Learning (remember user's project preferences)

**Related Files:**
- `core/rag.py` (metadata handling)
- `integrations/github.py` (repository indexing)

---

### 6. Mail Pattern Response Storage & Visibility
**Category:** Phase 20a (Email Intelligence)  
**Priority:** Medium  
**Status:** 🟡 Planning Phase Question

**Question:**
How does mail cache its pattern-recognized replies into Polly memory? Is this done via RAG? Do common replies get recognized and written to the knowledge base in some special way? Should these be visible in notes view, or only to RAG?

**Context:**
- Phase 20a includes email intelligence with pattern learning
- Common replies should be learned (e.g., "Thanks, I'll review and get back to you")
- Need to decide storage strategy

**Investigation Areas:**

**1. Storage Location:**
- Option A: Store in RAG only (invisible to user, fast retrieval)
- Option B: Store in knowledge base as notes (visible, editable)
- Option C: Hybrid: RAG for speed, notes for complex templates

**2. Pattern Recognition:**
- Use Phase 13 pattern learning for reply detection
- Track which responses user sends frequently
- Group similar responses into templates

**3. Visibility & Management:**
- Should users see all learned reply patterns?
- Provide UI for editing/managing canned responses?
- Link to Obsidian-style note templates?

**Proposed Solutions:**
- **Option 1:** Dedicated `~/.polly/email_patterns.json` (separate from general patterns)
- **Option 2:** Store in `~/.polly/notes/_Templates/Email/` as note templates
- **Option 3:** Hybrid: Common patterns in JSON, complex templates as notes

**UI Consideration:**
User should be able to:
- View all learned email patterns
- Edit/customize templates
- Approve/reject auto-applied drafts
- See pattern usage statistics

**Related Phases:**
- Phase 20a: Email Intelligence
- Phase 13: Pattern Learning
- Phase 16: Native Notes (template system)

**Related Files:**
- `PHASE20_INTELLIGENT_COMMUNICATION.md`
- `PHASE13A_PATTERN_LEARNING_CORE.md`

---

### 7. Pattern Response Visibility & Management
**Category:** Phase 13b (Pattern Learning UI)  
**Priority:** Medium  
**Status:** 🟡 UI Planning Question

**Question:**
How are pattern-recognized responses stored and made visible? Should they be visible in notes view? How is this managed?

**Context:**
- Phase 13a completed: patterns stored in `~/.polly/patterns.json`
- Phase 13b planned: Pattern Learning UI & Testing
- Need UI for browsing/managing learned patterns

**Current State:**
- Patterns stored in JSON (invisible to user)
- No UI for viewing/editing patterns
- Phase 13b will add pattern browser

**Questions to Answer:**

**1. What Should Be Visible?**
- All 3 pattern types (Query→Chunk, Domain→Collection, Conceptual)?
- Pattern confidence scores and usefulness tracking?
- Pattern application history?

**2. Where Should It Be Visible?**
- Dedicated "Patterns" page in navigation ribbon?
- Settings panel under "Learning" tab?
- Both? (page for browsing, settings for controls)

**3. Management Actions:**
- View pattern details (query, chunks, confidence)
- Delete individual patterns
- Export patterns (backup/sharing)
- Clear all patterns (with confirmation)
- Disable pattern learning temporarily

**4. Relationship to Notes:**
- Should patterns be converted to notes for editing?
- Or keep as structured data in JSON?
- Allow linking patterns to notes for documentation?

**Proposed UI:**
```
Patterns Page (Left Sidebar):
- Time range filter (Last 7 days, 30 days, All time)
- Category filter (Query→Chunk, Domain→Collection, Conceptual)
- Search patterns by keyword

Patterns Page (Center Content):
- Pattern list with:
  - Pattern type badge
  - Trigger/query text
  - Confidence score
  - Usage count
  - Last used timestamp
  - Actions: View Details, Delete, Export

Pattern Details Modal:
- Full pattern data
- Associated chunks/domains/concepts
- Usage history
- Effectiveness metrics
```

**Related Phases:**
- Phase 13b: Pattern Learning UI (will implement this)
- Phase 16: Native Notes (potential integration point)

**Related Files:**
- `PHASE13B_PATTERN_LEARNING_UI.md` (should document this)
- `learners/patterns.py` (backend storage)

---

## Answered Questions

*Completed questions will be moved here with answers documented*

---

## Investigation Template

When adding new questions, use this template:

```markdown
### [Number]. [Brief Title]
**Category:** [Phase Number] ([Phase Name])  
**Priority:** High / Medium / Low  
**Status:** 🔴 Critical / 🟡 Needs Investigation / 🟢 Answered

**Question:**
[Clear statement of the question]

**Context:**
[Background information, why this matters]

**Investigation Steps:**
1. [First step]
2. [Second step]
3. [Third step]

**Proposed Solutions:**
- **Option 1:** [Description]
- **Option 2:** [Description]
- **Option 3:** [Description]

**Related Files:**
- `path/to/file.ext`
- `PHASE_X_DOCUMENT.md`

**Test Case:** (if applicable)
[Code or example demonstrating the question]
```

---

## Notes

- Questions should be investigated before implementing related phases
- Mark questions as 🔴 Critical if they block development
- Document answers inline when resolved
- Move answered questions to "Answered Questions" section
- Update "Last Updated" date when modifying this file

---

**Document Created:** January 28, 2026  
**Status:** Living Document - Update as questions arise and are answered
