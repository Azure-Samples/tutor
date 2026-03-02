# Modernization Plan

> Phased plan for upgrading **The Tutor** from a standalone tutoring app to a multi-agent educational intelligence platform with modern dependencies, infrastructure, and architecture.

---

## Phase Overview

| Phase | Name | Duration | Dependencies |
| ----- | ---- | -------- | ------------ |
| **0** | Foundation | 1 week | None |
| **1** | Shared Library | 1 week | Phase 0 |
| **2** | Service Decoupling | 2 weeks | Phase 1 |
| **3** | Infrastructure Migration | 2 weeks | Phase 1 |
| **4** | Frontend Modernization | 2 weeks | Phase 2 |
| **5** | Security Layers | 1 week | Phase 3, 4 |
| **6** | Agent Evaluation | 1 week | Phase 2 |
| **7** | LMS Integration | 1.5 weeks | Phase 2, 5 |
| **8** | Observability & Hardening | 1 week | Phase 5, 6, 7 |
| **9** | Content Ingestion & OCR | 2 weeks | Phase 1, 3 |
| **10** | Supervision Domain | 2 weeks | Phase 3, 5, 9 |

---

## Phase 0 — Foundation

> Set up the development environment, update tooling, and establish conventions.

### Phase 0 Tasks

- [ ] **P0-01**: Update Python to 3.13 across all services
  - Update `pyproject.toml` to `requires-python = ">=3.13"`
  - Update CI/CD pipelines to use Python 3.13 image
  - Verify all dependencies are compatible with 3.13

- [ ] **P0-02**: Update Node.js to 22 LTS
  - Switch from Yarn 1.x to pnpm 9.x
  - Update `engines` field in `package.json`
  - Update CI/CD pipelines

- [ ] **P0-03**: Create development environment tooling
  - Add `.devcontainer/` with Python 3.13 + Node 22 + Terraform + azd
  - Add `Makefile` at root for common operations (`make dev`, `make test`, `make lint`)
  - Configure `azd env` for cloud-only development (no local emulators or docker-compose)

- [ ] **P0-04**: Clean up stale artifacts
  - Remove `apps/tutor.egg-info/`
  - Remove old `src/common/` references from pyproject.toml `pythonpath`
  - Fix dead imports (`webApp` in frontend components)

- [ ] **P0-05**: Establish coding standards
  - Add `ruff` (replaces black + isort + pylint) to all Python projects
  - Add `biome` (replaces ESLint + Prettier) to frontend
  - Add pre-commit hooks (`.pre-commit-config.yaml`)

---

## Phase 1 — Shared Library Extraction

> Extract common code into `lib/` to fix the broken `common` module and eliminate duplication.

### Phase 1 Tasks

- [x] **P1-01**: Create `lib/src/tutor_lib/` package scaffold
  - `config/settings.py` — Pydantic Settings with env loading
  - `config/app_factory.py` — `create_app()` with standard FastAPI middleware
  - `cosmos/client.py` — Singleton `CosmosClient` with `DefaultAzureCredential`
  - `cosmos/crud.py` — `CosmosCRUD` base class (extracted from existing services)
  - `schemas/envelope.py` — `ApiEnvelope[T]` response wrapper

- [ ] **P1-02**: Extract agent infrastructure into `lib/`
  - `agents/base.py` — `BaseTutorAgent` abstract class
  - `agents/builder.py` — `AgentBuilder` fluent API
  - `agents/registry.py` — `AgentRegistry` for discovery
  - `agents/foundry_client.py` — Azure AI Foundry client wrapper

- [x] **P1-03**: Add middleware to `lib/`
  - `middleware/auth.py` — Entra ID JWT validation (placeholder, activated in Phase 5)
  - `middleware/logging.py` — structlog request/response logging
  - `middleware/errors.py` — Standardized error responses

