# Domains (OpenSpec)

Source of truth for user-definable domain configuration (Phase 1.5). Detail: [docs/planning/phases/phase-1.5/](../../../docs/planning/phases/phase-1.5/), [docs/planning/tiers/TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md).

## Current Behavior

- **Storage:** `~/.polly/domains.json`. User-defined domains (no hardcoded list).
- **Properties (per domain):** name, description, color, icon, folderPath, ragWeight, autoTagRules, etc.
- **Templates:** Six templates (Software Dev, Research, Creative Writing, Personal Knowledge, Academic, Polly Creator). First-run quick-start domains available.
- **API:** CRUD via server; Settings UI for domain management (add, edit, delete).
- **Use:** Patterns, mental models, notes, RAG, and routing are domain-aware. Domain detection and auto-tagging for notes.

## Reference

- [PHASE1.5_DOMAIN_CONFIGURATION.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_DOMAIN_CONFIGURATION.md), [PHASE1.5_MIGRATION_COMPLETE.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_MIGRATION_COMPLETE.md)
- [PHASE1.5_DAY6_COMPLETE.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_DAY6_COMPLETE.md) — First-run wizard, templates
