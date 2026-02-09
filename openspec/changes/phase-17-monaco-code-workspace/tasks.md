# Tasks: Phase 17 – Monaco code workspace

Ordered implementation steps. Backend contract first so frontend can rely on it.

## 1. Backend: workspace and file APIs

- Add `GET /workspace/tree?root=...` (list directory tree; optional git status).
- Add `GET /workspace/file?path=...` (read file; path within root).
- Add `PUT /workspace/file` (write file; path within root).
- Validate workspace root and path (no escape outside root).
- Document in server or OpenAPI if present.

## 2. Backend: git status (optional for MVP)

- Add `GET /workspace/git/status?root=...` (porcelain or equivalent).
- Use for file tree badges (M/U/A); can defer to post-MVP if needed.

## 3. Backend: terminal (optional for MVP)

- Decide: PTY (node-pty) vs simple exec. If PTY: add WebSocket or stream endpoint for terminal session.
- If deferred: stub or hide terminal panel in UI until implemented.

## 4. Frontend: Code page and layout

- Add Code view to ribbon/sidebar (if not already).
- Layout: file tree (left), editor area (center, tabs + Monaco), chat panel (right or bottom), optional terminal (bottom).
- Resizable panels; persist sizes in electron-store if desired.

## 5. Frontend: file tree

- Component that calls `GET /workspace/tree` for selected root.
- Render tree with expand/collapse; file click opens file in editor (create tab + set Monaco model).
- Show git status on nodes when API available.

## 6. Frontend: Monaco code editor

- Reuse Monaco from Phase 16; configure for code (languages, theme, options).
- Tab bar: one tab per open file; switch model on tab change; close tab.
- Load content via `GET /workspace/file`; save via `PUT /workspace/file` (e.g. on blur or Cmd+S).

## 7. Frontend: chat panel in Code view

- Reuse existing chat (conversations, persona/model selects, send).
- Optional: add “code context” (current file path, selection) as pills or auto-include in prompt.
- Style/layout inspired by Cursor/Void (design reference only).

## 8. Frontend: terminal panel (if implemented)

- Embed xterm.js; connect to backend PTY or exec stream.
- Tabs for multiple terminals; basic commands (clear, etc.).

## 9. Integration and polish

- Wire workspace root selection (e.g. folder picker or settings).
- Error handling (invalid path, save failures, terminal disconnect).
- Update openspec/specs (e.g. specs/ui, specs/notes or new specs/code-workspace) and status/roadmap when done.

## Chat UI refresh (design reference)

- Treat as incremental: improve existing chat layout/controls to better match Cursor/Void patterns (e.g. context chips, model/persona visibility). Can be same change or a follow-up; no fork code.
