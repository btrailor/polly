"""
Budget Allocator for Polly context assembly.

Distributes a total token budget across context sections using
priority-based allocation with guaranteed minimums and hard caps.

Algorithm:
  Pass 1: Allocate min_tokens for all sections by priority order.
  Pass 2: Distribute remaining budget proportionally by target_pct.
  Pass 3: Cap at max_tokens, redistribute surplus.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SectionBudget:
    """Budget allocation for one context section."""
    name: str
    priority: int          # 1 = highest (guaranteed), 6 = lowest
    min_tokens: int        # Floor -- always allocated if budget allows
    max_tokens: int        # Ceiling -- never exceeded
    target_pct: float      # Target percentage of total budget
    allocated: int = 0     # Actual allocation after solving
    used: int = 0          # Tokens actually consumed


@dataclass
class BudgetPlan:
    """Complete budget allocation across all sections."""
    total_budget: int
    response_reserve: int
    sections: Dict[str, SectionBudget] = field(default_factory=dict)
    overflow_tokens: int = 0  # Unallocated surplus

    def remaining(self, section: str) -> int:
        """Tokens remaining for a section."""
        if section not in self.sections:
            return 0
        sb = self.sections[section]
        return max(0, sb.allocated - sb.used)

    def report_usage(self, section: str, tokens_used: int):
        """Record actual token usage for a section."""
        if section not in self.sections:
            logger.warning(f"Unknown section '{section}' in report_usage")
            return
        sb = self.sections[section]
        sb.used = min(tokens_used, sb.allocated)

    def total_allocated(self) -> int:
        """Total tokens allocated across all sections."""
        return sum(sb.allocated for sb in self.sections.values())

    def total_used(self) -> int:
        """Total tokens actually used across all sections."""
        return sum(sb.used for sb in self.sections.values())

    def summary(self) -> str:
        """Human-readable summary for debug logging."""
        lines = [f"Budget Plan: {self.total_budget} total, {self.response_reserve} reserved"]
        for name, sb in sorted(self.sections.items(), key=lambda x: x[1].priority):
            lines.append(
                f"  [{sb.priority}] {name}: {sb.allocated} allocated, "
                f"{sb.used} used, {sb.min_tokens}-{sb.max_tokens} bounds"
            )
        lines.append(f"  overflow: {self.overflow_tokens}")
        return "\n".join(lines)


class BudgetAllocator:
    """
    Distributes a total token budget across context sections
    using priority-based allocation with guaranteed minimums.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: context_budget config section with keys:
                response_reserve, model_context_windows, sections
        """
        self.response_reserve = config.get("response_reserve", 2000)
        self.model_context_windows = config.get("model_context_windows", {})
        self.section_configs = config.get("sections", {})

    def _get_context_window(self, model_id: str) -> int:
        """Get the context window size for a model."""
        model_lower = model_id.lower()

        # Try exact match first
        for key, window in self.model_context_windows.items():
            if key == model_lower:
                return window

        # Try prefix match
        for key, window in self.model_context_windows.items():
            if key != "default" and model_lower.startswith(key):
                return window

        # Try substring match (e.g., "claude-sonnet" matches "claude-sonnet-4-...")
        for key, window in self.model_context_windows.items():
            if key != "default" and key in model_lower:
                return window

        return self.model_context_windows.get("default", 8192)

    def allocate(
        self,
        model_context_window: Optional[int] = None,
        conversation_tokens: int = 0,
        model_id: str = "gpt-4"
    ) -> BudgetPlan:
        """
        Compute budget allocation for a query.

        Args:
            model_context_window: Total context window of target model.
                If None, looked up from config by model_id.
            conversation_tokens: Tokens already consumed by conversation history
            model_id: For context window lookup if model_context_window is None

        Returns:
            BudgetPlan with per-section allocations
        """
        if model_context_window is None:
            model_context_window = self._get_context_window(model_id)

        # Calculate available budget
        total = model_context_window - self.response_reserve
        available = max(0, total - conversation_tokens)

        # Build section budget objects from config
        sections = []
        for name, cfg in self.section_configs.items():
            sections.append(SectionBudget(
                name=name,
                priority=cfg.get("priority", 99),
                min_tokens=cfg.get("min", 0),
                max_tokens=cfg.get("max", 10000),
                target_pct=cfg.get("target_pct", 0.0),
            ))

        # Solve allocation
        solved = self._solve_allocation(available, sections)

        # Build plan
        plan = BudgetPlan(
            total_budget=model_context_window,
            response_reserve=self.response_reserve,
        )
        total_allocated = 0
        for sb in solved:
            plan.sections[sb.name] = sb
            total_allocated += sb.allocated

        plan.overflow_tokens = max(0, available - total_allocated)

        logger.debug(f"Budget allocation:\n{plan.summary()}")
        return plan

    def _solve_allocation(
        self,
        available: int,
        sections: List[SectionBudget]
    ) -> List[SectionBudget]:
        """
        Priority-based allocation solver.

        Pass 1: Allocate minimums for all sections (by priority order).
                If budget exhausted, lower-priority sections get 0.
        Pass 2: Distribute remaining budget proportionally by target_pct.
                Cap at max_tokens.
        Pass 3: Redistribute surplus from capped sections to uncapped ones.
        """
        # Sort by priority (1 = highest)
        sections = sorted(sections, key=lambda s: s.priority)

        if available <= 0:
            # No budget at all — everything gets 0
            for s in sections:
                s.allocated = 0
            return sections

        # Pass 1: Guarantee minimums by priority
        remaining = available
        for s in sections:
            if remaining >= s.min_tokens:
                s.allocated = s.min_tokens
                remaining -= s.min_tokens
            elif remaining > 0:
                # Partial allocation — give what we can
                s.allocated = remaining
                remaining = 0
            else:
                s.allocated = 0

        if remaining <= 0:
            return sections

        # Pass 2: Distribute remaining proportionally by target_pct
        # Only sections that haven't reached their max yet participate
        eligible = [s for s in sections if s.allocated < s.max_tokens]
        total_pct = sum(s.target_pct for s in eligible)

        if total_pct > 0:
            for s in eligible:
                # Proportional share of remaining budget
                share = int(remaining * (s.target_pct / total_pct))
                # Additional tokens on top of already-allocated minimum
                additional = min(share, s.max_tokens - s.allocated)
                s.allocated += additional

        # Pass 3: Cap at max and redistribute surplus
        # Repeat until stable (max 5 iterations to prevent infinite loop)
        for _ in range(5):
            surplus = 0
            uncapped = []
            for s in sections:
                if s.allocated > s.max_tokens:
                    surplus += s.allocated - s.max_tokens
                    s.allocated = s.max_tokens
                elif s.allocated < s.max_tokens:
                    uncapped.append(s)

            if surplus <= 0 or not uncapped:
                break

            # Redistribute surplus proportionally among uncapped sections
            total_uncapped_pct = sum(s.target_pct for s in uncapped) or 1.0
            for s in uncapped:
                share = int(surplus * (s.target_pct / total_uncapped_pct))
                additional = min(share, s.max_tokens - s.allocated)
                s.allocated += additional

        return sections
