---
title: "Connector: Design Integration"
description: "Design a new enterprise integration adapter (REST/GraphQL/OData) with architecture review and implementation plan."
mode: "TechLeadOrchestrator"
input: "Describe the target platform (PIM, DAM, CRM, Commerce, etc.), the API type (REST/GraphQL/OData), and the data flows required."
---

Coordinate enterprise connector design:

1. **API Discovery** — Invoke `enterprise-connectors` via `#runSubagent` to:
   - Analyze the target platform's API surface (endpoints, auth model, rate limits, pagination)
   - Identify the minimum API scope required for the use case
   - Document data models and field mappings (source → internal → target)
   - Classify the platform category (PIM, DAM, CRM, Commerce, Inventory/SCM, Data/Analytics, Integration, Workforce, Identity, Privacy)

2. **Architecture Design** — Invoke `system-architect` via `#runSubagent` to:
   - Define the connector's place in the overall integration architecture
   - Choose communication pattern (sync request-response, async events, batch ETL, webhook-driven)
   - Design error handling strategy (retry policies, dead-letter queues, circuit breakers)
   - Specify contract versioning approach for the connector API surface

3. **Implementation Plan** — Invoke the appropriate language specialist via `#runSubagent`:
   - `python-specialist` — For Python async connectors (httpx, aiohttp)
   - `rust-specialist` — For high-throughput connectors (reqwest, tokio)
   - `typescript-specialist` — For Node.js connectors (fetch, graphql-request)
   - Define: auth flow, pagination handling, rate limit respect, data transformation pipeline

4. **Security Review** — Invoke `platform-quality` via `#runSubagent` to verify:
   - Credential storage (Key Vault / env vars, never hardcoded)
   - OAuth token refresh handling
   - Input validation on all external data
   - Audit logging for compliance

5. **Testing Strategy** — Define:
   - Contract tests against the external API (recorded fixtures / WireMock)
   - Integration tests with sandbox environment
   - Load tests to validate rate limit handling

Deliver a connector design document with architecture diagram, data mapping table, implementation spec, and test plan.
