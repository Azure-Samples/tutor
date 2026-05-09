locals {
  ai_search_default_role_assignments = {
    search_index_data_contributor = {
      name                       = "${var.name}-search-index-data-contributor"
      role_definition_id_or_name = "Search Index Data Contributor"
    }
    search_service_contributor = {
      name                       = "${var.name}-search-service-contributor"
      role_definition_id_or_name = "Search Service Contributor"
    }
  }
  cosmosdb_default_role_assignments = {
    cosmosdb_operator = {
      name                       = "${var.name}-cosmosdb-operator"
      role_definition_id_or_name = "Cosmos DB Operator"
    }
  }
  storage_account_default_role_assignments = {
    storage_blob_data_contributor = {
      name                       = "${var.name}-storage-blob-data-contributor"
      role_definition_id_or_name = "Storage Blob Data Contributor"
    }
  }
}

resource "azurerm_role_assignment" "ai_search_role_assignments" {
  for_each = var.create_project_connections ? local.ai_search_default_role_assignments : {}

  principal_id   = azapi_resource.ai_foundry_project.output.identity.principalId
  scope          = var.create_project_connections ? var.ai_search_id : "/n/o/t/u/s/e/d"
  principal_type = "ServicePrincipal"
  #name                 = each.key
  role_definition_name = each.value.role_definition_id_or_name

  depends_on = [time_sleep.wait_project_identities]
}

resource "azurerm_role_assignment" "cosmosdb_role_assignments" {
  for_each = var.create_project_connections ? local.cosmosdb_default_role_assignments : {}

  principal_id   = azapi_resource.ai_foundry_project.output.identity.principalId
  scope          = var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d"
  principal_type = "ServicePrincipal"
  #name                 = each.key
  role_definition_name = each.value.role_definition_id_or_name

  depends_on = [time_sleep.wait_project_identities]
}


resource "azurerm_role_assignment" "storage_role_assignments" {
  for_each = var.create_project_connections ? local.storage_account_default_role_assignments : {}

  principal_id   = azapi_resource.ai_foundry_project.output.identity.principalId
  scope          = var.create_project_connections ? var.storage_account_id : "/n/o/t/u/s/e/d"
  principal_type = "ServicePrincipal"
  #name                 = each.key
  role_definition_name = each.value.role_definition_id_or_name

  depends_on = [time_sleep.wait_project_identities]
}


# Control-plane role assignments are handled in the main module to avoid dependency issues - causes cycle errors if done externally.  Move here.
# Data Plane Role Assignments for Cosmos DB containers created by AI Foundry Project
resource "azurerm_cosmosdb_sql_role_assignment" "thread_message_store" {
  count = var.create_ai_agent_service && var.create_project_connections ? 1 : 0

  account_name        = basename(var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d")
  principal_id        = azapi_resource.ai_foundry_project.output.identity.principalId
  resource_group_name = split("/", var.cosmos_db_id)[4]
  role_definition_id  = "${var.cosmos_db_id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  scope               = "${var.cosmos_db_id}/dbs/enterprise_memory/colls/${local.project_id_guid}-thread-message-store"
  name                = uuidv5("dns", "${azapi_resource.ai_foundry_project.name}${azapi_resource.ai_foundry_project.output.identity.principalId}userthreadmessage_dbsqlrole")

  depends_on = [
    azapi_resource.ai_agent_capability_host
  ]
}

resource "azurerm_cosmosdb_sql_role_assignment" "system_thread_message_store" {
  count = var.create_ai_agent_service && var.create_project_connections ? 1 : 0

  account_name        = basename(var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d")
  principal_id        = azapi_resource.ai_foundry_project.output.identity.principalId
  resource_group_name = split("/", var.cosmos_db_id)[4]
  role_definition_id  = "${var.cosmos_db_id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  scope               = "${var.cosmos_db_id}/dbs/enterprise_memory/colls/${local.project_id_guid}-system-thread-message-store"
  name                = uuidv5("dns", "${azapi_resource.ai_foundry_project.name}${azapi_resource.ai_foundry_project.output.identity.principalId}systemthread_dbsqlrole")

  depends_on = [
    azurerm_cosmosdb_sql_role_assignment.thread_message_store,
    azapi_resource.ai_agent_capability_host
  ]
}

resource "azurerm_cosmosdb_sql_role_assignment" "agent_entity_store" {
  count = var.create_ai_agent_service && var.create_project_connections ? 1 : 0

  account_name        = basename(var.create_project_connections ? var.cosmos_db_id : "/n/o/t/u/s/e/d")
  principal_id        = azapi_resource.ai_foundry_project.output.identity.principalId
  resource_group_name = split("/", var.cosmos_db_id)[4]
  role_definition_id  = "${var.cosmos_db_id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  scope               = "${var.cosmos_db_id}/dbs/enterprise_memory/colls/${local.project_id_guid}-agent-entity-store"
  name                = uuidv5("dns", "${azapi_resource.ai_foundry_project.name}${azapi_resource.ai_foundry_project.output.identity.principalId}entitystore_dbsqlrole")

  depends_on = [
    azurerm_cosmosdb_sql_role_assignment.system_thread_message_store,
    azapi_resource.ai_agent_capability_host
  ]
}

# Advanced Storage Blob Data Owner assignment with ABAC conditions
resource "azurerm_role_assignment" "storage_blob_data_owner" {
  count = var.create_ai_agent_service && var.create_project_connections ? 1 : 0

  principal_id         = azapi_resource.ai_foundry_project.output.identity.principalId
  scope                = var.storage_account_id
  condition            = <<-EOT
  (
    (
      !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})
      AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'})
      AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'})
    )
    OR
    (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringStartsWithIgnoreCase '${local.project_id_guid}'
    AND @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent')
  )
  EOT
  condition_version    = "2.0"
  name                 = uuidv5("dns", "${azapi_resource.ai_foundry_project.name}${azapi_resource.ai_foundry_project.output.identity.principalId}${basename(var.create_project_connections ? var.storage_account_id : "/n/o/t/u/s/e/d")}storageblobdataowner")
  principal_type       = "ServicePrincipal"
  role_definition_name = "Storage Blob Data Owner"

  depends_on = [
    azapi_resource.ai_agent_capability_host
  ]
}
