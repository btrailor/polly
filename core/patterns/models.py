"""
Unified Pattern data models.

Merges the Pattern models from:
- learners/patterns.py (rich: id, name, pattern_type, domains, examples, times_used/helpful)
- core/pattern_learning.py (simple: type, description, confidence, timestamp, metadata)

Into a single model that supports all use cases.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """All pattern categories supported by the unified engine."""

    # Core types (from both old systems)
    ROUTING = "routing"
    USER_PREFERENCE = "user_preference"
    TASK_TYPE = "task_type"
    DOMAIN = "domain"
    PERSONA = "persona"

    # From learners/patterns.py
    CONCEPTUAL = "conceptual"
    QUERY = "query"
    CODE = "code"
    DOMAIN_PRIORITY = "domain_priority"

    # Planned (for integration-contracts phase)
    WORKFLOW = "workflow"
    AESTHETIC = "aesthetic"
    ROUTING_OUTCOME = "routing_outcome"


@dataclass
class Pattern:
    """
    A learned interaction pattern — unified model.

    Merges fields from both learners/patterns.Pattern and
    core/pattern_learning.Pattern into one coherent model.
    """

    id: str
    pattern_type: PatternType
    name: str
    description: str

    # Confidence & frequency
    confidence: float  # 0.0–1.0
    occurrences: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    # Activation context
    domains: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # Rich data
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Usefulness tracking (from learners/patterns.py Phase 13A)
    times_used: int = 0
    times_helpful: int = 0

    # Relationships (foundation for entity-model-unification)
    related_patterns: List[str] = field(default_factory=list)
    entity_refs: List[str] = field(default_factory=list)

    # Source tracking
    source: str = "observation"  # "observation", "extraction", "compression", "user"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        data = {
            "id": self.id,
            "pattern_type": self.pattern_type.value if isinstance(self.pattern_type, PatternType) else self.pattern_type,
            "name": self.name,
            "description": self.description,
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "first_seen": self.first_seen.isoformat() if isinstance(self.first_seen, datetime) else self.first_seen,
            "last_seen": self.last_seen.isoformat() if isinstance(self.last_seen, datetime) else self.last_seen,
            "domains": self.domains,
            "keywords": self.keywords,
            "examples": self.examples,
            "metadata": self.metadata,
            "times_used": self.times_used,
            "times_helpful": self.times_helpful,
            "related_patterns": self.related_patterns,
            "entity_refs": self.entity_refs,
            "source": self.source,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pattern":
        """Create Pattern from dict, handling datetime parsing and enum conversion."""
        # Parse datetimes
        for dt_field in ("first_seen", "last_seen"):
            val = data.get(dt_field)
            if isinstance(val, str):
                try:
                    data[dt_field] = datetime.fromisoformat(val)
                except (ValueError, TypeError):
                    data[dt_field] = datetime.now()
            elif val is None:
                data[dt_field] = datetime.now()

        # Parse pattern_type to enum
        pt = data.get("pattern_type", "query")
        if isinstance(pt, str):
            try:
                data["pattern_type"] = PatternType(pt)
            except ValueError:
                data["pattern_type"] = PatternType.QUERY

        # Only pass known fields to constructor
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    @property
    def usefulness_ratio(self) -> float:
        """Ratio of helpful uses to total uses (0.0 if never used)."""
        if self.times_used == 0:
            return 0.0
        return self.times_helpful / self.times_used


def generate_pattern_id(pattern_type: str, name: str) -> str:
    """Generate a deterministic, stable pattern ID."""
    raw = f"{pattern_type}:{name.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ============================================================================
# Specialized pattern types (migrated from learners/patterns.py)
# These keep their dedicated dataclasses because they have unique schemas.
# ============================================================================


@dataclass
class QueryChunkPattern:
    """
    Pattern linking queries to successful RAG chunks.

    Tracks which document chunks successfully answer queries, enabling:
    - Faster RAG by directly boosting known-good chunks
    - Pattern-based chunk scoring before semantic search
    """

    pattern_id: str
    query_template: str
    query_signature: str
    successful_chunks: List[Dict[str, Any]]  # [{chunk_id, collection, hit_count, avg_score}]
    total_queries: int
    confidence: float
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "query_template": self.query_template,
            "query_signature": self.query_signature,
            "successful_chunks": self.successful_chunks,
            "total_queries": self.total_queries,
            "confidence": self.confidence,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueryChunkPattern":
        for dt_field in ("first_seen", "last_seen"):
            val = data.get(dt_field)
            if isinstance(val, str):
                data[dt_field] = datetime.fromisoformat(val)
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in cls.__dataclass_fields__.values()}})


@dataclass
class DomainPriorityPattern:
    """
    Pattern tracking collection priorities per domain.

    Learns which RAG collections are relevant for each domain, enabling:
    - Faster RAG by skipping irrelevant collections
    - Dynamic collection weights
    """

    pattern_id: str
    domain: str
    collection_weights: Dict[str, float]
    collection_stats: Dict[str, Dict[str, Any]]
    total_queries: int
    confidence: float
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "domain": self.domain,
            "collection_weights": self.collection_weights,
            "collection_stats": self.collection_stats,
            "total_queries": self.total_queries,
            "confidence": self.confidence,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainPriorityPattern":
        for dt_field in ("first_seen", "last_seen"):
            val = data.get(dt_field)
            if isinstance(val, str):
                data[dt_field] = datetime.fromisoformat(val)
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in cls.__dataclass_fields__.values()}})


@dataclass
class PatternQuery:
    """Query object for searching patterns."""

    text: Optional[str] = None
    pattern_types: Optional[List[PatternType]] = None
    domains: Optional[List[str]] = None
    min_confidence: float = 0.0
    limit: int = 10
    include_decayed: bool = False
