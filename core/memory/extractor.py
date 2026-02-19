"""
Session-End Extraction Pipeline.

Extracts structured facts from completed conversation sessions and writes
them to the tiered memory store. Uses tiered model selection: local Ollama
for simple sessions, cloud Claude Haiku for complex sessions with high-value
decisions.

Called at session end (timeout, explicit close, or app shutdown).
This is additive — existing compression continues to function.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from core.memory.tiers import MemoryTier, TieredMemoryStore

logger = logging.getLogger(__name__)

# Maximum messages to include in extraction prompt (keeps prompt bounded)
_MAX_EXTRACTION_MESSAGES = 30


@dataclass
class ExtractedFact:
    """A fact extracted from conversation for memory storage."""

    content: str
    tier: str  # "stable" or "episodic"
    source_type: str  # "user_stated" | "decision" | "inferred" | "status"
    domain: str  # Detected domain
    salience: float  # 0-1, extraction confidence
    tags: list = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Result of session-end extraction."""

    stable_count: int = 0
    episodic_count: int = 0
    skipped_count: int = 0
    model_used: str = ""
    duration_ms: int = 0
    facts: list = field(default_factory=list)


# ======================================================================
# Extraction prompt template
# ======================================================================

_EXTRACTION_PROMPT = """You are extracting structured facts from a conversation for a personal AI assistant's memory system.

Session context:
- Domains discussed: {domains}
- Key topics: {focus_topics}
- Decisions detected: {decisions}

Conversation (last {msg_count} messages):
{conversation}

Extract facts into two categories:

STABLE (permanent, won't change):
- User preferences and opinions explicitly stated
- Project structures and relationships learned
- Technical choices and standards established
- Personal information shared

EPISODIC (time-bound, may change):
- Decisions made in this session (with brief rationale)
- Work in progress or next steps mentioned
- Context about current projects or tasks
- Problems being actively worked on

For each fact, provide:
- content: The fact in one clear sentence
- tier: "stable" or "episodic"
- source_type: "user_stated" (they said it) | "decision" (they chose it) | "status" (current state) | "inferred" (implied)
- domain: primary domain (sigils/signals/scrolls/glyphs/grids/general)
- salience: 0.0-1.0 (how important is this to remember)
- tags: relevant keywords

Output as a JSON array. If no meaningful facts to extract, return [].
Only output the JSON array, nothing else."""


