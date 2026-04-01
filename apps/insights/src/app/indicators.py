"""Indicator strategies used by the insights briefing flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Protocol


@dataclass(frozen=True)
class IndicatorSnapshot:
    """Normalized indicator output consumed by the briefing orchestrator."""

    indicator: str
    score: float
    trend: str
    summary: str


class IndicatorStrategy(Protocol):
    """Strategy contract for each modular indicator collector."""

    indicator_name: str

    async def collect(self, school_id: str, *, week_of: str | None = None) -> IndicatorSnapshot:
        """Collect an indicator snapshot for a school and period."""


class FabricReadAdapter(Protocol):
    """Read-only adapter contract for indicator retrieval from Fabric-backed sources."""

    async def read_indicator_score(
        self,
        *,
        school_id: str,
        indicator_name: str,
        week_of: str | None,
        minimum: float,
        maximum: float,
    ) -> float | None:
        """Return a normalized score or None when no source value is available."""


def _seeded_score(school_id: str, salt: str, minimum: float, maximum: float) -> float:
    digest = sha256(f"{school_id}:{salt}".encode()).digest()
    span = maximum - minimum
    return round(minimum + ((digest[0] / 255.0) * span), 3)


def _trend_for_score(score: float) -> str:
    if score >= 0.8:
        return "improving"
    if score >= 0.65:
        return "stable"
    return "declining"


@dataclass(frozen=True)
class DeterministicFabricReadAdapter:
    """Deterministic fallback adapter used when no external Fabric connection is configured."""

    async def read_indicator_score(
        self,
        *,
        school_id: str,
        indicator_name: str,
        week_of: str | None,
        minimum: float,
        maximum: float,
    ) -> float | None:
        return _seeded_score(school_id, f"{week_of}:{indicator_name}", minimum=minimum, maximum=maximum)


async def _collect_fabric_backed_score(
    fabric_adapter: FabricReadAdapter,
    *,
    school_id: str,
    indicator_name: str,
    week_of: str | None,
    minimum: float,
    maximum: float,
) -> float:
    score = await fabric_adapter.read_indicator_score(
        school_id=school_id,
        indicator_name=indicator_name,
        week_of=week_of,
        minimum=minimum,
        maximum=maximum,
    )
    if score is None:
        return _seeded_score(school_id, f"{week_of}:{indicator_name}", minimum=minimum, maximum=maximum)

    bounded = max(minimum, min(maximum, score))
    return round(bounded, 3)


@dataclass(frozen=True)
class StandardizedAssessmentStrategy:
    """Strategy for standardized assessment outcomes."""

    indicator_name: str = "standardized_assessments"
    fabric_adapter: FabricReadAdapter = field(default_factory=DeterministicFabricReadAdapter)

    async def collect(self, school_id: str, *, week_of: str | None = None) -> IndicatorSnapshot:
        score = await _collect_fabric_backed_score(
            self.fabric_adapter,
            school_id=school_id,
            indicator_name=self.indicator_name,
            week_of=week_of,
            minimum=0.52,
            maximum=0.93,
        )
        trend = _trend_for_score(score)
        summary = "Assessment proficiency is tracking expected curriculum milestones."
        return IndicatorSnapshot(indicator=self.indicator_name, score=score, trend=trend, summary=summary)


@dataclass(frozen=True)
class AttendanceStrategy:
    """Strategy for attendance consistency."""

    indicator_name: str = "attendance"
    fabric_adapter: FabricReadAdapter = field(default_factory=DeterministicFabricReadAdapter)

    async def collect(self, school_id: str, *, week_of: str | None = None) -> IndicatorSnapshot:
        score = await _collect_fabric_backed_score(
            self.fabric_adapter,
            school_id=school_id,
            indicator_name=self.indicator_name,
            week_of=week_of,
            minimum=0.58,
            maximum=0.97,
        )
        trend = _trend_for_score(score)
        summary = "Attendance consistency indicates classroom stability and student engagement."
        return IndicatorSnapshot(indicator=self.indicator_name, score=score, trend=trend, summary=summary)


@dataclass(frozen=True)
class TaskCompletionStrategy:
    """Strategy for assignment/task completion rates."""

    indicator_name: str = "task_completion"
    fabric_adapter: FabricReadAdapter = field(default_factory=DeterministicFabricReadAdapter)

    async def collect(self, school_id: str, *, week_of: str | None = None) -> IndicatorSnapshot:
        score = await _collect_fabric_backed_score(
            self.fabric_adapter,
            school_id=school_id,
            indicator_name=self.indicator_name,
            week_of=week_of,
            minimum=0.49,
            maximum=0.95,
        )
        trend = _trend_for_score(score)
        summary = "Task completion reflects instructional pacing and intervention effectiveness."
        return IndicatorSnapshot(indicator=self.indicator_name, score=score, trend=trend, summary=summary)
