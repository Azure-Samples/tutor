"""Shared lifelong learner network contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CredentialDefinitionStatus = Literal["draft", "active", "retired"]
CredentialAwardStatus = Literal["pending_review", "active", "expired", "revoked"]
VerificationStatus = Literal["requested", "verified", "rejected", "expired"]
AffiliationStatus = Literal["active", "inactive", "opted_out"]
PathwayStatus = Literal["open", "waitlist", "closed"]
MentorRelationshipStatus = Literal["proposed", "active", "paused", "ended"]
CommunityEventStatus = Literal["scheduled", "completed", "cancelled"]
AgreementStatus = Literal["draft", "active", "expired", "revoked"]
ApprovalStatus = Literal["draft", "review_required", "approved", "rejected", "revoked"]


@dataclass(frozen=True, slots=True, kw_only=True)
class CredentialDefinition:
    """Definition of an institution-issued credential."""

    credential_id: str
    title: str
    issuer_id: str
    level: str
    criteria_refs: tuple[str, ...]
    status: CredentialDefinitionStatus
    version: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CredentialRevocation:
    """Revocation record for a previously awarded credential."""

    revoked_at: str
    reason: str
    authority_id: str
    appeal_available: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class CredentialAward:
    """Award or current status of a learner credential."""

    award_id: str
    credential_id: str
    learner_id: str
    awarded_at: str | None
    status: CredentialAwardStatus
    evidence_refs: tuple[str, ...]
    expires_at: str | None = None
    revocation: CredentialRevocation | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PortfolioArtifact:
    """Learner-owned portfolio artifact with minimized evidence references."""

    artifact_id: str
    learner_id: str
    title: str
    artifact_type: str
    evidence_refs: tuple[str, ...]
    visibility: Literal["private", "institution", "public"]
    created_at: str


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationRequest:
    """Third-party or institution verification request."""

    request_id: str
    credential_award_id: str
    requester_type: str
    requested_at: str
    status: VerificationStatus
    purpose: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AlumniAffiliation:
    """Alumni relationship to an institution or program."""

    affiliation_id: str
    learner_id: str
    institution_id: str
    program_id: str | None
    status: AffiliationStatus
    started_at: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReEntryPathway:
    """Curated path for returning learners or alumni."""

    pathway_id: str
    learner_id: str
    title: str
    target_program_id: str
    readiness: Literal["eligible", "needs_review", "not_ready"]
    status: PathwayStatus
    recommended_steps: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class MentorRelationship:
    """Mentoring relationship that remains learner-consented and reviewable."""

    relationship_id: str
    learner_id: str
    mentor_id: str
    status: MentorRelationshipStatus
    started_at: str | None = None
    focus_areas: tuple[str, ...] = tuple()


@dataclass(frozen=True, slots=True, kw_only=True)
class CommunityEvent:
    """Community event surfaced to lifelong learners."""

    event_id: str
    title: str
    host_id: str
    starts_at: str
    status: CommunityEventStatus
    audience: Literal["learners", "alumni", "mentors", "research_participants"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResearchDataset:
    """Governed research dataset descriptor."""

    dataset_id: str
    title: str
    steward_id: str
    data_categories: tuple[str, ...]
    de_identified: bool
    consent_basis: str
    retention_until: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DataUseAgreement:
    """Agreement constraining education or research data use."""

    agreement_id: str
    dataset_id: str
    status: AgreementStatus
    allowed_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    expires_at: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DeIdentificationRun:
    """Record of a de-identification process before research use."""

    run_id: str
    dataset_id: str
    method: str
    completed_at: str
    residual_risk: Literal["low", "medium", "high"]
    reviewer_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicationApproval:
    """Approval state for publication using governed learner data."""

    approval_id: str
    dataset_id: str
    status: ApprovalStatus
    submitted_at: str
    reviewer_id: str | None = None
    conditions: tuple[str, ...] = tuple()