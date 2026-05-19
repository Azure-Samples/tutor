"""Essay evaluation orchestrator built on Foundry-native agents."""

from __future__ import annotations

import base64
import binascii
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from string import Template
from typing import Any

from azure.core.exceptions import AzureError
from azure.cosmos import exceptions
from pydantic import ValidationError
from pypdf.errors import PdfReadError
from tutor_lib.agents import (
    AgentAttachment,
    AgentInvocationRequest,
    AgentInvocationResult,
    AgentReference,
    FoundryAgentFacade,
)
from tutor_lib.cosmos import AssemblyRepository

from app.config import get_settings
from app.file_processing import (
    ALLOWED_PDF_TYPES,
    extract_pdf_text,
    extract_text_with_doc_intelligence,
)
from app.schemas import AgentRef, Assembly, Essay, Resource


def _is_legacy_only_agent_reference(agent_name: str | None, legacy_agent_id: str | None) -> bool:
    return bool(legacy_agent_id) and (not agent_name or agent_name == legacy_agent_id)


def _agent_ref_from_reference(reference: AgentReference, fallback: AgentRef) -> AgentRef:
    return AgentRef(
        agent_name=reference.agent_name,
        agent_version=reference.agent_version,
        legacy_agent_id=fallback.legacy_agent_id or reference.legacy_agent_id,
        role=fallback.role,
        deployment=fallback.deployment or reference.model_name or "",
    )


class EssayStrategyType(StrEnum):
    """Enumeration describing available evaluation strategies."""

    ENEM = "enem"
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
    """Compose editable prompt artifacts with service-owned Markdown builders."""

    def __init__(self, template_dir: Path) -> None:
        self._template_dir = template_dir

    def render(self, template_name: str, essay: Essay, resources: Iterable[Resource]) -> str:
        template_text = (self._template_dir / template_name).read_text(encoding="utf-8")
        template_values = _build_essay_prompt_values(essay, list(resources))
        # PEP 292 Template keeps prompt files to strict $slot substitution.
        return Template(template_text).substitute(template_values)


def _build_essay_prompt_values(essay: Essay, resources: Sequence[Resource]) -> dict[str, str]:
    return {
        "essay_theme": essay.theme or "N/A",
        "essay_topic": essay.topic,
        "essay_file_url": essay.file_url or "nenhum",
        "essay_content": _format_essay_content(essay),
        "resources": _format_resources(resources),
    }


def _format_essay_content(essay: Essay) -> str:
    if essay.content:
        return f"Conteúdo:\n{essay.content}"
    return (
        "Conteúdo: não fornecido em texto. Leia integralmente os recursos anexados "
        "(incluindo imagens) para extrair o texto do ensaio antes de avaliá-lo."
    )


def _format_resources(resources: Sequence[Resource]) -> str:
    return "\n".join(_format_resource(resource) for resource in resources)


def _format_resource(resource: Resource) -> str:
    detail = _format_resource_detail(resource)
    objectives = ", ".join(resource.objective)
    metadata = resource.metadata or "nenhum"
    return (
        f"- ID do critério: {resource.id}\n"
        f"  Objetivos: {objectives}\n"
        f"  URL de referência: {resource.url or 'nenhum'}\n"
        f"  Nome do arquivo: {resource.file_name or 'nenhum'}\n"
        f"  Tipo de conteúdo: {resource.content_type or 'texto'}\n"
        f"  Metadados: {metadata}\n"
        f"  {detail}"
    )


def _format_resource_detail(resource: Resource) -> str:
    if resource.content:
        return f"Detalhes: {resource.content}"
    if resource.content_type and resource.content_type.startswith("image/"):
        file_label = resource.file_name or resource.id
        return (
            "Detalhes: A redação está fornecida como imagem "
            f"(arquivo {file_label}). Extraia todo o texto dessa imagem usando "
            "visão antes de avaliar; não solicite conteúdo adicional ao usuário."
        )
    return "Detalhes: n/a"


class EssayEvaluationStrategy:
    """Base class for strategy implementations."""

    template_name = "correct.md"

    def __init__(self, agent_facade: FoundryAgentFacade, composer: PromptComposer) -> None:
        self._agent_facade = agent_facade
        self._composer = composer

    async def evaluate(
        self,
        agent: AgentRef,
        essay: Essay,
        resources: Iterable[Resource],
    ) -> EssayEvaluationResult:
        prepared_resources = list(resources)
        prompt = self._composer.render(self.template_name, essay, prepared_resources)
        attachments = self._build_image_attachments(prepared_resources)
        resource_ids = tuple(resource.id for resource in prepared_resources if resource.id)
        request = AgentInvocationRequest(
            agent=agent.to_agent_reference(),
            input=prompt,
            context={
                "essay_id": essay.id,
                "role": agent.role,
                "strategy": self.strategy_type().value,
                "resource_ids": list(resource_ids),
            },
            attachments=tuple(attachments),
            evidence_refs=resource_ids,
            store=False,
        )
        result: AgentInvocationResult = await self._agent_facade.invoke(request)
        response_text = result.output_text
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


