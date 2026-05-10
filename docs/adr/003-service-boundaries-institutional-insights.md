# ADR-003: Service Boundaries and Institutional Insights

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Domain-driven service decoupling and supervisor/institutional insights integration |

---

## Context

Tutor started with services organized around technical functions. As the platform grew into assessment, tutoring, evaluation, LMS integration, upskilling, and governed intelligence, the service model needed clearer ownership boundaries.

The platform also introduced institutional and supervisor-facing insights. Those workflows consume school, cohort, learner-record, and Fabric-backed indicators; they require stricter scope controls than generic analytics and must not become cross-context database reads.

## Decision

Organize the backend around bounded contexts and keep agentic services separate from deterministic control-plane services.

Current service/domain mapping:

| Domain | Current services | Responsibility |
| ------ | ---------------- | -------------- |
| Platform | `configuration`, `lms-gateway` | Roster/configuration, pedagogical rules, feature flags, LMS anti-corruption, sync state |
| Assessment | `essays`, `questions` | Draft evaluations, assessment evidence, OCR-capable essay ingestion, question grading |
| Interaction | `avatar`, `chat` | Voice and text tutoring, guided hints, conversation context |
| Analytics and Governance | `upskilling`, `evaluation` | Teaching-plan analysis, advisory training plans, golden datasets, evaluation release gates |
| Institutional Insights | `insights` | School-unit intelligence, causal-study drafts, conformal-risk reports, lifelong-network projections, supervisor briefings |

Integration rules:

- Services do not perform cross-context database reads.
- External LMS, SIS, CRM, Fabric, and wallet schemas are normalized through anti-corruption layers.
- Read models follow CQRS: role workspaces and institutional briefings consume projections rather than write stores.
- `insights` may consume Fabric read-only indicators and learner-record projections, but it does not become the authoritative source for learner history.
- Principal, supervisor, and admin access to governed intelligence must enforce role and relationship scope.

## Consequences

### Positive

- Clearer service ownership and operational scaling boundaries.
- Institutional insight workflows have a dedicated governed projection home.
- External data dependencies are isolated behind adapters.
- Role workspaces can evolve without coupling directly to write-model containers.

### Negative

- Some workflows require API/event integration instead of simple shared-container reads.
- Boundary enforcement requires more explicit contracts and integration tests.
- Transitional services may temporarily advance more than one target bounded context.

### Guardrails

- Add a new service only when ownership, scale, or governance pressure justifies a split.
- Keep future `content-svc`, credentialing, community, and catalog contexts optional until they need independent operation.
- Treat institutional insight outputs as governed, advisory, reviewable, and uncertainty-aware.

## References

- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [CQRS pattern](https://learn.microsoft.com/azure/architecture/patterns/cqrs)
