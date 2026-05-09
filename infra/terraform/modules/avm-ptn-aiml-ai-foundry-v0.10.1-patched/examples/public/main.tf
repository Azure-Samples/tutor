terraform {
  required_version = ">= 1.9, < 2.0"

  required_providers {
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
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
  }
}

locals {
  base_name = "public"
}

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
      }
      ai_search_connection = {
        new_resource_map_key = "this"
      }
      storage_account_connection = {
        new_resource_map_key = "this"
      }
    }
  }
  ai_search_definition = {
    this = {}
  }
  cosmosdb_definition = {
    this = {
      local_authentication_disabled = true
      diagnostic_settings = {
        to_law = {
          name                           = "diag-to-law"
          workspace_resource_id          = azurerm_log_analytics_workspace.this.id
          log_analytics_destination_type = "Dedicated"
          log_groups                     = ["allLogs"]
          metric_categories              = ["SLI", "Requests"]
        }
      }
    }
  }
  create_byor              = true
  create_private_endpoints = false # default: false
  key_vault_definition = {
    this = {
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
    this = {}
  }
  tags = {
    workload = "ai-foundry"
  }
}
