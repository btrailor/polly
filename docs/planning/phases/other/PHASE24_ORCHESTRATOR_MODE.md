# Phase 24: Orchestrator Mode & Multi-Persona Workflows

**Status:** 📋 Planned  
**Priority:** HIGH (Foundation for power features)  
**Estimated Effort:** 2-3 weeks  
**Target Date:** March 2026  
**Depends On:** Phase 11c (Agent Personas) ✅

---

## Overview

Orchestrator Mode enables users to input multiple unrelated instructions that span across multiple persona capabilities in a single session. It represents the evolution from single-task AI assistance to true multi-capability coordination.

**Core Concept:** Instead of switching between personas manually, users can express complex, multi-faceted goals, and Polly intelligently routes work to the appropriate personas, coordinates their outputs, and synthesizes results.

---

## User Problem

**Current State:**
- User must manually switch between personas (Architect, Scribe, Professor, etc.)
- Each conversation is single-threaded and persona-specific
- Complex projects require juggling multiple chat sessions
- No way to express "do these 5 unrelated things" efficiently

**Example of Current Friction:**
```
User wants to:
1. Architect a new feature
2. Write documentation for it
3. Create a learning curriculum about the technology
4. Refactor some existing code

Today: Requires 4 separate conversations with manual context switching
```

**Desired State:**
- Single input: "I need to architect the new authentication system, write docs for it, create a learning path for OAuth 2.0, and refactor the current session handling"
- Polly orchestrates: Architect → Scribe → Professor → Programmer
- User sees: Coordinated progress across all tasks
- Result: Everything completed in one coordinated session

---

## Key Features

### 1. Multi-Instruction Input Parsing

**Capability:** Natural language understanding of compound requests

**Examples:**
```
User: "Help me build a React component for user profiles, 
       write a guide about React hooks, 
       and create a curriculum for learning TypeScript"

Polly detects:
- Task 1: Build component → Programmer persona
- Task 2: Write guide → Scribe persona  
- Task 3: Create curriculum → Professor persona
```

**Technical Approach:**
- Use Router v2 with intent classification
- Extract discrete tasks from compound input
- Identify appropriate persona for each task
- Determine task dependencies and ordering

### 2. Customizable Persona Routing

**Capability:** Define workflows and persona interaction patterns

**User-Defined Routings:**
```yaml
# Example: Web app development workflow
web_app_development:
  name: "Web App Development"
  trigger: "building a web app"
  workflow:
    - persona: Architect
      mode: Plan
      output_to: Designer
    - persona: Designer
      mode: Vision
      input_from: Architect
      output_to: Programmer
    - persona: Programmer
      mode: Implement
      input_from: Designer
      output_to: Scribe
    - persona: Scribe
      mode: Write
      task: "Create documentation"
      input_from: Programmer
```

**Built-In Routings:**
- Feature Development: Architect → Designer → Programmer → Scribe
- Learning Path: Librarian → Professor → Scribe
- Content Creation: Researcher → Scribe → Publisher
- Code Refactoring: Architect → Programmer → Tester

**User Benefits:**
- Save and reuse common workflows
- Share routings with team/community
- Build personal productivity patterns
- Reduce repetitive persona switching

### 3. Parallel and Sequential Task Execution

**Capability:** Intelligently schedule independent vs. dependent tasks

**Parallel Execution:**
```
User: "Write a blog post about AI, 
       create a Python curriculum, 
       and research Rust web frameworks"

Polly executes simultaneously:
├─ Scribe: Blog post (10 min)
├─ Professor: Curriculum (15 min)
└─ Librarian: Research (5 min)

Result: All complete in ~15 minutes (not 30)
```

**Sequential Execution:**
```
User: "Design a login page, 
       implement it in React, 
       then write tests for it"

Polly executes in order:
1. Designer: UI mockup → outputs to Programmer
2. Programmer: React implementation → outputs to Tester
3. Tester: Test suite creation

Result: Each step builds on previous
```

### 4. Cross-Persona Context Sharing

**Capability:** Personas can access each other's outputs within orchestration session

**Example Workflow:**
```
1. Architect (Plan mode): 
   Designs database schema for blog system
   Output: Schema document saved to context

2. Programmer (Implement mode):
   Receives schema from Architect's context
   Implements migration scripts
   Output: Code saved to context

3. Scribe (Write mode):
   Receives schema + code from context
   Writes comprehensive documentation
   Output: Documentation note
```

