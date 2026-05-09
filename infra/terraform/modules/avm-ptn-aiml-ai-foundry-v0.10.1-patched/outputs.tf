#TODO: Rewrite this to return the basename of the ai search service if a resource ID is provided, otherwise return the names (or resource id)

output "ai_agent_account_capability_host_id" {
  description = "The resource ID of the account-level AI agent capability host."
  value       = var.ai_foundry.create_ai_agent_service && var.ai_foundry.network_injections == null ? azapi_resource.ai_agent_capability_host[0].id : null
}

output "ai_agent_service_id" {
  description = "The resource ID of the AI agent capability host."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].ai_agent_capability_host_id }
}

output "ai_foundry_encryption_status" {
  description = "The encryption configuration status of the AI Foundry account."
  value = var.ai_foundry.customer_managed_key != null ? {
    enabled              = true
    key_vault_uri        = data.azurerm_key_vault.cmk[0].vault_uri
    key_name             = var.ai_foundry.customer_managed_key.key_name
    key_version          = var.ai_foundry.customer_managed_key.key_version != null ? var.ai_foundry.customer_managed_key.key_version : data.azurerm_key_vault_key.cmk[0].version
    identity_resource_id = var.ai_foundry.customer_managed_key.user_assigned_identity_resource_id
  } : { enabled = false }
}

output "ai_foundry_id" {
  description = "The resource ID of the AI Foundry account."
  value       = azapi_resource.ai_foundry.id
}

output "ai_foundry_name" {
  description = "The name of the AI Foundry account."
  value       = azapi_resource.ai_foundry.name
}

output "ai_foundry_project_id" {
  description = "The resource ID of the AI Foundry Project."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].ai_foundry_project_id }
}

output "ai_foundry_project_internal_id" {
  description = "The internal ID of the AI Foundry project used for container naming."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].ai_foundry_project_internal_id }
}

output "ai_foundry_project_name" {
  description = "The name of the AI Foundry Project."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].ai_foundry_project_name }
}

output "ai_foundry_project_system_identity_principal_id" {
  description = "The principal ID of the AI Foundry project's system-assigned managed identity."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].ai_foundry_project_system_identity_principal_id }
}

output "ai_model_deployment_ids" {
  description = "The resource IDs of all AI model deployments."
  value       = { for k, v in azapi_resource.ai_model_deployment : k => v.id }
}

output "ai_search_id" {
  description = "The resource ID of the AI Search service."
  #value       = { for k, v in var.ai_search_definition : k => try(v.existing_resource_id, null) != null ? v.existing_resource_id : module.ai_search[k].resource_id }
  value = { for k, v in var.ai_search_definition : k => try(v.existing_resource_id, null) != null ? v.existing_resource_id : azapi_resource.ai_search[k].id }
}

output "ai_search_name" {
  description = "The name of the AI Search service."
  #value       = { for k, v in var.ai_search_definition : k => try(v.existing_resource_id, null) != null ? basename(v.existing_resource_id) : basename(module.ai_search[k].resource_id) }
  value = { for k, v in var.ai_search_definition : k => try(v.existing_resource_id, null) != null ? basename(v.existing_resource_id) : basename(azapi_resource.ai_search[k].id) }
}

output "cosmos_db_id" {
  description = "The resource ID of the Cosmos DB account."
  value       = { for k, v in var.cosmosdb_definition : k => try(v.existing_resource_id, null) != null ? v.existing_resource_id : module.cosmosdb[k].resource_id }
}

output "cosmos_db_name" {
  description = "The name of the Cosmos DB account."
  value       = { for k, v in var.cosmosdb_definition : k => try(v.existing_resource_id, null) != null ? basename(v.existing_resource_id) : basename(module.cosmosdb[k].resource_id) }
}

output "key_vault_id" {
  description = "The resource ID of the Key Vault."
  value       = { for k, v in var.key_vault_definition : k => try(v.existing_resource_id, null) != null ? v.existing_resource_id : module.key_vault[k].resource_id }
}

output "key_vault_name" {
  description = "The name of the Key Vault."
  value       = { for k, v in var.key_vault_definition : k => try(v.existing_resource_id, null) != null ? basename(v.existing_resource_id) : basename(module.key_vault[k].resource_id) }
}

output "project_id_guid" {
  description = "The project ID formatted as GUID for container naming (only available when AI agent service is enabled)."
  value       = { for project, value in var.ai_projects : project => module.ai_foundry_project[project].project_id_guid }
}

output "resource_group_id" {
  description = "The resource ID of the resource group."
  value       = var.resource_group_resource_id
}

output "resource_group_name" {
  description = "The name of the resource group."
  value       = local.resource_group_name
}

output "resource_id" {
  description = "The resource IDs of the AI Foundry resource."
  value       = azapi_resource.ai_foundry.id
}

output "storage_account_id" {
  description = "The resource ID of the storage account."
  value       = { for k, v in var.storage_account_definition : k => try(v.existing_resource_id, null) != null ? v.existing_resource_id : module.storage_account[k].resource_id }
}

output "storage_account_name" {
  description = "The name of the storage account."
  value       = { for k, v in var.storage_account_definition : k => try(v.existing_resource_id, null) != null ? basename(v.existing_resource_id) : basename(module.storage_account[k].resource_id) }
}
