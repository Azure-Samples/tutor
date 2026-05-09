# Basic example

This deploys the module in its most basic form.

## Architecture

This example deploys only the core AI Foundry components:

```mermaid
graph TB
    subgraph "Azure Resource Group"
        AF[AI Foundry<br/>Account]
        AFP[AI Foundry<br/>Project]
        AMD[AI Model<br/>Deployment]
    end
    
    AF --> AFP
    AF --> AMD
    
    classDef required fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    class AF,AFP,AMD required
```

**Components:**
- AI Foundry Account with GPT-4 model deployment
- AI Foundry Project for development workspace  
- Public access (no private endpoints or BYOR services)
