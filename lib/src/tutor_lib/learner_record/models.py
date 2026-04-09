"""Canonical learner-record event contracts and builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Literal, Self

EVENT_SCHEMA_VERSION = "1.0"
LEARNER_RECORD_DOC_TYPE = "learner_record_event"
LEARNER_RECORD_WORKFLOW_VERSION = "learner-record-event-v1"

EventStatus = Literal["confirmed", "advisory", "degraded", "needs_review"]
EvaluationState = Literal["evaluated", "pending", "not_required"]
ReviewStatus = Literal["required", "recommended", "not_required", "completed"]


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordDeepLink:
    label: str
    href: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordEvidenceRef:
    evidence_id: str
    label: str
    kind: str
    deep_link: LearnerRecordDeepLink | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordSourceMetadata:
    service: str
    capability: str
    entity_type: str | None = None
    entity_id: str | None = None
    institution_id: str | None = None
    school_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordActor:
    role: str
    actor_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordReviewMetadata:
    status: ReviewStatus
    summary: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordProvenanceMetadata:
    source_type: str
    source_ids: tuple[str, ...]
    generator: str
    workflow_version: str
    model: str | None = None
    prompt_version: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordTrustMetadata:
    provenance: LearnerRecordProvenanceMetadata
    evaluation_state: EvaluationState
    human_review: LearnerRecordReviewMetadata
    degraded: bool = False
    advisory_only: bool = True
    note: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordCompensation:
    compensates_event_id: str
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecordEvent:
    event_id: str
    event_version: str
    learner_id: str
    learner_key: str
    event_type: str
    occurred_at: str
    recorded_at: str
    title: str
    summary: str
    status: EventStatus
    source: LearnerRecordSourceMetadata
    actor: LearnerRecordActor
    trust: LearnerRecordTrustMetadata
    deep_link: LearnerRecordDeepLink
    evidence_refs: tuple[LearnerRecordEvidenceRef, ...] = tuple()
    idempotency_key: str
    compensation: LearnerRecordCompensation | None = None


def build_learner_key(*, learner_id: str, institution_id: str | None = None) -> str:
    normalized_learner_id = learner_id.strip()
    normalized_institution_id = (institution_id or "").strip()
    if normalized_institution_id:
        return f"{normalized_institution_id}:{normalized_learner_id}"
    return normalized_learner_id


def normalize_timestamp(value: datetime | str | None, *, default: datetime | None = None) -> str:
    if value is None:
        resolved = default or datetime.now(UTC)
        return resolved.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")

    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        parsed = value

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def build_event_idempotency_key(
    *,
    learner_key: str,
    event_type: str,
    source_service: str,
    source_entity_type: str | None,
    source_entity_id: str | None,
    occurred_at: str,
    title: str,
    compensation_event_id: str | None,
) -> str:
    return "|".join(
        (
            EVENT_SCHEMA_VERSION,
            learner_key,
            event_type,
            source_service,
            source_entity_type or "",
            source_entity_id or "",
            occurred_at,
            title,
            compensation_event_id or "",
        )
    )


def build_event_id(idempotency_key: str) -> str:
    return sha256(idempotency_key.encode("utf-8")).hexdigest()


def build_trust_metadata(
    *,
    source_type: str,
    source_ids: list[str],
    generator: str,
    note: str,
    degraded: bool,
    evaluation_state: EvaluationState,
    review_status: ReviewStatus,
    review_summary: str,
    advisory_only: bool,
    model: str | None = None,
    prompt_version: str | None = None,
    workflow_version: str = LEARNER_RECORD_WORKFLOW_VERSION,
) -> LearnerRecordTrustMetadata:
    return LearnerRecordTrustMetadata(
        provenance=LearnerRecordProvenanceMetadata(
            source_type=source_type,
            source_ids=tuple(source_ids),
            generator=generator,
            workflow_version=workflow_version,
            model=model,
            prompt_version=prompt_version,
        ),
        evaluation_state=evaluation_state,
        human_review=LearnerRecordReviewMetadata(status=review_status, summary=review_summary),
        degraded=degraded,
        advisory_only=advisory_only,
        note=note,
    )


def sort_events(events: list[LearnerRecordEvent]) -> list[LearnerRecordEvent]:
    return sorted(events, key=lambda event: (event.occurred_at, event.recorded_at, event.event_id), reverse=True)


@dataclass(slots=True, kw_only=True)
class LearnerRecordEventBuilder:
    learner_id: str
    learner_key: str
    event_type: str
    source: LearnerRecordSourceMetadata
    _occurred_at: str | None = None
    _recorded_at: str | None = None
    _title: str | None = None
    _summary: str | None = None
    _status: EventStatus = "confirmed"
    _actor: LearnerRecordActor | None = None
    _trust: LearnerRecordTrustMetadata | None = None
    _deep_link: LearnerRecordDeepLink | None = None
    _evidence_refs: list[LearnerRecordEvidenceRef] = field(default_factory=list)
    _idempotency_key: str | None = None
    _compensation: LearnerRecordCompensation | None = None

    def occurred_at(self, value: datetime | str) -> Self:
        self._occurred_at = normalize_timestamp(value)
        return self

    def recorded_at(self, value: datetime | str) -> Self:
        self._recorded_at = normalize_timestamp(value)
        return self

    def title(self, value: str) -> Self:
        self._title = value.strip()
        return self

    def summary(self, value: str) -> Self:
        self._summary = value.strip()
        return self

    def status(self, value: EventStatus) -> Self:
        self._status = value
        return self

    def actor(self, *, role: str, actor_id: str | None = None) -> Self:
        self._actor = LearnerRecordActor(role=role, actor_id=actor_id)
        return self

    def trust(self, value: LearnerRecordTrustMetadata) -> Self:
        self._trust = value
        return self

    def deep_link(self, *, label: str, href: str) -> Self:
        self._deep_link = LearnerRecordDeepLink(label=label, href=href)
        return self

    def add_evidence(self, value: LearnerRecordEvidenceRef) -> Self:
        self._evidence_refs.append(value)
        return self

    def idempotency_key(self, value: str) -> Self:
        self._idempotency_key = value.strip()
        return self

    def compensates(self, *, event_id: str, reason: str) -> Self:
        self._compensation = LearnerRecordCompensation(
            compensates_event_id=event_id,
            reason=reason,
        )
        return self

    def build(self) -> LearnerRecordEvent:
        missing_fields: list[str] = []
        if not self._occurred_at:
            missing_fields.append("occurred_at")
        if not self._title:
            missing_fields.append("title")
        if not self._summary:
            missing_fields.append("summary")
        if self._actor is None:
            missing_fields.append("actor")
        if self._trust is None:
            missing_fields.append("trust")
        if self._deep_link is None:
            missing_fields.append("deep_link")
        if missing_fields:
            raise ValueError(f"LearnerRecordEventBuilder is missing required fields: {', '.join(missing_fields)}")

        occurred_at = self._occurred_at
        recorded_at = self._recorded_at or normalize_timestamp(None)
        idempotency_key = self._idempotency_key or build_event_idempotency_key(
            learner_key=self.learner_key,
            event_type=self.event_type,
            source_service=self.source.service,
            source_entity_type=self.source.entity_type,
            source_entity_id=self.source.entity_id,
            occurred_at=occurred_at,
            title=self._title,
            compensation_event_id=(
                self._compensation.compensates_event_id if self._compensation is not None else None
            ),
        )

        return LearnerRecordEvent(
            event_id=build_event_id(idempotency_key),
            event_version=EVENT_SCHEMA_VERSION,
            learner_id=self.learner_id,
            learner_key=self.learner_key,
            event_type=self.event_type,
            occurred_at=occurred_at,
            recorded_at=recorded_at,
            title=self._title,
            summary=self._summary,
            status=self._status,
            source=self.source,
            actor=self._actor,
            trust=self._trust,
            deep_link=self._deep_link,
            evidence_refs=tuple(self._evidence_refs),
            idempotency_key=idempotency_key,
            compensation=self._compensation,
        )


def event_to_payload(event: LearnerRecordEvent) -> dict[str, object]:
    return {
        "id": event.event_id,
        "docType": LEARNER_RECORD_DOC_TYPE,
        "event_id": event.event_id,
        "event_version": event.event_version,
        "learner_id": event.learner_id,
        "learner_key": event.learner_key,
        "event_type": event.event_type,
        "occurred_at": event.occurred_at,
        "recorded_at": event.recorded_at,
        "title": event.title,
        "summary": event.summary,
        "status": event.status,
        "source": {
            "service": event.source.service,
            "capability": event.source.capability,
            "entity_type": event.source.entity_type,
            "entity_id": event.source.entity_id,
            "institution_id": event.source.institution_id,
            "school_id": event.source.school_id,
        },
        "actor": {
            "role": event.actor.role,
            "actor_id": event.actor.actor_id,
        },
        "trust": {
            "provenance": {
                "source_type": event.trust.provenance.source_type,
                "source_ids": list(event.trust.provenance.source_ids),
                "generator": event.trust.provenance.generator,
                "workflow_version": event.trust.provenance.workflow_version,
                "model": event.trust.provenance.model,
                "prompt_version": event.trust.provenance.prompt_version,
            },
            "evaluation_state": event.trust.evaluation_state,
            "human_review": {
                "status": event.trust.human_review.status,
                "summary": event.trust.human_review.summary,
            },
            "degraded": event.trust.degraded,
            "advisory_only": event.trust.advisory_only,
            "note": event.trust.note,
        },
        "deep_link": {
            "label": event.deep_link.label,
            "href": event.deep_link.href,
        },
        "evidence_refs": [
            {
                "evidence_id": evidence.evidence_id,
                "label": evidence.label,
                "kind": evidence.kind,
                "deep_link": (
                    {
                        "label": evidence.deep_link.label,
                        "href": evidence.deep_link.href,
                    }
                    if evidence.deep_link is not None
                    else None
                ),
            }
            for evidence in event.evidence_refs
        ],
        "idempotency_key": event.idempotency_key,
        "compensation": (
            {
                "compensates_event_id": event.compensation.compensates_event_id,
                "reason": event.compensation.reason,
            }
            if event.compensation is not None
            else None
        ),
    }


def payload_to_event(payload: dict[str, Any]) -> LearnerRecordEvent:
    raw_source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    raw_actor = payload.get("actor") if isinstance(payload.get("actor"), dict) else {}
    raw_trust = payload.get("trust") if isinstance(payload.get("trust"), dict) else {}
    raw_provenance = (
        raw_trust.get("provenance") if isinstance(raw_trust.get("provenance"), dict) else {}
    )
    raw_review = (
        raw_trust.get("human_review") if isinstance(raw_trust.get("human_review"), dict) else {}
    )
    raw_link = payload.get("deep_link") if isinstance(payload.get("deep_link"), dict) else {}
    raw_evidence_refs = payload.get("evidence_refs") if isinstance(payload.get("evidence_refs"), list) else []
    raw_compensation = (
        payload.get("compensation") if isinstance(payload.get("compensation"), dict) else None
    )

    return LearnerRecordEvent(
        event_id=str(payload["event_id"]),
        event_version=str(payload.get("event_version", EVENT_SCHEMA_VERSION)),
        learner_id=str(payload["learner_id"]),
        learner_key=str(payload["learner_key"]),
        event_type=str(payload["event_type"]),
        occurred_at=str(payload["occurred_at"]),
        recorded_at=str(payload.get("recorded_at", payload["occurred_at"])),
        title=str(payload["title"]),
        summary=str(payload["summary"]),
        status=str(payload["status"]),
        source=LearnerRecordSourceMetadata(
            service=str(raw_source.get("service", "")),
            capability=str(raw_source.get("capability", "")),
            entity_type=(str(raw_source["entity_type"]) if raw_source.get("entity_type") else None),
            entity_id=(str(raw_source["entity_id"]) if raw_source.get("entity_id") else None),
            institution_id=(str(raw_source["institution_id"]) if raw_source.get("institution_id") else None),
            school_id=(str(raw_source["school_id"]) if raw_source.get("school_id") else None),
        ),
        actor=LearnerRecordActor(
            role=str(raw_actor.get("role", "")),
            actor_id=(str(raw_actor["actor_id"]) if raw_actor.get("actor_id") else None),
        ),
        trust=LearnerRecordTrustMetadata(
            provenance=LearnerRecordProvenanceMetadata(
                source_type=str(raw_provenance.get("source_type", "")),
                source_ids=tuple(str(item) for item in raw_provenance.get("source_ids", [])),
                generator=str(raw_provenance.get("generator", "")),
                workflow_version=str(raw_provenance.get("workflow_version", LEARNER_RECORD_WORKFLOW_VERSION)),
                model=(str(raw_provenance["model"]) if raw_provenance.get("model") else None),
                prompt_version=(
                    str(raw_provenance["prompt_version"])
                    if raw_provenance.get("prompt_version")
                    else None
                ),
            ),
            evaluation_state=str(raw_trust.get("evaluation_state", "pending")),
            human_review=LearnerRecordReviewMetadata(
                status=str(raw_review.get("status", "recommended")),
                summary=str(raw_review.get("summary", "")),
            ),
            degraded=bool(raw_trust.get("degraded", False)),
            advisory_only=bool(raw_trust.get("advisory_only", True)),
            note=str(raw_trust.get("note", "")),
        ),
        deep_link=LearnerRecordDeepLink(
            label=str(raw_link.get("label", "")),
            href=str(raw_link.get("href", "")),
        ),
        evidence_refs=tuple(
            LearnerRecordEvidenceRef(
                evidence_id=str(raw_ref.get("evidence_id", "")),
                label=str(raw_ref.get("label", "")),
                kind=str(raw_ref.get("kind", "")),
                deep_link=(
                    LearnerRecordDeepLink(
                        label=str(raw_ref["deep_link"].get("label", "")),
                        href=str(raw_ref["deep_link"].get("href", "")),
                    )
                    if isinstance(raw_ref.get("deep_link"), dict)
                    else None
                ),
            )
            for raw_ref in raw_evidence_refs
            if isinstance(raw_ref, dict)
        ),
        idempotency_key=str(payload.get("idempotency_key", "")),
        compensation=(
            LearnerRecordCompensation(
                compensates_event_id=str(raw_compensation.get("compensates_event_id", "")),
                reason=str(raw_compensation.get("reason", "")),
            )
            if raw_compensation is not None
            else None
        ),
    )