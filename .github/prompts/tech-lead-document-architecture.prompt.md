---
title: "Tech Lead: Document Architecture"
description: "Produce comprehensive platform documentation including architecture diagrams, ADRs, and design principia by coordinating business, architecture, and UI agents."
mode: "TechLeadOrchestrator"
input: "Specify the system or project to document. Include target audience (developers, stakeholders, ops) and any existing docs to update."
---

Coordinate multi-agent documentation of the platform:

1. **Business Context** — Invoke `business-strategy-agent` via `#runSubagent` to document:
   - System purpose and business value proposition
   - Key stakeholders and their concerns
   - Domain boundaries and bounded contexts
   - Non-functional requirements (SLAs, compliance, scaling targets)

2. **Architecture Documentation** — Invoke `system-architect` via `#runSubagent` to produce:
   - Architecture Decision Records (ADRs) for every non-trivial decision
   - Component responsibility matrix
   - Data flow and integration contracts between services
   - Technology stack rationale and trade-off analysis

3. **Visual Architecture** — Invoke `ui-agent` via `#runSubagent` to create:
   - **C4 diagrams** (Context, Container, Component, Code) as draw.io XML files
   - **High-level architecture** overview as a Mermaid diagram with consistent theming
   - **Sequence diagrams** for critical flows (auth, data pipeline, deployment)
   - **Design principia**: icon set selection, color palette definition, diagram style guide ensuring visual consistency across all artifacts

4. **Technical Reference** — Invoke language specialists via `#runSubagent` as needed:
   - `python-specialist` — API reference, async patterns guide, data model docs
   - `rust-specialist` — Crate architecture, safety invariants, performance contracts
   - `typescript-specialist` — Component catalog, state management patterns, route structure

5. **Operations Runbook** — Invoke `platform-quality` via `#runSubagent` to document:
   - Deployment procedures and rollback steps
   - Monitoring and alerting configuration
   - Incident response playbook
   - Environment setup and prerequisites

Deliver a documentation package with ADRs, diagrams (Mermaid + draw.io), API reference, and runbook organized by audience.
