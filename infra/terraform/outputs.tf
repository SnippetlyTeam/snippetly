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

# Все, що треба для DEV GitHub Actions, крім чутливих речей
output "github_dev_secrets" {
  description = "Values for GitHub Actions secrets (Dev)"
  value = {
    DEV_ACR_LOGIN_SERVER = azurerm_container_registry.acr.login_server

    # IP і юзер dev VM
    DEV_SSH_HOST = azurerm_public_ip.dev.ip_address
    DEV_SSH_USER = azurerm_linux_virtual_machine.dev.admin_username

    # Зручно, щоб руками скопіпастити в DEV_PUBLIC_URL, якщо немає домену
    DEV_PUBLIC_URL = "http://${azurerm_public_ip.dev.ip_address}"

    # storage, якщо захочеш використати його в GitHub або десь ще
    DEV_STORAGE_ACCOUNT_NAME = azurerm_storage_account.sa.name
    DEV_MEDIA_CONTAINER      = azurerm_storage_container.media_dev.name
    DEV_BACKUP_CONTAINER     = azurerm_storage_container.backup_dev.name
  }

  sensitive = true
}

output "github_prod_secrets" {
  description = "Values for GitHub Actions secrets (Prod)"
  value = {
    PROD_ACR_LOGIN_SERVER = azurerm_container_registry.acr.login_server

    # IP і юзер prod VM
    PROD_SSH_HOST = azurerm_public_ip.prod.ip_address
    PROD_SSH_USER = azurerm_linux_virtual_machine.prod.admin_username

    # For production, use HTTPS domain instead of IP
    # Set this manually in GitHub Secrets as: https://snippetly.codes
    PROD_PUBLIC_URL = "https://snippetly.codes"

    PROD_STORAGE_ACCOUNT_NAME = azurerm_storage_account.sa.name
    PROD_MEDIA_CONTAINER      = azurerm_storage_container.media_prod.name
    PROD_BACKUP_CONTAINER     = azurerm_storage_container.backup_prod.name
  }

  sensitive = true
}
