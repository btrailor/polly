# Undo for Destructive Actions

**Date:** February 2026
**Scope:** Frontend (primary) + Backend (soft-delete support)
**Priority:** P1 — critical safety net; currently zero undo capability anywhere in the app

---

## What We're Doing

Adding undo capability for destructive actions across the app. Instead of permanently executing destructive operations immediately after a `confirm()` dialog, the app will:

1. Execute a **soft-delete** (mark as deleted, hide from UI).
2. Show a **toast with an "Undo" button** that persists for 5 seconds.
3. If the user clicks "Undo," restore the item instantly.
4. If the timeout expires without undo, execute the permanent deletion.

This pattern is well-established (Gmail undo-send, Slack message deletion, macOS Trash) and provides a forgiving, anxiety-free interaction model.

## Why

- Every destructive action in the app is **permanent and immediate** with only a native `confirm()` gate.
- Users lose important conversations, notes, mental models, patterns, domains, curricula, and API keys with no recovery path.
- The conversation database already has a `deleted_at` column for soft deletes (`conversation-manager.js`) — it's just not leveraged for undo.
- The `confirm()` dialog is a weak guardrail: users develop "confirm fatigue" and click through it reflexively, especially for frequent operations like cleaning up old conversations.
- An undo pattern is less disruptive than a confirmation dialog — it allows the action to proceed immediately (no blocking modal) while offering a brief recovery window.

## Scope

- **In scope:** (1) Conversations (delete). (2) Mental models (delete). (3) Patterns (reset all). (4) Curricula (delete). (5) Domains (delete). (6) Agents (delete). (7) API keys (delete).
- **Out of scope:** Notes (auto-save undo is covered in `ux-notes-autosave-safety`). Settings reset (too complex to snapshot/restore — keep confirmation dialog). Graph garden operations (batch operations with complex state).

## Backend vs Frontend

- **Frontend:** All undo logic lives in the renderer — soft-delete, timer management, UI restoration, permanent deletion trigger.
- **Backend:** The conversation manager SQLite schema already supports soft deletes (`deleted_at` column). For other entities (mental models, patterns, domains), the backend delete endpoints can be called on timer expiry instead of immediately. No backend schema changes needed — we delay the permanent API call rather than adding soft-delete columns everywhere.

## Dependencies

- **`ux-custom-dialogs`:** The `ConfirmDialog` component replaces native `confirm()`. Undo can coexist: some actions use ConfirmDialog + Undo (high-risk), others use just Undo (low-risk).
- **`ux-consistent-feedback`:** The enhanced `showToast()` with action buttons is the mechanism for showing the undo option.
