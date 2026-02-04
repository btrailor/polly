# Phase 25: Code Architecture System

**Status:** 📋 Planned  
**Priority:** MEDIUM  
**Estimated Effort:** 3-4 weeks  
**Target Date:** April-May 2026  
**Depends On:** Phase 17 (Code Workspace)

---

## Overview

A visual code architecture system that maps dependencies, relationships, and structure across a codebase. Think of it as a "living architecture diagram" that keeps Polly aware of how code components connect, enabling better code assistance and architectural reasoning.

**Core Concept:** Most AI coding assistants are myopic—they see individual files but not the forest. The Code Architecture System gives Polly a bird's-eye view of the entire codebase, enabling architectural thinking rather than just code generation.

---

## User Problem

**Current State:**
- AI assistants (including Polly) work on isolated files
- No understanding of how changes ripple through system
- User must manually explain architecture every session
- Refactoring is risky—what breaks if I change this?
- Documentation becomes stale immediately

**Pain Points:**
```
Scenario 1: "Should I refactor this function?"
- User doesn't know what depends on it
- AI can't see call graph
- Risk: Break 5 things unknowingly

Scenario 2: "How does authentication work?"
- Code spans 8 files across 4 modules
- No visual map of flow
- User reads code linearly (slow, error-prone)

Scenario 3: "Onboarding new developer"
- Codebase is 50k lines
- No architecture documentation
- Takes weeks to understand structure
```

**Desired State:**
- Polly knows codebase architecture at all times
- Visual dependency graph shows relationships
- Click any component → see connections
- AI says: "Changing this affects these 3 modules"
- Architecture stays in sync with code automatically

---

## Key Features

### 1. Dependency Tree Generation

**Automatic Detection:**
- Parse import/include statements
- Track function calls across files
- Map class inheritance and composition
- Detect API endpoints and routes
- Identify database schema relationships

**Supported Languages (Phase 25a):**
- JavaScript/TypeScript (import/export)
- Python (import statements)
- React (component hierarchy)

**Example Output:**
```
auth_system/
├── auth_controller.py
│   ├─> [calls] auth_service.py::authenticate()
│   ├─> [calls] user_model.py::User.find_by_email()
│   └─> [called by] routes.py::/api/login
├── auth_service.py
│   ├─> [calls] jwt_util.py::generate_token()
│   ├─> [calls] database.py::query()
│   └─> [called by] auth_controller.py
└── jwt_util.py
    └─> [imported by] 3 modules
```

### 2. Visual Architecture Graph

**Interactive Graph View:**
- Nodes: Files, classes, functions, API endpoints
- Edges: Dependencies, calls, data flow
- Colors: By module/domain
- Size: By complexity (LOC, cyclomatic complexity)

**UI Concept:**
```
┌─────────────────────────────────────────────────┐
│ Code Architecture: polly-backend               │
├─────────────────────────────────────────────────┤
│  [Filters: ▼All] [Layout: Force ▼] [🔍]        │
│                                                 │
│     ┌─────────────┐                             │
│     │   core/     │◄────────┐                   │
│     │   polly.py  │         │                   │
│     └─────┬───────┘         │                   │
│           │                 │                   │
│           ▼                 │                   │
│     ┌─────────────┐   ┌─────────────┐          │
│     │ personas/   │   │   router/   │          │
│     │ architect.py│──►│ router_v2.py│          │
│     └─────────────┘   └─────────────┘          │
│           │                 ▲                   │
│           └─────────────────┘                   │
│                                                 │
│ Selected: personas/architect.py                │
│ ├─ Depends on: router_v2.py, config.py         │
│ ├─ Used by: orchestrator.py, server.py         │
│ └─ Complexity: 450 LOC, 15 functions            │
└─────────────────────────────────────────────────┘
```

**Graph Features:**
- **Zoom & Pan:** Navigate large codebases
- **Click Node:** Highlight all dependencies
- **Hover:** Show quick stats
- **Filter:** By module, file type, complexity
- **Search:** Find specific components
- **Layouts:** Force-directed, hierarchical, circular

### 3. Impact Analysis

**"What breaks if I change this?"**

**Capability:** Before refactoring, see ripple effects

