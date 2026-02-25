"""
Tests for Persona Memory — Enrichment Preferences (Core Framework Wave 4, Task #24)

Tests cover:
- _get_enrichment_preferences(): Mem0 read path, dedup, score filtering, formatting
- _get_pattern_context(): PatternEngine read path, formatting
- _record_enrichment_feedback(): write-back: template/domain, linking, structure memories
- Edit pattern detection logic (link removals, expansion, condensing, structural changes)
"""

import re
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime


# ===================== Fixtures =====================


def make_scribe(mem0=None, pattern_engine=None):
    """Create a minimal ScribePersona with mocked dependencies."""
    from core.personas.implementations.scribe import ScribePersona

    mock_router = Mock()
    scribe = ScribePersona(
        name="scribe",
        router=mock_router,
        skill_manager=None,
        rag=None,
        pattern_engine=pattern_engine,
    )
    # Bypass full Mem0 initialization — inject mock directly
    scribe.mem0 = mem0
    return scribe


def make_mem0_result(text: str, score: float = 0.9) -> dict:
    """Create a Mem0-style search result dict."""
    return {"memory": text, "score": score, "id": "test-id"}


# ===================== _get_enrichment_preferences =====================


class TestGetEnrichmentPreferences:
    """Tests for ScribePersona._get_enrichment_preferences()."""

    def test_returns_empty_when_no_mem0(self):
        scribe = make_scribe(mem0=None)
        result = scribe._get_enrichment_preferences("scrolls", "tutorial")
        assert result == ""

    def test_makes_three_queries(self):
        mock_mem0 = Mock()
        mock_mem0.search_memory.return_value = []
        scribe = make_scribe(mem0=mock_mem0)

        scribe._get_enrichment_preferences("scrolls", "tutorial")

        # Domain query, template query, edit feedback query
        assert mock_mem0.search_memory.call_count == 3

    def test_only_two_queries_when_template_is_standalone(self):
        """Template query is skipped when template_name == 'standalone'."""
        mock_mem0 = Mock()
        mock_mem0.search_memory.return_value = []
        scribe = make_scribe(mem0=mock_mem0)

        scribe._get_enrichment_preferences("scrolls", "standalone")

        assert mock_mem0.search_memory.call_count == 2

    def test_returns_empty_when_no_memories(self):
        mock_mem0 = Mock()
        mock_mem0.search_memory.return_value = []
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("scrolls", "tutorial")
        assert result == ""

    def test_filters_low_score_memories(self):
        """Memories with score < 0.5 should be excluded from output."""
        mock_mem0 = Mock()
        low_score = make_mem0_result("Low confidence memory", score=0.3)
        high_score = make_mem0_result("High confidence memory", score=0.8)
        mock_mem0.search_memory.return_value = [low_score, high_score]
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("scrolls", "standalone")

        assert "Low confidence memory" not in result
        assert "High confidence memory" in result

    def test_deduplicates_by_memory_text(self):
        """Same memory returned from multiple queries should appear only once."""
        mock_mem0 = Mock()
        dup = make_mem0_result("User prefers sparse linking", score=0.9)
        mock_mem0.search_memory.side_effect = [[dup], [dup]]  # Two queries, same result
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("scrolls", "standalone")

        # Memory text should appear exactly once
        assert result.count("User prefers sparse linking") == 1

    def test_formats_with_header(self):
        """Output should include the standardized header block."""
        mock_mem0 = Mock()
        mock_mem0.search_memory.return_value = [
            make_mem0_result("User prefers concise notes", score=0.85)
        ]
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("workshop", "standalone")

        assert "## User Enrichment Preferences" in result
        assert "User prefers concise notes" in result

    def test_caps_at_six_preferences(self):
        """Should not inject more than 6 preferences to avoid prompt bloat."""
        mock_mem0 = Mock()
        memories = [make_mem0_result(f"Preference {i}", score=0.9) for i in range(10)]
        mock_mem0.search_memory.return_value = memories
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("workshop", "standalone")

        # Count bullet points in output
        bullet_count = result.count("\n-")
        assert bullet_count <= 6

    def test_handles_mem0_exception_gracefully(self):
        """Should return empty string if Mem0 raises."""
        mock_mem0 = Mock()
        mock_mem0.search_memory.side_effect = RuntimeError("Mem0 offline")
        scribe = make_scribe(mem0=mock_mem0)

        result = scribe._get_enrichment_preferences("scrolls", "tutorial")
        assert result == ""


