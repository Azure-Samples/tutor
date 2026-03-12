# PR Reviewer Checklist

Use this checklist to review changes related to service compatibility, frontend coverage, and release safety.

## 1. API Compatibility

- [ ] Confirm no unintended route/path changes in questions, essays, configuration, avatar APIs.
- [ ] Verify not-found paths still return `404` where expected (no accidental `500` regression).
- [ ] Validate request/response payloads used by frontend pages still match backend schemas.

## 2. Frontend Capability Coverage

- [ ] Verify configuration routes include questions admin capabilities:
  - [ ] `/configuration/questions/graders`
  - [ ] `/configuration/questions/answers`
- [ ] Confirm create/update/delete flows for graders and answers are functional.
- [ ] Confirm no regressions on existing pages (chat, essays, avatar, questions, configuration).

## 3. Reliability & Resilience

- [ ] Confirm shared retry policies only retry transient faults (timeouts, 429, 5xx).
- [ ] Confirm non-transient failures are not wrapped in a way that breaks API status mapping.
- [ ] Confirm assembly lookup path uses shared repository abstraction consistently.

## 4. Configuration & Environment

- [ ] Verify required env vars are documented and consistent with runtime code.
- [ ] Confirm avatar speech flow documents `SPEECH_RESOURCE_ID` and `SPEECH_REGION`.
- [ ] Confirm frontend APIM base URL requirements remain unchanged.

## 5. CI/CD Safety

- [ ] Validate workflow variable wiring in deploy/guardrails jobs.
- [ ] Ensure no duplicate env keys or missing required outputs in workflows.
- [ ] Confirm no production deployment path bypasses GitHub workflows.

## 6. Quality Gates

- [ ] Backend focused tests pass.
- [ ] Frontend TypeScript check passes (`tsc --noEmit`).
- [ ] New/changed docs are updated (`CHANGELOG.md`, local development notes, frontend docs).

## 7. Merge Readiness

- [ ] Diff is scoped and grouped (compatibility, frontend pages, quality/ops).
- [ ] High-risk files (workflows, shared libraries) have explicit reviewer sign-off.
- [ ] Post-merge verification plan is defined (health checks + quick UI smoke).
