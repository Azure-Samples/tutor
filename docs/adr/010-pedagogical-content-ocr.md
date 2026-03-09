# ADR-010: Pedagogical Content Ingestion, OCR & RAG

| Metadata | Value |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-02 |
| **Decision Makers** | Architecture Team |
| **Business Needs** | BN-PED-1, BN-PED-2, BN-PED-3, BN-PED-5 |
| **Tracking** | [Issue #18](https://github.com/Azure-Samples/tutor/issues/18), [Issue #19](https://github.com/Azure-Samples/tutor/issues/19) |

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

## Implementation Scope

This ADR is implemented in **two sequential phases** to reduce risk and deliver incremental value.

### Phase A — OCR Ingestion in essays-svc (Issue #18, branch `feat/ocr-essay-ingestion`)

**Goal**: Replace the current `pypdf` + PIL client-side extraction in `file_processing.py` with Azure AI Document Intelligence for reliable handwritten and scanned essay extraction. Everything stays within the existing `essays-svc` boundary — no new services.

**In scope:**
- Add `azure-ai-documentintelligence` SDK to `apps/essays/pyproject.toml`
- Add `DocumentIntelligenceConfig` settings group to `apps/essays/src/app/config.py`
- Implement `extract_text_with_doc_intelligence(payload, content_type)` in `file_processing.py`
- Route PDFs and images through Document Intelligence (prebuilt-read model) when the DI endpoint is configured; fall back to `pypdf`/PIL when running locally without credentials
- Update `process_pdf()` and `process_image()` to call the new extractor via the `ProcessedUpload.extracted_text` field
- Unit tests with mock responses against the DI client

**Out of scope for this phase:** content-svc, AI Search, RAG grounding, ENEM strategy, chunking/embedding.

### Phase B — Content Service, RAG & ENEM Strategy (Issue #19 + future issues, Modernization Plan P9-01 → P9-07)

**Goal**: Build the full content ingestion pipeline (`content-svc`), wire RAG into assessment and interaction services, and implement the ENEM evaluation strategy.

**In scope:**
- `apps/content/` — new content-svc (port 8089)
- Azure AI Search index: hybrid vector + keyword, `text-embedding-3-large`
- RAG context retrieval in essays-svc, questions-svc, chat-svc
- `ENEMStrategy` in essays-svc (Competencies I–V, scores 0–1000)
- Pedagogical rules + feature flags CRUD in config-svc (P9-07)
- Content management UI page in frontend (P9-06)
- Terraform modules: `docintel.bicep` → `infra/terraform/modules/docintel.tf`, `search.bicep` → `infra/terraform/modules/search.tf`

---

## Decision

### Add Azure AI Document Intelligence for OCR

All handwritten essay scanning and pedagogical material text extraction use **Azure AI Document Intelligence** (prebuilt-read model):

- **Handwritten essays** → students photograph/scan handwritten essays → Document Intelligence extracts text → essays-svc evaluates the extracted text
- **Pedagogical materials** → administrators upload PDFs, images, DOCX → content-svc extracts text via Document Intelligence → text is chunked and indexed

**Phase A integration point (essays-svc)**: The `process_upload()` function in `file_processing.py` is the single entry point for all file ingestion. Document Intelligence wraps the call before the result reaches the evaluation agent. Environment variable `DOCUMENT_INTELLIGENCE_ENDPOINT` gates whether DI or the local fallback (`pypdf`/PIL) is used — enabling both cloud and local development without service mocking.

```
                  process_upload()
                       │
          ┌────────────┴────────────────┐
          │ DOCUMENT_INTELLIGENCE_ENDPOINT set?        │
         YES                                     NO
          │                                       │
          ▼                                       ▼
  DI prebuilt-read                     pypdf (PDF) / PIL (image)
  → extracted_text                     → extracted_text / encoded_content
```

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
- **Phase A delivers immediate value** (handwritten essay OCR) with a single SDK addition and no new infrastructure beyond reusing the existing Document Intelligence resource

### Negative

- Two new Azure services (Document Intelligence + AI Search) increase infrastructure cost
- Content ingestion pipeline adds latency between upload and availability in RAG
- ENEM strategy requires careful prompt engineering and ongoing rubric validation
- Phase A fallback logic (DI vs. pypdf) adds a conditional path that must be covered in tests

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
