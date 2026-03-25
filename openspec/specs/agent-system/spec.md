# Agent System — Current State

*What is built and running as of Phase 1.*

## Standard SOUL Baseline

Every Polly agent inherits 5 non-negotiable blocks:

1. **Context Management** — session window awareness, handoff behavior
2. **Work Character** — domain-specific defaults (tone, depth, directness)
3. **Tool Use** — how the agent uses tools vs. responds inline
4. **Memory Writes** — writes to `memory/YYYY-MM-DD.md`; 6 required sections including `## Reasoning`
5. **Epistemological Commitments** — Layer 7 (cui bono, material-first, scapegoat suspicion, defamiliarization, second-order honesty). Non-configurable.

## Agent Manifest Schema

```json
{
  "agent": {
    "id": "string — kebab-case",
    "category": "builders | thinkers | creators | operators | specialists | wildcards | system",
    "allowed_modes": ["search", "graph"]
  }
}
```

`allowed_modes` governs Knowledge Skill access. Phase 2 default: `["search", "graph"]`. Phase 3 adds `"analogy"` and `"dream"` per agent selectivity rules.

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
