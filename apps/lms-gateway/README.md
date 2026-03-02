# Tutor LMS Gateway Backend

This service synchronizes LMS data into Tutor configuration APIs.

## Objective

- Pull course and enrollment data from external LMS adapters
- Push normalized payloads to internal services

## Infrastructure Requirements

- Python 3.13+
- FastAPI
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
