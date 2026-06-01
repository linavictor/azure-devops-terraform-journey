provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_storage_account" "storage" {
  name                     = "storageaccount${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  shared_access_key_enabled        = false
  default_to_oauth_authentication = true

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

resource "random_string" "storage_suffix" {
  length  = 8
  special = false
  upper   = false
}