"""In-memory repositories for datasets and evaluation runs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

from azure.cosmos import exceptions as cosmos_exceptions
from tutor_lib.config import CosmosConfig
from tutor_lib.cosmos import CosmosCRUD


@dataclass
class DatasetRecord:
    dataset_id: str
    name: str
    items: list[dict[str, str]] = field(default_factory=list)
    dataset_version: str | None = None
    lineage: dict[str, object] = field(default_factory=dict)


@dataclass
class RunRecord:
    run_id: str
    agent_name: str
    dataset_id: str
    status: str
    total_cases: int
    agent_version: str | None = None
    legacy_agent_id: str | None = None
    dataset_version: str | None = None
    prompt_version: str | None = None
    thresholds: dict[str, float] = field(default_factory=dict)
    trace_id: str | None = None
    report_uri: str | None = None
    approval_state: str = "pending_review"
    safety_metrics: dict[str, float] = field(default_factory=dict)


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
            "dataset_version": dataset.dataset_version,
            "lineage": dataset.lineage,
        }
        await self._dataset_store.create_item(payload)
        return dataset

    async def list_datasets(self) -> list[DatasetRecord]:
        rows = await self._dataset_store.list_items(
            query=(
                "SELECT c.id, c.name, c.items, c.dataset_version, c.lineage "
                "FROM c WHERE c.docType = @docType"
            ),
            parameters=[{"name": "@docType", "value": "dataset"}],
        )
        return [_dataset_from_item(item) for item in rows]

    async def get_dataset(self, dataset_id: str) -> DatasetRecord | None:
        try:
            item = await self._dataset_store.read_item(dataset_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
        if item.get("docType") != "dataset":
            return None
        return _dataset_from_item(item)

    async def create_run(self, run: RunRecord) -> RunRecord:
        payload = {
            "id": run.run_id,
            "docType": "run",
            "agent_name": run.agent_name,
            "agent_version": run.agent_version,
            "legacy_agent_id": run.legacy_agent_id,
            "dataset_id": run.dataset_id,
            "dataset_version": run.dataset_version,
            "prompt_version": run.prompt_version,
            "thresholds": run.thresholds,
            "trace_id": run.trace_id,
            "report_uri": run.report_uri,
            "approval_state": run.approval_state,
            "safety_metrics": run.safety_metrics,
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
        return _run_from_item(item)


def to_dict(record: DatasetRecord | RunRecord) -> dict[str, object]:
    payload: dict[str, object] = asdict(record)
    if isinstance(record, RunRecord):
        payload["agent_id"] = record.legacy_agent_id or record.agent_name
    return payload


def _dataset_from_item(item: Mapping[str, Any]) -> DatasetRecord:
    return DatasetRecord(
        dataset_id=str(item.get("id", "")),
        name=str(item.get("name", "")),
        items=_string_item_list(item.get("items")),
        dataset_version=_optional_string(item.get("dataset_version")),
        lineage=_object_mapping(item.get("lineage")),
    )


def _run_from_item(item: Mapping[str, Any]) -> RunRecord:
    legacy_agent_id = _optional_string(item.get("legacy_agent_id") or item.get("agent_id"))
    agent_name = _optional_string(item.get("agent_name")) or legacy_agent_id or ""
    return RunRecord(
        run_id=str(item.get("id", "")),
        agent_name=agent_name,
        agent_version=_optional_string(item.get("agent_version")),
        legacy_agent_id=legacy_agent_id,
        dataset_id=str(item.get("dataset_id", "")),
        dataset_version=_optional_string(item.get("dataset_version")),
        prompt_version=_optional_string(item.get("prompt_version")),
        thresholds=_float_mapping(item.get("thresholds")),
        trace_id=_optional_string(item.get("trace_id")),
        report_uri=_optional_string(item.get("report_uri")),
        approval_state=_optional_string(item.get("approval_state")) or "pending_review",
        safety_metrics=_float_mapping(item.get("safety_metrics")),
        status=_optional_string(item.get("status")) or "queued",
        total_cases=_int_value(item.get("total_cases")),
    )


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return str(value)


def _object_mapping(value: Any) -> dict[str, object]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): item for key, item in value.items()}


def _float_mapping(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}

    result: dict[str, float] = {}
    for key, item in value.items():
        try:
            result[str(key)] = float(item)
        except (TypeError, ValueError):
            continue
    return result


def _string_item_list(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []

    items: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, Mapping):
            items.append({str(key): str(entry) for key, entry in item.items()})
    return items


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
