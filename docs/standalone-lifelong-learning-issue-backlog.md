# Standalone Lifelong Learning Issue Backlog

This backlog turns the standalone-platform research into GitHub-issue-ready work items.

Notes:

- These are issue drafts, not live GitHub issues.
- The repo has a generic issue template in [.github/ISSUE_TEMPLATE.md](../.github/ISSUE_TEMPLATE.md).
- For feature requests, `Minimal steps to reproduce` and `Any log messages given by the failure` are intentionally `N/A`.

## Priority Summary

| ID | Title | Type | Priority | Primary Owner | Dependencies |
| --- | --- | --- | --- | --- | --- |
| LL-01 | Adopt learner-record-centered platform ADR | documentation issue or request | P0 | SystemArchitect | None |
| LL-02 | Build tenant and relationship-based access control plane | feature request | P0 | PlatformEngineer | LL-01 |
| LL-03 | Introduce learning event backbone and provenance model | feature request | P0 | PlatformEngineer | LL-01 |
| LL-04 | Rebuild frontend into role-aware workspace shell | feature request | P0 | TypeScriptDeveloper | LL-01, LL-02 |
| LL-05 | Create academic design system and shared UX primitives | feature request | P1 | UIDesigner | LL-04 |
| LL-06 | Ship learner record and evidence timeline MVP | feature request | P0 | PythonDeveloper | LL-02, LL-03 |
| LL-07 | Add skills and competency graph services | feature request | P1 | PythonDeveloper | LL-06 |
| LL-08 | Launch student lifelong-learning workspace | feature request | P1 | TypeScriptDeveloper | LL-04, LL-05, LL-06 |
| LL-09 | Launch professor teaching and intervention workspace | feature request | P1 | TypeScriptDeveloper | LL-04, LL-05, LL-06 |
| LL-10 | Launch principal and supervisor intelligence workspace | feature request | P1 | TypeScriptDeveloper | LL-04, LL-05, LL-06 |
| LL-11 | Launch admin operations and governance workspace | feature request | P1 | TypeScriptDeveloper | LL-04, LL-05, LL-02 |
| LL-12 | Launch alumni record, re-entry, and mentoring workspace | feature request | P1 | TypeScriptDeveloper | LL-04, LL-05, LL-06 |
| LL-13 | Build pathways and advising core plus Advising Copilot | feature request | P0 | PythonDeveloper | LL-06, LL-07 |
| LL-14 | Build credentialing, portfolio, and CLR-ready export layer | feature request | P1 | PythonDeveloper | LL-06, LL-07 |
| LL-15 | Build community and mentor network domain | feature request | P2 | PythonDeveloper | LL-06, LL-12 |
| LL-16 | Build continuing-education catalog and commerce pilot | feature request | P2 | PlatformEngineer | LL-04, LL-13, LL-14 |
| LL-17 | Expand insights into institutional analytics and intervention engine | feature request | P1 | PythonDeveloper | LL-03, LL-06 |
| LL-18 | Add educational AI governance, safety, and evaluation gates | feature request | P0 | PlatformEngineer | LL-02, LL-03 |

## Issue Drafts

## LL-01 - Adopt learner-record-centered platform ADR

- Type: documentation issue or request
- Priority: P0
- Primary owner: SystemArchitect
- Dependencies: None
- Desired behavior: The repo should explicitly reposition Tutor from LMS enhancer to standalone lifelong learning and outcomes platform with optional LMS, SIS, CRM, and credential integrations behind anti-corruption layers.
- Acceptance criteria: supersede or materially update [docs/adr/001-lms-enhancer-platform.md](./adr/001-lms-enhancer-platform.md); update [docs/architecture.md](./architecture.md) and [docs/service-domains.md](./service-domains.md) with new target-state domains; document 3 migration horizons and core system-of-record responsibilities.

## LL-02 - Build tenant and relationship-based access control plane

- Type: feature request
- Priority: P0
- Primary owner: PlatformEngineer
- Dependencies: LL-01
- Desired behavior: Tutor should support institution, school, program, course, learner, advisor, guardian, supervisor, admin, and alumni scopes through relationship-aware authorization rather than basic role checks alone.
- Acceptance criteria: add tenant registry and organization model; support relationship scope in backend authorization; remove unmanaged identity fallbacks in hosted environments; enable role-aware navigation and action guards in frontend.

