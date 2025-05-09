import logging
import os
import sys
import time
import json

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, exceptions
from azure.ai.projects import AIProjectClient
from azure.ai.inference.prompts._patch import PromptTemplate
from dotenv import find_dotenv, load_dotenv

from app.schemas import ChatResponse

# Load environment variables
load_dotenv(find_dotenv())

DEFAULT_CREDENTIAL = DefaultAzureCredential()
GPT4_KEY = os.getenv("GPT4O_KEY", "")
GPT4_URL = os.getenv("GPT4O_URL", "")
MODEL_URL: str = os.environ.get("GPT4_URL", "")
MODEL_KEY: str = os.environ.get("GPT4_KEY", "")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DEPLOYMENT = "gpt-4o-essay-eval"
API_VERSION = "2025-01-01-preview"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

AI_PROJECT = AIProjectClient.from_connection_string(
    conn_str=os.getenv("AZURE_PROJECT_CONNECTION_STRING", ""),
    credential=DefaultAzureCredential()
)

class AvatarChat:

    def __init__(
        self,
        model_deployment: str = MODEL_DEPLOYMENT,
        endpoint: str = MODEL_URL,
        api_key: str = MODEL_KEY,
        api_version: str = API_VERSION
    ):
        self.model_deployment = model_deployment
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = AI_PROJECT.inference.get_chat_completions_client()
        self.template_dir = os.path.join(BASE_DIR, "prompts")

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
            database_name = os.getenv("DATABASE_NAME", "avatar")
            try:
                database = client.get_database_client(database_name)
                database.read()
            except exceptions.CosmosResourceNotFoundError:
                client.create_database(database_name)
                database = client.get_database_client(database_name)
            container_name = os.getenv("CONTAINER_NAME", "avatar_case")
            container = database.get_container_client(container_name)
            query = f"SELECT * FROM c WHERE c.id = '{case_id}'"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            if items:
                return items[0]
            raise exceptions.CosmosResourceNotFoundError(f"Case with id {case_id} not found.")

    def evaluate(self, avatar_data: dict, prompt_data: ChatResponse):
        start = time.time()
        template = PromptTemplate.from_prompty(f"{self.template_dir}\\{avatar_data.get("role", "interviewer")}.prompty")

        messages = template.create_messages(
            role=avatar_data["profile"]["role"],
            name=avatar_data["name"],
            profile=json.dumps(avatar_data["profile"]),
            case=avatar_data["role"],
            steps=json.dumps(avatar_data["steps"]),
            user_prompt=prompt_data.prompt
        )

        if prompt_data.chat_history:
            for msg in prompt_data.chat_history:
                if msg.get("role") == "assistant":
                    messages.append({"role": "assistant", "content": msg.get("content")})
                elif msg.get("role") == "system":
                    messages.append({"role": "system", "content": msg.get("content")})
                elif msg.get("role") == "user":
                    messages.append({"role": "user", "content": msg.get("content")})

        response = self.client.complete(
            model=self.model_deployment,
            messages=messages,
            **template.parameters
        )

        logger.info("Evaluation took: %s seconds", time.time() - start)
        return response.choices[0].message.content
