# Domains (OpenSpec)

Source of truth for user-definable domain configuration (Phase 1.5). Detail: [docs/planning/phases/phase-1.5/](../../../docs/planning/phases/phase-1.5/), [docs/planning/tiers/TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| DomainEngine, domain_config (YAML) | ✅ Implemented | `core/domains.py`, `core/domain_config.py` |
| Custom domains (load from domain_config) | ✅ Implemented | custom-domains-feature (backend) |
| CRUD API, Settings UI | ✅ Implemented | server + electron-app |
| detect_domains_with_custom, custom in prompts | 📐 Partial | Optional tasks pending; custom-domains-feature |
| Domain-triggered themes, smart routing | 💭 Vision | themes spec, capture spec |

## Current Behavior

- **Storage:** `~/.polly/domains.json`. User-defined domains (no hardcoded list).
- **Properties (per domain):** name, description, color, icon, folderPath, ragWeight, autoTagRules, etc.
- **Templates:** Six templates (Software Dev, Research, Creative Writing, Personal Knowledge, Academic, Polly Creator). First-run quick-start domains available.
- **API:** CRUD via server; Settings UI for domain management (add, edit, delete).
- **Use:** Patterns, mental models, notes, RAG, and routing are domain-aware. Domain detection and auto-tagging for notes.
- **Custom domains:** Domains added in Settings (any id, e.g. `work`, `my-domain`) are stored in `domains.json` and loaded by DomainEngine into `_custom_domains`. They are available for notes, folder organization, and RAG; inclusion in detection and prompts is planned (see [custom-domains-feature](../../changes/custom-domains-feature/design.md)).

## Domain Fluidity Principle

Domains are user-customizable. All features that use domains must work regardless of how the user configures them. The five-domain example (Sigils/Signals/Scrolls/Sights/Glyphs) is one user's configuration — not hardcoded.

Features must be domain-agnostic in implementation, domain-aware in behavior.

## Planned Extensions

### Cross-Domain Features
- **Multi-domain tagging:** Tag entries (notes, captures, canvases) with multiple domains simultaneously.
- **Domain intersection visualization:** Show where work in different domains connects.
- **Cross-domain influence tracking:** Track how work in one domain informs others.
- **Domain-specific capture modes:** Different default capture templates and routing per domain.

### Smart Routing for Captures
- **Content-to-domain classification:** LLM-based analysis to auto-suggest domain for new captures.
- **Custom keyword triggers:** User-defined keywords map to domains (e.g., "Docker" → Sigils, "norns" → Signals). Stored in domain `autoTagRules`.
- **Default domain per capture method:** Configurable (e.g., voice defaults to one domain, code to another).

### Domain Onboarding
- Built-in curriculum template (Professor-driven) teaching new users how to effectively configure and use domains for polymathic practice.

### Domain-Triggered Themes
- **Theme mapping:** Each domain can optionally map to a default aesthetic theme from the Theme Engine.
- **Auto-switch:** When user enters a domain context, theme shifts to the mapped theme (if configured). User can override.
- **Example mappings:** Sigils (code) → Reas, Signals (music) → Frank, Scrolls (writing) → Ghost Box, Sights (visual) → Riley, Glyphs (systems) → Albers.
- **Configurable:** Mappings are user-defined, not hardcoded. Stored in domain configuration.
- See [themes spec](../themes/spec.md) for theme definitions.

## Relationship to Other Systems

| System | Domain Integration |
|---|---|
| **Capture** | Auto-domain detection, keyword triggers, per-method defaults |
| **Notes** | Domain-based folder organization, domain tags |
| **RAG** | Domain-aware search filtering, ragWeight per domain |
| **Routing** | Domain influences model selection (domain-specialized models on DRM) |
| **Knowledge graph** | Entities have domain affiliation; cross-domain connections tracked |
| **Canvas** | Canvases tagged with relevant domains |
| **Patterns** | Domain-specific pattern learning |
| **Mental models** | Domain-based model activation |
| **Analytics** | Per-domain activity metrics, domain balance recommendations |
| **Agent Swarms** | Domain affinity on agents and templates; cross-domain swarm composition |
| **Themes** | Domain-triggered theme switching; per-domain theme mapping (e.g., Sigils → Reas, Signals → Frank). See [themes spec](../themes/spec.md) |
| **DRM** | Domain-specialized models on different nodes |

## Reference

- [PHASE1.5_DOMAIN_CONFIGURATION.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_DOMAIN_CONFIGURATION.md), [PHASE1.5_MIGRATION_COMPLETE.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_MIGRATION_COMPLETE.md)
- [PHASE1.5_DAY6_COMPLETE.md](../../../docs/planning/phases/phase-1.5/PHASE1.5_DAY6_COMPLETE.md) — First-run wizard, templates
- Capture system: [capture spec](../capture/spec.md)
- Analytics: [analytics spec](../analytics/spec.md)
