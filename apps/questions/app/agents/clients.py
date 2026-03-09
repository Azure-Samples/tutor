"""Agent framework wrappers for consistent agent creation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from agent_framework import ChatAgent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

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
    """Factory responsible for provisioning ChatAgent instances consistently."""

    def __init__(self, project_endpoint: str, credential_factory: Callable[[], Any] | None = None) -> None:
        self._project_endpoint = project_endpoint
        self._credential_factory = credential_factory or DefaultAzureCredential
        self._tool_builder = ToolBuilder()

    def create(self, spec: AgentSpec) -> ChatAgent:
        """Instantiate a ready-to-run agent respecting the supplied spec."""
        client = AzureAIAgentClient(
            project_endpoint=self._project_endpoint,
            model_deployment_name=spec.deployment,
            async_credential=self._credential_factory(),
            agent_name=spec.name,
        )
        configured_tools = self._tool_builder.from_callbacks(spec.tools)
        return ChatAgent(
            client=client,
            name=spec.name,
            instructions=spec.instructions,
            tools=configured_tools or None,
        )
