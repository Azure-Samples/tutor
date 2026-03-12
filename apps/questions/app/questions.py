"""Question evaluation orchestrator backed by the state pattern."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Protocol

import jinja2

from azure.cosmos import exceptions

from tutor_lib.agents import FoundryAgentService
from tutor_lib.config import get_settings
from tutor_lib.cosmos import AssemblyRepository

from app.interfaces import DimensionEvaluation, QuestionEvaluationResult, QuestionEvaluationStatus
from app.schemas import Answer, Assembly, Grader, Question


class QuestionState(Protocol):
    async def evaluate(self, context: "QuestionStateMachine") -> QuestionEvaluationResult: ...


class PendingState:
    async def evaluate(self, context: "QuestionStateMachine") -> QuestionEvaluationResult:
        context.transition(EvaluatingState())
        return await context.evaluate()


class EvaluatingState:
    async def evaluate(self, context: "QuestionStateMachine") -> QuestionEvaluationResult:
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

    async def _run_dimension(self, context: "QuestionStateMachine", grader: Grader) -> DimensionEvaluation:
        prompt = context.prompt_composer.render(
            "correct.jinja",
            question=context.question,
            answer=context.answer,
            dimension=grader.dimension,
        )
        raw_text = await context.agent_service.run_agent(grader.agent_id, prompt)
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

    async def evaluate(self, _: "QuestionStateMachine") -> QuestionEvaluationResult:
        return self._result


class PromptComposer:
    def __init__(self, template_dir: Path) -> None:
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))

    def render(self, template: str, *, question: Question, answer: Answer, dimension: str) -> str:
        template_obj = self._env.get_template(template)
        return template_obj.render(
            question=question.model_dump(),
            answer=answer.model_dump(),
            dimension=dimension,
        )


class QuestionStateMachine:
    def __init__(self, assembly_id: str, question: Question, answer: Answer) -> None:
        settings = get_settings()
        self._state: QuestionState = PendingState()
        self._settings = settings
        self._assembly_id = assembly_id
        self.question = question
        self.answer = answer
        self.agent_service = FoundryAgentService(settings.azure_ai.project_endpoint)
        self._assembly_repository = AssemblyRepository(settings.cosmos)
        self.prompt_composer = PromptComposer(Path(__file__).parent / "prompts")
        self.graders: list[Grader] = []
        self._result: QuestionEvaluationResult | None = None

    def transition(self, state: QuestionState) -> None:
        self._state = state

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
        graders: list[Grader] = []
        for entry in raw_agents:
            if isinstance(entry, dict):
                if "agent_id" in entry:
                    graders.append(Grader.model_validate(entry))
                elif "id" in entry:
                    graders.append(Grader(
                        agent_id=str(entry["id"]),
                        dimension=entry.get("dimension", ""),
                        deployment=entry.get("deployment", ""),
                    ))
        if not graders:
            raise ValueError(f"Assembly '{self._assembly_id}' has no graders")
        self.graders = graders


async def evaluate_question(assembly_id: str, question: Question, answer: Answer) -> QuestionEvaluationResult:
    machine = QuestionStateMachine(assembly_id, question, answer)
    return await machine.evaluate()
