# OpenSpec: Persist RollingContext Across Sessions

**Status:** 💭 Planned  
**Priority:** P3 — Cross-session continuity  
**Related:** `core/context/rolling_context.py`, `core/context/relevance_scorer.py`, `core/polly.py:_init_memory_context()`, `core/memory/tiers.py`  
**Motivation:** The `RollingContext` working set — with its carefully-built decay state, reference counts, and amplification history — is session-only and lives in memory. When a session ends, that context evaporates. Each new session starts cold despite Polly having persistent tiered memory. The working memory tier in `TieredMemoryStore` persists to Mem0 but the *RollingContext's structural state* (which items are hot, how much they've decayed, how many times each was referenced) does not survive the session boundary.

---

## Problem (Detailed)

The `RollingContext` class (`core/context/rolling_context.py`) maintains:

- `entries: List[ScoredEntry]` — the working set of scored context items
- Per-entry: `reference_count`, `last_referenced_turn`, `turns_since_reference`, `composite_score`
- `turn_count: int` — total turns in the session
- `_hash_index: Dict[str, int]` — deduplication index

At session end (when the `Polly` process terminates or a new session is created), all of this is lost. The next session must rebuild the working set from scratch by re-running all contributors at turn 0 — which means no amplification state, no reference history, and no decay context carried forward.

This is a particularly sharp gap for the "working" memory tier: `TieredMemoryStore` preserves working tier content in Mem0, but the `RollingContext` doesn't know which of those working memories were actively in-use and which were retrieved but ignored. The result is that the first few turns of every new session are lower quality than the last few turns of the previous session.

---

## Proposed Solution

Serialize the `RollingContext` working set to a lightweight SQLite table at session end. On session start, reload it and apply a **session-gap decay** proportional to the elapsed time — items that were fresh at session end are still relatively fresh at session start (if the gap was minutes), but stale if the gap was days.

This is distinct from the `TieredMemoryStore`'s episodic/stable tiers. Those are semantic memories extracted and synthesised from conversations. The persisted `RollingContext` is the *active working surface* — the specific items that were in play during the last session, with their structural scoring state.

---

## Architecture

### New table: `rolling_context_state` in `~/.polly/compression.db`

Reuse the existing SQLite database that `CompressionManager` already maintains.

```sql
CREATE TABLE IF NOT EXISTS rolling_context_state (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    saved_at        DATETIME NOT NULL,
    entry_hash      TEXT NOT NULL,          -- ScoredEntry.content_hash
    content         TEXT NOT NULL,
    source          TEXT NOT NULL,          -- "memory:stable", "mental_model", etc.
    raw_score       REAL NOT NULL,
    composite_score REAL NOT NULL,
    token_count     INTEGER NOT NULL,
    reference_count INTEGER NOT NULL DEFAULT 0,
    last_referenced_turn INTEGER NOT NULL DEFAULT 0,
    turns_since_reference INTEGER NOT NULL DEFAULT 0,
    key_terms_json  TEXT,                   -- JSON array of key terms
    metadata_json   TEXT,                   -- JSON dict of source metadata
    turn_count      INTEGER NOT NULL DEFAULT 0,  -- session turn_count at save
    UNIQUE(session_id, entry_hash)
);

CREATE INDEX IF NOT EXISTS idx_rc_state_session
    ON rolling_context_state(session_id, saved_at DESC);
```

### New methods on `RollingContext`

```python
def save(self, db_path: str, session_id: str) -> int:
    """
    Persist current working set to SQLite.
    Returns count of entries saved.
    
    Called from Polly._end_session() or at process exit.
    """
    ...

@classmethod
def load(
    cls,
    db_path: str,
    session_id: str,
    config: dict,
    scorer: Optional[RelevanceScorer] = None,
    max_age_hours: float = 72.0,
    session_gap_seconds: float = 0.0,
) -> "RollingContext":
    """
    Reload working set from SQLite and apply session-gap decay.
    
    session_gap_seconds: elapsed time since the saved session ended.
    Entries are decayed proportionally: composite_score *= decay_rate^(gap_turns)
    where gap_turns = session_gap_seconds / avg_turn_duration_seconds.
    
    Entries with composite_score below MIN_SCORE_THRESHOLD after decay are dropped.
    """
    ...
```

### Session-Gap Decay Formula

```
gap_equivalent_turns = session_gap_seconds / ASSUMED_TURN_DURATION_SECONDS
                       (default ASSUMED_TURN_DURATION_SECONDS = 30)

decayed_score = saved_composite_score * (decay_rate ^ gap_equivalent_turns)
             = saved_composite_score * (0.85 ^ gap_equivalent_turns)

If decayed_score < MIN_SCORE_THRESHOLD (0.05): drop entry.
```

Example: an entry with `composite_score = 0.9` saved 10 minutes ago:
- `gap_equivalent_turns = 600 / 30 = 20 turns`
- `decayed_score = 0.9 * (0.85^20) = 0.9 * 0.039 = 0.035` → below threshold, dropped

An entry saved 2 minutes ago:
- `gap_equivalent_turns = 120 / 30 = 4 turns`
- `decayed_score = 0.9 * (0.85^4) = 0.9 * 0.522 = 0.47` → kept, partially decayed

This behaviour is intentional: items from a session that ended very recently carry forward meaningfully; items from a session that ended hours ago are largely pruned, leaving only the highest-composite-score entries.

