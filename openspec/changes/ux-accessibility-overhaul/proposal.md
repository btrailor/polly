# Accessibility Overhaul

**Date:** February 2026
**Scope:** Frontend
**Priority:** P1 — foundational quality; affects usability for keyboard users and assistive technology

---

## What We're Doing

Bringing the Electron app's renderer up to WCAG 2.1 AA baseline for keyboard navigation, focus management, ARIA semantics, color contrast, and motion sensitivity. The current state is critically under-served:

- **8 ARIA attributes** across 21,000+ lines of JavaScript
- **2 ARIA attributes** in the entire `index.html` (3,100+ lines)
- **0 `role` attributes** in HTML (except 1 `role="switch"`)
- **0 `tabindex` attributes** anywhere
- **26 instances of `outline: none`** systematically removing focus indicators
- **0 `prefers-reduced-motion`** media queries — all animations play unconditionally
- **0 `:focus-visible`** selectors — no distinction between mouse and keyboard focus
- Color contrast failures: `--text-muted: #606060` on `--bg-primary: #1e1e1e` = ~2.7:1 ratio (fails WCAG AA)

## Why

- Electron apps are web apps — they inherit the web's accessibility capabilities but only if used. Currently, Polly is nearly invisible to screen readers and difficult to use with keyboard-only navigation.
- macOS VoiceOver users would encounter unlabeled buttons, unannounced dynamic content, and no logical document structure.
- Keyboard-only users cannot navigate the ribbon, sidebar items, or conversation list without mouse clicks.
- Users with motion sensitivity or vestibular disorders have no way to disable glitch effects, toast slide animations, or spinner animations.
- Even for sighted mouse users, the stripped focus indicators (`outline: none` × 26) make it impossible to track keyboard position when occasionally using Tab.

## Scope

- **In scope:** (1) ARIA roles and labels on all interactive elements. (2) Focus indicators and `:focus-visible` styles. (3) Focus trapping in modals. (4) `aria-live` regions for dynamic content. (5) Keyboard navigation for lists and menus. (6) `prefers-reduced-motion` support. (7) Color contrast fixes. (8) Skip-to-content link.
- **Out of scope:** Full WCAG AAA compliance. Screen reader optimization for the CodeMirror editor (CodeMirror 6 has its own accessibility layer). Internationalization (i18n).

## Backend vs Frontend

Frontend-only. All changes are in `electron-app/src/renderer/` (HTML, CSS, JS).

## Current State Audit

### Focus Indicators

| File | Issue |
|------|-------|
| `main.css` | 26 instances of `outline: none` across buttons, inputs, textareas, selects, sidebar items |
| `main.css` | `:focus` styles exist for inputs (change border-color) but no `:focus-visible` anywhere |
| `notes.css` | Additional `outline: none` on note list items |
| `persona-ui.css` | `outline: none` on persona buttons |
| Exception | `.toggle-switch:focus` has a proper focus ring — only good example |

### ARIA and Semantic HTML

| Area | Current | Gap |
|------|---------|-----|
| Navigation ribbon | `<div>` + `<button>` | No `role="navigation"`, no `aria-label`, no `aria-current` |
| Left sidebar | `<div>` sections | No `role="complementary"`, no heading hierarchy |
| Main content | `<div class="main-content">` | No `role="main"`, no `<main>` element |
| Chat messages | `<div>` list | No `role="log"`, no `aria-live` |
| Toast notifications | `<div>` | No `aria-live="polite"`, no `role="status"` |
| Modals | `<div>` overlays | No `role="dialog"`, no `aria-modal`, no focus trap |
| Icon buttons | `<button>` with icon only | No `aria-label` (except 3 instances) |
| Conversation list | `<div>` items | No `role="listbox"` or `role="list"` |

### Color Contrast

| Token | Hex | Background | Ratio | WCAG AA |
|-------|-----|-----------|-------|---------|
| `--text-muted` | `#606060` | `#1e1e1e` | ~2.7:1 | FAIL |
| `--text-secondary` | `#808080` | `#1e1e1e` | ~4.0:1 | PASS for large text, FAIL for small text (11px-13px) |
| `--text-primary` | `#e0e0e0` | `#1e1e1e` | ~12.3:1 | PASS |
| `--accent-primary` | `#f0903b` | `#1e1e1e` | ~4.8:1 | PASS (barely) |

### Motion

Animations with no reduced-motion alternative:
- Glitch effects (`glitch-effects.css`): `@keyframes glitch`, `glitch-box`, `glitch-glow`, `scan-line`, `glitch-clip`
- Toast slide-in/out (`main.css:8446-8465`): `@keyframes slideUp`
- Loading spinner (`main.css`): `@keyframes spin`
- Panel expand (`main.css`): `@keyframes expandPanel`
- Pulse effects: `@keyframes pulse`
