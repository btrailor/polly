# Persona Mode Invocation — Proposal

**Tier:** 2 (Personas & Learning)  
**Scope:** Backend + Frontend  
**Status:** In progress  
**Created:** February 2026  
**Relates to:** [personas spec](../../specs/personas/spec.md)

---

## What We're Doing

Introducing a unified slash command system so users can invoke specific persona modes from the chat input. With persona mode dropdowns removed, there is no way for users to:

1. **Professor modes** — Distinguish "teach me via dialogue" (Socratic) from "create a curriculum" (Curriculum) from "explain this" (Explain) or "quiz me" (Quiz).
2. **Scribe** — Invoke saving a conversation as a note without pre-selecting Scribe from the persona dropdown.
3. **Architect modes** — Switch between Plan and Build explicitly.

Slash commands (e.g. `/learning-path`, `/teach`, `/save`) give explicit, discoverable invocation. The frontend parses commands before send, and the backend activates the correct persona and mode.

## Why

Users shifted away from selectable persona mode dropdowns for a cleaner UI, but this left mode invocation opaque. Natural-language intent detection alone is unreliable and adds latency. Slash commands are deterministic, familiar (Slack, Discord), and extensible for future personas and modes.

## Scope

### In Scope
- Command registry (persona + mode mapping) in backend
- Extended `persona/process` API to accept optional `persona_mode`
- Polly flow: activate persona, then switch to specified mode when provided
- `GET /persona/commands` (or commands in persona list response) for autocomplete
- Frontend: parse `/command` prefix, strip command, pass persona+mode to API
- Command autocomplete dropdown when user types `/`
- Placeholder hint for discoverability

### Out of Scope
- Intent-based auto-suggestions (future enhancement; spec describes hybrid approach)
- New personas or modes (only invocation mechanism)
- Command palette (Ctrl+K) as separate UI

## Reference

- Plan: `.cursor/plans/persona_mode_invocation_*.plan.md`
- Personas spec: `openspec/specs/personas/spec.md`
