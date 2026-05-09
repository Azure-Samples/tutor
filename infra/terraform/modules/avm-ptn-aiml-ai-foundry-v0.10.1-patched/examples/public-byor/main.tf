terraform {
  required_version = ">= 1.9, < 2.0"

  required_providers {
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "azurerm" {
  storage_use_azuread = true
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

locals {
  base_name = "pubbyor"
}

data "azurerm_client_config" "current" {}

module "regions" {
  source  = "Azure/avm-utl-regions/azurerm"
  version = "0.5.2"

  availability_zones_filter = true
  geography_filter          = "Australia"
}

resource "random_shuffle" "locations" {
  input        = module.regions.valid_region_names
  result_count = 3
}

module "naming" {
  source  = "Azure/naming/azurerm"
  version = "0.4.2"

  suffix        = [local.base_name]
  unique-length = 5
}

resource "azurerm_resource_group" "this" {
  location = random_shuffle.locations.result[0]
  name     = module.naming.resource_group.name_unique
}

resource "azurerm_log_analytics_workspace" "this" {
  location            = azurerm_resource_group.this.location
  name                = module.naming.log_analytics_workspace.name_unique
  resource_group_name = azurerm_resource_group.this.name
  retention_in_days   = 30
  sku                 = "PerGB2018"
}

# BYOR

resource "azapi_resource" "ai_search" {
  location  = azurerm_resource_group.this.location
  name      = module.naming.search_service.name_unique
  parent_id = azurerm_resource_group.this.id
  type      = "Microsoft.Search/searchServices@2024-06-01-preview"
  body = {
    sku = {
      name = "standard"
    }

    identity = {
      type = "SystemAssigned"
    }

    properties = {

      # Search-specific properties
      replicaCount   = 2
      partitionCount = 1
      hostingMode    = "default"
      semanticSearch = "disabled"

      # Identity-related controls
      disableLocalAuth = false
      authOptions = {
        aadOrApiKey = {
          aadAuthFailureMode = "http401WithBearerChallenge"
        }
      }
      # Networking-related controls
      publicNetworkAccess = "Enabled"
      networkRuleSet = {
        bypass = "None"
      }
    }
  }
  schema_validation_enabled = true
}

module "key_vault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.10.2"

  location                        = azurerm_resource_group.this.location
  name                            = module.naming.key_vault.name_unique
  resource_group_name             = azurerm_resource_group.this.name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  network_acls = {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
}

module "storage_account" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "0.6.7"

  location                 = azurerm_resource_group.this.location
  name                     = module.naming.storage_account.name_unique
  resource_group_name      = azurerm_resource_group.this.name
  access_tier              = "Hot"
  account_kind             = "StorageV2"
  account_replication_type = "ZRS"
  account_tier             = "Standard"
}

module "cosmosdb" {
  source  = "Azure/avm-res-documentdb-databaseaccount/azurerm"
  version = "0.10.0"

  location                   = azurerm_resource_group.this.location
  name                       = module.naming.cosmosdb_account.name_unique
  resource_group_name        = azurerm_resource_group.this.name
  analytical_storage_enabled = true
  automatic_failover_enabled = true
  capacity = {
    total_throughput_limit = -1
  }
  consistency_policy = {
    consistency_level       = "Session"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100001
  }
  ip_range_filter = [
    "168.125.123.255",
    "170.0.0.0/24",                                                                 #TODO: check 0.0.0.0 for validity
    "0.0.0.0",                                                                      #Accept connections from within public Azure datacenters. https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-firewall#allow-requests-from-the-azure-portal
    "104.42.195.92", "40.76.54.131", "52.176.6.30", "52.169.50.45", "52.187.184.26" #Allow access from the Azure portal. https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-firewall#allow-requests-from-global-azure-datacenters-or-other-sources-within-azure
  ]
  local_authentication_disabled         = true
  multiple_write_locations_enabled      = false
  network_acl_bypass_for_azure_services = true
  partition_merge_enabled               = false
  public_network_access_enabled         = true
}

module "ai_foundry" {
  source = "../../"

  base_name                  = local.base_name
  location                   = azurerm_resource_group.this.location
  resource_group_resource_id = azurerm_resource_group.this.id
  ai_foundry = {
    create_ai_agent_service = true
    name                    = module.naming.cognitive_account.name_unique
  }
  ai_model_deployments = {
    "gpt-4o" = {
      name = "gpt-4.1"
      model = {
        format  = "OpenAI"
        name    = "gpt-4.1"
        version = "2025-04-14"
      }
      scale = {
        type     = "GlobalStandard"
        capacity = 1
      }
    }
  }
  ai_projects = {
    project_1 = {
      name                       = "project-1"
      description                = "Project 1 description"
      display_name               = "Project 1 Display Name"
      create_project_connections = true
      cosmos_db_connection = {
        new_resource_map_key = "this"
        existing_resource_id = module.cosmosdb.resource_id
      }
      ai_search_connection = {
        new_resource_map_key = "this"
        existing_resource_id = azapi_resource.ai_search.id
      }
      storage_account_connection = {
        new_resource_map_key = "this"
        existing_resource_id = module.storage_account.resource_id
      }
    }
  }
  ai_search_definition = {
    this = {
      existing_resource_id = azapi_resource.ai_search.id
    }
  }
  cosmosdb_definition = {
    this = {
      existing_resource_id = module.cosmosdb.resource_id
      diagnostic_settings = {
        to_law = {
          name                           = "diag-to-law"
          workspace_resource_id          = azurerm_log_analytics_workspace.this.id
          log_analytics_destination_type = "Dedicated"
          log_groups                     = ["allLogs"]
          metric_categories              = ["AllMetrics"]
        }
      }
    }
  }
  create_byor              = false # default: false
  create_private_endpoints = false # default: false
  key_vault_definition = {
    this = {
      existing_resource_id = module.key_vault.resource_id
      diagnostic_settings = {
        to_law = {
          name                           = "diag-to-law"
          workspace_resource_id          = azurerm_log_analytics_workspace.this.id
          log_analytics_destination_type = "Dedicated"
          log_groups                     = ["allLogs"]
          metric_categories              = ["AllMetrics"]
        }
      }
    }
  }
  storage_account_definition = {
    this = {
      existing_resource_id = module.storage_account.resource_id
      diagnostic_settings_storage_account = {
        to_law = {
          name                  = "diag-to-law"
          workspace_resource_id = azurerm_log_analytics_workspace.this.id
          metric_categories     = ["AllMetrics"]
        }
      }
    }
  }
  tags = {
    workload = "ai-foundry"
  }
}
