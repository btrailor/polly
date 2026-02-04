# Phase 16c: Scribe Persona + Skill System - Implementation Checklist

**Status:** Ready to Implement  
**Timeline:** 3-4 weeks (18 days)  
**Start Date:** January 30, 2026  
**Architecture:** See `docs/PERSONA_SYSTEM_ARCHITECTURE.md` (~35,000 words)

---

## Overview

This checklist breaks down Phase 16c into daily tasks with clear success criteria. Follow in order.

---

## Week 1: Foundation (Days 1-5)

### Day 1: PersonaManager Refactoring Part 1

**Goal:** Begin lazy-loading architecture

**Tasks:**
- [ ] Read current `core/personas/manager.py` to understand existing structure
- [ ] Create `PersonaMetadata` dataclass in `core/personas/models.py`:
  - `slug: str`
  - `name: str`
  - `description: str`
  - `modes: List[str]`
  - `icon: str`
- [ ] Add `_load_all_metadata()` method to PersonaManager
  - Discovers all YAML files in `core/personas/definitions/`
  - Loads only frontmatter (not full prompts)
  - Returns list of PersonaMetadata objects
- [ ] Add `metadata_cache: Dict[str, PersonaMetadata]` to PersonaManager
- [ ] Update `__init__()` to call `_load_all_metadata()` on startup

**Success Criteria:**
- PersonaManager loads metadata without full prompts
- Can list all available personas with descriptions
- Startup time is fast (<100ms for metadata loading)

**Files Modified:**
- `core/personas/manager.py`
- `core/personas/models.py` (new file)

---

### Day 2: PersonaManager Refactoring Part 2

**Goal:** Implement on-demand prompt loading

**Tasks:**
- [ ] Add `loaded_prompts: Dict[str, Dict[str, str]]` cache to PersonaManager
  - Key: `{slug}:{mode}` (e.g., "scribe:capture")
  - Value: Full prompt string
- [ ] Create `_load_persona_prompt(slug: str, mode: str) -> str` method
  - Reads YAML file from `core/personas/definitions/{slug}.yaml`
  - Extracts prompt for specified mode
  - Caches in `loaded_prompts`
  - Returns prompt string
- [ ] Update `activate_persona(slug: str, mode: str)` method
  - Check if prompt is cached
  - If not cached, call `_load_persona_prompt()`
  - Activate persona with loaded prompt
- [ ] Update `get_system_prompt()` to include persona metadata
  - Include active persona + mode
  - Include metadata for all available personas (for routing)

**Success Criteria:**
- Prompts load on-demand (not at startup)
- Second activation of same persona+mode uses cached prompt
- System prompt includes metadata for routing

**Files Modified:**
- `core/personas/manager.py`

---

### Day 3: PersonaManager Testing & Integration

**Goal:** Test lazy-loading and update integrations

**Tasks:**
- [ ] Write unit tests for PersonaManager lazy-loading:
  - Test metadata loading
  - Test prompt caching
  - Test activation with lazy-loading
  - Test system prompt includes metadata
- [ ] Update `core/polly.py` to use new PersonaManager
- [ ] Update `interfaces/server.py` persona endpoints (should already exist from Phase 11c)
- [ ] Test via curl:
  ```bash
  curl http://localhost:11436/polly/personas/list
  curl -X POST http://localhost:11436/polly/personas/activate \
    -H "Content-Type: application/json" \
    -d '{"slug":"scribe","mode":"capture"}'
  ```

**Success Criteria:**
- All tests passing
- API endpoints work correctly
- Can activate persona via API
- System prompt includes metadata

**Files Modified:**
- `tests/test_persona_manager_lazy_loading.py` (new file)
- `core/polly.py`
- `interfaces/server.py`

---

### Day 4: SkillManager Implementation Part 1

**Goal:** Create skill system foundation

