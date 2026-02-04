# Phase 23: Curriculum Learning System

**Status:** ✅ IMPLEMENTATION COMPLETE  
**Priority:** High (Tier 1 - Core Intelligence)  
**Actual Effort:** ~18 hours (Feb 3, 2026)  
**Complexity:** High

**Implementation Date:** February 3, 2026  
**All 6 Phases Completed:** Core Infrastructure, Templates, Engagement UI, Section Enrichment, Progress Visualization, Guided Learning

**Prerequisites:** 
- Phase 14 (Mental Models) ✅ Complete
- Phase 11c (Agent Personas - Professor) ✅ Complete
- Phase 16 (Native Notes) ✅ Complete
- Phase 22 (Teaching Mode) ✅ Complete (more advanced than documented)

---

## Executive Summary

Transform Polly's learning system from passive outline generation to active curriculum guidance. Currently, Professor can generate learning path outlines in chat, but these exist only as text with no structure, enrichment, progress tracking, or guided learning experience. Phase 23 creates a complete curriculum system with:

- **Structured curricula** stored in vault (separate from notes)
- **Domain-based templates** (not topic-specific)
- **Heavy enrichment** (explanations, diagrams, exercises, resources)
- **Hybrid smart enrichment** (auto-enrich current section on demand)
- **Subheading-level progress tracking**
- **Sessions + Ambient awareness** learning flow
- **Visual curriculum UI** with progress tracking

---

## Problem Statement

### Current State

**What Exists:**
- ✅ `LearningTracker` - Tracks topics, mastery levels (1-5), spaced repetition
- ✅ Professor curriculum mode - Generates learning path outlines in chat
- ✅ Skill packages - Curated content in `vault/.polly/skills/`
- ✅ Learning page UI - Stats dashboard, session view
- ✅ Visualization system - Diagrams, exercises

**What's Missing (The Gaps):**
- ❌ **No curriculum object model** - Outlines exist only as chat text, not structured data
- ❌ **No enrichment workflow** - Outlines don't become detailed lesson plans
- ❌ **No curriculum presentation UI** - Can't view/track progress through a learning path
- ❌ **No guided learning experience** - Professor doesn't know you're "following a curriculum"
- ❌ **No bridge** from chat → structured curriculum → active guidance

### User Pain Points

**Current Workflow:**
1. User: "Create a learning plan for React"
2. Professor: Generates text outline (8 weeks of content)
3. User: Now what? The outline is just text in chat
4. User: Must manually follow outline, track progress, build materials

**Problems:**
- Outline disappears in chat history
- No way to check progress
- No detailed materials (diagrams, exercises)
- Professor doesn't know user is "following a curriculum"
- No proactive guidance or next-step suggestions

---

## Solution Architecture

### Design Decisions (Confirmed)

#### 1. Curriculum Storage
- **Location:** `vault/.polly/curricula/` (separate from notes)
- **Format per curriculum:**
  - `CURRICULUM.md` - Human-readable markdown
  - `curriculum.json` - Machine-readable structure
  - `progress.json` - Progress tracking data
  - `resources/` - Curriculum-specific materials (diagrams, exercises, examples)

#### 2. Template Strategy
**5 domain-based templates** (not topic-specific):
1. **Programming Language** - Learn any language (Python, JavaScript, Lua, etc.)
2. **Framework/Library** - Learn any framework (React, Flask, Express, etc.)
3. **Skill Acquisition** - Learn tools/platforms (Monome Norns, Ableton, Figma, etc.)
4. **Problem-Solving** - Solve specific problems (optimize API, build synth engine, etc.)
5. **Domain Exploration** - Explore broad domains (ML, Audio DSP, Web3, etc.)

**Template Selection:**
- Professor auto-detects best template based on user request
- Shows recommended template in selector
- User can override and choose different template
- Templates use hybrid customization (keep structure, adapt content heavily)
- Template metadata visible in curriculum ("Based on Framework Template")
- **Extensible:** Users can save curricula as custom templates (future Phase 23b)

#### 3. Enrichment Strategy
- **Hybrid Smart Enrichment:**
  - Auto-enrich current section when user starts working on it
  - Heavy enrichment (explanations + diagrams + exercises + resources)
  - Triggered on-demand (~10-30s loading time)
  - Cached (section.enriched = true, no re-generation)
  - Can manually request enrichment of future sections

