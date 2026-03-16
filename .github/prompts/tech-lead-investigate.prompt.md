---
title: "Tech Lead: Investigate Issue"
description: "Investigate a bug or production issue by coordinating diagnostic agents across the stack."
mode: "TechLeadOrchestrator"
input: "Describe the issue: symptoms, reproduction steps, affected users/systems, and any error messages or logs."
---

Investigate the reported issue:

1. **Symptom Analysis** — Restate the problem. Identify affected components and user impact severity.
2. **Hypothesis Formation** — List the 3 most likely root causes ranked by probability.
3. **Evidence Gathering** — For each hypothesis, invoke the appropriate specialist agent via `#runSubagent` to gather evidence:
   - `python-specialist` — for Python stack traces, async bugs, type errors
   - `rust-specialist` — for Rust panics, ownership issues, linker failures
   - `typescript-specialist` — for TypeScript type errors, React rendering, bundle issues
   - `platform-quality` — for CI/CD failures, infrastructure, dependency problems
   - `system-architect` — for cross-service integration failures, architectural mismatches
4. **Root Cause Isolation** — Narrow to the confirmed cause. Document the causal chain.
5. **Fix Planning** — Decompose the fix into agent-assignable tasks. Invoke each specialist via `#runSubagent` to implement their portion.
6. **Prevention** — Delegate to `platform-quality` to recommend test/monitoring additions to prevent recurrence.

Deliver an investigation report with root cause, fix plan, and prevention recommendations.
