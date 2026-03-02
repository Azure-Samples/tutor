# Tutor Chat Backend

This service provides guided text tutoring for students during writing activities.

## Objective

- Offer contextual hints and pedagogical guidance
- Enforce guardrails (no direct-answer behavior)

## Infrastructure Requirements

- Python 3.13+
- FastAPI
- Azure OpenAI
- Cosmos DB (Azure)

## Running Locally

1. Install dependencies:

```pwsh
uv pip install --python .venv -e .[dev]
```

2. Start the API:

```pwsh
uvicorn app.main:app --reload
```

## Deploying to Azure

- Deploy as a container app using the `azd` + Terraform infrastructure
