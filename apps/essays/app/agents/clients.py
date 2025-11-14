"""Agent framework wrappers for consistent agent creation."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, AsyncIterator, Callable, Iterable, cast

from azure.ai.agents.models import Agent, ListSortOrder, RunStatus
from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

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


class FoundryAgentService:
    """Utility class to manage Azure AI Foundry agents and executions."""

    def __init__(
        self,
        endpoint: str,
        credential_factory: Callable[[], AsyncTokenCredential] | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._credential_factory = credential_factory or AsyncDefaultAzureCredential

    @asynccontextmanager
    async def _credential(self) -> AsyncIterator[AsyncTokenCredential]:
        credential = self._credential_factory()
        aenter = getattr(credential, "__aenter__", None)
        if aenter:
            token = await aenter()
            try:
                yield token
            finally:
                await credential.__aexit__(None, None, None)
        else:  # pragma: no cover - fallback path for credentials without context manager support
            try:
                yield credential
            finally:
                close = getattr(credential, "close", None)
                if close:
                    await close()

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[AIProjectClient]:
        async with self._credential() as credential:
            client = AIProjectClient(endpoint=self._endpoint, credential=credential)
            await client.__aenter__()
            try:
                yield client
            finally:
                await client.__aexit__(None, None, None)

    async def create_agent(
        self,
        *,
        name: str,
        instructions: str,
        deployment: str,
        temperature: float | None = None,
    ) -> Agent:
        payload: dict[str, Any] = {
            "name": name,
            "instructions": instructions,
            "model": deployment,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        async with self._client() as client:
            return await client.agents.create_agent(**payload)  # type: ignore[attr-defined]

    async def delete_agent(self, agent_id: str) -> None:
        async with self._client() as client:
            await client.agents.delete_agent(agent_id=agent_id)  # type: ignore[attr-defined]

    async def get_agent(self, agent_id: str) -> Agent:
        async with self._client() as client:
            return await client.agents.get_agent(agent_id=agent_id)  # type: ignore[attr-defined]

    async def get_agents(self, agent_ids: Iterable[str]) -> list[Agent]:
        agents: list[Agent] = []
        async with self._client() as client:
            for agent_id in agent_ids:
                agents.append(await client.agents.get_agent(agent_id=agent_id))  # type: ignore[attr-defined]
        return agents

    async def run_agent(self, agent_id: str, prompt: str) -> str:
        async with self._client() as client:
            thread = await client.agents.threads.create()  # type: ignore[attr-defined]
            await client.agents.messages.create(  # type: ignore[attr-defined]
                thread_id=thread.id,
                role="user",
                content=cast(Any, [{"type": "text", "text": prompt}]),
            )
            run = await client.agents.runs.create(  # type: ignore[attr-defined]
                thread_id=thread.id,
                agent_id=agent_id,
            )

            while run.status in {
                RunStatus.QUEUED,
                RunStatus.IN_PROGRESS,
                RunStatus.CANCELLING,
                RunStatus.STARTING,
            }:
                await asyncio.sleep(0.5)
                run = await client.agents.runs.get(  # type: ignore[attr-defined]
                    thread_id=thread.id,
                    run_id=run.id,
                )

            if run.status == RunStatus.REQUIRES_ACTION:
                raise RuntimeError("Agent run requires tool outputs, which is not supported in this flow.")
            if run.status != RunStatus.COMPLETED:
                raise RuntimeError(f"Agent run finished with unexpected status {run.status}.")

            accumulated: list[str] = []
            async for message in client.agents.messages.list(  # type: ignore[attr-defined]
                thread_id=thread.id,
                order=ListSortOrder.DESCENDING,
                limit=1,
            ):
                for content in getattr(message, "content", []) or []:
                    text_value: str | None = None
                    if isinstance(content, dict):  # pragma: no cover - defensive branch for dict payloads
                        text_value = content.get("text")
                    else:
                        text_value = getattr(content, "text", None)
                    if text_value:
                        accumulated.append(text_value)
                break

            return "\n".join(accumulated).strip()
