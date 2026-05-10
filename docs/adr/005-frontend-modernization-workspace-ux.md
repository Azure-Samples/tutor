# ADR-005: Frontend Modernization and Workspace UX

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Frontend modernization baseline and role-aware workspace direction |

---

## Context

Tutor's frontend must support student, professor, principal, supervisor, administrator, and alumni workflows across multiple backend services. It also needs APIM-only backend routing, typed API clients, accessible components, and role-aware workspace surfaces for governed intelligence and lifelong-network data.

The active baseline is:

- Next.js 15.5.10
- React 18.3.1
- TypeScript 5.7+
- pnpm 9.15.4
- Tailwind CSS 3.4.x
- Azure Static Web Apps hosting

React 19 and Tailwind 4 remain future migration decisions, not the current production baseline.

## Decision

Use Next.js App Router with typed TypeScript clients and role-aware workspace routes as the frontend architecture.

Frontend rules:

- Browser calls to backend services go through APIM via `NEXT_PUBLIC_APIM_BASE_URL`.
- Each backend domain has typed client functions and DTOs.
- Role workspaces surface only the actions and panels appropriate to the current role and scope.
- Governed intelligence and lifelong-network UI must avoid presenting advisory outputs as final, operational truth.
- UI controls must meet WCAG 2.2 AA expectations and preserve keyboard/focus behavior.
- Frontend build, typecheck, lint, and Playwright route/policy tests are required quality gates for user-facing changes.

Current role-aware surfaces include:

- Supervisor governed-intelligence briefings.
- Principal school-health intelligence.
- Alumni lifelong learner network record.
- Upskilling advisory training-plan workflow.

## Consequences

### Positive

- Consistent frontend routing through APIM.
- Stronger compile-time safety for multi-service DTOs.
- Clearer role separation for high-trust education workflows.
- Better accessibility and policy regression coverage.

### Negative

- More frontend client code to maintain as backend APIs evolve.
- Role-aware workspace routing requires careful test coverage.
- Future React/Tailwind upgrades remain a coordinated migration, not a casual dependency bump.

### Guardrails

- Do not add per-service public base URLs for production browser calls.
- Do not show causal, risk, or advisory outputs without governance labels and review state.
- Keep route smoke tests current when adding workspace pages.

## References

- [Next.js App Router](https://nextjs.org/docs/app)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
