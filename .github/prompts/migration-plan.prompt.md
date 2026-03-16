---
title: "Migration Plan"
description: "Plan a framework upgrade, major dependency bump, language version migration, or service migration with risk assessment and staged rollout."
mode: "TechLeadOrchestrator"
input: "Describe the migration: source version/framework → target version/framework. Include the reason for migrating and any deadline."
---

Coordinate a multi-agent migration plan:

1. **Impact Analysis** — Invoke `system-architect` via `#runSubagent` to assess:
   - Which components are affected by the migration
   - Breaking changes between source and target (changelog review)
   - Integration points that may need contract updates
   - Dependency graph: what else must upgrade as a consequence

2. **Code Migration** — Invoke the relevant language specialist(s) via `#runSubagent`:
   - `python-specialist` — Python version bumps, framework migrations (Django 4→5, FastAPI major), async runtime changes
   - `rust-specialist` — Rust edition upgrades, major crate bumps, MSRV changes, cargo workspace restructures
   - `typescript-specialist` — Node.js LTS upgrades, React major versions, Next.js pages→app router, bundler migrations
   - For each: identify deprecated APIs, removed features, new required patterns, and codemods if available

3. **Infrastructure Migration** — Invoke `platform-quality` via `#runSubagent` to plan:
   - CI/CD pipeline changes (new tool versions, updated actions, changed test commands)
   - IaC updates (new provider versions, resource API changes)
   - Container base image updates (new runtime version)
   - Environment variable or configuration format changes

4. **UI Migration** — If applicable, invoke `ui-agent` via `#runSubagent`:
   - Component library upgrade (breaking style changes, removed components)
   - CSS framework migration (Tailwind v3→v4, CSS-in-JS → Tailwind)
   - Accessibility regression check after visual changes

5. **Risk Assessment** — Invoke `risk-analysis-agent` via `#runSubagent`:
   - Categorize risks: data loss, downtime, behavioral change, performance regression
   - Identify rollback strategy for each migration stage
   - Flag migration steps that are irreversible

6. **Staged Migration Plan** — Deliver:
   - **Stage 1: Prepare** — Update tooling, CI, and dev environment. Run tests on target version.
   - **Stage 2: Coexistence** — If possible, support both versions temporarily (feature flags, compatibility shims)
   - **Stage 3: Migrate** — Apply code changes module by module. Run full test suite after each module.
   - **Stage 4: Validate** — Performance benchmarks, accessibility check, integration tests, manual smoke test
   - **Stage 5: Cleanup** — Remove compatibility shims, deprecated code paths, and old config
   - Rollback trigger criteria and procedure for each stage
   - Estimated timeline per stage
