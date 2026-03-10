# Incremental Infrastructure Provisioning Runbook

## Goal

Run provisioning only for stacks affected by a change set, without `terraform -target`, and keep deployment execution in GitHub Actions.

## Current State

- Backend image deployments are already selective by changed service.
- `azd provision` still applies the full Terraform graph from one root (`infra/terraform`).
- Frontend code deploy is handled by the SWA workflow.

## Recommended Stack Boundaries

Use explicit stack boundaries aligned to microservice ownership (microservices.io: Database per Service and API Gateway patterns) while keeping platform primitives in a shared foundation.

1. Foundation stack: `infra/terraform` (current root)

- Resource group, Log Analytics, Application Insights
- Container Apps environment, ACR, storage, Cosmos account/database/containers
- APIM service instance (not service-specific APIs)
- AI Foundry shared resources

1. Service-edge stacks (Phase 1): `infra/terraform/stacks/services/<service>/`

- APIM API artifact(s) for one service only
- APIM operations and policy for one service only

1. Service-runtime stacks (Phase 2): `infra/terraform/stacks/runtime/<service>/`

- Container App for one service only
- Service-specific RBAC and role assignments

1. Frontend infra stack (optional): `infra/terraform/stacks/frontend/`

- SWA infra-only changes (custom domain/auth/app settings) if needed
- Frontend UI code remains in SWA workflow

## Workflow Routing by Changed Paths

### Backend workflow (`.github/workflows/azd-deploy.yml`)

- `azure.yaml`, `infra/terraform/*` (excluding `infra/terraform/stacks/**`), `.github/workflows/azd-deploy.yml`:
  - `provision_required=true`
  - deploy backend image matrix for all services
- `apps/<service>/**`:
  - deploy backend image for that service only
  - no foundation provision
- `lib/**`:
  - deploy backend image matrix for all services
  - no foundation provision
- `infra/terraform/stacks/services/<service>/**`:
  - flag service infra change for that service (`service_infra_json`)
  - foundation provision remains off unless shared infra also changed
- `infra/terraform/stacks/frontend/**`:
  - flag frontend infra change (`changed_frontend_infra=true`)
  - foundation provision remains off unless shared infra also changed
- `frontend/**`:
  - tracked as `changed_frontend_ui=true` for observability only
  - no backend deploy/provision action

### Frontend workflow (`.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`)

- Triggers on:
  - `frontend/**`
  - `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`

This avoids unnecessary UI pipeline runs on backend-only merges.

## Phase Plan and Minimal File Edits

### Phase 1 (implemented now)

Changed files:

- `.github/workflows/azd-deploy.yml`
- `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`

What is implemented:

- Stack-aware path detection outputs (`service_infra_json`, frontend change flags).
- Foundation `azd provision` runs only for shared infra/root changes.
- Frontend workflow is path-scoped to frontend changes.

What remains to activate Phase 1 end-to-end:

- Add concrete Terraform roots under `infra/terraform/stacks/services/<service>/` for APIM service-edge resources.
- Add matrix apply job in backend workflow for `service_infra_json` once stack roots are merged.

### Phase 2 (prepared, not yet activated)

Planned file additions:

- `infra/terraform/stacks/runtime/<service>/*.tf` per service

Planned workflow extension:

- Add runtime-stack matrix apply job gated by `infra/terraform/stacks/runtime/<service>/**` changes.
- Keep execution order: foundation first, then runtime stacks in parallel.

## Safety and Governance Controls

- No `terraform -target`.
- Keep one stack per state key to avoid cross-stack drift.
- Maintain plan-before-apply in every stack job.
- Keep deployment policy intact: GitHub workflows are the only production deployment path.

## Risks

1. Split-brain ownership during migration if a resource is managed by both foundation and a new stack.
2. State migration mistakes when moving APIM or Container App resources to new stack state keys.
3. Path routing false negatives if new directories are added without updating patterns.

## Rollback Strategy

1. Disable stack-specific routing by reverting `.github/workflows/azd-deploy.yml` to previous detect logic.
2. Keep foundation-only provisioning path (`azd provision`) as authoritative fallback.
3. Re-run backend deployment matrix from workflow_dispatch after rollback to restore app revisions.
4. If frontend trigger scoping causes missed deploys, revert path filters in `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`.

## Validation Checklist

1. Push app-only change under `apps/essays/**`: only essays deploy job runs.
2. Push `frontend/**` change: only SWA workflow runs.
3. Push shared infra change under `infra/terraform/main.tf`: foundation provision runs.
4. Push file under `infra/terraform/stacks/services/avatar/**`: `service_infra_json` includes avatar.