#### 4. Learning Flow
- **Sessions + Ambient:**
  - **Formal sessions** for structured learning (explicit start/end)
  - **Ambient awareness** for context-aware help outside sessions
  - Supports both linear and exploratory learning
  - Session indicator in UI shows current section

#### 5. Progress Tracking
- **Subheading-level tracking:**
  - Track each section (week-1.1, week-1.2, etc.)
  - Status: `not_started`, `in_progress`, `completed`, `skipped`
  - Metadata per section:
    - Time spent (minutes)
    - Mastery level (1-5 self-reported)
    - Struggles (text notes)
    - Breakthroughs (text notes)
    - Notes created (linked files)
  - Overall stats: completion %, total time, average mastery

#### 6. Creation Flow
1. User requests curriculum in chat
2. Professor detects template, generates outline
3. **Review/edit dialog** appears with:
   - Left: Editable markdown textarea
   - Right: Preview (title, goal, duration, section count, structure tree)
   - Actions: "Ask for Changes", "Cancel", "Save & Activate"
4. User can edit text OR ask Professor for changes
5. User clicks "Save & Activate" → curriculum created in vault
6. Curriculum starts in "draft" status until activated

---

## Implementation Phases

### Phase 1: Core Infrastructure (4-6 hours)
**Goal:** Backend curriculum object model and storage

**Components:**

1. **`learners/curriculum_manager.py`** (NEW)
   - `CurriculumSection` dataclass
     - Fields: id, title, type, concepts, estimated_time, order, parent_id
     - Enrichment: resources, exercises, diagrams, examples
     - Progress: status, timestamps, time_spent, mastery_level, notes, struggles, breakthroughs
   - `Curriculum` dataclass
     - Metadata: id, title, goal, status, created, last_updated
     - Structure: sections list, current_section_id
     - Stats: completion_percentage, total_time, mastery_average
     - References: curriculum_template_id, skills_referenced
   - `CurriculumManager` class
     - CRUD: create, get, list, save, delete
     - Lifecycle: activate, pause, complete
     - Sections: start_section, complete_section, get_next_section
     - Enrichment: enrich_section, is_section_enriched
     - Progress: get_progress_summary, get_completion_percentage

2. **`interfaces/server.py`** (add endpoints)
   - `GET /polly/curricula/list` - List curricula (with optional status filter)
   - `GET /polly/curricula/{id}` - Get full curriculum details
   - `POST /polly/curricula/create` - Create new curriculum
   - `POST /polly/curricula/{id}/activate` - Activate (draft → active)
   - `POST /polly/curricula/{id}/sections/{section}/start` - Start section
   - `POST /polly/curricula/{id}/sections/{section}/complete` - Complete with reflection
   - `GET /polly/curricula/{id}/progress` - Get progress summary
   - `POST /polly/curricula/{id}/sections/{section}/enrich` - Enrich section (Phase 4)
   - `POST /polly/curricula/{id}/session/start` - Start formal session (Phase 6)
   - `POST /polly/curricula/session/end` - End session (Phase 6)

3. **`core/polly.py`** (integration)
   - Initialize `CurriculumManager` in `Polly.__init__`
   - Pass to `PersonaManager` for Professor access

4. **`electron-app/src/renderer/app.js`** (add API functions)
   - `fetchCurricula(status)` - Fetch list
   - `getCurriculum(id)` - Fetch details
   - `createCurriculum(title, goal, sections, metadata)` - Create
   - `activateCurriculum(id)` - Activate
   - `startSection(curriculumId, sectionId)` - Start
   - `completeSection(curriculumId, sectionId, reflection)` - Complete

**Files Created/Modified:**
- NEW: `learners/curriculum_manager.py` (~600 lines)
- MOD: `core/polly.py` (+30 lines initialization)
- MOD: `interfaces/server.py` (+150 lines endpoints)
- MOD: `electron-app/src/renderer/app.js` (+100 lines API functions)

**Testing:**
- Create curriculum via API → verify saved to vault
- Load curriculum → verify data structure
- Start/complete sections → verify progress updates

---

### Phase 2: Template System (3-4 hours)
**Goal:** Domain-based templates with auto-detection

**Components:**

