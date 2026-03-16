# ── Cosmos DB outputs ────────────────────────────────────────────────────────

output "cosmos_account_id" {
  description = "Cosmos DB account resource ID."
  value       = azurerm_cosmosdb_account.main.id
}

output "cosmos_account_name" {
  description = "Cosmos DB account name."
  value       = azurerm_cosmosdb_account.main.name
}

output "cosmos_endpoint" {
  description = "Cosmos DB endpoint."
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "cosmos_database_name" {
  description = "Cosmos DB SQL database name."
  value       = azurerm_cosmosdb_sql_database.main.name
}

# ── AI Foundry outputs ──────────────────────────────────────────────────────

output "ai_foundry_id" {
  description = "Resource ID of the AI Foundry (AI Services) account."
  value       = module.ai_foundry.ai_foundry_id
}

output "ai_foundry_name" {
  description = "Name of the AI Foundry (AI Services) account."
  value       = module.ai_foundry.ai_foundry_name
}

output "ai_foundry_project_id" {
  description = "Resource ID of the Tutor AI Foundry project."
  value       = module.ai_foundry.ai_foundry_project_id["tutor"]
}

output "ai_foundry_project_name" {
  description = "Name of the Tutor AI Foundry project."
  value       = module.ai_foundry.ai_foundry_project_name["tutor"]
}

output "ai_model_deployment_ids" {
  description = "Resource IDs of all AI model deployments."
  value       = module.ai_foundry.ai_model_deployment_ids
}

output "project_endpoint" {
  description = "Azure AI Foundry project endpoint."
  value       = "https://${module.ai_foundry.ai_foundry_name}.services.ai.azure.com/api/projects/${module.ai_foundry.ai_foundry_project_name["tutor"]}"
}

output "ai_services_endpoint" {
  description = "Azure AI Services endpoint for Foundry agents."
  value       = "https://${module.ai_foundry.ai_foundry_name}.cognitiveservices.azure.com/"
}
