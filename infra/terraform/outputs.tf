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

output "acr_id" {
  description = "Azure Container Registry resource ID."
  value       = azurerm_container_registry.main.id
}

output "container_app_environment_id" {
  description = "Container App Environment resource ID."
  value       = azurerm_container_app_environment.main.id
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

output "COSMOS_UPSKILLING_TABLE" {
  description = "Cosmos DB container name for upskilling plans."
  value       = "upskilling_plans"
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

output "COSMOS_PUBLIC_NETWORK_ACCESS_ENABLED" {
  description = "Current Cosmos DB public network access configuration from Terraform."
  value       = tostring(var.cosmos_public_network_access_enabled)
}

output "COSMOS_ALLOWED_PUBLIC_IP_RANGES" {
  description = "Configured Cosmos DB public IP/CIDR allowlist."
  value       = join(",", var.cosmos_allowed_public_ip_ranges)
}

output "COSMOS_LOCKOUT_RISK" {
  description = "True when Cosmos is configured private-only but ACA VNet integration is disabled."
  value       = tostring(var.cosmos_public_network_access_enabled == false && var.aca_vnet_integration_enabled == false)
}

output "COSMOS_BREAK_GLASS_COMMAND" {
  description = "Emergency command to re-enable Cosmos public access."
  value       = "az cosmosdb update -g ${azurerm_resource_group.main.name} -n ${azurerm_cosmosdb_account.main.name} --public-network-access Enabled"
}

output "COSMOS_AVATAR_CASE_TABLE" {
  description = "Cosmos DB container name for avatar case records."
  value       = "avatar_case"
}

output "COSMOS_LEARNER_RECORD_EVENTS_TABLE" {
  description = "Cosmos DB container name for learner-record append-only events."
  value       = "learner_record_events"
}

output "COSMOS_INSIGHTS_REPORT_TABLE" {
  description = "Cosmos DB container name for insights reports."
  value       = "insights_reports"
}

output "COSMOS_INSIGHTS_FEEDBACK_TABLE" {
  description = "Cosmos DB container name for insights feedback entries."
  value       = "insights_feedback"
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

output "SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE" {
  description = "Fully qualified namespace used by managed-identity Service Bus clients."
  value       = "${azurerm_servicebus_namespace.main.name}.servicebus.windows.net"
}

output "SERVICE_BUS_LEARNER_RECORD_TOPIC" {
  description = "Service Bus topic used to distribute learner-record integration events."
  value       = azurerm_servicebus_topic.learner_record.name
}

output "SERVICE_BUS_LEARNER_RECORD_SUBSCRIPTION" {
  description = "Default Service Bus subscription used for learner-record integration backlog inspection."
  value       = azurerm_servicebus_subscription.learner_record_integration_backlog.name
}

output "PROJECT_ENDPOINT" {
  description = "Azure AI Foundry project endpoint (AVM module, ADR-012)."
  value       = "https://${module.ai_foundry.ai_foundry_name}.services.ai.azure.com/api/projects/${module.ai_foundry.ai_foundry_project_name["tutor"]}"
}

output "AI_SERVICES_ENDPOINT" {
  description = "Azure AI Services endpoint for Foundry agents."
  value       = "https://${module.ai_foundry.ai_foundry_name}.cognitiveservices.azure.com/"
}

output "MODEL_DEPLOYMENT_NAME" {
  description = "Default model deployment name."
  value       = var.model_deployment_name
}

output "MODEL_REASONING_DEPLOYMENT" {
  description = "Reasoning model deployment name."
  value       = var.model_reasoning_deployment
}

output "ai_foundry_id" {
  description = "Resource ID of the AI Foundry (AI Services) account."
  value       = module.ai_foundry.ai_foundry_id
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
  value       = azurerm_container_app.backend_services["avatar"].id
}

output "SERVICE_CONFIGURATION_RESOURCE_ID" {
  description = "Resource ID for configuration service target."
  value       = azurerm_container_app.backend_services["configuration"].id
}

output "SERVICE_ESSAYS_RESOURCE_ID" {
  description = "Resource ID for essays service target."
  value       = azurerm_container_app.backend_services["essays"].id
}

output "SERVICE_QUESTIONS_RESOURCE_ID" {
  description = "Resource ID for questions service target."
  value       = azurerm_container_app.backend_services["questions"].id
}

output "SERVICE_UPSKILLING_RESOURCE_ID" {
  description = "Resource ID for upskilling service target."
  value       = azurerm_container_app.backend_services["upskilling"].id
}

output "SERVICE_CHAT_RESOURCE_ID" {
  description = "Resource ID for chat service target."
  value       = azurerm_container_app.backend_services["chat"].id
}

output "SERVICE_EVALUATION_RESOURCE_ID" {
  description = "Resource ID for evaluation service target."
  value       = azurerm_container_app.backend_services["evaluation"].id
}

output "SERVICE_INSIGHTS_RESOURCE_ID" {
  description = "Resource ID for insights service target."
  value       = azurerm_container_app.backend_services["insights"].id
}

output "SERVICE_LMS_GATEWAY_RESOURCE_ID" {
  description = "Resource ID for lms-gateway service target."
  value       = azurerm_container_app.backend_services["lms-gateway"].id
}

output "SERVICE_FRONTEND_RESOURCE_ID" {
  description = "Resource ID for frontend service target."
  value       = azurerm_static_web_app.frontend.id
}

output "APIM_BASE_URL" {
  description = "Base URL for Azure API Management gateway."
  value       = azurerm_api_management.main.gateway_url
}

output "NEXT_PUBLIC_APIM_BASE_URL" {
  description = "Frontend APIM gateway base URL."
  value       = azurerm_api_management.main.gateway_url
}

output "AVATAR_APP_BASE_URL" {
  description = "Public base URL for avatar backend service."
  value       = "https://${azurerm_container_app.backend_services["avatar"].ingress[0].fqdn}"
}

output "CONFIGURATION_APP_BASE_URL" {
  description = "Public base URL for configuration backend service."
  value       = "https://${azurerm_container_app.backend_services["configuration"].ingress[0].fqdn}"
}

output "ESSAYS_APP_BASE_URL" {
  description = "Public base URL for essays backend service."
  value       = "https://${azurerm_container_app.backend_services["essays"].ingress[0].fqdn}"
}

output "QUESTIONS_APP_BASE_URL" {
  description = "Public base URL for questions backend service."
  value       = "https://${azurerm_container_app.backend_services["questions"].ingress[0].fqdn}"
}

output "UPSKILLING_APP_BASE_URL" {
  description = "Public base URL for upskilling backend service."
  value       = "https://${azurerm_container_app.backend_services["upskilling"].ingress[0].fqdn}"
}

output "WEB_APP_BASE_URL" {
  description = "Public base URL for chat backend service."
  value       = "https://${azurerm_container_app.backend_services["chat"].ingress[0].fqdn}"
}

output "TRANSCRIPTION_APP_BASE_URL" {
  description = "Public base URL for transcription backend service."
  value       = ""  
}
