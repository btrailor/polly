# Phase 23: Project Management & Documentation-First Workflows

**Status:** Planning  
**Priority:** Medium (Tier 5 - Optional Enhancement)  
**Estimated Effort:** 3-4 weeks  
**Dependencies:** Phase 1.5 (Domains), Phase 13 (Pattern Learning), Phase 16 (Native Notes), Phase 17 (Code Workspace)  
**Last Updated:** January 28, 2026

---

## Overview

Phase 23 introduces comprehensive project management features with a **documentation-first philosophy**. Rather than treating documentation as an afterthought, Polly makes it central to project workflow - forcing intentional planning before building.

### Core Philosophy

**"You don't build a rough idea, you plan until it is a detailed vision."**

This comes from observing how development often jumps into building without sufficient planning, leading to:
- Architecture inconsistencies as projects evolve
- Lost context when switching between features
- Forgotten implementation details
- Documentation debt
- Misalignment between vision and execution

**Phase 23 makes Polly resist jumping into build phase until planning threshold is reached.**

---

## Problem Statement

From brain dump observations:

> "Thinking about how in developing Polly, you have to tell OpenCode to document, update documents, etc. What if projects could be standardized for workflows in a way that prioritizes documentation and organization?"

> "What if Polly as a coding assistant (for instance) always kept a high level overview of the project? What if it learned build patterns and didn't have to repeatedly learn to build a piece of firmware (thinking Aleph)?"

> "As software becomes more complex, gets refined through AI interaction over time, new ideas are introduced, old ideas discarded, developed ideas get iterated upon, planning document bloat and disorganization get introduced. It becomes increasingly difficult for the AI agent to keep track of everything."

> "We need a way to standardize the documentation process for ongoing development."

**The Challenge:**
- AI agents forget context between sessions
- Planning documents become bloated and disorganized over time
- No standard workflow ensures documentation stays current
- Agents must re-learn build commands, architecture, project structure repeatedly
- UI changes disconnect from documentation (Settings sidebar example)

---

## Core Features

### 1. Standardized Project Workflows

**What It Does:**
Projects follow documentation-first templates that ensure planning before building.

**Project Types:**
- **Code Projects:** Software, firmware, libraries, apps
- **Writing Projects:** Documentation, essays, books, research
- **Creative Projects:** Design, music, art, multimedia
- **Research Projects:** Academic research, explorations, experiments
- **Custom Projects:** User-defined workflows

**Standard Project Structure:**
```
~/Polly/Projects/Aleph/
├── PROJECT.md                  # High-level overview (always current)
├── ARCHITECTURE.md             # System design (updated on changes)
├── ROADMAP.md                  # Phases, milestones, status
├── BUILD.md                    # Build commands, dependencies
├── DECISIONS.md                # ADR (Architecture Decision Records)
├── PLANNING/                   # Detailed planning documents
│   ├── Phase1_Planning.md
│   ├── Phase2_Planning.md
│   └── Feature_X_Spec.md
├── SESSIONS/                   # Session summaries (auto-generated)
│   ├── 2026-01-28_UI_Refactor.md
│   └── 2026-01-29_Bug_Fixes.md
└── CODE/                       # Actual code (linked, not managed by Polly)
```

**Key Principle:** Documentation structure is standardized, but content is flexible.

---

### 2. Project-Specific Pattern Learning

**What It Does:**
Polly learns and remembers project-specific information that doesn't belong in general knowledge base.

**What Gets Learned Per-Project:**

**Build Patterns:**
- Build commands: `make`, `npm run build`, `cargo build --release`
- Test commands: `pytest tests/`, `npm test`, `cargo test`
- Deploy commands: `./deploy.sh production`
- Environment setup: virtual env, dependencies, configs

**Architecture Patterns:**
- Key file locations: "Settings are in sidebar.tsx, not settingsPanel.tsx"
- Naming conventions: "Components use PascalCase, utilities use camelCase"
- Code organization: "Business logic in /core, UI in /components"
- Dependency injection patterns

