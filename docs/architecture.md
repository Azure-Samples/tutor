# Architecture

> Target architecture for **The Tutor** — a multi-agent LMS-enhancer platform that integrates with existing educational ecosystems. This document describes every major flow using Mermaid diagrams and explains the system topology after modernization.

---

## 1. High-Level System Context

The Tutor operates within an existing educational ecosystem as an **AI enhancement layer** for the host LMS. It serves three primary personas: **students** (AI-assisted learning), **teachers** (AI-corrected assessments + pedagogical content), and **supervisors** (data-driven school supervision with narrative insight reports).

```mermaid
C4Context
    title System Context — The Tutor LMS Enhancer

    Person(student, "Student", "Learner: essays, questions, avatar tutoring")
    Person(teacher, "Teacher / Coordinator", "Configures rubrics, reviews evaluations")
    Person(supervisor, "Supervisor", "Pre-visit briefings, school insight reports")

    System(tutor, "The Tutor Platform", "Multi-agent LMS enhancer")
    System_Ext(escola_total, "External LMS Platform", "Source of truth: enrollment, grades, assignments")
    System_Ext(fabric, "Microsoft Fabric", "Semantic model: standardized assessments, attendance, task completion")
    System_Ext(azure_ai, "Azure AI Services", "OpenAI, Speech, Document Intelligence, AI Search, AI Foundry")
    System_Ext(identity, "Microsoft Entra ID", "Identity & access management with role-based scoping")

    Rel(student, tutor, "Submits essays (handwritten + digital), answers questions, chats with tutor")
    Rel(teacher, tutor, "Uploads pedagogical materials, configures rubrics and rules")
    Rel(supervisor, tutor, "Requests pre-visit briefings, reviews school insight reports")
    Rel(tutor, escola_total, "Syncs courses, students, assignments via LMS Gateway")
    Rel(tutor, fabric, "Reads educational indicators (standardized assessments, attendance, task completion)")
    Rel(tutor, azure_ai, "LLM inference, OCR, vector search, speech, agent evaluation")
    Rel(tutor, identity, "Authenticates via OAuth 2.0 / OIDC, enforces supervisor school scoping")
```

---

## 2. Container Diagram (Target State)

After modernization, the system is decomposed into **five business domains** with a **shared library** and centralized infrastructure. Two new domains (Supervision, Content) address the core business agendas directly.

