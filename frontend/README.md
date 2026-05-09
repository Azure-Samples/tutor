# Tutor Frontend (Next.js)

This is the frontend for The Tutor platform, built with [Next.js](https://nextjs.org/). It provides a modern, interactive web interface for students and educators to access all features of the Tutor system.

## Objective

The frontend enables:

- Student and teacher login (if enabled)
- Access to all learning modules: Avatar, Chat, Essays, Questions, and Configuration
- Real-time and asynchronous AI-powered feedback
- Submission and review of essays and questions
- Visualization of evaluation history and progress

## Main Functionalities

- **Avatar:** Practice conversations with an AI avatar, including speech synthesis and real-time feedback.
- **Chat:** Ask questions and discuss topics with the AI.
- **Essays:** Submit essays for detailed, multi-agent evaluation.
- **Questions:** Answer objective questions and receive instant, multi-part feedback.
- **Configuration:** Personalize your learning environment and manage settings, including question administration pages for graders and answers.

## Questions Administration Pages

The configuration area now includes dedicated routes for question-evaluation entities:

- `/configuration/questions/graders` — Manage grader definitions (`agent_id`, `dimension`, `deployment`)
- `/configuration/questions/answers` — Manage answer records used in question evaluation flows

## Route-to-Capability Map

The frontend keeps a data-oriented route registry in `utils/routeMetadata.ts`. Status values are
`implemented`, `adapter`, `blocked`, and `planned`.

| Route group | Routes | Capability | Status |
| --- | --- | --- | --- |
| Public | `/`, `/avatar`, `/chat`, `/essays`, `/questions`, `/upskilling`, `/lms-gateway`, `/evaluation`, `/evaluation/[runId]`, `/evidence-trust`, `/institutions`, `/programs` | Pilot entry points, learning tools, governance/evaluation, and positioning pages | Implemented |
| Workspace | `/workspace/[role]`, `/workspace/student/learning`, `/workspace/student/assignments`, `/workspace/professor/review`, `/workspace/professor/teaching-plans`, `/workspace/principal/school-health`, `/workspace/supervisor/briefings`, `/workspace/admin/ai-governance`, `/workspace/alumni/record` | Role-aware workspace shells over current capabilities | Implemented |
| Configuration | `/configuration`, `/configuration/cases`, `/configuration/themes`, `/configuration/questions`, `/configuration/questions/answers`, `/configuration/questions/graders`, `/configuration/agents`, `/configuration/supervisor`, `/configuration/lms-gateway`, `/configuration/upskilling` | Administrative utilities and content/policy setup | Implemented |
| Adapter | `/configuration/evaluation` | Advanced evaluation utility preserved for compatibility while `/evaluation` is the mature dashboard | Adapter |
| Blocked | `/avatar/settings` | Avatar preference and tenant/user settings | Blocked until backend contract exists |
| Planned | `/workspace/admin/audit` | Audit and policy evidence review | Planned |

## Evaluation Routes

- `/evaluation` loads datasets with `GET /api/evaluation/datasets`, creates datasets with `POST /api/evaluation/datasets`, and starts runs with `POST /api/evaluation/evaluation/run`.
- `/evaluation/[runId]` loads one run with `GET /api/evaluation/evaluation/run/{run_id}`.
- All evaluation calls use the existing `evaluationApi` APIM facade from `utils/api.ts`; do not add direct service URLs or bypass APIM.
- `/configuration/evaluation` remains available as an adapter/advanced utility page.

## E2E Tests

Playwright covers the APIM-only evaluation path and a small set of representative modern route
shells without requiring live backend services.

```pwsh
pnpm e2e:list
pnpm e2e
```

- `pnpm e2e:list` validates Playwright configuration and test collection without launching a browser.
- `pnpm e2e` starts Next locally through `playwright.config.ts` on `http://127.0.0.1:3100` and sets `NEXT_PUBLIC_APIM_BASE_URL` to that same local origin.
- Existing dev servers are not reused by default. Set `PLAYWRIGHT_REUSE_SERVER=1` for local debugging only when the running server was started with the same E2E environment.
- Evaluation tests mock only the APIM evaluation endpoints under `/api/evaluation/...`: dataset listing, dataset creation, run start, and run lookup.
- The mocks sit at the existing `utils/api.ts` APIM facade boundary, so tests do not add direct service URLs or service-internal calls.

## Avatar Settings Backend Contract Gap

`/avatar/settings` is intentionally blocked. The frontend must not call or document a
`/api/avatar/config` endpoint. Before the route can be implemented, the avatar backend needs an
APIM-exposed settings contract with:

- `GET /api/avatar/settings` returning effective user and tenant avatar settings.
- `PUT /api/avatar/settings` validating and persisting allowed avatar settings changes.
- Response fields for speech brokering state, default voice/avatar identifiers, tenant/user scope,
  validation errors, and safe fallback behavior.

## Infrastructure Requirements

- Node.js 22.x
- pnpm 9.x; this project pins `pnpm@9.15.4` via `packageManager`
- Access to the Tutor backend APIs (see main README)
- (For production) Azure Static Web Apps or compatible static hosting

## Running Locally

1. Install dependencies:

   ```pwsh
   pnpm install
   ```

2. Start the development server:

   ```pwsh
   pnpm dev
   ```

   The app will be available at [http://localhost:3000](http://localhost:3000).

3. Configure API endpoints:
   - Edit `.env.local` with APIM gateway URL.
   - Required key: `NEXT_PUBLIC_APIM_BASE_URL`; local development can use a local or mock URL while backend services are unavailable.
   - The frontend routes all backend traffic through APIM paths: `/api/avatar`, `/api/essays`, `/api/questions`, `/api/configuration`, `/api/upskilling`, `/api/chat`, `/api/evaluation`, `/api/lms-gateway`.
   - Avatar speech credentials are brokered by the avatar backend and do not require public speech keys in the frontend build.
   - In production, always use `https://` APIM gateway URLs.

## Deploying to Azure

- The frontend is designed to be deployed as an Azure Static Web App.
- Production deployments must go through the repository GitHub workflows, especially
   `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml`.
- Infrastructure and backend deployments are handled by `.github/workflows/azd-deploy.yml`.

For more details, see the main project README and Azure Static Web Apps documentation.
