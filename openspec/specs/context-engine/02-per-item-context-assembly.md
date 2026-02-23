# OpenSpec: Per-Item Granularity Context Assembly

**Status:** ✅ Implemented  
**Priority:** P2 — Budget system precision  
**Related:** `core/polly.py:923–1105` (`_gather_context`), `core/context/budget_allocator.py`, `core/context/rolling_context.py`, `core/context/relevance_scorer.py`, `core/mental_models.py`, `core/patterns/engine.py`, `core/memory/retriever.py`  
**Motivation:** The current `_gather_context()` receives one text blob per contributor. The bin-packing and relevance scoring operates at contributor-block granularity, not individual knowledge item granularity. A highly relevant mental model cannot be selected independently from an irrelevant one — they arrive as a package. This undermines the precision of the entire budget and rolling context system.

---

## Problem (Detailed)

### Current flow

```
MentalModelManager.build_context()  →  "## Mental Models\n[3 models concatenated]"  →  ScoredEntry (1 blob)
MemoryRetriever.build_context()     →  "## Relevant Memory\n[5 memories concatenated]"  →  ScoredEntry (1 blob)
PatternEngine.build_context()       →  "## Learned Patterns\n[4 patterns concatenated]"  →  ScoredEntry (1 blob)
EntityContextBuilder.build_context()→  "## Entities\n[6 entities concatenated]"  →  ScoredEntry (1 blob)
```

`_gather_context()` scores and bin-packs these 4 blobs. A low-relevance mental model drags along 2 high-relevance ones. A single irrelevant memory inflates the token cost of the entire memory block. The RollingContext tracks decay at blob granularity — if any key term from the blob appears in a subsequent query, the whole blob is "referenced" and decay resets for all items in it.

### What this loses

- The budget allocator cannot give a high-relevance item from one contributor more space than a lower-relevance item from a different contributor.
- The RollingContext's decay/amplification is noisy — one referenced key term keeps an entire multi-item blob alive.
- The `RelevanceScorer`'s domain affinity, recency, and retrieval similarity scores are computed once for the whole blob and miss per-item variance.
- Items that would score highly in isolation are bundled with low-relevance items and may be evicted together.

---

## Proposed Solution

### Change the ContextContributor protocol

Replace the current single-string return with a `List[ScoredEntry]` return. Every contributor returns individually-scored, individually-sized context items. `_gather_context()` receives a flat pool of items from all contributors and runs a single unified bin-packing pass over them.

### New Protocol Definition

```python
# core/protocols/context_contributor.py (new file or extend existing)

class ContextContributor(Protocol):
    context_priority: int  # Kept for fallback ordering

    def build_context_items(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> List[ScoredEntry]:
        """
        Return individually-scored context items.
        Each item is a ScoredEntry with content, source, raw_score,
        composite_score, token_count, and metadata set.
        """
        ...

    # Backward-compatible shim — default implementation wraps old build_context()
    def build_context(self, query, domains, **kwargs) -> str:
        items = self.build_context_items(query, domains, **kwargs)
        return "\n\n".join(item.content for item in items)
```

The backward-compatible shim means contributors can be migrated one at a time without breaking the system.

---

## Contributor Migration Plan

### 1. `MemoryRetriever` → returns `List[ScoredEntry]` (easiest)

`MemoryRetriever.retrieve()` already returns `List[MemoryEntry]`. The conversion is direct:

```python
def build_context_items(self, query, domains, **kwargs) -> List[ScoredEntry]:
    memories = self.retrieve(query, domains=domains)
    entries = []
    for mem in memories:
        entry = ScoredEntry(
            content=self._format_single_entry(mem),
            source=f"memory:{mem.tier.value}",
            raw_score=mem.score,
            composite_score=0.0,
            token_count=mem.token_count,
            metadata={
                "tier": mem.tier.value,
                "domain": mem.metadata.domain,
                "timestamp": mem.metadata.timestamp,
                "salience": mem.metadata.salience,
            },
        )
        entries.append(entry)
    return entries
```

Each memory item is a separate `ScoredEntry` with its own per-item score, tier metadata, and token count. The RollingContext now tracks decay per memory item — a referenced memory amplifies only itself, not all memories from that session.

