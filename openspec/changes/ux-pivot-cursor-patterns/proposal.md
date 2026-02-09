# Proposal: UX pivot — Cursor-type patterns across Polly

## What we're doing

Overhaul Polly's current UI so it matches **Cursor-type UX patterns** end-to-end. We are not forking Cursor/Void; we are reimplementing their patterns in Polly's existing stack (Electron, Monaco, current chat and persona system). Polly already uses Monaco (Notes); this pivot is about **how** the app looks and behaves—chat layout, model/persona presentation, context display, navigation—so it feels like a Cursor-style experience while staying 100% in our codebase.

## Why

- **User goal:** A Cursor-like experience (code + chat + context in one place, clear model/persona UI, professional layout).
- **Void fork abandoned:** Cascading TypeScript and build issues made the fork unsustainable. Decision: pivot to Monaco and adopt Cursor as **design reference only** (see [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md)).
- **Scope:** First, define and implement the **UX patterns** across Polly (chat, sidebar, input, context chips, model/persona UI). Then, in a separate detailed plan, build out the **Code profile** (code workspace with file tree, tabs, terminal, in-editor chat) to match Cursor-like feature sets.

## Scope

- **In scope:** (1) Document Cursor-type patterns we're adopting. (2) Overhaul current Polly UI to match: chat placement and layout, conversation/thread UX, model and persona selectors, context pills or inline context, input bar behavior, visual hierarchy. (3) Apply consistently across existing pages (Chat, Notes, Learning, etc.) and prepare the shell for the Code profile. (4) Detailed OpenSpec planning for the **Code profile** (Phase 17) to match Cursor-like feature sets—file tree, tabs, terminal, chat panel in code context—documented in the phase-17 change.
- **Out of scope for this change:** Full Phase 17 implementation (that is a separate build-out); backend RAG/persona logic changes (we're changing presentation, not APIs); Void/fork code.

## Backend vs frontend

Frontend-only for the UX pivot: layout, components, styling, and navigation in `electron-app/`. Backend stays as-is except where we add new endpoints for the Code profile later. The Code profile planning doc will call out backend needs (workspace, file, terminal, git).

## Relationship to Phase 17 (Code profile)

- **This change (UX pivot):** Defines and implements Cursor-type patterns **across Polly** (chat, sidebar, model/persona UI, context). Makes the app feel Cursor-like everywhere.
- **Phase 17 change (Code profile):** Detailed planning and then implementation of the **Code** workspace (Monaco for code, file tree, tabs, terminal, chat panel) to match Cursor-like **feature sets** in the code context. Depends on or aligns with the UX pivot so the Code page uses the same patterns.

## Design reference (no code reuse)

- **Cursor (and Void):** Screenshots, flows, and UX patterns only—layout, chat sidebar, model switcher, context pills, input placement, thread list. Do not use their code.
- **Void first-time setup and model integration:** [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md) — patterns we adopt for setup flow and model/API key UX; includes a Void codebase audit guide for the fork at `~/projects/polly-void`.
- **Current Polly:** [openspec/specs/ui/spec.md](../../specs/ui/spec.md), [docs/planning/phases/phase-0.5/](../../../docs/planning/phases/phase-0.5/).
