"""FastAPI application surface for the questions service."""

from __future__ import annotations

import logging
from dataclasses import asdict
from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cosmos_crud import CosmosCRUD
from app.questions import evaluate_question
from app.schemas import (
    RESPONSES,
    Answer,
    Assembly,
    BodyMessage,
    ChatResponse,
    ErrorMessage,
    Grader,
    Question,
    SuccessMessage,
)
from tutor_lib.config import get_settings
from tutor_lib.middleware import configure_entra_auth


logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Questions",
    version="2.0.0",
    description="Question evaluation microservice powered by Azure AI Foundry Agents",
    openapi_tags=[
        {"name": "Evaluation", "description": "Question grading flows"},
        {"name": "Questions", "description": "Question CRUD operations"},
        {"name": "Answers", "description": "Student answer management"},
        {"name": "Graders", "description": "Evaluator configuration"},
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


@lru_cache(maxsize=8)
def _crud(container: str) -> CosmosCRUD:
    return CosmosCRUD(container, settings.cosmos)


def _success(title: str, message: str, content: Any) -> JSONResponse:
    body = SuccessMessage(title=title, message=message, content=content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(body))


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
    logger.exception("Unhandled error in questions service", exc_info=exc)
    body = ErrorMessage(
        success=False,
        type="internal",
        title="Unexpected error",
        detail={"message": str(exc)},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(body))


@app.post("/grader/interaction", tags=["Evaluation"])
async def grader_interaction(payload: ChatResponse) -> JSONResponse:
    result = await evaluate_question(payload.case_id, payload.question, payload.answer)
    return JSONResponse(jsonable_encoder(asdict(result)))


@app.get("/questions", tags=["Questions"])
async def list_questions() -> JSONResponse:
    items = await _crud(settings.cosmos.question_container).list_items()
    return _success("Questions Retrieved", "Questions fetched successfully", items)


@app.post("/questions", tags=["Questions"])
async def create_question(question: Question) -> JSONResponse:
    created = await _crud(settings.cosmos.question_container).create_item(question.model_dump())
    return _success("Question Created", "Question stored", created)


@app.put("/questions/{question_id}", tags=["Questions"])
async def update_question(question_id: str, question: Question) -> JSONResponse:
    crud = _crud(settings.cosmos.question_container)
    try:
        existing = await crud.read_item(question_id)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Error reading question %s", question_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found") from exc
    merged = {**existing, **question.model_dump()}
    await crud.update_item(question_id, merged)
    return _success("Question Updated", "Question modified", merged)


@app.delete("/questions/{question_id}", tags=["Questions"])
async def delete_question(question_id: str) -> JSONResponse:
    try:
        await _crud(settings.cosmos.question_container).delete_item(question_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error deleting question %s", question_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found") from exc
    return _success("Question Deleted", "Question removed", {"question_id": question_id})


@app.get("/answers", tags=["Answers"])
async def list_answers() -> JSONResponse:
    items = await _crud(settings.cosmos.answer_container).list_items()
    return _success("Answers Retrieved", "Answers fetched", items)


@app.post("/answers", tags=["Answers"])
async def create_answer(answer: Answer) -> JSONResponse:
    created = await _crud(settings.cosmos.answer_container).create_item(answer.model_dump())
    return _success("Answer Created", "Answer stored", created)


@app.put("/answers/{answer_id}", tags=["Answers"])
async def update_answer(answer_id: str, answer: Answer) -> JSONResponse:
    crud = _crud(settings.cosmos.answer_container)
    try:
        existing = await crud.read_item(answer_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error reading answer %s", answer_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found") from exc
    merged = {**existing, **answer.model_dump()}
    await crud.update_item(answer_id, merged)
    return _success("Answer Updated", "Answer modified", merged)


@app.delete("/answers/{answer_id}", tags=["Answers"])
async def delete_answer(answer_id: str) -> JSONResponse:
    try:
        await _crud(settings.cosmos.answer_container).delete_item(answer_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error deleting answer %s", answer_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found") from exc
    return _success("Answer Deleted", "Answer removed", {"answer_id": answer_id})


@app.get("/graders", tags=["Graders"])
async def list_graders() -> JSONResponse:
    items = await _crud(settings.cosmos.grader_container).list_items()
    return _success("Graders Retrieved", "Graders fetched", items)


@app.post("/graders", tags=["Graders"])
async def create_grader(grader: Grader) -> JSONResponse:
    created = await _crud(settings.cosmos.grader_container).create_item(grader.model_dump())
    return _success("Grader Created", "Grader stored", created)


@app.put("/graders/{grader_id}", tags=["Graders"])
async def update_grader(grader_id: str, grader: Grader) -> JSONResponse:
    crud = _crud(settings.cosmos.grader_container)
    try:
        existing = await crud.read_item(grader_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error reading grader %s", grader_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grader not found") from exc
    merged = {**existing, **grader.model_dump()}
    await crud.update_item(grader_id, merged)
    return _success("Grader Updated", "Grader modified", merged)


@app.delete("/graders/{grader_id}", tags=["Graders"])
async def delete_grader(grader_id: str) -> JSONResponse:
    try:
        await _crud(settings.cosmos.grader_container).delete_item(grader_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error deleting grader %s", grader_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grader not found") from exc
    return _success("Grader Deleted", "Grader removed", {"grader_id": grader_id})


@app.get("/assemblies", tags=["Assemblies"])
async def list_assemblies() -> JSONResponse:
    items = await _crud(settings.cosmos.assembly_container).list_items()
    return _success("Assemblies Retrieved", "Assemblies fetched", items)


@app.post("/assemblies", tags=["Assemblies"])
async def create_assembly(assembly: Assembly) -> JSONResponse:
    created = await _crud(settings.cosmos.assembly_container).create_item(assembly.model_dump())
    return _success("Assembly Created", "Assembly stored", created)


@app.put("/assemblies/{assembly_id}", tags=["Assemblies"])
async def update_assembly(assembly_id: str, assembly: Assembly) -> JSONResponse:
    crud = _crud(settings.cosmos.assembly_container)
    try:
        existing = await crud.read_item(assembly_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error reading assembly %s", assembly_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    merged = {**existing, **assembly.model_dump()}
    await crud.update_item(assembly_id, merged)
    return _success("Assembly Updated", "Assembly modified", merged)


@app.delete("/assemblies/{assembly_id}", tags=["Assemblies"])
async def delete_assembly(assembly_id: str) -> JSONResponse:
    try:
        await _crud(settings.cosmos.assembly_container).delete_item(assembly_id)
    except Exception as exc:  # pragma: no cover
        logger.error("Error deleting assembly %s", assembly_id, exc_info=exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assembly not found") from exc
    return _success("Assembly Deleted", "Assembly removed", {"assembly_id": assembly_id})
