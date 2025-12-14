# Remote state backend configuration for Azure Storage
#
# Prerequisites:
# 1. Create storage account manually (one-time):
#    az group create --name snippetly-tfstate-rg --location westeurope
#    az storage account create \
#      --name snippetlytfstate \
#      --resource-group snippetly-tfstate-rg \
#      --location westeurope \
#      --sku Standard_LRS \
#      --encryption-services blob
#    az storage container create \
#      --name tfstate \
#      --account-name snippetlytfstate
#
# 2. Initialize Terraform with backend:
#    terraform init -migrate-state
#
# Benefits:
# - State stored securely in Azure Blob Storage
# - State locking prevents concurrent modifications
# - Team collaboration without conflicts
# - State versioning and backup

terraform {
  backend "azurerm" {
    resource_group_name  = "snippetly-tfstate-rg"
    storage_account_name = "snippetlytfstate"
    container_name       = "tfstate"
    key                  = "snippetly.tfstate"

    # State locking enabled by default in Azure Storage
    # Encryption at rest enabled by default
  }
}
