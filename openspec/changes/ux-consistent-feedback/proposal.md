# Consistent User Feedback System

**Date:** February 2026
**Scope:** Frontend
**Priority:** P1 — eliminates the most visible inconsistency in the app

---

## What We're Doing

Standardizing all user-facing feedback (success, error, warning, info messages) onto a single system: the existing `showToast()` function. Currently, the app uses four different feedback mechanisms depending on which section of code the user is interacting with, creating a disjointed experience.

## Why

The same type of action — "save settings" — produces completely different feedback depending on which settings panel the user is on:

| Settings Area | Feedback | Mechanism |
|--------------|----------|-----------|
| Main settings | `alert("Settings saved!")` | Native OS dialog (blocking) |
| Routing settings | `alert("Routing settings saved successfully!")` | Native OS dialog (blocking) |
| AI Features | `showToast("AI Features settings saved", "success")` | Themed toast (non-blocking) |
| General | `showToast(...)` | Themed toast |
| Compression | `showToast(...)` | Themed toast |
| Memory | `showToast(...)` | Themed toast |
| Budget | Button text changes to "Saved!" for 2s | Inline text mutation |
| API key | Green checkmark + auto-close | Inline status element |

Additionally, `showNotification()` (used in patterns section, `app.js:10254, 10257, 10291, 10295`) appears to be a separate function from `showToast()`, adding a fifth mechanism.

## Scope

- **In scope:** (1) Audit all feedback paths. (2) Consolidate `showNotification()` into `showToast()` (or verify they are the same). (3) Replace all `alert()`-based feedback with `showToast()` (overlaps with `ux-custom-dialogs` change — this change focuses on the feedback standardization aspect). (4) Replace inline status mutations with `showToast()`. (5) Add loading states to save buttons.
- **Out of scope:** Backend changes. New notification types. Notification center/history panel.

## Backend vs Frontend

Frontend-only. All changes are in `electron-app/src/renderer/`.

## Dependencies

- **`ux-custom-dialogs`:** That change builds the `ConfirmDialog` component and removes `alert()`/`confirm()`. This change complements it by ensuring the remaining feedback mechanisms are also consistent. These two changes can be implemented together or sequentially.
