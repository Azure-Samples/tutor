# Foundry Native Implementation Epics

Date: 2026-05-09

This program turns the improvement plan into implementation-ready epics. It is scoped to Wave 0 and Wave 1: architecture reset, Foundry Agent Service native runtime, removal of Microsoft Agent Framework, evaluation gates, and learner-record provenance integration.

## Program Principles

| Principle | Required behavior |
| --------- | ----------------- |
| Foundry-native runtime | Use Microsoft Foundry Agent Service agents, conversations, responses, tracing, and evaluations through `tutor_lib.agents`. |
| Model-catalog neutrality | Application code never branches on GPT-family or provider-specific response types. |
| Learner-record center | High-impact agent outputs append governed provenance into learner-record events or projections. |
| Human review | Agentic outputs remain advisory unless an authorized human confirms the action. |
| Privacy by default | Student/minor workflows default to application-controlled state, explicit retention, redacted traces, and no unnecessary PII. |
| Workflow-only production deployment | Production changes ship through GitHub workflows; local commands are development and validation only. |

## Validation Panel

Every feature in this program goes through the following ten evaluators:

| Evaluator | Question |
| --------- | -------- |
| Product value | Does this improve learner, professor, supervisor, or operator outcomes? |
| Learner outcomes | Does it improve learning without hiding uncertainty or review state? |
| Professor workflow | Does it reduce professor burden without becoming punitive ranking? |
| Supervisor decision quality | Does it support aggregate, purpose-bound decisions with provenance? |
| Architecture and DDD | Does it respect bounded contexts and no cross-context database reads? |
| Azure Foundry feasibility | Does it map cleanly to Foundry Agent Service and SDK capabilities? |
| Data and ML validity | Are assumptions, uncertainty, leakage, and drift addressed? |
| Security, privacy, compliance | Are tenant scope, PII, minor data, and retention controlled? |
| UX and accessibility | Can users understand status, review state, and degraded behavior? |
| Operability and cost | Can the team test, observe, roll back, and estimate cost? |

Each epic also receives three adversarial reviews:

| Adversarial agent | Attack focus |
| ----------------- | ------------ |
| Privacy and compliance red team | PII exposure, unauthorized scope, unfair ranking, retention failure. |
| Causal validity skeptic | Confounding, leakage, weak outcome/treatment definitions, causal overclaim. |
| Integration and operability skeptic | Provider variability, rate limits, outages, replay, SDK churn, and cost. |

The reasoning procedure is: evidence fit, adversarial critique, then decision and acceptance.

## Wave 0 Epics

### FN-00-01: ADR-008 Foundry Agent Runtime and Evaluation Governance

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | SystemArchitect |
| Supporting agents | AzureAIFoundrySpecialist, CodeReviewer, PlatformEngineer |
| Dependencies | None |

**Business context:** Restores architectural clarity before code migration and removes the conflict between learner-record platform goals and Agent Framework runtime coupling.

**Scope:** Use consolidated ADR-008 as the authority for Foundry Agent Service runtime, retained Foundry-managed-agent decisions, Cosmos-domain-data boundaries, evaluation gates, and workflow-only deployment decisions.

**Acceptance criteria:**

- ADR-008 declares Foundry Agent Service as the canonical runtime.
- ADR-008 prohibits Agent Framework runtime usage in `apps/` and `lib/`.
- ADR-008 defines app-facing contracts by `agent_name` and `agent_version`.
- ADR-008 states retention, provenance, safety, degraded mode, and human-review requirements.

**Quality gates:** Architecture review, CodeReviewer documentation review, `rg "Agent Framework rc3|AzureAIAgentClient" docs` limited to migration context.

### FN-00-02: Documentation Alignment

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | SystemArchitect |
| Supporting agents | PlatformEngineer, AzureAIFoundrySpecialist |
| Dependencies | FN-00-01 |

**Business context:** Keeps implementation teams from rebuilding against stale Agent Framework guidance.

**Scope:** Update architecture, service domains, modernization plan, agent evaluation, infrastructure docs, and ADR index.

**Acceptance criteria:**

