"""Execution helpers for running agents."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Any

from agent_framework import AgentRunResponse, ChatAgent


@dataclass(slots=True)
class AgentToolkit:
    """Bundle of tools shared across agent runs."""
    tools: Iterable[Any]


class AgentRunContext:
    """Wrapper around a chat agent to provide convenience methods."""

    def __init__(self, agent: ChatAgent) -> None:
        self._agent = agent
        self._thread = agent.get_new_thread()

    async def run(self, message: str, **options: Any) -> AgentRunResponse:
        """Execute the agent with a single message and return the response."""

        return await self._agent.run(message, thread=self._thread, **options)

    async def stream(self, message: str, **options: Any) -> AsyncIterator[str]:
        """Yield streaming text results from the agent."""

        async for update in self._agent.run_stream(message, thread=self._thread, **options):
            if update.text:
                yield update.text
