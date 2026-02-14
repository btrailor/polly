"""
Dual-Phenomenology Validation System
Hardened Knowledge Infrastructure — Wave 2

Separate, independent validation of information provenance (source trust)
and content quality.  Both checks run on every RAG retrieval result.
Inspired by the site-checker principle: DNS and HTTP fail independently —
checking both gives a richer picture than either alone.

Design principles:
- Provenance and content are *independent phenomena*
- A document can be authentic (source verified) but contain outdated info
- A claim can be factually correct but from an unreliable source
- Constitutional checks (scapegoat/essentialist detection) trigger deeper
  analysis, NOT blocking — per ethics spec
- Hard blocks reserved for PII and prompt injection only
- Runs as pre-filter before _gather_context(), not as ContextContributor
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
import sqlite3
import json
import logging

from core.hardened.failure import (
    FailureFactory,
    FailureLogger,
    FailureReport,
    FailureCategory,
    FailureSeverity,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trust Levels
# ---------------------------------------------------------------------------

class TrustLevel(Enum):
    """Source trust levels, ordered from most to least trusted."""
    HIGH_TRUST = "HIGH_TRUST"
    MEDIUM_TRUST = "MEDIUM_TRUST"
    LOW_TRUST = "LOW_TRUST"
    VERIFY_REQUIRED = "VERIFY_REQUIRED"
    UNTRUSTED = "UNTRUSTED"


# Default trust assignments for Polly source types
DEFAULT_SOURCE_TRUST: Dict[str, TrustLevel] = {
    "obsidian_vault": TrustLevel.HIGH_TRUST,
    "notes": TrustLevel.HIGH_TRUST,
    "curriculum_exercises": TrustLevel.HIGH_TRUST,
    "github_personal": TrustLevel.HIGH_TRUST,
    "codebase": TrustLevel.HIGH_TRUST,
    "pattern_derived": TrustLevel.MEDIUM_TRUST,
    "entity_graph": TrustLevel.MEDIUM_TRUST,
    "mem0_memories": TrustLevel.MEDIUM_TRUST,
    "github_starred": TrustLevel.MEDIUM_TRUST,
    "documents": TrustLevel.MEDIUM_TRUST,
    "library": TrustLevel.MEDIUM_TRUST,
    "web_search": TrustLevel.VERIFY_REQUIRED,
    "external_api": TrustLevel.LOW_TRUST,
    "unknown": TrustLevel.UNTRUSTED,
}

# Minimum combined score thresholds per trust level
DEFAULT_SCORE_THRESHOLDS: Dict[str, float] = {
    "HIGH_TRUST": 0.7,
    "MEDIUM_TRUST": 0.8,
    "LOW_TRUST": 0.9,
    "VERIFY_REQUIRED": 0.95,
    "UNTRUSTED": 1.0,  # Effectively blocked unless overridden
}


# ---------------------------------------------------------------------------
# Validation Results
# ---------------------------------------------------------------------------

class ValidationStatus(Enum):
    """Outcome of dual-phenomenology validation."""
    VERIFIED = "verified"
    TRUSTED_SOURCE_POOR_CONTENT = "trusted_source_poor_content"
    UNTRUSTED_SOURCE_GOOD_CONTENT = "untrusted_source_good_content"
    REJECTED = "rejected"


@dataclass
class ProvenanceResult:
    """Result of provenance (source trust) validation."""
    score: float                    # 0.0–1.0
    trust_level: TrustLevel
    passed: bool
    source_uri: str = ""
    source_type: str = ""
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentResult:
    """Result of content quality validation."""
    score: float                    # 0.0–1.0
    relevance_score: float = 0.0
    constitutional_pass: bool = True
    passed: bool = True
    reason: str = ""
    warnings: List[str] = field(default_factory=list)
    # If constitutional check detects epistemological concern,
    # this holds the enrichment action (not a block)
    epistemological_enrichment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Combined result of dual validation."""
    status: ValidationStatus
    confidence: float               # 0.0–1.0
    provenance: ProvenanceResult
    content: ContentResult
    reason: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": round(self.confidence, 3),
            "provenance_score": round(self.provenance.score, 3),
            "provenance_trust": self.provenance.trust_level.value,
            "content_score": round(self.content.score, 3),
            "relevance_score": round(self.content.relevance_score, 3),
            "constitutional_pass": self.content.constitutional_pass,
            "reason": self.reason,
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Provenance Validator
# ---------------------------------------------------------------------------

