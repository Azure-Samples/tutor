# ADR-010: Pedagogical Content Ingestion, OCR & RAG

| Metadata | Value |
|----------|-------|
| **Status** | Proposed |
| **Date** | 2025-01 |
| **Decision Makers** | Architecture Team |
| **Business Needs** | BN-PED-1, BN-PED-2, BN-PED-3, BN-PED-5 |

---

## Context

The **Pedagogical agenda** defines requirements for:

1. **BN-PED-1**: AI-based essay and discursive question correction with OCR for handwritten submissions and ENEM-aligned rubrics
2. **BN-PED-2**: Curated pedagogical material ingestion so AI responses are grounded in official department content
3. **BN-PED-3**: A virtual tutor that assists students during writing, grounded in pedagogical materials
4. **BN-PED-5**: Configurable pedagogical rules (topics, rubrics, triggers, guardrails)

The current architecture lacks:
- OCR capability for handwritten/scanned documents
- A content ingestion pipeline for pedagogical materials
- RAG (Retrieval-Augmented Generation) grounding for AI responses
- ENEM-specific evaluation strategies

---

## Decision

### Add Azure AI Document Intelligence for OCR

All handwritten essay scanning and pedagogical material text extraction use **Azure AI Document Intelligence** (prebuilt-read model):

- **Handwritten essays** → students photograph/scan handwritten essays → Document Intelligence extracts text → essays-svc evaluates the extracted text
- **Pedagogical materials** → administrators upload PDFs, images, DOCX → content-svc extracts text via Document Intelligence → text is chunked and indexed

### Add Azure AI Search for RAG

A **vector + keyword hybrid search** index in Azure AI Search stores chunked pedagogical material:

- **Embedding model**: Azure OpenAI `text-embedding-3-large` (1536 dimensions)
- **Index schema**: `content`, `content_vector`, `subject`, `grade`, `source_id`, `chunk_id`
- **Hybrid retrieval**: Both vector similarity and keyword BM25 are used, with RRF fusion

RAG is consumed by:
- **essays-svc** — retrieves rubric-relevant context before evaluating essays
- **questions-svc** — retrieves reference material for discursive question grading
- **chat-svc** — grounds guided tutoring responses in curated content

### Add `content-svc` to Platform Domain

A new service (`content-svc`, port 8089) manages the content ingestion pipeline:

```
Upload → Azure Blob Storage → Document Intelligence (OCR) → Chunking → Azure OpenAI (embedding) → AI Search (index)
```

| Aspect | Detail |
|--------|--------|
| **Port** | 8089 |
| **Data owned** | `platform_db`: materials_metadata |
| **Depends on** | Blob Storage, Document Intelligence, Azure OpenAI, AI Search |
| **Called by** | Frontend (admin/professor upload UI) |

### Add ENEM Strategy to essays-svc

A new `ENEMStrategy` evaluates essays against ENEM Competencies I–V:

| Competency | Assessment |
|------------|------------|
| I | Formal written Portuguese adherence |
| II | Theme comprehension and text type adherence |
| III | Information organization and argumentation |
| IV | Linguistic cohesion mechanisms |
| V | Intervention proposal respecting human rights |

The strategy is selected via `essay_configs.strategy = "enem"` and produces per-competency scores (0–200) plus a composite score (0–1000).

### Add configurable pedagogical rules to config-svc

New Cosmos containers in `platform_db`:
- `pedagogical_rules` (PK: tenantId, subject) — topics, rubrics, triggers, guardrails, conversation limits
- `feature_flags` (PK: tenantId) — pilot scoping by grade, subject, school

These rules are consumed by:
- **chat-svc** — enforces guardrails (topic boundaries, language, no-direct-answers)
- **essays-svc** — selects evaluation strategy based on rules
- **questions-svc** — determines which question types are enabled

---

## Consequences

### Positive

- AI responses are grounded in official pedagogical content, reducing hallucination
- Handwritten essay support enables paper-based classrooms to benefit from AI evaluation
- ENEM alignment makes the platform directly useful for Brazil's national examination preparation
- Configurable rules give professors and administrators control over AI behavior
- Feature flags enable controlled pilot rollout (BN-PED-6: 3rd-year physics)

### Negative

- Two new Azure services (Document Intelligence + AI Search) increase infrastructure cost
- Content ingestion pipeline adds latency between upload and availability in RAG
- ENEM strategy requires careful prompt engineering and ongoing rubric validation

### Cost Considerations

| Service | Estimated Monthly Cost (dev) | Notes |
|---------|------------------------------|-------|
| AI Document Intelligence | ~$50 | S0 tier, ~1000 pages/month |
| AI Search | ~$75 | Basic tier, 1 replica |
| Blob Storage | ~$5 | Hot tier, <10 GB |

---

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Use Azure OpenAI vision (GPT-4o) for OCR | Higher token cost per page; less reliable for structured extraction |
| Use Elasticsearch for RAG | Not Azure-native; no AVM support; additional operational burden |
| Store materials in Cosmos DB | Not optimized for vector search; no hybrid retrieval |
| Skip OCR — require typed essays only | Excludes schools with limited digital infrastructure |

---

## Related Documents

| Document | Link |
|----------|------|
| Business Alignment | [business-alignment.md](../business-alignment.md) |
| Architecture (Content + Essay flows) | [architecture.md](../architecture.md) |
| Service Domains (Platform, Assessment) | [service-domains.md](../service-domains.md) |
| Modernization Plan (Phase 9) | [modernization-plan.md](../modernization-plan.md) |
| Agent Evaluation (ENEM evaluators) | [agent-evaluation.md](../agent-evaluation.md) |
