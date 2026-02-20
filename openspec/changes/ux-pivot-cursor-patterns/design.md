# Design: UX pivot — Cursor-type patterns

## Cursor-type patterns we're adopting

(Observed from Cursor/Void; we reimplement in Polly.)

| Pattern | Description | Current Polly | Status / Notes |
|--------|-------------|---------------|----------------|
| **Chat in a sidebar** | Chat lives in a dedicated panel (left or right), not floating only. Thread list above, messages in middle, input at bottom. | Conversations sidebar + floating bar; input can be detached. | **Done.** Persistent right-column `#chat-panel`: tab strip → messages → input. Agents sidebar groups conversations by agent. |
| **Model + context at a glance** | Current model (and optionally persona) visible near the input or in header. No hunting in settings. | Model/persona in selects near chat; can feel buried. | **Done.** Pill-shaped `<select>` dropdowns for model and persona directly above the textarea in `.chat-controls`. |
| **Context pills / @-mentions** | User can attach "context" to the next message: files, symbols, selection. Shown as pills/chips above or beside input. | Little or no structured "context" attachment in chat. | **Done (basic).** `ContextPills` module: note + domain attachment, chip UI, payload sent to backend. @file/@selection deferred to Code profile (Phase 17). |
| **Single input, multiple modes** | One input bar that can do "chat", "edit", "composer" by mode or affordance. Clear and prominent. | Single query input; mode via persona. | **Done.** One persistent input; mode switching via persona selector. Composer/apply-to-code mode deferred to Code profile. |
| **Threads as first-class list** | Conversation list is a clear list (titles, maybe preview); easy to switch, rename, delete. | Conversation list exists; UX can be tightened. | **Done.** Tab strip (12 recent convos) + agents sidebar with full context menu (rename, delete, star, category). Keyboard nav (`tabindex`, `Enter`/`Space`, arrow keys). |
| **Dense but scannable layout** | Sidebars and panels are information-dense but organized; icons + labels; minimal chrome. | Already dense; can align to Cursor's balance. | **Done.** 48px ribbon, 11–13px fonts, single orange accent, Lucide icons, flat bordered sections throughout. |
| **Code-aware when in Code** | In code workspace: chat knows "current file", "selection", "workspace". Shown in UI and sent to backend. | N/A until Code profile exists. | **Deferred to phase-17.** Shell for Code view exists; full implementation in phase-17-monaco-code-workspace. |
| **First-time setup** | Short, clear flow; required vs optional deps; "add keys later"; skip/resume. | Multi-step setup (vault, code paths, install); server/Ollama check. | **Not changed.** Existing setup flow retained; Void-style simplification deferred to Phase 18 (optional). See [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md). |
| **Model integration** | Provider-agnostic; API keys in one place; model at point of use; local (Ollama) first-class; optional custom base URL. | Multi-model routing; keys in Settings; model selector in chat. | **Done (model at input).** Provider-agnostic routing and keys in Settings already in place. "Test connection" deferred. See [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md). |

## What was built (actual implementation)

- **Chat layout:** Persistent right-column `#chat-panel` alongside the main content area. Tab strip at top for recent conversations; agents sidebar groups all conversations by agent. Messages area in center; input at bottom.
- **Navigation:** Vertical ribbon (48px) with Lucide icons — Dashboard, Code, Knowledge, Notes, Graph, Learning, Search, Patterns, Domains, Calendar, Mail, Projects, Settings. Left sidebar is context-sensitive per view.
- **Notes / Learning / other pages:** All share the same `#chat-panel` column — no separate per-view chat. Learning auto-sets persona to Professor and pre-fills a slash command.
- **Settings:** Unchanged structure (14-item nav: General, Routing, API Keys, Providers, Domains, Notes, etc.).
- **Context pills:** `ContextPills` IIFE module in `app.js`. Picker builds options from `window.notesManager.currentNote` and domain selectors in the DOM. Payload merged into `queryOptions.context` on every send. Cleared on conversation switch.
- **Visual polish:** Already Cursor-like from prior UX changes (ux-css-architecture, ux-consistent-feedback, ux-empty-states, ux-skeleton-loading, ux-css-architecture).

## Out of scope for UX pivot (handled in Code profile plan)

- File tree, editor tabs, terminal, git UI: **Code profile** features specified in [phase-17-monaco-code-workspace](../../phase-17-monaco-code-workspace/).
- @file / @selection context pills: Code profile + context pills integration.
- Inline edits in the editor ("apply to buffer"): Code profile + chat integration.

## Implementation notes (as-built)

- **Reuse:** All changes are renderer-side (`app.js`, `index.html`, `main.css`). Existing chat backend and persona/model APIs unchanged.
- **`ContextPills` module:** IIFE in `app.js` near `setupEventListeners`. Public API: `init()`, `add(type, label, value)`, `remove(pillId)`, `clear()`, `getContextPayload()`. Initialized at the end of `setupEventListeners`.
- **Backend context field:** `PollyQueryRequest.context: Optional[Dict]` already existed; no backend change needed.
- **Thread list keyboard nav:** `setupListKeyboardNav` (existing utility) applied to `.agent-conversations` container; items given `tabindex="0"` and `Enter`/`Space` listeners.
