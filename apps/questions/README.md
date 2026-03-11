# Tutor Questions Backend

<!-- CI trigger: redeploy questions service -->

This service provides the question-answering and evaluation engine for The Tutor platform.

## Objective

- Store, serve, and evaluate objective questions for students
- Provide multi-agent, real-time feedback on student answers

## Functionalities

- CRUD for questions
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
