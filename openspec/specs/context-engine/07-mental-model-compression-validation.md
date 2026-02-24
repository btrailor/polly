# OpenSpec: Mental Model Compression Validation

**Status:** ✅ Implemented  
**Priority:** P7 — Validate or replace Compact Format  
**Related:** `core/mental_models.py`, `core/compression/compressor.py:_compress_mental_model()`, `config/config.yaml:models`  
**Motivation:** The Compact Format uses symbol substitution (`→`, `↻`, `↑`, `⇄`) to reduce mental model token count by ~40–60%. This is elegant but unvalidated. Small local models (qwen2.5:7b) were not trained to interpret these symbols in this semantic context. If Compact Format degrades comprehension for local models, it is actively harmful — spending tokens on noise rather than signal. No A/B comparison mechanism exists.

---

## Problem (Detailed)

### What Compact Format does

In `core/compression/compressor.py`, `_compress_mental_model()` converts full mental model text like:

```
Mental Model: First Principles Thinking
This model guides breaking down complex problems to their fundamental truths 
rather than reasoning by analogy. When faced with a complex challenge, strip 
away all assumptions and rebuild from the ground up.
Principles:
- Identify and question all assumptions
- Decompose to irreducible fundamentals  
- Rebuild from verified foundations
```

Into Compact Format:

```
MM:FirstPrinciples→decompose→fundamentals↻rebuild↑assumption_challenge
```

This saves ~80 tokens but only works correctly if the model reading it:
1. Knows that `→` means "leads to" in this context
2. Knows that `↻` means "iterate/cycle"
3. Knows that `↑` means "elevate/prioritise"
4. Understands chained symbol notation as a conceptual sequence

### The risk

`qwen2.5:7b` (the local model used for `fast` and `balanced` tiers) is a general-purpose model. Its tokenisation and attention may not reliably interpret these symbols as intended. The symbols exist in its training data in many other contexts (mathematical operators, arrows in diagrams, Unicode decorations). There is no published evidence that qwen2.5:7b correctly interprets this specific symbolic notation.

If the model misinterprets or ignores these symbols, the Compact Format wastes those tokens entirely — we get neither the benefit of full text nor accurate symbol interpretation. The current architecture injects these symbols into every query where mental models are active, meaning the risk is not theoretical but per-turn.

Claude/Sonnet models used in `quality` tier were trained on a much richer symbolic reasoning corpus and likely handle this notation correctly — but these are the more expensive routes, not the everyday path.

---

## Proposed Solution

An **A/B validation framework** that:

1. Periodically routes a small percentage of turns through **full-text mental models** instead of Compact Format.
2. Compares response quality between Compact-Format turns and Full-Text turns for the same query type and domain.
3. Uses the Context Quality Observability system (spec-06) to store the comparison data.
4. After sufficient sample size, produces a per-model recommendation: use Compact Format, use Full Text, or use model-specific format.

---

## Architecture

### A/B Mode Configuration

```yaml
# config/config.yaml
mental_models:
  compression:
    format: "compact"          # "compact" | "full" | "ab_test"
    ab_test:
      enabled: true
      sample_rate: 0.15        # 15% of turns use full-text (control group)
      min_samples: 50          # Minimum samples before drawing conclusions
      per_model: true          # Track separately per active model_used
```

### `MentalModelManager` — format selection

```python
def _select_format(self, model_used: str) -> str:
    """
    Determine whether to use compact or full format for this turn.
    
    If ab_test.enabled and random() < ab_test.sample_rate:
        return "full"
    
    If a validated recommendation exists for model_used:
        return recommendation (from stored A/B results)
    
    Otherwise: return configured format default.
    """
    if not self.ab_test_config.get("enabled"):
        return self.config.get("mental_models.compression.format", "compact")

    if random.random() < self.ab_test_config.get("sample_rate", 0.15):
        return "full"

    # Check for validated per-model recommendation
    recommendation = self._load_model_recommendation(model_used)
    if recommendation:
        return recommendation

    return self.config.get("mental_models.compression.format", "compact")
```

### Quality proxy metric

Without user feedback, direct quality comparison is hard. Use two proxy metrics available from the Context Quality Observability system (spec-06):

**1. Response length relative to context size**  
A response that is richer and more on-topic tends to be longer and better structured. Measure `response_length_tokens / total_context_tokens` as a rough signal of context efficiency. If Compact Format turns have significantly lower ratios, the mental model context is not being used effectively.

**2. Mental model term reference rate**  
After the response is generated, check whether the response text references any key terms from the active mental models. For full-text turns, extract terms directly. For Compact-Format turns, use the uncompressed model names and principles as reference terms.

```
mental_model_reference_rate = models_referenced_in_response / models_injected_in_context
```

A higher rate means the model is actually using the mental model context. If Compact-Format turns have a lower reference rate than Full-Text turns for the same model, this is evidence that the compact symbols are not being parsed correctly.

