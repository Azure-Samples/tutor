"""Persistence layer for upskilling teaching plans."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD


@dataclass
class PlanRecord:
    id: str
    professor_id: str
    title: str
    timeframe: str
    topic: str
    class_id: str
    status: str  # "draft", "evaluated", "revised", "archived"
    paragraphs: list[dict[str, str]] = field(default_factory=list)
    evaluations: list[dict] = field(default_factory=list)
    performance_history: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class UpskillingRepository(ABC):
    @abstractmethod
    async def create_plan(self, plan: PlanRecord) -> PlanRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_plans(self, professor_id: str | None = None) -> list[PlanRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_plan(self, plan_id: str) -> PlanRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def update_plan(self, plan: PlanRecord) -> PlanRecord:
        raise NotImplementedError

    @abstractmethod
    async def delete_plan(self, plan_id: str, professor_id: str) -> None:
        raise NotImplementedError


class InMemoryUpskillingRepository(UpskillingRepository):
    def __init__(self) -> None:
        self.plans: dict[str, PlanRecord] = {}

    async def create_plan(self, plan: PlanRecord) -> PlanRecord:
        self.plans[plan.id] = plan
        return plan

    async def list_plans(self, professor_id: str | None = None) -> list[PlanRecord]:
        plans = list(self.plans.values())
        if professor_id is not None:
            plans = [p for p in plans if p.professor_id == professor_id]
        return plans

    async def get_plan(self, plan_id: str) -> PlanRecord | None:
        return self.plans.get(plan_id)

    async def update_plan(self, plan: PlanRecord) -> PlanRecord:
        self.plans[plan.id] = plan
        return plan

    async def delete_plan(self, plan_id: str, professor_id: str) -> None:
        self.plans.pop(plan_id, None)


class CosmosUpskillingRepository(UpskillingRepository):
    def __init__(self, container_name: str, config: CosmosConfig) -> None:
        self._store = CosmosCRUD(container_name, config)

    async def create_plan(self, plan: PlanRecord) -> PlanRecord:
        payload = _plan_to_payload(plan)
        await self._store.create_item(payload)
        return plan

    async def list_plans(self, professor_id: str | None = None) -> list[PlanRecord]:
        if professor_id is not None:
            query = (
                "SELECT * FROM c "
                "WHERE c.docType = @docType AND c.professor_id = @professorId"
            )
            parameters = [
                {"name": "@docType", "value": "plan"},
                {"name": "@professorId", "value": professor_id},
            ]
        else:
            query = "SELECT * FROM c WHERE c.docType = @docType"
            parameters = [{"name": "@docType", "value": "plan"}]

        rows = await self._store.list_items(query=query, parameters=parameters)
        return [_row_to_plan(item) for item in rows]

    async def get_plan(self, plan_id: str) -> PlanRecord | None:
        query = (
            "SELECT * FROM c WHERE c.id = @id AND c.docType = @docType"
        )
        parameters = [
            {"name": "@id", "value": plan_id},
            {"name": "@docType", "value": "plan"},
        ]
        rows = await self._store.list_items(query=query, parameters=parameters)
        if not rows:
            return None
        return _row_to_plan(rows[0])

    async def update_plan(self, plan: PlanRecord) -> PlanRecord:
        payload = _plan_to_payload(plan)
        await self._store.create_item(payload)
        return plan

    async def delete_plan(self, plan_id: str, professor_id: str) -> None:
        await self._store.delete_item(plan_id, partition_key=professor_id)


def _plan_to_payload(plan: PlanRecord) -> dict:
    return {
        "id": plan.id,
        "docType": "plan",
        "professor_id": plan.professor_id,
        "title": plan.title,
        "timeframe": plan.timeframe,
        "topic": plan.topic,
        "class_id": plan.class_id,
        "status": plan.status,
        "paragraphs": plan.paragraphs,
        "evaluations": plan.evaluations,
        "performance_history": plan.performance_history,
        "created_at": plan.created_at,
        "updated_at": plan.updated_at,
    }


def _row_to_plan(item: dict) -> PlanRecord:
    return PlanRecord(
        id=item["id"],
        professor_id=item["professor_id"],
        title=item["title"],
        timeframe=item["timeframe"],
        topic=item["topic"],
        class_id=item["class_id"],
        status=item["status"],
        paragraphs=item.get("paragraphs", []),
        evaluations=item.get("evaluations", []),
        performance_history=item.get("performance_history", []),
        created_at=item.get("created_at", ""),
        updated_at=item.get("updated_at", ""),
    )


def plan_to_dict(record: PlanRecord) -> dict:
    return record.__dict__.copy()
