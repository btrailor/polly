"""
Rolling Context Window — dynamic working set with per-turn decay and bin-packing.

Maintains a working set of scored context entries across conversation turns.
Entries that are referenced in queries/responses get amplified (recency reset);
entries that go unreferenced decay and are eventually evicted.

Selection uses budget-aware greedy bin-packing with bounded look-ahead to
fit the most relevant entries within each section's token budget.
"""

import logging
import re
from typing import Dict, List, Optional, Set

from core.context.relevance_scorer import RelevanceScorer, ScoredEntry
from core.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)

# Common English words to exclude from key-term extraction
_STOPWORDS: Set[str] = {
    "about", "after", "again", "almost", "already", "always", "another",
    "because", "before", "between", "cannot", "change", "different",
    "during", "enough", "every", "example", "following", "further",
    "getting", "however", "important", "include", "instead", "looking",
    "making", "nothing", "number", "people", "perhaps", "please",
    "possible", "problem", "process", "provide", "really", "result",
    "running", "should", "simple", "something", "special", "started",
    "string", "system", "taking", "things", "though", "through",
    "together", "trying", "understand", "update", "updated", "using",
    "version", "wanted", "without", "working", "would",
}

# Source → section name mapping for bin-packing
_SOURCE_TO_SECTION: Dict[str, str] = {
    "memory:stable": "memory",
    "memory:episodic": "memory",
    "memory:working": "memory",
    "rag": "rag",
    "mental_model": "mental_models",
    "entity": "entities",
    "pattern": "entities",
}


