"""Utilities for turning Python callables into Agent Framework tools."""

from __future__ import annotations

from typing import Any
from collections.abc import Callable, Iterable

from agent_framework import ai_function


class ToolBuilder:
    """Create agent tools from Python callables with minimal boilerplate."""

    def from_callbacks(self, callbacks: Iterable[Callable[..., Any]]) -> list[Callable[..., Any]]:
        """Return a list of tool-wrapped callables."""

        wrapped: list[Callable[..., Any]] = []
        for callback in callbacks:
            if hasattr(callback, "__agent_tool_wrapped__"):
                wrapped.append(callback)
                continue

            # Attach metadata so we don't wrap twice.
            setattr(callback, "__agent_tool_wrapped__", True)
            wrapped.append(ai_function()(callback))
        return wrapped