**Project Context:**
- Tech stack: "React 18 + TypeScript + Tailwind"
- External APIs: "Uses Stripe API for payments"
- Third-party integrations: "Electron IPC for main/renderer communication"
- Performance requirements: "Must handle 10k+ notes without lag"

**Project-Specific Vocabulary:**
- Domain terms: "Aleph = audio framework, not the letter"
- Acronyms: "RAG = Retrieval Augmented Generation"
- Internal terminology: "Sigils = code domain"

**How It Works:**
- Patterns stored per-project in `~/Polly/Projects/{name}/.polly/patterns.json`
- Only loaded when working on that project
- Separate from global patterns (Phase 13)
- Prevents cross-project confusion (Aleph vs. aleph-builder)

**Integration with Phase 13:**
- Uses same pattern learning engine
- Separate storage per project
- Activated by project context (working in project folder)

---

### 3. Plan/Build Modes for Code Workspace

**What It Does:**
Polly has two distinct modes when working on code projects: **Plan Mode** and **Build Mode**.

**Plan Mode:**
- **Goal:** Gather requirements and create detailed specification before writing code
- **Behavior:** 
  - Asks clarifying questions to understand requirements
  - Refuses to write code until specification is complete
  - Documents architectural decisions
  - Identifies dependencies and constraints
  - Creates implementation plan with steps
- **Threshold:** Must reach minimum planning completeness (e.g., architecture defined, edge cases documented)
- **Mental Model:** Uses "Constraint as Meaning" - planning constraints enable better building

**Build Mode:**
- **Goal:** Execute implementation according to plan
- **Behavior:**
  - Writes code following specification
  - Refers back to planning documents for context
  - Updates documentation as implementation progresses
  - Flags deviations from plan and asks for approval
- **Threshold:** Can only enter after planning threshold met
- **Mental Model:** Uses "Instrument vs Track" - building is generative but follows framework

**Mode Switching:**
```
User: "Build a RAG system for Polly"

Polly (Plan Mode):
"Before we start building, let's plan this properly. I have some questions:

1. What types of documents will be indexed? (markdown, code, PDFs, etc.)
2. What embedding model should we use? (local/cloud, which one?)
3. What vector database? (Qdrant, Pinecone, FAISS, etc.)
4. What are the performance requirements? (# of documents, query latency)
5. How should it integrate with existing systems? (domains, patterns, etc.)

Let me create a specification document as we discuss."

[After thorough planning]

Polly (Build Mode):
"Planning complete. I have a clear specification:
- Local Qdrant vector DB
- sentence-transformers/all-MiniLM-L6-v2 for embeddings
- Support markdown, code, PDF
- Target: <200ms query latency for 10k docs
- Integration with domain system for filtering

Ready to build. Shall I start with the RAG core module?"
```

**How It Knows Planning Is Complete:**
1. **Architecture Decision:** Choice made for key components
2. **Requirements Documented:** Functional and non-functional requirements listed
3. **Edge Cases Considered:** Error handling, edge cases discussed
4. **Integration Points Defined:** How it connects to existing system
5. **Success Criteria Clear:** How to test if implementation works

**User Override:**
User can force Build Mode if needed: "I know the plan, just build it"

**Benefits:**
- Prevents incomplete implementations
- Ensures alignment before writing code
- Reduces rework from misunderstandings
- Creates documentation as a natural byproduct
- Builds "think before you code" habit

---

### 4. Always-Current Project Overview

**What It Does:**
Polly maintains a high-level `PROJECT.md` that is **always current** with latest architecture and state.

