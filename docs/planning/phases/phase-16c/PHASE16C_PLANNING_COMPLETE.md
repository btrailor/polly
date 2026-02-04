# Phase 16c Planning Session - COMPLETE ✅

**Date:** January 29, 2026  
**Duration:** Detailed planning and review session  
**Decision:** Option A - Full System with Architect Persona  

---

## What We Discussed

### Your Recall
You correctly remembered that the spec includes **in-window dialogues** and significant chat UI updates for AI note generation. This was accurate - the spec calls for:
- Dynamic inline Q&A components embedded in chat
- Note preview modals
- Mode switcher UI
- Rich interactive components beyond text

### Key Questions Reviewed

We reviewed **7 critical design decisions:**

1. **Chat UI Architecture** - Inline vs sidebar for planning interface
2. **Mode Switching** - How to handle Plan/Build workflow
3. **Template System** - Defaults and storage location
4. **Note Preview** - When and how to edit notes
5. **Intent Detection** - How Polly knows to create notes
6. **Learning Loop** - Whether to include edit tracking
7. **Architecture** - Simplified vs full Architect persona system

### The Big Decision: Architecture

**Three options presented:**

**Option A: Full System (8-10 weeks)**
- Build Phase 11 Multi-Model Router v2 first (4-5 weeks)
- Then build Phase 16c with complete Architect persona (4 weeks)
- Gets proper reusable persona framework
- Full Plan/Build workflow
- No technical debt

**Option B: Simplified (2-3 weeks)**
- Skip persona framework
- Direct note creation flow
- Working faster but may need refactoring

**Option C: Minimal Architect (3-4 weeks)**
- Lightweight persona just for notes
- Gets Plan/Build without full Phase 11

**Your Decision:** Option A - Full System ✅

---

## What This Means

### Timeline
**Total: 8-10 weeks (2-2.5 months)**

**Phase 11: Multi-Model Router v2 + Personas (4-5 weeks)**
- Week 1-2: Router v2 core
- Week 3: Persona framework
- Week 4: Architect persona
- Week 5: Integration & testing

**Phase 16c: AI Note Creation (4 weeks)**
- Week 1: Intent detection + templates
- Week 2: Plan mode integration
- Week 3: Build mode integration
- Week 4: Preview + polish

### What Gets Built

**Phase 11 Deliverables:**
- Complete multi-model router with provider management
- Confidence-based routing (fast/balanced/thorough)
- Token tracking and cost management
- Base persona framework (reusable)
- Architect persona with Plan/Build modes
- Mode switching system
- State management

**Phase 16c Deliverables:**
- Intent detection for note creation requests
- Template system with folder scanning
- 10 default templates (meeting, daily, concept, etc.)
- Inline Q&A UI components in chat
- Plan mode: Question generation and collection
- Build mode: Note generation with templates
- Auto-wikilink injection
- Full-screen preview modal (Preview/Edit/Raw tabs)
- Save to `_Drafts/` workflow
- Integration with Notes page for editing

### Architecture Benefits

**Why Option A is worth the extra time:**

1. **Reusable Foundation**
   - Architect persona can be used for other tasks
   - Easy to add Librarian, Critic, etc. personas later
   - Proper separation of concerns

2. **Sophisticated Workflow**
   - Plan mode: Analyze, ask questions, outline
   - Build mode: Generate, apply template, finalize
   - Clear mental model for users

3. **No Technical Debt**
   - Won't need refactoring when Phase 11 is needed
   - Proper architecture from start
   - Future-proof for agentic features

4. **Better UX**
   - Mode switching gives users control
   - Clear indication of what Polly is doing (planning vs building)
   - More thoughtful note generation

---

## Design Decisions Made

Based on Option A choice, we decided:

