"""
NexusCoordinator — agent routing and workflow execution (Phase 24a/24b/24e)

Phase 24a: Single-agent routing via keyword heuristics.
Phase 24b: Multi-agent DAG execution via WorkflowExecutor.
Phase 24e: Pattern learning wired via optional pattern_engine param.

Usage (single-agent, Phase 24a):
    coordinator = NexusCoordinator(registry, storage)
    coordinator.register_executable("persona_scribe", scribe_agent)
    result = await coordinator.route("Save this note", context={})

Usage (workflow, Phase 24b):
    coordinator = NexusCoordinator(registry, storage, template_registry=registry)
    result = await coordinator.execute_workflow("research-to-write", "my query", {})
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
from core.nexus.workflow import WorkflowResult

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
    Phase 24b: multi-agent DAG with dependency resolution via execute_workflow().
    Phase 24c: context mediation via optional NexusContextBroker.
    Phase 24e: pattern learning via optional pattern_engine.

    Args:
        registry:          AgentRegistry for contract lookup/discovery
        storage:           SwarmStorage for execution history persistence
        template_registry: Optional TemplateRegistry for workflow template lookup
        context_broker:    Optional NexusContextBroker for execution context mediation
        pattern_engine:    Optional PatternEngine for workflow pattern learning
    """

    def __init__(
        self,
        registry: Any,
        storage: Any,
        template_registry: Optional[Any] = None,
        context_broker: Optional[Any] = None,
        pattern_engine: Optional[Any] = None,
    ) -> None:
        self.registry = registry
        self.storage = storage
        self.template_registry = template_registry
        self.context_broker = context_broker
        self.pattern_engine = pattern_engine
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

    # ---- Workflow execution (Phase 24b) ----

    async def execute_workflow(
        self,
        template_id: str,
        user_input: str,
        context: Dict[str, Any],
    ) -> Optional[WorkflowResult]:
        """
        Execute a named workflow template with multi-agent DAG orchestration.

        Looks up the template from self.template_registry, validates it,
        then delegates to WorkflowExecutor.

        Args:
            template_id: ID of a registered WorkflowTemplate.
            user_input:  The user's original query.
            context:     Arbitrary context passed to each agent.

        Returns:
            WorkflowResult, or None if template_registry is not configured
            or the template is not found.
        """
        if self.template_registry is None:
            logger.warning(
                "NexusCoordinator.execute_workflow: no template_registry configured"
            )
            return None

        template = self.template_registry.get(template_id)
        if template is None:
            logger.warning(
                f"NexusCoordinator.execute_workflow: template '{template_id}' not found"
            )
            return None

        # Import here to avoid circular imports at module load time
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner

        planner = WorkflowPlanner()
        executor = WorkflowExecutor(
            coordinator=self,
            storage=self.storage,
            planner=planner,
        )

        logger.info(
            f"NexusCoordinator: executing workflow '{template_id}' "
            f"({len(template.steps)} steps)"
        )
        result = await executor.execute(template, user_input, context)

        # Phase 24e: feed successful completions to the pattern engine
        if result is not None and result.status == "completed" and self.pattern_engine is not None:
            try:
                from datetime import datetime
                from core.patterns.models import Pattern, PatternType
                now = datetime.now()
                self.pattern_engine.learn(Pattern(
                    id=f"workflow_{template_id}",
                    pattern_type=PatternType.WORKFLOW,
                    name=f"Workflow: {template.name}",
                    description=f"Successful execution of workflow '{template_id}'",
                    confidence=0.8,
                    occurrences=1,
                    first_seen=now,
                    last_seen=now,
                    domains=list(template.domain_affinity),
                    keywords=["workflow", "nexus", template_id],
                    examples=[user_input[:120]],
                    metadata={
                        "template_id": template_id,
                        "steps": len(template.steps),
                        "total_tokens": result.total_tokens,
                        "total_duration_ms": result.total_duration_ms,
                    },
                    source="observation",
                ))
                self.pattern_engine.save()
            except Exception as e:
                logger.warning(f"NexusCoordinator: pattern learning failed (non-critical): {e}")

        return result

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
