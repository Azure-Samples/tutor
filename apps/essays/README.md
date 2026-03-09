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
- Azure AI Document Intelligence (OCR for handwritten/image/PDF extraction)

## Running Locally

1. Install dependencies:

   ```pwsh
   uv pip install --python .venv -e .[dev]
   ```

2. Start the API:

   ```pwsh
   uvicorn app.main:app --reload
   ```

## OCR Configuration (Phase A)

Set these variables to enable OCR via Azure AI Document Intelligence:

- `DOCUMENT_INTELLIGENCE_ENDPOINT`
- `DOCUMENT_INTELLIGENCE_KEY`
- `DOCUMENT_INTELLIGENCE_MODEL` (default: `prebuilt-read`)

When `DOCUMENT_INTELLIGENCE_ENDPOINT` is not set, the service falls back to local extraction (`pypdf` for PDFs and metadata-only handling for images).

## Deploying to Azure

- Build a Docker image and push to ACR
- Deploy as a container app using the `azd` + Terraform infrastructure
- Configure environment variables for Cosmos DB and Azure OpenAI
