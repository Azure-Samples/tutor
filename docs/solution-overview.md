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

| Service | Port | Pattern | Responsibility |
|---------|------|---------|---------------|
| **Configuration** | 8081 | CRUD + Repository | Students, professors, courses, classes, groups, pedagogical rules, feature flags |
| **Questions** | 8082 | State Machine | Question evaluation pipeline: Pending → Evaluating → Completed (objective + discursive) |
| **Essays** | 8083 | Strategy + Orchestrator | Essay submission with OCR (Azure AI Document Intelligence — Phase A in progress, issue #18), multi-strategy ENEM-aligned evaluation (Phase B), RAG grounding (Phase B), Foundry agent provisioning |
| **Avatar** | 8084 | Agent + Speech | Real-time avatar interaction using Azure Speech SDK + AI Agents |
| **Upskilling** | 8085 | Repository + Visitor | Stateful teaching plan management (CRUD), multi-agent evaluation (Performance, ContentComplexity, GuidanceCoach, ENEMAlignment), Cosmos DB persistence with `/professor_id` partition |
| **Content** *(target)* | 8089 | Pipeline | Pedagogical material ingestion: upload → OCR → chunk → AI Search index |
| **Insights** *(target)* | 8090 | Strategy + Synthesis | Supervisor insight reports: Fabric indicators → narrative briefing |

### 2.2 Frontend (Next.js 14, React 18, TypeScript)

- Single-page application hosted on **Azure Static Web Apps**
- Five feature modules: Configuration, Questions, Essays, Avatar, Chat
- API clients per service (`axios` with `ApiEnvelope<T>` unwrapper)
- Azure Speech SDK integration for avatar WebRTC
- Tailwind CSS styling with Satoshi font family

### 2.3 Infrastructure (Azure Bicep)

| Resource | Module | Purpose |
|----------|--------|---------|
| VNet (10.0.0.0/22) | `vnet.bicep` | Network isolation, service/private endpoints |
| Log Analytics | `loga.bicep` | Centralized logging |
| Azure Container Registry | `acr.bicep` | Container image hosting |
| Azure Cosmos DB | `cosmos.bicep` | NoSQL data store (5 logical databases) |
| Azure Container Apps | `aca.bicep` | Microservice compute (10 services) |
| Azure OpenAI (gpt-4o) | `aoai.bicep` | LLM inference with private endpoints |
| Azure Speech Services | `speech.bicep` | TTS/STT for avatar |
| Azure Static Web App | `staticwapp.bicep` | Frontend hosting |
| Azure AI Document Intelligence | `docintel.bicep` *(target — Phase B infra; SDK wired in essays-svc in Phase A)* | OCR for handwritten essays and pedagogical materials |
| Azure AI Search | `search.bicep` *(target — Phase B)* | Vector + keyword index for RAG grounding |
| Microsoft Fabric | *(external)* | Read-only semantic model for standardized assessments, attendance, task completion indicators |

### 2.4 Data Store

All services share a single **Azure Cosmos DB** account with multiple containers:

- `students`, `professors`, `courses`, `classes`, `groups` — Configuration domain
- `cases`, `steps`, `essays` — Assessment domain
- `questions`, `evaluations` — Question evaluation domain
- `upskilling_plans` — Upskilling domain (teaching plans, partition key: `/professor_id`)
- `agents`, `swarms` — Agent provisioning domain

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
| Next.js | 14.2.5 | React framework |
| React | 18.3.1 | UI library |
| TypeScript | 5.6.3 | Type safety |
| Tailwind CSS | 3.4.14 | Utility-first CSS |
| axios | ≥1.13.2 | HTTP client |
| Azure Speech SDK | ≥1.47.0 | Speech integration |
| zustand | 4.5.4 | State management |

### Infrastructure

| Component | Version | Notes |
|-----------|---------|-------|
| Azure Bicep | latest | IaC language |
| Azure CLI | latest | Deployment CLI |

---

## 4. Design Patterns in Use

| Pattern | Service | Implementation |
|---------|---------|---------------|
| **Repository** | Configuration | `CosmosCRUD` base class with per-entity repositories |
| **State Machine** | Questions | `PendingState` → `EvaluatingState` → `CompletedState` transitions |
| **Strategy** | Essays | `AnalyticalStrategy`, `NarrativeStrategy`, `ENEMStrategy`, `DefaultStrategy` for evaluation |
| **Strategy** | Insights | `StandardizedTestStrategy`, `AttendanceStrategy`, `TaskCompletionStrategy` for indicator fetching |
| **Orchestrator** | Essays | `EssayOrchestrator` composes OCR + strategy + RAG + agent execution |
| **Pipeline** | Content | Upload → OCR → Chunk → AI Search index |
| **Visitor** | Upskilling | `PerformanceVisitor`, `ContentComplexityVisitor`, `GuidanceCoachVisitor`, `ENEMAlignmentVisitor` |
| **Builder** | Avatar | Agent configuration via `AvatarHandler` class |
| **Singleton** | All | `CosmosClient` and `Settings` reuse |
| **Guardrail** | Chat | Topic + language + answer-avoidance guardrails enforced by guided tutor |

---

## 5. Known Issues (Pre-Modernization)

| Issue | Impact | Severity |
|-------|--------|----------|
| Missing `common` module | Configuration, Questions, Upskilling fail to import `from common.config` | **Critical** |
| Empty Dockerfiles | No containerization possible | **High** |
| Duplicated dependencies | All 5 `pyproject.toml` share ~90% of deps with no shared library | **Medium** |
| Stale `tutor.egg-info` | Artifact from monolithic layout; confusing | **Low** |
| Frontend `webApp` import | Configuration components reference non-existent API export | **Medium** |
| No `azure.yaml` | Cannot use `azd` for deployment | **High** |
| No Terraform | Infrastructure not portable; no AVM compliance | **Medium** |
| No agent evaluation | No way to measure agent quality or regression | **High** |
| No authentication | No auth layer on any API or frontend | **Critical** |
| Tight coupling | All services share Cosmos logic but without a shared library | **Medium** |
| Empty components | `Transcriptions/index.tsx`, `Configuration/Cases.tsx` are empty stubs | **Low** |

---

## 6. Repository Structure

```
tutor/
├── apps/                          # Backend microservices
│   ├── avatar/                    # Avatar + Speech agent service
│   │   ├── src/app/               # FastAPI app, routes, agents, config
│   │   ├── dockerfile             # (empty)
│   │   └── pyproject.toml
│   ├── configuration/             # CRUD for students, courses, etc.
│   │   ├── src/app/               # FastAPI app, routes, repositories
│   │   ├── dockerfile             # (empty)
│   │   └── pyproject.toml
│   ├── essays/                    # Essay evaluation with strategies
│   │   ├── src/app/               # FastAPI app, orchestrator, strategies
│   │   ├── dockerfile             # (empty)
│   │   └── pyproject.toml
│   ├── questions/                 # Question evaluation state machine
│   │   ├── app/                   # FastAPI app, state machine, grader
│   │   ├── dockerfile             # (empty)
│   │   └── pyproject.toml
│   └── upskilling/                # Learning analytics visitors
│       ├── app/                   # FastAPI app, visitors, analyzers
│       ├── dockerfile             # (empty)
│       └── pyproject.toml
├── frontend/                      # Next.js 14 SPA
│   ├── app/                       # Pages (avatar, chat, config, essays, questions)
│   ├── components/                # React components per domain
│   ├── types/                     # TypeScript type definitions
│   ├── utils/                     # API clients, context providers
│   └── package.json
├── infra/                         # Azure Bicep modules
│   ├── main.bicep                 # Subscription-scope entry point
│   └── modules/                   # VNet, ACR, ACA, Cosmos, OpenAI, Speech, SWA
├── tests/                         # pytest test suites
│   ├── configuration/
│   ├── essays/
│   └── questions/
├── docs/                          # Documentation (this folder)
└── README.md
```
