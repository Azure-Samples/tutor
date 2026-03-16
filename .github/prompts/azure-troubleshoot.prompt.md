---
title: "Azure: Troubleshoot Service"
description: "Debug a failing Azure service by coordinating the relevant Azure specialist with platform diagnostics."
mode: "TechLeadOrchestrator"
input: "Describe the issue: which Azure service, error messages, affected endpoints, and when it started. Include resource group and service name."
---

Coordinate Azure service troubleshooting:

1. **Symptom Classification** — Identify the failing service type and route to the appropriate specialist via `#runSubagent`:
   - `AzureKubernetesSpecialist` — Pod crashes, image pull failures, node pressure, network policy blocks
   - `AzureAPIMSpecialist` — 502/504 errors, policy evaluation failures, backend timeouts, certificate issues
   - `AzureBlobStorageSpecialist` — 403 auth failures, throttling (429), lifecycle policy misfires, replication lag
   - `AzureContainerAppsSpecialist` — Cold start latency, scaling failures, Dapr sidecar errors, revision rollback
   - `AzureCosmosDBSpecialist` — 429 throttling (RU exceeded), cross-partition query timeouts, consistency anomalies
   - `AzureAIFoundrySpecialist` — Model deployment failures, quota exceeded, content filter blocks, inference latency
   - `AzurePostgreSQLSpecialist` — Connection exhaustion, slow queries, replication lag, storage full
   - `AzureRedisSpecialist` — Cache misses, eviction storms, connection timeouts, memory pressure
   - `AzureStaticWebAppsSpecialist` — Build failures, routing mismatches, auth callback errors, API cold starts

2. **Log Analysis** — Invoke `platform-quality` via `#runSubagent` to:
   - Query Azure Monitor / Log Analytics with KQL for the relevant error patterns
   - Check resource health and recent Azure status incidents
   - Review activity log for recent configuration changes that may have caused the regression

3. **Root Cause Isolation** — The Azure specialist narrows the cause. Typical categories:
   - Configuration drift (recent change broke something)
   - Scaling limit hit (quota, RU, connection pool exhaustion)
   - Dependency failure (downstream service, DNS, certificate expiry)
   - Code regression (bad deployment, missing env var)

4. **Fix Implementation** — Delegate the fix to the appropriate agent:
   - Infrastructure fix → `platform-quality`
   - Application code fix → `python-specialist` / `rust-specialist` / `typescript-specialist`
   - Configuration fix → relevant Azure specialist

5. **Verification** — Invoke `platform-quality` to confirm:
   - Error rate returns to baseline
   - Health checks pass
   - No new alerts triggered

Deliver a troubleshooting report with root cause, fix applied, and prevention recommendations.