- [x] **P1-04**: Update all services to depend on `tutor-lib`
  - Replace `from common.config` → `from tutor_lib.config`
  - Replace `from common.cosmos` → `from tutor_lib.cosmos`
  - Remove duplicated code from each service
  - Slim down per-service `pyproject.toml` to service-specific deps only

- [ ] **P1-05**: Add `lib/tests/` with unit tests
  - Test `CosmosCRUD` with mock client
  - Test `AppFactory` middleware registration
  - Test `ApiEnvelope` serialization
  - Test `AgentBuilder` fluent API

---

## Phase 2 — Service Decoupling

> Decompose services by business domain and add new services.

### Phase 2 Tasks

- [ ] **P2-01**: Refactor Configuration Service
  - Keep: students, professors, courses, classes, groups CRUD
  - Remove: agent-related endpoints (moved to Assessment domain)
  - Remove: case/steps management (moved to Assessment domain)
  - Add: bulk-sync endpoint for LMS Gateway

- [x] **P2-02**: Create Chat Service (`apps/chat/`)
  - Extract text-based chat from Avatar service
  - Implement as guided tutor with guardrails (topic, language, answer-avoidance)
  - RAG integration with AI Search for pedagogical context
  - Proactive pedagogical triggers based on configurable rules
  - Port 8088, uses Azure OpenAI for conversation
  - Business Need: BN-PED-3, BN-PED-5

- [x] **P2-03**: Create Evaluation Service (`apps/evaluation/`)
  - Scaffold FastAPI app with routes for evaluation runs
  - Integrate Azure AI Foundry Evaluation SDK
  - CRUD for golden datasets
  - Port 8086

- [x] **P2-04**: Create LMS Gateway Service (`apps/lms-gateway/`)
  - Abstract adapter interface (`BaseLMSAdapter`)
  - Stub adapters for Moodle and Canvas
  - Sync scheduler (timer-triggered)
  - Port 8087

> Note (2026-02-25): `chat`, `evaluation`, and `lms-gateway` service scaffolds were added; detailed adapters/evaluator logic and integration tests remain pending in Phase 2.

- [ ] **P2-05**: Standardize all service entry points
  - All services use `tutor_lib.config.create_app()` factory
  - Consistent health check endpoints (`GET /health`, `GET /ready`)
  - Consistent `Dockerfile` template (multi-stage, Python 3.13-slim)

- [ ] **P2-06**: Update tests for decoupled services
  - Update existing test suites (configuration, essays, questions)
  - Add tests for new services (chat, evaluation, lms-gateway)
  - Add integration test suite for inter-service communication

---

## Phase 3 — Infrastructure Migration

> Migrate from Bicep to Terraform with Azure Verified Modules, add azd support.

### Phase 3 Tasks

- [ ] **P3-01**: Set up Terraform remote state
  - Create state storage account (`tutortfstate`)
  - Configure `backend.tf` with Azure Storage backend
  - Add state locking

- [ ] **P3-02**: Create Terraform networking module
  - VNet with subnets (ACA, Private Endpoints, APIM)
  - NSGs with zero-trust rules
  - Private DNS zones for Cosmos, OpenAI, Speech, Blob, KV
  - Use AVM: `avm/res/network/virtual-network`

- [ ] **P3-03**: Create Terraform data module
  - Cosmos DB with Hierarchical Partition Keys
  - Blob Storage for essay files
  - Use AVM: `avm/res/document-db/database-account`, `avm/res/storage/storage-account`

- [ ] **P3-04**: Create Terraform compute module
  - ACA Environment + 10 Container Apps (one per service)
  - Per-service scaling rules
  - ACR for container images
  - Use AVM: `avm/res/app/managed-environment`, `avm/res/app/container-app`

- [ ] **P3-05**: Create Terraform AI module
  - Azure OpenAI with model deployments
  - Azure Speech Services
  - Azure AI Foundry project (for evaluation)
  - Azure AI Document Intelligence (OCR for essays and pedagogical materials)
  - Azure AI Search (vector + keyword index for RAG grounding)
  - Private endpoints for all AI services
  - Use AVM: `avm/res/cognitive-services/account`, `avm/res/search/search-service`

