variable "ai_agent_host_name" {
  type        = string
  description = "Name of the AI agent capability host"
}

variable "ai_foundry_id" {
  type        = string
  description = "Resource ID of the AI Foundry account"
}

variable "description" {
  type        = string
  description = "Description for the AI Foundry project"
}

variable "display_name" {
  type        = string
  description = "Display name for the AI Foundry project"
}

variable "location" {
  type        = string
  description = "Azure region for deployment"
  nullable    = false
}

variable "name" {
  type        = string
  description = "Name of the AI Foundry project"
}

variable "account_capability_host_id" {
  type        = string
  default     = null
  description = "Resource ID of the account-level capability host (if exists) to ensure it completes before project capability host creation"
}

variable "ai_search_id" {
  type        = string
  default     = null
  description = "Resource ID of the AI Search service"
}

variable "cosmos_db_id" {
  type        = string
  default     = null
  description = "Resource ID of the Cosmos DB account"
}

variable "create_ai_agent_service" {
  type        = bool
  default     = true
  description = "Whether to create the AI agent service"
}

variable "create_project_connections" {
  type        = bool
  default     = false
  description = "Whether to create project connections for AI Foundry, Cosmos DB, Key Vault, and AI Search. If set to false, the project will not create connections to these resources."
}

variable "sku" {
  type        = string
  default     = "S0"
  description = "SKU for the AI Foundry project"
}

variable "storage_account_id" {
  type        = string
  default     = null
  description = "Resource ID of the Storage Account"
}

variable "tags" {
  type        = map(string)
  default     = null
  description = "Tags to apply to resources"
}
