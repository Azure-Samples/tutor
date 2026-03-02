# ADR-004: Terraform with Azure Verified Modules

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The current infrastructure uses **Azure Bicep** with custom modules (`infra/modules/*.bicep`). While functional, this approach has limitations:

1. **No Azure Verified Module (AVM) compliance** — Custom Bicep modules don't leverage Microsoft's tested, maintained module library.
2. **No `azd` integration** — There is no `azure.yaml` manifest, so `azd up` / `azd deploy` cannot be used.
3. **Single deployment unit** — All resources deploy together; no way to provision shared infra separately from per-service resources.
4. **No state management** — Bicep deployments are idempotent but have no remote state tracking for drift detection.
5. **Limited team familiarity** — Terraform has broader community adoption and multi-cloud portability.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Keep Bicep (custom)** | Already written, Azure-native | No AVM, no state, no azd |
| **Bicep + AVM** | Azure-native, AVM compliant | Less portable, weaker state management |
| **Terraform + AVM** | State management, AVM modules, azd support, multi-cloud | Learning curve, extra tooling |
| **Pulumi** | Programmatic (Python), state mgmt | Smaller community, vendor lock-in |

## Decision

**Migrate infrastructure to Terraform using Azure Verified Modules (AVM)**, integrated with **Azure Developer CLI (`azd`)** for deployment orchestration.

### 1. Directory Structure

```
infra/
├── terraform/
│   ├── main.tf                    # Root module composition
│   ├── variables.tf               # Input variables
│   ├── outputs.tf                 # Output values
│   ├── providers.tf               # azurerm, azapi providers
│   ├── backend.tf                 # Remote state (Azure Storage)
│   ├── terraform.tfvars.sample    # Example variable values
│   └── modules/
│       ├── networking/
│       │   └── main.tf            # VNet, subnets, NSGs, private DNS
│       ├── data/
│       │   └── main.tf            # Cosmos DB, Blob Storage
│       ├── compute/
│       │   └── main.tf            # ACA Environment + Container Apps
│       ├── ai/
│       │   └── main.tf            # OpenAI, Speech, AI Foundry
│       ├── security/
│       │   └── main.tf            # Key Vault, Managed Identities, RBAC
│       ├── observability/
│       │   └── main.tf            # Log Analytics, App Insights
│       └── registry/
│           └── main.tf            # ACR
├── bicep/                         # Legacy (preserved for reference)
│   ├── main.bicep
│   └── modules/
└── environments/
    ├── dev.tfvars
    ├── test.tfvars
    └── prod.tfvars
```

### 2. Azure Verified Modules Used

| Resource | AVM Module | Registry Path |
|----------|-----------|---------------|
| VNet | `avm/res/network/virtual-network` | `registry.terraform.io/Azure/avm-res-network-virtualnetwork` |
| NSG | `avm/res/network/network-security-group` | `registry.terraform.io/Azure/avm-res-network-networksecuritygroup` |
| Cosmos DB | `avm/res/document-db/database-account` | `registry.terraform.io/Azure/avm-res-documentdb-databaseaccount` |
| Key Vault | `avm/res/key-vault/vault` | `registry.terraform.io/Azure/avm-res-keyvault-vault` |
| ACR | `avm/res/container-registry/registry` | `registry.terraform.io/Azure/avm-res-containerregistry-registry` |
| ACA Env | `avm/res/app/managed-environment` | `registry.terraform.io/Azure/avm-res-app-managedenvironment` |
| ACA App | `avm/res/app/container-app` | `registry.terraform.io/Azure/avm-res-app-containerapp` |
| Log Analytics | `avm/res/operational-insights/workspace` | `registry.terraform.io/Azure/avm-res-operationalinsights-workspace` |
| OpenAI | `avm/res/cognitive-services/account` | `registry.terraform.io/Azure/avm-res-cognitiveservices-account` |
| Storage | `avm/res/storage/storage-account` | `registry.terraform.io/Azure/avm-res-storage-storageaccount` |
| Static Web App | `avm/res/web/static-site` | `registry.terraform.io/Azure/avm-res-web-staticsite` |
| User Managed Identity | `avm/res/managed-identity/user-assigned-identity` | `registry.terraform.io/Azure/avm-res-managedidentity-userassignedidentity` |

### 3. `azd` Integration

```yaml
# azure.yaml
name: tutor
metadata:
  template: tutor@0.2.0

infra:
  provider: terraform
  path: infra/terraform

services:
  ui:
    project: frontend
    dist: .next
    language: js
    host: staticwebapp

  config-svc:
    project: apps/configuration/src
    language: python
    host: containerapp
    docker:
      path: ../../Dockerfile
      context: ../..

  essays-svc:
    project: apps/essays/src
    language: python
    host: containerapp
    docker:
      path: ../../Dockerfile
      context: ../..

  questions-svc:
    project: apps/questions
    language: python
    host: containerapp
    docker:
      path: ../Dockerfile
      context: ..

  avatar-svc:
    project: apps/avatar/src
    language: python
    host: containerapp
    docker:
      path: ../../Dockerfile
      context: ../..

  upskilling-svc:
    project: apps/upskilling
    language: python
    host: containerapp
    docker:
      path: ../Dockerfile
      context: ..

  evaluation-svc:
    project: apps/evaluation/src
    language: python
    host: containerapp
    docker:
      path: ../../Dockerfile
      context: ../..

  lms-gateway:
    project: apps/lms-gateway/src
    language: python
    host: containerapp
    docker:
      path: ../../Dockerfile
      context: ../..
```

### 4. Remote State

```hcl
# backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "tutor-state-rg"
    storage_account_name = "tutortfstate"
    container_name       = "tfstate"
    key                  = "tutor.terraform.tfstate"
  }
}
```

## Consequences

### Positive

- **AVM compliance** — All modules are Microsoft-tested, well-documented, and regularly updated.
- **State management** — Remote state enables drift detection, `terraform plan` preview, and team collaboration.
- **`azd` integration** — `azd up` provisions infra + deploys all services in one command.
- **Environment parity** — `dev.tfvars` / `test.tfvars` / `prod.tfvars` ensure consistent environments.
- **Modular composition** — Each domain (networking, data, compute) is an independent module.

### Negative

- **Migration effort** — Existing Bicep must be translated to Terraform (one-time cost).
- **Tooling requirement** — Team must install Terraform CLI alongside Azure CLI.
- **Two IaC languages** — During transition, both Bicep (legacy) and Terraform (target) coexist.

### Migration Path

1. Preserve existing `infra/` Bicep in `infra/bicep/` for reference.
2. Build Terraform modules incrementally (networking → data → compute → AI).
3. Import existing Azure resources into Terraform state with `terraform import`.
4. Validate parity with `terraform plan` (no-op expected).
5. Remove Bicep modules after successful production deployment.

## References

- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)
- [Terraform AVM Registry](https://registry.terraform.io/namespaces/Azure)
- [azd + Terraform](https://learn.microsoft.com/azure/developer/azure-developer-cli/use-terraform-for-azd)
- [Terraform remote state on Azure](https://learn.microsoft.com/azure/developer/terraform/store-state-in-azure-storage)
