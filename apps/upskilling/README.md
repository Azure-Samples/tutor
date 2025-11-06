# Tutor Questions Backend

This service provides the question-answering and evaluation engine for The Tutor platform.

## Objective

- Store, serve, and evaluate objective questions for students
- Provide multi-agent, real-time feedback on student answers

## Functionalities

- CRUD for questions
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
