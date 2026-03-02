# Security

> Defense-in-depth security architecture for **The Tutor** platform, implementing zero-trust principles across all layers.

---

## 1. Threat Model

```mermaid
graph TB
    subgraph Threats
        T1["Unauthorized API access"]
        T2["Data exfiltration (PII)"]
        T3["Prompt injection"]
        T4["Token theft / replay"]
        T5["Lateral movement (VNet)"]
        T6["Supply chain attacks"]
        T7["Excessive AI resource usage"]
        T8["Unsafe agent outputs"]
    end

    subgraph Mitigations
        M1["Entra ID + JWT validation"]
        M2["RBAC + data isolation by tenant"]
        M3["Input sanitization + system prompt hardening"]
        M4["Short-lived tokens + PKCE + refresh rotation"]
        M5["NSG deny-all + private endpoints"]
        M6["Dependabot + SBOM + signed containers"]
        M7["Rate limiting + RU caps + APIM throttling"]
        M8["Content Safety evaluator + output filtering"]
    end

    T1 --> M1
    T2 --> M2
    T3 --> M3
    T4 --> M4
    T5 --> M5
    T6 --> M6
    T7 --> M7
    T8 --> M8
```

---

## 2. Security Architecture Layers

### Layer 1: Identity (Microsoft Entra ID)

| Component | Implementation |
|-----------|---------------|
| **User authentication** | OAuth 2.0 Authorization Code + PKCE via MSAL React |
| **Service authentication** | User-Assigned Managed Identity on each ACA container |
| **Token format** | JWT v2.0 with `roles`, `oid`, `tid` claims |
| **Token lifetime** | Access: 1 hour, Refresh: 24 hours, Sliding session |
| **MFA** | Required via Conditional Access policy |
| **App registration** | Single Entra ID app with app roles: `student`, `professor`, `admin`, `supervisor` |

### Runtime controls for Entra validation

| Variable | Purpose |
|----------|---------|
| `ENTRA_AUTH_ENABLED` | Enables JWT validation middleware (`true`/`false`) |
| `ENTRA_TENANT_ID` | Tenant used to resolve Entra JWKS and issuer |
| `ENTRA_API_CLIENT_ID` | Backend API application ID used to derive audience (`api://<id>`) |
| `ENTRA_TOKEN_AUDIENCE` | Optional explicit audience override |
| `ENTRA_TOKEN_ISSUER` | Optional explicit issuer override |
| `ENTRA_ALLOWED_CLIENT_APP_IDS` | Optional allow-list for `azp`/`appid` claims |

### Stateless session model for agents

All services validate Entra JWTs on every request and avoid server-side session stores. After validation, only request-scoped identity context is propagated to agent workloads:

```json
{
    "subject": "<sub>",
    "tenant_id": "<tid>",
    "object_id": "<oid>",
    "roles": ["student", "professor"]
}
```

This keeps agent execution stateless and prevents cross-request session sharing for data that is not required by the agent.

### Layer 2: Edge Protection

| Control | Configuration |
|---------|--------------|
| **Rate limiting** | 100 requests/minute per user (APIM policy) |
| **Request size** | 10 MB max (essay uploads) |
| **CORS** | SWA origin only (`https://<swa-hostname>.azurestaticapps.net`) |
| **JWT pre-validation** | APIM validates token before routing to backend |
| **IP allowlisting** | Optional per environment (prod: VPN CIDRs only) |
| **WAF** | Azure Front Door WAF (recommended for production) |
| **TLS** | 1.2 minimum, auto-renewed certificates |

### Layer 3: Application Security

| Control | Implementation |
|---------|---------------|
| **RBAC enforcement** | `require_role()` decorator on every endpoint |
| **Input validation** | Pydantic models with strict type checking |
| **Output sanitization** | Strip internal IDs, stack traces, system prompts |
| **Structured logging** | structlog with PII redaction (email → `***@***`) |
| **Error masking** | Generic error messages in production; details in dev |
| **Dependency scanning** | Dependabot for Python + npm vulnerabilities |
| **SAST** | CodeQL on every PR |

### Layer 4: Network Security

```mermaid
graph TB
    subgraph VNet ["VNet 10.0.0.0/22"]
        subgraph ACA_Subnet ["ACA Subnet 10.0.0.0/23"]
            direction TB
            ACA["ACA Container Apps"]
            NSG_ACA["NSG: Allow 443 outbound to PE subnet only"]
        end
        
        subgraph PE_Subnet ["Private Endpoints 10.0.2.0/24"]
            direction TB
            PE_COSMOS["PE: Cosmos DB"]
            PE_OPENAI["PE: OpenAI"]
            PE_SPEECH["PE: Speech"]
            PE_BLOB["PE: Blob Storage"]
            PE_KV["PE: Key Vault"]
            PE_DOCINTEL["PE: Document Intelligence"]
            PE_SEARCH["PE: AI Search"]
            NSG_PE["NSG: Allow 443 inbound from ACA subnet only"]
        end
        
        subgraph APIM_Subnet ["APIM Subnet 10.0.3.0/28"]
            APIM["API Management"]
            NSG_APIM["NSG: Allow 443 inbound from Internet, outbound to ACA"]
        end
    end
    
    INTERNET((Internet)) -->|HTTPS 443| APIM
    APIM -->|HTTPS 443| ACA
    ACA -->|HTTPS 443| PE_Subnet
```

