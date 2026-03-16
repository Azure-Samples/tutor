---
applyTo: '**/*.py,**/*.ts,**/*.tsx,**/*.rs,**/*.js,**/*.jsx'
---

## Architectural Integration

When integrating components into the broader system, consult the architecture specialist agent (if available) to ensure:
- New modules respect the established architecture boundaries
- Event-driven patterns align with the event schema conventions
- Cross-cutting concerns (multi-tenancy, security, observability) are correctly propagated
- Architectural decision records (ADRs) and design constraints are honoured

> When working inside a repository that has architecture specifications in `.github/agents/data/`, load those files for repo-specific boundaries, ADR constraints, and integration patterns.