class ProvenanceValidator:
    """
    Verify source authenticity and trustworthiness independent of content.

    Trust is determined by source type (Obsidian vault = HIGH_TRUST,
    web search = VERIFY_REQUIRED, etc.) and can be tracked over time
    in hardened.db.
    """

    def __init__(
        self,
        source_trust: Optional[Dict[str, TrustLevel]] = None,
        score_thresholds: Optional[Dict[str, float]] = None,
    ):
        self.source_trust = source_trust or DEFAULT_SOURCE_TRUST
        self.score_thresholds = score_thresholds or DEFAULT_SCORE_THRESHOLDS

    def check(
        self,
        source_uri: str,
        source_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceResult:
        """
        Check source provenance.

        Args:
            source_uri: Document URI or file path
            source_type: Source type (e.g. 'notes', 'codebase', 'web_search')
            metadata: Additional source metadata

        Returns:
            ProvenanceResult with trust level and score
        """
        meta = metadata or {}
        trust_level = self.source_trust.get(source_type, TrustLevel.UNTRUSTED)

        # Base score from trust level
        trust_scores = {
            TrustLevel.HIGH_TRUST: 0.95,
            TrustLevel.MEDIUM_TRUST: 0.75,
            TrustLevel.LOW_TRUST: 0.5,
            TrustLevel.VERIFY_REQUIRED: 0.3,
            TrustLevel.UNTRUSTED: 0.1,
        }
        score = trust_scores.get(trust_level, 0.1)

        # Adjust score based on metadata signals
        # - Recently modified documents get a small boost
        if meta.get("last_modified"):
            try:
                last_mod = datetime.fromisoformat(str(meta["last_modified"]))
                age_days = (datetime.now() - last_mod).days
                if age_days < 7:
                    score = min(1.0, score + 0.05)
                elif age_days > 365:
                    score = max(0.0, score - 0.1)
            except (ValueError, TypeError):
                pass

        # Check against threshold
        threshold = self.score_thresholds.get(trust_level.value, 0.9)
        passed = score >= threshold

        reason = ""
        if not passed:
            reason = (
                f"Source type '{source_type}' trust level '{trust_level.value}' "
                f"score {score:.2f} below threshold {threshold:.2f}"
            )

        return ProvenanceResult(
            score=score,
            trust_level=trust_level,
            passed=passed,
            source_uri=source_uri,
            source_type=source_type,
            reason=reason,
            metadata=meta,
        )


# ---------------------------------------------------------------------------
# Content Validator
# ---------------------------------------------------------------------------

class ContentValidator:
    """
    Evaluate content quality, relevance, and epistemological alignment
    independent of source.

    Constitutional checks follow the ethics spec:
    - Scapegoat narrative detection → enrich with structural analysis
    - Essentialist claim detection → enrich with material analysis
    - PII detection → hard block (infrastructure security)
    - Prompt injection → hard block (infrastructure security)
    """

    def __init__(
        self,
        min_relevance_score: float = 0.6,
        min_quality_score: float = 0.5,
    ):
        self.min_relevance_score = min_relevance_score
        self.min_quality_score = min_quality_score

    def check(
        self,
        content: str,
        query: str,
        relevance_score: float = 0.0,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContentResult:
        """
        Check content quality and epistemological alignment.

        Args:
            content: Document content or chunk text
            query: User's query for relevance context
            relevance_score: Pre-computed relevance score from RAG
            domain: Active domain for context
            metadata: Additional content metadata

        Returns:
            ContentResult with quality score and constitutional status
        """
        meta = metadata or {}
        warnings: List[str] = []
        constitutional_pass = True
        epistemological_enrichment = None

        # --- Infrastructure security checks (hard blocks) ---
        pii_result = self._check_pii(content)
        if pii_result:
            return ContentResult(
                score=0.0,
                relevance_score=relevance_score,
                constitutional_pass=False,
                passed=False,
                reason=f"PII detected: {pii_result}",
                metadata=meta,
            )

        injection_result = self._check_prompt_injection(content)
        if injection_result:
            return ContentResult(
                score=0.0,
                relevance_score=relevance_score,
                constitutional_pass=False,
                passed=False,
                reason=f"Prompt injection detected: {injection_result}",
                metadata=meta,
            )

        # --- Epistemological alignment checks (enrichment, NOT blocking) ---
        scapegoat = self._check_scapegoat_narrative(content)
        if scapegoat:
            warnings.append(f"Scapegoat narrative pattern: {scapegoat}")
            epistemological_enrichment = "enrich_with_structural_analysis"
            # Note: does NOT set constitutional_pass = False

        essentialist = self._check_essentialist_claims(content)
        if essentialist:
            warnings.append(f"Essentialist claim pattern: {essentialist}")
            epistemological_enrichment = "enrich_with_material_analysis"

        # --- Quality scoring ---
        # Start with relevance score from RAG
        quality_score = relevance_score

        # Adjust for content length (very short = low quality)
        content_len = len(content.strip())
        if content_len < 50:
            quality_score *= 0.5
            warnings.append("Very short content")
        elif content_len < 200:
            quality_score *= 0.8

        # Combined score
        content_score = (relevance_score * 0.6 + quality_score * 0.4)

        # Check thresholds
        passed = (
            content_score >= self.min_quality_score
            and relevance_score >= self.min_relevance_score
        )

        reason = ""
        if not passed and constitutional_pass:
            reason = (
                f"Content score {content_score:.2f} or relevance {relevance_score:.2f} "
                f"below thresholds ({self.min_quality_score}, {self.min_relevance_score})"
            )

        return ContentResult(
            score=content_score,
            relevance_score=relevance_score,
            constitutional_pass=constitutional_pass,
            passed=passed,
            reason=reason,
            warnings=warnings,
            epistemological_enrichment=epistemological_enrichment,
            metadata=meta,
        )

    # --- Infrastructure security checks ---

    def _check_pii(self, content: str) -> Optional[str]:
        """
        Check for personally identifiable information.

        This is an infrastructure security check (hard block), not
        epistemological. Patterns from security_policy.yaml.
        """
        import re

        # Basic PII patterns (can be extended via config)
        patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "api_key_generic": r"\b(?:sk|pk|api)[-_][a-zA-Z0-9]{20,}\b",
        }

        for pii_type, pattern in patterns.items():
            if re.search(pattern, content):
                return pii_type

        return None

    def _check_prompt_injection(self, content: str) -> Optional[str]:
        """
        Check for prompt injection patterns in retrieved content.

        Infrastructure security — content in RAG results shouldn't contain
        injection attempts.
        """
        content_lower = content.lower()

        injection_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard your instructions",
            "you are now",
            "new instructions:",
            "system prompt:",
            "override:",
        ]

        for pattern in injection_patterns:
            if pattern in content_lower:
                return pattern

        return None

    # --- Epistemological alignment checks ---
    # These trigger ENRICHMENT, not blocking. Per ethics spec:
    # "build analytical capacity, don't filter content"

    def _check_scapegoat_narrative(self, content: str) -> Optional[str]:
        """
        Detect scapegoat narrative patterns that would benefit from
        structural analysis enrichment.

        Per ethics spec principle 3: "Arguments structured as 'things are
        bad because of [outgroup]' trigger deeper analysis rather than
        amplification."

        Returns description of detected pattern, or None.
        """
        content_lower = content.lower()

        # These are structural patterns, not keyword blocks
        scapegoat_indicators = [
            "because of immigrants",
            "because of foreigners",
            "they're taking our",
            "they're ruining",
            "they're destroying",
            "invasion of",
            "replace us",
            "great replacement",
        ]

        for indicator in scapegoat_indicators:
            if indicator in content_lower:
                return indicator

        return None

    def _check_essentialist_claims(self, content: str) -> Optional[str]:
        """
        Detect essentialist claims that attribute problems to inherent
        group qualities.

        Per ethics spec principle 1: "When encountering arguments that
        attribute social problems to inherent qualities of groups,
        Polly defaults to structural and historical analysis."

        Returns description of detected pattern, or None.
        """
        content_lower = content.lower()

        # Structural patterns for essentialist claims
        essentialist_indicators = [
            "inherently violent",
            "naturally inferior",
            "biologically determined",
            "genetically predisposed to crime",
            "racial iq",
            "born criminals",
        ]

        for indicator in essentialist_indicators:
            if indicator in content_lower:
                return indicator

        return None


