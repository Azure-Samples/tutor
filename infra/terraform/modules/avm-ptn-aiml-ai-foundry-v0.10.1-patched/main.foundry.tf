resource "azapi_resource" "ai_foundry" {
  location  = var.location
  name      = local.ai_foundry_name
  parent_id = var.resource_group_resource_id
  type      = "Microsoft.CognitiveServices/accounts@${var.cognitive_services_api_version}"
  body = {

    kind = "AIServices",
    sku = {
      name = var.ai_foundry.sku
    }
    identity = {
      type = var.ai_foundry.customer_managed_key != null ? "SystemAssigned, UserAssigned" : "SystemAssigned"
      userAssignedIdentities = var.ai_foundry.customer_managed_key != null ? {
        (var.ai_foundry.customer_managed_key.user_assigned_identity_resource_id) = {}
      } : null
    }

    properties = {
      disableLocalAuth       = var.ai_foundry.disable_local_auth
      allowProjectManagement = var.ai_foundry.allow_project_management
      customSubDomainName    = local.ai_foundry_name
      publicNetworkAccess    = var.create_private_endpoints ? "Disabled" : "Enabled"
      networkAcls = {
        defaultAction       = "Allow"
        virtualNetworkRules = []
        ipRules             = []
      }

      # Enable VNet injection for Standard Agents
      networkInjections = var.ai_foundry.create_ai_agent_service ? var.ai_foundry.network_injections : null
    }
  }
  create_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  delete_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  read_headers              = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  schema_validation_enabled = false
  tags                      = var.tags
  update_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null

  lifecycle {
    ignore_changes = [
      body.properties.encryption
    ]
  }
}


resource "azapi_resource" "ai_agent_capability_host" {
  count = var.ai_foundry.create_ai_agent_service && var.ai_foundry.network_injections == null ? 1 : 0

  name      = "ai-agent-service-${random_string.resource_token.result}"
  parent_id = azapi_resource.ai_foundry.id
  type      = "Microsoft.CognitiveServices/accounts/capabilityHosts@${var.cognitive_services_api_version}"
  body = {
    properties = {
      capabilityHostKind = "Agents"
    }
  }
  create_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  delete_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  read_headers              = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  schema_validation_enabled = false
  update_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null

  depends_on = [azapi_resource.ai_foundry]
}

resource "azapi_resource" "ai_model_deployment" {
  for_each = var.ai_model_deployments

  name      = each.value.name
  parent_id = azapi_resource.ai_foundry.id
  type      = "Microsoft.CognitiveServices/accounts/deployments@${var.cognitive_services_api_version}"
  body = {
    properties = {
      model = {
        format  = each.value.model.format
        name    = each.value.model.name
        version = each.value.model.version
      }
      raiPolicyName        = each.value.rai_policy_name
      versionUpgradeOption = each.value.version_upgrade_option
    }
    sku = {
      name     = each.value.scale.type
      capacity = each.value.scale.capacity
    }
  }
  create_headers = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  delete_headers = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  read_headers   = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  update_headers = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null

  depends_on = [azapi_resource.ai_foundry]
}

# Data sources for CMK configuration
data "azurerm_key_vault" "cmk" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  name                = split("/", var.ai_foundry.customer_managed_key.key_vault_resource_id)[8]
  resource_group_name = split("/", var.ai_foundry.customer_managed_key.key_vault_resource_id)[4]
}

data "azurerm_key_vault_key" "cmk" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  key_vault_id = var.ai_foundry.customer_managed_key.key_vault_resource_id
  name         = var.ai_foundry.customer_managed_key.key_name
}

data "azurerm_user_assigned_identity" "cmk" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  name                = split("/", var.ai_foundry.customer_managed_key.user_assigned_identity_resource_id)[8]
  resource_group_name = split("/", var.ai_foundry.customer_managed_key.user_assigned_identity_resource_id)[4]
}

# Role assignment for UAMI to access Key Vault
resource "azurerm_role_assignment" "cmk_key_vault_crypto_user" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  principal_id         = data.azurerm_user_assigned_identity.cmk[0].principal_id
  scope                = var.ai_foundry.customer_managed_key.key_vault_resource_id
  role_definition_name = "Key Vault Crypto User"

  depends_on = [azapi_resource.ai_foundry]
}

# Wait for role assignment propagation
resource "time_sleep" "cmk_rbac_wait" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  create_duration = "60s"

  depends_on = [azurerm_role_assignment.cmk_key_vault_crypto_user]
}

# Update AI Foundry with CMK encryption
resource "azapi_update_resource" "ai_foundry_cmk" {
  count = var.ai_foundry.customer_managed_key != null ? 1 : 0

  resource_id = azapi_resource.ai_foundry.id
  type        = "Microsoft.CognitiveServices/accounts@${var.cognitive_services_api_version}"
  body = {
    properties = {
      encryption = {
        keySource = "Microsoft.KeyVault"
        keyVaultProperties = {
          keyVaultUri      = data.azurerm_key_vault.cmk[0].vault_uri
          keyName          = var.ai_foundry.customer_managed_key.key_name
          keyVersion       = var.ai_foundry.customer_managed_key.key_version != null ? var.ai_foundry.customer_managed_key.key_version : data.azurerm_key_vault_key.cmk[0].version
          identityClientId = data.azurerm_user_assigned_identity.cmk[0].client_id
        }
      }
    }
  }
  read_headers   = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  update_headers = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null

  depends_on = [
    azapi_resource.ai_foundry,
    time_sleep.cmk_rbac_wait
  ]
}

resource "time_sleep" "ai_foundry_wait" {
  create_duration = "5m"

  depends_on = [azapi_resource.ai_foundry, azapi_update_resource.ai_foundry_cmk]
}

resource "azurerm_private_endpoint" "ai_foundry" {
  count = var.create_private_endpoints ? 1 : 0

  location            = var.location
  name                = "pe-${azapi_resource.ai_foundry.name}"
  resource_group_name = basename(var.resource_group_resource_id)
  subnet_id           = var.private_endpoint_subnet_resource_id
  tags                = var.tags

  private_service_connection {
    is_manual_connection           = false
    name                           = "psc-${azapi_resource.ai_foundry.name}"
    private_connection_resource_id = azapi_resource.ai_foundry.id
    subresource_names              = ["account"]
  }
  private_dns_zone_group {
    name                 = "pe-${azapi_resource.ai_foundry.name}-dns"
    private_dns_zone_ids = var.ai_foundry.private_dns_zone_resource_ids
  }

  depends_on = [azapi_resource.ai_foundry, time_sleep.ai_foundry_wait]
}

resource "azurerm_role_assignment" "foundry_role_assignments" {
  for_each = local.foundry_role_assignments

  principal_id                           = each.value.principal_id
  scope                                  = resource.azapi_resource.ai_foundry.id
  condition                              = each.value.condition
  condition_version                      = each.value.condition_version
  delegated_managed_identity_resource_id = each.value.delegated_managed_identity_resource_id
  principal_type                         = each.value.principal_type
  role_definition_id                     = strcontains(lower(each.value.role_definition_id_or_name), lower(local.role_definition_resource_substring)) ? each.value.role_definition_id_or_name : null
  role_definition_name                   = strcontains(lower(each.value.role_definition_id_or_name), lower(local.role_definition_resource_substring)) ? null : each.value.role_definition_id_or_name
  skip_service_principal_aad_check       = each.value.skip_service_principal_aad_check
}
