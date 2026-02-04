# Phase 16c Implementation Plan - Option A (Full System)

**Date:** January 29, 2026  
**Decision:** Full Architect Persona System  
**Total Duration:** 8-10 weeks  
**Approach:** Phase 11 (Multi-Model Router v2) → Phase 16c (AI Note Creation)

---

## Executive Summary

We're building the **complete system** as originally spec'd:
- Phase 11 Multi-Model Router v2 with Architect persona framework (4-5 weeks)
- Phase 16c AI Note Creation using Architect (4 weeks)
- Total: 8-10 weeks to fully working AI note creation

**Why this approach:**
- Proper architecture that's reusable for other personas (Librarian, Critic, etc.)
- Full Plan/Build workflow for sophisticated note creation
- Foundation for future agentic features
- No technical debt or refactoring needed later

---

## Two-Phase Breakdown

### Phase 11: Multi-Model Router v2 + Architect Persona (4-5 weeks)

**See:** `PHASE11_MULTI_MODEL_ENHANCED_V2.md` and `PHASE11_AGENT_PERSONAS.md`

**What gets built:**

#### Week 1-2: Router v2 Core
- Provider management (OpenAI, Anthropic, GitHub Copilot, Local)
- Confidence-based routing (fast/balanced/thorough)
- Token tracking and cost management
- Fallback logic and error handling

#### Week 3: Persona Framework
- Base `AgentPersona` class
- Mode switching system
- Context management
- State persistence across conversation

#### Week 4: Architect Persona
- Plan mode implementation
- Build mode implementation
- Mode-specific prompts
- Model routing per mode (Plan→Sonnet, Build→Opus)

#### Week 5: Integration & Testing
- Router v2 integration with existing query system
- Architect persona testing
- API endpoints for persona activation
- Documentation

**Deliverables:**
- `/core/router_v2/` - New router system
- `/core/personas/base.py` - Base persona class
- `/core/personas/architect.py` - Architect implementation
- Updated `/interfaces/server.py` - New endpoints
- Tests and documentation

**Result:** Working Architect persona that can be activated for any task, with proper Plan/Build workflow.

---

### Phase 16c: AI Note Creation (4 weeks)

**Builds on Phase 11's Architect persona**

#### Week 1: Intent Detection + Template System
- Note creation intent classifier
- Template folder scanning
- Template pattern extraction
- Template matching algorithm

#### Week 2: Plan Mode Integration
- Clarifying question generation
- Dynamic inline Q&A UI in chat
- Question/answer flow management
- Outline generation

#### Week 3: Build Mode Integration
- Note content generation
- Template application
- Auto-wikilink injection
- Note object creation

#### Week 4: Preview, Save & Polish
- Full-screen preview modal (Preview/Edit/Raw tabs)
- Save to `_Drafts/` workflow
- Edit in Notes page integration
- Error handling and edge cases

**Deliverables:**
- `/core/intent/note_detector.py` - Intent classification
- `/core/templates/manager.py` - Template system
- `/core/notes/generator.py` - Note generation
- Frontend: Inline Q&A components
- Frontend: Note preview modal
- Frontend: Mode switcher UI
- 5-10 default templates in `_Templates/`
- Full documentation

**Result:** Complete AI note creation system with Plan/Build workflow.

---

## Design Decisions (Based on Option A)

### 1. Chat UI: Inline Components ✅
- Questions appear as interactive cards in message stream
- Mode switcher in chat header: `🏗️ Architect | Plan Mode [Switch to Build ▼]`
- Inline forms for answering questions
- Visual feedback when answers submitted

### 2. Mode Switching ✅
- **Primary:** Explicit mode switch button in chat header
- **Secondary:** Auto-suggest switch after all questions answered
- **Tertiary:** Natural language triggers ("ok, build it now")
- Mode badge visible in chat header at all times

### 3. Templates ✅
- **Storage:** `~/.polly/notes/_Templates/` folder in vault
- **Defaults:** Ship with 10 templates:
  1. `meeting-note.md` - Meeting notes
  2. `daily-note.md` - Daily journal
  3. `concept-note.md` - Concepts/ideas
  4. `project-overview.md` - Project documentation
  5. `decision-record.md` - Decision logs
  6. `person-note.md` - Person/contact
  7. `task-note.md` - Task planning
  8. `research-note.md` - Research summaries
  9. `book-note.md` - Book notes
  10. `retrospective.md` - Retrospectives
- **Customization:** Settings UI for template folder location
- **Override:** User can add/edit/delete templates

