# ADR-008: Security Layers and Zero-Trust

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

The current platform has **no security layers**:

1. **No authentication** — All API endpoints are publicly accessible without credentials.
2. **No authorization** — No RBAC; anyone can access professor-only endpoints.
3. **No API gateway** — Services are directly exposed without rate limiting or request validation.
4. **Partial network isolation** — VNet exists with private endpoints for AI services, but ACA apps have public ingress.
5. **No secrets management at runtime** — Services use environment variables; Dockerfiles are empty.
6. **No Content Security Policy** — Frontend has no CSP headers.
7. **No input validation at the edge** — Each service validates its own input inconsistently.

## Decision

**Implement a defense-in-depth security architecture** with zero-trust principles across all layers.

### 1. Security Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: IDENTITY (Microsoft Entra ID)                       │
│  • OAuth 2.0 / OIDC for user authentication                 │
│  • MSAL on frontend, JWT validation on backend              │
│  • Managed Identity for service-to-service + Azure resources │
├──────────────────────────────────────────────────────────────┤
│ Layer 2: EDGE (API Management / ACA Ingress)                 │
│  • Rate limiting (100 req/min per user)                      │
│  • JWT validation (pre-authorized clients)                   │
│  • Request size limits (10 MB max)                           │
│  • CORS policy (SWA origin only)                             │
│  • IP allowlisting (optional per environment)                │
├──────────────────────────────────────────────────────────────┤
│ Layer 3: APPLICATION (FastAPI middleware)                     │
│  • RBAC enforcement (student/professor/admin roles)          │
│  • Input validation (Pydantic models)                        │
│  • Output sanitization                                       │
│  • Request/response logging (structlog, no PII)              │
│  • Error masking (no stack traces in production)             │
├──────────────────────────────────────────────────────────────┤
│ Layer 4: NETWORK (VNet + Private Endpoints)                  │
│  • ACA Environment in VNet subnet                            │
│  • Private Endpoints for Cosmos, OpenAI, Speech, Blob, KV    │
│  • NSG rules: deny all inbound except ACA → PE subnet        │
│  • No public IP on data services                             │
├──────────────────────────────────────────────────────────────┤
│ Layer 5: DATA (Encryption + Access Control)                  │
│  • Cosmos DB: RBAC (no master keys), encryption at rest      │
│  • Blob Storage: RBAC, SAS tokens (short-lived, scoped)      │
│  • Key Vault: RBAC, soft delete, purge protection            │
│  • TLS 1.2+ for all connections                              │
├──────────────────────────────────────────────────────────────┤
│ Layer 6: OBSERVABILITY (Audit + Monitoring)                  │
│  • Azure Monitor diagnostic settings on all resources        │
│  • App Insights for request tracing                          │
│  • Audit log for authentication events                       │
│  • Alert rules for 4xx/5xx spikes, latency, auth failures    │
└──────────────────────────────────────────────────────────────┘
```

### 2. Identity & Authentication

#### Frontend (MSAL React)

- `@azure/msal-react` for SSO with Microsoft Entra ID.
- Acquire access tokens with `api://<client-id>/.default` scope.
- Attach `Authorization: Bearer <token>` header to all API calls.
- Silent token refresh; redirect to login on 401.

#### Backend (JWT Validation)

```python
# lib/src/tutor_lib/middleware/auth.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

security = HTTPBearer()

class EntraIDAuth:
    def __init__(self, tenant_id: str, client_id: str):
        self.jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self.audience = f"api://{client_id}"
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self._jwk_client = PyJWKClient(self.jwks_url)

    async def validate(
        self, credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        token = credentials.credentials
        signing_key = self._jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.audience,
            issuer=self.issuer,
        )
        return payload
```

### 3. Role-Based Access Control (RBAC)

| Role | Allowed Endpoints | Scope |
|------|-------------------|-------|
| `student` | GET/POST on assessment endpoints, avatar/chat sessions | Own data only |
| `professor` | All student permissions + configuration, evaluation, upskilling | Course-scoped |
| `admin` | All permissions + LMS gateway, system configuration | Tenant-wide |

Roles are sourced from Entra ID app roles or group memberships, decoded from the JWT `roles` claim.

