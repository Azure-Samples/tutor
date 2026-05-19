"""Question evaluation orchestrator backed by the state pattern."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from pathlib import Path
from string import Template
from typing import Protocol

from azure.core.exceptions import AzureError
from azure.cosmos import exceptions
from pydantic import ValidationError
from tutor_lib.agents import (
    AgentInvocationRequest,
    AgentInvocationResult,
    AgentReference,
    FoundryAgentFacade,
)
from tutor_lib.config import get_settings
from tutor_lib.cosmos import AssemblyRepository

from app.interfaces import DimensionEvaluation, QuestionEvaluationResult, QuestionEvaluationStatus
from app.schemas import Answer, Grader, Question


def _is_legacy_only_agent_reference(agent_name: str | None, legacy_agent_id: str | None) -> bool:
    return bool(legacy_agent_id) and (not agent_name or agent_name == legacy_agent_id)


def _grader_from_agent_reference(reference: AgentReference, fallback: Grader) -> Grader:
    return Grader(
        agent_name=reference.agent_name,
        agent_version=reference.agent_version,
        legacy_agent_id=fallback.legacy_agent_id or reference.legacy_agent_id,
        dimension=fallback.dimension,
        deployment=fallback.deployment or reference.model_name or "",
    )


class QuestionState(Protocol):
    async def evaluate(self, context: QuestionStateMachine) -> QuestionEvaluationResult: ...


class PendingState:
    async def evaluate(self, context: QuestionStateMachine) -> QuestionEvaluationResult:
        context.transition(EvaluatingState())
        return await context.evaluate()


class EvaluatingState:
    async def evaluate(self, context: QuestionStateMachine) -> QuestionEvaluationResult:
        await context.ensure_assembly()
        tasks = [self._run_dimension(context, grader) for grader in context.graders]
        dimension_results = await asyncio.gather(*tasks)
        overall_summary = "\n".join(d.verdict for d in dimension_results)
        result = QuestionEvaluationResult(
            question_id=context.question.id,
            status=QuestionEvaluationStatus.COMPLETED,
            overall=overall_summary,
            dimensions=list(dimension_results),
        )
        context.transition(CompletedState(result))
        return result

    async def _run_dimension(self, context: QuestionStateMachine, grader: Grader) -> DimensionEvaluation:
        prompt = context.prompt_composer.render(
            "correct.md",
            question=context.question,
            answer=context.answer,
            dimension=grader.dimension,
        )
        request = AgentInvocationRequest(
            agent=grader.to_agent_reference(),
            input=prompt,
            context={
                "assembly_id": context.assembly_id,
                "question_id": context.question.id,
                "answer_id": context.answer.id,
                "dimension": grader.dimension,
            },
            store=False,
        )
        result: AgentInvocationResult = await context.agent_facade.invoke(request)
        raw_text = result.output_text
        notes = [line.strip() for line in raw_text.split("\n") if line.strip()]
        verdict = notes[0] if notes else "No verdict returned"
        confidence = self._infer_confidence(notes)
        return DimensionEvaluation(
            dimension=grader.dimension,
            verdict=verdict,
            confidence=confidence,
            notes=notes,
        )

    def _infer_confidence(self, notes: Iterable[str]) -> float:
        joined = " ".join(notes).lower()
        if "high confidence" in joined:
            return 0.9
        if "low confidence" in joined:
            return 0.4
        return 0.7


class CompletedState:
    def __init__(self, result: QuestionEvaluationResult) -> None:
        self._result = result

    async def evaluate(self, _: QuestionStateMachine) -> QuestionEvaluationResult:
        return self._result


class PromptComposer:
    """Compose question prompts from plain text slots and typed inputs."""

    def __init__(self, template_dir: Path) -> None:
        self._template_dir = template_dir

    def render(self, template: str, *, question: Question, answer: Answer, dimension: str) -> str:
        template_text = (self._template_dir / template).read_text(encoding="utf-8")
        # PEP 292 Template keeps prompt files to strict $slot substitution.
        return Template(template_text).substitute(
            {
                "question_topic": question.topic,
                "question_text": question.question,
                "question_explanation": _format_question_explanation(question),
                "answer_text": answer.text,
                "dimension": dimension,
            }
        )


def _format_question_explanation(question: Question) -> str:
    if question.explanation is None:
        return "None"
    return question.explanation


class QuestionStateMachine:
    def __init__(self, assembly_id: str, question: Question, answer: Answer) -> None:
        settings = get_settings()
        self._state: QuestionState = PendingState()
        self._settings = settings
        self._assembly_id = assembly_id
        self.question = question
        self.answer = answer
        self.agent_facade = FoundryAgentFacade(settings.azure_ai.project_endpoint)
        self._assembly_repository = AssemblyRepository(settings.cosmos)
        self.prompt_composer = PromptComposer(Path(__file__).parent / "prompts")
        self.graders: list[Grader] = []
        self._result: QuestionEvaluationResult | None = None

    def transition(self, state: QuestionState) -> None:
        self._state = state

    @property
    def assembly_id(self) -> str:
        return self._assembly_id

    async def evaluate(self) -> QuestionEvaluationResult:
        self._result = await self._state.evaluate(self)
        return self._result

    async def ensure_assembly(self) -> None:
        if self.graders:
            return
        try:
            item = await self._assembly_repository.get_by_id(self._assembly_id)
        except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover
            raise ValueError(f"Assembly not found: {self._assembly_id}") from exc

        raw_agents = item.get("agents") or item.get("avatars", [])
        if isinstance(raw_agents, (dict, str)):
            raw_agents = [raw_agents]
        graders: list[Grader] = []
        for entry in raw_agents:
            try:
                grader = Grader.model_validate(entry)
            except ValidationError:
                continue
            graders.append(await self._resolve_legacy_grader(grader))
        if not graders:
            raise ValueError(f"Assembly '{self._assembly_id}' has no graders")
        self.graders = graders

    async def _resolve_legacy_grader(self, grader: Grader) -> Grader:
        legacy_agent_id = grader.legacy_agent_id
        if not legacy_agent_id or not _is_legacy_only_agent_reference(
            grader.agent_name,
            legacy_agent_id,
        ):
            return grader

        get_remote_agent = getattr(self.agent_facade, "get_agent", None)
        if not callable(get_remote_agent):
            return grader

        try:
            reference = await get_remote_agent(legacy_agent_id)
        except (AttributeError, AzureError, RuntimeError, TypeError, ValueError):
            return grader
        return _grader_from_agent_reference(reference, grader)


async def evaluate_question(assembly_id: str, question: Question, answer: Answer) -> QuestionEvaluationResult:
    machine = QuestionStateMachine(assembly_id, question, answer)
    return await machine.evaluate()