**Example Interaction:**
```
User: "I want to rename auth_service.authenticate() to login()"

Polly (with Architecture System):
"⚠️  This change impacts:
 
 Direct dependencies (3):
 ├─ auth_controller.py:34 (direct call)
 ├─ api_routes.py:89 (direct call)
 └─ tests/test_auth.py:45 (unit test)
 
 Indirect dependencies (7):
 ├─ user_dashboard.js → calls auth_controller
 ├─ admin_panel.js → calls auth_controller
 └─ 5 other frontend components
 
 Should I:
 1. Refactor all references automatically
 2. Show me each change for review
 3. Cancel this refactoring"
```

**Technical Approach:**
- Static analysis of call graph
- Search codebase for references
- Parse AST (Abstract Syntax Tree)
- Track transitive dependencies

### 4. Architecture Documentation (Auto-Generated)

**Living Documentation:**
- Generate architecture docs from code
- Update automatically on changes
- Markdown + Mermaid diagrams
- Save to vault as notes

**Example Output:**
```markdown
# Polly Backend Architecture

## Module: Authentication System

### Overview
The authentication system handles user login, token generation, 
and session management across the application.

### Components
- **auth_controller.py**: HTTP request handling for auth endpoints
- **auth_service.py**: Business logic for authentication
- **jwt_util.py**: Token generation and validation

### Data Flow
mermaid
graph LR
    A[Client] -->|POST /login| B[auth_controller]
    B --> C[auth_service.authenticate]
    C --> D[user_model.find_by_email]
    C --> E[jwt_util.generate_token]
    E -->|JWT token| A


### Dependencies
- Depends on: user_model, jwt_util, database
- Used by: api_routes, user_dashboard, admin_panel

### Recent Changes
- 2026-02-01: Added OAuth support
- 2026-01-28: Refactored token expiration logic
```

### 5. Compression System Integration

**Context Compression for LLM:**
- Full codebase too large for context window
- Architecture graph provides high-level overview
- Polly can reason about structure without seeing all code

**How It Works:**
```
User: "How does data flow from API to database?"

Without Architecture System:
- Polly needs to read 20+ files (context overflow)
- Slow, expensive, may miss connections

With Architecture System:
- Polly reads compressed architecture graph
- Sees: API → Controller → Service → Model → Database
- Fast, cheap, complete picture
- Only loads specific files when needed
```

**Technical Implementation:**
- Store architecture as compressed graph
- Use graph query language (Cypher-like)
- Cache frequently accessed paths
- Incremental updates on file changes

### 6. AI Architectural Reasoning

**Architect Persona Integration:**
- Architect can query architecture graph
- "Show me all API endpoints"
- "Find circular dependencies"
- "What modules depend on this?"

**Example Queries:**
```
User: "Are there any circular dependencies in the codebase?"

Polly (Architect mode):
"🔍 Analyzing architecture graph...

Found 1 circular dependency:
├─ personas/architect.py
│  └─> orchestrator.py
│     └─> personas/architect.py

Recommendation: Extract shared interface to break cycle."
```

---

## Technical Architecture

### Components

#### 1. Code Parser (`core/architecture/parser.py`)

**Responsibilities:**
- Parse source files (AST analysis)
- Extract imports, function calls, class definitions
- Build dependency graph
- Support multiple languages

**Key Classes:**
```python
class CodeParser:
    def parse_file(self, filepath: str) -> FileNode
    def extract_imports(self, ast: AST) -> List[Import]
    def extract_calls(self, ast: AST) -> List[FunctionCall]
    def build_dependency_tree(self, files: List[FileNode]) -> DependencyGraph
    
class FileNode:
    path: str
    language: str
    imports: List[str]
    exports: List[str]
    calls: List[FunctionCall]
    classes: List[ClassDefinition]
    functions: List[FunctionDefinition]
    complexity: int
    
class DependencyGraph:
    nodes: Dict[str, FileNode]
    edges: List[Dependency]
    
    def find_dependents(self, node_id: str) -> List[str]
    def find_dependencies(self, node_id: str) -> List[str]
    def detect_circular_dependencies(self) -> List[List[str]]
    def calculate_impact(self, node_id: str) -> ImpactReport
```

#### 2. Architecture Store (`core/architecture/store.py`)

