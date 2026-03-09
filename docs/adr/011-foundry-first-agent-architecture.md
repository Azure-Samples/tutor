# ADR-011: Foundry-First Agent Architecture

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-09 |
| **Deciders** | Platform team |
| **Supersedes** | Partial updates to ADR-005 (Foundry Evaluation) |

---

## Context

The Tutor platform currently stores agent definitions (name, instructions, deployment, temperature) inside Cosmos DB containers (`assemblies`). Each service independently creates agents at runtime using the Agent Framework's `AzureAIAgentClient`, and agent lifecycle is managed through custom code in `FoundryAgentService`. This creates several problems:

1. **No centralized agent management** — agents are ephemeral, recreated per request or cached inconsistently across services.
2. **Agent Framework version drift** — `lib` pins `agent-framework-azure-ai>=0.2.0.dev0` while apps pin `>=1.0.0rc2`, causing backward-compatibility shims (`_resolve_azure_agent_client`, `_resolve_agent_class`).
3. **Agent Framework breaking change** — rc3 requires `azure-ai-projects>=2.0.0` GA, removes `Agent` class (now `ChatAgent`), removes `default_options`, changes orchestration surface.
4. **Missing Foundry resource** — no Azure AI Foundry project is provisioned in Terraform; the `PROJECT_ENDPOINT` is injected externally as a manual variable.
5. **Assemblies conflate agent definitions with orchestration** — a `Swarm` in Cosmos holds both agent specs and orchestration topology, but Agent Framework now provides first-class orchestration patterns (`SequentialBuilder`, `ConcurrentBuilder`, `HandoffBuilder`, `MagenticBuilder`).

## Decision

### 1. Provision Azure AI Foundry as Terraform-Managed Infrastructure

- Deploy an **Azure AI Foundry** resource (AI Services account + AI Hub + AI Project) in **westus3**, **outside the VNet** (public endpoint), using the AVM `avm/res/cognitive-services/account` and `avm/res/machine-learning-services/workspace` modules.
- The Foundry project endpoint becomes a Terraform output, eliminating the need for manual `PROJECT_ENDPOINT` injection.
- RBAC: all container app managed identities receive `Cognitive Services User` on the Foundry resource.

### 2. Agents Live in Foundry; Assemblies Orchestrate via Agent Framework

**What moves to Foundry:**
- All standalone agent definitions (graders, evaluators, upskilling visitors, chat guidance agents) are created and persisted as **Azure AI Foundry agents** — not stored in Cosmos.
- Each agent has a stable `agent_id` in Foundry, referenced by assemblies.

**What stays in Cosmos:**
- **Assemblies** — the orchestration topology that maps agents to business entities (essays, questions, avatars). An assembly record references Foundry `agent_id` values but does not store agent instructions.
- **Essay-tied data** — essay content, evaluation results, resources.
- **Question-tied data** — questions, answers, grader configs.
- **Avatar-tied data** — conversation history, avatar configurations.
- **All CRUD domain data** — students, professors, courses, etc.

**Assembly schema change:**
```python
# BEFORE: Agents stored as full definitions in Cosmos
class Swarm(BaseModel):
    id: str
    topic_name: str
    essay_id: str | None
    agents: list[ProvisionedAgent]  # Full agent definitions

# AFTER: Assemblies reference Foundry agent IDs
class Assembly(BaseModel):
    id: str
    topic_name: str
    entity_id: str | None  # essay_id, question_id, avatar_case_id
    entity_type: str       # "essay" | "question" | "avatar"
    agent_refs: list[AgentRef]  # Lightweight references to Foundry agents

class AgentRef(BaseModel):
    agent_id: str         # Foundry agent ID
    role: str             # Agent's role in the assembly (e.g., "grader", "reviewer")
    deployment: str       # Model deployment name
```

### 3. Agent Framework as Assembly Orchestrator

- Upgrade to `agent-framework>=1.0.0rc3` and `azure-ai-projects>=2.0.0`.
- Use `ChatAgent` (replacing removed `Agent` class) with `AzureAIAgentClient`.
- Use Agent Framework orchestration patterns for multi-agent assemblies:
  - **Essays**: `SequentialBuilder` (OCR → strategy selection → grading → feedback synthesis)
  - **Questions**: `ConcurrentBuilder` (parallel dimension grading → aggregation)
  - **Upskilling**: `ConcurrentBuilder` (parallel visitors) → `SequentialBuilder` (aggregation)
  - **Avatar**: Single `ChatAgent` with conversation memory
  - **Chat**: Single `ChatAgent` with guardrails
  - **Evaluation**: `SequentialBuilder` (agent run → evaluator run → metric collection)

### 4. Remove All Backward Compatibility

- Remove `_resolve_azure_agent_client()` multi-path import resolution.
- Remove `_resolve_agent_class()` Agent/RawAgent fallback.
- Remove compatibility wrapper modules (`apps/upskilling/app/cosmos.py`).
- Remove OCR fallback to pypdf/PIL — Document Intelligence is required.
- Remove legacy route fallbacks.
- Remove stateless evaluate backward compatibility tests.
- Pin exact dependency ranges — no version-sniffing at runtime.

## Consequences

### Positive
- **Single source of truth** for agents — Foundry manages agent lifecycle, versioning, and evaluation.
- **Infrastructure as code** — Foundry provisioned via Terraform, no manual setup.
- **Clean Agent Framework integration** — no compatibility shims, direct use of rc3 API.
- **Orchestration clarity** — assemblies define topology, Agent Framework executes it.
- **Simplified Cosmos** — only business data and assembly references, no agent definitions.

### Negative
- **Foundry dependency** — all agentic services require Foundry availability.
- **Migration effort** — existing Cosmos agent data must be re-provisioned in Foundry.
- **No backward compatibility** — all services must upgrade simultaneously.

### Risks
- **Agent Framework rc3 instability** — still pre-release; pin `>=1.0.0rc3,<2.0.0`.
- **Foundry regional availability** — westus3 must support AI Services + AI Hub.
- **RBAC complexity** — 8 container apps need Cognitive Services User on Foundry.

## Related
- ADR-004: Terraform with AVM (infrastructure patterns)
- ADR-005: Foundry Evaluation (evaluation service design)
- ADR-006: Domain Decoupling (service boundaries)
