---
applyTo: '**/*.tf,**/*.bicep,**/azure-*.yml,**/infra-*.yml'
---

## Azure Infrastructure & Deployment Standards

All Azure infrastructure and deployments MUST follow these rules:

### 1. IaC with Azure Verified Modules & Terraform
- **Always use Terraform** as the primary IaC tool
- Use [Azure Verified Modules (AVM)](https://azure.github.io/Azure-Verified-Modules/) for all resource definitions — never hand-roll modules when an AVM exists
- Pin module versions explicitly; never use `latest` or floating refs
- Store Terraform state in Azure Storage with state locking enabled
- Separate Terraform configurations by layer (networking → platform services → workloads)

### 2. VNet & Private Endpoints
- **Always deploy services with Private Endpoints** — disable public network access for production
- Configure Azure Private DNS Zones for the relevant service's `privatelink.*` domain
- Use **service endpoints** only as a transitional step; Private Endpoints are the target state
- Restrict firewalls to the VNet and specific management IPs only

### 3. Zero-Downtime Deployments
- All changes must be **additive** — avoid operations that block existing workloads
- Use feature flags, blue-green, or canary strategies for high-risk releases
- Test changes in a non-production environment first
- Deploy infrastructure changes in a separate workflow that runs before application deployments

### 4. Modular GitHub Workflows
- Separate workflows per concern: infrastructure (Terraform plan/apply), application deployment, integration tests
- Use **reusable workflows** for Terraform plan/apply patterns
- Use **OIDC federation** for GitHub Actions → Azure authentication — prefer Entra ID RBAC over keys/secrets
- Implement **environment protection rules** for production changes

### 5. Response Guidelines
- **Terraform first**: All resources provisioned via Terraform with AVM modules
- **Security by default**: Entra ID RBAC over access keys, Private Endpoints, no public access
- **Cost-aware**: Estimate costs and recommend right-sizing; prefer autoscale where available
- **Diagnostics-driven**: Capture and analyse diagnostic data for any performance investigation
