# Tutor Platform Documentation

> **Multi-Agent Educational Intelligence Platform** — A platform that augments existing Learning Management Systems with AI-powered assessment, guided tutoring, content management, and supervisor insights for students, professors, administrators, and regional supervisors.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Solution Overview](./solution-overview.md) | Current-state architecture, services, and technology stack |
| [Architecture](./architecture.md) | Target architecture with Mermaid diagrams for every flow |
| [Business Alignment](./business-alignment.md) | Traceability matrix: business needs ↔ architecture components |
| [ADR Index](./adr/README.md) | Architecture Decision Records (8 consolidated ADRs) |
| [Modernization Plan](./modernization-plan.md) | Phased upgrade tasks (10 phases), dependency updates, and infrastructure migration |
| [Agent Evaluation](./agent-evaluation.md) | Foundry Evaluation Engine integration, ENEM fidelity, and agent quality assurance |
| [Security](./security.md) | Security layers, zero-trust posture, supervisor RBAC, and ACA hardening |
| [Service Domains](./service-domains.md) | Business-domain decomposition (5 domains, 9 current backend services plus future context boundaries) |
| [Infrastructure](./infrastructure.md) | Azure Developer CLI (azd) + Terraform with Azure Verified Modules — cloud-only |
| [Local Development](./local-development.md) | Run services locally against cloud backends for sampling & testing |
| [Runbooks](./runbooks/azd-deployment.md) | Operational runbooks for deployment and support |
| [Reviewer Checklist](./runbooks/reviewer-checklist.md) | Fine-grained PR review checklist for compatibility, quality, and merge safety |

## Quick Links

- [ADR-001 - Shared Library and Cross-Service Contracts](./adr/001-shared-library-contracts.md)
- [ADR-002 - Azure Runtime and Infrastructure](./adr/002-azure-runtime-infrastructure.md)
- [ADR-003 - Service Boundaries and Institutional Insights](./adr/003-service-boundaries-institutional-insights.md)
- [ADR-004 - Security Layers and Zero-Trust](./adr/004-security-zero-trust.md)
- [ADR-005 - Frontend Modernization and Workspace UX](./adr/005-frontend-modernization-workspace-ux.md)
- [ADR-006 - Pedagogical Content, OCR, and RAG](./adr/006-pedagogical-content-ocr-rag.md)
- [ADR-007 - Learner-Record Platform and Distribution](./adr/007-learner-record-platform-distribution.md)
- [ADR-008 - Foundry Agent Runtime and Evaluation Governance](./adr/008-foundry-agent-runtime-evaluation.md)
