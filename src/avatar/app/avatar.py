import logging
import os
import sys
import time

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from azure.cosmos import exceptions
from dotenv import find_dotenv, load_dotenv
from promptflow.core import Prompty, AzureOpenAIModelConfiguration
from promptflow.tracing import trace

from app.schemas import ChatResponse


load_dotenv(find_dotenv())

DEFAULT_CREDENTIAL = DefaultAzureCredential()
GPT4_KEY = os.getenv("GPT4O_KEY", "")
GPT4_URL = os.getenv("GPT4O_URL", "")
MODEL_URL: str = os.environ.get("GPT4_URL", "")
MODEL_KEY: str = os.environ.get("GPT4_KEY", "")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_CONFIG = AzureOpenAIModelConfiguration(
    azure_deployment="gpt-4o-mini",
    azure_endpoint=MODEL_URL,
    api_version="2024-08-01-preview",
    api_key=MODEL_KEY
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class AvatarChat:

    def __init__(
            self,
            model_config: AzureOpenAIModelConfiguration = MODEL_CONFIG
        ):
        self.model_config = model_config
        self.case = None

    def __call__(self, prompt_data: ChatResponse):
        logger.info("Starting the avatar response...")
        start_time = time.time()
        self.case = self.case if self.case else self.get_case(prompt_data.case_id)
        evaluation = self.evaluate(self.case, prompt_data)
        logger.info("The evaluation process has taken: %s seconds", time.time() - start_time)
        return evaluation

    def get_case(self, case_id: str):
        with CosmosClient(COSMOS_ENDPOINT, DEFAULT_CREDENTIAL) as client:
            try:
                database = client.get_database_client(os.getenv("DATABASE_NAME", "avatar"))
                database.read()
            except exceptions.CosmosResourceNotFoundError:
                client.create_database(os.getenv("DATABASE_NAME", "avatar"))
            container = database.get_container_client(os.getenv("CONTAINER_NAME", "avatar_case"))
            query = f"SELECT * FROM c WHERE c.id = '{case_id}'"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            if items:
                return items[0]
            else:
                raise exceptions.CosmosResourceNotFoundError(f"Case with id {id} not found.")

    @trace
    def evaluate(self, avatar_data: dict, prompt_data: ChatResponse):
        start = time.time()
        prompty = Prompty.load(
            source=f"{BASE_DIR}/prompts/avatar.prompty",
            model={"configuration": self.model_config},
        )
        output = prompty(
            role=avatar_data["profile"]["role"],
            name=avatar_data["name"],
            profile=avatar_data["profile"],
            case=avatar_data["role"],
            steps=avatar_data["steps"],
            user_prompt=prompt_data.prompt
        )
        logger.info("Evaluation took: %s seconds", time.time() - start)
        return output
