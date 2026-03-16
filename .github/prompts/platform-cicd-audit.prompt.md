---
title: "Platform: CI/CD Audit"
description: "Audit CI/CD pipelines for reliability, security, test masking, and deployment safety."
mode: "platform-quality"
input: "Specify the pipeline file(s) or CI system (GitHub Actions, Azure Pipelines) to audit."
---

Audit the specified CI/CD pipelines:

1. **Test Masking** — Scan for `|| true`, `continue-on-error: true`, and other patterns that hide failures. Flag each with justification status.
2. **Security** — Secrets management (no hardcoded values). Dependency scanning step present. SAST integration. Minimal permissions (least-privilege tokens).
3. **Reliability** — Proper error handling in scripts. fail-fast strategy documented. Timeout configuration on long steps. Cache invalidation strategy.
4. **Deployment Safety** — Environment gates (approval required for production). Rollback strategy defined. Blue-green or canary support.
5. **Linting** — actionlint validation for GitHub Actions. No deprecated actions. Pin action versions to SHA, not tags.
6. **Coverage** — Test coverage gates present. Coverage delta comparison on PRs. Minimum threshold configured.

Deliver findings as a compliance table with pass/fail, evidence, and remediation steps.
