"""
Pattern relevance scoring.

Migrated from Polly._get_patterns_for_prompt() scoring logic.
Scores patterns based on confidence, occurrences, recency, domain match,
and query keyword match to select the most relevant patterns for a context.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Set

from .models import Pattern, PatternType

import logging

logger = logging.getLogger(__name__)


class PatternScorer:
    """
    Scores patterns for relevance to a given query context.

    Scoring dimensions (migrated from Polly._get_patterns_for_prompt):
    1. Confidence weight (0–3 points)
    2. Occurrence weight (0–2 points, capped)
    3. Recency weight (0–2 points)
    4. Domain match (0–3 points)
    5. Query keyword match (0–2 points for query patterns)
    6. Code pattern boost (0–1 point for code-related queries)
    7. Conceptual pattern boost (0–1 point for exploratory queries)
    """

    # Keywords that signal code-related queries
    CODE_KEYWORDS: Set[str] = {
        "code", "function", "class", "implement", "write", "create",
        "pattern", "error", "handling", "debug", "fix", "refactor",
    }

    # Keywords that signal exploratory queries
    EXPLORE_KEYWORDS: Set[str] = {
        "how", "what", "why", "explain", "understand", "learn",
        "explore", "compare", "difference", "between",
    }

    def score(
        self,
        pattern: Pattern,
        query_keywords: Set[str],
        domain_values: List[str],
    ) -> float:
        """
        Score a single pattern for relevance.

        Args:
            pattern: The pattern to score
            query_keywords: Set of lowercased words from the user query
            domain_values: List of detected domain string values

        Returns:
            Relevance score (higher = more relevant)
        """
        score = 0.0

        # 1. Confidence weight (0–3 points)
        score += pattern.confidence * 3

        # 2. Occurrence weight (0–2 points, capped)
        score += min(pattern.occurrences / 10.0, 2.0)

        # 3. Recency weight (0–2 points)
        try:
            days_ago = (datetime.now() - pattern.last_seen).days
            if days_ago <= 7:
                score += 2.0
            elif days_ago <= 30:
                score += 1.0
            elif days_ago <= 90:
                score += 0.5
        except (TypeError, AttributeError):
            pass

        # 4. Domain match (0–3 points)
        if pattern.domains and domain_values:
            matching = set(pattern.domains) & set(domain_values)
            if matching:
                score += min(len(matching) * 1.5, 3.0)

        # 5. Pattern-type-specific boosts
        pt = pattern.pattern_type
        if isinstance(pt, str):
            try:
                pt = PatternType(pt)
            except ValueError:
                pass

        # Query pattern: keyword match (0–2 points)
        if pt == PatternType.QUERY:
            pattern_words = set(pattern.name.lower().split())
            matches = pattern_words & query_keywords
            if matches:
                score += min(len(matches) * 0.5, 2.0)

        # Code pattern: boost for code-related queries (0–1 point)
        if pt == PatternType.CODE:
            if query_keywords & self.CODE_KEYWORDS:
                score += 1.0

        # Conceptual pattern: boost for exploratory queries (0–1 point)
        if pt == PatternType.CONCEPTUAL:
            if query_keywords & self.EXPLORE_KEYWORDS:
                score += 1.0

        return score

    def rank(
        self,
        patterns: List[Pattern],
        query: str,
        domains: List[str],
        limit: int = 5,
    ) -> List[Pattern]:
        """
        Rank patterns by relevance and return the top N.

        Args:
            patterns: All candidate patterns
            query: The user's query text
            domains: Detected domain string values
            limit: Max patterns to return

        Returns:
            Top-N patterns sorted by relevance score (descending)
        """
        if not patterns:
            return []

        query_keywords = set(query.lower().split())

        scored = [
            (self.score(p, query_keywords, domains), p)
            for p in patterns
        ]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [pattern for _score, pattern in scored[:limit]]