### 2. `MentalModelManager` → returns one `ScoredEntry` per activated model

`MentalModelManager` already activates models individually with per-model activation scores. Currently it compresses all activated models into one string. The refactor makes each activated model its own entry:

```python
def build_context_items(self, query, domains, **kwargs) -> List[ScoredEntry]:
    activated = self._activate_models(query, domains, **kwargs)
    entries = []
    for model, activation_score in activated:
        compressed = model.to_compact_format()  # existing compression
        entry = ScoredEntry(
            content=compressed,
            source="mental_model",
            raw_score=activation_score,  # 0-100 activation score
            composite_score=0.0,
            token_count=TokenCounter.count(compressed),
            metadata={
                "model_id": model.id,
                "model_name": model.name,
                "category": model.category,
                "domain": domains[0] if domains else "general",
            },
        )
        entries.append(entry)
    return entries
```

Now a mental model with activation score 85 and one with score 12 are bin-packed independently. The low-score model may be evicted by the budget allocator while the high-score one is always included.

### 3. `PatternEngine` → one `ScoredEntry` per pattern

`PatternEngine.get_patterns_for_prompt()` returns a list of `Pattern` objects. Currently they are formatted and concatenated. The refactor:

```python
def build_context_items(self, query, domains, **kwargs) -> List[ScoredEntry]:
    patterns = self.get_patterns_for_prompt(query, domains)
    entries = []
    for pattern in patterns:
        text = self._format_pattern(pattern)
        entry = ScoredEntry(
            content=text,
            source="pattern",
            raw_score=pattern.confidence,
            composite_score=0.0,
            token_count=TokenCounter.count(text),
            metadata={
                "pattern_id": pattern.id,
                "pattern_type": pattern.pattern_type.value,
                "domain": pattern.domains[0] if pattern.domains else "general",
                "occurrences": pattern.occurrences,
            },
        )
        entries.append(entry)
    return entries
```

### 4. `EntityContextBuilder` → one `ScoredEntry` per entity

Similar approach: each entity is its own entry with its relevance score from the entity store.

### 5. `CompressionManager` → one `ScoredEntry` per compressed conversation segment

The compressed conversation summary is already one item (a single summary string), so this contributor remains a single entry but gains proper per-item scoring.

---

## Changes to `_gather_context()` in `polly.py`

```python
def _gather_context(self, query, domains, persona=None, mode=None,
                    budget_plan=None, retrieval_tier=None, **kwargs) -> str:

    # 1. Collect items from all contributors
    all_items: List[ScoredEntry] = []

    for section, contributor, priority in contributor_specs:
        try:
            # Call new protocol if available; fall back to old build_context
            if hasattr(contributor, "build_context_items"):
                items = contributor.build_context_items(
                    query, domains, persona=persona, mode=mode,
                    token_budget=0,  # no per-contributor budget limit now
                    **call_kw
                )
            else:
                # Legacy fallback: wrap text blob as single ScoredEntry
                text = contributor.build_context(query, domains, **call_kw)
                if text:
                    items = [ScoredEntry(
                        content=text, source=_section_to_source(section),
                        raw_score=priority / 100.0, composite_score=0.0,
                        token_count=TokenCounter.count(text),
                        metadata={"domain": domains[0] if domains else "general"},
                    )]
                else:
                    items = []

            # Apply retrieval tier adjustments per item
            for item in items:
                if retrieval_tier is not None:
                    _apply_retrieval_tier_adjustment(item, retrieval_tier)

            all_items.extend(items)

        except Exception as e:
            logger.debug(f"Context contributor {section} failed: {e}")

    # 2. Score all items through unified RelevanceScorer
    for item in all_items:
        self.relevance_scorer.score(
            item,
            query_domains=domains,
            current_turn=self.rolling_context.turn_count if self.rolling_context else 0,
        )

    # 3. Ingest into RollingContext (per-item dedup and decay tracking)
    if self.rolling_context:
        self.rolling_context.ingest(all_items)

    # 4. If budget system active: bin-pack from RollingContext
    if budget_plan and self.rolling_context:
        section_budgets = {
            name: budget_plan.remaining(name)
            for name in budget_plan.sections
        }
        selected = self.rolling_context.select(section_budgets)
        parts = []
        for section_name, entries in selected.items():
            for entry in entries:
                parts.append(entry.content)
                budget_plan.report_usage(section_name, entry.token_count)
        return "\n\n".join(parts)

    # 5. Fallback: sort by composite score and concatenate
    all_items.sort(key=lambda e: e.composite_score, reverse=True)
    return "\n\n".join(item.content for item in all_items)
```

