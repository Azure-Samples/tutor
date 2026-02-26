# ADR-006: Domain-Driven Service Decoupling

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The current five services are organized by technical function, not by business domain:

| Current Service | Mixes |
|----------------|-------|
| Configuration | Student CRUD + Course CRUD + Agent config + Case management |
| Questions | Evaluation logic + Agent orchestration + Data persistence |
| Essays | Evaluation strategies + Foundry agent provisioning + File storage |
| Avatar | Speech processing + Agent orchestration + Session management |
| Upskilling | Analytics + Agent orchestration + Recommendation generation |

This causes:

1. **Cross-cutting concerns scattered** — Agent management code is duplicated in essays, questions, avatar, and upskilling.
2. **Configuration service overloaded** — It manages students, courses, classes, groups, cases, steps, agents — too many responsibilities.
3. **No separation of agentic vs. non-agentic** — CRUD operations and AI-agent operations have different scaling, security, and cost profiles.
4. **No clear domain boundaries** — Changing "how students are modeled" requires touching Configuration, Questions, Essays, and Upskilling.

## Decision

**Decompose services into four business domains**, separating agentic (AI-powered) services from non-agentic (CRUD/platform) services.

### Domain Map

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE TUTOR PLATFORM                          │
├──────────────────┬──────────────────────────────────────────────┤
│                  │                                              │
│  PLATFORM        │  AGENTIC DOMAINS                             │
│  (Non-Agentic)   │                                              │
│                  │  ┌─────────────────────────────────────┐     │
│  ┌────────────┐  │  │ ASSESSMENT DOMAIN                   │     │
│  │ config-svc │  │  │  ├─ essays-svc (Strategy pattern)   │     │
│  │            │  │  │  └─ questions-svc (State machine)    │     │
│  │ • students │  │  └─────────────────────────────────────┘     │
│  │ • courses  │  │                                              │
│  │ • classes  │  │  ┌─────────────────────────────────────┐     │
│  │ • groups   │  │  │ INTERACTION DOMAIN                   │     │
│  └────────────┘  │  │  ├─ avatar-svc (Speech + Agent)      │     │
│                  │  │  └─ chat-svc (Text + Agent)           │     │
│  ┌────────────┐  │  └─────────────────────────────────────┘     │
│  │ lms-gw     │  │                                              │
│  │            │  │  ┌─────────────────────────────────────┐     │
│  │ • sync     │  │  │ ANALYTICS DOMAIN                     │     │
│  │ • adapters │  │  │  ├─ upskilling-svc (Visitors)        │     │
│  └────────────┘  │  │  └─ evaluation-svc (Foundry eval)    │     │
│                  │  └─────────────────────────────────────┘     │
│  ┌────────────┐  │                                              │
│  │identity-prx│  │                                              │
│  │            │  │                                              │
│  │ • auth     │  │                                              │
│  │ • RBAC     │  │                                              │
│  └────────────┘  │                                              │
└──────────────────┴──────────────────────────────────────────────┘
```

### Domain Definitions

#### 1. Platform Domain (Non-Agentic)

Services that handle data management, integration, and identity — no AI inference.

| Service | Responsibility | Scaling Profile |
|---------|---------------|-----------------|
| **config-svc** | CRUD for students, professors, courses, classes, groups | Low CPU, steady traffic |
| **lms-gateway** | External LMS sync adapters (Moodle, Canvas) | Burst during sync, idle otherwise |
| **identity-proxy** | Entra ID authentication, RBAC enforcement | Proportional to all traffic |

#### 2. Assessment Domain (Agentic)

Services that evaluate student work using AI agents.

| Service | Responsibility | Scaling Profile |
|---------|---------------|-----------------|
| **essays-svc** | Essay submission, strategy selection, Foundry agent evaluation | High token usage, medium latency |
| **questions-svc** | Real-time question grading, state machine pipeline | Low latency required (debounced UI) |

#### 3. Interaction Domain (Agentic)

Services that provide real-time AI conversation experiences.

| Service | Responsibility | Scaling Profile |
|---------|---------------|-----------------|
| **avatar-svc** | Speech-driven avatar tutoring (WebRTC + TTS/STT) | Always-on, connection-based scaling |
| **chat-svc** | Text-based tutoring conversations | Session-based, moderate latency |

#### 4. Analytics Domain (Agentic)

Services that analyze learning patterns and evaluate agent quality.

| Service | Responsibility | Scaling Profile |
|---------|---------------|-----------------|
| **upskilling-svc** | Performance analysis, learning path recommendations | Batch, async |
| **evaluation-svc** | Agent quality evaluation via Foundry evaluators | Batch, high token usage |

### Data Ownership

Each domain owns its Cosmos DB containers:

```
Cosmos DB Account: tutor-cosmosdb
├── Platform Database
│   ├── students       (PK: tenantId/courseId)     → config-svc
│   ├── professors     (PK: tenantId)              → config-svc
│   ├── courses        (PK: tenantId)              → config-svc
│   ├── classes        (PK: courseId)               → config-svc
│   ├── groups         (PK: classId)               → config-svc
│   └── sync_logs      (PK: tenantId)              → lms-gateway
│
├── Assessment Database
│   ├── essays         (PK: courseId/studentId)     → essays-svc
│   ├── essay_configs  (PK: courseId)               → essays-svc
│   ├── questions      (PK: courseId/studentId)     → questions-svc
│   └── evaluations    (PK: courseId/studentId)     → questions-svc
│
├── Interaction Database
│   ├── conversations  (PK: sessionId)             → avatar-svc, chat-svc
│   ├── transcripts    (PK: sessionId)             → avatar-svc
│   └── agent_configs  (PK: tenantId)              → avatar-svc, chat-svc
│
└── Analytics Database
    ├── analyses       (PK: studentId)              → upskilling-svc
    ├── eval_runs      (PK: agentId)                → evaluation-svc
    └── golden_datasets(PK: agentType)              → evaluation-svc
