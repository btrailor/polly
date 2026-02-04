# Phase 26: Project Management & Planning

**Status:** 📋 Planned  
**Priority:** MEDIUM  
**Estimated Effort:** 2-3 weeks  
**Target Date:** May 2026  
**Depends On:** Phase 24 (Orchestrator Mode), Phase 23 (Curriculum System) ✅

---

## Overview

Transform Polly into a comprehensive project management system with visual roadmaps, OmniFocus-style task management, and AI-powered planning. This phase brings the structure you use for Polly's own development (phases, tiers, roadmaps) directly into the UI for all users.

**Core Concept:** Project plans aren't static documents—they're living artifacts that evolve with your work. Polly makes them interactive, AI-assisted, and deeply integrated with your actual workflow.

---

## User Problem

**Current State:**
- Project planning happens in scattered documents
- Roadmaps become stale immediately
- No connection between plans and actual work
- Todo lists live separately from project context
- No visual progress tracking

**Pain Points:**
```
Scenario 1: Managing a software project
- Roadmap in ROADMAP.md (rarely updated)
- Tasks in todo app (disconnected from code)
- Progress tracking manual (estimates wrong)
- No way to see "what's blocking what"

Scenario 2: Learning a new skill
- Created curriculum in Phase 23 ✅
- But no project-level view of progress
- Can't see: "I'm 60% done with React learning"
- No milestones or checkpoints

Scenario 3: Complex multi-phase project
- Like building Polly itself!
- Managing 25+ phases manually
- Tracking dependencies between phases
- Updating CURRENT.md by hand
```

**Desired State:**
- Visual roadmap built from markdown documents
- Tasks auto-extracted from conversations
- Progress tracked automatically
- Dependencies visualized as graph
- AI helps keep plans realistic and updated

---

## Key Features

### 1. Project Plan Representation in UI

**Capability:** Render markdown project plans as interactive UI elements

**Input Format (Markdown):**
```markdown
# Project: Build Blog Platform

## Phase 1: Backend API
**Status:** In Progress  
**Estimated:** 2 weeks  
**Depends on:** None

Tasks:
- [ ] Design database schema
- [x] Set up Express server
- [ ] Create user authentication
- [ ] Build post CRUD API

## Phase 2: Frontend
**Status:** Not Started  
**Estimated:** 3 weeks  
**Depends on:** Phase 1

Tasks:
- [ ] React component structure
- [ ] Routing with React Router
- [ ] State management (Redux)
```

**Output UI:**
```
┌─────────────────────────────────────────────────┐
│ Project: Build Blog Platform                    │
│ Progress: ██████░░░░░░░░ 35% (2/5 phases)       │
├─────────────────────────────────────────────────┤
│                                                 │
│  [✓] Phase 0: Setup (2 days)                    │
│      100% complete                              │
│                                                 │
│  [⏳] Phase 1: Backend API (in progress)        │
│      ████████░░░░ 50% (2/4 tasks)               │
│      └─ Depends on: None                        │
│                                                 │
│  [  ] Phase 2: Frontend (not started)           │
│      Est: 3 weeks                               │
│      └─ Depends on: Phase 1 ⚠️                  │
│                                                 │
│  [  ] Phase 3: Deployment (not started)         │
│      └─ Depends on: Phase 1, Phase 2            │
│                                                 │
│ Next up: Complete Phase 1 to unblock Phase 2   │
└─────────────────────────────────────────────────┘
```

**Supported Plan Formats:**
- Polly's own phase system (CURRENT.md, MASTER_ROADMAP.md)
- Simple markdown task lists
- OmniFocus-style GTD projects
- Agile sprint plans
- Research project milestones

### 2. Visual Roadmap

**Capability:** Timeline view of project phases and milestones

**Timeline View:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Roadmap: Blog Platform                       [Monthly ▼]        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ February          March              April              May     │
│ ─────────────────────────────────────────────────────────────── │
│ ┌────────┐                                                      │
│ │ Setup  │                                                      │
│ └────────┘                                                      │
│     ┌──────────────────┐                                        │
│     │  Backend API     │◄─ You are here                        │
│     └──────────────────┘                                        │
│                   ┌────────────────────────┐                    │
│                   │     Frontend           │                    │
│                   └────────────────────────┘                    │
│                                       ┌──────────┐              │
│                                       │ Deploy   │              │
│                                       └──────────┘              │
│                                                                 │
│ Milestones:                                                     │
│ ▼ Feb 15: API Complete                                          │
│ ○ Mar 30: Frontend Beta                                         │
│ ○ Apr 20: Production Launch                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Drag phases to adjust timeline
- Click phase → see tasks
- Color-coded by status (not started, in progress, complete, blocked)
- Milestone markers
- Today indicator
- Zoom levels (day, week, month, quarter)

