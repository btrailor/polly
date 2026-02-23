# OpenSpec: Semantic Compression Trigger

**Status:** 💭 Planned  
**Priority:** P4 — Preserve valuable dense conversations  
**Related:** `core/compression/manager.py:should_compress()`, `core/compression/compressor.py`, `core/polly.py:_try_compress_conversation()`, `config/config.yaml:compression`  
**Motivation:** The current compression trigger fires on `message_threshold: 20` and `age_hours: 24` — purely structural signals. A 15-message deep technical conversation may be far more valuable than a 25-message stream of trivial one-liners. Compression should be driven by semantic redundancy, not message count.

---

## Problem (Detailed)

`CompressionManager.should_compress()` (`core/compression/manager.py:85–130`) checks:

1. `exchange_count > COMPRESSION_THRESHOLD * 2` (hard count)
2. `age_hours > COMPRESSION_AGE_HOURS and exchange_count > COMPRESSION_THRESHOLD` (age + count)

This means:

- A 21-message conversation about a single complex ongoing project compresses and loses rich working context.
- A 25-message conversation that is 80% repetitive ("got it", "yes", "ok", re-asked questions) is preserved in full — wasting tokens on every subsequent turn.
- There is no recognition of information density. The system cannot distinguish "this conversation is highly novel and information-dense" from "this conversation is mostly noise."

The compression trigger should answer the question: **"Is this conversation still adding meaningful new information, or has it become redundant enough to compress?"**

---

## Proposed Solution

Replace the binary count/age trigger with a **Semantic Redundancy Score (SRS)**. The SRS measures how much marginal new information each recent message adds relative to what has already been said. When marginal gain falls below a threshold, compression is appropriate regardless of message count.

Compression still fires on the count/age triggers as a hard fallback, but the semantic trigger is the primary decision path.

---

## Semantic Redundancy Score (SRS)

### Concept

Given the last N messages of a conversation, compute the **information density** as follows:

1. Embed each message using the existing `nomic-embed-text` model (already in use via `UnifiedRAG.embed_text()`).
2. Compute the **centroid** of all message embeddings.
3. For each message, compute its **distance from the centroid** (cosine distance). High distance = high novelty. Low distance = redundant/repetitive.
4. Compute a rolling average of the last K messages' distances. If the rolling average falls below `redundancy_threshold`, the conversation is semantically saturated.

### Formula

```
SRS = mean(cosine_distance(embed(msg_i), centroid))
      for msg_i in last_k_messages

where centroid = mean(embed(msg_j)) for all messages in conversation

compression_recommended = SRS < redundancy_threshold
```

### Calibration

| SRS Value | Interpretation | Action |
|-----------|---------------|--------|
| > 0.25 | High novelty, conversation is actively evolving | Do not compress |
| 0.15–0.25 | Moderate novelty, some repetition | Consider compression if count also high |
| < 0.15 | Low novelty, conversation is semantically saturated | Compress |

These thresholds are configurable and will be tuned based on observed conversation patterns.

---

## Implementation

### New method: `CompressionManager.compute_srs()`

```python
def compute_srs(
    self,
    conversation_history: List[Dict],
    embed_fn: Callable[[str], List[float]],
    window_size: int = 6,  # last K messages for rolling average
) -> float:
    """
    Compute Semantic Redundancy Score for a conversation.
    
    Returns a float 0.0–1.0:
        0.0 = completely redundant (all messages identical)
        1.0 = completely novel (no semantic overlap)
    
    Args:
        conversation_history: List of {"role": ..., "content": ...} dicts
        embed_fn: Embedding function (UnifiedRAG.embed_text)
        window_size: Number of recent messages to score for rolling average
    
    Returns:
        float — mean cosine distance of recent messages from conversation centroid
    """
    if len(conversation_history) < 4:
        return 1.0  # Too short to assess — don't compress

    # Extract text content from messages
    texts = [
        msg["content"] for msg in conversation_history
        if msg.get("content") and len(msg["content"]) > 20  # skip trivial acks
    ]
    if len(texts) < 4:
        return 1.0

    import numpy as np

    # Embed all messages
    embeddings = np.array([embed_fn(text) for text in texts])

    # Compute centroid
    centroid = embeddings.mean(axis=0)
    centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)

    # Compute cosine distance from centroid for each message
    distances = []
    for emb in embeddings:
        emb_norm = emb / (np.linalg.norm(emb) + 1e-9)
        cosine_sim = np.dot(emb_norm, centroid_norm)
        cosine_dist = 1.0 - cosine_sim
        distances.append(float(cosine_dist))

    # Rolling average of last window_size messages
    recent_distances = distances[-window_size:]
    return float(np.mean(recent_distances))
```

### Updated `CompressionManager.should_compress()`