1. **`learners/curriculum_template_manager.py`** (NEW)
   - `CurriculumTemplateManager` class
     - Load templates from `vault/.polly/curriculum-templates/`
     - `list_templates(category)` - List available
     - `get_template(template_id)` - Get specific template
     - `create_from_template(template_id, customizations)` - Instantiate

2. **`vault/.polly/curriculum-templates/`** (NEW directory)
   Create 5 template directories:
   - `programming-language/` - TEMPLATE.md + template.json
   - `framework-library/` - TEMPLATE.md + template.json
   - `skill-acquisition/` - TEMPLATE.md + template.json
   - `problem-solving/` - TEMPLATE.md + template.json
   - `domain-exploration/` - TEMPLATE.md + template.json

   **Template JSON Structure:**
   ```json
   {
     "id": "programming-language",
     "name": "Programming Language",
     "category": "programming",
     "description": "Learn any programming language systematically",
     "customization_questions": [
       "Which language are you learning?",
       "What's your programming experience?",
       "What do you want to build?"
     ],
     "structure": [
       {
         "id": "week-1",
         "title": "Syntax & Fundamentals",
         "sections": [...]
       }
     ]
   }
   ```

3. **`core/personas/implementations/professor.py`** (enhance)
   - `detect_template(goal)` - Analyze user request, return recommended template_id
     - Use keyword patterns (e.g., "learn Python" → programming-language)
     - Return template_id + confidence score
   - `customize_template(template, user_responses)` - Adapt template to specific topic
     - Replace placeholders
     - Adjust sections based on experience level
     - Add/remove sections for focus areas

4. **`interfaces/server.py`** (add endpoints)
   - `GET /polly/templates/list` - List templates
   - `GET /polly/templates/{id}` - Get template details
   - `POST /polly/templates/detect` - Detect template from goal
   - `POST /polly/templates/{id}/customize` - Customize template

5. **`electron-app/src/renderer/app.js`** (add template functions)
   - `fetchTemplates()` - Get available templates
   - `detectTemplate(goal)` - Get recommended template
   - `customizeTemplate(templateId, answers)` - Customize template

**Files Created/Modified:**
- NEW: `learners/curriculum_template_manager.py` (~300 lines)
- NEW: `vault/.polly/curriculum-templates/*/` (5 template packages, ~200 lines each)
- MOD: `core/personas/implementations/professor.py` (+200 lines template detection)
- MOD: `interfaces/server.py` (+80 lines endpoints)
- MOD: `electron-app/src/renderer/app.js` (+60 lines functions)

**Template Example: Programming Language**

**Structure:**
```
Week 1: Syntax & Fundamentals
  1.1 Basic syntax and data types
  1.2 Control flow (if/loops)
  1.3 Functions and scope

Week 2: Core Concepts
  2.1 Data structures
  2.2 Error handling
  2.3 Modules/imports

Week 3: Paradigms
  3.1 Object-oriented features
  3.2 Functional features
  3.3 Best practices

Week 4: Standard Library
  4.1 File I/O
  4.2 String/data manipulation
  4.3 Common utilities

Week 5-6: Practical Applications
  5.1 Build small CLI tool
  5.2 Work with external libraries
  5.3 Testing and debugging

Week 7-8: Real Project
  7.1 Domain-specific project
  7.2 Code review and refinement
```

**Customization Questions:**
- What language are you learning?
- What's your prior programming experience?
- What do you want to build with it?
- Any specific areas of focus? (web, data, automation, etc.)

**Testing:**
- Request "learn Python" → verify programming-language template recommended
- Request "learn React" → verify framework-library template recommended
- Customize template → verify sections adapted to specific topic

---

### Phase 3: Creation & Review Flow (3-4 hours)
**Goal:** Generate outline → Review dialog → Save

**Components:**

1. **`core/personas/implementations/professor.py`** (enhance curriculum mode)
   - Check if iteration on existing outline OR new creation
   - **New creation flow:**
     - Detect template (from Phase 2)
     - Ask customization questions
     - Generate outline using template
     - Parse outline into structured data
     - Return `review_curriculum` PersonaAction
   - `_parse_curriculum_outline(text)` - Extract sections from markdown
     - Regex for `## Week X`, `### X.Y Section`
     - Extract concepts, estimated times
     - Build section structure with IDs
   - **PersonaAction: review_curriculum**
     ```python
     PersonaAction(
       type="review_curriculum",
       data={
         "curriculum_outline": "markdown text",
         "curriculum_data": {
           "title": "...",
           "goal": "...",
           "template_id": "programming-language",
           "sections": [...]
         }
       }
     )
     ```

