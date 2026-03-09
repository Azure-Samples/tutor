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
  apim_required_services = [
    "avatar",
    "configuration",
    "essays",
    "questions",
    "upskilling",
    "chat",
    "evaluation",
    "lms-gateway",
  ]
  apim_service_paths = {
    for service_name in local.apim_required_services :
    service_name => "api/${service_name}"
  }
  apim_operation_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
  apim_operations = {
    for operation in flatten([
      for service_name, _ in local.apim_service_paths : [
        for method in local.apim_operation_methods : {
          key          = "${service_name}-${lower(method)}"
          service_name = service_name
          method       = method
        }
      ]
    ]) : operation.key => operation
  }
  apim_allowed_origins = distinct(compact(concat(
    [
      "https://${azurerm_static_web_app.frontend.default_host_name}",
      "http://localhost:3000",
      "http://localhost:5173",
    ],
    var.apim_additional_allowed_origins,
  )))
  agent_role_scopes = {
    "Cosmos DB Built-in Data Contributor" = azurerm_cosmosdb_account.main.id
    "Storage Blob Data Contributor"       = azurerm_storage_account.uploads.id
    "AcrPull"                             = azurerm_container_registry.main.id
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

      liveness_probe {
        path      = "/health"
        port      = 8000
        transport = "HTTP"
      }

      readiness_probe {
        path      = "/ready"
        port      = 8000
        transport = "HTTP"
      }
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

resource "azurerm_api_management" "main" {
  name                = "${var.name_prefix}-${var.environment}-apim"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "Tutor Platform"
  publisher_email     = "platform@contoso.com"
  sku_name            = "Consumption_0"

  tags = {
    "azd-env-name" = var.environment
  }
}

resource "azurerm_api_management_api" "backend_services" {
  for_each = local.apim_service_paths

  name                  = "${replace(each.key, "-", "")}-api"
  resource_group_name   = azurerm_resource_group.main.name
  api_management_name   = azurerm_api_management.main.name
  revision              = "1"
  display_name          = "${each.key} API"
  path                  = each.value
  protocols             = ["https"]
  service_url           = "https://${azurerm_container_app.backend_services[each.key].latest_revision_fqdn}"
  subscription_required = false
}

resource "azurerm_api_management_api_operation" "backend_catch_all" {
  for_each = local.apim_operations

  operation_id        = replace(each.key, "-", "")
  api_name            = azurerm_api_management_api.backend_services[each.value.service_name].name
  api_management_name = azurerm_api_management.main.name
  resource_group_name = azurerm_resource_group.main.name
  display_name        = "${each.value.method} catch-all"
  method              = each.value.method
  url_template        = "/{*path}"

  template_parameter {
    name     = "path"
    required = true
    type     = "string"
  }

  response {
    status_code = 200
  }
}

resource "azurerm_api_management_api_policy" "backend_services_hardening" {
  for_each = azurerm_api_management_api.backend_services

  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  api_name            = each.value.name

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <cors allow-credentials="false">
          <allowed-origins>
${join("\n", [for origin in local.apim_allowed_origins : "            <origin>${origin}</origin>"])}
          </allowed-origins>
          <allowed-methods preflight-result-max-age="300">
            <method>*</method>
          </allowed-methods>
          <allowed-headers>
            <header>*</header>
          </allowed-headers>
          <expose-headers>
            <header>*</header>
          </expose-headers>
        </cors>
        <rate-limit-by-key calls="${var.apim_rate_limit_calls}" renewal-period="${var.apim_rate_limit_renewal_period_seconds}" counter-key="@(context.Request.IpAddress)" />
      </inbound>
      <backend>
        <base />
      </backend>
      <outbound>
        <base />
      </outbound>
      <on-error>
        <base />
      </on-error>
    </policies>
  XML
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
