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

# Frontend infra stack placeholder. Add SWA-specific infra resources here when needed.
