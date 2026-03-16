variable "resource_group_name" {
  type = string
}

variable "api_management_name" {
  type = string
}

variable "service_name" {
  type = string
}

variable "api_path" {
  type = string
}

variable "container_app_name" {
  type = string
}

variable "allowed_origins" {
  type        = list(string)
  default     = []
  description = "Additional CORS allowed origins (e.g. SWA hostname). Must be full URLs with scheme, host, and optional port."
}
