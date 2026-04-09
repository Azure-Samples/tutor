# Architecture

> Target architecture for **The Tutor** as a learner-record-centered lifelong-learning and outcomes platform. The platform preserves the repo's deterministic-core plus agentic-services split and evolves through Strangler Fig around the services and Azure topology already present in this repository.

---

## 1. High-Level System Context

Tutor is moving from an LMS enhancement layer to the institution-owned control plane for lifelong learning. Following DDD bounded contexts and TOGAF architecture building blocks, Tutor owns learner records, evidence, role-aware workflows, and credentials, while LMS, SIS, CRM, analytics, and wallet ecosystems remain external systems behind anti-corruption layers.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#FFB3BA',
  'primaryTextColor':'#000',
  'primaryBorderColor':'#FF8B94',
  'lineColor':'#BAE1FF',
  'secondaryColor':'#BAE1FF',
  'tertiaryColor':'#FFFFFF'
}}}%%
C4Context
    title System Context — The Tutor Standalone Lifelong-Learning Platform

    Person(learner, "Learner / Alumni", "Owns progress, evidence, record, credentials, and re-entry journeys")
    Person(faculty, "Professor / Advisor", "Designs learning, reviews evidence, guides interventions")
    Person(leader, "Principal / Supervisor / Program Leader", "Reviews cohort, school, and program briefings")
    Person(admin, "Administrator", "Manages programs, policies, integrations, and governance")

    System(tutor, "The Tutor Platform", "Institution-owned lifelong-learning and outcomes platform")
    System_Ext(academic, "Academic Systems", "LMS, SIS, registrar, CRM, and roster sources")
    System_Ext(credential_ecosystem, "Credential Ecosystem", "Wallets, verifiers, partner and employer systems")
    System_Ext(analytics, "Institutional Data Sources", "Microsoft Fabric and other approved analytics feeds")
    System_Ext(azure_ai, "Azure AI Services", "OpenAI, Speech, Document Intelligence, AI Search, Foundry")
    System_Ext(identity, "Microsoft Entra ID", "Identity, roles, and relationship-aware access inputs")

    Rel(learner, tutor, "Uses role-aware workspaces for learning, progress, record, and credentials")
    Rel(faculty, tutor, "Reviews assessments, evidence, cohort progress, and interventions")
    Rel(leader, tutor, "Consumes narrative briefings and deterministic program read models")
    Rel(admin, tutor, "Manages governance, integrations, policies, and platform operations")
    Rel(tutor, academic, "Normalizes external data through anti-corruption layers")
    Rel(tutor, credential_ecosystem, "Publishes and verifies portable credentials when required")
    Rel(tutor, analytics, "Consumes approved institutional indicators for read models and briefings")
    Rel(tutor, azure_ai, "Uses agentic capabilities for assessment, tutoring, advising, and synthesis")
    Rel(tutor, identity, "Authenticates users and enforces role + relationship scope")
```

---

## 2. Target-State Control Plane and Bounded Contexts

The target state has four cooperating layers: a role-aware workspace shell, a deterministic control plane, bounded agentic services, and CQRS-style read models. The logical design changes now; the deployment substrate can remain APIM + ACA + Cosmos DB + Blob Storage + Azure AI while the migration proceeds.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#FFB3BA',
  'primaryTextColor':'#000',
  'primaryBorderColor':'#FF8B94',
  'lineColor':'#BAE1FF',
  'secondaryColor':'#BAE1FF',
  'tertiaryColor':'#FFFFFF'
}}}%%
flowchart TB
    EXT["External LMS / SIS / CRM / Wallets / Analytics"]

    subgraph WORKSPACES["Role-Aware Workspaces"]
        SHELL["Workspace Shell"]
        STUDENT_WS["Student"]
        FACULTY_WS["Professor"]
        LEADER_WS["Leader"]
        ADMIN_WS["Admin"]
        ALUMNI_WS["Alumni"]
    end

    subgraph CORE["Deterministic Core / Control Plane"]
        ID["Identity & Tenancy"]
        INTEGRATION["Integration Hub\nAnti-Corruption Layers"]
        CATALOG["Catalog & Pathways"]
        LIFECYCLE["Enrollment & Lifecycle"]
        RECORD["Learner Record\nAppend-Only History"]
        CONTENT["Content & Knowledge"]
        CREDENTIALS["Credentialing & Portfolio"]
        COMMUNITY["Community & Network"]
        GOVERNANCE["Governance & Provenance"]
    end

    subgraph AGENTIC["Agentic Services"]
        ASSESS["Assessment & Evidence"]
        COACH["Coaching & Interaction"]
        ADVISE["Advising & Success"]
        INSIGHTS["Institutional Insights"]
        EVAL["Agent Evaluation"]
    end

    subgraph READ["CQRS Read Models"]
        TODAY["Today / Work Queues"]
        TIMELINE["Learner Timeline"]
        COHORT["Cohort / Program Progress"]
        BRIEFINGS["Briefings / Alerts"]
        REENTRY["Alumni Re-Entry"]
    end

    EXT --> INTEGRATION
    INTEGRATION --> LIFECYCLE
    INTEGRATION --> CATALOG
    INTEGRATION --> RECORD
    ID --> LIFECYCLE
    CATALOG --> RECORD
    LIFECYCLE --> RECORD
    CONTENT --> ASSESS
    CONTENT --> COACH
    GOVERNANCE --> ASSESS
    GOVERNANCE --> COACH
    GOVERNANCE --> ADVISE
    GOVERNANCE --> INSIGHTS
    EVAL --> GOVERNANCE
    ASSESS --> RECORD
    COACH --> RECORD
    ADVISE --> RECORD
    INSIGHTS --> RECORD
    CREDENTIALS --> RECORD
    COMMUNITY --> RECORD
    RECORD --> TODAY
    RECORD --> TIMELINE
    RECORD --> COHORT
    RECORD --> BRIEFINGS
    RECORD --> REENTRY
    TODAY --> SHELL
    TIMELINE --> SHELL
    COHORT --> SHELL
    BRIEFINGS --> SHELL
    REENTRY --> SHELL
    SHELL --> STUDENT_WS
    SHELL --> FACULTY_WS
    SHELL --> LEADER_WS
    SHELL --> ADMIN_WS
    SHELL --> ALUMNI_WS
```