- [ ] **P3-06**: Create Terraform security module
  - Key Vault with RBAC
  - User-Assigned Managed Identities (one per service)
  - RBAC role assignments (Cosmos, OpenAI, Speech, Blob, KV, ACR)
  - Use AVM: `avm/res/key-vault/vault`, `avm/res/managed-identity/user-assigned-identity`

- [ ] **P3-07**: Create Terraform observability module
  - Log Analytics workspace
  - Application Insights
  - Diagnostic settings on all resources
  - Alert rules

- [ ] **P3-08**: Create `azure.yaml` for azd
  - Define all 10 services + frontend
  - Map to Terraform provider
  - Add pre-deploy hooks for container builds

- [ ] **P3-09**: Write Dockerfiles for all services
  - Multi-stage build: `python:3.13-slim`
  - Install `lib/` first, then service
  - Non-root user, health check CMD
  - `.dockerignore` per service

- [ ] **P3-10**: Import existing resources into Terraform state
  - `terraform import` for each existing Azure resource
  - Validate with `terraform plan` (expect no-op)

- [ ] **P3-11**: Preserve legacy Bicep
  - Move existing Bicep to `infra/bicep/` for reference
  - Add deprecation note

> Note (2026-02-25): Phase 3 scaffolding started with remote-state bootstrap script (`infra/terraform/scripts/bootstrap-state.ps1`), backend sample config (`infra/terraform/backend.hcl.sample`), and CI terraform validation in `.github/workflows/azd-deploy.yml`.

---

## Phase 4 — Frontend Modernization

> Upgrade to Next.js 15, React 19, and add new UI capabilities.

### Phase 4 Tasks

- [ ] **P4-01**: Upgrade core framework
  - Next.js 14 → 15 (follow migration guide)
  - React 18 → 19 (update component patterns)
  - TypeScript 5.6 → 5.7+
  - Switch Yarn 1.x → pnpm 9.x

- [ ] **P4-02**: Upgrade styling
  - Tailwind CSS 3.x → 4.x
  - Migrate `tailwind.config.ts` to CSS-based config
  - Update PostCSS configuration

- [ ] **P4-03**: Add authentication (MSAL)
  - Install `@azure/msal-browser`, `@azure/msal-react`
  - Create `MsalProvider` wrapper
  - Add `LoginButton`, `LogoutButton` components
  - Protect all routes with `AuthenticatedTemplate`

- [ ] **P4-04**: Create Evaluation Dashboard page
  - `/evaluation` — list evaluation runs with scores
  - `/evaluation/[runId]` — detailed run with per-test scores
  - Charts for quality trends (recharts)

- [ ] **P4-05**: Create Avatar Parameter Selector
  - Component for voice, style, language, persona selection
  - Persist selections via `PUT /api/avatar/config`
  - Load saved config on avatar page mount

- [ ] **P4-06**: Fix dead components
  - Implement `Transcriptions/index.tsx`
  - Implement `Configuration/Cases.tsx`
  - Fix `webApp` import → use correct API clients
  - Remove unused code

- [ ] **P4-07**: Add API client for new services
  - `evaluationApi` client for Evaluation Service
  - `lmsApi` client for LMS Gateway
  - Update existing clients with auth token injection

- [ ] **P4-08**: Add security headers
  - CSP, X-Frame-Options, X-Content-Type-Options
  - Permissions-Policy for camera/microphone
  - Configure in `next.config.mjs`

---

## Phase 5 — Security Layers

> Implement zero-trust security across all layers.

### Phase 5 Tasks

- [ ] **P5-01**: Configure Entra ID app registration
  - Register app in Entra ID
  - Define app roles: `student`, `professor`, `admin`, `supervisor`
  - Configure redirect URIs for SWA
  - Supervisor role includes school-scoped claims via Entra ID groups / Graph API
  - Business Need: BN-SUP-5

