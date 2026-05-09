# Public with BYOR example

This deploys the module with public network access and Bring Your Own Resources (BYOR) services.

## Architecture

This example demonstrates a public deployment with custom Key Vault, Storage, Cosmos DB, and AI Search:

```mermaid
graph TB
    subgraph "Azure Resource Group"
        AF[AI Foundry<br/>Account]
        AFP[AI Foundry<br/>Project]
        AMD[AI Model<br/>Deployment]
        KV[Key Vault<br/>BYOR]
        ST[Storage Account<br/>BYOR]
        CS[Cosmos DB<br/>BYOR]
        AS[AI Search<br/>BYOR]
    end

    INTERNET((Internet)) --> AF
    INTERNET --> KV
    INTERNET --> ST
    INTERNET --> CS
    INTERNET --> AS

    AF --> AFP
    AF --> AMD
    AF -.-> KV
    AF -.-> ST
    AF -.-> CS
    AF -.-> AS

    classDef required fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef byor fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    class AF,AFP,AMD required
    class KV,ST,CS,AS byor
    class INTERNET external
```

**Components:**
- AI Foundry Account with GPT-4 model deployment
- AI Foundry Project for development workspace
- Public network access enabled
- BYOR: Key Vault, Storage Account, Cosmos DB, AI Search
