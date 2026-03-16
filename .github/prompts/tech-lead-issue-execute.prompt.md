---
title: "Tech Lead: Execute Issue"
description: "Pick up a GitHub issue and drive it to completion — analyze requirements, decompose into tasks, delegate to specialists, verify, and close."
mode: "TechLeadOrchestrator"
input: "Paste the GitHub issue URL, number, or full description. Include any additional context such as related PRs, blockers, or stakeholder constraints."
---

Drive a GitHub issue from open to closed:

1. **Issue Analysis** — Parse the issue and restate:
   - Business need: why does this matter? Who is affected?
   - Acceptance criteria: extract or define a clear checklist
   - Scope boundary: what is explicitly in and out of scope
   - Priority and severity: infer from labels, description, or ask

2. **Codebase Reconnaissance** — Invoke `Explore` via `#runSubagent` to:
   - Identify the files, modules, and services affected
   - Map dependencies and potential blast radius
   - Surface existing tests and related code

3. **Task Decomposition** — Break the issue into atomic, agent-assignable sub-tasks:
   - Each sub-task has: clear scope, input/output, acceptance criteria, assigned agent
   - Identify dependencies between sub-tasks and sequence them
   - Estimate complexity (trivial / small / medium / large)

4. **Architecture Check** — If the issue crosses service boundaries or changes data flow, invoke `system-architect` via `#runSubagent` to:
   - Validate the approach against established patterns
   - Identify integration contracts that need updating
   - Flag any ADR that should be created or amended

5. **Implementation** — Delegate each sub-task to the appropriate specialist via `#runSubagent`:
   - `python-specialist` — Python implementation, tests, type checking
   - `rust-specialist` — Rust implementation, ownership correctness, cargo tests
   - `typescript-specialist` — TypeScript/React implementation, type safety, Vitest
   - `ui-agent` — UI components, accessibility, responsive design
   - `platform-quality` — CI/CD changes, infrastructure, dependency updates
   - `enterprise-connectors` — External API integrations, connector changes

6. **Verification** — After implementation:
   - Confirm all acceptance criteria are met
   - Run tests and verify no regressions
   - Invoke `pr-evaluator` via `#runSubagent` for merge-readiness review

7. **Closure** — Summarize what was done:
   - Changes made (files, modules, tests)
   - Decisions taken and rationale
   - Any follow-up items or deferred scope

Deliver a completion report linking the issue to the changes, with verification evidence.