## LL-03 - Introduce learning event backbone and provenance model

- Type: feature request
- Priority: P0
- Primary owner: PlatformEngineer
- Dependencies: LL-01
- Desired behavior: Tutor should emit canonical learning events and persist provenance for high-impact AI outputs so learner history, analytics, and governance workflows are trustworthy and replayable.
- Acceptance criteria: define canonical event contract for learning, assessment, coaching, advising, and credential events; capture provenance fields for model, source ids, prompt or workflow version, actor, and evaluation status; introduce event transport and durable retention strategy; create first read models for learner timeline and institutional analytics.

## LL-04 - Rebuild frontend into role-aware workspace shell

- Type: feature request
- Priority: P0
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-01, LL-02
- Desired behavior: The frontend should be organized around durable role workspaces and product domains, not backend feature launchers or configuration pages.
- Acceptance criteria: introduce public, shared, and role-specific route groups; add role switcher and context switcher; move current pages into student, professor, supervisor, admin, and alumni workspaces; keep navigation permission-aware and server-first where possible.

## LL-05 - Create academic design system and shared UX primitives

- Type: feature request
- Priority: P1
- Primary owner: UIDesigner
- Dependencies: LL-04
- Desired behavior: Tutor should present a consistent, professional academic interface with shared components for progress, evidence, feedback, and actions.
- Acceptance criteria: define color, typography, spacing, density, and status tokens; add shared components for Today rail, mastery map, rubric panel, evidence timeline, narrative briefing card, and work queue; standardize loading, empty, degraded, and error states; improve accessibility and focus affordances across the shell.

## LL-06 - Ship learner record and evidence timeline MVP

- Type: feature request
- Priority: P0
- Primary owner: PythonDeveloper
- Dependencies: LL-02, LL-03
- Desired behavior: Tutor should own a longitudinal learner record that aggregates coursework, assessment outcomes, tutoring activity, feedback, interventions, and milestones into one timeline.
- Acceptance criteria: create learner-record domain model and APIs; ingest initial data from existing services and LMS gateway; render learner record in student and professor views; preserve append-oriented history and provenance metadata.

## LL-07 - Add skills and competency graph services

- Type: feature request
- Priority: P1
- Primary owner: PythonDeveloper
- Dependencies: LL-06
- Desired behavior: Tutor should map assignments, assessments, programs, and achievements to competencies and skills that can be tracked over time.
- Acceptance criteria: define competency and skill graph model; link existing assessment outputs to competency evidence; support confidence, mastery, and evidence references; expose learner, cohort, and program skill views.

## LL-08 - Launch student lifelong-learning workspace

- Type: feature request
- Priority: P1
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-04, LL-05, LL-06
- Desired behavior: Students should land on a Today experience with clear next actions, pathway progress, tutoring entry points, feedback, and credential context.
- Acceptance criteria: add student home with next-best-action, upcoming work, and progress summary; unify essays, questions, tutoring, and pathway actions inside the workspace; expose learner record, portfolio, and credentials from the same shell.

## LL-09 - Launch professor teaching and intervention workspace

- Type: feature request
- Priority: P1
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-04, LL-05, LL-06
- Desired behavior: Professors should have one workspace for grading, feedback, cohort progress, intervention planning, and content management.
- Acceptance criteria: add review queue for essays and questions; show cohort mastery and at-risk learners; connect rubric feedback to pathway and competency outcomes; support teacher actions without exposing admin configuration complexity.

## LL-10 - Launch principal and supervisor intelligence workspace

- Type: feature request
- Priority: P1
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-04, LL-05, LL-06
- Desired behavior: Principals and supervisors should receive narrative, school- or network-scoped briefings with trend summaries, intervention cues, and visit planning support.
- Acceptance criteria: create school and network briefing dashboards; support comparisons, alerts, and intervention workflows; preserve scope isolation by school, region, and role.

## LL-11 - Launch admin operations and governance workspace

- Type: feature request
- Priority: P1
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-04, LL-05, LL-02
- Desired behavior: Admins should manage programs, users, integrations, policies, audit history, and AI evaluation from one operations workspace.
- Acceptance criteria: create admin home and navigation model; expose program, user, integration, policy, and audit modules; add AI evaluation and feature-flag visibility.

