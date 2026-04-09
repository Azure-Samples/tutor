# Standalone lifelong-learning UX IA and low-fidelity wireframes

## Purpose

This document translates the standalone lifelong-learning strategy into an implementation-facing UX information architecture for the frontend. It is intentionally grounded in the current repo baseline and approved backlog, not a full speculative product rewrite.

Primary source inputs:

- [Standalone lifelong-learning innovation brief](./standalone-lifelong-learning-innovation-brief.md)
- [Standalone lifelong-learning issue backlog](./standalone-lifelong-learning-issue-backlog.md)
- [Standalone lifelong-learning risk assessment](./standalone-lifelong-learning-risk-assessment.md)
- [Architecture](./architecture.md)
- [Service domains](./service-domains.md)
- [ADR-007 Frontend modernization](./adr/007-frontend-modernization.md)

## Current-state grounding

The current repo already exposes the functional building blocks that the standalone IA should reorganize into role-first workspaces:

- Student and professor learning flows already exist through essays, questions, chat, and avatar services.
- Professor planning and analysis already exists through upskilling.
- Supervisor intelligence already exists through insights.
- Admin and governance flows already exist in configuration, evaluation, and LMS gateway surfaces.
- Shared authentication support exists in the backend, but frontend identity and relationship-aware scoping are not complete yet.

That means the UX should reorganize existing capabilities into durable workspaces before inventing broad new feature surfaces.

## Design constraints

| Constraint | UX consequence |
| --- | --- |
| Deterministic system of record owns identity, learner record, pathway state, credential state, permissions, and audit. | Every workspace home starts with deterministic summaries first. Agentic output appears as a layer on top, never as the only source of truth. |
| LL-03 and LL-18 require provenance and degraded-mode clarity. | Every high-impact agent card shows source status, provenance access, and a visible degraded label when orchestration falls back or fails. |
| LL-02 is not complete yet. | The first rollout needs a mocked persona and context selector for pilots, with a clean swap to relationship-aware auth later. |
| LL-16 is a curated continuing-education pilot, not a full marketplace. | The public front door should expose a curated programs view, not a broad commerce catalog. |
| LL-04 and LL-05 favor role-first composition and shared primitives. | Navigation is organized by role and durable jobs-to-be-done, not by backend service names or configuration menus. |

## Experience model

The platform is organized into three layers:

1. Public front door
2. Shared workspace shell
3. Role-aware workspaces

### 1. Public front door

The public surface should explain the platform, show curated program or re-entry options, and let a user enter the correct workspace without exposing backend feature launchers.

Recommended public IA:

- `/` - landing page and value proposition
- `/programs` - curated programs and re-entry offers, limited pilot scope
- `/programs/[programSlug]` - program detail and evidence of outcomes
- `/evidence-trust` - deterministic record model, provenance, degraded states, and AI boundary explanation
- `/institutions` - institution-facing pitch, pilot flow, and integration posture
- `/sign-in` - phase 0 mocked persona entry, later replaced by relationship-aware auth

Public top navigation:

- Tutor home
- Programs
- Evidence and Trust
- For Institutions
- Help
- Sign in

### 2. Shared workspace shell

All authenticated experiences should use one shell contract.

Shared top bar slots:

- Tutor mark and workspace home link
- Role switcher
- Context switcher
- Global search
- Notifications
- Help and trust
- Profile menu

Shared shell rules:

- Role switcher changes workspace, not just nav labels.
- Context switcher changes scope within a workspace such as institution, school, program, course, cohort, or term.
- Search scope is role-aware and deterministic first. Agentic summarization can refine results, but raw results remain accessible.
- Help and trust opens guidance on provenance, evaluation status, degraded states, and human-review boundaries.
- A secondary utility rail is allowed on desktop for Today, alerts, and trust state. On smaller screens it collapses below the main content.

### 3. Role-aware workspaces

Recommended route structure:

