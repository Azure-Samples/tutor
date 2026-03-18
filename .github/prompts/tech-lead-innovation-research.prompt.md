---
title: "Tech Lead: Innovation Research"
description: "Research innovative solutions by coordinating business strategy agents for opportunity framing and technical agents for feasibility analysis."
mode: "TechLeadOrchestrator"
input: "Describe the problem space or opportunity to explore. Include business constraints, current limitations, and desired outcomes."
---

Coordinate a multi-agent innovation research cycle:

**Delegation compatibility**: If the workspace has `.github/agents/data/team-mapping.md`, resolve exact agent names from it before calling `#runSubagent`. Otherwise, use the canonical agent names in this prompt and fall back to current-agent execution if a specialist is unavailable.

1. **Opportunity Framing** — Invoke business agents via `#runSubagent` to define the innovation space:
   - `BusinessStrategist` — Market positioning, competitive landscape, strategic fit
   - `CompetitiveIntelAnalyst` — What competitors and adjacent industries are doing differently
   - `FinancialModeler` — Cost-benefit modeling, ROI projections for candidate solutions
   - `RiskAnalyst` — Risk assessment for each candidate (technical, market, regulatory)

2. **State of the Art** — Use the available research, workspace, and web tools directly to survey:
   - Recent academic papers (arXiv, ACM, IEEE) for novel approaches in the problem space
   - Community adoption trends, emerging frameworks, open-source momentum
   - Comparable implementations in open-source projects

3. **Technical Feasibility** — Invoke engineering agents via `#runSubagent` to evaluate:
   - `SystemArchitect` — Architectural fit, integration complexity, migration path from current state
   - `PythonDeveloper` / `RustDeveloper` / `TypeScriptDeveloper` — Prototype feasibility, language ecosystem maturity, library availability
   - `PlatformEngineer` — Infrastructure requirements, deployment complexity, operational burden

4. **Synthesis** — Combine business and technical findings into a decision matrix:
   - Score each candidate on: business value, technical feasibility, time-to-value, operational cost, risk
   - Recommend top 1-2 candidates with implementation roadmap
   - Identify proof-of-concept scope for validation

5. **Proof of Concept** — If approved, delegate PoC implementation to the appropriate specialist agents with a time-boxed scope.

Deliver an innovation brief with opportunity analysis, candidate comparison matrix, recommended approach, and PoC plan.
