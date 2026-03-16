output "apim_gateway_url" {
  description = "Base URL for Azure API Management gateway."
  value       = azurerm_api_management.main.gateway_url
}

output "apim_name" {
  description = "Azure API Management instance name."
  value       = azurerm_api_management.main.name
}

output "apim_id" {
  description = "Azure API Management resource ID."
  value       = azurerm_api_management.main.id
}
