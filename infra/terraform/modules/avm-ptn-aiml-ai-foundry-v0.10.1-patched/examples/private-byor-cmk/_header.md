# Private with BYOR and CMK example

This deploys the module with private networking, BYOR services, and Customer Managed Keys (CMK).

## Architecture

This example demonstrates a fully secured private deployment with encryption using customer-managed keys:

```mermaid
graph TB
    subgraph "Azure Resource Group"
        subgraph "Virtual Network"
            PE_SUBNET[Private Endpoint<br/>Subnet]
            PE_AF[PE: AI Foundry]
            PE_KV[PE: Key Vault]
            PE_ST[PE: Storage]
            PE_CS[PE: Cosmos DB]
            PE_AS[PE: AI Search]
        end

        AF[AI Foundry<br/>Account]
        AFP[AI Foundry<br/>Project]
        AMD[AI Model<br/>Deployment]
        KV[Key Vault<br/>BYOR + CMK]
        ST[Storage Account<br/>BYOR + CMK]
        CS[Cosmos DB<br/>BYOR + CMK]
        AS[AI Search<br/>BYOR]
        CMK[Customer Managed<br/>Key]
    end

    AF --> AFP
    AF --> AMD
    AF -.-> KV
    AF -.-> ST
    AF -.-> CS
    AF -.-> AS

    KV --> CMK
    AF -. encrypted with .-> CMK
    ST -. encrypted with .-> CMK
    CS -. encrypted with .-> CMK

    PE_AF -.-> AF
    PE_KV -.-> KV
    PE_ST -.-> ST
    PE_CS -.-> CS
    PE_AS -.-> AS

    PE_SUBNET --> PE_AF
    PE_SUBNET --> PE_KV
    PE_SUBNET --> PE_ST
    PE_SUBNET --> PE_CS
    PE_SUBNET --> PE_AS

    classDef required fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef byor fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef security fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    class AF,AFP,AMD required
    class KV,ST,CS,AS byor
    class PE_SUBNET,PE_AF,PE_KV,PE_ST,PE_CS,PE_AS network
    class CMK security
```

**Components:**
- AI Foundry Account with GPT-4 model deployment
- AI Foundry Project for development workspace
- Private endpoints for all services
- BYOR: Key Vault, Storage Account, Cosmos DB, AI Search
- Customer Managed Keys (CMK) for encryption at rest
