#Moving AI_search to it's own file since we're basically creating a resource module for it.

resource "azapi_resource" "ai_search" {
  for_each = { for k, v in var.ai_search_definition : k => v if v.existing_resource_id == null && var.create_byor == true }

  location  = var.location
  name      = try(each.value.name, null) != null ? each.value.name : (try(var.base_name, null) != null ? "${var.base_name}-${each.key}-ai-foundry-ai-search-${random_string.resource_token.result}" : "${each.key}-ai-foundry-ai-search-${random_string.resource_token.result}")
  parent_id = var.resource_group_resource_id
  type      = "Microsoft.Search/searchServices@2024-06-01-preview"
  body = {
    sku = {
      name = each.value.sku
    }

    identity = {
      type = "SystemAssigned"
    }

    properties = merge(
      {
        replicaCount   = each.value.replica_count
        partitionCount = each.value.partition_count
        hostingMode    = each.value.hosting_mode
        semanticSearch = each.value.semantic_search

        # Identity-related controls
        disableLocalAuth = each.value.local_authentication_enabled ? false : true #inverted logic to match the variable definition

        # Networking-related controls
        publicNetworkAccess = var.create_private_endpoints ? "Disabled" : "Enabled"
        networkRuleSet = {
          bypass = "None"
        }
      },
      each.value.local_authentication_enabled ? {
        authOptions = {
          aadOrApiKey = {
            aadAuthFailureMode = "http401WithBearerChallenge"
          }
        }
      } : {}
    )
  }
  create_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  delete_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  read_headers              = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
  schema_validation_enabled = true
  update_headers            = var.enable_telemetry ? { "User-Agent" : local.avm_azapi_header } : null
}

resource "azurerm_private_endpoint" "pe_aisearch" {
  for_each = { for k, v in var.ai_search_definition : k => v if v.existing_resource_id == null && var.create_byor == true && var.create_private_endpoints == true && v.private_endpoints_manage_dns_zone_group == true }

  location            = var.location
  name                = "${azapi_resource.ai_search[each.key].name}-private-endpoint"
  resource_group_name = local.resource_group_name
  subnet_id           = var.private_endpoint_subnet_resource_id
  tags                = var.tags

  private_service_connection {
    is_manual_connection           = false
    name                           = "${azapi_resource.ai_search[each.key].name}-private-link-service-connection"
    private_connection_resource_id = azapi_resource.ai_search[each.key].id
    subresource_names = [
      "searchService"
    ]
  }
  dynamic "private_dns_zone_group" {
    for_each = each.value.private_dns_zone_resource_id != null ? ["this"] : []

    content {
      name                 = "${azapi_resource.ai_search[each.key].name}-dns-config"
      private_dns_zone_ids = [each.value.private_dns_zone_resource_id]
    }
  }

  depends_on = [
    module.cosmosdb,
    azapi_resource.ai_search
  ]
}

resource "azurerm_private_endpoint" "pe_aisearch_unmanaged_dns_zone_groups" {
  for_each = { for k, v in var.ai_search_definition : k => v if v.existing_resource_id == null && var.create_byor == true && var.create_private_endpoints == true && v.private_endpoints_manage_dns_zone_group == false }

  location            = var.location
  name                = "${azapi_resource.ai_search[each.key].name}-private-endpoint"
  resource_group_name = local.resource_group_name
  subnet_id           = var.private_endpoint_subnet_resource_id
  tags                = var.tags

  private_service_connection {
    is_manual_connection           = false
    name                           = "${azapi_resource.ai_search[each.key].name}-private-link-service-connection"
    private_connection_resource_id = azapi_resource.ai_search[each.key].id
    subresource_names = [
      "searchService"
    ]
  }

  depends_on = [
    module.cosmosdb,
    azapi_resource.ai_search
  ]

  lifecycle {
    ignore_changes = [private_dns_zone_group]
  }
}

resource "azurerm_role_assignment" "this_aisearch" {
  for_each = local.ai_search_rbac

  principal_id                           = each.value.role_assignment.principal_id
  scope                                  = azapi_resource.ai_search[each.value.ai_key].id
  condition                              = each.value.role_assignment.condition
  condition_version                      = each.value.role_assignment.condition_version
  delegated_managed_identity_resource_id = each.value.role_assignment.delegated_managed_identity_resource_id
  principal_type                         = each.value.role_assignment.principal_type
  role_definition_id                     = strcontains(lower(each.value.role_assignment.role_definition_id_or_name), lower(local.role_definition_resource_substring)) ? each.value.role_assignment.role_definition_id_or_name : null
  role_definition_name                   = strcontains(lower(each.value.role_assignment.role_definition_id_or_name), lower(local.role_definition_resource_substring)) ? null : each.value.role_assignment.role_definition_id_or_name
  skip_service_principal_aad_check       = each.value.role_assignment.skip_service_principal_aad_check
}

resource "azurerm_monitor_diagnostic_setting" "this_aisearch" {
  for_each = merge([
    for search_key, search_value in var.ai_search_definition : {
      for diag_key, diag_value in search_value.diagnostic_settings :
      "${search_key}-${diag_key}" => merge(diag_value, {
        target_resource_id = search_value.existing_resource_id != null ? search_value.existing_resource_id : azapi_resource.ai_search[search_key].id
      })
    }
  ]...)

  name                           = each.value.name != null ? each.value.name : "diag-${split("/", each.value.target_resource_id)[8]}"
  target_resource_id             = each.value.target_resource_id
  eventhub_authorization_rule_id = each.value.event_hub_authorization_rule_resource_id
  eventhub_name                  = each.value.event_hub_name
  log_analytics_destination_type = each.value.log_analytics_destination_type
  log_analytics_workspace_id     = each.value.workspace_resource_id
  partner_solution_id            = each.value.marketplace_partner_resource_id
  storage_account_id             = each.value.storage_account_resource_id

  dynamic "enabled_log" {
    for_each = each.value.log_categories

    content {
      category = enabled_log.value
    }
  }
  dynamic "enabled_log" {
    for_each = each.value.log_groups

    content {
      category_group = enabled_log.value
    }
  }
  dynamic "enabled_metric" {
    for_each = each.value.metric_categories

    content {
      category = enabled_metric.value
    }
  }
}
