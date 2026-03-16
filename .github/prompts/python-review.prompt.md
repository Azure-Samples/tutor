---
title: "Python: Review Code"
description: "Review Python code for type safety, async correctness, security, and adherence to PEP standards."
mode: "python-specialist"
input: "Provide the file(s) or module to review. Optionally specify focus areas (security, performance, correctness)."
---

Review the specified Python code checking for:

1. **Type Completeness** — All public functions have full signatures. No bare `Any` without justification.
2. **Async Correctness** — No blocking calls inside async functions. Proper TaskGroup/gather usage. No fire-and-forget tasks.
3. **Security** — OWASP Top 10 compliance. Parameterized queries. No secrets in code. Pydantic validation at boundaries.
4. **Error Handling** — Specific exception types. No bare `except:`. Proper cleanup in finally blocks.
5. **Code Smells** — Long methods, feature envy, shotgun surgery. Flag refactoring candidates with technique recommendations.
6. **Test Quality** — Coverage of edge cases. Proper mocking boundaries. No testing implementation details.

Provide findings as a prioritized list with file locations, severity (critical/warning/info), and fix recommendations.
