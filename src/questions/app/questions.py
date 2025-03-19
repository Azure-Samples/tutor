"""
Module: questions

This module implements the orchestration of multiple avatar agents (graders) in parallel 
using Semantic Kernel and Azure OpenAI services. It provides the core components needed 
to configure, execute, and aggregate responses from multiple grader agents. 

Components:
  - Mediator: An abstract interface for mediator implementations that handle notifications 
    from sub-avatar agents.
  - GraderBase: An abstract base class defining the interface for grader agents capable of 
    interacting with prompts asynchronously.
  - AnswerGrader: A concrete grader that uses a ChatCompletionAgent to process prompts and 
    generate responses. It loads its configuration via Jinja2 templates.
  - GraderFactory: A factory for building a shared Semantic Kernel and creating AnswerGrader 
    instances from an Assembly document.
  - AnswerOrchestrator: A high-level orchestrator that fetches an Assembly document from 
    Cosmos DB, creates grader instances, and executes their interactions concurrently or 
    sequentially.

Usage:
    1. Ensure environment variables (e.g. COSMOS_QNA_NAME, COSMOS_ENDPOINT, COSMOS_ASSEMBLY_TABLE, 
       AZURE_MODEL_KEY, AZURE_MODEL_URL) are defined in a .env file placed at the root (two levels 
       above this module).
    2. Prepare an Assembly document in Cosmos DB which contains grader (avatar) configurations.
    3. Instantiate an AnswerOrchestrator and call its run_interaction method with an assembly_id, 
       question, and answer to obtain aggregated responses from all configured grader agents.
       
Dependencies:
    - semantic_kernel: Provides ChatCompletionAgent, ChatHistory, KernelArguments, etc.
    - jinja2: Used for templating of prompt instructions.
    - azure.cosmos and azure.identity: For Cosmos DB access and authentication.
    - dotenv: For environment variable loading.
    - asyncio: For asynchronous execution.

"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional, Literal, override
from dotenv import load_dotenv
import jinja2
import semantic_kernel as sk
import asyncio

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory, ChatMessageContent, AuthorRole
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_arguments import KernelArguments

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from app.schemas import Assembly, Grader, Question, Answer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

COSMOS_DB_NAME = os.getenv("COSMOS_QNA_NAME", "mydb")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://myendpoint.documents.azure.com:443/")
COSMOS_ASSEMBLY_TABLE = os.getenv("COSMOS_ASSEMBLY_TABLE", "assembly")
AZURE_MODEL_KEY = os.getenv("AZURE_MODEL_KEY", "")
AZURE_MODEL_URL = os.getenv("AZURE_MODEL_URL", "")
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
    Interface for mediator implementations.

    A mediator collects notifications from sub-avatar agents. Implementations of this
    interface should provide a way to handle notifications (e.g. logging or aggregating
    responses).
    """
    @abstractmethod
    def notify(self, sender: object, event: str, data: dict) -> None:
        """
        Handle a notification event from a sub-avatar.

        :param sender: The object sending the notification.
        :param event: A string indicating the event type.
        :param data: A dictionary containing any data associated with the event.
        """


class GraderBase(ABC):
    """
    Abstract base for an avatar (grader) that can interact with a prompt.

    This class defines the core interface for graders, including an asynchronous
    interaction method.
    """
    def __init__(self) -> None:
        self.mediator: Optional[Mediator] = None

    @abstractmethod
    async def interact(self) -> None:
        """
        Asynchronously perform interaction with a prompt.

        Implementations must provide their own logic to process a prompt and generate
        a response.
        """


