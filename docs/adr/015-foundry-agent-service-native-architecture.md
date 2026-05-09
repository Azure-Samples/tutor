# ADR-015: Foundry Agent Service Native Architecture

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-09 |
| **Deciders** | Platform Team |
| **Supersedes** | Agent Framework orchestration, `AzureAIAgentClient`, thread/run polling, and `agent_id` as the primary app-facing agent contract in [ADR-011](./011-foundry-first-agent-architecture.md) and [ADR-012](./012-cosmos-foundry-agent-migration.md) |
| **Extends** | [ADR-005](./005-foundry-evaluation.md), [ADR-006](./006-domain-decoupling.md), [ADR-008](./008-security-layers.md), [ADR-013](./013-learner-record-standalone-platform.md), [ADR-014](./014-hybrid-learner-record-service-bus-distribution.md) |
| **Drivers** | [Foundry Native Implementation Epics](../foundry-native-implementation-epics.md), [Standalone Lifelong Learning Issue Backlog](../standalone-lifelong-learning-issue-backlog.md) |

---

## Context

ADR-011 and ADR-012 correctly moved agent definitions toward Azure AI Foundry and kept Cosmos DB focused on domain data and lightweight references. Their remaining runtime decision now conflicts with the target architecture: application services still depend on Microsoft Agent Framework, `AzureAIAgentClient`, older thread/run polling, and `agent_id` as the primary contract.

Microsoft Foundry Agent Service now provides the native runtime concepts Tutor needs: project endpoints, named and versioned agents, conversations, responses, tool calls, tracing, evaluations, identity, and publishing. The runtime model allows Tutor to keep application code model-catalog neutral while Foundry hosts prompt, workflow, and hosted agents.

Tutor also handles high-impact educational workflows involving students, minors, professors, and supervisors. Agent runtime contracts must therefore make retention, provenance, safety state, review state, and degraded behavior explicit instead of leaving those controls implicit in SDK response objects.

## Decision

Adopt Microsoft Foundry Agent Service as the canonical agent runtime for Tutor. Remove Microsoft Agent Framework from all `apps/` and `lib/` runtime paths.

### 1. Runtime Boundary

Only `tutor_lib.agents` may import Foundry SDK or OpenAI-compatible client primitives. Application services must interact with data-oriented Tutor contracts rather than provider response classes.

The shared library exposes these app-facing contracts:

| Contract | Purpose |
| -------- | ------- |
| `AgentReference` | Stable reference to a Foundry agent by `agent_name`, optional `agent_version`, role, dimension, model metadata, prompt version, and governance state. |
| `AgentInvocationRequest` | Command payload for one invocation, including input, context, conversation or previous invocation continuity, attachments, retention policy, streaming/background flags, evidence refs, tenant scope, and trace correlation. |
| `AgentInvocationResult` | Normalized response with output text, invocation id, conversation id, tool calls, usage, trace id, model provider/name, agent name/version, safety state, degraded state, and review requirement. |
| `AgentEvaluationReference` | Release-gate record for Foundry evaluations, dataset lineage, thresholds, status, and report URI. |

Legacy `agent_id` values may be read only through compatibility adapters during migration. New writes must use `agent_name` and `agent_version`.

### 2. Invocation Model

Tutor uses Foundry Agent Service agents, conversations, and responses. For student/minor-sensitive workflows, the default retention policy is application-controlled state with service-side storage disabled unless a documented policy explicitly permits Foundry-side conversation retention.

Application services must not call thread/run polling APIs directly. The facade is responsible for mapping Tutor invocation requests to the current Foundry Agent Service SDK or REST shape and normalizing responses.

### 3. Model-Catalog Neutrality

Application code must not assume GPT-family models, provider-specific clients, or provider-specific response fields. Model names, deployments, and providers are metadata carried by `AgentReference`, configuration, and governance records.

### 4. Governance

High-impact educational outputs must carry:

- agent name and version
- prompt or workflow version
- model provider and model name
- evidence references
- trace or correlation id
- safety state
- degraded state
- human-review requirement
- retention policy

Agent Evaluation and Governance remains the release gate. Evaluation datasets should be synthetic, anonymized, or explicitly approved for the purpose; no prompt, trace, tool argument, or evaluation item may contain secrets, raw student ids, or unnecessary PII.

### 5. Deployment

Production deployment remains workflow-only. This ADR does not authorize direct production `azd deploy`, container app updates, manual image pushes, or production Foundry mutation outside the approved GitHub workflow path and documented break-glass rules.

## Patterns

| Pattern | Usage |
| ------- | ----- |
| Facade | `tutor_lib.agents` hides Foundry Agent Service SDK and REST details. |
| Adapter | SDK response normalization, attachment conversion, and legacy `agent_id` read compatibility. |
| Command | Invocation and evaluation requests are explicit command objects. |
| Strategy | Retention, safety, role, dimension, and degraded-mode policies are selected by context. |
| Repository | Persist agent references, evaluation references, learner-record events, and projection metadata through owned repositories. |
| Anti-Corruption Layer | Foundry SDK contracts and external LMS/SIS/CRM schemas stop at the boundary. |
| CQRS / Projection | Role workspaces and supervisor briefings read projections rather than cross-context write stores. |

## Consequences

### Positive

- Removes prerelease Agent Framework runtime debt from Tutor services.
- Gives application code a stable, testable contract around agent invocations.
- Aligns agent identity with Foundry Agent Service named/versioned assets.
- Makes privacy, retention, safety, and provenance explicit in high-impact workflows.
- Preserves Foundry-managed agent lifecycle and Cosmos-owned domain data decisions from ADR-011 and ADR-012.

### Negative

- Requires coordinated migration across shared library, questions, essays, avatar, chat, upskilling, evaluation, and configuration packages.
- Legacy data still containing `agent_id` needs a read-only compatibility path until rewritten.
- Tests and fakes must move from thread/run behavior to response/conversation behavior.

### Non-Goals

- This ADR does not replace ADR-013's learner-record platform direction.
- This ADR does not change the authoritative learner-record store or Service Bus distribution model from ADR-014.
- This ADR does not permit autonomous punitive decisions by agents.
- This ADR does not require a new Azure topology beyond the existing Foundry project endpoint and workflow-managed deployment model.

## Acceptance Gates

- `rg "agent_framework|agent-framework|agent_framework_azure_ai|AzureAIAgentClient" apps lib` returns no matches after Wave 1.
- `import tutor_lib.agents` works in a clean environment without Agent Framework installed.
- New app-facing agent writes use `agent_name` and `agent_version`; `agent_id` is read-only migration compatibility.
- Student/minor workflows default to application-controlled state and strict retention.
- Evaluation release gates store agent version, dataset lineage, thresholds, trace/report URI, safety result, and approval state.
- No cross-context database reads are introduced.

## References

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Microsoft Foundry Agent Service Overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
- [Foundry Agent Runtime Components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components)
- [Refactoring Guru Design Patterns Catalog](https://refactoring.guru/design-patterns/catalog)
- [Refactoring Guru Refactoring Techniques](https://refactoring.guru/refactoring/techniques)
- [Foundry Native Implementation Epics](../foundry-native-implementation-epics.md)