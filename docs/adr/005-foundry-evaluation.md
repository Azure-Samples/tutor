# ADR-005: Foundry Agent Evaluation

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The platform currently has no way to measure or track the quality of its AI agents. Specifically:

1. **No regression detection** — When prompts or agent configurations change, there is no automated way to verify that output quality didn't degrade.
2. **No quality metrics** — No standardized scoring across agents (groundedness, relevance, coherence, fluency, safety).
3. **No golden dataset** — No curated test inputs with expected outputs for benchmarking.
4. **Agent swarms are configurable** — Professors can provision custom agents via the essays service Foundry integration, but there's no way to evaluate them before deployment.

Azure AI Foundry provides an **Evaluation Engine** that supports:

- Built-in evaluators (groundedness, relevance, coherence, fluency, similarity, F1)
- Custom evaluators (Python functions or prompty-based)
- Batch evaluation runs against datasets
- Integration with AI Foundry Projects for tracking runs over time

## Decision

**Introduce a dedicated Evaluation Service** that uses the Azure AI Foundry Evaluation Engine to assess agent quality, and expose avatar parameter selection on the frontend with backend reflection.

### 1. Evaluation Service Architecture

```
apps/evaluation/
├── src/
│   └── app/
│       ├── main.py              # FastAPI app (port 8086)
│       ├── config.py            # Service settings
│       ├── routes.py            # /run, /results, /datasets endpoints
│       ├── evaluators/
│       │   ├── __init__.py
│       │   ├── essay_evaluator.py      # Essay agent quality
│       │   ├── question_evaluator.py   # Question agent quality
│       │   ├── avatar_evaluator.py     # Avatar conversation quality
│       │   └── custom_evaluator.py     # User-defined evaluators
│       ├── datasets/
│       │   ├── __init__.py
│       │   └── manager.py       # Golden dataset CRUD (Cosmos)
│       └── runners/
│           ├── __init__.py
│           └── foundry_runner.py  # Azure AI Foundry evaluation runner
├── tests/
│   └── test_evaluation.py
├── Dockerfile
└── pyproject.toml
```

### 2. Evaluation Flow

```python
from azure.ai.evaluation import evaluate
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    SimilarityEvaluator,
    ContentSafetyEvaluator,
)

async def run_evaluation(
    agent_id: str,
    dataset_id: str,
    evaluator_names: list[str],
) -> EvaluationResult:
    """Execute an evaluation run against a target agent."""
    
    # 1. Load golden dataset from Cosmos
    dataset = await datasets.load(dataset_id)
    
    # 2. Configure evaluators
    evaluators = {
        "groundedness": GroundednessEvaluator(model_config),
        "relevance": RelevanceEvaluator(model_config),
        "coherence": CoherenceEvaluator(model_config),
        "fluency": FluencyEvaluator(model_config),
        "similarity": SimilarityEvaluator(model_config),
        "safety": ContentSafetyEvaluator(azure_ai_project),
    }
    
    # 3. Define target function (the agent under test)
    target = build_agent_target(agent_id)
    
    # 4. Run evaluation
    result = evaluate(
        data=dataset.to_pandas(),
        target=target,
        evaluators={k: v for k, v in evaluators.items() if k in evaluator_names},
        azure_ai_project=azure_ai_project,
        evaluation_name=f"eval-{agent_id}-{datetime.utcnow().isoformat()}",
    )
    
    # 5. Persist results
    await results_repo.save(result)
    
    return result
```

### 3. Golden Dataset Schema

```json
{
    "id": "essay-golden-v1",
    "agentType": "essay_evaluator",
    "version": "1.0.0",
    "entries": [
        {
            "input": "Analyze the impact of climate change on biodiversity...",
            "context": "This is an analytical essay for a graduate environmental science course.",
            "expected_output": "The essay demonstrates strong thesis development...",
            "metadata": {
                "strategy": "analytical",
                "difficulty": "advanced",
                "courseId": "ENV-501"
            }
        }
    ]
}
```

### 4. Evaluation Metrics Dashboard

The frontend exposes evaluation results via a new `/evaluation` page:

| Metric | Target | Description |
|--------|--------|-------------|
| Groundedness | ≥ 4.0/5.0 | Agent response is factually grounded in provided context |
| Relevance | ≥ 4.0/5.0 | Response addresses the actual question/essay topic |
| Coherence | ≥ 4.0/5.0 | Response is logically structured and well-organized |
| Fluency | ≥ 4.0/5.0 | Response uses correct grammar and natural language |
| Similarity | ≥ 0.7 | Response aligns with the golden expected output |
| Safety | Pass | No harmful, biased, or inappropriate content |

### 5. Avatar Parameter Selection

The frontend adds an **AvatarParameterSelector** component that allows configuration of:

| Parameter | Options | Backend Mapping |
|-----------|---------|-----------------|
| Voice | `en-US-JennyNeural`, `en-US-GuyNeural`, `en-US-AriaNeural` | `speech.voice_name` |
| Speaking Style | `friendly`, `professional`, `empathetic` | `speech.style` |
| Language | `en-US`, `pt-BR`, `es-ES` | `speech.language` |
| Avatar Style | `casual`, `formal`, `technical` | `agent.persona` |
| Response Length | `concise`, `detailed`, `comprehensive` | `agent.max_tokens` |
| Expertise Level | `beginner`, `intermediate`, `advanced` | `agent.system_prompt` modifier |

These parameters are persisted in Cosmos DB under the `agent_configs` container and loaded by the Avatar Service at session start.

## Consequences

### Positive

- **Quality assurance** — Every agent change can be validated before production deployment.
- **Regression detection** — Automated evaluation runs in CI/CD catch quality degradation.
- **Standardized metrics** — All agents are measured with the same evaluators for comparability.
- **Professor confidence** — Educators can see evaluation scores before enabling agents for students.
- **Avatar personalization** — Students/professors can tune avatar behavior from the UI.

### Negative

- **Cost** — Evaluation runs consume Azure OpenAI tokens (evaluators use LLM-as-judge).
- **Golden dataset maintenance** — Requires ongoing curation as courses and content evolve.
- **Evaluation latency** — Full evaluation runs can take minutes for large datasets.

### Mitigations

- Run evaluations on schedule (nightly) or on PR merge, not on every commit.
- Start with small golden datasets (20-50 entries per agent type).
- Cache evaluation results aggressively; only re-run when agent config changes.

## References

- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk)
- [Azure AI Foundry Evaluation](https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-approach-gen-ai)
- [Built-in evaluators](https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#built-in-evaluators)
- [Custom evaluators](https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#custom-evaluators)
