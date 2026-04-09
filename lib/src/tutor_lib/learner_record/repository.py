"""Learner-record event repository implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD

from .models import LearnerRecordEvent, event_to_payload, payload_to_event, sort_events


@dataclass(frozen=True, slots=True)
class LearnerRecordAppendResult:
    event: LearnerRecordEvent
    created: bool


class LearnerRecordEventRepository(Protocol):
    async def append_event_result(self, event: LearnerRecordEvent) -> LearnerRecordAppendResult:
        raise NotImplementedError

    async def append_event(self, event: LearnerRecordEvent) -> LearnerRecordEvent:
        raise NotImplementedError

    async def list_events(self, *, learner_key: str) -> list[LearnerRecordEvent]:
        raise NotImplementedError


class InMemoryLearnerRecordEventRepository:
    def __init__(self) -> None:
        self._events_by_id: dict[str, LearnerRecordEvent] = {}
        self._event_ids_by_learner: dict[str, list[str]] = {}

    async def append_event_result(self, event: LearnerRecordEvent) -> LearnerRecordAppendResult:
        existing = self._events_by_id.get(event.event_id)
        if existing is not None:
            return LearnerRecordAppendResult(event=existing, created=False)

        self._events_by_id[event.event_id] = event
        self._event_ids_by_learner.setdefault(event.learner_key, []).append(event.event_id)
        return LearnerRecordAppendResult(event=event, created=True)

    async def append_event(self, event: LearnerRecordEvent) -> LearnerRecordEvent:
        return (await self.append_event_result(event)).event

    async def list_events(self, *, learner_key: str) -> list[LearnerRecordEvent]:
        event_ids = self._event_ids_by_learner.get(learner_key, [])
        return sort_events([self._events_by_id[event_id] for event_id in event_ids])


class CosmosLearnerRecordEventRepository:
    def __init__(self, cosmos: CosmosConfig) -> None:
        self._store = CosmosCRUD(cosmos.learner_record_events_container, cosmos)

    async def append_event_result(self, event: LearnerRecordEvent) -> LearnerRecordAppendResult:
        stored = await self._store.create_item_strict(
            event_to_payload(event),
            partition_key=event.learner_key,
        )
        return LearnerRecordAppendResult(
            event=payload_to_event(stored.item),
            created=stored.created,
        )

    async def append_event(self, event: LearnerRecordEvent) -> LearnerRecordEvent:
        return (await self.append_event_result(event)).event

    async def list_events(self, *, learner_key: str) -> list[LearnerRecordEvent]:
        rows = await self._store.list_items(
            query=(
                "SELECT * FROM c "
                "WHERE c.docType = @docType AND c.learner_key = @learnerKey"
            ),
            parameters=[
                {"name": "@docType", "value": "learner_record_event"},
                {"name": "@learnerKey", "value": learner_key},
            ],
            partition_key=learner_key,
        )
        return sort_events([payload_to_event(row) for row in rows])