## LL-12 - Launch alumni record, re-entry, and mentoring workspace

- Type: feature request
- Priority: P1
- Primary owner: TypeScriptDeveloper
- Dependencies: LL-04, LL-05, LL-06
- Desired behavior: Alumni should retain access to their record, credentials, and portfolio, and receive re-skilling, mentoring, and continuing-education opportunities.
- Acceptance criteria: create alumni role and lifecycle state; provide alumni dashboard with credentials, record, and re-entry recommendations; support mentor participation and public-share settings where appropriate.

## LL-13 - Build pathways and advising core plus Advising Copilot

- Type: feature request
- Priority: P0
- Primary owner: PythonDeveloper
- Dependencies: LL-06, LL-07
- Desired behavior: Tutor should support deterministic pathway planning and advising case management, with agentic next-best-action support layered on top.
- Acceptance criteria: create pathway and milestone domain model; add advising cases, owners, interventions, and statuses; add Advising Copilot in advisory mode only; support human confirmation for high-impact actions.

## LL-14 - Build credentialing, portfolio, and CLR-ready export layer

- Type: feature request
- Priority: P1
- Primary owner: PythonDeveloper
- Dependencies: LL-06, LL-07
- Desired behavior: Tutor should award internal credentials with evidence, revocation, and verification support, while preparing for CLR and Open Badges compatible exports.
- Acceptance criteria: create credential definitions, eligibility rules, and award records; connect awards to evidence and portfolio artifacts; provide verification and revocation workflows; define export model for CLR and badge-aligned packaging.

## LL-15 - Build community and mentor network domain

- Type: feature request
- Priority: P2
- Primary owner: PythonDeveloper
- Dependencies: LL-06, LL-12
- Desired behavior: Tutor should support cohort communities, mentor relationships, and structured alumni engagement instead of treating the platform as a single-user utility.
- Acceptance criteria: add groups, memberships, mentor relationships, and moderation state; support community browsing and recommendations; connect community milestones to learner record and alumni re-entry.

## LL-16 - Build continuing-education catalog and commerce pilot

- Type: feature request
- Priority: P2
- Primary owner: PlatformEngineer
- Dependencies: LL-04, LL-13, LL-14
- Desired behavior: Tutor should offer a branded front door for continuing education and re-entry learning, starting with a curated pilot rather than a full marketplace.
- Acceptance criteria: add public catalog, program pages, and enrollment journey; support audience segmentation and simple entitlement logic; keep first release limited to curated offerings and pilot monetization flows.

## LL-17 - Expand insights into institutional analytics and intervention engine

- Type: feature request
- Priority: P1
- Primary owner: PythonDeveloper
- Dependencies: LL-03, LL-06
- Desired behavior: Tutor should move from point-in-time briefing generation to broader institutional analytics with intervention-ready read models.
- Acceptance criteria: define learner, cohort, school, and program projections; expose trends, risk surfaces, and intervention triggers; preserve narrative briefing capability on top of deterministic read models.

## LL-18 - Add educational AI governance, safety, and evaluation gates

- Type: feature request
- Priority: P0
- Primary owner: PlatformEngineer
- Dependencies: LL-02, LL-03
- Desired behavior: High-impact educational AI features should be governed by evaluation gates, provenance, transparency, and explicit human-review rules.
- Acceptance criteria: require provenance fields for high-impact outputs; extend evaluation coverage for assessment, advising, and credential agents; block autonomous high-impact actions without human confirmation; document degraded-mode behavior and fallbacks clearly in product and ops flows.

## Suggested Sequencing

### Wave 1

- LL-01
- LL-02
- LL-03
- LL-04
- LL-06
- LL-18

### Wave 2

- LL-05
- LL-08
- LL-09
- LL-10
- LL-11
- LL-13
- LL-17

### Wave 3

- LL-07
- LL-12
- LL-14
- LL-15
- LL-16

## Recommended Labels

- `epic`
- `platform`
- `ux`
- `frontend`
- `backend`
- `identity`
- `analytics`
- `credentials`
- `alumni`
- `risk-review`
- `ai-governance`
- `lifelong-learning`
