# Curriculum (OpenSpec)

Source of truth for the curriculum learning system (Phase 23). Full spec: [docs/planning/phases/phase-23/PHASE23_CURRICULUM_SYSTEM.md](../../../docs/planning/phases/phase-23/PHASE23_CURRICULUM_SYSTEM.md).

## Current Behavior

- **Storage:** `vault/.polly/curricula/` (per curriculum: CURRICULUM.md, curriculum.json, progress.json, resources/). Templates: `vault/.polly/curriculum-templates/`.
- **Templates:** Five domain-based templates (Programming Language, Framework/Library, Skill Acquisition, Problem-Solving, Domain Exploration). 88 sections across 5 templates. Keyword-based template selection.
- **Lifecycle:** Create (from chat or UI) → activate → enrich sections (Professor) → learn (progress, exercises) → complete. Section enrichment: explanations, Mermaid diagrams, code examples, practice exercises, resources; cached.
- **Progress:** Section-level status (not started / in progress / completed). Mastery ratings (1–5 stars). Animated progress bars, completion timestamps. Backend: `learners/curriculum_manager.py`, `curriculum_template_manager.py`.
- **Exercises:** Code editor in UI; run code (sandboxed Python, timeout); “Check solution” with Professor validation. Output console; hints and solution reveal.
- **API:** Create/activate curriculum, start/complete sections, progress, enrichment, exercise run/validate.

## Reference

- [PHASE23_CURRICULUM_SYSTEM.md](../../../docs/planning/phases/phase-23/PHASE23_CURRICULUM_SYSTEM.md) — Full spec
- [PHASE23_QUICK_REFERENCE.md](../../../docs/planning/phases/phase-23/PHASE23_QUICK_REFERENCE.md), [PHASE23_TEST_PLAN.md](../../../docs/planning/phases/phase-23/PHASE23_TEST_PLAN.md)