- Architecture docs describe Foundry agents, conversations, responses, tracing, evaluations, and name/version identity.
- Infrastructure docs expose the Foundry project endpoint URL, not a resource id, as app configuration.
- Evaluation docs describe versioned Foundry Agent Service release gates and adversarial panels.
- Service-domain docs keep agentic services inside the governance envelope.

**Quality gates:** Documentation diff review, Mermaid theme compliance for any new diagrams, link review.

### FN-00-03: Migration Inventory and Compatibility Policy

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PlatformEngineer |
| Supporting agents | PythonDeveloper, CodeReviewer |
| Dependencies | FN-00-01 |

**Business context:** Reduces migration risk by making every runtime dependency and schema compatibility point visible before code changes.

**Scope:** Inventory Agent Framework imports/dependencies, `AgentRegistry`/`AgentSpec` call sites, thread/run polling, `agent_id` schemas, lockfile residues, and test fakes.

**Acceptance criteria:**

- Inventory lists app, shared library, tests, pyproject, and lockfile findings.
- Compatibility policy states legacy `agent_id` is read-only migration data.
- New write path policy requires `agent_name` and `agent_version`.
- CI scan gate is specified.

**Quality gates:** `rg` scan report attached to PR, CodeReviewer confirmation that no new compatibility shim leaks into app logic.

### FN-00-04: Governance and Deployment Guardrails

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PlatformEngineer |
| Supporting agents | RiskAnalyst, AzureAIFoundrySpecialist, CodeReviewer |
| Dependencies | FN-00-01 |

**Business context:** Protects students, professors, supervisors, and institutions from unsafe AI automation and uncontrolled production changes.

**Scope:** Codify privacy, RBAC, retention, redacted tracing, evaluation, deployment, and high-impact human-review gates.

**Acceptance criteria:**

- Student/minor workflows default to strict retention and application-controlled state.
- Runtime identity uses least privilege; publishing/versioning identity is separate.
- High-impact outputs require evidence refs, trace/correlation id, safety state, degraded state, and review state.
- Production deployment remains GitHub Workflow only.

**Quality gates:** Security/privacy review, workflow review, adversarial red-team checklist.

## Wave 1 Epics

### FN-01-01: Build `tutor_lib.agents` Foundry Native Facade

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | AzureAIFoundrySpecialist, CodeReviewer |
| Dependencies | FN-00-01, FN-00-03 |

**Business context:** Creates the single stable seam that lets app teams remove Agent Framework without duplicating SDK churn across services.

**Scope:** Replace Agent Framework registry/run wrappers with data-oriented contracts, an invocation facade, SDK response adapters, retry handling, attachment support, and test fakes.

**Acceptance criteria:**

- `AgentReference`, `AgentInvocationRequest`, `AgentInvocationResult`, and `AgentEvaluationReference` are exported from `tutor_lib.agents`.
- `import tutor_lib.agents` succeeds without Agent Framework installed.
- The facade invokes Foundry Agent Service through project endpoint and OpenAI-compatible responses APIs.
- Default invocation request uses application-controlled state unless retention policy permits stored conversations.
- Unit tests cover response normalization, retryable errors, retention flags, and fake clients.

**Quality gates:** Python tests for `lib`, type-aware review, `rg "agent_framework|AzureAIAgentClient" lib` returns no matches.

### FN-01-02: Remove Agent Framework Dependencies

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | PlatformEngineer, CodeReviewer |
| Dependencies | FN-01-01 |

**Business context:** Eliminates the current dependency mismatch and import-time failures.

**Scope:** Remove Agent Framework packages/imports/stubs from `lib`, app packages, tests, and lockfiles.

**Acceptance criteria:**

- `agent-framework` and `agent-framework-azure-ai` are removed from pyproject dependencies.
- Runtime imports of `agent_framework`, `agent_framework_azure_ai`, and `AzureAIAgentClient` are gone.
- Lockfiles are regenerated or explicitly scheduled in the migration PR if package tooling is unavailable.

**Quality gates:** Dependency scan gate and app import smoke test.

### FN-01-03: Migrate Questions and Essays

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | CodeReviewer, AzureAIFoundrySpecialist |
| Dependencies | FN-01-01, FN-01-02 |

**Business context:** Restores the critical assessment paths and validates the facade with the services most exposed to existing `agent_id` debt.

