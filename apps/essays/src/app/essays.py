"""Essay evaluation orchestrator built on Microsoft Agent Framework."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Sequence

import jinja2

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from app.agents.clients import AgentAttachment, FoundryAgentService
from app.config import get_settings
from app.file_processing import ALLOWED_PDF_TYPES, extract_pdf_text
from app.schemas import Essay, ProvisionedAgent, Resource, Swarm

try:
    from pypdf.errors import PdfReadError  # type: ignore[import]
except ImportError:  # pragma: no cover - older PyPDF versions expose errors differently
    PdfReadError = ValueError  # type: ignore[assignment]


class EssayStrategyType(str, Enum):
    """Enumeration describing available evaluation strategies."""

    ANALYTICAL = "analytical"
    NARRATIVE = "narrative"
    DEFAULT = "default"


@dataclass(slots=True)
class EssayEvaluationResult:
    """Container for the structured response returned to the API layer."""

    strategy: EssayStrategyType
    verdict: str
    strengths: list[str]
    improvements: list[str]


class PromptComposer:
    """Render Jinja prompts using the essay and its supporting resources."""

    def __init__(self, template_dir: Path) -> None:
        loader = jinja2.FileSystemLoader(str(template_dir))
        self._env = jinja2.Environment(loader=loader, autoescape=False)

    def render(self, template_name: str, essay: Essay, resources: Iterable[Resource]) -> str:
        template = self._env.get_template(template_name)
        return template.render(essay=essay.model_dump(), resources=[r.model_dump() for r in resources])


class EssayEvaluationStrategy:
    """Base class for strategy implementations."""

    template_name = "correct.jinja"

    def __init__(self, agent_service: FoundryAgentService, composer: PromptComposer) -> None:
        self._agent_service = agent_service
        self._composer = composer

    async def evaluate(
        self,
        agent: ProvisionedAgent,
        essay: Essay,
        resources: Iterable[Resource],
    ) -> EssayEvaluationResult:
        prompt = self._composer.render(self.template_name, essay, resources)
        attachments = self._build_image_attachments(resources)
        response_text = await self._agent_service.run_agent(agent.id, prompt, attachments=attachments)
        verdict, strengths, improvements = self._parse_response(response_text)
        return EssayEvaluationResult(
            strategy=self.strategy_type(),
            verdict=verdict,
            strengths=strengths,
            improvements=improvements,
        )

    def _build_image_attachments(self, resources: Iterable[Resource]) -> list[AgentAttachment]:
        attachments: list[AgentAttachment] = []
        for resource in resources:
            encoded = resource.encoded_content
            content_type = resource.content_type
            if not encoded or not content_type or not content_type.lower().startswith("image/"):
                continue
            try:
                payload = base64.b64decode(encoded)
            except binascii.Error:  # pragma: no cover - invalid payloads are skipped
                continue
            file_name = resource.file_name or f"{resource.id or 'resource'}.bin"
            attachments.append(
                AgentAttachment(
                    file_name=file_name,
                    content_type=content_type,
                    payload=payload,
                )
            )
        return attachments

    def strategy_type(self) -> EssayStrategyType:
        raise NotImplementedError

    def _parse_response(self, text: str) -> tuple[str, list[str], list[str]]:
        """Parse the LLM response into the structured schema we surface to clients."""

        strengths: list[str] = []
        improvements: list[str] = []
        verdict = text.strip()
        sections = text.split("\n\n")
        for section in sections:
            header, _, body = section.partition(":")
            normalized = header.strip().lower()
            if normalized.startswith("strength"):
                strengths.append(body.strip())
            elif normalized.startswith("improvement"):
                improvements.append(body.strip())
        return verdict, strengths or ["No strengths identified"], improvements or ["No improvements suggested"]


class AnalyticalEssayStrategy(EssayEvaluationStrategy):
    """Strategy specialised for analytical essays."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401 - short override
        return EssayStrategyType.ANALYTICAL


class NarrativeEssayStrategy(EssayEvaluationStrategy):
    """Strategy specialised for narrative or creative writing."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401
        return EssayStrategyType.NARRATIVE


class DefaultEssayStrategy(EssayEvaluationStrategy):
    """Fallback strategy used when no specialised routing is required."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401
        return EssayStrategyType.DEFAULT


class StrategyResolver:
    """Decide which evaluation strategy to apply for a given essay."""

    def resolve(self, essay: Essay, resources: Iterable[Resource]) -> EssayStrategyType:
        objectives = {obj.lower() for resource in resources for obj in resource.objective}
        if essay.theme and "analytical" in essay.theme.lower():
            return EssayStrategyType.ANALYTICAL
        if any("creativ" in obj for obj in objectives):
            return EssayStrategyType.NARRATIVE
        return EssayStrategyType.DEFAULT


