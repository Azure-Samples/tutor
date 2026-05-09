import pytest
from questions.app.questions import (
    QuestionEvaluationStatus,
    QuestionStateMachine,
    evaluate_question,
)
from questions.app.schemas import Answer, Grader, Question
from tutor_lib.agents import AgentInvocationRequest, AgentInvocationResult, AgentReference


@pytest.fixture(autouse=True)
def _configure_environment(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://localhost:8081/")
    monkeypatch.setenv("PROJECT_ENDPOINT", "https://fake-endpoint.azure.com/")
    monkeypatch.setenv("COSMOS_DATABASE", "unit-test-db")
    monkeypatch.setenv("COSMOS_QUESTION_TABLE", "questions")
    monkeypatch.setenv("COSMOS_ANSWER_TABLE", "answers")
    monkeypatch.setenv("COSMOS_GRADER_TABLE", "graders")
    monkeypatch.setenv("COSMOS_ASSEMBLY_TABLE", "assemblies")


class _StubFoundryAgentFacade:
    """Stub that returns a fixed text response for any agent invocation."""
    response_text = "Strong verdict with high confidence\nHigh confidence justification"
    instances = []

    def __init__(self, *_args, **_kwargs):
        self.requests: list[AgentInvocationRequest] = []
        _StubFoundryAgentFacade.instances.append(self)

    async def invoke(self, request: AgentInvocationRequest) -> AgentInvocationResult:
        self.requests.append(request)
        return AgentInvocationResult(
            output_text=self.response_text,
            agent=request.agent,
            store=request.store,
        )


@pytest.mark.asyncio
async def test_evaluate_question_returns_completed(monkeypatch):
    _StubFoundryAgentFacade.instances.clear()
    monkeypatch.setattr("questions.app.questions.FoundryAgentFacade", _StubFoundryAgentFacade)

    async def _fake_ensure(self):
        self.graders = [
            Grader(
                agent_name="accuracy-grader",
                agent_version="2026-05-01",
                legacy_agent_id="grader-1",
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
    request = _StubFoundryAgentFacade.instances[0].requests[0]
    assert request.agent.agent_name == "accuracy-grader"
    assert request.agent.agent_version == "2026-05-01"
    assert request.agent.legacy_agent_id == "grader-1"
    assert request.agent.dimension == "accuracy"
    assert request.context["assembly_id"] == "assembly-123"
    assert request.context["question_id"] == "q1"
    assert request.context["answer_id"] == "a1"
    assert request.store is False


class _LowConfidenceFoundryAgentFacade(_StubFoundryAgentFacade):
    response_text = "Needs work\nLow confidence in assessment"


@pytest.mark.asyncio
async def test_confidence_inference_handles_low_confidence(monkeypatch):
    monkeypatch.setattr("questions.app.questions.FoundryAgentFacade", _LowConfidenceFoundryAgentFacade)

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


@pytest.mark.asyncio
async def test_legacy_assembly_references_hydrate(monkeypatch):
    class _Repository:
        async def get_by_id(self, _assembly_id):
            return {
                "id": "assembly-legacy",
                "agents": [
                    {"agent_id": "legacy-agent", "dimension": "accuracy", "deployment": "gpt-5-nano"},
                    {"id": "legacy-id", "dimension": "clarity", "deployment": "gpt-5"},
                    "legacy-string",
                ],
            }

    machine = QuestionStateMachine(
        assembly_id="assembly-legacy",
        question=Question(id="q-legacy", topic="Math", question="2+2", explanation=None),
        answer=Answer(id="a-legacy", text="4", question_id="q-legacy", respondent="Student"),
    )
    monkeypatch.setattr(machine, "_assembly_repository", _Repository())
    machine.agent_facade = object()

    await machine.ensure_assembly()

    assert [grader.agent_name for grader in machine.graders] == [
        "legacy-agent",
        "legacy-id",
        "legacy-string",
    ]
    assert [grader.legacy_agent_id for grader in machine.graders] == [
        "legacy-agent",
        "legacy-id",
        "legacy-string",
    ]
    assert machine.graders[2].dimension == "default"


@pytest.mark.asyncio
async def test_legacy_assembly_references_resolve_foundry_agent_names(monkeypatch):
    class _Repository:
        async def get_by_id(self, _assembly_id):
            return {
                "id": "assembly-legacy",
                "agents": [
                    {
                        "agent_id": "legacy-agent-id",
                        "dimension": "accuracy",
                        "deployment": "gpt-5-nano",
                    }
                ],
            }

    class _ResolvingFacade:
        async def get_agent(self, agent_id: str) -> AgentReference:
            assert agent_id == "legacy-agent-id"
            return AgentReference(
                agent_name="accuracy-grader",
                agent_version="2026-05-09",
                legacy_agent_id=agent_id,
                model_name="gpt-5-nano",
            )

    machine = QuestionStateMachine(
        assembly_id="assembly-legacy",
        question=Question(id="q-legacy", topic="Math", question="2+2", explanation=None),
        answer=Answer(id="a-legacy", text="4", question_id="q-legacy", respondent="Student"),
    )
    monkeypatch.setattr(machine, "_assembly_repository", _Repository())
    machine.agent_facade = _ResolvingFacade()

    await machine.ensure_assembly()

    assert len(machine.graders) == 1
    assert machine.graders[0].agent_name == "accuracy-grader"
    assert machine.graders[0].agent_version == "2026-05-09"
    assert machine.graders[0].legacy_agent_id == "legacy-agent-id"
    assert machine.graders[0].dimension == "accuracy"