```mermaid
C4Container
    title Container Diagram — The Tutor Platform

    Person(student, "Student")
    Person(teacher, "Teacher")
    Person(supervisor, "Supervisor")

    Container_Boundary(frontend_boundary, "Frontend") {
        Container(ui, "Tutor UI", "Next.js 15 / React 19", "SPA hosted on Azure Static Web Apps")
    }

    Container_Boundary(gateway, "API Gateway") {
        Container(apim, "API Management", "Azure APIM", "Rate limiting, auth, routing")
    }

    Container_Boundary(platform_domain, "Platform Domain (Non-Agentic)") {
        Container(config_svc, "Configuration Service", "FastAPI / ACA", "CRUD: students, courses, pedagogical rules")
        Container(lms_gateway, "LMS Gateway", "FastAPI / ACA", "Adapter for external LMS sync")
        Container(content_svc, "Content Service", "FastAPI / ACA", "Pedagogical material ingestion & RAG index")
    }

    Container_Boundary(assessment_domain, "Assessment Domain (Agentic)") {
        Container(essays_svc, "Essays Service", "FastAPI / ACA", "Strategy-based essay evaluation + OCR + ENEM")
        Container(questions_svc, "Questions Service", "FastAPI / ACA", "State-machine question grading + discursive")
    }

    Container_Boundary(interaction_domain, "Interaction Domain (Agentic)") {
        Container(avatar_svc, "Avatar Service", "FastAPI / ACA", "Speech-driven avatar tutoring")
        Container(chat_svc, "Chat Service", "FastAPI / ACA", "Guided text tutoring during writing")
    }

    Container_Boundary(analytics_domain, "Analytics Domain (Agentic)") {
        Container(upskilling_svc, "Upskilling Service", "FastAPI / ACA", "Performance & guidance analysis")
        Container(evaluation_svc, "Evaluation Service", "FastAPI / ACA", "Agent quality evaluation via Foundry")
    }

    Container_Boundary(supervision_domain, "Supervision Domain (Agentic)") {
        Container(insights_svc, "Insights Service", "FastAPI / ACA", "Supervisor briefings from Fabric indicators")
    }

    Container_Boundary(data, "Data Layer") {
        ContainerDb(cosmos, "Azure Cosmos DB", "NoSQL", "5 databases with HPK")
        ContainerDb(blob, "Azure Blob Storage", "Object Store", "Essays, pedagogical materials")
    }

    Container_Boundary(ai, "AI Services (Cloud Only)") {
        Container(openai, "Azure OpenAI", "GPT-4o", "LLM inference")
        Container(speech, "Azure Speech", "TTS/STT", "Avatar voice")
        Container(foundry, "Azure AI Foundry", "Agents", "Agent orchestration & evaluation")
        Container(doc_intel, "AI Document Intelligence", "OCR", "Handwritten essay scanning")
        Container(ai_search, "Azure AI Search", "Vector Index", "RAG over pedagogical materials")
    }

    Container_Boundary(external, "External Systems") {
        Container(fabric, "Microsoft Fabric", "Semantic Model", "Standardized assessments, attendance, task completion")
    }

    Rel(student, ui, "HTTPS")
    Rel(teacher, ui, "HTTPS")
    Rel(supervisor, ui, "HTTPS")
    Rel(ui, apim, "REST / WebSocket")
    Rel(apim, essays_svc, "")
    Rel(apim, questions_svc, "")
    Rel(apim, avatar_svc, "")
    Rel(apim, chat_svc, "")
    Rel(apim, upskilling_svc, "")
    Rel(apim, evaluation_svc, "")
    Rel(apim, config_svc, "")
    Rel(apim, lms_gateway, "")
    Rel(apim, content_svc, "")
    Rel(apim, insights_svc, "")

    Rel(essays_svc, cosmos, "")
    Rel(essays_svc, blob, "")
    Rel(essays_svc, foundry, "")
    Rel(essays_svc, doc_intel, "OCR handwritten essays")
    Rel(essays_svc, ai_search, "RAG: rubrics & exemplars")
    Rel(questions_svc, cosmos, "")
    Rel(questions_svc, foundry, "")
    Rel(questions_svc, ai_search, "RAG: pedagogical context")
    Rel(avatar_svc, cosmos, "")
    Rel(avatar_svc, openai, "")
    Rel(avatar_svc, speech, "")
    Rel(chat_svc, cosmos, "")
    Rel(chat_svc, openai, "")
    Rel(chat_svc, ai_search, "RAG: guided tutoring context")
    Rel(upskilling_svc, cosmos, "")
    Rel(evaluation_svc, foundry, "")
    Rel(insights_svc, fabric, "Read educational indicators")
    Rel(insights_svc, openai, "Narrative synthesis")
    Rel(insights_svc, cosmos, "")
    Rel(content_svc, blob, "Store materials")
    Rel(content_svc, doc_intel, "Extract text from uploads")
    Rel(content_svc, ai_search, "Index for RAG")
    Rel(config_svc, cosmos, "")
    Rel(lms_gateway, cosmos, "")
```

---

## 3. Service Interaction Flows

### 3.1 Essay Evaluation Flow (with OCR + ENEM)

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

    alt Handwritten essay (image/PDF)
        Essays->>DocIntel: OCR extraction (cloud)
        DocIntel-->>Essays: Extracted text + layout
    end

    Essays->>Essays: Select strategy (ENEM/analytical/narrative/default)
    Essays->>AISearch: Query rubrics + exemplars for grounding (RAG)
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

### 3.4 Upskilling Analysis Flow

```mermaid
sequenceDiagram
    autonumber
    actor Professor
    participant UI as Tutor UI
    participant APIM as API Gateway
    participant Upskilling as Upskilling Service
    participant Cosmos as Cosmos DB
    participant Foundry as Azure AI Foundry

    Professor->>UI: Request student performance analysis
    UI->>APIM: GET /api/upskilling/analyze/{studentId}
    APIM->>Upskilling: Forward (authenticated)
    Upskilling->>Cosmos: Fetch student evaluations history
    
    par Visitor Pattern — parallel analysis
        Upskilling->>Upskilling: PerformanceVisitor.visit()
        Upskilling->>Upskilling: ContentComplexityVisitor.visit()
        Upskilling->>Upskilling: GuidanceCoachVisitor.visit()
    end
    
    Upskilling->>Foundry: Generate upskilling recommendations
    Foundry-->>Upskilling: Personalized learning path
    Upskilling->>Cosmos: Persist analysis
    Upskilling-->>APIM: UpskillingReport
    APIM-->>UI: 200 OK + report
    UI-->>Professor: Display recommendations dashboard
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
    UI->>APIM: POST /api/chat/guide (courseId, context, question)
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

## 4. Deployment Topology

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
            FOUNDRY["AI Foundry Project"]
            DOC_INTEL["AI Document Intelligence"]
            AI_SEARCH["Azure AI Search"]
        end
        
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

## 5. Shared Library Architecture

Following the [holiday-peak-hub](https://github.com/Azure-Samples/holiday-peak-hub) reference, all services consume a shared `lib/` package.

```mermaid
graph TB
    subgraph lib["lib/ (tutor-lib)"]
        CONFIG["config/\nAppFactory, Settings"]
        COSMOS_MOD["cosmos/\nCosmosCRUD, repositories"]
        AGENTS["agents/\nAgentBuilder, BaseAgent"]
        SCHEMAS["schemas/\nShared Pydantic models"]
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

