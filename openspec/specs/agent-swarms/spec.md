# Agent Swarms (OpenSpec)

Source of truth for Polly's configurable multi-agent workflow architecture. Subsumes and expands the original Phase 24 Orchestrator Mode concept.

## Overview

Agent Swarms is Polly's system for composing multiple AI agents into collaborative workflows. Rather than a single LLM processing everything sequentially, complex tasks decompose into subtasks handled by specialized agents that coordinate through a central Nexus.

The architecture distinguishes three things:

1. **Agent interface** — What an agent can do (capability declaration, input/output schemas, execution context requirements).
2. **Nexus** — The coordination layer that matches tasks to agents, composes workflows, and manages handoffs. Named to avoid collision with existing Router v2 (model selection) and DRM Router (node selection).
3. **Workflow** — A composed sequence or graph of agent invocations that achieves a user goal.

This creates a third routing tier in Polly's stack:

```
User Query → Nexus (which agents?) → DRM Router (which node?) → Router v2 (which model?)
```

## Design Principles

- **Composability over monoliths** — Agents declare capabilities; the Nexus composes them. No agent needs to know about other agents.
- **Progressive autonomy** — Tight oversight initially, looser as user trust builds. Intervention points at every agent boundary.
- **Templates over blank canvases** — Pre-configured swarms for common workflows. Users fork and modify, not build from scratch.
- **Agent pools, not rigid pipelines** — User defines available agents; Nexus dynamically composes workflows based on task analysis rather than pre-defined chains.
- **Transparency in execution** — Show which agent is working, what it's producing, where handoffs occur. Builds user understanding and enables debugging.

## Agent Interface Specification

Every agent in Polly (including existing personas) declares a formal capability contract:

### Core Agent Properties

```yaml
agent:
  id: "code-reviewer"
  name: "Code Reviewer"
  version: "1.0"

  # What this agent consumes
  input_schema:
    required:
      - code: string        # Source code to review
      - language: string     # Programming language
    optional:
      - style_guide: string  # Project style guide reference
      - focus_areas: [string] # Specific concerns to check

  # What this agent produces
  output_schema:
    issues: [{ severity: string, line: number, message: string }]
    summary: string
    score: number  # 0-100 quality score

  # What tasks it can handle
  capabilities:
    - code_review
    - style_checking
    - security_audit
    - performance_analysis

  # What other agent outputs it needs (optional)
  dependencies:
    optional:
      - file_context: "file-reader"  # Can use file reader output

  # Synchronous/asynchronous, interactive/autonomous
  execution_mode:
    type: autonomous         # autonomous | interactive | hybrid
    async_capable: true
    streaming: true

  # Resource constraints
  resource_constraints:
    max_tokens: 4096
    timeout_seconds: 120
    cost_cap_usd: 0.10
    prefer_local: true       # Prefer local model when capable

  # Execution contexts required (brokered via Capability Broker)
  execution_contexts:
    required: []
    optional:
      - github              # Can access repos if available
      - filesystem           # Can read project files if available

  # Domain affinity (for domain-aware routing)
  domain_affinity:
    primary: ["sigils"]      # Example: code-related domain
    secondary: []
```

### Persona-to-Agent Mapping

Existing personas become agents with formal declarations:

| Persona | Agent Capabilities | Execution Contexts | Modes as Sub-Agents |
|---|---|---|---|
| **Architect** | planning, decomposition, canvas_analysis | filesystem, github | Plan Agent, Build Agent, Canvas Agent |
| **Scribe** | writing, enrichment, publishing, organization | obsidian, ghost_cms | Capture Agent, Organize Agent, Enrich Agent, Edit Agent, Publish Agent |
| **Professor** | teaching, assessment, curriculum, explanation | curriculum_db | Explain Agent, Socratic Agent, Quiz Agent |

Each persona mode becomes a distinct agent capability that the Nexus can invoke independently. The persona itself becomes an agent *group* — a pre-composed swarm.

## Nexus: Agent Coordination Layer

### Responsibility

