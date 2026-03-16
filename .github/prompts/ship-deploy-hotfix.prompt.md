---
title: "Ship: Deploy and Hotfix"
description: "End-to-end deployment workflow: issue → branch → PR → merge → deploy → monitor → hotfix. Delegates to all relevant specialists."
mode: "TechLeadOrchestrator"
input: "Describe the change to ship. Include the triggering issue/PR number if it exists, or describe the change so an issue can be created."
---

Execute the full deployment lifecycle for the described change. This prompt is agent-independent — it handles changes originating from any domain (UI, backend, infrastructure, dependencies).

## Phase 1: Issue & Branch

1. **Issue** — If no issue exists, create one with `[Deploy] <summary>` title, acceptance criteria checklist, and appropriate labels.
2. **Branch** — Create a feature branch from the default branch named `fix/<issue-number>-<slug>` or `feat/<issue-number>-<slug>`.
3. **Scope Lock** — Document exactly what files and modules are affected. Nothing outside this scope ships in this cycle.

## Phase 2: Implementation & Validation

Delegate implementation and validation to the appropriate specialist agents via `#runSubagent` based on what changed:

| Change Type | Agent | Validation |
|---|---|---|
| Python code | `python-specialist` | Type check (mypy), tests (pytest), lint |
| Rust code | `rust-specialist` | cargo check, cargo clippy, cargo test |
| TypeScript/React | `typescript-specialist` | tsc --noEmit, ESLint, Vitest |
| UI/accessibility | `ui-agent` | WCAG 2.2 AA audit, visual regression |
| CI/CD / infra | `platform-quality` | actionlint, dry-run deploy, IaC validate |
| Architecture impact | `system-architect` | ADR compliance, integration contract review |
| Azure resources | Relevant Azure specialist | Resource validation, config drift check |

Run **all** applicable validations — most changes touch multiple domains.

## Phase 3: Pull Request

1. **Create PR** — Invoke `pr-evaluator` via `#runSubagent` to:
   - Open the PR referencing the issue (`Closes #<number>`)
   - Verify all CI checks pass
   - Confirm test coverage is non-negative
   - Validate no security regressions (OWASP Top 10)
   - Obtain architecture sign-off from `system-architect` if the change crosses service boundaries
2. **Review Gate** — PR must have:
   - [ ] All checks green
   - [ ] No unresolved review comments
   - [ ] Acceptance criteria from the issue satisfied

## Phase 4: Merge & Deploy

1. **Merge** — Squash-merge into the default branch. Ensure commit message references the issue.
2. **Deploy** — Invoke `platform-quality` via `#runSubagent` to:
   - Trigger the deployment pipeline
   - Monitor deployment progress (build → staging → production)
   - Verify health checks pass post-deploy

## Phase 5: Monitor & Hotfix

After deployment, actively monitor for regressions:

1. **Health Check** — Invoke `platform-quality` to verify:
   - Application health endpoints return 200
   - No new errors in logs (compare error rate before/after)
   - Performance metrics within baseline (latency, throughput)
   - CI/CD pipeline status remains green

2. **Hotfix Protocol** — If any issue is detected post-deploy:
   - **Severity Assessment** — Classify as P1 (user-facing outage), P2 (degraded), P3 (cosmetic), P4 (minor)
   - **P1/P2: Immediate hotfix** —
     - Create a `hotfix/<issue>-<slug>` branch from the default branch
     - Invoke the responsible specialist agent to implement the fix
     - Fast-track PR: `pr-evaluator` reviews with expedited checklist (tests pass + no regression)
     - Merge and redeploy immediately
   - **P3/P4: Deferred fix** —
     - Create a new issue with `[Hotfix]` prefix
     - Link to the originating deploy issue
     - Schedule for next regular cycle

3. **Post-Mortem** — For P1/P2 hotfixes, document:
   - Root cause and causal chain
   - Why existing tests didn't catch it
   - Prevention measures (new tests, monitoring, validation steps)
   - Delegate prevention implementation to `platform-quality`

## Completion Criteria

- [ ] Issue exists and is linked to PR
- [ ] All specialist validations pass
- [ ] PR merged to default branch
- [ ] Deployment successful with health checks passing
- [ ] No P1/P2 regressions within monitoring window
- [ ] Any hotfixes completed and documented