**PROJECT.md Structure:**
```markdown
# Aleph Audio Framework

**Status:** Active Development (Phase 2)  
**Last Updated:** 2026-01-28 (automated)

## What It Is
Aleph is a modular audio processing framework for embedded systems,
designed for Monome hardware with real-time DSP capabilities.

## Architecture
[High-level diagram or description]

## Current State
- Phase 1 (Audio Engine): ✅ Complete
- Phase 2 (UI System): 🚧 In Progress (60% complete)
- Phase 3 (Module System): 📋 Planned

## Key Components
- Audio Engine: `src/audio/` - Real-time DSP processing
- UI System: `src/ui/` - Grid-based interface (refactored Jan 2026)
- Module System: `src/modules/` - Pluggable audio modules

## Recent Major Changes
- 2026-01-28: Refactored UI system to use new grid layout
- 2026-01-15: Added MIDI input support
- 2025-12-10: Initial audio engine implementation

## Build Commands
```bash
make          # Build all
make test     # Run tests
make flash    # Deploy to hardware
```

## Next Steps
- Complete UI system refactor
- Begin module system planning
- See ROADMAP.md for details
```

**How It Stays Current:**

**Option 1: Manual Update Prompts**
- After major changes, Polly asks: "Should I update PROJECT.md?"
- User confirms, Polly updates high-level summary
- Simple, explicit control

**Option 2: Automatic Updates**
- Polly detects architectural changes (Phase 17 integration)
- Automatically updates PROJECT.md in background
- User reviews changes in SESSIONS/ summary
- More proactive, less manual

**Option 3: Hybrid (Recommended)**
- Minor updates: automatic (build command changes, status updates)
- Major updates: prompt for confirmation (architecture changes, new phases)
- Best balance of automation and control

**Integration with Architecture Changes:**
> "Anytime a code project makes architectural changes, it asks how does this change our high-level understanding of the project?"

When Polly detects major changes:
```
Polly: "I noticed we made significant UI changes (grid layout → flex layout).

This affects our architecture:
- UI rendering system now uses flex-based layout
- Settings panel moved from sidebar to header
- Component structure reorganized

Should I update:
1. PROJECT.md (high-level architecture section)
2. ARCHITECTURE.md (detailed UI architecture)
3. Create ADR (Architecture Decision Record) for this change?

[Yes, update all] [Just PROJECT.md] [I'll do it manually]"
```

**Benefits:**
- New AI sessions start with current context
- Onboarding new developers is instant
- No more "read 20 documents to understand project"
- Architecture and reality stay aligned
- Documentation debt prevented, not accumulated

---

### 5. Architectural Change Awareness

**What It Does:**
Polly actively tracks when architectural changes happen and ensures documentation stays synchronized.

**Detection Triggers:**

**Code Changes:**
- Moving files between directories
- Renaming core components
- Changing API contracts
- Refactoring major modules

**UI Changes:**
- Moving UI elements (Settings sidebar → header)
- Changing navigation structure
- Modifying user workflows

**System Changes:**
- Adding new dependencies
- Changing build system
- Modifying database schema
- Introducing new integrations

**Response:**
```
Polly: "Architectural change detected: Settings moved from sidebar to header.

I should update documentation:
- ARCHITECTURE.md: UI structure section
- PROJECT.md: Component locations
- Patterns: 'Settings location' pattern

I should also check:
- Are there other files that reference old Settings location?
- Should this be documented as an ADR (why we moved it)?

[Update docs automatically] [Show me what would change] [Skip]"
```

**ADR (Architecture Decision Records):**
When major architectural changes occur, Polly can create ADRs:

```markdown
# ADR-003: Move Settings from Sidebar to Header

**Date:** 2026-01-28  
**Status:** Accepted  
**Deciders:** User + Polly  

## Context
Settings panel was in left sidebar, causing layout issues as sidebar
content grew. Users reported difficulty finding settings.

## Decision
Move Settings to header as dedicated button, opens modal overlay.

## Consequences
**Positive:**
- More discoverable (always visible in header)
- Frees sidebar space for contextual content
- Consistent with Obsidian-inspired design

**Negative:**
- Requires modal overlay (additional UI complexity)
- Settings not visible alongside content (but rarely needed)

## Implementation
- Created SettingsModal component
- Removed settings-panel from sidebar
- Added settings button to header (gear icon)
```

