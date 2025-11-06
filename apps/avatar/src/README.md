# Tutor Avatar Backend

This service provides the avatar-based conversational engine for The Tutor platform.

## Objective

- Enable real-time, speech-based AI avatar interactions
- Provide context-aware, multimodal feedback

## Functionalities

- Real-time chat and speech synthesis
- Avatar memory and context management
- Integration with Azure Speech and OpenAI

## Infrastructure Requirements

- Python 3.10+
- FastAPI
- Azure Speech
- Azure OpenAI

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
- Configure environment variables for Azure Speech and OpenAI