### 3. OmniFocus-Style Task Management

**Capability:** GTD-inspired task system with Polly AI integration

**Task Organization:**
```
Inbox (22)
├─ Process these into projects/contexts
└─ Quick capture from chat, notes, anywhere

Projects (8)
├─ Blog Platform (active)
├─ Learn React (active)
├─ Polly Phase 26 (on hold)
└─ Write Book Chapter 3 (active)

Contexts
├─ @computer (15 tasks)
├─ @email (3 tasks)
├─ @calls (2 tasks)
└─ @errands (5 tasks)

Perspectives
├─ Today (8 tasks)
├─ This Week (23 tasks)
├─ Waiting For (4 tasks)
└─ Someday/Maybe (12 projects)
```

**AI Chat Integration:**
```
User in chat: "I need to refactor the auth system, 
               update docs, and email the team about it"

Polly: "📝 I found 3 action items:

1. ☐ Refactor auth system
   Project: Backend API
   Context: @computer
   Est: 2 hours
   
2. ☐ Update authentication docs
   Project: Backend API
   Context: @computer
   Est: 30 minutes
   Depends on: Task 1
   
3. ☐ Email team about auth changes
   Project: Backend API
   Context: @email
   Est: 10 minutes
   Depends on: Task 1
   
[Add to Tasks] [Edit] [Dismiss]"
```

**Quick Capture:**
- Keyboard shortcut: `Cmd+T` from anywhere
- Natural language: "Call John tomorrow @calls"
- Polly parses: Due date, context, project (if mentioned)

### 4. Dynamic Todo Lists in Chat (OpenCode Style)

**Capability:** Real-time task tracking visible in conversation

**Your Brain Dump Referenced:**
> "Programmer and architect should be able to generate 'todos' list like OpenCode that dynamically update in the chat window"

**Implementation:**
```
User: "Help me implement Phase 26"

Architect:
"I'll break this down into tasks:

┌─ Implementation Tasks ─────────────────────────┐
│ [⏳] 1. Design project data model              │
│ [  ] 2. Create backend API endpoints           │
│ [  ] 3. Build roadmap visualization            │
│ [  ] 4. Implement task management UI           │
│ [  ] 5. Integrate with orchestrator            │
│ [  ] 6. Write documentation                    │
└────────────────────────────────────────────────┘

Let me start with the data model...

[Working on task 1...]

[After 5 minutes]

┌─ Implementation Tasks ─────────────────────────┐
│ [✓] 1. Design project data model (5m 23s)     │
│ [⏳] 2. Create backend API endpoints           │
│ [  ] 3. Build roadmap visualization            │
│ [  ] 4. Implement task management UI           │
│ [  ] 5. Integrate with orchestrator            │
│ [  ] 6. Write documentation                    │
└────────────────────────────────────────────────┘

Task 1 complete! Here's the data model...
```

**Features:**
- Updates in real-time as AI works
- Shows time elapsed per task
- Click task to see details/outputs
- Can pause/resume from UI
- Persists if you close chat (resume later)

### 5. Dependency Visualization

**Capability:** See what's blocking what

**Graph View:**
```
┌─────────────────────────────────────────────────┐
│ Project Dependencies: Blog Platform             │
├─────────────────────────────────────────────────┤
│                                                 │
│         ┌──────────┐                            │
│         │  Setup   │                            │
│         └─────┬────┘                            │
│               │                                 │
│               ▼                                 │
│         ┌──────────┐                            │
│         │ Backend  │◄─── You are here          │
│         └─────┬────┘                            │
│               │                                 │
│          ┌────┴────┐                            │
│          ▼         ▼                            │
│    ┌──────────┐  ┌──────────┐                  │
│    │ Frontend │  │ Testing  │                  │
│    └─────┬────┘  └─────┬────┘                  │
│          └────┬────────┘                        │
│               ▼                                 │
│         ┌──────────┐                            │
│         │ Deploy   │                            │
│         └──────────┘                            │
│                                                 │
│ Completing Backend unlocks: Frontend + Testing  │
└─────────────────────────────────────────────────┘
```

**Insights:**
- Critical path highlighted
- Bottlenecks identified
- "If you finish X, Y and Z become available"
- Parallel work opportunities

### 6. AI-Powered Planning Assistant

