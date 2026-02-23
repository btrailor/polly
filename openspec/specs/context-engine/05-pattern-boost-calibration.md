# OpenSpec: Pattern Boost Calibration & Negative Patterns

**Status:** 💭 Planned  
**Priority:** P5 — Better retrieval learning  
**Related:** `core/rag.py:961–992` (chunk boosting), `core/patterns/engine.py`, `core/patterns/models.py:QueryChunkPattern`  
**Motivation:** The `QueryChunkPattern` boost range of 1.1–1.5x is too conservative to meaningfully affect ranking against raw cosine similarity scores. A chunk confirmed useful 10+ times for a query type should be boosted far more aggressively. Additionally, there is no mechanism to penalise chunks that are consistently retrieved but never referenced in responses — these are false positives that waste context budget.

---

## Problem (Detailed)

### Boost range too conservative

In `core/rag.py:974–976`:

```python
# Boost factor: 1.1 to 1.5 based on hit count
boost = min(1.0 + (sc.get("hit_count", 1) * 0.05), 1.5)
```

A chunk confirmed useful 8 times receives a boost of `1.0 + (8 * 0.05) = 1.4x`. A competing chunk with raw cosine similarity 0.85 vs. the boosted chunk's 0.70 would produce final scores of:

- Learned chunk: `0.70 * 1.4 = 0.98`
- Unlearned chunk: `0.85 * 1.0 = 0.85`

This works. But a chunk confirmed useful only 2 times receives `1.0 + (2 * 0.05) = 1.1x`:

- Learned chunk: `0.70 * 1.1 = 0.77`
- Unlearned chunk: `0.85 * 1.0 = 0.85`

The learned chunk still loses despite having direct positive evidence. Pattern learning fails to influence retrieval at low-to-medium confidence levels. The signal is too weak.

### No negative patterns

When a chunk is retrieved but the response does not reference its content, this is weak negative evidence — the chunk was probably not useful. Currently this evidence is discarded entirely. Over many interactions, Polly accumulates no knowledge about which chunks are reliably unhelpful for certain query types, meaning the same false-positive chunks get retrieved repeatedly.

---

## Proposed Solution

### 1. Calibrated boost curve

Replace the linear `hit_count * 0.05` formula with a **confidence-tier boost curve** that applies meaningfully different multipliers at each confidence tier:

```
hit_count 1:    1.2x  (mild signal)
hit_count 2–3:  1.5x  (moderate signal)
hit_count 4–7:  2.0x  (strong signal)
hit_count 8–14: 3.0x  (very strong signal)
hit_count 15+:  4.0x  (high confidence — chunk is canonical for this query type)
```

These are multiplied by a **confidence scaling factor** from the `QueryChunkPattern.confidence` field (0.0–1.0), so a pattern with low overall confidence doesn't over-boost individual chunks:

```
effective_boost = tier_boost * (0.5 + 0.5 * pattern.confidence)
```

Example: `hit_count=5`, `pattern.confidence=0.7`:
- `tier_boost = 2.0`
- `effective_boost = 2.0 * (0.5 + 0.5 * 0.7) = 2.0 * 0.85 = 1.7x`

This means a moderately-confident pattern with moderate hit count produces a 1.7x boost — strong enough to influence ranking against a higher raw-similarity competitor.

### 2. Negative chunk patterns

Track chunks that are retrieved but whose content is not referenced in the final response as **negative evidence**. Over multiple retrievals with no reference, assign a **penalty multiplier** < 1.0 to the chunk for similar queries.

---

## Data Model Changes

### `QueryChunkPattern` — add negative evidence fields

In `core/patterns/models.py`, extend `QueryChunkPattern`:

