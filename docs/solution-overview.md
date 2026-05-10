# Solution Overview

> Current-state analysis of **The Tutor** platform — a multi-agent educational intelligence platform that adds AI-powered assessment, tutoring, content management, and supervisor insights to an existing Learning Management System ecosystem.

---

## 1. Platform Identity

**The Tutor** is an intelligent tutoring platform designed to **augment** an existing educational ecosystem — not replace it. It integrates with the host **LMS platform** (the institution's learning and student information system) and **Microsoft Fabric** (the department's BI/analytics platform) to provide:

- **AI-powered essay and discursive question evaluation** with OCR for handwritten submissions, configurable ENEM-aligned strategies, and RAG grounding from curated pedagogical materials
- **Real-time question assessment** using a state-machine evaluation pipeline supporting both objective and discursive question types
- **Guided virtual tutoring** for students during writing activities — providing hints and pedagogical prompts without giving direct answers
- **Conversational avatar tutoring** via Azure Speech + Azure AI Agents for voice-driven learning
- **Pedagogical material ingestion** with OCR via Azure AI Document Intelligence and indexing via Azure AI Search for RAG grounding
- **Supervisor insight reports** consuming Microsoft Fabric indicators (standardized assessments, attendance, task completion) and synthesizing Strava-like narrative briefings for pre-visit preparation
- **Stateful upskilling plan management** with persistent teaching plans, multi-agent evaluation via visitor pattern (Performance, ContentComplexity, GuidanceCoach, ENEMAlignment), and professor-scoped plan lifecycle (draft → evaluated → revised → archived)
- **Course/student/professor/school management** as a lightweight configuration layer with configurable pedagogical rules and feature flags

The system is positioned as an **LMS enhancer**: it consumes LMS context (courses, students, assignments) and Fabric analytics (standardized assessment scores, attendance, task completion rates) to produce **agent-driven educational insights** for four personas:

| Persona | Role | Key Capabilities |
|---------|------|-------------------|
| **Student** | Learner | Receive essay/question feedback, interact with guided tutor, use avatar for voice tutoring |
| **Professor** | Educator | Configure essay strategies, view class analytics, manage pedagogical rules |
| **Administrator** | Platform manager | Manage courses/schools, configure feature flags, run agent evaluations |
| **Supervisor** | Regional supervisor | Access per-school insight reports, pre-visit briefings, indicator trends |

---

## 2. Current Architecture

### 2.1 Backend Services (Python 3.13, FastAPI)

The current deployed backend set is nine Azure Container Apps, matching `azure.yaml` and the backend deployment workflow.

| Service | APIM path | Pattern | Responsibility |
|---------|-----------|---------|---------------|
| **Avatar** | `/api/avatar` | Agent + Speech | Conversational avatar tutoring using Azure Speech, Foundry-managed agents, and governed case context |
| **Chat** | `/api/chat` | Guardrail + Repository | Guided tutor responses with answer-avoidance guardrails and conversation persistence |
| **Configuration** | `/api/configuration` | CRUD + Repository | Students, professors, courses, classes, groups, pedagogical rules, themes, feature flags |
| **Essays** | `/api/essays` | Strategy + Orchestrator | Essay submission, OCR-capable ingestion, multi-strategy evaluation, and Foundry agent invocation |
| **Evaluation** | `/api/evaluation` | Dataset + Run Pipeline | Golden datasets, evaluation runs, and quality gates for high-impact agent behavior |
| **Insights** | `/api/insights` | CQRS Projection + Governance | School-unit intelligence, causal-study drafts, conformal-risk reports, lifelong learner network payloads, and Fabric-backed supervisor briefings |
| **LMS Gateway** | `/api/lms-gateway` | Adapter + Job Queue | LMS anti-corruption layer, sync idempotency, connector state, and dead-letter tracking |
| **Questions** | `/api/questions` | State Machine | Question evaluation pipeline: Pending → Evaluating → Completed (objective + discursive) |
| **Upskilling** | `/api/upskilling` | Repository + Visitor | Stateful teaching-plan management, multi-agent evaluation, and governed advisory training-plan drafts |

