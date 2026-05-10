"""Tests for P2/P3 shared contracts."""

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
    CredentialRevocation,
    DataUseAgreement,
    DeIdentificationRun,
    MentorRelationship,
    PortfolioArtifact,
    PublicationApproval,
    ReEntryPathway,
    ResearchDataset,
    VerificationRequest,
)


def test_intelligence_governance_contract_exposes_required_metadata() -> None:
    governance = IntelligenceGovernanceMetadata(
        provenance=IntelligenceProvenance(
            source_type="unit-test",
            source_ids=("source:1",),
            generator="tests",
            workflow_version="test-v1",
        ),
        assumptions=(
            GovernanceAssumption(
                assumption_id="assumption:1",
                statement="Sample data is representative.",
                category="model",
            ),
        ),
        uncertainty=UncertaintyMetadata(
            point_estimate=0.5,
            lower_bound=0.4,
            upper_bound=0.6,
            confidence_level=0.9,
            interval_width=0.2,
            method="unit-test",
        ),
        calibration=CalibrationMetadata(
            calibration_set_id="calibration:1",
            calibrated_at="2026-05-09T12:00:00Z",
            method="unit-test",
            sample_count=30,
            expected_coverage=0.9,
            observed_coverage=0.88,
        ),
        coverage=CoverageMetadata(
            population="learners",
            eligible_count=40,
            covered_count=30,
            coverage_rate=0.75,
            minimum_required=30,
        ),
        drift=(
            DriftMetadata(
                metric_name="score",
                status="stable",
                score=0.03,
                threshold=0.2,
                measured_at="2026-05-09T12:00:00Z",
                reference_window="baseline",
                current_window="current",
            ),
        ),
        suppression=SuppressionMetadata(
            suppressed=True,
            reason="small_cell",
            minimum_count=10,
            observed_count=6,
            suppressed_fields=("label",),
        ),
        review=ReviewState(status="required", required=True, summary="Review required."),
        appeal=AppealState(status="available", available=True),
        abstention=AbstentionMetadata(
            abstained=True,
            degraded=True,
            reason="small_cell",
            fallback_behavior="human_review",
        ),
    )

    assert governance.assumptions[0].required_for_use
    assert governance.uncertainty.interval_width == 0.2
    assert governance.calibration.observed_coverage == 0.88
    assert governance.coverage.minimum_required == 30
    assert governance.drift[0].status == "stable"
    assert governance.suppression.reason == "small_cell"
    assert governance.review.required
    assert governance.appeal.available
    assert governance.abstention.degraded
    assert governance.advisory_only
    assert not governance.final_decision


def test_lifelong_network_contracts_cover_required_concepts() -> None:
    credential_definition = CredentialDefinition(
        credential_id="credential:1",
        title="Credential",
        issuer_id="institution:1",
        level="micro",
        criteria_refs=("criteria:1",),
        status="active",
        version="1",
    )
    revocation = CredentialRevocation(
        revoked_at="2026-05-09T12:00:00Z",
        reason="issued in error",
        authority_id="authority:1",
    )
    credential = CredentialAward(
        award_id="award:1",
        credential_id=credential_definition.credential_id,
        learner_id="learner:1",
        awarded_at="2026-05-01T12:00:00Z",
        status="revoked",
        evidence_refs=("evidence:1",),
        revocation=revocation,
    )
    portfolio = PortfolioArtifact(
        artifact_id="artifact:1",
        learner_id="learner:1",
        title="Portfolio",
        artifact_type="summary",
        evidence_refs=("evidence:1",),
        visibility="private",
        created_at="2026-05-09T12:00:00Z",
    )
    verification = VerificationRequest(
        request_id="verification:1",
        credential_award_id=credential.award_id,
        requester_type="learner",
        requested_at="2026-05-09T12:00:00Z",
        status="requested",
        purpose="portfolio export",
    )
    affiliation = AlumniAffiliation(
        affiliation_id="affiliation:1",
        learner_id="learner:1",
        institution_id="institution:1",
        program_id="program:1",
        status="active",
        started_at="2026-05-01",
    )
    pathway = ReEntryPathway(
        pathway_id="pathway:1",
        learner_id="learner:1",
        title="Return path",
        target_program_id="program:2",
        readiness="eligible",
        status="open",
        recommended_steps=("confirm goals",),
    )
    mentor = MentorRelationship(
        relationship_id="mentor:1",
        learner_id="learner:1",
        mentor_id="mentor:2",
        status="proposed",
    )
    event = CommunityEvent(
        event_id="event:1",
        title="Community event",
        host_id="institution:1",
        starts_at="2026-06-01T12:00:00Z",
        status="scheduled",
        audience="alumni",
    )
    dataset = ResearchDataset(
        dataset_id="dataset:1",
        title="Dataset",
        steward_id="institution:1",
        data_categories=("credential_status",),
        de_identified=True,
        consent_basis="consent",
        retention_until="2027-05-09",
    )
    agreement = DataUseAgreement(
        agreement_id="dua:1",
        dataset_id=dataset.dataset_id,
        status="active",
        allowed_uses=("approved research",),
        prohibited_uses=("re-identification",),
        expires_at="2027-05-09",
    )
    de_identification = DeIdentificationRun(
        run_id="deid:1",
        dataset_id=dataset.dataset_id,
        method="aggregation",
        completed_at="2026-05-09T12:00:00Z",
        residual_risk="low",
    )
    approval = PublicationApproval(
        approval_id="publication:1",
        dataset_id=dataset.dataset_id,
        status="review_required",
        submitted_at="2026-05-09T12:00:00Z",
    )

    assert credential_definition.status == "active"
    assert credential.revocation is revocation
    assert portfolio.visibility == "private"
    assert verification.status == "requested"
    assert affiliation.status == "active"
    assert pathway.status == "open"
    assert mentor.status == "proposed"
    assert event.audience == "alumni"
    assert dataset.de_identified
    assert agreement.prohibited_uses == ("re-identification",)
    assert de_identification.residual_risk == "low"
    assert approval.status == "review_required"