"""Briefing orchestration for supervisor-facing narratives."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.indicators import IndicatorSnapshot, IndicatorStrategy


@dataclass(frozen=True)
class BriefingNarrative:
    """Narrative sections returned to supervisors."""

    indicators: list[IndicatorSnapshot]
    trends: list[str]
    alerts: list[str]
    focus_points: list[str]
    improvements: list[str]


# Strategy pattern: each indicator strategy encapsulates independent collection logic.
async def build_briefing(
    school_id: str,
    strategies: list[IndicatorStrategy],
    *,
    week_of: str | None = None,
) -> BriefingNarrative:
    tasks: list[asyncio.Task[IndicatorSnapshot]] = []
    async with asyncio.TaskGroup() as task_group:
        for strategy in strategies:
            tasks.append(task_group.create_task(strategy.collect(school_id, week_of=week_of)))

    indicator_snapshots = [task.result() for task in tasks]

    trends = [
        f"{snapshot.indicator} is {snapshot.trend} ({snapshot.score:.0%})."
        for snapshot in indicator_snapshots
    ]

    alerts = [
        f"{snapshot.indicator} dropped below target at {snapshot.score:.0%}."
        for snapshot in indicator_snapshots
        if snapshot.score < 0.65
    ]

    weakest = sorted(indicator_snapshots, key=lambda item: item.score)[:2]
    focus_points = [
        f"Prioritize {snapshot.indicator} with short-cycle intervention planning."
        for snapshot in weakest
    ]

    strongest = sorted(indicator_snapshots, key=lambda item: item.score, reverse=True)[:2]
    improvements = [
        f"Scale practices from {snapshot.indicator} where momentum is {snapshot.trend}."
        for snapshot in strongest
    ]

    return BriefingNarrative(
        indicators=indicator_snapshots,
        trends=trends,
        alerts=alerts,
        focus_points=focus_points,
        improvements=improvements,
    )