**Tasks:**
- [ ] Create `core/skills/base.py`:
  - `SkillMetadata` dataclass:
    - `name: str`
    - `category: str`
    - `personas: List[str]` (which personas use this skill)
    - `version: str`
    - `path: str`
  - `Skill` class:
    - `metadata: SkillMetadata`
    - `content: str` (full markdown content)
    - `load() -> None` (load content from file)
    - `get_section(section_name: str) -> str` (extract specific section)
- [ ] Create `core/skills/__init__.py`
- [ ] Write basic tests for Skill and SkillMetadata classes

**Success Criteria:**
- SkillMetadata and Skill classes work correctly
- Can load skill content from markdown file
- Can extract sections from skill

**Files Created:**
- `core/skills/base.py`
- `core/skills/__init__.py`
- `tests/test_skill_base.py` (new file)

---

### Day 5: SkillManager Implementation Part 2

**Goal:** Complete skill discovery and loading

**Tasks:**
- [ ] Create `core/skills/manager.py`:
  - `SkillManager` class
  - `__init__(skills_dir: str)` - Default to `~/.polly/skills/`
  - `_discover_skills() -> List[SkillMetadata]` method:
    - Scan skills directory
    - Parse YAML frontmatter from each SKILL.md
    - Return metadata list
  - `load_skill(name: str) -> Skill` method:
    - Load full skill content
    - Cache in memory
    - Return Skill object
  - `get_skills_for_persona(persona_slug: str) -> List[SkillMetadata]` method:
    - Filter skills by persona
    - Return metadata only (not full content)
  - `skill_cache: Dict[str, Skill]` - In-memory cache
- [ ] Write tests for SkillManager
- [ ] Integrate SkillManager into PersonaManager:
  - Add `skill_manager: SkillManager` attribute
  - Add `get_persona_skills(slug: str) -> List[SkillMetadata]` method

**Success Criteria:**
- SkillManager discovers all skills in directory
- Skills load on-demand (lazy-loading)
- Skills cache in memory after first load
- PersonaManager can list skills for each persona

**Files Created:**
- `core/skills/manager.py`
- `tests/test_skill_manager.py` (new file)

**Files Modified:**
- `core/personas/manager.py`

---

## Week 2: Scribe Persona (Days 6-10)

### Day 6: Scribe YAML Definition

**Goal:** Create Scribe persona definition file

**Tasks:**
- [ ] Create directory: `core/personas/definitions/`
- [ ] Create `core/personas/definitions/scribe.yaml`:
  ```yaml
  name: Scribe
  slug: scribe
  description: Transform conversations into structured notes
  icon: 📝
  primary_domain: scrolls
  
  modes:
    capture:
      name: Capture
      description: Analyze conversation and extract key concepts
      prompt: |
        You are Polly's Scribe persona in Capture mode. Your role is to...
        [Full prompt here - ~500 words]
    
    organize:
      name: Organize
      description: Ask clarifying questions via radio buttons
      prompt: |
        You are Polly's Scribe persona in Organize mode...
        [Full prompt here - ~500 words]
    
    enrich:
      name: Enrich
      description: Generate markdown with auto [[wiki-links]]
      prompt: |
        You are Polly's Scribe persona in Enrich mode...
        [Full prompt here - ~500 words]
    
    edit:
      name: Edit
      description: Improve existing notes
      prompt: |
        You are Polly's Scribe persona in Edit mode...
        [Full prompt here - ~500 words]
  
  skills:
    - template-guide
    - wiki-linking
    - domain-structure
  
  collaboration:
    partners:
      - librarian  # For searching related notes
  ```
- [ ] Write detailed prompts for each mode
- [ ] Test YAML parsing with PersonaManager

**Success Criteria:**
- YAML file is valid and parsable
- PersonaManager can load Scribe metadata
- All 4 modes are defined with prompts
- Skills are specified

**Files Created:**
- `core/personas/definitions/scribe.yaml`

---

### Day 7: Write Scribe Skills Part 1

**Goal:** Create first 2 skills

