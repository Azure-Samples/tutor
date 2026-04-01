"""Persistence abstractions and repositories for insights reports and feedback."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field

from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD


@dataclass
class ReportRecord:
    report_id: str
    school_id: str
    supervisor_id: str
    week_of: str | None
    generated_at: str
    source: str
    indicators: list[dict[str, object]] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    focus_points: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    feedback_count: int = 0


@dataclass
class FeedbackRecord:
    feedback_id: str
    report_id: str
    school_id: str
    supervisor_id: str
    rating: int
    comments: str | None
    submitted_at: str


@dataclass
class PilotMetricsRecord:
    total_reports: int
    total_feedback: int
    reports_with_feedback: int
    average_rating: float | None
    feedback_rate: float
    school_count: int


class InsightsRepository(ABC):
    @abstractmethod
    async def create_report(self, report: ReportRecord) -> ReportRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_reports(self, school_ids: set[str] | None = None) -> list[ReportRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_report(self, report_id: str) -> ReportRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def create_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_feedback(self, report_id: str) -> list[FeedbackRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_pilot_metrics(self, school_ids: set[str] | None = None) -> PilotMetricsRecord:
        raise NotImplementedError


class InMemoryInsightsRepository(InsightsRepository):
    def __init__(self) -> None:
        self.reports: dict[str, ReportRecord] = {}
        self.feedback_entries: dict[str, FeedbackRecord] = {}

    async def create_report(self, report: ReportRecord) -> ReportRecord:
        self.reports[report.report_id] = report
        return report

    async def list_reports(self, school_ids: set[str] | None = None) -> list[ReportRecord]:
        rows = list(self.reports.values())
        if school_ids is not None:
            rows = [row for row in rows if row.school_id in school_ids]
        rows.sort(key=lambda row: row.generated_at, reverse=True)
        return rows

    async def get_report(self, report_id: str) -> ReportRecord | None:
        return self.reports.get(report_id)

    async def create_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        self.feedback_entries[feedback.feedback_id] = feedback
        report = self.reports.get(feedback.report_id)
        if report is not None:
            report.feedback_count += 1
        return feedback

    async def list_feedback(self, report_id: str) -> list[FeedbackRecord]:
        rows = [entry for entry in self.feedback_entries.values() if entry.report_id == report_id]
        rows.sort(key=lambda row: row.submitted_at, reverse=True)
        return rows

    async def get_pilot_metrics(self, school_ids: set[str] | None = None) -> PilotMetricsRecord:
        reports = await self.list_reports(school_ids)
        report_ids = {report.report_id for report in reports}

        feedback_rows = [entry for entry in self.feedback_entries.values() if entry.report_id in report_ids]
        ratings = [entry.rating for entry in feedback_rows]
        reports_with_feedback = len({entry.report_id for entry in feedback_rows})

        average_rating = round(sum(ratings) / len(ratings), 3) if ratings else None
        feedback_rate = round(reports_with_feedback / len(reports), 3) if reports else 0.0
        school_count = len({report.school_id for report in reports})

        return PilotMetricsRecord(
            total_reports=len(reports),
            total_feedback=len(feedback_rows),
            reports_with_feedback=reports_with_feedback,
            average_rating=average_rating,
            feedback_rate=feedback_rate,
            school_count=school_count,
        )


class CosmosInsightsRepository(InsightsRepository):
    def __init__(self, cosmos: CosmosConfig) -> None:
        self._report_store = CosmosCRUD(cosmos.insights_report_container, cosmos)
        self._feedback_store = CosmosCRUD(cosmos.insights_feedback_container, cosmos)

    async def create_report(self, report: ReportRecord) -> ReportRecord:
        await self._report_store.create_item(_report_to_payload(report))
        return report

    async def list_reports(self, school_ids: set[str] | None = None) -> list[ReportRecord]:
        if school_ids is None:
            query = "SELECT * FROM c WHERE c.docType = @docType ORDER BY c.generated_at DESC"
            parameters = [{"name": "@docType", "value": "insight_report"}]
        elif not school_ids:
            return []
        else:
            query = (
                "SELECT * FROM c "
                "WHERE c.docType = @docType AND ARRAY_CONTAINS(@schoolIds, c.school_id) "
                "ORDER BY c.generated_at DESC"
            )
            parameters = [
                {"name": "@docType", "value": "insight_report"},
                {"name": "@schoolIds", "value": sorted(school_ids)},
            ]

        rows = await self._report_store.list_items(query=query, parameters=parameters)
        return [_payload_to_report(row) for row in rows]

    async def get_report(self, report_id: str) -> ReportRecord | None:
        rows = await self._report_store.list_items(
            query="SELECT * FROM c WHERE c.id = @id AND c.docType = @docType",
            parameters=[
                {"name": "@id", "value": report_id},
                {"name": "@docType", "value": "insight_report"},
            ],
        )
        if not rows:
            return None
        return _payload_to_report(rows[0])

    async def create_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        await self._feedback_store.create_item(_feedback_to_payload(feedback))

        report = await self.get_report(feedback.report_id)
        if report is not None:
            report.feedback_count += 1
            await self._report_store.create_item(_report_to_payload(report))

        return feedback

    async def list_feedback(self, report_id: str) -> list[FeedbackRecord]:
        rows = await self._feedback_store.list_items(
            query=(
                "SELECT * FROM c "
                "WHERE c.docType = @docType AND c.report_id = @reportId "
                "ORDER BY c.submitted_at DESC"
            ),
            parameters=[
                {"name": "@docType", "value": "insight_feedback"},
                {"name": "@reportId", "value": report_id},
            ],
        )
        return [_payload_to_feedback(row) for row in rows]

    async def get_pilot_metrics(self, school_ids: set[str] | None = None) -> PilotMetricsRecord:
        reports = await self.list_reports(school_ids)
        report_ids = {report.report_id for report in reports}

        feedback_rows = await self._list_feedback(school_ids)
        feedback_rows = [entry for entry in feedback_rows if entry.report_id in report_ids]
        ratings = [entry.rating for entry in feedback_rows]
        reports_with_feedback = len({entry.report_id for entry in feedback_rows})

        average_rating = round(sum(ratings) / len(ratings), 3) if ratings else None
        feedback_rate = round(reports_with_feedback / len(reports), 3) if reports else 0.0
        school_count = len({report.school_id for report in reports})

        return PilotMetricsRecord(
            total_reports=len(reports),
            total_feedback=len(feedback_rows),
            reports_with_feedback=reports_with_feedback,
            average_rating=average_rating,
            feedback_rate=feedback_rate,
            school_count=school_count,
        )

    async def _list_feedback(self, school_ids: set[str] | None = None) -> list[FeedbackRecord]:
        if school_ids is None:
            query = "SELECT * FROM c WHERE c.docType = @docType"
            parameters = [{"name": "@docType", "value": "insight_feedback"}]
        elif not school_ids:
            return []
        else:
            query = (
                "SELECT * FROM c "
                "WHERE c.docType = @docType AND ARRAY_CONTAINS(@schoolIds, c.school_id)"
            )
            parameters = [
                {"name": "@docType", "value": "insight_feedback"},
                {"name": "@schoolIds", "value": sorted(school_ids)},
            ]

        rows = await self._feedback_store.list_items(query=query, parameters=parameters)
        return [_payload_to_feedback(row) for row in rows]


def _report_to_payload(report: ReportRecord) -> dict[str, object]:
    payload = asdict(report)
    payload["id"] = report.report_id
    payload["docType"] = "insight_report"
    return payload


def _feedback_to_payload(feedback: FeedbackRecord) -> dict[str, object]:
    payload = asdict(feedback)
    payload["id"] = feedback.feedback_id
    payload["docType"] = "insight_feedback"
    return payload


def _payload_to_report(payload: dict[str, object]) -> ReportRecord:
    return ReportRecord(
        report_id=str(payload["report_id"]),
        school_id=str(payload["school_id"]),
        supervisor_id=str(payload["supervisor_id"]),
        week_of=(str(payload["week_of"]) if payload.get("week_of") else None),
        generated_at=str(payload["generated_at"]),
        source=str(payload["source"]),
        indicators=list(payload.get("indicators", [])),
        trends=list(payload.get("trends", [])),
        alerts=list(payload.get("alerts", [])),
        focus_points=list(payload.get("focus_points", [])),
        improvements=list(payload.get("improvements", [])),
        feedback_count=int(payload.get("feedback_count", 0)),
    )


def _payload_to_feedback(payload: dict[str, object]) -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id=str(payload["feedback_id"]),
        report_id=str(payload["report_id"]),
        school_id=str(payload["school_id"]),
        supervisor_id=str(payload["supervisor_id"]),
        rating=int(payload["rating"]),
        comments=(str(payload["comments"]) if payload.get("comments") else None),
        submitted_at=str(payload["submitted_at"]),
    )


def report_to_dict(record: ReportRecord) -> dict[str, object]:
    return asdict(record)


def feedback_to_dict(record: FeedbackRecord) -> dict[str, object]:
    return asdict(record)


def pilot_metrics_to_dict(record: PilotMetricsRecord) -> dict[str, object]:
    return asdict(record)
