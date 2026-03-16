---
title: "Tech Lead: Plan Feature"
description: "Decompose a feature request into sequenced, agent-assignable tasks with acceptance criteria and risk assessment."
mode: "TechLeadOrchestrator"
input: "Describe the feature or initiative. Include business context, scope boundaries, and any known constraints."
---

Plan the requested feature:

1. **Business Context** — Restate the requirement. Connect to user outcome or business metric.
2. **Architecture Assessment** — Delegate to `system-architect` via `#runSubagent` to evaluate system impact, affected components, and integration points.
3. **Task Decomposition** — Break into atomic, testable sub-tasks. Each must be completable by a single specialist agent.
4. **Agent Assignment** — Map each sub-task to the appropriate specialist agent. Use these exact agent names for delegation via `#runSubagent`:
   - `python-specialist` — Python implementation
   - `rust-specialist` — Rust implementation
   - `typescript-specialist` — TypeScript/React implementation
   - `ui-agent` — UI/UX design and accessibility
   - `platform-quality` — CI/CD, IaC, and cross-cutting infrastructure
   - `system-architect` — Architecture decisions, ADRs, pattern validation
   - `pr-evaluator` — Final PR review before merge
5. **Dependency Graph** — Sequence tasks. Identify which can run in parallel vs which block others.
6. **Risk Assessment** — Document risks (breaking changes, security, performance, scope creep) with mitigations.
7. **Acceptance Criteria** — Define "done" for each sub-task and for the feature as a whole.

Deliver a plan as a structured table with task ID, title, agent name, dependencies, acceptance criteria, and risk level. Then execute the plan by invoking each agent via `#runSubagent` in dependency order.
