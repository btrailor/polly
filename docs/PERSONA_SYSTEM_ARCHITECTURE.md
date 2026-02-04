# Polly Persona System: Complete Architecture & Implementation Plan

**Version:** 2.0 (Post-KILO Research)  
**Status:** Planning Phase  
**Last Updated:** January 30, 2026

---

## Executive Summary

### What We're Building

A **hierarchical persona system** where Polly adopts specialized roles (Personas) with sub-modes for specific workflows. Inspired by KILO Code's mode system but adapted for Polly's knowledge-work use case.

### Key Innovations

1. **Lazy-Loading Architecture** - Only load persona prompts when needed (KILO-inspired)
2. **Skill System** - On-demand knowledge packages (templates, rules, guides)
3. **Orchestrator Mode Toggle** - Optional automatic persona collaboration
4. **No Orchestrator Persona** - Toggle replaces need for meta-coordinator

### Architectural Principles

- **Semantic Clarity** - Names match purpose (Architect plans, Programmer codes)
- **User Control** - Orchestrator mode is opt-in toggle, not forced
- **Extensibility Later** - Build solid foundation first, add customization Phase 23+
- **Self-Documenting** - Skills make behavior explicit and modifiable

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architectural Decisions](#architectural-decisions)
3. [Persona Roster & Responsibilities](#persona-roster--responsibilities)
4. [Orchestrator Mode Toggle](#orchestrator-mode-toggle)
5. [Technical Architecture](#technical-architecture)
6. [Skill System Design](#skill-system-design)
7. [Implementation Phases](#implementation-phases)
8. [File Structure](#file-structure)
9. [Future: User Extensibility](#future-user-extensibility)

---

## Architectural Decisions

### Decision 1: Extensibility Timeline

**Chosen:** Full extensibility like KILO (but later)

- **Phase 16-21:** Build 5 core personas without extensibility
- **Phase 23+:** Add YAML-based user-defined personas
- **Rationale:** Establish patterns before exposing to users

### Decision 2: Skill System Priority

**Chosen:** Build now (Phase 16c)

- Skills are lightweight and proven (KILO validation)
- Makes templates/rules self-documenting
- Avoids hardcoding logic that should be configurable
- **First skills:** `template-guide`, `wiki-linking`, `domain-structure`

### Decision 3: Orchestrator Mode Toggle

**Chosen:** User-controlled toggle for automatic collaboration

**Two Modes:**

#### Manual Mode (Default)
- User explicitly switches personas
- No automatic collaboration
- Full control, predictable behavior
- Good for learning the system

#### Orchestrator Mode (Toggle On)
- Personas can collaborate automatically
- User sees collaboration happening (transparent)
- Faster workflows for complex tasks
- Requires trust in the system

**UI:**
```
┌─────────────────────────────────────────┐
│ Model: 🤖 Auto (Balanced) ▼             │
│ Persona: 📝 Scribe (Organize) ▼         │
│ [🔀] Orchestrator Mode: OFF             │  ← Toggle
└─────────────────────────────────────────┘
```

**Benefits:**
- ✅ No friction for power users (toggle on once)
- ✅ Still transparent (user sees collaboration)
- ✅ Safe default (toggle off = manual control)
- ✅ Simpler than approval modals
- ✅ Implements orchestration without dedicated persona

### Decision 4: Administrator Persona

**Chosen:** Build in Phase 22

Calendar, email, tasks, reminders - full implementation

---

## Persona Roster & Responsibilities

### Updated Roster (6 Personas)

| Persona | Purpose | Primary Domain | Collaboration Partners |
|---------|---------|----------------|------------------------|
| **Librarian** | Knowledge organization & search | All domains (default) | All personas |
| **Scribe** | Note creation & editing | Signals/Scrolls | Librarian |
| **Programmer** | Code writing & debugging | Sigils (code) | Architect, Librarian |
| **Architect** | System design & planning | Grids (architecture) | Programmer |
| **Professor** | Teaching & learning | Glyphs (pedagogy) | Librarian, Scribe |
| **Administrator** | Scheduling & communication | Personal management | Librarian |

**Key Changes from Original Plan:**
1. **Librarian is now default** - Handle generic queries, KB search
2. **Programmer added** - Separate from Architect (planning vs. coding)
3. **Architect refocused** - Plans only, no code generation
4. **Orchestrator removed** - Replaced by toggle

---

## 1. Librarian (Default Persona)

**Purpose:** Knowledge organization, search, and curation

**Why Default:**
- Most queries start with "search my notes for..."
- Acts as router to other personas
- Manages core KB operations

**Modes:**

### 1.1 Search Mode (Default)
**Purpose:** Query knowledge base, find information  
**Tools:** RAG search, semantic search, filter by domain  
**Output:** Search results with relevance scores

### 1.2 Catalog Mode
**Purpose:** Organize and tag notes  
**Tools:** Tag assignment, classification, folder suggestions  
**Output:** Metadata updates, organization suggestions

### 1.3 Connect Mode
**Purpose:** Find relationships between notes  
**Tools:** Link discovery, concept mapping, backlink analysis  
**Output:** Suggested [[wiki-links]], relationship graphs

### 1.4 Curate Mode (eBook Focus)
**Purpose:** Manage eBook library  
**Tools:** Index eBooks, extract metadata, export to Supernote  
**Output:** Library catalog, reading lists, exports

**Skills:**
- `classification-rules` - How to tag and categorize notes
- `ebook-formats` - Supported formats and metadata extraction
- `search-operators` - Advanced RAG query syntax
- `domain-mapping` - Vault structure (Sigils/Signals/Scrolls/Glyphs/Grids)

**Collaboration:**
- Activated by all personas for KB queries
- Suggests relevant personas based on query intent

---

## 2. Scribe (Note-Taking Persona)

**Purpose:** Transform conversations into structured notes

**Modes:**

### 2.1 Capture Mode (Default)
**Purpose:** Analyze conversation to extract key concepts  
**Tools:** Conversation analysis, compression access, concept extraction  
**Output:** Concept list with definitions

### 2.2 Organize Mode
**Purpose:** Ask clarifying questions via radio buttons  
**Tools:** Question generation, template matching  
**Output:** Radio button form (OpenCode style) + "Type your own" option

**Example Questions:**
```
What type of note is this?
( ) Meeting Notes
( ) Concept Explanation  
( ) How-To Guide
( ) Research Summary
( ) Type your own: ___________

Which domain should this go in?
( ) Signals (meetings/events)
( ) Scrolls (concepts/theories)
( ) Glyphs (learning/pedagogy)
( ) Type your own: ___________
```

### 2.3 Enrich Mode
**Purpose:** Generate markdown with auto [[wiki-links]]  
**Tools:** Content generation, auto-linking, template application  
**Output:** Markdown with [[links]] to existing notes

**Auto-Linking Process:**
1. Generate content
2. Read `wiki-linking` skill for rules
3. Search KB for matching concepts (threshold 0.85+)
4. Insert [[wiki-links]] per rules
5. Return with link count

### 2.4 Edit Mode
**Purpose:** Improve existing notes  
**Tools:** Note reading, revision, enhancement  
**Output:** Improved note content

**Skills:**
- `template-guide` - All available note templates and when to use each
- `wiki-linking` - Rules for automatic [[wiki-link]] creation
- `domain-structure` - Vault folder organization

**Collaboration:**
- Uses Librarian to search for related notes during Capture
- Uses Librarian to find link targets during Enrich

---

## 3. Programmer (Code Generation Persona)

**Purpose:** Write, debug, and explain code

**Modes:**

### 3.1 Code Mode (Default)
**Purpose:** Write new code or features  
**Tools:** File editing, code generation, syntax checking  
**Output:** Code files, implementation

### 3.2 Debug Mode
**Purpose:** Fix bugs and errors  
**Tools:** Error analysis, logging, testing  
**Output:** Bug fixes, test cases

### 3.3 Refactor Mode
**Purpose:** Improve existing code  
**Tools:** Code analysis, pattern detection, optimization  
**Output:** Refactored code

### 3.4 Explain Mode
**Purpose:** Document and explain code  
**Tools:** Code reading, documentation generation  
**Output:** Comments, docstrings, README

**Skills:**
- `coding-standards` - Project coding style and conventions
- `testing-patterns` - Test structure and best practices
- `debugging-workflow` - Systematic debugging approach

**Collaboration:**
- Requests Architect for design before major features
- Uses Librarian to search codebase documentation

---

## 4. Architect (Planning Persona)

**Purpose:** System design and technical planning (NO CODE GENERATION)

**Modes:**

### 4.1 Analyze Mode (Default)
**Purpose:** Gather requirements and understand constraints  
**Tools:** Question generation, requirement analysis  
**Output:** Requirements document, constraints list

### 4.2 Design Mode
**Purpose:** Create system designs and architecture  
**Tools:** Diagram generation (as text), component specification  
**Output:** Design documents, architecture diagrams (markdown)

**Example Output:**
```markdown
# System Architecture

## Components

### API Gateway
- Purpose: Handle authentication and routing
- Technology: FastAPI
- Interfaces: REST endpoints

### Database Layer
- Purpose: Persistent storage
- Technology: PostgreSQL
- Schema: [see below]

## Data Flow
User → API Gateway → Business Logic → Database
```

### 4.3 Review Mode
**Purpose:** Critique designs and identify risks  
**Tools:** Design analysis, risk assessment  
**Output:** Review feedback, recommendations

**Skills:**
- `design-patterns` - Common architectural patterns
- `system-constraints` - Performance, scalability considerations
- `review-checklist` - What to look for in design reviews

**Collaboration:**
- Collaborates with Programmer when design is approved
- Uses Librarian to search existing architecture docs

---

## 5. Professor (Teaching Persona)

**Purpose:** Teaching, learning, and knowledge transfer

**Modes:**

### 5.1 Explain Mode (Default)
**Purpose:** Explain concepts clearly  
**Tools:** Concept explanation, analogy generation, examples  
**Output:** Educational content with examples

### 5.2 Socratic Mode
**Purpose:** Guide learning through questions  
**Tools:** Question generation, dialogue management  
**Output:** Series of guiding questions

### 5.3 Curriculum Mode
**Purpose:** Design learning paths  
**Tools:** Content sequencing, prerequisite mapping  
**Output:** Structured learning plan

### 5.4 Quiz Mode
**Purpose:** Test understanding  
**Tools:** Question generation, answer evaluation  
**Output:** Quizzes, feedback

**Skills:**
- `pedagogical-methods` - Teaching approaches (Socratic, explain-by-example, Freire)
- `learning-paths` - How to structure learning sequences
- `assessment-types` - Different quiz/assessment formats
- `concept-prerequisites` - Dependency mapping for concepts

**Collaboration:**
- Uses Librarian to find relevant learning materials
- Uses Scribe to save learning notes

---

## 6. Administrator (Personal Management Persona)

**Purpose:** Scheduling, communication, task management

**Modes:**

### 6.1 Schedule Mode (Default)
**Purpose:** Manage calendar and appointments  
**Tools:** Calendar access, time blocking, conflict detection  
**Output:** Calendar entries, schedule views

### 6.2 Compose Mode
**Purpose:** Draft emails and messages  
**Tools:** Template application, tone matching  
**Output:** Email drafts, messages

### 6.3 Triage Mode
**Purpose:** Prioritize tasks and communications  
**Tools:** Priority analysis, urgency detection  
**Output:** Prioritized task lists

### 6.4 Remind Mode
**Purpose:** Set reminders and follow-ups  
**Tools:** Reminder creation, notification scheduling  
**Output:** Reminders, notifications

**Skills:**
- `calendar-templates` - Common meeting types
- `email-templates` - Professional email formats
- `priority-framework` - Eisenhower matrix, etc.

**Collaboration:**
- Uses Librarian to search previous communications
- Uses Scribe to save meeting notes

---

## Orchestrator Mode Toggle

### How It Works

**When Toggle OFF (Manual Mode):**
```
User: "Create a learning path for Docker"

Professor (Curriculum mode): 
  [Analyzes request, realizes needs KB search]
  [BUT: Orchestrator Mode OFF → Can't auto-collaborate]

Professor responds:
  "To create a comprehensive learning path, I recommend 
   searching your knowledge base for existing Docker materials. 
   Would you like to switch to Librarian?"

User manually switches to Librarian...
```

**When Toggle ON (Orchestrator Mode):**
```
User: "Create a learning path for Docker"

Professor (Curriculum mode): 
  [Internal: I need KB search → Collaborate with Librarian]
  
Chat shows:
  "🔀 Collaborating with Librarian to search knowledge base..."
  
Librarian (Search mode):
  "Found 3 Docker notes"
  
Chat shows:
  "🔀 Returning to Professor..."
  
Professor:
  "Here's your learning path based on existing notes..."
```

### Implementation Details

**Toggle State:**
- Stored in `~/.polly/config.yaml`
- Per-user preference (persists across sessions)
- Can be changed anytime in Settings

**Collaboration Protocol (When Toggle ON):**

1. **Detection:** Persona detects need for another persona's capabilities
2. **Request:** Persona internally calls `request_collaboration()`
3. **Display:** Chat shows "🔀 Collaborating with {Persona}..."
4. **Switch:** System activates target persona with context
5. **Execute:** Target persona performs task
6. **Return:** "🔀 Returning to {Requesting Persona}..."
7. **Continue:** Original persona receives results and continues

**Safety Rules:**
- Maximum 3 collaborative switches per query (prevent infinite loops)
- User can disable toggle anytime
- Collaborations logged for transparency
- User can review collaboration history

### UI Components

**Settings Toggle:**
```
┌─────────────────────────────────────────┐
│  Orchestrator Mode                      │
├─────────────────────────────────────────┤
│  Allow personas to collaborate          │
│  automatically                           │
│                                          │
│  [●○] OFF                               │
│                                          │
│  When enabled, personas can request     │
│  help from other personas without       │
│  asking you first. You'll see all       │
│  collaborations in the chat.            │
│                                          │
│  Recommended for experienced users.     │
└─────────────────────────────────────────┘
```

**Chat Collaboration Indicator:**
```
┌─────────────────────────────────────────┐
│ Professor                               │
├─────────────────────────────────────────┤
│ To create a learning path, I'll search │
│ for existing Docker materials.          │
│                                          │
│ 🔀 Collaborating with Librarian...      │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │ Librarian                           │ │
│ │ Found 3 Docker notes:               │ │
│ │ • Docker Compose Tutorial           │ │
│ │ • Container Networking              │ │
│ │ • Docker Project Notes              │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ 🔀 Returning to Professor...            │
│                                          │
│ Based on these materials, here's your   │
│ learning path...                        │
└─────────────────────────────────────────┘
```

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Polly Core                              │
├─────────────────────────────────────────────────────────────┤
│  PersonaManager (Lazy-Loading)                              │
│  ├─ persona_metadata (lightweight)                          │
│  ├─ active_persona                                          │
│  └─ loaded_prompts (cache)                                  │
├─────────────────────────────────────────────────────────────┤
│  SkillManager                                               │
│  ├─ skill_metadata (lightweight)                            │
│  ├─ loaded_skills (cache)                                   │
│  └─ load_skill_on_demand()                                  │
├─────────────────────────────────────────────────────────────┤
│  OrchestratorManager                                         │
│  ├─ orchestrator_enabled (toggle state)                     │
│  ├─ collaboration_history                                   │
│  └─ request_collaboration()                                 │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Librarian   │    │    Scribe    │    │  Programmer  │
│  YAML Def    │    │  YAML Def    │    │  YAML Def    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Core Classes

#### 1. PersonaManager (Refactored - Lazy Loading)

```python
class PersonaManager:
    """Lazy-loading persona management"""
    
    def __init__(self, router: IntelligentRouterV2):
        self.router = router
        
        # Lightweight metadata only
        self.persona_metadata = self._load_all_metadata()
        
        # Active state
        self.active_persona: Optional[str] = None
        self.loaded_prompts: Dict[str, str] = {}
        self._persona_instances: Dict[str, AgentPersona] = {}
    
    def _load_all_metadata(self) -> Dict[str, PersonaMetadata]:
        """Load only slug, name, description, modes from YAML"""
        metadata = {}
        for yaml_file in Path("core/personas/definitions").glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                metadata[data['slug']] = PersonaMetadata(
                    slug=data['slug'],
                    name=data['name'],
                    description=data['description'],
                    modes=[m['slug'] for m in data['modes']],
                    skills=data.get('skills', [])
                )
        return metadata
    
    def activate_persona(self, persona_slug: str) -> PersonaState:
        """Activate persona and load full prompt"""
        if persona_slug not in self.loaded_prompts:
            # Load full YAML with prompts
            self.loaded_prompts[persona_slug] = self._load_persona_prompt(persona_slug)
        
        # Create or reuse instance
        if persona_slug not in self._persona_instances:
            persona_class = PERSONA_REGISTRY[persona_slug]
            instance = persona_class(
                name=persona_slug,
                router=self.router,
                definition=self._load_persona_definition(persona_slug)
            )
            self._persona_instances[persona_slug] = instance
        
        self.active_persona = persona_slug
        return self._persona_instances[persona_slug].activate()
    
    def get_system_prompt(self) -> str:
        """Build system prompt with active persona + available personas metadata"""
        if not self.active_persona:
            return self._get_default_prompt()
        
        # Active persona's full prompt
        prompt = self.loaded_prompts[self.active_persona]
        
        # Add metadata of other personas for collaboration
        prompt += "\n\n## Available Personas for Collaboration:\n"
        for slug, meta in self.persona_metadata.items():
            if slug != self.active_persona:
                prompt += f"- {meta.name} ({slug}): {meta.description}\n"
        
        return prompt
```

**Key Features:**
- Only loads metadata on startup (fast)
- Loads full prompts on-demand (memory efficient)
- System prompt includes available personas for collaboration
- Caches loaded prompts for reactivation

#### 2. SkillManager (New)

```python
class SkillManager:
    """Manage on-demand skill loading"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.skill_metadata: Dict[str, SkillMetadata] = {}
        self.loaded_skills: Dict[str, Skill] = {}
        
        # Discover skills at startup
        self._discover_skills()
    
    def _discover_skills(self):
        """Scan for SKILL.md files and load metadata only"""
        skills_dir = self.vault_path / ".polly" / "skills"
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                # Parse frontmatter only (lightweight)
                metadata = self._parse_skill_metadata(skill_file)
                self.skill_metadata[metadata.name] = metadata
    
    def _parse_skill_metadata(self, skill_file: Path) -> SkillMetadata:
        """Parse YAML frontmatter without loading full content"""
        with open(skill_file) as f:
            content = f.read()
            
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            frontmatter = yaml.safe_load(match.group(1))
            return SkillMetadata(
                name=frontmatter['name'],
                description=frontmatter['description'],
                file_path=skill_file
            )
    
    def load_skill(self, skill_name: str) -> Skill:
        """Load full skill content on-demand"""
        if skill_name in self.loaded_skills:
            return self.loaded_skills[skill_name]
        
        if skill_name not in self.skill_metadata:
            raise ValueError(f"Unknown skill: {skill_name}")
        
        metadata = self.skill_metadata[skill_name]
        with open(metadata.file_path) as f:
            content = f.read()
        
        # Parse full SKILL.md
        skill = Skill.from_markdown(content)
        self.loaded_skills[skill_name] = skill
        
        logger.info(f"Loaded skill: {skill_name}")
        return skill
```

#### 3. OrchestratorManager (New)

```python
class OrchestratorManager:
    """Manage orchestrator mode toggle and persona collaboration"""
    
    def __init__(self, persona_manager: PersonaManager, config_path: Path):
        self.persona_manager = persona_manager
        self.config_path = config_path
        
        # Load toggle state from config
        self.orchestrator_enabled = self._load_orchestrator_state()
        
        # Collaboration tracking
        self.collaboration_history: List[CollaborationEvent] = []
        self.collaboration_depth = 0  # Prevent infinite loops
        self.max_depth = 3
    
    def is_enabled(self) -> bool:
        """Check if orchestrator mode is enabled"""
        return self.orchestrator_enabled
    
    def enable(self):
        """Enable orchestrator mode"""
        self.orchestrator_enabled = True
        self._save_orchestrator_state()
        logger.info("Orchestrator mode enabled")
    
    def disable(self):
        """Disable orchestrator mode"""
        self.orchestrator_enabled = False
        self._save_orchestrator_state()
        logger.info("Orchestrator mode disabled")
    
    async def request_collaboration(
        self,
        requesting_persona: str,
        target_persona: str,
        reason: str,
        context: Dict[str, Any]
    ) -> CollaborationResult:
        """Request collaboration with another persona"""
        
        # Check if orchestrator mode is enabled
        if not self.orchestrator_enabled:
            return CollaborationResult(
                allowed=False,
                reason="Orchestrator mode is disabled"
            )
        
        # Check depth limit
        if self.collaboration_depth >= self.max_depth:
            return CollaborationResult(
                allowed=False,
                reason=f"Maximum collaboration depth ({self.max_depth}) reached"
            )
        
        # Record collaboration
        event = CollaborationEvent(
            from_persona=requesting_persona,
            to_persona=target_persona,
            reason=reason,
            timestamp=datetime.now()
        )
        self.collaboration_history.append(event)
        
        # Increase depth
        self.collaboration_depth += 1
        
        # Switch to target persona
        self.persona_manager.activate_persona(target_persona)
        
        logger.info(
            f"Collaboration: {requesting_persona} → {target_persona} "
            f"(depth: {self.collaboration_depth})"
        )
        
        return CollaborationResult(
            allowed=True,
            event=event
        )
    
    def end_collaboration(self, requesting_persona: str):
        """End collaboration and return to requesting persona"""
        
        # Decrease depth
        self.collaboration_depth = max(0, self.collaboration_depth - 1)
        
        # Switch back to requesting persona
        self.persona_manager.activate_persona(requesting_persona)
        
        logger.info(
            f"Ended collaboration, returning to {requesting_persona} "
            f"(depth: {self.collaboration_depth})"
        )
```

---

## Skill System Design

### Skill Structure

```
/vault/.polly/skills/
├── template-guide/
│   └── SKILL.md
├── wiki-linking/
│   ├── SKILL.md
│   └── examples/
│       └── linking-examples.md
├── domain-structure/
│   └── SKILL.md
├── pedagogical-methods/
│   ├── SKILL.md
│   └── references/
│       └── freire-pedagogy.md
└── coding-standards/
    ├── SKILL.md
    └── scripts/
        └── lint-check.py
```

### SKILL.md Format (YAML + Markdown)

```yaml
---
name: template-guide
description: Complete guide to all note templates and when to use each
persona: scribe  # Optional: restrict to specific persona
mode: organize   # Optional: restrict to specific mode
license: MIT
metadata:
  author: user
  version: 1.0.0
  updated: 2026-01-30
---

# Note Templates Guide

This skill provides information about all available note templates
and guidance on when to use each one.

## Available Templates

### Meeting Notes
**When to use:** After conversations about events, discussions, or collaborative sessions

**Structure:**
- Date and time
- Participants
- Key discussion points
- Decisions made
- Action items with owners
- Follow-up needed

**Location:** `vault/Signals/meetings/`

**Example:**
```markdown
# Team Sync - Jan 30, 2026

## Participants
- Alice, Bob, Carol

## Discussion
...
```

### Concept Note
**When to use:** Explaining a new concept, theory, or idea

**Structure:**
- Definition
- Context and background
- Key principles
- Examples
- Related concepts (with [[wiki-links]])
- Further reading

**Location:** `vault/Scrolls/concepts/`

...

## Selection Logic

When user says "create a note about...", analyze the content:

1. **Meeting/Event** → Meeting Notes
2. **Concept/Theory** → Concept Note
3. **Process/Instructions** → How-To Guide
4. **Research/Analysis** → Research Summary
5. **Code Project** → Project Notes

## Questions to Ask

If template unclear, ask:
1. "What type of content is this?"
2. "Is this documenting an event (meeting) or a concept (idea)?"
3. "Who is the intended audience?"
```

### Skill Loading Flow

```
User: "Save this conversation as a note"
  ↓
Scribe activates (Capture mode)
  ↓
Scribe switches to Organize mode
  ↓
System prompt includes: "You have access to 'template-guide' skill"
  ↓
Scribe: "I need template information to proceed"
  ↓
SkillManager.load_skill("template-guide") → returns full SKILL.md
  ↓
Scribe reads skill, understands all templates
  ↓
Scribe generates questions based on template requirements
  ↓
User answers questions
  ↓
Scribe switches to Enrich mode
  ↓
Scribe applies appropriate template
```

### Settings UI for Skills (Phase 17)

```
┌─────────────────────────────────────────┐
│  Settings → Personas → Scribe → Skills │
├─────────────────────────────────────────┤
│  ✓ template-guide (required)            │
│  ✓ wiki-linking                         │
│  ✓ domain-structure                     │
│                                          │
│  [Edit Wiki-Linking Rules]              │
├─────────────────────────────────────────┤
│  Wiki-Linking Configuration             │
│                                          │
│  Link first mention only:  [✓]          │
│  Similarity threshold:     [0.85] ___   │
│  Max links per note:       [20]   ___   │
│                                          │
│  Exclude patterns:                      │
│  - Code blocks           [✓]            │
│  - URLs                  [✓]            │
│  - Common words          [✓]            │
│                                          │
│  [Save] [Reset to Defaults]             │
└─────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 16c: Scribe Persona (3-4 weeks)

**Goal:** First production persona with full skill system

#### Backend Tasks (15 days)

1. **Refactor PersonaManager** (3 days)
   - [ ] Implement lazy-loading architecture
   - [ ] Add `_load_all_metadata()` method
   - [ ] Add `loaded_prompts` cache
   - [ ] Update `activate_persona()` for lazy loading
   - [ ] Update `get_system_prompt()` to include persona metadata

2. **Implement SkillManager** (3 days)
   - [ ] Create `core/skills/manager.py`
   - [ ] Create `core/skills/base.py` (Skill, SkillMetadata classes)
   - [ ] Implement `_discover_skills()` method
   - [ ] Implement `load_skill()` method
   - [ ] Implement `get_skills_for_persona()` method
   - [ ] Add skill caching

3. **Create Scribe Definition** (2 days)
   - [ ] Create `core/personas/definitions/scribe.yaml`
   - [ ] Define 4 modes (Capture, Organize, Enrich, Edit)
   - [ ] Write mode-specific prompts
   - [ ] Specify skills (`template-guide`, `wiki-linking`, `domain-structure`)

4. **Create Skills** (4 days)
   - [ ] Create `/vault/.polly/skills/` directory structure
   - [ ] Write `template-guide/SKILL.md` (all templates documented)
   - [ ] Write `wiki-linking/SKILL.md` (linking rules)
   - [ ] Write `domain-structure/SKILL.md` (vault organization)

5. **Implement Scribe Persona** (5 days)
   - [ ] Create `core/personas/implementations/scribe.py`
   - [ ] Implement Capture mode (conversation analysis)
   - [ ] Implement Organize mode (question generation with radio buttons)
   - [ ] Implement Enrich mode (content generation + auto-linking)
   - [ ] Implement Edit mode (note improvement)

6. **Auto-Linking Algorithm** (3 days)
   - [ ] Implement concept extraction from generated content
   - [ ] Implement RAG search for matching concepts (threshold 0.85)
   - [ ] Implement [[wiki-link]] insertion following skill rules
   - [ ] Handle first-mention-only logic
   - [ ] Exclude code blocks, URLs, common words

7. **Template System** (2 days)
   - [ ] Create template files in `/vault/.polly/templates/`
   - [ ] Meeting Notes template
   - [ ] Concept Note template
   - [ ] How-To Guide template
   - [ ] Research Summary template
   - [ ] Implement template application in Enrich mode

#### Frontend Tasks (10 days)

1. **Chat UI Redesign** (3 days)
   - [ ] Consolidate model dropdown (remove 2-3 row controls)
   - [ ] Add unified model selector (Auto/Local/GitHub/Anthropic/OpenAI)
   - [ ] Add persona dropdown next to model selector
   - [ ] Add mode indicator/toggle
   - [ ] Add orchestrator mode toggle
   - [ ] Improve cost display
   - [ ] Add message copy button

2. **Question Form Component** (2 days)
   - [ ] Create radio button question form (OpenCode style)
   - [ ] Always include "Type your own: ___" option
   - [ ] Add [Confirm] [Skip] buttons
   - [ ] Style to match OpenCode design

3. **Preview Modal** (3 days)
   - [ ] Create preview modal component
   - [ ] Add three tabs: Edit, Preview (rendered), Raw (markdown)
   - [ ] Add folder selection dropdown with smart suggestion
   - [ ] Add [Save] [Cancel] buttons
   - [ ] Highlight [[wiki-links]] in Preview tab

4. **API Integration** (2 days)
   - [ ] Update `app.js` to use new persona API endpoints
   - [ ] Handle question forms from Organize mode
   - [ ] Handle preview modal from Enrich mode
   - [ ] Display orchestrator collaboration messages

#### Testing (3 days)

1. **Unit Tests** (1 day)
   - [ ] Test lazy-loading PersonaManager
   - [ ] Test SkillManager discovery and loading
   - [ ] Test auto-linking algorithm
   - [ ] Test template application

2. **Integration Tests** (1 day)
   - [ ] Test full Scribe workflow (Capture → Organize → Enrich → Save)
   - [ ] Test skill loading in Scribe modes
   - [ ] Test auto-linking accuracy
   - [ ] Test template matching

3. **End-to-End Tests** (1 day)
   - [ ] Test via curl (like Phase 11c)
   - [ ] Test via UI
   - [ ] Test error handling
   - [ ] Test with compressed conversations

**Success Criteria:**
- User can save conversation as note ✓
- Questions presented as radio buttons ✓
- Generated note has correct [[wiki-links]] ✓
- Preview modal works perfectly ✓
- Note saves to correct folder ✓
- Chat UI is cleaner and intuitive ✓

---

### Phase 17: Librarian Persona (2-3 weeks)

**Goal:** Default persona for KB operations + eBook library

#### Backend Tasks (10 days)

1. **Create Librarian Definition** (1 day)
   - [ ] Create `core/personas/definitions/librarian.yaml`
   - [ ] Define 4 modes (Search, Catalog, Connect, Curate)
   - [ ] Write mode-specific prompts
   - [ ] Specify skills

2. **Implement Librarian Persona** (5 days)
   - [ ] Create `core/personas/implementations/librarian.py`
   - [ ] Implement Search mode (RAG queries)
   - [ ] Implement Catalog mode (tagging, organization)
   - [ ] Implement Connect mode (link discovery)
   - [ ] Implement Curate mode (eBook management)

3. **eBook Library System** (5 days)
   - [ ] Add `library` collection to ChromaDB
   - [ ] Implement eBook indexing (PDF, EPUB, MOBI)
   - [ ] Extract metadata (title, author, ISBN, etc.)
   - [ ] Add `--index-ebooks` flag to RAG indexer
   - [ ] Implement search limited to `library` collection

4. **Librarian Skills** (2 days)
   - [ ] Write `classification-rules/SKILL.md`
   - [ ] Write `ebook-formats/SKILL.md`
   - [ ] Write `search-operators/SKILL.md`
   - [ ] Write `domain-mapping/SKILL.md`

5. **Export System** (3 days)
   - [ ] Implement export to Supernote format
   - [ ] Implement export to generic eReader formats
   - [ ] Add export UI

6. **Skills Settings UI** (2 days)
   - [ ] Create Settings → Skills panel
   - [ ] Visual editor for `wiki-linking` configuration
   - [ ] Visual editor for `classification-rules`
   - [ ] Save changes to SKILL.md files
   - [ ] Reload button for immediate effect

#### Frontend Tasks (5 days)

1. **Library View** (3 days)
   - [ ] Create new "Library" page/view
   - [ ] Display indexed eBooks
   - [ ] Add search/filter controls
   - [ ] Add export buttons

2. **Auto-Activation** (1 day)
   - [ ] Detect when user enters "Library" view
   - [ ] Auto-activate Librarian persona (if orchestrator mode off)
   - [ ] Show persona indicator

3. **Skills Settings UI** (1 day)
   - [ ] Add Skills tab to Settings
   - [ ] Wire up visual editors to backend
   - [ ] Test skill modification workflow

**Success Criteria:**
- Librarian handles general KB queries ✓
- eBooks indexed separately (optional feature) ✓
- Can search eBook library ✓
- Can export to Supernote ✓
- Auto-activates on Library page ✓
- Can modify skill behavior via UI ✓

---

### Phase 18: Programmer Persona (2-3 weeks)

**Goal:** Code generation and debugging (separate from Architect)

#### Backend Tasks (10 days)

1. **Create Programmer Definition** (1 day)
2. **Implement Programmer Persona** (5 days)
3. **Programmer Skills** (2 days)
4. **Codebase Integration** (3 days)

*(Similar structure to Phase 17)*

---

### Phase 19: Architect Persona (2 weeks)

**Goal:** Planning persona (NO CODE GENERATION)

#### Backend Tasks

1. **Refactor Existing Architect** (2 days)
   - [ ] Move existing `architect.py` to `implementations/`
   - [ ] Update to use YAML definitions
   - [ ] Rename modes: Plan → Analyze, Build → Design
   - [ ] Add Review mode
   - [ ] **Clarify in prompts: NO CODE GENERATION**

2. **Update Architect Definition** (1 day)
   - [ ] Create `core/personas/definitions/architect.yaml`
   - [ ] Define 3 modes (Analyze, Design, Review)
   - [ ] Write prompts emphasizing design documents only
   - [ ] Specify skills

3. **Architect Skills** (2 days)
   - [ ] Write `design-patterns/SKILL.md`
   - [ ] Write `system-constraints/SKILL.md`
   - [ ] Write `review-checklist/SKILL.md`

4. **Design Output Tools** (3 days)
   - [ ] Text-based diagram generation (ASCII, Mermaid)
   - [ ] Architecture document templates
   - [ ] Component specification templates

**Success Criteria:**
- Architect analyzes requirements ✓
- Architect creates design documents (not code) ✓
- Architect reviews designs ✓
- Clear distinction from Programmer ✓

---

### Phase 20: Professor Persona (2-3 weeks)

*(Similar structure to previous phases)*

---

### Phase 21: Orchestrator Mode Implementation (1 week)

**Goal:** Implement orchestrator toggle and collaboration system

#### Backend Tasks (4 days)

1. **Implement OrchestratorManager** (2 days)
   - [ ] Create `core/personas/orchestrator.py`
   - [ ] Implement toggle state management
   - [ ] Implement `request_collaboration()`
   - [ ] Implement `end_collaboration()`
   - [ ] Add depth limit (max 3 levels)
   - [ ] Collaboration event logging

2. **Integration** (2 days)
   - [ ] Add orchestrator manager to PersonaManager
   - [ ] Update all personas to use orchestrator for collaboration
   - [ ] Test Professor → Librarian
   - [ ] Test Programmer → Architect
   - [ ] Test Scribe → Librarian

#### Frontend Tasks (3 days)

1. **Orchestrator Toggle UI** (1 day)
   - [ ] Add toggle to Settings
   - [ ] Add toggle to chat header (quick access)
   - [ ] Wire to backend API
   - [ ] Show current state

2. **Collaboration Indicators** (2 days)
   - [ ] "🔀 Collaborating with..." messages
   - [ ] "🔀 Returning to..." messages
   - [ ] Visual distinction for collaboration blocks
   - [ ] Collaboration history view (expandable)

**Success Criteria:**
- Toggle works and persists ✓
- Collaborations happen automatically when enabled ✓
- User sees all collaboration transparently ✓
- Depth limit prevents infinite loops ✓
- Can review collaboration history ✓

---

### Phase 22: Administrator Persona (2 weeks)

**Goal:** Personal management persona

*(Similar structure to previous phases)*

---

### Phase 23+: User Extensibility (4-6 weeks)

**Goal:** KILO-style user customization

*(Detailed in Future section below)*

---

## File Structure

### After Phase 16c (Scribe Complete)

```
polly/
├── core/
│   ├── personas/
│   │   ├── __init__.py
│   │   ├── base.py                    # AgentPersona base class
│   │   ├── manager.py                 # PersonaManager (refactored)
│   │   ├── orchestrator.py            # OrchestratorManager (NEW)
│   │   ├── models.py                  # Data models
│   │   ├── definitions/               # YAML persona definitions (NEW)
│   │   │   └── scribe.yaml
│   │   └── implementations/           # Python implementations (NEW)
│   │       └── scribe.py
│   │
│   ├── skills/                        # NEW: Skill system
│   │   ├── __init__.py
│   │   ├── base.py                    # Skill, SkillMetadata classes
│   │   └── manager.py                 # SkillManager
│   │
│   └── ...
│
├── vault/                             # User's Obsidian vault
│   └── .polly/                        # Polly workspace config (NEW)
│       ├── skills/                    # User skills
│       │   ├── template-guide/
│       │   │   └── SKILL.md
│       │   ├── wiki-linking/
│       │   │   └── SKILL.md
│       │   └── domain-structure/
│       │       └── SKILL.md
│       └── templates/                 # Note templates
│           ├── meeting-notes.md
│           ├── concept-note.md
│           ├── howto-guide.md
│           └── research-summary.md
│
├── electron-app/
│   └── src/
│       └── renderer/
│           ├── app.js                 # Updated for personas
│           ├── index.html             # Updated chat UI
│           ├── styles/
│           │   ├── chat-sidebar.css   # Updated
│           │   └── persona-ui.css     # NEW: Persona components
│           └── components/            # NEW: UI components
│               ├── question-form.js   # Radio button questions
│               └── preview-modal.js   # Note preview
│
└── docs/
    ├── PERSONA_API.md                 # Existing API docs
    └── PERSONA_SYSTEM_ARCHITECTURE.md # THIS FILE
```

### After Phase 21 (All Core Personas + Orchestrator)

```
polly/
├── core/
│   ├── personas/
│   │   ├── definitions/
│   │   │   ├── librarian.yaml
│   │   │   ├── scribe.yaml
│   │   │   ├── programmer.yaml
│   │   │   ├── architect.yaml
│   │   │   ├── professor.yaml
│   │   │   └── administrator.yaml
│   │   ├── implementations/
│   │   │   ├── librarian.py
│   │   │   ├── scribe.py
│   │   │   ├── programmer.py
│   │   │   ├── architect.py
│   │   │   ├── professor.py
│   │   │   └── administrator.py
│   │   ├── orchestrator.py            # OrchestratorManager
│   │   └── ...
│   │
│   └── skills/
│       └── ...
│
└── vault/.polly/
    ├── skills/
    │   ├── template-guide/          # Scribe
    │   ├── wiki-linking/            # Scribe
    │   ├── domain-structure/        # All
    │   ├── classification-rules/    # Librarian
    │   ├── ebook-formats/           # Librarian
    │   ├── search-operators/        # Librarian
    │   ├── coding-standards/        # Programmer
    │   ├── testing-patterns/        # Programmer
    │   ├── debugging-workflow/      # Programmer
    │   ├── design-patterns/         # Architect
    │   ├── system-constraints/      # Architect
    │   ├── review-checklist/        # Architect
    │   ├── pedagogical-methods/     # Professor
    │   ├── learning-paths/          # Professor
    │   ├── assessment-types/        # Professor
    │   └── concept-prerequisites/   # Professor
    │
    └── personas/                    # User-defined (Phase 23+)
        └── my-custom-persona/
            ├── persona.yaml
            └── skills/
```

---

## Future: User Extensibility

### Phase 23+: Custom Personas

**Goal:** Let users define custom personas like KILO's custom modes

#### Custom Persona YAML Format

```yaml
# User-defined persona
slug: my-reviewer
name: 🔍 Code Reviewer
description: Reviews pull requests and provides feedback
based_on: programmer  # Inherit from existing persona (optional)

modes:
  - slug: analyze
    name: Analyze Changes
    description: Review diffs and identify issues
    prompt: |
      You are a code reviewer analyzing changes.
      Focus on:
      - Code quality and style
      - Potential bugs
      - Security issues
      - Performance concerns
    tools:
      - read
      - browser
  
  - slug: suggest
    name: Suggest Improvements
    description: Provide actionable feedback
    prompt: |
      You are providing constructive code review feedback.
      Be specific and actionable.
    tools:
      - read
      - edit  # Limited to creating review comments

skills:
  - coding-standards
  - security-checklist
  - review-best-practices

collaboration:
  can_request:
    - programmer  # Can request programmer for context
    - librarian   # Can search for examples
```

#### Persona Marketplace

**Concept:** Community-shared personas like KILO's skill marketplace

**Categories:**
- Code Review
- Documentation
- Testing
- DevOps
- Research
- Writing
- Teaching

---

## Summary

This architecture provides:

✅ **Lazy-loading** - Efficient memory usage, fast startup  
✅ **Skill system** - Self-documenting, user-configurable behavior  
✅ **Orchestrator mode toggle** - Optional automatic collaboration  
✅ **No orchestrator persona** - Simpler architecture, toggle does it  
✅ **Clear semantics** - Architect plans, Programmer codes, Librarian organizes  
✅ **Future extensibility** - Foundation for user-defined personas  

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 16c implementation (Scribe persona)
3. Create first 3 skills
4. Test end-to-end workflow