class RollingContext:
    """
    Maintains a dynamic working set of context entries across turns.
    Entries decay when unreferenced and amplify when re-referenced.
    Selection uses budget-aware greedy bin-packing.
    """

    def __init__(self, config: dict, scorer: Optional[RelevanceScorer] = None):
        """
        Args:
            config: context_budget.rolling section with keys:
                decay_per_turn, eviction_turns, amplification_reset
            scorer: Optional RelevanceScorer for re-scoring entries
        """
        self.decay_rate: float = config.get("decay_per_turn", 0.85)
        self.eviction_turns: int = config.get("eviction_turns", 5)
        self.amplification_reset: bool = config.get("amplification_reset", True)
        self.scorer = scorer

        self.entries: List[ScoredEntry] = []
        self.turn_count: int = 0

        # Index for fast dedup lookup
        self._hash_index: Dict[str, int] = {}  # content_hash → index in entries

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def ingest(self, new_entries: List[ScoredEntry]):
        """
        Add new entries from this turn's retrieval.

        Deduplicates against existing entries (same content hash).
        New entries that match existing ones update the existing
        entry's score if the new score is higher. Also extracts and
        caches key_terms for new entries.
        """
        for entry in new_entries:
            # Ensure key_terms are extracted
            if not entry.key_terms:
                entry.key_terms = _extract_key_terms(entry.content)

            # Ensure token_count is set
            if entry.token_count == 0:
                entry.token_count = TokenCounter.count(entry.content)

            # Check for duplicate
            if entry.content_hash in self._hash_index:
                idx = self._hash_index[entry.content_hash]
                existing = self.entries[idx]

                # Update score if new one is higher
                if entry.composite_score > existing.composite_score:
                    existing.composite_score = entry.composite_score
                    existing.raw_score = entry.raw_score
                    existing.metadata = entry.metadata
                    logger.debug(
                        f"Updated existing entry score to "
                        f"{entry.composite_score:.3f}: "
                        f"{entry.content[:50]}..."
                    )
            else:
                # New entry
                idx = len(self.entries)
                self.entries.append(entry)
                self._hash_index[entry.content_hash] = idx

    # ------------------------------------------------------------------
    # Turn tracking
    # ------------------------------------------------------------------

    def on_new_turn(
        self,
        query: str,
        response: str,
        query_domains: Optional[List[str]] = None,
    ):
        """
        Called after each turn completes. Updates all entries:

        1. Increment turn_count
        2. For each entry, check if referenced in query or response
        3. Referenced: reset recency, increment reference_count
        4. Not referenced: multiply composite_score by decay_rate
        5. Evict entries past eviction threshold
        """
        self.turn_count += 1
        combined_text = f"{query} {response}"

        evict_indices: List[int] = []

        for idx, entry in enumerate(self.entries):
            referenced = _detect_reference(entry, combined_text)

            if referenced:
                # Amplification: reset recency, increment reference count
                entry.reference_count += 1
                entry.last_referenced_turn = self.turn_count
                entry.turns_since_reference = 0

                if self.amplification_reset:
                    # Re-score with fresh recency
                    if self.scorer:
                        self.scorer.score(
                            entry,
                            query_domains=query_domains or [],
                            current_turn=self.turn_count,
                        )
            else:
                # Decay: increase turns since reference, reduce score
                entry.turns_since_reference += 1

                # Apply multiplicative decay to composite score
                entry.composite_score *= self.decay_rate

                # Check for eviction
                if entry.turns_since_reference >= self.eviction_turns:
                    evict_indices.append(idx)

        # Evict expired entries (reverse order to preserve indices)
        if evict_indices:
            for idx in sorted(evict_indices, reverse=True):
                evicted = self.entries[idx]
                logger.debug(
                    f"Evicting entry after {evicted.turns_since_reference} "
                    f"unreferenced turns: {evicted.content[:50]}..."
                )
                # Remove from hash index
                self._hash_index.pop(evicted.content_hash, None)
                self.entries.pop(idx)

            # Rebuild hash index after eviction
            self._rebuild_hash_index()

    # ------------------------------------------------------------------
    # Selection (bin-packing)
    # ------------------------------------------------------------------

    def select(
        self, section_budgets: Dict[str, int]
    ) -> Dict[str, List[ScoredEntry]]:
        """
        Bin-pack entries into sections within their budgets.

        Algorithm:
        1. Group entries by source section
        2. For each section, sort entries by composite_score descending
        3. Greedily take entries until section budget exhausted
        4. Look-ahead of 5: if next entry doesn't fit, check smaller entries

        Args:
            section_budgets: {section_name: token_budget} from BudgetAllocator

        Returns:
            {section_name: [selected entries]} for each section
        """
        # Group entries by section
        section_entries: Dict[str, List[ScoredEntry]] = {}
        for entry in self.entries:
            section = _SOURCE_TO_SECTION.get(entry.source, "entities")
            if section not in section_entries:
                section_entries[section] = []
            section_entries[section].append(entry)

        # Sort each section by score descending
        for section in section_entries:
            section_entries[section].sort(
                key=lambda e: e.composite_score, reverse=True
            )

        # Bin-pack with look-ahead
        selected: Dict[str, List[ScoredEntry]] = {}

        for section_name, budget in section_budgets.items():
            if budget <= 0:
                selected[section_name] = []
                continue

            candidates = section_entries.get(section_name, [])
            if not candidates:
                selected[section_name] = []
                continue

            picked, _ = self._greedy_binpack(candidates, budget, look_ahead=5)
            selected[section_name] = picked

        return selected

    @staticmethod
    def _greedy_binpack(
        entries: List[ScoredEntry],
        budget: int,
        look_ahead: int = 5,
    ) -> tuple:
        """
        Greedy bin-packing with bounded look-ahead.

        Returns (selected_entries, tokens_used).
        """
        selected: List[ScoredEntry] = []
        remaining = budget
        skip_set: set = set()  # indices to skip (already taken or skipped)

        i = 0
        while i < len(entries):
            if i in skip_set:
                i += 1
                continue

            entry = entries[i]

            if entry.token_count <= remaining:
                # Fits — take it
                selected.append(entry)
                remaining -= entry.token_count
                skip_set.add(i)
                i += 1
            else:
                # Doesn't fit — look ahead for smaller entries
                found_smaller = False
                for j in range(i + 1, min(i + 1 + look_ahead, len(entries))):
                    if j in skip_set:
                        continue
                    if entries[j].token_count <= remaining:
                        selected.append(entries[j])
                        remaining -= entries[j].token_count
                        skip_set.add(j)
                        found_smaller = True
                        break

                if not found_smaller:
                    # Nothing fits within look-ahead — we're done
                    break

                i += 1

            if remaining <= 0:
                break

        tokens_used = budget - remaining
        return selected, tokens_used

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rebuild_hash_index(self):
        """Rebuild the content_hash → index mapping after eviction."""
        self._hash_index = {
            entry.content_hash: idx for idx, entry in enumerate(self.entries)
        }

    # ------------------------------------------------------------------
    # Persistence (Spec 03)
    # ------------------------------------------------------------------

    def save(self, db_path: str, session_id: str) -> int:
        """
        Persist current working set to SQLite (compression.db).

        Called from Polly._end_session() on graceful shutdown.

        Returns count of entries saved.
        """
        import sqlite3
        import json
        from datetime import datetime
        from pathlib import Path

        db_path = str(Path(db_path).expanduser())
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Ensure table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rolling_context_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                entry_hash TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                raw_score REAL NOT NULL,
                composite_score REAL NOT NULL,
                token_count INTEGER NOT NULL,
                reference_count INTEGER NOT NULL DEFAULT 0,
                last_referenced_turn INTEGER NOT NULL DEFAULT 0,
                turns_since_reference INTEGER NOT NULL DEFAULT 0,
                key_terms_json TEXT,
                metadata_json TEXT,
                turn_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(session_id, entry_hash)
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_rc_state_session
            ON rolling_context_state(session_id, saved_at DESC)
        """)

        # Delete existing entries for this session (replace on save)
        cur.execute("DELETE FROM rolling_context_state WHERE session_id = ?", (session_id,))

        saved_at = datetime.now().isoformat()
        count = 0
        for entry in self.entries:
            try:
                cur.execute("""
                    INSERT INTO rolling_context_state (
                        session_id, saved_at, entry_hash, content, source,
                        raw_score, composite_score, token_count,
                        reference_count, last_referenced_turn, turns_since_reference,
                        key_terms_json, metadata_json, turn_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    saved_at,
                    entry.content_hash,
                    entry.content,
                    entry.source,
                    entry.raw_score,
                    entry.composite_score,
                    entry.token_count,
                    entry.reference_count,
                    entry.last_referenced_turn,
                    entry.turns_since_reference,
                    json.dumps(entry.key_terms or []),
                    json.dumps(entry.metadata or {}),
                    self.turn_count,
                ))
                count += 1
            except Exception as e:
                logger.warning(f"Failed to save rolling context entry: {e}")

        conn.commit()
        conn.close()
        logger.debug(f"Saved {count} RollingContext entries for session {session_id}")
        return count

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
        import sqlite3
        import json
        from datetime import datetime
        from pathlib import Path

        db_path = str(Path(db_path).expanduser())
        if not Path(db_path).exists():
            logger.debug(f"No RollingContext DB at {db_path}, starting fresh")
            return cls(config, scorer=scorer)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Load entries for this session
        cur.execute("""
            SELECT entry_hash, content, source, raw_score, composite_score,
                   token_count, reference_count, last_referenced_turn,
                   turns_since_reference, key_terms_json, metadata_json, saved_at
            FROM rolling_context_state
            WHERE session_id = ?
            ORDER BY saved_at DESC
        """, (session_id,))

        rows = cur.fetchall()
        conn.close()

        if not rows:
            logger.debug(f"No RollingContext entries for session {session_id}")
            return cls(config, scorer=scorer)

        # Calculate gap decay
        ASSUMED_TURN_DURATION_SECONDS = 30.0
        MIN_SCORE_THRESHOLD = 0.05

        gap_turns = session_gap_seconds / ASSUMED_TURN_DURATION_SECONDS
        decay_rate = config.get("decay_per_turn", 0.85)
        gap_decay = decay_rate ** gap_turns

        # Create new instance
        ctx = cls(config, scorer=scorer)

        for row in rows:
            (entry_hash, content, source, raw_score, composite_score,
             token_count, reference_count, last_ref_turn, turns_since_ref,
             key_terms_json, metadata_json, saved_at_str) = row

            # Check max_age_hours
            try:
                saved_at = datetime.fromisoformat(saved_at_str)
                age_hours = (datetime.now() - saved_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    logger.debug(f"Dropping entry {entry_hash[:8]}... (age {age_hours:.1f}h > {max_age_hours}h)")
                    continue
            except Exception:
                pass

            # Apply gap decay
            decayed_score = composite_score * gap_decay
            if decayed_score < MIN_SCORE_THRESHOLD:
                logger.debug(f"Dropping entry {entry_hash[:8]}... (decayed to {decayed_score:.3f} < {MIN_SCORE_THRESHOLD})")
                continue

            # Reconstruct ScoredEntry
            entry = ScoredEntry(
                content=content,
                source=source,
                raw_score=raw_score,
                composite_score=decayed_score,
                token_count=token_count,
                key_terms=json.loads(key_terms_json) if key_terms_json else [],
                metadata=json.loads(metadata_json) if metadata_json else {},
                reference_count=reference_count,
                last_referenced_turn=0,  # Reset to avoid stale turn numbers
                turns_since_reference=turns_since_ref,
            )
            ctx.entries.append(entry)
            ctx._hash_index[entry.content_hash] = len(ctx.entries) - 1

        logger.info(f"Loaded {len(ctx.entries)} RollingContext entries (gap_decay={gap_decay:.3f})")
        return ctx

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """Return serializable state for debugging/metrics."""
        section_counts: Dict[str, int] = {}
        for entry in self.entries:
            section = _SOURCE_TO_SECTION.get(entry.source, "other")
            section_counts[section] = section_counts.get(section, 0) + 1

        top_entries = sorted(
            self.entries, key=lambda e: e.composite_score, reverse=True
        )[:5]

        return {
            "turn_count": self.turn_count,
            "total_entries": len(self.entries),
            "section_counts": section_counts,
            "top_scores": [
                {
                    "content": e.content[:60],
                    "score": round(e.composite_score, 3),
                    "source": e.source,
                    "refs": e.reference_count,
                }
                for e in top_entries
            ],
        }


# ======================================================================
# Module-level utility functions
# ======================================================================


def _extract_key_terms(content: str) -> List[str]:
    """
    Extract key terms from content for reference detection.

    Extracts:
    - Terms in backticks (code references)
    - Capitalized words (likely proper nouns / entities)
    - Terms > 6 chars that aren't common stopwords

    Returns deduplicated list of max 10 terms.
    """
    terms: Set[str] = set()

    # 1. Terms in backticks
    backtick_terms = re.findall(r"`([^`]+)`", content)
    for term in backtick_terms:
        cleaned = term.strip()
        if cleaned:
            terms.add(cleaned.lower())

    # 2. Capitalized words (proper nouns)
    # Skip first word of sentences (always capitalized)
    sentences = re.split(r"[.!?]\s+", content)
    for sentence in sentences:
        words = sentence.split()
        for word in words[1:]:  # Skip first word
            cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "", word)
            if cleaned and cleaned[0].isupper() and len(cleaned) > 2:
                terms.add(cleaned.lower())

    # 3. Long technical terms
    words = re.findall(r"\b\w+\b", content)
    for word in words:
        if len(word) > 6 and word.lower() not in _STOPWORDS:
            terms.add(word.lower())

    # Deduplicate and limit
    return sorted(list(terms))[:10]


def _detect_reference(entry: ScoredEntry, text: str) -> bool:
    """
    Check if an entry's content is referenced in text.
    Uses key_terms overlap (not semantic search — too expensive per-turn).

    Threshold: >= 2 matching terms, or >= 1 if entry has <= 3 total terms.
    """
    if not entry.key_terms:
        return False

    text_lower = text.lower()
    text_tokens = set(re.findall(r"\b\w+\b", text_lower))

    matching = 0
    for term in entry.key_terms:
        # Check both token-level match and substring match
        # (substring handles multi-word backtick terms like "token_counter")
        if term in text_tokens or term in text_lower:
            matching += 1

    threshold = 1 if len(entry.key_terms) <= 3 else 2
    return matching >= threshold
