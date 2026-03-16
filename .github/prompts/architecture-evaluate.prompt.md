---
title: "Architecture: Evaluate Design"
description: "Evaluate a proposed architecture or system design for pattern correctness, integration safety, and scalability."
mode: "SystemArchitect"
input: "Describe the system or component being designed. Include context on scale, integration points, and constraints."
---

Evaluate the proposed design:

1. **Pattern Identification** — Which architectural patterns are in play? (Event-Driven, CQRS, Saga, Gateway, Circuit Breaker, etc.)
2. **Responsibility Assignment** — Does each component have a single, clear responsibility? Are boundaries well-defined?
3. **Integration Contracts** — Are API shapes, event schemas, and data formats specified at boundaries? Are they versioned?
4. **Dependency Direction** — Do dependencies flow inward (domain has no infra deps)? Are there circular dependencies?
5. **Failure Modes** — What happens when each component fails? Are there circuit breakers, retries, dead-letter queues?
6. **Scalability** — Can each component scale independently? Are there shared-state bottlenecks?
7. **Trade-offs** — Document alternatives considered, why this approach was chosen, and what is sacrificed.

Deliver an assessment with a diagram (Mermaid), risk table, and recommendations.
