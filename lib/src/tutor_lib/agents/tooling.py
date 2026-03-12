"""Utilities for turning Python callables into Agent Framework tools."""

from __future__ import annotations

import agent_framework as _af
from collections.abc import Callable, Iterable
from typing import Any

_agent_tool = getattr(_af, "tool", getattr(_af, "ai_function", None))


class ToolBuilder:
    """Wraps plain callables as Agent Framework tool definitions."""

    def from_callbacks(self, callbacks: Iterable[Callable[..., Any]]) -> list[Callable[..., Any]]:
        if _agent_tool is None:
            raise RuntimeError(
                "The installed agent-framework package does not export tool/ai_function. "
                "Install a compatible agent-framework version."
            )
        wrapped: list[Callable[..., Any]] = []
        for callback in callbacks:
            if hasattr(callback, "__agent_tool_wrapped__"):
                wrapped.append(callback)
                continue
            setattr(callback, "__agent_tool_wrapped__", True)
            wrapped.append(_agent_tool()(callback))
        return wrapped
