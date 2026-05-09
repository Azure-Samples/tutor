resource "azapi_resource" "ai_foundry_project" {
  location  = var.location
  name      = var.name
  parent_id = var.ai_foundry_id
  type      = "Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview"
  body = {
    sku = {
      name = var.sku
    }
    identity = {
      type = "SystemAssigned"
    }
    properties = {
      displayName = var.display_name
      description = var.description
    }
  }
  response_export_values = [
    "identity.principalId",
    "properties.internalId"
  ]
  schema_validation_enabled = false
  tags                      = var.tags
}

locals {
  # Extract project internal ID and format as GUID for container naming
  project_id_guid = var.create_ai_agent_service ? "${substr(azapi_resource.ai_foundry_project.output.properties.internalId, 0, 8)}-${substr(azapi_resource.ai_foundry_project.output.properties.internalId, 8, 4)}-${substr(azapi_resource.ai_foundry_project.output.properties.internalId, 12, 4)}-${substr(azapi_resource.ai_foundry_project.output.properties.internalId, 16, 4)}-${substr(azapi_resource.ai_foundry_project.output.properties.internalId, 20, 12)}" : ""
}

resource "time_sleep" "wait_project_identities" {
  create_duration = "10s"

  depends_on = [azapi_resource.ai_foundry_project]
}

resource "azapi_resource" "connection_storage" {
  count = var.create_project_connections ? 1 : 0

  name      = basename(var.create_project_connections ? var.storage_account_id : "/n/o/t/u/s/e/d")
  parent_id = azapi_resource.ai_foundry_project.id
  type      = "Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview"
  body = {
    properties = {
      category = "AzureStorageAccount"
      target   = "https://${basename(var.create_project_connections ? var.storage_account_id : "/n/o/t/u/s/e/d")}.blob.core.windows.net/"
      authType = "AAD"
      metadata = {
        ApiType    = "Azure"
        ResourceId = var.storage_account_id
        location   = var.location
      }
    }
  }
  response_export_values = [
    "identity.principalId"
  ]
  schema_validation_enabled = false

  depends_on = [azapi_resource.connection_cosmos, azurerm_role_assignment.storage_role_assignments]
}

resource "azapi_resource" "connection_cosmos" {
  count = var.create_project_connections ? 1 : 0

  name      = basename(var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d")
  parent_id = azapi_resource.ai_foundry_project.id
  type      = "Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview"
  body = {
    properties = {
      category = "CosmosDb"
      target   = "https://${basename(var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d")}.documents.azure.com:443/"
      authType = "AAD"
      metadata = {
        ApiType    = "Azure"
        ResourceId = var.cosmos_db_id
        location   = var.location
      }
    }
  }
  response_export_values = [
    "identity.principalId"
  ]
  schema_validation_enabled = false

  depends_on = [azurerm_role_assignment.cosmosdb_role_assignments]
}

resource "azapi_resource" "connection_search" {
  count = var.create_project_connections ? 1 : 0

  name      = basename(var.create_project_connections ? var.ai_search_id : "/n/o/t/u/s/e/d")
  parent_id = azapi_resource.ai_foundry_project.id
  type      = "Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview"
  body = {
    properties = {
      category = "CognitiveSearch"
      target   = "https://${basename(var.create_project_connections ? var.ai_search_id : "/n/o/t/u/s/e/d")}.search.windows.net"
      authType = "AAD"
      metadata = {
        ApiType    = "Azure"
        ApiVersion = "2024-05-01-preview"
        ResourceId = var.ai_search_id
        location   = var.location
      }
    }
  }
  schema_validation_enabled = false

  depends_on = [azurerm_role_assignment.ai_search_role_assignments,
    azapi_resource.connection_cosmos,
  azapi_resource.connection_storage]

  lifecycle {
    ignore_changes = [name]
  }
}

#TODO: do we need to add support for Key Vault connections?
resource "azapi_resource" "ai_agent_capability_host" {
  count = var.create_ai_agent_service && var.create_project_connections ? 1 : 0

  name      = var.ai_agent_host_name
  parent_id = azapi_resource.ai_foundry_project.id
  type      = "Microsoft.CognitiveServices/accounts/projects/capabilityHosts@2025-04-01-preview"
  body = {
    properties = {
      capabilityHostKind = "Agents"
      vectorStoreConnections = var.ai_search_id != null ? [
        azapi_resource.connection_search[0].name
      ] : []
      storageConnections = var.storage_account_id != null ? [
        azapi_resource.connection_storage[0].name
      ] : []
      threadStorageConnections = var.cosmos_db_id != null ? [
        azapi_resource.connection_cosmos[0].name
      ] : []
    }
  }
  schema_validation_enabled = false

  depends_on = [
    azapi_resource.connection_storage,
    azapi_resource.connection_cosmos,
    azapi_resource.connection_search,
    time_sleep.wait_rbac_before_capability_host,
    var.account_capability_host_id
  ]
}

resource "time_sleep" "wait_rbac_before_capability_host" {
  create_duration = "60s"

  depends_on = [
    azapi_resource.ai_foundry_project,
    azapi_resource.connection_storage,
    azapi_resource.connection_cosmos,
    azapi_resource.connection_search,
    azurerm_role_assignment.ai_search_role_assignments,
    azurerm_role_assignment.cosmosdb_role_assignments,
    azurerm_role_assignment.storage_role_assignments,
    time_sleep.wait_project_identities
  ]
}

