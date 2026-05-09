"""Local metadata helpers for configuration agent tools."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentToolkit:
    """Bundle of tools shared across agent runs."""

    tools: Iterable[Any]
