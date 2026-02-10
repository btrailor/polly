# BAD Canvas (OpenSpec)

Source of truth for the Business Aware Design canvas system — structured project planning with RAG-powered intelligence.

## Overview

The BAD Canvas is a structured project planning tool within Polly that enforces simultaneous consideration of user needs, competitive landscape, and business viability. It integrates with existing RAG, domains, and personas to provide intelligent gap detection, auto-population from the knowledge base, and cross-canvas pattern recognition.

Canvas is a new page in the Polly UI alongside Chat, Notes, Patterns, Mental Models, Learning, and Settings.

---

## Canvas Data Model

Each canvas contains interconnected zones:

| Zone | Contents |
|---|---|
| **Design Process** | Key users (with confidence level), problems/needs, solutions, requirements |
| **User Analysis** | Target segments, needs hierarchy, pain points, user journey touchpoints |
| **Competitor Analysis** | Competitors (strengths/weaknesses/positioning), UVP, blue ocean factors (eliminate/reduce/raise/create) |
| **Business Model** | Revenue streams, key metrics, discovery-driven planning (assumptions with criticality + validation status) |
| **Iteration Planning** | Scenarios (product/process/business model innovation) with impact analysis across all three domains |

### Confidence Markers

Every field can have a confidence level:
- **Validated:** Backed by evidence or testing.
- **Assumed:** Based on belief, not yet tested.
- **Unknown:** Explicitly marked as a gap.

### Cross-References

Elements in one zone reference elements in other zones:
- Solution → linked user need
- Revenue stream → target customer segment
- UVP → differentiation from stated competitors

### Storage

- SQLite tables in `~/.polly/knowledge.db`: `canvases` (metadata, maturity stage, domains) + `canvas_zones` (zone type, JSON content).
- Maturity stage tracking uses shared maturity system (30-Ideas/20-Active/10-Archive).
- Domain tagging uses existing domain system.

## Zone Customization

BAD's triadic structure (User/Competition/Business) is the default template. Users can define custom canvas zone structures for different workflows:
- Research canvas: Hypothesis / Methodology / Evidence / Publication
- Creative canvas: Concept / Execution / Medium / Audience
- Custom zones with user-defined fields and cross-references

## RAG Integration

### Canvas-Aware Retrieval
When working in a canvas, RAG queries are filtered by canvas domains and relevant zones. Related knowledge from the vault surfaces alongside canvas fields.

### Auto-Population
On canvas creation, search knowledge base for existing content about the project:
- Extract user needs from existing documentation.
- Find competitor mentions.
- Surface past decisions and related project notes.

### Smart Gap Detection
Analyze canvas for incomplete/uncertain areas:
- Fields marked "unknown" or "assumed" → suggest validation actions.
- Orphaned elements (no cross-references) → prompt for connections.
- Missing business model for stated user segments → flag as critical gap.
- RAG searches for existing evidence that could fill gaps.

## Cross-Canvas Intelligence

### Pattern Recognition
Find transferable patterns across canvases:
- Common user segments across projects.
- Successful revenue models from archived canvases.
- Differentiation strategies that worked.

### Dependency Validation
Ensure cross-references make logical sense:
- Every solution addresses a stated user need.
- Every revenue stream targets a user segment.
- UVP actually differentiates from stated competitors.

### Discovery-Driven Planning
Guide users through critical assumption testing:
- Prioritize by criticality and validation status.
- Search knowledge base for existing evidence.
- Suggest test methods for unvalidated critical assumptions.

## UI

### View Modes

- **Full Canvas:** All zones visible with connection lines. Overview of project health.
- **Focus Mode:** Drill into one zone with side-by-side RAG retrieval panel.
- **Gap View:** Surfaces all incomplete/uncertain areas with severity (critical/important/minor) and suggested actions.
- **RAG Assist:** Dedicated panel showing knowledge base results relevant to current zone.

### Obsidian Sync

Canvas data serializes to Obsidian-compatible markdown with `[[wikilinks]]` for cross-references. Canvas structure survives export.

### GitHub Integration

Link canvases to relevant repos. Auto-detect repos by project name. Pull issues/discussions as potential user feedback.

## Persona Integration

### Architect (Canvas-Aware Plan Mode)

When Architect persona is active and user is in a canvas, it shifts behavior:
- Challenge assumptions tactfully.
- Surface gaps and cross-domain dependencies.
- Connect design decisions to business outcomes.
- Reference past successful patterns from other canvases.

This is a mode of the existing Architect persona, not a new persona.

### Scribe for Canvas Content

Scribe's Research/Write/Refine modes apply to canvas content — enriching zone fields with well-structured, wiki-linked content.

### Professor for Onboarding

Canvas creation process could include a guided tutorial (Professor-driven curriculum template) for new users learning the BAD framework.

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **RAG** | Canvas-aware retrieval, auto-population, gap detection via search |
| **Domains** | Canvases are domain-tagged; domain-specific prompting for canvas zones |
| **Notes** | Canvas references notes; notes can link to canvases |
| **Knowledge graph** | Canvas cross-references become graph edges; gap detection uses entity graph |
| **Maturity lifecycle** | Canvases use shared 30-Ideas/20-Active/10-Archive system |
| **Patterns** | Cross-canvas pattern recognition extends pattern learning |
| **Obsidian** | Bidirectional sync of canvas as markdown |
| **GitHub** | Link canvases to repos; extract user needs from issues |

## Implementation Phases

### Canvas Foundation (2–3 weeks)
- Data model (SQLite), CRUD API
- Basic canvas UI with zone editor
- Obsidian markdown sync

### RAG Integration (2–3 weeks)
- Canvas-aware retrieval
- Gap detection algorithms
- Auto-population from knowledge base

### Intelligence Layer (2–3 weeks)
- Cross-canvas pattern recognition
- Dependency validation
- Discovery-driven planning workflow

### Persona Integration (1–2 weeks)
- Architect canvas-aware Plan mode
- Scribe zone enrichment
- Full canvas view modes (Focus, Gap View, RAG Assist)

## Reference

- Existing personas: [personas spec](../personas/spec.md)
- RAG system: [rag spec](../rag/spec.md)
- Domain system: [domains spec](../domains/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)
