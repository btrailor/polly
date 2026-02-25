# Keyboard Shortcut Discoverability and Fixes

**Date:** February 2026
**Scope:** Frontend
**Priority:** P3 — quality-of-life improvement for power users

---

## What We're Doing

Fixing keyboard shortcut conflicts, adding a discoverable shortcut help panel, and adding tooltips to icon buttons showing associated shortcuts. Currently, keyboard shortcuts exist but are completely invisible to users and have at least one conflict.

## Why

### Existing shortcuts (undiscoverable)

| Shortcut | Action | File/Line |
|----------|--------|-----------|
| `Cmd+B` | Toggle left sidebar | `app.js:2444-2449` |
| `Cmd+B` (in input) | Toggle conversations sidebar (different function!) | `app.js:2676-2679` |
| `Cmd+/` | Toggle right sidebar | `app.js:2452-2455` |
| `Cmd+N` | New conversation | `app.js:2686` |
| `Cmd+L` | Focus search | `app.js:2701` |
| `Cmd+F` | Focus search (chat view only) | `app.js:2702-2706` |
| `Escape` | Close overlays/panels | various |
| `/` | Focus query input (chat view) | `app.js:2709-2714` |

### Problems

1. **Cmd+B conflict:** Fires `toggleLeftSidebar()` normally but `toggleConversationsSidebar()` when an input is focused — two different functions with different behaviors for the same key.
2. **No shortcut help panel:** No way for users to discover available shortcuts. No `Cmd+?` help dialog.
3. **No tooltips:** Icon-only buttons in the ribbon and toolbar show no hint that keyboard shortcuts exist.
4. **Missing shortcuts:** No shortcut for switching between views (e.g., `Cmd+1` through `Cmd+9`), no shortcut for deleting a conversation, no shortcut for saving settings.
5. **`/` key guard:** `app.js:2709-2714` listens for `/` to focus the query input, but doesn't check if a non-input element has focus. Could interfere with other interactions.

## Scope

- **In scope:** (1) Fix Cmd+B conflict. (2) Build a keyboard shortcut help panel (`Cmd+?` or `?`). (3) Add tooltips to ribbon/toolbar buttons with shortcut hints. (4) Add view-switching shortcuts (`Cmd+1` through `Cmd+9`). (5) Guard `/` key to only fire when appropriate.
- **Out of scope:** Customizable keyboard shortcuts (key remapping). Vim/Emacs keybinding modes. CodeMirror editor keybindings (handled by CodeMirror itself).

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/`.