**Tasks:**
- [ ] Create directory: `vault/.polly/skills/`
- [ ] Create `vault/.polly/skills/template-guide/SKILL.md`:
  ```markdown
  ---
  name: template-guide
  category: note-taking
  personas: [scribe, librarian]
  version: 1.0
  ---
  
  # Template Guide
  
  ## Available Templates
  
  ### Meeting Notes
  **When to use:** Recording discussions, decisions, action items
  **Structure:**
  - Date & Attendees
  - Agenda
  - Discussion Points
  - Decisions
  - Action Items
  
  [Continue for all templates...]
  ```
- [ ] Create `vault/.polly/skills/wiki-linking/SKILL.md`:
  ```markdown
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
  
  ## Exclusions
  - Don't link in code blocks
  - Don't link URLs
  - Don't link common words (the, and, is, etc.)
  - Only link first mention of concept
  
  [Continue with examples...]
  ```
- [ ] Test skill loading with SkillManager

**Success Criteria:**
- Both skills are valid markdown with YAML frontmatter
- SkillManager can discover and load both skills
- Skills are well-documented with examples

**Files Created:**
- `vault/.polly/skills/template-guide/SKILL.md`
- `vault/.polly/skills/wiki-linking/SKILL.md`

---

### Day 8: Write Scribe Skills Part 2 + Create Templates

**Goal:** Complete skill system and create note templates

**Tasks:**
- [ ] Create `vault/.polly/skills/domain-structure/SKILL.md`:
  ```markdown
  ---
  name: domain-structure
  category: organization
  personas: [scribe, librarian]
  version: 1.0
  ---
  
  # Domain Structure Guide
  
  ## Current Vault Organization
  
  ### Sigils (Code)
  - Path: `vault/Sigils/`
  - Purpose: Code, infrastructure, automation
  - File types: .py, .rs, .go, .sh
  
  ### Signals (Audio)
  - Path: `vault/Signals/`
  - Purpose: Audio programming, synthesis
  - File types: .scd, .lua, .txt
  
  [Continue for all domains...]
  ```
- [ ] Create template directory: `vault/.polly/templates/`
- [ ] Create 4 note templates:
  - `vault/.polly/templates/meeting-notes.md`
  - `vault/.polly/templates/concept-note.md`
  - `vault/.polly/templates/howto-guide.md`
  - `vault/.polly/templates/research-summary.md`
- [ ] Test all 3 skills load correctly

**Success Criteria:**
- All 3 Scribe skills are complete and loadable
- 4 note templates created with proper structure
- Templates follow Obsidian markdown conventions

**Files Created:**
- `vault/.polly/skills/domain-structure/SKILL.md`
- `vault/.polly/templates/meeting-notes.md`
- `vault/.polly/templates/concept-note.md`
- `vault/.polly/templates/howto-guide.md`
- `vault/.polly/templates/research-summary.md`

---

### Day 9: Scribe Implementation Part 1 (Capture & Organize)

**Goal:** Implement first 2 Scribe modes

**Tasks:**
- [ ] Create directory: `core/personas/implementations/`
- [ ] Create `core/personas/implementations/scribe.py`:
  ```python
  from core.personas.base import AgentPersona
  from core.skills.manager import SkillManager
  
  class ScribePersona(AgentPersona):
      def __init__(self, persona_manager, skill_manager):
          super().__init__(persona_manager)
          self.skill_manager = skill_manager
      
      async def capture_mode(self, conversation_history: List[Dict]) -> Dict:
          """Analyze conversation and extract concepts"""
          # Load compressed conversation if long
          # Extract key concepts, definitions, insights
          # Return structured concept list
          pass
      
      async def organize_mode(self, concepts: List[str], context: Dict) -> Dict:
          """Generate clarifying questions with radio buttons"""
          # Load template-guide skill
          # Generate questions based on conversation type
          # Return questions in radio button format
          pass
  ```
- [ ] Implement `capture_mode()`:
  - Access conversation history
  - Use compression if >8k tokens (Phase 11 compression)
  - Extract key concepts, definitions, insights
  - Return structured data
