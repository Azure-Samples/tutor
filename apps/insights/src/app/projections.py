"""Workspace snapshot and learner-record projection builders."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from tutor_lib.learner_record import (
    LEARNER_RECORD_WORKFLOW_VERSION,
    LearnerRecordDeepLink,
    LearnerRecordEvent,
    LearnerRecordEventBuilder,
    LearnerRecordEventRepository,
    LearnerRecordEvidenceRef,
    LearnerRecordSourceMetadata,
    LearnerRecordTrustMetadata,
    build_learner_key,
    build_trust_metadata,
)
from tutor_lib.middleware.auth import AccessContext, AuthenticatedUser

from app.indicators import IndicatorStrategy
from app.orchestrator import build_briefing
from app.schemas import (
    CursorPage,
    DeepLink,
    FreshnessMetadata,
    LearnerRecordEntry,
    LearnerRecordTimelinePayload,
    ProvenanceMetadata,
    ReviewMetadata,
    SnapshotItem,
    TimelineEvidence,
    TrustMetadata,
    WorkspaceSnapshotPayload,
)
from app.store import InsightsRepository, ReportRecord

_BASE_TIME = datetime(2026, 4, 8, 12, 0, tzinfo=UTC)
_WORKFLOW_VERSION = "workspace-projection-v1"


def _seed_bytes(seed: str) -> bytes:
    return sha256(seed.encode("utf-8")).digest()


def _seed_int(seed: str, minimum: int, maximum: int, *, byte_index: int = 0) -> int:
    if minimum >= maximum:
        return minimum
    digest = _seed_bytes(seed)
    span = maximum - minimum + 1
    return minimum + (digest[byte_index % len(digest)] % span)


def _seed_ratio(seed: str, minimum: float, maximum: float, *, byte_index: int = 0) -> float:
    digest = _seed_bytes(seed)
    span = maximum - minimum
    return round(minimum + ((digest[byte_index % len(digest)] / 255.0) * span), 3)


def _seed_bool(seed: str, *, byte_index: int = 0, threshold: int = 64) -> bool:
    return _seed_bytes(seed)[byte_index % 32] < threshold


def _seed_time(seed: str, *, offset_hours: int = 0, max_hours: int = 96, byte_index: int = 0) -> datetime:
    return _BASE_TIME - timedelta(hours=offset_hours + _seed_int(seed, 0, max_hours, byte_index=byte_index))


def _parse_timestamp(raw_value: str | None) -> datetime | None:
    if not raw_value:
        return None
    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _status_for_freshness(*, generated_at: datetime, source_updated_at: datetime | None, degraded: bool) -> str:
    if degraded:
        return "degraded"
    if source_updated_at is None:
        return "derived"
    if generated_at - source_updated_at > timedelta(days=3):
        return "stale"
    return "fresh"


def _freshness_metadata(
    *,
    generated_at: datetime,
    source_updated_at: datetime | None,
    degraded: bool,
    note: str,
) -> FreshnessMetadata:
    return FreshnessMetadata(
        generated_at=generated_at.isoformat(),
        source_updated_at=source_updated_at.isoformat() if source_updated_at is not None else None,
        status=_status_for_freshness(
            generated_at=generated_at,
            source_updated_at=source_updated_at,
            degraded=degraded,
        ),
        note=note,
    )


def _trust_metadata(
    *,
    source_type: str,
    source_ids: list[str],
    generator: str,
    note: str,
    degraded: bool,
    evaluation_state: str,
    review_status: str,
    review_summary: str,
    advisory_only: bool,
    model: str | None = None,
) -> TrustMetadata:
    return TrustMetadata(
        provenance=ProvenanceMetadata(
            source_type=source_type,
            source_ids=source_ids,
            generator=generator,
            workflow_version=_WORKFLOW_VERSION,
            model=model,
        ),
        evaluation_state=evaluation_state,
        human_review=ReviewMetadata(status=review_status, summary=review_summary),
        degraded=degraded,
        advisory_only=advisory_only,
        note=note,
    )


def _item(item_id: str, tone: str, title: str, summary: str, href: str, label: str, metric: str | None = None) -> SnapshotItem:
    return SnapshotItem(
        item_id=item_id,
        tone=tone,
        title=title,
        summary=summary,
        metric=metric,
        deep_link=DeepLink(label=label, href=href),
    )


def _safe_trust(record: ReportRecord) -> TrustMetadata | None:
    if not record.trust:
        return None
    try:
        return TrustMetadata.model_validate(record.trust)
    except Exception:
        return None


def _safe_freshness(record: ReportRecord) -> FreshnessMetadata | None:
    if not record.freshness:
        return None
    try:
        return FreshnessMetadata.model_validate(record.freshness)
    except Exception:
        return None


def _timeline_trust_metadata(trust: LearnerRecordTrustMetadata) -> TrustMetadata:
    return TrustMetadata(
        provenance=ProvenanceMetadata(
            source_type=trust.provenance.source_type,
            source_ids=list(trust.provenance.source_ids),
            generator=trust.provenance.generator,
            workflow_version=trust.provenance.workflow_version,
            model=trust.provenance.model,
        ),
        evaluation_state=trust.evaluation_state,
        human_review=ReviewMetadata(
            status=trust.human_review.status,
            summary=trust.human_review.summary,
        ),
        degraded=trust.degraded,
        advisory_only=trust.advisory_only,
        note=trust.note,
    )


def _timeline_entry_from_event(event: LearnerRecordEvent) -> LearnerRecordEntry:
    return LearnerRecordEntry(
        record_id=event.event_id,
        occurred_at=event.occurred_at,
        event_type=event.event_type,
        source_service=event.source.service,
        title=event.title,
        summary=event.summary,
        status=event.status,
        actor_role=event.actor.role,
        evidence=[
            TimelineEvidence(
                evidence_id=evidence.evidence_id,
                label=evidence.label,
                kind=evidence.kind,
                deep_link=(
                    DeepLink(label=evidence.deep_link.label, href=evidence.deep_link.href)
                    if evidence.deep_link is not None
                    else None
                ),
            )
            for evidence in event.evidence_refs
        ],
        trust=_timeline_trust_metadata(event.trust),
        deep_link=DeepLink(label=event.deep_link.label, href=event.deep_link.href),
    )


class WorkspaceProjectionBuilder:
    """Build first-generation workspace and learner-record projections."""

    def __init__(
        self,
        *,
        repository: InsightsRepository,
        indicator_strategies: Sequence[IndicatorStrategy],
        learner_record_repository: LearnerRecordEventRepository,
    ) -> None:
        self._repository = repository
        self._indicator_strategies = tuple(indicator_strategies)
        self._learner_record_repository = learner_record_repository

    async def build_workspace_snapshot(
        self,
        *,
        role: str,
        context: AccessContext,
        user: AuthenticatedUser,
    ) -> WorkspaceSnapshotPayload:
        if role in {"principal", "supervisor"}:
            return await self._build_leader_snapshot(role=role, context=context)
        if role == "professor":
            return self._build_professor_snapshot(context=context)
        if role == "student":
            return self._build_student_snapshot(context=context, user=user)
        if role == "alumni":
            return self._build_alumni_snapshot(context=context)
        return self._build_admin_snapshot(context=context)

    async def build_learner_record_timeline(
        self,
        *,
        learner_id: str,
        context: AccessContext,
        limit: int,
        cursor: str | None,
    ) -> LearnerRecordTimelinePayload:
        start_index = 0
        if cursor:
            try:
                start_index = int(cursor)
            except ValueError as exc:
                raise ValueError("Cursor must be an integer offset") from exc
        if start_index < 0:
            raise ValueError("Cursor must be an integer offset")

        learner_key = build_learner_key(
            learner_id=learner_id,
            institution_id=self._context_institution_id(context),
        )
        events = await self._load_learner_record_events(
            learner_id=learner_id,
            learner_key=learner_key,
        )
        entries = [_timeline_entry_from_event(event) for event in events]

        page_entries = entries[start_index : start_index + limit]
        next_index = start_index + limit
        next_cursor = str(next_index) if next_index < len(entries) else None
        latest_event = _parse_timestamp(entries[0].occurred_at) if entries else None
        generated_at = _parse_timestamp(events[0].recorded_at) if events else _BASE_TIME

        return LearnerRecordTimelinePayload(
            learner_id=learner_id,
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"Learner record timeline contains {len(entries)} recent entries for {learner_id} "
                f"within {context.label}."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at or _BASE_TIME,
                source_updated_at=latest_event,
                degraded=any(entry.status == "degraded" for entry in page_entries),
                note="Learner-record entries are projected from durable append-only learner-record events.",
            ),
            page=CursorPage(
                limit=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=next_cursor is not None,
            ),
            entries=page_entries,
            deep_links=[
                DeepLink(label="Open writing workspace", href="/essays"),
                DeepLink(label="Open guided practice", href="/questions"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
            ],
        )

    async def _build_leader_snapshot(self, *, role: str, context: AccessContext) -> WorkspaceSnapshotPayload:
        school_ids = set(context.scope.school_ids)
        report = await self._latest_report(school_ids)
        if report is not None:
            return self._snapshot_from_report(role=role, context=context, report=report)

        school_id = next(iter(sorted(school_ids)), context.context_id)
        briefing = await build_briefing(school_id, list(self._indicator_strategies), week_of="2026-W14")
        generated_at = _seed_time(f"{role}:{context.context_id}:generated", max_hours=18)
        trust = _trust_metadata(
            source_type="insight_projection",
            source_ids=[f"school:{school_id}", f"context:{context.context_id}"],
            generator="insights.workspace-snapshot",
            note="No stored briefing report was available, so the snapshot was derived from deterministic indicator strategies.",
            degraded=False,
            evaluation_state="pending",
            review_status="recommended",
            review_summary="Narrative summaries should be reviewed alongside the deterministic school indicators.",
            advisory_only=True,
            model=None,
        )
        deterministic_highlights = [
            _item(
                item_id=f"indicator:{snapshot.indicator}",
                tone="deterministic",
                title=_title_from_indicator(snapshot.indicator),
                summary=snapshot.summary,
                metric=f"{snapshot.score:.0%}",
                href="/configuration/supervisor",
                label="Open school briefings",
            )
            for snapshot in briefing.indicators[:2]
        ]
        advisory_items = [
            _item(
                item_id=f"focus:{index}",
                tone="advisory",
                title="Priority follow-up",
                summary=focus_point,
                href="/configuration/supervisor",
                label="Review briefing details",
            )
            for index, focus_point in enumerate(briefing.focus_points[:2], start=1)
        ]
        attention_items = [
            _item(
                item_id=f"alert:{index}",
                tone="attention",
                title="Alert requiring supervisor attention",
                summary=alert,
                href="/configuration/supervisor",
                label="Open school briefings",
            )
            for index, alert in enumerate(briefing.alerts[:2], start=1)
        ]

        return WorkspaceSnapshotPayload(
            role=role,
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"{context.label} currently shows {len(briefing.alerts)} active alerts and "
                f"{len(briefing.focus_points)} advisory follow-up items."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at,
                source_updated_at=generated_at,
                degraded=False,
                note="Deterministic seeded projection assembled for Wave 1 because no stored briefing exists yet.",
            ),
            trust=trust,
            deterministic_highlights=deterministic_highlights,
            advisory_items=advisory_items,
            attention_items=attention_items,
            deep_links=[
                DeepLink(label="Open school briefings", href="/configuration/supervisor"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
            ],
        )

    def _snapshot_from_report(self, *, role: str, context: AccessContext, report: ReportRecord) -> WorkspaceSnapshotPayload:
        generated_at = _parse_timestamp(report.generated_at) or _BASE_TIME
        trust = _safe_trust(report) or _trust_metadata(
            source_type="insight_report",
            source_ids=[report.report_id, f"school:{report.school_id}"],
            generator="insights.report-store",
            note="Stored briefing report reused for the workspace snapshot.",
            degraded=False,
            evaluation_state="evaluated",
            review_status="recommended",
            review_summary="Narrative briefings should stay paired with the underlying school indicators.",
            advisory_only=True,
            model="gpt-4o",
        )
        freshness = _safe_freshness(report) or _freshness_metadata(
            generated_at=generated_at,
            source_updated_at=generated_at,
            degraded=trust.degraded,
            note="Stored briefing report reused for this workspace snapshot.",
        )
        deterministic_highlights = [
            _item(
                item_id=f"report-indicator:{index}",
                tone="deterministic",
                title=_title_from_indicator(str(indicator.get("indicator", f"Indicator {index}"))),
                summary=str(indicator.get("summary", "Indicator detail is available in the stored report.")),
                metric=(
                    f"{float(indicator.get('score', 0.0)):.0%}"
                    if isinstance(indicator.get("score"), (int, float))
                    else None
                ),
                href="/configuration/supervisor",
                label="Open school briefings",
            )
            for index, indicator in enumerate(report.indicators[:2], start=1)
        ]
        advisory_items = [
            _item(
                item_id=f"focus:{index}",
                tone="advisory",
                title="Recommended focus point",
                summary=focus_point,
                href="/configuration/supervisor",
                label="Review briefing details",
            )
            for index, focus_point in enumerate(report.focus_points[:2], start=1)
        ] + [
            _item(
                item_id=f"improvement:{index}",
                tone="advisory",
                title="Positive practice to scale",
                summary=improvement,
                href="/configuration/supervisor",
                label="Review briefing details",
            )
            for index, improvement in enumerate(report.improvements[:1], start=1)
        ]
        attention_items = [
            _item(
                item_id=f"alert:{index}",
                tone="attention",
                title="Alert requiring attention",
                summary=alert,
                href="/configuration/supervisor",
                label="Open school briefings",
            )
            for index, alert in enumerate(report.alerts[:2], start=1)
        ]

        return WorkspaceSnapshotPayload(
            role=role,
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"Stored briefing for {report.school_id} includes {len(report.alerts)} alerts and "
                f"{len(report.focus_points)} focus areas for follow-up."
            ),
            freshness=freshness,
            trust=trust,
            deterministic_highlights=deterministic_highlights,
            advisory_items=advisory_items,
            attention_items=attention_items,
            deep_links=[
                DeepLink(label="Open school briefings", href="/configuration/supervisor"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
            ],
        )

    async def _latest_report(self, school_ids: set[str]) -> ReportRecord | None:
        if not school_ids:
            return None
        reports = await self._repository.list_reports(school_ids)
        return reports[0] if reports else None

    @staticmethod
    def _context_institution_id(context: AccessContext) -> str | None:
        institution_ids = tuple(context.scope.institution_ids)
        return institution_ids[0] if institution_ids else None

    async def _load_learner_record_events(
        self,
        *,
        learner_id: str,
        learner_key: str,
    ) -> list[LearnerRecordEvent]:
        events = await self._learner_record_repository.list_events(learner_key=learner_key)
        if events:
            return events

        await self._seed_wave_one_learner_events(learner_id=learner_id, learner_key=learner_key)
        return await self._learner_record_repository.list_events(learner_key=learner_key)

    def _build_professor_snapshot(self, *, context: AccessContext) -> WorkspaceSnapshotPayload:
        seed = f"professor:{context.context_id}"
        queue_count = _seed_int(f"{seed}:queue", 12, 28)
        at_risk_count = _seed_int(f"{seed}:risk", 2, 7)
        plan_count = _seed_int(f"{seed}:plans", 1, 4)
        degraded = _seed_bool(f"{seed}:degraded", threshold=40)
        generated_at = _seed_time(f"{seed}:generated", max_hours=12)

        return WorkspaceSnapshotPayload(
            role="professor",
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"{context.label} has {queue_count} review items, {at_risk_count} learners needing "
                f"follow-up, and {plan_count} teaching-plan drafts awaiting confirmation."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at,
                source_updated_at=generated_at,
                degraded=degraded,
                note="Wave 1 faculty projection assembled from deterministic seeded review and cohort signals.",
            ),
            trust=_trust_metadata(
                source_type="faculty_projection",
                source_ids=[context.context_id],
                generator="insights.workspace-snapshot",
                note="Faculty summaries combine deterministic queue signals with advisory recommendations that require human judgment.",
                degraded=degraded,
                evaluation_state="pending",
                review_status="required",
                review_summary="Any grading or intervention recommendation remains a draft until a professor confirms it.",
                advisory_only=True,
                model="gpt-4o-mini",
            ),
            deterministic_highlights=[
                _item(
                    item_id="review-queue",
                    tone="deterministic",
                    title="Review queue waiting for faculty action",
                    summary="Essay and question work is grouped into one faculty queue instead of scattered product entry points.",
                    metric=f"{queue_count} items",
                    href="/essays",
                    label="Open review queue",
                ),
                _item(
                    item_id="cohort-watch",
                    tone="deterministic",
                    title="Cohort progress requires targeted follow-up",
                    summary="Deterministic participation and completion signals are elevated before any narrative interpretation.",
                    metric=f"{at_risk_count} learners",
                    href="/questions",
                    label="Review question work",
                ),
            ],
            advisory_items=[
                _item(
                    item_id="teaching-plan",
                    tone="advisory",
                    title="Refresh the next teaching-plan sequence",
                    summary="Tutor recommends a short plan review before publishing the next cohort milestone.",
                    metric=f"{plan_count} drafts",
                    href="/upskilling",
                    label="Open teaching plans",
                ),
                _item(
                    item_id="content-guardrails",
                    tone="advisory",
                    title="Reconfirm rubric and guardrail settings",
                    summary="This is advisory only and intended to keep grounded content aligned with the active section.",
                    href="/configuration",
                    label="Open configuration",
                ),
            ],
            attention_items=(
                [
                    _item(
                        item_id="degraded-evaluation",
                        tone="attention",
                        title="One evaluation path is degraded",
                        summary="Tutor marks degraded scoring paths so faculty can route them to validation instead of treating them as final.",
                        href="/evaluation",
                        label="Open AI governance",
                    )
                ]
                if degraded
                else []
            ),
            deep_links=[
                DeepLink(label="Open review queue", href="/essays"),
                DeepLink(label="Open teaching plans", href="/upskilling"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
            ],
        )

    def _build_student_snapshot(self, *, context: AccessContext, user: AuthenticatedUser) -> WorkspaceSnapshotPayload:
        seed = f"student:{context.context_id}:{user.subject}"
        due_count = _seed_int(f"{seed}:due", 2, 5)
        evidence_count = _seed_int(f"{seed}:evidence", 3, 8)
        progress = _seed_ratio(f"{seed}:progress", 0.58, 0.91)
        degraded = _seed_bool(f"{seed}:degraded", threshold=52)
        generated_at = _seed_time(f"{seed}:generated", max_hours=10)

        return WorkspaceSnapshotPayload(
            role="student",
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"{context.label} shows {due_count} current work items, {evidence_count} recent record updates, "
                f"and {progress:.0%} pathway progress."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at,
                source_updated_at=generated_at,
                degraded=degraded,
                note="Wave 1 learner projection assembled from deterministic seeded assignment and record signals.",
            ),
            trust=_trust_metadata(
                source_type="learner_projection",
                source_ids=[context.context_id, user.subject],
                generator="insights.workspace-snapshot",
                note="Learner-facing recommendations stay advisory and do not update progression or credential state on their own.",
                degraded=degraded,
                evaluation_state="pending",
                review_status="recommended",
                review_summary="Assessment and coaching suggestions should be read alongside the underlying evidence and deadlines.",
                advisory_only=True,
                model="gpt-4o-mini",
            ),
            deterministic_highlights=[
                _item(
                    item_id="essay-revision",
                    tone="deterministic",
                    title="Essay revision remains the highest-priority work item",
                    summary="Writing work stays linked to feedback and evidence instead of disappearing behind a tool launcher.",
                    metric=f"{due_count} due",
                    href="/essays",
                    label="Open essays",
                ),
                _item(
                    item_id="record-updates",
                    tone="deterministic",
                    title="Recent evidence was appended to the learner record",
                    summary="Tutor keeps learner-visible evidence updates explicit so progress remains inspectable.",
                    metric=f"{evidence_count} updates",
                    href="/questions",
                    label="Open practice work",
                ),
            ],
            advisory_items=[
                _item(
                    item_id="coach-session",
                    tone="advisory",
                    title="Book a short guided coaching session",
                    summary="Tutor suggests a rehearsal session before the next milestone, but leaves the choice to the learner.",
                    href="/avatar",
                    label="Open guided learning",
                ),
                _item(
                    item_id="prompt-support",
                    tone="advisory",
                    title="Use guided chat to plan the next revision",
                    summary="The suggestion is grounded in recent feedback patterns and stays clearly advisory.",
                    href="/chat",
                    label="Open guided chat",
                ),
            ],
            attention_items=(
                [
                    _item(
                        item_id="degraded-feedback",
                        tone="attention",
                        title="One feedback path is degraded and queued for review",
                        summary="Tutor suppresses authoritative language when a fallback path or delayed source affects the projection.",
                        href="/evidence-trust",
                        label="Review evidence and trust",
                    )
                ]
                if degraded
                else []
            ),
            deep_links=[
                DeepLink(label="Open essays", href="/essays"),
                DeepLink(label="Open guided learning", href="/avatar"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
            ],
        )

    def _build_admin_snapshot(self, *, context: AccessContext) -> WorkspaceSnapshotPayload:
        seed = f"admin:{context.context_id}"
        policy_count = _seed_int(f"{seed}:policies", 2, 5)
        sync_health = _seed_ratio(f"{seed}:health", 0.88, 0.97)
        degraded_count = _seed_int(f"{seed}:degraded", 1, 3)
        generated_at = _seed_time(f"{seed}:generated", max_hours=8)

        return WorkspaceSnapshotPayload(
            role="admin",
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"{context.label} currently has {policy_count} governance reviews pending, sync health at "
                f"{sync_health:.0%}, and {degraded_count} degraded incidents requiring operational attention."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at,
                source_updated_at=generated_at,
                degraded=False,
                note="Wave 1 admin projection is a deterministic operational summary over current configuration, gateway, and evaluation surfaces.",
            ),
            trust=_trust_metadata(
                source_type="admin_projection",
                source_ids=[context.context_id],
                generator="insights.workspace-snapshot",
                note="Admin summaries treat evaluation coverage, degraded paths, and policy state as visible operational concerns.",
                degraded=False,
                evaluation_state="not_required",
                review_status="not_required",
                review_summary="This workspace surfaces operational state rather than high-impact educational decisions.",
                advisory_only=False,
            ),
            deterministic_highlights=[
                _item(
                    item_id="integration-health",
                    tone="deterministic",
                    title="Gateway and sync posture remain visible",
                    summary="Operational health stays in the shell so admins do not have to hunt through service-specific entry points.",
                    metric=f"{sync_health:.0%}",
                    href="/lms-gateway",
                    label="Open integrations",
                ),
                _item(
                    item_id="policy-review",
                    tone="deterministic",
                    title="Governance review workload is pending",
                    summary="Configuration and policy surfaces remain reachable while the surrounding shell becomes role-aware.",
                    metric=f"{policy_count} pending",
                    href="/configuration/questions",
                    label="Open policies",
                ),
            ],
            advisory_items=[
                _item(
                    item_id="evaluation-readiness",
                    tone="advisory",
                    title="Reconfirm evaluation readiness before widening access",
                    summary="This is a prioritization suggestion only; Tutor does not perform release decisions automatically.",
                    href="/evaluation",
                    label="Open AI governance",
                )
            ],
            attention_items=[
                _item(
                    item_id="degraded-incidents",
                    tone="attention",
                    title="Degraded AI paths need operational review",
                    summary="Degraded incidents remain visible in the admin shell instead of being hidden in logs or service internals.",
                    metric=f"{degraded_count} incidents",
                    href="/evaluation",
                    label="Open AI governance",
                )
            ],
            deep_links=[
                DeepLink(label="Open integrations", href="/lms-gateway"),
                DeepLink(label="Open AI governance", href="/evaluation"),
                DeepLink(label="Open configuration", href="/configuration"),
            ],
        )

    def _build_alumni_snapshot(self, *, context: AccessContext) -> WorkspaceSnapshotPayload:
        seed = f"alumni:{context.context_id}"
        evidence_count = _seed_int(f"{seed}:evidence", 8, 16)
        pathway_count = _seed_int(f"{seed}:pathways", 2, 4)
        mentor_count = _seed_int(f"{seed}:mentors", 1, 3)
        degraded = _seed_bool(f"{seed}:degraded", threshold=28)
        generated_at = _seed_time(f"{seed}:generated", max_hours=14)

        return WorkspaceSnapshotPayload(
            role="alumni",
            context_id=context.context_id,
            context_label=context.label,
            summary=(
                f"{context.label} keeps {evidence_count} credential-ready record entries visible, with {pathway_count} curated re-entry options "
                f"and {mentor_count} mentoring cues."
            ),
            freshness=_freshness_metadata(
                generated_at=generated_at,
                source_updated_at=generated_at,
                degraded=degraded,
                note="Wave 1 alumni projection demonstrates durable record continuity and curated re-entry positioning.",
            ),
            trust=_trust_metadata(
                source_type="alumni_projection",
                source_ids=[context.context_id],
                generator="insights.workspace-snapshot",
                note="Tutor treats the learner record and credential evidence as durable assets that outlast a single term or cohort.",
                degraded=degraded,
                evaluation_state="pending",
                review_status="recommended",
                review_summary="Portfolio and re-entry suggestions remain advisory until later credential and pathway services are in place.",
                advisory_only=True,
                model="gpt-4o-mini",
            ),
            deterministic_highlights=[
                _item(
                    item_id="durable-record",
                    tone="deterministic",
                    title="Credential-ready evidence remains visible",
                    summary="The alumni view keeps record continuity explicit instead of resetting the learner relationship after graduation.",
                    metric=f"{evidence_count} entries",
                    href="/programs",
                    label="Explore curated programs",
                )
            ],
            advisory_items=[
                _item(
                    item_id="reentry-pathways",
                    tone="advisory",
                    title="Curated re-entry pathways are available",
                    summary="The public programs surface remains intentionally narrow and curated rather than acting like a full marketplace.",
                    metric=f"{pathway_count} options",
                    href="/programs",
                    label="Explore curated programs",
                ),
                _item(
                    item_id="mentoring-cues",
                    tone="advisory",
                    title="Mentoring remains a guided future-wave surface",
                    summary="Tutor can signal likely mentoring opportunities without pretending the community domain is already complete.",
                    metric=f"{mentor_count} cues",
                    href="/institutions",
                    label="See institution view",
                ),
            ],
            attention_items=(
                [
                    _item(
                        item_id="portfolio-advisory",
                        tone="attention",
                        title="Portfolio narrative help is still advisory",
                        summary="Generated wording support does not replace the underlying evidence or credential state.",
                        href="/evidence-trust",
                        label="Review evidence and trust",
                    )
                ]
                if degraded
                else []
            ),
            deep_links=[
                DeepLink(label="Explore curated programs", href="/programs"),
                DeepLink(label="Review evidence and trust", href="/evidence-trust"),
                DeepLink(label="See institution view", href="/institutions"),
            ],
        )

    async def _seed_wave_one_learner_events(self, *, learner_id: str, learner_key: str) -> None:
        templates = [
            {
                "event_type": "essay_feedback",
                "source_service": "essays-svc",
                "title": "Rubric-backed essay feedback appended",
                "summary": "Essay evidence, feedback, and rubric alignment were appended to the learner record.",
                "status": "needs_review",
                "actor_role": "professor",
                "href": "/essays",
                "evaluation_state": "evaluated",
                "review_status": "required",
                "review_summary": "Essay feedback is high-impact and remains human-reviewable.",
                "advisory_only": False,
            },
            {
                "event_type": "practice_set_completed",
                "source_service": "questions-svc",
                "title": "Practice set completed",
                "summary": "Question-set completion and formative signals were preserved for the active pathway.",
                "status": "confirmed",
                "actor_role": "student",
                "href": "/questions",
                "evaluation_state": "evaluated",
                "review_status": "not_required",
                "review_summary": "Formative completion signals are captured directly from the learner workflow.",
                "advisory_only": False,
            },
            {
                "event_type": "coach_session",
                "source_service": "avatar-svc",
                "title": "Guided coaching session summarized",
                "summary": "A coaching transcript summary was attached for later learner and faculty review.",
                "status": "advisory",
                "actor_role": "coach",
                "href": "/avatar",
                "evaluation_state": "pending",
                "review_status": "recommended",
                "review_summary": "Coaching summaries remain advisory until a human chooses to act on them.",
                "advisory_only": True,
            },
            {
                "event_type": "revision_plan",
                "source_service": "chat-svc",
                "title": "Revision plan suggested",
                "summary": "Tutor generated a revision plan linked to recent essay evidence and deadlines.",
                "status": "advisory",
                "actor_role": "student",
                "href": "/chat",
                "evaluation_state": "pending",
                "review_status": "recommended",
                "review_summary": "Revision suggestions guide the learner without altering deadlines or scoring state.",
                "advisory_only": True,
            },
            {
                "event_type": "teaching_plan_note",
                "source_service": "upskilling-svc",
                "title": "Intervention note captured",
                "summary": "A faculty intervention note was appended to explain the next support step for this learner cluster.",
                "status": "confirmed",
                "actor_role": "professor",
                "href": "/upskilling",
                "evaluation_state": "not_required",
                "review_status": "completed",
                "review_summary": "This note reflects a confirmed faculty-owned action.",
                "advisory_only": False,
            },
            {
                "event_type": "credential_checkpoint",
                "source_service": "configuration-svc",
                "title": "Credential checkpoint recalculated",
                "summary": "Tutor refreshed credential-readiness posture using current deterministic evidence links.",
                "status": "confirmed",
                "actor_role": "system",
                "href": "/programs",
                "evaluation_state": "not_required",
                "review_status": "not_required",
                "review_summary": "Credential posture remains derived from deterministic record state.",
                "advisory_only": False,
            },
        ]

        for index, template in enumerate(templates):
            seed = f"{learner_id}:{template['event_type']}:{index}"
            degraded = template["status"] == "advisory" and _seed_bool(f"{seed}:degraded", threshold=36)
            status = "degraded" if degraded else str(template["status"])
            occurred_at = _seed_time(seed, offset_hours=index * 18, max_hours=6, byte_index=index)
            event_builder = LearnerRecordEventBuilder(
                learner_id=learner_id,
                learner_key=learner_key,
                event_type=str(template["event_type"]),
                source=LearnerRecordSourceMetadata(
                    service=str(template["source_service"]),
                    capability="wave1-backfill",
                    entity_type="pilot_event",
                    entity_id=f"{template['event_type']}:{learner_id}:{index + 1}",
                ),
            )
            event = (
                event_builder
                .occurred_at(occurred_at)
                .recorded_at(occurred_at + timedelta(minutes=5))
                .title(str(template["title"]))
                .summary(str(template["summary"]))
                .status(status)
                .actor(role=str(template["actor_role"]))
                .deep_link(label="Open related surface", href=str(template["href"]))
                .add_evidence(
                    LearnerRecordEvidenceRef(
                        evidence_id=f"evidence:{learner_id}:{index + 1}",
                        label="Open related workspace surface",
                        kind="projection-link",
                        deep_link=LearnerRecordDeepLink(
                            label="Open related surface",
                            href=str(template["href"]),
                        ),
                    )
                )
                .trust(
                    build_trust_metadata(
                        source_type="pilot_backfill",
                        source_ids=[
                            f"pilot:{template['event_type']}:{index + 1}",
                            f"learner:{learner_id}",
                        ],
                        generator="insights.wave1-backfill",
                        workflow_version=LEARNER_RECORD_WORKFLOW_VERSION,
                        note=(
                            "A degraded path was detected for this entry, so Tutor downgrades the authority of the advisory layer."
                            if degraded
                            else "This record entry preserves source lineage and review state for the learner timeline."
                        ),
                        degraded=degraded,
                        evaluation_state=str(template["evaluation_state"]),
                        review_status=str(template["review_status"]),
                        review_summary=str(template["review_summary"]),
                        advisory_only=bool(template["advisory_only"]),
                        model="gpt-4o-mini" if bool(template["advisory_only"]) else None,
                    )
                )
                .build()
            )
            await self._learner_record_repository.append_event(event)


def _title_from_indicator(raw_indicator: str) -> str:
    return " ".join(part.capitalize() for part in raw_indicator.replace("_", " ").split())