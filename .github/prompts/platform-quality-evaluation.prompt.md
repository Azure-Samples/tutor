---
title: "Platform: Quality Evaluation"
description: "Comprehensive platform quality audit delegating to specialist agents for best practices, architecture, and compliance checks."
mode: "TechLeadOrchestrator"
input: "Specify the project or repository to evaluate. Optionally narrow scope to specific areas (CI/CD, dependencies, architecture, code quality)."
---

Conduct a full platform quality evaluation by delegating to specialist agents:

1. **CI/CD & Infrastructure** — Invoke `platform-quality` via `#runSubagent` to audit:
   - Pipeline reliability (test masking, error handling, timeout configuration)
   - Security posture (secrets management, SAST integration, least-privilege tokens)
   - Dependency hygiene (vulnerability scan, version currency, license compliance)
   - Environment promotion strategy and deployment safety

2. **Architecture Compliance** — Invoke `system-architect` via `#runSubagent` to evaluate:
   - ADR adherence (are documented decisions being followed?)
   - Dependency direction (domain layer has no infra imports?)
   - Integration patterns (event contracts versioned? circuit breakers present?)
   - Component boundaries (single responsibility, no god services)

3. **Code Quality by Language** — Invoke the appropriate specialist per language stack:
   - `python-specialist` — Type coverage, async correctness, test quality, PEP compliance
   - `rust-specialist` — Unsafe audit, error handling patterns, clippy compliance, cargo audit
   - `typescript-specialist` — Strict mode compliance, ESLint zero-warnings, React patterns, bundle analysis

4. **Accessibility & UI** — Invoke `ui-agent` via `#runSubagent` to audit:
   - WCAG 2.2 AA compliance across UI surfaces
   - Semantic HTML structure and keyboard navigation
   - Core Web Vitals performance (LCP, INP, CLS)

5. **Consolidation** — Aggregate findings into a quality scorecard:
   - Category scores (pass/partial/fail) with evidence
   - Prioritized remediation backlog (critical → low)
   - Comparison with previous evaluation if available

Deliver a quality report with per-category scores, top 10 remediation items, and trend indicators.
