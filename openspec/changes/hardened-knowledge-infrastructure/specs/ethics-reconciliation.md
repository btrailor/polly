# Ethics Reconciliation — Hardened Knowledge Infrastructure

## Problem

The original OPSEC-inspired specs proposed "harmful_ideology_detection" as a constitutional check that would **block** content. This contradicts Polly's ethics spec (`openspec/specs/ethics/spec.md`) which explicitly rejects content filtering in favor of epistemological shaping:

> "Antifascism as foundation, not filter. Values encoded as epistemological commitments produce consistently better analysis. Content filters are reactive, brittle, and patronizing."

## Resolution

All constitutional checks in the Content Validator have been reframed from **blocking** to **enrichment**:

| Original Proposal | Polly Implementation | Behavior |
|---|---|---|
| `harmful_ideology_detection` → HARD_BLOCK | `scapegoat_narrative_detection` → ENRICH | Triggers `enrich_with_structural_analysis` (adds cui bono, material causes context) |
| `anti-harmful-ideology scan` → block | `essentialist_claim_detection` → ENRICH | Triggers `enrich_with_material_analysis` (adds historical construction, structural analysis context) |
| `personal_info_detection` → HARD_BLOCK | `pii_detection` → HARD_BLOCK | Unchanged — infrastructure security, not epistemological |
| `fact_contradiction_check` → SOFT_BLOCK | `fact_contradiction_check` → WARNING | Soft warning, allows override |

## Implementation Details

### ContentValidator (core/hardened/validator.py)

The `ContentResult` dataclass includes an `epistemological_enrichment` field that signals to the generation pipeline what additional context to inject:

- `"enrich_with_structural_analysis"` — Add cui bono, material causes, power structure analysis
- `"enrich_with_material_analysis"` — Add historical construction, structural vs essentialist framing

This field is set by `_check_scapegoat_narrative()` and `_check_essentialist_claims()`, which detect structural patterns (not keywords) in retrieved content.

### FailureFactory (core/hardened/failure.py)

The `scapegoat_narrative_detected` and `essentialist_claim_detected` methods produce `FailureReport` objects with:
- `severity = INFO` (not ERROR)
- `user_message = ""` (not shown to user — internal enrichment signal)
- `metadata.action = "enrich_with_structural_analysis"` or `"enrich_with_material_analysis"`

These are informational markers, not blocks.

### Hard Blocks (Infrastructure Security)

Only two checks produce hard blocks:
1. **PII detection** — SSNs, credit cards, API keys in retrieved content
2. **Prompt injection** — Injection attempts embedded in RAG results

These are infrastructure security concerns, not epistemological. They operate at the retrieval layer before any LLM sees the content.

## Alignment with Ethics Spec Principles

1. **Material Analysis over Essentialism** → Essentialist claim detection triggers material analysis enrichment
2. **Cui Bono as Default Heuristic** → Scapegoat narrative detection triggers structural analysis enrichment
3. **Suspicion of Scapegoat Narratives** → Detection adds context rather than blocking

Per the conduct rules: "Never label users or their questions" — the system enriches responses with structural analysis rather than flagging content as harmful.

## Reference

- Ethics spec: `openspec/specs/ethics/spec.md`
- Content Validator: `core/hardened/validator.py` → `ContentValidator._check_scapegoat_narrative()`, `_check_essentialist_claims()`
- Failure Factory: `core/hardened/failure.py` → `FailureFactory.scapegoat_narrative_detected()`, `essentialist_claim_detected()`
