"""Utilities for turning Python callables into Agent Framework tools."""

from __future__ import annotations

import agent_framework as agent_framework_module
from typing import Any
from collections.abc import Callable, Iterable

def _wrap_agent_tool(callback: Any) -> Any:
    decorator_symbol = getattr(agent_framework_module, "tool", None)
    if decorator_symbol is None:
        decorator_symbol = getattr(agent_framework_module, "ai_function", None)
    if decorator_symbol is None or not callable(decorator_symbol):
        return callback

    try:
        decorator_or_wrapped = decorator_symbol(callback)
        return decorator_or_wrapped if decorator_or_wrapped is not None else callback
    except TypeError:
        try:
            decorator = decorator_symbol()
            if callable(decorator):
                decorated = decorator(callback)
                return decorated if decorated is not None else callback
        except TypeError:
            return callback
    return callback


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
            wrapped.append(_wrap_agent_tool(callback))
        return wrapped
