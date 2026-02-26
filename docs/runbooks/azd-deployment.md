# azd Deployment Runbook

This runbook describes how to provision and deploy Tutor with Azure Developer CLI (`azd`) and Terraform.

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

## Workflow Defaults

Current workflow defaults in `.github/workflows/azd-deploy.yml`:

- `AZURE_ENV_NAME=prod`
- `AZURE_LOCATION=eastus`

Adjust in the workflow file if your target environment differs.

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
4. Validate frontend endpoint and critical backend APIs.

## Rollback

- Re-run deployment from a known-good commit on `main`.
- If infrastructure drift is suspected:

```pwsh
cd infra/terraform
terraform plan
```

- Use ACA revision rollback for affected service if needed.

## Incident Notes Template

Capture for each incident:

- Time window (UTC)
- Affected service(s)
- Failing workflow run URL
- Error signature
- Mitigation performed
- Follow-up action item