`content-svc` remains a future service boundary for a dedicated content ingestion workflow. Current grounding and pedagogical-rule work is split between configuration, essays, chat, Blob Storage, AI Search, and shared contracts.

### 2.2 Frontend (Next.js 15, React 18, TypeScript)

- Single-page application hosted on **Azure Static Web Apps**
- Workspace and feature modules for Configuration, Questions, Essays, Avatar, Chat, Evaluation, LMS Gateway, Upskilling, governed intelligence, and lifelong learner network views
- API clients per service (`axios` with `ApiEnvelope<T>` unwrapper)
- Azure Speech SDK integration for avatar WebRTC
- Tailwind CSS styling with Satoshi font family

### 2.3 Infrastructure (Terraform + azd + GitHub Actions)

| Resource | Module | Purpose |
|----------|--------|---------|
| VNet (10.0.0.0/22) | `infra/terraform` networking modules | Network isolation, service/private endpoints |
| Log Analytics + Application Insights | `infra/terraform` observability resources | Centralized logging, diagnostics, and telemetry |
| Azure Container Registry | `infra/terraform` registry resources | Container image hosting |
| Azure Cosmos DB | `infra/terraform` data resources | NoSQL data store for service-owned containers and projections |
| Azure Container Apps | `infra/terraform` service resources | Microservice compute for nine backend services |
| Azure OpenAI / Foundry project | `infra/terraform` AI resources | LLM inference and Foundry Agent Service runtime |
| Azure Speech Services | `infra/terraform` AI resources | TTS/STT for avatar |
| Azure Static Web App | `infra/terraform` frontend resources + SWA workflow | Frontend hosting |
| Azure AI Document Intelligence | `infra/terraform` AI resources | OCR for handwritten essays and pedagogical materials |
| Azure AI Search | `infra/terraform` data/AI resources | Vector + keyword index for RAG grounding |
| Microsoft Fabric | *(external)* | Read-only semantic model for standardized assessments, attendance, task completion indicators |

### 2.4 Data Store

All services share a single **Azure Cosmos DB** account with multiple containers:

- `students`, `professors`, `courses`, `classes`, `groups` — Configuration domain
- `cases`, `steps`, `essays` — Assessment domain
- `questions`, `evaluations` — Question evaluation domain
- `upskilling_plans` — Upskilling domain (teaching plans, partition key: `/professor_id`)
- `learner_record_events`, `insights_reports`, `insights_feedback`, integration connector/idempotency/dead-letter containers — Insights and integration projections
- Agent references and invocation metadata — Foundry Agent Service assets are invoked through `tutor_lib.agents`; Cosmos keeps only domain-owned data and lightweight references

---

## 3. Technology Stack

### Backend

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.13 | All services |
| FastAPI | ≥0.115.5 | HTTP framework |
| Uvicorn | ≥0.32.0 | ASGI server |
| Pydantic | ≥2.9.2 | Data validation |
| Azure Cosmos SDK | ≥4.9.0 | Data access |
| Azure AI Agents SDK | ≥1.0.0b2 | Agent orchestration |
| Azure AI Projects SDK | ≥1.0.0b10 | Foundry integration |
| Jinja2 | ≥3.1.6 | Prompt templating |
| structlog | ≥24.3.0 | Structured logging |
| tenacity | ≥9.0.0 | Retry logic |

### Frontend

| Component | Version | Notes |
|-----------|---------|-------|
| Next.js | 15.5.10 | React framework |
| React | 18.3.1 | UI library |
| TypeScript | 5.7+ | Type safety |
| Tailwind CSS | 3.4.14 | Utility-first CSS |
| axios | ≥1.13.2 | HTTP client |
| Azure Speech SDK | ≥1.47.0 | Speech integration |
| zustand | 4.5.4 | State management |

### Infrastructure

| Component | Version | Notes |
|-----------|---------|-------|
| Terraform | latest | Primary IaC implementation under `infra/terraform` |
| Azure Developer CLI | latest | Environment orchestration used by approved workflows and bootstrap paths |
| Azure CLI | latest | Diagnostics and operational support |

