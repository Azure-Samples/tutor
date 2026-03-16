---
applyTo: '**'
description: Delegation bootstrap that binds agent handoffs to team mapping and available workspace agents.
---
# Delegation Bootstrap

## Ownership Metadata

- Ownership class: `Derived-Generated` (see `.github/ownership-taxonomy.md`)
- Canonical source metadata: `.github/agents/data/team-mapping.md` generated from shared-agent families enabled in `repos/asset-map.yaml`
- Generated mirror role: this instruction file is a generated delegation mirror for compatibility with instruction loaders

Before delegating to any agent:

1. Read `.github/agents/data/team-mapping.md` as the canonical agent registry.
2. Restrict delegation to agents whose `.agent.md` files exist under `.github/agents/`.
3. If a mapped agent is not available in `.github/agents/`, fall back to the current agent and continue with available tools.
4. Do not invent agent names that are absent from team mapping or unavailable in the workspace.

## Managed File Update Policy

For these delegation-managed files:
- `.github/copilot-instructions.md`
- `.github/instructions/team-mapping.instructions.md`
- `.github/agents/data/team-mapping.md`

Apply the following rules:
1. Do not perform automatic corrections, auto-refactors, or opportunistic rewrites.
2. Keep changes minimal and scoped only to the intended synchronization/update.
3. Any update must go through a dedicated PR named `agent-update`.
4. The `agent-update` PR must always target the repository default branch (`main`).

## Temporary Artifact Policy

For all agent-generated temporary files:
1. Use only the repository-local `.tmp/` folder as the temporary workspace.
2. Delete temporary files from `.tmp/` after all related PRs are completed.
3. Never commit or version files from `.tmp/`.

## Language Policy

For all agent-authored content:
1. UI text, UX copy, documentation, prompts, and operational notes must be written in en-US.
2. Avoid mixing locales in the same artifact; keep wording consistently en-US.

## Shared Agents Enabled By Control Plane

The following shared agent files are currently enabled for export by `repos/asset-map.yaml`:

- `azure-aks.agent.md`
- `azure-apim.agent.md`
- `azure-blob.agent.md`
- `azure-container-apps.agent.md`
- `azure-cosmos.agent.md`
- `azure-foundry.agent.md`
- `azure-postgres.agent.md`
- `azure-redis.agent.md`
- `azure-swa.agent.md`
- `business-strategy-agent.agent.md`
- `cataldi-librarian.agent.md`
- `code-guidelines-agent.agent.md`
- `competitive-intelligence-agent.agent.md`
- `enterprise-connectors.agent.md`
- `financial-modeling-agent.agent.md`
- `platform-quality.agent.md`
- `pr-evaluator.agent.md`
- `process-management-agent.agent.md`
- `python-specialist.agent.md`
- `report-generator.agent.md`
- `risk-analysis-agent.agent.md`
- `rust-specialist.agent.md`
- `system-architect.agent.md`
- `tech-manager.agent.md`
- `typescript-specialist.agent.md`
- `ui-agent.agent.md`
