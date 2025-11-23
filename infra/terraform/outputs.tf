output "dev_vm_public_ip" {
  description = "Public IP of the dev VM"
  value       = azurerm_public_ip.dev.ip_address
}

output "prod_vm_public_ip" {
  description = "Public IP of the prod VM"
  value       = azurerm_public_ip.prod.ip_address
}

output "storage_account_name" {
  value = azurerm_storage_account.sa.name
}

output "media_containers" {
  value = {
    dev  = azurerm_storage_container.media_dev.name
    prod = azurerm_storage_container.media_prod.name
  }
}

output "backup_containers" {
  value = {
    dev  = azurerm_storage_container.backup_dev.name
    prod = azurerm_storage_container.backup_prod.name
  }
}

output "acr_login_server" {
  description = "ACR login server hostname"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_name" {
  value = azurerm_container_registry.acr.name
}

output "backend_image_repo" {
  value = "${azurerm_container_registry.acr.login_server}/snippetly-backend"
}

output "frontend_image_repo" {
  value = "${azurerm_container_registry.acr.login_server}/snippetly-frontend"
}

output "registry" {
  description = "Container registry hostname"
  value       = azurerm_container_registry.acr.login_server
}
