# ADR-002: Azure Runtime and Infrastructure

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | Azure Container Apps runtime, Terraform with Azure Verified Modules, and workflow-governed Azure deployment |

---

## Context

Tutor needs independently deployable backend services, secure cloud resources, repeatable infrastructure provisioning, and auditable deployment operations. The platform currently runs nine backend services and a Static Web Apps frontend:

- `avatar`
- `chat`
- `configuration`
- `essays`
- `evaluation`
- `insights`
- `lms-gateway`
- `questions`
- `upskilling`

These services have different scaling profiles and security needs. Agentic services consume AI resources, configuration and integration services need stable data access, and the frontend must route through APIM rather than directly to service-specific origins.

## Decision

Use Azure Container Apps as the backend runtime, Azure Static Web Apps as the frontend host, API Management as the API edge, and Terraform with Azure Verified Modules as the primary infrastructure-as-code path.

Normal Azure deployments are performed only through the repository GitHub workflows:

- `.github/workflows/azd-deploy.yml` for infrastructure and backend Container Apps.
- `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml` for the frontend Static Web App.

`azd provision` and `azd deploy` are reserved for first-time environment bootstrap or documented break-glass work. Direct production `az containerapp update`, manual Docker pushes, and ad hoc production mutation are not authorized.

Core infrastructure responsibilities:

- Terraform under `infra/terraform` is the primary IaC implementation.
- Legacy Bicep under `infra/main.bicep` and `infra/modules/` is preserved only as reference while Terraform remains authoritative.
- Each backend Container App uses managed identity for Azure resource access.
- Container images are built and deployed through GitHub Actions.
- APIM fronts backend APIs and the frontend consumes APIM paths.
- Log Analytics and Application Insights capture operational diagnostics.
- Terraform remote state is used for drift-aware infrastructure operations.

## Consequences

### Positive

- Independent scaling and deployment for each backend service.
- Repeatable, auditable, workflow-governed Azure changes.
- Stronger parity between environments through Terraform variables and modules.
- Reduced production risk by routing deployment through CI checks and OIDC-based identity.

### Negative

- More moving parts than a single-app deployment.
- Terraform, azd, APIM, ACA, and GitHub Actions all need operational literacy.
- Bootstrap and break-glass processes must be clearly separated from normal deployment.

### Guardrails

- Do not bypass GitHub workflows for normal Azure deployment.
- Keep `azure.yaml` aligned to the actual service inventory.
- Keep APIM routes, frontend environment resolution, and backend health probes in sync.
- Treat direct Azure changes as incidents or bootstrap steps, not routine operations.

## References

- [Azure Container Apps documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)
- [azd with Terraform](https://learn.microsoft.com/azure/developer/azure-developer-cli/use-terraform-for-azd)
- [Terraform remote state on Azure](https://learn.microsoft.com/azure/developer/terraform/store-state-in-azure-storage)
