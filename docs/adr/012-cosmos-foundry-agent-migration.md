# ADR-012: Cosmos-to-Foundry Agent Migration Implementation

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-16 |
| **Deciders** | Platform team |
| **Implements** | ADR-011 (Foundry-First Agent Architecture) |
| **Tracking** | [Issue #49](https://github.com/Azure-Samples/tutor/issues/49) |

---

## Context

ADR-011 established the architectural vision: agent definitions must live in Azure AI Foundry; Cosmos DB retains only orchestration topology and domain data. Before this migration, each microservice carried its own copy of agent-client code, agent schemas bundled full instructions and names into Cosmos documents, and there was no shared surface for Foundry operations. Concretely:

1. **Duplicated agent-client code** — `essays-svc` and `questions-svc` each contained a local `FoundryAgentService` with identical create/run/delete logic, making bug-fixes a multi-repo affair.
2. **Heavyweight Cosmos documents** — agent records stored `name`, `instructions`, `deployment`, and `temperature` inside Cosmos assemblies, creating a second source of truth that drifted from Foundry state.
3. **Brittle agent selection** — essays-svc picked an evaluation strategy by keyword-searching the `instructions` field, coupling orchestration logic to prompt prose.
4. **Missing `role`/`dimension` semantics** — no first-class field existed to express an agent's purpose within an assembly; selection relied on positional assumptions or instruction parsing.
5. **Frontend drift** — TypeScript types still reflected the heavyweight Cosmos shapes, causing form fields to expose stale properties.

This ADR documents the concrete implementation that resolves these problems.

---

## Decision

### 1. Shared Library Promotion — `tutor_lib.agents`

`FoundryAgentService` and `AgentAttachment` were promoted from `apps/essays/src/app/agents/clients.py` to `lib/src/tutor_lib/agents/clients.py`. The shared module exports:

| Symbol | Purpose |
|--------|---------|
| `FoundryAgentService` | Wraps `AIProjectClient.agents` — `create_agent`, `delete_agent`, `run_agent`, `get_agent`, `list_agents` |
| `AgentAttachment` | Binary payload dataclass (file_name, content_type, payload, purpose, tool_type) |
| `AgentRegistry` | Factory that creates `ChatAgent` instances via `AzureAIAgentClient` (retained for backward-compatible orchestration during transition) |
| `AgentRunContext` | Wrapper that executes a `ChatAgent` and returns the response |
| `AgentSpec` | Dataclass specifying name, instructions, deployment, tools, temperature |

All six microservices now import from `tutor_lib.agents` — no service maintains a local agent-client copy.

### 2. Essays Service — Lightweight `AgentRef` + Role-Based Selection

**Schema changes:**

```python
class AgentRef(BaseModel):
    """Lightweight reference stored in Cosmos — agent lives in Foundry."""
    agent_id: str       # Azure AI Foundry agent ID
    role: str           # "analytical" | "narrative" | "default"
    deployment: str     # Model deployment name

class AgentDefinition(BaseModel):
    """Full definition used for Foundry provisioning (create/update)."""
    agent_id: Optional[str]   # Omit to create new
    name: str
    instructions: str
    deployment: str
    role: str                 # Strategy selection key
    temperature: Optional[float]
```

**Behavioral changes:**

- `_materialize_agent()` provisions in Foundry, returns lightweight `AgentRef` (no instructions in Cosmos).
- `_select_agent()` matches on `agent.role` instead of keyword-searching instructions.
- `evaluate()` invokes Foundry agents via `FoundryAgentService.run_agent(agent_id, prompt)`.
- `_hydrate_agents()` includes a legacy `id` field fallback for reading existing Cosmos documents written before migration.

### 3. Questions Service — Lightweight `Grader` + Dimension-Based Selection

**Schema changes:**

```python
class Grader(BaseModel):
    """Lightweight reference stored in Cosmos."""
    agent_id: str       # Azure AI Foundry agent ID
    dimension: str      # Evaluation dimension (e.g. "grammar", "reasoning")
    deployment: str     # Model deployment name

class GraderDefinition(BaseModel):
    """Full definition used for Foundry provisioning."""
    agent_id: Optional[str]
    name: str
    instructions: str
    deployment: str
    dimension: str

class AssemblyDefinition(BaseModel):
    """Payload for assembly create/update — carries full GraderDefinitions."""
    id: str
    topic_name: str
    agents: List[GraderDefinition]
```

**Behavioral changes:**

- `create_assembly` and `update_assembly` endpoints provision agents in Foundry before storing the lightweight `Assembly` (with `Grader` refs) in Cosmos.
- `QuestionStateMachine` uses `FoundryAgentService` directly, replacing `AgentRegistry`.
- `_run_dimension()` calls `agent_service.run_agent(grader.agent_id, prompt)` — returns a string result.
- `ensure_assembly()` includes a legacy `id`→`agent_id` fallback for existing Cosmos documents.

### 4. Frontend Alignment

TypeScript types updated to match the new backend schemas:

| Type | Key change |
|------|-----------|
| `AgentRef` | `{agent_id, role, deployment}` — no instructions/name |
| `AgentDefinition` | Gains `role: string` field |
| `Grader` | `{agent_id, dimension, deployment}` — replaces `id, name, instructions, deployment` |
| `GraderDefinition` | Full definition shape for create/update forms |

Five React components updated for new field names: `Agent.tsx` (role dropdown), `Assemblies.tsx` (role/dimension display), `Essays.tsx` (agent_id display), `Lists/Assemblies.tsx`, `Lists/Essays.tsx`.

### 5. Seed Data Migration

`scripts/seed_demo_data.py` updated:

- `EssayAgent` gains `role: str` — all 18 instances given explicit roles (`default`, `narrative`, `analytical`).
- `QuestionGrader.id` renamed to `agent_id` — all 11 instances use the new field.

### 6. Test Infrastructure

- All test mocks updated to match new schemas (`agent_id`, `role`, `dimension` fields).
- Cross-service `sys.path` contamination fixed: module-level path inserts moved to fixtures; force-insert pattern replaces check-before-insert to prevent import resolution conflicts.
- Full suite: 39/39 tests passing.

---

## Consequences

### Positive

- **Single source of truth** — agent instructions live exclusively in Foundry; Cosmos stores only lightweight references (`agent_id` + `role`/`dimension` + `deployment`).
- **Eliminated code duplication** — one `FoundryAgentService` in `tutor_lib.agents`, six consumers.
- **Semantic agent selection** — `role` (essays) and `dimension` (questions) replace fragile instruction-keyword matching.
- **Backward-compatible reads** — legacy Cosmos documents with `id` instead of `agent_id` are hydrated transparently; no data migration required for existing records.
- **Type-safe frontend** — TypeScript types mirror backend Pydantic models exactly.

### Negative

- **Two schema shapes per domain** — `AgentRef`/`AgentDefinition` (essays) and `Grader`/`GraderDefinition` (questions) create parallel lightweight-vs-full pairs that must stay synchronized.
- **Legacy fallback code** — the `id`→`agent_id` shims in `_hydrate_agents()` and `ensure_assembly()` are technical debt that should be removed after all Cosmos documents are rewritten.

### Pending

- **Remaining services** — `avatar-svc`, `chat-svc`, `upskilling-svc`, and `evaluation-svc` still use `AgentRegistry` for orchestration; their migration to `FoundryAgentService` is tracked separately.
- **Agent Framework rc3 upgrade** — ADR-011 specified upgrading to `agent-framework>=1.0.0rc3` with `ChatAgent` orchestration patterns (`SequentialBuilder`, `ConcurrentBuilder`); this ADR focused on the data-plane migration and did not change orchestration topology.
- **Legacy fallback removal** — once all Cosmos documents have `agent_id` fields, the `id` fallback paths can be deleted.

---

## Related

- [ADR-011](./011-foundry-first-agent-architecture.md) — Foundry-First Agent Architecture (this ADR implements its agent migration vision)
- [ADR-005](./005-foundry-evaluation.md) — Foundry Evaluation (evaluation service design)
- [ADR-006](./006-domain-decoupling.md) — Domain-Driven Service Decoupling (service boundaries)
- [ADR-002](./002-shared-library.md) — Shared Library Extraction (`tutor-lib`)
