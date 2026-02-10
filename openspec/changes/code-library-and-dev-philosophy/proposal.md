# Code Library & Development Philosophy — Proposal

**Created:** February 2026  
**Scope:** Backend + Frontend + Knowledge Base structure  
**Tier/Phase:** Cross-cutting — touches Tier 1 (patterns, personas), Tier 3 (knowledge platform), Tier 4 (code architecture, plugin ecosystem)

---

## What

Two interconnected systems:

1. **Reusable Code Library** — A living, growing library of reusable code modules that Polly builds as a byproduct of working. Uses the Agent Skills format (SKILL.md + scripts/references/assets). Lives at `_polly/library/` in the user's knowledge base. Organized into patterns, components, prompts, and workflows. Grows through pattern recognition during coding, abstraction extraction, and progressive refinement.

2. **Development Philosophy Configuration** — A guided process for making implicit development decisions explicit. Positions projects along configurable spectrums (open/constrained, friendly/powerful, convention/configuration, local/cloud, build/buy, MVP/architecture). Produces a living `development-philosophy.md` that informs all persona behavior.

## Why

### Code Library
- Polly already has a pattern learning system (Phase 13a) that recognizes recurring structures. The Code Library gives those patterns a **concrete, reusable form** — not just metadata about what happened, but executable modules that can be instantiated in new projects.
- The "instruments over tracks" philosophy means Polly should build ongoing capabilities, not one-off solutions. The library is the instrument Polly plays across projects.
- The Agent Skills format is becoming a cross-platform standard (Claude Code, Codex, Kilo Code, VS Code Copilot). Adopting it means Polly's library modules are portable.
- Multi-model cost optimization: free/budget models handle 50%+ of library operations (extraction, formatting, indexing), reserving frontier models for genuinely hard problems.

### Development Philosophy
- Every project involves implicit decisions about constraint, power, locality, and velocity. Polly should make these explicit rather than imposing hidden defaults.
- The guided process is itself a thinking exercise — the conversation clarifies the user's priorities.
- The philosophy document becomes project-level context for all personas, ensuring consistent behavior.
- The spectrums are extensible (users can add their own) and the philosophy is a living document (Polly prompts for review at milestones).

## Why Now

- The Programmer persona (Phase 25/Tier 4) will be the primary producer and consumer of library modules. Defining the library format and registry now means the Programmer has an instrument to play from day one.
- Pattern learning (Phase 13a, complete) and code pattern extraction already exist. The library is the natural next step — giving those patterns a durable, reusable form.
- The design spec and themes spec establish Polly's aesthetic philosophy. The development philosophy system extends this to the technical dimension — positioning projects on spectrums just as themes position aesthetics.
- Agent Skills compatibility aligns with the Open Polly Tools (Phase 28) vision.

## Scope

### In Scope
- Library directory structure and registry format (`_polly/library/`, `registry.yml`)
- SKILL.md module format (Agent Skills compatible)
- Four module categories: patterns, components, prompts, workflows
- Pattern recognition → extraction → library workflow
- Registry maintenance (usage tracking, provenance, confidence)
- AI Slop review skill (code quality pass)
- Development philosophy guided process (Frame → Position → Generate)
- Spectrum definitions and extensibility
- Philosophy document format and persona integration
- Slash command definitions (library + philosophy)
- Multi-model routing configuration for library operations

### Out of Scope (for now)
- Library sharing/export between users (Tier 5 — needs DRM)
- Pre-built philosophy templates for common project types
- Automated spectrum drift detection
- Full Programmer persona implementation (Phase 25)
- Plugin marketplace integration (Phase 28)

## Impact on Existing Systems

| System | Impact |
|--------|--------|
| **Patterns** (Phase 13a) | Patterns that reach high confidence can be promoted to library modules. New pattern type: `library_usage` tracks which modules are applied where. |
| **Personas** | Each persona gets a defined relationship to the library (producer, consumer, reviewer, indexer, documenter). Philosophy document injected into persona system prompts. |
| **RAG** | Library modules indexed in a `code-library` ChromaDB collection. Library search via RAG for `/library search`. |
| **Design spec** | Expanded with development philosophy as the technical counterpart to aesthetic philosophy. |
| **Architecture** | New subsystem: Code Library (`_polly/library/`). New component: Philosophy Configuration. |
| **Skill system** | Library modules ARE skills. The existing persona skill system (`core/personas/skills/`) and the library converge on the same SKILL.md format. |
| **Agent Swarms** | Nexus can invoke library modules as capabilities. Library extraction could be a swarm workflow. |
| **Config** | New config sections: `library` (paths, auto-extract settings) and `philosophy` (active spectrums, review cadence). |

## Relationship to Existing Specs

- **library/spec.md** — Currently BookLore (ebook library). The Code Library is a separate system. Will create a new `code-library/spec.md` domain spec to avoid confusion. BookLore = reading library. Code Library = reusable code modules.
- **patterns/spec.md** — The Code Library is where high-confidence patterns graduate to. Pattern → Library is a promotion pipeline.
- **personas/spec.md** — Each persona's relationship to the library documented. Philosophy integration defined.
- **design/spec.md** — Expanded with development philosophy spectrums and guided process.

## Reference

- Agent Skills spec: https://agentskills.io
- awesome-cursorrules: Community collection demonstrating appetite for reusable AI coding context
- Kilo Code approach: Multi-model cost optimization, free models for 50%+ of tasks
- promptz.dev taxonomy: Libraries, Prompts, Agents, Powers, Steering, Hooks
- Existing pattern system: [patterns spec](../../specs/patterns/spec.md)
- Existing design philosophy: [design spec](../../specs/design/spec.md)