**Technical Implementation:**
- Shared context pool for orchestration session
- Each persona can read from pool
- Outputs automatically added to pool
- Context cleanup after session complete

### 5. Progress Tracking & Visualization

**Capability:** Real-time visibility into orchestration progress

**UI Concept:**
```
┌─────────────────────────────────────────────────┐
│ Orchestrator Session: Web App Feature          │
├─────────────────────────────────────────────────┤
│ ✅ Architect: Feature design (2 min)            │
│ ⏳ Designer: UI mockup (in progress...)         │
│ ⏸️  Programmer: Implementation (waiting)        │
│ ⏸️  Scribe: Documentation (waiting)             │
└─────────────────────────────────────────────────┘
```

**Features:**
- Dynamic todo list (OpenCode-style) in chat
- Progress indicators for each task
- Estimated time remaining
- Ability to pause/resume/cancel individual tasks
- Click to view task details/outputs

---

## Orchestrator Modes

### Mode 1: Smart Detection (Default)

**Behavior:** Polly automatically detects when input requires orchestration

**Triggers:**
- Multiple verbs in single input ("design AND implement AND document")
- Comma-separated task list
- Explicit keywords: "I need to..., ..., and ..."
- Multiple distinct domains in single request

**User Experience:**
```
User: "I want to build a blog, write about it, and teach others how to do it"

Polly: "🎭 I detected 3 tasks across multiple areas:
        1. Build blog → Programmer
        2. Write about it → Scribe
        3. Teach others → Professor
        
        Should I orchestrate these together? 
        [Yes, coordinate these] [Handle separately]"
```

### Mode 2: Explicit Toggle (Power Users)

**Behavior:** User enables Orchestrator mode explicitly

**UI:**
```
Chat Input Bar:
┌────────────────────────────────────────────────┐
│ [Persona: All ▼] [Model: ▼] [🎭 Orchestrate] │
│ Type your message...                           │
└────────────────────────────────────────────────┘
```

When enabled:
- All inputs treated as orchestration opportunities
- Polly always looks for multi-task patterns
- More aggressive task decomposition

### Mode 3: Workflow Templates (Advanced)

**Behavior:** Select pre-defined workflow, fill in blanks

**UI:**
```
Workflows Menu:
├─ Web App Development
├─ Content Creation Pipeline
├─ Learning Path Creation
├─ Code Refactoring Suite
└─ Research & Documentation

User selects "Web App Development":
┌────────────────────────────────────────────────┐
│ Web App Development Workflow                   │
├────────────────────────────────────────────────┤
│ Feature: [_______________________________]     │
│ Tech Stack: [React] [TypeScript] [Node.js]    │
│ Include tests? [✓] Include docs? [✓]          │
│                                                │
│              [Start Workflow]                  │
└────────────────────────────────────────────────┘
```

---

## Technical Architecture

### Components

#### 1. Orchestrator Engine (`core/orchestrator.py`)

**Responsibilities:**
- Parse compound instructions
- Decompose into discrete tasks
- Assign tasks to personas
- Manage execution order (parallel vs sequential)
- Coordinate context sharing
- Track progress and state

**Key Classes:**
```python
class OrchestratorEngine:
    def parse_instruction(self, user_input: str) -> List[Task]
    def create_execution_plan(self, tasks: List[Task]) -> ExecutionPlan
    def execute_plan(self, plan: ExecutionPlan) -> OrchestratorSession
    def coordinate_personas(self, session: OrchestratorSession)
    
class Task:
    id: str
    description: str
    persona: PersonaType
    mode: str
    dependencies: List[str]  # Task IDs this depends on
    context_inputs: List[str]  # Context keys needed
    context_outputs: List[str]  # Context keys produced
    status: TaskStatus
    
class ExecutionPlan:
    tasks: List[Task]
    execution_order: List[List[str]]  # Parallel groups
    estimated_time: int
    
class OrchestratorSession:
    id: str
    plan: ExecutionPlan
    context_pool: Dict[str, Any]
    active_tasks: List[Task]
    completed_tasks: List[Task]
    outputs: Dict[str, Any]
```