# ---------------------------------------------------------------------------
# Dual Validator — combines provenance and content
# ---------------------------------------------------------------------------

class DualValidator:
    """
    Dual-phenomenology validation: independent provenance and content checks
    run on every RAG retrieval result.

    Integration point: runs between UnifiedRAG.search() and _gather_context()
    as a pre-filter. Only VERIFIED and (optionally) UNTRUSTED_SOURCE_GOOD_CONTENT
    results enter the context pipeline.
    """

    def __init__(
        self,
        provenance_validator: Optional[ProvenanceValidator] = None,
        content_validator: Optional[ContentValidator] = None,
        failure_logger: Optional[FailureLogger] = None,
    ):
        self.provenance = provenance_validator or ProvenanceValidator()
        self.content = content_validator or ContentValidator()
        self.failure_logger = failure_logger or FailureLogger()

    def validate(
        self,
        content: str,
        query: str,
        source_uri: str,
        source_type: str,
        relevance_score: float = 0.0,
        domain: Optional[str] = None,
        source_metadata: Optional[Dict[str, Any]] = None,
        content_metadata: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Run dual validation on a single retrieval result.

        Args:
            content: Document content or chunk text
            query: User's query
            source_uri: Document URI or path
            source_type: Source type for trust lookup
            relevance_score: Pre-computed relevance from RAG
            domain: Active domain
            source_metadata: Additional source metadata
            content_metadata: Additional content metadata

        Returns:
            ValidationResult with combined status and scores
        """
        # Run both checks independently
        prov_result = self.provenance.check(
            source_uri=source_uri,
            source_type=source_type,
            metadata=source_metadata,
        )
        cont_result = self.content.check(
            content=content,
            query=query,
            relevance_score=relevance_score,
            domain=domain,
            metadata=content_metadata,
        )

        # Combine results
        warnings = list(cont_result.warnings)

        if prov_result.passed and cont_result.passed:
            return ValidationResult(
                status=ValidationStatus.VERIFIED,
                confidence=min(prov_result.score, cont_result.score),
                provenance=prov_result,
                content=cont_result,
                warnings=warnings,
            )

        if prov_result.passed and not cont_result.passed:
            # Log but don't use — source is good but content is not
            if not cont_result.constitutional_pass:
                # Security block
                self.failure_logger.log_failure(
                    FailureFactory.pii_detected(
                        pii_type="content_check",
                        context=cont_result.reason,
                    )
                    if "PII" in cont_result.reason
                    else FailureFactory.prompt_injection_detected(
                        pattern=cont_result.reason,
                    ),
                    operation="dual_validation",
                    domain=domain,
                )

            return ValidationResult(
                status=ValidationStatus.TRUSTED_SOURCE_POOR_CONTENT,
                confidence=0.0,
                provenance=prov_result,
                content=cont_result,
                reason=cont_result.reason,
                warnings=warnings,
            )

        if not prov_result.passed and cont_result.passed:
            # Content looks good but source untrusted — penalize confidence
            return ValidationResult(
                status=ValidationStatus.UNTRUSTED_SOURCE_GOOD_CONTENT,
                confidence=cont_result.score * 0.5,
                provenance=prov_result,
                content=cont_result,
                reason=prov_result.reason,
                warnings=warnings + [
                    "Content appears valid but source is not fully trusted"
                ],
            )

        # Both failed
        return ValidationResult(
            status=ValidationStatus.REJECTED,
            confidence=0.0,
            provenance=prov_result,
            content=cont_result,
            reason=(
                f"Provenance: {prov_result.reason}; "
                f"Content: {cont_result.reason}"
            ),
            warnings=warnings,
        )

    def validate_batch(
        self,
        results: List[Dict[str, Any]],
        query: str,
        domain: Optional[str] = None,
    ) -> List[Tuple[Dict[str, Any], ValidationResult]]:
        """
        Validate a batch of RAG results.

        Each result dict should have:
          - content: str
          - source_uri: str (or 'uri', 'path', 'source')
          - source_type: str
          - relevance_score: float (or 'score', 'distance')

        Returns list of (original_result, validation) tuples.
        """
        validated = []
        for result in results:
            # Normalize field names for flexibility
            content = result.get("content", result.get("text", ""))
            source_uri = result.get(
                "source_uri",
                result.get("uri", result.get("path", result.get("source", ""))),
            )
            source_type = result.get("source_type", "unknown")
            relevance_score = result.get(
                "relevance_score",
                result.get("score", result.get("distance", 0.0)),
            )

            validation = self.validate(
                content=content,
                query=query,
                source_uri=source_uri,
                source_type=source_type,
                relevance_score=relevance_score,
                domain=domain,
                source_metadata=result.get("metadata"),
            )

            validated.append((result, validation))

        return validated

    def filter_verified(
        self,
        results: List[Dict[str, Any]],
        query: str,
        domain: Optional[str] = None,
        include_untrusted_good_content: bool = True,
    ) -> Tuple[List[Dict[str, Any]], List[ValidationResult]]:
        """
        Filter RAG results to only verified content.

        Returns:
            (filtered_results, all_validations)
        """
        validated = self.validate_batch(results, query, domain)

        filtered = []
        all_validations = []
        for result, validation in validated:
            all_validations.append(validation)

            if validation.status == ValidationStatus.VERIFIED:
                filtered.append(result)
            elif (
                include_untrusted_good_content
                and validation.status == ValidationStatus.UNTRUSTED_SOURCE_GOOD_CONTENT
            ):
                filtered.append(result)

        return filtered, all_validations