| Layer | Primary bounded contexts | Design intent | Current repo anchors |
| ----- | ------------------------ | ------------- | -------------------- |
| **Deterministic core** | Identity and Tenancy, Integration Hub, Catalog and Pathways, Enrollment and Lifecycle, Learner Record, Content and Knowledge, Credentialing and Portfolio, Community and Network, Governance and Provenance | Own institutional records, policies, lifecycle state, and provenance | `config-svc`, `lms-gateway`, `content-svc`, shared auth middleware, and future learner-record / credential contexts |
| **Agentic services** | Assessment and Evidence, Coaching and Interaction, Advising and Success, Institutional Insights, Agent Evaluation | Constrain probabilistic reasoning to high-value educational workflows | `essays-svc`, `questions-svc`, `avatar-svc`, `chat-svc`, `upskilling-svc`, `insights-svc`, `evaluation-svc` |
| **Read models** | Learner timeline, work queues, cohort and school projections, alumni re-entry views | Project append-only records into role-specific experiences | Existing dashboards plus future role-aware workspace shell |

### 2.1 Migration Horizons

| Horizon | Wave | Objective | Approved backlog alignment | Current repo implication |
| ------- | ---- | --------- | -------------------------- | ------------------------ |
| **H1: Record-First Overlay** | Wave 1 | Establish relationship-based access control, event backbone, provenance capture, learner-record MVP, and role-aware shell without breaking current enhancer flows. | LL-01, LL-02, LL-03, LL-04, LL-06, LL-18 | Existing services stay in place and begin writing governed learner-record events and projections. |
| **H2: Standalone Learning Core** | Wave 2 | Introduce deterministic advising, interventions, role workspaces, and institutional read models. | LL-05, LL-08, LL-09, LL-10, LL-11, LL-13, LL-17 | Current assessment, interaction, and insights services become the execution fabric behind role-specific workspaces and intervention flows. |
| **H3: Lifelong Network Platform** | Wave 3 | Add skills graph, credentialing, alumni re-entry, community, and continuing-education expansion. | LL-07, LL-12, LL-14, LL-15, LL-16 | New bounded contexts can start inside existing services or shared libraries and split only when ownership or scale justifies it. |

> Sections 3-8 describe the current Wave 1 runtime realization. They remain the implementation reference for the services already in the repo while the target bounded contexts above are introduced incrementally.

---

## 3. Service Interaction Flows

### 3.1 Essay Evaluation Flow (with OCR + ENEM)

