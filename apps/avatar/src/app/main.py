"""FastAPI surface for the avatar service."""

from __future__ import annotations

import random
import uuid
from functools import lru_cache
from typing import Any, Iterable

from azure.cosmos import exceptions
from fastapi import Body, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.avatar import AvatarChat, build_avatar_chat
from app.config import get_settings
from app.cosmos import CosmosCRUD
from app.speech import SpeechTokenBroker
from app.schemas import BodyMessage, Case, ChatResponse, ErrorMessage, RESPONSES, SuccessMessage
from tutor_lib.middleware import configure_entra_auth


settings = get_settings()

app = FastAPI(
    title="Avatar",
    version="2.0.0",
    description="Avatar conversational agent and case management service",
    openapi_tags=[
        {"name": "Avatar", "description": "Avatar conversation endpoints"},
        {"name": "Configuration", "description": "Case management operations"},
    ],
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore[arg-type]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=r"https://.*\.azurestaticapps\.net",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
configure_entra_auth(app)


@app.get("/health", tags=["Avatar"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["Avatar"])
async def ready() -> dict[str, str]:
    return {"status": "ready"}


def _success(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


@lru_cache(maxsize=1)
def _case_repository() -> CosmosCRUD:
    return CosmosCRUD(settings.cosmos.case_container, settings.cosmos)  # pylint: disable=no-member


@lru_cache(maxsize=1)
def _avatar() -> AvatarChat:
    return build_avatar_chat(settings, _case_repository())


@lru_cache(maxsize=1)
def _speech_broker() -> SpeechTokenBroker:
    speech_settings = settings.model_dump().get("speech", {})
    return SpeechTokenBroker(
        resource_id=str(speech_settings.get("resource_id", "")),
        region=str(speech_settings.get("region", "")),
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
    body = ErrorMessage(success=False, type="internal", title="Unexpected error", detail={"message": str(exc)})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(body))


@app.post("/response", tags=["Avatar"])
async def avatar_response(params: ChatResponse) -> JSONResponse:
    text = await _avatar().respond(params)
    return JSONResponse({"text": text})


@app.get("/profile", tags=["Avatar"])
async def avatar_profile() -> JSONResponse:
    cases = await _case_repository().list_items()
    if not cases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cases available")
    return JSONResponse({"result": random.choice(cases)})


@app.get("/speech/session-token", tags=["Avatar"])
async def speech_session_token() -> JSONResponse:
    try:
        session = await _speech_broker().create_session()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Speech token broker unavailable: {exc}") from exc

    payload = {
        "authorizationToken": session.authorization_token,
        "region": session.region,
        "expiresOn": session.expires_on,
        "relay": session.relay,
    }
    return _success("Speech Session Token Retrieved", "Speech session token fetched", payload)


@app.post("/create-case", tags=["Configuration"])
async def create_case(case: Case) -> JSONResponse:
    payload = case.model_dump()
    if not payload.get("id"):
        payload["id"] = str(uuid.uuid4())
    await _case_repository().create_item(payload)
    return _success("Case Created", "Case stored", payload)


@app.get("/cases", tags=["Configuration"])
async def list_cases() -> JSONResponse:
    items = await _case_repository().list_items()
    return _success("Cases Retrieved", "Cases fetched", items)


@app.get("/cases/{case_id}", tags=["Configuration"])
async def get_case(case_id: str) -> JSONResponse:
    try:
        item = await _case_repository().read_item(case_id)
    except exceptions.CosmosResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found") from exc
    return _success("Case Retrieved", "Case fetched", item)


@app.delete("/cases/{case_id}", tags=["Configuration"])
async def delete_case(case_id: str) -> JSONResponse:
    try:
        await _case_repository().delete_item(case_id)
    except exceptions.CosmosResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found") from exc
    return _success("Case Deleted", "Case removed", {"case_id": case_id})


@app.patch("/cases/{case_id}/steps", tags=["Configuration"])
async def patch_case_steps(case_id: str, steps: Iterable[Any] = Body(...)) -> JSONResponse:
    repo = _case_repository()
    try:
        existing = await repo.read_item(case_id)
    except exceptions.CosmosResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found") from exc
    updated = {**existing, "steps": list(steps)}
    await repo.update_item(case_id, updated)
    return _success("Case Updated", "Steps replaced", updated)


@app.put("/cases/{case_id}", tags=["Configuration"])
async def update_case(case_id: str, case: Case) -> JSONResponse:
    repo = _case_repository()
    try:
        await repo.read_item(case_id)
    except exceptions.CosmosResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found") from exc
    payload = case.model_dump()
    payload["id"] = case_id
    await repo.update_item(case_id, payload)
    return _success("Case Updated", "Case stored", payload)


@app.get("/cases/available", tags=["Configuration"])
async def get_available_cases() -> JSONResponse:
    items = await _case_repository().list_items()
    return _success("Cases Retrieved", "Available cases fetched", items)
