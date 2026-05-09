# Basic CMK (Customer-Managed Key) Encryption Example

This example demonstrates how to deploy an AI Foundry account with customer-managed key (CMK) encryption using a user-assigned managed identity (UAMI).

## Architecture

This example deploys AI Foundry with CMK encryption across these components:

**Security & Encryption Layer:**
- User-Assigned Managed Identity (UAMI) - Provides secure authentication to Key Vault
- Key Vault with RBAC authorization and purge protection - Stores and manages encryption keys
- RSA 2048-bit Key Vault Key - Used for data encryption at rest

**Core AI Foundry Resources:**
- AI Foundry Account with CMK encryption enabled
- AI Foundry Project for development workspace
- GPT-4 model deployment for AI workloads
2. Deploy AI Foundry account (initially without CMK)
3. Assign "Key Vault Crypto User" role to the UAMI
4. Update AI Foundry account to apply CMK encryption

This two-step approach is necessary because the AI Foundry account must exist before CMK encryption can be configured.
