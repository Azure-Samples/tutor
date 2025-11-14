"""FastAPI application surface for the essays service."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agents.clients import FoundryAgentService
from app.cosmos import CosmosCRUD
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


settings = get_settings()


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
    return SwarmDefinition(id=swarm.id, topic_name=swarm.topic_name, agents=agents)


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
    )
    return _swarm_definition_from_swarm(swarm)


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


def _create_success_response(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
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
    return _create_success_response("Resources Retrieved", "Resources fetched", items)


@app.post("/resources", tags=["Resources"])
async def create_resource(resource: Resource) -> JSONResponse:
    created = await _crud(settings.cosmos.resources_container).create_item(resource.model_dump())
    return _create_success_response("Resource Created", "Resource stored", created)


@app.put("/resources/{resource_id}", tags=["Resources"])
async def update_resource(resource_id: str, resource: Resource) -> JSONResponse:
    crud = _crud(settings.cosmos.resources_container)
    try:
        existing = await crud.read_item(resource_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc
    merged = {**existing, **resource.model_dump()}
    await crud.update_item(resource_id, merged)
    return _create_success_response("Resource Updated", "Resource modified", merged)


@app.delete("/resources/{resource_id}", tags=["Resources"])
async def delete_resource(resource_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.resources_container)
    try:
        await crud.delete_item(resource_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc
    return _create_success_response("Resource Deleted", "Resource removed", {"resource_id": resource_id})


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


@app.get("/agents/{agent_id}", tags=["Assemblies"])
async def get_agent(agent_id: str) -> JSONResponse:
    try:
        remote = await agent_service.get_agent(agent_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found") from exc

    provisioned = _materialize_agent(remote)
    return _create_success_response("Agent Retrieved", "Agent fetched", provisioned.model_dump())


@app.get("/assemblies", tags=["Assemblies"])
async def list_assemblies() -> JSONResponse:
    records = await _crud(settings.cosmos.assembly_container).list_items()
    hydrated = [await _hydrate_swarm_record(record) for record in records]
    return _create_success_response(
        "Assemblies Retrieved",
        "Assemblies fetched",
        [swarm.model_dump() for swarm in hydrated],
    )


@app.post("/assemblies", tags=["Assemblies"])
async def create_assembly(assembly: SwarmDefinition) -> JSONResponse:
    try:
        provisioned = await _ensure_provisioned_agents(assembly.agents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to provision agents") from exc
    stored = Swarm(id=assembly.id, topic_name=assembly.topic_name, agents=provisioned)
    await _crud(settings.cosmos.assembly_container).create_item(stored.model_dump())
    response = _swarm_definition_from_swarm(stored)
    return _create_success_response("Assembly Created", "Assembly stored", response.model_dump())


@app.put("/assemblies/{assembly_id}", tags=["Assemblies"])
async def update_assembly(assembly_id: str, assembly: SwarmDefinition) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        await crud.read_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    try:
        provisioned = await _ensure_provisioned_agents(assembly.agents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to provision agents") from exc
    stored = Swarm(id=assembly_id, topic_name=assembly.topic_name, agents=provisioned)
    await crud.update_item(assembly_id, stored.model_dump())
    response = _swarm_definition_from_swarm(stored)
    return _create_success_response("Assembly Updated", "Assembly modified", response.model_dump())


@app.delete("/assemblies/{assembly_id}", tags=["Assemblies"])
async def delete_assembly(assembly_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        await crud.delete_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    return _create_success_response("Assembly Deleted", "Assembly removed", {"assembly_id": assembly_id})
