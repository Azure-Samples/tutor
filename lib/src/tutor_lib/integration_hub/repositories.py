"""Integration Hub repository implementations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from azure.cosmos import exceptions as cosmos_exceptions

from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD

from .contracts import ConnectorState, DeadLetterEntry


@dataclass(frozen=True, slots=True)
class IdempotencyCheckResult:
    """Result of idempotency check."""

    idempotency_key: str
    already_processed: bool
    first_processed_at: str | None = None


def _tenant_id_from_connector_id(connector_id: str) -> str | None:
    _, separator, tenant_id = connector_id.rpartition(":")
    if not separator or not tenant_id:
        return None
    return tenant_id


def _tenant_id_from_idempotency_key(idempotency_key: str) -> str:
    tenant_id, separator, _ = idempotency_key.partition("|")
    if not separator or not tenant_id:
        raise ValueError("Idempotency key must start with a tenant_id segment")
    return tenant_id


def _idempotency_document_id(idempotency_key: str) -> str:
    digest = sha256(idempotency_key.encode("utf-8")).hexdigest()
    return f"idempotency:{digest}"


def _idempotency_payload_fields(idempotency_key: str) -> dict[str, str]:
    parts = idempotency_key.split("|")
    tenant_id = _tenant_id_from_idempotency_key(idempotency_key)
    fields = {"tenant_id": tenant_id}
    if len(parts) >= 4:
        fields.update(
            {
                "provider": parts[1],
                "provider_instance_id": parts[2],
                "source_event_id": parts[3],
            }
        )
    if len(parts) >= 5 and parts[4]:
        fields["event_version"] = parts[4]
    return fields


class IdempotencyRepository(Protocol):
    """Repository for tracking processed external events."""

    async def get_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        """Check if event was already processed without recording it."""
        raise NotImplementedError

    async def record_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        """Record a successfully processed event."""
        raise NotImplementedError

    async def check_and_record(self, idempotency_key: str) -> IdempotencyCheckResult:
        """Check if event was already processed; record if new."""
        raise NotImplementedError


class InMemoryIdempotencyRepository:
    """In-memory idempotency tracking."""

    def __init__(self) -> None:
        self._processed: dict[str, str] = {}

    async def get_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        first_seen = self._processed.get(idempotency_key)
        if first_seen is not None:
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                already_processed=True,
                first_processed_at=first_seen,
            )
        return IdempotencyCheckResult(
            idempotency_key=idempotency_key,
            already_processed=False,
        )

    async def record_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        existing = await self.get_processed(idempotency_key)
        if existing.already_processed:
            return existing
        now = datetime.now(UTC).isoformat()
        self._processed[idempotency_key] = now
        return IdempotencyCheckResult(
            idempotency_key=idempotency_key,
            already_processed=False,
            first_processed_at=now,
        )

    async def check_and_record(self, idempotency_key: str) -> IdempotencyCheckResult:
        existing = await self.get_processed(idempotency_key)
        if existing.already_processed:
            return existing
        return await self.record_processed(idempotency_key)


class CosmosIdempotencyRepository:
    """Cosmos-backed idempotency tracking."""

    def __init__(self, cosmos: CosmosConfig) -> None:
        self._store = CosmosCRUD(cosmos.integration_idempotency_container, cosmos)

    async def get_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        doc_id = _idempotency_document_id(idempotency_key)
        tenant_id = _tenant_id_from_idempotency_key(idempotency_key)

        try:
            payload = await self._store.read_item(doc_id, partition_key=tenant_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                already_processed=False,
            )

        if payload.get("docType") != "idempotency_record":
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                already_processed=False,
            )

        return IdempotencyCheckResult(
            idempotency_key=idempotency_key,
            already_processed=True,
            first_processed_at=payload.get("processed_at"),
        )

    async def record_processed(self, idempotency_key: str) -> IdempotencyCheckResult:
        doc_id = _idempotency_document_id(idempotency_key)
        idempotency_fields = _idempotency_payload_fields(idempotency_key)
        tenant_id = idempotency_fields["tenant_id"]
        now = datetime.now(UTC).isoformat()

        payload = {
            "id": doc_id,
            "docType": "idempotency_record",
            **idempotency_fields,
            "idempotency_key": idempotency_key,
            "processed_at": now,
        }

        result = await self._store.create_item_strict(payload, partition_key=tenant_id)

        if result.created:
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                already_processed=False,
                first_processed_at=now,
            )
        else:
            return IdempotencyCheckResult(
                idempotency_key=idempotency_key,
                already_processed=True,
                first_processed_at=result.item.get("processed_at"),
            )

    async def check_and_record(self, idempotency_key: str) -> IdempotencyCheckResult:
        existing = await self.get_processed(idempotency_key)
        if existing.already_processed:
            return existing
        return await self.record_processed(idempotency_key)


class ConnectorStateRepository(Protocol):
    """Repository for connector registration and sync state."""

    async def save_connector(self, state: ConnectorState) -> ConnectorState:
        raise NotImplementedError

    async def get_connector(self, connector_id: str, *, tenant_id: str | None = None) -> ConnectorState | None:
        raise NotImplementedError

    async def list_connectors(self, tenant_id: str) -> list[ConnectorState]:
        raise NotImplementedError


class InMemoryConnectorStateRepository:
    """In-memory connector state storage."""

    def __init__(self) -> None:
        self._connectors: dict[str, ConnectorState] = {}

    async def save_connector(self, state: ConnectorState) -> ConnectorState:
        self._connectors[state.connector_id] = state
        return state

    async def get_connector(self, connector_id: str, *, tenant_id: str | None = None) -> ConnectorState | None:
        del tenant_id
        return self._connectors.get(connector_id)

    async def list_connectors(self, tenant_id: str) -> list[ConnectorState]:
        return [c for c in self._connectors.values() if c.tenant_id == tenant_id]


class CosmosConnectorStateRepository:
    """Cosmos-backed connector state."""

    def __init__(self, cosmos: CosmosConfig) -> None:
        self._store = CosmosCRUD(cosmos.integration_connectors_container, cosmos)

    async def save_connector(self, state: ConnectorState) -> ConnectorState:
        payload = {
            "id": state.connector_id,
            "docType": "connector_state",
            **asdict(state),
        }
        try:
            await self._store.read_item(state.connector_id, partition_key=state.tenant_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            result = (
                await self._store.create_item_strict(
                    payload,
                    partition_key=state.tenant_id,
                )
            ).item
        else:
            result = await self._store.update_item(
                state.connector_id,
                payload,
                partition_key=state.tenant_id,
            )
        return self._payload_to_state(result)

    async def get_connector(self, connector_id: str, *, tenant_id: str | None = None) -> ConnectorState | None:
        partition_key = tenant_id or _tenant_id_from_connector_id(connector_id)
        if partition_key is None:
            return None

        try:
            payload = await self._store.read_item(connector_id, partition_key=partition_key)
            if payload.get("docType") != "connector_state":
                return None
            return self._payload_to_state(payload)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None

    async def list_connectors(self, tenant_id: str) -> list[ConnectorState]:
        rows = await self._store.list_items(
            query="SELECT * FROM c WHERE c.docType = @docType AND c.tenant_id = @tenantId",
            parameters=[
                {"name": "@docType", "value": "connector_state"},
                {"name": "@tenantId", "value": tenant_id},
            ],
            partition_key=tenant_id,
        )
        return [self._payload_to_state(row) for row in rows]

    @staticmethod
    def _payload_to_state(payload: dict) -> ConnectorState:
        return ConnectorState(
            tenant_id=payload["tenant_id"],
            provider=payload["provider"],
            provider_instance_id=payload["provider_instance_id"],
            connector_id=payload["connector_id"],
            status=payload["status"],
            last_sync_at=payload.get("last_sync_at"),
            last_sync_cursor=payload.get("last_sync_cursor"),
            error_message=payload.get("error_message"),
            registered_at=payload["registered_at"],
            config=payload.get("config"),
        )


class DeadLetterRepository(Protocol):
    """Repository for dead-letter queue entries."""

    async def add_dead_letter(self, entry: DeadLetterEntry) -> DeadLetterEntry:
        raise NotImplementedError

    async def get_dead_letter(
        self,
        dead_letter_id: str,
        *,
        tenant_id: str,
    ) -> DeadLetterEntry | None:
        raise NotImplementedError

    async def list_dead_letters(
        self,
        tenant_id: str,
        *,
        replayed: bool | None = None,
    ) -> list[DeadLetterEntry]:
        raise NotImplementedError

    async def mark_replayed(
        self,
        dead_letter_id: str,
        replayed_at: str,
        *,
        tenant_id: str | None = None,
    ) -> DeadLetterEntry | None:
        raise NotImplementedError


class InMemoryDeadLetterRepository:
    """In-memory dead-letter storage."""

    def __init__(self) -> None:
        self._entries: dict[str, DeadLetterEntry] = {}

    async def add_dead_letter(self, entry: DeadLetterEntry) -> DeadLetterEntry:
        self._entries[entry.dead_letter_id] = entry
        return entry

    async def get_dead_letter(
        self,
        dead_letter_id: str,
        *,
        tenant_id: str,
    ) -> DeadLetterEntry | None:
        entry = self._entries.get(dead_letter_id)
        if entry is None or entry.tenant_id != tenant_id:
            return None
        return entry

    async def list_dead_letters(
        self,
        tenant_id: str,
        *,
        replayed: bool | None = None,
    ) -> list[DeadLetterEntry]:
        entries = [e for e in self._entries.values() if e.tenant_id == tenant_id]
        if replayed is not None:
            entries = [e for e in entries if e.replayed == replayed]
        return sorted(entries, key=lambda e: e.received_at, reverse=True)

    async def mark_replayed(
        self,
        dead_letter_id: str,
        replayed_at: str,
        *,
        tenant_id: str | None = None,
    ) -> DeadLetterEntry | None:
        entry = self._entries.get(dead_letter_id)
        if entry is None:
            return None
        if tenant_id is not None and entry.tenant_id != tenant_id:
            return None

        updated = DeadLetterEntry(
            dead_letter_id=entry.dead_letter_id,
            tenant_id=entry.tenant_id,
            provider=entry.provider,
            provider_instance_id=entry.provider_instance_id,
            source_event_id=entry.source_event_id,
            event_type=entry.event_type,
            occurred_at=entry.occurred_at,
            received_at=entry.received_at,
            error_type=entry.error_type,
            error_message=entry.error_message,
            raw_payload=entry.raw_payload,
            retry_count=entry.retry_count + 1,
            replayed=True,
            replayed_at=replayed_at,
        )
        self._entries[dead_letter_id] = updated
        return updated


class CosmosDeadLetterRepository:
    """Cosmos-backed dead-letter storage."""

    def __init__(self, cosmos: CosmosConfig) -> None:
        self._store = CosmosCRUD(cosmos.integration_dead_letters_container, cosmos)

    async def add_dead_letter(self, entry: DeadLetterEntry) -> DeadLetterEntry:
        payload = {
            "id": entry.dead_letter_id,
            "docType": "dead_letter_entry",
            **asdict(entry),
        }
        result = await self._store.create_item_strict(
            payload,
            partition_key=entry.tenant_id,
        )
        return self._payload_to_entry(result.item)

    async def get_dead_letter(
        self,
        dead_letter_id: str,
        *,
        tenant_id: str,
    ) -> DeadLetterEntry | None:
        try:
            payload = await self._store.read_item(dead_letter_id, partition_key=tenant_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
        if payload.get("docType") != "dead_letter_entry":
            return None
        return self._payload_to_entry(payload)

    async def list_dead_letters(
        self,
        tenant_id: str,
        *,
        replayed: bool | None = None,
    ) -> list[DeadLetterEntry]:
        query = "SELECT * FROM c WHERE c.docType = @docType AND c.tenant_id = @tenantId"
        parameters = [
            {"name": "@docType", "value": "dead_letter_entry"},
            {"name": "@tenantId", "value": tenant_id},
        ]

        if replayed is not None:
            query += " AND c.replayed = @replayed"
            parameters.append({"name": "@replayed", "value": replayed})

        rows = await self._store.list_items(query=query, parameters=parameters, partition_key=tenant_id)
        return sorted([self._payload_to_entry(row) for row in rows], key=lambda e: e.received_at, reverse=True)

    async def mark_replayed(
        self,
        dead_letter_id: str,
        replayed_at: str,
        *,
        tenant_id: str | None = None,
    ) -> DeadLetterEntry | None:
        if tenant_id is None:
            return None

        try:
            payload = await self._store.read_item(dead_letter_id, partition_key=tenant_id)
            if payload.get("docType") != "dead_letter_entry":
                return None

            entry = self._payload_to_entry(payload)
            updated_payload = {
                "id": entry.dead_letter_id,
                "docType": "dead_letter_entry",
                **asdict(entry),
                "replayed": True,
                "replayed_at": replayed_at,
                "retry_count": entry.retry_count + 1,
            }
            result = await self._store.update_item(
                entry.dead_letter_id,
                updated_payload,
                partition_key=tenant_id,
            )
            return self._payload_to_entry(result)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None

    @staticmethod
    def _payload_to_entry(payload: dict) -> DeadLetterEntry:
        return DeadLetterEntry(
            dead_letter_id=payload["dead_letter_id"],
            tenant_id=payload["tenant_id"],
            provider=payload["provider"],
            provider_instance_id=payload["provider_instance_id"],
            source_event_id=payload["source_event_id"],
            event_type=payload["event_type"],
            occurred_at=payload["occurred_at"],
            received_at=payload["received_at"],
            error_type=payload["error_type"],
            error_message=payload["error_message"],
            raw_payload=payload["raw_payload"],
            retry_count=payload.get("retry_count", 0),
            replayed=payload.get("replayed", False),
            replayed_at=payload.get("replayed_at"),
        )