### 4. Note Preview & Editing ✅
- **Full-screen modal** with three tabs (Preview, Edit, Raw)
- **Save to `_Drafts/` first** (never lose work)
- **Metadata editable:** Title, folder, tags
- **Actions:**
  - "Save to Drafts" - Saves and closes modal
  - "Open in Notes" - Opens in Notes page for full editing
  - "Cancel" - Discards note

### 5. Intent Detection ✅
- **Hybrid approach:**
  - Explicit triggers: "create a note about X"
  - Implicit patterns: "can you document this?"
  - Context-aware: long detailed answer → suggest "save as note?"
- **Confirmation:** Show button: "📝 Create note about X?" before activating Architect
- **Skip option:** User can dismiss suggestion

### 6. Learning Loop ✅
- **Defer to Phase 16d**
- Focus on core workflow first
- Add learning after users have used it and request improvements

### 7. Architecture ✅
- **Full Architect persona system** (chosen)
- Reusable for future personas
- Proper separation of concerns
- No technical debt

---

## Implementation Timeline

### Month 1: Phase 11 Router v2 + Personas (Weeks 1-5)

**Week 1: Router v2 Foundation**
- Days 1-2: Provider abstraction layer
- Days 3-4: Confidence-based routing logic
- Day 5: Token tracking system

**Week 2: Router v2 Core Features**
- Days 6-7: Fallback logic and error handling
- Days 8-9: Cost management and budgets
- Day 10: Integration with existing query system

**Week 3: Persona Framework**
- Days 11-12: Base `AgentPersona` class
- Days 13-14: Mode switching system
- Day 15: Context and state management

**Week 4: Architect Persona**
- Days 16-17: Plan mode implementation
- Days 18-19: Build mode implementation
- Day 20: Mode-specific model routing

**Week 5: Integration & Testing**
- Days 21-22: API endpoints for personas
- Days 23-24: Testing and bug fixes
- Day 25: Documentation

**Checkpoint:** Working Architect persona, ready for Phase 16c

---

### Month 2: Phase 16c AI Note Creation (Weeks 6-9)

**Week 6: Intent + Templates**
- Days 26-27: Intent detection classifier
- Days 28-29: Template scanning and extraction
- Day 30: Template matching algorithm

**Week 7: Plan Mode Integration**
- Days 31-32: Question generation logic
- Days 33-34: Inline Q&A UI components
- Day 35: Question/answer flow management

**Week 8: Build Mode Integration**
- Days 36-37: Note content generation
- Days 38-39: Template application and wiki-links
- Day 40: Note object creation

**Week 9: Preview + Polish**
- Days 41-42: Preview modal UI
- Days 43-44: Save to Drafts workflow
- Day 45: Error handling and edge cases

**Week 10 (Optional): Buffer & Documentation**
- Days 46-48: Bug fixes, testing, polish
- Days 49-50: User documentation and examples

---

## Key Milestones

### Milestone 1: Router v2 Working (End of Week 2)
- Can route queries to different providers based on confidence
- Token tracking functional
- Fallback logic works

### Milestone 2: Architect Persona Functional (End of Week 5)
- Can activate Architect persona
- Plan mode asks questions
- Build mode generates content
- Mode switching works

### Milestone 3: Intent Detection Working (End of Week 6)
- Detects "create a note" requests
- Shows confirmation button
- Activates Architect when confirmed

### Milestone 4: Template System Working (End of Week 7)
- Scans `_Templates/` folder
- Extracts template patterns
- Matches appropriate template to request
- 10 default templates available

### Milestone 5: End-to-End Note Creation (End of Week 9)
- User requests note
- Architect asks questions in Plan mode
- User switches to Build mode
- Polly generates note with template
- Preview modal shows
- User saves to Drafts
- Can edit in Notes page

### Milestone 6: Production Ready (End of Week 10)
- All edge cases handled
- Error messages helpful
- Performance acceptable (<5s generation)
- Documentation complete

---

## Dependencies & Prerequisites

### Technical Dependencies
- ✅ Phase 16 (Notes Frontend) - Already complete
- ✅ Phase 1.5 (Domain Configuration) - Already complete
- ✅ Phase 2 (RAG System) - Already complete
- ⏳ Phase 11 (Multi-Model Router v2) - To be built in Weeks 1-5
- ⏳ Architect Persona Framework - To be built in Weeks 3-5

### External Dependencies
- OpenAI API access (for Opus/Sonnet routing)
- Anthropic API access (for Claude models)
- GitHub Copilot API access (optional)
- Ollama running locally (for fast tier)

### User Requirements
- Notes vault configured (`~/.polly/notes/`)
- At least one domain set up (Phase 1.5)
- API keys configured for cloud providers

---

## Success Criteria