2. **`electron-app/src/renderer/index.html`** (add dialog)
   - **Curriculum Review Dialog:**
     - Left panel: Editable markdown textarea
     - Right panel: Preview (title, goal, duration, section count)
     - Structure tree: Collapsible weeks/sections with time estimates
     - Footer buttons:
       - "Cancel" - Close dialog
       - "Ask for Changes" - Send feedback to Professor
       - "Save & Activate" - Create curriculum

3. **`electron-app/src/renderer/app.js`** (add handlers)
   - `handlePersonaAction()` - Add case for `review_curriculum`
   - `showCurriculumReviewDialog(data)` - Display dialog
   - `parseCurriculumOutline(text)` - Parse edited markdown
   - `updateCurriculumPreview(data)` - Update preview panel
   - `saveCurriculum(outline, data)` - Call create API
   - Button handlers for cancel/changes/save

4. **`electron-app/src/renderer/styles/main.css`** (add styles)
   - `.curriculum-review-modal` - Dialog layout
   - `.curriculum-outline-panel` - Left editor
   - `.curriculum-preview-panel` - Right preview
   - `.structure-tree` - Section hierarchy
   - `.time-badge` - Estimated time pills

**Files Created/Modified:**
- MOD: `core/personas/implementations/professor.py` (+300 lines curriculum generation)
- MOD: `electron-app/src/renderer/index.html` (+150 lines dialog UI)
- MOD: `electron-app/src/renderer/app.js` (+250 lines handlers)
- MOD: `electron-app/src/renderer/styles/main.css` (+100 lines styles)

**Testing:**
- Create "learn Python" → review dialog appears
- Edit outline in textarea → preview updates
- Click "Ask for Changes" → sends to Professor
- Click "Save & Activate" → curriculum created in vault

---

### Phase 4: Section Enrichment Engine (4-5 hours)
**Goal:** Heavy enrichment triggered on section start

**Components:**

1. **`core/personas/implementations/professor.py`** (add method)
   - `enrich_section(curriculum_id, section_id, section_data)` - Async method
     - Build enrichment prompt (request diagrams, examples, exercises, etc.)
     - Check for related skill packages
     - Generate enrichment using THOROUGH confidence (best model)
     - Parse LLM response into structured data
     - Incorporate skill package materials if found
     - Return enrichment dict
   - `_parse_enrichment_response(content)` - Extract structured data from LLM
     - Parse JSON or structured text
     - Extract: explanation, diagrams, examples, exercises, resources, assessment_criteria

   **Enrichment Output Structure:**
   ```python
   {
     "status": "success",
     "enrichment": {
       "explanation": "detailed markdown text",
       "diagrams": [
         {"type": "mermaid", "source": "graph TD...", "caption": "..."}
       ],
       "examples": [
         {"title": "...", "code": "...", "explanation": "..."}
       ],
       "exercises": [
         {"id": "ex-1", "title": "...", "description": "...", 
          "starter_code": "...", "solution": "...", "test_cases": [...]}
       ],
       "resources": [
         {"type": "skill_package", "name": "...", "path": "..."},
         {"type": "documentation", "url": "...", "title": "..."}
       ],
       "assessment_criteria": [
         "You can explain X to others",
         "You can build Y without help"
       ]
     }
   }
   ```

2. **`interfaces/server.py`** (endpoint already added in Phase 1)
   - `POST /polly/curricula/{id}/sections/{section}/enrich`
     - Call `Professor.enrich_section()`
     - Save enrichment to `CurriculumManager`
     - Mark `section.enriched = True`

3. **`electron-app/src/renderer/app.js`** (add display functions)
   - `startCurriculumSection(curriculumId, sectionId)` - Unified start flow
     - Call start API
     - Show loading message
     - Call enrich API
     - Display enriched materials
   - `displaySectionMaterials(curriculumId, sectionId, enrichment)` - Render in session view
     - Section header with title, badge
     - Explanation (formatted markdown)
     - Diagrams (with zoom controls)
     - Examples (code blocks with syntax highlighting)
     - Exercises (interactive UI)
     - Assessment criteria checklist
     - "Mark Complete" button
   - **Loading UX:**
     - Show spinner: "Enriching section with materials..."
     - Progress indicator if possible
     - Cancel button (optional)