# ===================== _get_pattern_context =====================


class TestGetPatternContext:
    """Tests for ScribePersona._get_pattern_context()."""

    def test_returns_empty_when_no_pattern_engine(self):
        scribe = make_scribe(pattern_engine=None)
        result = scribe._get_pattern_context("Python decorators", "workshop")
        assert result == ""

    def test_returns_empty_when_no_patterns_found(self):
        mock_engine = Mock()
        mock_engine.get_patterns_for_prompt.return_value = []
        scribe = make_scribe(pattern_engine=mock_engine)

        result = scribe._get_pattern_context("Python decorators", "workshop")
        assert result == ""

    def test_formats_patterns_with_context_block(self):
        """Output should include a recognizable context block header."""
        mock_engine = Mock()
        # _get_pattern_context accesses p.pattern_type.value, p.confidence, p.description
        mock_pattern = Mock()
        mock_pattern.pattern_type = Mock()
        mock_pattern.pattern_type.value = "domain"
        mock_pattern.confidence = 0.9
        mock_pattern.description = "Use 'workshop' for technical notes"
        mock_engine.get_patterns_for_prompt.return_value = [mock_pattern]
        scribe = make_scribe(pattern_engine=mock_engine)

        result = scribe._get_pattern_context("decorators", "workshop")
        assert result  # non-empty
        assert "## Relevant Patterns" in result
        assert "workshop" in result.lower() or "technical" in result.lower()

    def test_handles_pattern_engine_exception_gracefully(self):
        """Should return empty string if PatternEngine raises."""
        mock_engine = Mock()
        mock_engine.get_patterns_for_prompt.side_effect = RuntimeError("DB locked")
        scribe = make_scribe(pattern_engine=mock_engine)

        result = scribe._get_pattern_context("decorators", "workshop")
        assert result == ""


# ===================== _record_enrichment_feedback =====================


class TestRecordEnrichmentFeedback:
    """Tests for ScribePersona._record_enrichment_feedback()."""

    def _call_feedback(self, scribe, domain="scrolls", template="tutorial", content=None, links=None, tags=None):
        """Helper to call _record_enrichment_feedback with defaults."""
        if content is None:
            content = "# Test Note\n\nSome content here with [[Link A]] and [[Link B]].\n\n## Summary\n\nMore text."
        if links is None:
            links = {"inserted": ["Link A", "Link B"]}
        scribe._record_enrichment_feedback(
            title="Test Note",
            domain=domain,
            template_name=template,
            content=content,
            inserted_links=links,
            tags=tags or [],
        )

    def test_noop_when_no_mem0(self):
        scribe = make_scribe(mem0=None)
        # Should not raise
        self._call_feedback(scribe)

    def test_always_stores_template_domain_memory(self):
        mock_mem0 = Mock()
        scribe = make_scribe(mem0=mock_mem0)
        scribe._add_memory = Mock()

        self._call_feedback(scribe, domain="scrolls", template="tutorial")

        # At least one call should be for template_domain
        call_metadata = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        subtypes = [m.get("subtype") for m in call_metadata]
        assert "template_domain" in subtypes

    def test_stores_linking_style_when_links_present(self):
        mock_mem0 = Mock()
        scribe = make_scribe(mem0=mock_mem0)
        scribe._add_memory = Mock()

        content = "Note with [[Link A]] and [[Link B]] and [[Link C]]."
        self._call_feedback(scribe, content=content)

        subtypes = [c.kwargs.get("metadata", {}).get("subtype") for c in scribe._add_memory.call_args_list]
        assert "linking_style" in subtypes

    def test_skips_linking_style_when_no_links(self):
        mock_mem0 = Mock()
        scribe = make_scribe(mem0=mock_mem0)
        scribe._add_memory = Mock()

        content = "Note with no wiki-links at all."
        self._call_feedback(scribe, content=content)

        subtypes = [c.kwargs.get("metadata", {}).get("subtype") for c in scribe._add_memory.call_args_list]
        assert "linking_style" not in subtypes

    def test_always_stores_structure_style_memory(self):
        mock_mem0 = Mock()
        scribe = make_scribe(mem0=mock_mem0)
        scribe._add_memory = Mock()

        self._call_feedback(scribe)

        subtypes = [c.kwargs.get("metadata", {}).get("subtype") for c in scribe._add_memory.call_args_list]
        assert "structure_style" in subtypes

    # --- Length preference categorization ---

    def test_concise_length_category(self):
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        # < 300 words
        content = " ".join(["word"] * 200)
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["length_preference"] == "concise"

    def test_moderate_length_category(self):
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        # 300-800 words
        content = " ".join(["word"] * 500)
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["length_preference"] == "moderate"

    def test_detailed_length_category(self):
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        # >= 800 words
        content = " ".join(["word"] * 900)
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["length_preference"] == "detailed"

    # --- Link density categorization ---

    def test_no_link_density(self):
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        content = "No links here."
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["link_density"] == "none"

    def test_sparse_link_density(self):
        """1-3 links → sparse."""
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        content = "Has [[Link A]] and [[Link B]]."
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["link_density"] == "sparse"

    def test_moderate_link_density(self):
        """4-7 links → moderate."""
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        links = " ".join(f"[[Link {i}]]" for i in range(5))
        content = f"Many links: {links}."
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["link_density"] == "moderate"

    def test_dense_link_density(self):
        """8+ links → dense."""
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock()
        links = " ".join(f"[[Link {i}]]" for i in range(9))
        content = f"Dense: {links}."
        self._call_feedback(scribe, content=content)

        metadata_list = [c.kwargs.get("metadata", {}) for c in scribe._add_memory.call_args_list]
        td = next(m for m in metadata_list if m.get("subtype") == "template_domain")
        assert td["link_density"] == "dense"

    def test_handles_exception_gracefully(self):
        """Should not propagate exceptions."""
        scribe = make_scribe(mem0=Mock())
        scribe._add_memory = Mock(side_effect=RuntimeError("Mem0 write failed"))
        # Should not raise
        self._call_feedback(scribe)


