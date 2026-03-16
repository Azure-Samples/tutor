---
title: "Security Audit"
description: "Full-stack security audit across code, infrastructure, dependencies, secrets, and cloud configuration."
mode: "TechLeadOrchestrator"
input: "Specify the scope: entire repo, specific service, or specific concern (OWASP category, dependency CVE, secret leak). Include compliance targets if applicable (SOC2, HIPAA, PCI-DSS)."
---

Coordinate a comprehensive security audit by delegating to all relevant specialists:

1. **Dependency Vulnerabilities** — Invoke `platform-quality` via `#runSubagent` to:
   - Run all package audits (npm audit, cargo audit, pip-audit, trivy)
   - Classify findings by severity (critical/high/medium/low)
   - Identify transitive dependency risks (nested vulnerabilities)
   - Check for abandoned packages (no updates in 12+ months)

2. **Application Code** — Invoke language specialists via `#runSubagent` to audit OWASP Top 10:
   - `python-specialist` — SQL injection (parameterized queries), SSRF, insecure deserialization, auth bypass
   - `rust-specialist` — Unsafe blocks, FFI boundary validation, panic paths in production, input parsing
   - `typescript-specialist` — XSS (dangerouslySetInnerHTML), CSRF, prototype pollution, JWT validation

3. **Infrastructure & Secrets** — Invoke `platform-quality` via `#runSubagent` to check:
   - No secrets in code, env files, or CI logs (scan for patterns: API keys, tokens, connection strings)
   - Secret rotation policy (Key Vault, GitHub Secrets — age and expiry)
   - CI/CD pipeline security (least-privilege tokens, no --no-verify, signed commits)
   - Container image scanning (if applicable)

4. **Cloud Configuration** — Invoke relevant Azure specialists via `#runSubagent`:
   - Network exposure (public endpoints, NSG rules, private endpoints)
   - Identity (managed identities vs shared keys, RBAC scope)
   - Encryption (at rest, in transit, customer-managed keys if required)
   - Logging (diagnostic settings, audit trails, retention)

5. **Architecture** — Invoke `system-architect` via `#runSubagent` to review:
   - Trust boundaries (where does the system trust external input?)
   - Authentication flow (token lifecycle, session management)
   - Authorization model (RBAC, ABAC — is least privilege enforced?)
   - Data classification (PII handling, encryption requirements)

6. **Security Report** — Deliver:
   - Findings table: severity, category, location, description, remediation
   - Executive summary with overall risk posture
   - Critical/high findings requiring immediate action
   - Compliance gap analysis (against specified standards)
   - Remediation backlog with effort estimates