```text
frontend/app
  (public)/
    page.tsx                               -> /
    programs/page.tsx                      -> /programs
    programs/[programSlug]/page.tsx        -> /programs/[programSlug]
    evidence-trust/page.tsx                -> /evidence-trust
    institutions/page.tsx                  -> /institutions
    sign-in/page.tsx                       -> /sign-in
  (workspace)/
    workspace/layout.tsx                   -> shared authenticated shell
    workspace/student/page.tsx             -> /workspace/student
    workspace/student/learning/page.tsx    -> /workspace/student/learning
    workspace/student/assignments/page.tsx -> /workspace/student/assignments
    workspace/student/progress/page.tsx    -> /workspace/student/progress
    workspace/student/record/page.tsx      -> /workspace/student/record
    workspace/student/portfolio/page.tsx   -> /workspace/student/portfolio
    workspace/student/credentials/page.tsx -> /workspace/student/credentials
    workspace/professor/page.tsx                  -> /workspace/professor
    workspace/professor/classes/page.tsx          -> /workspace/professor/classes
    workspace/professor/review/page.tsx           -> /workspace/professor/review
    workspace/professor/content/page.tsx          -> /workspace/professor/content
    workspace/professor/cohort-progress/page.tsx  -> /workspace/professor/cohort-progress
    workspace/professor/interventions/page.tsx    -> /workspace/professor/interventions
    workspace/professor/teaching-plans/page.tsx   -> /workspace/professor/teaching-plans
    workspace/principal/page.tsx                  -> /workspace/principal
    workspace/principal/school-health/page.tsx    -> /workspace/principal/school-health
    workspace/principal/programs/page.tsx         -> /workspace/principal/programs
    workspace/principal/interventions/page.tsx    -> /workspace/principal/interventions
    workspace/principal/staff-development/page.tsx-> /workspace/principal/staff-development
    workspace/supervisor/page.tsx                 -> /workspace/supervisor
    workspace/supervisor/schools/page.tsx         -> /workspace/supervisor/schools
    workspace/supervisor/briefings/page.tsx       -> /workspace/supervisor/briefings
    workspace/supervisor/visits/page.tsx          -> /workspace/supervisor/visits
    workspace/supervisor/trends/page.tsx          -> /workspace/supervisor/trends
    workspace/supervisor/alerts/page.tsx          -> /workspace/supervisor/alerts
    workspace/admin/page.tsx                      -> /workspace/admin
    workspace/admin/programs/page.tsx             -> /workspace/admin/programs
    workspace/admin/users/page.tsx                -> /workspace/admin/users
    workspace/admin/integrations/page.tsx         -> /workspace/admin/integrations
    workspace/admin/policies/page.tsx             -> /workspace/admin/policies
    workspace/admin/audit/page.tsx                -> /workspace/admin/audit
    workspace/admin/ai-governance/page.tsx        -> /workspace/admin/ai-governance
    workspace/alumni/page.tsx                     -> /workspace/alumni
    workspace/alumni/record/page.tsx              -> /workspace/alumni/record
    workspace/alumni/credentials/page.tsx         -> /workspace/alumni/credentials
    workspace/alumni/pathways/page.tsx            -> /workspace/alumni/pathways
    workspace/alumni/career/page.tsx              -> /workspace/alumni/career
    workspace/alumni/mentoring/page.tsx           -> /workspace/alumni/mentoring
    workspace/alumni/re-engage/page.tsx           -> /workspace/alumni/re-engage
```

Implementation note:

- Principal and supervisor should keep separate IA because their jobs-to-be-done differ.
- If engineering needs one initial leader code path, both can share shell components and nav configuration while still keeping separate route groups.

## Role navigation and context switching

### Student workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/student` |
| Left rail | Today, Learning, Assignments, Progress, Record, Portfolio, Credentials |
| Top-nav emphasis | Search assignments, resources, and learner-record entries; show notifications and trust status; allow role switch only if the user also has another valid relationship such as alumni. |
| Context switching | Program, cohort, and term. Student does not switch into another learner record. If the user also has alumni access, that is a role switch, not a context switch. |
| Home composition | Next actions, due work, progress snapshot, recent evidence, credential progress, and an optional coach panel with provenance. |

### Professor workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/professor` |
| Left rail | Home, Classes, Review, Content, Cohort Progress, Interventions, Teaching Plans |
| Top-nav emphasis | Search classes, learners, rubrics, and teaching plans; surface review queue count; expose trust state for grading and intervention recommendations. |
| Context switching | Institution, program, course section, and term. Preserve the current section when moving between Home, Review, and Cohort Progress. |
| Home composition | Review queue, class health snapshot, at-risk learner list, teaching-plan status, and rubric-grounded feedback summaries. |

