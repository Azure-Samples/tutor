---
title: "Tech Lead: Innovation Research"
description: "Research innovative solutions by coordinating business strategy agents for opportunity framing and technical agents for feasibility analysis."
mode: "TechLeadOrchestrator"
input: "Describe the problem space or opportunity to explore. Include business constraints, current limitations, and desired outcomes."
---

Coordinate a multi-agent innovation research cycle:

1. **Opportunity Framing** — Invoke business agents via `#runSubagent` to define the innovation space:
   - `business-strategy-agent` — Market positioning, competitive landscape, strategic fit
   - `competitive-intelligence-agent` — What competitors and adjacent industries are doing differently
   - `financial-modeling-agent` — Cost-benefit modeling, ROI projections for candidate solutions
   - `risk-analysis-agent` — Risk assessment for each candidate (technical, market, regulatory)

2. **State of the Art** — Invoke `Explore` via `#runSubagent` to survey:
   - Recent academic papers (arXiv, ACM, IEEE) for novel approaches in the problem space
   - Community adoption trends, emerging frameworks, open-source momentum
   - Comparable implementations in open-source projects

3. **Technical Feasibility** — Invoke engineering agents via `#runSubagent` to evaluate:
   - `system-architect` — Architectural fit, integration complexity, migration path from current state
   - `python-specialist` / `rust-specialist` / `typescript-specialist` — Prototype feasibility, language ecosystem maturity, library availability
   - `platform-quality` — Infrastructure requirements, deployment complexity, operational burden

4. **Synthesis** — Combine business and technical findings into a decision matrix:
   - Score each candidate on: business value, technical feasibility, time-to-value, operational cost, risk
   - Recommend top 1-2 candidates with implementation roadmap
   - Identify proof-of-concept scope for validation

5. **Proof of Concept** — If approved, delegate PoC implementation to the appropriate specialist agents with a time-boxed scope.

Deliver an innovation brief with opportunity analysis, candidate comparison matrix, recommended approach, and PoC plan.
