# Terraform Stack Roots

This directory is the target layout for changed-only provisioning.

## Planned roots

- `services/<service>/`: APIM service-edge resources for one backend service (Phase 1)
- `runtime/<service>/`: Container App and service RBAC for one backend service (Phase 2)
- `frontend/`: optional frontend infrastructure resources (SWA settings/domain/auth)

## Ownership rules

- One stack root maps to one remote state key.
- A resource must belong to exactly one stack to avoid split ownership.
- Production applies run only from GitHub Actions workflows.
