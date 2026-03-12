"""Shared Cosmos CRUD repository."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable, Mapping
from contextlib import asynccontextmanager
from typing import Any, cast

from azure.core import exceptions as azure_exceptions
from azure.cosmos import exceptions as cosmos_exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from tutor_lib.config import CosmosConfig


class CosmosCRUD:
    def __init__(self, container_name: str, config: CosmosConfig) -> None:
        self._endpoint = config.endpoint
        self._database = config.database
        self._container = container_name

    @asynccontextmanager
    async def _container_client(self) -> AsyncIterator[Any]:
        async with DefaultAzureCredential() as credential:
            async with CosmosClient(self._endpoint, credential=credential) as client:
                database = client.get_database_client(self._database)
                container = database.get_container_client(self._container)
                yield container

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {key: self._normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._normalize(item) for item in value]
        if isinstance(value, tuple):
            return [self._normalize(item) for item in value]
        return value

    @staticmethod
    def _is_retryable_cosmos_error(exc: Exception) -> bool:
        if isinstance(exc, (azure_exceptions.ServiceRequestError, azure_exceptions.ServiceResponseError)):
            return True

        status_code = cast(int | None, getattr(exc, "status_code", None))
        if status_code is None:
            return isinstance(exc, azure_exceptions.AzureError)
        if status_code in {408, 429}:
            return True
        return status_code >= 500

    async def _with_retries(self, operation: str, callback: Any) -> Any:
        delay_seconds = 0.5
        max_attempts = 3
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                return await callback()
            except cosmos_exceptions.CosmosResourceNotFoundError:
                raise
            except (
                cosmos_exceptions.CosmosHttpResponseError,
                azure_exceptions.ServiceRequestError,
                azure_exceptions.ServiceResponseError,
                azure_exceptions.AzureError,
            ) as exc:
                if not self._is_retryable_cosmos_error(exc):
                    raise
                last_error = exc
                if attempt == max_attempts:
                    break
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Operation '{operation}' failed without an explicit exception")

    async def list_items(
        self,
        query: str = "SELECT * FROM c",
        parameters: Iterable[dict[str, Any]] | None = None,
    ) -> list[Any]:
        params = list(parameters or [])

        async def _execute() -> list[Any]:
            async with self._container_client() as container:
                return [self._normalize(item) async for item in container.query_items(query=query, parameters=params)]

        return await self._with_retries("list_items", _execute)

    async def create_item(self, item: dict[str, Any]) -> Any:
        async def _execute() -> Any:
            async with self._container_client() as container:
                created = await container.upsert_item(item)
                return self._normalize(created)

        return await self._with_retries("create_item", _execute)

    async def read_item(self, item_id: str, partition_key: str | None = None) -> Any:
        key = partition_key or item_id

        async def _execute() -> Any:
            async with self._container_client() as container:
                item = await container.read_item(item=item_id, partition_key=key)
                return self._normalize(item)

        return await self._with_retries("read_item", _execute)

    async def update_item(
        self,
        item_id: str,
        item: dict[str, Any],
        partition_key: str | None = None,
    ) -> Any:
        key = partition_key or item_id

        async def _execute() -> Any:
            async with self._container_client() as container:
                updated = await container.replace_item(item=item_id, body=item, partition_key=key)
                return self._normalize(updated)

        return await self._with_retries("update_item", _execute)

    async def delete_item(self, item_id: str, partition_key: str | None = None) -> Any:
        key = partition_key or item_id

        async def _execute() -> Any:
            async with self._container_client() as container:
                return await container.delete_item(item=item_id, partition_key=key)

        return await self._with_retries("delete_item", _execute)
