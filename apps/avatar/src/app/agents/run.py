"""Execution helpers for running agents."""

from __future__ import annotations

import asyncio
from typing import Any

from agent_framework import ChatAgent


class AgentRunContext:
    """Wrapper around a ChatAgent to provide convenience methods."""

    def __init__(self, agent: ChatAgent) -> None:
        self._agent = agent

    async def run(self, message: str, **kwargs: Any) -> Any:
        """Execute the agent with a single message and return the response."""
        result = self._agent.run(message)
        if asyncio.iscoroutine(result):
            return await result
        return result
