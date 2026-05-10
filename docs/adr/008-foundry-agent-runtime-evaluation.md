# ADR-008: Foundry Agent Runtime and Evaluation Governance

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Foundry evaluation, pre-native Foundry migration, Cosmos-to-Foundry agent reference migration, and current Foundry Agent Service native runtime |

---

## Context

Tutor uses AI agents for assessment, tutoring, evaluation, upskilling, narrative synthesis, and governed intelligence. Earlier implementations moved agent definitions toward Azure AI Foundry and lightweight Cosmos references, but they also introduced runtime coupling to prerelease Microsoft Agent Framework concepts, `AzureAIAgentClient`, thread/run polling, and `agent_id` as the primary app-facing contract.

The current platform requires a stable, testable, privacy-aware agent boundary for high-impact education workflows.

## Decision

Use Microsoft Foundry Agent Service as Tutor's canonical agent runtime and keep evaluation governance as the release gate for high-impact agent behavior.

Runtime rules:

- Application services call `tutor_lib.agents`, not provider SDKs directly.
- `AgentReference` identifies Foundry agents by `agent_name` and optional `agent_version`, with role, dimension, model metadata, prompt version, and governance state.
- `AgentInvocationRequest` and `AgentInvocationResult` are the app-facing command/result contracts.
- Legacy `agent_id` may be read only through compatibility adapters during migration. New writes use `agent_name` and `agent_version`.
- Microsoft Agent Framework runtime dependencies, `AzureAIAgentClient`, direct thread/run polling, and provider response primitives do not cross into application services.
- Cosmos DB stores domain-owned data, lightweight references, learner-record events, evaluation references, and projection metadata; Foundry owns agent runtime assets.

Evaluation rules:

- High-impact agent versions must pass evaluation gates before release.
- Evaluation records include dataset lineage, thresholds, run id, trace/report URI, status, safety result, and approval state.
- Evaluation datasets must be synthetic, anonymized, or explicitly approved for the purpose.
- Prompt, trace, tool argument, and evaluation data must not contain secrets, raw student ids, or unnecessary PII.

Governance metadata for high-impact outputs must include:

- agent name and version
- prompt or workflow version
- model provider and model name
- evidence references
- trace or correlation id
- safety state
- degraded state
- human-review requirement
- retention policy

## Patterns

| Pattern | Usage |
| ------- | ----- |
| Facade | `tutor_lib.agents` hides Foundry SDK and REST details. |
| Adapter | SDK response normalization, attachment conversion, and legacy `agent_id` compatibility. |
| Command | Invocation and evaluation requests are explicit command objects. |
| Strategy | Retention, safety, role, dimension, and degraded-mode policies are selected by context. |
| Repository | Persist agent references, evaluation references, learner-record events, and projection metadata through owned repositories. |
| Anti-Corruption Layer | Foundry SDK contracts and external schemas stop at the service boundary. |

## Consequences

### Positive

- Removes prerelease Agent Framework runtime debt.
- Gives application code a stable Foundry Agent Service contract.
- Aligns agent identity with named and versioned Foundry assets.
- Makes privacy, retention, safety, degraded behavior, and provenance explicit.
- Preserves the useful migration direction: agents are Foundry-managed and Cosmos keeps domain data plus lightweight references.

### Negative

- Requires coordinated contract discipline across shared library, services, tests, and frontend DTOs.
- Legacy data containing `agent_id` needs read-only compatibility until rewritten.
- Evaluations consume model capacity and require ongoing dataset stewardship.

### Guardrails

- `apps/` and `lib/` runtime paths must not import Agent Framework packages.
- Student/minor workflows default to application-controlled state and strict retention.
- No high-impact agent output ships without provenance and evaluation coverage.
- Production deployment and Foundry mutation remain workflow-governed.

## References

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview)
- [Microsoft Foundry Agent Service Overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
- [Foundry Agent Runtime Components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components)
- [Azure AI Evaluation](https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-approach-gen-ai)
- [Refactoring Guru Design Patterns Catalog](https://refactoring.guru/design-patterns/catalog)
