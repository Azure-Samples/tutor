---
title: "Azure: Cost Optimization"
description: "Identify over-provisioned Azure resources and recommend SKU changes, reserved instances, and architectural simplifications."
mode: "TechLeadOrchestrator"
input: "Specify the subscription, resource group, or service to optimize. Include current monthly spend if known and target budget."
---

Coordinate Azure cost optimization across all resource types:

1. **Resource Inventory** — Invoke `platform-quality` via `#runSubagent` to catalog:
   - All active resources with current SKU, tier, and pricing model (pay-as-you-go vs reserved)
   - Utilization metrics for the last 30 days (CPU, memory, storage, RU, DTU)
   - Orphaned resources (unattached disks, unused public IPs, empty resource groups)

2. **Service-Specific Optimization** — Invoke each relevant Azure specialist via `#runSubagent`:
   - `AzureKubernetesSpecialist` — Node pool right-sizing, spot nodes for batch, cluster autoscaler tuning
   - `AzureAPIMSpecialist` — Tier suitability (Consumption vs Standard vs Premium), unused APIs
   - `AzureBlobStorageSpecialist` — Access tier optimization (hot→cool→archive), lifecycle automation
   - `AzureContainerAppsSpecialist` — Min replicas reduction, idle scaling to zero, consumption vs dedicated plan
   - `AzureCosmosDBSpecialist` — RU right-sizing, autoscale vs manual throughput, serverless for low-traffic
   - `AzureAIFoundrySpecialist` — Model deployment consolidation, PTU vs pay-per-call, unused endpoints
   - `AzurePostgreSQLSpecialist` — Compute tier right-sizing, storage autogrow limits, burstable vs general purpose
   - `AzureRedisSpecialist` — Cache tier downgrade, eviction policy tuning, clustering necessity
   - `AzureStaticWebAppsSpecialist` — Free vs Standard tier, unused staging environments

3. **Financial Modeling** — Invoke `financial-modeling-agent` via `#runSubagent` to:
   - Build cost comparison: current vs optimized (per resource and aggregate)
   - Model reserved instance savings (1-year vs 3-year commitments)
   - Estimate savings from architectural changes (e.g., merge services, replace premium with standard)

4. **Risk Assessment** — Invoke `risk-analysis-agent` via `#runSubagent` to:
   - Flag optimization proposals that could degrade reliability or performance
   - Identify minimum viable SKUs below which SLAs are at risk

5. **Optimization Plan** — Deliver:
   - Prioritized list of changes ranked by savings (quick wins first)
   - Estimated monthly savings per change
   - Implementation steps and rollback plan for each
   - Total projected monthly/annual savings
