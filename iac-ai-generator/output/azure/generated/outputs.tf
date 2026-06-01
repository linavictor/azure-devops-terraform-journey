output "resource_group_id" {
  value       = azurerm_resource_group.rg.id
  description = "The ID of the created Resource Group"
}

output "storage_account_id" {
  value       = azurerm_storage_account.storage.id
  description = "The ID of the created Storage Account"
}

output "storage_account_name" {
  value       = azurerm_storage_account.storage.name
  description = "The name of the created Storage Account"
}