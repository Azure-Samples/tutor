terraform {
  required_version = ">= 1.9.0, < 2.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.4"
    }
  }
}

provider "azurerm" {
  storage_use_azuread = true
  features {}
}

provider "azapi" {}
