"""Shared Cosmos CRUD repository."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Mapping
from contextlib import asynccontextmanager
from typing import Any

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

    async def list_items(
        self,
        query: str = "SELECT * FROM c",
        parameters: Iterable[dict[str, Any]] | None = None,
    ) -> list[Any]:
        params = list(parameters or [])
        async with self._container_client() as container:
            return [self._normalize(item) async for item in container.query_items(query=query, parameters=params)]

    async def create_item(self, item: dict[str, Any]) -> Any:
        async with self._container_client() as container:
            created = await container.upsert_item(item)
            return self._normalize(created)

    async def read_item(self, item_id: str, partition_key: str | None = None) -> Any:
        key = partition_key or item_id
        async with self._container_client() as container:
            item = await container.read_item(item=item_id, partition_key=key)
            return self._normalize(item)

    async def update_item(
        self,
        item_id: str,
        item: dict[str, Any],
        partition_key: str | None = None,
    ) -> Any:
        key = partition_key or item_id
        async with self._container_client() as container:
            updated = await container.replace_item(item=item_id, body=item, partition_key=key)
            return self._normalize(updated)

    async def delete_item(self, item_id: str, partition_key: str | None = None) -> Any:
        key = partition_key or item_id
        async with self._container_client() as container:
            return await container.delete_item(item=item_id, partition_key=key)