The Nexus receives a task, determines whether a single agent suffices or a multi-agent workflow is needed, then orchestrates execution.

### Routing Logic

```
1. Parse incoming task/query
2. Classify task complexity and required capabilities
3. Match against agent capability declarations
4. Determine if single agent suffices or multi-agent workflow needed
5. If multi-agent: construct execution graph based on dependencies
6. Route outputs between agents according to schema compatibility
7. Monitor execution, handle failures, manage intervention points
8. Present aggregated result or hand back to user for continuation
```

### Execution Graph

Multi-agent workflows form a DAG (directed acyclic graph):

```
          ┌─── Agent A ───┐
Task ───→ │                ├───→ Merge → Result
          └─── Agent B ───┘
               ↓
          Agent C (depends on B)
```

The Nexus manages:
- **Parallel execution** — Independent agents run simultaneously.
- **Sequential dependencies** — Agent C waits for Agent B's output.
- **Merge strategies** — Combine results (first-response, consensus, ensemble, reduce).
- **Intervention points** — User can pause, redirect, or take over at any agent boundary.

### Task Complexity Assessment

```yaml
complexity_signals:
  simple:    # Single agent
    - Single capability required
    - No cross-context needs
    - Low token budget
  moderate:  # 2-3 agents, mostly sequential
    - Multiple capabilities but clear order
    - One execution context
  complex:   # Full swarm
    - Multiple capabilities in parallel
    - Multiple execution contexts
    - Cross-domain reasoning
    - Iterative refinement needed
```

### Failure Handling

- **Agent failure** — Retry same agent with modified parameters, route to fallback agent with same capability, or escalate to user.
- **Timeout** — Partial results returned with status indicator. User decides: wait, retry, or accept partial.
- **Schema mismatch** — If Agent A's output doesn't match Agent B's expected input, Nexus attempts automatic transformation or asks user to resolve.
- **Feedback loop** — Agent outputs evaluated against task requirements. If insufficient, Nexus can re-route or request elaboration.

## Workflow Templates

Pre-configured swarms for common workflows. Users start here and customize.

### Built-in Templates

| Template | Agents | Workflow |
|---|---|---|
| **Research → Write** | Scribe(Research) → Scribe(Organize) → Scribe(Write) → Scribe(Edit) | Sequential pipeline for turning research into a draft |
| **Code Review + Docs** | Architect(Build) → Code Reviewer → Doc Generator | Review code, then generate documentation |
| **Plan → Build → Test** | Architect(Plan) → Architect(Build) → Code Reviewer | Full development cycle |
| **Teach → Assess → Refine** | Professor(Explain) → Professor(Quiz) → Professor(Socratic) | Teaching workflow with assessment |
| **Capture → Enrich → Publish** | Scribe(Capture) → Scribe(Enrich) → Scribe(Publish) | POSE publishing pipeline as swarm |
| **Multi-Domain Analysis** | Domain Agent A ∥ Domain Agent B → Merge Agent | Parallel analysis across domains |
| **Canvas Validation** | Architect(Canvas) → Business Analyst → User Researcher | BAD Canvas gap analysis |

### Template Structure

```yaml
template:
  id: "research-to-publish"
  name: "Research → Publish"
  description: "Turn research into a published piece"
  domain_affinity: ["scrolls"]  # Suggested for writing domains

  agents:
    - id: researcher
      type: scribe
      mode: research
      input: { topic: "$user_input" }

    - id: organizer
      type: scribe
      mode: organize
      input: { content: "$researcher.output" }
      depends_on: [researcher]

    - id: writer
      type: scribe
      mode: write
      input: { outline: "$organizer.output", style: "$user_preferences.writing_style" }
      depends_on: [organizer]

    - id: editor
      type: scribe
      mode: edit
      input: { draft: "$writer.output" }
      depends_on: [writer]

  intervention_points:
    - after: researcher
      prompt: "Review research findings before proceeding?"
    - after: writer
      prompt: "Review draft before editing?"

  output: "$editor.output"
```

## Execution Contexts