**Capabilities:**
1. **Realistic Estimates:** "That's ambitious for 1 week—more like 2-3 weeks"
2. **Dependency Detection:** "Phase 3 depends on Phase 2 completing first"
3. **Progress Tracking:** Auto-update CURRENT.md as you work
4. **Blockers:** "Phase 2 is blocked—you need to finish Phase 1"
5. **Suggestions:** "Consider splitting Phase 4 into 4a and 4b"

**Example Interaction:**
```
User: "Create a plan for building an e-commerce site"

Polly (Architect mode):
"Here's a realistic plan:

┌─ E-commerce Site Project ──────────────────────┐
│ Total estimate: 8-12 weeks                     │
│                                                │
│ Phase 1: Foundation (2 weeks)                  │
│ ├─ Database design                             │
│ ├─ API structure                               │
│ └─ Authentication                              │
│                                                │
│ Phase 2: Product Management (2 weeks)          │
│ ├─ Product CRUD                                │
│ ├─ Image uploads                               │
│ └─ Inventory tracking                          │
│                                                │
│ Phase 3: Shopping Cart (1.5 weeks)             │
│ ├─ Cart state management                       │
│ ├─ Checkout flow                               │
│ └─ Order processing                            │
│                                                │
│ Phase 4: Payment Integration (1 week)          │
│ ├─ Stripe setup                                │
│ ├─ Payment webhooks                            │
│ └─ Receipt generation                          │
│                                                │
│ Dependencies:                                  │
│ - Phase 2 depends on Phase 1                   │
│ - Phase 3 depends on Phase 2                   │
│ - Phase 4 can start after Phase 1              │
│                                                │
│ I can:                                         │
│ 1. Save this as project plan                   │
│ 2. Break into detailed tasks                   │
│ 3. Start with Phase 1                          │
│                                                │
│ What would you like to do?"                    │
└────────────────────────────────────────────────┘
```

---

## Technical Architecture

### Data Model

#### Project
```python
class Project:
    id: str
    name: str
    description: str
    status: ProjectStatus  # active, on_hold, completed
    phases: List[Phase]
    milestones: List[Milestone]
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime]
    metadata: Dict[str, Any]
    
    # Integration
    linked_notes: List[str]  # Note IDs
    linked_conversations: List[str]  # Conversation IDs
    source_file: Optional[str]  # If from markdown
```

#### Phase
```python
class Phase:
    id: str
    project_id: str
    name: str
    description: str
    status: PhaseStatus  # not_started, in_progress, completed, blocked
    tasks: List[Task]
    dependencies: List[str]  # Phase IDs
    estimated_duration: int  # hours
    actual_duration: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    # Progress tracking
    completion_percentage: float
    blocker_reason: Optional[str]
```

#### Task
```python
class Task:
    id: str
    phase_id: str
    title: str
    description: str
    status: TaskStatus  # inbox, todo, in_progress, waiting, completed
    
    # GTD properties
    project: Optional[str]
    context: Optional[str]  # @computer, @email, etc.
    due_date: Optional[datetime]
    defer_date: Optional[datetime]  # Don't show until this date
    
    # Metadata
    estimated_time: Optional[int]  # minutes
    actual_time: Optional[int]
    tags: List[str]
    dependencies: List[str]  # Task IDs
    
    # AI-generated
    created_by: str  # "user" or "ai"
    extracted_from: Optional[str]  # Conversation ID
```

#### Milestone
```python
class Milestone:
    id: str
    project_id: str
    name: str
    description: str
    target_date: datetime
    status: MilestoneStatus  # upcoming, achieved, missed
    linked_phases: List[str]  # Phases that must complete
```

### Storage

**Location:**
```
vault/.polly/projects/
├── projects.json               # All projects metadata
├── project_<id>/
│   ├── phases.json
│   ├── tasks.json
│   ├── milestones.json
│   └── timeline_cache.json
└── contexts.yaml               # GTD contexts

vault/Projects/                 # User-editable markdown
├── Blog Platform/
│   ├── PLAN.md
│   ├── ROADMAP.md
│   └── CURRENT.md
└── Learn React/
    └── CURRICULUM.md
```

**Bi-directional Sync:**
- UI edits → update markdown
- Markdown edits → update UI
- File watcher for markdown changes

### Backend (`core/projects/`)

```python
# project_manager.py
class ProjectManager:
    def create_project(self, name: str, description: str) -> Project
    def parse_markdown_plan(self, filepath: str) -> Project
    def export_to_markdown(self, project_id: str) -> str
    def get_project_progress(self, project_id: str) -> ProgressReport
    def get_next_tasks(self, project_id: str) -> List[Task]
    
# task_extractor.py
class TaskExtractor:
    """Extract tasks from conversations using NLU"""
    def extract_tasks_from_message(self, message: str) -> List[Task]
    def suggest_project_assignment(self, task: Task) -> Optional[str]
    def suggest_context(self, task: Task) -> Optional[str]
    
# dependency_analyzer.py
class DependencyAnalyzer:
    def detect_dependencies(self, phases: List[Phase]) -> Dict[str, List[str]]
    def find_critical_path(self, project: Project) -> List[Phase]
    def identify_bottlenecks(self, project: Project) -> List[Phase]
    def suggest_parallelization(self, project: Project) -> List[List[Phase]]
```