The `max_age_hours` parameter (default 72h) is a hard ceiling: entries older than this are always dropped regardless of score.

---

## Integration in `polly.py`

### Session start — `_init_memory_context()`

```python
def _init_memory_context(self):
    # ... existing init code ...

    # Attempt to reload persisted RollingContext from previous session
    db_path = str(Path(self.config.get("knowledge_base.path", "~/.polly")).expanduser() 
                  / "compression.db")
    
    if self.config.get("context_budget.rolling.persist_across_sessions", True):
        saved_session_id = self._load_last_session_id(db_path)
        if saved_session_id:
            try:
                saved_at = self._load_session_saved_at(db_path, saved_session_id)
                gap_seconds = (datetime.now() - saved_at).total_seconds()
                
                self.rolling_context = RollingContext.load(
                    db_path=db_path,
                    session_id=saved_session_id,
                    config=rolling_config,
                    scorer=self.relevance_scorer,
                    session_gap_seconds=gap_seconds,
                )
                loaded_count = len(self.rolling_context.entries)
                logger.info(
                    f"Restored RollingContext: {loaded_count} entries from "
                    f"session {saved_session_id} ({gap_seconds/3600:.1f}h ago)"
                )
            except Exception as e:
                logger.warning(f"Could not restore RollingContext: {e}. Starting fresh.")
                self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
        else:
            self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
    else:
        self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
```

### Session end — `_end_session()`

```python
def _end_session(self):
    """Called on graceful shutdown or explicit session end."""
    if self.rolling_context and self.config.get("context_budget.rolling.persist_across_sessions", True):
        db_path = ...
        session_id = f"session_{self.session_start.isoformat()}"
        count = self.rolling_context.save(db_path, session_id)
        self._save_last_session_id(db_path, session_id)
        logger.info(f"Persisted RollingContext: {count} entries for session {session_id}")
```

### Trigger `_end_session()` from:

1. `interfaces/server.py` — `@app.on_event("shutdown")` handler
2. `interfaces/server.py` — `POST /api/session/end` endpoint (for Electron to call before quit)
3. Python `atexit` handler registered during `Polly.__init__()` as fallback

---

## Configuration

```yaml
# config/config.yaml — add to context_budget.rolling section
context_budget:
  rolling:
    persist_across_sessions: true
    session_gap_turn_duration_secs: 30   # Assumed seconds per turn for gap decay
    max_persist_age_hours: 72            # Hard cutoff: entries older than this dropped
    min_score_after_decay: 0.05          # Drop entries that decay below this
```

---

## What Is and Is Not Persisted

| Persisted | Not Persisted |
|-----------|--------------|
| Entry content | BudgetPlan (recomputed each turn) |
| composite_score (pre-decay) | turn_count (resets to 0 in new session) |
| reference_count | Session-specific call kwargs |
| turns_since_reference | |
| key_terms | |
| source and metadata | |
| raw_score | |

`turn_count` resets to 0 in the new session — the loaded entries' reference/decay state is preserved but the absolute turn numbering restarts.

---

## Interaction with Tiered Memory

This feature complements, not replaces, the `TieredMemoryStore`. The relationship:

| System | What it stores | Persistence |
|--------|---------------|-------------|
| `TieredMemoryStore` (WORKING tier) | Semantic content extracted from the session (facts, decisions, summaries) | Mem0 / ChromaDB |
| `RollingContext` persistence | Structural state of the active working surface (scores, decay, reference counts) | SQLite |

A memory entry may exist in both: the `TieredMemoryStore` holds its content semantically indexed; the `RollingContext` persistence holds its current "temperature" (how recently it was in active use).

On session start, the reloaded `RollingContext` entries and newly-retrieved entries from `TieredMemoryStore` are merged via the existing `ingest()` deduplication logic (content hash comparison). If the same content appears in both, the existing entry wins but its score is updated to the higher of the two.

---

## Cleanup

Old sessions should not accumulate indefinitely. A cleanup pass runs on session start:

```python
# Delete rolling_context_state rows older than max_persist_age_hours
# (except the most recently saved session, which is always kept)
DELETE FROM rolling_context_state
WHERE saved_at < datetime('now', '-72 hours')
  AND session_id != :current_session_id;
```

---

## Files Touched

| File | Change |
|------|--------|
| `core/context/rolling_context.py` | Add `save()` and `load()` class methods |
| `core/polly.py` | Update `_init_memory_context()` to reload; add `_end_session()` |
| `interfaces/server.py` | Call `_end_session()` on shutdown; add `POST /api/session/end` |
| `~/.polly/compression.db` | New `rolling_context_state` table (migration on first run) |
| `config/config.yaml` | Add `context_budget.rolling.persist_across_sessions` and related keys |

---

## Success Criteria

- [ ] After a session ends and a new session starts within 5 minutes, at least 50% of high-score RollingContext entries from the previous session are present at session start
- [ ] Session-gap decay correctly reduces scores proportional to elapsed time
- [ ] Entries older than `max_persist_age_hours` are never loaded
- [ ] No regression: sessions that load stale state perform no worse than cold-start sessions
- [ ] `_end_session()` completes in < 200ms for a typical working set of 50 entries
- [ ] Cleanup correctly removes entries older than the configured threshold
