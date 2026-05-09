output "key_vault_id" {
  description = "The resource ID of the Key Vault"
  value       = azurerm_key_vault.this.id
}

output "key_vault_key_id" {
  description = "The resource ID of the Key Vault Key"
  value       = azurerm_key_vault_key.cmk.id
}

output "resource_id" {
  description = "The resource ID of the AI Foundry account"
  value       = module.ai_foundry.resource_id
}

output "user_assigned_identity_id" {
  description = "The resource ID of the User-Assigned Managed Identity"
  value       = azurerm_user_assigned_identity.cmk.id
}
