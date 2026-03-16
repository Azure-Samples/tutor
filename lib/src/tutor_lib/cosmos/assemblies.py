"""Assembly-focused repository abstractions."""

from __future__ import annotations

from typing import Any

from tutor_lib.config import CosmosConfig

from .crud import CosmosCRUD


class AssemblyRepository:
    """Repository for reading assembly documents from Cosmos DB."""

    def __init__(self, config: CosmosConfig, container_name: str | None = None) -> None:
        container = container_name or config.assembly_container
        self._crud = CosmosCRUD(container, config)

    async def get_by_id(self, assembly_id: str) -> dict[str, Any]:
        record = await self._crud.read_item(assembly_id)
        if not isinstance(record, dict):
            raise TypeError("Assembly record is not a JSON object")
        return record

    async def list_for_essay(self, essay_id: str) -> list[dict[str, Any]]:
        rows = await self._crud.list_items(
            query="SELECT * FROM c WHERE c.essay_id = @essay_id",
            parameters=[{"name": "@essay_id", "value": essay_id}],
        )
        return [row for row in rows if isinstance(row, dict)]
