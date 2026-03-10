# Copilot Instructions for Tutor Platform

## Deployment Policy (MANDATORY)

All deployments to Azure **MUST** be performed via GitHub Workflows. Never suggest or execute direct `azd deploy`, `az containerapp update`, or manual Docker pushes for production environments.

**Authorized deployment paths:**

- `.github/workflows/azd-deploy.yml` — Infrastructure + 8 backend services (triggers on push to `main` or `workflow_dispatch`)
- `.github/workflows/azure-static-web-apps-polite-wave-029b18f0f.yml` — Frontend SWA (triggers on push to `main`, PR events, or `workflow_dispatch`)

When a user asks to deploy, always guide them to merge into `main` (which auto-triggers workflows) or to use `workflow_dispatch` from the GitHub Actions UI.

Local `azd provision` and `azd deploy` are permitted **only** for first-time environment bootstrap per the [deployment runbook](docs/runbooks/azd-deployment.md).