# ===================== Edit Pattern Detection Logic =====================
# These tests exercise the diff logic from _track_edit_patterns by replicating
# the same regex/arithmetic patterns used in interfaces/server.py.


class TestEditPatternDetectionLogic:
    """
    Unit tests for the edit-diff logic in _track_edit_patterns.
    Tests use the same computation as the server function directly.
    """

    def _compute_diff(self, old: str, new: str):
        """Mirror the diff computation from _track_edit_patterns."""
        old_links = set(re.findall(r'\[\[(.+?)(?:\|.+?)?\]\]', old))
        new_links = set(re.findall(r'\[\[(.+?)(?:\|.+?)?\]\]', new))
        removed_links = old_links - new_links
        added_links = new_links - old_links

        old_words = len(old.split())
        new_words = len(new.split())
        word_delta = new_words - old_words
        word_pct_change = (word_delta / max(old_words, 1)) * 100

        old_headings = re.findall(r'^#{1,6}\s+(.+)$', old, re.MULTILINE)
        new_headings = re.findall(r'^#{1,6}\s+(.+)$', new, re.MULTILINE)

        return {
            "removed_links": removed_links,
            "added_links": added_links,
            "word_delta": word_delta,
            "word_pct_change": word_pct_change,
            "old_headings": old_headings,
            "new_headings": new_headings,
        }

    def test_detects_link_removal(self):
        old = "Note with [[Link A]] and [[Link B]]."
        new = "Note with [[Link A]]."
        diff = self._compute_diff(old, new)
        assert "Link B" in diff["removed_links"]
        assert len(diff["removed_links"]) == 1

    def test_detects_link_addition(self):
        old = "Note with [[Link A]]."
        new = "Note with [[Link A]] and [[Link B]]."
        diff = self._compute_diff(old, new)
        assert len(diff["removed_links"]) == 0
        assert "Link B" in diff["added_links"]

    def test_no_link_change(self):
        old = "Note with [[Link A]]."
        new = "Note with [[Link A]]."
        diff = self._compute_diff(old, new)
        assert len(diff["removed_links"]) == 0
        assert len(diff["added_links"]) == 0

    def test_content_expansion_triggers(self):
        """Expansion: >20% more words AND >50 words delta."""
        old = " ".join(["word"] * 200)
        new = " ".join(["word"] * 400)  # +200 words = +100%
        diff = self._compute_diff(old, new)
        assert diff["word_pct_change"] > 20
        assert diff["word_delta"] > 50

    def test_content_expansion_below_threshold(self):
        """Small expansion (<20%) should NOT trigger."""
        old = " ".join(["word"] * 200)
        new = " ".join(["word"] * 210)  # +5%
        diff = self._compute_diff(old, new)
        assert diff["word_pct_change"] < 20

    def test_content_expansion_small_delta_no_trigger(self):
        """Large % but <50 word delta should NOT trigger."""
        old = "hello world"  # 2 words
        new = "hello world foo bar baz qux"  # 6 words = +200% but only +4 words
        diff = self._compute_diff(old, new)
        assert diff["word_pct_change"] > 20
        assert diff["word_delta"] <= 50  # Doesn't meet threshold

    def test_content_condensing_triggers(self):
        """Condensing: >20% fewer words AND >50 words delta."""
        old = " ".join(["word"] * 400)
        new = " ".join(["word"] * 200)  # -200 words = -50%
        diff = self._compute_diff(old, new)
        assert diff["word_pct_change"] < -20
        assert abs(diff["word_delta"]) > 50

    def test_structural_change_detected_two_headings_removed(self):
        old = "# H1\n## H2\n## H3\nContent"
        new = "# H1\nContent"  # removed H2 and H3
        diff = self._compute_diff(old, new)
        heading_delta = len(diff["new_headings"]) - len(diff["old_headings"])
        assert abs(heading_delta) >= 2

    def test_structural_change_below_threshold(self):
        """Removing only 1 heading should NOT trigger (threshold is >=2)."""
        old = "# H1\n## H2\nContent"
        new = "# H1\nContent"
        diff = self._compute_diff(old, new)
        heading_delta = len(diff["new_headings"]) - len(diff["old_headings"])
        assert abs(heading_delta) < 2

    def test_pipe_alias_links_normalized(self):
        """[[Link|Alias]] should be treated as 'Link', not 'Link|Alias'."""
        old = "Note with [[Python Programming|Python]]."
        new = "Note without any links."
        diff = self._compute_diff(old, new)
        assert "Python Programming" in diff["removed_links"]
        assert "Python Programming|Python" not in diff["removed_links"]

    def test_identical_content_no_changes(self):
        content = "# Title\n\nSome content with [[Link A]].\n"
        diff = self._compute_diff(content, content)
        assert len(diff["removed_links"]) == 0
        assert len(diff["added_links"]) == 0
        assert diff["word_delta"] == 0


