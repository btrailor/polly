"""
PromptAgent — user-defined LLM agent driven by a system prompt (Phase 24e)

A lightweight Nexus Executable that wraps a user-authored system prompt and
calls UnifiedLLM to produce a response. Enables users to create custom agent
capabilities without writing Python code.

Usage:
    agent = PromptAgent(
        agent_id="custom_summariser",
        name="Custom Summariser",
        system_prompt="You are a concise summariser. Return bullet points.",
        capability_name="summarise_text",
        domain_affinity=["knowledge"],
        llm=polly.llm,
    )
    coordinator.register_executable(agent.agent_id, agent)
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, List, Optional

from core.nexus.interface import (
    AgentCapability,
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    ExecutionMode,
    ResourceConstraints,
)

logger = logging.getLogger(__name__)


class PromptAgent:
    """
    Nexus Executable driven by a user-written system prompt.

    Calls UnifiedLLM with the configured system prompt prepended to the user
    query. Designed to be created at runtime from user input and registered
    with NexusCoordinator.

    Args:
        agent_id:        Unique identifier (e.g. "prompt_summariser_abc123")
        name:            Human-readable display name
        system_prompt:   The full system prompt for this agent
        capability_name: Single capability this agent declares (e.g. "summarise_text")
        domain_affinity: List of domain slugs (e.g. ["knowledge", "writing"])
        llm:             UnifiedLLM instance (injected at registration time)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        system_prompt: str,
        capability_name: str,
        domain_affinity: Optional[List[str]] = None,
        llm: Optional[Any] = None,
    ) -> None:
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self._llm = llm

        self.contract = AgentContract(
            id=agent_id,
            name=name,
            agent_type="prompt",
            capabilities=[
                AgentCapability(
                    name=capability_name,
                    description=name,
                    input_schema={"query": "string"},
                    output_schema={"content": "string"},
                )
            ],
            domain_affinity=domain_affinity or [],
            execution_mode=ExecutionMode.AUTONOMOUS,
            resource_constraints=ResourceConstraints(prefer_local=True),
        )

    def can_handle(self, capability: str) -> bool:
        """Return True if this agent declares the given capability."""
        return self.contract.has_capability(capability)

    async def execute(self, agent_input: AgentInput) -> AgentResult:
        """
        Execute the prompt agent: send system_prompt + user query to LLM.

        Collects the full streaming response before returning so the caller
        gets a complete AgentResult.
        """
        start_ms = time.monotonic() * 1000
        exec_id = agent_input.execution_id or str(uuid.uuid4())

        if self._llm is None:
            return AgentResult(
                agent_id=self.agent_id,
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                error="PromptAgent has no LLM configured",
                duration_ms=int(time.monotonic() * 1000 - start_ms),
            )

        try:
            messages = [{"role": "user", "content": agent_input.query}]

            # Collect streaming response into a single string
            chunks: List[str] = []
            async for chunk in self._llm.chat(
                messages=messages,
                system_prompt=self.system_prompt,
                temperature=0.5,
                max_tokens=1500,
                stream=False,
            ):
                if chunk:
                    chunks.append(chunk)

            content = "".join(chunks)
            duration_ms = int(time.monotonic() * 1000 - start_ms)

            logger.debug(
                f"PromptAgent '{self.agent_id}' completed "
                f"({len(content)} chars, {duration_ms}ms)"
            )

            return AgentResult(
                agent_id=self.agent_id,
                execution_id=exec_id,
                status=AgentStatus.COMPLETED,
                content=content,
                tokens_used=0,   # UnifiedLLM doesn't expose token counts per call
                cost_usd=0.0,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int(time.monotonic() * 1000 - start_ms)
            logger.warning(f"PromptAgent '{self.agent_id}' failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                content="",
                error=str(e),
                duration_ms=duration_ms,
            )

    def __repr__(self) -> str:
        cap = self.contract.capabilities[0].name if self.contract.capabilities else "?"
        return f"<PromptAgent id={self.agent_id!r} capability={cap!r}>"