**Why ADRs Matter:**
- Documents *why* decisions were made (prevents future confusion)
- Shows evolution of thinking over time
- Helps new contributors understand history
- Prevents re-litigating old decisions

---

### 6. Compression & Memory System

**What It Does:**
Polly uses "shorthand" compression for conversation context, keeping full history without context limit bloat.

**Problem:**
> "You know what shorthand is? What if Polly had its own version of shorthand that it uses with itself in cases where say the memory for conversation context is dwindling? It then summarizes for itself in its own super efficient shorthand so that it has everything in context and can move forward with complete knowledge of what came before and with greater efficiency?"

**Polly Shorthand Format:**

**Human Conversation:**
```
User: "I want to add a dark mode toggle to the application"
Polly: "Great idea! We should implement this with CSS variables for easy theming..."
[200+ tokens of discussion]
```

**Compressed Shorthand:**
```json
{
  "intent": "add_feature",
  "feature": "dark_mode_toggle",
  "decisions": {
    "approach": "css_variables",
    "ui_location": "settings_panel",
    "storage": "localStorage"
  },
  "status": "planning_complete",
  "next": "implement_css_vars"
}
```

**Compression Ratio:** 10:1 to 100:1 depending on conversation

**When Compression Happens:**
1. Conversation reaches token limit (e.g., 6k / 8k tokens)
2. Polly compresses oldest portions into shorthand
3. Retains compressed version + recent context
4. Can "uncompress" if user asks about old topic

**Compressed Storage:**
```
~/Polly/Projects/Aleph/.polly/compressed_context.json
[
  {
    "timestamp": "2026-01-28T10:30:00Z",
    "topic": "ui_refactor",
    "compressed": { ... },
    "tokens_saved": 1250
  },
  ...
]
```

**Integration with Patterns:**
> "Make sure that when compression strategy is implemented (shorthand) that patterns use compressed language formats. Integrate compression and pattern storage."

Patterns stored in compressed format:
```json
{
  "pattern_type": "build_command",
  "trigger": "build_aleph",
  "action": {
    "cmd": "make",
    "cwd": "/Users/brett/aleph",
    "env": {"ARCH": "arm"}
  },
  "confidence": 0.95
}
```

Instead of storing full conversation explaining build process.

**Benefits:**
- Extended conversation memory without hitting limits
- Project context preserved across sessions
- Efficient storage and retrieval
- Patterns and compression work together

---

### 7. Context-Aware RAG Filtering

**What It Does:**
Different Polly modes prioritize different knowledge sources - Calendar doesn't need codebase, Code doesn't need calendar.

**Problem:**
> "Consider how knowledge chunks from things like connected codebases could be made more contextually relevant when chatting to code window vs chatting with calendar. Calendar doesn't need to know my codebase for Aleph. How do we separate these things out from one another such that RAG retrieval is again being efficient as possible?"

**Context-Based RAG Priorities:**

**Code Workspace (Phase 17):**
```python
rag_weights = {
    "connected_codebases": 0.5,   # Highest priority
    "github_repos": 0.3,
    "notes_code_domain": 0.15,
    "docs_context7": 0.05,
    "notes_other_domains": 0.0,   # Ignore calendar, personal notes
    "obsidian_personal": 0.0
}
```

**Calendar View:**
```python
rag_weights = {
    "calendar_events": 0.5,       # Highest priority
    "meeting_notes": 0.3,
    "notes_personal_domain": 0.15,
    "email_context": 0.05,
    "connected_codebases": 0.0,   # Ignore code
    "github_repos": 0.0
}
```

**General Chat (Dashboard):**
```python
rag_weights = {
    "all_sources": 0.2,           # Balanced across all
    # Let query determine best sources
}
```

