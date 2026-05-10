# ADR-006: Pedagogical Content, OCR, and RAG

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-05-10 |
| **Deciders** | Platform Team |
| **Consolidates** | OCR ingestion, approved pedagogical content, AI Search grounding, and ENEM-aligned assessment direction |

---

## Context

Tutor needs to support handwritten/scanned essays, official pedagogical materials, grounded tutoring, discursive question evaluation, and ENEM-aligned essay feedback. These capabilities require document extraction, approved-content governance, retrieval over curated materials, and configurable pedagogical rules.

A dedicated `content-svc` is a future service boundary. Current approved-content behavior is split across configuration, assessment, interaction, Blob Storage, AI Search, and shared governance contracts.

## Decision

Use Azure AI Document Intelligence for OCR and Azure AI Search for retrieval over approved pedagogical material.

Current and target responsibilities:

- `essays` handles OCR-capable essay ingestion and evaluation workflow.
- `configuration` owns pedagogical rules, feature flags, and current approved-content metadata where needed.
- `chat`, `essays`, and `questions` may retrieve approved context from AI Search for grounded outputs.
- Blob Storage stores source documents and evidence files.
- A future `content-svc` may own upload, approval, extraction, chunking, indexing, versioning, and lifecycle when that boundary needs independent operation.
- ENEM-aligned essay strategy remains a pedagogical strategy inside the assessment domain, governed by evaluation and human review policies.

Grounded generation rules:

- Only approved materials can ground tutoring, assessment, or advising outputs.
- Source ids, prompt/workflow version, model metadata, and evaluation evidence must be captured for high-impact outputs.
- Fallback or degraded extraction must be explicit and cannot silently become authoritative scoring.

## Consequences

### Positive

- Handwritten and scanned submissions become usable in AI-assisted workflows.
- RAG reduces unsupported responses by grounding outputs in approved materials.
- Pedagogical teams can manage rules and rollout through configuration rather than code changes.
- The future content service can be split without changing the whole assessment architecture.

### Negative

- Document Intelligence, AI Search, Blob Storage, and model usage add cost.
- Content quality and approval workflow become operational responsibilities.
- Ingestion latency can delay content availability for grounding.

### Guardrails

- Treat `content-svc` as future until it is actually deployed.
- Do not allow unapproved material to ground high-impact education outputs.
- Keep OCR, RAG, and ENEM behavior under evaluation and review gates.

## References

- [Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [Azure AI Search vector search](https://learn.microsoft.com/azure/search/vector-search-overview)
- [Retrieval Augmented Generation on Azure](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
