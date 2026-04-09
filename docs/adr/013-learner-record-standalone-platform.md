# ADR-013: Learner-Record-Centered Standalone Lifelong-Learning Platform

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-04-08 |
| **Deciders** | Platform Team |
| **Supersedes** | [ADR-001](./001-lms-enhancer-platform.md) |
| **Extends** | [ADR-006](./006-domain-decoupling.md), [ADR-008](./008-security-layers.md), [ADR-011](./011-foundry-first-agent-architecture.md), [ADR-012](./012-cosmos-foundry-agent-migration.md) |
| **Drivers** | [Standalone Lifelong Learning Innovation Brief](../standalone-lifelong-learning-innovation-brief.md), [Standalone Lifelong Learning Issue Backlog](../standalone-lifelong-learning-issue-backlog.md), [Standalone Lifelong Learning Platform Risk Assessment](../standalone-lifelong-learning-risk-assessment.md) |

---

## Context

ADR-001 correctly repositioned Tutor away from a greenfield LMS replacement, but it still framed the platform as an enhancement layer around an external LMS. The approved research brief, backlog, and risk assessment now establish a stronger direction:

1. **Tutor must own a longitudinal learner record** rather than treating learning evidence as point-in-time service data.
2. **Institutional differentiation depends on owning the control plane** for pathways, evidence, credentials, interventions, and alumni re-entry.
3. **External LMS, SIS, CRM, and credential ecosystems remain necessary**, but they should sit behind anti-corruption layers rather than define Tutor's internal model.
4. **The existing deterministic-core plus agentic-services split remains valid** because educational records, governance, and policy enforcement must stay deterministic, while tutoring, assessment, advising, and narrative synthesis benefit from agentic services.
5. **High-governance controls are mandatory**. The risk assessment identifies identity scope, assessment fairness, provenance, retention, and human-oversight requirements as design-time constraints, not operational follow-ups.

Using DDD bounded contexts and TOGAF architecture building blocks, Tutor now needs a durable platform architecture that is standalone in product ownership while remaining interoperable in runtime topology.

## Options Considered

| Option | Description | Benefits | Trade-offs |
| ------ | ----------- | -------- | ---------- |
| **A. Stay LMS-enhancer-first** | Keep Tutor as an AI augmentation layer whose primary job is to enrich an external LMS. | Lowest short-term change; minimal governance surface expansion. | Locks the product behind LMS data models, weakens alumni and credential continuity, and prevents Tutor from becoming the learner system of engagement. |
| **B. Replace LMS/SIS outright** | Rebuild the full academic platform immediately and make Tutor the source of truth for every institutional workflow. | Maximum product ownership and cleaner internal model. | Too risky, too broad, and misaligned with current repo capabilities; creates a one-way-door platform rewrite and unnecessary migration burden. |
| **C. Adopt a learner-record-centered standalone platform with anti-corruption layers** | Make Tutor the institution-owned lifelong-learning and outcomes platform while integrating LMS, SIS, CRM, analytics, and credential systems through explicit adapters. | Preserves current strengths, creates a durable system of record for evidence and credentials, supports lifelong learning, and enables incremental migration through Strangler Fig. | Requires new control-plane contexts, stricter governance, and a multi-wave migration path. |

## Decision

Adopt **Option C**.

Tutor becomes the **institution-owned lifelong-learning and outcomes platform** with a learner-record-centered architecture. External academic and commercial systems remain important, but they are integrated through anti-corruption layers and do not define Tutor's internal bounded contexts.

### 1. Preserve the platform split

The existing architectural split remains a hard constraint:

- **Deterministic core** owns identity, relationship scope, learner lifecycle, records, policies, pathways, credentials, audit, and provenance.
- **Agentic services** provide high-value reasoning for assessment, tutoring, advising, and narrative synthesis, but they do not become the system of record for high-impact decisions.

### 2. Establish the target bounded contexts

The target platform is organized around these bounded contexts:

- **Identity and Tenancy**
- **Integration Hub**
- **Catalog and Pathways**
- **Enrollment and Lifecycle**
- **Learner Record**
- **Content and Knowledge**
- **Assessment and Evidence**
- **Coaching and Interaction**
- **Advising and Success**
- **Credentialing and Portfolio**
- **Community and Network**
- **Institutional Analytics and Read Models**
- **Agent Evaluation and Governance**

