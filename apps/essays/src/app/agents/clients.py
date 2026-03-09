"""Agent framework wrappers for consistent agent creation."""

from __future__ import annotations

import asyncio
import inspect
import logging
from io import BytesIO
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Iterable, Sequence, cast

from agent_framework import ChatAgent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agents.models import Agent, ListSortOrder, RunStatus
from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from .tooling import ToolBuilder


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentSpec:
    """Declarative description for constructing an agent."""

    name: str
    instructions: str
    deployment: str
    tools: Iterable[Callable[..., Any]] = field(default_factory=tuple)
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass(slots=True)
class AgentAttachment:
    """Binary payload destined for Azure AI Agents message content."""

    file_name: str
    content_type: str
    payload: bytes
    purpose: str = "assistants"
    tool_type: str = "vision"


class AgentRegistry:
    """Factory responsible for provisioning `ChatAgent` instances consistently."""

    def __init__(self, endpoint: str, credential_factory: Callable[[], Any] | None = None) -> None:
        self._endpoint = endpoint
        self._credential_factory = credential_factory or DefaultAzureCredential
        self._tool_builder = ToolBuilder()

    def _client(self, deployment: str) -> AzureAIAgentClient:
        """Create a client for the provided deployment."""

        return AzureAIAgentClient(
            project_endpoint=self._endpoint,
            model_deployment_name=deployment,
            async_credential=self._credential_factory(),
        )

    def create(self, spec: AgentSpec) -> ChatAgent:
        """Instantiate a ready-to-run agent respecting the supplied spec."""

        client = self._client(spec.deployment)
        configured_tools = self._tool_builder.from_callbacks(spec.tools)
        return ChatAgent(
            client=client,
            name=spec.name,
            instructions=spec.instructions,
            tools=configured_tools,
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
        has_async_cm = all(
            callable(getattr(credential, attr, None)) for attr in ("__aenter__", "__aexit__")
        )
        if has_async_cm:
            token = await credential.__aenter__()
            try:
                yield token
            finally:
                await credential.__aexit__(None, None, None)
        else:  # pragma: no cover - fallback path for credentials without context manager support
            try:
                yield credential
            finally:
                close_method = getattr(credential, "close", None)
                if callable(close_method):
                    result = close_method()
                    if inspect.isawaitable(result):
                        await result

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[Any]:
        async with self._credential() as credential:
            project_client = AIProjectClient(endpoint=self._endpoint, credential=credential)
            await project_client.__aenter__()
            try:
                yield project_client.agents
            finally:
                await project_client.__aexit__(None, None, None)

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
            try:
                return await client.create_agent(**payload)
            except AzureError as exc:
                logger.error("Failed to create agent %s: %s", name, exc)
                raise RuntimeError(f"Failed to create agent '{name}': {exc}") from exc

    async def delete_agent(self, agent_id: str) -> None:
        async with self._client() as client:
            await client.delete_agent(agent_id=agent_id)

    async def run_agent(
        self,
        agent_id: str,
        prompt: str,
        *,
        attachments: Sequence[AgentAttachment] | None = None,
    ) -> str:
        async with self._client() as client:
            thread = await client.threads.create()
            uploaded_files: list[str] = []
            streams: list[BytesIO] = []
            content_blocks: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
            message_attachments: list[dict[str, Any]] = []

            try:
                if attachments:
                    for attachment in attachments:
                        if not attachment.payload:
                            continue
                        stream = BytesIO(attachment.payload)
                        streams.append(stream)
                        file_name = attachment.file_name or "resource.bin"
                        content_type = attachment.content_type or "application/octet-stream"
                        purpose = attachment.purpose or "vision"
                        file_info = await client.files.upload(
                            file=(file_name, stream, content_type),
                            purpose=purpose,
                            filename=file_name,
                        )
                        file_id = getattr(file_info, "id", None)
                        if isinstance(file_id, str):
                            uploaded_files.append(file_id)
                            tool_type = attachment.tool_type or "vision"
                            message_attachments.append(
                                {
                                    "file_id": file_id,
                                    "tools": [{"type": tool_type}],
                                }
                            )

                await client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=cast(Any, content_blocks),
                    attachments=cast(Any, message_attachments) if message_attachments else None,
                )

                run = await client.runs.create(
                    thread_id=thread.id,
                    agent_id=agent_id,
                )

                transitional_statuses = {
                    RunStatus.QUEUED,
                    RunStatus.IN_PROGRESS,
                    RunStatus.CANCELLING,
                }
                starting_status = getattr(RunStatus, "STARTING", None)
                if starting_status is not None:
                    transitional_statuses.add(starting_status)

                while run.status in transitional_statuses:
                    await asyncio.sleep(0.5)
                    run = await client.runs.get(
                        thread_id=thread.id,
                        run_id=run.id,
                    )

                if run.status == RunStatus.REQUIRES_ACTION:
                    raise RuntimeError("Agent run requires tool outputs, which is not supported in this flow.")
                if run.status != RunStatus.COMPLETED:
                    raise RuntimeError(f"Agent run finished with unexpected status {run.status}.")

                accumulated: list[str] = []
                async for message in client.messages.list(
                    thread_id=thread.id,
                    order=ListSortOrder.DESCENDING,
                    limit=1,
                ):
                    for content in getattr(message, "content", []) or []:
                        raw_text: Any = None
                        if isinstance(content, dict):  # pragma: no cover - defensive branch for dict payloads
                            raw_text = content.get("text")
                        else:
                            raw_text = getattr(content, "text", None)

                        text_value: str | None = None
                        if isinstance(raw_text, str):
                            text_value = raw_text
                        elif raw_text is not None:
                            value_attr = getattr(raw_text, "value", None)
                            if isinstance(value_attr, str):
                                text_value = value_attr
                            else:
                                text_value = str(raw_text)

                        if text_value:
                            accumulated.append(text_value)
                    break

                return "\n".join(accumulated).strip()
            finally:
                for stream in streams:
                    stream.close()
                for file_id in uploaded_files:
                    try:
                        await client.files.delete(file_id=file_id)
                    except AzureError as exc:  # pragma: no cover - best-effort cleanup
                        logger.warning("Failed to delete uploaded file %s: %s", file_id, exc)

    async def get_agent(self, agent_id: str) -> Agent:
        async with self._client() as client:
            return await client.get_agent(agent_id=agent_id)

    async def get_agents(self, agent_ids: Iterable[str]) -> list[Agent]:
        agents: list[Agent] = []
        async with self._client() as client:
            for agent_id in agent_ids:
                agents.append(await client.get_agent(agent_id=agent_id))
        return agents

    async def list_agents(self, *, limit: int | None = None) -> list[Agent]:
        async with self._client() as client:
            iterator: Callable[[], Any] | None = None
            candidate = getattr(client, "list_agents", None)
            if callable(candidate):
                iterator = candidate  # type: ignore[assignment]
            else:
                agents_attr = getattr(client, "agents", None)
                list_attr = getattr(agents_attr, "list", None)
                if callable(list_attr):
                    iterator = list_attr  # type: ignore[assignment]

            if iterator is None:
                raise RuntimeError("AgentsClient does not expose a list_agents operation.")

            results: list[Agent] = []
            produced = iterator()
            if hasattr(produced, "__aiter__"):
                async for agent in produced:  # type: ignore[attr-defined]
                    results.append(agent)
                    if limit is not None and len(results) >= limit:
                        break
            else:  # pragma: no cover - fallback for non-async iterables
                values = await produced  # type: ignore[func-returns-value]
                for agent in values:
                    results.append(agent)
                    if limit is not None and len(results) >= limit:
                        break

            return results
