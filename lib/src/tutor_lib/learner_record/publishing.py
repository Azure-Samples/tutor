"""Learner-record integration publishers and repository decorator."""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, Protocol

from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from .models import LearnerRecordEvent, event_to_payload
from .repository import LearnerRecordAppendResult, LearnerRecordEventRepository

logger = logging.getLogger(__name__)


class LearnerRecordEventPublisher(Protocol):
    async def publish(self, event: LearnerRecordEvent) -> None:
        raise NotImplementedError


class NoOpLearnerRecordEventPublisher:
    async def publish(self, event: LearnerRecordEvent) -> None:
        del event


class InMemoryLearnerRecordEventPublisher:
    def __init__(self) -> None:
        self._published_events: list[LearnerRecordEvent] = []

    @property
    def published_events(self) -> tuple[LearnerRecordEvent, ...]:
        return tuple(self._published_events)

    async def publish(self, event: LearnerRecordEvent) -> None:
        self._published_events.append(event)


class AzureServiceBusLearnerRecordEventPublisher:
    def __init__(
        self,
        *,
        fully_qualified_namespace: str,
        topic_name: str,
        credential_factory: Callable[[], AsyncTokenCredential] | None = None,
    ) -> None:
        self._fully_qualified_namespace = fully_qualified_namespace.strip()
        self._topic_name = topic_name.strip()
        self._credential_factory = credential_factory or AsyncDefaultAzureCredential

    @asynccontextmanager
    async def _credential(self) -> AsyncIterator[AsyncTokenCredential]:
        credential = self._credential_factory()
        has_async_cm = all(
            callable(getattr(credential, attr, None)) for attr in ("__aenter__", "__aexit__")
        )
        if has_async_cm:
            token = await credential.__aenter__()
            try:
                yield token
            finally:
                await credential.__aexit__(None, None, None)
        else:
            try:
                yield credential
            finally:
                close_method = getattr(credential, "close", None)
                if callable(close_method):
                    result = close_method()
                    if inspect.isawaitable(result):
                        await result

    @staticmethod
    def _message(event: LearnerRecordEvent) -> Any:
        from azure.servicebus import ServiceBusMessage

        payload = json.dumps(event_to_payload(event), sort_keys=True, separators=(",", ":"))
        return ServiceBusMessage(
            payload,
            content_type="application/json",
            subject=event.event_type,
            message_id=event.event_id,
            correlation_id=event.event_id,
            application_properties={
                "learner_id": event.learner_id,
                "learner_key": event.learner_key,
                "event_type": event.event_type,
                "source_service": event.source.service,
                "status": event.status,
                "event_version": event.event_version,
            },
        )

    async def publish(self, event: LearnerRecordEvent) -> None:
        from azure.servicebus.aio import ServiceBusClient

        async with self._credential() as credential:
            async with ServiceBusClient(
                fully_qualified_namespace=self._fully_qualified_namespace,
                credential=credential,
                logging_enable=False,
            ) as client:
                sender = client.get_topic_sender(topic_name=self._topic_name)
                async with sender:
                    await sender.send_messages(self._message(event))


class PublishingLearnerRecordEventRepository:
    """Decorator that publishes newly appended learner-record events."""

    def __init__(
        self,
        *,
        repository: LearnerRecordEventRepository,
        publisher: LearnerRecordEventPublisher,
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    async def append_event_result(self, event: LearnerRecordEvent) -> LearnerRecordAppendResult:
        result = await self._repository.append_event_result(event)
        if result.created:
            try:
                await self._publisher.publish(result.event)
            except Exception:
                logger.exception(
                    "Learner-record event was stored but broker publication failed for event %s",
                    result.event.event_id,
                )
        return result

    async def append_event(self, event: LearnerRecordEvent) -> LearnerRecordEvent:
        return (await self.append_event_result(event)).event

    async def list_events(self, *, learner_key: str) -> list[LearnerRecordEvent]:
        return await self._repository.list_events(learner_key=learner_key)