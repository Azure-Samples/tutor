"""FastAPI application surface for the essays service."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Iterable
from uuid import uuid4

from pydantic import ValidationError

from fastapi import File, FastAPI, Form, HTTPException, Request, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agents.clients import FoundryAgentService
from app.cosmos import CosmosCRUD
from app.file_processing import (
    ProcessedUpload,
    encode_base64,
    normalise_objectives,
    process_upload,
    read_upload_bytes,
)
from app.essays import EssayOrchestrator
from app.schemas import (
    RESPONSES,
    BodyMessage,
    AgentDefinition,
    ChatResponse,
    Essay,
    ErrorMessage,
    ProvisionedAgent,
    Resource,
    SuccessMessage,
    Swarm,
    SwarmDefinition,
)
from app.config import get_settings
from tutor_lib.middleware import configure_entra_auth


ESSAY_FIELDS: tuple[str, ...] = (
    "id",
    "topic",
    "content",
    "explanation",
    "content_file_location",
    "theme",
    "file_url",
    "assembly_id",
)

RESOURCE_FIELDS: tuple[str, ...] = (
    "id",
    "objective",
    "content",
    "url",
    "essay_id",
    "file_name",
    "content_type",
    "encoded_content",
    "metadata",
)


settings = get_settings()
MAX_RESOURCE_DOCUMENT_BYTES = 1_900_000  # Cosmos DB enforces a 2 MB per-item limit

_RESOURCE_CONTENT_CACHE: dict[str, BytesIO] = {}


app = FastAPI(
    title="Essays",
    version="2.0.0",
    description="Essay evaluation microservice powered by Azure AI Foundry Agents",
    openapi_tags=[
        {"name": "Evaluation", "description": "Essay grading flows"},
        {"name": "Essays", "description": "Essay CRUD operations"},
        {"name": "Resources", "description": "Reference material management"},
        {"name": "Assemblies", "description": "Agent assembly management"},
    ],
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore[arg-type]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
configure_entra_auth(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    body = BodyMessage(
        success=False,
        type="validation",
        title="Invalid request payload",
        detail={"invalid-params": list(exc.errors())},
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder(body))


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    body = ErrorMessage(
        success=False,
        type="internal",
        title="Unexpected error",
        detail={"message": str(exc)},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(body))


orchestrator = EssayOrchestrator()
agent_service = FoundryAgentService(settings.azure_ai.project_endpoint)


def _crud(container: str) -> CosmosCRUD:
    return CosmosCRUD(container, settings.cosmos)


def _filter_payload(record: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    return {field: record.get(field) for field in fields if field in record}


def _cache_resource_bytes(resource_id: str, payload: bytes | None) -> None:
    """Persist binary resource payloads in memory for the current process only."""

    if payload is None:
        _RESOURCE_CONTENT_CACHE.pop(resource_id, None)
        return
    _RESOURCE_CONTENT_CACHE[resource_id] = BytesIO(payload)


def _get_cached_resource_bytes(resource_id: str) -> bytes | None:
    """Retrieve any binary content stored in the in-memory cache."""

    buffer = _RESOURCE_CONTENT_CACHE.get(resource_id)
    if buffer is None:
        return None
    return buffer.getvalue()


def _get_cached_resource_content(resource_id: str) -> str | None:
    """Return a base64 representation of cached bytes, if present."""

    payload = _get_cached_resource_bytes(resource_id)
    if payload is None:
        return None
    return encode_base64(payload)


def _decode_base64_payload(data: str) -> bytes:
    """Decode base64 input, raising a helpful HTTP error on failure."""

    try:
        return base64.b64decode(data, validate=True)
    except Exception as exc:  # pragma: no cover - depends on client payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 payload supplied for encoded_content.",
        ) from exc


def _essay_from_record(record: dict[str, Any]) -> Essay:
    payload = _filter_payload(record, ESSAY_FIELDS)
    try:
        return Essay.model_validate(payload)
    except ValidationError as exc:  # pragma: no cover - persisted data shape error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored essay document is missing required fields",
        ) from exc


async def _resources_for_essay(essay_id: str) -> list[Resource]:
    records = await _crud(settings.cosmos.resources_container).list_items(
        query="SELECT * FROM c WHERE c.essay_id = @essay_id",
        parameters=[{"name": "@essay_id", "value": essay_id}],
    )
    resources: list[Resource] = []
    for entry in records:
        payload = _filter_payload(entry, RESOURCE_FIELDS)
        objectives = payload.get("objective", [])
        if not isinstance(objectives, list):
            objectives = [objectives]
        payload["objective"] = objectives
        metadata = payload.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            metadata = None
        payload["metadata"] = metadata
        encoded = payload.get("encoded_content")
        if encoded is not None and not isinstance(encoded, str):
            encoded = None
        resource_id = str(payload.get("id") or "")
        if resource_id:
            cached_encoded = _get_cached_resource_content(resource_id)
            if cached_encoded is not None:
                encoded = cached_encoded
        payload["encoded_content"] = encoded
        try:
            resources.append(Resource.model_validate(payload))
        except ValidationError:
            continue
    return resources


def _materialize_agent(agent: Any, fallback: AgentDefinition | None = None) -> ProvisionedAgent:
    """Build a ProvisionedAgent from Azure AI Foundry response with safe fallbacks."""

    name = getattr(agent, "name", None) or (fallback.name if fallback else getattr(agent, "id", "unknown-agent"))
    instructions = getattr(agent, "instructions", None) or (fallback.instructions if fallback else "")
    deployment = (
        getattr(agent, "model", None)
        or getattr(agent, "model_id", None)
        or getattr(agent, "deployment_name", None)
        or (fallback.deployment if fallback else "")
    )
    temperature = getattr(agent, "temperature", None)
    if temperature is None and fallback is not None:
        temperature = fallback.temperature

    return ProvisionedAgent(
        id=getattr(agent, "id"),
        name=name,
        instructions=instructions,
        deployment=deployment,
        temperature=temperature,
    )


async def _ensure_provisioned_agents(definitions: list[AgentDefinition]) -> list[ProvisionedAgent]:
    provisioned: list[ProvisionedAgent] = []
    for definition in definitions:
        if definition.id:
            remote = await agent_service.get_agent(definition.id)
            provisioned.append(_materialize_agent(remote, fallback=definition))
            continue

        created = await agent_service.create_agent(
            name=definition.name,
            instructions=definition.instructions,
            deployment=definition.deployment,
            temperature=definition.temperature,
        )
        remote = await agent_service.get_agent(created.id)
        provisioned.append(_materialize_agent(remote, fallback=definition))
    return provisioned


def _swarm_definition_from_swarm(swarm: Swarm) -> SwarmDefinition:
    agents = [AgentDefinition(**agent.model_dump()) for agent in swarm.agents]
    return SwarmDefinition(id=swarm.id, topic_name=swarm.topic_name, essay_id=swarm.essay_id, agents=agents)


async def _hydrate_swarm_record(raw: dict[str, Any]) -> SwarmDefinition:
    raw_agents = raw.get("agents", []) or []
    provisioned: list[ProvisionedAgent] = []
    for entry in raw_agents:
        if isinstance(entry, dict):
            provisioned.append(ProvisionedAgent.model_validate(entry))
        elif isinstance(entry, str):
            try:
                remote = await agent_service.get_agent(entry)
                provisioned.append(_materialize_agent(remote))
            except Exception:
                provisioned.append(
                    ProvisionedAgent(
                        id=entry,
                        name=entry,
                        instructions="",
                        deployment="",
                        temperature=None,
                    )
                )

    swarm = Swarm(
        id=str(raw.get("id") or ""),
        topic_name=raw.get("topic_name") or raw.get("topicName", ""),
        agents=provisioned,
        essay_id=str(raw.get("essay_id") or raw.get("essayId") or ""),
    )
    return _swarm_definition_from_swarm(swarm)


async def _get_essay_document(essay_id: str) -> dict[str, Any] | None:
    try:
        return await _crud(settings.cosmos.essay_container).read_item(essay_id)
    except Exception:
        return None


async def _require_essay_document(essay_id: str) -> dict[str, Any]:
    document = await _get_essay_document(essay_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")
    return document


async def _assemblies_for_essay(essay_id: str) -> list[dict[str, Any]]:
    query = "SELECT * FROM c WHERE c.essay_id = @essay_id"
    return await _crud(settings.cosmos.assembly_container).list_items(
        query=query,
        parameters=[{"name": "@essay_id", "value": essay_id}],
    )


async def _link_essay_to_assembly(essay_document: dict[str, Any], assembly_id: str) -> None:
    if not essay_document.get("id"):
        return
    if essay_document.get("assembly_id") == assembly_id:
        return
    essay_document["assembly_id"] = assembly_id
    await _crud(settings.cosmos.essay_container).update_item(essay_document["id"], essay_document)


async def _unlink_essay_from_assembly(essay_id: str, assembly_id: str) -> None:
    document = await _get_essay_document(essay_id)
    if not document:
        return
    if document.get("assembly_id") != assembly_id:
        return
    document.pop("assembly_id", None)
    await _crud(settings.cosmos.essay_container).update_item(essay_id, document)


@app.post("/grader/interaction", tags=["Evaluation"])
async def grader_interaction(payload: ChatResponse) -> JSONResponse:
    result = await orchestrator.invoke(payload.case_id, payload.essay, payload.resources)
    return JSONResponse(
        {
            "strategy": result.strategy.value,
            "verdict": result.verdict,
            "strengths": result.strengths,
            "improvements": result.improvements,
        }
    )


@app.post("/essays/{essay_id}/evaluate", tags=["Evaluation"])
async def reprocess_essay_evaluation(essay_id: str) -> JSONResponse:
    try:
        document = await _crud(settings.cosmos.essay_container).read_item(essay_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found") from exc

    assembly_id = document.get("assembly_id")
    if not assembly_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Essay is not associated with an assembly",
        )

    essay_model = _essay_from_record(document)
    resources = await _resources_for_essay(essay_model.id)
    result = await orchestrator.invoke(assembly_id, essay_model, resources)
    evaluation_payload = {
        "strategy": result.strategy.value,
        "verdict": result.verdict,
        "strengths": result.strengths,
        "improvements": result.improvements,
    }
    return _create_success_response(
        "Essay Evaluated",
        "Essay evaluation completed",
        evaluation_payload,
    )


def _create_success_response(title: str, message: str, content: Any) -> JSONResponse:
    serialisable_content = jsonable_encoder(content)
    body = SuccessMessage(title=title, message=message, content=serialisable_content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


@app.get("/essays", tags=["Essays"])
async def list_essays() -> JSONResponse:
    items = await _crud(settings.cosmos.essay_container).list_items()
    return _create_success_response("Essays Retrieved", "Essays fetched successfully", items)


@app.post("/essays", tags=["Essays"])
async def create_essay(essay: Essay) -> JSONResponse:
    await _crud(settings.cosmos.essay_container).create_item(essay.model_dump())
    return _create_success_response("Essay Created", "Essay stored", essay.model_dump())


@app.put("/essays/{essay_id}", tags=["Essays"])
async def update_essay(essay_id: str, essay: Essay) -> JSONResponse:
    crud = _crud(settings.cosmos.essay_container)
    try:
        existing = await crud.read_item(essay_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found") from exc
    merged = {**existing, **essay.model_dump()}
    await crud.update_item(essay_id, merged)
    return _create_success_response("Essay Updated", "Essay modified", merged)


@app.delete("/essays/{essay_id}", tags=["Essays"])
async def delete_essay(essay_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.essay_container)
    try:
        await crud.delete_item(essay_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found") from exc
    return _create_success_response("Essay Deleted", "Essay removed", {"essay_id": essay_id})


@app.get("/resources", tags=["Resources"])
async def list_resources() -> JSONResponse:
    items = await _crud(settings.cosmos.resources_container).list_items()
    for entry in items:
        resource_id = str(entry.get("id") or "")
        if not resource_id:
            continue
        cached_encoded = _get_cached_resource_content(resource_id)
        if cached_encoded is not None:
            entry["encoded_content"] = cached_encoded
    return _create_success_response("Resources Retrieved", "Resources fetched", items)


@app.post("/resources", tags=["Resources"])
async def create_resource(resource: Resource) -> JSONResponse:
    payload = resource.model_dump()
    encoded = payload.get("encoded_content")
    binary_payload: bytes | None = None
    if isinstance(encoded, str):
        binary_payload = _decode_base64_payload(encoded)
    _cache_resource_bytes(payload["id"], binary_payload)
    document_payload = {**payload, "encoded_content": None}
    _ensure_resource_document_size(document_payload)
    await _crud(settings.cosmos.resources_container).create_item(document_payload)
    resource_model = Resource.model_validate(payload)
    return _create_success_response("Resource Created", "Resource stored", resource_model.model_dump())


@app.post("/resources/upload", tags=["Resources"])
async def upload_resource(
    essay_id: str = Form(...),
    objective: str = Form(...),
    file: UploadFile | None = File(None),
    description: str | None = Form(None),
    submission_text: str | None = Form(None),
) -> JSONResponse:
    await _require_essay_document(essay_id)

    objectives = normalise_objectives(objective)
    if not objectives:
        objectives = ["student_submission"]

    payload_content: str | None = None
    file_name: str | None = None
    content_type: str | None = None
    encoded_content: str | None = None
    binary_payload: bytes | None = None
    metadata: dict[str, Any] = {}

    if file is not None:
        file_bytes = read_upload_bytes(await file.read())
        content_type = file.content_type or "application/octet-stream"
        processed: ProcessedUpload = process_upload(file_bytes, file.filename or "uploaded-file", content_type)

        content_parts: list[str] = []
        if description:
            content_parts.append(description)
        if processed.extracted_text:
            content_parts.append(processed.extracted_text)
        payload_content = "\n\n".join(part for part in content_parts if part.strip()) or None

        metadata = dict(processed.metadata)
        if description:
            metadata["description"] = description

        file_name = processed.file_name
        content_type = processed.content_type
        encoded_content = processed.encoded_content
        binary_payload = processed.binary or (
            _decode_base64_payload(encoded_content) if encoded_content else file_bytes
        )
    elif submission_text:
        payload_content = submission_text.strip() or None
        if description:
            metadata["description"] = description
        metadata.setdefault("hint", "Direct text submission")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a file upload or submission text is required",
        )

    if description and not payload_content:
        payload_content = description

    metadata.setdefault("uploaded_at", datetime.now(timezone.utc).isoformat())

    resource_id = str(uuid4())
    resource_payload: dict[str, Any] = {
        "id": resource_id,
        "essay_id": essay_id,
        "objective": objectives,
        "content": payload_content,
        "url": None,
        "file_name": file_name,
        "content_type": content_type,
        "encoded_content": encoded_content,
        "metadata": metadata or None,
    }

    document_payload = {**resource_payload, "encoded_content": None}

    _cache_resource_bytes(resource_id, binary_payload)
    _ensure_resource_document_size(document_payload)

    await _crud(settings.cosmos.resources_container).create_item(document_payload)
    try:
        resource_model = Resource.model_validate(resource_payload)
    except ValidationError as exc:  # pragma: no cover - should not happen with controlled payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource payload") from exc

    return _create_success_response(
        "Resource Uploaded",
        "Resource stored with processed content",
        resource_model.model_dump(),
    )


@app.put("/resources/{resource_id}", tags=["Resources"])
async def update_resource(resource_id: str, resource: Resource) -> JSONResponse:
    crud = _crud(settings.cosmos.resources_container)
    try:
        existing = await crud.read_item(resource_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc
    incoming = resource.model_dump()
    encoded = incoming.get("encoded_content")
    binary_payload: bytes | None = None
    if isinstance(encoded, str):
        binary_payload = _decode_base64_payload(encoded)
    _cache_resource_bytes(resource_id, binary_payload)
    merged = {**existing, **incoming}
    document_payload = {**merged, "encoded_content": None}
    _ensure_resource_document_size(document_payload)
    await crud.update_item(resource_id, document_payload)
    response_payload = {**merged, "encoded_content": _get_cached_resource_content(resource_id)}
    resource_model = Resource.model_validate(response_payload)
    return _create_success_response("Resource Updated", "Resource modified", resource_model.model_dump())


@app.delete("/resources/{resource_id}", tags=["Resources"])
async def delete_resource(resource_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.resources_container)
    try:
        await crud.delete_item(resource_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc
    _cache_resource_bytes(resource_id, None)
    return _create_success_response("Resource Deleted", "Resource removed", {"resource_id": resource_id})


def _ensure_resource_document_size(payload: dict[str, Any]) -> None:
    """Ensure we never send an oversized item to Cosmos DB."""

    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    size_bytes = len(serialized.encode("utf-8"))
    if size_bytes > MAX_RESOURCE_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resource is too large to store. Please upload a smaller file or shorten the submission.",
        )


@app.post("/agents", tags=["Assemblies"])
async def create_agent(definition: AgentDefinition) -> JSONResponse:
    try:
        provisioned = await _ensure_provisioned_agents([definition])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to provision agent") from exc
    agent = provisioned[0]
    return _create_success_response(
        "Agent Created",
        "Agent provisioned in Azure AI Foundry",
        agent.model_dump(),
    )


@app.get("/agents", tags=["Assemblies"])
async def list_agents(limit: int | None = None) -> JSONResponse:
    try:
        agents = await agent_service.list_agents(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to list agents") from exc
    hydrated = [_materialize_agent(agent).model_dump() for agent in agents]
    return _create_success_response("Agents Retrieved", "Agents fetched", hydrated)


@app.get("/agents/{agent_id}", tags=["Assemblies"])
async def get_agent(agent_id: str) -> JSONResponse:
    try:
        remote = await agent_service.get_agent(agent_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found") from exc

    provisioned = _materialize_agent(remote)
    return _create_success_response("Agent Retrieved", "Agent fetched", provisioned.model_dump())


@app.get("/assemblies", tags=["Assemblies"])
async def list_assemblies(essay_id: str | None = None) -> JSONResponse:
    if essay_id:
        records = await _assemblies_for_essay(essay_id)
    else:
        records = await _crud(settings.cosmos.assembly_container).list_items()
    hydrated = [await _hydrate_swarm_record(record) for record in records]
    return _create_success_response(
        "Assemblies Retrieved",
        "Assemblies fetched",
        [swarm.model_dump() for swarm in hydrated],
    )


@app.post("/assemblies", tags=["Assemblies"])
async def create_assembly(assembly: SwarmDefinition) -> JSONResponse:
    essay_document = await _require_essay_document(assembly.essay_id)

    existing_for_essay = await _assemblies_for_essay(assembly.essay_id)
    if existing_for_essay:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Essay already has an assembly",
        )

    try:
        provisioned = await _ensure_provisioned_agents(assembly.agents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to provision agents") from exc
    stored = Swarm(
        id=assembly.id,
        topic_name=assembly.topic_name,
        essay_id=assembly.essay_id,
        agents=provisioned,
    )
    await _crud(settings.cosmos.assembly_container).create_item(stored.model_dump())
    await _link_essay_to_assembly(essay_document, stored.id)
    response = _swarm_definition_from_swarm(stored)
    return _create_success_response("Assembly Created", "Assembly stored", response.model_dump())


@app.put("/assemblies/{assembly_id}", tags=["Assemblies"])
async def update_assembly(assembly_id: str, assembly: SwarmDefinition) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        existing = await crud.read_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    existing_essay_id = existing.get("essay_id") or existing.get("essayId")
    if existing_essay_id and existing_essay_id != assembly.essay_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the essay associated with this assembly",
        )

    essay_document = await _require_essay_document(assembly.essay_id)

    try:
        provisioned = await _ensure_provisioned_agents(assembly.agents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to provision agents") from exc
    stored = Swarm(
        id=assembly_id,
        topic_name=assembly.topic_name,
        essay_id=essay_document["id"],
        agents=provisioned,
    )
    await crud.update_item(assembly_id, stored.model_dump())
    await _link_essay_to_assembly(essay_document, stored.id)
    response = _swarm_definition_from_swarm(stored)
    return _create_success_response("Assembly Updated", "Assembly modified", response.model_dump())


@app.delete("/assemblies/{assembly_id}", tags=["Assemblies"])
async def delete_assembly(assembly_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        record = await crud.read_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    await crud.delete_item(assembly_id)
    essay_identifier = record.get("essay_id") or record.get("essayId")
    if isinstance(essay_identifier, str) and essay_identifier:
        await _unlink_essay_from_assembly(essay_identifier, assembly_id)
    return _create_success_response("Assembly Deleted", "Assembly removed", {"assembly_id": assembly_id})
