# Design: UX pivot — Cursor-type patterns

## Cursor-type patterns we're adopting

(Observed from Cursor/Void; we reimplement in Polly.)

| Pattern | Description | Current Polly | Target |
|--------|-------------|---------------|--------|
| **Chat in a sidebar** | Chat lives in a dedicated panel (left or right), not floating only. Thread list above, messages in middle, input at bottom. | Conversations sidebar + floating bar; input can be detached. | Single, consistent chat panel: thread list → messages → input. Optional floating/minimized mode. |
| **Model + context at a glance** | Current model (and optionally persona) visible near the input or in header. No hunting in settings. | Model/persona in selects near chat; can feel buried. | Always-visible model (and persona) chip or dropdown near input; one click to change. |
| **Context pills / @-mentions** | User can attach “context” to the next message: files, symbols, selection. Shown as pills/chips above or beside input. | Little or no structured “context” attachment in chat. | Context pills: e.g. “@file”, “@selection”, “@folder”. Display selected context; send with message. |
| **Single input, multiple modes** | One input bar that can do “chat”, “edit”, “composer” by mode or affordance. Clear and prominent. | Single query input; mode via persona. | One primary input; optional mode toggle (chat vs apply-to-code, etc.) for Code profile. |
| **Threads as first-class list** | Conversation list is a clear list (titles, maybe preview); easy to switch, rename, delete. | Conversation list exists; UX can be tightened. | Clean thread list: title, optional snippet, actions (rename, delete). Keyboard nav. |
| **Dense but scannable layout** | Sidebars and panels are information-dense but organized; icons + labels; minimal chrome. | Already dense; can align to Cursor’s balance. | Reduce clutter where possible; consistent iconography (Lucide); clear hierarchy. |
| **Code-aware when in Code** | In code workspace: chat knows “current file”, “selection”, “workspace”. Shown in UI and sent to backend. | N/A until Code profile exists. | Code profile: current file and selection (and optionally symbols) as attachable context; shown in chat panel. |
| **First-time setup** | Short, clear flow; required vs optional deps; "add keys later"; skip/resume. | Multi-step setup (vault, code paths, install); server/Ollama check. | Adopt Void-style: fewer perceived steps, single place for keys, optional get-started after. See [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md). |
| **Model integration** | Provider-agnostic; API keys in one place; model at point of use; local (Ollama) first-class; optional custom base URL. | Multi-model routing; keys in Settings; model selector in chat. | Same; ensure Settings has "Test" where feasible; model/persona at input (already in pivot). See [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md). |

## How we overhaul current Polly

- **Chat page / default view:** Rework to one main chat panel (sidebar or main area): thread list → message area → input. Model and persona selector right at the input (chip or compact dropdown). Introduce context pills above input (e.g. “@notes”, “@domain” to start; “@file”/“@selection” when Code profile exists).
- **Navigation:** Keep ribbon (Home, Chat, Notes, Patterns, Mental Models, Learning, Settings). Add **Code** when Phase 17 is implemented. Sidebar content stays context-sensitive per page; ensure chat panel pattern is reusable (same component or pattern on Chat and Code).
- **Notes / Learning / other pages:** Reuse the same chat panel pattern where chat is shown (e.g. Learning with Professor). Consistency: same input treatment, same model/persona placement, same context pill behavior where applicable.
- **Settings:** No structural Cursor mimicry; keep settings as a dedicated page. Optionally expose “default model” and “default persona” in a prominent place so the chip/dropdown defaults make sense.
- **Visual polish:** Typography, spacing, and contrast to feel “Cursor-like” (clean, professional). Keep Polly’s design system (Obsidian-inspired, dark) but align component patterns (buttons, inputs, panels) to the reference.

## Out of scope for UX pivot (handled in Code profile plan)

- File tree, editor tabs, terminal, git UI: these are **Code profile** features and are specified in [phase-17-monaco-code-workspace](../../phase-17-monaco-code-workspace/) and its detailed planning doc.
- Inline edits in the editor (e.g. “apply to buffer”): Code profile + chat integration.

## Implementation notes

- **Reuse:** Existing chat backend and persona/model APIs. Changes are renderer-side: layout, components, and how we call existing APIs.
- **New UI pieces:** Context pill component (display + add/remove); optional “attach context” button that opens a picker (files, selection when in Code). Model/persona chip or compact selector component used everywhere chat appears.
- **Phasing:** (1) Chat layout + model/persona at input + thread list polish. (2) Context pills (basic: e.g. domain or note; extended: file/selection in Code profile). (3) Code profile build-out per Phase 17 planning doc.
