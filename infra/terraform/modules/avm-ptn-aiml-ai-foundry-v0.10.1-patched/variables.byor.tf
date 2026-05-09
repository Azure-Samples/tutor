variable "ai_search_definition" {
  type = map(object({
    existing_resource_id                    = optional(string, null)
    name                                    = optional(string)
    private_dns_zone_resource_id            = optional(string, null)
    private_endpoints_manage_dns_zone_group = optional(bool, true)
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      storage_account_resource_id              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    sku                          = optional(string, "standard")
    local_authentication_enabled = optional(bool, true)
    partition_count              = optional(number, 1)
    replica_count                = optional(number, 2)
    semantic_search              = optional(string, "disabled")
    hosting_mode                 = optional(string, "default")
    tags                         = optional(map(string), {})
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
    enable_telemetry = optional(bool, true)
  }))
  default     = {}
  description = <<DESCRIPTION
Configuration object for the Azure AI Search service to be created as part of the enterprise and public knowledge services.

- `map key` - The key for the map entry. This key should match the AI project key when creating multiple projects with multiple AI search services.
  - `existing_resource_id` - (Optional) The resource ID of an existing AI Search service to use. If provided, the service will not be created and the other inputs will be ignored.
  - `name` - (Optional) The name of the AI Search service. If not provided, a name will be generated.
  - `private_dns_zone_resource_id` - (Optional) The resource ID of the existing private DNS zone for AI Search. If not provided or set to null, no DNS zone group will be created.
  - `private_endpoints_manage_dns_zone_group` - (Optional) Whether to manage private DNS zone groups with this module. If set to false, you must manage private DNS zone groups externally, e.g. using Azure Policy. Default is true.
  - `diagnostic_settings` - (Optional) A map of diagnostic settings to create. Each entry follows the AVM diagnostic_settings interface.
  - `sku` - (Optional) The SKU of the AI Search service. Default is "standard".
  - `local_authentication_enabled` - (Optional) Whether local authentication is enabled. Default is true.
  - `partition_count` - (Optional) The number of partitions for the search service. Default is 1.
  - `replica_count` - (Optional) The number of replicas for the search service. Default is 2.
  - `semantic_search` - (Optional) The semantic search tier. Possible values are "disabled", "free", or "standard". Default is "disabled".
  - `hosting_mode` - (Optional) The hosting mode for the search service. Default is "default".
  - `tags` - (Optional) Map of tags to assign to the AI Search service.
  - `role_assignments` - (Optional) Map of role assignments to create on the AI Search service. The map key is deliberately arbitrary to avoid issues where map keys may be unknown at plan time.
    - `role_definition_id_or_name` - The role definition ID or name to assign.
    - `principal_id` - The principal ID to assign the role to.
    - `description` - (Optional) Description of the role assignment.
    - `skip_service_principal_aad_check` - (Optional) Whether to skip AAD check for service principal.
    - `condition` - (Optional) Condition for the role assignment.
    - `condition_version` - (Optional) Version of the condition.
    - `delegated_managed_identity_resource_id` - (Optional) Resource ID of the delegated managed identity.
    - `principal_type` - (Optional) Type of the principal (User, Group, ServicePrincipal).
  - `enable_telemetry` - (Optional) Whether telemetry is enabled for the AI Search module. Default is true.
DESCRIPTION
}

