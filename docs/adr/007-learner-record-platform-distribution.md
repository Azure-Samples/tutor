# ADR-007: Learner-Record Platform and Distribution

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Product pivot from LMS enhancer to learner-record control plane, standalone lifelong-learning architecture, and hybrid learner-record event distribution |

---

## Context

Tutor is no longer only an LMS enhancement layer. It is evolving into an institution-owned lifelong-learning and outcomes platform that keeps interoperability with LMS, SIS, CRM, analytics, and credential ecosystems while owning the durable learner record and role-aware experiences.

The platform needs longitudinal evidence, credentials, advising history, alumni re-entry, institutional read models, and high-governance controls. At the same time, external systems remain important migration-era sources and distribution channels.

## Decision

Make the learner record the architectural center of Tutor.

Core decisions:

- Tutor owns an append-oriented learner record for learning, assessment, tutoring, advising, credential, portfolio, community, and governance events.
- Cosmos DB remains the authoritative learner-record event store.
- Service Bus is a secondary distribution layer for newly accepted learner-record integration events; it is not the source of truth.
- Read models project from the authoritative store and feed role workspaces, school/unit intelligence, alumni views, and work queues.
- LMS, SIS, CRM, Fabric, and wallet ecosystems remain behind anti-corruption layers.
- Agents may advise, summarize, and draft, but they do not autonomously decide grade, placement, credential, discipline, or access outcomes.

Migration horizons:

| Horizon | Goal |
| ------- | ---- |
| Record-first overlay | Relationship-based access control, event backbone, provenance, learner-record MVP, role-aware shell |
| Standalone learning core | Advising, interventions, role workspaces, institutional read models |
| Lifelong network platform | Skills graph, credentials, alumni re-entry, community, continuing education |

## Consequences

### Positive

- Tutor has a durable architecture beyond isolated AI features.
- Learner history, evidence, credentials, and alumni continuity share a common record model.
- Event distribution enables future consumers without weakening the authoritative store.
- Governance, retention, and review requirements become design-time constraints.

### Negative

- More deterministic control-plane modeling is required.
- Event publication and replay add operational complexity.
- External system integration still needs careful schema isolation and data-quality handling.

### Guardrails

- Do not replace LMS/SIS/CRM wholesale as part of this decision.
- Keep Cosmos DB authoritative for learner-record history.
- Keep Service Bus consumers from becoming hidden systems of record.
- Preserve review, appeal, retention, provenance, and degraded-mode controls for high-impact outputs.

## References

- [1EdTech Comprehensive Learner Record](https://www.1edtech.org/clr)
- [1EdTech Open Badges](https://www.1edtech.org/standards/open-badges)
- [Microsoft Learn: CQRS pattern](https://learn.microsoft.com/azure/architecture/patterns/cqrs)
- [Microsoft Learn: Event Sourcing pattern](https://learn.microsoft.com/azure/architecture/patterns/event-sourcing)
- [Azure Service Bus authentication and authorization](https://learn.microsoft.com/azure/service-bus-messaging/authenticate-application)