Agents don't just need LLM access — they need brokered access to external systems. The Nexus requests execution contexts from the Capability Broker (Phase 23.5 security system).

### Context Types

| Context | Provides | Used By |
|---|---|---|
| **filesystem** | Read/write files, directory listing | Architect, Code agents |
| **github** | Repo access, PR operations, issue management | Code agents, Project agents |
| **obsidian** | Vault read/write, wikilink resolution | Scribe, Knowledge agents |
| **ghost_cms** | Post creation, media upload, scheduling | Scribe(Publish) |
| **email** | Inbox access, SMTP send, template library | Communication agents |
| **calendar** | Event read/write, availability check | Scheduling agents |
| **knowledge_graph** | Entity queries, connection metrics | Any agent needing context |
| **rag** | Semantic search, domain-filtered retrieval | Any agent needing knowledge |
| **drm** | Task distribution to peer nodes | Nexus (for distributed swarms) |

### Context Brokering

```
Agent requests: { contexts: ["github", "filesystem"] }
                      ↓
Capability Broker checks:
  - Is this agent authorized for these contexts?
  - Does the user allow these contexts for this workflow?
  - Are credentials available?
                      ↓
Grants scoped access token with:
  - Time-limited validity
  - Operation restrictions (read-only vs read-write)
  - Resource scope (specific repos, directories)
```

This extends the Phase 23.5 Capability Broker from LLM-focused to agent-execution-focused. The broker mediates trust between agents and external systems.

## Progressive Disclosure (Configuration Levels)

Users interact with swarm configuration at the level matching their task complexity and technical comfort.

### Level 1: Pre-Configured Swarms (Most Users)

One-click activation of workflow templates. Natural language task description, system selects appropriate template.

```
User: "Turn my research notes on shift registers into a blog post"
Polly: [Activates Research → Publish template with Signals domain context]
```

### Level 2: Modify Existing Swarms

Add/remove agents from templates. Adjust parameters (temperature, token limits, intervention points). Change routing logic (parallel vs sequential). Save modified templates for reuse.

### Level 3: Define Custom Agents

Full agent specification via structured form. Define input/output schemas, capabilities, execution contexts. Connect custom agents to existing workflows.

### Level 4: Code-Level Control (Power Users)

Write routing logic as Python. Algorithmic control over agent coordination. Custom merge strategies and evaluation functions. Direct API access to the Nexus.

```python
# Level 4 example
from polly.swarms import Nexus, Agent, Workflow

nexus = Nexus()

# Define custom agent
analyzer = Agent(
    capabilities=["code_analysis", "pattern_detection"],
    input_schema={"code": str, "patterns": list},
    output_schema={"matches": list, "suggestions": list},
    execution_contexts=["github"],
    resource_constraints={"timeout_seconds": 60}
)

# Compose workflow
workflow = Workflow([
    ("analyze", analyzer, {"code": user_code}),
    ("review", nexus.get_agent("code-reviewer"), {"input": "$analyze.output"}),
])

result = await nexus.execute(workflow)
```

Most users operate at Level 1–2. Polymathic power users at Level 3–4.

## DRM Integration

Agent Swarms compose logically; DRM distributes physically. When the Nexus decomposes a task into parallel agent invocations, DRM distributes those across available nodes.

```
Nexus creates 3 parallel agent tasks
  ↓
DRM Router assigns:
  - Agent A → desktop-polly (has Sigils model loaded)
  - Agent B → nas-polly (available capacity)
  - Agent C → local (low latency, interactive)
  ↓
Results return to Nexus for merge
```

The DRM's existing scoring function (capability + load + locality) applies directly to agent task distribution. Agent capability declarations map to DRM task requirements.

## Domain-Aware Swarm Routing

The Nexus uses domain context when composing workflows:

- **Domain affinity on templates** — "Research → Publish" is suggested when user is in Scrolls domain.
- **Domain-specific agent pools** — Code-domain agents (linter, reviewer) surface for Sigils work.
- **Cross-domain swarms** — When a task spans domains (e.g., "Review this SuperCollider code for pedagogical clarity"), the Nexus composes agents from multiple domain pools.
- **Custom keyword triggers** — Domain `autoTagRules` inform which swarm templates are relevant.

