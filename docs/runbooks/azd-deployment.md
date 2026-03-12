# azd Deployment Runbook

This runbook describes how to provision and deploy Tutor with Azure Developer CLI (`azd`) and Terraform.

> **DEPLOYMENT POLICY — MANDATORY**
>
> All deployments to Azure **MUST** be performed via GitHub Workflows. Direct `azd deploy`, `az containerapp update`, or manual Docker pushes to ACR are **prohibited** for production environments. The only authorized deployment paths are:
>
> Authorized workflows:
>
- `.github/workflows/azd-deploy.yml` → Infrastructure + 8 backend services (Container Apps), triggered by push to `main` or `workflow_dispatch`.
- `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml` → Frontend (Static Web App), triggered by push to `main`, PR events, or `workflow_dispatch`.
>
> **Why:** GitHub Workflows provide auditable, reproducible deployments with proper secret management via OIDC federation. Manual deployments bypass CI checks, status gates, and deployment traceability.
>
> Local `azd provision` and `azd deploy` are permitted **only** for first-time bootstrap of a new environment (see [First-Time Bootstrap](#first-time-bootstrap-local)).

## Scope

- Repository: `Azure-Samples/tutor`
- Branch strategy: feature branches merge into `main`
- Deployment workflow: `.github/workflows/azd-deploy.yml`
- Infrastructure path: `infra/terraform`

## Required GitHub Secrets

Set these in repository or environment secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `NEXT_PUBLIC_APIM_BASE_URL` (used by Static Web Apps frontend build)

## Release Routing Policy

Current deployment routing in `.github/workflows/azd-deploy.yml` and `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`:

- Push to `main` triggers the authorized backend/frontend workflows.
- Manual `workflow_dispatch` can be used for controlled reruns.
- Production hardening and guardrails are enforced in workflow execution.

Default deployment region remains `eastus2`.

## First-Time Bootstrap (Local)

1. Authenticate:

```pwsh
az login
azd auth login
```

1. Select or create environment:

```pwsh
azd env select prod
# or
azd env new prod
```

1. Provision infra:

```pwsh
azd provision
```

1. Deploy services:

```pwsh
azd deploy --all
```

## APIM-First Deployment Order (Required)

Use this order to avoid frontend calls falling back to localhost or stale service URLs:

1. Provision infrastructure first (creates/updates APIM and routing resources):

```pwsh
azd provision
```

1. Deploy backend services through GitHub Actions workflow builds (recommended):

- Run `.github/workflows/azd-deploy.yml` with `workflow_dispatch`.
- The workflow now builds and pushes backend images to ACR, then updates Container Apps by image reference.
- Local `azd deploy <service>` Docker builds are no longer required for normal production delivery.

1. Validate APIM routes before frontend deployment:

```pwsh
$apim = azd env get-value NEXT_PUBLIC_APIM_BASE_URL
Invoke-RestMethod "$apim/api/avatar/health"
Invoke-RestMethod "$apim/api/configuration/ready"
Invoke-RestMethod "$apim/api/essays/health"
Invoke-RestMethod "$apim/api/questions/ready"
Invoke-RestMethod "$apim/api/upskilling/health"
Invoke-RestMethod "$apim/api/chat/ready"
Invoke-RestMethod "$apim/api/evaluation/health"
Invoke-RestMethod "$apim/api/lms-gateway/ready"
```

1. Frontend redeploy only after APIM is functional:
   - Set GitHub secret `NEXT_PUBLIC_APIM_BASE_URL` to the APIM gateway URL.
   - Run `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml` (`workflow_dispatch`) to redeploy only the frontend.

## Terraform Validation Before Deployment

```pwsh
cd infra/terraform
terraform init -backend=false
terraform validate
```

## Runtime Configuration Wiring

The app environment variables are sourced from Terraform outputs and mapped in `azure.yaml` per service.

Examples:

- `COSMOS_ENDPOINT`
- `COSMOS_DATABASE`
- `PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `MODEL_REASONING_DEPLOYMENT`
- `BLOB_CONNECTION_STRING`

For Entra-secured deployments, Terraform also emits:

- `ENTRA_AUTH_ENABLED`
- `ENTRA_TENANT_ID`
- `ENTRA_API_CLIENT_ID`
- `ENTRA_TOKEN_AUDIENCE`
- `ENTRA_ALLOWED_CLIENT_APP_IDS`

## Microsoft Entra app registration (session validation)

Use one Entra app registration for the backend API and one for the frontend client:

1. Create API app registration in Entra ID.
2. Expose API scope with Application ID URI `api://<ENTRA_API_CLIENT_ID>`.
3. Add app roles: `student`, `professor`, `admin`, `supervisor`.
4. Create frontend app registration and grant delegated permission to the API scope.
5. Assign test users/groups to API app roles.
6. Set Terraform vars: `entra_auth_enabled=true`, `entra_tenant_id`, `entra_api_client_id`, `entra_allowed_client_app_ids`.

Validate API session management by requesting a token and calling a protected endpoint:

```pwsh
# Example token retrieval depends on your client flow; once acquired:
$token = "<access_token>"
Invoke-RestMethod -Uri "https://<service-url>/datasets" -Headers @{ Authorization = "Bearer $token" }
```

Expected behavior:

- Missing/invalid token → `401`
- Valid token with wrong role → `403`
- Valid token with allowed role → `200`

The backend is stateless: no server-side session cache is used. Identity is validated per request from JWT claims and only a minimal request-scoped identity payload is passed to agents (`subject`, `tenant_id`, `object_id`, `roles`).

## Agent Entra permissions on provisioning

Set `agent_principal_object_ids` in Terraform for each agent-managed identity or service principal. Provisioning automatically assigns required roles on Cosmos, Blob, and ACR.

## Operational Checks

After deployment:

1. Confirm workflow succeeded in GitHub Actions.
2. Verify Container Apps revisions are healthy.
3. Check service logs in Log Analytics for startup errors.
4. Validate APIM endpoint and critical backend APIs through APIM paths.
5. Validate frontend endpoint after the SWA workflow completes.

## Rollback

- Re-run deployment from a known-good commit on `main`.
- If infrastructure drift is suspected:

```pwsh
cd infra/terraform
terraform plan
```

- Use ACA revision rollback for affected service if needed.

## Fast Environment Deprovision

Use `scripts/deprovision-environment.ps1` to remove and prune one environment quickly.

Dry-run:

```pwsh
pwsh ./scripts/deprovision-environment.ps1 -Environment dev
```

Execute deletion:

```pwsh
pwsh ./scripts/deprovision-environment.ps1 -Environment dev -Execute -WaitForDelete -ConfirmResourceGroup tutor-dev
```

Execute deletion + prune environment-specific ACR repositories:

```pwsh
pwsh ./scripts/deprovision-environment.ps1 -Environment dev -Execute -PruneAcrImages -WaitForDelete -ConfirmResourceGroup tutor-dev
```

## Incident Notes Template

Capture for each incident:

- Time window (UTC)
- Affected service(s)
- Failing workflow run URL
- Error signature
- Mitigation performed
- Follow-up action item
