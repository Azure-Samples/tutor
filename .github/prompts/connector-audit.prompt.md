---
title: "Connector: Audit Integrations"
description: "Audit existing enterprise integrations for reliability, error handling, compliance, and operational health."
mode: "TechLeadOrchestrator"
input: "Specify the integration(s) to audit. Include the external platform, data flow direction, and any known issues."
---

Coordinate an enterprise integration audit:

1. **Integration Inventory** — Invoke `enterprise-connectors` via `#runSubagent` to catalog:
   - All active integrations (platform, protocol, direction, frequency)
   - Authentication method per integration (API key, OAuth, mTLS, service account)
   - Data volume and throughput per connector
   - Error rates and last-known failure dates

2. **Reliability Assessment** — Invoke `enterprise-connectors` via `#runSubagent` to evaluate:
   - Retry logic and idempotency guarantees
   - Circuit breaker implementation (or lack thereof)
   - Rate limit handling (backoff strategy, quota monitoring)
   - Timeout configuration and connection pool management
   - Dead-letter handling for failed messages

3. **Code Quality** — Invoke the relevant language specialist via `#runSubagent`:
   - `python-specialist` / `rust-specialist` / `typescript-specialist` — Review connector code for error handling, type safety, test coverage

4. **Security & Compliance** — Invoke `risk-analysis-agent` via `#runSubagent` to check:
   - Credential rotation policy (are secrets expired or long-lived?)
   - Data handling compliance (PII masking, retention policies, GDPR/LGPD)
   - Audit trail completeness (can we trace every data exchange?)
   - Least-privilege access (are API scopes minimal?)

5. **Operational Health** — Invoke `platform-quality` via `#runSubagent` to verify:
   - Monitoring coverage (alerts on failure, latency, throughput drop)
   - Logging (structured, correlation IDs, no PII in logs)
   - Runbook exists for each integration failure scenario
   - Dependency health checks (external API status monitoring)

6. **Audit Report** — Deliver:
   - Per-integration health scorecard (reliability, security, observability)
   - Critical findings requiring immediate remediation
   - Improvement recommendations ranked by risk reduction
   - Suggested SLA definitions for each integration
