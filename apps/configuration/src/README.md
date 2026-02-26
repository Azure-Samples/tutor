# Tutor Configuration Backend

This service provides configuration and management APIs for The Tutor platform.

## Objective

- Manage system-wide settings, rules, and evaluation criteria

## Functionalities

- CRUD for configuration items
- API for rules and settings

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

- Build a Docker image and push to ACR
- Deploy as a container app using the `azd` + Terraform infrastructure
- Configure environment variables for Cosmos DB