class AnswerGrader(GraderBase):
    """
    A grader that interacts with a prompt using a ChatCompletionAgent.

    Loads its personality and instructions from its profile, renders the prompt via a
    Jinja2 template, and generates a response. Notifies a mediator when interaction is complete.
    """
    def __init__(self, grader: Grader, kernel: sk.Kernel) -> None:
        """
        Initialize an AnswerGrader.

        :param grader: The Grader configuration data (including id, name, metaprompt, model_id).
        :param kernel: A shared Semantic Kernel instance configured with services.
        """
        super().__init__()
        self.grader = grader
        self.kernel = kernel
        self.agent: ChatCompletionAgent
        self.__prepare()

    def __prepare(self):
        """
        Prepare the grader for interaction by configuring the ChatCompletionAgent.

        Renders the instruction settings from a Jinja2 template and retrieves the settings based on
        the grader's model_id. Then creates the ChatCompletionAgent instance.
        """
        instruction_template = JINJA_ENV.get_template("instruction.jinja")
        rendered_settings = instruction_template.render(
            instructions=self.grader.metaprompt,
        )
        settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id=self.grader.model_id)
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        self.agent = ChatCompletionAgent(
            kernel=self.kernel,
            name=self.grader.name,
            instructions=rendered_settings,
            arguments=KernelArguments(settings=settings),
        )

    @override
    async def interact(self, question: Question, answer: Answer, chat: ChatHistory) -> str:  # pylint: disable=arguments-differ
        """
        Interact with a provided question and answer using the ChatCompletionAgent.

        Renders the prompt using a Jinja2 template, sends it to the agent, accumulates the responses,
        adds messages to the provided ChatHistory, and notifies the mediator upon completion.

        :param question: The question object for the interaction.
        :param answer: The answer object associated with the question.
        :param chat: A ChatHistory instance for logging the conversation.
        :return: The aggregated response generated by the agent.
        """
        prompt_template = JINJA_ENV.get_template("correct.jinja")
        rendered_prompt = prompt_template.render(
            question=question,
            answer=answer
        )
        chat.add_message(ChatMessageContent(role=AuthorRole.USER, content=rendered_prompt))
        response = ""
        async for message in self.agent.invoke(chat):
            response += message.content
            chat.add_message(ChatMessageContent(role=AuthorRole.ASSISTANT, content=message.content))

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
    Factory for building a shared Semantic Kernel and creating AnswerGrader instances.

    Uses the provided Assembly object to create graders for each agent defined in the assembly.
    """
    @staticmethod
    def __build_kernel() -> sk.Kernel:
        """
        Build and return a shared Semantic Kernel.

        Adds each service in AVAILABLE_MODELS to the kernel.

        :return: A configured Semantic Kernel instance.
        """
        kernel = sk.Kernel()
        for service in AVAILABLE_MODELS:
            kernel.add_service(service)
        return kernel

    def create_graders(self, assembly: Assembly) -> List[AnswerGrader]:
        """
        Create a list of AnswerGrader instances from an Assembly.

        Assumes that assembly.agents is a list of Grader configuration models.

        :param assembly: The Assembly containing agent configurations.
        :return: A list of instantiated AnswerGrader objects.
        """
        return [AnswerGrader(grader=ad, kernel=self.__build_kernel()) for ad in assembly.agents]


class AnswerOrchestrator:
    """
    High-level orchestrator that merges grader management and interaction execution.

    Fetches assemblies from Cosmos DB, creates grader instances via GraderFactory, and executes
    interactions in either parallel or sequential mode.
    """
    def __init__(self) -> None:
        self.graders: List[AnswerGrader] = []

    async def _parallel_processing(self, question: Question, answer: Answer) -> List:
        """
        Execute the 'interact' method of all graders concurrently.

        :param question: The question to be processed.
        :param answer: The associated answer object.
        :return: A list of responses from all graders executed in parallel.
        """
        async def interact_with_grader(grader: AnswerGrader, chat: ChatHistory) -> str:
            return await grader.interact(question, answer, chat)

        chat = ChatHistory()
        return await asyncio.gather(*(interact_with_grader(grader, chat) for grader in self.graders))

    async def _sequential_processing(self, question: Question, answer: Answer) -> List:
        """
        Execute the 'interact' method of all graders sequentially.

        :param question: The question to be processed.
        :param answer: The corresponding answer object.
        :return: A list of dictionaries mapping grader identifiers to their responses.
        """
        answers = []
        for index, grader in enumerate(self.graders):
            chat = ChatHistory()
            result = await grader.interact(question, answer, chat)
            answers.append({f"agent_{index}": result})
        return answers

    async def run_interaction(
            self,
            assembly_id: str,
            question: Question,
            answer: Answer,
            strategy: Literal["parallel", "sequential"] = "parallel") -> str:
        """
        Orchestrate the grader interactions for a given assembly.

        This method performs the following steps:
          1) Builds a shared kernel.
          2) Creates AnswerGrader instances using GraderFactory.
          3) Fetches the Assembly document from Cosmos DB.
          4) Executes grader interactions using the specified strategy (parallel or sequential).
          5) Returns the aggregated responses.

        :param assembly_id: The ID of the Assembly in Cosmos DB.
        :param question: The question object to send to graders.
        :param answer: The answer object associated with the question.
        :param strategy: The processing strategy ("parallel" or "sequential").
        :return: The aggregated responses from all grader interactions.
        """
        factory = GraderFactory()
        assembly = await self.fetch_assembly(assembly_id)
        self.graders = factory.create_graders(assembly)
        answers = await getattr(self, f"_{strategy}_processing")(question, answer)
        return answers

    async def fetch_assembly(self, assembly_id: str) -> Assembly:
        """
        Fetch an Assembly document from Cosmos DB using its ID.

        Raises a ValueError if the database or assembly is not found.

        :param assembly_id: The ID of the assembly to fetch.
        :return: An Assembly object constructed from the retrieved document.
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