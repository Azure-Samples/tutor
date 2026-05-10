# ADR-001: Shared Library and Cross-Service Contracts

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Shared library extraction and current cross-service contract ownership |

---

## Context

Tutor runs multiple FastAPI services that share configuration, Cosmos DB access, middleware, response envelopes, agent invocation contracts, governance metadata, and learner-network data contracts. Duplicating those concerns inside each service creates dependency drift, inconsistent error handling, and repeated migration effort whenever platform contracts change.

The original issue was a missing `common` module and duplicated service utilities. The current platform has moved beyond that narrow concern: the shared library is now the boundary where cross-service contracts are owned and where external SDK details are kept out of application services.

## Decision

Use `lib/` as the installable `tutor-lib` package for shared, service-neutral contracts and helpers.

The shared library owns:

- `tutor_lib.config` for settings and FastAPI app factory behavior.
- `tutor_lib.cosmos` for reusable Cosmos DB access patterns.
- `tutor_lib.middleware` for authentication, logging, and standardized error handling.
- `tutor_lib.schemas` for envelopes and stable shared DTOs.
- `tutor_lib.agents` for the app-facing Foundry Agent Service facade and invocation contracts.
- `tutor_lib.intelligence` for high-impact governance, uncertainty, review, appeal, drift, and suppression metadata.
- `tutor_lib.lifelong_network` for credential, portfolio, alumni, mentor, community, and research-governance contracts.

Application services may depend on these shared contracts, but service-specific business workflows stay inside their owning service. Provider SDK response objects, direct thread/run polling, external LMS schemas, and database implementation details must not leak through shared public contracts.

## Consequences

### Positive

- One source of truth for cross-service behavior and DTOs.
- Faster creation of new backend services with consistent middleware and response contracts.
- Lower migration cost when Foundry, Cosmos, Entra, or governance contracts change.
- Cleaner test fakes for shared platform boundaries.

### Negative

- Breaking changes in `tutor-lib` can affect many services at once.
- The library can become a dumping ground if service ownership boundaries are not enforced.
- Shared contract changes need broader review than isolated service changes.

### Guardrails

- Keep domain behavior in services unless multiple bounded contexts truly share the contract.
- Prefer data-oriented contracts and pure helpers over service-specific abstractions.
- Run shared-library and affected service tests for any contract change.
- Version or migrate contracts explicitly when high-impact data shapes change.

## References

- [Python Packaging: path dependencies](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
- [Azure Cosmos DB SDK guidance](https://learn.microsoft.com/azure/cosmos-db/nosql/best-practice-python)