These contexts align with DDD service boundaries and with the TOGAF principle that stable architecture building blocks should be explicit before delivery scales.

### 3. Make the learner record the architectural center

Tutor owns a **longitudinal, append-oriented learner record** that captures:

- learner identity and affiliation history
- learning, assessment, tutoring, advising, and credential events
- evidence links and competency progress
- provenance for high-impact AI outputs
- human review and approval state where required

This is not full event sourcing for every subsystem. It is an append-only institutional record pattern with CQRS-style read models for learner timelines, role work queues, cohort views, school briefings, and alumni re-entry experiences.

### 4. Keep external systems behind anti-corruption layers

Tutor integrates with LMS, SIS, CRM, analytics, and wallet ecosystems through explicit anti-corruption layers in the **Integration Hub**:

- LMS and SIS remain migration-era sources for roster, schedule, and assignment baselines.
- CRM and advancement tools remain external systems for relationship management until Tutor owns the required workflow.
- Credential wallets and external verification ecosystems remain distribution channels, not the authoritative store of institutional evidence.

### 5. Apply governance and provenance boundaries

The risk assessment becomes a hard architectural constraint:

- high-impact outputs must carry provenance metadata
- agentic recommendations remain advisory unless a human confirms the action
- degraded-mode outputs cannot silently act as authoritative outcomes
- minors, credentials, assessment, and cross-institution analytics require explicit review controls

### 6. Migrate via Strangler Fig across three waves

Tutor will evolve through an incremental Strangler Fig migration rather than a platform rewrite:

- **Wave 1 / Horizon 1**: record-first overlay, relationship-based access control, event backbone, role-aware shell, learner-record MVP, and governance gates
- **Wave 2 / Horizon 2**: standalone learning core for advising, role workspaces, institutional read models, and intervention workflows
- **Wave 3 / Horizon 3**: skills graph, credentials, alumni, community, and continuing-education expansion

The current repo deployment model remains valid during this transition. No new Azure topology is assumed by this ADR beyond what the repository already supports.

## Consequences

### Positive

- **Clear product position**: Tutor now has a durable architecture story beyond "AI for an LMS."
- **Longitudinal value**: evidence, credentials, advising, and alumni continuity now share a common record model.
- **Incremental delivery**: the repo can keep current services and Azure deployment patterns while new bounded contexts are introduced gradually.
- **Governance alignment**: provenance, evaluation, and human-oversight requirements are built into the architecture instead of treated as later controls.

### Negative

- **More control-plane complexity**: additional deterministic contexts must be modeled before feature delivery can scale safely.
- **Data-governance burden**: lifecycle separation, retention, revocation, and scope enforcement become first-class responsibilities.
- **Migration overhead**: current service boundaries do not yet map one-to-one to the target bounded contexts, so transitional seams are required.

### Non-Goals

- This ADR does **not** declare an immediate LMS, SIS, or CRM replacement.
- This ADR does **not** add a new Azure deployment topology beyond the repo's existing APIM, ACA, Cosmos DB, Blob Storage, and Azure AI patterns.
- This ADR does **not** authorize autonomous high-impact educational actions by agents.

## References

- [Standalone Lifelong Learning Innovation Brief](../standalone-lifelong-learning-innovation-brief.md)
- [Standalone Lifelong Learning Issue Backlog](../standalone-lifelong-learning-issue-backlog.md)
- [Standalone Lifelong Learning Platform Risk Assessment](../standalone-lifelong-learning-risk-assessment.md)
- [ADR-001: LMS-Enhancer Multi-Agent Platform](./001-lms-enhancer-platform.md)
- [ADR-006: Domain-Driven Service Decoupling](./006-domain-decoupling.md)
- [ADR-008: Security Layers and Zero-Trust](./008-security-layers.md)
- [ADR-011: Foundry-First Agent Architecture](./011-foundry-first-agent-architecture.md)
- [1EdTech Comprehensive Learner Record FAQ](https://www.1edtech.org/clr/faq)
- [1EdTech Open Badges](https://www.1edtech.org/standards/open-badges)
- [ADL xAPI](https://www.adlnet.gov/projects/xapi/)