> **Implementation status:**
>
> - Steps 1–4 (upload → Blob): ✅ Live
> - Steps 5–6 (OCR via Document Intelligence): 🔧 Phase A — branch `feat/ocr-essay-ingestion` (issue #18)
> - Steps 7–8 (RAG via AI Search): ⏳ Phase B (issue #19)
> - Steps 9 (ENEM strategy + Foundry evaluation): ⏳ Phase B

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Essays as Essays Service
    participant DocIntel as AI Document Intelligence
    participant AISearch as Azure AI Search
    participant Foundry as Azure AI Foundry
    participant Cosmos as Cosmos DB
    participant Blob as Blob Storage

    Student->>UI: Upload essay (handwritten scan or digital text)
    UI->>APIM: POST /api/essays/submit
    APIM->>Essays: Forward (authenticated)
    Essays->>Blob: Store original document

    alt Handwritten essay (image/PDF) — Phase A
        Essays->>DocIntel: OCR extraction via prebuilt-read model
        DocIntel-->>Essays: Extracted text + layout confidence scores
        Note over Essays: Falls back to pypdf/PIL if DI endpoint not configured
    end

    Essays->>Essays: Select strategy (ENEM/analytical/narrative/default) — Phase B
    Essays->>AISearch: Query rubrics + exemplars for grounding (RAG) — Phase B
    AISearch-->>Essays: Relevant pedagogical context
    Essays->>Foundry: Create evaluation agent thread (with rubric context)
    Foundry-->>Essays: Agent response (feedback, ENEM competency scores)
    Essays->>Cosmos: Persist evaluation result
    Essays-->>APIM: EssayEvaluation response
    APIM-->>UI: 200 OK + evaluation
    UI-->>Student: Display competency scores, strengths, improvements
```

### 3.2 Question Evaluation Flow (State Machine)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Questions as Questions Service
    participant Foundry as Azure AI Foundry
    participant Cosmos as Cosmos DB

    Student->>UI: Type answer to question
    UI->>APIM: POST /api/grader/interaction (debounced 600ms)
    APIM->>Questions: Forward (authenticated)

    Note over Questions: State = PendingState
    Questions->>Questions: Transition → EvaluatingState
    Questions->>Foundry: Evaluate answer against rubric
    Foundry-->>Questions: Dimension scores + confidence

    alt confidence ≥ threshold
        Questions->>Questions: Transition → CompletedState
        Questions->>Cosmos: Persist final evaluation
    else confidence < threshold
        Questions->>Questions: Stay in EvaluatingState
        Questions-->>UI: Partial feedback (keep typing)
    end

    Questions-->>APIM: EvaluationResult
    APIM-->>UI: 200 OK + dimensions + feedback
    UI-->>Student: Real-time feedback overlay
```

### 3.3 Avatar Interaction Flow

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant UI as Tutor UI
    participant Speech as Azure Speech SDK (client)
    participant APIM as API Gateway
    participant Avatar as Avatar Service
    participant AzureSpeech as Azure Speech Services
    participant OpenAI as Azure OpenAI
    participant Cosmos as Cosmos DB

    Student->>UI: Click "Start Avatar Session"
    UI->>Speech: Initialize WebRTC + STT
    Speech-->>UI: Microphone stream ready

    loop Conversation turns
        Student->>Speech: Speak question
        Speech->>Speech: STT → text transcript
        Speech->>APIM: POST /api/avatar/chat
        APIM->>Avatar: Forward (authenticated)
        Avatar->>Cosmos: Load conversation history
        Avatar->>OpenAI: Generate response (with context)
        OpenAI-->>Avatar: Text response
        Avatar->>AzureSpeech: Synthesize speech (SSML)
        AzureSpeech-->>Avatar: Audio stream
        Avatar->>Cosmos: Persist turn
        Avatar-->>APIM: { text, audioUrl, visemes }
        APIM-->>UI: Response
        UI->>Speech: Play audio + animate avatar
        Speech-->>Student: Avatar speaks response
    end
```

### 3.4 Upskilling Plan Management Flow

```mermaid
sequenceDiagram
    autonumber
    actor Professor
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Upskilling as Upskilling Service
    participant Cosmos as Cosmos DB
    participant Foundry as Azure AI Foundry

    Professor->>UI: Create teaching plan
    UI->>APIM: POST /api/upskilling/plans
    APIM->>Upskilling: Forward (authenticated, RBAC: professor)
    Upskilling->>Cosmos: Persist plan (status: draft)
    Cosmos-->>Upskilling: PlanRecord
    Upskilling-->>APIM: 201 Created + plan
    APIM-->>UI: Plan created
    UI-->>Professor: Show plan in list

    Professor->>UI: Request AI evaluation
    UI->>APIM: POST /api/upskilling/plans/{id}/evaluate
    APIM->>Upskilling: Forward (authenticated)
    Upskilling->>Cosmos: Fetch plan by id

    par Visitor Pattern — parallel analysis
        Upskilling->>Foundry: PerformanceInsightVisitor
        Upskilling->>Foundry: ContentComplexityVisitor
        Upskilling->>Foundry: GuidanceCoachVisitor
    end

    Foundry-->>Upskilling: Agent feedback per paragraph
    Upskilling->>Cosmos: Update plan (evaluations, status: evaluated)
    Upskilling-->>APIM: 200 OK + plan with evaluations
    APIM-->>UI: Display coaching feedback
    UI-->>Professor: Show strengths & improvements per paragraph

    Professor->>UI: Revise plan paragraphs
    UI->>APIM: PUT /api/upskilling/plans/{id}
    APIM->>Upskilling: Forward (authenticated)
    Upskilling->>Cosmos: Update plan (status: revised)
    Upskilling-->>APIM: 200 OK + updated plan
    UI-->>Professor: Plan updated, ready for re-evaluation
```

### 3.5 Configuration CRUD Flow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Professor / Admin
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Config as Configuration Service
    participant Cosmos as Cosmos DB

    Admin->>UI: Navigate to Configuration
    UI->>APIM: GET /api/config/courses
    APIM->>Config: Forward (authenticated, RBAC: admin)
    Config->>Cosmos: Query courses container
    Cosmos-->>Config: Course[]
    Config-->>APIM: ApiEnvelope<Course[]>
    APIM-->>UI: 200 OK
    UI-->>Admin: Display course list

    Admin->>UI: Create new course
    UI->>APIM: POST /api/config/courses
    APIM->>Config: Forward (authenticated)
    Config->>Cosmos: Upsert course item
    Cosmos-->>Config: Created
    Config-->>APIM: ApiEnvelope<Course>
    APIM-->>UI: 201 Created
    UI-->>Admin: Course added to list
```

### 3.6 Agent Evaluation Flow (New)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Platform Admin
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant EvalSvc as Evaluation Service
    participant Foundry as Azure AI Foundry
    participant Cosmos as Cosmos DB

    Admin->>UI: Trigger agent evaluation run
    UI->>APIM: POST /api/evaluation/run
    APIM->>EvalSvc: Forward (authenticated)
    
    EvalSvc->>Cosmos: Load test dataset (golden Q&A pairs)
    EvalSvc->>Foundry: Create evaluation run
    
    loop For each test case
        Foundry->>Foundry: Execute target agent
        Foundry->>Foundry: Score with evaluator (groundedness, relevance, coherence, fluency)
    end
    
    Foundry-->>EvalSvc: EvaluationResult (scores, traces)
    EvalSvc->>Cosmos: Persist run results
    EvalSvc-->>APIM: EvaluationRunSummary
    APIM-->>UI: 200 OK + summary
    UI-->>Admin: Display quality dashboard (pass/fail, trends)
```

### 3.7 LMS Gateway Sync Flow (New)

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Cron / Event Trigger
    participant LMSGw as LMS Gateway Service
    participant ExtLMS as External LMS (Moodle/Canvas)
    participant Config as Configuration Service
    participant Cosmos as Cosmos DB

    Scheduler->>LMSGw: Trigger sync job
    LMSGw->>ExtLMS: GET /api/v1/courses (OAuth 2.0)
    ExtLMS-->>LMSGw: Courses + enrollments
    LMSGw->>LMSGw: Transform to Tutor schema
    LMSGw->>Config: POST /api/config/courses/bulk-sync
    Config->>Cosmos: Upsert courses + students
    Config-->>LMSGw: Sync result
    LMSGw->>Cosmos: Log sync audit trail
```

### 3.8 Supervisor Insight Report Flow (New)

```mermaid
sequenceDiagram
    autonumber
    actor Supervisor
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Insights as Insights Service
    participant Fabric as Microsoft Fabric
    participant OpenAI as Azure OpenAI
    participant Cosmos as Cosmos DB
    participant Entra as Entra ID / Graph

    Supervisor->>UI: Request pre-visit briefing for school
    UI->>APIM: POST /api/insights/briefing
    APIM->>Insights: Forward (authenticated, role=supervisor)

    Insights->>Entra: Resolve supervisor → assigned schools
    Entra-->>Insights: School scope (schoolIds[])
    Insights->>Insights: Validate requested school ∈ scope

    par Fetch indicators in parallel
        Insights->>Fabric: GET standardized assessment results (school, period)
        Insights->>Fabric: GET Attendance data (school, period)
        Insights->>Fabric: GET Task completion rates (school, period)
    end
    Fabric-->>Insights: Structured indicator data

    Insights->>Insights: Apply indicator strategies (trend, anomaly, delta)
    Insights->>OpenAI: Synthesize narrative briefing (indicators + context)
    OpenAI-->>Insights: Qualitative narrative (trends, alerts, focus points)

    Insights->>Cosmos: Persist briefing report
    Insights-->>APIM: InsightBriefing response
    APIM-->>UI: 200 OK + narrative report
    UI-->>Supervisor: Display Strava-like briefing cards
```

### 3.9 Pedagogical Content Ingestion Flow (New)

```mermaid
sequenceDiagram
    autonumber
    actor Teacher
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Content as Content Service
    participant Blob as Blob Storage
    participant DocIntel as AI Document Intelligence
    participant AISearch as Azure AI Search
    participant Cosmos as Cosmos DB

    Teacher->>UI: Upload pedagogical material (rubric, exemplar, template)
    UI->>APIM: POST /api/content/materials
    APIM->>Content: Forward (authenticated, role=teacher|admin)

    Content->>Blob: Store original document
    Content->>DocIntel: Extract text + structure (cloud OCR)
    DocIntel-->>Content: Extracted content

    Content->>Content: Chunk text into segments
    Content->>AISearch: Index chunks with embeddings (vector + keyword)
    AISearch-->>Content: Indexed document ID

    Content->>Cosmos: Persist material metadata (subject, grade, type, version)
    Content-->>APIM: MaterialMetadata response
    APIM-->>UI: 201 Created
    UI-->>Teacher: Material available for AI grounding
```

### 3.10 Guided Tutoring Flow (Chat Service)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant UI as Tutor UI (Essay Page)
    participant APIM as API Gateway
    participant Chat as Chat Service
    participant AISearch as Azure AI Search
    participant Config as Configuration Service
    participant OpenAI as Azure OpenAI
    participant Cosmos as Cosmos DB

    Student->>UI: Writing essay — pauses or types question
    UI->>APIM: POST /api/guide (courseId, context, question)
    APIM->>Chat: Forward (authenticated)

    Chat->>Config: Load pedagogical rules (topic, guardrails, limits)
    Config-->>Chat: Rules (max hints, forbidden answers, trigger thresholds)

    Chat->>AISearch: Query rubrics + exemplars relevant to topic
    AISearch-->>Chat: Pedagogical context for RAG

    Chat->>OpenAI: Generate guidance (with rules + context + student question)
    OpenAI-->>Chat: Guidance response (hint, not an answer)

    Chat->>Chat: Apply guardrails (no direct answers, respect limits)
    Chat->>Cosmos: Persist conversation turn
    Chat-->>APIM: GuidanceResponse
    APIM-->>UI: 200 OK + guidance
    UI-->>Student: Display guidance inline while writing
```

---

## 4. Deployment Topology (Current Runtime Substrate)

```mermaid
graph TB
    subgraph Azure["Azure Subscription"]
        subgraph RG["Resource Group: tutor-rg"]
            subgraph VNet["VNet (10.0.0.0/22)"]
                subgraph ACA_Subnet["ACA Subnet (10.0.0.0/23)"]
                    ACA_ENV["ACA Environment"]
                    
                    subgraph Platform["Platform Domain"]
                        CONFIG["config-svc"]
                        LMS_GW["lms-gateway"]
                        CONTENT["content-svc"]
                    end

                    subgraph Assessment["Assessment Domain"]
                        ESSAYS["essays-svc"]
                        QUESTIONS["questions-svc"]
                    end
                    
                    subgraph Interaction["Interaction Domain"]
                        AVATAR["avatar-svc"]
                        CHAT["chat-svc"]
                    end
                    
                    subgraph Analytics["Analytics Domain"]
                        UPSKILLING["upskilling-svc"]
                        EVALUATION["evaluation-svc"]
                    end

                    subgraph Supervision["Supervision Domain"]
                        INSIGHTS["insights-svc"]
                    end
                end
                
                subgraph PE_Subnet["Private Endpoints Subnet (10.0.2.0/24)"]
                    PE_COSMOS["PE: Cosmos DB"]
                    PE_OPENAI["PE: OpenAI"]
                    PE_SPEECH["PE: Speech"]
                    PE_BLOB["PE: Blob Storage"]
                    PE_KV["PE: Key Vault"]
                    PE_SEARCH["PE: AI Search"]
                    PE_DOCINTEL["PE: Document Intelligence"]
                end
            end
            
            COSMOS[("Cosmos DB — 5 databases")]
            OPENAI["Azure OpenAI"]
            SPEECH["Azure Speech"]
            BLOB["Blob Storage"]
            KV["Key Vault"]
            ACR["Container Registry"]
            LOG["Log Analytics"]
            APIM["API Management"]
            DOC_INTEL["AI Document Intelligence"]
            AI_SEARCH["Azure AI Search"]
        end
        
        FOUNDRY["AI Foundry Project\n(westus3, public endpoint,\nTerraform-managed — ADR-011)"]
        SWA["Static Web App (Frontend)"]
        ENTRA["Microsoft Entra ID"]
    end

    FABRIC["Microsoft Fabric\n(External Semantic Model)"]

    USER_S((Student)) --> SWA
    USER_T((Teacher)) --> SWA
    USER_SUP((Supervisor)) --> SWA
    SWA --> APIM
    APIM --> ACA_ENV

    INSIGHTS --> FABRIC
    
    PE_COSMOS --- COSMOS
    PE_OPENAI --- OPENAI
    PE_SPEECH --- SPEECH
    PE_BLOB --- BLOB
    PE_KV --- KV
    PE_SEARCH --- AI_SEARCH
    PE_DOCINTEL --- DOC_INTEL
    
    ACA_ENV --> ACR
    ACA_ENV --> LOG
```

---

## 5. Shared Library Architecture (Current Runtime)

Following the [holiday-peak-hub](https://github.com/Azure-Samples/holiday-peak-hub) reference, all services consume a shared `lib/` package.

```mermaid
graph TB
    subgraph lib["lib/ (tutor-lib)"]
        CONFIG["config/\nAppFactory, Settings"]
        COSMOS_MOD["cosmos/\nCosmosCRUD, repositories"]
        AGENTS["agents/\nChatAgent wrappers, AzureAIAgentClient\nOrchestration: Sequential · Concurrent · Handoff"]
        SCHEMAS["schemas/\nShared Pydantic models (Assembly, AgentRef)"]
        MIDDLEWARE["middleware/\nAuth, logging, error handling"]
        EVAL["evaluation/\nFoundryEvaluator client"]
        SEARCH["search/\nAI Search client wrapper"]
        DOCINTEL["document/\nDocument Intelligence client"]
        FABRIC_CLIENT["fabric/\nFabric REST API client"]
    end
    
    subgraph services["Service Layer (10 Container Apps)"]
        ESSAYS_SVC["essays-svc"]
        QUESTIONS_SVC["questions-svc"]
        AVATAR_SVC["avatar-svc"]
        CHAT_SVC["chat-svc"]
        UPSKILLING_SVC["upskilling-svc"]
        CONFIG_SVC["config-svc"]
        EVAL_SVC["evaluation-svc"]
        LMS_GW_SVC["lms-gateway"]
        CONTENT_SVC["content-svc"]
        INSIGHTS_SVC["insights-svc"]
    end
    
    ESSAYS_SVC --> lib
    QUESTIONS_SVC --> lib
    AVATAR_SVC --> lib
    CHAT_SVC --> lib
    UPSKILLING_SVC --> lib
    CONFIG_SVC --> lib
    EVAL_SVC --> lib
    LMS_GW_SVC --> lib
    CONTENT_SVC --> lib
    INSIGHTS_SVC --> lib
```

---

## 6. Wave 1 Data Model (Cosmos DB Partitioning)

```mermaid
erDiagram
    STUDENT {
        string id PK
        string tenantId "Partition Key L1"
        string courseId "Partition Key L2"
        string name
        string email
    }
    
    COURSE {
        string id PK
        string tenantId "Partition Key"
        string name
        string professorId
    }
    
    PEDAGOGICAL_RULE {
        string id PK
        string courseId "Partition Key"
        string type "topic|rubric|trigger|guardrail"
        object config
    }

    ESSAY_SUBMISSION {
        string id PK
        string courseId "Partition Key L1"
        string studentId "Partition Key L2"
        string strategy "ENEM|analytical|narrative|default"
        object evaluation
        string blobUri
        string ocrSource "handwritten|digital"
    }
    
    QUESTION_EVALUATION {
        string id PK
        string courseId "Partition Key L1"
        string studentId "Partition Key L2"
        string state
        string questionType "multiple_choice|discursive"
        object dimensions
        float confidence
    }
    
    MATERIAL {
        string id PK
        string subjectId "Partition Key L1"
        string gradeLevel "Partition Key L2"
        string type "rubric|exemplar|template"
        string blobUri
        string searchIndexId
        string version
    }

    INSIGHT_REPORT {
        string id PK
        string supervisorId "Partition Key L1"
        string schoolId "Partition Key L2"
        object indicators
        string narrative
        datetime generatedAt
    }

    INDICATOR_CONFIG {
        string id PK
        string tenantId "Partition Key"
        string type "standardized_test|attendance|task_completion"
        object thresholds
    }

    ASSEMBLY {
        string id PK
        string tenantId "Partition Key L1"
        string entityId "Partition Key L2 — essay, question, or avatar case"
        string entityType "essay | question | avatar"
        string topicName
        array agentRefs "list of AgentRef (Foundry agent_id + role + deployment)"
    }

    EVALUATION_RUN {
        string id PK
        string agentId "Partition Key — Foundry agent ID"
        string status
        object scores
        datetime timestamp
    }

    COURSE ||--o{ STUDENT : enrolls
    COURSE ||--o{ PEDAGOGICAL_RULE : defines
    STUDENT ||--o{ ESSAY_SUBMISSION : submits
    STUDENT ||--o{ QUESTION_EVALUATION : attempts
    COURSE ||--o{ ESSAY_SUBMISSION : contains
    COURSE ||--o{ QUESTION_EVALUATION : contains
    MATERIAL }o--o{ ESSAY_SUBMISSION : grounds
    INSIGHT_REPORT }o--|| INDICATOR_CONFIG : uses
    ASSEMBLY ||--o{ EVALUATION_RUN : evaluated_by
    ASSEMBLY }o--|| ESSAY_SUBMISSION : orchestrates
    ASSEMBLY }o--|| QUESTION_EVALUATION : orchestrates
```

---

## 7. Wave 1 Frontend Component Architecture

```mermaid
graph TB
    subgraph NextJS["Next.js 15 App Router"]
        LAYOUT["layout.tsx\n(DefaultLayout + Providers)"]
        
        subgraph Pages["App Pages"]
            HOME["/ (Dashboard)"]
            ESSAYS_PAGE["/essays"]
            QUESTIONS_PAGE["/questions"]
            AVATAR_PAGE["/avatar"]
            CONFIG_PAGE["/configuration"]
            EVAL_PAGE["/evaluation"]
            SUPERVISION_PAGE["/supervision (new)"]
            CONTENT_PAGE["/content (new)"]
        end
        
        subgraph Components["Component Library"]
            subgraph Assessment_UI["Assessment"]
                ESSAY_FORM["EssaySubmission\n(OCR upload + digital)"]
                QUESTION_FORM["StudentQuestionAnswer\n(MC + discursive)"]
            end
            
            subgraph Interaction_UI["Interaction"]
                AVATAR_COMP["Avatar (WebRTC)"]
                CHAT_COMP["ChatCard\n(guided tutoring)"]
            end
            
            subgraph Config_UI["Configuration"]
                LISTS["Lists (Essays, Questions)"]
                FORMS["Forms (Courses, Students)"]
                RULES["PedagogicalRules\n(topics, rubrics, guardrails)"]
            end
            
            subgraph Eval_UI["Evaluation"]
                EVAL_DASHBOARD["EvalDashboard"]
                EVAL_RUN["EvalRunViewer"]
                AVATAR_PARAMS["AvatarParameterSelector"]
            end

            subgraph Supervision_UI["Supervision (new)"]
                BRIEFING["BriefingReport\n(Strava-like narrative)"]
                SCHOOL_SELECT["SchoolSelector\n(scoped to supervisor)"]
                INDICATOR_TRENDS["IndicatorTrends\n(sparkline cards)"]
            end

            subgraph Content_UI["Content (new)"]
                MATERIAL_UPLOAD["MaterialUpload"]
                MATERIAL_LIST["MaterialLibrary"]
            end
        end
        
        subgraph State["State Management"]
            ZUSTAND["Zustand stores"]
            CONTEXTS["React contexts"]
        end
        
        subgraph API_Layer["API Layer"]
            API_CLIENTS["Typed axios clients\n(per service, 10 total)"]
        end
    end
    
    LAYOUT --> Pages
    Pages --> Components
    Components --> State
    Components --> API_Layer
```

---

## 8. Agentic Microservice Implementation Flows

This section documents the **as-implemented** internal architecture of each microservice, showing how design patterns, agent orchestration, and Azure service integrations are wired in code.

> **Foundry-First Architecture (ADR-011):** All agent definitions live in Azure AI Foundry as persistent agents with stable `agent_id` values. Services load agents from Foundry via `AzureAIAgentClient` and orchestrate them with Agent Framework rc3 patterns (`SequentialBuilder`, `ConcurrentBuilder`, `HandoffBuilder`). Cosmos DB stores **assemblies** — lightweight references that map Foundry agents to business entities (essays, questions, avatars). No backward compatibility shims exist; all services target Agent Framework `>=1.0.0rc3` with `azure-ai-projects>=2.0.0`.

### 8.1 Essays Service — Strategy + Orchestrator Pattern

The essays service uses a **Strategy pattern** to select the evaluation approach and an **Orchestrator** to compose OCR, RAG, and Foundry agent execution.

```mermaid
flowchart TD
    API["POST /grader/interaction\nPOST /essays/{id}/evaluate\nPATCH /essays/{id}"]
    ORCH["EssayOrchestrator.invoke()"]
    RESOLVER["StrategyResolver.resolve()"]
    LOAD_ASSEMBLY["_load_assembly()\nCosmos DB → Assembly"]

    subgraph Strategies["Strategy Selection"]
        ANALYTICAL["AnalyticalEssayStrategy"]
        NARRATIVE["NarrativeEssayStrategy"]
        DEFAULT["DefaultEssayStrategy"]
    end

    COMPOSE["PromptComposer.render()\nJinja2 template"]
    ATTACHMENTS["_build_image_attachments()\nBase64 → binary for vision"]
    FOUNDRY["FoundryAgentService.run_agent()\nAzure AI Foundry"]
    THREAD["Create thread → upload files\n→ send message → poll run"]
    PARSE["_parse_response()\n→ verdict, strengths, improvements"]
    RESULT["EssayEvaluationResult\n{strategy, verdict, strengths, improvements}"]

    API --> ORCH
    ORCH --> RESOLVER
    ORCH --> LOAD_ASSEMBLY
    RESOLVER -->|"theme=analytical"| ANALYTICAL
    RESOLVER -->|"objective=creative"| NARRATIVE
    RESOLVER -->|"fallback"| DEFAULT
    
    ANALYTICAL --> COMPOSE
    NARRATIVE --> COMPOSE
    DEFAULT --> COMPOSE
    COMPOSE --> ATTACHMENTS
    ATTACHMENTS --> FOUNDRY
    FOUNDRY --> THREAD
    THREAD --> PARSE
    PARSE --> RESULT
```

**Key integration points:**

- **Cosmos DB**: Assemblies (Foundry agent references), essays, resources
- **Blob Storage**: Original essay documents and resource files
- **Azure AI Foundry**: Agent execution via `AzureAIAgentClient` + `ChatAgent` (threads, messages, file uploads)
- **AI Document Intelligence**: OCR for handwritten essay scanning (required — no fallback)
- **AI Search** (target): RAG grounding for rubrics and exemplars
- **Agent Framework rc3**: `SequentialBuilder` for OCR → strategy → grading → synthesis pipeline
- **Partial updates**: `PATCH /essays/{id}` via `EssayPatch` model; `PUT` filters `None` values to prevent destructive overwrites of linked fields like `assembly_id`

---

### 8.2 Questions Service — State Machine Pattern

The questions service implements a **State Machine** for evaluation lifecycle with parallel agent dimension grading.

```mermaid
stateDiagram-v2
    [*] --> PendingState: evaluate_question() called
    PendingState --> EvaluatingState: transition()
    EvaluatingState --> CompletedState: all dimensions scored
    EvaluatingState --> EvaluatingState: confidence < threshold
    CompletedState --> [*]: return result
```

```mermaid
flowchart TD
    API["POST /grader/interaction"]
    MACHINE["QuestionStateMachine(assembly_id, question, answer)"]
    PENDING["PendingState.evaluate()"]
    EVALUATING["EvaluatingState.evaluate()"]

    subgraph Assembly["Assembly Loading"]
        COSMOS_READ["Cosmos DB → read assembly"]
        GRADERS["Extract Grader[] from assembly.agents"]
    end

    subgraph Parallel["Parallel Dimension Evaluation"]
        DIM1["Grader: dimension_1\nagent via AgentRegistry"]
        DIM2["Grader: dimension_2\nagent via AgentRegistry"]
        DIM_N["Grader: dimension_N\nagent via AgentRegistry"]
    end

    PROMPT["PromptComposer.render()\ncorrect.jinja + question + answer"]
    AGENT["AzureAIAgentClient(agent_id)\n→ ChatAgent from Foundry"]
    RUN["ChatAgent.run(prompt)\n→ AgentRunResponse"]
    CONFIDENCE["_infer_confidence(notes)"]
    COMPLETED["CompletedState(result)\nQuestionEvaluationResult"]

    API --> MACHINE --> PENDING
    PENDING -->|"transition()"| EVALUATING
    EVALUATING --> Assembly
    Assembly --> COSMOS_READ --> GRADERS
    GRADERS --> Parallel
    DIM1 --> PROMPT --> AGENT --> RUN
    DIM2 --> PROMPT
    DIM_N --> PROMPT
    RUN --> CONFIDENCE --> COMPLETED
```

**Key integration points:**

- **Cosmos DB**: Assemblies (Foundry agent references), questions, answers, graders
- **Azure AI Foundry**: Agent execution via Agent Framework rc3 (`ChatAgent` + `ConcurrentBuilder` for parallel dimensions)
- **Jinja2**: Prompt rendering with question/answer context per grading dimension

---

### 8.3 Avatar Service — Agent + Speech Pipeline

The avatar service orchestrates **conversational AI tutoring** backed by case profiles loaded from Cosmos DB.

```mermaid
flowchart TD
    API_RESP["POST /response"]
    API_PROF["GET /profile"]
    
    subgraph AvatarChat["AvatarChat Orchestrator"]
        RESOLVE["_resolve_case(case_id)\nCosmos → case with cache"]
        EVALUATE["_evaluate(case, prompt_data)"]
        HISTORY["_coerce_history()\nparse chat_history JSON"]
        SYSTEM_MSG["SIMULATION_PROMPT\nTemplate substitution:\nname, profile, role, steps, case, previous_chat"]
        AGENT_SPEC["AgentRef from Assembly\n(Foundry agent_id + deployment)"]
        REGISTRY["AzureAIAgentClient(agent_id)\n→ ChatAgent"]
        RUN_CTX["ChatAgent.run(prompt)\n→ AgentRunResponse"]
        EXTRACT["_extract_text(response)"]
    end

    subgraph CaseManagement["Case CRUD"]
        CREATE_CASE["POST /create-case"]
        LIST_CASES["GET /cases"]
        UPDATE_CASE["PUT /cases/{id}"]
        DELETE_CASE["DELETE /cases/{id}"]
        PATCH_STEPS["PATCH /cases/{id}/steps"]
        COSMOS_CRUD["CosmosCRUD\n(case_container)"]
    end

    API_RESP --> RESOLVE --> EVALUATE
    EVALUATE --> HISTORY --> SYSTEM_MSG
    SYSTEM_MSG --> AGENT_SPEC --> REGISTRY --> RUN_CTX --> EXTRACT

    API_PROF --> COSMOS_CRUD
    CREATE_CASE --> COSMOS_CRUD
    LIST_CASES --> COSMOS_CRUD
    UPDATE_CASE --> COSMOS_CRUD
    DELETE_CASE --> COSMOS_CRUD
    PATCH_STEPS --> COSMOS_CRUD
```

**Key integration points:**

- **Cosmos DB**: Case profiles (steps, patient data) for avatar persona
- **Azure AI Foundry** (via Agent Framework rc3): Conversation generation with `ChatAgent`
- **Azure Speech** (target): TTS/STT + WebRTC for voice interaction

---

### 8.4 Upskilling Service — Visitor Pattern with Async Iteration

The upskilling service evaluates professor lesson plans paragraph-by-paragraph using multiple **Visitor agents** and an **async iterator**.

```mermaid
flowchart TD
    API["POST /plans/{plan_id}/evaluate"]
    ORCH["PlanEvaluationOrchestrator.evaluate(request)"]
    CTX["PlanContext\n{timeframe, topic, class_id, performance_history}"]
    ITER["PlanEvaluationIterable\n→ PlanEvaluationIterator"]

    subgraph Paragraph["For Each Paragraph"]
        ELEMENT["PlanParagraphElement(index, paragraph, context)"]
        
        subgraph Visitors["Visitor Agents (sequential per paragraph)"]
            PERF["PerformanceInsightVisitor\nagent: performance-analyst\ntemplate: performance.jinja"]
            CONTENT["ContentComplexityVisitor\nagent: content-curator\ntemplate: content_complexity.jinja"]
            GUIDANCE["GuidanceCoachVisitor\nagent: guidance-coach\ntemplate: guidance.jinja"]
        end

        ACCEPT["element.accept(visitor)\n→ AgentFeedback"]
    end

    PROMPT["PromptComposer.render()\nJinja2 template with paragraph + context"]
    AGENT_RUN["ChatAgent.run(prompt) via AzureAIAgentClient\nFoundry agent loaded by agent_id"]
    PARSE["_parse_feedback(text)\n→ verdict, strengths, improvements"]
    EVAL["ParagraphEvaluation\n{paragraph_index, title, feedback[]}"]
    RESULT["PlanEvaluationResponse\n{timeframe, topic, evaluations[]}"]

    API --> ORCH --> CTX --> ITER
    ITER -->|"async for"| Paragraph
    ELEMENT --> ACCEPT
    ACCEPT --> PERF
    ACCEPT --> CONTENT
    ACCEPT --> GUIDANCE
    PERF --> PROMPT --> AGENT_RUN --> PARSE --> EVAL
    CONTENT --> PROMPT
    GUIDANCE --> PROMPT
    EVAL --> RESULT
```

**Key integration points:**

- **Azure AI Foundry**: Three specialized agents per paragraph evaluation (loaded by Foundry agent_id)
- **Jinja2**: Template-driven prompt composition with performance history context
- **tutor_lib**: Shared `ChatAgent` wrappers, `AzureAIAgentClient`, `Assembly` models

---

### 8.5 Configuration Service — Repository + Bulk Sync

The configuration service manages roster data with a **repository pattern** and provides bulk LMS synchronization.

```mermaid
flowchart TD
    subgraph CRUD["Entity CRUD Operations"]
        direction TB
        STUDENTS["POST/GET /students"]
        PROFS["POST/GET /professors"]
        COURSES["POST/GET /courses"]
        CLASSES["POST/GET /classes"]
        GROUPS["POST/GET /groups"]
        ASSIGN["POST /groups/{id}/assign-cases"]
    end

    subgraph BulkSync["LMS Bulk Sync"]
        BULK_API["POST /lms/bulk-sync"]
        PAYLOAD["BulkRosterSyncRequest\n{students[], professors[], courses[], classes[], groups[]}"]
        BULK_FN["_bulk_create(container, items)\nSequential CosmosCRUD.create_item()"]
        COUNTS["Response: counts per entity type"]
    end

    AUTH["require_professor()\nX-User-Id header check"]
    CRUD_FN["_crud(container)\nCosmosCRUD (lru_cached)"]
    COSMOS["Azure Cosmos DB\n(per-entity containers)"]

    STUDENTS --> AUTH --> CRUD_FN --> COSMOS
    PROFS --> AUTH
    COURSES --> AUTH
    CLASSES --> AUTH
    GROUPS --> AUTH
    ASSIGN --> AUTH

    BULK_API --> AUTH --> PAYLOAD --> BULK_FN --> COSMOS
    BULK_FN --> COUNTS
```

---

### 8.6 LMS Gateway — Adapter + Background Job Queue

The LMS gateway implements the **Adapter pattern** for external LMS providers and a **background job queue** for async sync operations.

```mermaid
flowchart TD
    subgraph Endpoints
        SYNC["POST /lms/sync\n(immediate)"]
        SCHEDULE["POST /lms/sync/schedule\n(background)"]
        STATUS["GET /lms/sync/jobs/{job_id}"]
    end

    subgraph Adapters["Adapter Pattern"]
        BASE["BaseLMSAdapter (ABC)\nget_courses, get_students,\nget_assignments, push_scores"]
        MOODLE["MoodleAdapter\nprovider=moodle\nhttpx → /api/v1/*"]
        CANVAS["CanvasAdapter\nprovider=canvas\nhttpx → /api/v1/*"]
    end

    subgraph Jobs["Background Job Queue"]
        QUEUE["SyncJobQueue"]
        CREATE_JOB["create_job(adapter)\n→ SyncJob(status=queued)"]
        BG_TASK["run_in_background(job, adapter)\nasyncio.create_task"]
        RUN_JOB["_run_job()\nqueued → running → completed/failed"]
        EXECUTE["_execute_sync(adapter)\n→ SyncResult"]
    end

    subgraph Store["Job Persistence"]
        STORE_ABC["SyncJobStore (ABC)"]
        MEM_STORE["InMemorySyncJobStore"]
        COSMOS_STORE["CosmosSyncJobStore\ndocType=lms_sync_job"]
    end

    SETTINGS["LMSGatewaySettings\nMoodle/Canvas URL + token\n(env vars)"]

    SYNC --> MOODLE
    SYNC --> CANVAS
    SCHEDULE --> CREATE_JOB --> BG_TASK --> RUN_JOB --> EXECUTE
    EXECUTE --> MOODLE
    EXECUTE --> CANVAS
    STATUS --> QUEUE

    BASE --> MOODLE
    BASE --> CANVAS
    QUEUE --> STORE_ABC
    STORE_ABC --> MEM_STORE
    STORE_ABC --> COSMOS_STORE

    SETTINGS --> MOODLE
    SETTINGS --> CANVAS
```

**Key integration points:**

- **External LMS APIs**: Moodle and Canvas via HTTP (`httpx`)
- **Cosmos DB**: Job persistence with `CosmosSyncJobStore` (docType-filtered)
- **Environment**: `LMS_JOB_STORE=memory|cosmos` for store selection

---

### 8.7 Evaluation Service — Dataset + Run Orchestration

The evaluation service manages **golden datasets** and **evaluation runs** for agent quality measurement.

```mermaid
flowchart TD
    subgraph DatasetOps["Dataset Management"]
        CREATE_DS["POST /datasets\nDatasetRequest → DatasetRecord"]
        LIST_DS["GET /datasets\n→ DatasetRecord[]"]
    end

    subgraph RunOps["Evaluation Run Lifecycle"]
        START_RUN["POST /evaluation/run\nRunRequest(agent_id, dataset_id)"]
        GET_RUN["GET /evaluation/run/{run_id}\n→ RunRecord"]
        VALIDATE["Verify dataset exists\n404 if not found"]
        CREATE_RUN["RunRecord(\nrun_id, agent_id, dataset_id,\nstatus=queued, total_cases)"]
    end

    subgraph Repository["Repository Abstraction"]
        REPO_ABC["EvaluationRepository (ABC)"]
        MEM_REPO["InMemoryEvaluationRepository\ndict-based"]
        COSMOS_REPO["CosmosEvaluationRepository\ndocType=dataset|run"]
    end

    ENV["EVALUATION_REPOSITORY=memory|cosmos"]

    CREATE_DS --> REPO_ABC
    LIST_DS --> REPO_ABC
    START_RUN --> VALIDATE --> CREATE_RUN --> REPO_ABC
    GET_RUN --> REPO_ABC

    REPO_ABC --> MEM_REPO
    REPO_ABC --> COSMOS_REPO
    ENV --> REPO_ABC
```

**Integration** (evaluation execution pipeline):

- **Azure AI Foundry**: Execute target agent against golden dataset cases via `AzureAIAgentClient`
- **Foundry Evaluators**: Score with groundedness, relevance, coherence, fluency
- **Cosmos DB**: Persist run results and quality trend data
- **Agent Framework rc3**: `SequentialBuilder` for agent run → evaluator run → metric collection

---

### 8.8 Chat Service — Guided Tutoring (Scaffold)

The chat service is scaffolded for **guided writing support** that provides hints without direct answers.

```mermaid
flowchart TD
    API["POST /guide"]
    REQ["GuidanceRequest\n{student_id, course_id, prompt}"]
    HEALTH["GET /health"]

    subgraph Target["Target Architecture"]
        RULES["config-svc → Load pedagogical rules\n(guardrails, triggers, limits)"]
        RAG["AI Search → Query rubrics + exemplars"]
        LLM["Azure OpenAI → Generate guidance\n(hint, not answer)"]
        GUARD["Apply guardrails\n(no direct answers, respect limits)"]
        PERSIST["Cosmos DB → Persist conversation turn"]
    end

    API --> REQ
    REQ -->|"current: stub response"| RESPONSE["Static guidance string"]
    REQ -.->|"target: full pipeline"| RULES --> RAG --> LLM --> GUARD --> PERSIST
    HEALTH --> OK["status: ok"]
```

---

### 8.9 Platform Integration Overview

This diagram shows how all **implemented** services connect through the shared infrastructure.

```mermaid
graph TB
    subgraph Frontend["Next.js SPA"]
        UI["Tutor UI\n(Static Web App)"]
    end

    subgraph Platform["Platform Domain"]
        CONFIG["config-svc\nFastAPI :8081\nRepository Pattern"]
        LMS_GW["lms-gateway\nFastAPI :8087\nAdapter + Job Queue"]
    end

    subgraph Assessment["Assessment Domain"]
        ESSAYS["essays-svc\nFastAPI :8083\nStrategy + Orchestrator"]
        QUESTIONS["questions-svc\nFastAPI :8082\nState Machine"]
    end

    subgraph Interaction["Interaction Domain"]
        AVATAR["avatar-svc\nFastAPI :8084\nAgent + Speech"]
        CHAT["chat-svc\nFastAPI :8088\nGuided Tutoring"]
    end

    subgraph Analytics["Analytics Domain"]
        UPSKILLING["upskilling-svc\nFastAPI :8085\nVisitor Pattern"]
        EVALUATION["evaluation-svc\nFastAPI :8086\nDataset + Run Pipeline"]
    end

    subgraph SharedLib["tutor-lib"]
        LIB_CONFIG["config/\nSettings, AppFactory"]
        LIB_COSMOS["cosmos/\nCosmosCRUD"]
        LIB_AGENTS["agents/\nChatAgent, AzureAIAgentClient\nSequentialBuilder, ConcurrentBuilder"]
    end

    subgraph Azure["Azure Services"]
        COSMOS[("Cosmos DB")]
        FOUNDRY["AI Foundry\n(Agents)"]
        OPENAI["Azure OpenAI"]
        SPEECH["Azure Speech"]
        BLOB["Blob Storage"]
    end

    subgraph External["External"]
        EXT_LMS["Moodle / Canvas\nLMS APIs"]
    end

    UI --> CONFIG & ESSAYS & QUESTIONS & AVATAR & CHAT & UPSKILLING & EVALUATION

    CONFIG --> LIB_CONFIG & LIB_COSMOS --> COSMOS
    LMS_GW --> LIB_CONFIG
    LMS_GW --> EXT_LMS
    LMS_GW --> COSMOS

    ESSAYS --> LIB_COSMOS & LIB_AGENTS
    ESSAYS --> COSMOS & FOUNDRY & BLOB

    QUESTIONS --> LIB_COSMOS & LIB_AGENTS
    QUESTIONS --> COSMOS & FOUNDRY

    AVATAR --> LIB_COSMOS
    AVATAR --> COSMOS & OPENAI & SPEECH

    UPSKILLING --> LIB_AGENTS
    UPSKILLING --> FOUNDRY

    EVALUATION --> LIB_COSMOS
    EVALUATION --> COSMOS
```

---

### 8.10 Design Pattern Summary

| Service | Pattern | Agent Framework (rc3) | Orchestration | Persistence | External AI |
| ------- | ------- | --------------------- | ------------- | ----------- | ----------- |
| **essays-svc** | Strategy + Orchestrator | `ChatAgent` via `AzureAIAgentClient` | `SequentialBuilder` (OCR → strategy → grading → synthesis) | Cosmos DB (assemblies) + Blob | AI Foundry, Doc Intel, AI Search |
| **questions-svc** | State Machine | `ChatAgent` via `AzureAIAgentClient` | `ConcurrentBuilder` (parallel dimension grading) | Cosmos DB (assemblies) | AI Foundry |
| **avatar-svc** | Agent + Speech | `ChatAgent` via `AzureAIAgentClient` | Single agent with conversation memory | Cosmos DB (cases) | AI Foundry, Speech |
| **upskilling-svc** | Visitor + Async Iterator | `ChatAgent` via `AzureAIAgentClient` | `ConcurrentBuilder` (visitors) → `SequentialBuilder` (aggregation) | Cosmos DB | AI Foundry |
| **config-svc** | Repository + Bulk Sync | N/A (non-agentic) | N/A | Cosmos DB | None |
| **lms-gateway** | Adapter + Job Queue | N/A (non-agentic) | N/A | Cosmos DB | External LMS APIs |
| **evaluation-svc** | Dataset + Run Pipeline | Foundry Evaluators | `SequentialBuilder` (agent run → evaluator → metrics) | Cosmos DB | AI Foundry |
| **chat-svc** | Guided Tutoring (scaffold) | `ChatAgent` via `AzureAIAgentClient` | Single agent with guardrails | Cosmos DB | AI Foundry, AI Search |
