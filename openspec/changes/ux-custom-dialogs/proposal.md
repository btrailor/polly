# Replace Native alert()/confirm() with Custom Styled Dialogs

**Date:** February 2026
**Scope:** Frontend
**Priority:** P0 — affects every user interaction across the entire app

---

## What We're Doing

Eliminating all 90 instances of native `alert()` and 10+ instances of native `confirm()` from the Electron renderer codebase. Replacing them with two purpose-built UI components that match Polly's dark theme and interaction model:

1. **Toast notifications** — for informational, success, warning, and error messages that don't require user input. The `showToast()` system already exists (`app.js:240`) and is well-styled; we just need to use it consistently.

2. **Confirmation dialog** — a new themed modal component for destructive or important actions that require explicit user consent. Supports customizable title, description, confirm/cancel buttons, destructive-action styling, and full keyboard support.

## Why

- Native `alert()` and `confirm()` are visually jarring in an Electron app with a carefully designed dark, monospace aesthetic. They render as OS-level chrome that breaks the immersive experience.
- `alert()` is modal and thread-blocking — it freezes the entire renderer process until dismissed.
- Native dialogs cannot be styled, themed, or extended (e.g., cannot add an "Undo" button to a delete confirmation).
- The app already has `showToast()` with success/error/warning/info support, styled CSS (`.polly-toast` in `main.css:8380-8466`), auto-dismiss, and close buttons — it's simply not used in ~90 places where it should be.
- The inconsistency between native dialogs and themed toasts creates a disjointed experience depending on which feature the user is interacting with.

## Scope

- **In scope:** (1) Build a reusable `ConfirmDialog` component. (2) Replace all `alert()` calls with `showToast()`. (3) Replace all `confirm()` calls with `ConfirmDialog`. (4) Fix the `showToast()` fallback that itself calls `alert()` (`app.js:254`).
- **Out of scope:** Backend changes. New notification types beyond what `showToast()` already supports. Push notifications or OS-level notification center integration.

## Backend vs Frontend

Frontend-only. All changes are in `electron-app/src/renderer/`.

## Current State (Audit)

### alert() instances (90 total)

| File | Count | Worst Offenders |
|------|-------|-----------------|
| `app.js` | ~80 | Settings save (`10358, 10752`), note save to Obsidian (`5867`), mental model validation (`13165-13190` — 6 sequential alerts), sync errors (`11145-11318` — 8 alerts), graph garden ops (`20579-20782` — 7+ alerts) |
| `api-keys-manager.js` | ~5 | Key deletion error (`480`), budget validation (`492`), budget save error (`527`) |
| `notes-manager.js` | ~3 | Note append validation (`2619`) |
| Components | ~2 | Scattered across component files |

### confirm() instances (10+)

| File | Line | Action |
|------|------|--------|
| `app.js` | `2187` | Delete conversation |
| `app.js` | `2776` | Reset all settings |
| `app.js` | `1586` | Delete agent |
| `app.js` | `7217` | Delete curriculum |
| `app.js` | `10265` | Reset all patterns |
| `app.js` | `13300` | Delete mental model |
| `app.js` | `13903` | Delete domain |
| `app.js` | `20695` | Prune weak graph connections |
| `api-keys-manager.js` | `461` | Delete API key |

### showToast() fallback bug

`app.js:254` — When the toast container DOM element is not yet mounted, the fallback logic calls `alert()`, which defeats the purpose. This creates a jarring native dialog during app startup or before the toast container initializes.
