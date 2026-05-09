# Public example

This deploys the module with public network access.

## Architecture

This example demonstrates a deployment with public endpoints for development/testing:

```mermaid
graph TB
    subgraph "Azure Resource Group"
        AF[AI Foundry<br/>Account]
        AFP[AI Foundry<br/>Project]
        AMD[AI Model<br/>Deployment]
    end

    INTERNET((Internet)) --> AF
    AF --> AFP
    AF --> AMD

    classDef required fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef external fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    class AF,AFP,AMD required
    class INTERNET external
```

**Components:**
- AI Foundry Account with GPT-4 model deployment
- AI Foundry Project for development workspace
- Public network access enabled (no private endpoints)
- No BYOR services (uses managed AI Foundry services)
