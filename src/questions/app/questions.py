"""
avatars.py

This module implements the orchestration of multiple avatar agents in parallel.
Each avatar is loaded with a different personality (profile) and implements its own set 
of interactions based on its configuration. The SuperGrader acts as a mediator, 
registering sub-avatars, launching them in parallel, and aggregating their responses.

Components:
  - GraderBase: Abstract base for an avatar that can interact with a prompt.
  - ConcreteGrader: An avatar that uses ChatCompletionAgent for LLM interactions.
  - SuperGrader: Extends GraderBase and implements a mediator pattern to orchestrate sub-avatars.
  - GraderEvaluationPlan: A Plan that runs sub-avatar interactions concurrently.
  - GraderFactory: Builds a shared Kernel and produces sub-avatar instances from an Assembly.
  - GraderOrchestrator: High-level class that assembles the pieces and runs the interaction.

Usage:
    # 1) Build or load an Assembly (with .avatars defined).
    # 2) Call GraderOrchestrator.run_interaction(assembly_id, prompt)
    #    -> Returns the aggregated responses from all sub-avatars.
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional, Literal, override
from dotenv import load_dotenv

import jinja2
import semantic_kernel as sk

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from app.schemas import Assembly, Grader, Question, Answer
import asyncio


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"Base dir: {BASE_DIR}")
ENV_FILE = os.path.join(BASE_DIR, ".env")
print(f"Env file: {ENV_FILE}")
load_dotenv(ENV_FILE)


COSMOS_DB_NAME = os.getenv("COSMOS_QNA_NAME", "mydb")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://myendpoint.documents.azure.com:443/")

AZURE_MODEL_KEY = os.getenv("AZURE_MODEL_KEY", "")
AZURE_MODEL_URL = os.getenv("AZURE_MODEL_URL", "")

COSMOS_ASSEMBLY_TABLE = os.getenv("COSMOS_ASSEMBLY_TABLE", "assembly")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "prompts")
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))


AVAILABLE_MODELS: list[AzureChatCompletion] = [
    AzureChatCompletion(
        service_id="default",
        api_key=AZURE_MODEL_KEY,
        deployment_name="gpt-4o",
        endpoint=AZURE_MODEL_URL,
    ),
    AzureChatCompletion(
        service_id="mini",
        api_key=AZURE_MODEL_KEY,
        deployment_name="gpt-4o-mini",
        endpoint=AZURE_MODEL_URL,
    )
]


class Mediator(ABC):
    """
    Interface for a mediator that collects notifications from sub-avatars.
    """
    @abstractmethod
    def notify(self, sender: object, event: str, data: dict) -> None:
        """
        Notifies the mediator of an event from a sub-avatar.
        """


class GraderBase(ABC):
    """
    Abstract base for an avatar that can interact with a prompt.
    """
    def __init__(self) -> None:
        self.mediator: Optional[Mediator] = None

    @abstractmethod
    async def interact(self) -> None:
        """
        Interact with the prompt asynchronously.
        """


class AnswerGrader(GraderBase):
    """
    An avatar that uses a ChatCompletionAgent to interact with a prompt.
    Each avatar loads its own personality and instructions from its profile.
    """
    def __init__(self, grader: Grader, kernel: sk.Kernel) -> None:
        super().__init__()
        self.grader = grader
        self.kernel = kernel
        self.agent: ChatCompletionAgent
        self.__prepare()

    def __prepare(self):
        """
        Prepare the avatar for interaction.
        This method can be overridden to implement any setup logic.
        """
        instruction_template = JINJA_ENV.get_template("instruction.jinja")

        rendered_settings = instruction_template.render(
            instructions = self.grader.metaprompt,
        )

        settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id=self.grader.model_id)
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        self.agent = ChatCompletionAgent(
            service_id=str(self.grader.model_id),
            kernel=self.kernel,
            name=self.grader.name,
            instructions=rendered_settings,
            arguments=KernelArguments(settings=settings),
        )

    @override
    async def interact(self, question: Question, answer: Answer, chat: ChatHistory):  # pylint: disable=arguments-differ
        """
        Use a ChatCompletionAgent to interact with the prompt.
        The agent uses the avatar's personality (loaded from a JSON metaprompt)
        to generate a response. Before sending the prompt to the agent,
        the prompt is rendered via a Jinja2 template (if specified).
        When finished, notify the mediator.
        """

        prompt_template = JINJA_ENV.get_template("correct.jinja")
        rendered_prompt = prompt_template.render(
            question=question,
            answer=answer
        )

        chat.add_user_message(rendered_prompt)
        response = ""
        async for message in self.agent.invoke(chat):
            response += message.content
            chat.add_assistant_message(message)

        if self.mediator:
            self.mediator.notify(
                sender=self,
                event="interaction_done",
                data={
                    "avatar_id": self.grader.id,
                    "avatar_name": self.grader.name,
                }
            )
        return response


class GraderFactory:
    """
    Factory to build a shared Kernel and produce sub-avatar instances from an Assembly.
    """

    @staticmethod
    def __build_kernel() -> sk.Kernel:
        """
        Build and return a shared Kernel for avatar interactions.
        """
        kernel = sk.Kernel()
        for service in AVAILABLE_MODELS:
            kernel.add_service(service)
        return kernel

    def create_graders(self, assembly: Assembly) -> List[AnswerGrader]:
        """
        Produce a list of ConcreteGrader objects from the provided Assembly.
        Assumes assembly.avatars is a list of Grader models.
        """
        return [AnswerGrader(grader=ad, kernel=self.__build_kernel()) for ad in assembly.agents]


class AnswerOrchestrator:
    """
    High-level class that merges SuperGrader and GraderFactory into a single interaction procedure.
    """

    def __init__(self) -> None:
        self.graders: List[AnswerGrader] = []

    async def __parallel_processing(self, question: Question, answer: Answer):  # pylint: disable=unused-private-member
        """
        Execute the 'interact' method of all graders in parallel.
        """

        async def interact_with_grader(grader):
            chat = ChatHistory()
            await grader.interact(question, answer, chat)

        return await asyncio.gather(*(interact_with_grader(grader) for grader in self.graders))

    async def __sequential_processing(self, question: Question, answer: Answer):  # pylint: disable=unused-private-member
        """
        Execute the 'interact' method of all graders sequentially.
        """
        answers = []
        for index, grader in enumerate(self.graders):
            chat = ChatHistory()
            answers.append({f"agent_{index}": await grader.interact(question, answer, chat)})
        return answers

    async def run_interaction(
            self,
            assembly_id: str,
            question: Question,
            answer: Answer,
            strategy: Literal["parallel", "sequential"] = "parallel") -> str:
        """
        1) Build a shared kernel.
        2) Instantiate a SuperGrader referencing that kernel.
        3) Fetch the Assembly from Cosmos DB.
        4) Create sub-avatars via GraderFactory.
        5) Register them in the SuperGrader.
        6) Let the SuperGrader orchestrate the interactions.
        7) Return the aggregated responses.
        """
        factory = GraderFactory()
        assembly = await self.fetch_assembly(assembly_id)
        self.graders = factory.create_graders(assembly)
        answers = getattr(self, f"__{strategy}_processing")(question, answer)
        return answers

    async def fetch_assembly(self, assembly_id: str) -> Assembly:
        """
        Helper function to fetch an Assembly document from Cosmos DB by its ID.
        Raises a ValueError if not found.
        """
        async with CosmosClient(COSMOS_ENDPOINT, DefaultAzureCredential()) as client:
            try:
                database = client.get_database_client(COSMOS_DB_NAME)
                await database.read()
            except exceptions.CosmosResourceNotFoundError as exc:
                raise ValueError(f"Database not found: {COSMOS_DB_NAME}") from exc

            container = database.get_container_client(COSMOS_ASSEMBLY_TABLE)
            try:
                item = await container.read_item(item=assembly_id, partition_key=assembly_id)
            except exceptions.CosmosResourceNotFoundError as exc:
                raise ValueError(f"Assembly not found: {assembly_id}") from exc
            return Assembly(**{"id": item["id"], "agents": item["avatars"], "topic_name": item["topic_name"]})
