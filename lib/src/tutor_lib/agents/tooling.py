"""Utilities for turning Python callables into Agent Framework tools."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from agent_framework import ai_function


class ToolBuilder:
    """Wraps plain callables as Agent Framework tool definitions."""

    def from_callbacks(self, callbacks: Iterable[Callable[..., Any]]) -> list[Callable[..., Any]]:
        wrapped: list[Callable[..., Any]] = []
        for callback in callbacks:
            if hasattr(callback, "__agent_tool_wrapped__"):
                wrapped.append(callback)
                continue
            setattr(callback, "__agent_tool_wrapped__", True)
            wrapped.append(ai_function()(callback))
        return wrapped
