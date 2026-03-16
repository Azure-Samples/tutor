variable "name_prefix" {
  description = "Prefix used for Azure resource names."
  type        = string
  default     = "tutor"
}

variable "environment" {
  description = "Deployment environment name (for example: dev, test, prod)."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
}

variable "resource_group_id" {
  description = "Resource ID of the resource group."
  type        = string
}

variable "location" {
  description = "Azure region for Cosmos DB resources."
  type        = string
}

variable "foundry_location" {
  description = "Azure region for AI Foundry resources (Hub, Project, AI Services)."
  type        = string
  default     = "westus3"
}

variable "normalized_prefix" {
  description = "Lower-cased prefix without hyphens, used for resource naming."
  type        = string
}

variable "random_suffix" {
  description = "Random suffix from the foundation stack, used for globally unique names."
  type        = string
}

variable "cosmos_db_name" {
  description = "Cosmos DB SQL database name."
  type        = string
  default     = "tutor"
}

variable "cosmos_containers" {
  description = "Cosmos DB SQL containers with partition key paths."
  type = map(object({
    partition_key_path = string
  }))
}

variable "cosmos_public_network_access_enabled" {
  description = "Controls Cosmos DB public network access."
  type        = bool
  default     = true
}

variable "cosmos_lockout_acknowledged" {
  description = "Explicit acknowledgement required before disabling Cosmos public access."
  type        = bool
  default     = false
}

variable "cosmos_allowed_public_ip_ranges" {
  description = "Optional public IPv4/CIDR allowlist for Cosmos DB."
  type        = list(string)
  default     = []
}

variable "aca_vnet_integration_enabled" {
  description = "Whether the ACA environment is integrated with a VNet."
  type        = bool
  default     = false
}

variable "cosmos_pe_subnet_id" {
  description = "Subnet ID for the Cosmos DB private endpoint. Required when aca_vnet_integration_enabled is true."
  type        = string
  default     = ""
}

variable "cosmos_dns_zone_ids" {
  description = "Private DNS zone IDs for Cosmos DB private endpoint. Required when aca_vnet_integration_enabled is true."
  type        = list(string)
  default     = []
}

variable "storage_account_id" {
  description = "Resource ID of the Storage Account for Foundry project connection."
  type        = string
}

variable "model_deployment_name" {
  description = "Default model deployment name used by services."
  type        = string
  default     = "gpt-5-nano"
}

variable "model_reasoning_deployment" {
  description = "Reasoning model deployment name used by services."
  type        = string
  default     = "gpt-5"
}
