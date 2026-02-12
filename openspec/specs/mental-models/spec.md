# Mental Models (OpenSpec)

Source of truth for the mental models system (Phase 14 + refinement). Detail: [docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md](../../../docs/planning/phases/phase-14/PHASE14_MENTAL_MODELS.md).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| MentalModelManager (storage, activation, build_context) | ✅ Implemented | `core/mental_models.py` |
| ContextContributor (priority 60) | ✅ Implemented | _gather_context in polly.py |
| PersonaAware, effectiveness tracking | ✅ Implemented | integration-contracts |
| Refined scoring (exact keywords, threshold, cap) | ✅ Implemented | mental-models-refinement change |
| Per-conversation override modal (fixed UX) | ✅ Implemented | mental-models-refinement change |
| Global default models picker | ✅ Implemented | mental-models-refinement change |
| Page context resolution (chat view) | ✅ Implemented | mental-models-refinement change |
| Constitutional tier (Cui Bono, etc.) | 💭 Vision | constitutional-epistemology change; spec-only |
| Constitutional models always active | 📐 Designed | ethics spec; not yet in code |

## Integration Contracts (Feb 2026)

- **ContextContributor** — `MentalModelManager.build_context(query, domains, persona, mode)` returns the "Active Mental Models (Compressed)" block; `context_priority = 60`.
- **PersonaAware** — `set_active_persona(name, mode)` is called when the user activates or switches persona; `get_models_for_context()` uses the stored persona when persona/mode are not passed explicitly.
- **Effectiveness tracking** — `record_activation(model_ids, signals)` logs which models were active and outcome signals (e.g. `conversation_continued`). `get_effectiveness_summary()` returns log summary for tuning. Polly calls `record_activation()` after each query with the list of activated model IDs.

See [integration-contracts design](../../changes/integration-contracts/design.md).

## Current Behavior

- **Storage:** `~/.polly/mental_models.yaml`. Default models across five tiers (Core Philosophy, Learning, Systems, Communication, Aesthetic & Craft).
- **Activation:** Three-tier scoring — page (+10), persona/mode (+8), category (+5), domain (+3), keyword (+2 per exact match, capped at +6). Models must reach a minimum score of 5 to be included. Top 3–5 models selected per query.
- **Keyword matching:** Exact whole-word equality only (no substring matching). Prevents false positives like "form" matching "information".
- **Score threshold:** `MIN_SCORE_THRESHOLD = 5`. A single keyword match (+2) or lone domain match (+3) is insufficient; models need deliberate contextual signals.
- **Keyword cap:** `MAX_KEYWORD_SCORE = 6`. Prevents keyword flooding from overwhelming page/persona signals.
- **Page resolution:** When the user is in the "chat" view, the effective page is derived from the active conversation's `page_context` field, not the literal view name.
- **Compression:** Compact Format (formerly PIL) ~2.3x compression; injected into system prompt.
- **UI:** Settings tab with full CRUD; template-based creation; per-conversation override (context menu, localStorage) with improved UX; global default models picker (Settings > Mental Models). Visual tag system, animated toggles.
- **Global defaults:** Users can pin specific models as always-active via the "Default Models" picker in Settings > Mental Models. Stored in localStorage as `mm_global_defaults`. When enabled, overrides auto-assignment for all conversations without a per-conversation override.
- **Per-conversation override:** Accessed via conversation context menu. "Use Defaults" toggle clearly hides/shows the model selection list. Entire model rows are clickable to toggle checkboxes. Override modal z-index 10001 (above other overlays).
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