- [ ] **P5-02**: Activate JWT validation middleware
  - Enable `EntraIDAuth` middleware in `tutor-lib`
  - Apply to all service routers
  - Add `require_role` decorator to protected endpoints

- [ ] **P5-03**: Configure Managed Identity RBAC
  - Create User-Assigned Managed Identity per service (Terraform)
  - Assign roles: Cosmos Contributor, OpenAI User, Speech User, etc.
  - Remove all connection strings from env vars

- [ ] **P5-04**: Configure API Management (optional)
  - Deploy APIM in Consumption tier
  - Configure JWT validation policy
  - Add rate limiting (100 req/min per user)
  - CORS policy for SWA origin

- [ ] **P5-05**: Network hardening
  - Enable NSG deny-all-inbound rules
  - Verify private endpoints for all data services
  - Disable public access on Cosmos, OpenAI, Speech, Blob, KV

- [ ] **P5-06**: Add audit logging
  - Log all authentication events
  - Log RBAC authorization decisions
  - Forward to Log Analytics for compliance

---

## Phase 6 — Agent Evaluation

> Implement the Foundry Evaluation Engine integration.

### Phase 6 Tasks

- [ ] **P6-01**: Implement evaluation service backend
  - Foundry evaluation runner (`azure-ai-evaluation` SDK)
  - Built-in evaluators: groundedness, relevance, coherence, fluency, similarity
  - Custom evaluators for education-specific metrics:
    - ENEM Competency I–V rubric fidelity evaluator
    - Discursive question accuracy evaluator
    - Pedagogical accuracy evaluator (alignment with department rubrics)
    - Guardrail compliance evaluator (topic, language, no-answer)
  - Business Need: BN-PED-1 (ENEM fidelity), BN-PED-6 (pilot validation metrics)

- [ ] **P6-02**: Create golden datasets
  - Essay evaluation dataset (20 entries, ENEM-aligned rubric scores)
  - Discursive question evaluation dataset (20 entries)
  - Question evaluation dataset (20 entries)
  - Avatar conversation dataset (10 multi-turn conversations)
  - Guided tutor dataset (10 writing-assistance conversations with guardrail tests)
  - Store in Cosmos DB `golden_datasets` container

- [ ] **P6-03**: Add evaluation CI/CD integration
  - GitHub Action: run evaluation on PR merge to `main`
  - Fail pipeline if any metric drops below threshold
  - Post evaluation summary as PR comment

- [ ] **P6-04**: Add avatar parameter reflection
  - Backend `PUT /api/avatar/config` endpoint
  - Load avatar params at session start
  - Reflect params in system prompt and Speech SDK config

---

## Phase 7 — LMS Integration

> Build the LMS Gateway for external LMS sync.

### Phase 7 Tasks

- [ ] **P7-01**: Implement base LMS adapter interface
  - `BaseLMSAdapter` with methods: `get_courses()`, `get_students()`, `get_assignments()`, `push_scores()`
  - Error handling and retry logic

- [ ] **P7-02**: Implement Moodle adapter
  - Moodle REST Web Services API integration
  - Token-based authentication
  - Course and enrollment sync

- [ ] **P7-03**: Implement Canvas adapter (stub)
  - Canvas REST API integration
  - OAuth 2.0 authentication
  - Course and enrollment sync

- [ ] **P7-04**: Implement sync scheduler
  - Timer-triggered sync (configurable interval)
  - Delta sync (only changed records)
  - Sync audit log in Cosmos DB

- [ ] **P7-05**: Add LMS configuration UI
  - Frontend page for LMS connection setup
  - Adapter selection, credentials, sync schedule
  - Sync status dashboard

---

## Phase 8 — Observability & Hardening

> Final hardening, monitoring, and production readiness.

### Phase 8 Tasks

