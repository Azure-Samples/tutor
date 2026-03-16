# ── Cosmos DB ────────────────────────────────────────────────────────────────

resource "azurerm_cosmosdb_account" "main" {
  name                          = "${var.normalized_prefix}${var.random_suffix}cosmos"
  location                      = var.location
  resource_group_name           = var.resource_group_name
  offer_type                    = "Standard"
  kind                          = "GlobalDocumentDB"
  public_network_access_enabled = var.cosmos_public_network_access_enabled
  ip_range_filter               = toset(var.cosmos_allowed_public_ip_ranges)

  lifecycle {
    precondition {
      condition = !(
        var.cosmos_public_network_access_enabled == false
        && var.aca_vnet_integration_enabled == false
      )
      error_message = "Blocked: Cosmos public network access cannot be disabled while ACA has no VNet/private path."
    }

    precondition {
      condition = !(
        var.cosmos_public_network_access_enabled == false
        && var.cosmos_lockout_acknowledged == false
      )
      error_message = "Blocked: set cosmos_lockout_acknowledged=true to confirm intentional private-only Cosmos rollout."
    }
  }

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }
}

resource "azurerm_private_endpoint" "cosmos" {
  count = var.aca_vnet_integration_enabled ? 1 : 0

  name                = "${var.name_prefix}-${var.environment}-cosmos-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.cosmos_pe_subnet_id

  private_service_connection {
    name                           = "${var.name_prefix}-${var.environment}-cosmos-psc"
    private_connection_resource_id = azurerm_cosmosdb_account.main.id
    subresource_names              = ["Sql"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "cosmos-private-dns"
    private_dns_zone_ids = var.cosmos_dns_zone_ids
  }
}

resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.cosmos_db_name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = var.cosmos_containers

  name                  = each.key
  resource_group_name   = var.resource_group_name
  account_name          = azurerm_cosmosdb_account.main.name
  database_name         = azurerm_cosmosdb_sql_database.main.name
  partition_key_paths   = [each.value.partition_key_path]
  partition_key_version = 2
}

# ── Azure AI Foundry (ADR-011 → ADR-012: AVM module, public endpoint) ──────

module "ai_foundry" {
  source  = "Azure/avm-ptn-aiml-ai-foundry/azurerm"
  version = "0.10.0"

  base_name                  = substr("${var.normalized_prefix}${var.random_suffix}", 0, 9)
  location                   = var.foundry_location
  resource_group_resource_id = var.resource_group_id

  ai_foundry = {
    name                    = "${var.normalized_prefix}${var.random_suffix}ai"
    create_ai_agent_service = false
    disable_local_auth      = false
  }

  ai_model_deployments = {
    "gpt-5-nano" = {
      name = var.model_deployment_name
      model = {
        format  = "OpenAI"
        name    = "gpt-5-nano"
        version = "2025-08-07"
      }
      scale = {
        type     = "GlobalStandard"
        capacity = 1
      }
    }
    "gpt-5" = {
      name = var.model_reasoning_deployment
      model = {
        format  = "OpenAI"
        name    = "gpt-5"
        version = "2025-08-07"
      }
      scale = {
        type     = "GlobalStandard"
        capacity = 1
      }
    }
  }

  ai_projects = {
    tutor = {
      name                       = "${var.name_prefix}-${var.environment}-ai-project"
      display_name               = "Tutor AI Project"
      description                = "Tutor platform AI project (${var.environment})"
      create_project_connections = false

      cosmos_db_connection = {
        existing_resource_id = azurerm_cosmosdb_account.main.id
      }

      storage_account_connection = {
        existing_resource_id = var.storage_account_id
      }
    }
  }

  create_byor              = false
  create_private_endpoints = false
  enable_telemetry         = false
}
