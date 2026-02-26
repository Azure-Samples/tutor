output "azure_location" {
  description = "Azure region used for the deployment."
  value       = azurerm_resource_group.main.location
}

output "resource_group_name" {
  description = "Resource group name."
  value       = azurerm_resource_group.main.name
}

output "AZURE_RESOURCE_GROUP" {
  description = "Azure resource group used by azd service target resolution."
  value       = azurerm_resource_group.main.name
}

output "acr_name" {
  description = "Azure Container Registry name."
  value       = azurerm_container_registry.main.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server."
  value       = azurerm_container_registry.main.login_server
}

output "AZURE_CONTAINER_REGISTRY_ENDPOINT" {
  description = "Container registry endpoint used by azd publish operations."
  value       = azurerm_container_registry.main.login_server
}

output "application_insights_connection_string" {
  description = "Application Insights connection string."
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "storage_account_name" {
  description = "Storage account name used for file uploads."
  value       = azurerm_storage_account.uploads.name
}

output "blob_endpoint" {
  description = "Blob service endpoint."
  value       = azurerm_storage_account.uploads.primary_blob_endpoint
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

output "COSMOS_ENDPOINT" {
  description = "Cosmos DB endpoint for backend services."
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "COSMOS_DATABASE" {
  description = "Cosmos DB SQL database name for backend services."
  value       = azurerm_cosmosdb_sql_database.main.name
}

output "COSMOS_ESSAY_TABLE" {
  description = "Cosmos DB container name for essays."
  value       = "essays"
}

output "COSMOS_QUESTION_TABLE" {
  description = "Cosmos DB container name for questions."
  value       = "questions"
}

output "COSMOS_ANSWER_TABLE" {
  description = "Cosmos DB container name for answers."
  value       = "answers"
}

output "COSMOS_CONFIGURATION_TABLE" {
  description = "Cosmos DB container name for configuration records."
  value       = "configuration"
}

output "COSMOS_RESOURCE_TABLE" {
  description = "Cosmos DB container name for resources."
  value       = "resources"
}

output "COSMOS_GRADER_TABLE" {
  description = "Cosmos DB container name for graders."
  value       = "graders"
}

output "COSMOS_ASSEMBLY_TABLE" {
  description = "Cosmos DB container name for assemblies."
  value       = "assemblies"
}

output "COSMOS_STUDENT_TABLE" {
  description = "Cosmos DB container name for students."
  value       = "students"
}

output "COSMOS_PROFESSOR_TABLE" {
  description = "Cosmos DB container name for professors."
  value       = "professors"
}

output "COSMOS_COURSE_TABLE" {
  description = "Cosmos DB container name for courses."
  value       = "courses"
}

output "COSMOS_CLASS_TABLE" {
  description = "Cosmos DB container name for classes."
  value       = "classes"
}

output "COSMOS_GROUP_TABLE" {
  description = "Cosmos DB container name for groups."
  value       = "groups"
}

output "COSMOS_AVATAR_CASE_TABLE" {
  description = "Cosmos DB container name for avatar case records."
  value       = "avatar_case"
}

output "BLOB_CONNECTION_STRING" {
  description = "Storage account connection string used by services."
  value       = azurerm_storage_account.uploads.primary_connection_string
  sensitive   = true
}

output "BLOB_CONTAINER_NAME" {
  description = "Blob container name used by services."
  value       = azurerm_storage_container.uploads.name
}

output "PROJECT_ENDPOINT" {
  description = "Azure AI Foundry project endpoint."
  value       = var.project_endpoint
}

output "MODEL_DEPLOYMENT_NAME" {
  description = "Default model deployment name."
  value       = var.model_deployment_name
}

output "MODEL_REASONING_DEPLOYMENT" {
  description = "Reasoning model deployment name."
  value       = var.model_reasoning_deployment
}

output "ENTRA_TENANT_ID" {
  description = "Entra tenant ID for service authentication settings."
  value       = var.entra_tenant_id
}

output "ENTRA_AUTH_ENABLED" {
  description = "Feature flag enabling Entra JWT validation middleware in services."
  value       = tostring(var.entra_auth_enabled)
}

output "ENTRA_API_CLIENT_ID" {
  description = "Entra application client ID exposed as API audience base value."
  value       = var.entra_api_client_id
}

output "ENTRA_TOKEN_AUDIENCE" {
  description = "JWT audience expected by APIs."
  value       = var.entra_api_client_id != "" ? "api://${var.entra_api_client_id}" : ""
}

output "ENTRA_ALLOWED_CLIENT_APP_IDS" {
  description = "Allowed client application IDs accepted by API middleware."
  value       = var.entra_allowed_client_app_ids
}

output "ENTRA_TEACHER_CLIENT_ID" {
  description = "Entra teacher client ID."
  value       = var.entra_teacher_client_id
}

output "ENTRA_TEACHER_CLIENT_SECRET" {
  description = "Entra teacher client secret."
  value       = var.entra_teacher_client_secret
  sensitive   = true
}

output "STUDENT_SECRET_SALT" {
  description = "Student secret salt value."
  value       = var.student_secret_salt
  sensitive   = true
}

output "SERVICE_AVATAR_RESOURCE_ID" {
  description = "Resource ID for avatar service target."
  value       = try(azurerm_container_app.backend_services["avatar"].id, "")
}

output "SERVICE_CONFIGURATION_RESOURCE_ID" {
  description = "Resource ID for configuration service target."
  value       = try(azurerm_container_app.backend_services["configuration"].id, "")
}

output "SERVICE_ESSAYS_RESOURCE_ID" {
  description = "Resource ID for essays service target."
  value       = try(azurerm_container_app.backend_services["essays"].id, "")
}

output "SERVICE_QUESTIONS_RESOURCE_ID" {
  description = "Resource ID for questions service target."
  value       = try(azurerm_container_app.backend_services["questions"].id, "")
}

output "SERVICE_UPSKILLING_RESOURCE_ID" {
  description = "Resource ID for upskilling service target."
  value       = try(azurerm_container_app.backend_services["upskilling"].id, "")
}

output "SERVICE_CHAT_RESOURCE_ID" {
  description = "Resource ID for chat service target."
  value       = try(azurerm_container_app.backend_services["chat"].id, "")
}

output "SERVICE_EVALUATION_RESOURCE_ID" {
  description = "Resource ID for evaluation service target."
  value       = try(azurerm_container_app.backend_services["evaluation"].id, "")
}

output "SERVICE_LMS_GATEWAY_RESOURCE_ID" {
  description = "Resource ID for lms-gateway service target."
  value       = try(azurerm_container_app.backend_services["lms-gateway"].id, "")
}

output "SERVICE_FRONTEND_RESOURCE_ID" {
  description = "Resource ID for frontend service target."
  value       = azurerm_static_web_app.frontend.id
}
