# Agent System — Spec Domain

The agent system governs how Polly agents are defined, created, and behave. This includes agent templates (SOUL files), the Standard SOUL Baseline that every agent inherits, team rosters, and the runtime behavioral systems that shape how agents engage.

## Specs in this domain

| File | What it covers | Status |
|------|---------------|--------|
| `agent-templates.md` | All 43 agent SOUL templates, Standard SOUL Baseline (5 blocks incl. Epistemological Commitments), team membership table, Sensibility + manifest schemas | Active — canonical |
| `agent-bootstrap.md` | First-run bootstrap behavior for agents in development | Active |
| `somatic-interface.md` | Prosodic engagement state system — how agents detect and respond to user emotional/physiological state | Active — locked |
| `conversation-architecture.md` | Turn structure, context management, handoff patterns between agents | Active |
| `chorus-mode.md` | Multi-agent simultaneous response mode | Planned |
| `anti-productivity.md` | Anti-productivity / rest-aware agent behavior spec | Planned |

## Key decisions locked

- Standard SOUL Baseline has 5 non-negotiable blocks (was 4). Block 5 = Epistemological Commitments (Layer 7 in prompt injection hierarchy).
- `## Reasoning` section is required in all agent memory writes — feeds Phase 3 conversation history indexing.
- Prosodic Sensitivity section required on every agent SOUL — 4 states (confident/flowing, uncertain/deliberating, emotionally activated, clipped/minimal).
- Agent manifest schema includes `allowed_modes` field governing Knowledge Skill access (search, graph, analogy, dream).
- Sensibility schema includes `structural_rules` field (empty Phase 1, activated Phase 3 via Creative Constraint Engine).

## Cross-domain dependencies

- Agent memory format → Knowledge Skill conversation history adapter (`knowledge/knowledge-skill.md`)
- `allowed_modes` → Knowledge Service tool contracts (`knowledge/service-contracts.md`)
- Prosodic Sensitivity / Somatic Interface → iOS client engagement state detection (`ios-app/ios-spec.md §20`)
- Epistemological Commitments (Layer 7) → Prompt injection hierarchy (`knowledge/service-contracts.md §4`)
