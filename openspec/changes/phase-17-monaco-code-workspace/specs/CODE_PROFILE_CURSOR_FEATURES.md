# Code profile: Cursor-like feature set (OpenSpec planning)

**Purpose:** Detailed planning for building the **Code workspace/profile** in Polly so it matches Cursor-like feature sets. This doc is the OpenSpec planning session output: we map Cursor features to our stack (Monaco + Electron + existing chat/RAG), define scope and dependencies, and order implementation.

**Related:** [UX pivot (Cursor-type patterns)](../../../ux-pivot-cursor-patterns/) — app-wide chat/layout/context patterns. The Code profile uses those patterns and adds code-specific features below.

---

## 1. Cursor-like feature set → Polly implementation

| Cursor-style feature | Polly implementation | Phase 17 scope | Backend | Notes |
|----------------------|----------------------|----------------|---------|--------|
| **File tree (left)** | Custom file tree component; data from workspace API | ✅ In scope | `GET /workspace/tree?root=...` | Expand/collapse, icons, git badges (M/U/A) when API ready |
| **Multi-file tabs** | Single Monaco instance; one model per open file; tab bar in renderer | ✅ In scope | `GET/PUT /workspace/file` | Tab state in frontend; load/save via API |
| **Editor (code)** | Same Monaco as Notes (Phase 16); configured for code (syntax, minimap, folding, languages) | ✅ In scope | — | Reuse Phase 16 setup; add language config (Python, JS/TS, etc.) |
| **Chat panel (right/bottom)** | Reuse existing chat; same layout as UX pivot (thread list, messages, input); model/persona at input | ✅ In scope | Existing chat + optional code-context in request | Context pills: @file, @selection; send with message |
| **Context pills (@file, @selection)** | Pills above input; current file + selection attachable; shown in chat request | ✅ In scope | Chat API accepts optional `context: { filePath?, selection? }` | Part of UX pivot + Code; backend may just pass through to prompt |
| **Integrated terminal** | xterm.js in resizable panel; PTY via backend (node-pty) or simple exec | ✅ MVP or post-MVP | WebSocket/stream for PTY; optional for Week 1 | Can stub panel and add later |
| **Git status in tree** | Badges on file tree nodes (M/U/A) from workspace/git API | ✅ In scope (can defer) | `GET /workspace/git/status?root=...` | Optional for first ship |
| **Workspace root** | User picks folder; stored in app/settings; all paths relative to root | ✅ In scope | Root validation; all file/tree/git scoped to root | Folder picker or settings |
| **Apply to code / inline edit** | Chat response can suggest edit; "Apply" writes to buffer or file | 🔶 Follow-up | — | After core Code + chat panel; optional |
| **Composer / multi-file edit** | Cursor-style "composer" that can propose edits across files | 🔶 Later | — | Out of initial Phase 17 |
| **LSP / IntelliSense** | Monaco built-in only (basic); no custom LSP in Phase 17 | ✅ In scope (limit) | — | Document as 80/20: advanced in external IDE |
| **Right-click code actions** | Explain, Find similar, Save as note (Phase 17 vision) | 🔶 After MVP | Existing chat + RAG | After file tree + editor + chat panel |
| **RAG code search** | Semantic search over workspace + notes | 🔶 Later | RAG + workspace | Post-MVP; Phase 17 vision doc has it in Week 2 |
| **Git UI (stage, commit, diff)** | Dedicated Git panel (stage, commit, diff viewer) | 🔶 Post-MVP | Git endpoints | After core editor + terminal; see PHASE17_CODE_WORKSPACE.md |
| **Multi-terminal tabs** | Multiple terminal tabs in bottom panel | 🔶 With terminal | Same PTY/stream | When terminal is implemented |

**Legend:** ✅ In scope for Phase 17 (MVP or explicit); 🔶 Follow-up / post-MVP / optional.

---

## 2. Scope and phasing

### Phase 17 Code profile — must-have (first ship)