# ===================== Integration: Preferences Round-Trip =====================


class TestEnrichmentPreferencesRoundTrip:
    """
    Verify that _record_enrichment_feedback stores memories that
    _get_enrichment_preferences would subsequently surface.
    """

    def test_recorded_preferences_appear_in_retrieval(self):
        """
        After recording a preference, a search for that domain should
        return a memory that includes the stored text.
        """
        stored = []

        # Mock _add_memory to capture what's stored
        mock_mem0 = Mock()
        scribe = make_scribe(mem0=mock_mem0)

        def capture_add(content, metadata=None):
            stored.append({"memory": content, "score": 0.9})

        scribe._add_memory = Mock(side_effect=capture_add)

        # Step 1: Record feedback (simulates enrichment completion)
        scribe._record_enrichment_feedback(
            title="Python Decorators",
            domain="workshop",
            template_name="tutorial",
            content="# Python Decorators\n\n" + " ".join(["word"] * 350) + "\n[[Link A]]",
            inserted_links={"inserted": ["Link A"]},
            tags=["python"],
        )

        assert len(stored) >= 2  # At least template_domain + structure_style

        # Step 2: Simulate retrieval — mock search to return stored memories
        mock_mem0.search_memory.return_value = stored

        result = scribe._get_enrichment_preferences("workshop", "tutorial")

        assert result  # non-empty
        assert "## User Enrichment Preferences" in result
        # The stored memory about "workshop" + "tutorial" should be present
        assert "tutorial" in result or "workshop" in result
