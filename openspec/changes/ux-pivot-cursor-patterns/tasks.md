# Tasks: UX pivot — Cursor-type patterns

High-level order. Detailed Code profile tasks stay in [phase-17-monaco-code-workspace/tasks.md](../../phase-17-monaco-code-workspace/tasks.md).

**Status: Substantially complete.** Tasks 1–5 are done (organically, across prior UX changes and this one). Task 6 is deferred to phase-17.

---

## 1. Document and lock the pattern list ✅

- Pattern table finalized in [design.md](design.md).
- Void setup/model patterns documented in [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md).
- Void codebase audit is optional and has not been run; deferred indefinitely (Void fork abandoned).

## 2. Chat layout and thread list ✅

- Implemented as a persistent right-column `#chat-panel` (tab strip + agents sidebar → messages → input). This differs from the original "one panel, thread list on top" plan but achieves the same goal.
- Thread list: conversations grouped under agents in the agents sidebar; tab strip (`#chat-tabs`) shows up to 12 recent conversations with close buttons and a + new tab.
- Rename/delete/star/category available via the `⋮` context menu on each conversation item.
- Keyboard nav: `tabindex="0"` and `Enter`/`Space` activation added to `.agent-conversation-item`; `setupListKeyboardNav` wired to the `.agent-conversations` container.

## 3. Model and persona at input ✅

- Both are small pill-shaped `<select>` dropdowns (`.persona-selector`, `.model-selector`) sitting directly above the textarea in `.chat-controls`.
- Model selector populated with ~27 options (3 Auto tiers + 8 providers × 3 tiers). Persona selector has 4 options (Default, Architect, Scribe, Professor).
- Wired to existing model/persona APIs; no backend change.

## 4. Context pills (basic) ✅

- `ContextPills` module implemented in `app.js`: state management, `add`/`remove`/`clear`/`getContextPayload`.
- Picker dropdown built from current open note (`window.notesManager.currentNote`) and available domains (DOM + sidebar filter).
- Pills rendered as chips above the textarea with remove (×) button and Lucide icon per type.
- Context payload (`{ attached: [{type, label, value}] }`) injected into `queryOptions.context` on every `sendQueryInternal` call; backend already accepts `context: Optional[Dict]` on `PollyQueryRequest`.
- Pills cleared on `switchToConversation` (covers new conversation too).
- Extended context (@file, @selection) deferred to Code profile (Phase 17).

## 5. Visual and hierarchy pass ✅

- Dark, dense Cursor-like layout in place: 48px ribbon, 11–13px fonts, single orange accent, Lucide icons throughout, flat bordered sections.
- All views (Notes, Learning, etc.) share the same persistent `#chat-panel` — no separate per-view chat UI.
- Completed through prior UX change series (ux-css-architecture, ux-consistent-feedback, ux-empty-states, ux-skeleton-loading, etc.).

## 6. Code profile (separate change — deferred)

- Detailed planning: [phase-17-monaco-code-workspace/specs/CODE_PROFILE_CURSOR_FEATURES.md](../phase-17-monaco-code-workspace/specs/CODE_PROFILE_CURSOR_FEATURES.md).
- Implementation: follow [phase-17-monaco-code-workspace/tasks.md](../phase-17-monaco-code-workspace/tasks.md).
- Not started; awaiting phase-17.
