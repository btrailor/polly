# Replace setTimeout Race Conditions with Robust Patterns

**Date:** February 2026
**Scope:** Frontend
**Priority:** P3 — reliability improvement; eliminates fragile timing assumptions

---

## What We're Doing

Replacing `setTimeout` calls that are used as workarounds for timing/ordering issues with robust alternatives: `MutationObserver`, `requestAnimationFrame` chains, readiness checks, or proper state machines. These magic-number delays create fragile timing assumptions that work on fast machines but can fail on slower ones or under load.

## Why

Multiple places in the codebase use `setTimeout` with arbitrary delays to work around DOM readiness, rendering timing, or async ordering issues:

| File | Line | Code | Delay | Purpose |
|------|------|------|-------|---------|
| `app.js` | `3095-3099` | `setTimeout(() => { /* init notes */ }, 100)` | 100ms | Wait for notes DOM to be ready after view switch |
| `app.js` | `2375` | `setTimeout(() => lucide.createIcons(), 50)` | 50ms | Re-render icons after DOM change (sidebar toggle) |
| `app.js` | `2391, 2410, 2603+` | Same `lucide.createIcons()` pattern | 50ms | Repeated in multiple locations |
| `app.js` | `5371-5383` | `setTimeout(async () => { /* persona step */ }, 500)` | 500ms | Auto-advance to next persona workflow step |
| `app.js` | `8745-8747` | `setTimeout(() => autoCategorizeConversation(), 200)` | 200ms | Delay auto-categorization after response |

These are symptoms, not solutions:
- The 100ms notes init delay assumes the DOM will be ready in 100ms. On a slow machine or with a complex DOM, it might not be.
- The 50ms Lucide icon delay assumes icons are in the DOM within 50ms of the operation. If the DOM mutation is async or batched, icons won't render.
- The 500ms persona auto-advance is an arbitrary delay with no cancellation mechanism — if the user sends another message within 500ms, the auto-advance might fire on stale state.

## Scope

- **In scope:** (1) Replace DOM-readiness `setTimeout` with `MutationObserver` or `requestAnimationFrame`. (2) Replace icon re-render delays with a post-render callback. (3) Replace persona auto-advance delay with a proper state machine or event-driven trigger. (4) Add cancellation to delayed operations.
- **Out of scope:** Refactoring the entire app architecture. Server-side timing issues. Debounce patterns (covered in `ux-debounce-inputs`).

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/`.
