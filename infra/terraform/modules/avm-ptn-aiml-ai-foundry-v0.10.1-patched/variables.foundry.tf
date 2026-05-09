variable "ai_foundry" {
  type = object({
    name                     = optional(string, null)
    disable_local_auth       = optional(bool, false)
    allow_project_management = optional(bool, true)
    create_ai_agent_service  = optional(bool, false)
    network_injections = optional(list(object({
      scenario                   = optional(string, "agent")
      subnetArmId                = string
      useMicrosoftManagedNetwork = optional(bool, false)
    })), null)
    private_dns_zone_resource_ids = optional(list(string), [])
    sku                           = optional(string, "S0")
    customer_managed_key = optional(object({
      key_vault_resource_id              = string
      key_name                           = string
      key_version                        = optional(string, null)
      user_assigned_identity_resource_id = string
    }), null)
    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
      principal_type                         = optional(string, null)
    })), {})
  })
  default     = {}
  description = <<DESCRIPTION
Configuration object for the Azure AI Foundry service to be created for AI workloads and model management.

- `name` - (Optional) The name of the AI Foundry service. If not provided, a name will be generated.
- `disable_local_auth` - (Optional) Whether to disable local authentication for the AI Foundry service. Default is false.
- `allow_project_management` - (Optional) Whether to allow project management capabilities in the AI Foundry service. Default is true.
- `create_ai_agent_service` - (Optional) Whether to create an AI agent service as part of the AI Foundry deployment. Default is false.
- `network_injections` - (Optional) List of network injection configurations for the AI Foundry service.
  - `scenario` - (Optional) The scenario for the network injection. Default is "agent".
  - `subnetArmId` - The subnet ARM ID for the AI agent service.
  - `useMicrosoftManagedNetwork` - (Optional) Whether to use Microsoft managed network for the injection. Default is false.
- `private_dns_zone_resource_ids` - (Optional) The resource IDs of the existing private DNS zones for AI Foundry. Required when `create_private_endpoints` is true.
- `sku` - (Optional) The SKU of the AI Foundry service. Default is "S0".
- `customer_managed_key` - (Optional) Customer-managed key encryption configuration. Requires a Key Vault with an existing key and a user-assigned managed identity with "Key Vault Crypto User" role on the Key Vault.
  - `key_vault_resource_id` - Resource ID of the Key Vault containing the encryption key.
  - `key_name` - Name of the Key Vault key to use for encryption.
  - `key_version` - (Optional) Version of the Key Vault key. If not specified, uses the latest version.
  - `user_assigned_identity_resource_id` - Resource ID of the user-assigned managed identity with access to the Key Vault.
- `role_assignments` - (Optional) Map of role assignments to create on the AI Foundry service. The map key is deliberately arbitrary to avoid issues where map keys may be unknown at plan time.
  - `role_definition_id_or_name` - The role definition ID or name to assign.
  - `principal_id` - The principal ID to assign the role to.
  - `description` - (Optional) Description of the role assignment.
  - `skip_service_principal_aad_check` - (Optional) Whether to skip AAD check for service principal.
  - `condition` - (Optional) Condition for the role assignment.
  - `condition_version` - (Optional) Version of the condition.
  - `delegated_managed_identity_resource_id` - (Optional) Resource ID of the delegated managed identity.
  - `principal_type` - (Optional) Type of the principal (User, Group, ServicePrincipal).
DESCRIPTION
}

variable "cognitive_services_api_version" {
  type        = string
  default     = "2025-10-01-preview"
  description = "API version used for Microsoft.CognitiveServices account resources. Use `2025-07-01-preview` for compatibility with AzAPI provider versions that do not include `2025-10-01-preview`."

  validation {
    condition = contains([
      "2025-07-01-preview",
      "2025-10-01-preview"
    ], var.cognitive_services_api_version)
    error_message = "Allowed values for cognitive_services_api_version are 2025-07-01-preview and 2025-10-01-preview."
  }
}
