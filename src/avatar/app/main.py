"""
The configuration for the web api.
"""

import os
import random
import uuid

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from azure.cosmos import exceptions

from app.schemas import RESPONSES, BodyMessage, ChatResponse, Case
from app.avatar import AvatarChat


load_dotenv(find_dotenv())

BLOB_CONN = os.getenv("BLOB_CONNECTION_STRING", "")
MODEL_URL: str = os.environ.get("GPT4O_URL", "")
MODEL_KEY: str = os.environ.get("GPT4O_KEY", "")
MONITOR: str = os.environ.get("AZ_CONNECTION_LOG", "")
DEFAULT_CREDENTIAL = DefaultAzureCredential()
GPT4_KEY = os.getenv("GPT4O_KEY", "")
GPT4_URL = os.getenv("GPT4O_URL", "")
MODEL_URL: str = os.environ.get("GPT4_URL", "")
MODEL_KEY: str = os.environ.get("GPT4_KEY", "")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


tags_metadata: list[dict] = [
    {
        "name": "Avatar",
        "description": """Endpoints de gerenciamento de dados do Avatar.""",
    },
]

description: str = """
    Uma API Web para gerenciar o avatar.
"""


app: FastAPI = FastAPI(
    title="Avatar",
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

chat = AvatarChat()


@app.post("/response", tags=["Avatar"])
async def avatar_response(params: ChatResponse) -> JSONResponse:
    """
    Uploads an audio file and starts a background task to process it.
    """
    response = chat(params)
    return JSONResponse({'text': response})


@app.get("/profile", tags=["Avatar"])
async def avatar_profile() -> JSONResponse:
    """
    Endpoint para reprocessar lotes de arquivos.
    """
    with CosmosClient(COSMOS_ENDPOINT, DEFAULT_CREDENTIAL) as client:
        try:
            database = client.get_database_client(os.getenv("DATABASE_NAME", "avatar"))
            database.read()
        except exceptions.CosmosResourceNotFoundError:
            client.create_database(os.getenv("DATABASE_NAME", "avatar"))
        container = database.get_container_client(os.getenv("CONTAINER_NAME", "avatar_case"))
        cases = list(container.read_all_items())
    return JSONResponse({"result": random.choice(cases)})


@app.post("/create-case", tags=["Avatar"])
async def create_case(case: Case) -> JSONResponse:
    """
    Endpoint para reprocessar lotes de arquivos.
    """
    with CosmosClient(COSMOS_ENDPOINT, DEFAULT_CREDENTIAL) as client:
        try:
            database = client.get_database_client(os.getenv("DATABASE_NAME", "avatar"))
            database.read()
        except exceptions.CosmosResourceNotFoundError:
            client.create_database(os.getenv("DATABASE_NAME", "avatar"))
        container = database.get_container_client(os.getenv("CONTAINER_NAME", "avatar_case"))
        if not case.id:
            case.id = str(uuid.uuid4())
        container.create_item(body=case.model_dump())
    return JSONResponse({"result": "OK"})
