"""Utilities for preserving callback tool metadata at the facade boundary."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any


class ToolBuilder:
    """Return callbacks unchanged for Foundry-managed tool configuration."""

    def from_callbacks(self, callbacks: Iterable[Callable[..., Any]]) -> list[Callable[..., Any]]:
        return list(callbacks)