**Responsibilities:**
- Persist architecture graph to disk
- Incremental updates (don't rebuild entire graph)
- Query interface for fast lookups
- Version tracking (see architecture history)

**Storage Format:**
```json
{
  "version": "1.0",
  "project": "polly-backend",
  "analyzed_at": "2026-02-03T10:00:00Z",
  "nodes": [
    {
      "id": "core/polly.py",
      "type": "file",
      "language": "python",
      "lines": 850,
      "complexity": 45,
      "imports": ["router_v2", "personas/architect"],
      "exports": ["Polly", "handle_request"]
    }
  ],
  "edges": [
    {
      "from": "core/polly.py",
      "to": "router/router_v2.py",
      "type": "imports",
      "line": 12
    }
  ]
}
```

**Storage Location:**
```
vault/.polly/architecture/
├── projects/
│   ├── polly-backend/
│   │   ├── graph.json
│   │   ├── history/
│   │   │   ├── 2026-02-03.json
│   │   │   └── 2026-02-01.json
│   │   └── cache/
│   │       └── query_cache.json
│   └── my-react-app/
│       └── graph.json
└── config.yaml
```

#### 3. Impact Analyzer (`core/architecture/impact.py`)

**Responsibilities:**
- Calculate refactoring impact
- Find all references to a symbol
- Detect breaking changes
- Estimate refactoring effort

**Key Functions:**
```python
class ImpactAnalyzer:
    def analyze_change(self, 
                       node_id: str, 
                       change_type: ChangeType) -> ImpactReport
    
    def find_all_references(self, symbol: str) -> List[Reference]
    
    def calculate_refactoring_cost(self, 
                                   changes: List[Change]) -> RefactoringCost

class ImpactReport:
    direct_dependencies: List[str]  # Files that directly depend
    indirect_dependencies: List[str]  # Transitive dependencies
    affected_tests: List[str]
    affected_frontend: List[str]  # If backend change
    breaking_change: bool
    estimated_effort: int  # minutes
```

#### 4. Visualization Engine (`frontend: architecture-viewer.js`)

**Responsibilities:**
- Render interactive graph
- Handle user interactions (zoom, pan, click)
- Update in real-time
- Export diagrams

**Technologies:**
- **Cytoscape.js**: Graph visualization library
- **D3.js**: Alternative (more customizable)
- **Mermaid**: For embedded diagrams in notes

**Features:**
```javascript
class ArchitectureViewer {
    // Load and render graph
    async loadProject(projectPath) { }
    
    // User interactions
    onNodeClick(nodeId) { }  // Highlight dependencies
    onNodeHover(nodeId) { }  // Show quick info
    
    // Filtering
    filterByModule(moduleName) { }
    filterByComplexity(min, max) { }
    
    // Layouts
    setLayout('force-directed' | 'hierarchical' | 'circular') { }
    
    // Export
    exportAsSVG() { }
    exportAsPNG() { }
    exportAsMermaid() { }
}
```

#### 5. Watcher (`core/architecture/watcher.py`)

**Responsibilities:**
- Monitor code directory for changes
- Trigger incremental graph updates
- Avoid full rebuilds
- Debounce rapid changes

**How It Works:**
```python
class ArchitectureWatcher:
    def __init__(self, project_path: str):
        self.watcher = FileSystemWatcher(project_path)
        self.debounce_timer = None
        
    def on_file_changed(self, filepath: str):
        # Debounce: wait 2 seconds for more changes
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = Timer(2.0, self.update_graph)
        self.debounce_timer.start()
    
    def update_graph(self):
        # Incremental update (only changed files)
        changed_files = self.get_changed_files()
        self.parser.update_nodes(changed_files)
        self.graph.rebuild_edges()
        self.store.save()
```

---

## Integration with SummonAI Kit

**Research Area:** Your brain dump mentioned SummonAI Kit for code stack analysis

**Potential Integration:**
```python
# If SummonAI provides better parsing
from summonai import CodeAnalyzer

class PollyCodeParser(CodeParser):
    def __init__(self):
        self.summon_analyzer = CodeAnalyzer()
    
    def parse_with_summon(self, filepath: str):
        # Use SummonAI for deeper analysis
        analysis = self.summon_analyzer.analyze(filepath)
        return self.convert_to_polly_format(analysis)
```

**What to Research:**
- Does SummonAI offer dependency analysis?
- Is it better than AST parsing?
- Can it detect runtime dependencies (not just static)?
- Licensing and cost?

---

## User Workflows

### Workflow 1: Understanding a New Codebase

**User:** "I just joined a project. Help me understand the architecture."

**Polly Interaction:**
```
1. User opens Code Workspace
2. Clicks "Analyze Architecture" button
3. Polly parses codebase (30 seconds)
4. Shows interactive graph in sidebar

User: "Show me the authentication flow"

Polly: [Highlights auth-related nodes in graph]
       "The authentication system consists of:
        - auth_controller.py (API entry point)
        - auth_service.py (business logic)
        - jwt_util.py (token management)
        
        Data flows: 
        Client → Controller → Service → JWT Util → Database"

5. Polly generates architecture note (auto-saved to vault)
```

### Workflow 2: Safe Refactoring

**User:** "I want to rename the `User` class to `Account`"

**Polly Interaction:**
```
1. User right-clicks User class in code
2. Selects "Refactor → Rename"
3. Polly queries architecture graph

Polly: "⚠️  This class is used in 23 files:
        
        Direct references (15):
        ├─ user_controller.py (8 locations)
        ├─ auth_service.py (3 locations)
        └─ ... 13 more files
        
        Indirect references (8):
        ├─ API endpoints that return User objects
        └─ Frontend components expecting User schema
        
        I can refactor all references automatically.
        Estimated time: 2 minutes
        
        [Proceed] [Show me each change] [Cancel]"

4. User clicks "Proceed"
5. Polly refactors all files
6. Updates architecture graph
7. Shows diff for review
```

### Workflow 3: Architecture-Aware Coding

**User:** "Add a new payment processing module"

**Polly Interaction (Architect mode):**
```
Polly: "I'll design this with your existing architecture in mind.

Based on your codebase structure, I recommend:

📁 Project Structure:
payment/
├── payment_controller.py  (API endpoints)
├── payment_service.py     (business logic)
├── stripe_adapter.py      (payment provider)
└── payment_model.py       (database schema)

This matches your existing pattern:
- Controllers handle HTTP
- Services contain business logic
- Adapters for external APIs
- Models for data persistence

Dependencies:
├─ payment_service → stripe_adapter (calls)
├─ payment_controller → payment_service (calls)
└─ routes.py → payment_controller (imports)

Impact on existing code:
- Need to add routes in routes.py
- Update database schema in migrations/
- Frontend: Create new payment components

Should I proceed with implementation?"
```

---

## API Design

### Backend Endpoints

```python
# Analyze project
POST /architecture/analyze
Request: {
    "project_path": "/path/to/project",
    "languages": ["python", "javascript"],
    "include_tests": true
}
Response: {
    "graph_id": "proj_abc123",
    "status": "analyzing",
    "progress": 0
}

# Get graph status
GET /architecture/graphs/<graph_id>
Response: {
    "status": "complete",
    "nodes": 156,
    "edges": 423,
    "last_updated": "2026-02-03T10:00:00Z"
}

# Get graph data
GET /architecture/graphs/<graph_id>/data
Response: {
    "nodes": [...],
    "edges": [...]
}

# Query graph
POST /architecture/graphs/<graph_id>/query
Request: {
    "query": "FIND dependents OF 'core/polly.py'"
}
Response: {
    "results": ["router_v2.py", "server.py", "orchestrator.py"]
}

# Impact analysis
POST /architecture/graphs/<graph_id>/impact
Request: {
    "node_id": "auth_service.py",
    "change_type": "rename_function",
    "symbol": "authenticate"
}
Response: {
    "impact": ImpactReport
}

# Export documentation
POST /architecture/graphs/<graph_id>/export
Request: {
    "format": "markdown",
    "include_diagrams": true
}
Response: {
    "note_id": "note_xyz789",
    "path": "vault/Architecture/polly-backend.md"
}
```

---

## UI/UX Design

### Architecture Viewer Location

**Option 1: New Page (Recommended)**
```
Left Navigation Ribbon:
├─ Dashboard
├─ Chat
├─ Notes
├─ Learning
├─ Calendar
├─ Settings
└─ 🏗️ Architecture (NEW)
```

**Option 2: Code Workspace Integration**
```
Code Workspace Page:
├─ Left: File tree
├─ Center: Code editor
└─ Right: Architecture viewer (collapsible)
```

### Graph Interaction Patterns

**Click Behaviors:**
- **Single click node:** Highlight dependencies (both directions)
- **Double click node:** Open file in editor
- **Right click node:** Context menu (refactor, find references, etc.)
- **Click edge:** Show connection details (line numbers, type)

**Keyboard Shortcuts:**
- `Cmd+F`: Search nodes
- `Cmd+[`: Go back
- `Cmd+]`: Go forward
- `Space`: Toggle layout
- `+/-`: Zoom in/out

---

## Success Criteria

### Phase 25 Complete When:

**Backend:**
- [x] Code parser working for Python + JavaScript
- [x] Dependency graph generation functional
- [x] Architecture store with incremental updates
- [x] Impact analyzer operational
- [x] File watcher detecting changes
- [x] API endpoints complete

**Frontend:**
- [x] Interactive graph viewer (Cytoscape.js)
- [x] Node/edge interactions working
- [x] Filter and search functional
- [x] Multiple layout algorithms
- [x] Export functionality (SVG, PNG, Markdown)

**Architect Integration:**
- [x] Architect can query architecture graph
- [x] Architecture-aware code generation
- [x] Impact warnings before refactoring
- [x] Auto-generated architecture notes

**Testing:**
- [x] Parse 1000+ file codebase in <1 minute
- [x] Incremental updates in <5 seconds
- [x] Circular dependency detection working
- [x] Impact analysis accurate (no false negatives)
- [x] Graph rendering smooth for 500+ nodes

**Documentation:**
- [x] User guide for architecture viewer
- [x] API documentation
- [x] Parser extension guide (new languages)

---

## Future Enhancements (Post-Phase 25)

### Phase 25b: Advanced Analysis
- Runtime dependency tracking (not just static)
- Performance hotspot detection
- Security vulnerability scanning
- Code smell detection
- Test coverage overlay on graph

### Phase 25c: Collaborative Architecture
- Shared architecture across team
- Architecture review workflows
- Comment on architecture components
- Architecture decision records (ADRs)

### Phase 25d: AI Architecture Evolution
- Polly suggests architectural improvements
- "This module is too complex, consider splitting"
- "These 3 modules could be extracted to library"
- Proactive refactoring recommendations

---

## Dependencies

**Required Phases:**
- Phase 17: Code Workspace (location for architecture viewer)
- ✅ Phase 11c: Agent Personas (Architect integration)

**Enhances:**
- Phase 24: Orchestrator Mode (architecture-aware orchestration)
- Phase 27: Designer Persona (UI architecture visualization)
- Phase 16c: AI Note Creation (auto-generate architecture docs)

**Research Dependencies:**
- SummonAI Kit evaluation (better parsing?)
- AST parsing libraries (Python: ast, JS: Babel)
- Graph visualization performance benchmarks

---

## Risk Assessment

**High Risk:**
- Performance: Large codebases (10k+ files) may be slow
- Accuracy: Static analysis misses runtime dependencies
- Complexity: Graph can become overwhelming (too many edges)

**Mitigations:**
- Lazy loading: Only render visible portion of graph
- Sampling: Analyze subset for large projects
- Filtering: Hide low-importance edges by default
- Progressive enhancement: Start with imports, add calls later

**Medium Risk:**
- Multi-language support: Each language needs parser
- Incremental updates: Hard to keep graph in sync
- False positives: Impact analysis may over-report

**Mitigations:**
- Start with 2-3 languages (Python, JS, TypeScript)
- File watcher with debouncing
- Conservative analysis (err on side of caution)

---

## Questions to Resolve

1. **SummonAI Integration:** Is it worth integrating vs. building custom parsers?
2. **Graph Database:** Should we use Neo4j or stay with JSON files?
3. **Real-time Updates:** How fast can we update graph after code change?
4. **Language Priority:** What languages to support first? Python + JS? Add Rust?
5. **Compression Format:** How to efficiently compress large architecture graphs?

---

**Document Created:** February 3, 2026  
**Status:** Ready for research phase (SummonAI evaluation)  
**Next Step:** Investigate SummonAI Kit capabilities, then create implementation plan
