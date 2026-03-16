locals {
  normalized_prefix              = lower(replace("${var.name_prefix}${var.environment}", "-", ""))
  container_app_environment_name = "${var.name_prefix}-${var.environment}-acae"
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

  # Computed names for resources managed by downstream stacks.
  # Using deterministic naming avoids data source lookups that fail on ground-zero.
  cosmos_account_name = "${local.normalized_prefix}${random_string.suffix.result}cosmos"
  cosmos_endpoint     = "https://${local.cosmos_account_name}.documents.azure.com:443/"
  apim_name           = "${var.name_prefix}-${var.environment}-apim"
  apim_gateway_url    = "https://${local.apim_name}.azure-api.net"
  ai_services_name    = "${local.normalized_prefix}${random_string.suffix.result}ai"
}

data "azurerm_client_config" "current" {}

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

resource "azurerm_virtual_network" "aca" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                = "${var.name_prefix}-${var.environment}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.aca_vnet_address_space
}

resource "azurerm_subnet" "aca_infrastructure" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                 = "aca-infrastructure"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.aca[0].name
  address_prefixes     = [var.aca_infrastructure_subnet_cidr]

  delegation {
    name = "aca-environment"

    service_delegation {
      name = "Microsoft.App/environments"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_subnet" "cosmos_private_endpoint" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                              = "cosmos-private-endpoint"
  resource_group_name               = azurerm_resource_group.main.name
  virtual_network_name              = azurerm_virtual_network.aca[0].name
  address_prefixes                  = [var.cosmos_private_endpoint_subnet_cidr]
  private_endpoint_network_policies = "Disabled"
}

resource "azurerm_private_dns_zone" "cosmos" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                = var.cosmos_private_dns_zone_name
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "cosmos" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                  = "${var.name_prefix}-${var.environment}-cosmos-dns-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.cosmos[0].name
  virtual_network_id    = azurerm_virtual_network.aca[0].id
}

# One-time migration: moves the indexed resource to a non-indexed address.
# After first successful apply, remove this moved block and the data source below.
moved {
  from = azurerm_container_app_environment.main[0]
  to   = azurerm_container_app_environment.main
}

resource "azurerm_container_app_environment" "main" {
  name                       = local.container_app_environment_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id   = var.aca_vnet_integration_enabled ? azurerm_subnet.aca_infrastructure[0].id : null

  lifecycle {
    prevent_destroy = true

    ignore_changes = [
      infrastructure_subnet_id,
      infrastructure_resource_group_name,
    ]
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

# ── Cosmos DB (moved to stacks/data-ai/ per ADR-013) ────────────────────────
# Resources are now managed by infra/terraform/stacks/data-ai/.
# The removed blocks below prevent Terraform from destroying existing resources
# when they are migrated out of this state file.

removed {
  from = azurerm_cosmosdb_account.main
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_private_endpoint.cosmos
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_cosmosdb_sql_database.main
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_cosmosdb_sql_container.containers
  lifecycle {
    destroy = false
  }
}

# Cosmos DB values are computed from deterministic naming (no data source lookup).
# This enables ground-zero deployments where the Cosmos account doesn't exist yet.

# ── Backend Container Apps (moved to stacks/aca-apps/ per ADR-013) ──────────
# Resources are now managed by infra/terraform/stacks/aca-apps/.
# The removed blocks below prevent Terraform from destroying existing apps
# when they are migrated out of this state file.

removed {
  from = azurerm_container_app.backend_services
  lifecycle {
    destroy = false
  }
}

# ACA app values are computed from deterministic naming (no data source lookup).
# This enables ground-zero deployments where the apps don't exist yet.

# ── APIM (moved to stacks/gateway-rbac/ per ADR-013) ───────────────────────
# Resources are now managed by infra/terraform/stacks/gateway-rbac/.

removed {
  from = azurerm_api_management.main
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_api_management_api.backend_services
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_api_management_api_operation.backend_catch_all
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_api_management_api_policy.backend_services_hardening
  lifecycle {
    destroy = false
  }
}

# APIM values are computed from deterministic naming (no data source lookup).
# This enables ground-zero deployments where APIM doesn't exist yet.

# ── RBAC (moved to stacks/gateway-rbac/ per ADR-013) ───────────────────────

# AcrPull role assignments moved to stacks/aca-apps/ per ADR-013.
removed {
  from = azurerm_role_assignment.container_app_acr_pull
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_role_assignment.container_app_cognitive_services
  lifecycle {
    destroy = false
  }
}

removed {
  from = azurerm_role_assignment.agent_permissions
  lifecycle {
    destroy = false
  }
}

# ── AI Foundry (moved to stacks/data-ai/ per ADR-013) ──────────────────────

removed {
  from = module.ai_foundry
  lifecycle {
    destroy = false
  }
}

# AI Services values are computed from deterministic naming (no data source lookup).
# This enables ground-zero deployments where the AI Services account doesn't exist yet.

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

