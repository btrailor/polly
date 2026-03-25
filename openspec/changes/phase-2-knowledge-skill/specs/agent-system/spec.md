# Delta: Agent System — Phase 2

## MODIFIED Requirements

### Requirement: Memory Write Format — Reasoning Section
(Previously: 4-section memory write format)
Agent memory writes MUST include a `## Reasoning` section capturing the inferential structure of the session — what was claimed, what it was based on, and where the uncertainty lies. This section is NOT optional. It feeds Phase 3 conversation history indexing.

Required sections (all 6 mandatory):
1. `## Goal`
2. `## Decisions made`
3. `## Open items`
4. `## Key facts`
5. `## Reasoning`
6. `## Context for continuation`

#### Scenario: Reasoning section populated
- GIVEN an agent writing a session memory summary
- WHEN the agent writes to `memory/YYYY-MM-DD.md`
- THEN the `## Reasoning` section MUST be present
- AND it MUST contain the inferential moves made (claims, basis, uncertainties)
- AND it MUST NOT contain only a restatement of the Decisions Made section

## ADDED Requirements

### Requirement: Epistemological Commitments Block
Every Polly agent SOUL MUST include the Epistemological Commitments block as the 5th non-negotiable baseline block. This block covers: cui bono analysis, material-first reasoning, scapegoat suspicion, defamiliarization, and second-order honesty.

This block operates at Layer 7 of the prompt injection hierarchy and MUST NOT be configurable by users or agents.

Phase 2+: this block moves from static SOUL text to runtime injection via `polly.constitutional.layer` gateway config key. The content does not change.
