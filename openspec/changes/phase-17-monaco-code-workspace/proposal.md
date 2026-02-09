# Proposal: Phase 17 – Monaco code workspace

## What we're doing

Implement Phase 17 (Integrated Code Workspace) using **Monaco + custom shell** in Polly's existing Electron app. No VSCode/Void fork. This aligns with the documented architecture in [PHASE17_POLLY_CODE_VISION.md](../../../docs/planning/phases/other/PHASE17_POLLY_CODE_VISION.md) and [PHASE17_CODE_WORKSPACE.md](../../../docs/planning/phases/other/PHASE17_CODE_WORKSPACE.md).

## Why

- **Cursor-like UI goal:** We want Cursor-like code UI and a stronger chat experience. The vision doc and Phase 17 spec already choose Monaco over a fork: full control for RAG/personas, no 160k-line upstream, same stack as current Polly (Electron + Monaco in Notes).
- **Void fork:** We explored a Void/VSCodium fork for faster time-to-feature; the build hit many TypeScript/compile issues. Decision: either fix Void with a bounded config-only audit (see [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md)) or pivot to this path. This change is the **Monaco path**; Void/Cursor are **design reference only** (screenshots, flows, UX patterns).

## Scope

- **In scope:** Code workspace in Polly: Monaco editor for code, file tree with git status, multi-file tabs, integrated terminal (xterm.js), git operations UI, chat panel in the same window. Backend: file/terminal/git APIs as needed. UI patterns inspired by Cursor/Void where useful (layout, model/persona chips, context display)—reimplemented in our stack, not forked.
- **Out of scope (later phases):** Full LSP/IntelliSense beyond Monaco built-in, Designer persona, extension marketplace. Chat UX improvements are part of this change only as “design reference” and small, incremental upgrades; a larger chat overhaul can be a follow-up change.

## Backend vs frontend

Both: new server endpoints for file tree, file read/write, terminal lifecycle, git status/diff; Electron renderer for Code page (file tree, editor, terminal, chat panel). Existing chat and persona APIs stay; we add code-context and workspace APIs.

## Tier/phase

Phase 17 (Code Workspace). Prerequisites: Phase 1.5, 2, 11, 16 (domains, RAG, multi-model, notes). See [openspec/specs/project/roadmap.md](../../specs/project/roadmap.md).

## Design reference

- **Void / Cursor:** Use for UX patterns only (chat layout, model switcher, context pills, sidebar layout). Do not fork or reuse their code.
- **UX pivot:** App-wide Cursor-type patterns (chat panel, model/persona at input, context pills) are specified in [ux-pivot-cursor-patterns](../../ux-pivot-cursor-patterns/). The Code profile uses those patterns and adds code-specific features.
- **Code profile planning:** Detailed mapping of Cursor-like feature sets to Polly/Monaco implementation, scope, and implementation order: [specs/CODE_PROFILE_CURSOR_FEATURES.md](specs/CODE_PROFILE_CURSOR_FEATURES.md).
- **Specs:** [PHASE17_CODE_WORKSPACE.md](../../../docs/planning/phases/other/PHASE17_CODE_WORKSPACE.md) (3-week breakdown), [PHASE17_POLLY_CODE_VISION.md](../../../docs/planning/phases/other/PHASE17_POLLY_CODE_VISION.md) (long-term vision).