**Files Created/Modified:**
- MOD: `core/personas/implementations/professor.py` (+400 lines enrichment)
- MOD: `interfaces/server.py` (endpoint already added in Phase 1)
- MOD: `electron-app/src/renderer/app.js` (+300 lines display)

**Testing:**
- Start section → verify enrichment API called
- Check vault → verify enrichment saved to curriculum.json
- Verify UI shows: explanation, diagrams, examples, exercises
- Start same section again → verify uses cached enrichment (no re-generate)

---

### Phase 5: Progress Tracking & UI (5-6 hours)
**Goal:** Visualize curricula and track progress

**Components:**

1. **`electron-app/src/renderer/index.html`** (enhance Learning page)
   - **Sidebar additions:**
     - "Active Curricula" section above stats
     - Curriculum cards with mini progress bars
     - "View All Curricula" button
   - **Main area additions:**
     - **Curriculum Detail View** (new)
       - Header: title, back button, pause/continue buttons
       - Progress bar: completion %, time spent
       - Curriculum structure: collapsible weeks/sections with status icons
     - Keep existing: Dashboard, Session View

2. **`electron-app/src/renderer/app.js`** (add UI functions)
   - `loadActiveCurricula()` - Fetch and display in sidebar
   - `showCurriculumDetail(curriculumId)` - Show detail view
   - `buildCurriculumStructure(curriculum)` - Build week/section tree
     - Group sections by parent (weeks)
     - Status icons: ⭕ not started, ⏳ in progress, ✅ completed
     - Click section to start
   - `completeCurriculumSection(curriculumId, sectionId)` - Completion flow
     - Prompt for reflection (mastery, struggles, breakthroughs)
     - Submit to API
     - Show success notification
     - Ask about continuing to next section
   - `getNextSection(curriculumId)` - Find next uncompleted section

3. **`electron-app/src/renderer/styles/main.css`** (add curriculum UI styles)
   - `.active-curricula-section` - Sidebar section
   - `.curriculum-card` - Curriculum card with progress bar
   - `.curriculum-detail-view` - Main detail view
   - `.curriculum-progress-bar` - Overall progress visualization
   - `.curriculum-structure` - Week/section tree
   - `.curriculum-week` - Week container
   - `.curriculum-section` - Section row with status icon
   - `.section-icon` - Status indicator styling
   - Status colors: grey (not started), blue (in progress), green (completed)

**Progress Calculation:**
- Frontend calculates live from `curriculum.sections` array
- Backend recalculates on save
- Show: X/Y sections complete, completion %, total time, avg mastery

**Files Created/Modified:**
- MOD: `electron-app/src/renderer/index.html` (+200 lines UI)
- MOD: `electron-app/src/renderer/app.js` (+400 lines functions)
- MOD: `electron-app/src/renderer/styles/main.css` (+150 lines styles)

**Testing:**
- Open Learning page → verify active curricula shown in sidebar
- Click curriculum card → detail view appears
- Verify progress bar accurate
- Verify section tree shows correct statuses
- Complete section with reflection → verify progress updates in real-time
- Complete section → verify "next section?" prompt appears

---

### Phase 6: Guided Learning (Sessions + Ambient) (3-4 hours)
**Goal:** Professor context-aware guidance

**Components:**

1. **`core/personas/implementations/professor.py`** (enhance)
   - Add instance variable: `active_curriculum_session` (dict or None)
   - `start_curriculum_session(curriculum_id, section_id)` - Enter session mode
     - Store session context in instance
     - Log session start
   - `end_curriculum_session()` - Exit session mode
     - Calculate session duration
     - Clear session context
   - `_get_active_curricula_for_user()` - Query `CurriculumManager`
     - Return list of active curricula for ambient awareness
   - **Enhance `process(context)`:**
     - Add curriculum context to `PersonaContext` metadata
     - Session context if in session
     - Active curricula list for ambient mode
   - **Enhance mode methods (explain, socratic, etc.):**
     - Check for curriculum context in metadata
     - Prefix responses with context if relevant
     - Example: "[Within week-1.2] Your question about..."
     - Example: "(This relates to your Monome Norns curriculum - Week 2)"

