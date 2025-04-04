"""
The configuration for the web api.
"""

import os
from venv import logger

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from azure.identity.aio import DefaultAzureCredential

from app.schemas import RESPONSES, BodyMessage, ErrorMessage, SuccessMessage, ChatResponse, Grader, Question, Answer, Assembly
from app.cosmos_crud import CosmosCRUD
from app.questions import AnswerOrchestrator


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"Base dir: {BASE_DIR}")
ENV_FILE = os.path.join(BASE_DIR, ".env")
print(f"Env file: {ENV_FILE}")
load_dotenv(ENV_FILE)


BLOB_CONN = os.getenv("BLOB_CONNECTION_STRING", "")
MONITOR: str = os.environ.get("AZ_CONNECTION_LOG", "")
DEFAULT_CREDENTIAL = DefaultAzureCredential()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COSMOS_QUESTION_TABLE = "COSMOS_QUESTION_TABLE"
COSMOS_ANSWER_TABLE = "COSMOS_ANSWER_TABLE"
COSMOS_GRADER_TABLE = "COSMOS_GRADER_TABLE"
COSMOS_ASSEMBLY_TABLE = "COSMOS_ASSEMBLY_TABLE"


tags_metadata: list[dict] = [
    {
        "name": "Interação do Avaliador",
        "description": "Endpoint para a interação com o avaliador, usando /grader/interaction.",
    },
    {
        "name": "CRUD - Perguntas",
        "description": "Endpoints para criar, ler, atualizar e deletar perguntas.",
    },
    {
        "name": "CRUD - Respostas",
        "description": "Endpoints para criar, ler, atualizar e deletar respostas.",
    },
    {
        "name": "CRUD - Avaliadores",
        "description": "Endpoints para criar, ler, atualizar e deletar avaliadores.",
    },
    {
        "name": "CRUD - Montagens",
        "description": "Endpoints para criar, ler, atualizar e deletar montagens.",
    },
    {
        "name": "Configuração da API",
        "description": "Endpoints para a configuração e monitoramento da API.",
    },
]


description: str = """
Uma API Web para gerenciar Perguntas e Respostas.
"""


app: FastAPI = FastAPI(
    title="Questions",
    version="Alpha",
    description=description,
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json",
    responses=RESPONSES,  # type: ignore
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError  # pylint: disable=unused-argument
) -> JSONResponse:
    """
    validation_exception_handler Exception handler for validations.

    Args:
        request (Request): the request from the api
        exc (RequestValidationError): the validation raised by the process

    Returns:
        JSONResponse: A json encoded response with the validation errors.
    """

    response_body: BodyMessage = BodyMessage(
        success=False,
        type="Validation Error",
        title="Your request parameters didn't validate.",
        detail={"invalid-params": list(exc.errors())},
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(response_body),
    )


@app.exception_handler(ResponseValidationError)
async def response_exception_handler(
    request: Request, exc: ResponseValidationError  # pylint: disable=unused-argument
) -> JSONResponse:
    """
    response_exception_handler Exception handler for response validations.

    Args:
        request (Request): the request from the api
        exc (RequestValidationError): the validation raised by the process

    Returns:
        JSONResponse: A json encoded response with the validation errors.
    """

    response_body: ErrorMessage = ErrorMessage(
        success=False,
        type="Response Error",
        title="Found Errors on processing your requests.",
        detail={"invalid-params": list(exc.errors())},
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(response_body),
    )


answer_orchestrator = AnswerOrchestrator()


@app.post("/grader/interaction", tags=["Interação do Avaliador"])
async def grader_interaction(payload: ChatResponse) -> JSONResponse:
    """
    Runs the grader interaction orchestration.
    Expects a request body containing the 'case_id' and 'prompt'.
    Returns the evaluated answer from the agents involved.
    """
    aggregated_response = await answer_orchestrator.run_interaction(payload.case_id, payload.question, payload.answer)
    return JSONResponse({"text": jsonable_encoder(aggregated_response)})


