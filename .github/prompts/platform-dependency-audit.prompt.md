---
title: "Platform: Dependency Audit"
description: "Audit project dependencies for vulnerabilities, currency, and license compliance."
mode: "platform-quality"
input: "Specify the project or lockfile to audit (package.json, Cargo.toml, pyproject.toml, etc.)."
---

Audit dependencies for the specified project:

1. **Vulnerability Scan** — Run the appropriate audit tool (npm audit, cargo audit, pip-audit). Report all findings by severity.
2. **Version Currency** — Identify dependencies more than 2 major versions behind. Flag abandoned packages (no release in 12+ months).
3. **License Compliance** — Check for GPL/AGPL in proprietary projects. Flag unknown or custom licenses. Ensure SPDX identifiers present.
4. **Duplicate Dependencies** — Identify multiple versions of the same package in the dependency tree.
5. **Size Impact** — For frontend projects, flag dependencies >100KB that could be replaced with smaller alternatives.
6. **Upgrade Path** — For critical vulnerabilities, provide the minimum version bump required and assess breaking change risk.

Deliver a report with severity-ranked findings and an upgrade plan.