**Implementation:**
```python
# In core/rag.py
def get_context_weights(page_context: str) -> dict:
    """
    Return RAG collection weights based on current page context.
    
    Args:
        page_context: "dashboard", "code", "calendar", "notes", etc.
    
    Returns:
        Dict mapping collection names to weight (0.0-1.0)
    """
    context_weights = {
        "code": {
            "codebase": 0.5,
            "github": 0.3,
            "code_notes": 0.15,
            "docs": 0.05,
            # Other collections: 0.0 (skipped)
        },
        "calendar": {
            "calendar": 0.5,
            "meetings": 0.3,
            "personal_notes": 0.15,
            "email": 0.05,
            # Code collections: 0.0
        },
        # ... other contexts
    }
    
    return context_weights.get(page_context, default_weights)
```

**Integration with Phase 0.5:**
- Page context already tracked in conversation DB (`page_context` column)
- RAG can access current page context
- Automatic filtering without user intervention

**Benefits:**
- Faster RAG retrieval (skip irrelevant collections)
- More relevant results (prioritize contextual sources)
- Reduced token usage (fewer irrelevant chunks)
- Better user experience (less noise)

---

### 8. Dashboard as Daily Briefing

**What It Does:**
Dashboard becomes an intelligent daily overview, summarizing important information across all domains.

**Daily Briefing Sections:**

**1. Today's Focus:**
- Active projects and next steps
- Tasks due today (from Phase 23 task system)
- Calendar events requiring prep

**2. Recent Activity:**
- Last 3 conversations across all domains
- Recent notes created/edited
- Recent code commits (if GitHub connected)

**3. Pattern Insights:**
- "You often work on Aleph on Monday mornings" (suggest loading project context)
- "RAG speed improved 30% this week" (pattern learning working)
- "You haven't reviewed weekly goals" (reminder)

**4. Knowledge Updates:**
- New documents added to RAG
- Connections discovered in knowledge graph
- Patterns learned this week

**5. Action Items:**
- Extracted from emails (Phase 20a)
- Extracted from meetings (Phase 20b)
- Extracted from conversations
- Follow-ups needed

**UI Mock:**
```
┌─────────────────────────────────────────────────────────┐
│ Good morning, Brett                                     │
│ Monday, January 28, 2026                                │
├─────────────────────────────────────────────────────────┤
│ TODAY'S FOCUS                                           │
│ ▶ Aleph: Complete UI refactor (60% done)              │
│ ▶ Meeting at 2pm: Project review with Sarah           │
│ ▶ 3 tasks due today                                   │
├─────────────────────────────────────────────────────────┤
│ RECENT ACTIVITY                                         │
│ 🔧 Code: Worked on RAG optimization (1 hour ago)      │
│ 📝 Notes: Created "Pattern Learning Guide" (2h ago)   │
│ 💬 Chat: Discussed compression strategy (4h ago)      │
├─────────────────────────────────────────────────────────┤
│ INSIGHTS                                                │
│ 📊 RAG efficiency up 25% this week                     │
│ 🎯 You're most productive on Aleph Mon-Wed mornings   │
│ 🔗 5 new connections discovered in knowledge graph     │
├─────────────────────────────────────────────────────────┤
│ ACTION ITEMS                                            │
│ ☐ Review Sarah's PR (from email)                      │
│ ☐ Update ARCHITECTURE.md (from yesterday's changes)   │
│ ☐ Respond to aleph-builder issue #42 (GitHub)         │
└─────────────────────────────────────────────────────────┘
```

**How It Works:**
- Aggregates data from all Polly systems
- Uses pattern learning to surface relevant information
- Personalized based on user's working habits
- Updates throughout the day (not static)

**Intelligence:**
- Learns what information user finds useful
- Surfaces proactive suggestions based on patterns
- Prioritizes items by importance (learned from user behavior)

---

### 9. Project Maturity Framework Integration

**What It Does:**
Tracks project maturity across multiple dimensions, guiding development priorities.

**Maturity Dimensions:**

**1. Planning Maturity (0-5):**
- 0: Rough idea only
- 1: Basic requirements documented
- 2: Architecture designed
- 3: Detailed specifications written
- 4: Edge cases documented, ADRs created
- 5: Comprehensive plan, ready to build

