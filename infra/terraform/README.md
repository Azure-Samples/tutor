# Terraform Provisioning (azd)

This directory contains the baseline Azure provisioning for Tutor using Terraform and Azure Developer CLI.

## Provisioned resources

- Resource Group
- Log Analytics Workspace
- Application Insights
- Azure Container Registry
- Storage Account + `uploads` container
- Azure Cosmos DB (SQL API) with service containers

## Prerequisites

- Azure CLI (`az`)
- Azure Developer CLI (`azd`)
- Terraform (`terraform`)

## Quickstart

```pwsh
azd auth login
azd env new <environment-name>
azd provision
```

## Remote state bootstrap (Phase 3)

1. Create Azure Storage backend resources:

```pwsh
./scripts/bootstrap-state.ps1 -Location eastus
```

1. Copy the sample backend config and adjust key/env values:

```pwsh
Copy-Item backend.hcl.sample backend.hcl
```

1. Initialize Terraform with remote backend settings:

```pwsh
terraform init -backend-config=backend.hcl
```

## CI backend validation path

The deployment workflow validates Terraform against the real remote backend (not `-backend=false`).

Add these repository secrets for `.github/workflows/azd-deploy.yml`:

- `TERRAFORM_STATE_RESOURCE_GROUP`
- `TERRAFORM_STATE_STORAGE_ACCOUNT`
- `TERRAFORM_STATE_CONTAINER`
- `TERRAFORM_STATE_KEY` (optional; defaults to `tutor-<AZURE_ENV_NAME>.tfstate`)

During CI, the workflow writes `infra/terraform/backend.hcl`, runs:

```bash
terraform init -reconfigure -backend-config=backend.hcl
terraform state pull
terraform validate
```

## Validate locally

```pwsh
cd infra/terraform
terraform init -backend=false
terraform validate
terraform plan -var-file=terraform.tfvars.sample
```

## Entra ID authentication and agent permissions

Set these Terraform variables to enable backend JWT validation:

- `entra_auth_enabled` (`true` to enforce token validation)
- `entra_tenant_id` (tenant GUID)
- `entra_api_client_id` (App Registration client ID for the backend API)
- `entra_allowed_client_app_ids` (comma-separated frontend/API client IDs allowed as `azp`/`appid`)

Set `agent_principal_object_ids` with managed identity object IDs for agent workloads so Terraform assigns:

- `Cosmos DB Built-in Data Contributor`
- `Storage Blob Data Contributor`
- `AcrPull`

Example:

```hcl
entra_auth_enabled           = true
entra_tenant_id              = "00000000-0000-0000-0000-000000000000"
entra_api_client_id          = "11111111-1111-1111-1111-111111111111"
entra_allowed_client_app_ids = "22222222-2222-2222-2222-222222222222"

agent_principal_object_ids = [
  "33333333-3333-3333-3333-333333333333",
  "44444444-4444-4444-4444-444444444444",
]
```

## Notes

- This is a foundation scaffold to unblock provisioning and service wiring.
- Existing Bicep assets in `infra/` remain available for reference during migration.
- `backend.hcl` is intentionally untracked; keep per-environment backend files local or in secure CI variables.
