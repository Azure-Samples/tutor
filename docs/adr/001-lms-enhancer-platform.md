# ADR-001: LMS-Enhancer Multi-Agent Platform

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The Tutor started as a standalone intelligent tutoring application with five independent FastAPI services (Configuration, Questions, Essays, Avatar, Upskilling). While functional, the platform:

1. **Does not integrate with existing LMS platforms** — The target institution already operates a host **LMS platform** as its learning and student information system. A standalone system creates data silos and duplicates enrollment workflows.
2. **Has no formal agent orchestration strategy** — Each service implements its own agent patterns (Strategy, State Machine, Visitor) without a unifying framework.
3. **Lacks a life-long learning perspective** — Evaluations are point-in-time; there is no longitudinal analysis of student growth across courses and semesters.
4. **Is positioned as a replacement rather than a complement** — Education departments are unlikely to abandon their existing LMS investment.
5. **Has no supervisor dimension** — Regional supervisors need insight reports derived from educational indicators (standardized assessments, attendance, task completion) available in Microsoft Fabric.
6. **Lacks OCR and content ingestion** — Handwritten essays cannot be processed, and AI responses are not grounded in official pedagogical materials.

## Decision

**Reposition The Tutor as an LMS Enhancer**: a system that augments an existing educational ecosystem with multi-agent AI capabilities for four personas (student, professor, administrator, supervisor), rather than replacing existing platforms.

### Core Principles

1. **Enhance, don't replace** — The platform consumes course/student/assignment context from external LMS systems via adapters and produces AI-driven insights that flow back.
2. **Multi-agent architecture** — Each domain (assessment, interaction, analytics) exposes specialized AI agents that can be composed, evaluated, and evolved independently.
3. **Life-long learning analytics** — Longitudinal tracking of student performance across courses, semesters, and learning modalities (essays, questions, avatar sessions).
4. **Tenant-aware multi-tenancy** — Support multiple institutions, each with their own LMS integration, agent configurations, and data boundaries.

### New System Boundaries

| Boundary | The Tutor Owns | Host LMS / Department Owns |
|----------|---------------|--------------------------|
| **Enrollment** | ✗ | ✓ |
| **Calendars / Scheduling** | ✗ | ✓ |
| **Grade books** | ✗ (contributes scores) | ✓ |
| **AI Essay/Question Evaluation** | ✓ (OCR + ENEM + RAG) | ✗ |
| **Agent Orchestration** | ✓ | ✗ |
| **Guided Virtual Tutoring** | ✓ | ✗ |
| **Avatar Tutoring** | ✓ | ✗ |
| **Content Ingestion / RAG** | ✓ | ✗ |
| **Supervisor Insight Reports** | ✓ (narrative synthesis) | ✗ |
| **Educational Indicators** | ✗ (consumes) | ✓ (Fabric semantic model) |
| **Learning Analytics** | ✓ (augmented) | ✓ (basic) |
| **Course Configuration** | ✓ (mirror + extend) | ✓ (source of truth) |
| **Pedagogical Rules** | ✓ | ✗ |

### LMS Gateway

A new **LMS Gateway** service implements the Adapter pattern for each supported LMS:

```
LMSGateway
├── adapters/
│   ├── moodle.py      # Moodle REST API adapter
│   ├── canvas.py      # Canvas LTI / REST adapter
│   └── base.py        # Abstract adapter interface
├── sync/
│   ├── scheduler.py   # Periodic sync jobs
│   └── transformer.py # LMS → Tutor schema mapping
└── routes.py          # Manual sync triggers + status
```

## Consequences

### Positive

- **Adoption barrier reduced** — Institutions keep their LMS; The Tutor plugs in alongside.
- **Clear value proposition** — "Add AI agents to your existing LMS" is easier to sell than "replace your LMS."
- **Data consistency** — LMS remains the source of truth for enrollment; The Tutor syncs rather than duplicates.
- **Extensibility** — New LMS integrations are just new adapter implementations.

### Negative

- **Integration complexity** — Each LMS has different APIs, auth models, and data schemas.
- **Sync latency** — Data is eventually consistent between LMS and Tutor.
- **Dependency risk** — Breaking changes in LMS APIs can affect sync operations.

### Risks

- LMS API rate limits may constrain sync frequency for large institutions.
- LTI 1.3 compliance requires careful security implementation.

## References

- [IMS Global LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [Moodle Web Services API](https://docs.moodle.org/dev/Web_service_API_functions)
- [Canvas LMS REST API](https://canvas.instructure.com/doc/api/)
- [holiday-peak-hub reference architecture](https://github.com/Azure-Samples/holiday-peak-hub/tree/feat/api-layer)
