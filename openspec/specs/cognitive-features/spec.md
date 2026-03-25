# Cognitive Features — Spec Domain

The cognitive features domain covers Phase 3 intelligence systems — capabilities that require the Knowledge Skill's shared index infrastructure to function. None of these ship until Phase 2 (Knowledge Skill) is complete.

## Specs in this domain

| File | What it covers | Status |
|------|---------------|--------|
| `epistemic-immune-system.md` | Detects rhetorical pattern reuse in user's own arguments — flags when reasoning structures from past conversations recur in new contexts. Layer 6 prompt injection. | Planned — blocked on conversation history adapter |
| `metacognitive-dashboard.md` | Tracks mental model usage across conversations. Surfaces patterns. | Planned — blocked on conversation history adapter |
| `creative-constraint-engine.md` | Structural rules for creative work — `structural_rules` field in Sensibility schema. Phase 3 activation. | Planned |
| `tree-of-thoughts.md` | Multi-path reasoning for complex decisions. | Planned |
| `monome-layer.md` | Hardware integration — Monome grid as physical interface for agent state. | Speculative |
| `cl4r1t4s-research.md` | Research notes on Cl4r1t4s project. | Research |

## Phase 3 blocking dependency

All features in this domain that consume Knowledge Skill data are blocked until:
1. Phase 2 Knowledge Skill ships (graph layer, conversation history adapter)
2. The relevant index hooks are registered at startup

See `knowledge/service-contracts.md` — Consumer Dependency Declaration table.

## Key decisions locked

- EIS flags: runtime-injected via `polly.epistemic.flags` gateway config key (Layer 6). Push or request-scoped read TBD pending @backend §4 review.
- `structural_rules` in Sensibility schema: empty at Phase 1, activated Phase 3 via Creative Constraint Engine. Field exists in schema from Phase 1 — no migration needed.
- Metacognitive Dashboard requires `## Reasoning` section in agent memory writes — already mandated in Standard SOUL Baseline.