1. **Code page and layout** — File tree (left), editor area (tabs + Monaco), chat panel (right or bottom). Resizable panels. Matches UX pivot layout patterns.
2. **Workspace and file APIs** — Tree, read file, write file; workspace root validation.
3. **File tree** — Renders tree; click opens file in editor (tab + Monaco model); optional git badges when API exists.
4. **Monaco code editor** — Reuse Phase 16 Monaco; code languages, tabs, load/save via workspace API.
5. **Chat panel in Code** — Same component/pattern as UX pivot; context pills for current file and selection; send with query.
6. **Context attachment** — Backend accepts (or frontend injects) current file path and selection into prompt when in Code view.

### Phase 17 — nice-to-have / same release if time

- Git status API + badges in file tree.
- Terminal panel (xterm.js + PTY or exec); can be stubbed and shown after.

### Post–Phase 17 (follow-up changes)

- Git operations UI (stage, commit, diff viewer).
- Code actions (Explain, Find similar, Save as note) as right-click or toolbar.
- Apply-to-code / inline edit from chat.
- RAG code search over workspace.
- Composer-style multi-file edits.

---

## 3. Dependencies

- **UX pivot** — Chat layout, model/persona at input, context pills. Code profile reuses these; implement pivot (or at least the shared chat panel + pills) before or in parallel with Code page.
- **Phase 16 (Notes)** — Monaco already integrated; reuse instance/config for code.
- **Backend** — New routes: `/workspace/tree`, `/workspace/file` (GET/PUT), optional `/workspace/git/status`, optional terminal WebSocket/stream. No change to chat or persona APIs beyond optional context payload.
- **Electron** — Code view in renderer; optional folder picker (e.g. `dialog.open` for workspace root).

---

## 4. Implementation order (Code profile)

Align with [../tasks.md](../tasks.md); this refines the “Cursor-like” ordering:

1. **Backend: workspace + file** — Tree and file read/write; root validation.
2. **Backend: git status (optional)** — For tree badges.
3. **Backend: terminal (optional)** — PTY or exec; can defer and stub UI.
4. **Frontend: Code page and layout** — Add Code to nav; layout: tree | editor | chat; resizable; reuse chat panel from UX pivot.
5. **Frontend: file tree** — Call tree API; expand/collapse; open file → new tab + set Monaco model; load content via file API.
6. **Frontend: Monaco code editor** — Tabs, one model per file; load/save via file API; code language config.
7. **Frontend: chat panel + context in Code** — Reuse chat; add @file and @selection pills; include in request.
8. **Frontend: terminal panel (if built)** — xterm.js, connect to backend.
9. **Integration** — Workspace root selection; error handling; docs and OpenSpec updates.

---

## 5. Contracts (recap)

- **Workspace root:** String path; validated; all APIs scoped to it.
- **File tree node:** `{ type: 'file'|'directory', name, path, gitStatus?, children? }`.
- **Editor:** One Monaco instance; one model per open file; tab state in renderer.
- **Chat context (Code):** Optional `{ filePath?, selection?, content? }` sent with chat request so backend or prompt builder can include in prompt.

---

## 6. References

- [Phase 17 proposal](../proposal.md) — Monaco code workspace; no fork.
- [Phase 17 design](../design.md) — Monaco, file tree, terminal, chat panel.
- [Phase 17 tasks](../tasks.md) — Ordered implementation steps.
- [UX pivot: Cursor-type patterns](../../../ux-pivot-cursor-patterns/) — App-wide UX overhaul; Code profile consumes it.
- [PHASE17_CODE_WORKSPACE.md](../../../../docs/planning/phases/other/PHASE17_CODE_WORKSPACE.md) — Full vision and 3-week breakdown.
- [PHASE17_POLLY_CODE_VISION.md](../../../../docs/planning/phases/other/PHASE17_POLLY_CODE_VISION.md) — Long-term code-in-Polly vision.
