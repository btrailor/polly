# Teaching & Learning (OpenSpec)

Source of truth for teaching mode and learning tracking (Phase 22). Detail: [docs/planning/phases/phase-22/](../../../docs/planning/phases/phase-22/).

## Current Behavior

- **LearningTracker:** `learners/learning_tracker.py`. Tracks topics, mastery levels (1–5), spaced repetition, learning notes. Storage and API for mode switching and analytics.
- **Professor Socratic mode:** Questioning framework; learning note creation with structured templates. Mode switch via `POST /persona/switch-mode`.
- **Backend:** 100% complete. Frontend: ~40% — mode switcher UI, learning dashboard (topics, mastery, stats), learning note prompts/preview, and visual mode indicators pending. Overall phase ~75% complete; 1–2 days to finish UI.

## Reference

- [PHASE22_TEACHING_MODE.md](../../../docs/planning/phases/phase-22/PHASE22_TEACHING_MODE.md) — Spec
- [PHASE22_STATUS_ASSESSMENT.md](../../../docs/planning/phases/phase-22/PHASE22_STATUS_ASSESSMENT.md) — Implementation assessment
