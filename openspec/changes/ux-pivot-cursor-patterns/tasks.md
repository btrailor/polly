# Tasks: UX pivot — Cursor-type patterns

High-level order. Detailed Code profile tasks stay in [phase-17-monaco-code-workspace/tasks.md](../../phase-17-monaco-code-workspace/tasks.md).

## 1. Document and lock the pattern list

- Finalize [design.md](design.md) pattern table with any additions.
- Optional: add a one-page “Cursor pattern reference” (screenshots or bullet list) in this change folder for implementers.
- **Void setup and model patterns:** Use [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md) as the spec; optionally run the Void codebase audit (in `~/projects/polly-void`) and add a short “Void findings” section there.

## 2. Chat layout and thread list

- Rework chat UI so one primary panel has: thread list (top) → messages (middle) → input (bottom).
- Ensure thread list is first-class: clear titles, optional preview, rename/delete, keyboard nav.
- If we keep a floating/minimized mode, make it a toggle from this panel rather than the default.

## 3. Model and persona at input

- Add or refactor so model (and persona) are always visible at the input: chip or compact dropdown, one click to change.
- Wire to existing model/persona APIs; no backend change.

## 4. Context pills (basic)

- Design and implement context pill UI: show attached context above or beside input; add/remove.
- First version: attach “domain” or “current note” (for Notes page) or similar; backend can accept context in existing or extended chat request.
- Extended context (@file, @selection) comes with Code profile (Phase 17).

## 5. Visual and hierarchy pass

- Apply Cursor-like density and hierarchy: consistent iconography (Lucide), spacing, and panel styling across Chat, Notes, Learning.
- Reuse the same chat panel component (or pattern) everywhere chat is shown.

## 6. Code profile (separate change)

- Detailed planning: [phase-17-monaco-code-workspace/specs/CODE_PROFILE_CURSOR_FEATURES.md](../phase-17-monaco-code-workspace/specs/CODE_PROFILE_CURSOR_FEATURES.md).
- Implementation: follow [phase-17-monaco-code-workspace/tasks.md](../phase-17-monaco-code-workspace/tasks.md) and the Code profile planning doc. Code page uses the same chat panel and context patterns from this UX pivot.
