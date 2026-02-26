# Tutor Essays Backend

This service provides the essay submission and evaluation engine for The Tutor platform.

## Objective

- Store, serve, and evaluate student essays
- Provide detailed, multi-agent feedback on essay submissions

## Functionalities

- CRUD for essays
- Multi-agent evaluation via /grader/interaction
- Submission history and answer storage

## Infrastructure Requirements

- Python 3.13+
- FastAPI
- Cosmos DB (Azure)
- Azure OpenAI (for evaluation)

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

- Build a Docker image and push to ACR
- Deploy as a container app using the `azd` + Terraform infrastructure
- Configure environment variables for Cosmos DB and Azure OpenAI
