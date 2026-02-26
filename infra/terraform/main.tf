locals {
  normalized_prefix = lower(replace("${var.name_prefix}${var.environment}", "-", ""))
  backend_service_names = [
    "avatar",
    "configuration",
    "essays",
    "questions",
    "upskilling",
    "chat",
    "evaluation",
    "lms-gateway",
  ]
  agent_role_scopes = {
    "Cosmos DB Built-in Data Contributor" = azurerm_cosmosdb_account.main.id
    "Storage Blob Data Contributor"        = azurerm_storage_account.uploads.id
    "AcrPull"                              = azurerm_container_registry.main.id
  }

  agent_role_assignments = {
    for pair in setproduct(var.agent_principal_object_ids, keys(local.agent_role_scopes)) :
    "${pair[0]}-${replace(lower(pair[1]), " ", "-")}" => {
      principal_id = pair[0]
      role_name    = pair[1]
      scope        = local.agent_role_scopes[pair[1]]
    }
  }
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_resource_group" "main" {
  name     = "${var.name_prefix}-${var.environment}"
  location = var.location
  tags = {
    "azd-env-name" = var.environment
  }
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.name_prefix}-${var.environment}-log"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "main" {
  name                = "${var.name_prefix}-${var.environment}-appi"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
}

resource "azurerm_container_app_environment" "main" {
  name                       = "${var.name_prefix}-${var.environment}-acae"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags = {
    "azd-env-name" = var.environment
  }
}

resource "azurerm_container_registry" "main" {
  name                = "${local.normalized_prefix}${random_string.suffix.result}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_storage_account" "uploads" {
  name                     = "${local.normalized_prefix}${random_string.suffix.result}sa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

resource "azurerm_storage_container" "uploads" {
  name                  = "uploads"
  storage_account_id    = azurerm_storage_account.uploads.id
  container_access_type = "private"
}

resource "azurerm_cosmosdb_account" "main" {
  name                = "${local.normalized_prefix}${random_string.suffix.result}cosmos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }
}

resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.cosmos_db_name
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = var.cosmos_containers

  name                  = each.key
  resource_group_name   = azurerm_resource_group.main.name
  account_name          = azurerm_cosmosdb_account.main.name
  database_name         = azurerm_cosmosdb_sql_database.main.name
  partition_key_paths   = [each.value.partition_key_path]
  partition_key_version = 2
}

resource "azurerm_container_app" "backend_services" {
  for_each = toset(local.backend_service_names)

  name                         = "${var.name_prefix}-${each.key}-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = "system"
  }

  template {
    container {
      name   = each.key
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = {
    "azd-env-name"     = var.environment
    "azd-service-name" = each.key
  }
}

resource "azurerm_role_assignment" "container_app_acr_pull" {
  for_each             = azurerm_container_app.backend_services
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = each.value.identity[0].principal_id
}

resource "azurerm_static_web_app" "frontend" {
  name                = "${var.name_prefix}-${var.environment}-frontend"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = {
    "azd-env-name"     = var.environment
    "azd-service-name" = "frontend"
  }
}

resource "azurerm_role_assignment" "agent_permissions" {
  for_each             = local.agent_role_assignments
  scope                = each.value.scope
  role_definition_name = each.value.role_name
  principal_id         = each.value.principal_id
}
