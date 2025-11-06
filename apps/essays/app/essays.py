"""Essay evaluation orchestrator built on Microsoft Agent Framework."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

import jinja2

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from common.agents import AgentRegistry, AgentRunContext, AgentSpec
from common.config import get_settings

from app.schemas import Essay, Resource


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

    def __init__(self, registry: AgentRegistry, composer: PromptComposer, deployment: str) -> None:
        self._registry = registry
        self._composer = composer
        self._deployment = deployment

    async def evaluate(self, essay: Essay, resources: Iterable[Resource]) -> EssayEvaluationResult:
        prompt = self._composer.render(self.template_name, essay, resources)
        agent = self._registry.create(self._build_spec())
        context = AgentRunContext(agent)
        response = await context.run(prompt, temperature=0.2)
        verdict, strengths, improvements = self._parse_response(str(response.text))
        return EssayEvaluationResult(
            strategy=self.strategy_type(),
            verdict=verdict,
            strengths=strengths,
            improvements=improvements,
        )

    def strategy_type(self) -> EssayStrategyType:
        raise NotImplementedError

    def _build_spec(self) -> AgentSpec:
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

    def _build_spec(self) -> AgentSpec:
        instructions = (
            "You are an analytical writing coach. Provide evidence-based feedback on thesis strength, "
            "argument coherence, and use of references. Summarise in bullet form when possible."
        )
        return AgentSpec(
            name="analytical-reviewer",
            instructions=instructions,
            deployment=self._deployment,
            max_tokens=800,
        )


class NarrativeEssayStrategy(EssayEvaluationStrategy):
    """Strategy specialised for narrative or creative writing."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401
        return EssayStrategyType.NARRATIVE

    def _build_spec(self) -> AgentSpec:
        instructions = (
            "You are a creative writing editor. Focus feedback on voice, pacing, emotional impact, and "
            "consistency of narrative perspective. Highlight memorable lines and areas to tighten."
        )
        return AgentSpec(
            name="narrative-reviewer",
            instructions=instructions,
            deployment=self._deployment,
            max_tokens=800,
        )


class DefaultEssayStrategy(EssayEvaluationStrategy):
    """Fallback strategy used when no specialised routing is required."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401
        return EssayStrategyType.DEFAULT

    def _build_spec(self) -> AgentSpec:
        instructions = (
            "You evaluate student essays. Provide balanced feedback that covers structure, clarity, grammar, "
            "and alignment to the prompt. Include at least one actionable suggestion."
        )
        return AgentSpec(
            name="general-reviewer",
            instructions=instructions,
            deployment=self._deployment,
            max_tokens=600,
        )


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
        self._registry = AgentRegistry(settings.azure_ai.project_endpoint)
        self._cosmos_endpoint = settings.cosmos.endpoint
        self._database_name = settings.cosmos.database
        self._assembly_container = settings.cosmos.assembly_container
        self._credential = DefaultAzureCredential()
        self._strategies: dict[EssayStrategyType, EssayEvaluationStrategy] = {
            EssayStrategyType.ANALYTICAL: AnalyticalEssayStrategy(
                self._registry, self._composer, settings.azure_ai.reasoning_deployment
            ),
            EssayStrategyType.NARRATIVE: NarrativeEssayStrategy(
                self._registry, self._composer, settings.azure_ai.default_deployment
            ),
            EssayStrategyType.DEFAULT: DefaultEssayStrategy(
                self._registry, self._composer, settings.azure_ai.default_deployment
            ),
        }

    async def invoke(self, assembly_id: str, essay: Essay, resources: Iterable[Resource]) -> EssayEvaluationResult:
        await self._ensure_assembly_exists(assembly_id)
        strategy_type = self._resolver.resolve(essay, resources)
        strategy = self._strategies[strategy_type]
        return await strategy.evaluate(essay, resources)

    async def _ensure_assembly_exists(self, assembly_id: str) -> None:
        async with CosmosClient(self._cosmos_endpoint, self._credential) as client:
            database = client.get_database_client(self._database_name)
            try:
                await database.read()
            except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover - configuration error
                raise ValueError(f"Database not found: {self._database_name}") from exc

            container = database.get_container_client(self._assembly_container)
            try:
                await container.read_item(item=assembly_id, partition_key=assembly_id)
            except exceptions.CosmosResourceNotFoundError as exc:
                raise ValueError(f"Assembly not found: {assembly_id}") from exc
