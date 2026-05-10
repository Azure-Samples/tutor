# Architecture Decision Records

This directory contains the current Architecture Decision Records (ADRs) for **The Tutor** platform. Historical ADR versions are not kept as live archive files; use Git history when the older decision trail is needed.

## ADR Index

| ADR | Title | Status | Date |
| --- | ----- | ------ | ---- |
| [001](./001-shared-library-contracts.md) | Shared Library and Cross-Service Contracts | Accepted | 2026-05-10 |
| [002](./002-azure-runtime-infrastructure.md) | Azure Runtime and Infrastructure | Accepted | 2026-05-10 |
| [003](./003-service-boundaries-institutional-insights.md) | Service Boundaries and Institutional Insights | Accepted | 2026-05-10 |
| [004](./004-security-zero-trust.md) | Security Layers and Zero-Trust | Accepted | 2026-05-10 |
| [005](./005-frontend-modernization-workspace-ux.md) | Frontend Modernization and Workspace UX | Accepted | 2026-05-10 |
| [006](./006-pedagogical-content-ocr-rag.md) | Pedagogical Content, OCR, and RAG | Accepted | 2026-05-10 |
| [007](./007-learner-record-platform-distribution.md) | Learner-Record Platform and Distribution | Accepted | 2026-05-10 |
| [008](./008-foundry-agent-runtime-evaluation.md) | Foundry Agent Runtime and Evaluation Governance | Accepted | 2026-05-10 |

## Current Authority Map

| Topic | Authoritative ADR |
| ----- | ----------------- |
| Shared library and cross-service contracts | [ADR-001](./001-shared-library-contracts.md) |
| Azure runtime, Terraform, ACA, APIM, workflow deployment | [ADR-002](./002-azure-runtime-infrastructure.md) |
| Service boundaries, supervision domain, Fabric-backed institutional insights | [ADR-003](./003-service-boundaries-institutional-insights.md) |
| Identity, RBAC, network, data, and audit security | [ADR-004](./004-security-zero-trust.md) |
| Frontend baseline and role-aware workspace UX | [ADR-005](./005-frontend-modernization-workspace-ux.md) |
| Pedagogical content, OCR, AI Search, RAG, ENEM direction | [ADR-006](./006-pedagogical-content-ocr-rag.md) |
| Learner-record platform, anti-corruption layers, Service Bus distribution | [ADR-007](./007-learner-record-platform-distribution.md) |
| Foundry Agent Service runtime, agent contracts, evaluation governance | [ADR-008](./008-foundry-agent-runtime-evaluation.md) |

## ADR Format

Each ADR follows this structure:

1. **Title** - Short descriptive name
2. **Status** - Proposed / Accepted / Deprecated / Superseded
3. **Context** - What problem are we solving?
4. **Decision** - What did we decide?
5. **Consequences** - What trade-offs are accepted?
6. **References** - Links to related resources
