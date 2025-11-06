"""Agent framework wrappers for consistent agent creation."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Iterable

from azure.identity import DefaultAzureCredential

try:
    from agent_framework import ChatAgent
    from agent_framework.azure import AzureAIAgentClient
except ImportError as exc:  # pragma: no cover - dependency is required at runtime
    raise ImportError(
        "Microsoft Agent Framework is required. Install with 'pip install agent-framework-azure-ai --pre'."
    ) from exc

from .tooling import ToolBuilder


@dataclass(slots=True)
class AgentSpec:
    """Declarative description for constructing an agent."""

    name: str
    instructions: str
    deployment: str
    tools: Iterable[Callable[..., Any]] = field(default_factory=tuple)
    temperature: float | None = None
    max_tokens: int | None = None


class AgentRegistry:
    """Factory responsible for provisioning `ChatAgent` instances consistently."""

    def __init__(self, endpoint: str, credential_factory: Callable[[], Any] | None = None) -> None:
        self._endpoint = endpoint
        self._credential_factory = credential_factory or DefaultAzureCredential
        self._tool_builder = ToolBuilder()

    @lru_cache(maxsize=32)
    def _client(self, deployment: str) -> AzureAIAgentClient:
        """Create or reuse a client for the provided deployment."""

        return AzureAIAgentClient(
            endpoint=self._endpoint,
            credential=self._credential_factory(),
            deployment=deployment,
        )

    def create(self, spec: AgentSpec) -> ChatAgent:
        """Instantiate a ready-to-run agent respecting the supplied spec."""

        client = self._client(spec.deployment)
        configured_tools = self._tool_builder.from_callbacks(spec.tools)
        return client.create_agent(
            name=spec.name,
            instructions=spec.instructions,
            tools=configured_tools,
            temperature=spec.temperature,
            max_output_tokens=spec.max_tokens,
        )
