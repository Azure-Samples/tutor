---
title: "Tech Debt Assessment"
description: "Inventory technical debt across the codebase, score by business impact, and create a prioritized remediation backlog."
mode: "TechLeadOrchestrator"
input: "Specify scope: entire repo or specific areas. Optionally include known pain points or recent incidents caused by tech debt."
---

Coordinate a systematic tech debt inventory:

1. **Code-Level Debt** — Invoke language specialists via `#runSubagent` to scan for:
   - `python-specialist` — Missing type hints, bare except blocks, deprecated APIs, TODO/FIXME/HACK comments, untested code paths
   - `rust-specialist` — Clippy warnings suppressed, unwrap() in non-test code, outdated edition, unsafe without justification
   - `typescript-specialist` — `any` type usage, disabled ESLint rules, legacy class components, untyped APIs, outdated dependencies

2. **Architecture Debt** — Invoke `system-architect` via `#runSubagent` to identify:
   - Circular dependencies between modules/services
   - God classes/modules with too many responsibilities
   - Missing abstraction layers (business logic in controllers, SQL in handlers)
   - Stale ADRs that no longer reflect reality
   - Integration contracts that have drifted from specification

3. **Infrastructure Debt** — Invoke `platform-quality` via `#runSubagent` to catalog:
   - Manual deployment steps that should be automated
   - Missing or flaky tests in CI/CD pipeline
   - Outdated base images, deprecated GitHub Actions, legacy IaC patterns
   - Monitoring gaps (services without health checks, missing alerts)
   - Documentation that's out of date with actual behavior

4. **UI Debt** — If applicable, invoke `ui-agent` via `#runSubagent` to identify:
   - Accessibility violations accumulated over time
   - Inconsistent component patterns (multiple button styles, duplicated layouts)
   - Performance regressions (large bundles, layout shifts, slow interactions)

5. **Business Impact Scoring** — For each debt item, evaluate:
   - **Frequency**: How often does this cause friction? (daily/weekly/monthly/rarely)
   - **Severity**: What happens when it bites? (outage/bug/slowdown/annoyance)
   - **Blast radius**: How much of the system is affected?
   - **Remediation cost**: Effort to fix (hours/days/weeks)
   - **Score**: (Frequency × Severity × Blast Radius) / Remediation Cost

6. **Remediation Backlog** — Deliver:
   - Debt inventory table with category, location, description, and business impact score
   - Top 10 items ranked by score (highest ROI fixes first)
   - Quick wins (< 1 day effort, high impact) highlighted separately
   - Estimated total remediation effort (in engineering days)
   - Recommended cadence for debt reduction (e.g., 20% of each sprint)