```python
# lib/src/tutor_lib/middleware/auth.py
from functools import wraps

def require_role(*allowed_roles: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = Depends(auth.validate), **kwargs):
            user_roles = user.get("roles", [])
            if not any(r in allowed_roles for r in user_roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

# Usage:
@router.post("/courses")
@require_role("professor", "admin")
async def create_course(course: CourseCreate, user: dict = Depends(auth.validate)):
    ...
```

### 4. Managed Identity for Azure Resources

Each ACA Container App uses a **User-Assigned Managed Identity**:

| Resource | RBAC Role | Scope |
|----------|-----------|-------|
| Cosmos DB | `Cosmos DB Built-in Data Contributor` | Database-level |
| Azure OpenAI | `Cognitive Services OpenAI User` | Account-level |
| Azure Speech | `Cognitive Services Speech User` | Account-level |
| Blob Storage | `Storage Blob Data Contributor` | Container-level |
| Key Vault | `Key Vault Secrets User` | Vault-level |
| ACR | `AcrPull` | Registry-level |
| AI Foundry | `Azure AI Developer` | Project-level |

**No connection strings or API keys in environment variables.** All access uses `DefaultAzureCredential` → Managed Identity.

### 5. Network Security

```hcl
# Terraform NSG rules
resource "azurerm_network_security_rule" "deny_all_inbound" {
  name                       = "DenyAllInbound"
  priority                   = 4096
  direction                  = "Inbound"
  access                     = "Deny"
  protocol                   = "*"
  source_port_range          = "*"
  destination_port_range     = "*"
  source_address_prefix      = "*"
  destination_address_prefix = "*"
}

resource "azurerm_network_security_rule" "allow_aca_to_pe" {
  name                       = "AllowAcaToPrivateEndpoints"
  priority                   = 100
  direction                  = "Outbound"
  access                     = "Allow"
  protocol                   = "Tcp"
  source_port_range          = "*"
  destination_port_range     = "443"
  source_address_prefix      = "10.0.0.0/23"   # ACA subnet
  destination_address_prefix = "10.0.2.0/24"    # PE subnet
}
```

### 6. Content Security Policy (Frontend)

```typescript
// next.config.mjs
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval'",  // Required for Next.js dev
      "style-src 'self' 'unsafe-inline'",
      `connect-src 'self' https://login.microsoftonline.com https://*.azurecontainer.io`,
      "img-src 'self' data: blob:",
      "media-src 'self' blob:",
      "frame-src 'none'",
    ].join('; '),
  },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(self), geolocation=()' },
];
```

### 7. Secret Management

| Environment | Approach |
|-------------|----------|
| **Local dev** | `.env` files (not committed) with Managed Identity via `az login` |
| **CI/CD** | GitHub Secrets → ACA environment variables (non-sensitive only) |
| **Production** | Key Vault references in ACA; Managed Identity reads secrets |

## Consequences

### Positive

- **Zero-trust posture** — No implicit trust; every request is authenticated and authorized.
- **Defense in depth** — Six layers from identity to data; single-layer failure doesn't compromise system.
- **No secrets in code** — Managed Identity eliminates connection strings and API keys.
- **Audit trail** — All authentication and authorization events logged for compliance.
- **CORS enforcement** — Only the SWA frontend can call backend APIs.

### Negative

- **Complexity** — Six security layers add configuration and debugging overhead.
- **Latency** — JWT validation and RBAC checks add ~5-10ms per request.
- **Local development** — Developers need Entra ID app registration for local auth testing.

### Mitigations

- Provide a `dev` auth mode with simplified token validation for local development.
- Use `DefaultAzureCredential` which falls back to `az login` for developers.
- Centralize all security middleware in `tutor-lib` to avoid per-service configuration.

## References

- [Microsoft Zero Trust Model](https://learn.microsoft.com/security/zero-trust/)
- [ACA managed identity](https://learn.microsoft.com/azure/container-apps/managed-identity)
- [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/)
- [MSAL React](https://learn.microsoft.com/entra/identity-platform/tutorial-v2-react)
- [Azure RBAC for Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/how-to-setup-rbac)
- [CSP for Next.js](https://nextjs.org/docs/advanced-features/security-headers)
