"""
Unified Pattern Engine for Polly

Consolidates pattern learning, storage, and retrieval into a single system.
Replaces both learners/patterns.py and core/pattern_learning.py.

Usage:
    from core.patterns import PatternEngine, Pattern, PatternType, PatternQuery

    engine = PatternEngine(json_path=Path("~/.polly/patterns.json"))
    engine.learn_from_query(query, domains, response)
    results = engine.search(PatternQuery(text="docker patterns", limit=5))
"""

from .models import (
    Pattern,
    PatternType,
    PatternQuery,
    QueryChunkPattern,
    DomainPriorityPattern,
)
from .engine import PatternEngine

__all__ = [
    "PatternEngine",
    "Pattern",
    "PatternType",
    "PatternQuery",
    "QueryChunkPattern",
    "DomainPriorityPattern",
]
