resource "azurerm_container_app" "backend_services" {
  for_each = toset(var.backend_service_names)

  name                         = "${var.name_prefix}-${each.key}-${var.environment}"
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  registry {
    server   = var.acr_login_server
    identity = "system"
  }

  template {
    container {
      name    = each.key
      image   = "mcr.microsoft.com/azurelinux/base/python:3.12"
      command = ["python"]
      args    = ["-m", "http.server", "8000"]
      cpu     = 0.5
      memory  = "1Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = {
    "azd-env-name"     = var.environment
    "azd-service-name" = each.key
  }

  # Infrastructure fields (env, identity, registry, ingress, tags) remain Terraform-managed.
  # Only runtime-mutable fields are ignored so app deploys don't cause drift.
  lifecycle {
    ignore_changes = [
      template[0].container[0].image,
      template[0].container[0].env,
      template[0].min_replicas,
      template[0].max_replicas,
      template[0].revision_suffix,
      secret,
    ]
  }
}

resource "azurerm_role_assignment" "container_app_acr_pull" {
  for_each             = toset(var.backend_service_names)
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.backend_services[each.key].identity[0].principal_id
}