class EssayOrchestrator:
    """Coordinate agent execution using the strategy pattern."""

    def __init__(self) -> None:
        settings = get_settings()
        self._resolver = StrategyResolver()
        prompt_dir = Path(__file__).parent / "prompts"
        self._composer = PromptComposer(prompt_dir)
        self._agent_service = FoundryAgentService(settings.azure_ai.project_endpoint)  # pylint: disable=no-member
        self._cosmos_endpoint = settings.cosmos.endpoint  # pylint: disable=no-member
        self._database_name = settings.cosmos.database  # pylint: disable=no-member
        self._assembly_container = settings.cosmos.assembly_container  # pylint: disable=no-member
        self._credential = DefaultAzureCredential()
        self._strategies: dict[EssayStrategyType, EssayEvaluationStrategy] = {
            EssayStrategyType.ANALYTICAL: AnalyticalEssayStrategy(
                self._agent_service, self._composer
            ),
            EssayStrategyType.NARRATIVE: NarrativeEssayStrategy(
                self._agent_service, self._composer
            ),
            EssayStrategyType.DEFAULT: DefaultEssayStrategy(
                self._agent_service, self._composer
            ),
        }

    async def invoke(self, assembly_id: str, essay: Essay, resources: Iterable[Resource]) -> EssayEvaluationResult:
        prepared_resources = self._prepare_resources(list(resources))
        swarm = await self._load_swarm(assembly_id, fallback_essay_id=essay.id)
        strategy_type = self._resolver.resolve(essay, prepared_resources)
        strategy = self._strategies[strategy_type]
        agent = self._select_agent(swarm, strategy_type)
        return await strategy.evaluate(agent, essay, prepared_resources)

    async def _load_swarm(self, assembly_id: str, fallback_essay_id: str | None = None) -> Swarm:
        async with CosmosClient(self._cosmos_endpoint, self._credential) as client:
            database = client.get_database_client(self._database_name)
            try:
                await database.read()
            except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover - configuration error
                raise ValueError(f"Database not found: {self._database_name}") from exc

            container = database.get_container_client(self._assembly_container)
            try:
                record = await container.read_item(item=assembly_id, partition_key=assembly_id)
            except exceptions.CosmosResourceNotFoundError as exc:
                raise ValueError(f"Assembly not found: {assembly_id}") from exc
        agents = await self._hydrate_agents(record.get("agents", []))
        if not agents:
            raise ValueError(f"Assembly '{assembly_id}' is missing provisioned agents")
        topic = record.get("topic_name") or record.get("topicName") or "Essay Evaluation"
        swarm_id = record.get("id") or assembly_id
        essay_id = (
            record.get("essay_id")
            or record.get("essayId")
            or record.get("essayID")
            or fallback_essay_id
        )
        if not essay_id:
            raise ValueError(f"Assembly '{assembly_id}' did not include an essay identifier")
        return Swarm(id=swarm_id, topic_name=topic, agents=agents, essay_id=essay_id)

    async def _hydrate_agents(self, items: Sequence[Any]) -> list[ProvisionedAgent]:
        provisioned: list[ProvisionedAgent] = []
        for entry in items:
            if isinstance(entry, dict):
                provisioned.append(ProvisionedAgent.model_validate(entry))
                continue
            if isinstance(entry, str):
                remote = await self._agent_service.get_agent(entry)
                provisioned.append(self._materialize_agent(remote))
                continue
        return provisioned

    def _materialize_agent(self, remote: Any) -> ProvisionedAgent:
        agent_id = getattr(remote, "id", None)
        if not agent_id:
            raise ValueError("Azure AI agent response did not include an id")
        name = getattr(remote, "name", agent_id)
        instructions = getattr(remote, "instructions", "")
        deployment = (
            getattr(remote, "model", None)
            or getattr(remote, "model_id", None)
            or getattr(remote, "deployment_name", None)
            or ""
        )
        temperature = getattr(remote, "temperature", None)
        return ProvisionedAgent(
            id=agent_id,
            name=name,
            instructions=instructions,
            deployment=deployment,
            temperature=temperature,
        )

    def _select_agent(self, swarm: Swarm, strategy_type: EssayStrategyType) -> ProvisionedAgent:
        if not swarm.agents:
            raise ValueError(f"Swarm '{swarm.id}' does not contain agents")

        keywords = {
            EssayStrategyType.ANALYTICAL: ["analytic", "analysis", "analytical"],
            EssayStrategyType.NARRATIVE: ["narrative", "creative", "story"],
            EssayStrategyType.DEFAULT: ["general", "default", "review"],
        }
        candidates = keywords.get(strategy_type, [])
        for agent in swarm.agents:
            haystack = f"{agent.name} {agent.instructions}".lower()
            if any(keyword in haystack for keyword in candidates):
                return agent
        return swarm.agents[0]

    def _prepare_resources(self, resources: Iterable[Resource]) -> list[Resource]:
        prepared: list[Resource] = []
        for resource in resources:
            updated = resource
            if (
                resource.content_type in ALLOWED_PDF_TYPES
                and not resource.content
                and resource.encoded_content
            ):
                try:
                    payload = base64.b64decode(resource.encoded_content)
                    extracted = extract_pdf_text(payload)
                except (binascii.Error, PdfReadError, ValueError):  # pragma: no cover - corrupted payloads are skipped
                    extracted = None
                if extracted:
                    updated = resource.model_copy(update={"content": extracted})
            prepared.append(updated)
        return prepared