**2. Implementation Maturity (0-5):**
- 0: No code written
- 1: Proof of concept
- 2: Core functionality working
- 3: Feature complete (no polish)
- 4: Polished, tested
- 5: Production-ready

**3. Documentation Maturity (0-5):**
- 0: No documentation
- 1: Basic README
- 2: Architecture documented
- 3: API documentation, user guide
- 4: Examples, tutorials
- 5: Comprehensive docs, videos

**4. Testing Maturity (0-5):**
- 0: No tests
- 1: Smoke tests
- 2: Unit tests for core
- 3: Integration tests
- 4: E2E tests, >80% coverage
- 5: Comprehensive test suite, CI/CD

**5. Deployment Maturity (0-5):**
- 0: Runs locally only
- 1: Manual deployment process
- 2: Scripted deployment
- 3: CI/CD pipeline
- 4: Automated with rollback
- 5: Zero-downtime, monitored

**Project Maturity Score:**
Weighted average across dimensions (user-configurable weights)

**Example:**
```
Aleph Project Maturity: 3.2 / 5.0

Planning:        ████░ 4/5 (Strong)
Implementation:  ███░░ 3/5 (Good)
Documentation:   ██░░░ 2/5 (Needs Work) ← Priority
Testing:         ███░░ 3/5 (Good)
Deployment:      ███░░ 3/5 (Good)

Recommendation: Focus on documentation before adding new features.
```

**How Polly Uses This:**

**Guidance:**
- Suggests next steps based on weakest dimension
- Warns when implementation outpaces planning
- Prompts for documentation when code changes
- Recommends test coverage improvements

**Blocking:**
- Can block new features if planning maturity too low
- Requires documentation updates before architectural changes
- Enforces minimum testing before deployment

**Slack-Like Project Management Integration:**
- Maturity displayed in project card
- Filters: Show projects needing documentation
- Sort: By maturity score (find projects needing attention)

---

### 10. Slack-Like Project Interface

**What It Does:**
Project management UI inspired by Slack's channel-based organization, but for projects and their artifacts.

**UI Structure:**

**Left Sidebar: Project List**
```
┌─────────────────────────┐
│ PROJECTS                │
├─────────────────────────┤
│ # Aleph         [3.2] ● │ ← Active
│ # Polly         [4.1] ● │
│ # polly-docs    [2.8]   │
│ # norns-scripts [3.5]   │
│                         │
│ + New Project           │
├─────────────────────────┤
│ ARCHIVED                │
│ # old-project   [3.0]   │
└─────────────────────────┘
```

**Center: Project View**
```
┌───────────────────────────────────────────────────────┐
│ # Aleph                          [Pin] [Settings] [×] │
├───────────────────────────────────────────────────────┤
│ [Overview] [Files] [Sessions] [Tasks] [Build] [Chat] │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ALEPH AUDIO FRAMEWORK                               │
│  Status: Active Development (Phase 2)                │
│  Maturity: 3.2/5.0                                   │
│                                                       │
│  Recent Activity:                                    │
│  • 2h ago: UI refactor progress (60% complete)       │
│  • 5h ago: Fixed MIDI input bug                      │
│  • Yesterday: Completed Phase 1 milestones          │
│                                                       │
│  Quick Actions:                                      │
│  [Resume Last Session] [Build] [Run Tests]          │
│                                                       │
└───────────────────────────────────────────────────────┘
```

**Right Sidebar: Project Context**
```
┌─────────────────────────┐
│ PROJECT DETAILS         │
├─────────────────────────┤
│ Maturity: 3.2/5.0       │
│ ████████░░ Planning 4/5 │
│ ██████░░░░ Impl 3/5     │
│ ████░░░░░░ Docs 2/5 ⚠️  │
│                         │
│ FILES                   │
│ 📄 PROJECT.md           │
│ 📄 ARCHITECTURE.md      │
│ 📄 ROADMAP.md           │
│ 📄 BUILD.md             │
│                         │
│ QUICK LINKS             │
│ 🔗 GitHub Repo          │
│ 🔗 Documentation        │
│ 🔗 Production Deploy    │
└─────────────────────────┘
```

