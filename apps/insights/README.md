# Tutor Insights Backend

This service generates supervisor briefing reports scoped to assigned schools.

## Objective

- Generate weekly and on-demand narrative briefings
- Persist reports and supervisor feedback
- Enforce supervisor/admin role and school-scoped access
- Support pilot-only flow controls for supervisor/school allowlists
- Expose per-report feedback and pilot metrics summaries

## Indicator Collection

- Indicator collectors use a Strategy pattern with a Fabric read-only adapter contract.
- The default adapter is deterministic and network-free for local and test environments.
- Real Fabric-backed adapters can be introduced later by implementing the same adapter contract.

## Pilot Flow Controls

Set these environment variables to enforce pilot restrictions:

- `INSIGHTS_PILOT_ENABLED=true|false`
- `INSIGHTS_PILOT_SCHOOL_IDS=school-a,school-b`
- `INSIGHTS_PILOT_SUPERVISOR_IDS=supervisor-1,supervisor-2`

When enabled, callers must be allowlisted supervisors and requests are constrained to allowlisted schools.

## API Additions

- `GET /reports/{report_id}/feedback`: returns feedback rows for a specific report
- `GET /pilot/metrics?school_id=...`: returns basic pilot reporting metrics

## Infrastructure Requirements

- Python 3.13+
- FastAPI
- Cosmos DB (Azure)
- Falls back to in-memory storage when Cosmos configuration is absent in a dev environment

## Running Locally

1. Install dependencies:

```pwsh
uv pip install --python .venv -e .[dev]
```

2. Start the API:

```pwsh
uvicorn app.main:app --reload
```

## Deploying to Azure

- Deploy as a container app using the `azd` + Terraform infrastructure
