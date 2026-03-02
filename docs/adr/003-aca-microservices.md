# ADR-003: Azure Container Apps for Microservices

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The current infrastructure provisions a single Azure Container App (`tutor-api`) via the `aca.bicep` module. However, the platform has 5 (growing to 8+) independent microservices that need:

- Independent scaling based on workload (avatar sessions vs. essay batch processing)
- Independent deployment (update essays without redeploying avatar)
- Service-to-service communication within a VNet
- Health checks and graceful shutdown per service
- Cost-efficient scale-to-zero for low-traffic services

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **AKS (Kubernetes)** | Full control, Helm, KEDA | Operational overhead, node management |
| **Azure Container Apps** | Serverless, KEDA built-in, Dapr sidecar | Less control, newer service |
| **Azure App Service** | Familiar, easy | No scale-to-zero, higher cost |
| **Azure Functions** | True serverless | Cold start, not ideal for long-running agent threads |

## Decision

**Continue using Azure Container Apps (ACA)** as the compute platform for all microservices, with the following improvements:

### 1. One Container App per Service

```
ACA Environment (tutor-aca-env)
├── tutor-essays-svc          # Port 8083, min 0 / max 5
├── tutor-questions-svc       # Port 8082, min 0 / max 5
├── tutor-avatar-svc          # Port 8084, min 1 / max 3 (always-on for WebRTC)
├── tutor-upskilling-svc      # Port 8085, min 0 / max 3
├── tutor-config-svc          # Port 8081, min 1 / max 3
├── tutor-evaluation-svc      # Port 8086, min 0 / max 2
├── tutor-lms-gateway         # Port 8087, min 0 / max 2
└── tutor-chat-svc            # Port 8088, min 0 / max 3
```

### 2. Scaling Rules

| Service | CPU Trigger | HTTP Trigger | Custom |
|---------|-------------|-------------|--------|
| Essays | 70% | 50 concurrent | — |
| Questions | 70% | 100 concurrent | — |
| Avatar | 60% | 10 concurrent | WebSocket connections |
| Upskilling | 70% | 30 concurrent | — |
| Config | 50% | 100 concurrent | — |
| Evaluation | 80% | — | Queue depth (evaluation jobs) |
| LMS Gateway | 50% | — | Timer (sync schedule) |

### 3. Dapr Sidecars (Future)

Enable Dapr for:
- **Service invocation** — Service-to-service calls via `dapr invoke` (replaces hardcoded URLs)
- **State management** — Cosmos DB state store binding
- **Pub/Sub** — Event-driven communication between domains

### 4. Managed Identity

Each Container App uses a **User-Assigned Managed Identity** for:
- Cosmos DB data-plane access (RBAC: `Cosmos DB Built-in Data Contributor`)
- Azure OpenAI inference
- Azure Speech Services
- Key Vault secret access
- ACR image pull

## Consequences

### Positive

- **Independent scaling** — Avatar stays warm; evaluation scales to zero when idle.
- **Independent deployments** — Each service has its own CI/CD pipeline and image tag.
- **Cost efficiency** — Scale-to-zero for low-traffic services saves ~40% vs. always-on.
- **Built-in observability** — ACA integrates natively with Log Analytics and App Insights.
- **No cluster management** — Unlike AKS, no node pools or upgrades to manage.

### Negative

- **Limited networking control** — No custom ingress controllers or service mesh.
- **Revision management** — Must handle blue-green deployments carefully.
- **Dapr maturity** — Some Dapr components are still in preview on ACA.

## References

- [Azure Container Apps documentation](https://learn.microsoft.com/azure/container-apps/)
- [ACA scaling rules](https://learn.microsoft.com/azure/container-apps/scale-app)
- [ACA managed identity](https://learn.microsoft.com/azure/container-apps/managed-identity)
- [Dapr on ACA](https://learn.microsoft.com/azure/container-apps/dapr-overview)
