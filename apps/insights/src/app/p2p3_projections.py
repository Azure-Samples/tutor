"""Deterministic P2/P3 projection builders for insights APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from tutor_lib.intelligence import (
    AbstentionMetadata,
    AppealState,
    CalibrationMetadata,
    CoverageMetadata,
    DriftMetadata,
    GovernanceAssumption,
    IntelligenceGovernanceMetadata,
    IntelligenceProvenance,
    ReviewState,
    SuppressionMetadata,
    UncertaintyMetadata,
)
from tutor_lib.lifelong_network import (
    AlumniAffiliation,
    CommunityEvent,
    CredentialAward,
    CredentialDefinition,
    DataUseAgreement,
    DeIdentificationRun,
    MentorRelationship,
    PortfolioArtifact,
    PublicationApproval,
    ReEntryPathway,
    ResearchDataset,
    VerificationRequest,
)

from app.schemas import (
    CausalDagEdge,
    CausalRefutationResult,
    CausalSensitivityCheck,
    CausalStudyCommand,
    CausalStudyReport,
    ConformalRiskItem,
    ConformalRiskReport,
    LifelongLearnerNetworkPayload,
    SchoolUnitIntelligencePayload,
    SchoolUnitMetric,
)

_BASE_TIME = datetime(2026, 5, 9, 12, 0, tzinfo=UTC)
_WORKFLOW_VERSION = "p2-p3-deterministic-projection-v1"


def _timestamp() -> str:
    return _BASE_TIME.isoformat()


def _seed_bytes(seed: str) -> bytes:
    return sha256(seed.encode()).digest()


def _seed_int(seed: str, minimum: int, maximum: int, *, byte_index: int = 0) -> int:
    if minimum >= maximum:
        return minimum
    digest = _seed_bytes(seed)
    return minimum + (digest[byte_index % len(digest)] % (maximum - minimum + 1))


def _seed_ratio(seed: str, minimum: float, maximum: float, *, byte_index: int = 0) -> float:
    digest = _seed_bytes(seed)
    span = maximum - minimum
    return round(minimum + ((digest[byte_index % len(digest)] / 255.0) * span), 3)


@dataclass(frozen=True, slots=True, kw_only=True)
class SmallCellSuppressionPolicy:
    """Policy object for small-cell suppression."""

    minimum_count: int = 10

    def evaluate(self, *, observed_count: int, suppressed_fields: tuple[str, ...]) -> SuppressionMetadata:
        if observed_count < self.minimum_count:
            return SuppressionMetadata(
                suppressed=True,
                reason="small_cell",
                minimum_count=self.minimum_count,
                observed_count=observed_count,
                suppressed_fields=suppressed_fields,
                rationale="The cell count is below the minimum reporting threshold.",
            )
        return SuppressionMetadata(
            suppressed=False,
            reason="none",
            minimum_count=self.minimum_count,
            observed_count=observed_count,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ConformalRiskPolicy:
    """Policy object for conformal label suppression and abstention."""

    minimum_sample_count: int = 30
    maximum_interval_width: float = 0.35

    def evaluate(self, *, sample_count: int, interval_width: float) -> tuple[SuppressionMetadata, AbstentionMetadata]:
        if sample_count < self.minimum_sample_count:
            suppression = SuppressionMetadata(
                suppressed=True,
                reason="low_sample",
                minimum_count=self.minimum_sample_count,
                observed_count=sample_count,
                suppressed_fields=("risk_label", "score"),
                rationale="The conformal calibration cohort is too small for learner-level labeling.",
            )
            abstention = AbstentionMetadata(
                abstained=True,
                degraded=True,
                reason="low_sample",
                fallback_behavior="human_review",
            )
            return suppression, abstention

        if interval_width > self.maximum_interval_width:
            suppression = SuppressionMetadata(
                suppressed=True,
                reason="wide_uncertainty",
                minimum_count=self.minimum_sample_count,
                observed_count=sample_count,
                suppressed_fields=("risk_label", "score"),
                rationale="The prediction interval is too wide for learner-level labeling.",
            )
            abstention = AbstentionMetadata(
                abstained=True,
                degraded=True,
                reason="wide_uncertainty",
                fallback_behavior="suppress_prediction",
            )
            return suppression, abstention

        return (
            SuppressionMetadata(
                suppressed=False,
                reason="none",
                minimum_count=self.minimum_sample_count,
                observed_count=sample_count,
            ),
            AbstentionMetadata(
                abstained=False,
                degraded=False,
                reason=None,
                fallback_behavior="show_advisory",
            ),
        )


def _calibration(*, seed: str, sample_count: int, observed_coverage: float | None = None) -> CalibrationMetadata:
    return CalibrationMetadata(
        calibration_set_id=f"calibration:{sha256(seed.encode()).hexdigest()[:12]}",
        calibrated_at=_timestamp(),
        method="deterministic-conformal-read-model",
        sample_count=sample_count,
        expected_coverage=0.9,
        observed_coverage=observed_coverage if observed_coverage is not None else _seed_ratio(seed, 0.84, 0.94),
    )


def _coverage(*, population: str, eligible_count: int, covered_count: int, minimum_required: int) -> CoverageMetadata:
    coverage_rate = round(covered_count / eligible_count, 3) if eligible_count else 0.0
    return CoverageMetadata(
        population=population,
        eligible_count=eligible_count,
        covered_count=covered_count,
        coverage_rate=coverage_rate,
        minimum_required=minimum_required,
    )


def _uncertainty(*, point_estimate: float | None, interval_width: float, method: str) -> UncertaintyMetadata:
    if point_estimate is None:
        return UncertaintyMetadata(
            point_estimate=None,
            lower_bound=None,
            upper_bound=None,
            confidence_level=0.9,
            interval_width=interval_width,
            method=method,
            wide=True,
            rationale="Point estimate was suppressed by policy.",
        )

    lower_bound = max(0.0, round(point_estimate - (interval_width / 2), 3))
    upper_bound = min(1.0, round(point_estimate + (interval_width / 2), 3))
    return UncertaintyMetadata(
        point_estimate=point_estimate,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        confidence_level=0.9,
        interval_width=interval_width,
        method=method,
        wide=interval_width > 0.35,
        rationale="Interval is computed from deterministic seeded projection inputs.",
    )


def _drift(*, seed: str, metric_name: str) -> DriftMetadata:
    score = _seed_ratio(seed, 0.02, 0.18)
    status = "stable" if score < 0.12 else "watch"
    return DriftMetadata(
        metric_name=metric_name,
        status=status,
        score=score,
        threshold=0.2,
        measured_at=_timestamp(),
        reference_window="2026-W01..2026-W08",
        current_window="2026-W09..2026-W14",
    )


def _governance(
    *,
    source_type: str,
    source_ids: tuple[str, ...],
    generator: str,
    assumptions: tuple[GovernanceAssumption, ...],
    uncertainty: UncertaintyMetadata,
    calibration: CalibrationMetadata,
    coverage: CoverageMetadata,
    suppression: SuppressionMetadata,
    abstention: AbstentionMetadata,
    review_required: bool,
    review_summary: str,
    drift: tuple[DriftMetadata, ...] = tuple(),
) -> IntelligenceGovernanceMetadata:
    return IntelligenceGovernanceMetadata(
        provenance=IntelligenceProvenance(
            source_type=source_type,
            source_ids=source_ids,
            generator=generator,
            workflow_version=_WORKFLOW_VERSION,
        ),
        assumptions=assumptions,
        uncertainty=uncertainty,
        calibration=calibration,
        coverage=coverage,
        drift=drift,
        suppression=suppression,
        review=ReviewState(
            status="required" if review_required else "recommended",
            required=review_required,
            summary=review_summary,
        ),
        appeal=AppealState(status="available", available=True),
        abstention=abstention,
        advisory_only=True,
        final_decision=False,
    )


def build_school_unit_intelligence(
    *,
    school_id: str,
    unit_id: str | None,
    tenant_id: str | None,
) -> SchoolUnitIntelligencePayload:
    resolved_unit_id = unit_id or "school-wide"
    policy = SmallCellSuppressionPolicy()
    metric_specs = (
        ("unit_attendance", "Attendance consistency"),
        ("unit_task_completion", "Task completion"),
        ("unit_formative_growth", "Formative growth"),
    )
    metrics: list[SchoolUnitMetric] = []
    suppress_first_metric = "small" in resolved_unit_id.lower()

    for metric_index, (metric_id, label) in enumerate(metric_specs):
        seed = f"{school_id}:{resolved_unit_id}:{metric_id}"
        sample_count = (
            policy.minimum_count - 2
            if suppress_first_metric and metric_index == 0
            else _seed_int(seed, 12, 96, byte_index=metric_index)
        )
        suppression = policy.evaluate(
            observed_count=sample_count,
            suppressed_fields=("value",),
        )
        value = None if suppression.suppressed else _seed_ratio(seed, 0.54, 0.93, byte_index=metric_index)
        metrics.append(
            SchoolUnitMetric(
                metric_id=metric_id,
                label=label,
                value=value,
                sample_count=sample_count,
                status="suppressed" if suppression.suppressed else "visible",
                suppression=suppression,
            )
        )

    observed_count = sum(metric.sample_count for metric in metrics)
    suppression = next((metric.suppression for metric in metrics if metric.suppression.suppressed), metrics[0].suppression)
    uncertainty = _uncertainty(
        point_estimate=None if suppression.suppressed else round(sum(metric.value or 0.0 for metric in metrics) / len(metrics), 3),
        interval_width=0.18 if not suppression.suppressed else 0.42,
        method="deterministic-school-unit-projection",
    )
    governance = _governance(
        source_type="school_unit_projection",
        source_ids=(f"school:{school_id}", f"unit:{resolved_unit_id}"),
        generator="insights.school-unit-intelligence",
        assumptions=(
            GovernanceAssumption(
                assumption_id="school-unit-cqrs-read",
                statement="Metrics are projection read models and do not perform cross-context database reads.",
                category="data_quality",
                evidence_refs=(f"school:{school_id}",),
            ),
            GovernanceAssumption(
                assumption_id="no-punitive-automation",
                statement="Outputs are advisory and cannot trigger punitive or final educational decisions.",
                category="policy",
            ),
        ),
        uncertainty=uncertainty,
        calibration=_calibration(seed=f"{school_id}:{resolved_unit_id}:unit", sample_count=observed_count),
        coverage=_coverage(
            population=f"school-unit:{resolved_unit_id}",
            eligible_count=max(observed_count, policy.minimum_count),
            covered_count=observed_count,
            minimum_required=policy.minimum_count,
        ),
        suppression=suppression,
        abstention=AbstentionMetadata(
            abstained=suppression.suppressed,
            degraded=suppression.suppressed,
            reason=suppression.reason if suppression.suppressed else None,
            fallback_behavior="deterministic_only",
        ),
        review_required=suppression.suppressed,
        review_summary="Suppressed school-unit cells require human interpretation before follow-up.",
        drift=(_drift(seed=f"{school_id}:{resolved_unit_id}:drift", metric_name="unit_distribution"),),
    )
    return SchoolUnitIntelligencePayload(
        school_id=school_id,
        unit_id=resolved_unit_id,
        tenant_id=tenant_id,
        generated_at=_timestamp(),
        metrics=metrics,
        governance=governance,
    )


def missing_causal_command_fields(command: CausalStudyCommand) -> list[str]:
    missing: list[str] = []
    if not command.dag_edges and (not command.dag or not command.dag.strip()):
        missing.append("dag")
    if not command.treatment or not command.treatment.strip():
        missing.append("treatment")
    if not command.outcome or not command.outcome.strip():
        missing.append("outcome")
    if not command.estimand or not command.estimand.strip():
        missing.append("estimand")
    if not command.population or not command.population.strip():
        missing.append("population")
    if not command.confounders or not any(str(item).strip() for item in command.confounders):
        missing.append("confounders")
    if not command.refutation_checks or not any(str(item).strip() for item in command.refutation_checks):
        missing.append("refutation_checks")
    return missing


# No GoF pattern applies -- these helpers validate deterministic command data.
def _normalize_causal_text(value: str) -> str:
    return " ".join(value.replace("_", " ").replace("-", " ").lower().split())


def _parse_dag_edges(dag: str | None) -> list[CausalDagEdge]:
    edges: list[CausalDagEdge] = []
    for raw_segment in (dag or "").replace("\n", ";").split(";"):
        if "->" not in raw_segment:
            continue
        source, target = raw_segment.split("->", 1)
        source = source.strip()
        target = target.strip()
        if source and target:
            edges.append(CausalDagEdge(source=source, target=target))
    return edges


def _causal_dag_edges(command: CausalStudyCommand) -> list[CausalDagEdge]:
    parsed_edges = _parse_dag_edges(command.dag)
    provided_edges = list(command.dag_edges or [])
    return [*parsed_edges, *provided_edges]


def _causal_dag_text(command: CausalStudyCommand, edges: list[CausalDagEdge]) -> str:
    if command.dag and command.dag.strip():
        return command.dag.strip()
    return "; ".join(f"{edge.source} -> {edge.target}" for edge in edges)


def _causal_node_present(*, node: str, dag_text: str, edges: list[CausalDagEdge]) -> bool:
    normalized_node = _normalize_causal_text(node)
    normalized_dag = _normalize_causal_text(dag_text)
    if normalized_node and normalized_node in normalized_dag:
        return True

    return any(
        normalized_node in {
            _normalize_causal_text(edge.source),
            _normalize_causal_text(edge.target),
        }
        for edge in edges
    )


def causal_command_validation_errors(command: CausalStudyCommand) -> list[dict[str, str]]:
    edges = _causal_dag_edges(command)
    dag_text = _causal_dag_text(command, edges)
    errors: list[dict[str, str]] = []

    if command.treatment and command.treatment.strip() and not _causal_node_present(
        node=command.treatment,
        dag_text=dag_text,
        edges=edges,
    ):
        errors.append(
            {
                "field": "dag",
                "reason": "treatment must appear in dag or dag_edges",
            }
        )

    if command.outcome and command.outcome.strip() and not _causal_node_present(
        node=command.outcome,
        dag_text=dag_text,
        edges=edges,
    ):
        errors.append(
            {
                "field": "dag",
                "reason": "outcome must appear in dag or dag_edges",
            }
        )

    return errors


def _causal_sensitivity_checks(
    *,
    confounders: list[str],
    estimand: str,
    seed: str,
) -> list[CausalSensitivityCheck]:
    return [
        CausalSensitivityCheck(
            check_id=f"sensitivity:{sha256(f'{seed}:{confounder}'.encode()).hexdigest()[:10]}",
            method="adjustment-set-review",
            target=confounder,
            status="needs_review",
            summary=f"{confounder} is included for human sensitivity review of {estimand}.",
        )
        for confounder in confounders
    ]


def _causal_refutation_results(refutation_checks: list[str]) -> list[CausalRefutationResult]:
    return [
        CausalRefutationResult(
            check=check,
            status="needs_review",
            result="Deterministic placeholder result requires qualified human review before program use.",
        )
        for check in refutation_checks
    ]


def build_causal_study_report(command: CausalStudyCommand) -> CausalStudyReport:
    confounders = [str(item).strip() for item in command.confounders or [] if str(item).strip()]
    refutation_checks = [str(item).strip() for item in command.refutation_checks or [] if str(item).strip()]
    edges = _causal_dag_edges(command)
    dag_text = _causal_dag_text(command, edges)
    estimand = command.estimand or ""
    seed = f"{command.school_id}:{command.treatment}:{command.outcome}:{estimand}:{command.population}"
    raw_effect = _seed_ratio(seed, 0.42, 0.68)
    effect_estimate = round(raw_effect - 0.5, 3)
    interval_width = 0.16 + (0.02 * min(len(confounders), 4))
    sensitivity_checks = _causal_sensitivity_checks(
        confounders=confounders,
        estimand=estimand,
        seed=seed,
    )
    refutation_results = _causal_refutation_results(refutation_checks)
    uncertainty = UncertaintyMetadata(
        point_estimate=effect_estimate,
        lower_bound=round(effect_estimate - interval_width, 3),
        upper_bound=round(effect_estimate + interval_width, 3),
        confidence_level=0.9,
        interval_width=round(interval_width * 2, 3),
        method="deterministic-causal-sensitivity-read-model",
        wide=False,
        rationale="Report is a deterministic command/read model and not a causal decision engine.",
    )
    governance = _governance(
        source_type="causal_study_projection",
        source_ids=(f"school:{command.school_id}", f"treatment:{command.treatment}", f"outcome:{command.outcome}"),
        generator="insights.causal-study",
        assumptions=(
            GovernanceAssumption(
                assumption_id="dag-required",
                statement="The supplied DAG or edge list is required before interpreting any effect estimate.",
                category="causal",
                evidence_refs=("dag",),
            ),
            GovernanceAssumption(
                assumption_id="estimand-required",
                statement="The estimand defines the precise causal quantity under review.",
                category="causal",
                evidence_refs=(estimand,),
            ),
            GovernanceAssumption(
                assumption_id="refutation-required",
                statement="Refutation checks must be reviewed before using the report for program planning.",
                category="causal",
                evidence_refs=tuple(refutation_checks),
            ),
        ),
        uncertainty=uncertainty,
        calibration=_calibration(seed=f"{seed}:causal", sample_count=64, observed_coverage=0.88),
        coverage=_coverage(population=command.population or "", eligible_count=84, covered_count=64, minimum_required=30),
        suppression=SuppressionMetadata(suppressed=False, reason="none"),
        abstention=AbstentionMetadata(
            abstained=False,
            degraded=False,
            reason=None,
            fallback_behavior="human_review",
        ),
        review_required=True,
        review_summary="Causal reports remain draft research artifacts until a qualified human review is completed.",
        drift=(_drift(seed=f"{seed}:causal-drift", metric_name="covariate_shift"),),
    )
    return CausalStudyReport(
        study_id=f"causal:{sha256(seed.encode()).hexdigest()[:16]}",
        school_id=command.school_id,
        tenant_id=command.tenant_id,
        generated_at=_timestamp(),
        dag=dag_text,
        dag_edges=edges,
        treatment=command.treatment or "",
        outcome=command.outcome or "",
        estimand=estimand,
        population=command.population or "",
        adjustment_set=confounders,
        refutation_checks=refutation_checks,
        sensitivity_checks=sensitivity_checks,
        refutation_results=refutation_results,
        effect_estimate=effect_estimate,
        uncertainty=uncertainty,
        governance=governance,
    )


def build_conformal_risk_report(
    *,
    learner_id: str,
    context_id: str,
    tenant_id: str | None,
    sample_count: int,
    interval_width: float,
) -> ConformalRiskReport:
    policy = ConformalRiskPolicy()
    suppression, abstention = policy.evaluate(sample_count=sample_count, interval_width=interval_width)
    seed = f"{learner_id}:{context_id}:conformal-risk"
    point_estimate = None if suppression.suppressed else _seed_ratio(seed, 0.38, 0.82)
    uncertainty = _uncertainty(
        point_estimate=point_estimate,
        interval_width=interval_width,
        method="split-conformal-deterministic-read-model",
    )
    risk = ConformalRiskItem(
        risk_id=f"risk:{sha256(seed.encode()).hexdigest()[:12]}",
        risk_type="engagement",
        risk_label=None if suppression.suppressed else "Needs advisory follow-up",
        score=point_estimate,
        sample_count=sample_count,
        uncertainty=uncertainty,
        suppression=suppression,
    )
    calibration = _calibration(seed=f"{seed}:calibration", sample_count=sample_count)
    coverage = _coverage(
        population=f"context:{context_id}",
        eligible_count=max(sample_count + 12, policy.minimum_sample_count),
        covered_count=sample_count,
        minimum_required=policy.minimum_sample_count,
    )
    drift = _drift(seed=f"{seed}:drift", metric_name="risk_score_distribution")
    governance = _governance(
        source_type="conformal_risk_projection",
        source_ids=(f"learner:{learner_id}", f"context:{context_id}"),
        generator="insights.conformal-risk",
        assumptions=(
            GovernanceAssumption(
                assumption_id="conformal-calibration-window",
                statement="Coverage assumes the current learner context resembles the calibration window.",
                category="model",
                evidence_refs=(calibration.calibration_set_id,),
            ),
            GovernanceAssumption(
                assumption_id="risk-is-advisory",
                statement="Risk labels are advisory and cannot produce final educational decisions.",
                category="policy",
            ),
        ),
        uncertainty=uncertainty,
        calibration=calibration,
        coverage=coverage,
        suppression=suppression,
        abstention=abstention,
        review_required=abstention.abstained,
        review_summary="Conformal risk labels require human review when the model abstains or degrades.",
        drift=(drift,),
    )
    return ConformalRiskReport(
        learner_id=learner_id,
        context_id=context_id,
        tenant_id=tenant_id,
        generated_at=_timestamp(),
        calibration=calibration,
        coverage=coverage,
        drift=drift,
        abstention=abstention,
        risks=[risk],
        governance=governance,
    )


def build_lifelong_network_payload(
    *,
    learner_id: str,
    context_id: str,
    tenant_id: str | None,
) -> LifelongLearnerNetworkPayload:
    credential_definition = CredentialDefinition(
        credential_id="credential:learning-analytics-foundations",
        title="Learning Analytics Foundations",
        issuer_id=tenant_id or "institution:local-dev",
        level="micro-credential",
        criteria_refs=("criteria:ethics", "criteria:applied-project"),
        status="active",
        version="2026.1",
    )
    credential = CredentialAward(
        award_id=f"award:{sha256(f'{learner_id}:credential'.encode()).hexdigest()[:12]}",
        credential_id=credential_definition.credential_id,
        learner_id=learner_id,
        awarded_at="2026-04-30T12:00:00+00:00",
        status="active",
        evidence_refs=("evidence:project-rubric", "evidence:mentor-review"),
    )
    research_dataset = ResearchDataset(
        dataset_id="dataset:lifelong-outcomes-aggregate",
        title="Lifelong outcomes aggregate",
        steward_id=tenant_id or "institution:local-dev",
        data_categories=("credential_status", "pathway_engagement", "portfolio_counts"),
        de_identified=True,
        consent_basis="learner-consented-aggregate-research",
        retention_until="2027-05-09",
    )
    suppression = SuppressionMetadata(suppressed=False, reason="none")
    uncertainty = _uncertainty(
        point_estimate=0.72,
        interval_width=0.22,
        method="deterministic-lifelong-network-read-model",
    )
    governance = _governance(
        source_type="lifelong_network_projection",
        source_ids=(f"learner:{learner_id}", f"context:{context_id}"),
        generator="insights.lifelong-network",
        assumptions=(
            GovernanceAssumption(
                assumption_id="learner-centered-minimization",
                statement="Learner-scoped identifiers appear only in learner-authorized context; direct contact fields and raw evidence are not returned.",
                category="policy",
            ),
            GovernanceAssumption(
                assumption_id="research-deidentified",
                statement="Research payloads use dataset descriptors and de-identified aggregate categories only.",
                category="access",
                evidence_refs=(research_dataset.dataset_id,),
            ),
        ),
        uncertainty=uncertainty,
        calibration=_calibration(seed=f"{learner_id}:lifelong", sample_count=48, observed_coverage=0.9),
        coverage=_coverage(population=f"learner:{learner_id}", eligible_count=4, covered_count=4, minimum_required=1),
        suppression=suppression,
        abstention=AbstentionMetadata(
            abstained=False,
            degraded=False,
            reason=None,
            fallback_behavior="show_advisory",
        ),
        review_required=False,
        review_summary="Portfolio and re-entry suggestions are learner-facing and advisory.",
    )
    return LifelongLearnerNetworkPayload(
        learner_id=learner_id,
        context_id=context_id,
        tenant_id=tenant_id,
        generated_at=_timestamp(),
        credential_definitions=[credential_definition],
        credentials=[credential],
        portfolio_artifacts=[
            PortfolioArtifact(
                artifact_id="artifact:capstone-summary",
                learner_id=learner_id,
                title="Capstone evidence summary",
                artifact_type="evidence_summary",
                evidence_refs=("evidence:project-rubric",),
                visibility="private",
                created_at="2026-04-28T12:00:00+00:00",
            )
        ],
        verification_requests=[
            VerificationRequest(
                request_id="verification:credential-status",
                credential_award_id=credential.award_id,
                requester_type="learner",
                requested_at="2026-05-01T12:00:00+00:00",
                status="verified",
                purpose="learner portfolio export",
            )
        ],
        alumni_affiliations=[
            AlumniAffiliation(
                affiliation_id="affiliation:alumni-primary",
                learner_id=learner_id,
                institution_id=tenant_id or "institution:local-dev",
                program_id="program:analytics",
                status="active",
                started_at="2026-05-01",
            )
        ],
        re_entry_pathways=[
            ReEntryPathway(
                pathway_id="pathway:advanced-analytics",
                learner_id=learner_id,
                title="Advanced analytics return pathway",
                target_program_id="program:advanced-analytics",
                readiness="eligible",
                status="open",
                recommended_steps=("confirm current goals", "review prerequisite refreshers"),
            )
        ],
        mentor_relationships=[
            MentorRelationship(
                relationship_id="mentor:analytics-mentor",
                learner_id=learner_id,
                mentor_id="mentor:aggregated-match",
                status="proposed",
                focus_areas=("portfolio review", "career transition"),
            )
        ],
        community_events=[
            CommunityEvent(
                event_id="event:alumni-reentry-lab",
                title="Alumni re-entry lab",
                host_id=tenant_id or "institution:local-dev",
                starts_at="2026-06-01T17:00:00+00:00",
                status="scheduled",
                audience="alumni",
            )
        ],
        research_datasets=[research_dataset],
        data_use_agreements=[
            DataUseAgreement(
                agreement_id="dua:lifelong-outcomes-aggregate",
                dataset_id=research_dataset.dataset_id,
                status="active",
                allowed_uses=("aggregate program improvement", "approved research publication"),
                prohibited_uses=("individual ranking", "punitive decisioning", "unauthorized re-identification"),
                expires_at="2027-05-09",
            )
        ],
        de_identification_runs=[
            DeIdentificationRun(
                run_id="deid:lifelong-outcomes-2026-05",
                dataset_id=research_dataset.dataset_id,
                method="cohort aggregation with direct identifier removal",
                completed_at="2026-05-09T12:00:00+00:00",
                residual_risk="low",
                reviewer_id="reviewer:privacy-board",
            )
        ],
        publication_approvals=[
            PublicationApproval(
                approval_id="publication:lifelong-outcomes-brief",
                dataset_id=research_dataset.dataset_id,
                status="review_required",
                submitted_at="2026-05-09T12:00:00+00:00",
                conditions=("aggregate-only tables", "suppress cohorts below threshold"),
            )
        ],
        data_minimization={
            "direct_identifiers": "not_returned",
            "learner_scoped_identifiers": "present_only_within_learner_authorized_context",
            "research_payload": "de_identified_dataset_descriptors_only",
            "portfolio_evidence": "evidence_refs_without_raw_content",
        },
        governance=governance,
    )