### Frontend

**New Page: Projects**
```javascript
// projects-manager.js

class ProjectsManager {
    // Project CRUD
    async createProject(name, description) { }
    async loadProjects() { }
    
    // Visualization
    renderRoadmap(project) { }
    renderDependencyGraph(project) { }
    renderTaskList(phase) { }
    
    // Interaction
    onPhaseClick(phaseId) { }  // Open phase details
    onTaskComplete(taskId) { }
    onDragPhase(phaseId, newDate) { }  // Reschedule
    
    // AI integration
    async generateProjectPlan(description) { }
    async suggestNextTasks(projectId) { }
}
```

**Chat Integration:**
```javascript
// In app.js

// Task extraction from chat
function extractTasksFromMessage(message) {
    const tasksDetected = await api.post('/projects/extract-tasks', {
        message: message
    });
    
    if (tasksDetected.length > 0) {
        showTaskConfirmation(tasksDetected);
    }
}

// Dynamic todo list rendering
function renderDynamicTodoList(todos) {
    const todoElement = `
        <div class="dynamic-todos">
            ${todos.map(todo => renderTodoItem(todo)).join('')}
        </div>
    `;
    appendToChatMessage(todoElement);
    
    // Update in real-time
    subscribeTo TodoUpdates((update) => {
        updateTodoItem(update.todoId, update.status);
    });
}
```

---

## Integration with Existing Phases

### With Phase 23: Curriculum System ✅

**Use Case:** Learning projects as project plans

```javascript
// Convert curriculum to project
async function curriculumToProject(curriculumId) {
    const curriculum = await getCurriculum(curriculumId);
    
    return {
        name: curriculum.topic,
        phases: curriculum.sections.map(section => ({
            name: section.title,
            tasks: section.exercises.map(ex => ({
                title: ex.title,
                status: section.completed ? 'completed' : 'todo'
            }))
        }))
    };
}
```

**UI:** "View as Project" button in Learning page

### With Phase 24: Orchestrator Mode

**Use Case:** Orchestrated workflows tracked as projects

```javascript
// When orchestration starts
async function onOrchestrationStart(session) {
    // Create temporary project
    const project = await createProject({
        name: session.name,
        type: 'orchestration',
        phases: session.plan.tasks.map(task => ({
            name: task.description,
            status: 'not_started'
        }))
    });
    
    // Track progress
    session.on('task_completed', (taskId) => {
        updatePhaseStatus(project, taskId, 'completed');
    });
}
```

### With Phase 16: Native Notes

**Use Case:** Project plans live as notes

```markdown
<!-- In vault/Projects/Blog Platform/PLAN.md -->

# Blog Platform Project

## Phase 1: Backend
**Status:** in_progress
**Est:** 2 weeks

- [x] Database schema
- [ ] API endpoints

<!-- Polly renders this in Projects UI -->
```

**Sync:** Bi-directional (edit note → updates UI, edit UI → updates note)

---

## User Workflows

### Workflow 1: Create New Project from Chat

```
User: "I want to build a task management app"

Polly (Architect): 
"Let me create a project plan for you:

┌─ Task Management App Project ─────────────────┐
│ Estimated: 6-8 weeks                          │
│                                               │
│ Phase 1: Core Backend (2 weeks)               │
│ Phase 2: Web Frontend (2 weeks)               │
│ Phase 3: Mobile App (3 weeks)                 │
│ Phase 4: Polish & Launch (1 week)             │
│                                               │
│ [Save as Project] [Refine Plan] [Start Now]  │
└───────────────────────────────────────────────┘"

User clicks "Save as Project"

Polly: 
"✓ Project saved!
 
 View in:
 - Projects page for roadmap
 - vault/Projects/Task App/PLAN.md
 
 Next: Should I start with Phase 1?"
```

### Workflow 2: Import Existing Markdown Plan

```
User: Opens Projects page → "Import from File"

Selects: vault/Development/My App/ROADMAP.md

Polly:
"Found project plan in ROADMAP.md:
 
 - 5 phases identified
 - 23 tasks extracted
 - 3 milestones detected
 
 [Import as New Project] [Merge with Existing]"

After import:
- Timeline view shows phases
- Tasks appear in task list
- Dependencies auto-detected
- Edits sync back to markdown
```