| Rule | Source | Destination | Port | Action |
|------|--------|-------------|------|--------|
| Allow APIM → ACA | 10.0.3.0/28 | 10.0.0.0/23 | 443 | Allow |
| Allow ACA → PE | 10.0.0.0/23 | 10.0.2.0/24 | 443 | Allow |
| Deny all inbound to PE | * | 10.0.2.0/24 | * | Deny |
| Deny all inbound to ACA | * | 10.0.0.0/23 | * | Deny |

### Layer 5: Data Security

| Resource | Control | Details |
|----------|---------|---------|
| **Cosmos DB** | RBAC (no master keys) | `Cosmos DB Built-in Data Contributor` per service MI |
| **Cosmos DB** | Encryption at rest | Microsoft-managed keys (CMK optional) |
| **Cosmos DB** | Network | Private endpoint only; public access disabled |
| **Blob Storage** | RBAC | `Storage Blob Data Contributor` per service MI |
| **Blob Storage** | SAS tokens | Short-lived (1 hour), scoped to container + read-only |
| **Key Vault** | RBAC | `Key Vault Secrets User` per service MI |
| **Key Vault** | Soft delete | Enabled, 90-day retention |
| **Key Vault** | Purge protection | Enabled |
| **All data services** | TLS 1.2+ | Enforced on all connections |

### Layer 6: AI Safety

| Control | Implementation |
|---------|---------------|
| **Content Safety** | Azure AI Content Safety evaluator in evaluation pipeline |
| **Prompt injection defense** | System prompt hardening with clear instruction boundaries |
| **Output filtering** | Post-processing to remove any PII echoed in responses |
| **Jailbreak detection** | Foundry evaluator for adversarial prompt detection |
| **Token budget** | Per-request max_tokens limit; per-user daily token cap |
| **Model access** | Azure OpenAI behind private endpoint; no public API key exposure |

---

## 3. RBAC Matrix

| Endpoint | Student | Professor | Admin | Supervisor |
|----------|---------|-----------|-------|------------|
| `GET /config/courses` | ✅ (enrolled) | ✅ (teaching) | ✅ (all) | ❌ |
| `POST /config/courses` | ❌ | ✅ | ✅ | ❌ |
| `GET /config/pedagogical-rules` | ❌ | ✅ (course) | ✅ (all) | ❌ |
| `PUT /config/pedagogical-rules` | ❌ | ✅ | ✅ | ❌ |
| `GET /config/feature-flags` | ❌ | ❌ | ✅ | ❌ |
| `PUT /config/feature-flags` | ❌ | ❌ | ✅ | ❌ |
| `POST /essays/submit` | ✅ | ❌ | ✅ | ❌ |
| `GET /essays/evaluations` | ✅ (own) | ✅ (course) | ✅ (all) | ❌ |
| `POST /questions/interaction` | ✅ | ❌ | ✅ | ❌ |
| `POST /avatar/session` | ✅ | ✅ | ✅ | ❌ |
| `PUT /avatar/config` | ❌ | ✅ | ✅ | ❌ |
| `POST /chat/session` | ✅ | ❌ | ✅ | ❌ |
| `GET /upskilling/analyze` | ✅ (own) | ✅ (course) | ✅ (all) | ❌ |
| `POST /evaluation/run` | ❌ | ✅ | ✅ | ❌ |
| `GET /evaluation/runs` | ❌ | ✅ (own) | ✅ (all) | ❌ |
| `POST /lms/sync` | ❌ | ❌ | ✅ | ❌ |
| `GET /lms/status` | ❌ | ✅ | ✅ | ❌ |
| `POST /content/upload` | ❌ | ✅ | ✅ | ❌ |
| `GET /content/materials` | ❌ | ✅ | ✅ | ❌ |
| `GET /insights/reports` | ❌ | ❌ | ✅ (all) | ✅ (school-scoped) |
| `POST /insights/generate` | ❌ | ❌ | ✅ | ✅ (school-scoped) |
| `GET /insights/indicators` | ❌ | ❌ | ✅ (all) | ✅ (school-scoped) |
| `PUT /insights/indicator-config` | ❌ | ❌ | ✅ | ❌ |

### Supervisor Data Scoping (BN-SUP-5)

The `supervisor` role has **school-scoped access**. Unlike other roles that use `tenantId` for data isolation, supervisors access data scoped to their assigned schools:

| Claim | Source | Purpose |
|-------|--------|---------|
| `roles: ["supervisor"]` | Entra ID App Role | Route access control |
| `school_ids: [...]` | Entra ID Groups / Microsoft Graph API | Data scoping — supervisor only sees data for assigned schools |