```python
def should_compress(
    self,
    conversation_history: List[Dict],
    conversation_id: Optional[str] = None,
    created_at: Optional[datetime] = None,
    embed_fn: Optional[Callable] = None,  # NEW: optional embedding function
) -> bool:
    """
    Determine whether conversation should be compressed.
    
    Decision logic (in priority order):
    
    1. HARD MINIMUM: Never compress below min_messages (default 10).
       Short conversations always preserve in full.
    
    2. SEMANTIC TRIGGER (primary, if embed_fn provided):
       Compress if SRS < redundancy_threshold AND message count >= min_for_semantic.
    
    3. STRUCTURAL FALLBACK (always active):
       Compress if message count > hard_count_threshold.
       Compress if age > age_hours AND count > age_count_threshold.
    """
    message_count = len(conversation_history)

    # Hard minimum — never compress very short conversations
    min_messages = self.config.get("compression.min_messages", 10)
    if message_count < min_messages:
        return False

    # Semantic trigger (primary path)
    if embed_fn is not None:
        semantic_enabled = self.config.get(
            "compression.semantic_trigger.enabled", True
        )
        if semantic_enabled:
            min_for_semantic = self.config.get(
                "compression.semantic_trigger.min_messages", 12
            )
            if message_count >= min_for_semantic:
                try:
                    srs = self.compute_srs(
                        conversation_history,
                        embed_fn,
                        window_size=self.config.get(
                            "compression.semantic_trigger.window_size", 6
                        ),
                    )
                    threshold = self.config.get(
                        "compression.semantic_trigger.redundancy_threshold", 0.15
                    )
                    if srs < threshold:
                        logger.info(
                            f"Semantic compression trigger: SRS={srs:.3f} "
                            f"< threshold={threshold:.3f} "
                            f"({message_count} messages)"
                        )
                        return True
                    else:
                        logger.debug(
                            f"Semantic trigger not met: SRS={srs:.3f} "
                            f">= threshold={threshold:.3f}"
                        )
                except Exception as e:
                    logger.warning(f"SRS computation failed: {e}. Falling back to structural.")

    # Structural fallback
    exchange_count = message_count // 2
    hard_threshold = self.config.get("compression.message_threshold", 20)
    
    if exchange_count > hard_threshold * 2:
        return True

    if created_at:
        age_hours = (datetime.now() - created_at).total_seconds() / 3600
        age_threshold = self.config.get("compression.age_hours", 24)
        age_count = self.config.get("compression.age_count_threshold", 10)
        if age_hours > age_threshold and exchange_count > age_count:
            return True

    return False
```

### Pass `embed_fn` from `polly.py`

In `Polly._try_compress_conversation()`, pass the RAG embed function:

```python
embed_fn = self.rag.embed_text if self.rag else None

if self.compression_manager.should_compress(
    self.conversation_history,
    conversation_id=conv_id,
    created_at=self.session_start,
    embed_fn=embed_fn,  # NEW
):
    ...
```

---

## SRS Caching

Embedding all conversation messages on every `should_compress()` call would be expensive. Cache the SRS computation:

- Recompute only when `len(conversation_history)` has changed since last computation.
- Store `(message_count_at_last_compute, srs_value)` in `CompressionManager` instance state.
- If `message_count` unchanged: return cached SRS.
- If changed by 1–2 messages: incremental update (add new message embeddings, recompute centroid delta).
- If changed by > 2 messages (shouldn't normally happen): full recompute.

```python
self._srs_cache: Optional[Tuple[int, float]] = None  # (msg_count, srs)
```

---

## Configuration

```yaml
# config/config.yaml — update compression section
compression:
  enabled: true
  message_threshold: 20      # Structural fallback: compress after N exchanges
  age_hours: 24              # Structural fallback: compress after N hours
  keep_recent: 10
  min_messages: 10           # Never compress below this count

  semantic_trigger:
    enabled: true
    min_messages: 12                  # Minimum messages before semantic trigger fires
    redundancy_threshold: 0.15        # SRS below this → compress
    window_size: 6                    # Messages in rolling average window
    log_srs: false                    # Log SRS on each check (debug)
```

---

## SRS as a Diagnostic Signal

Beyond compression triggering, the SRS is a useful signal on its own:

- **High SRS sustained conversation:** Polly is being used for genuine exploration — each message adds novel information. This is the mode where compression should be most conservative.
- **Low SRS conversation:** The user and Polly are circling the same topic repeatedly. This may indicate a clarification failure or an incomplete answer. The SRS dip could be surfaced as a gentle signal ("It looks like we've covered this ground a few times — want me to summarise where we've landed?").

This diagnostic use is out of scope for this spec but noted as a future enhancement.

---

## Files Touched

| File | Change |
|------|--------|
| `core/compression/manager.py` | Add `compute_srs()`, refactor `should_compress()` to accept `embed_fn` |
| `core/polly.py` | Pass `embed_fn=self.rag.embed_text` to `should_compress()` in `_try_compress_conversation()` |
| `config/config.yaml` | Add `compression.semantic_trigger` section |

---

## Success Criteria

- [ ] Short but information-dense conversations (< 20 messages, high SRS) are not compressed
- [ ] Long but repetitive conversations (> 12 messages, low SRS) trigger compression earlier than the count threshold would
- [ ] SRS computation adds < 500ms to `should_compress()` calls (with caching active)
- [ ] Structural fallback still fires correctly when `embed_fn` is unavailable
- [ ] No regression: all existing compression tests pass
- [ ] SRS values visible in debug logs when `semantic_trigger.log_srs: true`