class EnemEssayStrategy(EssayEvaluationStrategy):
    """Strategy specialised for ENEM competency-based evaluations."""

    def strategy_type(self) -> EssayStrategyType:  # noqa: D401
        return EssayStrategyType.ENEM


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

    ENEM_THEME_MARKERS: tuple[str, ...] = (
        "enem",
        "competencia",
        "competência",
        "redacao enem",
        "redação enem",
    )

    ENEM_OBJECTIVE_MARKERS: tuple[str, ...] = (
        "enem",
        "competencia",
        "competência",
    )

    def resolve(self, essay: Essay, resources: Iterable[Resource]) -> EssayStrategyType:
        theme = (essay.theme or "").lower()
        objectives = {obj.lower() for resource in resources for obj in resource.objective}
        if any(marker in theme for marker in self.ENEM_THEME_MARKERS):
            return EssayStrategyType.ENEM
        if any(
            marker in objective
            for objective in objectives
            for marker in self.ENEM_OBJECTIVE_MARKERS
        ):
            return EssayStrategyType.ENEM
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
        self._agent_facade = FoundryAgentFacade(settings.azure_ai.project_endpoint)  # pylint: disable=no-member
        self._assembly_repository = AssemblyRepository(settings.cosmos)
        self._strategies: dict[EssayStrategyType, EssayEvaluationStrategy] = {
            EssayStrategyType.ENEM: EnemEssayStrategy(
                self._agent_facade, self._composer
            ),
            EssayStrategyType.ANALYTICAL: AnalyticalEssayStrategy(
                self._agent_facade, self._composer
            ),
            EssayStrategyType.NARRATIVE: NarrativeEssayStrategy(
                self._agent_facade, self._composer
            ),
            EssayStrategyType.DEFAULT: DefaultEssayStrategy(
                self._agent_facade, self._composer
            ),
        }

    async def invoke(self, assembly_id: str, essay: Essay, resources: Iterable[Resource]) -> EssayEvaluationResult:
        prepared_resources = self._prepare_resources(list(resources))
        assembly = await self._load_assembly(assembly_id, fallback_essay_id=essay.id)
        strategy_type = self._resolver.resolve(essay, prepared_resources)
        strategy = self._strategies[strategy_type]
        agent = self._select_agent(assembly, strategy_type)
        return await strategy.evaluate(agent, essay, prepared_resources)

    async def _load_assembly(self, assembly_id: str, fallback_essay_id: str | None = None) -> Assembly:
        try:
            record = await self._assembly_repository.get_by_id(assembly_id)
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
        return Assembly(id=swarm_id, topic_name=topic, agents=agents, essay_id=essay_id)

    async def _hydrate_agents(self, items: Sequence[Any]) -> list[AgentRef]:
        provisioned: list[AgentRef] = []
        for entry in items:
            if isinstance(entry, dict):
                try:
                    agent_ref = AgentRef.model_validate(entry)
                except ValidationError:
                    continue
                provisioned.append(await self._resolve_legacy_agent_ref(agent_ref))
                continue
            if isinstance(entry, str):
                agent_ref = AgentRef.model_validate(entry)
                provisioned.append(await self._resolve_legacy_agent_ref(agent_ref))
                continue
        return provisioned

    async def _resolve_legacy_agent_ref(self, agent_ref: AgentRef) -> AgentRef:
        legacy_agent_id = agent_ref.legacy_agent_id
        if not legacy_agent_id or not _is_legacy_only_agent_reference(
            agent_ref.agent_name,
            legacy_agent_id,
        ):
            return agent_ref

        get_remote_agent = getattr(self._agent_facade, "get_agent", None)
        if not callable(get_remote_agent):
            return agent_ref

        try:
            reference = await get_remote_agent(legacy_agent_id)
        except (AttributeError, AzureError, RuntimeError, TypeError, ValueError):
            return agent_ref
        return _agent_ref_from_reference(reference, agent_ref)

    def _select_agent(self, assembly: Assembly, strategy_type: EssayStrategyType) -> AgentRef:
        if not assembly.agents:
            raise ValueError(f"Assembly '{assembly.id}' does not contain agents")

        role_map = {
            EssayStrategyType.ENEM: "enem",
            EssayStrategyType.ANALYTICAL: "analytical",
            EssayStrategyType.NARRATIVE: "narrative",
            EssayStrategyType.DEFAULT: "default",
        }
        target_role = role_map.get(strategy_type, "default")
        for agent in assembly.agents:
            if agent.role == target_role:
                return agent
        return assembly.agents[0]

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
                    extracted = extract_text_with_doc_intelligence(payload, resource.content_type) or extract_pdf_text(
                        payload
                    )
                except (binascii.Error, PdfReadError, ValueError):  # pragma: no cover - corrupted payloads are skipped
                    extracted = None
                if extracted:
                    updated = resource.model_copy(update={"content": extracted})
            prepared.append(updated)
        return prepared