## RAG Integration

Agents access Polly's knowledge through the RAG system:

- **Swarm-context retrieval** — When a swarm is active, RAG searches are filtered by the swarm's domain context and active agents' needs.
- **Agent memory** — The Nexus maintains a shared context for the swarm execution: what each agent produced, what decisions were made. This context is available to subsequent agents.
- **Knowledge graph traversal** — Agents can request entity-graph queries (e.g., "find all notes connected to this concept within 2 hops").
- **Cross-agent RAG** — If Agent B needs context that Agent A already retrieved, the Nexus passes it through rather than re-querying.

## State Management

### Within a Workflow

- **Shared context** — Each agent sees: (a) its specific input, (b) shared workflow context curated by Nexus, (c) optional: full conversation history.
- **Configurable context scope** — Users can choose between "full history" (every agent sees everything) and "relevant context" (Nexus curates what each agent needs).
- **State persistence** — In-flight workflow state saved to SQLite. Workflows survive server restarts.

### Across Workflows

- **Workflow history** — Completed workflows stored with metadata: which agents ran, what they produced, total cost/time.
- **Pattern learning** — Successful workflow patterns fed to PatternLearner. If "Research → Write" consistently works well for Scrolls domain, that's learned.
- **Template evolution** — User modifications to templates tracked. Frequently-used modifications suggested as defaults.

## Feedback and Improvement

- **Agent output evaluation** — User ratings (thumbs up/down) on agent outputs feed back to routing decisions.
- **Routing pattern learning** — Which agents work best for which task types, learned over time via PatternLearner.
- **Automatic template suggestion** — Based on task analysis + learned patterns, Nexus suggests templates before user chooses.
- **Cost tracking** — Per-agent and per-workflow cost/token/time metrics. Budget-aware swarm composition (prefer cheaper agents when quality is sufficient).

## API

### Nexus Endpoints

```
POST /swarms/execute          # Submit task for swarm execution
GET  /swarms/{id}             # Query workflow status
POST /swarms/{id}/intervene   # User intervention at agent boundary
POST /swarms/{id}/cancel      # Cancel in-flight workflow

GET  /swarms/templates        # List available workflow templates
POST /swarms/templates        # Create custom template
PUT  /swarms/templates/{id}   # Modify template

GET  /agents                  # List registered agents with capabilities
POST /agents                  # Register custom agent
GET  /agents/{id}/schema      # Get agent input/output schema

GET  /swarms/history          # Completed workflow history
GET  /swarms/metrics          # Cost, time, success metrics
```

### Data Model

