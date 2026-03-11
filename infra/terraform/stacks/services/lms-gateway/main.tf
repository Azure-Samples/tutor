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

locals {
  service_name = "lms-gateway"
}

# No-op change to trigger service-edge stack reconciliation in CI.

module "service_edge" {
  source = "../../../modules/service-edge-apim"

  resource_group_name = "${var.name_prefix}-${var.environment}"
  api_management_name = "${var.name_prefix}-${var.environment}-apim"
  service_name        = local.service_name
  api_path            = "api/${local.service_name}"
  container_app_name  = "${var.name_prefix}-${local.service_name}-${var.environment}"
}
