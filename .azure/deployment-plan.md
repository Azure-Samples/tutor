# Hybrid Learner-Record Distribution Plan

## Problem Statement

Tutor now has an authoritative learner-record event backbone in Cosmos DB, but downstream distribution is still tightly coupled to direct reads. That limits decoupling for workflow consumers, read-model refresh, and future external integrations. The platform needs a hybrid architecture that preserves Cosmos as the system of record while introducing Azure Service Bus where broker semantics add value.

## Architectural Decision

### Options considered

| Option | Summary | Benefits | Trade-offs |
| --- | --- | --- | --- |
| A. Cosmos-only | Keep append-only learner-record storage and direct read-model replay without a broker. | Lowest cost and lowest implementation risk. | Leaves downstream consumers coupled to the authoritative store and does not establish a durable integration seam. |
| B. Service Bus as source of truth | Replace the learner-record event store with brokered topics/queues. | Simplifies fan-out semantics. | Rejected. Violates ADR-013 by moving the authoritative learner record out of an append-oriented store, weakens replay/history, and turns transient messaging into the institutional record. |
| C. Hybrid Cosmos plus Service Bus | Keep Cosmos as the authoritative append-only store and publish accepted learner-record integration events to Service Bus. | Preserves replayable history while adding decoupled workflow distribution, dead-lettering, and future subscriber fan-out. | Adds infra, RBAC, and message-publication complexity. |

### Recommendation

Adopt **Option C**.

This aligns with:

- **ADR-013**: the learner record remains the architectural center and stays append-oriented.
- **CQRS / Event Sourcing guidance** from Microsoft Learn: the event store remains authoritative while projections and downstream consumers subscribe through separate mechanisms.
- **Service Bus guidance** from Microsoft Learn: topics/subscriptions are appropriate for workflow-grade business messaging with RBAC, dead-lettering, and controlled fan-out.

## Current-State Findings

- The learner-record write model is currently Cosmos-backed append-only storage in `tutor_lib.learner_record`.
- There is no active Service Bus or Event Hubs runtime path in the current code or Terraform.
- The only current production writer is the insights wave-one seed/backfill path, so the first hybrid cut must attach at the shared learner-record repository seam rather than at multiple domain-specific writers that do not exist yet.
- The current `azd` and Terraform contract is missing two environment outputs already needed by the current app shape:
  - `COSMOS_LEARNER_RECORD_EVENTS_TABLE`
  - `COSMOS_UPSKILLING_TABLE`

## Planned Scope

### 1. Shared library changes

- Add a `ServiceBusConfig` settings object in `tutor_lib.config`.
- Introduce a `LearnerRecordAppendResult` data carrier so the repository can distinguish **new append** from **idempotent replay**.
- Extend shared Cosmos CRUD helpers with a strict-create result shape that returns both the stored item and whether it was newly created.
- Add a learner-record publisher abstraction with:
  - no-op publisher for local/test or unconfigured environments
  - in-memory publisher for unit tests
  - Azure Service Bus publisher using `DefaultAzureCredential` and `azure-servicebus`
- Add a repository decorator that publishes only when the authoritative append succeeds for a newly created event.

### 2. Service wiring

- Update `apps/insights` to wrap the authoritative learner-record repository with the publishing decorator.
- Keep current in-memory test behavior intact when Cosmos or Service Bus is not configured.
- Preserve existing read-model behavior: projections continue to replay from Cosmos, not from Service Bus.

### 3. Infrastructure and environment contract

- Add Azure Service Bus infrastructure to Terraform:
  - one namespace
  - one learner-record topic
  - one default subscription for inspectable integration backlog and future consumers
- Add RBAC role assignments for container apps:
  - `Azure Service Bus Data Sender` for publisher workloads
  - receiver roles only if an app in this repo actually consumes in this slice
- Emit Terraform outputs for:
  - Service Bus fully qualified namespace
  - learner-record topic name
  - missing learner-record and upskilling Cosmos container outputs
- Map the new outputs into `azure.yaml` only for the services that need them in this slice.

### 4. Documentation and governance

- Add an ADR documenting the hybrid decision and the reason Service Bus is a secondary distribution layer instead of the source of truth.
- Update infrastructure or runbook documentation only where the new namespace/topic/output contract changes operational behavior.

## Candidate Files To Change

- `lib/src/tutor_lib/config/settings.py`
- `lib/src/tutor_lib/config/__init__.py`
- `lib/src/tutor_lib/cosmos/crud.py`
- `lib/src/tutor_lib/learner_record/__init__.py`
- `lib/src/tutor_lib/learner_record/repository.py`
- `lib/src/tutor_lib/learner_record/publishing.py` (new)
- `apps/insights/src/app/main.py`
- `apps/insights/src/app/projections.py`
- `tests/insights/test_insights_api.py`
- `lib/pyproject.toml`
- `azure.yaml`
- `infra/terraform/main.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/outputs.tf`
- `infra/terraform/main.tfvars.json`
- `infra/terraform/terraform.tfvars.sample`
- `docs/adr/014-hybrid-learner-record-service-bus-distribution.md` (new)

## Quality Attribute Impact

| Attribute | Expected impact | Notes |
| --- | --- | --- |
| Modifiability | Improved | New consumers can subscribe without coupling to the Cosmos read path. |
| Reliability | Improved for async workflows | Service Bus adds dead-lettering and replay at the subscription boundary. |
| Governance | Preserved | Cosmos remains the authoritative learner-record store. |
| Cost | Increased | Adds a Service Bus namespace and topic/subscription resources. |
| Operational complexity | Increased | Adds RBAC, monitoring, and message publication diagnostics. |

## Validation Plan

1. Run targeted Python tests for insights and shared learner-record behavior.
2. Add tests proving idempotent appends do not republish duplicate broker messages.
3. Run Terraform validation against the updated root module.
4. Verify the `azure.yaml` env contract remains consistent with Terraform outputs.

## Deployment Notes

- Deployment remains workflow-only through `.github/workflows/azd-deploy.yml`.
- No direct live deployment commands are part of this implementation.
- Service Bus will be provisioned through the existing Terraform + `azd` workflow after the code and infra changes merge.

## Risks And Rollback

- If Service Bus publication fails, the implementation should fail closed on publication only where explicitly intended; the authoritative Cosmos event path must remain understandable and testable.
- If Terraform provisioning introduces issues, rollback is a standard revert of the infrastructure/code change and rerun of the authorized GitHub workflow.
- If broker usage proves premature, the publishing decorator can be disabled by configuration without removing the authoritative event store.

## Approval Checkpoint

After approval, implement the hybrid slice in this order:

1. shared learner-record publication seam
2. insights wiring and tests
3. Terraform outputs and Service Bus resources
4. `azure.yaml` wiring and docs
5. targeted validation
