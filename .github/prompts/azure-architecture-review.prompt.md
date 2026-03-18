---
title: "Azure: Architecture Review"
description: "Review Azure resource topology for high availability, security, cost efficiency, and Well-Architected Framework alignment."
mode: "TechLeadOrchestrator"
input: "Specify the Azure resource group, subscription, or architecture diagram to review. Include SLA targets and compliance requirements."
---

Coordinate a multi-specialist Azure architecture review:

**Delegation compatibility**: If the workspace has `.github/agents/data/team-mapping.md`, resolve exact agent names from it before calling `#runSubagent`. Otherwise, use the canonical agent names in this prompt and fall back to current-agent execution if a specialist is unavailable.

1. **Topology Discovery** — Invoke `SystemArchitect` via `#runSubagent` to map:
   - Resource dependency graph (what talks to what)
   - Data flow paths (ingress → processing → storage → egress)
   - Network topology (VNets, subnets, NSGs, private endpoints)
   - Identity and access boundaries (managed identities, RBAC assignments)

2. **Service-Specific Review** — Invoke the relevant Azure specialists via `#runSubagent` to audit each resource against best practices:
   - `AzureKubernetesSpecialist` — Node pool sizing, pod disruption budgets, network policies, upgrade strategy
   - `AzureAPIMSpecialist` — Policy chain correctness, rate limiting, caching, backend health probes
   - `AzureBlobStorageSpecialist` — Access tiers, lifecycle policies, redundancy (LRS/ZRS/GRS), private endpoints
   - `AzureContainerAppsSpecialist` — Scaling rules, Dapr components, revision management, ingress config
   - `AzureCosmosDBSpecialist` — Partition key choice, RU budgeting, consistency level, indexing policy
   - `AzureAIFoundrySpecialist` — Model deployment SKU, content safety filters, quota allocation
   - `AzurePostgreSQLSpecialist` — HA configuration, connection pooling (PgBouncer), backup retention, pgvector indexes
   - `AzureRedisSpecialist` — Eviction policy, clustering, persistence, connection limits
   - `AzureStaticWebAppsSpecialist` — Custom domains, API routing, auth providers, staging environments

3. **Cross-Cutting Assessment** — Invoke `PlatformEngineer` via `#runSubagent` to check:
   - IaC coverage (are all resources defined in Bicep/Terraform?)
   - Monitoring and alerting completeness (Azure Monitor, Application Insights)
   - Disaster recovery posture (RPO/RTO targets met?)
   - Secret management (Key Vault integration, no hardcoded credentials)

4. **Cost Analysis** — Invoke `FinancialModeler` via `#runSubagent` to:
   - Estimate monthly cost by resource
   - Identify over-provisioned resources (SKU downgrades, reserved instances)
   - Compare current architecture cost vs optimized alternative

5. **Findings Report** — Consolidate into a Well-Architected Framework scorecard:
   - Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency
   - Per-pillar score (pass/partial/fail) with evidence
   - Top 10 remediation items ranked by impact

Deliver the scorecard, architecture diagram (Mermaid), and prioritized remediation backlog.
