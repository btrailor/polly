# Custom Domains Feature — Proposal

**Created:** February 2026  
**Status:** In progress  
**Scope:** Frontend (Settings) + Backend (DomainEngine)

---

## What we're doing

Make **custom domains** (user-added domains beyond the five built-in: Sigils, Signals, Scrolls, Glyphs, Grids) a first-class feature: users can add, edit, reorder, and delete domains in Settings, and the backend uses them everywhere domains are used (detection, RAG, notes, patterns, etc.).

## Why

- **Domains spec** states: "Domains are user-customizable. All features that use domains must work regardless of how the user configures them."
- **Phase 1.5** added `~/.polly/domains.json` and Settings UI for domain CRUD, but DomainEngine currently **ignores** any domain whose id is not in the `DomainType` enum (sigils, signals, scrolls, glyphs, grids). So "Add domain" in the UI saves to JSON but those domains are never used by detection/RAG/prompts.
- **Integration-contracts (Task 12)** added YAML domain config and `_custom_domains` for YAML-loaded custom domains; we should align the **domains.json** path so UI-added domains are also loaded into the engine.

## Scope

| Area | In scope | Out of scope (later) |
|------|----------|----------------------|
| Backend | Load domains.json custom ids into DomainEngine (`_custom_domains`); use them in detection/scoring | RAG collection per custom domain; theme mapping |
| Frontend | Keep existing Settings domain CRUD; clarify "Add domain" = custom; optional: show ID, prevent overwriting built-in ids | First-run wizard changes; domain templates for custom |
| Single source of truth | `~/.polly/domains.json` (API + UI). Config YAML `domains:` remains optional override. | Merging YAML + JSON in one view |

## Success

- User adds a domain "Work" in Settings → it is saved to domains.json.
- On next query (or app reload), DomainEngine loads that domain into `_custom_domains` and uses it (e.g. in detection if we extend scoring).
- User can edit/delete/reorder custom domains; built-in five can still be edited (name, keywords, etc.) but not deleted.

## Dependencies

- Existing: Phase 1.5 domain_config, GET/POST/PUT/DELETE `/polly/domains/*`, Settings domains tab.
- Recent: Integration-contracts Task 12 (DomainConfig, YAML, `_custom_domains`).

## Optional direction: pure user-defined domains

If we move away from built-in domains entirely (no required "five"), see **[pure-user-defined-domains.md](pure-user-defined-domains.md)** for a design exploration: single store by string id, no `DomainType` enum in the API, first-run template choice (Polly Five / Quick Start / Empty), and rough effort.

## Reference

- [domains spec](../../specs/domains/spec.md)
- [integration-contracts tasks](../integration-contracts/tasks.md) Task 12
- [PHASE1.5_DOMAIN_CONFIGURATION.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_DOMAIN_CONFIGURATION.md)
