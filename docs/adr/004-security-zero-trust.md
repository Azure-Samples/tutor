# ADR-004: Security Layers and Zero-Trust

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Identity, authorization, network, data, and observability security controls |

---

## Context

Tutor handles student data, educator workflows, supervisor-scoped school data, agent outputs, learning records, and future credential evidence. The platform cannot rely on a single security layer or implicit trust between services.

High-impact educational workflows need authentication, authorization, relationship-aware scope checks, auditability, and safe degradation. This is especially important for minors, assessment feedback, learner-record projections, supervisor insights, and credential/portfolio data.

## Decision

Adopt defense-in-depth zero-trust security across the platform.

Required layers:

1. **Identity**: Microsoft Entra ID for users and managed identities for workloads.
2. **Edge**: API Management for routing, policy enforcement, request limits, and APIM-first frontend access.
3. **Application**: FastAPI middleware for JWT validation, role checks, resource-scope checks, input validation, and safe errors.
4. **Network**: VNet-integrated Container Apps and private endpoints where supported.
5. **Data**: RBAC, encryption, least-privilege managed identity, and no secrets in code.
6. **Observability**: Audit logs, App Insights, Log Analytics, diagnostics, alerts, and incident evidence.

Authorization rules:

- Role checks alone are not enough for sensitive data. Resource-level checks must also validate tenant, school, course, learner, professor, supervisor, or alumni relationship scope.
- Supervisor and principal institutional intelligence must remain scoped to assigned schools/units.
- High-impact outputs must preserve provenance, review state, and appeal or override paths.
- Service-to-service access uses managed identity and APIs/events, not direct cross-context database reads.

## Consequences

### Positive

- Stronger protection for learner records, assessment outputs, and supervisor intelligence.
- Clear separation between authentication, role authorization, and data-scope authorization.
- Better auditability for incidents, appeals, and compliance reviews.
- Reduced secret exposure through managed identity and Key Vault patterns.

### Negative

- Additional configuration and troubleshooting complexity.
- Local testing requires clear auth modes and documented token setup.
- Scope enforcement must be tested continuously to prevent drift.

### Guardrails

- No production endpoint should rely on development header fallbacks.
- All sensitive read and write endpoints need negative authorization tests.
- Keep APIM, middleware, and frontend route protection aligned.
- Never allow agentic services to autonomously make punitive or grade-affecting decisions.

## References

- [Microsoft Zero Trust Model](https://learn.microsoft.com/security/zero-trust/)
- [Azure Container Apps managed identity](https://learn.microsoft.com/azure/container-apps/managed-identity)
- [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/)
- [Azure RBAC for Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/how-to-setup-rbac)