```sql
-- Workflow execution tracking
CREATE TABLE swarm_executions (
    id TEXT PRIMARY KEY,
    template_id TEXT,
    status TEXT,  -- 'pending', 'running', 'paused', 'completed', 'failed'
    input_data TEXT,  -- JSON
    output_data TEXT, -- JSON
    agents_used TEXT, -- JSON array of agent IDs
    total_tokens INTEGER,
    total_cost_usd REAL,
    total_time_ms INTEGER,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Per-agent execution within a workflow
CREATE TABLE swarm_agent_runs (
    id TEXT PRIMARY KEY,
    execution_id TEXT REFERENCES swarm_executions(id),
    agent_id TEXT,
    status TEXT,
    input_data TEXT,  -- JSON
    output_data TEXT, -- JSON
    tokens_used INTEGER,
    cost_usd REAL,
    duration_ms INTEGER,
    node_id TEXT,  -- DRM node that executed this (NULL = local)
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Workflow templates
CREATE TABLE swarm_templates (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    domain_affinity TEXT,  -- JSON array
    template_data TEXT,    -- JSON (full template YAML as JSON)
    is_builtin BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    avg_rating REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Agent registry
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,  -- 'persona', 'custom', 'builtin'
    capabilities TEXT,      -- JSON array
    input_schema TEXT,      -- JSON
    output_schema TEXT,     -- JSON
    execution_contexts TEXT, -- JSON array
    resource_constraints TEXT, -- JSON
    domain_affinity TEXT,    -- JSON array
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

Storage in `~/.polly/knowledge.db` alongside other knowledge platform tables.

## UI

### Swarm Execution View

```
┌─────────────────────────────────────────────────────┐
│ Swarm: Research → Publish          ⏱ 2m 34s  $0.08 │
│ Domain: Scrolls                    Status: Running  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  [Researcher] ✅ → [Organizer] ✅ → [Writer] 🔄 → [Editor] ⏳ │
│                                                       │
│  ┌─ Writer Output (streaming) ──────────────────────┐│
│  │ The shift register, at its core, is a digital    ││
│  │ circuit that moves data through a chain of       ││
│  │ flip-flops with each clock cycle...              ││
│  └──────────────────────────────────────────────────┘│
│                                                       │
│  [⏸ Pause] [✋ Intervene] [⏭ Skip Agent] [✕ Cancel] │
└─────────────────────────────────────────────────────┘
```

### Template Browser

```
┌─────────────────────────────────────────────────────┐
│ Workflow Templates                    [+ New Template]│
├─────────────────────────────────────────────────────┤
│ Suggested for Scrolls domain:                        │
│                                                       │
│  📝 Research → Publish    ★ 4.8  Used 12x           │
│  📚 Capture → Enrich      ★ 4.5  Used 8x            │
│  🎓 Teach → Assess        ★ 4.2  Used 3x            │
│                                                       │
│ All templates:                                        │
│                                                       │
│  🔧 Plan → Build → Test   ★ 4.6  Used 15x           │
│  🔍 Code Review + Docs    ★ 4.3  Used 7x            │
│  🎯 Canvas Validation     ★ 4.0  Used 2x            │
│  📊 Multi-Domain Analysis  ★ 3.9  Used 5x            │
│                                                       │
│ [Browse All] [My Templates] [Create from Scratch]    │
└─────────────────────────────────────────────────────┘
```

### Agent Configuration (Level 3)

```
┌─────────────────────────────────────────────────────┐
│ Define Agent: Custom Code Analyzer                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│ Capabilities: [code_analysis] [pattern_detection] +  │
│                                                       │
│ Input Schema:                                         │
│   code (string, required)                             │
│   language (string, required)                         │
│   patterns (array, optional)                          │
│                                                       │
│ Output Schema:                                        │
│   matches (array)                                     │
│   suggestions (array)                                 │
│   score (number)                                      │
│                                                       │
│ Execution Contexts: [github ✓] [filesystem ✓]        │
│                                                       │
│ Constraints:                                          │
│   Max tokens: [4096]  Timeout: [120s]  Cost cap: [$0.10] │
│   ☑ Prefer local model                               │
│                                                       │
│ Domain Affinity: [Sigils ✓]                           │
│                                                       │
│ [Test Agent] [Save] [Add to Template]                │
└─────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 24a: Nexus Foundation (2–3 weeks)

- Agent interface specification (capability declarations, schemas)
- Nexus core: task classification, single-agent routing
- Persona-to-agent adapter (existing personas wrapped as agents)
- Agent registry (SQLite)
- Basic API endpoints

### Phase 24b: Multi-Agent Workflows (2–3 weeks)

- Workflow template system (YAML templates, built-in templates)
- Execution graph construction and management
- Sequential and parallel agent execution
- Result merge strategies
- Intervention points and user control
- Workflow state persistence

### Phase 24c: Execution Contexts + Capability Broker Integration (1–2 weeks)

- Execution context declarations and brokering
- Extend Phase 23.5 Capability Broker for agent contexts
- Scoped access tokens with time limits and operation restrictions
- Context types: filesystem, github, obsidian, rag, knowledge_graph

### Phase 24d: Template UI + Progressive Disclosure (2–3 weeks)

