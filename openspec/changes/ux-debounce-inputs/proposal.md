# Debounce Search and Input Operations

**Date:** February 2026
**Scope:** Frontend
**Priority:** P2 — performance improvement; prevents unnecessary DOM re-renders on every keystroke

---

## What We're Doing

Adding debounce to all input-driven filtering and search operations across the app. Currently, most search inputs trigger full DOM re-renders on every keystroke with no throttling. As data grows (hundreds of conversations, notes, patterns), this causes noticeable jank.

## Why

- Conversation search (`app.js:2611`) fires `searchConversations()` on every `input` event with zero debounce. Each call runs `renderConversationList()` which rebuilds the entire conversation list DOM — filtering, sorting, grouping, and re-rendering all elements.
- The garden entity search correctly uses a 300ms debounce (`app.js:20826`) — proving the pattern is known but inconsistently applied.
- For a user with 100+ conversations, typing a 5-character search term causes 5 full list re-renders in rapid succession.
- Debounce is a standard UX practice for search inputs — it waits until the user pauses typing before executing the search, reducing work by 60-80%.

## Scope

- **In scope:** (1) Extract a reusable `debounce()` utility. (2) Apply to conversation search. (3) Apply to notes search/filter. (4) Apply to any other input-driven filtering (patterns, mental models, etc.). (5) Apply to auto-save triggers.
- **Out of scope:** Backend search API optimization. Full-text search implementation. Virtual scrolling for large lists (separate concern).

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/`.

## Current State

| Input | File | Line | Debounce | Behavior |
|-------|------|------|----------|----------|
| Conversation search | `app.js` | `2611` | None | Re-renders full list on every keystroke |
| Conversation search (duplicate) | `app.js` | `4116` | None | Same handler registered twice |
| Garden entity search | `app.js` | `20821-20826` | 300ms | Uses `clearTimeout`/`setTimeout` pattern — correct |
| Notes auto-save | `notes-manager.js` | `39` | 2000ms | Uses `autoSaveDelay` — correct but could use standard utility |
| Notes search (if exists) | `notes-manager.js` | varies | Unknown | Needs audit |
| Wiki-link autocomplete | `notes-manager.js` | `48` | Unknown | Needs audit |
