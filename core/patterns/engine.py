"""
Unified Pattern Engine for Polly.

Replaces both learners/patterns.PatternLearner and core/pattern_learning.PatternLearner
with a single engine that uses pluggable storage backends (JSON + optional Mem0).

Core responsibilities:
- Learn patterns from queries, compressed conversations, code, and domain interactions
- Search patterns via keyword (JSON) and semantic (Mem0) search
- Score and rank patterns for prompt injection
- Manage pattern lifecycle (decay, pruning)
- Manage specialized pattern types (QueryChunkPattern, DomainPriorityPattern)
"""

from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .models import (
    DomainPriorityPattern,
    Pattern,
    PatternQuery,
    PatternType,
    QueryChunkPattern,
    generate_pattern_id,
)
from .scorer import PatternScorer
from .storage.json_backend import JSONBackend
from .storage.mem0_backend import Mem0Backend

logger = logging.getLogger(__name__)


def _domains_to_strings(domains) -> List[str]:
    """Convert domains to list of strings, handling DomainType enums and strings."""
    if not domains:
        return []
    result = []
    for d in domains:
        if hasattr(d, "value"):
            result.append(d.value)
        elif isinstance(d, str):
            result.append(d)
    return result


class PatternEngine:
    """
    Unified pattern learning and retrieval engine.

    Usage:
        engine = PatternEngine(
            json_path=Path("~/.polly/patterns.json"),
            mem0_config=config_dict if mem0_enabled else None
        )

        # Learn from a query
        engine.learn_from_query(query, domains, response)

        # Search patterns
        results = engine.search(PatternQuery(text="docker", limit=5))

        # Get patterns for prompt injection
        top_patterns = engine.get_patterns_for_prompt(query, domains)

        # Save to disk
        engine.save()
    """

    def __init__(
        self,
        json_path: Path,
        mem0_config: Optional[Dict[str, Any]] = None,
    ):
        # Primary storage (always active)
        self.json_backend = JSONBackend(json_path)

        # Semantic storage (optional)
        self.mem0_backend: Optional[Mem0Backend] = None
        if mem0_config:
            self.mem0_backend = Mem0Backend(mem0_config)

        # Scorer for ranking patterns
        self._scorer = PatternScorer()

        # Tracking for pattern discovery (migrated from learners/patterns.py)
        self._concept_mentions: Counter = Counter()
        self._cross_domain_pairs: Counter = Counter()

        # Persona context (set by integration-contracts later)
        self._active_persona: Optional[str] = None
        self._active_mode: Optional[str] = None

    # ========== Properties ==========

    @property
    def patterns(self) -> Dict[str, Pattern]:
        """Direct access to pattern cache (backward compatibility)."""
        return self.json_backend.load_all()

    @property
    def query_chunk_patterns(self) -> Dict[str, QueryChunkPattern]:
        return self.json_backend.query_chunk_patterns

    @property
    def domain_priority_patterns(self) -> Dict[str, DomainPriorityPattern]:
        return self.json_backend.domain_priority_patterns

    @property
    def query_history(self) -> List[Dict[str, Any]]:
        return self.json_backend.query_history

    # ========== Learning API ==========

    def learn(self, pattern: Pattern) -> Pattern:
        """
        Learn a new pattern or reinforce an existing one.

        If a matching pattern exists (same ID or same type + similar description),
        reinforces it (increment occurrences, boost confidence).
        Otherwise creates a new pattern.

        Saves to all active backends.
        """
        existing = self.json_backend.load_all().get(pattern.id)

        if existing:
            # Reinforce existing pattern
            now = datetime.now()

            # Apply decay if stale
            days_since = (now - existing.last_seen).days
            if days_since > 60:
                decay = 0.98 ** (days_since - 60)
                existing.confidence *= decay

            existing.occurrences += 1
            existing.last_seen = now
            existing.domains = list(set(existing.domains + pattern.domains))

            # Merge examples
            for ex in pattern.examples:
                if ex not in existing.examples:
                    existing.examples.append(ex)
                    if len(existing.examples) > 10:
                        existing.examples = existing.examples[-10:]

            # Recalculate confidence — can recover from decay
            new_confidence = min(existing.occurrences / 10, 1.0)
            if new_confidence > existing.confidence:
                existing.confidence = new_confidence

            # Merge metadata
            existing.metadata.update(pattern.metadata)

            self.json_backend.save(existing)
            if self.mem0_backend:
                self.mem0_backend.save(existing)

            return existing
        else:
            # New pattern
            self.json_backend.save(pattern)
            if self.mem0_backend:
                self.mem0_backend.save(pattern)

            logger.info(
                f"Learned new pattern: [{pattern.pattern_type.value if isinstance(pattern.pattern_type, PatternType) else pattern.pattern_type}] {pattern.name}"
            )
            return pattern

    def learn_from_query(
        self,
        query: str,
        domains,
        response: Optional[str] = None,
    ) -> List[Pattern]:
        """
        Extract and learn patterns from a query-response pair.

        Migrated from learners/patterns.PatternLearner.record_query().
        """
        domain_strs = _domains_to_strings(domains)
        now = datetime.now()
        learned: List[Pattern] = []

        # Record in query history
        self.json_backend.append_query_history(
            {
                "query": query,
                "domains": domain_strs,
                "timestamp": now.isoformat(),
                "persona": self._active_persona,
            }
        )

        # Track cross-domain connections
        if len(domain_strs) > 1:
            for i, d1 in enumerate(domain_strs):
                for d2 in domain_strs[i + 1 :]:
                    pair = tuple(sorted([d1, d2]))
                    self._cross_domain_pairs[pair] += 1

                    # Create conceptual pattern for cross-domain connection
                    if self._cross_domain_pairs[pair] >= 3:
                        pid = generate_pattern_id("conceptual", f"{pair[0]}_{pair[1]}_connection")
                        meta: Dict[str, Any] = {}
                        if self._active_persona:
                            meta["persona"] = self._active_persona
                            meta["mode"] = self._active_mode or ""
                        p = Pattern(
                            id=pid,
                            pattern_type=PatternType.CONCEPTUAL,
                            name=f"{pair[0]}↔{pair[1]} connection",
                            description=f"Cross-domain pattern connecting {pair[0]} and {pair[1]}",
                            confidence=min(self._cross_domain_pairs[pair] / 20.0, 0.9),
                            occurrences=self._cross_domain_pairs[pair],
                            first_seen=now,
                            last_seen=now,
                            domains=list(pair),
                            source="observation",
                            metadata=meta,
                        )
                        self.learn(p)
                        learned.append(p)

        return learned

    def learn_from_compressed(
        self,
        compressed_data: dict,
        conversation_id: str,
        rag_metadata: Optional[dict] = None,
    ) -> Dict[str, int]:
        """
        Learn RAG optimization patterns from compressed conversation data.

        Migrated from learners/patterns.PatternLearner.learn_from_compressed().
        """
        counts = {
            "query_chunk_patterns": 0,
            "domain_priority_patterns": 0,
            "total": 0,
        }

        try:
            # Learn from RAG metadata (highest value)
            if rag_metadata:
                for query_data in rag_metadata.get("queries", []):
                    query_text = query_data.get("query", "")
                    chunk_ids = query_data.get("chunks", [])
                    collections = query_data.get("collections", [])

                    if query_text and chunk_ids:
                        query_sig = self._create_query_signature(query_text)
                        pattern_id = f"qcp_{query_sig}"

                        existing = self.json_backend.query_chunk_patterns.get(pattern_id)
                        if existing:
                            existing.total_queries += 1
                            existing.last_seen = datetime.now()
                            for cid in chunk_ids[:5]:
                                found = False
                                for sc in existing.successful_chunks:
                                    if sc["chunk_id"] == cid:
                                        sc["hit_count"] += 1
                                        found = True
                                        break
                                if not found:
                                    existing.successful_chunks.append(
                                        {
                                            "chunk_id": cid,
                                            "collection": collections[0] if collections else "unknown",
                                            "hit_count": 1,
                                            "avg_score": 0.8,
                                        }
                                    )
                            existing.confidence = min(1.0, 0.5 + existing.total_queries * 0.05)
                            self.json_backend.save_query_chunk_pattern(existing)
                        else:
                            qcp = QueryChunkPattern(
                                pattern_id=pattern_id,
                                query_template=query_text,
                                query_signature=query_sig,
                                successful_chunks=[
                                    {
                                        "chunk_id": cid,
                                        "collection": collections[0] if collections else "unknown",
                                        "hit_count": 1,
                                        "avg_score": 0.8,
                                    }
                                    for cid in chunk_ids[:5]
                                ],
                                total_queries=1,
                                confidence=0.6,
                                first_seen=datetime.now(),
                                last_seen=datetime.now(),
                            )
                            self.json_backend.save_query_chunk_pattern(qcp)
                        counts["query_chunk_patterns"] += 1

                # Learn domain→collection patterns
                for domain in rag_metadata.get("domains", []):
                    collections_used: Set[str] = set()
                    for qd in rag_metadata.get("queries", []):
                        collections_used.update(qd.get("collections", []))

                    if collections_used:
                        pattern_id = f"domain_priority_{domain}"
                        existing_dpp = self.json_backend.domain_priority_patterns.get(pattern_id)

                        if existing_dpp:
                            existing_dpp.total_queries += len(rag_metadata.get("queries", []))
                            for coll in collections_used:
                                existing_dpp.collection_weights[coll] = (
                                    existing_dpp.collection_weights.get(coll, 0) + 0.1
                                )
                            # Normalize
                            total_w = sum(existing_dpp.collection_weights.values())
                            if total_w > 0:
                                existing_dpp.collection_weights = {
                                    k: v / total_w
                                    for k, v in existing_dpp.collection_weights.items()
                                }
                            existing_dpp.confidence = min(1.0, 0.5 + existing_dpp.total_queries * 0.02)
                            existing_dpp.last_seen = datetime.now()
                            self.json_backend.save_domain_priority_pattern(existing_dpp)
                        else:
                            weights = {c: 1.0 / len(collections_used) for c in collections_used}
                            dpp = DomainPriorityPattern(
                                pattern_id=pattern_id,
                                domain=domain,
                                collection_weights=weights,
                                collection_stats={},
                                total_queries=len(rag_metadata.get("queries", [])),
                                confidence=0.6,
                                first_seen=datetime.now(),
                                last_seen=datetime.now(),
                            )
                            self.json_backend.save_domain_priority_pattern(dpp)
                        counts["domain_priority_patterns"] += 1

            counts["total"] = sum(v for v in counts.values() if isinstance(v, int))
            return counts

        except Exception as e:
            logger.error(f"Error learning from compressed data: {e}")
            return counts

    def learn_domain_priorities(
        self,
        query: str,
        domain: str,
        collection_scores: Dict[str, float],
    ) -> None:
        """
        Learn domain→collection priority weights from search results.

        Migrated from learners/patterns.PatternLearner.learn_domain_priorities().
        """
        pattern_id = f"dpp_{domain}"
        now = datetime.now()

        existing = self.json_backend.domain_priority_patterns.get(pattern_id)
        if existing:
            existing.total_queries += 1
            existing.last_seen = now

            # Update stats
            for coll, score in collection_scores.items():
                if coll not in existing.collection_stats:
                    existing.collection_stats[coll] = {"queries": 0, "hits": 0, "avg_score": 0.0}
                stats = existing.collection_stats[coll]
                stats["queries"] += 1
                if score > 0:
                    stats["hits"] += 1
                    stats["avg_score"] = (
                        stats["avg_score"] * (stats["hits"] - 1) + score
                    ) / stats["hits"]

            # Recalculate weights from stats
            total_hits = sum(s.get("hits", 0) for s in existing.collection_stats.values())
            if total_hits > 0:
                existing.collection_weights = {
                    coll: stats.get("hits", 0) / total_hits
                    for coll, stats in existing.collection_stats.items()
                    if stats.get("hits", 0) > 0
                }

            existing.confidence = min(1.0, 0.5 + existing.total_queries * 0.02)
            self.json_backend.save_domain_priority_pattern(existing)
        else:
            weights = {}
            stats = {}
            for coll, score in collection_scores.items():
                weights[coll] = 1.0 if score > 0 else 0.0
                stats[coll] = {"queries": 1, "hits": 1 if score > 0 else 0, "avg_score": score}

            # Normalize
            total_w = sum(weights.values())
            if total_w > 0:
                weights = {k: v / total_w for k, v in weights.items()}

            dpp = DomainPriorityPattern(
                pattern_id=pattern_id,
                domain=domain,
                collection_weights=weights,
                collection_stats=stats,
                total_queries=1,
                confidence=0.5,
                first_seen=now,
                last_seen=now,
            )
            self.json_backend.save_domain_priority_pattern(dpp)

    def learn_code_patterns(self, code: str, domains, filepath: str = "") -> List[Pattern]:
        """
        Extract code patterns from source code.

        Migrated from learners/patterns.PatternLearner._analyze_code_patterns().
        """
        domain_strs = _domains_to_strings(domains)
        learned: List[Pattern] = []
        now = datetime.now()

        patterns_to_detect = [
            ("error_handling", r"try\s*:.*except|\.catch\(|if err != nil", "Error Handling Pattern", "Consistent error handling approach"),
            ("async_pattern", r"async\s+(?:def|function)|await\s+", "Async/Await Pattern", "Asynchronous programming pattern"),
            ("factory_pattern", r"def\s+create_\w+|function\s+make\w+|fn\s+new_\w+", "Factory Pattern", "Object/instance creation pattern"),
            ("callback_pattern", r"on_\w+\s*=|\.on\(|callback\s*[=:]", "Callback Pattern", "Event-driven callback pattern"),
            ("midi_handling", r"midi_?\w*|note_?on|note_?off|cc_?\d*", "MIDI Handling Pattern", "MIDI event processing"),
            ("state_machine", r"state\s*=|set_?state|current_?state", "State Machine Pattern", "State management pattern"),
        ]

        for pid, regex, name, desc in patterns_to_detect:
            if re.search(regex, code, re.IGNORECASE):
                pattern = Pattern(
                    id=pid,
                    pattern_type=PatternType.CODE,
                    name=name,
                    description=desc,
                    confidence=0.5,
                    occurrences=1,
                    first_seen=now,
                    last_seen=now,
                    domains=domain_strs,
                    examples=[code[:200]],
                    source="extraction",
                    metadata={"filepath": filepath} if filepath else {},
                )
                result = self.learn(pattern)
                learned.append(result)

        return learned

    def record_pattern_usage(self, pattern_id: str, was_helpful: bool = True) -> None:
        """Record that a pattern was used and whether it was helpful."""
        all_patterns = self.json_backend.load_all()
        pattern = all_patterns.get(pattern_id)
        if pattern:
            pattern.times_used += 1
            if was_helpful:
                pattern.times_helpful += 1
            self.json_backend.save(pattern)

    # ========== Search API ==========

    def search(self, query: PatternQuery) -> List[Pattern]:
        """Search patterns across all backends, merge and deduplicate."""
        # Get from JSON backend (primary)
        results = self.json_backend.search(query)
        seen_ids = {p.id for p in results}

        # Merge Mem0 semantic results if available and text query provided
        if self.mem0_backend and query.text:
            mem0_results = self.mem0_backend.search_semantic(query.text, limit=query.limit)
            for p in mem0_results:
                if p.id not in seen_ids:
                    # Apply query filters
                    if query.pattern_types and p.pattern_type not in query.pattern_types:
                        continue
                    if query.domains and not set(p.domains or []) & set(query.domains):
                        continue
                    if p.confidence < query.min_confidence and not query.include_decayed:
                        continue
                    results.append(p)
                    seen_ids.add(p.id)

        # Sort by confidence, then occurrences
        results.sort(key=lambda p: (p.confidence, p.occurrences), reverse=True)
        return results[: query.limit]

    def search_semantic(self, text: str, limit: int = 10) -> List[Pattern]:
        """Semantic search — Mem0 when available, keyword fallback."""
        if self.mem0_backend:
            results = self.mem0_backend.search_semantic(text, limit=limit)
            if results:
                return results

        # Fallback to keyword search
        return self.json_backend.search(PatternQuery(text=text, limit=limit))

    def get_patterns_for_prompt(
        self,
        query: str,
        domains: List[str],
        limit: int = 5,
    ) -> List[Pattern]:
        """
        Get most relevant patterns for system prompt injection.

        Uses the PatternScorer to rank all patterns by relevance.
        Boosts patterns attributed to the active persona when set.
        """
        # Gather all candidate patterns
        all_patterns = list(self.json_backend.load_all().values())

        # Merge Mem0 semantic results
        if self.mem0_backend:
            try:
                mem0_results = self.mem0_backend.search_semantic(query, limit=limit * 2)
                seen_ids = {p.id for p in all_patterns}
                for p in mem0_results:
                    if p.id not in seen_ids:
                        all_patterns.append(p)
                        seen_ids.add(p.id)
            except Exception as e:
                logger.debug(f"Mem0 search for prompt patterns failed (non-critical): {e}")

        if not all_patterns:
            return []

        ranked = self._scorer.rank(all_patterns, query, domains, limit=limit * 2)
        # Boost persona-specific patterns when active persona is set
        if self._active_persona:
            ranked = sorted(
                ranked,
                key=lambda p: (
                    0.3 if p.metadata.get("persona") == self._active_persona else 0,
                    p.confidence,
                    p.occurrences,
                ),
                reverse=True,
            )
        return ranked[:limit]

    def get_conceptual_patterns(self, concept: str) -> List[Pattern]:
        """Get cross-concept connection patterns for a concept."""
        results = []
        concept_lower = concept.lower()

        for p in self.json_backend.load_all().values():
            pt = p.pattern_type
            if isinstance(pt, str):
                try:
                    pt = PatternType(pt)
                except ValueError:
                    continue
            if pt != PatternType.CONCEPTUAL:
                continue
            if concept_lower in p.name.lower() or concept_lower in p.description.lower():
                results.append(p)

        results.sort(key=lambda p: p.confidence, reverse=True)
        return results

    def get_domain_priorities(self, domain: str) -> Dict[str, float]:
        """Get learned collection weights for a domain."""
        pattern_id = f"dpp_{domain}"
        dpp = self.json_backend.domain_priority_patterns.get(pattern_id)
        if dpp:
            return dict(dpp.collection_weights)
        return {}

    # ========== ContextContributor (integration-contracts) ==========

    context_priority = 20

    def build_context(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        user_name: str = "the user",
        **kwargs: object,
    ) -> str:
        """Build learned-patterns context block for system prompt (ContextContributor)."""
        domain_values = [d if isinstance(d, str) else getattr(d, "value", str(d)) for d in (domains or [])]
        relevant = self.get_patterns_for_prompt(query, domain_values, limit=5)
        if not relevant:
            return ""
        parts = ["\n\n## Learned Patterns from Your Work\n", f"You've observed these patterns in how {user_name} works:\n\n"]
        for p in relevant:
            pt = p.pattern_type
            pt_val = pt.value if hasattr(pt, "value") else pt
            if pt_val == "query":
                parts.append(f"- **{p.name}**: You ask this type of question often (seen {p.occurrences} times)\n")
            elif pt_val == "code":
                parts.append(f"- **{p.name}**: {p.description} (found in {p.occurrences} files)\n")
                if p.examples:
                    parts.append(f"  Example: `{p.examples[0][:150]}...`\n")
            elif pt_val == "conceptual":
                parts.append(f"- **{p.name}**: {p.description}\n")
            elif pt_val == "workflow":
                parts.append(f"- **{p.name}**: {p.description} (observed {p.occurrences} times)\n")
            else:
                parts.append(f"- **{p.name}**: {p.description}\n")
        parts.append("\nUse these patterns to anticipate needs, reference familiar tools/concepts, and provide more relevant responses.\n")
        return "".join(parts)

    def get_persona_patterns(self, persona_name: str, limit: int = 50) -> List[Pattern]:
        """Return patterns attributed to the given persona (for persona↔entity affinity)."""
        all_p = list(self.json_backend.load_all().values())
        persona_patterns = [p for p in all_p if p.metadata.get("persona") == persona_name]
        persona_patterns.sort(key=lambda p: (p.confidence, p.occurrences), reverse=True)
        return persona_patterns[:limit]

    def get_persona_context(self, persona_name: str, mode: str) -> Dict[str, Any]:
        """Return persona-specific context (e.g. pattern counts)."""
        persona_patterns = self.get_persona_patterns(persona_name)
        return {"pattern_count": len(persona_patterns), "persona": persona_name, "mode": mode}

    # ========== Persona Context (for integration-contracts) ==========

    def set_active_persona(self, persona_name: str, mode: str) -> None:
        """Set the active persona context. Patterns learned will be attributed."""
        self._active_persona = persona_name
        self._active_mode = mode

    # ========== Lifecycle API ==========

    def decay(self, half_life_days: int = 30) -> int:
        """Apply time-based confidence decay. Returns count of decayed patterns."""
        now = datetime.now()
        decayed = 0
        all_patterns = self.json_backend.load_all()

        for pattern in all_patterns.values():
            days_since = (now - pattern.last_seen).days
            if days_since > 60:
                decay_factor = 0.98 ** (days_since - 60)
                old_conf = pattern.confidence
                pattern.confidence *= decay_factor
                if pattern.confidence < old_conf * 0.95:
                    self.json_backend.save(pattern)
                    decayed += 1

        return decayed

    def prune(self, min_confidence: float = 0.05, min_occurrences: int = 1) -> int:
        """Remove low-value patterns. Returns count pruned."""
        pruned = 0
        all_patterns = self.json_backend.load_all()
        to_delete = []

        for pid, pattern in all_patterns.items():
            if pattern.confidence < min_confidence and pattern.occurrences <= min_occurrences:
                to_delete.append(pid)

        for pid in to_delete:
            self.json_backend.delete(pid)
            pruned += 1

        if pruned > 0:
            logger.info(f"Pruned {pruned} low-quality patterns")

        return pruned

    def save(self) -> None:
        """Flush all changes to all backends."""
        # Prune before saving
        self.prune()
        self.json_backend.flush()
        # Mem0 writes are immediate, no flush needed

    def get_stats(self) -> Dict[str, Any]:
        """Get pattern statistics."""
        all_patterns = self.json_backend.load_all()

        stats: Dict[str, Any] = {
            "total_patterns": len(all_patterns),
            "by_type": {},
            "avg_confidence": 0.0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "query_chunk_patterns": len(self.json_backend.query_chunk_patterns),
            "domain_priority_patterns": len(self.json_backend.domain_priority_patterns),
            "has_mem0": self.mem0_backend is not None,
        }

        if not all_patterns:
            return stats

        confidences = []
        for p in all_patterns.values():
            pt_val = p.pattern_type.value if isinstance(p.pattern_type, PatternType) else p.pattern_type
            stats["by_type"][pt_val] = stats["by_type"].get(pt_val, 0) + 1
            confidences.append(p.confidence)

        stats["avg_confidence"] = sum(confidences) / len(confidences)
        stats["high_confidence"] = sum(1 for c in confidences if c >= 0.8)
        stats["medium_confidence"] = sum(1 for c in confidences if 0.5 <= c < 0.8)
        stats["low_confidence"] = sum(1 for c in confidences if c < 0.5)

        return stats

    def export(self) -> Dict[str, Any]:
        """Export all patterns for analysis."""
        all_patterns = self.json_backend.load_all()
        return {
            "patterns": [p.to_dict() for p in all_patterns.values()],
            "query_chunk_patterns": [
                qcp.to_dict() for qcp in self.json_backend.query_chunk_patterns.values()
            ],
            "domain_priority_patterns": [
                dpp.to_dict() for dpp in self.json_backend.domain_priority_patterns.values()
            ],
            "stats": self.get_stats(),
            "exported_at": datetime.now().isoformat(),
        }

    # ========== Internal Helpers ==========

    @staticmethod
    def _create_query_signature(query: str) -> str:
        """Create a normalized signature for query deduplication."""
        words = re.sub(r"[^a-z0-9\s]", "", query.lower()).split()
        # Remove very common words
        stop = {"the", "a", "an", "is", "are", "was", "were", "to", "in", "on", "for", "of", "with", "and", "or", "i"}
        filtered = [w for w in words if w not in stop]
        return "_".join(filtered[:8])