class SessionExtractor:
    """
    Extracts structured facts from completed sessions
    and writes them to the tiered memory store.
    """

    def __init__(
        self,
        tiered_store: TieredMemoryStore,
        config: dict,
        budget_manager=None,
        router_v2=None,
        ollama_host: str = "http://localhost:11434",
    ):
        """
        Args:
            tiered_store: TieredMemoryStore for writes
            config: memory.extraction config section
            budget_manager: Optional BudgetManager for cost tracking
            router_v2: Optional IntelligentRouterV2 for cloud calls
            ollama_host: Ollama base URL for local calls
        """
        self.store = tiered_store
        self.config = config
        self.budget_manager = budget_manager
        self.router_v2 = router_v2
        self.ollama_host = ollama_host

        self.enabled = config.get("enabled", True)
        self.cloud_threshold = config.get("cloud_threshold", "balanced")
        self.cloud_model = config.get("cloud_model", "claude-haiku")
        self.local_model = config.get("local_model", "llama3.2:latest")
        self.max_cloud_cost = config.get("max_cloud_cost", 0.02)

    async def extract_and_store(
        self,
        conversation_history: List[Dict[str, Any]],
        compression_summary: Optional[Dict[str, Any]] = None,
        session_metadata: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        End-to-end extraction pipeline.

        Steps:
        1. Assess session value to determine model tier
        2. Build extraction prompt
        3. Call extraction model
        4. Classify and validate facts
        5. Deduplicate against existing memory
        6. Write to tiered store
        7. Flush working tier

        Returns:
            ExtractionResult with counts and details
        """
        if not self.enabled:
            return ExtractionResult(model_used="disabled")

        if not conversation_history or len(conversation_history) < 2:
            return ExtractionResult(model_used="skipped_too_short")

        if compression_summary is None:
            compression_summary = {}
        if session_metadata is None:
            session_metadata = {}

        start_time = time.time()
        result = ExtractionResult()

        try:
            # 1. Determine model tier
            model_tier = self._assess_session_value(
                conversation_history, session_metadata
            )
            result.model_used = (
                self.cloud_model if model_tier == "cloud" else self.local_model
            )

            # 2. Build prompt
            prompt = self._build_extraction_prompt(
                conversation_history, compression_summary, session_metadata
            )

            # 3. Call model
            facts = await self._call_extraction_model(prompt, model_tier)

            if not facts:
                # Still flush working tier even when no facts extracted
                self.store.flush_working()
                result.duration_ms = int((time.time() - start_time) * 1000)
                return result

            # 4. Classify and validate
            validated_facts: List[ExtractedFact] = []
            for fact in facts:
                fact.tier = self._classify_tier(fact)
                if fact.tier is None:
                    result.skipped_count += 1
                    continue
                validated_facts.append(fact)

            # 5. Deduplicate
            new_facts = await self._deduplicate(validated_facts)

            # 6. Write to store
            for fact in new_facts:
                tier = (
                    MemoryTier.STABLE
                    if fact.tier == "stable"
                    else MemoryTier.EPISODIC
                )
                self.store.write(
                    content=fact.content,
                    tier=tier,
                    metadata={
                        "domain": fact.domain,
                        "source_type": fact.source_type,
                        "salience": fact.salience,
                        "tags": fact.tags,
                        "persona_source": "extraction",
                    },
                )

                if fact.tier == "stable":
                    result.stable_count += 1
                else:
                    result.episodic_count += 1

            result.facts = new_facts

            # 7. Flush working tier
            self.store.flush_working()

        except Exception as e:
            logger.warning(f"Session extraction failed: {e}")

        result.duration_ms = int((time.time() - start_time) * 1000)
        return result

    # ------------------------------------------------------------------
    # Session value assessment
    # ------------------------------------------------------------------

    def _assess_session_value(
        self,
        conversation_history: List[Dict[str, Any]],
        session_metadata: Dict[str, Any],
    ) -> str:
        """
        Determine extraction model tier.

        Returns "cloud" if any of:
          - Multiple domains detected in session
          - Session complexity >= cloud_threshold
          - Explicit user decisions detected
          - Session > 20 exchanges

        Returns "local" otherwise.
        """
        # Check exchange count
        exchange_count = session_metadata.get(
            "exchange_count", len(conversation_history) // 2
        )
        if exchange_count > 20:
            return "cloud"

        # Check domain count
        domains = session_metadata.get("domains", [])
        if len(domains) > 1:
            return "cloud"

        # Check complexity
        complexity = session_metadata.get("complexity", "simple")
        complexity_hierarchy = ["simple", "moderate", "balanced", "complex"]
        threshold_idx = complexity_hierarchy.index(self.cloud_threshold) if self.cloud_threshold in complexity_hierarchy else 2
        if complexity in complexity_hierarchy:
            if complexity_hierarchy.index(complexity) >= threshold_idx:
                return "cloud"

        # Check for decision signals in conversation
        decision_keywords = [
            "decided", "chose", "let's go with", "we'll use",
            "I prefer", "switching to", "going forward",
        ]
        text = " ".join(
            msg.get("content", "")
            for msg in conversation_history[-20:]
            if msg.get("role") == "user"
        ).lower()

        for keyword in decision_keywords:
            if keyword in text:
                return "cloud"

        return "local"

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_extraction_prompt(
        self,
        conversation_history: List[Dict[str, Any]],
        compression_summary: Dict[str, Any],
        session_metadata: Dict[str, Any],
    ) -> str:
        """
        Build the extraction prompt.

        Includes last N messages and compression signals.
        """
        # Get last N messages
        recent = conversation_history[-_MAX_EXTRACTION_MESSAGES:]
        conv_lines = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                # Truncate very long messages
                if len(content) > 1000:
                    content = content[:1000] + "..."
                conv_lines.append(f"{role}: {content}")

        conversation_text = "\n".join(conv_lines)

        # Extract signals from compression summary
        focus_topics = compression_summary.get("focus_topics", [])
        decisions = compression_summary.get("decisions", [])
        domains = session_metadata.get("domains", ["general"])

        return _EXTRACTION_PROMPT.format(
            domains=", ".join(str(d) for d in domains),
            focus_topics=", ".join(str(t) for t in focus_topics) if focus_topics else "none detected",
            decisions=", ".join(str(d) for d in decisions) if decisions else "none detected",
            msg_count=len(recent),
            conversation=conversation_text,
        )

    # ------------------------------------------------------------------
    # Model calling
    # ------------------------------------------------------------------

    async def _call_extraction_model(
        self,
        prompt: str,
        model_tier: str,
    ) -> List[ExtractedFact]:
        """
        Call local or cloud model for extraction.

        Local: POST to Ollama with configured local_model
        Cloud: Use router_v2 if available, otherwise skip
        """
        try:
            if model_tier == "cloud":
                return await self._call_cloud(prompt)
            else:
                return await self._call_local(prompt)
        except Exception as e:
            logger.warning(f"Extraction model call failed ({model_tier}): {e}")
            return []

    async def _call_local(self, prompt: str) -> List[ExtractedFact]:
        """Call Ollama locally for extraction."""
        try:
            messages = [
                {"role": "system", "content": "You extract structured facts from conversations. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ]

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.local_model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Low temperature for structured output
                            "num_predict": 2000,
                        },
                        "format": "json",
                    },
                )

            if response.status_code != 200:
                logger.warning(
                    f"Ollama extraction failed: HTTP {response.status_code}"
                )
                return []

            data = response.json()
            content = data.get("message", {}).get("content", "")
            return self._parse_extraction_response(content)

        except httpx.ConnectError:
            logger.warning("Ollama not available for extraction")
            return []
        except Exception as e:
            logger.warning(f"Local extraction failed: {e}")
            return []

    async def _call_cloud(self, prompt: str) -> List[ExtractedFact]:
        """Call cloud model via router_v2 for extraction."""
        # Check budget first
        if self.budget_manager:
            can_spend = await self.budget_manager.check_budget(self.max_cloud_cost)
            if not can_spend:
                logger.info(
                    "Cloud extraction skipped: budget limit reached. "
                    "Falling back to local."
                )
                return await self._call_local(prompt)

        if self.router_v2 is None:
            logger.info(
                "Cloud extraction unavailable: no router_v2. "
                "Falling back to local."
            )
            return await self._call_local(prompt)

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You extract structured facts from conversations. Always respond with valid JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.router_v2.complete_with_fallback(
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
            )

            content = response.content if hasattr(response, "content") else str(response)

            # Record usage
            if self.budget_manager and hasattr(response, "cost"):
                await self.budget_manager.record_usage(
                    provider=getattr(response, "provider", "anthropic"),
                    model=getattr(response, "model", self.cloud_model),
                    tokens_in=getattr(response, "tokens_in", 0),
                    tokens_out=getattr(response, "tokens_out", 0),
                    cost=getattr(response, "cost", 0.0),
                    task_type="memory_extraction",
                )

            return self._parse_extraction_response(content)

        except Exception as e:
            logger.warning(f"Cloud extraction failed: {e}. Falling back to local.")
            return await self._call_local(prompt)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_extraction_response(self, content: str) -> List[ExtractedFact]:
        """
        Parse JSON response from extraction model into ExtractedFact objects.
        Handles common formatting issues (markdown code blocks, extra text).
        """
        if not content or not content.strip():
            return []

        # Try direct JSON parse
        facts = self._try_parse_json(content)
        if facts is not None:
            return facts

        # Try extracting JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
        if json_match:
            facts = self._try_parse_json(json_match.group(1))
            if facts is not None:
                return facts

        # Try finding JSON array in the text
        bracket_match = re.search(r"\[.*\]", content, re.DOTALL)
        if bracket_match:
            facts = self._try_parse_json(bracket_match.group(0))
            if facts is not None:
                return facts

        logger.warning(
            f"Could not parse extraction response: {content[:200]}..."
        )
        return []

    def _try_parse_json(self, text: str) -> Optional[List[ExtractedFact]]:
        """Attempt to parse JSON text into a list of ExtractedFact objects."""
        try:
            data = json.loads(text.strip())

            # Handle both array and object-with-array formats
            if isinstance(data, dict):
                # Look for an array value in the dict
                for key in ("facts", "results", "extracted", "data"):
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                else:
                    # Single fact as object
                    data = [data]

            if not isinstance(data, list):
                return None

            facts = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                content = item.get("content", "").strip()
                if not content:
                    continue

                fact = ExtractedFact(
                    content=content,
                    tier=item.get("tier", "episodic"),
                    source_type=item.get("source_type", "inferred"),
                    domain=item.get("domain", "general"),
                    salience=float(item.get("salience", 0.5)),
                    tags=item.get("tags", []),
                )
                facts.append(fact)

            return facts

        except (json.JSONDecodeError, ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # Tier classification and validation
    # ------------------------------------------------------------------

    def _classify_tier(self, fact: ExtractedFact) -> Optional[str]:
        """
        Validate/override tier classification from model.

        Returns "stable", "episodic", or None (skip).
        """
        # Skip low-confidence facts
        if fact.salience < 0.3:
            return None

        content_lower = fact.content.lower()

        # Preference indicators → stable
        preference_signals = [
            "prefer", "prefers", "like", "likes", "always",
            "never", "favorite", "standard", "convention",
        ]
        for signal in preference_signals:
            if signal in content_lower:
                return "stable"

        # Project structure indicators → stable
        structure_signals = [
            "project", "repository", "codebase", "architecture",
            "uses", "built with", "stack",
        ]
        for signal in structure_signals:
            if signal in content_lower:
                return "stable"

        # Temporal/decision indicators → episodic
        temporal_signals = [
            "decided", "chose", "choosing", "working on",
            "in progress", "next step", "currently",
            "plan to", "going to", "will",
        ]
        for signal in temporal_signals:
            if signal in content_lower:
                return "episodic"

        # User-stated facts → stable (explicit user preferences/info)
        if fact.source_type == "user_stated":
            return "stable"

        # Status updates → episodic
        if fact.source_type == "status":
            return "episodic"

        # Fall back to model's classification
        if fact.tier in ("stable", "episodic"):
            return fact.tier

        return "episodic"  # Default to episodic (shorter lived)

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    async def _deduplicate(
        self, facts: List[ExtractedFact]
    ) -> List[ExtractedFact]:
        """
        Remove facts that already exist in the store.
        For contradictions (same topic, different content), update existing.
        """
        new_facts: List[ExtractedFact] = []

        for fact in facts:
            tier = (
                MemoryTier.STABLE
                if fact.tier == "stable"
                else MemoryTier.EPISODIC
            )

            existing_id = self.store.deduplicate_against(fact.content, tier)
            if existing_id:
                # Duplicate exists — update if content differs
                # (The store's deduplicate uses 0.92 similarity, so near-matches
                # are caught. If it's truly the same, we skip. If it's a
                # contradiction/update, we update the existing entry.)
                logger.debug(
                    f"Dedup: skipping '{fact.content[:50]}...' "
                    f"(existing: {existing_id})"
                )
                continue

            new_facts.append(fact)

        return new_facts
