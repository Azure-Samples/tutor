---
title: "Codebase Onboarding"
description: "Fast repository orientation: understand architecture, entry points, conventions, and how to run/test/deploy."
mode: "TechLeadOrchestrator"
input: "Optionally specify focus areas (backend, frontend, infra, a specific service). Otherwise, the full repo is scanned."
---

Coordinate a multi-agent codebase onboarding scan:

1. **Architecture Overview** — Invoke `system-architect` via `#runSubagent` to map:
   - High-level architecture (services, databases, external dependencies)
   - Communication patterns (sync HTTP, async events, shared DB)
   - Entry points (API endpoints, CLI commands, event handlers, scheduled jobs)
   - Architecture decisions (look for ADRs, design docs, or infer from structure)
   - Generate a Mermaid architecture diagram

2. **Technology Stack** — Invoke the relevant language specialist(s) via `#runSubagent`:
   - `python-specialist` — Python version, framework (FastAPI/Django/Flask), package manager, key libraries
   - `rust-specialist` — Rust edition, workspace structure, key crates, build targets
   - `typescript-specialist` — Node/Deno/Bun runtime, framework (Next.js/Express/Remix), bundler, key packages

3. **Infrastructure & DevOps** — Invoke `platform-quality` via `#runSubagent` to document:
   - How to run locally (setup steps, env vars, prerequisites)
   - How to run tests (commands, fixtures, test databases)
   - How to deploy (CI/CD pipeline, manual steps, environments)
   - IaC overview (Bicep/Terraform/CDK — what manages what)

4. **UI Layer** — If applicable, invoke `ui-agent` via `#runSubagent` to assess:
   - Component structure and design system
   - Styling approach (Tailwind, CSS modules, styled-components)
   - Accessibility baseline (initial WCAG read)

5. **Code Conventions** — Scan for:
   - Linter/formatter configuration (ESLint, Prettier, black, rustfmt, clippy)
   - Naming conventions (files, variables, functions, types)
   - Git workflow (branching strategy, commit conventions, PR process)
   - Documentation patterns (inline comments, README quality, API docs)

6. **Onboarding Guide** — Deliver:
   - One-page architecture summary with diagram
   - "How to..." quick reference (run, test, deploy, add a feature)
   - Key files and directories to know
   - Common gotchas and pitfalls
   - Suggested first tasks for new contributors
