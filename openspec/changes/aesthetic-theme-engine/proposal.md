# Aesthetic Theme Engine

**Date:** February 2026
**Scope:** Backend + Frontend
**Tier/Phase:** Phase 27b (Artist Mode) under Tier 4 — aligns with Designer Persona (Phase 27)

---

## What We're Doing

Implementing an artist-derived aesthetic theme system that operates on two levels simultaneously:

1. **Surface-level UI presentation** — Colors, typography, textures, spacing, motion, and chrome derived from specific artists' visual practices. Themes map to CSS custom properties for real-time switching.

2. **Deep-level behavioral configuration** — Each theme configures persona defaults (compositional logic, color philosophy, documentation style, voice, emergence tolerance). Switching themes changes how Polly's AI personas think and make decisions, not just how the UI looks.

Seven initial themes derived from the Affinity Suite Techniques Catalogue:

- **Reas** (Casey Reas) — Systems create emergence
- **Fidenza** (Tyler Hobbs) — Probabilistic systems with controlled chaos
- **Ghost Box** (Julian House) — Memory over reference, hauntological aesthetic
- **Martens** (Karel Martens) — Process is content, overprint color
- **Jetset** (Experimental Jetset) — Material awareness, the medium refuses to disappear
- **Riley** (Bridget Riley) — Perception is content, systematic variation
- **Albers** (Anni Albers) — Grid is generative, material leads

Plus a composability system for hybrid theme creation and a cross-domain ripple mechanism where theme choices propagate across all five practice domains.

## Why

Polly's design philosophy centers on "continuation over completion" and "emergence over prescription." The theme system operationalizes these principles: themes are not cosmetic — they are epistemological stances that encode compositional logic, relationship to material, tolerance for ambiguity, and orientation toward emergence versus control. This directly serves Polly's identity as infrastructure for polymathic practice.

The Affinity Suite Techniques Catalogue (38 techniques, 12 artists) provides the source material — concrete, operational design knowledge that translates into both visual and behavioral configuration.

## Dependencies

- **Phase 27 (Designer Persona):** Theme engine is the operational core of Phase 27b (Artist Mode). Can begin independently as configuration system; full integration requires Designer persona.
- **Persona system (Phase 11):** Behavior layer feeds into existing persona prompt construction. Current system supports this — no structural changes needed.
- **UI design system:** Presentation layer maps to CSS custom properties. Extends current Obsidian-inspired aesthetic with switchable alternatives.
- **Settings page:** Theme browser and composition matrix added to Settings.

## Shared Infrastructure

| Component                    | Used By                              |
| ---------------------------- | ------------------------------------ |
| Theme JSON schema + registry | All themes, hybrid composition       |
| CSS custom property mapping  | Electron renderer, all UI components |
| Persona behavior adapter     | All personas, all themes             |
| Composition engine           | Hybrid themes, conflict resolution   |
| Cross-domain ripple          | Persona switching, agent swarms      |
