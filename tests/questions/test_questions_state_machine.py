import pytest

from questions.app.questions import (
    QuestionEvaluationStatus,
    QuestionStateMachine,
    evaluate_question,
)
from questions.app.schemas import Answer, Grader, Question


@pytest.fixture(autouse=True)
def _configure_environment(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("COSMOS_QUESTION_TABLE", "questions")
    monkeypatch.setenv("COSMOS_ANSWER_TABLE", "answers")
    monkeypatch.setenv("COSMOS_GRADER_TABLE", "graders")
    monkeypatch.setenv("COSMOS_ASSEMBLY_TABLE", "assemblies")


class _StubFoundryAgentService:
    """Stub that returns a fixed text response for any agent invocation."""
    response_text = "Strong verdict with high confidence\nHigh confidence justification"

    def __init__(self, *_args, **_kwargs):
        self.calls: list[tuple[str, str]] = []

    async def run_agent(self, agent_id: str, prompt: str, **kwargs) -> str:
        self.calls.append((agent_id, prompt))
        return self.response_text


@pytest.mark.asyncio
async def test_evaluate_question_returns_completed(monkeypatch):
    monkeypatch.setattr("questions.app.questions.FoundryAgentService", _StubFoundryAgentService)

    async def _fake_ensure(self):
        self.graders = [
            Grader(
                agent_id="grader-1",
                deployment="fake-deployment",
                dimension="accuracy",
            )
        ]

    monkeypatch.setattr(QuestionStateMachine, "ensure_assembly", _fake_ensure)

    result = await evaluate_question(
        assembly_id="assembly-123",
        question=Question(id="q1", topic="Math", question="2+2", explanation=None),
        answer=Answer(id="a1", text="4", question_id="q1", respondent="Student"),
    )

    assert result.status is QuestionEvaluationStatus.COMPLETED
    assert result.overall.startswith("Strong verdict")
    assert len(result.dimensions) == 1
    dim = result.dimensions[0]
    assert dim.dimension == "accuracy"
    assert dim.confidence == pytest.approx(0.9)
    assert dim.notes[0] == "Strong verdict with high confidence"


class _LowConfidenceFoundryAgentService(_StubFoundryAgentService):
    response_text = "Needs work\nLow confidence in assessment"


@pytest.mark.asyncio
async def test_confidence_inference_handles_low_confidence(monkeypatch):
    monkeypatch.setattr("questions.app.questions.FoundryAgentService", _LowConfidenceFoundryAgentService)

    async def _fake_ensure(self):
        self.graders = [
            Grader(
                agent_id="grader-2",
                deployment="fake-deployment",
                dimension="clarity",
            )
        ]

    monkeypatch.setattr(QuestionStateMachine, "ensure_assembly", _fake_ensure)

    result = await evaluate_question(
        assembly_id="assembly-456",
        question=Question(id="q2", topic="Writing", question="Explain scene", explanation=None),
        answer=Answer(id="a2", text="It's okay", question_id="q2", respondent="Student"),
    )

    dim = result.dimensions[0]
    assert dim.confidence == pytest.approx(0.4)
    assert "Low confidence" in " ".join(dim.notes)