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
        <set-variable name="request-origin" value="@(context.Request.Headers.GetValueOrDefault(&quot;Origin&quot;, &quot;&quot;))" />
        <choose>
          <when condition="@(
            context.Request.Method == &quot;OPTIONS&quot;
            &amp;&amp; !string.IsNullOrEmpty((string)context.Variables[&quot;request-origin&quot;])
            &amp;&amp; (
              ((string)context.Variables[&quot;request-origin&quot;]).EndsWith(&quot;.azurestaticapps.net&quot;, StringComparison.OrdinalIgnoreCase)
              || ((string)context.Variables[&quot;request-origin&quot;]).Equals(&quot;http://localhost:3000&quot;, StringComparison.OrdinalIgnoreCase)
              || ((string)context.Variables[&quot;request-origin&quot;]).Equals(&quot;http://localhost:5173&quot;, StringComparison.OrdinalIgnoreCase)
            )
          )">
            <return-response>
              <set-status code="204" reason="No Content" />
              <set-header name="Access-Control-Allow-Origin" exists-action="override">
                <value>@((string)context.Variables[&quot;request-origin&quot;])</value>
              </set-header>
              <set-header name="Access-Control-Allow-Methods" exists-action="override">
                <value>GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD</value>
              </set-header>
              <set-header name="Access-Control-Allow-Headers" exists-action="override">
                <value>*</value>
              </set-header>
              <set-header name="Access-Control-Max-Age" exists-action="override">
                <value>86400</value>
              </set-header>
              <set-header name="Vary" exists-action="append">
                <value>Origin</value>
              </set-header>
            </return-response>
          </when>
        </choose>
      </inbound>
      <backend>
        <base />
      </backend>
      <outbound>
        <base />
        <choose>
          <when condition="@(
            !string.IsNullOrEmpty((string)context.Variables[&quot;request-origin&quot;])
            &amp;&amp; (
              ((string)context.Variables[&quot;request-origin&quot;]).EndsWith(&quot;.azurestaticapps.net&quot;, StringComparison.OrdinalIgnoreCase)
              || ((string)context.Variables[&quot;request-origin&quot;]).Equals(&quot;http://localhost:3000&quot;, StringComparison.OrdinalIgnoreCase)
              || ((string)context.Variables[&quot;request-origin&quot;]).Equals(&quot;http://localhost:5173&quot;, StringComparison.OrdinalIgnoreCase)
            )
          )">
            <set-header name="Access-Control-Allow-Origin" exists-action="override">
              <value>@((string)context.Variables[&quot;request-origin&quot;])</value>
            </set-header>
            <set-header name="Vary" exists-action="append">
              <value>Origin</value>
            </set-header>
          </when>
        </choose>
      </outbound>
      <on-error>
        <base />
      </on-error>
    </policies>
  XML
}