2. **`interfaces/server.py`** (endpoints added in Phase 1)
   - Already defined: `session/start`, `session/end`

3. **`electron-app/src/renderer/app.js`** (enhance session flow)
   - Update `startCurriculumSection()`:
     - Call session start API before displaying materials
     - Store session context in window global
   - `showSessionIndicator(curriculumId, sectionId)` - Display in UI
     - Floating indicator: "📚 Learning: week-1.2"
     - "End Session" button
   - `endCurriculumSession()` - End session flow
     - Call session end API
     - Remove indicator
     - Return to curriculum detail view
   - Update `completeCurriculumSection()`:
     - Automatically end session on completion
     - Offer to start next section (which starts new session)
   - **Session Indicator UI:**
     - Floating element (top-right or bottom-right)
     - Shows current section
     - End session button
     - Non-intrusive but visible

**Ambient Awareness Flow:**
- User not in session, asks question
- Professor checks active curricula
- If question relates to curriculum topic, adds context to response
- Doesn't interrupt flow, just adds helpful context

**Files Created/Modified:**
- MOD: `core/personas/implementations/professor.py` (+150 lines session management)
- MOD: `interfaces/server.py` (endpoints already added in Phase 1)
- MOD: `electron-app/src/renderer/app.js` (+200 lines session UI)
- MOD: `electron-app/src/renderer/styles/main.css` (+50 lines session indicator)

**Testing:**
- Start section → verify session API called, indicator appears
- Ask Professor question → verify response contextualized
- End session → verify indicator removed, session ended
- Complete section → verify session auto-ended, next section offered
- Ask unrelated question → verify ambient context added if relevant

---

## File Structure Summary

### New Backend Files
```
core/
├── learners/
│   ├── curriculum_manager.py          (Phase 1) - 600 lines
│   └── curriculum_template_manager.py (Phase 2) - 300 lines

vault/.polly/
├── curricula/                          (Phase 1)
│   └── {curriculum-id}/
│       ├── CURRICULUM.md
│       ├── curriculum.json
│       ├── progress.json
│       └── resources/
│
└── curriculum-templates/               (Phase 2)
    ├── programming-language/
    ├── framework-library/
    ├── skill-acquisition/
    ├── problem-solving/
    └── domain-exploration/
```

### Modified Files
```
interfaces/server.py        (Phases 1, 2: add endpoints) +280 lines
core/polly.py              (Phase 1: init CurriculumManager) +30 lines
core/personas/implementations/professor.py  (Phases 2, 3, 4, 6: enhancements) +1050 lines
electron-app/src/renderer/index.html       (Phases 3, 5: add UI) +350 lines
electron-app/src/renderer/app.js           (Phases 1, 3, 4, 5, 6: add functions) +1410 lines
electron-app/src/renderer/styles/main.css  (Phases 3, 5: add styles) +300 lines
```

### Total Lines of Code
- **New files:** ~900 lines
- **Modified files:** ~3,420 lines
- **Template content:** ~1,000 lines (5 templates)
- **Total:** ~5,320 lines

---

## Implementation Order & Dependencies

**Must be done sequentially:**

1. **Phase 1 (Infrastructure)** - Foundation for everything
2. **Phase 2 (Templates)** - Needed for creation
3. **Phase 3 (Creation/Review)** - Builds on Phase 1+2
4. **Phase 4 (Enrichment)** - Builds on Phase 1
5. **Phase 5 (UI/Progress)** - Builds on Phase 1+3+4
6. **Phase 6 (Guided Learning)** - Builds on all previous

**Timeline:**
- **MVP (Phases 1-4):** ~15-20 hours - Get basic creation and enrichment working
- **Full Polish (Phases 5-6):** ~5-8 hours - UI and guidance features
- **Total:** 20-28 hours

---

## Success Criteria

