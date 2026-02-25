# Skeleton Loading States

**Date:** February 2026
**Scope:** Frontend
**Priority:** P2 — perceived performance improvement; reduces layout shift when switching views

---

## What We're Doing

Replacing "Loading..." text strings and blank areas with skeleton placeholder screens that match the final layout dimensions. When users switch between views (Dashboard, Notes, Knowledge, etc.), they will see a shimmer-animated placeholder that morphs into the real content, instead of a text string followed by an abrupt layout change.

## Why

- When switching views, `showView()` (`app.js:3037`) replaces sidebar content with a "Loading..." text message. When the data arrives, the text is replaced by the full content, causing a visible layout shift (jump from single-line text to complex multi-element layout).
- There are **zero skeleton screen implementations** in the codebase — the word "skeleton" appears nowhere.
- Loading states are either plain text ("Loading notes...", "Loading curricula...") or a spinner with text (`<div class="loading"><div class="loading-spinner"></div>Processing...</div>`).
- Skeleton screens are a well-established pattern (used by Facebook, YouTube, GitHub, Notion) that reduce perceived load time by giving users a structural preview of what's coming.

## Scope

- **In scope:** (1) Create a skeleton component library (text blocks, cards, list items, stat cards). (2) Apply to view transitions in `showView()`. (3) Apply to sidebar content loading. (4) Apply to conversation list loading.
- **Out of scope:** Backend performance optimization. Virtual scrolling. Progressive/lazy loading of data.

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/`.
