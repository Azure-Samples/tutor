"""FastAPI application surface for the essays service."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cosmos_crud import CosmosCRUD
from app.essays import EssayOrchestrator
from app.schemas import (
    RESPONSES,
    BodyMessage,
    ChatResponse,
    Essay,
    ErrorMessage,
    Resource,
    SuccessMessage,
    Swarm,
)
from common.config import get_settings


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


def _crud(container: str) -> CosmosCRUD:
    return CosmosCRUD(container, settings.cosmos)


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


@app.get("/assemblies", tags=["Assemblies"])
async def list_assemblies() -> JSONResponse:
    items = await _crud(settings.cosmos.assembly_container).list_items()
    return _create_success_response("Assemblies Retrieved", "Assemblies fetched", items)


@app.post("/assemblies", tags=["Assemblies"])
async def create_assembly(assembly: Swarm) -> JSONResponse:
    created = await _crud(settings.cosmos.assembly_container).create_item(assembly.model_dump())
    return _create_success_response("Assembly Created", "Assembly stored", created)


@app.put("/assemblies/{assembly_id}", tags=["Assemblies"])
async def update_assembly(assembly_id: str, assembly: Swarm) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        existing = await crud.read_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    merged = {**existing, **assembly.model_dump()}
    await crud.update_item(assembly_id, merged)
    return _create_success_response("Assembly Updated", "Assembly modified", merged)


@app.delete("/assemblies/{assembly_id}", tags=["Assemblies"])
async def delete_assembly(assembly_id: str) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        await crud.delete_item(assembly_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    return _create_success_response("Assembly Deleted", "Assembly removed", {"assembly_id": assembly_id})