### Principal workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/principal` |
| Left rail | Home, School Health, Programs, Interventions, Staff Development |
| Top-nav emphasis | Search school programs, intervention cases, and staff development assets; keep briefing provenance visible because summaries are high-impact. |
| Context switching | School year, program, and reporting period. School is typically fixed by role relationship. |
| Home composition | School health summary, intervention watchlist, program performance, staff-development prompts, and narrative briefings grounded in deterministic indicators. |

### Supervisor workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/supervisor` |
| Left rail | Home, Schools, Briefings, Visits, Trends, Alerts |
| Top-nav emphasis | Search schools, briefings, alerts, and visit plans; keep trust and provenance entry points prominent. |
| Context switching | Region or network, school, reporting period, and visit cycle. When switching schools, preserve the current section if the target route is valid. |
| Home composition | Network summary, school comparison, visit prep, alert queue, and narrative briefings layered over deterministic read models. |

### Admin workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/admin` |
| Left rail | Home, Programs, Users, Integrations, Policies, Audit, AI Governance |
| Top-nav emphasis | Search users, programs, integrations, policies, evaluations, and audit events. Notifications focus on failures, fallbacks, and policy exceptions. |
| Context switching | Tenant, institution, environment, and module scope. Any switch that changes privilege boundary requires explicit confirmation. |
| Home composition | Operational status, pending admin actions, integration health, evaluation pass status, audit highlights, and degraded-state incident counts. |

### Alumni workspace

| Element | Decision |
| --- | --- |
| Home route | `/workspace/alumni` |
| Left rail | Home, Record, Credentials, Pathways, Career, Mentoring, Re-engage |
| Top-nav emphasis | Search credentials, evidence, pathways, mentors, and re-entry options. Keep portfolio sharing and privacy controls accessible from the profile area. |
| Context switching | Affiliation history, credential set, and active re-entry pathway. Alumni does not change into another learner identity. |
| Home composition | Credential wallet, record summary, re-entry recommendations, mentoring opportunities, and curated continuing-learning offers. |

## Shared UX primitives

These are platform primitives and should not be redesigned per page.

| Primitive | First appearance | Deterministic base | Agentic layer |
| --- | --- | --- | --- |
| Today rail | Student home and professor home | Upcoming work, due dates, events, queue counts | Next-best-action suggestions with provenance |
| Context switcher | Shared workspace shell | Relationship and scope data | None; this remains deterministic |
| Work queue | Professor Review and Admin Home | Essay, question, evaluation, and integration queues | Optional summaries or prioritization hints |
| Mastery map | Student Progress and Professor Cohort Progress | Competency and evidence projections | Gap explanation only, never hidden scoring logic |
| Rubric feedback panel | Student assignment detail and Professor Review | Rubric version, scores, comments, source references | Draft feedback suggestions and wording refinement |
| Narrative briefing card | Principal Home and Supervisor Home | Read-model indicators, trend deltas, thresholds | Narrative synthesis with provenance and evaluation status |
| Pathway card | Student Home and Alumni Pathways | Program milestones, eligibility, deterministic progress | Recommended next step and rationale |
| Evidence timeline | Student Record and Alumni Record | Append-oriented learner-record events | Optional narrative summary of evidence clusters |
| Credential wallet | Student Credentials and Alumni Credentials | Credential definitions, awards, revocations | Gap explanation and portfolio draft assistance |
| Recommendation shelf | Student Home, Principal Home, and Alumni Home | Rule-based relevance and eligibility | Advisory ranking with visible confidence |
| Provenance drawer | Any agent-assisted card | Event ids, source ids, model or workflow version, evaluation state | None; this is the transparency surface itself |
| Degraded-state banner | Essays, Questions, Briefings, Evaluations | Service health and fallback status | None; this suppresses misleading AI authority |

## Current-route migration guidance

The repo should migrate away from the current feature-launcher home page toward the role-first shell below.

