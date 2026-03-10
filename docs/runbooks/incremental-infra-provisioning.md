# Incremental Infrastructure Provisioning Runbook

## Goal
Enable infrastructure provisioning to run only for changed domains/apps while keeping production stable.

## Current State
- CI deploys backend app images selectively per changed service.
- Infrastructure provisioning uses one Terraform root/state, so `azd provision` applies the full graph.
- UI changes are deployed via the Static Web Apps workflow and generally do not require infra apply.

## Why full-graph apply happens today
A single state contains shared resources plus app resources:
- Shared foundation (RG, networking, APIM, Cosmos, ACR, Foundry, etc.)
- Per-service resources (Container Apps, APIM API artifacts, identities, role assignments)

With this model, safe changed-only infra provisioning is not guaranteed, because dependency edges cross service boundaries.

## Feasibility Summary
- Backend image-only change: fully feasible today (already selective).
- UI-only change: fully feasible today (SWA workflow handles it).
- Infra changed-only for one app: not safely feasible with current single state.
- Infra changed-only per app: feasible after stack/state decomposition.

## Target Architecture
Split infrastructure into multiple Terraform stacks/states:

1) Foundation stack (shared)
- Resource group, VNet/subnets, Log Analytics, Application Insights
- APIM service (instance only), Cosmos account/database (shared decisions), ACR
- Shared identities/policies that are not app-specific

2) Service stack per backend app
- Container App for that service
- Service-specific managed identity role assignments
- APIM API, operations, and policy for only that service

3) Frontend stack (optional)
- Only if frontend infra changes are needed (custom domains, auth providers, app settings)
- Keep normal UI code deploy in SWA workflow

## Migration Phases

### Phase 0: Stabilize current pipeline
- Keep `provision` gated to infra/shared changes only.
- Keep selective backend image deploy matrix.

Exit criteria:
- App-only backend pushes do not run infra provision.

### Phase 1: Extract APIM per-service resources
- Move APIM API resources into service-specific Terraform modules.
- Keep APIM service itself in foundation stack.

Exit criteria:
- A change in one service APIM policy/API does not require touching other service APIM resources.

### Phase 2: Extract service runtime resources
- Move each `azurerm_container_app` + app-specific RBAC to per-service stacks.
- Keep shared ACR and networking in foundation.

Exit criteria:
- Service infra can be planned/applied independently with no cross-service drift.

### Phase 3: CI orchestration for stack routing
- Detect changed paths and map to stack(s):
  - `infra/foundation/**` -> foundation plan/apply
  - `infra/services/<service>/**` -> only that service stack
  - `frontend/**` -> SWA build/deploy workflow; run frontend infra stack only if frontend infra paths changed
- Add apply ordering when multiple stacks changed:
  - foundation first, then service stacks in parallel.

Exit criteria:
- Provisioning scope matches changed stack scope.

### Phase 4: Hardening
- Add drift detection jobs per stack (plan-only on schedule).
- Add stack-level lock and retry strategy.
- Add change windows for foundation stack.

Exit criteria:
- Predictable, low-latency CI for app-level infra changes.

## CI Design Notes
- Continue path-based detection in `detect-changes`.
- Introduce outputs:
  - `changed_foundation`
  - `changed_services_json`
  - `changed_frontend_infra`
- Use matrix job over changed service stacks for infra apply.
- Keep production deployment policy: deployments happen via GitHub workflows only.

## Safety Controls
- No `-target` in production applies (use separated stacks instead).
- Require successful plan for each stack before apply.
- Require foundation apply success before dependent service applies.
- Keep state backend and RBAC checks in every stack job.

## Recommended Next Increment
Implement Phase 1 first:
- Extract APIM API/operation/policy for each service into per-service modules.
- Keep outputs/contracts from foundation for APIM service id/name.
- Update workflow to run per-service APIM module apply based on changed service paths.

This gives immediate value with lower blast radius and minimal disruption.
