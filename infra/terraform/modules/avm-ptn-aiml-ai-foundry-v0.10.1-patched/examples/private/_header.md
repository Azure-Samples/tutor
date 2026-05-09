# Private example

This deploys the module with private networking and secure access.

## Architecture

This example demonstrates a deployment with private endpoints for secure connectivity:

```mermaid
graph TB
    subgraph "Azure Resource Group"
        subgraph "Virtual Network"
            PE_SUBNET[Private Endpoint<br/>Subnet]
            PE_AF[Private Endpoint<br/>AI Foundry]
        end

        AF[AI Foundry<br/>Account]
        AFP[AI Foundry<br/>Project]
        AMD[AI Model<br/>Deployment]
    end

    AF --> AFP
    AF --> AMD
    PE_AF -.-> AF
    PE_SUBNET --> PE_AF

    classDef required fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef network fill:#fff3e0,stroke:#e65100,stroke-width:2px
    class AF,AFP,AMD required
    class PE_SUBNET,PE_AF network
```

**Components:**
- AI Foundry Account with GPT-4 model deployment
- AI Foundry Project for development workspace
- Private endpoints for secure network access
- No BYOR services (uses managed AI Foundry services)
