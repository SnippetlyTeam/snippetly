variable "location" {
  description = "Azure region (e.g., westeurope)"
  type        = string
}

variable "resource_group_name" {
  description = "Azure Resource Group name"
  type        = string
  default     = "rg-snippetly"
}

variable "display_name_prefix" {
  description = "Prefix for created resources"
  type        = string
  default     = "snippetly"
}

variable "ssh_public_key" {
  description = "SSH public key content to access the VMs"
  type        = string
}

variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_B2ms"
  # Note: If Standard_B2ms is unavailable in your region, try:
  # Standard_B2als_v2, Standard_D2s_v3, Standard_DS2_v2, or Standard_B1ms (cheaper but less powerful)
}

variable "admin_username" {
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}

variable "vnet_cidr" {
  description = "VNet CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "Subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "allow_dev_ports" {
  description = "Whether to allow temporary dev ports 8000/5173 from the Internet"
  type        = bool
  default     = false
}

variable "repo_url" {
  description = "Git repo URL to clone on the VM"
  type        = string
  default     = "https://github.com/<your-org>/snippetly"
}

variable "backend_env_content_dev" {
  description = "Optional backend/.env content specifically for dev VM"
  type        = string
  default     = ""
}

variable "backend_env_content_prod" {
  description = "Optional backend/.env content specifically for prod VM"
  type        = string
  default     = ""
}

variable "storage_account_name" {
  description = "Azure Storage Account name (must be globally unique, 3-24 lowercase alphanumerics)"
  type        = string
}

variable "media_container_dev" {
  description = "Dev media container name"
  type        = string
  default     = "media-dev"
}

variable "media_container_prod" {
  description = "Prod media container name"
  type        = string
  default     = "media"
}

variable "backup_container_dev" {
  description = "Dev backup container name"
  type        = string
  default     = "backups-dev"
}

variable "backup_container_prod" {
  description = "Prod backup container name"
  type        = string
  default     = "backups"
}

variable "acr_name" {
  description = "Azure Container Registry name (3-50 alphanumerics)"
  type        = string
}
