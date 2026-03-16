output "principal_ids" {
  description = "Map of service name to managed identity principal ID."
  value = {
    for name, app in azurerm_container_app.backend_services :
    name => app.identity[0].principal_id
  }
}

output "app_ids" {
  description = "Map of service name to Container App resource ID."
  value = {
    for name, app in azurerm_container_app.backend_services :
    name => app.id
  }
}

output "app_fqdns" {
  description = "Map of service name to Container App ingress FQDN."
  value = {
    for name, app in azurerm_container_app.backend_services :
    name => app.ingress[0].fqdn
  }
}

output "app_latest_revision_fqdns" {
  description = "Map of service name to Container App latest revision FQDN."
  value = {
    for name, app in azurerm_container_app.backend_services :
    name => try(app.latest_revision_fqdn, "")
  }
}
