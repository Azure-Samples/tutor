data "azurerm_client_config" "current" {}

resource "random_string" "resource_token" {
  length  = 5
  lower   = true
  numeric = true
  special = false
  upper   = false
}


module "ai_foundry_project" {
  source   = "./modules/ai-foundry-project"
  for_each = var.ai_projects

  ai_agent_host_name         = local.resource_names.ai_agent_host
  ai_foundry_id              = azapi_resource.ai_foundry.id
  description                = each.value.description
  display_name               = each.value.display_name
  location                   = local.location
  name                       = each.value.name
  account_capability_host_id = try(azapi_resource.ai_agent_capability_host[0].id, null)
  #ai_search_id               = try(coalesce(each.value.ai_search_connection.existing_resource_id, try(module.ai_search[each.value.ai_search_connection.new_resource_map_key].resource_id, null)), null)
  ai_search_id               = try(coalesce(each.value.ai_search_connection.existing_resource_id, try(azapi_resource.ai_search[each.value.ai_search_connection.new_resource_map_key].id, null)), null)
  cosmos_db_id               = try(coalesce(each.value.cosmos_db_connection.existing_resource_id, try(module.cosmosdb[each.value.cosmos_db_connection.new_resource_map_key].resource_id, null)), null)
  create_ai_agent_service    = var.ai_foundry.create_ai_agent_service
  create_project_connections = each.value.create_project_connections
  storage_account_id         = try(coalesce(each.value.storage_account_connection.existing_resource_id, try(module.storage_account[each.value.storage_account_connection.new_resource_map_key].resource_id, null)), null)
  tags                       = var.tags

  depends_on = [
    azapi_resource.ai_foundry,
    azapi_resource.ai_agent_capability_host,
    azurerm_private_endpoint.ai_foundry,
    azapi_resource.ai_search,
    azurerm_private_endpoint.pe_aisearch, #module.ai_search,
    module.cosmosdb,
    module.storage_account
  ]
}
