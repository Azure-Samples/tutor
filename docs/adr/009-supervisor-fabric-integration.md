# ADR-009: Supervisor Insights & Microsoft Fabric Integration

| Metadata | Value |
|----------|-------|
| **Status** | Proposed |
| **Date** | 2025-01 |
| **Decision Makers** | Architecture Team |
| **Business Needs** | BN-SUP-1, BN-SUP-2, BN-SUP-3, BN-SUP-4, BN-SUP-5 |

---

## Context

The **Supervisor Insights AI agenda** defines five business needs for regional supervisors:

1. **BN-SUP-1**: Automated insight generation from educational indicators (standardized assessments, attendance, task completion)
2. **BN-SUP-2**: Pre-visit briefing reports with Strava-like narrative synthesis
3. **BN-SUP-3**: Modular indicator system that starts with 3 indicators and grows
4. **BN-SUP-4**: UX validation with real supervisors
5. **BN-SUP-5**: Governance — school-scoped data access via Entra ID

The current architecture has no supervisor persona, no external data integration with Microsoft Fabric, and no report generation capability.

---

## Decision

### Add a Supervision Domain with `insights-svc`

A new **Supervision Domain** is introduced as the 5th business domain, containing a single service (`insights-svc`, port 8090) that:

1. Consumes educational indicators from **Microsoft Fabric** via its REST API (read-only semantic model)
2. Applies modular **indicator strategies** (Strategy Pattern) for each data source
3. Synthesizes **narrative briefing reports** via Azure OpenAI
4. Stores reports in a dedicated `supervision_db` Cosmos database
5. Enforces **school-scoped access** using Entra ID claims

### Microsoft Fabric Integration

- **Read-only access** — insights-svc consumes Fabric's semantic model REST API; it never writes to Fabric
- **Authentication** — Service-to-service via Managed Identity with `Fabric.Read.All` scope
- **Data sources** — Standardized assessment scores, attendance rates, and task completion rates are pre-modeled in Fabric by the department's BI team
- **No Fabric provisioning** — Fabric is external infrastructure managed by the education department; The Tutor only reads from it

### Indicator Strategy Pattern

```python
class IndicatorStrategy(ABC):
    @abstractmethod
    async def fetch(self, school_id: str, period: str) -> IndicatorData: ...
    @abstractmethod
    async def summarize(self, data: IndicatorData) -> str: ...

# Initial strategies
class StandardizedTestStrategy(IndicatorStrategy): ...
class AttendanceStrategy(IndicatorStrategy): ...
class TaskCompletionStrategy(IndicatorStrategy): ...
```

New indicators can be added by implementing the `IndicatorStrategy` interface and registering them in `indicator_configs`.

### Narrative Synthesis

Reports follow a "Strava-like" format — concise, data-driven narratives that highlight:
- Key performance deltas vs. previous period
- Schools/indicators requiring attention
- Positive trends worth acknowledging

Azure OpenAI generates the narrative from structured indicator data using a prompt template.

### Supervisor RBAC

| Claims | Source | Purpose |
|--------|--------|---------|
| `roles: ["supervisor"]` | Entra ID App Role | Route access control |
| `school_ids: [...]` | Entra ID Groups / Graph API | Data scoping |

insights-svc validates that the requesting supervisor has access to the requested school before returning any data.

---

## Consequences

### Positive

- Supervisors get pre-visit briefings without manual data gathering
- Modular indicator system supports future expansion (drop-out rates, teacher performance, etc.)
- School-scoped access ensures data governance compliance
- No Fabric provisioning burden — leverages existing department BI infrastructure

### Negative

- Dependency on Fabric REST API availability and semantic model schema stability
- Narrative quality depends on prompt engineering and structured data completeness
- New domain adds operational surface area (monitoring, scaling, identity)

### Risks

| Risk | Mitigation |
|------|-----------|
| Fabric API changes break indicator strategies | Pin semantic model version; add integration tests against schema |
| Narrative hallucination | Constrain synthesis to tabular data; add factual grounding evaluator |
| Supervisor adoption | Phase 10 includes UX validation sessions (BN-SUP-4) |

---

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Embed supervisor features in upskilling-svc | Violates single-responsibility; different data sources and personas |
| Direct Power BI embedding | Does not support narrative synthesis or proactive briefings |
| Build custom BI pipeline | Duplicates Fabric capabilities; higher cost and maintenance |

---

## Related Documents

| Document | Link |
|----------|------|
| Business Alignment | [business-alignment.md](../business-alignment.md) |
| Architecture (Supervision flows) | [architecture.md](../architecture.md) |
| Service Domains (Supervision) | [service-domains.md](../service-domains.md) |
| Security (Supervisor RBAC) | [security.md](../security.md) |
| Modernization Plan (Phase 10) | [modernization-plan.md](../modernization-plan.md) |
