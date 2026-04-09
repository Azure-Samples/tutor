# ADR-014: Hybrid Learner-Record Service Bus Distribution

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-04-08 |
| **Deciders** | Platform Team |
| **Extends** | [ADR-013](./013-learner-record-standalone-platform.md), [ADR-004](./004-terraform-avm.md), [ADR-008](./008-security-layers.md) |

---

## Context

ADR-013 established the learner record as the append-oriented architectural center of Tutor. The current implementation persists authoritative learner-record events in Cosmos DB and projects read models directly from that store. This preserves replayability and governance, but it does not yet provide a brokered integration seam for downstream workflow consumers, operational backlog inspection, or future fan-out.

The platform needs a hybrid pattern that adds messaging where it improves decoupling without turning the message broker into the institutional source of truth.

## Options Considered

| Option | Description | Benefits | Trade-offs |
| ------ | ----------- | -------- | ---------- |
| **A. Cosmos-only** | Keep direct append and direct replay with no broker. | Lowest cost and lowest change surface. | Leaves integration consumers coupled to the authoritative store. |
| **B. Broker as source of truth** | Replace the learner-record event store with Service Bus topics and subscriptions. | Simplifies producer-consumer topology. | Rejected. A broker is not the authoritative learner record and weakens replay, governance, and institutional history. |
| **C. Hybrid Cosmos plus Service Bus** | Keep Cosmos as the authoritative append-only store and publish newly accepted learner-record events to Service Bus. | Preserves governed history while enabling decoupled workflow distribution and operational fan-out. | Adds infrastructure, RBAC, and publication-path complexity. |

## Decision

Adopt **Option C**.

Tutor will use a hybrid architecture with these responsibilities:

- **Cosmos DB** remains the authoritative learner-record event store.
- **Service Bus** acts as a secondary distribution layer for learner-record integration events.
- **Read models** continue to replay from Cosmos, not from Service Bus.

This follows:

- **CQRS** guidance from Microsoft Learn: the write model and read/distribution concerns remain separate.
- **Event Notification pattern** from microservices.io: domain changes are published to interested downstream consumers.
- **Publish-Subscribe Channel** from Enterprise Integration Patterns: Service Bus topics/subscriptions distribute integration events without redefining record ownership.

## Implementation Notes

### 1. Repository decoration at the application seam

The initial implementation uses a **Decorator** around the learner-record repository:

- the inner repository appends authoritative events to Cosmos
- the decorator publishes newly created events to Service Bus
- idempotent re-appends do not republish duplicates from the application layer

This keeps broker logic outside the authoritative repository implementation and preserves a clean separation of concerns.

### 2. Messaging scope

The first production publisher is the `insights` service because it currently owns the implemented learner-record backfill/write path. No Service Bus receiver is introduced in this slice; the namespace includes a default subscription for backlog inspection and future consumers.

### 3. Security model

- Container Apps use `DefaultAzureCredential` and managed identity.
- Local/SAS authentication is disabled on the Service Bus namespace.
- Only publishing workloads receive `Azure Service Bus Data Sender` RBAC in this slice.

## Consequences

### Positive

- **Decoupling improves**: future consumers no longer need to read the authoritative store directly just to react to new events.
- **Governance is preserved**: Cosmos continues to hold the learner-record history.
- **Incremental migration remains possible**: new bounded contexts can subscribe later without replacing the current write model.

### Negative

- **Operational complexity increases**: Service Bus adds RBAC, monitoring, and publication-path diagnostics.
- **This is not yet a full outbox pattern**: the first slice adds an integration seam, not a dedicated asynchronous publication worker.

## Non-Goals

- This ADR does **not** replace the authoritative learner-record store.
- This ADR does **not** move read-model projection materialization onto Service Bus.
- This ADR does **not** introduce autonomous high-impact actions by broker consumers.

## References

- [ADR-013: Learner-Record-Centered Standalone Lifelong-Learning Platform](./013-learner-record-standalone-platform.md)
- [Microsoft Learn: CQRS pattern](https://learn.microsoft.com/azure/architecture/patterns/cqrs)
- [Microsoft Learn: Event Sourcing pattern](https://learn.microsoft.com/azure/architecture/patterns/event-sourcing)
- [Microsoft Learn: Authenticate and authorize an application with Microsoft Entra ID to access Azure Service Bus entities](https://learn.microsoft.com/azure/service-bus-messaging/authenticate-application)
- [microservices.io: Event Notification pattern](https://microservices.io/patterns/data/event-notification.html)
- [Enterprise Integration Patterns: Publish-Subscribe Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html)
