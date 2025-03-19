terraform {
  required_version = ">= 1.3.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5.0, < 4.0.0"
    }
  }
}

variable "subscription_id" {
  description = "The Azure subscription ID to use for the provider."
  type        = string
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
  subscription_id = var.subscription_id
}

module "naming" {
  source  = "Azure/naming/azurerm"
  version = ">= 0.3.0"
}

#####################################################
# RESOURCE GROUP
#####################################################
resource "azurerm_resource_group" "llm_as_judge" {
  name     = "the-tutor"
  location = "East US"
}

#####################################################
# RANDOM SUFFIX FOR UNIQUE NAMES
#####################################################
resource "random_string" "suffix" {
  length  = 5
  numeric = false
  special = false
  upper   = false
}

#####################################################
# CONTAINER REGISTRY
#####################################################
resource "azurerm_container_registry" "acr" {
  name                = "tutor-registry-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
  sku                 = "Basic"
  admin_enabled       = true
}

#####################################################
# COSMOS DB ACCOUNT
#####################################################
resource "azurerm_cosmosdb_account" "cosmosdb" {
  name                = "tutor-databases-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  consistency_policy {
    consistency_level = "Session"
  }
  geo_location {
    location          = azurerm_resource_group.llm_as_judge.location
    failover_priority = 0
  }
  capabilities {
    name = "EnableServerless"
  }
  network_acl_bypass_for_azure_services = false
}

#####################################################
# STORAGE ACCOUNT
#####################################################
resource "azurerm_storage_account" "storage" {
  name                     = "tutorfiles"  # Ensure this name is globally unique
  resource_group_name      = azurerm_resource_group.llm_as_judge.name
  location                 = azurerm_resource_group.llm_as_judge.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

#####################################################
# COGNITIVE ACCOUNTS
#####################################################
resource "azurerm_cognitive_account" "openai" {
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
  name                = "tutor-openai-${random_string.suffix.result}"
  kind                = "OpenAI"
  sku_name            = "S0"
}

resource "azurerm_cognitive_account" "speech" {
  name                = "tutor-speech-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
  kind                = "SpeechServices"
  sku_name            = "S1"
}

resource "azurerm_cognitive_account" "vision" {
  name                = "tutor-vision-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
  kind                = "ComputerVision"
  sku_name            = "S1"
}

#####################################################
# CONTAINER APP ENVIRONMENT
#####################################################
resource "azurerm_container_app_environment" "env" {
  name                = "tutor-apps-environment-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.llm_as_judge.name
  location            = azurerm_resource_group.llm_as_judge.location
}

#####################################################
# CONTAINER APP WITH SYSTEM-MANAGED IDENTITY
#####################################################
resource "azurerm_container_app" "app" {
  name                         = "tutor-apps-${random_string.suffix.result}"
  resource_group_name          = azurerm_resource_group.llm_as_judge.name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  template {
    container {
      name   = "judge-container"
      image  = "${azurerm_container_registry.acr.login_server}/judge-container:latest"
      cpu    = "0.5"
      memory = "1.0Gi"

      env {
        name  = "BLOB_CONNECTION_STRING"
        value = "BlobEndpoint=${azurerm_storage_account.storage.primary_blob_endpoint};QueueEndpoint=https://${azurerm_storage_account.storage.name}.queue.core.windows.net/;FileEndpoint=https://${azurerm_storage_account.storage.name}.file.core.windows.net/;TableEndpoint=https://${azurerm_storage_account.storage.name}.table.core.windows.net/;SharedAccessSignature=${azurerm_storage_account.storage.primary_access_key}"
      }
      env {
        name  = "COSMOS_ENDPOINT"
        value = azurerm_cosmosdb_account.cosmosdb.endpoint
      }
      env {
        name  = "COSMOS_KEY"
        value = azurerm_cosmosdb_account.cosmosdb.primary_key
      }
      env {
        name  = "GPT4_KEY"
        value = azurerm_cognitive_account.openai.primary_access_key
      }
      env {
        name  = "GPT4_URL"
        value = azurerm_cognitive_account.openai.endpoint
      }
      env {
        name  = "AI_SPEECH_URL"
        value = azurerm_cognitive_account.speech.endpoint
      }
      env {
        name  = "AI_SPEECH_KEY"
        value = azurerm_cognitive_account.speech.primary_access_key
      }
      env {
        name  = "AI_VISION_URL"
        value = azurerm_cognitive_account.vision.endpoint
      }
      env {
        name  = "AI_VISION_KEY"
        value = azurerm_cognitive_account.vision.primary_access_key
      }
    }
  }
}

#####################################################
# LOCAL EXEC PROVISIONER: UPLOAD IMAGE
#####################################################
resource "null_resource" "upload_image" {
  provisioner "local-exec" {
    command = "powershell.exe -ExecutionPolicy Bypass -File \"${path.module}/configuration/conf-image.ps1\" -gitRepositoryAddress \"${path.module}\" -imageRepositoryName \"${azurerm_container_registry.acr.name}\" -imageName \"judge-container\""
  }
  depends_on = [azurerm_container_registry.acr]
}

#####################################################
# ROLE ASSIGNMENTS FOR CONTAINER APP IDENTITY
#####################################################

# Cosmos DB: Grant the container app identity the Cosmos DB Built-in Data Contributor role
resource "azurerm_role_assignment" "cosmosdb_data_contributor" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "Cosmos DB Built-in Data Contributor"
  principal_id         = azurerm_container_app.app.identity.principal_id
}

# Blob Storage: Grant the container app identity the Storage Blob Data Contributor role
resource "azurerm_role_assignment" "storage_blob_data_contributor" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_container_app.app.identity.principal_id
}

# Cognitive Services (OpenAI): Grant the container app identity the Cognitive Services User role
resource "azurerm_role_assignment" "cognitive_openai_user" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_container_app.app.identity.principal_id
}

# Cognitive Services (Speech): Grant the container app identity the Cognitive Services User role
resource "azurerm_role_assignment" "cognitive_speech_user" {
  scope                = azurerm_cognitive_account.speech.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_container_app.app.identity.principal_id
}

# Cognitive Services (Vision): Grant the container app identity the Cognitive Services User role
resource "azurerm_role_assignment" "cognitive_vision_user" {
  scope                = azurerm_cognitive_account.vision.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_container_app.app.identity.principal_id
}
