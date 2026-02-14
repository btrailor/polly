"""
Routing models: enums and data classes for IntelligentRouterV2.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from polly_routing.providers.base import ProviderAdapter


class ConfidenceLevel(Enum):
    """User confidence/quality preference."""
    FAST = "fast"           # Speed over quality, low cost
    BALANCED = "balanced"   # Balance speed, quality, cost
    THOROUGH = "thorough"   # Quality over speed, higher cost


class TaskType(Enum):
    """Types of tasks for complexity classification."""
    SIMPLE_QUERY = "simple_query"
    CODE_COMPLETION = "code_completion"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    MULTI_FILE = "multi_file"
    REFACTORING = "refactoring"
    ARCHITECTURAL = "architectural"
    CREATIVE = "creative"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"


@dataclass
class RoutingDecision:
    """Result of routing logic."""
    provider: "ProviderAdapter"
    model: str
    confidence: ConfidenceLevel
    complexity_score: int  # 1-10
    estimated_cost: float
    reason: str
    fallback_chain: List[tuple]  # List of (provider, model)


@dataclass
class TierConfig:
    """Configuration for a routing tier."""
    name: str
    max_cost_per_request: float
    providers: List[tuple]  # (provider_name, model, priority)