- [ ] Implement `organize_mode()`:
  - Load `template-guide` skill
  - Generate 3-5 radio button questions
  - Always include "Type your own: ___" option
  - Return question structure for frontend

**Success Criteria:**
- Capture mode extracts concepts from conversation
- Organize mode generates appropriate questions
- Skills are loaded and used correctly

**Files Created:**
- `core/personas/implementations/scribe.py`

---

### Day 10: Scribe Implementation Part 2 (Enrich & Edit)

**Goal:** Complete Scribe implementation

**Tasks:**
- [ ] Implement `enrich_mode()` in `scribe.py`:
  - Load `wiki-linking` and `template-guide` skills
  - Generate markdown content based on selected template
  - Call auto-linking algorithm (to be implemented Day 16)
  - Return markdown with [[links]]
- [ ] Implement `edit_mode()` in `scribe.py`:
  - Read existing note from vault
  - Apply improvements based on user request
  - Maintain structure and links
  - Return updated markdown
- [ ] Add Scribe to PersonaManager's persona list
- [ ] Test all 4 modes via unit tests
- [ ] Create integration test for full workflow:
  ```python
  async def test_scribe_full_workflow():
      # Capture
      concepts = await scribe.capture_mode(conversation)
      assert len(concepts) > 0
      
      # Organize
      questions = await scribe.organize_mode(concepts)
      assert "Type your own" in questions
      
      # Enrich
      note = await scribe.enrich_mode(concepts, user_answers)
      assert "[[" in note  # Has wiki-links
      
      # Edit
      improved = await scribe.edit_mode(note, "Make it shorter")
      assert len(improved) < len(note)
  ```

**Success Criteria:**
- All 4 Scribe modes implemented
- Integration test passes
- Scribe is registered in PersonaManager

**Files Modified:**
- `core/personas/implementations/scribe.py`
- `core/personas/manager.py`
- `tests/test_scribe_persona.py` (new file)

---

## Week 3: Frontend (Days 11-15)

### Day 11: Chat UI Redesign Part 1 (Model Dropdown)

**Goal:** Consolidate model selection UI

**Tasks:**
- [ ] Read current chat UI in `electron-app/src/renderer/app.js`
- [ ] Identify current model/provider selection controls (likely 2-3 rows)
- [ ] Design new consolidated dropdown:
  ```
  Model: 🤖 Auto (Balanced) ▼
  ```
  Options:
  - Auto (Balanced) - Intelligent routing
  - Auto (Fast) - Prefer fast models
  - Auto (Thorough) - Prefer powerful models
  - Local Only (Ollama)
  - GitHub Copilot
  - Anthropic Claude
  - OpenAI GPT
- [ ] Replace existing controls with single dropdown
- [ ] Update `app.js` to handle new selection format
- [ ] Test model selection works correctly

**Success Criteria:**
- Single unified model dropdown
- All routing options accessible
- Cleaner UI (removed 1-2 rows of controls)
- Model selection persists

**Files Modified:**
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/styles/chat-sidebar.css`

---

### Day 12: Chat UI Redesign Part 2 (Persona Dropdown)

**Goal:** Add persona selector to chat UI

**Tasks:**
- [ ] Add persona dropdown next to model dropdown:
  ```
  Model: 🤖 Auto (Balanced) ▼
  Persona: 📝 Scribe (Organize) ▼
  ```
- [ ] Fetch available personas from API on startup:
  ```javascript
  const personas = await fetch('/polly/personas/list').then(r => r.json());
  ```
- [ ] Populate persona dropdown with options:
  - Librarian (Search) 📚
  - Scribe (Capture) 📝
  - Scribe (Organize) 📝
  - Scribe (Enrich) 📝
  - Scribe (Edit) 📝
- [ ] Add mode indicator/toggle
- [ ] Update chat state to track active persona+mode
- [ ] Send persona+mode with each query:
  ```javascript
  const response = await fetch('/polly/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: userInput,
      persona: 'scribe',
      mode: 'organize'
    })
  });
  ```

**Success Criteria:**
- Persona dropdown shows available personas
- Mode indicator shows current mode
- Active persona+mode sent with queries
- Persona selection persists during conversation

**Files Modified:**
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/styles/chat-sidebar.css`

