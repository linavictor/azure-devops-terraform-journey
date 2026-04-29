output "aks_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "sql_server" {
  value = azurerm_mssql_server.sql.name
}

output "key_vault" {
  value = azurerm_key_vault.kv.name
}