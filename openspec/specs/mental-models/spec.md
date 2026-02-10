# Mental Models (OpenSpec)

Source of truth for the mental models system (Phase 14). Detail: [docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md).

## Current Behavior

- **Storage:** `~/.polly/mental_models.yaml`. Twelve default models across four tiers (Core Philosophy, Learning, Systems, Communication).
- **Activation:** Three-tier — domain, page, persona. Top 3–5 models per query selected and injected.
- **Compression:** Compact Format (formerly PIL) ~2.3x compression; injected into system prompt.
- **UI:** Settings tab with full CRUD; template-based creation; per-conversation override (context menu, localStorage). Visual tag system, animated toggles.
- **API:** REST CRUD (7 endpoints). Integration in `core/polly.py` and compressor.

## Constitutional Tier (Always Active)

Three models derived from the constitutional epistemology layer. These are non-toggleable — always active, no UI to disable them. They complement the four existing tiers:

| Model | Heuristic | Application |
|-------|-----------|-------------|
| **Cui Bono** | "Who benefits from this framing?" | Applied to political, economic, and social narratives |
| **Historical Construction** | "When was this idea created and what did it serve?" | Applied to claims about group qualities, naturalized hierarchies |
| **Structural Analysis** | "What systems/institutions/policies produce this outcome?" | Applied to social problems, inequality, institutional failure |

These models enhance existing ones:
- **First Principles** gains constitutional weight: decompose social claims to material conditions, not cultural narratives
- **Systems Thinking** gains constitutional weight: trace systemic causes rather than individual/group blame
- **Steelmanning** gains constitutional nuance: steelman the *underlying grievance*, not the scapegoat narrative

See [ethics spec](../ethics/spec.md) for the full constitutional epistemology system.

## Reference

- [PHASE14_MENTAL_MODELS.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md) — Full spec
- [PHASE14_IMPLEMENTATION_COMPLETE.md](../../../docs/planning/phases/phase-14/PHASE14_IMPLEMENTATION_COMPLETE.md), [PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md)
- [MENTAL_MODELS_USER_GUIDE.md](../../../MENTAL_MODELS_USER_GUIDE.md) (root)
