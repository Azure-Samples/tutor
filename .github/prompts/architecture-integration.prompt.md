---
title: "Architecture: Design Integration"
description: "Design a cross-service integration with event contracts, API versioning, and failure handling."
mode: "SystemArchitect"
input: "Describe the services to integrate, data flows, and consistency requirements (eventual vs strong)."
---

Design the integration between the specified services:

1. **Communication Pattern** — Choose sync (REST/gRPC) vs async (events/queues) based on coupling and latency requirements.
2. **Contract Definition** — Define the API or event schema. Specify versioning strategy (URL path, content negotiation, schema registry).
3. **Data Consistency** — Choose consistency model. If eventual: define saga or choreography pattern with compensating actions.
4. **Error Handling** — Dead-letter queues for failed messages. Circuit breakers for sync calls. Retry policies with exponential backoff.
5. **Observability** — Correlation IDs across service boundaries. Structured logging at entry/exit points. Distributed tracing spans.
6. **Security** — Authentication between services (mTLS, token exchange). Authorization at gateway. Input validation at each boundary.

Deliver a Mermaid sequence diagram, contract specifications, and implementation guidance for each service.