**Scope:** Replace `run_agent(agent_id, prompt)` with `invoke(AgentInvocationRequest)` and convert create/update flows to named/versioned agent references.

**Acceptance criteria:**

- Questions graders use `agent_name` and `agent_version` for new writes.
- Essays agent refs use role plus `agent_name` and `agent_version` for new writes.
- Legacy `agent_id` read compatibility is isolated to adapters/hydration code.
- Assessment outputs persist normalized provenance-ready result metadata.
- Existing questions and essays tests pass with fake Foundry facade.

**Quality gates:** Questions/essays tests, schema migration tests, CodeReviewer assessment regression review.

### FN-01-04: Migrate Avatar, Chat, Upskilling, and Configuration

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | UIDesigner for any user-facing state text, CodeReviewer |
| Dependencies | FN-01-01, FN-01-02 |

**Business context:** Removes the remaining local orchestration dependency and enforces retention policy on conversational workflows.

**Scope:** Avatar and chat invoke named/versioned tutoring agents with explicit conversation/retention policy. Upskilling turns visitor calls into `AgentInvocationRequest` commands. Configuration becomes Foundry-free except metadata management.

**Acceptance criteria:**

- No `AgentRegistry`, `AgentSpec`, or `AgentRunContext` imports remain in apps.
- Avatar/chat tests verify application-controlled state defaults and explicit conversation ids only when allowed.
- Upskilling preserves existing visitor-oriented domain output while replacing the runtime call path.
- Configuration has no runtime Foundry dependency for deterministic CRUD paths.

**Quality gates:** Avatar/chat/upskilling/configuration tests, privacy retention review.

### FN-01-05: Foundry Evaluation and Trace Gate

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | AzureAIFoundrySpecialist, PlatformEngineer, CodeReviewer |
| Dependencies | FN-01-01, FN-01-03 |

**Business context:** Prevents unreviewed agent changes from reaching learners or professor/supervisor workflows.

**Scope:** Evolve evaluation service from run CRUD to a Foundry Agent Service release gate storing agent name/version, dataset id, eval run id, thresholds, trace/report URI, and approval status.

**Acceptance criteria:**

- Evaluation run requests use agent references, not `agent_id` as the primary contract.
- Datasets carry lineage, anonymization/synthetic status, and approved-use metadata.
- Safety, groundedness, relevance, rubric alignment, privacy, and adversarial metrics can block release.
- Trace/report summaries are redacted before supervisor or admin projection use.

**Quality gates:** Evaluation tests, privacy adversarial test cases, release-gate decision tests.

### FN-01-06: Learner Record Provenance Integration

| Field | Value |
| ----- | ----- |
| Priority | P0 |
| Primary owner | PythonDeveloper |
| Supporting agents | AzureCosmosDBSpecialist, CodeReviewer, SystemArchitect |
| Dependencies | FN-01-03, FN-01-04, FN-01-05 |

**Business context:** Makes AI-generated assessment, coaching, and advising outputs trustworthy, replayable, and reviewable.

**Scope:** Append provenance-bearing learner-record events for high-impact outputs and project sanitized summaries for role workspaces.

**Acceptance criteria:**

- High-impact outputs include evidence refs, agent/model/prompt version, trace/correlation id, safety state, degraded state, and review state.
- Corrections and appeals are compensating events, not destructive overwrites.
- Cosmos access follows high-cardinality partitioning and projection-based reads.
- Supervisor views consume sanitized projections only.

**Quality gates:** Learner-record tests, Cosmos partition review, no cross-context DB read scan.

## Program Exit Gates

- No Agent Framework packages or imports remain in `apps/` or `lib/`.
- App-facing agent contracts use `agent_name` and `agent_version` for new writes.
- Foundry integration tests are marked separately and do not run against production by default.
- Backend test suites for questions, essays, avatar, upskilling, chat, evaluation, insights, configuration, and lms-gateway pass or unrelated failures are documented.
- Evaluation gates include safety, groundedness, relevance, rubric alignment, discursive accuracy, privacy, adversarial scenarios, and degraded-state behavior.
- All connector ingests and learner-record appends are idempotent and replay-safe.