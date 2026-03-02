"""Core orchestration logic for the upskilling service."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

import jinja2

from tutor_lib.agents import AgentRegistry, AgentRunContext, AgentSpec
from tutor_lib.config import get_settings

from .schemas import AgentFeedback, ParagraphEvaluation, PlanParagraph, PlanRequest


@dataclass(slots=True)
class PlanContext:
    """Immutable state shared across visitor evaluations."""

    timeframe: str
    topic: str
    class_id: str
    performance_history: List[dict]


@dataclass(slots=True)
class PlanParagraphElement:
    """Wrapper around the paragraph to comply with the visitor contract."""

    index: int
    paragraph: PlanParagraph
    context: PlanContext

    async def accept(self, visitor: "PlanAgentVisitor") -> AgentFeedback:
        return await visitor.visit(self)


class PlanAgentVisitor:
    """Base visitor capable of evaluating a paragraph with an Azure AI agent."""

    agent_name: str
    template_name: str

    def __init__(
        self,
        composer: "PromptComposer",
        registry: AgentRegistry,
        instructions: str,
        deployment: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._composer = composer
        agent = registry.create(
            AgentSpec(
                name=self.agent_name,
                instructions=instructions,
                deployment=deployment,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
        self._runner = AgentRunContext(agent)

    async def visit(self, element: PlanParagraphElement) -> AgentFeedback:
        prompt = self._composer.render(
            self.template_name,
            paragraph=element.paragraph.model_dump(),
            context={
                "timeframe": element.context.timeframe,
                "topic": element.context.topic,
                "class_id": element.context.class_id,
            },
            performance_history=element.context.performance_history,
        )
        response = await self._runner.run(prompt)
        text = _extract_text(response)
        verdict, strengths, improvements = _parse_feedback(text)
        return AgentFeedback(
            agent=self.agent_name,
            verdict=verdict,
            strengths=strengths,
            improvements=improvements,
        )


class PerformanceInsightVisitor(PlanAgentVisitor):
    agent_name = "performance-analyst"
    template_name = "performance.jinja"


class ContentComplexityVisitor(PlanAgentVisitor):
    agent_name = "content-curator"
    template_name = "content_complexity.jinja"


class GuidanceCoachVisitor(PlanAgentVisitor):
    agent_name = "guidance-coach"
    template_name = "guidance.jinja"


class PromptComposer:
    """Simple Jinja template wrapper for prompt rendering."""

    def __init__(self, template_dir: Path) -> None:
        loader = jinja2.FileSystemLoader(str(template_dir))
        self._env = jinja2.Environment(loader=loader, autoescape=False, trim_blocks=True, lstrip_blocks=True)

    def render(self, template_name: str, **context) -> str:
        return self._env.get_template(template_name).render(**context)


class PlanEvaluationIterator:
    """Async iterator that walks through plan paragraphs and applies all visitors."""

    def __init__(self, plan: PlanRequest, visitors: Iterable[PlanAgentVisitor], context: PlanContext) -> None:
        self._plan = plan
        self._visitors = list(visitors)
        self._context = context
        self._index = 0

    def __aiter__(self) -> "PlanEvaluationIterator":
        return self

    async def __anext__(self) -> ParagraphEvaluation:
        if self._index >= len(self._plan.paragraphs):
            raise StopAsyncIteration

        paragraph = self._plan.paragraphs[self._index]
        element = PlanParagraphElement(self._index, paragraph, self._context)
        feedback: List[AgentFeedback] = []
        for visitor in self._visitors:
            feedback.append(await element.accept(visitor))

        evaluation = ParagraphEvaluation(
            paragraph_index=self._index,
            title=paragraph.title,
            feedback=feedback,
        )
        self._index += 1
        return evaluation


class PlanEvaluationIterable:
    """Factory that returns a fresh iterator for each evaluation run."""

    def __init__(self, plan: PlanRequest, visitors: Iterable[PlanAgentVisitor], context: PlanContext) -> None:
        self._plan = plan
        self._visitors = list(visitors)
        self._context = context

    def __aiter__(self) -> PlanEvaluationIterator:
        return PlanEvaluationIterator(self._plan, self._visitors, self._context)


class PlanEvaluationOrchestrator:
    """High level orchestration entry-point used by the API layer."""

    def __init__(self, *, visitors: Iterable[PlanAgentVisitor]) -> None:
        self._visitors = list(visitors)

    async def evaluate(self, request: PlanRequest) -> List[ParagraphEvaluation]:
        context = PlanContext(
            timeframe=request.timeframe,
            topic=request.topic,
            class_id=request.class_id,
            performance_history=[snapshot.model_dump() for snapshot in request.performance_history],
        )
        iterable = PlanEvaluationIterable(request, self._visitors, context)
        evaluations: List[ParagraphEvaluation] = []
        async for evaluation in iterable:
            evaluations.append(evaluation)
        return evaluations


def _parse_feedback(text: str) -> tuple[str, List[str], List[str]]:
    verdict = text.strip()
    strengths: List[str] = []
    improvements: List[str] = []

    sections = [section.strip() for section in text.split("\n\n") if section.strip()]
    for section in sections:
        header, _, body = section.partition(":")
        normalized = header.lower()
        if normalized.startswith("strength"):
            strengths.append(body.strip() or "No strengths explicitly listed.")
        elif normalized.startswith("improvement") or normalized.startswith("gap"):
            improvements.append(body.strip() or "No improvements explicitly listed.")
    if not strengths:
        strengths = ["No specific strengths captured."]
    if not improvements:
        improvements = ["No improvement opportunities captured."]
    if sections:
        verdict = sections[0]
    return verdict, strengths, improvements


def _extract_text(response: object) -> str:
    maybe_text = getattr(response, "text", None)
    if isinstance(maybe_text, str) and maybe_text.strip():
        return maybe_text
    content = getattr(response, "content", None)
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts) if parts else "No response returned."
    return "No response returned."


@lru_cache(maxsize=1)
def build_orchestrator() -> PlanEvaluationOrchestrator:
    settings = get_settings()
    registry = AgentRegistry(settings.azure_ai.project_endpoint)
    template_dir = Path(__file__).parent / "prompts"
    composer = PromptComposer(template_dir)

    performance_instructions = (
        "You coach professors by analysing historical performance data."
        " Highlight trends, skills to reinforce, and gaps to close."
    )
    content_instructions = (
        "You assess the rigor and scaffolding of the planned content."
        " Balance challenge and accessibility for the students described."
    )
    guidance_instructions = (
        "You mentor professors while they write. Provide actionable, encouraging feedback"
        " for each paragraph they author, including pacing, differentiation, and assessment ideas."
    )
    deployment_default = settings.azure_ai.default_deployment
    deployment_reasoning = settings.azure_ai.reasoning_deployment

    visitors = [
        PerformanceInsightVisitor(composer, registry, performance_instructions, deployment_reasoning, temperature=0.2, max_tokens=800),
        ContentComplexityVisitor(composer, registry, content_instructions, deployment_default, temperature=0.3, max_tokens=700),
        GuidanceCoachVisitor(composer, registry, guidance_instructions, deployment_default, temperature=0.4, max_tokens=700),
    ]
    return PlanEvaluationOrchestrator(visitors=visitors)
