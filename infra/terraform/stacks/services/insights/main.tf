terraform {
  required_version = ">= 1.9.0, < 2.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  storage_use_azuread = true
  features {}
}

variable "name_prefix" {
  type    = string
  default = "tutor"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "allowed_origins" {
  type        = list(string)
  default     = []
  description = "Additional CORS origins allowed by APIM in this service-edge stack."
}

data "azurerm_static_web_app" "frontend" {
  name                = "${var.name_prefix}-${var.environment}-frontend"
  resource_group_name = "${var.name_prefix}-${var.environment}"
}

locals {
  service_name              = "insights"
  swa_default_origin        = "https://${data.azurerm_static_web_app.frontend.default_host_name}"
  effective_allowed_origins = distinct(compact(concat(
    [local.swa_default_origin],
    var.allowed_origins,
  )))
}

module "service_edge" {
  source = "../../../modules/service-edge-apim"

  resource_group_name = "${var.name_prefix}-${var.environment}"
  api_management_name = "${var.name_prefix}-${var.environment}-apim"
  service_name        = local.service_name
  api_path            = "api/${local.service_name}"
  container_app_name  = "${var.name_prefix}-${local.service_name}-${var.environment}"
  allowed_origins     = local.effective_allowed_origins
}