- Level 1: Template browser with domain suggestions
- Level 2: Template modification UI
- Swarm execution view with streaming, intervention, cost tracking
- Workflow history and metrics

### Phase 24e: Advanced Features (2–3 weeks)

- Level 3: Custom agent definition UI
- Level 4: Code-level Nexus API
- DRM integration (distribute agent tasks across nodes)
- Pattern learning integration (successful workflow patterns)
- Cross-domain swarm routing
- Cost-aware swarm composition

**Dependencies:** Phase 23.5 (Security / Capability Broker) must complete first. Personas (Phase 11) already done. DRM integration optional but enhances.

## Relationship to Other Systems

| System | Integration |
|---|---|
| **Personas** | Personas wrapped as agents; modes become agent capabilities. Nexus replaces planned "Orchestrator mode" toggle |
| **DRM** | Physical distribution layer for parallel agent tasks. DRM scoring applies to agent task assignment |
| **Router v2** | Model selection remains within each agent. Nexus sits above: Nexus → DRM → Router v2 |
| **RAG** | Agents access knowledge via RAG. Cross-agent context sharing prevents redundant queries |
| **Knowledge Graph** | Agents query entity graph for context. Swarm outputs can trigger entity extraction |
| **Security** | Capability Broker mediates agent access to execution contexts. Trust model enforced |
| **Patterns** | Successful workflow patterns learned. Template suggestions improve over time |
| **Domains** | Domain affinity on agents and templates. Cross-domain swarms for polymathic tasks |
| **Canvas** | Canvas validation as a workflow template. Architect(Canvas) as specialized agent |
| **Publishing** | POSE pipeline expressible as a swarm workflow. Scribe modes as publishing agents |
| **Capture** | Capture processing pipelines as lightweight swarms (entity extraction → routing → enrichment) |
| **Analytics** | Per-workflow and per-agent metrics. Swarm efficiency tracking |

## Key Architectural Decisions

### Why "Nexus" not "Orchestrator"?

"Orchestrator" implies top-down control. Nexus emphasizes the connection-point role — agents have autonomy; the Nexus routes and connects. It also avoids naming collision with existing Phase 24 "Orchestrator Mode" label, since the concept has expanded significantly.

### Why not CrewAI directly?

The original Phase 24 plan used CrewAI as the framework. The Agent Swarms architecture is more fundamental — it defines a Polly-native agent interface that *could* use CrewAI as one implementation backend, but isn't coupled to it. Benefits:
- Agent interface is Polly's own, portable across execution backends
- Existing persona system maps cleanly without framework translation layer
- DRM integration is native (CrewAI doesn't know about node distribution)
- Progressive disclosure (Levels 1–4) is a Polly design principle, not a framework feature

CrewAI can still be used under the hood for workflow execution if its patterns prove valuable, but the agent interface and Nexus are Polly-owned.

### Why formal capability declarations?

Composability. If agents declare what they can do and what they need, the Nexus can dynamically compose workflows without hard-coded routing logic. New agents plug in without modifying existing code. This is the plugin architecture made concrete.

### Why execution contexts as a first-class concept?

Agents in Polly don't just generate text — they interact with systems (GitHub, Obsidian, Ghost CMS, filesystem). Treating these as declared, brokered execution contexts means:
- Security model is explicit (Capability Broker mediates all access)
- New integrations automatically become available to agents
- Users can see and control what agents can access

### Why progressive disclosure for configuration?

Matches Polly's core design principle. Most users need Level 1 (pre-configured workflows). Power users doing polymathic work across domains need Level 3–4. The system serves both without overwhelming either.

## Reference

- Personas: [personas spec](../personas/spec.md)
- DRM: [drm spec](../drm/spec.md)
- Security / Capability Broker: [security spec](../security/spec.md)
- RAG: [rag spec](../rag/spec.md)
- Patterns: [patterns spec](../patterns/spec.md)
- Canvas: [canvas spec](../canvas/spec.md)
- Publishing: [publishing spec](../publishing/spec.md)
- Domains: [domains spec](../domains/spec.md)