#### 2. Task Decomposer (`core/orchestrator/decomposer.py`)

**Responsibilities:**
- NLU for compound instructions
- Intent classification per sub-task
- Persona assignment logic
- Dependency detection

**LLM Prompt Pattern:**
```python
DECOMPOSITION_PROMPT = """
Analyze this user request and break it into discrete tasks:

"{user_input}"

For each task, identify:
1. Task description (what needs to be done)
2. Appropriate persona (Architect, Designer, Programmer, Scribe, Professor, Librarian)
3. Persona mode (if applicable)
4. Dependencies (which tasks must complete first)
5. Context requirements (what information is needed)

Return structured task list in JSON format.
"""
```

#### 3. Workflow Manager (`core/orchestrator/workflows.py`)

**Responsibilities:**
- Store and retrieve workflow templates
- Workflow CRUD operations
- Template variable substitution
- Workflow sharing/export

**Storage:**
```
~/.polly/orchestrator/
├── workflows/
│   ├── web_app_development.yaml
│   ├── content_creation.yaml
│   ├── learning_path.yaml
│   └── custom_user_workflow.yaml
└── sessions/
    └── <session_id>.json
```

#### 4. Progress Tracker (`core/orchestrator/progress.py`)

**Responsibilities:**
- Real-time status updates
- Time estimation
- UI state management
- Event broadcasting to frontend

**WebSocket Events:**
```javascript
// Frontend listens to:
orchestrator.task_started
orchestrator.task_progress
orchestrator.task_completed
orchestrator.task_failed
orchestrator.session_completed
```

---

## API Design

### Backend Endpoints

```python
# Start orchestration session
POST /orchestrator/sessions
Request: {
    "instruction": "Build feature X, document it, create learning path",
    "mode": "auto" | "explicit" | "workflow",
    "workflow_id": "web_app_development" (if mode=workflow)
}
Response: {
    "session_id": "orch_abc123",
    "execution_plan": ExecutionPlan,
    "estimated_time": 900  # seconds
}

# Get session status
GET /orchestrator/sessions/<session_id>
Response: {
    "session": OrchestratorSession,
    "progress": {
        "completed": 2,
        "in_progress": 1,
        "pending": 3,
        "total": 6
    }
}

# Cancel/pause/resume session
POST /orchestrator/sessions/<session_id>/control
Request: {
    "action": "pause" | "resume" | "cancel",
    "task_ids": ["task1", "task2"]  # optional
}

# Workflow CRUD
GET /orchestrator/workflows
POST /orchestrator/workflows
PUT /orchestrator/workflows/<workflow_id>
DELETE /orchestrator/workflows/<workflow_id>
```

### Frontend Integration

**Chat UI Updates:**
```javascript
// In app.js
async function handleOrchestratorInput(message) {
    const session = await startOrchestrationSession(message);
    
    // Show orchestration UI
    showOrchestratorPanel(session);
    
    // Listen for updates
    subscribeToSessionUpdates(session.id, (event) => {
        updateOrchestratorUI(event);
    });
}

// Display orchestration progress
function showOrchestratorPanel(session) {
    const panel = `
        <div class="orchestrator-session">
            <h3>🎭 Orchestrating: ${session.name}</h3>
            <div class="task-list">
                ${session.plan.tasks.map(renderTask).join('')}
            </div>
            <div class="progress-bar">
                <div class="progress" style="width: ${session.progress}%"></div>
            </div>
        </div>
    `;
    // Render in chat or sidebar
}
```

---

## User Workflows

### Workflow 1: Feature Development

**User Input:**
```
"I need to build a user authentication system with OAuth, 
 create UI designs for login/signup pages, 
 implement it in React, 
 write comprehensive documentation, 
 and create a learning curriculum about OAuth 2.0"
```

**Polly Orchestration:**
```
1. Architect (Plan mode) - 5 min
   → Design auth system architecture
   → Output: Architecture document

2. Designer (Vision mode) - 10 min
   → Create UI mockups for login/signup
   → Input: Architecture from step 1
   → Output: UI designs (Figma/mockups)

3. Programmer (Implement mode) - 30 min
   → Implement React components
   → Input: Architecture + UI designs
   → Output: Code files

4. Scribe (Write mode) - 15 min
   → Write documentation
   → Input: Architecture + Code
   → Output: Documentation note

5. Professor (Curriculum mode) - 20 min
   → Create OAuth 2.0 learning path
   → Output: Curriculum with exercises
```