---

### Day 13: Chat UI Redesign Part 3 (Orchestrator Toggle)

**Goal:** Add orchestrator mode toggle

**Tasks:**
- [ ] Add orchestrator toggle below persona dropdown:
  ```
  Model: 🤖 Auto (Balanced) ▼
  Persona: 📝 Scribe (Organize) ▼
  [🔀] Orchestrator Mode: OFF
  ```
- [ ] Style toggle switch (CSS):
  - OFF state: gray
  - ON state: orange (#f0903b)
- [ ] Fetch orchestrator state from config on startup:
  ```javascript
  const config = await fetch('/polly/config').then(r => r.json());
  orchestratorToggle.checked = config.personas.orchestrator_mode;
  ```
- [ ] Save orchestrator state to config on toggle:
  ```javascript
  await fetch('/polly/config/personas', {
    method: 'POST',
    body: JSON.stringify({orchestrator_mode: isEnabled})
  });
  ```
- [ ] Show tooltip on hover explaining orchestrator mode
- [ ] Add visual indicator when orchestrator is active

**Success Criteria:**
- Toggle appears in UI
- State persists across sessions
- Tooltip explains functionality
- Visual feedback on state change

**Files Modified:**
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/styles/chat-sidebar.css`

---

### Day 14: Question Form Component

**Goal:** Create radio button question UI (OpenCode style)

**Tasks:**
- [ ] Create `electron-app/src/renderer/components/question-form.js`:
  ```javascript
  class QuestionForm {
    constructor(questions) {
      this.questions = questions;
      this.answers = {};
    }
    
    render() {
      // Generate HTML for radio button form
      // Always include "Type your own: ___" option
      // Add [Confirm] [Skip] buttons
    }
    
    getAnswers() {
      // Collect user answers
      return this.answers;
    }
  }
  ```
- [ ] Style radio buttons to match OpenCode design:
  - Clean, minimal styling
  - Orange accent color for selected
  - Hover effects
  - Text input for "Type your own"
- [ ] Handle form submission:
  - Collect answers
  - Send back to Scribe Organize mode
  - Display next step (Enrich mode)
- [ ] Test with sample questions

**Success Criteria:**
- Radio button form displays correctly
- "Type your own" option always present
- Form submission works
- Styling matches app design

**Files Created:**
- `electron-app/src/renderer/components/question-form.js`
- `electron-app/src/renderer/styles/question-form.css` (new file)

**Files Modified:**
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`

---

### Day 15: Preview Modal Component

**Goal:** Create note preview modal with 3 tabs

**Tasks:**
- [ ] Create `electron-app/src/renderer/components/preview-modal.js`:
  ```javascript
  class PreviewModal {
    constructor(noteContent, folderSuggestion) {
      this.content = noteContent;
      this.folder = folderSuggestion;
      this.currentTab = 'preview'; // preview, edit, raw
    }
    
    render() {
      // Generate modal HTML
      // Three tabs: Edit | Preview | Raw
      // Folder selection dropdown
      // [Save] [Cancel] buttons
    }
    
    switchTab(tab) {
      // Switch between Edit/Preview/Raw views
    }
    
    save() {
      // Save note to vault via API
    }
  }
  ```
- [ ] Implement 3 tab views:
  - **Edit:** Textarea with markdown content (editable)
  - **Preview:** Rendered markdown with highlighted [[wiki-links]]
  - **Raw:** Read-only markdown source
- [ ] Add folder selection dropdown:
  - Populate with vault folders
  - Smart suggestion highlighted
  - User can select different folder
- [ ] Implement save functionality:
  ```javascript
  await fetch('/polly/notes/create', {
    method: 'POST',
    body: JSON.stringify({
      content: this.content,
      folder: this.folder,
      title: extractTitle(this.content)
    })
  });
  ```
- [ ] Style modal (full-screen overlay with centered content)
- [ ] Test all 3 tabs and save functionality

**Success Criteria:**
- Modal displays with 3 working tabs
- Edit tab allows modifications
- Preview tab renders markdown correctly
- Raw tab shows source
- Folder selection works
- Save creates note in vault
- Modal closes after save

**Files Created:**
- `electron-app/src/renderer/components/preview-modal.js`
- `electron-app/src/renderer/styles/preview-modal.css` (new file)

**Files Modified:**
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`

---

## Week 4: Integration & Testing (Days 16-18)

### Day 16: Auto-Linking Algorithm

**Goal:** Implement automatic [[wiki-link]] insertion

**Tasks:**
- [ ] Create `core/linking/auto_linker.py`:
  ```python
  class AutoLinker:
      def __init__(self, rag_engine, skill_manager):
          self.rag = rag_engine
          self.skill_manager = skill_manager
      
      async def add_wiki_links(self, content: str, threshold: float = 0.85) -> Tuple[str, int]:
          """Add [[wiki-links]] to content
          
          Returns:
              (linked_content, link_count)
          """
          # 1. Load wiki-linking skill for rules
          # 2. Extract concepts from content
          # 3. Search RAG for matching notes (threshold 0.85+)
          # 4. Insert [[links]] following skill rules
          # 5. Return modified content + link count
          pass
  ```
- [ ] Implement concept extraction:
  - Use spaCy (from Phase 13a) to extract noun phrases
  - Filter common words using stopwords list
  - Exclude code blocks, URLs
- [ ] Implement RAG search for matches:
  - Query RAG with each concept
  - Filter results by similarity threshold (0.85+)
  - Deduplicate by note title
- [ ] Implement link insertion:
  - Load `wiki-linking` skill for rules
  - Only link first mention of each concept
  - Preserve existing links
  - Use format: `[[Note Title]]`
- [ ] Add to Scribe's `enrich_mode()`:
  ```python
  async def enrich_mode(self, concepts, answers):
      # Generate content
      content = await self.generate_content(concepts, answers)
      
      # Add wiki-links
      linked_content, link_count = await self.auto_linker.add_wiki_links(content)
      
      return {
          'content': linked_content,
          'link_count': link_count
      }
  ```
- [ ] Write tests for auto-linking algorithm

**Success Criteria:**
- Auto-linker finds relevant notes (0.85+ similarity)
- Links only first mention of each concept
- Excludes code blocks and URLs
- Follows wiki-linking skill rules
- Tests pass

**Files Created:**
- `core/linking/auto_linker.py`
- `tests/test_auto_linker.py` (new file)

**Files Modified:**
- `core/personas/implementations/scribe.py`

---

### Day 17: Integration Testing

**Goal:** Test complete Scribe workflow

**Tasks:**
- [ ] Create integration test: `tests/integration/test_scribe_workflow.py`
- [ ] Test full workflow via API:
  ```python
  async def test_scribe_full_workflow():
      # 1. Start conversation
      conv_id = await create_conversation()
      
      # 2. Have conversation about Docker
      await send_message(conv_id, "Let's talk about Docker containers...")
      await send_message(conv_id, "Docker uses namespaces for isolation...")
      
      # 3. Activate Scribe Capture mode
      await activate_persona('scribe', 'capture')
      concepts = await send_message(conv_id, "Save this as a note")
      assert len(concepts) > 0
      
      # 4. Scribe Organize mode (questions)
      questions = await get_questions(conv_id)
      assert "What type of note?" in questions[0]['question']
      
      # 5. Answer questions
      answers = {
          'note_type': 'Concept Explanation',
          'domain': 'Scrolls',
          'tags': 'docker,containers,devops'
      }
      await submit_answers(conv_id, answers)
      
      # 6. Scribe Enrich mode (generate note)
      note = await get_generated_note(conv_id)
      assert '[[' in note['content']  # Has wiki-links
      assert note['link_count'] > 0
      
      # 7. Preview and save
      await save_note(conv_id, note['content'], 'Scrolls')
      
      # 8. Verify note exists in vault
      note_path = f"vault/Scrolls/{note['title']}.md"
      assert os.path.exists(note_path)
  ```
- [ ] Test edge cases:
  - Empty conversation (should fail gracefully)
  - Very long conversation (should compress)
  - No matching notes for linking (should create note without links)
  - User skips questions (should use defaults)
- [ ] Test with different note types:
  - Meeting Notes
  - Concept Explanation
  - How-To Guide
  - Research Summary
- [ ] Fix any issues found

**Success Criteria:**
- Full workflow completes successfully
- All 4 Scribe modes work together
- Edge cases handled gracefully
- Different note types work correctly

**Files Created:**
- `tests/integration/test_scribe_workflow.py`

---

### Day 18: End-to-End Testing & Documentation

**Goal:** Final testing and documentation

**Tasks:**
- [ ] Test via UI (manual testing):
  - Start conversation about a topic
  - Click "Save as note" button (or type command)
  - Verify Scribe Capture activates automatically
  - Answer radio button questions
  - Preview note in modal (all 3 tabs)
  - Save note to vault
  - Verify note appears in Notes view
  - Verify wiki-links are clickable
- [ ] Test orchestrator mode toggle:
  - Toggle ON
  - Ask question that requires Librarian
  - Verify Scribe → Librarian collaboration
  - Verify "🔀 Collaborating with..." message appears
- [ ] Test error handling:
  - RAG unavailable
  - Skill files missing
  - Invalid YAML in persona definition
  - Network errors during save
- [ ] Performance testing:
  - Measure persona activation time (<200ms)
  - Measure skill loading time (<100ms)
  - Measure auto-linking time (<2s for typical note)
  - Measure full workflow time (<10s total)
- [ ] Create user documentation:
  - `docs/SCRIBE_PERSONA_USER_GUIDE.md`:
    - What is Scribe?
    - When to use each mode
    - How to save conversations as notes
    - Understanding auto [[wiki-links]]
    - Customizing skills
- [ ] Create developer documentation:
  - `docs/PERSONA_DEVELOPMENT_GUIDE.md`:
    - How to create new personas
    - How to write skills
    - Lazy-loading architecture explanation
    - Orchestrator integration guide
- [ ] Update MASTER_ROADMAP.md:
  - Mark Phase 16c as COMPLETE
  - Update timeline estimates

**Success Criteria:**
- All manual tests pass
- Error handling works correctly
- Performance targets met
- Documentation complete
- Phase 16c ready for production

**Files Created:**
- `docs/SCRIBE_PERSONA_USER_GUIDE.md`
- `docs/PERSONA_DEVELOPMENT_GUIDE.md`

**Files Modified:**
- `MASTER_ROADMAP.md`

---

## Success Criteria Summary

At the end of Phase 16c, you should have:

### Backend
- ✅ PersonaManager with lazy-loading (metadata vs full prompts)
- ✅ SkillManager with on-demand skill loading
- ✅ Scribe persona with 4 working modes (Capture/Organize/Enrich/Edit)
- ✅ 3 Scribe skills (template-guide, wiki-linking, domain-structure)
- ✅ Auto-linking algorithm (0.85+ similarity threshold)
- ✅ 4 note templates
- ✅ All tests passing

### Frontend
- ✅ Consolidated model dropdown (cleaner UI)
- ✅ Persona dropdown with mode indicator
- ✅ Orchestrator mode toggle (OFF by default)
- ✅ Radio button question form (OpenCode style)
- ✅ Note preview modal (Edit/Preview/Raw tabs)
- ✅ Folder selection with smart suggestions

### Integration
- ✅ Full Scribe workflow working end-to-end
- ✅ User can save conversations as notes
- ✅ Generated notes have auto [[wiki-links]]
- ✅ Preview modal allows editing before save
- ✅ Notes save to correct folder in vault
- ✅ Orchestrator collaboration functional

### Documentation
- ✅ User guide for Scribe persona
- ✅ Developer guide for creating personas
- ✅ MASTER_ROADMAP.md updated

### Performance
- ✅ Persona activation: <200ms
- ✅ Skill loading: <100ms per skill
- ✅ Auto-linking: <2s for typical note
- ✅ Full workflow: <10s total

---

## Files Summary

### New Files (Backend)
- `core/personas/models.py` - PersonaMetadata dataclass
- `core/personas/definitions/scribe.yaml` - Scribe persona definition
- `core/personas/implementations/scribe.py` - Scribe implementation
- `core/personas/orchestrator.py` - OrchestratorManager (minimal, for future)
- `core/skills/__init__.py`
- `core/skills/base.py` - Skill and SkillMetadata classes
- `core/skills/manager.py` - SkillManager
- `core/linking/auto_linker.py` - Auto-linking algorithm
- `vault/.polly/skills/template-guide/SKILL.md`
- `vault/.polly/skills/wiki-linking/SKILL.md`
- `vault/.polly/skills/domain-structure/SKILL.md`
- `vault/.polly/templates/meeting-notes.md`
- `vault/.polly/templates/concept-note.md`
- `vault/.polly/templates/howto-guide.md`
- `vault/.polly/templates/research-summary.md`

### New Files (Frontend)
- `electron-app/src/renderer/components/question-form.js`
- `electron-app/src/renderer/components/preview-modal.js`
- `electron-app/src/renderer/styles/question-form.css`
- `electron-app/src/renderer/styles/preview-modal.css`
- `electron-app/src/renderer/styles/persona-ui.css`

### New Files (Tests)
- `tests/test_persona_manager_lazy_loading.py`
- `tests/test_skill_base.py`
- `tests/test_skill_manager.py`
- `tests/test_scribe_persona.py`
- `tests/test_auto_linker.py`
- `tests/integration/test_scribe_workflow.py`

### New Files (Documentation)
- `docs/SCRIBE_PERSONA_USER_GUIDE.md`
- `docs/PERSONA_DEVELOPMENT_GUIDE.md`

### Modified Files (Backend)
- `core/personas/manager.py` - Lazy-loading refactor
- `core/personas/base.py` - Skill integration
- `core/polly.py` - PersonaManager integration
- `interfaces/server.py` - Persona endpoints (should already exist)

### Modified Files (Frontend)
- `electron-app/src/renderer/app.js` - UI updates
- `electron-app/src/renderer/index.html` - Structure updates
- `electron-app/src/renderer/styles/chat-sidebar.css` - Styling

### Modified Files (Documentation)
- `MASTER_ROADMAP.md` - Mark Phase 16c complete

---

## Next Steps After Phase 16c

1. **Phase 17: Librarian Persona (2-3 weeks)**
   - DEFAULT persona for KB operations
   - 4 modes: Search/Catalog/Connect/Curate
   - eBook library management
   - Intent-based routing to other personas

2. **Phase 18: Programmer Persona (2-3 weeks)**
   - Code writing & debugging
   - 4 modes: Code/Debug/Refactor/Explain
   - Collaboration with Architect

3. **Continue through Phase 23+** (User Extensibility)

---

## Questions & Issues

If you encounter issues during implementation, refer to:
- `docs/PERSONA_SYSTEM_ARCHITECTURE.md` - Complete architecture (~35,000 words)
- `MASTER_ROADMAP.md` - Phase 16c entry with overview
- Existing persona code: `core/personas/architect.py` (example to follow)

**Common Issues:**
- **Skill not loading:** Check YAML frontmatter format, ensure file is in `vault/.polly/skills/`
- **Persona not activating:** Check YAML definition is valid, check PersonaManager cache
- **Auto-linking not working:** Check RAG is running, check similarity threshold (0.85)
- **Questions not displaying:** Check QuestionForm component is rendered, check JSON format from Organize mode

---

**Good luck with Phase 16c! 🚀**
