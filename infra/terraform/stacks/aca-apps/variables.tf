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
  description = "Name of the resource group where ACA apps are deployed."
  type        = string
}

variable "container_app_environment_id" {
  description = "Resource ID of the Container App Environment."
  type        = string
}

variable "acr_id" {
  description = "Resource ID of the Azure Container Registry."
  type        = string
}

variable "backend_service_names" {
  description = "List of backend service names to create as Container Apps."
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
