# Mental Models (OpenSpec)

Source of truth for the mental models system (Phase 14). Detail: [docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md).

## Current Behavior

- **Storage:** `~/.polly/mental_models.yaml`. Twelve default models across four tiers (Core Philosophy, Learning, Systems, Communication).
- **Activation:** Three-tier — domain, page, persona. Top 3–5 models per query selected and injected.
- **Compression:** PIL (Polly Internal Language) ~2.3x compression; injected into system prompt.
- **UI:** Settings tab with full CRUD; template-based creation; per-conversation override (context menu, localStorage). Visual tag system, animated toggles.
- **API:** REST CRUD (7 endpoints). Integration in `core/polly.py` and compressor.

## Reference

- [PHASE14_MENTAL_MODELS.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md) — Full spec
- [PHASE14_IMPLEMENTATION_COMPLETE.md](../../../docs/planning/phases/phase-14/PHASE14_IMPLEMENTATION_COMPLETE.md), [PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md)
- [MENTAL_MODELS_USER_GUIDE.md](../../../MENTAL_MODELS_USER_GUIDE.md) (root)