variable "cosmosdb_definition" {
  type = map(object({
    existing_resource_id                    = optional(string, null)
    private_dns_zone_resource_id            = optional(string, null)
    private_endpoints_manage_dns_zone_group = optional(bool, true)
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      storage_account_resource_id              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    name = optional(string)
    secondary_regions = optional(list(object({
      location          = string
      zone_redundant    = optional(bool, true)
      failover_priority = optional(number, 0)
    })), [])
    public_network_access_enabled    = optional(bool, false)
    analytical_storage_enabled       = optional(bool, true)
    automatic_failover_enabled       = optional(bool, true)
    local_authentication_disabled    = optional(bool, true)
    partition_merge_enabled          = optional(bool, false)
    multiple_write_locations_enabled = optional(bool, false)
    analytical_storage_config = optional(object({
      schema_type = string
    }), null)
    consistency_policy = optional(object({
      max_interval_in_seconds = optional(number, 300)
      max_staleness_prefix    = optional(number, 100001)
      consistency_level       = optional(string, "Session")
    }), {})
    backup = optional(object({
      retention_in_hours  = optional(number)
      interval_in_minutes = optional(number)
      storage_redundancy  = optional(string)
      type                = optional(string)
      tier                = optional(string)
    }), {})
    capabilities = optional(set(object({
      name = string
    })), [])
    capacity = optional(object({
      total_throughput_limit = optional(number, -1)
    }), {})
    cors_rule = optional(object({
      allowed_headers    = set(string)
      allowed_methods    = set(string)
      allowed_origins    = set(string)
      exposed_headers    = set(string)
      max_age_in_seconds = optional(number, null)
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
    tags = optional(map(string), {})
  }))
  default     = {}
  description = <<DESCRIPTION
Configuration object for the Azure Cosmos DB account to be created for GenAI services.

- `map key` - The key for the map entry. This key should match the AI project key when creating multiple projects and multiple CosmosDB accounts.
  - `existing_resource_id` - (Optional) The resource ID of an existing Cosmos DB account to use. If provided, the account will not be created and the other inputs will be ignored.
  - `private_dns_zone_resource_id` - (Optional) The resource ID of the existing private DNS zone for Cosmos DB. If not provided or set to null, no DNS zone group will be created.
  - `private_endpoints_manage_dns_zone_group` - (Optional) Whether to manage private DNS zone groups with this module. If set to false, you must manage private DNS zone groups externally, e.g. using Azure Policy. Default is true.
  - `diagnostic_settings` - (Optional) A map of diagnostic settings to create. Each entry follows the AVM diagnostic_settings interface.
  - `name` - (Optional) The name of the Cosmos DB account. If not provided, a name will be generated.
  - `secondary_regions` - (Optional) List of secondary regions for geo-replication.
    - `location` - The Azure region for the secondary location.
    - `zone_redundant` - (Optional) Whether zone redundancy is enabled for the secondary region. Default is true.
    - `failover_priority` - (Optional) The failover priority for the secondary region. Default is 0.
  - `public_network_access_enabled` - (Optional) Whether public network access is enabled. Default is false.
  - `analytical_storage_enabled` - (Optional) Whether analytical storage is enabled. Default is true.
  - `automatic_failover_enabled` - (Optional) Whether automatic failover is enabled. Default is false.
  - `local_authentication_disabled` - (Optional) Whether local authentication is disabled. Default is true.
  - `partition_merge_enabled` - (Optional) Whether partition merge is enabled. Default is false.
  - `multiple_write_locations_enabled` - (Optional) Whether multiple write locations are enabled. Default is false.
  - `analytical_storage_config` - (Optional) Analytical storage configuration.
    - `schema_type` - The schema type for analytical storage.
  - `consistency_policy` - (Optional) Consistency policy configuration.
    - `max_interval_in_seconds` - (Optional) Maximum staleness interval in seconds. Default is 300.
    - `max_staleness_prefix` - (Optional) Maximum staleness prefix. Default is 100001.
    - `consistency_level` - (Optional) The consistency level. Default is "Session".
  - `backup` - (Optional) Backup configuration.
    - `retention_in_hours` - (Optional) Backup retention in hours.
    - `interval_in_minutes` - (Optional) Backup interval in minutes.
    - `storage_redundancy` - (Optional) Storage redundancy for backups.
    - `type` - (Optional) The backup type.
    - `tier` - (Optional) The backup tier.
  - `capabilities` - (Optional) Set of capabilities to enable on the Cosmos DB account.
    - `name` - The name of the capability.
  - `capacity` - (Optional) Capacity configuration.
    - `total_throughput_limit` - (Optional) Total throughput limit. Default is -1 (unlimited).
  - `cors_rule` - (Optional) CORS rule configuration.
    - `allowed_headers` - Set of allowed headers.
    - `allowed_methods` - Set of allowed HTTP methods.
    - `allowed_origins` - Set of allowed origins.
    - `exposed_headers` - Set of exposed headers.
    - `max_age_in_seconds` - (Optional) Maximum age in seconds for CORS.
  - `role_assignments` - (Optional) Map of role assignments to create on the Cosmos DB account. The map key is deliberately arbitrary to avoid issues where map keys may be unknown at plan time.
    - `role_definition_id_or_name` - The role definition ID or name to assign.
    - `principal_id` - The principal ID to assign the role to.
    - `description` - (Optional) Description of the role assignment.
    - `skip_service_principal_aad_check` - (Optional) Whether to skip AAD check for service principal.
    - `condition` - (Optional) Condition for the role assignment.
    - `condition_version` - (Optional) Version of the condition.
    - `delegated_managed_identity_resource_id` - (Optional) Resource ID of the delegated managed identity.
    - `principal_type` - (Optional) Type of the principal (User, Group, ServicePrincipal).
  - `tags` - (Optional) Map of tags to assign to the Cosmos DB account.
DESCRIPTION
}

variable "key_vault_definition" {
  type = map(object({
    existing_resource_id                    = optional(string, null)
    name                                    = optional(string)
    private_dns_zone_resource_id            = optional(string, null)
    private_endpoints_manage_dns_zone_group = optional(bool, true)
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      storage_account_resource_id              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    sku       = optional(string, "standard")
    tenant_id = optional(string)
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
    tags = optional(map(string), {})
  }))
  default     = {}
  description = <<DESCRIPTION
Configuration object for the Azure Key Vault to be created for GenAI services.

- `map key` - The key for the map entry. This key should match the AI project key when creating multiple projects with multiple Key Vaults. This can be used in naming, so short alphanumeric keys are required to avoid hitting naming length limits for the Key Vault when using the base name naming option.
  - `existing_resource_id` - (Optional) The resource ID of an existing Key Vault to use. If provided, the vault will not be created and the other inputs will be ignored.
  - `name` - (Optional) The name of the Key Vault. If not provided, a name will be generated.
  - `private_dns_zone_resource_id` - (Optional) The resource ID of the existing private DNS zone for Key Vault. If not provided or set to null, no DNS zone group will be created.
  - `private_endpoints_manage_dns_zone_group` - (Optional) Whether to manage private DNS zone groups with this module. If set to false, you must manage private DNS zone groups externally, e.g. using Azure Policy. Default is true.
  - `diagnostic_settings` - (Optional) A map of diagnostic settings to create. Each entry follows the AVM diagnostic_settings interface.
  - `sku` - (Optional) The SKU of the Key Vault. Default is "standard".
  - `tenant_id` - (Optional) The tenant ID for the Key Vault. If not provided, the current tenant will be used.
  - `role_assignments` - (Optional) Map of role assignments to create on the Key Vault. The map key is deliberately arbitrary to avoid issues where map keys may be unknown at plan time.
    - `role_definition_id_or_name` - The role definition ID or name to assign.
    - `principal_id` - The principal ID to assign the role to.
    - `description` - (Optional) Description of the role assignment.
    - `skip_service_principal_aad_check` - (Optional) Whether to skip AAD check for service principal.
    - `condition` - (Optional) Condition for the role assignment.
    - `condition_version` - (Optional) Version of the condition.
    - `delegated_managed_identity_resource_id` - (Optional) Resource ID of the delegated managed identity.
    - `principal_type` - (Optional) Type of the principal (User, Group, ServicePrincipal).
  - `tags` - (Optional) Map of tags to assign to the Key Vault.
DESCRIPTION
}

variable "storage_account_definition" {
  type = map(object({
    existing_resource_id = optional(string, null)
    diagnostic_settings_storage_account = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      storage_account_resource_id              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    name                     = optional(string, null)
    account_kind             = optional(string, "StorageV2")
    account_tier             = optional(string, "Standard")
    account_replication_type = optional(string, "ZRS")
    endpoints = optional(map(object({
      type                                    = string
      private_dns_zone_resource_id            = optional(string, null)
      private_endpoints_manage_dns_zone_group = optional(bool, true)
      })), {
      blob = {
        type = "blob"
      }
    })
    access_tier               = optional(string, "Hot")
    shared_access_key_enabled = optional(bool, false)
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
    tags = optional(map(string), {})

    #TODO:
    # Implement subservice passthrough here
  }))
  default     = {}
  description = <<DESCRIPTION
Configuration object for the Azure Storage Account to be created for GenAI services.

- `map key` - The key for the map entry. This key should match the AI project key when creating multiple projects with multiple Storage Accounts. This can be used in naming, so short alphanumeric keys are required to avoid hitting naming length limits for the Storage Account when using the base name naming option.
  - `existing_resource_id` - (Optional) The resource ID of an existing Storage Account to use. If provided, the account will not be created and the other inputs will be ignored.
  - `diagnostic_settings_storage_account` - (Optional) A map of diagnostic settings to create on the storage account. Each entry follows the AVM diagnostic_settings interface.
  - `name` - (Optional) The name of the Storage Account. If not provided, a name will be generated.
  - `account_kind` - (Optional) The kind of storage account. Default is "StorageV2".
  - `account_tier` - (Optional) The performance tier of the storage account. Default is "Standard".
  - `account_replication_type` - (Optional) The replication type for the storage account. Default is "ZRS".
  - `endpoints` - (Optional) Map of endpoint configurations to enable. Default includes blob endpoint.
    - `type` - The type of endpoint (e.g., "blob", "file", "queue", "table").
    - `private_dns_zone_resource_id` - (Optional) The resource ID of the existing private DNS zone for the endpoint. If not provided or set to null, no DNS zone group will be created.
    - `private_endpoints_manage_dns_zone_group` - (Optional) Whether to manage private DNS zone groups with this module. If set to false, you must manage private DNS zone groups externally, e.g. using Azure Policy. Default is true.
  - `access_tier` - (Optional) The access tier for the storage account. Default is "Hot".
  - `shared_access_key_enabled` - (Optional) Whether shared access keys are enabled. Default is false.
  - `role_assignments` - (Optional) Map of role assignments to create on the Storage Account. The map key is deliberately arbitrary to avoid issues where map keys may be unknown at plan time.
    - `role_definition_id_or_name` - The role definition ID or name to assign.
    - `principal_id` - The principal ID to assign the role to.
    - `description` - (Optional) Description of the role assignment.
    - `skip_service_principal_aad_check` - (Optional) Whether to skip AAD check for service principal.
    - `condition` - (Optional) Condition for the role assignment.
    - `condition_version` - (Optional) Version of the condition.
    - `delegated_managed_identity_resource_id` - (Optional) Resource ID of the delegated managed identity.
    - `principal_type` - (Optional) Type of the principal (User, Group, ServicePrincipal).
  - `tags` - (Optional) Map of tags to assign to the Storage Account.
DESCRIPTION
}
