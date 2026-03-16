---
title: "Tech Lead: Issue Correction"
description: "Map identified problems into GitHub issues and delegate each to the appropriate specialist agent for resolution."
mode: "TechLeadOrchestrator"
input: "Describe the problems found: error logs, failing tests, user reports, or code smells. Include affected files or modules if known."
---

Analyze the reported problems and create a structured remediation plan:

1. **Problem Inventory** — Catalog each distinct problem. Classify by type: bug, regression, tech debt, security vulnerability, performance degradation.
2. **Impact Assessment** — For each problem, assess user impact (critical/high/medium/low) and blast radius (single file, module, cross-service).
3. **Issue Creation** — Create a GitHub issue for each problem with:
   - Clear title following `[P{1-4}] <component>: <summary>` convention
   - Reproduction steps or evidence (logs, stack traces, test output)
   - Acceptance criteria as a checklist
   - Labels for priority, component, and issue type
4. **Agent Assignment** — Assign each issue to the appropriate specialist agent via `#runSubagent`:
   - `python-specialist` — Python bugs, type errors, async issues, test failures
   - `rust-specialist` — Rust panics, ownership bugs, linker issues, unsafe violations
   - `typescript-specialist` — TypeScript errors, React rendering bugs, bundle failures
   - `ui-agent` — Accessibility violations, layout regressions, responsive breakage
   - `platform-quality` — CI/CD failures, dependency vulnerabilities, infra misconfigurations
   - `system-architect` — Integration contract violations, architectural drift
5. **Dependency Sequencing** — Order issue resolution by dependency graph. Identify which fixes unblock others.
6. **Execution** — Invoke each specialist via `#runSubagent` with the issue brief. Track completion against the issue checklist.

Deliver a table mapping each issue number to its agent, priority, dependencies, and status.
