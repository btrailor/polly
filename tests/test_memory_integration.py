"""
Integration tests for Scalable Memory Layers.

Tests the full pipeline: budget allocation → memory retrieval → relevance scoring
→ rolling context → bin-packing → extraction. Uses mocks for Mem0 and LLM calls.
"""

import json
import math
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from core.context.token_counter import TokenCounter
from core.context.budget_allocator import BudgetAllocator, BudgetPlan, SectionBudget
from core.context.relevance_scorer import RelevanceScorer, ScoredEntry
from core.context.rolling_context import RollingContext
from core.memory.tiers import TieredMemoryStore, MemoryTier, MemoryEntry, MemoryMetadata
from core.memory.extractor import SessionExtractor, ExtractedFact, ExtractionResult


# ======================================================================
# Shared mock fixtures
# ======================================================================


class MockMem0Adapter:
    """Mock Mem0 adapter with word-overlap scoring."""

    def __init__(self):
        self._memories = {}  # user_id → list of dicts

    def add_memory(self, content, user_id, metadata=None):
        if user_id not in self._memories:
            self._memories[user_id] = []
        mem_id = f"mem_{user_id}_{len(self._memories[user_id])}"
        entry = {
            "id": mem_id,
            "content": content,
            "user_id": user_id,
            "metadata": metadata or {},
        }
        self._memories[user_id].append(entry)
        return {"id": mem_id}

    def search_memory(self, query, user_id, limit=10):
        results = []
        for mem in self._memories.get(user_id, []):
            query_words = set(query.lower().split())
            content_words = set(mem["content"].lower().split())
            overlap = len(query_words & content_words)
            score = min(overlap / max(len(query_words), 1), 1.0)
            results.append({
                "id": mem["id"],
                "memory": mem["content"],
                "score": score,
                "metadata": mem.get("metadata", {}),
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_all_memories(self, user_id):
        return self._memories.get(user_id, [])

    def reset(self, user_id):
        self._memories.pop(user_id, None)

    def update_memory(self, memory_id, content, metadata=None):
        for user_memories in self._memories.values():
            for mem in user_memories:
                if mem["id"] == memory_id:
                    if content:
                        mem["content"] = content
                    if metadata:
                        mem["metadata"].update(metadata)
                    return


def _make_budget_config():
    """Create a budget allocator config with sections."""
    return {
        "response_reserve": 500,
        "model_context_windows": {
            "default": 8192,
        },
        "sections": {
            "system_prompt": {"priority": 1, "min": 200, "max": 1000, "target_pct": 0.15},
            "rag": {"priority": 2, "min": 100, "max": 3000, "target_pct": 0.30},
            "mental_models": {"priority": 3, "min": 50, "max": 1500, "target_pct": 0.15},
            "memory": {"priority": 4, "min": 50, "max": 1500, "target_pct": 0.15},
            "entities": {"priority": 5, "min": 50, "max": 1000, "target_pct": 0.15},
            "conversation": {"priority": 6, "min": 100, "max": 2000, "target_pct": 0.10},
        },
    }


def _make_scorer_config():
    """Config for RelevanceScorer."""
    return {
        "retrieval_similarity": 0.35,
        "recency": 0.25,
        "reference_frequency": 0.15,
        "domain_affinity": 0.15,
        "tier_weight": 0.10,
    }


def _make_rolling_config():
    """Config for RollingContext."""
    return {
        "decay_per_turn": 0.85,
        "eviction_turns": 5,
        "amplification_reset": True,
    }


def _make_store():
    """Create a TieredMemoryStore with mock adapter."""
    adapter = MockMem0Adapter()
    config = {
        "tiers": {
            "stable": {"collection": "memory_stable"},
            "episodic": {"collection": "memory_episodic", "decay_halflife_days": 90},
            "working": {"collection": "memory_working"},
        },
        "retrieval": {
            "stable_limit": 5,
            "episodic_limit": 5,
            "min_similarity": 0.0,
        },
    }
    store = TieredMemoryStore(mem0_adapter=adapter, config=config)
    store.session_id = "test_session"
    return store, adapter


# ======================================================================
# Test 1: Full Pipeline — Budget → Score → Bin-Pack
# ======================================================================


class TestFullPipeline:
    """Tests the full context assembly pipeline."""

    def test_budget_to_score_to_binpack(self):
        """Budget allocation → scoring → bin-packing produces valid output."""
        # 1. Budget allocation
        allocator = BudgetAllocator(_make_budget_config())
        plan = allocator.allocate(
            model_context_window=8192,
            conversation_tokens=1000,
        )

        assert plan.total_budget == 8192
        total_alloc = plan.total_allocated()
        assert total_alloc > 0
        assert total_alloc <= (8192 - 500 - 1000)  # minus reserve and conversation

        # 2. Simulate context entries from different sources
        scorer = RelevanceScorer(_make_scorer_config())

        entries = [
            ScoredEntry(content="TypeScript is the preferred language for frontend development", source="memory:stable", raw_score=0.85, composite_score=0, token_count=0),
            ScoredEntry(content="The entity manager handles knowledge graph operations", source="entity", raw_score=0.7, composite_score=0, token_count=0),
            ScoredEntry(content="RAG retrieved this document about Python testing best practices", source="rag", raw_score=0.9, composite_score=0, token_count=0),
            ScoredEntry(content="Mental model: teacher-student dynamic for explanation", source="mental_model", raw_score=65.0, composite_score=0, token_count=0),
            ScoredEntry(content="Working memory: user is currently refactoring the API module", source="memory:working", raw_score=0.6, composite_score=0, token_count=0),
        ]

        # Score entries
        for entry in entries:
            entry.token_count = TokenCounter.count(entry.content)
            scorer.score(entry, query_domains=["sigils"], current_turn=1)

        # All entries should have composite scores in [0, 1]
        for entry in entries:
            assert 0.0 <= entry.composite_score <= 1.0
            assert entry.token_count > 0

        # 3. Bin-packing via RollingContext
        rolling = RollingContext(_make_rolling_config(), scorer=scorer)
        rolling.ingest(entries)

        section_budgets = {
            name: sb.allocated for name, sb in plan.sections.items()
        }

        selected = rolling.select(section_budgets)

        # Verify structure
        assert isinstance(selected, dict)
        # Verify no section exceeds its budget
        for section_name, section_entries in selected.items():
            total_tokens = sum(e.token_count for e in section_entries)
            if section_name in section_budgets:
                assert total_tokens <= section_budgets[section_name], (
                    f"Section {section_name} used {total_tokens} tokens but "
                    f"budget was {section_budgets[section_name]}"
                )

    def test_total_context_within_budget(self):
        """Verify the total selected context respects the overall budget."""
        allocator = BudgetAllocator(_make_budget_config())
        plan = allocator.allocate(model_context_window=4096, conversation_tokens=500)

        scorer = RelevanceScorer(_make_scorer_config())
        rolling = RollingContext(_make_rolling_config(), scorer=scorer)

        # Create many entries to stress the budget
        entries = []
        for i in range(20):
            entry = ScoredEntry(
                content=f"Context entry number {i} with some padding text to make it longer " * 3,
                source=["rag", "memory:stable", "entity", "mental_model", "memory:working"][i % 5],
                raw_score=0.5 + (i % 10) * 0.05,
                composite_score=0,
                token_count=0,
            )
            entry.token_count = TokenCounter.count(entry.content)
            scorer.score(entry, query_domains=["sigils"], current_turn=1)
            entries.append(entry)

        rolling.ingest(entries)
        section_budgets = {name: sb.allocated for name, sb in plan.sections.items()}
        selected = rolling.select(section_budgets)

        total_selected_tokens = sum(
            sum(e.token_count for e in entries_list)
            for entries_list in selected.values()
        )
        available_budget = plan.total_budget - plan.response_reserve - 500
        assert total_selected_tokens <= available_budget

    def test_memory_section_present_when_memories_exist(self):
        """When memories exist and are scored, memory section should have entries."""
        store, adapter = _make_store()

        # Write some memories
        store.write("User prefers Python for backend", tier=MemoryTier.STABLE)
        store.write("Currently working on API refactor", tier=MemoryTier.EPISODIC)

        # Read them back
        results = store.read("Python API development", tiers=[MemoryTier.STABLE, MemoryTier.EPISODIC])
        assert len(results) >= 1  # At least the Python one should match

        # Create scored entries from memory results
        scorer = RelevanceScorer(_make_scorer_config())
        entries = []
        for mem_entry in results:
            se = ScoredEntry(
                content=mem_entry.content,
                source=f"memory:{mem_entry.tier.value}",
                raw_score=mem_entry.score,
                composite_score=0,
                token_count=0,
            )
            se.token_count = TokenCounter.count(se.content)
            scorer.score(se, query_domains=["sigils"], current_turn=1)
            entries.append(se)

        rolling = RollingContext(_make_rolling_config(), scorer=scorer)
        rolling.ingest(entries)

        section_budgets = {"memory": 500, "rag": 500, "mental_models": 500, "entities": 500}
        selected = rolling.select(section_budgets)

        # Memory section should be populated
        assert "memory" in selected
        assert len(selected["memory"]) >= 1


# ======================================================================
# Test 2: Session Lifecycle — Write → Read → Extract
# ======================================================================


class TestSessionLifecycle:
    """Tests the full session lifecycle: write → query → extract."""

    def test_preference_stored_and_retrieved(self):
        """A stated preference should be stored and later retrieved."""
        store, _ = _make_store()

        # User states a preference
        store.write(
            content="User prefers TypeScript over JavaScript for all frontend work",
            tier=MemoryTier.STABLE,
            metadata={"domain": "sigils", "source_type": "user_stated", "salience": 0.95},
        )

        # Later, query related to that preference
        results = store.read("What language for frontend?", tiers=[MemoryTier.STABLE])
        assert len(results) >= 1
        assert any("TypeScript" in r.content for r in results)

    def test_working_memory_scoped_to_session(self):
        """Working tier memories are session-scoped."""
        store, adapter = _make_store()
        store.session_id = "session_A"

        store.write("Discussing API design", tier=MemoryTier.WORKING)

        # Can read from same session
        user_id_a = "tier:working:session_A"
        assert len(adapter.get_all_memories(user_id_a)) == 1

        # Flush clears it
        store.flush_working()
        assert len(adapter.get_all_memories(user_id_a)) == 0

    @pytest.mark.asyncio
    async def test_extraction_stores_facts(self):
        """Session extraction should store facts back to the tiered store."""
        store, adapter = _make_store()
        extractor = SessionExtractor(
            tiered_store=store,
            config={"enabled": True, "local_model": "llama3.2:latest"},
        )

        # Simulate a conversation with a clear preference
        conversation = [
            {"role": "user", "content": "I prefer using React over Vue for all my projects"},
            {"role": "assistant", "content": "Noted! I'll keep in mind your preference for React."},
            {"role": "user", "content": "Also, I decided to use PostgreSQL for the database"},
            {"role": "assistant", "content": "Great choice. PostgreSQL is solid for this use case."},
        ]

        # Mock the model call to return structured facts
        mock_facts = [
            ExtractedFact(
                content="User prefers React over Vue for frontend",
                tier="stable",
                source_type="user_stated",
                domain="sigils",
                salience=0.9,
                tags=["preference", "react"],
            ),
            ExtractedFact(
                content="Decided to use PostgreSQL for database",
                tier="episodic",
                source_type="decision",
                domain="sigils",
                salience=0.8,
                tags=["database", "decision"],
            ),
        ]

        with patch.object(extractor, '_call_extraction_model', new_callable=AsyncMock, return_value=mock_facts):
            # Also need to mock deduplicate to return None (no dupes)
            with patch.object(store, 'deduplicate_against', return_value=None):
                result = await extractor.extract_and_store(conversation)

        assert result.stable_count == 1
        assert result.episodic_count == 1

        # Verify facts were written to the correct tiers
        stable_mems = adapter.get_all_memories("tier:stable")
        episodic_mems = adapter.get_all_memories("tier:episodic")
        assert len(stable_mems) >= 1
        assert len(episodic_mems) >= 1

    @pytest.mark.asyncio
    async def test_extraction_flushes_working_tier(self):
        """After extraction, working tier should be flushed."""
        store, adapter = _make_store()
        extractor = SessionExtractor(
            tiered_store=store,
            config={"enabled": True},
        )

        # Add working memory first
        store.write("Session state data", tier=MemoryTier.WORKING)
        working_uid = f"tier:working:{store.session_id}"
        assert len(adapter.get_all_memories(working_uid)) == 1

        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        # Mock to return empty facts (nothing to extract, but flush should still happen)
        with patch.object(extractor, '_call_extraction_model', new_callable=AsyncMock, return_value=[]):
            result = await extractor.extract_and_store(conversation)

        # Working tier should be flushed
        assert len(adapter.get_all_memories(working_uid)) == 0


# ======================================================================
# Test 3: Decay and Amplification Over Multiple Turns
# ======================================================================


class TestDecayAndAmplification:
    """Tests decay, amplification, and eviction behavior."""

    def test_unreferenced_entries_decay(self):
        """Entries not referenced in queries should have reduced scores."""
        scorer = RelevanceScorer(_make_scorer_config())
        rolling = RollingContext(_make_rolling_config(), scorer=scorer)

        entry_a = ScoredEntry(
            content="Topic A is about machine learning models",
            source="rag",
            raw_score=0.8,
            composite_score=0.8,
            token_count=20,
        )
        rolling.ingest([entry_a])

        initial_score = entry_a.composite_score

        # 3 turns about topic B (not referencing topic A)
        for i in range(3):
            rolling.on_new_turn(
                query=f"Tell me about topic B turn {i}",
                response=f"Topic B response {i}",
            )

        # Score should have decayed
        assert entry_a.composite_score < initial_score
        expected = initial_score * (0.85 ** 3)
        assert abs(entry_a.composite_score - expected) < 0.01

    def test_referenced_entries_amplify(self):
        """Entries referenced in conversation should not decay."""
        scorer = RelevanceScorer(_make_scorer_config())
        rolling = RollingContext(_make_rolling_config(), scorer=scorer)

        entry = ScoredEntry(
            content="TypeScript is the preferred language",
            source="memory:stable",
            raw_score=0.8,
            composite_score=0.8,
            token_count=10,
            key_terms=["typescript", "preferred", "language"],
        )
        rolling.ingest([entry])

        initial_score = entry.composite_score

        # Turn that references the entry
        rolling.on_new_turn(
            query="What language should I use? TypeScript?",
            response="Yes, TypeScript is preferred.",
        )

        # Should not have decayed (may have been re-scored)
        assert entry.reference_count == 1
        assert entry.turns_since_reference == 0

    def test_eviction_after_threshold(self):
        """Entries unreferenced for eviction_turns should be removed."""
        rolling = RollingContext({"decay_per_turn": 0.85, "eviction_turns": 3})

        entry = ScoredEntry(
            content="Old topic that becomes irrelevant",
            source="rag",
            raw_score=0.5,
            composite_score=0.5,
            token_count=10,
        )
        rolling.ingest([entry])
        assert len(rolling.entries) == 1

        # Simulate 3 turns without reference
        for i in range(3):
            rolling.on_new_turn(
                query=f"Unrelated query {i}",
                response=f"Unrelated response {i}",
            )

        # Should be evicted
        assert len(rolling.entries) == 0

    def test_topic_transition_decay_vs_new_topic(self):
        """
        After switching from topic A to topic B:
        - Topic A entries should decay
        - Topic B entries should be prominent
        """
        scorer = RelevanceScorer(_make_scorer_config())
        rolling = RollingContext(
            {"decay_per_turn": 0.85, "eviction_turns": 10},
            scorer=scorer,
        )

        # Ingest topic A entries
        entry_a = ScoredEntry(
            content="Machine learning model training pipeline",
            source="rag",
            raw_score=0.9,
            composite_score=0.9,
            token_count=15,
            key_terms=["machine", "learning", "training", "pipeline"],
        )
        rolling.ingest([entry_a])

        # 5 turns about topic B
        for i in range(5):
            rolling.on_new_turn(
                query=f"How do I set up a database schema {i}?",
                response=f"Here's how to design the schema {i}.",
            )

        # Now add topic B entry
        entry_b = ScoredEntry(
            content="Database schema design best practices",
            source="rag",
            raw_score=0.85,
            composite_score=0.85,
            token_count=12,
            key_terms=["database", "schema", "design"],
        )
        rolling.ingest([entry_b])

        # Topic A should be heavily decayed
        assert entry_a.composite_score < 0.5
        # Topic B should be fresh and prominent
        assert entry_b.composite_score > entry_a.composite_score


# ======================================================================
# Test 4: Budget Enforcement Under Pressure
# ======================================================================


class TestBudgetEnforcement:
    """Tests budget enforcement with oversized context."""

    def test_budget_constrains_oversized_context(self):
        """Even with many large entries, budget caps are respected."""
        config = _make_budget_config()
        # Use a small context window to force truncation
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=2048, conversation_tokens=200)

        scorer = RelevanceScorer(_make_scorer_config())
        rolling = RollingContext(_make_rolling_config(), scorer=scorer)

        # Create 50 entries of ~100 tokens each (5000 tokens total)
        entries = []
        for i in range(50):
            sources = ["rag", "memory:stable", "entity", "mental_model", "memory:working"]
            content = f"Entry {i}: " + "word " * 95  # ~100 tokens
            entry = ScoredEntry(
                content=content,
                source=sources[i % len(sources)],
                raw_score=0.5 + (i % 10) * 0.05,
                composite_score=0,
                token_count=0,
            )
            entry.token_count = TokenCounter.count(entry.content)
            scorer.score(entry, query_domains=["sigils"], current_turn=1)
            entries.append(entry)

        rolling.ingest(entries)
        section_budgets = {name: sb.allocated for name, sb in plan.sections.items()}
        selected = rolling.select(section_budgets)

        # Total selected must fit within available budget
        total_selected = sum(
            sum(e.token_count for e in elist)
            for elist in selected.values()
        )
        available = 2048 - 500 - 200  # 1348 tokens available
        assert total_selected <= available

    def test_priority_sections_allocated_under_pressure(self):
        """High-priority sections should still get their minimums under pressure."""
        config = _make_budget_config()
        allocator = BudgetAllocator(config)
        # Very small window
        plan = allocator.allocate(model_context_window=1500, conversation_tokens=0)

        # system_prompt (priority 1) should have at least its min (200)
        assert plan.sections["system_prompt"].allocated >= 200
        # rag (priority 2) should have at least its min (100)
        assert plan.sections["rag"].allocated >= 100

    def test_zero_conversation_tokens_maximizes_context(self):
        """With no conversation history, maximum budget is available."""
        config = _make_budget_config()
        allocator = BudgetAllocator(config)
        plan_no_conv = allocator.allocate(model_context_window=8192, conversation_tokens=0)
        plan_with_conv = allocator.allocate(model_context_window=8192, conversation_tokens=3000)

        assert plan_no_conv.total_allocated() > plan_with_conv.total_allocated()


# ======================================================================
# Test 5: Backward Compatibility
# ======================================================================


class TestBackwardCompatibility:
    """Tests that the system degrades gracefully."""

    def test_rolling_context_empty_entries(self):
        """RollingContext with no entries should return empty selection."""
        rolling = RollingContext(_make_rolling_config())
        selected = rolling.select({"rag": 1000, "memory": 500})
        assert selected == {} or all(len(v) == 0 for v in selected.values())

    def test_budget_plan_zero_budget(self):
        """Zero budget produces zero allocations."""
        allocator = BudgetAllocator(_make_budget_config())
        plan = allocator.allocate(model_context_window=500, conversation_tokens=500)
        # With 500 window and 500 reserve, 0 tokens available
        for sb in plan.sections.values():
            assert sb.allocated == 0

    def test_scorer_works_without_domains(self):
        """Scorer should work when no domains are provided."""
        scorer = RelevanceScorer(_make_scorer_config())
        entry = ScoredEntry(
            content="Some context without domain info",
            source="rag",
            raw_score=0.7,
            composite_score=0,
            token_count=10,
        )
        score = scorer.score(entry, query_domains=None, current_turn=1)
        assert 0.0 <= score <= 1.0
        assert entry.composite_score == score

    def test_scorer_works_with_empty_content(self):
        """Scorer should handle empty content gracefully."""
        scorer = RelevanceScorer(_make_scorer_config())
        entry = ScoredEntry(
            content="",
            source="rag",
            raw_score=0.0,
            composite_score=0,
            token_count=0,
        )
        score = scorer.score(entry, query_domains=["sigils"], current_turn=1)
        assert 0.0 <= score <= 1.0

    def test_tiered_store_write_read_roundtrip(self):
        """Basic write → read roundtrip on all tiers."""
        store, _ = _make_store()

        store.write("Stable fact", tier=MemoryTier.STABLE)
        store.write("Episodic fact", tier=MemoryTier.EPISODIC)
        store.write("Working fact", tier=MemoryTier.WORKING)

        stable = store.read("fact", tiers=[MemoryTier.STABLE])
        episodic = store.read("fact", tiers=[MemoryTier.EPISODIC])
        working = store.read("fact", tiers=[MemoryTier.WORKING])

        assert len(stable) >= 1
        assert len(episodic) >= 1
        assert len(working) >= 1

    @pytest.mark.asyncio
    async def test_disabled_extraction_returns_immediately(self):
        """When extraction is disabled, it should return immediately."""
        store, _ = _make_store()
        extractor = SessionExtractor(
            tiered_store=store,
            config={"enabled": False},
        )
        result = await extractor.extract_and_store([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ])
        assert result.model_used == "disabled"
        assert result.stable_count == 0
        assert result.episodic_count == 0

    def test_dedup_prevents_duplicate_writes(self):
        """Deduplication should detect near-identical content."""
        store, adapter = _make_store()

        # Write initial fact
        store.write("User prefers Python for backend", tier=MemoryTier.STABLE)

        # Try to dedup against it
        existing_id = store.deduplicate_against(
            "User prefers Python for backend",
            MemoryTier.STABLE,
        )
        # Mock adapter returns exact match with score 1.0
        # and dedup threshold is 0.92, so this should match
        assert existing_id is not None


# ======================================================================
# Test 6: Extraction — Tier Classification
# ======================================================================


class TestExtractionTierClassification:
    """Tests the extraction tier classification logic."""

    def test_preference_classified_as_stable(self):
        """Facts with preference signals should be classified as stable."""
        store, _ = _make_store()
        extractor = SessionExtractor(tiered_store=store, config={"enabled": True})

        fact = ExtractedFact(
            content="User prefers dark mode",
            tier="episodic",  # Model said episodic, but classifier should override
            source_type="user_stated",
            domain="general",
            salience=0.8,
        )
        result = extractor._classify_tier(fact)
        assert result == "stable"

    def test_decision_classified_as_episodic(self):
        """Facts with decision/temporal signals should be classified as episodic."""
        store, _ = _make_store()
        extractor = SessionExtractor(tiered_store=store, config={"enabled": True})

        fact = ExtractedFact(
            content="Decided to use PostgreSQL going forward",
            tier="stable",
            source_type="decision",
            domain="sigils",
            salience=0.7,
        )
        # "Decided" is a temporal signal → episodic
        result = extractor._classify_tier(fact)
        assert result == "episodic"

    def test_low_salience_skipped(self):
        """Facts with salience < 0.3 should be skipped."""
        store, _ = _make_store()
        extractor = SessionExtractor(tiered_store=store, config={"enabled": True})

        fact = ExtractedFact(
            content="Something vague",
            tier="episodic",
            source_type="inferred",
            domain="general",
            salience=0.2,
        )
        result = extractor._classify_tier(fact)
        assert result is None

    def test_project_structure_classified_as_stable(self):
        """Facts about project structure should be classified as stable."""
        store, _ = _make_store()
        extractor = SessionExtractor(tiered_store=store, config={"enabled": True})

        fact = ExtractedFact(
            content="The project uses a monorepo architecture with shared libs",
            tier="episodic",
            source_type="inferred",
            domain="sigils",
            salience=0.85,
        )
        result = extractor._classify_tier(fact)
        assert result == "stable"


# ======================================================================
# Test 7: Time Decay for Episodic Memories
# ======================================================================


class TestEpisodicTimeDecay:
    """Tests time-based decay for episodic tier."""

    def test_recent_episodic_minimal_decay(self):
        """Recently created episodic memories should have minimal decay."""
        store, _ = _make_store()

        entry = MemoryEntry(
            content="Recent decision",
            tier=MemoryTier.EPISODIC,
            metadata=MemoryMetadata(
                tier="episodic",
                timestamp=datetime.now().isoformat(),
            ),
            score=0.8,
        )

        decayed_score = store._apply_time_decay(entry)
        # Score should be very close to original (< 1 day old)
        assert decayed_score > 0.79

    def test_old_episodic_significant_decay(self):
        """Episodic memories older than half-life should be significantly decayed."""
        store, _ = _make_store()

        from datetime import timedelta
        old_date = datetime.now() - timedelta(days=90)

        entry = MemoryEntry(
            content="Old decision",
            tier=MemoryTier.EPISODIC,
            metadata=MemoryMetadata(
                tier="episodic",
                timestamp=old_date.isoformat(),
            ),
            score=0.8,
        )

        decayed_score = store._apply_time_decay(entry)
        # At exactly the half-life, score should be ~0.4
        assert abs(decayed_score - 0.4) < 0.05

    def test_no_timestamp_no_decay(self):
        """Entries without a timestamp should not have decay applied."""
        store, _ = _make_store()

        entry = MemoryEntry(
            content="No timestamp",
            tier=MemoryTier.EPISODIC,
            metadata=MemoryMetadata(tier="episodic", timestamp=""),
            score=0.8,
        )

        decayed_score = store._apply_time_decay(entry)
        assert decayed_score == 0.8