## 6. Data Model (Cosmos DB Partitioning)

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

    AGENT_CONFIG {
        string id PK
        string tenantId "Partition Key"
        string type
        object parameters
    }
    
    EVALUATION_RUN {
        string id PK
        string agentId "Partition Key"
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
    AGENT_CONFIG ||--o{ EVALUATION_RUN : evaluated_by
```

---

## 7. Frontend Component Architecture

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

### 8.1 Essays Service — Strategy + Orchestrator Pattern

The essays service uses a **Strategy pattern** to select the evaluation approach and an **Orchestrator** to compose OCR, RAG, and Foundry agent execution.

```mermaid
flowchart TD
    API["POST /grader/interaction\nPOST /essays/{id}/evaluate"]
    ORCH["EssayOrchestrator.invoke()"]
    RESOLVER["StrategyResolver.resolve()"]
    LOAD_SWARM["_load_swarm()\nCosmos DB → Assembly"]

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
    ORCH --> LOAD_SWARM
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

- **Cosmos DB**: Assemblies (agent configurations), essays, resources
- **Blob Storage**: Original essay documents and resource files
- **Azure AI Foundry**: Agent execution via `AgentsClient` (threads, messages, file uploads)
- **AI Document Intelligence** (target): OCR for handwritten essay scanning
- **AI Search** (target): RAG grounding for rubrics and exemplars

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
    AGENT["AgentRegistry.create(AgentSpec)\n→ ChatAgent"]
    RUN["AgentRunContext.run(prompt)"]
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

- **Cosmos DB**: Assemblies, questions, answers, graders
- **Azure AI Foundry**: Agent execution via Microsoft Agent Framework (`ChatAgent`)
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
        AGENT_SPEC["AgentSpec(\nname, instructions, deployment, temperature)"]
        REGISTRY["AgentRegistry.create(spec)\n→ ChatAgent"]
        RUN_CTX["AgentRunContext.run(prompt)\n→ AgentRunResponse"]
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
- **Azure OpenAI** (via Agent Framework): Conversation generation
- **Azure Speech** (target): TTS/STT + WebRTC for voice interaction

---

### 8.4 Upskilling Service — Visitor Pattern with Async Iteration

The upskilling service evaluates professor lesson plans paragraph-by-paragraph using multiple **Visitor agents** and an **async iterator**.

```mermaid
flowchart TD
    API["POST /plan/evaluate"]
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
    AGENT_RUN["AgentRunContext.run(prompt)\nvia AgentRegistry → ChatAgent"]
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

- **Azure AI Foundry**: Three specialized agents per paragraph evaluation
- **Jinja2**: Template-driven prompt composition with performance history context
- **tutor_lib**: Shared `AgentRegistry`, `AgentRunContext`, `AgentSpec`

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

**Target integration** (evaluation execution pipeline):

- **Azure AI Foundry**: Execute target agent against golden dataset cases
- **Foundry Evaluators**: Score with groundedness, relevance, coherence, fluency
- **Cosmos DB**: Persist run results and quality trend data

---

### 8.8 Chat Service — Guided Tutoring (Scaffold)

The chat service is scaffolded for **guided writing support** that provides hints without direct answers.

```mermaid
flowchart TD
    API["POST /chat/guide"]
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
        LIB_AGENTS["agents/\nAgentRegistry, AgentRunContext"]
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

| Service | Pattern | Agent Framework | Persistence | External AI |
|---------|---------|-----------------|-------------|-------------|
| **essays-svc** | Strategy + Orchestrator | FoundryAgentService (threads + files) | Cosmos DB + Blob | AI Foundry, Doc Intel, AI Search |
| **questions-svc** | State Machine | AgentRegistry + AgentRunContext | Cosmos DB | AI Foundry |
| **avatar-svc** | Agent + Speech | AgentRegistry + AgentRunContext | Cosmos DB | OpenAI, Speech |
| **upskilling-svc** | Visitor + Async Iterator | AgentRegistry + AgentRunContext | Cosmos DB | AI Foundry |
| **config-svc** | Repository + Bulk Sync | N/A (non-agentic) | Cosmos DB | None |
| **lms-gateway** | Adapter + Job Queue | N/A (non-agentic) | Cosmos DB | External LMS APIs |
| **evaluation-svc** | Dataset + Run Pipeline | Foundry Evaluators (target) | Cosmos DB | AI Foundry (target) |
| **chat-svc** | Guided Tutoring (scaffold) | OpenAI + RAG (target) | Cosmos DB (target) | OpenAI, AI Search |
