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

variable "location" {
  description = "Azure region for resources."
  type        = string
}

# ── Inputs from aca-apps stack ──────────────────────────────────────────────

variable "container_app_principal_ids" {
  description = "Map of backend service name to managed identity principal ID."
  type        = map(string)
}

variable "backend_service_fqdns" {
  description = "Map of backend service name to ingress FQDN."
  type        = map(string)
  default     = {}
}

# ── Inputs from data-ai stack ──────────────────────────────────────────────

variable "ai_foundry_id" {
  description = "Resource ID of the AI Foundry (AI Services) account."
  type        = string
}

variable "cosmos_account_id" {
  description = "Resource ID of the Cosmos DB account."
  type        = string
}

# ── Inputs from foundation ──────────────────────────────────────────────────

variable "storage_account_id" {
  description = "Resource ID of the uploads storage account."
  type        = string
}

variable "acr_id" {
  description = "Resource ID of the Azure Container Registry."
  type        = string
}

variable "frontend_default_hostname" {
  description = "Default hostname of the Static Web App frontend."
  type        = string
}

# ── APIM configuration ─────────────────────────────────────────────────────

variable "apim_additional_allowed_origins" {
  description = "Additional origins allowed by APIM CORS policy."
  type        = list(string)
  default     = []
}

variable "apim_rate_limit_calls" {
  description = "Maximum number of API calls allowed per renewal period per client IP."
  type        = number
  default     = 120
}

variable "apim_rate_limit_renewal_period_seconds" {
  description = "Renewal period in seconds for APIM rate limiting."
  type        = number
  default     = 60
}

variable "manage_apim_service_edge" {
  description = "Whether APIM API/operations/policies for backend services are managed by this stack."
  type        = bool
  default     = false
}

# ── Agent RBAC ──────────────────────────────────────────────────────────────

variable "agent_principal_object_ids" {
  description = "Object IDs for Entra service principals or managed identities used by agent workloads."
  type        = list(string)
  default     = []
}

# ── Service list ────────────────────────────────────────────────────────────

variable "backend_service_names" {
  description = "List of backend service names for RBAC and APIM operations."
  type        = list(string)
  default = [
    "avatar",
    "configuration",
    "essays",
    "questions",
    "upskilling",
    "chat",
    "evaluation",
    "lms-gateway",
  ]
}
