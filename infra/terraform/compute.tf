locals {
  repo_url = var.repo_url
  username = var.admin_username

  backend_env_content_dev  = var.backend_env_content_dev
  backend_env_flag_dev     = var.backend_env_content_dev != "" ? "1" : ""
  backend_env_content_prod = var.backend_env_content_prod
  backend_env_flag_prod    = var.backend_env_content_prod != "" ? "1" : ""

  cloud_init_dev = templatefile("${path.module}/templates/cloud-init.sh.tftpl", {
    username            = local.username
    repo_url            = local.repo_url
    backend_env_content = local.backend_env_content_dev
    backend_env_flag    = local.backend_env_flag_dev
  })

  cloud_init_prod = templatefile("${path.module}/templates/cloud-init.sh.tftpl", {
    username            = local.username
    repo_url            = local.repo_url
    backend_env_content = local.backend_env_content_prod
    backend_env_flag    = local.backend_env_flag_prod
  })
}

resource "azurerm_public_ip" "dev" {
  name                = "${var.display_name_prefix}-dev-pip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_public_ip" "prod" {
  name                = "${var.display_name_prefix}-prod-pip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "dev" {
  name                = "${var.display_name_prefix}-dev-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.dev.id
  }
}

resource "azurerm_network_interface" "prod" {
  name                = "${var.display_name_prefix}-prod-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.prod.id
  }
}

resource "azurerm_network_interface_security_group_association" "dev" {
  network_interface_id      = azurerm_network_interface.dev.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_network_interface_security_group_association" "prod" {
  network_interface_id      = azurerm_network_interface.prod.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_linux_virtual_machine" "dev" {
  name                            = "${var.display_name_prefix}-dev-vm"
  location                        = azurerm_resource_group.rg.location
  resource_group_name             = azurerm_resource_group.rg.name
  size                            = var.vm_size
  admin_username                  = var.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.dev.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 100
  }

  custom_data = base64encode(local.cloud_init_dev)
}

resource "azurerm_linux_virtual_machine" "prod" {
  name                            = "${var.display_name_prefix}-prod-vm"
  location                        = azurerm_resource_group.rg.location
  resource_group_name             = azurerm_resource_group.rg.name
  size                            = var.vm_size
  admin_username                  = var.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.prod.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 100
  }

  custom_data = base64encode(local.cloud_init_prod)
}