| Current route | Target route | Notes |
| --- | --- | --- |
| `/avatar` and `/avatar/[id]` | `/workspace/student/learning` | Avatar remains a student learning surface. Session detail can live under the learning section rather than as a top-level product. |
| `/chat` | `/workspace/student/learning` | Chat becomes contextual guidance inside learning and assignment detail, not a standalone chatbot destination. |
| `/essays` and `/essays/[id]` | `/workspace/student/assignments` and `/workspace/professor/review` | Student submission and professor review become mirrored role views over the same capability. |
| `/questions` and `/questions/[id]` | `/workspace/student/assignments` and `/workspace/professor/review` | Same split as essays. Keep assessment provenance and degraded states visible. |
| `/upskilling` | `/workspace/professor/teaching-plans` | Rename around professor work rather than internal service vocabulary. |
| `/evaluation` | `/workspace/admin/ai-governance` | Move agent evaluation into governance rather than a public launcher. |
| `/lms-gateway` | `/workspace/admin/integrations` | Keep LMS sync as admin-only operational tooling. |
| `/configuration` | `/workspace/admin` | General configuration becomes operations and governance IA. |
| `/configuration/questions/*` | `/workspace/admin/programs` or `/workspace/admin/ai-governance` | Place grader and answer configuration under explicit admin jobs. |
| `/configuration/supervisor/*` | `/workspace/supervisor/schools` or `/workspace/admin/users` | School-scoped operational views stay in leader or admin space, not a global config bucket. |

## Phased rollout notes

| Phase | UX behavior |
| --- | --- |
| Phase 0: before LL-02 relationship-aware auth | `/sign-in` opens a mocked persona and seeded context selector for demo and pilot use. Role switcher values come from fixtures or allowlists. UI labels this as mocked context. |
| Phase 1: LL-02 plus LL-04 | Shared shell, role switcher, and deterministic context resolution go live for student, professor, principal, supervisor, and admin workspaces. |
| Phase 2: LL-06, LL-13, LL-14, LL-17 | Learner record, pathways, evidence, advising, credentials, and institutional read models become first-class deterministic panels with agentic sidecars. |
| Phase 3: LL-12 and LL-16 | Alumni workspace, curated re-entry flows, and public programs pilot expand the public front door. |

## Low-fidelity wireframes

### Public landing page

```text
+----------------------------------------------------------------------------------+
| Tutor | Programs | Evidence and Trust | For Institutions | Help | Sign in       |
+----------------------------------------------------------------------------------+
| Hero: Institution-owned lifelong learning platform                               |
| [Enter pilot workspace] [Explore programs] [See evidence and trust]              |
+-----------------------------------+----------------------------------------------+
| Role previews                     | Why trust this platform                      |
| Student | Professor | Leader      | Deterministic learner record                |
| Admin | Alumni                    | Provenance visible on AI outputs            |
|                                   | Degraded states never hidden                |
+-----------------------------------+----------------------------------------------+
| Curated programs and re-entry offers                                             |
| [Program card] [Program card] [Alumni re-entry card]                             |
+----------------------------------------------------------------------------------+
| Proof points: assessment, tutoring, learner record, leadership intelligence      |
+----------------------------------------------------------------------------------+
```

### Student workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Student | Context: Program > Cohort > Term | Search | Alerts | Me |
+----------------------+-----------------------------------------------------------+
| Today                | TODAY                                                     |
| Learning             | [Next action] [Upcoming deadlines] [Coach draft]          |
| Assignments          | [Pathway progress] [Recent feedback]                      |
| Progress             | [Evidence timeline excerpt] [Credential progress]         |
| Record               |                                                           |
| Portfolio            | Utility: status synced | provenance | help                |
| Credentials          | Degraded: essay feedback delayed -> review queued         |
+----------------------+-----------------------------------------------------------+
```

### Professor workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Professor | Context: Course section > Term | Search | Queue | Me  |
+----------------------+-----------------------------------------------------------+
| Home                 | HOME                                                      |
| Classes              | [Review queue] [Class health] [At-risk learners]          |
| Review               | [Rubric consistency] [Pending essays] [Pending questions] |
| Content              | [Teaching-plan status] [Recent content updates]           |
| Cohort Progress      |                                                           |
| Interventions        | Utility: trust state | evaluation status | help           |
| Teaching Plans       | Draft recommendation always requires human confirmation   |
+----------------------+-----------------------------------------------------------+
```

