---
title: "Azure: Migration Plan"
description: "Plan migration between Azure services, from on-premises, or from other cloud providers with risk assessment and staged rollout."
mode: "TechLeadOrchestrator"
input: "Describe the source (current service/provider) and target (desired Azure service). Include data volumes, latency requirements, and downtime tolerance."
---

Coordinate multi-agent migration planning:

**Delegation compatibility**: If the workspace has `.github/agents/data/team-mapping.md`, resolve exact agent names from it before calling `#runSubagent`. Otherwise, use the canonical agent names in this prompt and fall back to current-agent execution if a specialist is unavailable.

1. **Current State Assessment** — Invoke `SystemArchitect` via `#runSubagent` to document:
   - Current architecture topology and dependencies
   - Data stores, volumes, and access patterns
   - Integration points that will be affected
   - Non-functional requirements (latency, throughput, availability SLA)

2. **Target Architecture Design** — Invoke the relevant Azure specialist(s) via `#runSubagent`:
   - `AzureKubernetesSpecialist` — Container orchestration migration (Docker Compose → AKS, ECS → AKS)
   - `AzureContainerAppsSpecialist` — Serverless container migration (Lambda → Container Apps, Fargate → Container Apps)
   - `AzureCosmosDBSpecialist` — NoSQL migration (DynamoDB → Cosmos DB, MongoDB → Cosmos DB)
   - `AzurePostgreSQLSpecialist` — Relational migration (RDS → Azure PostgreSQL, on-prem → Flexible Server)
   - `AzureRedisSpecialist` — Cache migration (ElastiCache → Azure Redis, Memcached → Redis)
   - `AzureBlobStorageSpecialist` — Object storage migration (S3 → Blob, GCS → Blob)
   - `AzureAPIMSpecialist` — API gateway migration (Kong → APIM, AWS API Gateway → APIM)
   - `AzureAIFoundrySpecialist` — AI/ML migration (SageMaker → AI Foundry, Vertex → AI Foundry)
   - `AzureStaticWebAppsSpecialist` — Frontend hosting migration (Vercel/Netlify → SWA, S3+CloudFront → SWA)

3. **Application Changes** — Invoke language specialists via `#runSubagent` to assess code impact:
   - `PythonDeveloper` / `RustDeveloper` / `TypeScriptDeveloper` — SDK changes, connection string updates, feature parity gaps

4. **Infrastructure Changes** — Invoke `PlatformEngineer` via `#runSubagent` to plan:
   - IaC templates (Bicep/Terraform) for the target architecture
   - CI/CD pipeline changes for new deployment targets
   - DNS cutover, certificate provisioning, and network routing

5. **Risk Analysis** — Invoke `RiskAnalyst` via `#runSubagent` to evaluate:
   - Data loss risk during migration
   - Downtime windows and rollback procedures
   - Feature parity gaps between source and target
   - Cost delta (source vs target steady-state)

6. **Migration Stages** — Deliver a phased plan:
   - **Stage 1: Prepare** — Provision target resources, set up parallel pipelines
   - **Stage 2: Dual-Write** — Write to both source and target, validate consistency
   - **Stage 3: Cutover** — Switch reads to target, monitor error rates
   - **Stage 4: Decommission** — Remove source resources after validation period
   - Rollback trigger criteria for each stage
