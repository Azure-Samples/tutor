"""Shared governance contracts for deterministic and ML-backed intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

GOVERNANCE_SCHEMA_VERSION = "2.0"

AssumptionCategory = Literal["data_quality", "causal", "model", "policy", "access"]
DriftStatus = Literal["stable", "watch", "drifted", "unknown"]
SuppressionReason = Literal[
    "none",
    "small_cell",
    "wide_uncertainty",
    "low_sample",
    "low_coverage",
    "policy",
    "manual_review",
]
ReviewStatus = Literal["required", "recommended", "not_required", "completed"]
AppealStatus = Literal["unavailable", "available", "requested", "in_review", "resolved"]
FallbackBehavior = Literal[
    "deterministic_only",
    "human_review",
    "show_advisory",
    "suppress_prediction",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class GovernanceAssumption:
    """Assumption required to interpret an intelligence payload."""

    assumption_id: str
    statement: str
    category: AssumptionCategory
    evidence_refs: tuple[str, ...] = tuple()
    required_for_use: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class IntelligenceProvenance:
    """Source lineage for governed intelligence contracts."""

    source_type: str
    source_ids: tuple[str, ...]
    generator: str
    workflow_version: str
    model: str | None = None
    prompt_version: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UncertaintyMetadata:
    """Uncertainty interval and interpretation state for an estimate."""

    point_estimate: float | None
    lower_bound: float | None
    upper_bound: float | None
    confidence_level: float
    interval_width: float | None
    method: str
    wide: bool = False
    rationale: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class CalibrationMetadata:
    """Calibration set and observed calibration quality."""

    calibration_set_id: str
    calibrated_at: str
    method: str
    sample_count: int
    expected_coverage: float
    observed_coverage: float


@dataclass(frozen=True, slots=True, kw_only=True)
class CoverageMetadata:
    """Population coverage for a projection or governed report."""

    population: str
    eligible_count: int
    covered_count: int
    coverage_rate: float
    minimum_required: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DriftMetadata:
    """Drift signal comparing the current window to a reference window."""

    metric_name: str
    status: DriftStatus
    score: float | None
    threshold: float | None
    measured_at: str
    reference_window: str
    current_window: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SuppressionMetadata:
    """Suppression state for fields hidden by policy."""

    suppressed: bool
    reason: SuppressionReason
    minimum_count: int | None = None
    observed_count: int | None = None
    suppressed_fields: tuple[str, ...] = tuple()
    rationale: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewState:
    """Human review state for advisory or high-impact outputs."""

    status: ReviewStatus
    required: bool
    summary: str
    reviewer_id: str | None = None
    reviewed_at: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AppealState:
    """Appeal availability and lifecycle for reviewable outputs."""

    status: AppealStatus
    available: bool
    appeal_id: str | None = None
    submitted_at: str | None = None
    resolution_summary: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AbstentionMetadata:
    """Abstention, degraded mode, and fallback behavior."""

    abstained: bool
    degraded: bool
    reason: str | None
    fallback_behavior: FallbackBehavior


def _default_provenance() -> IntelligenceProvenance:
    return IntelligenceProvenance(
        source_type="deterministic_projection",
        source_ids=tuple(),
        generator="tutor_lib.intelligence",
        workflow_version=GOVERNANCE_SCHEMA_VERSION,
    )


def _default_uncertainty() -> UncertaintyMetadata:
    return UncertaintyMetadata(
        point_estimate=None,
        lower_bound=None,
        upper_bound=None,
        confidence_level=0.0,
        interval_width=None,
        method="not_applicable",
    )


def _default_calibration() -> CalibrationMetadata:
    return CalibrationMetadata(
        calibration_set_id="not_applicable",
        calibrated_at="",
        method="not_applicable",
        sample_count=0,
        expected_coverage=0.0,
        observed_coverage=0.0,
    )


def _default_coverage() -> CoverageMetadata:
    return CoverageMetadata(
        population="not_applicable",
        eligible_count=0,
        covered_count=0,
        coverage_rate=0.0,
        minimum_required=0,
    )


def _default_suppression() -> SuppressionMetadata:
    return SuppressionMetadata(suppressed=False, reason="none")


def _default_review() -> ReviewState:
    return ReviewState(
        status="recommended",
        required=False,
        summary="Review is recommended before acting on advisory outputs.",
    )


def _default_appeal() -> AppealState:
    return AppealState(status="available", available=True)


def _default_abstention() -> AbstentionMetadata:
    return AbstentionMetadata(
        abstained=False,
        degraded=False,
        reason=None,
        fallback_behavior="show_advisory",
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class IntelligenceGovernanceMetadata:
    """Complete governance envelope for P2/P3 intelligence contracts."""

    provenance: IntelligenceProvenance = field(default_factory=_default_provenance)
    assumptions: tuple[GovernanceAssumption, ...] = tuple()
    uncertainty: UncertaintyMetadata = field(default_factory=_default_uncertainty)
    calibration: CalibrationMetadata = field(default_factory=_default_calibration)
    coverage: CoverageMetadata = field(default_factory=_default_coverage)
    drift: tuple[DriftMetadata, ...] = tuple()
    suppression: SuppressionMetadata = field(default_factory=_default_suppression)
    review: ReviewState = field(default_factory=_default_review)
    appeal: AppealState = field(default_factory=_default_appeal)
    abstention: AbstentionMetadata = field(default_factory=_default_abstention)
    advisory_only: bool = True
    final_decision: bool = False