### Principal workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Principal | Context: School year > Program | Search | Alerts | Me |
+----------------------+-----------------------------------------------------------+
| Home                 | HOME                                                      |
| School Health        | [School health summary] [Attendance/risk surface]        |
| Programs             | [Program performance] [Intervention watchlist]           |
| Interventions        | [Narrative briefing] [Staff-development prompts]         |
| Staff Development    |                                                           |
|                      | Utility: deterministic indicators first                  |
|                      | Provenance drawer for every narrative card               |
+----------------------+-----------------------------------------------------------+
```

### Supervisor workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Supervisor | Context: Region > School > Period | Search | Me      |
+----------------------+-----------------------------------------------------------+
| Home                 | HOME                                                      |
| Schools              | [Network summary] [School comparison]                    |
| Briefings            | [Visit prep] [Narrative briefing cards]                  |
| Visits               | [Open alerts] [Planned visits]                           |
| Trends               |                                                           |
| Alerts               | Utility: provenance | evaluation status | fallback flags |
|                      | Degraded briefings suppress risk labels                  |
+----------------------+-----------------------------------------------------------+
```

### Admin workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Admin | Context: Tenant > Institution > Env | Search | Alerts | Me|
+----------------------+-----------------------------------------------------------+
| Home                 | HOME                                                      |
| Programs             | [Provisioning queue] [Integration health]                |
| Users                | [Policy exceptions] [Pending approvals]                  |
| Integrations         | [Evaluation pass status] [Recent audit events]           |
| Policies             |                                                           |
| Audit                | Utility: service health | degraded incidents | help      |
| AI Governance        | High-impact automation stays advisory only               |
+----------------------+-----------------------------------------------------------+
```

### Alumni workspace home

```text
+----------------------------------------------------------------------------------+
| Tutor | Role: Alumni | Context: Affiliation > Active pathway | Search | Me      |
+----------------------+-----------------------------------------------------------+
| Home                 | HOME                                                      |
| Record               | [Credential wallet] [Record summary]                     |
| Credentials          | [Re-entry recommendations] [Mentoring opportunities]     |
| Pathways             | [Curated continuing-learning offers]                     |
| Career               |                                                           |
| Mentoring            | Utility: sharing settings | provenance | privacy         |
| Re-engage            | Public catalog remains curated, not marketplace-wide      |
+----------------------+-----------------------------------------------------------+
```

## Responsive and mobile behavior

- Desktop keeps the left rail persistent and allows an optional utility rail for Today, alerts, and trust.
- Tablet collapses the utility rail below the main column and keeps the left rail as an icon-plus-label drawer.
- Mobile replaces the persistent left rail with a bottom navigation for the top three to five role actions plus a More sheet.
- Role switcher and context switcher become stacked controls inside a top-sheet or bottom-sheet on smaller screens.
- Large tables such as review queues, alert lists, audit logs, and comparisons must reflow to stacked cards or list rows before horizontal scrolling is required.
- Provenance, trust, and degraded-state details open in full-width drawers on mobile.
- Program cards, evidence cards, and briefing cards should stack into one column first, then expand into multiple columns as space allows.

## Accessibility notes

- Preserve the current skip-link pattern already present in the app shell.
- Use landmark structure consistently with `header`, labeled `nav`, `main`, and supporting `aside` regions.
- Keep repeated navigation in a stable order across workspaces.
- Ensure role switcher, context switcher, drawers, and tables are fully keyboard-operable and never trap focus.
- Surface degraded states, warnings, provenance, and evaluation status as text and iconography, not color alone.
- Use visible focus indicators and keep focused controls unobscured by sticky bars or drawers.
- Treat status changes such as queued review, degraded output, sync completion, and evaluation completion as assistive-technology-readable status messages.
- Do not let agent-generated recommendations silently change context, scores, placement, or intervention state.
- For any future authentication flow, avoid cognitive-only challenges and preserve work on re-authentication where possible.

## Build-oriented summary

The implementation sequence should be:

1. Replace the current feature-launcher home with a public front door and a shared `/workspace/*` shell.
2. Move existing feature routes behind student, professor, supervisor or principal, and admin workspaces.
3. Add provenance and degraded-state primitives before expanding AI-driven summaries.
4. Introduce learner record, credentials, and alumni flows only when deterministic record surfaces exist.
5. Keep the public programs surface curated until identity, entitlement, and commerce rules are ready.
