## Tutor Platform Changelog

<a name="1.0.0"></a>
# 1.0.0 (2025-03-09)

*Features*
* **OCR Phase A** — Document Intelligence SDK integration in essays service (`file_processing.py`), with `pypdf`/PIL fallback for local development (ADR-010)
* **Essay PATCH endpoint** — `PATCH /essays/{essay_id}` for partial updates using `EssayPatch` model with `exclude_unset=True`
* **Upskilling stateful transformation** — full CRUD plan management with Cosmos DB persistence (`upskilling_plans` container, PK `/professor_id`), multi-agent evaluation, repository pattern (`InMemoryUpskillingRepository`, `CosmosUpskillingRepository`)
* **Configuration UIs** — admin pages for Agents, Upskilling, Evaluation, and LMS Gateway under `/configuration`
* **Avatar speech auth** — `DefaultAzureCredential` for Azure Speech in avatar service
* **Demo seed script** — `scripts/seed_demo_data.py` provisions 90 items across all services with essay↔assembly linkage via PATCH
* **APIM alignment** — all frontend traffic routed through APIM; backend endpoints normalized across chat, questions, essays, avatar, configuration
* **Showcase navigation** — homepage and sidebar include upskilling, evaluation, and lms-gateway pages
* **Theme management** — configuration service exposes `GET/POST/PUT/DELETE /themes`

*Bug Fixes*
* **Essay assembly linkage** — `update_essay` PUT no longer destructively overwrites `assembly_id` with `None`; incoming payload filtered for non-None values before merge
* **Seed script re-link** — `link_essays_to_assemblies()` step uses PATCH to bind essays to assemblies after initial seeding
* **Test stub drift** — fixed 4 pre-existing test failures in `test_essays_orchestrator.py` (stubs updated for `fallback_essay_id`, `attachments`, `essay_id`)
* **Frontend SWA deployment** — GitHub Actions workflow fixed for Oryx managed build

*Infrastructure*
* Terraform variables for upskilling Cosmos container provisioning and RBAC
* `azure.yaml` updated with upskilling service definition
* Terraform outputs for `NEXT_PUBLIC_APIM_BASE_URL` and `APIM_BASE_URL`

*Breaking Changes*
* None
