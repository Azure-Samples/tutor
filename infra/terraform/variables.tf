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

variable "cosmos_db_name" {
  description = "Cosmos DB SQL database name."
  type        = string
  default     = "tutor"
}

variable "project_endpoint" {
  description = "Azure AI Foundry project endpoint used by agentic services."
  type        = string
  default     = ""
}

variable "model_deployment_name" {
  description = "Default model deployment name used by services."
  type        = string
  default     = "gpt-4o"
}

variable "model_reasoning_deployment" {
  description = "Reasoning model deployment name used by services."
  type        = string
  default     = "o3-mini"
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
  }
}
