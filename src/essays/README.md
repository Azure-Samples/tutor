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

- Python 3.10+
- FastAPI
- Cosmos DB (Azure)
- Azure OpenAI (for evaluation)

## Running Locally

1. Install dependencies:

   ```pwsh
   poetry install
   ```

2. Start the API:

   ```pwsh
   poetry run uvicorn app.main:app --reload
   ```

## Deploying to Azure

- Build a Docker image and push to ACR
- Deploy as a container app using the provided Bicep infra
- Configure environment variables for Cosmos DB and Azure OpenAI
