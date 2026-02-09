# Design: Phase 17 – Monaco code workspace

## Approach

- **Monaco editor:** Reuse the same Monaco setup as Phase 16 (Notes). Configure for code: syntax (Python, JS/TS, C/C++, C#, Lua, Rust, Go), minimap, folding, bracket colorization, multi-cursor, find/replace. No new editor dependency.
- **Custom shell:** Build in Polly's Electron renderer: file tree (left), editor area (tabs + Monaco), optional terminal (bottom), chat panel (right or bottom). Match Polly's existing layout patterns (ribbon, sidebar, main content); Code page becomes a dedicated workspace view.
- **File tree:** Custom component. Data from backend: list dir, git status (porcelain). Icons by type; expand/collapse; open file → set Monaco model and tab.
- **Terminal:** xterm.js in a resizable panel. Backend: optional PTY (node-pty) or proxy to local shell; start with simple exec/shell adapter if needed. Tabs for multiple terminals.
- **Chat panel:** Reuse existing chat stack (conversations, persona/model selects, send). Optionally add “code context” pills (current file, selection) that get sent with the query. Layout and styling can mirror Cursor/Void patterns (design reference only).
- **APIs (backend):** File tree: `GET /workspace/tree?root=...`, `GET /workspace/file?path=...`, `PUT /workspace/file` (save). Terminal: WebSocket or long-poll for PTY. Git: `GET /workspace/git/status?root=...`, optional diff endpoints. All scoped to a workspace root (e.g. user-selected folder).

## Impact on existing code

- **electron-app:** New Code page/view; new components: file tree, code editor wrapper (Monaco), terminal panel, chat panel (or reuse existing chat component with a “code context” mode). Navigation: add Code to ribbon/sidebar if not already.
- **interfaces/server.py:** New routes under `/workspace/` and terminal/PTY handling. No changes to existing chat or persona endpoints.
- **core:** Optional small helpers for workspace root validation and safe path handling; no change to RAG or personas for this phase.

## Key types / contracts

- Workspace root: string path (validated, inside user-allowed dirs).
- File tree node: `{ type: 'file'|'directory', name, path, gitStatus?, children? }`.
- Editor: one Monaco instance; model per open file; tab state in renderer.

## Design reference (no code reuse)

- Cursor/Void: chat sidebar layout, model/persona selector placement, context chips, terminal position.
- [specs/CODE_PROFILE_CURSOR_FEATURES.md](specs/CODE_PROFILE_CURSOR_FEATURES.md): Cursor-like feature set → Polly implementation map, scope, and implementation order.
- [PHASE17_CODE_WORKSPACE.md](../../../docs/planning/phases/other/PHASE17_CODE_WORKSPACE.md): UI wireframes, 80/20 philosophy, Week 1–3 breakdown.
