"""In-memory repositories for datasets and evaluation runs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from azure.cosmos import exceptions as cosmos_exceptions
from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD


@dataclass
class DatasetRecord:
    dataset_id: str
    name: str
    items: list[dict[str, str]] = field(default_factory=list)


@dataclass
class RunRecord:
    run_id: str
    agent_id: str
    dataset_id: str
    status: str
    total_cases: int


class EvaluationRepository(ABC):
    @abstractmethod
    async def create_dataset(self, dataset: DatasetRecord) -> DatasetRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_datasets(self) -> list[DatasetRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> DatasetRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def create_run(self, run: RunRecord) -> RunRecord:
        raise NotImplementedError

    @abstractmethod
    async def get_run(self, run_id: str) -> RunRecord | None:
        raise NotImplementedError


class InMemoryEvaluationRepository(EvaluationRepository):
    def __init__(self) -> None:
        self.datasets: dict[str, DatasetRecord] = {}
        self.runs: dict[str, RunRecord] = {}

    async def create_dataset(self, dataset: DatasetRecord) -> DatasetRecord:
        self.datasets[dataset.dataset_id] = dataset
        return dataset

    async def list_datasets(self) -> list[DatasetRecord]:
        return list(self.datasets.values())

    async def get_dataset(self, dataset_id: str) -> DatasetRecord | None:
        return self.datasets.get(dataset_id)

    async def create_run(self, run: RunRecord) -> RunRecord:
        self.runs[run.run_id] = run
        return run

    async def get_run(self, run_id: str) -> RunRecord | None:
        return self.runs.get(run_id)


class CosmosEvaluationRepository(EvaluationRepository):
    def __init__(self, cosmos: CosmosConfig) -> None:
        self._dataset_store = CosmosCRUD(cosmos.resources_container, cosmos)
        self._run_store = CosmosCRUD(cosmos.grader_container, cosmos)

    async def create_dataset(self, dataset: DatasetRecord) -> DatasetRecord:
        payload = {
            "id": dataset.dataset_id,
            "docType": "dataset",
            "name": dataset.name,
            "items": dataset.items,
        }
        await self._dataset_store.create_item(payload)
        return dataset

    async def list_datasets(self) -> list[DatasetRecord]:
        rows = await self._dataset_store.list_items(
            query="SELECT c.id, c.name, c.items FROM c WHERE c.docType = @docType",
            parameters=[{"name": "@docType", "value": "dataset"}],
        )
        return [
            DatasetRecord(
                dataset_id=item["id"],
                name=item["name"],
                items=item.get("items", []),
            )
            for item in rows
        ]

    async def get_dataset(self, dataset_id: str) -> DatasetRecord | None:
        try:
            item = await self._dataset_store.read_item(dataset_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
        if item.get("docType") != "dataset":
            return None
        return DatasetRecord(
            dataset_id=item["id"],
            name=item["name"],
            items=item.get("items", []),
        )

    async def create_run(self, run: RunRecord) -> RunRecord:
        payload = {
            "id": run.run_id,
            "docType": "run",
            "agent_id": run.agent_id,
            "dataset_id": run.dataset_id,
            "status": run.status,
            "total_cases": run.total_cases,
        }
        await self._run_store.create_item(payload)
        return run

    async def get_run(self, run_id: str) -> RunRecord | None:
        try:
            item = await self._run_store.read_item(run_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
        if item.get("docType") != "run":
            return None
        return RunRecord(
            run_id=item["id"],
            agent_id=item["agent_id"],
            dataset_id=item["dataset_id"],
            status=item["status"],
            total_cases=item["total_cases"],
        )


def to_dict(record: DatasetRecord | RunRecord) -> dict[str, object]:
    return dict(record.__dict__)
