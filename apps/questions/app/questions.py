"""Question evaluation orchestrator backed by the state pattern."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Protocol

import jinja2

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from tutor_lib.agents import AgentRegistry, AgentRunContext, AgentSpec
from tutor_lib.config import get_settings

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
        agent = context.registry.create(
            AgentSpec(
                name=f"question-{grader.dimension}",
                instructions=grader.instructions,
                deployment=grader.deployment,
                max_tokens=600,
                temperature=0.1,
            )
        )
        run_context = AgentRunContext(agent)
        response = await run_context.run(prompt)
        raw_text = getattr(response, "text", "") or ""
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
        self.registry = AgentRegistry(settings.azure_ai.project_endpoint)
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
        async with DefaultAzureCredential() as credential:
            async with CosmosClient(self._settings.cosmos.endpoint, credential) as client:
                database = client.get_database_client(self._settings.cosmos.database)
                try:
                    await database.read()
                except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover
                    raise ValueError(f"Database not found: {self._settings.cosmos.database}") from exc
                container = database.get_container_client(self._settings.cosmos.assembly_container)
                try:
                    item = await container.read_item(item=self._assembly_id, partition_key=self._assembly_id)
                except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover
                    raise ValueError(f"Assembly not found: {self._assembly_id}") from exc
                payload = {**item, "agents": item.get("agents") or item.get("avatars", [])}
                if "topic_name" not in payload and "topic" in item:
                    payload["topic_name"] = item["topic"]
                assembly = Assembly(**payload)
                self.graders = assembly.agents


async def evaluate_question(assembly_id: str, question: Question, answer: Answer) -> QuestionEvaluationResult:
    machine = QuestionStateMachine(assembly_id, question, answer)
    return await machine.evaluate()