**Tabs:**

**1. Overview Tab:**
- Project status and maturity
- Recent activity
- Next steps
- Quick actions

**2. Files Tab:**
- Project documentation files
- Code directory (linked to Phase 17)
- Quick file access

**3. Sessions Tab:**
- List of all work sessions
- Session summaries
- Link to restore session context

**4. Tasks Tab:**
- Project-specific tasks (integration with Phase 23 task system)
- Milestones and phases
- Blockers and dependencies

**5. Build Tab:**
- Build commands (from BUILD.md)
- Test results
- Deployment status
- CI/CD integration

**6. Chat Tab:**
- Project-specific chat with full context
- All project files loaded in RAG
- Project-specific patterns active
- Can execute build commands from chat

---

## Implementation Plan

### Week 1-2: Core Project System (10-14 days)

**Day 1-3: Project Data Model**
- Project configuration schema
- SQLite table: `projects` (id, name, path, type, maturity, config)
- CRUD operations for projects
- Project file structure generator

**Day 4-6: Standardized Templates**
- Code project template
- Writing project template
- Creative project template
- Research project template
- Template customization system

**Day 7-10: Project-Specific Pattern Learning**
- Extend Phase 13 pattern system
- Per-project pattern storage
- Project context detection
- Pattern activation/deactivation based on active project

**Day 11-14: Always-Current Overview System**
- PROJECT.md auto-update logic
- Architectural change detection (file moves, refactors)
- ADR (Architecture Decision Record) generation
- Update prompts and automation

---

### Week 3: Plan/Build Modes (5-7 days)

**Day 1-2: Mode System**
- Plan Mode implementation
- Build Mode implementation
- Mode switching logic and thresholds
- Planning completeness scoring

**Day 3-4: Planning Assistant**
- Clarifying question generation
- Requirement documentation
- Architecture decision prompts
- Specification document creation

**Day 5-7: Build Mode Integration**
- Code generation with plan reference
- Deviation detection and approval
- Documentation updates during build
- Phase 17 (Code Workspace) integration

---

### Week 4: UI & Integration (5-7 days)

**Day 1-3: Slack-Like Project Interface**
- Project list sidebar
- Project view tabs (Overview, Files, Sessions, Tasks, Build, Chat)
- Project context sidebar
- Navigation and routing

**Day 4-5: Dashboard Briefing**
- Daily briefing aggregation
- Pattern insights display
- Action item extraction
- Real-time updates

**Day 6-7: Context-Aware RAG**
- RAG filtering by page context
- Collection weight configuration
- Performance optimization
- Testing and validation

---

## Storage

### Project Configuration
```yaml
# ~/.polly/projects/{project_id}/config.yaml
project:
  name: "Aleph"
  type: "code"
  path: "~/Code/aleph"
  created: "2025-08-15"
  maturity:
    planning: 4
    implementation: 3
    documentation: 2
    testing: 3
    deployment: 3
    weights:
      planning: 0.25
      implementation: 0.25
      documentation: 0.2
      testing: 0.15
      deployment: 0.15
  modes:
    current: "plan"  # or "build"
    plan_threshold: 0.7  # 70% planning completeness required
  patterns:
    path: ".polly/patterns.json"
    count: 47
  files:
    overview: "PROJECT.md"
    architecture: "ARCHITECTURE.md"
    roadmap: "ROADMAP.md"
    build: "BUILD.md"
    decisions: "DECISIONS.md"
  integrations:
    github: "https://github.com/monome/aleph"
    docs: "https://monome.org/docs/aleph"
```

