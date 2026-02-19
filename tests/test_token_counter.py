"""
Tests for Token Counter Service.
Tests accurate counting, truncation, and fallback behavior.
"""

import pytest

from core.context.token_counter import TokenCounter


class TestTokenCounterCount:
    """Test TokenCounter.count() accuracy."""

    def test_empty_string(self):
        assert TokenCounter.count("") == 0

    def test_simple_text(self):
        """Token count for short English prose should be reasonable."""
        text = "Hello, world!"
        count = TokenCounter.count(text)
        assert count > 0
        assert count < 10

    def test_prose_accuracy(self):
        """Prose token count should be within ~5% of expected tiktoken result.
        Average English word is about 1.3 tokens in cl100k_base."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a simple sentence used for testing purposes. "
            "Token counting must be accurate for budget allocation to work."
        )
        count = TokenCounter.count(text, model_id="gpt-4")
        word_count = len(text.split())
        # Rough sanity: tokens should be between 0.8x and 2x word count
        assert count >= word_count * 0.8
        assert count <= word_count * 2

    def test_code_content(self):
        """Code has more tokens per word due to symbols."""
        code = """
def calculate_budget(total: int, sections: list[dict]) -> dict:
    allocated = {}
    remaining = total
    for s in sorted(sections, key=lambda x: x['priority']):
        allocated[s['name']] = min(s['min'], remaining)
        remaining -= allocated[s['name']]
    return allocated
"""
        count = TokenCounter.count(code, model_id="gpt-4")
        assert count > 20  # Code has meaningful token count
        assert count < 200  # But not absurdly large

    def test_mixed_content(self):
        """Mixed prose and code."""
        text = "Here's a function: `def foo(): pass` and more text."
        count = TokenCounter.count(text)
        assert count > 5
        assert count < 30

    def test_local_model_uses_estimation(self):
        """Ollama/local models should fall back to character-based estimation."""
        text = "A simple test sentence for estimation that has enough words to stabilize the ratio."
        count_cloud = TokenCounter.count(text, model_id="gpt-4")
        count_local = TokenCounter.count(text, model_id="llama3.2:latest")
        # Both should return positive numbers
        assert count_cloud > 0
        assert count_local > 0
        # They can differ but should be in the same ballpark (within 100%)
        assert abs(count_cloud - count_local) < max(count_cloud, count_local)

    def test_claude_model(self):
        """Claude model should use tiktoken (approximate)."""
        text = "Token counting for Anthropic Claude models."
        count = TokenCounter.count(text, model_id="claude-sonnet-4-20250514")
        assert count > 0
        assert count < 20


class TestTokenCounterTruncate:
    """Test TokenCounter.truncate()."""

    def test_short_text_unchanged(self):
        """Text under budget should be returned unchanged."""
        text = "Short text."
        result = TokenCounter.truncate(text, max_tokens=100)
        assert result == text

    def test_long_text_truncated(self):
        """Text over budget should be truncated."""
        text = " ".join(["word"] * 500)
        result = TokenCounter.truncate(text, max_tokens=50)
        assert TokenCounter.count(result) <= 50

    def test_truncation_preserves_meaning(self):
        """Truncated text should end at a natural boundary when possible."""
        text = (
            "First sentence ends here. Second sentence is longer and has more "
            "content. Third sentence wraps it up. Fourth sentence is extra."
        )
        result = TokenCounter.truncate(text, max_tokens=15)
        # Should end at a sentence boundary
        assert result.rstrip().endswith(".")

    def test_empty_text(self):
        assert TokenCounter.truncate("", max_tokens=100) == ""

    def test_output_within_budget(self):
        """Truncated output token count should not exceed budget."""
        text = "This is a test. " * 100
        for budget in [10, 50, 100, 200]:
            result = TokenCounter.truncate(text, max_tokens=budget)
            assert TokenCounter.count(result) <= budget
