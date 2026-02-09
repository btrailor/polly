# Personas (OpenSpec)

Source of truth for the agent persona system. Full architecture: [docs/PERSONA_SYSTEM_ARCHITECTURE.md](../../../docs/PERSONA_SYSTEM_ARCHITECTURE.md). API: [docs/PERSONA_API.md](../../../docs/PERSONA_API.md).

## Current Personas

- **Architect** — Plan and Build modes; structured planning and execution. Used for note creation and complex tasks.
- **Scribe** — Research, Write, Refine modes; writing and organization. Skills: template-guide, wiki-linking, domain-structure.
- **Professor** — Teaching, curriculum generation, section enrichment, exercise validation. Used in curriculum (Phase 23) and teaching mode (Phase 22).

## Behavior

- **Lazy-loading:** Persona prompts/skills loaded when activated. User can switch manually; context-aware switching (Scribe/Architect intent detection).
- **Modes:** Each persona has modes (e.g. Architect: plan, build). Activate via API or UI; state persisted.
- **Orchestrator mode (planned):** Toggle for automatic multi-persona collaboration (Phase 24).

## API (Summary)

- `GET /persona/list` — Available personas and modes.
- `POST /persona/activate` — Activate persona (default mode).
- `POST /persona/switch-mode` — Change mode (e.g. teaching mode).
- Persona-specific endpoints for plan/build, note creation, curriculum, etc.

## Scribe Standalone Enrich (Core Framework Refinement)

- **`enrich_standalone(content, title, domain, conversation_history)`** — Direct enrichment method added to `ScribePersona`. Skips Capture/Organize pipeline; used by `KnowledgeWriter` for Scribe-assisted saves. Returns enriched content + metadata.
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Reference

- [docs/PERSONA_SYSTEM_ARCHITECTURE.md](../../../docs/PERSONA_SYSTEM_ARCHITECTURE.md) — Roster, skills, orchestrator design
- [docs/PERSONA_API.md](../../../docs/PERSONA_API.md) — REST API
- [docs/planning/phases/phase-11/](../../../docs/planning/phases/phase-11/) — Phase 11/11c implementation
