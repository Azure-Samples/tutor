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
    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

data "azurerm_client_config" "current" {}

locals {
  base_name = "pubcmk"
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

# User-Assigned Managed Identity for CMK
resource "azurerm_user_assigned_identity" "cmk" {
  location            = azurerm_resource_group.this.location
  name                = module.naming.user_assigned_identity.name_unique
  resource_group_name = azurerm_resource_group.this.name
}

# Key Vault for CMK
resource "azurerm_key_vault" "this" {
  location                   = azurerm_resource_group.this.location
  name                       = module.naming.key_vault.name_unique
  resource_group_name        = azurerm_resource_group.this.name
  sku_name                   = "standard"
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  enable_rbac_authorization  = true
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
}

# Grant current user Key Vault Administrator role
resource "azurerm_role_assignment" "kv_admin_current_user" {
  principal_id         = data.azurerm_client_config.current.object_id
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Administrator"
}

# Wait for RBAC propagation
resource "time_sleep" "rbac_wait" {
  create_duration = "60s"

  depends_on = [azurerm_role_assignment.kv_admin_current_user]
}

# Key Vault Key for encryption
resource "azurerm_key_vault_key" "cmk" {
  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
  key_type     = "RSA"
  key_vault_id = azurerm_key_vault.this.id
  name         = "cmk-key"
  key_size     = 2048

  depends_on = [time_sleep.rbac_wait]
}

# AI Foundry module with CMK encryption
module "ai_foundry" {
  source = "../../"

  base_name                  = local.base_name
  location                   = azurerm_resource_group.this.location
  resource_group_resource_id = azurerm_resource_group.this.id
  ai_foundry = {
    name                    = module.naming.cognitive_account.name_unique
    create_ai_agent_service = false
    customer_managed_key = {
      key_vault_resource_id              = azurerm_key_vault.this.id
      key_name                           = azurerm_key_vault_key.cmk.name
      key_version                        = null # Use latest version
      user_assigned_identity_resource_id = azurerm_user_assigned_identity.cmk.id
    }
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
      description                = "Project with CMK encryption"
      display_name               = "Project 1"
      create_project_connections = false
    }
  }
  create_byor              = false
  create_private_endpoints = false

  depends_on = [
    azurerm_key_vault_key.cmk
  ]
}