### Phase 11 Success Criteria
- ✅ Router can select appropriate provider based on task
- ✅ Confidence levels (fast/balanced/thorough) route correctly
- ✅ Token usage tracked and reported
- ✅ Fallback works when primary provider fails
- ✅ Architect persona can be activated
- ✅ Plan mode generates relevant questions
- ✅ Build mode produces quality content
- ✅ Mode switching is smooth and clear

### Phase 16c Success Criteria
- ✅ Detects note creation intent with >90% accuracy
- ✅ Templates load and match correctly
- ✅ Questions are relevant and helpful (3-5 per note)
- ✅ Generated notes follow template structure
- ✅ Wiki-links added to related notes
- ✅ Preview modal works on all browsers
- ✅ Notes save to `_Drafts/` successfully
- ✅ Edit in Notes page works seamlessly
- ✅ Generation time <5 seconds (balanced tier) or <10 seconds (thorough tier)
- ✅ User can create 10 notes without encountering a bug

---

## Files to Create/Modify

### Phase 11 Files

**New Files:**
- `/core/router_v2/provider.py` - Provider abstraction
- `/core/router_v2/router.py` - Main router logic
- `/core/router_v2/confidence.py` - Confidence scoring
- `/core/router_v2/token_tracker.py` - Token usage tracking
- `/core/personas/base.py` - Base persona class
- `/core/personas/architect.py` - Architect implementation
- `/tests/test_router_v2.py` - Router tests
- `/tests/test_personas.py` - Persona tests

**Modified Files:**
- `/core/polly.py` - Integrate Router v2
- `/interfaces/server.py` - New persona endpoints
- `/config.yaml` - Router v2 configuration

### Phase 16c Files

**New Files:**
- `/core/intent/note_detector.py` - Intent classification
- `/core/templates/manager.py` - Template system
- `/core/templates/applicator.py` - Template application
- `/core/notes/generator.py` - Note generation
- `/core/notes/qa_flow.py` - Question/answer flow
- `/electron-app/src/renderer/note-creation-ui.js` - Inline UI components
- `/electron-app/src/renderer/note-preview.js` - Preview modal
- `/electron-app/src/renderer/styles/note-creation.css` - Styling
- `~/.polly/notes/_Templates/*.md` - 10 default templates
- `/tests/test_intent_detection.py` - Intent tests
- `/tests/test_templates.py` - Template tests
- `/tests/test_note_generation.py` - Generation tests

**Modified Files:**
- `/core/polly.py` - Intent detection integration
- `/interfaces/server.py` - Note creation endpoints
- `/electron-app/src/renderer/app.js` - Persona UI, mode switcher
- `/electron-app/src/renderer/index.html` - UI components
- `/electron-app/src/renderer/styles/main.css` - Global styles

**Total:** ~25 new files, ~10 modified files, ~10,000-12,000 lines of code

---

## Risk Assessment

### High Risk
- **Complexity:** Two major systems (Router v2 + Note Creation) = high chance of bugs
- **Timeline:** 8-10 weeks is long, scope creep risk
- **Dependencies:** If Phase 11 takes longer, Phase 16c delayed

**Mitigation:**
- Strict milestone tracking
- Weekly progress reviews
- Build incrementally, test frequently
- Keep scope tight, defer nice-to-haves

### Medium Risk
- **API costs:** Cloud routing may be expensive during testing
- **Template quality:** Default templates may not suit all users
- **Performance:** Note generation may be slow with thorough tier

**Mitigation:**
- Use local models during development
- Design templates to be easily customizable
- Profile and optimize generation code

### Low Risk
- **UI complexity:** Inline components are well-spec'd
- **Note saving:** Built on proven Phase 16 foundation
- **Wiki-links:** BacklinksIndex already works

---

## Next Steps

### Immediate (This Week)
1. ✅ Planning session complete - Decision made (Option A)
2. 📋 Review Phase 11 specs in detail
3. 📋 Set up project tracking (milestones, tasks)
4. 📋 Start Phase 11 Week 1: Router v2 Foundation

### Week 1 Kickoff
- Read `PHASE11_MULTI_MODEL_ENHANCED_V2.md` thoroughly
- Read `PHASE11_AGENT_PERSONAS.md` thoroughly
- Create todo list for Phase 11 Week 1
- Set up API keys for OpenAI, Anthropic, GitHub Copilot
- Begin provider abstraction layer implementation

---

## Questions Before We Start

**Q1:** Do you have API keys set up for:
- OpenAI (for GPT-4)
- Anthropic (for Claude Opus/Sonnet)
- GitHub Copilot (optional)

**Q2:** Are you comfortable with the 8-10 week timeline?

**Q3:** Any other features you want to add/remove before we start?

**Q4:** Should we create a detailed week-by-week task breakdown before starting, or dive in?

---

**Ready to begin Phase 11 Week 1?**
