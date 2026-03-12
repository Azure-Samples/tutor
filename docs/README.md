# Tutor Platform Documentation

> **Multi-Agent Educational Intelligence Platform** — A platform that augments existing Learning Management Systems with AI-powered assessment, guided tutoring, content management, and supervisor insights for students, professors, administrators, and regional supervisors.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Solution Overview](./solution-overview.md) | Current-state architecture, services, and technology stack |
| [Architecture](./architecture.md) | Target architecture with Mermaid diagrams for every flow |
| [Business Alignment](./business-alignment.md) | Traceability matrix: business needs ↔ architecture components |
| [ADR Index](./adr/README.md) | Architecture Decision Records (10 ADRs) |
| [Modernization Plan](./modernization-plan.md) | Phased upgrade tasks (10 phases), dependency updates, and infrastructure migration |
| [Agent Evaluation](./agent-evaluation.md) | Foundry Evaluation Engine integration, ENEM fidelity, and agent quality assurance |
| [Security](./security.md) | Security layers, zero-trust posture, supervisor RBAC, and ACA hardening |
| [Service Domains](./service-domains.md) | Business-domain decomposition (5 domains, 10 services) |
| [Infrastructure](./infrastructure.md) | Azure Developer CLI (azd) + Terraform with Azure Verified Modules — cloud-only |
| [Local Development](./local-development.md) | Run services locally against cloud backends for sampling & testing |
| [Runbooks](./runbooks/azd-deployment.md) | Operational runbooks for deployment and support |
| [Reviewer Checklist](./runbooks/reviewer-checklist.md) | Fine-grained PR review checklist for compatibility, quality, and merge safety |

## Quick Links

- [ADR-001 — LMS-Enhancer Multi-Agent Platform](./adr/001-lms-enhancer-platform.md)
- [ADR-002 — Shared Library Extraction](./adr/002-shared-library.md)
- [ADR-003 — Azure Container Apps for Microservices](./adr/003-aca-microservices.md)
- [ADR-004 — Terraform with Azure Verified Modules](./adr/004-terraform-avm.md)
- [ADR-005 — Foundry Agent Evaluation](./adr/005-foundry-evaluation.md)
- [ADR-006 — Domain-Driven Service Decoupling](./adr/006-domain-decoupling.md)
- [ADR-007 — Frontend Modernization (Next.js 15 + React 19)](./adr/007-frontend-modernization.md)
- [ADR-008 — Security Layers and Zero-Trust](./adr/008-security-layers.md)
- [ADR-009 — Supervisor Insights & Microsoft Fabric Integration](./adr/009-supervisor-fabric-integration.md)
- [ADR-010 — Pedagogical Content Ingestion, OCR & RAG](./adr/010-pedagogical-content-ocr.md)