### Project Patterns
```json
// ~/.polly/projects/aleph/.polly/patterns.json
{
  "version": "2.0",
  "project_id": "aleph",
  "patterns": [
    {
      "type": "build_command",
      "trigger": ["build", "compile", "make"],
      "command": "make",
      "cwd": "~/Code/aleph",
      "env": {"ARCH": "arm"},
      "confidence": 0.95,
      "last_used": "2026-01-28T10:30:00Z"
    },
    {
      "type": "test_command",
      "trigger": ["test", "run tests"],
      "command": "make test",
      "cwd": "~/Code/aleph",
      "confidence": 0.9
    },
    {
      "type": "architecture_location",
      "trigger": ["settings", "settings panel", "where are settings"],
      "location": "src/ui/header/SettingsModal.tsx",
      "note": "Moved from sidebar to header in Jan 2026 refactor",
      "confidence": 0.98
    }
  ]
}
```

### Compressed Context
```json
// ~/.polly/projects/aleph/.polly/compressed_context.json
[
  {
    "session_id": "sess_2026-01-28_10",
    "timestamp": "2026-01-28T10:30:00Z",
    "topic": "ui_refactor",
    "compressed": {
      "intent": "refactor_ui_layout",
      "from": "sidebar_based",
      "to": "flex_based",
      "reason": "better_responsiveness",
      "files_changed": ["ui/layout.tsx", "ui/sidebar.tsx", "ui/header.tsx"],
      "status": "in_progress_60pct"
    },
    "original_tokens": 2500,
    "compressed_tokens": 125,
    "compression_ratio": 20
  }
]
```

---

## Integration with Existing Phases

### Phase 1.5: Domain Configuration
- Projects can belong to one or more domains
- Project files auto-tagged with domain
- Domain-specific project templates

### Phase 13: Pattern Learning
- Project-specific patterns extend Phase 13 system
- Separate pattern storage per project
- Pattern activation based on project context

### Phase 16: Native Notes
- Project documentation stored as notes
- Automatic linking between project files and notes
- Project templates use note templates

### Phase 17: Code Workspace
- Plan/Build modes integrated into Code Workspace
- Project patterns available in code chat
- Build commands executed from workspace

### Phase 20: Email & Calendar
- Project-related emails auto-tagged
- Meeting notes linked to projects
- Action items extracted per project

---

## User Benefits

1. **Never Lose Context:** Project-specific patterns and compression ensure Polly always remembers
2. **Documentation is Natural:** Standardized workflows make documentation a byproduct, not a chore
3. **Intentional Development:** Plan/Build modes force thoughtful planning before coding
4. **Always Current:** PROJECT.md stays synchronized with reality automatically
5. **Efficient AI Usage:** Context-aware RAG reduces token waste and improves relevance
6. **Clear Project Status:** Maturity framework shows exactly where to focus effort
7. **Unified Interface:** Slack-like UI provides single place for all project activity

---

## Marketing Alignment

**"Build capability, don't rent it"**
- Project management integrated, not another SaaS subscription

**"Knowledge that compounds"**
- Project patterns improve over time, making development faster

**"Stop organizing. Start working."**
- Standardized workflows remove decision fatigue

**"Polly teaches you as you teach Polly"**
- Plan/Build modes encourage intentional development practices

**"Your work doesn't fit in boxes"**
- Projects can span multiple domains naturally

---

## Open Questions

From brain dump items not yet fully addressed:

1. **Cross-user family integration:** How would project management work across multiple users? Shared projects?

2. **Figma integration for code persona:** Should Phase 23 include design file integration? Would PROJECT.md link to Figma files?

3. **Research Motion.ai and Airflow:** What can we learn about integrated workflows from these tools?

4. **How granular should project tracking be?** File-level? Function-level? Just high-level?

---

## Success Criteria

Phase 23 is successful when:

- ✅ Projects have standardized, always-current documentation
- ✅ Polly remembers project-specific context across sessions
- ✅ Plan/Build modes encourage thoughtful development
- ✅ Architectural changes automatically update documentation
- ✅ RAG filtering is context-aware and efficient
- ✅ Dashboard provides useful daily briefing
- ✅ Project maturity framework guides development priorities
- ✅ Slack-like UI provides unified project interface
- ✅ Users never have to "remind" Polly about project specifics

---

**Document Created:** January 28, 2026  
**Status:** Planning Complete - Ready for Implementation After Tier 1