### Workflow 3: AI-Assisted Task Capture

```
User in chat: 
"I need to fix the login bug, write tests, 
 update documentation, and deploy to staging"

Polly:
"📝 4 tasks extracted:

1. ☐ Fix login bug
   @computer | Est: 1h | Project: Backend

2. ☐ Write tests for login
   @computer | Est: 30m | Depends on: Task 1

3. ☐ Update login documentation
   @computer | Est: 20m | Depends on: Task 1

4. ☐ Deploy to staging
   @computer | Est: 15m | Depends on: All above

[Add to Tasks] [Edit] [Dismiss]"

User clicks "Add to Tasks"

Tasks appear in:
- Projects > Backend project
- Context: @computer
- Today's tasks (if due today)
```

---

## API Endpoints

```python
# Projects
GET /projects                    # List all projects
POST /projects                   # Create project
GET /projects/<id>               # Get project details
PUT /projects/<id>               # Update project
DELETE /projects/<id>            # Delete project

# Parse markdown
POST /projects/import/markdown   # Convert .md to project
POST /projects/<id>/export       # Export project to .md

# Phases
GET /projects/<id>/phases
POST /projects/<id>/phases
PUT /projects/<id>/phases/<phase_id>
GET /projects/<id>/roadmap       # Timeline data

# Tasks
GET /tasks                       # All tasks (filterable)
POST /tasks                      # Create task
PUT /tasks/<id>                  # Update task
POST /tasks/extract              # Extract from text

# AI features
POST /projects/generate          # AI-generated plan
POST /projects/<id>/suggest-next # What to work on next
POST /projects/<id>/analyze-dependencies
```

---

## Success Criteria

### Phase 26 Complete When:

**Backend:**
- [x] Project/Phase/Task/Milestone data models
- [x] Markdown import/export working
- [x] Task extraction from chat
- [x] Dependency analysis functional
- [x] API endpoints complete
- [x] File watcher for markdown sync

**Frontend:**
- [x] Projects page with list view
- [x] Roadmap visualization (timeline)
- [x] Dependency graph view
- [x] Task list with filters
- [x] Quick capture (Cmd+T)
- [x] Dynamic todos in chat (OpenCode-style)

**Integration:**
- [x] Chat extracts tasks automatically
- [x] Curriculum converts to project
- [x] Orchestration creates project
- [x] Markdown files stay in sync

**AI Capabilities:**
- [x] Generate realistic project plans
- [x] Suggest next tasks
- [x] Detect dependencies
- [x] Estimate durations
- [x] Identify bottlenecks

**Testing:**
- [x] Import complex markdown plan (like MASTER_ROADMAP.md)
- [x] Bi-directional sync working
- [x] Task extraction 90%+ accurate
- [x] Dependency detection working
- [x] Dynamic todos update in real-time

---

## Future Enhancements

### Phase 26b: Advanced Project Management
- Gantt charts
- Resource allocation
- Time tracking integration
- Budget tracking
- Risk management

### Phase 26c: Collaborative Projects
- Shared projects across team
- Task assignment
- Comments and discussions
- Activity feed
- Notifications

### Phase 26d: Project Templates
- Reusable project templates
- Template marketplace
- Custom template builder
- Import from JIRA/Asana/Trello

---

## Dependencies

**Required:**
- ✅ Phase 23: Curriculum System (reference for learning projects)
- ✅ Phase 16: Native Notes (markdown sync)
- Phase 24: Orchestrator Mode (creates projects)

**Enhances:**
- Phase 11c: Architect persona (generates plans)
- Phase 22: Teaching Mode (learning projects)
- Phase 25: Code Architecture (dev projects)

---

## Risk Assessment

**High Risk:**
- Complexity: Balancing power and simplicity
- Scope creep: Could become full project management suite
- Markdown sync: Hard to keep UI and files in sync

**Mitigations:**
- Start simple: Focus on visualization first
- Don't compete with Jira: Different audience
- One-way sync initially: MD → UI (easier)

**Medium Risk:**
- Task extraction accuracy
- Dependency detection false positives
- Performance with 100+ task projects

---

## Questions to Resolve

1. **HyperTask.ai Research:** What can we learn from them? (Your brain dump)
2. **Markdown Format:** Standardize on format or support multiple?
3. **Real-time Collaboration:** Support multi-user editing?
4. **Mobile:** Does this need mobile app support?

---

**Document Created:** February 3, 2026  
**Status:** Ready for implementation planning  
**Next Step:** Research HyperTask.ai, then create detailed implementation plan