### 1. Chat UI: Inline Components ✅
- Questions appear as interactive cards in message stream
- Mode switcher badge in chat header: `🏗️ Architect | Plan Mode`
- Inline forms for answers (don't create separate messages)
- Visual feedback when answers submitted

### 2. Mode Switching ✅
- **Explicit button:** "Switch to Build Mode" in header
- **Auto-suggest:** Offer switch after all questions answered
- **Natural language:** Also accept "ok, build it" as trigger
- Mode badge always visible

### 3. Templates ✅
- **Location:** `~/.polly/notes/_Templates/` folder
- **Defaults:** Ship with 10 templates
- **Customization:** User can add/edit/delete
- **Variables:** Simple `{{var}}` replacement (not full templating engine)

### 4. Preview & Editing ✅
- **Full-screen modal** with three tabs
- **Save to `_Drafts/` first** (never lose work)
- **Then edit in Notes page** (familiar workflow)
- Metadata editable: title, folder, tags

### 5. Intent Detection ✅
- **Hybrid approach:**
  - Explicit: "create a note about X"
  - Implicit: "can you document this?"
  - Context-aware suggestions
- **Confirmation button** before activating Architect
- User can dismiss if incorrect

### 6. Learning Loop ✅
- **Defer to Phase 16d**
- Focus on core functionality first
- Add learning after users request it

### 7. Architecture ✅
- **Full Architect persona** (already decided - Option A)
- Reusable, proper, future-proof

---

## Files & Documentation

**Created during planning:**
1. `PHASE16C_PLANNING_SESSION.md` - All questions and options
2. `PHASE16C_OPTION_A_PLAN.md` - Complete implementation plan
3. Updated `PHASE_CHECKLIST.md` - Next steps clear
4. Updated `CURRENT_STATUS.md` - Status reflects decision

**Existing specs to reference:**
1. `PHASE11_MULTI_MODEL_ENHANCED_V2.md` - Router v2 spec
2. `PHASE11_AGENT_PERSONAS.md` - Persona framework spec
3. `PHASE16C_AI_NOTE_CREATION.md` - Original AI note creation spec

---

## Next Steps

### Immediate
1. ✅ Planning session complete
2. ✅ Decision made (Option A)
3. ✅ Implementation plan created
4. 📋 Review Phase 11 specs in detail
5. 📋 Set up API keys (OpenAI, Anthropic, GitHub)
6. 📋 Start Phase 11 Week 1: Router v2 Foundation

### Week 1 Kickoff
**Phase 11, Week 1: Router v2 Foundation**

**Days 1-2:** Provider abstraction layer
- Create base `Provider` class
- Implement OpenAI provider
- Implement Anthropic provider
- Implement local (Ollama) provider

**Days 3-4:** Confidence-based routing logic
- Define confidence tiers (fast/balanced/thorough)
- Implement routing algorithm
- Add task type classification

**Day 5:** Token tracking system
- Track tokens per provider
- Cost calculation
- Usage reporting

---

## Success Metrics

**Phase 11 Complete When:**
- ✅ Router selects appropriate provider for task
- ✅ Confidence levels route correctly
- ✅ Token usage tracked accurately
- ✅ Fallback works on errors
- ✅ Architect persona can be activated
- ✅ Plan/Build modes work smoothly
- ✅ Mode switching is clear to user

**Phase 16c Complete When:**
- ✅ Detects note creation intent accurately
- ✅ Templates load and match correctly
- ✅ Plan mode asks relevant questions
- ✅ Build mode generates quality notes
- ✅ Wiki-links added correctly
- ✅ Preview modal works flawlessly
- ✅ Save to Drafts workflow is smooth
- ✅ User can create 10+ notes without bugs

**Overall Success:**
- User can say "create a note about X"
- Polly asks clarifying questions
- User switches to Build mode when ready
- Note is generated with proper template
- User reviews, edits, saves
- Process feels natural and helpful

---

## Risk Mitigation

**Timeline Risk:**
- 8-10 weeks is long
- **Mitigation:** Weekly progress reviews, strict milestone tracking

**Complexity Risk:**
- Two major systems at once
- **Mitigation:** Build incrementally, test frequently, keep scope tight

**API Cost Risk:**
- Cloud routing may be expensive during testing
- **Mitigation:** Use local models during development, add rate limiting

**Scope Creep Risk:**
- Easy to add "just one more feature"
- **Mitigation:** Defer all nice-to-haves to Phase 16d/17, stay focused

---

## Questions Answered

**Q: Do we need Phase 11 before Phase 16c?**
A: Yes, Phase 16c depends on Architect persona which is built in Phase 11.

**Q: Can we simplify and do it faster?**
A: Yes (Option B = 2-3 weeks), but you chose Option A for proper architecture.

**Q: Will this work with existing notes system?**
A: Yes, Phase 16 (notes frontend) is already complete. We're building on it.

**Q: What if we want to add more personas later?**
A: Easy! Base framework is reusable. Just create new persona class.

**Q: Can we change our mind later?**
A: Yes, but best to commit now to avoid wasted work. Option A is future-proof.

---

## Ready to Start?

**Next action:** Start Phase 11 Week 1

**Before starting, confirm:**
1. API keys ready? (OpenAI, Anthropic, optional GitHub)
2. Comfortable with 8-10 week timeline?
3. Any last-minute additions/removals?
4. Want detailed week-by-week task breakdown, or start building?

**When ready, say:** "Let's start Phase 11 Week 1" and we'll begin implementation!

---

**Planning Session Status:** ✅ COMPLETE  
**Decision:** Option A - Full System  
**Next:** Phase 11, Week 1, Day 1 - Provider Abstraction Layer