### Functional Requirements
- ✅ Curricula stored in vault (separate from notes)
- ✅ 5 domain-based templates available
- ✅ Professor auto-detects best template for user request
- ✅ Review/edit dialog appears before saving curriculum
- ✅ User can edit outline or ask for changes
- ✅ Curriculum saved to vault with structured data
- ✅ Section enrichment triggered on start (~10-30s loading)
- ✅ Heavy enrichment includes: explanations, diagrams, examples, exercises, resources
- ✅ Enrichment cached (no re-generation on restart)
- ✅ Subheading-level progress tracking (status, time, mastery, reflection)
- ✅ Visual curriculum UI with progress bars
- ✅ Week/section tree with status icons (⭕⏳✅)
- ✅ Click section to start/continue
- ✅ Completion flow prompts for reflection
- ✅ "Next section?" suggestion after completion
- ✅ Formal session mode (start/end with indicator)
- ✅ Ambient awareness (Professor knows active curricula)
- ✅ Context-aware responses related to curriculum

### User Experience
- ✅ Curriculum creation takes < 2 minutes
- ✅ Review dialog is intuitive and easy to edit
- ✅ Section enrichment feels polished (loading indicators, smooth UX)
- ✅ Progress tracking is clear and motivating
- ✅ Session mode feels focused and guided
- ✅ Ambient mode is helpful but not intrusive

### Technical Quality
- ✅ All API endpoints have proper error handling
- ✅ File I/O is robust (handles missing files, corruption)
- ✅ Frontend handles loading states gracefully
- ✅ No blocking operations on main thread
- ✅ Proper TypeScript types for all data structures (if using TypeScript)
- ✅ Comprehensive logging for debugging

---

## Integration with Other Phases

### Phase 11 (Multi-Model Routing & Personas) ✅
- **Professor persona** generates curriculum outlines
- **Router v2** selects best model for enrichment (uses THOROUGH confidence)
- Heavy enrichment uses best available model for quality

### Phase 14 (Mental Models) ✅
- Curriculum system could integrate with mental models
- Example: Activate "teaching mode" mental model during curriculum sessions
- Mental models could guide Professor's teaching approach per curriculum

### Phase 16 (Native Notes) ✅
- Curricula stored in vault (separate from notes)
- Section materials reference notes via wikilinks
- Learning notes can link to curriculum sections

### Phase 21 (Knowledge Deduplication) ✅
- Prevent duplicate curricula on similar topics
- Suggest appending to existing curriculum vs. creating new
- Similar curriculum detection when creating

### Phase 22 (Teaching Mode) ✅ (More Advanced Than Documented)
- Teaching mode mental model can be activated during curriculum sessions
- Socratic questioning during section enrichment
- Progressive difficulty adjustment based on curriculum progress
- Learning tracker integration with curriculum progress
- **Note:** Teaching Mode is further along in implementation than documentation suggests

### Future: Phase 12 (Knowledge Graph)
- Curriculum sections become graph nodes
- Visualize learning path and concept dependencies
- "Explore from here" suggests related curricula
- Prerequisite detection and visualization

---

## User Experience Flows

### Flow 1: Create Curriculum
1. User: "Create a learning plan for React"
2. Professor detects → "framework-library" template (recommended)
3. Professor asks customization questions:
   - What's your JavaScript experience?
   - What type of application do you want to build?
   - How much time per week?
4. Professor generates outline (8 weeks)
5. **Review dialog appears:**
   - Left: Editable outline
   - Right: Preview (title, goal, 16 sections, 8 weeks)
6. User reviews, optionally edits
7. User clicks "Save & Activate"
8. Curriculum created in `vault/.polly/curricula/react-mastery/`
9. Notification: "Curriculum created! Ready to start Week 1?"

### Flow 2: Follow Curriculum (Linear)
1. User opens Learning page → sees "React Mastery" in active curricula
2. User clicks → Curriculum detail view appears
3. Progress bar: 0%, 0/16 sections
4. Week/section tree shows structure
5. User clicks "Week 1.1: React Basics"
6. Loading: "Enriching section with materials..." (~15s)
7. **Session view displays:**
   - Explanation of React fundamentals
   - Diagram: React component lifecycle
   - 3 code examples (simple → complex)
   - 4 practice exercises
   - Assessment criteria checklist
8. User works through materials
9. User clicks "Mark Complete"
10. Prompt for reflection:
    - Mastery level: 3/5
    - Struggles: "Confused about state vs. props"
    - Breakthroughs: "Aha! Components are functions"
11. Progress saved
12. Notification: "Section complete! Continue to 1.2: Components?"