- [ ] **P8-01**: Configure Application Insights
  - OpenTelemetry instrumentation for all services
  - Distributed tracing across service-to-service calls
  - Custom events for agent evaluation runs

- [ ] **P8-02**: Create monitoring dashboards
  - Azure Monitor workbook for platform health
  - Per-service metrics (latency, error rate, RU consumption)
  - Agent evaluation quality trends

- [ ] **P8-03**: Configure alert rules
  - 5xx error rate > 1% → high severity
  - P99 latency > 5s → medium severity
  - Cosmos RU consumption > 80% → medium severity
  - Agent evaluation score drop > 10% → high severity
  - Auth failure spike → critical severity

- [ ] **P8-04**: Load testing
  - Locust scripts for each service
  - Baseline performance metrics
  - Auto-scaling validation

- [ ] **P8-05**: Documentation finalization
  - Update all README files
  - Runbook for common operational tasks
  - Incident response playbook
  - Onboarding guide for new developers

---

## Phase 9 — Content Ingestion & OCR

> Build the pedagogical material ingestion pipeline and OCR capability for handwritten essays.

### Phase 9 Tasks

- [ ] **P9-01**: Create Content Service (`apps/content/`)
  - Scaffold FastAPI app with `tutor-lib`
  - Upload endpoint accepting PDF, DOCX, image files
  - Azure Blob Storage for raw file storage
  - Port 8089
  - Business Need: BN-PED-2

