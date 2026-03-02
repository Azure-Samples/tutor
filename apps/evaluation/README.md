# Tutor Evaluation Backend

This service runs quality evaluation workflows for Tutor agents.

## Objective

- Execute repeatable evaluation runs
- Store and expose evaluation run metadata

## Infrastructure Requirements

- Python 3.13+
- FastAPI
- Azure AI Foundry
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
