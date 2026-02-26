"""
NexusCoordinator — single-agent routing (Phase 24a)

Routes a query to the best registered Executable based on task complexity
and required capability. Phase 24a scope: single-agent only.
Multi-agent DAG orchestration is deferred to Phase 24b.

Usage:
    coordinator = NexusCoordinator(registry, storage)
    coordinator.register_executable("persona_scribe", scribe_agent)
    result = await coordinator.route("Save this note", context={})
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from core.nexus.interface import (
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    Executable,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task complexity heuristics (Phase 24a: simple keyword-based)
# ---------------------------------------------------------------------------

class TaskComplexity:
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


# Keywords that suggest each complexity tier
_COMPLEX_KEYWORDS = frozenset([
    "architecture", "design", "plan", "implement", "refactor", "system",
    "analyze", "research", "compare", "evaluate", "strategy",
])
_SIMPLE_KEYWORDS = frozenset([
    "save", "note", "write", "record", "capture", "store",
    "what is", "define", "explain briefly",
])


class NexusCoordinator:
    """
    Routes queries to registered Executable agents.

    Phase 24a: single-agent routing via keyword heuristics.
    Phase 24b: multi-agent DAG with dependency resolution.

    Args:
        registry: AgentRegistry for contract lookup/discovery
        storage:  SwarmStorage for execution history persistence
    """

    def __init__(self, registry: Any, storage: Any) -> None:
        self.registry = registry
        self.storage = storage
        # Maps agent_id → Executable instance
        self._executables: Dict[str, Any] = {}

    # ---- Registration ----

    def register_executable(self, agent_id: str, executable: Any) -> None:
        """
        Register an Executable with the coordinator.

        Also registers the executable's contract in the AgentRegistry
        so it's discoverable via find_by_capability / find_by_domain.
        """
        self._executables[agent_id] = executable
        try:
            self.registry.register(executable.contract)
        except Exception as e:
            logger.warning(
                f"NexusCoordinator: failed to register contract for '{agent_id}': {e}"
            )
        logger.debug(f"NexusCoordinator: registered executable '{agent_id}'")

    # ---- Task classification ----

    def classify_task(self, query: str, context: Dict[str, Any]) -> str:
        """
        Classify a query as simple / moderate / complex.

        Phase 24a: keyword heuristics. Phase 24b: replace with LLM classifier.
        """
        q_lower = query.lower()
        word_count = len(query.split())

        if any(kw in q_lower for kw in _COMPLEX_KEYWORDS) or word_count > 50:
            return TaskComplexity.COMPLEX
        if any(kw in q_lower for kw in _SIMPLE_KEYWORDS):
            return TaskComplexity.SIMPLE
        return TaskComplexity.MODERATE

    # ---- Agent selection ----

    def select_agent(
        self,
        query: str,
        context: Dict[str, Any],
        required_capability: Optional[str] = None,
    ) -> Optional[AgentContract]:
        """
        Select the best agent for a query.

        Selection strategy (Phase 24a):
        1. If required_capability is specified, find agents that declare it
        2. Otherwise, find all active agents
        3. Return the first match (single-agent Phase 24a)

        Returns the AgentContract, or None if no suitable agent found.
        """
        if required_capability:
            candidates = self.registry.find_by_capability(required_capability)
        else:
            candidates = self.registry.list_active()

        # Filter to only those with a live Executable registered
        live_candidates = [c for c in candidates if c.id in self._executables]
        if not live_candidates:
            return None

        # Phase 24a: return first live candidate
        return live_candidates[0]

    # ---- Routing ----

    async def route(
        self,
        query: str,
        context: Dict[str, Any],
        required_capability: Optional[str] = None,
    ) -> Optional[AgentResult]:
        """
        Route a query to the best available agent and record the execution.

        Returns:
            AgentResult if an agent handled the query successfully (or failed).
            None if no suitable agent is registered.
        """
        contract = self.select_agent(query, context, required_capability)
        if contract is None:
            logger.debug("NexusCoordinator: no suitable agent found")
            return None

        executable = self._executables.get(contract.id)
        if executable is None:
            logger.warning(
                f"NexusCoordinator: contract found for '{contract.id}' but no Executable"
            )
            return None

        # Record execution in storage
        exec_id = self.storage.create_execution(
            input_data={"query": query, "context": context},
        )
        run_id = self.storage.create_agent_run(
            execution_id=exec_id,
            agent_id=contract.id,
            input_data={"query": query},
        )

        agent_input = AgentInput(
            query=query,
            data={},
            context=context,
            execution_id=exec_id,
        )

        try:
            result = await executable.execute(agent_input)

            # Update storage
            self.storage.update_agent_run(
                run_id=run_id,
                status=result.status.value,
                output_data={"content": result.content, **result.output},
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                duration_ms=result.duration_ms,
                error=result.error,
            )
            self.storage.update_execution(
                exec_id=exec_id,
                status=result.status.value,
                output_data={"content": result.content},
                error=result.error,
            )

            logger.info(
                f"NexusCoordinator: routed to '{contract.id}' "
                f"(status={result.status.value}, {result.duration_ms}ms)"
            )
            return result

        except Exception as e:
            logger.error(
                f"NexusCoordinator: execution failed for '{contract.id}': {e}"
            )
            self.storage.update_agent_run(
                run_id=run_id,
                status="failed",
                error=str(e),
            )
            self.storage.update_execution(
                exec_id=exec_id,
                status="failed",
                error=str(e),
            )
            return AgentResult(
                agent_id=contract.id,
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                error=str(e),
            )

    # ---- Introspection ----

    def list_executables(self) -> List[AgentContract]:
        """Return contracts for all registered live Executables."""
        result = []
        for agent_id in self._executables:
            contract = self.registry.get(agent_id)
            if contract is not None:
                result.append(contract)
        return result

    def __repr__(self) -> str:
        return (
            f"<NexusCoordinator "
            f"{len(self._executables)} executables, "
            f"storage={self.storage}>"
        )