insights-svc validates school access on every request:

```python
@require_role("supervisor")
async def get_report(school_id: str, user: AuthenticatedUser):
    if school_id not in user.school_ids:
        raise HTTPException(403, "No access to this school")
    return await insight_service.get_report(school_id)
```

---

## 4. Managed Identity Assignments

```mermaid
graph LR
    subgraph Identities
        MI_CONFIG["MI: config-svc"]
        MI_ESSAYS["MI: essays-svc"]
        MI_QUESTIONS["MI: questions-svc"]
        MI_AVATAR["MI: avatar-svc"]
        MI_UPSKILLING["MI: upskilling-svc"]
        MI_EVAL["MI: evaluation-svc"]
        MI_LMS["MI: lms-gateway"]
        MI_CHAT["MI: chat-svc"]
        MI_CONTENT["MI: content-svc"]
        MI_INSIGHTS["MI: insights-svc"]
    end

    subgraph Resources
        COSMOS[("Cosmos DB")]
        OPENAI["OpenAI"]
        SPEECH["Speech"]
        BLOB["Blob Storage"]
        KV["Key Vault"]
        ACR["ACR"]
        FOUNDRY["AI Foundry"]
        DOCINTEL["Document Intelligence"]
        SEARCH["AI Search"]
        FABRIC["Microsoft Fabric"]
    end

    MI_CONFIG -->|Data Contributor| COSMOS
    MI_CONFIG -->|Secrets User| KV
    MI_CONFIG -->|AcrPull| ACR

    MI_ESSAYS -->|Data Contributor| COSMOS
    MI_ESSAYS -->|OpenAI User| OPENAI
    MI_ESSAYS -->|Blob Contributor| BLOB
    MI_ESSAYS -->|AI Developer| FOUNDRY
    MI_ESSAYS -->|Secrets User| KV
    MI_ESSAYS -->|AcrPull| ACR
    MI_ESSAYS -->|Search Index Reader| SEARCH
    MI_ESSAYS -->|CogSvc User| DOCINTEL

    MI_QUESTIONS -->|Data Contributor| COSMOS
    MI_QUESTIONS -->|OpenAI User| OPENAI
    MI_QUESTIONS -->|AI Developer| FOUNDRY
    MI_QUESTIONS -->|Secrets User| KV
    MI_QUESTIONS -->|AcrPull| ACR
    MI_QUESTIONS -->|Search Index Reader| SEARCH

    MI_AVATAR -->|Data Contributor| COSMOS
    MI_AVATAR -->|OpenAI User| OPENAI
    MI_AVATAR -->|Speech User| SPEECH
    MI_AVATAR -->|Secrets User| KV
    MI_AVATAR -->|AcrPull| ACR

    MI_EVAL -->|Data Contributor| COSMOS
    MI_EVAL -->|AI Developer| FOUNDRY
    MI_EVAL -->|Secrets User| KV
    MI_EVAL -->|AcrPull| ACR

    MI_CONTENT -->|Data Contributor| COSMOS
    MI_CONTENT -->|Blob Contributor| BLOB
    MI_CONTENT -->|CogSv User| DOCINTEL
    MI_CONTENT -->|Search Index Contributor| SEARCH
    MI_CONTENT -->|OpenAI User| OPENAI
    MI_CONTENT -->|Secrets User| KV
    MI_CONTENT -->|AcrPull| ACR

    MI_INSIGHTS -->|Data Contributor| COSMOS
    MI_INSIGHTS -->|OpenAI User| OPENAI
    MI_INSIGHTS -->|Fabric.Read| FABRIC
    MI_INSIGHTS -->|Secrets User| KV
    MI_INSIGHTS -->|AcrPull| ACR
```

---

## 5. Security Checklist

### Pre-Production

- [ ] Entra ID app registration with app roles configured
- [ ] JWT validation middleware enabled on all services
- [ ] RBAC decorators applied to all endpoints
- [ ] Managed Identity assigned to all ACA container apps
- [ ] All Azure resources behind private endpoints
- [ ] NSG rules enforced (deny-all-inbound + specific allows)
- [ ] Key Vault soft delete and purge protection enabled
- [ ] Connection strings removed from all environment variables
- [ ] Content-Security-Policy headers on frontend
- [ ] CORS restricted to SWA origin
- [ ] Dependabot enabled for Python and npm
- [ ] CodeQL SAST enabled in CI
- [ ] Diagnostic settings enabled on all resources
- [ ] Alert rules configured for auth failures and error spikes
- [ ] Content Safety evaluator in evaluation pipeline
- [ ] Container images signed and pulled from private ACR

### Post-Production (Ongoing)

- [ ] Monthly dependency vulnerability review
- [ ] Quarterly penetration testing
- [ ] Annual security architecture review
- [ ] Continuous monitoring via Azure Security Center
- [ ] Incident response plan tested semi-annually