- [ ] **P9-02**: Integrate Azure AI Document Intelligence
  - Add `azure-ai-documentintelligence` SDK to `tutor-lib`
  - Implement OCR pipeline: extract text from uploaded PDFs/images
  - Handle handwritten essay scanning (prebuilt-read model)
  - Business Need: BN-PED-1 (handwritten essay OCR), BN-PED-2 (material text extraction)
  > **Phase A (branch `feat/ocr-essay-ingestion`, issue #18):** SDK is added directly to `apps/essays/pyproject.toml` (not `tutor-lib`) to keep the scope small and deliverable independently. Migration to `tutor-lib` occurs when `content-svc` is built in Phase B. The `DOCUMENT_INTELLIGENCE_ENDPOINT` env var gates whether DI or the local `pypdf`/PIL fallback is used — see ADR-010 for the integration flow diagram.

- [ ] **P9-03**: Integrate Azure AI Search for RAG
  - Add `azure-search-documents` SDK to `tutor-lib`
  - Create search index with vector + keyword fields
  - Implement chunking strategy for pedagogical documents
  - Implement embedding generation (Azure OpenAI `text-embedding-3-large`)
  - Business Need: BN-PED-2 (grounded AI responses)

- [ ] **P9-04**: Wire RAG into Assessment and Interaction domains
  - Update essays-svc to retrieve pedagogical context before evaluation
  - Update questions-svc to retrieve reference material for discursive questions
  - Update chat-svc to ground guided tutoring responses in curated materials
  - Business Need: BN-PED-1, BN-PED-3

- [ ] **P9-05**: Add ENEM strategy to essays-svc
  - Implement `ENEMStrategy` evaluating Competencies I–V
  - Strategy selection based on essay config (analytical, narrative, persuasive, ENEM)
  - Add discursive question evaluation to questions-svc
  - Business Need: BN-PED-1
  > **Deferred to Phase B** — depends on RAG context (P9-03 / P9-04) to provide rubric grounding for evaluators. Not part of issue #18.

- [ ] **P9-06**: Create Content Management UI
  - `/content` page: upload materials, view library, filter by subject/grade
  - `/content/[id]` page: document detail with extracted text preview
  - Integration with pedagogical rules configuration
  - Business Need: BN-PED-2

- [ ] **P9-07**: Add pedagogical rules and feature flags to config-svc
  - CRUD endpoints for `pedagogical_rules` (topics, rubrics, triggers, guardrails)
  - CRUD endpoints for `feature_flags` (pilot scoping by tenant, grade, subject)
  - Frontend UI for rule management
  - Business Need: BN-PED-5 (configurable rules), BN-PED-6 (controlled pilot)

---

## Phase 10 — Supervision Domain

> Build the supervisor insights service for regional supervisors.

### Phase 10 Tasks

- [ ] **P10-01**: Create Insights Service (`apps/insights/`)
  - Scaffold FastAPI app with `tutor-lib`
  - Define indicator strategy pattern (StandardizedTestStrategy, AttendanceStrategy, TaskCompletionStrategy)
  - Port 8090
  - Business Need: BN-SUP-1, BN-SUP-3

- [ ] **P10-02**: Integrate Microsoft Fabric REST API
  - Add `fabric/` client module to `tutor-lib`
  - Implement authenticated read-only access to Fabric semantic model
  - Fetch standardized assessment scores, attendance data, task completion rates per school
  - Business Need: BN-SUP-1

- [ ] **P10-03**: Implement narrative synthesis pipeline
  - Assemble indicator data from multiple strategies
  - Synthesize Strava-like narrative report via Azure OpenAI
  - Store reports in `supervision_db.insight_reports` with school partition key
  - Support scheduled (weekly) and on-demand report generation
  - Business Need: BN-SUP-2

- [ ] **P10-04**: Add supervisor RBAC and school scoping
  - Supervisor role in Entra ID with school-scoped claims
  - insights-svc validates school access via Entra groups / Graph API
  - Data isolation: supervisor can only access assigned schools' data
  - Business Need: BN-SUP-5

- [ ] **P10-05**: Create Supervisor Dashboard UI
  - `/supervision` page: school selector, indicator trends, recent briefings
  - `/supervision/[schoolId]` page: full briefing report with charts
  - Indicator configuration panel (add/remove indicator types)
  - Business Need: BN-SUP-2, BN-SUP-4

- [ ] **P10-06**: UX validation with supervisors
  - Conduct usability sessions with regional supervisors
  - Iterate on report format and dashboard layout
  - Validate indicator relevance and narrative quality
  - Business Need: BN-SUP-4

---

## Dependency Update Summary

### Python Dependencies

| Package | Current | Target | Breaking Changes |
| ------- | ------- | ------ | ---------------- |
| Python | 3.13 | 3.13 | Already current |
| FastAPI | ≥0.115.5 | ≥0.115.5 | Already current |
| Pydantic | ≥2.9.2 | ≥2.10 | Minor |
| azure-cosmos | ≥4.9.0 | ≥4.10 | Minor |
| azure-ai-agents | ≥1.0.0b2 | ≥1.0.0 (GA) | Beta → GA migration |
| azure-ai-projects | ≥1.0.0b10 | ≥1.0.0 (GA) | Beta → GA migration |
| azure-identity | ≥1.20.0 | ≥1.21 | Minor |
| structlog | ≥24.3.0 | ≥25.1 | Minor |
| **NEW**: azure-ai-evaluation | — | ≥1.0.0 | New dependency |
| **NEW**: azure-ai-documentintelligence | — | ≥1.0.0 | New dependency (OCR) |
| **NEW**: azure-search-documents | — | ≥11.5 | New dependency (RAG) |
| **NEW**: opentelemetry-api | — | ≥1.28 | New dependency |
| **NEW**: PyJWT | — | ≥2.9 | New dependency |
| **REMOVE**: black, isort, pylint | various | — | Replaced by ruff |
| **REMOVE**: moviepy | ≥2.1.1 | — | Unused |
| **REMOVE**: scikit-learn | ≥1.5.2 | — | Evaluate if still needed |

### Frontend Dependencies

| Package | Current | Target | Breaking Changes |
| ------- | ------- | ------ | ---------------- |
| Node.js | 18+ | 22 LTS | Major |
| Next.js | 14.2.5 | 15.x | Major (App Router changes) |
| React | 18.3.1 | 19.x | Major (Server Components default) |
| TypeScript | 5.6.3 | 5.7+ | Minor |
| Tailwind CSS | 3.4.14 | 4.x | Major (config format change) |
| ESLint | 8.57.0 | 9.x | Major (flat config) |
| zustand | 4.5.4 | 5.x | Major (API changes) |
| **NEW**: @azure/msal-browser | — | ≥4.0 | New dependency |
| **NEW**: @azure/msal-react | — | ≥3.0 | New dependency |
| **NEW**: recharts | — | ≥2.13 | New dependency |
| **REMOVE**: flatpickr | 4.6.13 | — | Replace with native/headless |
| **REMOVE**: jsvectormap | 1.7.0 | — | Evaluate if still needed |
| **SWITCH**: Yarn 1.x | 1.22.21 | pnpm 9.x | Package manager change |

---

## Target Repository Structure

```text
tutor/
├── .azure/                        # azd environment config
├── .devcontainer/                  # Dev container config
├── .github/
│   └── workflows/                 # CI/CD pipelines
├── azure.yaml                     # azd service manifest (10 services + frontend)
├── Makefile                       # Root-level task runner
│
├── lib/                           # Shared library (tutor-lib)
│   ├── src/tutor_lib/
│   │   ├── config/                # Settings, AppFactory
│   │   ├── cosmos/                # CosmosClient, CosmosCRUD
│   │   ├── agents/                # BaseTutorAgent, AgentBuilder, AgentRegistry
│   │   ├── search/                # AI Search client for RAG
│   │   ├── document/              # Document Intelligence client for OCR
│   │   ├── fabric/                # Fabric REST client for indicator fetching
│   │   ├── schemas/               # ApiEnvelope, shared models
│   │   └── middleware/            # Auth, logging, errors
│   ├── tests/
│   └── pyproject.toml
│
├── apps/                          # Backend services (10)
│   ├── configuration/             # Platform Domain
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── lms-gateway/               # Platform Domain (NEW)
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── content/                   # Platform Domain (NEW — Phase 9)
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── essays/                    # Assessment Domain
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── questions/                 # Assessment Domain
│   │   ├── src/app/ (was app/)
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── avatar/                    # Interaction Domain
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── chat/                      # Interaction Domain (NEW)
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── upskilling/                # Analytics Domain
│   │   ├── src/app/ (was app/)
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── evaluation/                # Analytics Domain (NEW)
│   │   ├── src/app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── insights/                  # Supervision Domain (NEW — Phase 10)
│       ├── src/app/
│       ├── tests/
│       ├── Dockerfile
│       └── pyproject.toml
│
├── frontend/                      # Next.js 15 SPA
│   ├── app/
│   │   ├── supervision/           # Supervisor dashboard (NEW)
│   │   └── content/               # Content management (NEW)
│   ├── components/
│   │   ├── Supervision/           # BriefingReport, SchoolSelector, IndicatorTrends
│   │   └── Content/               # MaterialUpload, MaterialLibrary, PedagogicalRules
│   ├── types/
│   ├── utils/
│   ├── package.json
│   └── pnpm-lock.yaml
│
├── infra/                         # Infrastructure
│   ├── terraform/                 # Terraform + AVM (target)
│   │   ├── main.tf
│   │   ├── modules/
│   │   └── environments/
│   └── bicep/                     # Legacy Bicep (preserved)
│       ├── main.bicep
│       └── modules/
│
├── tests/                         # Integration tests
│   ├── configuration/
│   ├── essays/
│   ├── questions/
│   ├── evaluation/
│   ├── content/
│   ├── insights/
│   └── integration/
│
└── docs/                          # Documentation
    ├── README.md
    ├── solution-overview.md
    ├── architecture.md
    ├── business-alignment.md
    ├── modernization-plan.md
    ├── agent-evaluation.md
    ├── security.md
    ├── service-domains.md
    ├── infrastructure.md
    └── adr/
```