---

## Changes to `RollingContext`

### Per-item source → section mapping refinement

The existing `_SOURCE_TO_SECTION` map in `rolling_context.py` maps source strings to section budget names. With per-item granularity, each item carries its own source, so the mapping becomes richer:

```python
_SOURCE_TO_SECTION: Dict[str, str] = {
    "memory:stable":   "memory",
    "memory:episodic": "memory",
    "memory:working":  "memory",
    "rag":             "rag",
    "mental_model":    "mental_models",
    "entity":          "entities",
    "pattern":         "entities",
    "compression":     "compression",
}
```

No change needed — already works. The benefit is that individual memory entries from different tiers are now correctly placed in the "memory" section budget and compete individually against each other.

### Decay becomes per-item

With blobs replaced by individual items, a memory entry about "Finite and Infinite Games" that appears in queries decays independently of a memory about "TypeScript configuration". Previously both would have reset decay together if either key term appeared. Now each has its own `reference_count` and `turns_since_reference`.

---

## Migration Strategy

This is a protocol change, not a breaking rewrite. The backward-compatible `build_context()` shim means:

1. Implement `build_context_items()` on `MemoryRetriever` first (easiest).
2. Update `_gather_context()` to call `build_context_items()` when available.
3. Migrate `MentalModelManager`, `PatternEngine`, `EntityContextBuilder` in sequence.
4. Remove shim after all contributors migrated.
5. Remove `_gather_context()`'s blob-wrapping fallback path.

Each migration step is independently testable and independently deployable.

---

## Files Touched

| File | Change |
|------|--------|
| `core/protocols/context_contributor.py` | New — `build_context_items()` protocol + shim |
| `core/memory/retriever.py` | Add `build_context_items()` — convert `MemoryEntry` list to `ScoredEntry` list |
| `core/mental_models.py` | Add `build_context_items()` — one entry per activated model |
| `core/patterns/engine.py` | Add `build_context_items()` — one entry per pattern |
| `core/entities/context.py` | Add `build_context_items()` — one entry per entity |
| `core/compression/manager.py` | Add `build_context_items()` — single entry for compression summary |
| `core/polly.py` | Refactor `_gather_context()` to call `build_context_items()` when available |
| `core/context/rolling_context.py` | No changes required — already handles `List[ScoredEntry]` |

---

## Implementation Notes

### Completed
- `core/memory/retriever.py` — `build_context_items()` added; one `ScoredEntry` per `MemoryEntry` with tier, domain, timestamp, salience metadata
- `core/mental_models.py` — `build_context_items()` added; one `ScoredEntry` per activated model with activation score normalised to 0–1. Added `get_models_for_context_scored()` helper returning `(model, score)` tuples to avoid discarding activation scores.
- `core/patterns/engine.py` — `build_context_items()` added; one `ScoredEntry` per pattern with `confidence` as raw score
- `core/entities/context.py` — `build_context_items()` added; one `ScoredEntry` per entity with `authority` as raw score
- `core/polly.py` — `_gather_context()` refactored: calls `build_context_items()` when available, falls back to legacy `build_context()` blob wrapping. Flat pool of items scored, ingested, and bin-packed individually. Observability metrics now reflect real `items_returned` counts per contributor.

### Not Migrated
- `CompressionManager` — single summary string by nature; kept as single ScoredEntry via legacy fallback path.

---

## Success Criteria

- [x] Each contributor returns `List[ScoredEntry]` with individual scores and token counts
- [x] `_gather_context()` operates on a flat pool of individually-scored items
- [x] RollingContext decay/amplification fires per-item, not per-contributor-blob
- [ ] A low-relevance mental model does not prevent a high-relevance memory from being included when budget is tight (observable via Spec 06 metrics)
- [ ] Budget utilisation improves: less "allocated but unused" space within sections
- [ ] No regression in context quality as measured by response coherence on standard queries