### Flow 3: Ambient Awareness (Outside Session)
1. User in normal chat (not in curriculum session)
2. User: "How do I pass data between React components?"
3. Professor checks active curricula → sees "React Mastery (Week 1.2)"
4. Professor responds:
   > "(This relates to your React Mastery curriculum - you're on Week 1.2)
   >
   > Great question! There are three main ways to pass data in React..."
5. No interruption, just helpful context

### Flow 4: Exploratory Learning (Non-Linear)
1. User on Week 2, but wants to jump ahead
2. User clicks Week 5.1 in curriculum tree
3. System asks: "This is ahead of your current progress. Jump ahead?"
4. User confirms
5. Section enrichment starts
6. System marks path as "non-linear" in metadata
7. Learning continues normally

---

## Future Enhancements (Not in Phase 23)

### Phase 23b: User-Created Templates
- "Save as Template" button in curriculum detail view
- Template creation dialog (name, description, category)
- Save to `vault/.polly/curriculum-templates/custom/`
- List custom templates alongside system templates
- Share templates (export/import JSON)

### Phase 23c: Collaborative Learning
- Share curricula with other users
- Community-contributed templates
- Collaborative progress tracking
- Group learning sessions

### Phase 23d: Adaptive Difficulty
- AI-powered difficulty adjustment based on struggles
- Auto-generate additional exercises if user struggles
- Skip sections if user demonstrates mastery
- Personalized learning path optimization

### Phase 23e: Gamification
- Achievement badges for milestones
- Learning streaks
- Mastery score visualizations
- Leaderboards (optional, privacy-respecting)

### Phase 23f: Integration Enhancements
- Spaced repetition reminders
- Calendar integration for scheduled learning
- Export curriculum to Anki/RemNote
- PDF/blog post export of learning journey

---

## Marketing Alignment

### Theme
**"Polly guides your learning journey, step by step"**

### Message
Transform scattered learning into structured growth. Polly creates personalized curricula, enriches them with diagrams and exercises, tracks your progress, and guides you through each step. Learning becomes systematic, not haphazard.

### User Benefit
- **Structure:** Clear learning path from beginner to mastery
- **Guidance:** Professor actively guides through each section
- **Progress:** Visual tracking shows how far you've come
- **Depth:** Heavy enrichment provides real understanding, not surface knowledge
- **Flexibility:** Linear or exploratory learning, your choice

### Differentiator vs. ChatGPT/Claude
- They give learning outlines → **Polly builds complete curricula with materials**
- They answer one-off questions → **Polly guides multi-week learning journeys**
- They don't track progress → **Polly shows visual progress and mastery**
- They forget context → **Polly remembers what you're learning and helps accordingly**

---

## Open Questions

1. **Enrichment Loading Time:** Is 10-30s acceptable when starting a section? Should we show estimated time?

2. **Reflection Friction:** Is prompting for mastery/struggles/breakthroughs too much friction on completion? Or valuable for learning?

3. **Template Coverage:** Do 5 domain templates cover most use cases? Any critical templates missing?

4. **Skill Package Integration:** Should enrichment always pull from skill packages when available? Or ask user?

5. **Export/Import:** Should curricula be exportable/importable between Polly instances?

6. **Collaboration:** Is collaborative learning (sharing curricula with others) a priority for Phase 23, or defer to 23b?

---

## References

**Planning Session Document:** (this conversation)

**Related Phases:**
- Phase 11: Multi-Model Routing & Personas (Complete)
- Phase 14: Mental Models (Complete)
- Phase 16: Native Notes (Complete)
- Phase 21: Knowledge Deduplication (Complete)
- Phase 22: Teaching Mode (Planned, not implemented)

**Key Files:**
- `/core/personas/implementations/professor.py` - Professor persona
- `/learners/learning_tracker.py` - Existing learning tracker (Phase 22 planning)
- `/vault/.polly/skills/` - Existing skill packages
- `/docs/planning/phases/phase-22/PHASE22_TEACHING_MODE.md` - Teaching mode plan

---

**Status:** Planning Complete  
**Ready to Implement:** Yes  
**Estimated Start Date:** TBD  
**Estimated Completion:** TBD (20-28 hours)

---

**Document Created:** February 2, 2026  
**Last Updated:** February 2, 2026  
**Author:** Development Team  
**Version:** 1.0
