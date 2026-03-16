locals {
  apim_service_paths = {
    for service_name in var.backend_service_names :
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
      "https://${var.frontend_default_hostname}",
      "http://localhost:3000",
      "http://localhost:5173",
    ],
    var.apim_additional_allowed_origins,
  )))

  agent_role_scopes = {
    "Cosmos DB Built-in Data Contributor" = var.cosmos_account_id
    "Storage Blob Data Contributor"       = var.storage_account_id
    "AcrPull"                             = var.acr_id
    "Cognitive Services User"             = var.ai_foundry_id
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

# ── APIM ────────────────────────────────────────────────────────────────────

resource "azurerm_api_management" "main" {
  name                = "${var.name_prefix}-${var.environment}-apim"
  location            = var.location
  resource_group_name = var.resource_group_name
  publisher_name      = "Tutor Platform"
  publisher_email     = "platform@contoso.com"
  sku_name            = "Consumption_0"

  tags = {
    "azd-env-name" = var.environment
  }
}

resource "azurerm_api_management_api" "backend_services" {
  for_each = var.manage_apim_service_edge ? local.apim_service_paths : {}

  name                  = "${each.key}-api"
  resource_group_name   = var.resource_group_name
  api_management_name   = azurerm_api_management.main.name
  revision              = "1"
  display_name          = "${each.key} API"
  path                  = each.value
  protocols             = ["https"]
  service_url           = "https://${var.backend_service_fqdns[each.key]}"
  subscription_required = false
}

resource "azurerm_api_management_api_operation" "backend_catch_all" {
  for_each = var.manage_apim_service_edge ? local.apim_operations : {}

  operation_id        = replace(each.key, "-", "")
  api_name            = azurerm_api_management_api.backend_services[each.value.service_name].name
  api_management_name = azurerm_api_management.main.name
  resource_group_name = var.resource_group_name
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
  for_each = var.manage_apim_service_edge ? local.apim_service_paths : {}

  resource_group_name = var.resource_group_name
  api_management_name = azurerm_api_management.main.name
  api_name            = "${each.key}-api"

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
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

# ── Cognitive Services RBAC for backend container apps ──────────────────────

resource "azurerm_role_assignment" "container_app_cognitive_services" {
  for_each             = var.container_app_principal_ids
  scope                = var.ai_foundry_id
  role_definition_name = "Cognitive Services User"
  principal_id         = each.value
}

# ── Agent RBAC ──────────────────────────────────────────────────────────────

resource "azurerm_role_assignment" "agent_permissions" {
  for_each             = local.agent_role_assignments
  scope                = each.value.scope
  role_definition_name = each.value.role_name
  principal_id         = each.value.principal_id
}