```

### Inter-Service Communication

Services communicate via **REST APIs over the ACA internal network** (service discovery). No direct database cross-reads.

```mermaid
graph LR
    subgraph Platform
        CONFIG["config-svc"]
        LMS["lms-gateway"]
    end

    subgraph Assessment
        ESSAYS["essays-svc"]
        QUESTIONS["questions-svc"]
    end

    subgraph Interaction
        AVATAR["avatar-svc"]
        CHAT["chat-svc"]
    end

    subgraph Analytics
        UPSKILLING["upskilling-svc"]
        EVAL["evaluation-svc"]
    end

    ESSAYS -->|GET /students/{id}| CONFIG
    QUESTIONS -->|GET /students/{id}| CONFIG
    AVATAR -->|GET /courses/{id}| CONFIG
    UPSKILLING -->|GET /evaluations| ESSAYS
    UPSKILLING -->|GET /evaluations| QUESTIONS
    EVAL -->|POST /evaluate| ESSAYS
    EVAL -->|POST /evaluate| QUESTIONS
    EVAL -->|POST /evaluate| AVATAR
    LMS -->|POST /courses/bulk-sync| CONFIG
```

## Consequences

### Positive

- **Clear ownership** — Each team/developer owns a full domain, not a thin horizontal slice.
- **Independent scaling** — Agentic services (high token cost) scale differently from CRUD services.
- **Security segmentation** — Non-agentic services don't need AI service credentials.
- **Failure isolation** — A failing evaluation run doesn't affect student-facing essay evaluation.
- **Easier testing** — Each domain has a bounded context with clear inputs and outputs.

### Negative

- **Network overhead** — Inter-service calls add latency vs. in-process function calls.
- **Data duplication risk** — Services may cache copies of cross-domain data.
- **Operational complexity** — More services to monitor, deploy, and debug.

### Mitigations

- Use ACA internal DNS for low-latency service-to-service calls.
- Implement caching with TTLs for cross-domain data.
- Centralized observability via Log Analytics + App Insights.

## References

- [Domain-Driven Design (Evans, 2003)](https://www.domainlanguage.com/ddd/)
- [Microservices Patterns (Richardson, 2018)](https://microservices.io/patterns/)
- [Azure Container Apps service discovery](https://learn.microsoft.com/azure/container-apps/connect-apps)
