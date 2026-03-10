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

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "eastus"
}

variable "foundry_location" {
  description = "Azure region for AI Foundry resources (Hub, Project, AI Services). Deployed outside VNet."
  type        = string
  default     = "westus3"
}

variable "cosmos_db_name" {
  description = "Cosmos DB SQL database name."
  type        = string
  default     = "tutor"
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

variable "entra_tenant_id" {
  description = "Microsoft Entra tenant ID for authentication settings."
  type        = string
  default     = ""
}

variable "entra_api_client_id" {
  description = "Microsoft Entra application (API) client ID used as JWT audience."
  type        = string
  default     = ""
}

variable "entra_auth_enabled" {
  description = "Enables Microsoft Entra JWT authentication in backend services."
  type        = bool
  default     = false
}

variable "entra_allowed_client_app_ids" {
  description = "Comma-separated allowed client application IDs (azp/appid) accepted by APIs."
  type        = string
  default     = ""
}

variable "entra_teacher_client_id" {
  description = "Entra application client ID for teacher authentication flows."
  type        = string
  default     = ""
}

variable "entra_teacher_client_secret" {
  description = "Entra application client secret for teacher authentication flows."
  type        = string
  default     = ""
  sensitive   = true
}

variable "student_secret_salt" {
  description = "Salt value used to derive student secrets."
  type        = string
  default     = ""
  sensitive   = true
}

variable "agent_principal_object_ids" {
  description = "Object IDs for Entra service principals or managed identities used by agent workloads."
  type        = list(string)
  default     = []
}

variable "cosmos_containers" {
  description = "Cosmos DB SQL containers with partition key paths."
  type = map(object({
    partition_key_path = string
  }))
  default = {
    essays = {
      partition_key_path = "/student_id"
    }
    questions = {
      partition_key_path = "/student_id"
    }
    answers = {
      partition_key_path = "/student_id"
    }
    configuration = {
      partition_key_path = "/id"
    }
    resources = {
      partition_key_path = "/id"
    }
    graders = {
      partition_key_path = "/id"
    }
    assemblies = {
      partition_key_path = "/id"
    }
    students = {
      partition_key_path = "/id"
    }
    professors = {
      partition_key_path = "/id"
    }
    courses = {
      partition_key_path = "/id"
    }
    classes = {
      partition_key_path = "/id"
    }
    groups = {
      partition_key_path = "/id"
    }
    avatar_case = {
      partition_key_path = "/id"
    }
    upskilling_plans = {
      partition_key_path = "/professor_id"
    }
  }
}

variable "apim_additional_allowed_origins" {
  description = "Additional origins allowed by APIM CORS policy. Static Web App and local origins are added automatically."
  type        = list(string)
  default     = []
}

variable "apim_rate_limit_calls" {
  description = "Maximum number of API calls allowed per renewal period per client IP at APIM."
  type        = number
  default     = 120
}

variable "apim_rate_limit_renewal_period_seconds" {
  description = "Renewal period in seconds for APIM rate limiting."
  type        = number
  default     = 60
}

variable "manage_apim_service_edge_in_foundation" {
  description = "Whether APIM API/operations/policies for backend services are managed by the foundation stack."
  type        = bool
  default     = false
}

variable "reuse_existing_container_app_environment" {
  description = "Whether to reuse an existing Container Apps Environment instead of managing it in this stack."
  type        = bool
  default     = false
}

variable "existing_container_app_environment_name" {
  description = "Optional existing Container Apps Environment name to reuse when reuse_existing_container_app_environment is true."
  type        = string
  default     = ""
}

variable "aca_vnet_integration_enabled" {
  description = "Whether the ACA environment is integrated with a VNet that can privately reach Cosmos DB."
  type        = bool
  default     = false
}

variable "aca_vnet_address_space" {
  description = "Address space for the VNet used by ACA private data-path components."
  type        = list(string)
  default     = ["10.40.0.0/16"]
}

variable "aca_infrastructure_subnet_cidr" {
  description = "CIDR for the ACA infrastructure subnet."
  type        = string
  default     = "10.40.0.0/23"
}

variable "cosmos_private_endpoint_subnet_cidr" {
  description = "CIDR for the subnet hosting the Cosmos DB private endpoint."
  type        = string
  default     = "10.40.2.0/24"
}

variable "cosmos_private_dns_zone_name" {
  description = "Private DNS zone for Cosmos DB private endpoint name resolution."
  type        = string
  default     = "privatelink.documents.azure.com"
}

variable "cosmos_public_network_access_enabled" {
  description = "Controls Cosmos DB public network access. Keep true until private connectivity is in place."
  type        = bool
  default     = true
}

variable "cosmos_lockout_acknowledged" {
  description = "Explicit acknowledgement required before disabling Cosmos public access."
  type        = bool
  default     = false
}

variable "cosmos_allowed_public_ip_ranges" {
  description = "Optional public IPv4/CIDR allowlist for Cosmos DB when public network access is enabled."
  type        = list(string)
  default     = []
}