@app.get("/questions", tags=["CRUD - Perguntas"])
async def list_questions_endpoint() -> JSONResponse:
    crud = CosmosCRUD(COSMOS_QUESTION_TABLE)
    items = await crud.list_items()
    response_body: SuccessMessage = SuccessMessage(
        title=f"{len(items) if items else 0} Questions Retrieved",
        message="Successfully retrieved question data.",
        content=items,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.post("/questions", tags=["CRUD - Perguntas"])
async def create_question(question: Question) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_QUESTION_TABLE)
    created = await crud.create_item(question.model_dump())
    response_body: SuccessMessage = SuccessMessage(
        title="Question Created",
        message="Question created successfully.",
        content=created,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.put("/questions/{question_id}", tags=["CRUD - Perguntas"])
async def update_question(question_id: str, question: Question) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_QUESTION_TABLE)
    try:
        existing = await crud.read_item(question_id)
        if not existing:
            existing = {}
    except Exception as exc:
        logger.error("Error reading question: %s", exc)
        raise HTTPException(status_code=404, detail="Question not found.") from exc
    updated = {**existing, **question.model_dump()}
    await crud.update_item(question_id, updated)
    response_body: SuccessMessage = SuccessMessage(
        title="Question Updated",
        message="Question updated successfully.",
        content=updated,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.delete("/questions/{question_id}", tags=["CRUD - Perguntas"])
async def delete_question(question_id: str) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_QUESTION_TABLE)
    try:
        await crud.delete_item(question_id)
    except Exception as exc:
        logger.error("Error deleting question: %s", exc)
        raise HTTPException(status_code=404, detail="Question not found.") from exc
    response_body: SuccessMessage = SuccessMessage(
        title="Question Deleted",
        message="Question deleted successfully.",
        content={"question_id": question_id},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.get("/answers", tags=["CRUD - Respostas"])
async def list_answers_endpoint() -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ANSWER_TABLE)
    items = await crud.list_items()
    response_body: SuccessMessage = SuccessMessage(
        title=f"{len(items) if items else 0} Answers Retrieved",
        message="Successfully retrieved answer data.",
        content=items,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.post("/answers", tags=["CRUD - Respostas"])
async def create_answer(answer: Answer) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ANSWER_TABLE)
    created = await crud.create_item(answer.model_dump())
    response_body: SuccessMessage = SuccessMessage(
        title="Answer Created",
        message="Answer created successfully.",
        content=created,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.put("/answers/{answer_id}", tags=["CRUD - Respostas"])
async def update_answer(answer_id: str, answer: Answer) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ANSWER_TABLE)
    try:
        existing = await crud.read_item(answer_id)
        if not existing:
            existing = {}
    except Exception as exc:
        logger.error("Error reading answer: %s", exc)
        raise HTTPException(status_code=404, detail="Answer not found.") from exc
    updated = {**existing, **answer.model_dump()}
    await crud.update_item(answer_id, updated)
    response_body: SuccessMessage = SuccessMessage(
        title="Answer Updated",
        message="Answer updated successfully.",
        content=updated,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.delete("/answers/{answer_id}", tags=["CRUD - Respostas"])
async def delete_answer(answer_id: str) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ANSWER_TABLE)
    try:
        await crud.delete_item(answer_id)
    except Exception as exc:
        logger.error("Error deleting answer: %s", exc)
        raise HTTPException(status_code=404, detail="Answer not found.") from exc
    response_body: SuccessMessage = SuccessMessage(
        title="Answer Deleted",
        message="Answer deleted successfully.",
        content={"answer_id": answer_id},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.get("/graders", tags=["CRUD - Avaliadores"])
async def list_graders_endpoint() -> JSONResponse:
    crud = CosmosCRUD(COSMOS_GRADER_TABLE)
    items = await crud.list_items()
    response_body: SuccessMessage = SuccessMessage(
        title=f"{len(items) if items else 0} Graders Retrieved",
        message="Successfully retrieved grader data.",
        content=items,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.post("/graders", tags=["CRUD - Avaliadores"])
async def create_grader(grader: Grader) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_GRADER_TABLE)
    created = await crud.create_item(grader.model_dump())
    response_body: SuccessMessage = SuccessMessage(
        title="Grader Created",
        message="Grader created successfully.",
        content=created,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.put("/graders/{grader_id}", tags=["CRUD - Avaliadores"])
async def update_grader(grader_id: str, grader: Grader) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_GRADER_TABLE)
    try:
        existing = await crud.read_item(grader_id)
        if not existing:
            existing = {}
    except Exception as exc:
        logger.error("Error reading grader: %s", exc)
        raise HTTPException(status_code=404, detail="Grader not found.") from exc
    updated = {**existing, **grader.model_dump()}
    await crud.update_item(grader_id, updated)
    response_body: SuccessMessage = SuccessMessage(
        title="Grader Updated",
        message="Grader updated successfully.",
        content=updated,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.delete("/graders/{grader_id}", tags=["CRUD - Avaliadores"])
async def delete_grader(grader_id: str) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_GRADER_TABLE)
    try:
        await crud.delete_item(grader_id)
    except Exception as exc:
        logger.error("Error deleting grader: %s", exc)
        raise HTTPException(status_code=404, detail="Grader not found.") from exc
    response_body: SuccessMessage = SuccessMessage(
        title="Grader Deleted",
        message="Grader deleted successfully.",
        content={"grader_id": grader_id},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.get("/assemblies", tags=["CRUD - Montagens"])
async def list_assemblies_endpoint() -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ASSEMBLY_TABLE)
    items = await crud.list_items()
    response_body: SuccessMessage = SuccessMessage(
        title=f"{len(items) if items else 0} Assemblies Retrieved",
        message="Successfully retrieved assembly data.",
        content=items,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.post("/assemblies", tags=["CRUD - Montagens"])
async def create_assembly(assembly: Assembly) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ASSEMBLY_TABLE)
    created = await crud.create_item(assembly.model_dump())
    response_body: SuccessMessage = SuccessMessage(
        title="Assembly Created",
        message="Assembly created successfully.",
        content=created,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.put("/assemblies/{assembly_id}", tags=["CRUD - Montagens"])
async def update_assembly(assembly_id: str, assembly: Assembly) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ASSEMBLY_TABLE)
    try:
        existing = await crud.read_item(assembly_id)
        if not existing:
            existing = {}
    except Exception as exc:
        logger.error("Error reading assembly: %s", exc)
        raise HTTPException(status_code=404, detail="Assembly not found.") from exc
    updated = {**existing, **assembly.model_dump()}
    await crud.update_item(assembly_id, updated)
    response_body: SuccessMessage = SuccessMessage(
        title="Assembly Updated",
        message="Assembly updated successfully.",
        content=updated,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))


@app.delete("/assemblies/{assembly_id}", tags=["CRUD - Montagens"])
async def delete_assembly(assembly_id: str) -> JSONResponse:
    crud = CosmosCRUD(COSMOS_ASSEMBLY_TABLE)
    try:
        await crud.delete_item(assembly_id)
    except Exception as exc:
        logger.error("Error deleting assembly: %s", exc)
        raise HTTPException(status_code=404, detail="Assembly not found.") from exc
    response_body: SuccessMessage = SuccessMessage(
        title="Assembly Deleted",
        message="Assembly deleted successfully.",
        content={"assembly_id": assembly_id},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body))