**Total Time:** ~80 minutes (coordinated)  
**Manual Time:** ~120+ minutes (context switching overhead)

### Workflow 2: Content Creation Pipeline

**User Input:**
```
"Research the latest developments in AI agents, 
 write a blog post about it, 
 create social media snippets, 
 and publish to Ghost CMS"
```

**Polly Orchestration:**
```
1. Librarian (Research mode) - Parallel
   → Research AI agent developments
   → Output: Research summary with sources

2. Scribe (Write mode) - Sequential (depends on 1)
   → Write blog post
   → Input: Research summary
   → Output: Blog post draft

3. Scribe (Refine mode) - Parallel with 4
   → Create social snippets
   → Input: Blog post
   → Output: Twitter, LinkedIn posts

4. Publisher (Publish mode) - Parallel with 3
   → Format for Ghost CMS
   → Input: Blog post
   → Output: Published article
```

### Workflow 3: Learning Project

**User Input:**
```
"I want to learn Rust by building a CLI tool. 
 Create a curriculum, guide me through architecture, 
 and help me implement it step by step"
```

**Polly Orchestration:**
```
1. Professor (Curriculum mode) - 10 min
   → Create Rust CLI curriculum
   → Output: Learning path with 8 sections

2. Architect (Plan mode) - 5 min
   → Design CLI tool architecture
   → Output: Project structure, modules

3. Professor (Teaching mode) - Interactive session
   → Guided learning through each section
   → Input: Curriculum + Architecture
   → Teaches concepts, provides exercises

4. Programmer (Pair mode) - Interactive
   → Code alongside user
   → Input: Architecture + current lesson
   → Assists with implementation
```

---

## Pattern Learning Integration

**Orchestrator learns user patterns over time:**

**Pattern Type: Workflow Preferences**
```json
{
  "pattern_type": "workflow",
  "learned": {
    "user_prefers": "documentation_after_code",
    "typical_sequence": [
      "architect_plan",
      "programmer_implement", 
      "scribe_document"
    ],
    "frequency": 23,
    "confidence": 0.89
  }
}
```

**Usage:**
- Polly suggests workflows based on past behavior
- Auto-routes tasks according to learned preferences
- Adapts execution order to user's style

**Example:**
```
User: "Build a new API endpoint"

Polly: "Based on your past projects, I'll:
        1. Architect the endpoint design
        2. Implement the code
        3. Write documentation
        
        This matches your usual workflow. Sound good?"
```

---

## UI/UX Design

### Orchestrator Toggle

**Location:** Chat input bar (bottom of screen)

```
┌────────────────────────────────────────────────┐
│ [Persona ▼] [Model ▼] [🎭 Orchestrate: OFF]  │
│ ┌────────────────────────────────────────────┐ │
│ │ Type your message...                       │ │
│ └────────────────────────────────────────────┘ │
│                                   [Send]       │
└────────────────────────────────────────────────┘
```

**States:**
- OFF (gray): Single-persona mode
- AUTO (blue): Smart detection enabled
- ON (orange): Explicit orchestration mode

### Orchestration Panel

**Location:** Right sidebar or inline in chat

**Active Session View:**
```
┌─────────────────────────────────────────────────┐
│ 🎭 Orchestration Session                        │
│ "Build authentication system..."                │
├─────────────────────────────────────────────────┤
│ ✅ Architect: System design (2m 34s)            │
│    └─ View output →                             │
│                                                 │
│ ⏳ Designer: UI mockups (1m 12s / ~3m)          │
│    └─ [Progress: ████████░░░░ 60%]             │
│                                                 │
│ ⏸️  Programmer: Implementation                  │
│    └─ Waiting for Designer...                  │
│                                                 │
│ ⏸️  Scribe: Documentation                       │
│    └─ Waiting for Programmer...                │
│                                                 │
│ Progress: 2/4 tasks complete                    │
│ Est. remaining: ~25 minutes                     │
│                                                 │
│ [Pause] [View All Outputs] [Settings]          │
└─────────────────────────────────────────────────┘
```

