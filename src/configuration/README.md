# Tutor Configuration Backend

This service provides configuration and management APIs for The Tutor platform.

## Objective

- Manage system-wide settings, rules, and evaluation criteria

## Functionalities

- CRUD for configuration items
- API for rules and settings

## Infrastructure Requirements

- Python 3.10+
- FastAPI
- Cosmos DB (Azure)

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
- Configure environment variables for Cosmos DB
