location            = "westeurope"
resource_group_name = "rg-snippetly"

# SSH public key to access VMs
ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ4izvdjs8+Rp7QIAIlgKPZVA81mqczyqemHHx7Zs//1 illia-mac"

# VM size and admin user
vm_size        = "Standard_B2ms"
admin_username = "azureuser"

# Networking
vnet_cidr       = "10.0.0.0/16"
subnet_cidr     = "10.0.1.0/24"
allow_dev_ports = false

# Repository to clone on VMs
repo_url = "https://github.com/SnippetlyTeam/snippetly"

# Optional: per-env backend .env content injected by cloud-init
backend_env_content_dev  = ""
backend_env_content_prod = ""

# Azure Storage Account and containers (must be globally unique)
storage_account_name  = "snippetlystor12345"
media_container_dev   = "media-dev"
media_container_prod  = "media"
backup_container_dev  = "backups-dev"
backup_container_prod = "backups"

# Azure Container Registry (ACR)
acr_name = "snippetlyacr"
