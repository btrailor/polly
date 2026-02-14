"""
Three-Tier Retrieval Classification
Hardened Knowledge Infrastructure — Wave 2

Replace binary found/not-found with three-tier system that reveals
retrieval quality and guides next actions.

Inspired by the site-checker's DNS-ONLY category: the middle state
where DNS resolves but no HTTP response is where interesting findings
live.  Polly's equivalent: partial matches, tangential knowledge,
stale connections.

Tiers:
  DIRECT   — High-confidence answer from verified source
  ADJACENT — Related information exists, but query needs refinement
  ABSENT   — No relevant information in knowledge base

Design:
- Domain-aware: cross-domain matches are ADJACENT even if scores are high
- Integrates with DualValidator results
- Suggests next actions per tier (external search, query refinement, etc.)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
import logging

from core.hardened.validator import ValidationResult, ValidationStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retrieval Tiers
# ---------------------------------------------------------------------------

class RetrievalTier(Enum):
    """Three-tier retrieval classification."""
    DIRECT = "direct"       # High-confidence, verified answer
    ADJACENT = "adjacent"   # Related but not a direct answer
    ABSENT = "absent"       # No relevant information


# ---------------------------------------------------------------------------
# Tier Results
# ---------------------------------------------------------------------------

@dataclass
class TierResult:
    """Result of retrieval classification."""
    tier: RetrievalTier
    confidence: float                       # 0.0–1.0
    results: List[Dict[str, Any]] = field(default_factory=list)
    validations: List[ValidationResult] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "confidence": round(self.confidence, 3),
            "result_count": len(self.results),
            "suggestions": self.suggestions,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# Retrieval Classifier
# ---------------------------------------------------------------------------

class RetrievalClassifier:
    """
    Classify retrieval results into DIRECT / ADJACENT / ABSENT tiers.

    Configuration:
        direct_threshold:   Minimum score for DIRECT classification (default 0.8)
        adjacent_threshold: Minimum score for ADJACENT classification (default 0.5)
        domain_match_boost: Boost for results matching query domain (default 0.1)
        cross_domain_penalty: Penalty for cross-domain results (default 0.15)

    Usage:
        classifier = RetrievalClassifier()
        tier_result = classifier.classify(
            query="How does Docker networking work?",
            results=rag_results_as_dicts,
            validations=validation_results,
            query_domains=["Sigils"],
        )
    """

    def __init__(
        self,
        direct_threshold: float = 0.8,
        adjacent_threshold: float = 0.5,
        domain_match_boost: float = 0.1,
        cross_domain_penalty: float = 0.15,
    ):
        self.direct_threshold = direct_threshold
        self.adjacent_threshold = adjacent_threshold
        self.domain_match_boost = domain_match_boost
        self.cross_domain_penalty = cross_domain_penalty

    def classify(
        self,
        query: str,
        results: List[Dict[str, Any]],
        validations: Optional[List[ValidationResult]] = None,
        query_domains: Optional[List[str]] = None,
    ) -> TierResult:
        """
        Classify retrieval results into a tier.

        Args:
            query: User's query
            results: RAG retrieval results (dicts with score, content, etc.)
            validations: Optional DualValidator results (parallel list)
            query_domains: Detected domains for the query

        Returns:
            TierResult with tier, confidence, filtered results, and suggestions
        """
        if not results:
            return self._absent_result(
                query=query,
                reason="No documents retrieved",
                docs_searched=0,
            )

        # Score each result with domain awareness
        scored = self._score_results(results, validations, query_domains)

        if not scored:
            return self._absent_result(
                query=query,
                reason="All results filtered out by validation",
                docs_searched=len(results),
            )

        # Sort by adjusted score (descending)
        scored.sort(key=lambda x: x["adjusted_score"], reverse=True)
        best = scored[0]

        # --- Classify ---
        if best["adjusted_score"] >= self.direct_threshold:
            direct_results = [
                s for s in scored
                if s["adjusted_score"] >= self.direct_threshold
            ]
            return TierResult(
                tier=RetrievalTier.DIRECT,
                confidence=best["adjusted_score"],
                results=[s["result"] for s in direct_results],
                validations=[
                    s["validation"] for s in direct_results
                    if s.get("validation")
                ],
                reason="High-confidence answer from verified sources",
                metadata={
                    "total_scored": len(scored),
                    "direct_count": len(direct_results),
                    "best_score": round(best["adjusted_score"], 3),
                },
            )

        if best["adjusted_score"] >= self.adjacent_threshold:
            adjacent_results = [
                s for s in scored
                if s["adjusted_score"] >= self.adjacent_threshold
            ]
            suggestions = self._generate_refinement_suggestions(
                query, adjacent_results, query_domains
            )
            return TierResult(
                tier=RetrievalTier.ADJACENT,
                confidence=best["adjusted_score"],
                results=[s["result"] for s in adjacent_results],
                validations=[
                    s["validation"] for s in adjacent_results
                    if s.get("validation")
                ],
                suggestions=suggestions,
                reason="Related information found but not a direct answer",
                metadata={
                    "total_scored": len(scored),
                    "adjacent_count": len(adjacent_results),
                    "best_score": round(best["adjusted_score"], 3),
                },
            )

        # Below adjacent threshold
        return self._absent_result(
            query=query,
            reason=self._diagnose_absence(scored),
            docs_searched=len(results),
            best_score=best["adjusted_score"],
            similar_topics=self._extract_topics(scored[:3]),
        )

    def _score_results(
        self,
        results: List[Dict[str, Any]],
        validations: Optional[List[ValidationResult]],
        query_domains: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Score results with domain awareness and validation integration.

        Returns list of dicts with:
          result, validation, base_score, adjusted_score, domain_match
        """
        scored = []
        query_domain_set = set(d.lower() for d in (query_domains or []))

        for i, result in enumerate(results):
            # Base score from RAG
            base_score = float(
                result.get("score", result.get("relevance_score",
                           result.get("distance", 0.0)))
            )

            # Validation integration
            validation = None
            if validations and i < len(validations):
                validation = validations[i]
                # Skip REJECTED results entirely
                if validation.status == ValidationStatus.REJECTED:
                    continue
                # Penalize untrusted sources
                if validation.status == ValidationStatus.UNTRUSTED_SOURCE_GOOD_CONTENT:
                    base_score *= 0.7
                elif validation.status == ValidationStatus.TRUSTED_SOURCE_POOR_CONTENT:
                    continue  # Skip — trusted source but bad content

            adjusted_score = base_score

            # Domain awareness
            result_domain = (
                result.get("domain", result.get("collection", ""))
            ).lower()
            domain_match = False

            if query_domain_set and result_domain:
                if result_domain in query_domain_set:
                    # Matching domain — boost
                    adjusted_score = min(1.0, adjusted_score + self.domain_match_boost)
                    domain_match = True
                else:
                    # Cross-domain — penalize
                    adjusted_score = max(0.0, adjusted_score - self.cross_domain_penalty)

            scored.append({
                "result": result,
                "validation": validation,
                "base_score": base_score,
                "adjusted_score": adjusted_score,
                "domain_match": domain_match,
            })

        return scored

    def _absent_result(
        self,
        query: str,
        reason: str,
        docs_searched: int = 0,
        best_score: float = 0.0,
        similar_topics: Optional[List[str]] = None,
    ) -> TierResult:
        """Construct an ABSENT tier result with helpful suggestions."""
        suggestions = [
            "Search external sources for this information",
            "Add relevant documents to your knowledge base",
        ]
        if similar_topics:
            suggestions.append(
                f"Related topics I know about: {', '.join(similar_topics)}"
            )

        return TierResult(
            tier=RetrievalTier.ABSENT,
            confidence=0.0,
            suggestions=suggestions,
            reason=reason,
            metadata={
                "docs_searched": docs_searched,
                "best_score": round(best_score, 3),
                "similar_topics": similar_topics or [],
            },
        )

    def _generate_refinement_suggestions(
        self,
        query: str,
        adjacent_results: List[Dict[str, Any]],
        query_domains: Optional[List[str]],
    ) -> List[str]:
        """Generate query refinement suggestions from adjacent results."""
        suggestions = []

        # Check if it's a domain mismatch
        cross_domain_results = [
            r for r in adjacent_results if not r.get("domain_match", True)
        ]
        if cross_domain_results:
            domains_found = set()
            for r in cross_domain_results:
                d = r["result"].get("domain", r["result"].get("collection", ""))
                if d:
                    domains_found.add(d)
            if domains_found:
                suggestions.append(
                    f"I found related content in {', '.join(domains_found)} "
                    f"but not in your queried domain"
                )

        # Suggest narrowing
        if len(adjacent_results) > 5:
            suggestions.append("Try being more specific to narrow results")

        # Suggest broadening
        if len(adjacent_results) <= 2:
            suggestions.append("Try broadening your query for more results")

        # Suggest external search
        suggestions.append("Would you like me to search external sources?")

        return suggestions

    def _diagnose_absence(self, scored: List[Dict[str, Any]]) -> str:
        """Diagnose why results didn't meet thresholds."""
        if not scored:
            return "No scored results"

        best = scored[0]
        if best["adjusted_score"] < 0.2:
            return "No relevant documents in knowledge base"
        elif best["adjusted_score"] < self.adjacent_threshold:
            return (
                f"Best match scored {best['adjusted_score']:.2f} — "
                f"below adjacent threshold ({self.adjacent_threshold})"
            )
        return "Results below classification thresholds"

    def _extract_topics(self, scored_results: List[Dict[str, Any]]) -> List[str]:
        """Extract topic hints from low-scoring results for suggestions."""
        topics = []
        for s in scored_results:
            result = s["result"]
            # Try to get a meaningful topic from the result
            title = result.get("title", result.get("source", ""))
            if title and len(title) < 100:
                topics.append(title)
        return topics[:3]