### Storage

Add two fields to `context_turns` (spec-06 table):

```sql
ALTER TABLE context_turns ADD COLUMN mm_format TEXT;           -- "compact" | "full"
ALTER TABLE context_turns ADD COLUMN mm_reference_rate REAL;   -- 0.0–1.0
```

---

## Analysis Pipeline

After `min_samples` turns have accumulated for each format+model_used combination, compute:

```python
def analyse_ab_results(
    model_used: str,
    min_samples: int = 50,
) -> ABResult:
    """
    Query context_turns for compact vs full turns with the same model_used.
    Compute mean and stddev of mm_reference_rate for each group.
    Return recommendation: "compact", "full", or "inconclusive".
    """
    compact_rates = query_reference_rates(model_used, mm_format="compact")
    full_rates    = query_reference_rates(model_used, mm_format="full")

    if len(compact_rates) < min_samples or len(full_rates) < min_samples:
        return ABResult(recommendation="inconclusive", reason="insufficient_samples")

    compact_mean = mean(compact_rates)
    full_mean    = mean(full_rates)
    
    # Require > 10% difference to declare a winner (within noise tolerance)
    if full_mean > compact_mean * 1.10:
        return ABResult(
            recommendation="full",
            reason=f"full_text {full_mean:.3f} > compact {compact_mean:.3f} (+{(full_mean/compact_mean - 1)*100:.0f}%)",
        )
    elif compact_mean > full_mean * 1.05:
        return ABResult(
            recommendation="compact",
            reason=f"compact {compact_mean:.3f} ≥ full_text {full_mean:.3f}",
        )
    else:
        return ABResult(
            recommendation="compact",  # default to compact when equivalent (it saves tokens)
            reason=f"equivalent performance (compact={compact_mean:.3f}, full={full_mean:.3f})",
        )
```

### Automatic format promotion

Once a recommendation is established for a model, store it in `~/.polly/mental_model_format_recommendations.json`:

```json
{
  "qwen2.5:7b": {
    "recommendation": "full",
    "compact_rate": 0.31,
    "full_rate": 0.47,
    "samples": 84,
    "decided_at": "2026-02-23T..."
  },
  "claude-sonnet-4-20250514": {
    "recommendation": "compact",
    "compact_rate": 0.62,
    "full_rate": 0.59,
    "samples": 67,
    "decided_at": "2026-02-23T..."
  }
}
```

The `MentalModelManager` loads this on init and uses it to select format per model without needing the A/B test overhead once decided.

---

## Fallback: Per-Model Format Profiles

If the A/B framework is disabled or has insufficient data, use a **static per-model format profile** as the default:

```yaml
mental_models:
  compression:
    model_format_profiles:
      "qwen2.5:7b": "full"          # Assumed: local models benefit from full text
      "claude-sonnet-4": "compact"   # Assumed: Sonnet handles symbols correctly
      "claude-opus-4": "compact"     # Same
      "gpt-4": "compact"
      "default": "compact"           # fallback for unknown models
```

This static profile reflects the conservative assumption that local small models should receive full-text mental models by default until A/B data suggests otherwise.

---

## Compact Format v2 (Future)

If A/B results show that Compact Format works for large models but not small ones, and if full-text is too token-expensive for small models, a third option is **Compact Format v2** — a structured prose shorthand that avoids symbolic notation but is more compressed than full text:

```
[Mental Model: First Principles]
Break every problem down to its fundamental truths. Question all assumptions. 
Rebuild from verified foundations rather than analogy.
```

This is ~40 tokens vs. ~90 for full-text and ~8 for Compact Format v1. The tradeoff: less compression but more reliably interpreted. This is a future enhancement contingent on A/B results.

---

## Files Touched

| File | Change |
|------|--------|
| `core/mental_models.py` | Add `_select_format()`, A/B sampling logic, `_load_model_recommendation()` |
| `core/compression/compressor.py` | Pass `format` parameter to `_compress_mental_model()` |
| `config/config.yaml` | Add `mental_models.compression` section with A/B config |
| `~/.polly/usage.db` | Add `mm_format`, `mm_reference_rate` columns to `context_turns` |
| `~/.polly/mental_model_format_recommendations.json` | New — auto-generated recommendations file |
| `interfaces/server.py` | Add `GET /api/metrics/mental-models/ab-results` endpoint |

---

## Success Criteria

- [x] A/B framework routes ~15% of turns to full-text format with no user-visible impact
- [x] `mm_reference_rate` is computed and stored for every turn where mental models are active
- [x] After 50+ samples per model, `analyse_ab_results()` produces a recommendation
- [x] Recommendation is persisted and applied automatically on subsequent sessions
- [x] Full-text turns are no more than 200ms slower than Compact-Format turns (format selection overhead negligible)
- [x] Static per-model format profiles apply correctly when A/B is disabled