### Workflow Builder (Advanced)

**Location:** Settings > Orchestrator > Workflows

**UI for creating custom workflows:**
```
┌─────────────────────────────────────────────────┐
│ Create Custom Workflow                          │
├─────────────────────────────────────────────────┤
│ Name: [_______________________________]         │
│ Description: [__________________________]       │
│                                                 │
│ Trigger phrase: [_______________________]       │
│                                                 │
│ Steps:                                          │
│ ┌───────────────────────────────────────────┐  │
│ │ 1. [Architect ▼] [Plan ▼]                │  │
│ │    Output to: [Designer ▼]               │  │
│ │                               [Delete] [↕]│  │
│ ├───────────────────────────────────────────┤  │
│ │ 2. [Designer ▼] [Vision ▼]               │  │
│ │    Input from: [Architect]                │  │
│ │    Output to: [Programmer ▼]             │  │
│ │                               [Delete] [↕]│  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ [+ Add Step]                                    │
│                                                 │
│ [Save Workflow] [Test] [Cancel]                │
└─────────────────────────────────────────────────┘
```

---

## Success Criteria

### Phase 24 Complete When:

**Backend:**
- [x] Orchestrator engine implemented
- [x] Task decomposition working
- [x] Context sharing between personas functional
- [x] Progress tracking operational
- [x] API endpoints complete

**Frontend:**
- [x] Orchestrator toggle in chat UI
- [x] Real-time progress panel
- [x] Task status visualization
- [x] Output viewing interface
- [x] Workflow builder (basic)

**Testing:**
- [x] Successfully orchestrate 3+ persona workflow
- [x] Parallel task execution verified
- [x] Sequential dependencies working
- [x] Context properly shared between personas
- [x] Progress updates in real-time
- [x] User can pause/resume/cancel tasks

**Documentation:**
- [x] User guide for orchestrator mode
- [x] Workflow template examples
- [x] API documentation
- [x] Pattern learning integration documented

---

## Future Enhancements (Post-Phase 24)

### Phase 24b: Advanced Orchestration
- Conditional branching (if/else in workflows)
- Looping (iterate until condition met)
- Error handling and retry logic
- Workflow versioning and rollback

### Phase 24c: Collaborative Orchestration
- Multi-user workflows
- Workflow sharing marketplace
- Team workflow templates
- Orchestration analytics dashboard

### Phase 24d: Autonomous Orchestration
- Polly suggests orchestration opportunities
- Proactive task decomposition
- Learning from failed orchestrations
- Self-optimizing workflows

---

## Dependencies

**Required Phases:**
- ✅ Phase 11c: Agent Personas Framework
- ✅ Phase 11a: Router v2 (for intent classification)
- ✅ Phase 13a: Pattern Learning (for workflow learning)

**Unlocks:**
- Phase 26: Project Management (uses orchestration)
- Phase 27: Designer Persona (integrates with workflows)
- Phase 17: Code Workspace (programmer orchestration)

---

## Risk Assessment

**High Risk:**
- Complexity: Coordinating multiple personas is architecturally complex
- UX: Could feel overwhelming if not designed carefully
- Performance: Multiple concurrent LLM calls could be expensive

**Mitigations:**
- Start with simple 2-3 persona workflows
- Make orchestration opt-in, not default
- Implement cost caps and warnings
- Progressive disclosure: hide complexity initially

**Medium Risk:**
- Context bleeding: Personas might receive irrelevant context
- Dependency detection: Automatically determining task order is hard
- User expectations: Users might expect magic that's not possible

**Mitigations:**
- Clear context isolation boundaries
- Allow manual dependency specification
- Transparent about what orchestration can/cannot do

---

## Questions to Resolve

1. **Pricing Model:** How do we handle increased LLM costs from orchestration?
2. **Context Limits:** What's the maximum context pool size before performance degrades?
3. **Workflow Discovery:** How do users find/learn about workflow templates?
4. **Failure Handling:** What happens if one task in orchestration fails?
5. **Real-time vs Batch:** Should all tasks execute immediately or queue for later?

---

**Document Created:** February 3, 2026  
**Status:** Ready for implementation planning  
**Next Step:** Create detailed implementation plan with file-by-file breakdown
