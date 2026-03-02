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

- Python 3.13+
- FastAPI
- Azure Speech
- Azure OpenAI

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
- Configure environment variables for Azure Speech and OpenAI
   - `SPEECH_RESOURCE_ID`: Full Azure resource ID of the Speech resource
   - `SPEECH_REGION`: Azure region of the Speech resource (for example, `westus2`)
