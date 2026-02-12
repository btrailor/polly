# Mental Models Refinement

## What

Refine the mental models auto-assignment system and override UI so that:
1. Auto-assignment produces genuinely context-relevant models instead of always selecting the same three Core Philosophy models.
2. The per-conversation override modal works correctly (broken checkboxes fixed).
3. Users can manually select mental models via a global default picker.

## Why

Every conversation currently receives the same three models (Infinite Games, Instruments Over Tracks, Constraint as Meaning-Creation) regardless of query content, page, or persona. The root causes are: overly loose substring keyword matching, overly broad activation configs on Core Philosophy models, and a broken page-context signal. Additionally, the override modal's checkboxes are non-functional due to a disabled-by-default UX with no clear affordance, and there is no global manual selection surface.

## Scope

- **Backend** (`core/mental_models.py`): Fix scoring algorithm (keyword matching, score thresholds, keyword caps), narrow default model activation configs.
- **Frontend** (`electron-app/src/renderer/app.js`, `index.html`, `main.css`): Fix page tracking, fix override modal UX, add global default models picker.
- **Specs** (`openspec/specs/mental-models/spec.md`): Update to reflect refined behavior.

## References

- Phase 14 mental models spec
- `openspec/specs/mental-models/spec.md`