```python
@dataclass
class QueryChunkPattern:
    # ... existing fields ...
    successful_chunks: List[Dict]    # existing: [{chunk_id, hit_count, avg_score, ...}]
    
    # NEW: negative evidence
    penalised_chunks: List[Dict] = field(default_factory=list)
    # Format: [{
    #   "chunk_id": str,
    #   "collection": str,
    #   "miss_count": int,       # times retrieved but not referenced
    #   "last_miss": str,        # ISO timestamp
    #   "penalty": float,        # computed penalty multiplier (0.5–0.95)
    # }]
```

### Penalty formula

```
penalty = max(0.5, 1.0 - (miss_count * 0.08))

miss_count 1:   0.92x  (weak signal — might just be irrelevant for this specific query)
miss_count 3:   0.76x  (moderate signal)
miss_count 5:   0.60x  (strong signal — consistently unhelpful)
miss_count 7+:  0.50x  (floor — never drop below 0.5x to avoid over-penalising)
```

The floor at 0.5x prevents a chunk from being effectively excluded from retrieval entirely based on pattern evidence alone — raw semantic similarity still matters.

---

## Learning Pipeline Changes

### Positive reinforcement (updated)

In `core/rag.py`, after a response is generated, the response text is checked for references to retrieved chunk content. Chunks whose key terms appear in the response are reinforced.

Currently this happens in `Polly._record_routing_outcome()` via `learn_from_compressed()`. The mechanism exists but fires only at compression time (post-hoc). The spec for this spec calls for adding a **per-turn reinforcement** path:

```python
# In polly.py, after response is generated (end of chat() loop):
if self.pattern_engine and rag_chunks_used:
    self._reinforce_chunk_patterns(
        query=query,
        response=response,
        retrieved_chunks=rag_chunks_used,
    )

def _reinforce_chunk_patterns(self, query, response, retrieved_chunks):
    """
    For each retrieved chunk, check if its content is referenced in response.
    Reinforce positive chunks; record negative evidence for unreferenced ones.
    """
    response_lower = response.lower()
    query_sig = self.pattern_engine._create_query_signature(query)
    pattern_id = f"qcp_{query_sig}"

    for chunk in retrieved_chunks:
        # Simple reference check: key terms from chunk appear in response
        chunk_terms = _extract_key_terms(chunk.content)
        match_count = sum(1 for t in chunk_terms if t in response_lower)
        referenced = match_count >= (1 if len(chunk_terms) <= 3 else 2)

        if referenced:
            self.pattern_engine.record_chunk_hit(
                pattern_id=pattern_id,
                chunk_id=chunk.id,
                collection=chunk.source_type,
                query=query,
            )
        else:
            self.pattern_engine.record_chunk_miss(
                pattern_id=pattern_id,
                chunk_id=chunk.id,
                collection=chunk.source_type,
            )
```

### New `PatternEngine` methods

```python
def record_chunk_hit(self, pattern_id, chunk_id, collection, query): ...
    # Increment hit_count for chunk_id in QueryChunkPattern.successful_chunks
    # Remove from penalised_chunks if present (positive evidence overrides negative)

def record_chunk_miss(self, pattern_id, chunk_id, collection): ...
    # Increment miss_count for chunk_id in QueryChunkPattern.penalised_chunks
    # If chunk_id is in successful_chunks with high hit_count, don't penalise
    # (trust positive evidence over negative when there's a strong positive history)
```

### Override rule: positive trumps negative

If a chunk has `hit_count >= 5` in `successful_chunks`, it cannot be penalised regardless of `miss_count`. High positive confirmation overrides occasional misses (perhaps the query varied slightly).

---

## Updated Boost Application in `core/rag.py`

