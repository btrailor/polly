# OpenSpec index — Polly

Quick index for project tracking and development workflow.

## Project tracking (source of truth)

| Question                     | Where to look                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Where are we now?            | [specs/project/status.md](specs/project/status.md)                                                                                                                                                                                                                                                                                            |
| What to build next?          | [specs/project/roadmap.md](specs/project/roadmap.md)                                                                                                                                                                                                                                                                                          |
| Active changes (in progress) | [changes/](changes/) — **Architecture Integration** (see below), [core-framework-refinement/](changes/core-framework-refinement/), [knowledge-graph-advanced/](changes/knowledge-graph-advanced/), [ux-pivot-cursor-patterns/](changes/ux-pivot-cursor-patterns/), [phase-17-monaco-code-workspace/](changes/phase-17-monaco-code-workspace/) |
| Completion history           | [../docs/status/CHANGELOG.md](../docs/status/CHANGELOG.md)                                                                                                                                                                                                                                                                                    |

## Specs (current behavior)

| Domain                 | Spec                                                       |
| ---------------------- | ---------------------------------------------------------- |
| Overview               | [specs/overview/spec.md](specs/overview/spec.md)           |
| Project status         | [specs/project/status.md](specs/project/status.md)         |
| Project roadmap        | [specs/project/roadmap.md](specs/project/roadmap.md)       |
| Architecture           | [specs/architecture/spec.md](specs/architecture/spec.md)   |
| Design                 | [specs/design/spec.md](specs/design/spec.md)               |
| UI                     | [specs/ui/spec.md](specs/ui/spec.md)                       |
| Themes                 | [specs/themes/spec.md](specs/themes/spec.md)               |
| RAG & routing          | [specs/rag/spec.md](specs/rag/spec.md)                     |
| Personas               | [specs/personas/spec.md](specs/personas/spec.md)           |
| Domains                | [specs/domains/spec.md](specs/domains/spec.md)             |
| Notes                  | [specs/notes/spec.md](specs/notes/spec.md)                 |
| Curriculum             | [specs/curriculum/spec.md](specs/curriculum/spec.md)       |
| Teaching               | [specs/teaching/spec.md](specs/teaching/spec.md)           |
| Patterns & compression | [specs/patterns/spec.md](specs/patterns/spec.md)           |
| Mental models          | [specs/mental-models/spec.md](specs/mental-models/spec.md) |
| Integrations           | [specs/integrations/spec.md](specs/integrations/spec.md)   |
| Security               | [specs/security/spec.md](specs/security/spec.md)           |

**Full doc → spec map:** [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) (maps all existing docs into OpenSpec)

## Architecture Integration (Priority — Feb 2026)

Comprehensive audit found 10 integration gaps across core systems. Remediation in 4 phases:

| Phase | Change                                                                     | Priority | Effort      |
| ----- | -------------------------------------------------------------------------- | -------- | ----------- |
| Audit | [architecture-integration-audit/](changes/architecture-integration-audit/) | —        | ✅ Complete |
| A.1   | [unified-pattern-engine/](changes/unified-pattern-engine/)                 | P0       | ~2 weeks    |
| A.2   | [entity-model-unification/](changes/entity-model-unification/)             | P0       | ~2 weeks    |
| B     | [integration-contracts/](changes/integration-contracts/)                   | P1       | ~3 weeks    |
| C     | [library-extraction/](changes/library-extraction/)                         | P2       | ~4 weeks    |

A.1 and A.2 can run in parallel. B depends on both. C depends on B.

## Reference (detailed docs, not authority)

- Phase specs and tiers: [../docs/planning/](../docs/planning/)
- Full roadmap text: [../archive/root-docs/MASTER_ROADMAP.md](../archive/root-docs/MASTER_ROADMAP.md) (root [MASTER_ROADMAP.md](../MASTER_ROADMAP.md) is a redirect)
- Long-form status: [../docs/status/CURRENT.md](../docs/status/CURRENT.md)
- Backlog / braindumps: [../archive/root-docs/FEATURES_TO_BUILD.md](../archive/root-docs/FEATURES_TO_BUILD.md), [../archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md](../archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md), [../planning/investigations/](../planning/investigations/), [../archive/](../archive/)

## Workflow

See [README.md](README.md) for OPSX workflow and [.cursorrules](../.cursorrules) for required steps on each change.
