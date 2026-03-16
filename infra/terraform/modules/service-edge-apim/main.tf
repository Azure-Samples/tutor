terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

data "azurerm_container_app" "service" {
  name                = var.container_app_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_api_management_api" "service" {
  name                  = "${var.service_name}-api"
  resource_group_name   = var.resource_group_name
  api_management_name   = var.api_management_name
  revision              = "1"
  display_name          = "${var.service_name} API"
  path                  = var.api_path
  protocols             = ["https"]
  service_url           = "https://${data.azurerm_container_app.service.ingress[0].fqdn}"
  subscription_required = false
}

locals {
  operation_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
}

resource "azurerm_api_management_api_operation" "catch_all" {
  for_each = { for method in local.operation_methods : lower(method) => method }

  operation_id        = replace("${var.service_name}-${each.key}", "-", "")
  api_name            = azurerm_api_management_api.service.name
  api_management_name = var.api_management_name
  resource_group_name = var.resource_group_name
  display_name        = "${each.value} catch-all"
  method              = each.value
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

resource "azurerm_api_management_api_policy" "service" {
  resource_group_name = var.resource_group_name
  api_management_name = var.api_management_name
  api_name            = azurerm_api_management_api.service.name

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <cors allow-credentials="false">
          <allowed-origins>
            <origin>http://localhost:3000</origin>
            <origin>http://localhost:5173</origin>
            ${join("\n            ", [for o in var.allowed_origins : "<origin>${o}</origin>"])}
          </allowed-origins>
          <allowed-methods preflight-result-max-age="86400">
            <method>*</method>
          </allowed-methods>
          <allowed-headers>
            <header>*</header>
          </allowed-headers>
        </cors>
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
