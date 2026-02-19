"""
Tests for Budget Allocator.
Tests priority-based allocation, minimums, caps, and surplus redistribution.
"""

import pytest

from core.context.budget_allocator import BudgetAllocator, BudgetPlan, SectionBudget


def _make_config(sections=None, response_reserve=2000, context_windows=None):
    """Helper to build a config dict for BudgetAllocator."""
    if sections is None:
        sections = {
            "rag": {"priority": 1, "min": 200, "max": 3000, "target_pct": 0.40},
            "mental_models": {"priority": 2, "min": 100, "max": 1500, "target_pct": 0.15},
            "memory": {"priority": 3, "min": 100, "max": 2000, "target_pct": 0.20},
            "entities": {"priority": 4, "min": 50, "max": 1000, "target_pct": 0.15},
            "conversation": {"priority": 5, "min": 100, "max": 2000, "target_pct": 0.10},
        }
    return {
        "response_reserve": response_reserve,
        "model_context_windows": context_windows or {"default": 8192},
        "sections": sections,
    }


class TestBudgetAllocatorBasic:
    """Test basic allocation behavior."""

    def test_allocation_returns_budget_plan(self):
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=8192, conversation_tokens=0)
        assert isinstance(plan, BudgetPlan)
        assert plan.total_budget == 8192
        assert plan.response_reserve == 2000

    def test_all_sections_present(self):
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=8192)
        assert set(plan.sections.keys()) == {"rag", "mental_models", "memory", "entities", "conversation"}

    def test_total_allocated_does_not_exceed_available(self):
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=8192, conversation_tokens=1000)
        available = 8192 - 2000 - 1000  # 5192
        assert plan.total_allocated() <= available

    def test_no_section_below_minimum_when_budget_allows(self):
        """When total budget is large, every section should get at least its min."""
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=16000, conversation_tokens=0)
        for name, sb in plan.sections.items():
            section_cfg = config["sections"][name]
            assert sb.allocated >= section_cfg["min"], f"{name} got {sb.allocated} < min {section_cfg['min']}"

    def test_no_section_exceeds_maximum(self):
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=100000, conversation_tokens=0)
        for name, sb in plan.sections.items():
            section_cfg = config["sections"][name]
            assert sb.allocated <= section_cfg["max"], f"{name} got {sb.allocated} > max {section_cfg['max']}"


class TestBudgetAllocatorPressure:
    """Test behavior under tight budgets."""

    def test_small_budget_priority_ordering(self):
        """When budget is very small, higher-priority sections should get more."""
        config = _make_config()
        allocator = BudgetAllocator(config)
        # Only 600 tokens available (8192 - 2000 - 5592)
        plan = allocator.allocate(model_context_window=8192, conversation_tokens=5592)
        # RAG (priority 1) should get at least its minimum (200)
        assert plan.sections["rag"].allocated >= 200
        # Total should not exceed 600
        assert plan.total_allocated() <= 600

    def test_zero_budget(self):
        """When no budget is available, all sections should get 0."""
        config = _make_config()
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=2000, conversation_tokens=0)
        # Available = 2000 - 2000 = 0
        for sb in plan.sections.values():
            assert sb.allocated == 0


class TestBudgetAllocatorSurplus:
    """Test surplus redistribution."""

    def test_surplus_redistribution_when_section_capped(self):
        """If one section reaches max, surplus should go to others."""
        # Create a config where one section has a very low max
        sections = {
            "small": {"priority": 1, "min": 50, "max": 100, "target_pct": 0.50},
            "large": {"priority": 2, "min": 50, "max": 5000, "target_pct": 0.50},
        }
        config = _make_config(sections=sections)
        allocator = BudgetAllocator(config)
        plan = allocator.allocate(model_context_window=10000, conversation_tokens=0)
        # small should be capped at 100
        assert plan.sections["small"].allocated <= 100
        # large should get surplus
        assert plan.sections["large"].allocated > 100


class TestBudgetPlan:
    """Test BudgetPlan methods."""

    def test_remaining(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        plan.sections["rag"] = SectionBudget(
            name="rag", priority=1, min_tokens=200, max_tokens=3000,
            target_pct=0.4, allocated=1000, used=300,
        )
        assert plan.remaining("rag") == 700

    def test_remaining_unknown_section(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        assert plan.remaining("nonexistent") == 0

    def test_report_usage(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        plan.sections["rag"] = SectionBudget(
            name="rag", priority=1, min_tokens=200, max_tokens=3000,
            target_pct=0.4, allocated=1000,
        )
        plan.report_usage("rag", 500)
        assert plan.sections["rag"].used == 500

    def test_report_usage_caps_at_allocated(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        plan.sections["rag"] = SectionBudget(
            name="rag", priority=1, min_tokens=200, max_tokens=3000,
            target_pct=0.4, allocated=1000,
        )
        plan.report_usage("rag", 2000)
        assert plan.sections["rag"].used == 1000  # Capped at allocated

    def test_total_used(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        plan.sections["a"] = SectionBudget(
            name="a", priority=1, min_tokens=0, max_tokens=1000,
            target_pct=0.5, allocated=500, used=200,
        )
        plan.sections["b"] = SectionBudget(
            name="b", priority=2, min_tokens=0, max_tokens=1000,
            target_pct=0.5, allocated=500, used=300,
        )
        assert plan.total_used() == 500

    def test_summary_is_string(self):
        plan = BudgetPlan(total_budget=8192, response_reserve=2000)
        plan.sections["rag"] = SectionBudget(
            name="rag", priority=1, min_tokens=200, max_tokens=3000,
            target_pct=0.4, allocated=1000,
        )
        summary = plan.summary()
        assert isinstance(summary, str)
        assert "rag" in summary
