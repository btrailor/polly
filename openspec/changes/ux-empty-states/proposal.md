# Empty States with Calls-to-Action

**Date:** February 2026
**Scope:** Frontend
**Priority:** P2 — reduces confusion and guides users through first-use experiences

---

## What We're Doing

Replacing all minimal text-only empty states across the app with a consistent, informative empty-state component that includes an icon, headline, description, and a primary action button. Adding empty states where none currently exist (e.g., search returning zero results).

## Why

- Current empty states are plain text strings like "No conversations yet" or "No directories selected" with no visual hierarchy, no illustrations, and no guidance for what to do next.
- Some areas have **no empty state at all** — searching conversations that match nothing renders a blank void with zero feedback.
- The "Coming soon" placeholders in the settings sidebar (`app.js:3506-3517`) use inline styles (`style="padding: 16px; color: #808080; font-size: 13px;"`) rather than CSS classes, making them impossible to theme.
- First-time users landing on an empty dashboard, empty knowledge base, or empty patterns list get no onboarding guidance.

## Scope

- **In scope:** (1) Build a reusable `EmptyState` component. (2) Apply to all views that can be empty. (3) Add missing empty states (search no-results, filtered lists). (4) Replace inline-styled "Coming soon" placeholders.
- **Out of scope:** Onboarding wizard redesign (separate concern). Illustrations/artwork (use Lucide icons for now).

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/`.

## Current State Audit

### Existing empty states (text-only)

| View/Area | Location | Current Empty State |
|-----------|----------|-------------------|
| Conversations | `app.js:1404-1414` | `<div class="conversations-empty">` with icon + "No conversations yet" + "Click 'New Chat' to start" |
| Code paths | `app.js:4526` | `'<div class="path-empty">No directories selected</div>'` |
| Settings sidebar stubs | `app.js:3506-3517` | Inline-styled "Calendar navigation coming soon", "Mail folders coming soon", etc. |
| Patterns | `app.js` (patterns view) | "No patterns learned yet" text |
| Curricula | `app.js` (curricula view) | "No curricula created yet" text |
| Notes browse | `notes-manager.js` | "No notes found" text |
| API keys | `api-keys-manager.js` | "No API keys configured" text |

### Missing empty states

| View/Area | When It's Empty | Current Behavior |
|-----------|----------------|-----------------|
| Conversation search (no results) | Search query matches nothing | **Blank area — no feedback at all** |
| Dashboard stats | No data indexed yet | Shows "0" values — technically correct but no guidance |
| Knowledge base | No sources indexed | Shows empty source list |
| Graph visualization | No entities | Empty canvas |
| Mental models | No custom models | Falls through to defaults (partially handled) |
| Domains (custom) | No custom domains | Empty list |
| Learning tracker | No tracked topics | Empty list |
