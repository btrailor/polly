"""
Context Quality Metrics — Per-turn observability for context systems.

Stores metrics about context assembly, contributor usage, and RAG quality
in SQLite (~/.polly/usage.db) to power the Context Health dashboard:
budget utilisation %, contributor token breakdown, chunk precision, etc.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContributorMetrics:
    """Metrics for a single contributor in a turn."""
    contributor: str
    items_returned: int = 0
    tokens_allocated: int = 0
    tokens_used: int = 0
    utilisation: float = 0.0
    top_score: float = 0.0
    avg_score: float = 0.0
    items_selected: int = 0
    items_evicted: int = 0


@dataclass
class ContextTurnRecord:
    """Complete context metrics for a single turn."""
    session_id: str
    turn_number: int
    query_length_tokens: int = 0
    response_length_tokens: int = 0
    domains: str = "[]"  # JSON array
    persona: Optional[str] = None
    model_used: str = ""
    routing_confidence: str = ""  # "fast" | "balanced" | "thorough"
    cache_hit: bool = False
    cache_similarity: float = 0.0
    total_context_tokens: int = 0
    budget_utilisation: float = 0.0
    srs_at_turn: Optional[float] = None
    decomposed: bool = False
    sub_query_count: int = 0
    mm_format: Optional[str] = None           # "compact" | "full" (Spec 07)
    mm_reference_rate: Optional[float] = None  # 0.0–1.0 (Spec 07)


class ContextMetrics:
    """
    Tracks context system performance per turn.

    Uses the same SQLite database as AutonomyMetrics (~/.polly/usage.db).
    Creates additional tables:
    - context_turns: per-turn context metrics
    - context_contributor_turns: per-contributor breakdown
    - context_rag_turns: RAG-specific metrics
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / '.polly' / 'usage.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        logger.info("ContextMetrics initialized")

    def _init_tables(self):
        """Create context-specific tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main context turns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    query_length_tokens INTEGER,
                    response_length_tokens INTEGER,
                    domains TEXT,
                    persona TEXT,
                    model_used TEXT,
                    routing_confidence TEXT,
                    cache_hit INTEGER NOT NULL DEFAULT 0,
                    cache_similarity REAL,
                    total_context_tokens INTEGER,
                    budget_utilisation REAL,
                    srs_at_turn REAL,
                    decomposed INTEGER NOT NULL DEFAULT 0,
                    sub_query_count INTEGER,
                    mm_format TEXT,
                    mm_reference_rate REAL
                )
            """)

            # Migrate existing databases — add Spec 07 columns if absent
            for col, col_def in [("mm_format", "TEXT"), ("mm_reference_rate", "REAL")]:
                try:
                    cursor.execute(f"ALTER TABLE context_turns ADD COLUMN {col} {col_def}")
                except Exception:
                    pass  # Column already exists

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ct_timestamp
                ON context_turns(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ct_session
                ON context_turns(session_id, turn_number)
            """)

            # Contributor breakdown table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_contributor_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turn_id INTEGER NOT NULL,
                    contributor TEXT NOT NULL,
                    items_returned INTEGER,
                    tokens_allocated INTEGER,
                    tokens_used INTEGER,
                    utilisation REAL,
                    top_score REAL,
                    avg_score REAL,
                    items_selected INTEGER,
                    items_evicted INTEGER,
                    FOREIGN KEY (turn_id) REFERENCES context_turns(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cct_turn_id
                ON context_contributor_turns(turn_id)
            """)

            # RAG-specific metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_rag_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turn_id INTEGER NOT NULL,
                    chunks_retrieved INTEGER,
                    chunks_used INTEGER,
                    chunks_unused INTEGER,
                    top_chunk_score REAL,
                    avg_chunk_score REAL,
                    hybrid_enabled INTEGER,
                    pattern_boosted INTEGER,
                    pattern_penalised INTEGER,
                    collections_searched TEXT,
                    retrieval_tier TEXT,
                    FOREIGN KEY (turn_id) REFERENCES context_turns(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_crt_turn_id
                ON context_rag_turns(turn_id)
            """)

            conn.commit()

    # ------------------------------------------------------------------
    # Recording Methods
    # ------------------------------------------------------------------

    def record_turn(
        self,
        turn: ContextTurnRecord,
        contributors: List[ContributorMetrics],
        rag_metrics: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Record a complete turn's context metrics.
        
        Returns the turn_id for linking contributor/rag records.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO context_turns (
                    session_id, turn_number, timestamp,
                    query_length_tokens, response_length_tokens, domains,
                    persona, model_used, routing_confidence,
                    cache_hit, cache_similarity,
                    total_context_tokens, budget_utilisation, srs_at_turn,
                    decomposed, sub_query_count,
                    mm_format, mm_reference_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                turn.session_id,
                turn.turn_number,
                datetime.now().isoformat(),
                turn.query_length_tokens,
                turn.response_length_tokens,
                turn.domains,
                turn.persona,
                turn.model_used,
                turn.routing_confidence,
                1 if turn.cache_hit else 0,
                turn.cache_similarity,
                turn.total_context_tokens,
                turn.budget_utilisation,
                turn.srs_at_turn,
                1 if turn.decomposed else 0,
                turn.sub_query_count,
                turn.mm_format,
                turn.mm_reference_rate,
            ))

            turn_id = cursor.lastrowid

            # Contributor records
            for c in contributors:
                cursor.execute("""
                    INSERT INTO context_contributor_turns (
                        turn_id, contributor, items_returned,
                        tokens_allocated, tokens_used, utilisation,
                        top_score, avg_score, items_selected, items_evicted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turn_id, c.contributor, c.items_returned,
                    c.tokens_allocated, c.tokens_used, c.utilisation,
                    c.top_score, c.avg_score, c.items_selected, c.items_evicted,
                ))

            # RAG metrics (optional)
            if rag_metrics:
                cursor.execute("""
                    INSERT INTO context_rag_turns (
                        turn_id, chunks_retrieved, chunks_used, chunks_unused,
                        top_chunk_score, avg_chunk_score, hybrid_enabled,
                        pattern_boosted, pattern_penalised,
                        collections_searched, retrieval_tier
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turn_id,
                    rag_metrics.get("chunks_retrieved", 0),
                    rag_metrics.get("chunks_used", 0),
                    rag_metrics.get("chunks_unused", 0),
                    rag_metrics.get("top_chunk_score", 0.0),
                    rag_metrics.get("avg_chunk_score", 0.0),
                    1 if rag_metrics.get("hybrid_enabled") else 0,
                    rag_metrics.get("pattern_boosted", 0),
                    rag_metrics.get("pattern_penalised", 0),
                    rag_metrics.get("collections_searched", "[]"),
                    rag_metrics.get("retrieval_tier", ""),
                ))

            conn.commit()
            return turn_id

    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------

    def get_aggregated_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get aggregated context metrics over a time period."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main turn stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_turns,
                    AVG(total_context_tokens) as avg_context_tokens,
                    AVG(budget_utilisation) as avg_budget_util,
                    SUM(cache_hit) as cache_hits,
                    AVG(cache_similarity) as avg_cache_sim,
                    SUM(decomposed) as decomposed_turns,
                    AVG(sub_query_count) as avg_sub_queries
                FROM context_turns
                WHERE timestamp > datetime('now', '-' || ? || ' days')
            """, (days,))

            row = cursor.fetchone()
            total_turns = row[0] or 0
            cache_hits = row[3] or 0

            # Contributor breakdown
            cursor.execute("""
                SELECT 
                    cct.contributor,
                    AVG(cct.tokens_used) as avg_tokens,
                    AVG(cct.utilisation) as avg_util,
                    AVG(cct.items_selected) as avg_selected,
                    AVG(cct.items_evicted) as avg_evicted
                FROM context_contributor_turns cct
                JOIN context_turns ct ON cct.turn_id = ct.id
                WHERE ct.timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY cct.contributor
            """, (days,))

            contributor_rows = cursor.fetchall()

            # RAG quality
            cursor.execute("""
                SELECT 
                    AVG(crt.chunks_retrieved) as avg_retrieved,
                    AVG(crt.chunks_used) as avg_used,
                    AVG(crt.pattern_boosted) as avg_boosted
                FROM context_rag_turns crt
                JOIN context_turns ct ON crt.turn_id = ct.id
                WHERE ct.timestamp > datetime('now', '-' || ? || ' days')
            """, (days,))

            rag_row = cursor.fetchone()

            # Routing distribution
            cursor.execute("""
                SELECT routing_confidence, COUNT(*) as count
                FROM context_turns
                WHERE timestamp > datetime('now', '-' || ? || ' days')
                  AND routing_confidence != ''
                GROUP BY routing_confidence
            """, (days,))

            routing_rows = cursor.fetchall()
            routing_dist = {r[0]: r[1] for r in routing_rows}
            total_routed = sum(routing_dist.values()) if routing_dist else 1

            return {
                "period_days": days,
                "total_turns": total_turns,
                "cache_hit_rate": cache_hits / total_turns if total_turns > 0 else 0.0,
                "avg_budget_utilisation": row[2] or 0.0,
                "avg_total_context_tokens": int(row[1] or 0),
                "contributor_breakdown": [
                    {
                        "contributor": r[0],
                        "avg_tokens_used": int(r[1] or 0),
                        "avg_utilisation": r[2] or 0.0,
                        "avg_items_selected": r[3] or 0.0,
                    }
                    for r in contributor_rows
                ],
                "rag_quality": {
                    "avg_chunks_retrieved": rag_row[0] or 0.0,
                    "avg_chunks_used": rag_row[1] or 0.0,
                    "chunk_utilisation_rate": (rag_row[1] / rag_row[0]) if rag_row[0] and rag_row[0] > 0 else 0.0,
                    "avg_pattern_boosted": rag_row[2] or 0.0,
                },
                "routing": {
                    "fast_pct": routing_dist.get("fast", 0) / total_routed,
                    "balanced_pct": routing_dist.get("balanced", 0) / total_routed,
                    "thorough_pct": routing_dist.get("thorough", 0) / total_routed,
                }
            }

    def get_mm_ab_results(self, min_samples: int = 50) -> Dict[str, Any]:
        """
        Analyse A/B results for mental model format validation (Spec 07).

        For each (model_used, mm_format) combination with at least min_samples,
        compute mean mm_reference_rate and produce a recommendation:
          - "full" if full-text reference rate is >10% higher than compact
          - "compact" otherwise (compact is the default — it saves tokens)
          - "inconclusive" if either group lacks min_samples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Aggregate per model_used × mm_format
            cursor.execute("""
                SELECT model_used, mm_format,
                       COUNT(*) as samples,
                       AVG(mm_reference_rate) as mean_rate,
                       MIN(mm_reference_rate) as min_rate,
                       MAX(mm_reference_rate) as max_rate
                FROM context_turns
                WHERE mm_format IS NOT NULL
                  AND mm_reference_rate IS NOT NULL
                GROUP BY model_used, mm_format
                ORDER BY model_used, mm_format
            """)
            rows = cursor.fetchall()

        # Organise by model_used
        by_model: Dict[str, Dict[str, Any]] = {}
        for model_used, mm_format, samples, mean_rate, min_rate, max_rate in rows:
            if model_used not in by_model:
                by_model[model_used] = {}
            by_model[model_used][mm_format] = {
                "samples": samples,
                "mean_reference_rate": round(mean_rate or 0.0, 4),
                "min_reference_rate": round(min_rate or 0.0, 4),
                "max_reference_rate": round(max_rate or 0.0, 4),
            }

        results = {}
        for model_used, formats in by_model.items():
            compact_data = formats.get("compact", {})
            full_data = formats.get("full", {})
            compact_n = compact_data.get("samples", 0)
            full_n = full_data.get("samples", 0)

            if compact_n < min_samples or full_n < min_samples:
                recommendation = "inconclusive"
                reason = f"insufficient_samples (compact={compact_n}, full={full_n}, need={min_samples})"
            else:
                compact_mean = compact_data.get("mean_reference_rate", 0.0)
                full_mean = full_data.get("mean_reference_rate", 0.0)
                if full_mean > compact_mean * 1.10:
                    recommendation = "full"
                    pct = (full_mean / compact_mean - 1) * 100 if compact_mean > 0 else float("inf")
                    reason = f"full_text {full_mean:.3f} > compact {compact_mean:.3f} (+{pct:.0f}%)"
                else:
                    recommendation = "compact"
                    reason = f"compact {compact_mean:.3f} ≥ full {full_mean:.3f} (default to compact)"

            results[model_used] = {
                "recommendation": recommendation,
                "reason": reason,
                "compact": compact_data,
                "full": full_data,
            }

        return {"min_samples_threshold": min_samples, "models": results}

    def get_recent_turns(self, limit: int = 20, session_id: Optional[str] = None) -> List[Dict]:
        """Get recent turn records for debugging."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if session_id:
                cursor.execute("""
                    SELECT id, session_id, turn_number, timestamp,
                           total_context_tokens, budget_utilisation, cache_hit
                    FROM context_turns
                    WHERE session_id = ?
                    ORDER BY turn_number DESC
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor.execute("""
                    SELECT id, session_id, turn_number, timestamp,
                           total_context_tokens, budget_utilisation, cache_hit
                    FROM context_turns
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            return [
                {
                    "turn_id": r[0],
                    "session_id": r[1],
                    "turn_number": r[2],
                    "timestamp": r[3],
                    "total_context_tokens": r[4],
                    "budget_utilisation": r[5],
                    "cache_hit": bool(r[6]),
                }
                for r in rows
            ]


# Global instance
_metrics: Optional[ContextMetrics] = None


def get_context_metrics() -> Optional[ContextMetrics]:
    """Get the global ContextMetrics instance."""
    return _metrics


def init_context_metrics(db_path: Optional[Path] = None) -> ContextMetrics:
    """Initialize the global ContextMetrics instance."""
    global _metrics
    _metrics = ContextMetrics(db_path=db_path)
    return _metrics
