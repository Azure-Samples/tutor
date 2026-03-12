# Local Development Guide

> Run Tutor services locally against **real Azure cloud backends** (Cosmos DB, Azure AI Foundry, Blob Storage, Speech, Vision) for sampling and testing.

This guide follows the project's **cloud-only development policy** (see [Business Alignment — §7](./business-alignment.md)): no local emulators or simulated backends. Every service runs on your machine via `uvicorn` while connecting to shared Azure resources through `DefaultAzureCredential` or explicit connection strings.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Azure Authentication](#2-azure-authentication)
3. [Repository Bootstrap](#3-repository-bootstrap)
4. [Environment Variables](#4-environment-variables)
5. [Running Backend Services](#5-running-backend-services)
6. [Running the Frontend](#6-running-the-frontend)
7. [Running Tests](#7-running-tests)
8. [Service Port Map](#8-service-port-map)
9. [Service Matrix — Cloud Dependencies](#9-service-matrix--cloud-dependencies)
10. [Sampling & Quick Smoke Tests](#10-sampling--quick-smoke-tests)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.13+ | Backend services & shared library |
| **Node.js** | 22+ | Frontend (Next.js) |
| **pnpm** | 9.x | Frontend package manager (via `corepack enable`) |
| **uv** | latest | Fast Python package installer |
| **Azure CLI** | latest | `az login` for `DefaultAzureCredential` |
| **Git** | latest | Version control |
| **Docker** | latest | Optional — only needed if you want to build/test container images locally |

> **Windows note:** The root `Makefile` uses `py -3.13` (the Windows Python launcher). On Linux/macOS, replace with `python3.13` or ensure `python` points to 3.13+.

---

## 2. Azure Authentication

All services connect to Azure through [`DefaultAzureCredential`](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential), which automatically picks up your Azure CLI session.

```pwsh
# 1 — Sign in to the Azure subscription that hosts the dev resources
az login
az account set --subscription "<your-subscription-id>"

# 2 — (Optional) If using azd workflows
azd auth login
```

Verify your identity has the required RBAC roles on the dev resource group:

| Resource | Required Role |
|----------|---------------|
| Azure Cosmos DB | **Cosmos DB Built-in Data Contributor** |
| Azure AI Foundry project | **Azure AI Developer** |
| Azure Blob Storage | **Storage Blob Data Contributor** |
| Azure OpenAI | **Cognitive Services OpenAI User** |

> If you only want to run a single service for quick testing, you only need the roles for that service's cloud dependencies (see [§9](#9-service-matrix--cloud-dependencies)).

---

## 3. Repository Bootstrap

```pwsh
git clone https://github.com/Azure-Samples/tutor.git
cd tutor

# Create virtual environment & install all backend packages (editable)
py -3.13 -m pip install --upgrade uv
py -3.13 -m uv venv .venv
.\.venv\Scripts\Activate.ps1            # Windows
# source .venv/bin/activate             # Linux / macOS

# Install shared library + all service packages in editable mode
uv pip install -e .\lib[dev]
uv pip install -e .\apps\chat -e .\apps\essays -e .\apps\questions
uv pip install -e .\apps\configuration -e .\apps\avatar -e .\apps\upskilling
uv pip install -e .\apps\evaluation -e .\apps\lms-gateway

# Install frontend
corepack enable
pnpm --dir frontend install
```

Or use the Makefile shortcut (installs lib + frontend, but **not** individual apps):

```pwsh
make bootstrap
```

After bootstrap, manually install the apps you plan to work on:

```pwsh
uv pip install -e .\apps\<service>
```

---

## 4. Environment Variables

### 4.1 — Create the `.env` file

Copy the template and fill in your Azure resource values:

```pwsh
cp .env.example .env
```

> The `.env.example` file at the repository root contains every variable used across all services. See below for how to obtain each value.

### 4.2 — Required Variables (All Services)

| Variable | How to Obtain |
|----------|---------------|
| `COSMOS_ENDPOINT` | Azure Portal → Cosmos DB account → **Settings → Keys** → URI (e.g. `https://<account>.documents.azure.com:443/`) |
| `COSMOS_DATABASE` | Database name — defaults to `tutor` |
| `PROJECT_ENDPOINT` | Azure Portal → AI Foundry project → **Overview** → Project endpoint |
| `MODEL_DEPLOYMENT_NAME` | The deployment name in the AI Foundry project (default: `gpt-4o`) |
| `MODEL_REASONING_DEPLOYMENT` | Reasoning model deployment (default: `o3-mini`) |

### 4.3 — Service-Specific Variables

<details>
<summary><strong>essays</strong> — extra Cognitive Services keys</summary>

| Variable | Notes |
|----------|-------|
| `COSMOS_KEY` | Cosmos DB primary key (essays uses key-based auth in current code) |
| `BLOB_CONNECTION_STRING` | Storage account → **Access keys** |
| `BLOB_SERVICE_CLIENT` | Same connection string (essays config alias) |
| `AI_SPEECH_URL` | Speech Services endpoint |
| `AI_SPEECH_KEY` | Speech Services key |
| `AZURE_VISION_ENDPOINT` | Azure AI Vision endpoint |
| `AZURE_VISION_KEY` | Azure AI Vision key |
| `AZURE_MODEL_KEY` | Azure OpenAI key |
| `AZURE_MODEL_URL` | Azure OpenAI endpoint |

</details>

<details>
<summary><strong>configuration</strong> — Blob Storage & Entra teacher auth</summary>

| Variable | Notes |
|----------|-------|
| `BLOB_CONNECTION_STRING` | Storage account connection string |
| `BLOB_CONTAINER_NAME` | Defaults to `uploads` |
| `ENTRA_TEACHER_CLIENT_ID` | Entra app reg for teacher flows |
| `ENTRA_TEACHER_CLIENT_SECRET` | Corresponding client secret |
| `STUDENT_SECRET_SALT` | Salt for student credential hashing |

</details>

<details>
<summary><strong>lms-gateway</strong> — External LMS credentials</summary>

| Variable | Notes |
|----------|-------|
| `LMS_MOODLE_BASE_URL` | Moodle instance URL (blank to skip) |
| `LMS_MOODLE_TOKEN` | Moodle API token |
| `LMS_CANVAS_BASE_URL` | Canvas LMS URL (blank to skip) |
| `LMS_CANVAS_TOKEN` | Canvas API token |
| `LMS_JOB_STORE` | `cosmos` or `memory` (use `memory` for quick tests) |

</details>

<details>
<summary><strong>evaluation</strong> — Storage mode</summary>

| Variable | Notes |
|----------|-------|
| `EVALUATION_REPOSITORY` | `cosmos` or `memory` (use `memory` for quick tests without DB) |

</details>

<details>
<summary><strong>avatar</strong> — Speech session token brokering</summary>

| Variable | Notes |
|----------|-------|
| `SPEECH_RESOURCE_ID` | Azure Speech resource ARM ID used to build AAD token (`aad#<resourceId>#<token>`) |
| `SPEECH_REGION` | Azure Speech region used by relay token endpoint |

If these variables are not set, `/speech/session-token` will return service-unavailable.

</details>

### 4.4 — Disable Authentication for Local Testing

By default authentication is **disabled** (`ENTRA_AUTH_ENABLED=false`). This is the recommended setting for local development and sampling. When enabled, all API calls require a valid Entra ID JWT.

### 4.5 — Loading the `.env` File

Services built with the shared library (`tutor_lib`) use `pydantic-settings`, which reads from environment variables. Load the root `.env` before launching:

```pwsh
# PowerShell — load .env into current session
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+?)\s*=\s*"?(.*?)"?\s*$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
    }
}
```

```bash
# Bash / Linux / macOS
set -a; source .env; set +a
```

---

## 5. Running Backend Services

Each service is a FastAPI app started with `uvicorn`. Since all services default to port **8000**, assign a unique port to each one you want to run simultaneously.

### 5.1 — Run a Single Service

```pwsh
# Activate venv and load env vars (see §4.5)
.\.venv\Scripts\Activate.ps1

# Example: run the chat service on port 8081
cd apps/chat/src
uvicorn app.main:app --reload --port 8081
```

### 5.2 — Run Multiple Services (Recommended Ports)

Open a separate terminal per service (each terminal must have the `.env` loaded):

| Service | Command | Port |
|---------|---------|------|
| **avatar** | `cd apps/avatar/src && uvicorn app.main:app --reload --port 8081` | 8081 |
| **configuration** | `cd apps/configuration/src && uvicorn app.main:app --reload --port 8082` | 8082 |
| **essays** | `cd apps/essays/src && uvicorn app.main:app --reload --port 8083` | 8083 |
| **questions** | `cd apps/questions && uvicorn app.main:app --reload --port 8084` | 8084 |
| **upskilling** | `cd apps/upskilling && uvicorn app.main:app --reload --port 8085` | 8085 |
| **chat** | `cd apps/chat/src && uvicorn app.main:app --reload --port 8086` | 8086 |
| **evaluation** | `cd apps/evaluation/src && uvicorn app.main:app --reload --port 8087` | 8087 |
| **lms-gateway** | `cd apps/lms-gateway/src && uvicorn app.main:app --reload --port 8088` | 8088 |

> **Tip:** Each service exposes a **`GET /health`** endpoint. After starting, verify with `curl http://localhost:<port>/health`.

### 5.3 — Minimal Set: Pick Only What You Need

You rarely need all 8 services running. For common sampling scenarios:

| Scenario | Services to Run |
|----------|----------------|
| **Chat/tutoring demo** | `chat` |
| **Essay evaluation** | `essays` |
| **Question grading** | `questions` |
| **Avatar conversation** | `avatar` |
| **Admin/roster management** | `configuration` |
| **Agent quality checks** | `evaluation` (set `EVALUATION_REPOSITORY=memory` for no-DB mode) |
| **LMS sync testing** | `lms-gateway` (set `LMS_JOB_STORE=memory` for no-DB mode) |
| **Full end-to-end** | All 8 services + frontend |

---

## 6. Running the Frontend

```pwsh
cd frontend
pnpm dev
```

Opens at [http://localhost:3000](http://localhost:3000).

### Frontend → Backend Routing

The frontend is APIM-only. All browser traffic to backend services must flow through Azure API Management.

### APIM Gateway Routing (recommended)

Set:

```env
NEXT_PUBLIC_APIM_BASE_URL="https://<your-apim-hostname>"
```

The frontend client in `frontend/utils/api.ts` routes service calls through APIM with these paths:

| Frontend client | APIM base path | Typical backend domain |
|---|---|---|
| `avatarEngine` | `/api/avatar` | avatar |
| `essaysEngine` | `/api/essays` | essays |
| `questionsEngine` | `/api/questions` | questions |
| `configurationApi` | `/api/configuration` | configuration |
| `upskillingApi` | `/api/upskilling` | upskilling |
| `chatApi` | `/api/chat` | chat |
| `evaluationApi` | `/api/evaluation` | evaluation |
| `lmsGatewayApi` | `/api/lms-gateway` | lms-gateway |

In all builds, `NEXT_PUBLIC_APIM_BASE_URL` is required and the frontend fails fast if missing.

### Production deployment sequence

Deploy APIM before frontend publication:

1. `azd provision`
2. Deploy backend Container Apps
3. Validate APIM health/readiness routes
4. Redeploy Static Web App with `NEXT_PUBLIC_APIM_BASE_URL` set

See [azd Deployment Runbook](./runbooks/azd-deployment.md) for exact commands.

---

## 7. Running Tests

```pwsh
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run all backend tests
python -m pytest tests -q

# Lint
ruff check apps tests
ruff format --check apps tests

# Frontend lint
pnpm --dir frontend lint
```

Or via Makefile:

```pwsh
make test          # backend tests
make lint          # backend + frontend lint
make format        # auto-format both
```

---

## 8. Service Port Map

Reference map for when running all services locally:

```
┌────────────────────┬──────┬───────────────────────────────────┐
│ Service            │ Port │ Swagger Docs                      │
├────────────────────┼──────┼───────────────────────────────────┤
│ avatar             │ 8081 │ http://localhost:8081/docs         │
│ configuration      │ 8082 │ http://localhost:8082/docs         │
│ essays             │ 8083 │ http://localhost:8083/docs         │
│ questions          │ 8084 │ http://localhost:8084/docs         │
│ upskilling         │ 8085 │ http://localhost:8085/docs         │
│ chat               │ 8086 │ http://localhost:8086/docs         │
│ evaluation         │ 8087 │ http://localhost:8087/docs         │
│ lms-gateway        │ 8088 │ http://localhost:8088/docs         │
├────────────────────┼──────┼───────────────────────────────────┤
│ frontend           │ 3000 │ http://localhost:3000              │
└────────────────────┴──────┴───────────────────────────────────┘
```

---

## 9. Service Matrix — Cloud Dependencies

Use this table to understand which Azure resources each service needs when running locally:

| Service | Cosmos DB | AI Foundry (Agents) | Blob Storage | Speech | Vision | LMS | Min-Cloud Footprint |
|---------|:---------:|:-------------------:|:------------:|:------:|:------:|:---:|:-------------------:|
| **avatar** | ✅ | ✅ | — | — | — | — | Cosmos + AI |
| **chat** | ✅ | ✅ | — | — | — | — | Cosmos + AI |
| **configuration** | ✅ | ✅ | ✅ | — | — | — | Cosmos + AI + Blob |
| **essays** | ✅ | ✅ | ✅ | ✅ | ✅ | — | Cosmos + AI + Blob + Cognitive |
| **questions** | ✅ | ✅ | — | — | — | — | Cosmos + AI |
| **upskilling** | ✅ | ✅ | — | — | — | — | Cosmos + AI |
| **evaluation** | ⚪ | — | — | — | — | — | None (`memory` mode) |
| **lms-gateway** | ⚪ | — | — | — | — | ⚪ | None (`memory` mode) |

✅ = required &nbsp; ⚪ = optional (has in-memory fallback)

> **Cheapest sampling path:** Run `evaluation` or `lms-gateway` with `EVALUATION_REPOSITORY=memory` / `LMS_JOB_STORE=memory` — these require **zero** cloud resources.

---

## 10. Sampling & Quick Smoke Tests

### 10.1 — Health Checks

After starting any service, verify it boots correctly:

```pwsh
curl http://localhost:8081/health
# Expected: {"status": "healthy"} or 200 OK
```

### 10.2 — Interactive API Docs

Every FastAPI service auto-generates Swagger UI. Open `http://localhost:<port>/docs` in a browser to explore and test endpoints interactively.

### 10.3 — Chat Service Sample Call

```pwsh
curl -X POST http://localhost:8086/guide `
  -H "Content-Type: application/json" `
  -d '{
    "student_id": "test-student-001",
    "course_id": "course-001",
    "message": "Explain photosynthesis step by step"
  }'
```

### 10.4 — Questions Service Sample Call

```pwsh
# List questions for an assembly
curl http://localhost:8084/questions?assembly_id=<assembly-id>

# Submit an answer for grading
curl -X POST http://localhost:8084/grader/interaction `
  -H "Content-Type: application/json" `
  -d '{
    "question_id": "<question-id>",
    "student_id": "test-student-001",
    "answer": "The mitochondria is the powerhouse of the cell"
  }'
```

### 10.5 — Essays Service Sample Call

```pwsh
curl -X POST http://localhost:8083/essays `
  -H "Content-Type: application/json" `
  -d '{
    "student_id": "test-student-001",
    "assembly_id": "<assembly-id>",
    "title": "Climate Change Effects",
    "content": "Climate change is one of the most pressing issues..."
  }'
```

### 10.6 — Evaluation Service (No Cloud Required)

```pwsh
# Set EVALUATION_REPOSITORY=memory, then start on port 8087
curl http://localhost:8087/health

# Create an evaluation run
curl -X POST http://localhost:8087/evaluations `
  -H "Content-Type: application/json" `
  -d '{
    "agent": "essays",
    "dataset_id": "golden-set-001",
    "metrics": ["groundedness", "relevance"]
  }'
```

### 10.7 — LMS Gateway (No Cloud Required)

```pwsh
# Set LMS_JOB_STORE=memory, then start on port 8088
curl http://localhost:8088/health

# Trigger a sync (will fail gracefully if no LMS configured)
curl -X POST http://localhost:8088/sync `
  -H "Content-Type: application/json" `
  -d '{"adapter": "moodle", "course_id": "demo-course"}'
```

---

## 11. Troubleshooting

### `COSMOS_ENDPOINT` validation error on startup

The shared library requires `COSMOS_ENDPOINT` and `PROJECT_ENDPOINT`. If you only need services with in-memory fallback (`evaluation`, `lms-gateway`), set dummy values:

```env
COSMOS_ENDPOINT=https://placeholder.documents.azure.com:443/
PROJECT_ENDPOINT=https://placeholder.services.ai.azure.com/api
```

### `DefaultAzureCredential` authentication failed

1. Run `az login` and ensure the correct subscription is selected.
2. Verify your user has the required RBAC roles (see [§2](#2-azure-authentication)).
3. If behind a VPN/proxy, ensure your machine can reach `login.microsoftonline.com`.

### `ModuleNotFoundError: No module named 'tutor_lib'`

The shared library is not installed. Run:

```pwsh
uv pip install -e .\lib
```

### Port already in use

Another process is using the port. Either choose a different `--port` or kill the existing process:

```pwsh
# Find process on port 8081
netstat -ano | findstr :8081
# Kill it
taskkill /PID <pid> /F
```

### Frontend can't reach backends

Ensure the relevant `NEXT_PUBLIC_*_APP_BASE_URL` variable points to the correct local service port. The frontend now reads only `NEXT_PUBLIC_*` keys.

### Frontend production build fails with APIM env error

If you see `NEXT_PUBLIC_APIM_BASE_URL is required in production deployments`, configure APIM first and set `NEXT_PUBLIC_APIM_BASE_URL` in your SWA deployment workflow secrets.

### Essays service: `COSMOS_KEY` required

The essays service uses its own config with key-based Cosmos auth (not `DefaultAzureCredential`). You must provide `COSMOS_KEY` from the Cosmos DB account's **Keys** blade in the Azure Portal.

---

## Related Documentation

- [Solution Overview](./solution-overview.md) — Current-state architecture and known issues
- [Architecture](./architecture.md) — Target architecture with C4 diagrams
- [Service Domains](./service-domains.md) — Business-domain decomposition and service contracts
- [Infrastructure](./infrastructure.md) — Cloud infrastructure with Terraform + azd
- [Security](./security.md) — Auth layers and RBAC
- [azd Deployment Runbook](./runbooks/azd-deployment.md) — Cloud deployment steps
