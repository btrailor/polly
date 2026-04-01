# Agent System — Current State

*What is built and running as of Phase 1.*

## Standard SOUL Baseline

Every Polly agent inherits 6 non-negotiable blocks:

1. **Session Startup** — bootstrap from MEMORY.md + SOUL.md; read today's memory
2. **Context Management** — session window awareness, handoff behavior, context flush at ~80 messages
3. **Blockers & Honesty** — report blockers immediately; never struggle silently; never claim certainty you don't have
4. **Memory Writes** — writes to `memory/YYYY-MM-DD.md`; 6 required sections including `## Reasoning`
5. **Epistemological Commitments** — Layer 7 (cui bono, material-first, scapegoat suspicion, defamiliarization, second-order honesty). Non-configurable.
6. **Tool Use** — retrieval decision framework; confidence communication (DIRECT/ADJACENT/ABSENT); vault write-back protocol; group chat coordination signals. Phase 1 variant: web search + workspace only. Phase 2+: Knowledge Skill tools. See `AGENT_BEHAVIOR_CONTRACT.md §3`.

Full behavioral contract (when to use tools, retrieval confidence tiers, autonomy levels, domain boundaries, group speaking rules): `AGENT_BEHAVIOR_CONTRACT.md`  
Full SOUL Baseline text: `POLLY_AGENT_TEMPLATES.md §Standard SOUL Baseline`

## Agent Manifest Schema

```json
{
  "agent": {
    "id": "string — kebab-case",
    "category": "builders | thinkers | creators | operators | specialists | wildcards | system",
    "allowed_modes": ["search", "graph"],
    "autonomy_level": "reactive | proactive | autonomous"
  }
}
```

`allowed_modes` governs Knowledge Skill access. Phase 2 default: `["search", "graph"]`. Phase 3 adds `"analogy"` and `"dream"` per agent selectivity rules.

`autonomy_level`: `"reactive"` (default, 41/43 agents) — responds only when messaged. `"proactive"` — Ops Coordinator + The Scheduler (heartbeat-triggered). `"autonomous"` — Ambient Agent + Janitor (cron-scheduled, read-only, Today View cards only). See `AGENT_BEHAVIOR_CONTRACT.md §4`.

## Sensibility Schema

```json
{
  "sensibility": {
    "aesthetic": {
      "register": "sparse | dense | balanced",
      "vocabulary": "technical | plain | mixed",
      "compression": "float 0.0–1.0"
    },
    "structural": {
      "structural_rules": {
        "mode": null,
        "rules": [],
        "activation": null
      }
    }
  }
}
```

`structural_rules` is empty at Phase 1. Activated Phase 3 via Creative Constraint Engine.

## Prosodic Sensitivity

Every agent SOUL has a `## Prosodic Sensitivity` section covering 4 states: confident/flowing, uncertain/deliberating, emotionally activated, clipped/minimal.

## Agent Roster

43 agents defined in `POLLY_AGENT_TEMPLATES.md`. **33 have full SOUL templates written. 10 are stubs pending full templates** — see `phase-1-agent-system` change tasks.

### Full SOUL Templates Written (33)
- **Builders (6):** Code Architect, Frontend Developer, Backend Architect, QA Engineer, Security Auditor, Infra Engineer
- **Thinkers (9):** Design Engineer, Product Thinker, The Analyst, The Strategist, The Researcher, The Contrarian, The AI Expert, The Systems Thinker, The Futurist
- **Creators (6):** The Writer, The Editor, Narrative Architect, The Cartographer, Audio Producer, Music Producer
- **Operators (3):** Ops Coordinator, The Scheduler, The Generalist
- **Specialists (4):** Legal Thinker, Data Scientist, The Philosopher, The Educator
- **Wildcards (5):** Devil's Advocate, The Mentor, + 3 others

### Stubs Only — Full Templates Pending (10)
Estimator, Librarian, Mirror, Janitor, Interlocutor, Scaffolder, Archivist, Ambient Agent, Experimentalist, Translator

## Team Templates (16 total)

Dev Squad, Startup, Content Studio, Marketing, Life Team, Finance, App Launch, Learning, Home Ops, Research Lab, Decision Theater, Maker's Bench, Maintenance Crew, Signals Studio, Systems Design, Civic Workshop

Source: `POLLY_AGENT_TEMPLATES.md` — Agent → Team Membership table is authoritative.

---

## Ward SOUL Design Principles

*Source: `SPEC_INTEGRATION_BRIEFING.md`. Apply when writing or reviewing any spec that touches agent SOULs, entry point behavior, routing intelligence, or ambient system agents. SHOULD-level constraints (RFC 2119) unless marked MUST.*

### 1. Silence is an active state, not a fallback
List silence as a **first-class behavior with its own trigger conditions**. For routing agents: an agent that says nothing and routes correctly has done its job better than one that confirms aloud. The SOUL should tell the agent *why* silence is appropriate, not just when.

### 2. Character lives in the register, not the content
Express personality through **how** it speaks — concrete analogs over adjective lists. One vivid analog ("the fine dining waiter: present when needed, invisible when not") is worth more than six adjectives.

### 3. Routing agents MUST prioritize invisibility
**MUST: Routing agents MUST NOT narrate their routing decisions. The destination is the response.** Confirmations are almost always noise. One disambiguation question is the maximum before acting. "How can I help?" is prohibited for routing agents.

### 4. Context temperature informs surfacing priority

| Temperature | Definition | Surface priority |
|-------------|-----------|-----------------|
| `waiting` | Last exchange ended with open question | First |
| `mid-task` | Thread interrupted, workflow in progress | Second |
| `clean` | Thread reached natural stopping point | Last / not at all |

Temperature computed by gateway from final exchange patterns and injected as a signal — agents read it, don't compute it.

### 5. Transition moments are a distinct invocation type
Do NOT ask "what would you like to do?" — DO surface the most contextually obvious next move once without pushing. If nothing obvious presents itself, wait. Transition = listening state, not prompting state.

### 6. Memory for routing agents is logistical and observational
Wide but shallow: knows the shape of everything, depth of nothing. Should record: active domains, standing practices, arrival patterns. Should NOT record: conversation content, decisions in other agents' threads.

### 7. Duality in a single agent requires mode detection, not mode selection
**MUST: The user MUST NOT select, configure, or name a mode.** The agent reads its invocation context and determines its own mode in the first step. Gateway delivers different context injection per invocation type.

### 8. The Monome Principle applies to agent behavior, not just UX
The default behavior path should be the shortest and most invisible path. Advanced behavior is triggered by context, not offered proactively. The depth is there — it should not announce itself.
