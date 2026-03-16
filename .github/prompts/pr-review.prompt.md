---
title: "PR: Review Pull Request"
description: "Review a pull request for architecture compliance, test coverage, security, and merge readiness."
mode: "pr-evaluator"
input: "Provide the PR number or let the agent detect the active PR. Optionally specify focus areas."
---

Review the pull request for merge readiness:

1. **Architecture Compliance** — Changes align with established ADRs and patterns. No unauthorized architectural shifts.
2. **Test Coverage** — New code has tests. Existing tests not weakened. Coverage delta is non-negative.
3. **Security** — No new vulnerabilities (OWASP Top 10). Secrets not committed. Input validation at boundaries.
4. **Breaking Changes** — API changes are backward-compatible or properly versioned. Migration path documented if needed.
5. **CI Status** — All checks pass. No test masking. Lint warnings addressed.
6. **Documentation** — README, API docs, or changelog updated if user-facing behavior changes.
7. **Code Quality** — No code smells introduced. Consistent style. Clear naming.

Deliver a review summary with approve/request-changes verdict, blocking issues, and optional improvements.