```python
# Step 1.5: Apply query→chunk pattern boosting (updated)
if self.pattern_learner and all_results:
    query_sig = self.pattern_learner._create_query_signature(query)
    matching_qcp = self.pattern_learner.query_chunk_patterns.get(f"qcp_{query_sig}")

    if matching_qcp:
        # Build boost lookup (positive)
        boost_lookup = {}
        for sc in matching_qcp.successful_chunks:
            hit_count = sc.get("hit_count", 1)
            tier_boost = _hit_count_to_tier_boost(hit_count)
            confidence_scale = 0.5 + 0.5 * matching_qcp.confidence
            boost_lookup[sc["chunk_id"]] = tier_boost * confidence_scale

        # Build penalty lookup (negative)
        penalty_lookup = {}
        for pc in matching_qcp.penalised_chunks:
            # Only apply penalty if chunk NOT in positive list with high confidence
            cid = pc["chunk_id"]
            if cid not in boost_lookup or boost_lookup[cid] < 1.5:
                miss_count = pc.get("miss_count", 1)
                penalty_lookup[cid] = max(0.5, 1.0 - (miss_count * 0.08))

        # Apply to results
        for result in all_results:
            cid = result.chunk.id
            if cid in boost_lookup:
                result.score *= boost_lookup[cid]
            elif cid in penalty_lookup:
                result.score *= penalty_lookup[cid]

        all_results.sort(key=lambda r: r.score, reverse=True)


def _hit_count_to_tier_boost(hit_count: int) -> float:
    if hit_count >= 15: return 4.0
    if hit_count >= 8:  return 3.0
    if hit_count >= 4:  return 2.0
    if hit_count >= 2:  return 1.5
    return 1.2
```

---

## Tracking Retrieved Chunks for Reinforcement

The `chat()` method in `polly.py` needs to track which RAG chunks were retrieved for the current turn so `_reinforce_chunk_patterns()` can reference them. Currently chunks are retrieved inside `_gather_rag_context()` but not stored on the instance.

Add a turn-scoped attribute:

```python
self._current_turn_chunks: List[Chunk] = []  # cleared each turn
```

Set in `_gather_rag_context()` after search, read in `_reinforce_chunk_patterns()` after response.

---

## Decay of Negative Evidence

Negative evidence (miss counts) should decay over time. An old miss from a different context is less meaningful than a recent one. Apply the same half-life decay logic that positive patterns use (30-day half-life):

```python
# When loading penalised_chunks for a pattern:
days_since_miss = (now - last_miss_date).days
if days_since_miss > 30:
    decay = 0.98 ** (days_since_miss - 30)
    effective_miss_count = pc["miss_count"] * decay
```

---

## Configuration

```yaml
# config/config.yaml — add to rag or patterns section
rag:
  pattern_boost:
    enabled: true
    per_turn_reinforcement: true     # Reinforce on every turn (not just at compression)
    negative_patterns: true          # Track and apply miss penalties
    max_boost: 4.0                   # Hard ceiling on positive boost multiplier
    min_penalty: 0.5                 # Floor on penalty multiplier
    positive_override_threshold: 5   # hit_count above which positive overrides negative
```

---

## Files Touched

| File | Change |
|------|--------|
| `core/patterns/models.py` | Add `penalised_chunks` field to `QueryChunkPattern` |
| `core/patterns/engine.py` | Add `record_chunk_hit()`, `record_chunk_miss()` methods |
| `core/patterns/storage/json_backend.py` | Persist `penalised_chunks` alongside `successful_chunks` |
| `core/rag.py` | Replace linear boost with tier curve; add penalty lookup application |
| `core/polly.py` | Add `_reinforce_chunk_patterns()`, `_current_turn_chunks` tracking |
| `config/config.yaml` | Add `rag.pattern_boost` section |

---

## Success Criteria

- [ ] A chunk with `hit_count=5` receives ≥ 2.0x boost (vs. 1.25x currently)
- [ ] A chunk with `miss_count=5` receives ≤ 0.60x penalty when no positive history exists
- [ ] Positive evidence with `hit_count >= 5` overrides negative evidence
- [ ] Per-turn reinforcement fires within 50ms (key term matching, no LLM call)
- [ ] After 30 days inactivity, miss penalties decay to < 0.1x their original value
- [ ] No previously-unseen regression: chunks with no pattern history receive 1.0x (unchanged)