---

## 4. Design Patterns in Use

| Pattern | Service | Implementation |
|---------|---------|---------------|
| **Repository** | Configuration | `CosmosCRUD` base class with per-entity repositories |
| **State Machine** | Questions | `PendingState` → `EvaluatingState` → `CompletedState` transitions |
| **Strategy** | Essays | `AnalyticalStrategy`, `NarrativeStrategy`, `ENEMStrategy`, `DefaultStrategy` for evaluation |
| **Strategy** | Insights | `StandardizedTestStrategy`, `AttendanceStrategy`, `TaskCompletionStrategy` for indicator fetching |
| **Orchestrator** | Essays | `EssayOrchestrator` composes OCR + strategy + RAG + agent execution |
| **Pipeline** | Content *(future service boundary)* | Upload → OCR → Chunk → AI Search index |
| **Visitor** | Upskilling | `PerformanceVisitor`, `ContentComplexityVisitor`, `GuidanceCoachVisitor`, `ENEMAlignmentVisitor` |
| **Builder** | Avatar | Agent configuration via `AvatarHandler` class |
| **Singleton** | All | `CosmosClient` and `Settings` reuse |
| **Guardrail** | Chat | Topic + language + answer-avoidance guardrails enforced by guided tutor |
| **CQRS Projection** | Insights | Deterministic school-unit, conformal-risk, causal-study, and lifelong-network read models with governance metadata |

---

## 5. Current Modernization Status

The earlier pre-modernization blockers have been retired or moved into governed follow-up work: `tutor-lib` replaces the missing `common` module, service Dockerfiles and `azure.yaml` exist, Terraform is the active infrastructure path, APIM routes cover the deployed service set, and Foundry Agent Service is accessed through `tutor_lib.agents` per ADR-008.

Current high-trust P2/P3 capabilities are implemented and live-validated in the `108dev` environment:

| Capability | Current status |
|------------|----------------|
| School-unit intelligence | Implemented in `insights-svc`, exposed to principals, supervisors, and admins with role/scope controls |
| Causal-study drafts | Implemented as governed supervisor/admin drafts; outputs are advisory and reviewable |
| Conformal-risk reports | Implemented with explicit learner membership requirements and uncertainty metadata |
| Lifelong learner network | Implemented for alumni record surfaces using shared lifelong-network contracts |
| Advisory training plans | Implemented in `upskilling-svc` with governance, calibration, and review-state metadata |

Remaining work is tracked as targeted hardening rather than foundational enablement: APIM policy hardening, broader integration tests, dedicated content-service extraction when justified, and continued production security/accessibility reviews.

---

## 6. Repository Structure

```
tutor/
├── apps/                          # Backend microservices
│   ├── avatar/                    # Avatar + Speech agent service
│   ├── chat/                      # Guided tutoring service
│   ├── configuration/             # CRUD for students, courses, rules, themes
│   ├── essays/                    # Essay evaluation with strategies
│   ├── evaluation/                # Agent quality datasets and runs
│   ├── insights/                  # Governed intelligence and lifelong-network projections
│   ├── lms-gateway/               # LMS adapter and sync gateway
│   ├── questions/                 # Question evaluation state machine
│   └── upskilling/                # Teaching-plan evaluation and advisory training plans
├── frontend/                      # Next.js 15 SPA
│   ├── app/                       # Pages and role-aware workspace routes
│   ├── components/                # React components per domain
│   ├── types/                     # TypeScript type definitions
│   ├── utils/                     # API clients, context providers
│   └── package.json
├── infra/                         # Terraform primary IaC; Bicep retained as legacy reference
│   ├── terraform/                 # Root module, service stacks, outputs
│   ├── main.bicep                 # Legacy subscription-scope entry point
│   └── modules/                   # Legacy Bicep modules
├── tests/                         # pytest test suites
│   ├── configuration/
│   ├── essays/
│   ├── insights/
│   ├── lms_gateway/
│   ├── questions/
│   └── upskilling/
├── docs/                          # Documentation (this folder)
└── README.md
```
