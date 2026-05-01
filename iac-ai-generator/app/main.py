from fastapi import FastAPI
from pydantic import BaseModel
from app.prompt_builder import build_prompt
from app.llm_client import call_llm
import os

app = FastAPI()


# -------- Request Model --------
class Request(BaseModel):
    requirement: str


# -------- Home Route --------
@app.get("/")
def home():
    return {"message": "AI Terraform Generator running 🚀"}


# -------- Clean AI Output --------
def clean_code(code: str):
    lines = code.splitlines()
    cleaned = []

    for line in lines:
        if "```" in line:
            continue
        if line.strip() == "":
            continue
        cleaned.append(line)

    return "\n".join(cleaned)


# -------- Fallback Terraform --------
def fallback_code():
    return """
// main.tf
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

// variables.tf
variable "resource_group_name" {
  type = string
}

variable "location" {
  type    = string
  default = "East US"
}

variable "tags" {
  type = map(string)
  default = {
    environment = "dev"
    project     = "iac-ai"
  }
}

// outputs.tf
output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}
"""


# -------- Enterprise AKS Template --------
def aks_template():
    return """
// main.tf
provider "azurerm" {
  features {}
}

# ---------------- RESOURCE GROUP ----------------
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ---------------- VNET ----------------
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.prefix}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.tags
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "private_endpoint_subnet" {
  name                 = "private-endpoint-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

# ---------------- AKS ----------------
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.prefix}-aks"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "${var.prefix}-dns"

  private_cluster_enabled = true

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name           = "default"
    node_count     = var.node_count
    vm_size        = "Standard_DS2_v2"
    vnet_subnet_id = azurerm_subnet.aks_subnet.id
  }

  network_profile {
    network_plugin     = "azure"
    load_balancer_sku  = "standard"
  }

  tags = var.tags
}

# ---------------- KEY VAULT ----------------
resource "azurerm_key_vault" "kv" {
  name                        = "${var.prefix}-kv"
  location                    = var.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = var.tenant_id
  sku_name                    = "standard"

  purge_protection_enabled    = true
  soft_delete_retention_days  = 7

  public_network_access_enabled = false

  tags = var.tags
}

# ---------------- SQL ----------------
resource "azurerm_mssql_server" "sql" {
  name                         = "${var.prefix}-sql"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_password

  public_network_access_enabled = false

  tags = var.tags
}

resource "azurerm_mssql_database" "db" {
  name      = "appdb"
  server_id = azurerm_mssql_server.sql.id
  sku_name  = "S0"
}

# ---------------- PRIVATE DNS ----------------
resource "azurerm_private_dns_zone" "sql_dns" {
  name                = "privatelink.database.windows.net"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone" "kv_dns" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "sql_link" {
  name                  = "sql-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.sql_dns.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}

resource "azurerm_private_dns_zone_virtual_network_link" "kv_link" {
  name                  = "kv-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.kv_dns.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}

# ---------------- PRIVATE ENDPOINT (SQL) ----------------
resource "azurerm_private_endpoint" "sql_pe" {
  name                = "sql-private-endpoint"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "sql-connection"
    private_connection_resource_id = azurerm_mssql_server.sql.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }
}

# ---------------- PRIVATE ENDPOINT (KEY VAULT) ----------------
resource "azurerm_private_endpoint" "kv_pe" {
  name                = "kv-private-endpoint"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "kv-connection"
    private_connection_resource_id = azurerm_key_vault.kv.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
}

// variables.tf
variable "resource_group_name" {
  type = string
}

variable "location" {
  default = "East US"
}

variable "prefix" {
  default = "secureaks"
}

variable "node_count" {
  default = 2
}

variable "tenant_id" {
  type = string
}

variable "sql_admin" {
  type = string
}

variable "sql_password" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
  default = {
    environment = "dev"
    project     = "iac-ai"
  }
}

// outputs.tf
output "aks_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "sql_server" {
  value = azurerm_mssql_server.sql.name
}

output "key_vault" {
  value = azurerm_key_vault.kv.name
}
"""


# -------- Main API --------
@app.post("/generate")
def generate_iac(req: Request, cloud: str):

    print("Request:", req.requirement, cloud)

    prompt = build_prompt(req.requirement, cloud)
    req_text = req.requirement.lower()

    # -------- Smart Routing --------
    if "aks" in req_text:
        print("Using AKS enterprise template")
        terraform_code = aks_template()
    else:
        try:
            terraform_code = call_llm(prompt)
            terraform_code = clean_code(terraform_code)
        except Exception as e:
            print("LLM ERROR:", e)
            terraform_code = ""

    # -------- Fallback --------
    if not terraform_code or "main.tf" not in terraform_code:
        print("Using fallback Terraform")
        terraform_code = fallback_code()

    # -------- Create Output Folder --------
    os.makedirs("output", exist_ok=True)

    # -------- Split Files --------
    files = {}
    current_file = None

    for line in terraform_code.splitlines():
        if line.startswith("//"):
            current_file = line.replace("//", "").strip()
            files[current_file] = ""
        else:
            if current_file:
                files[current_file] += line + "\n"

    # -------- Write Files --------
    for filename, content in files.items():
        with open(f"output/{filename}", "w") as f:
            f.write(content.strip())

        print(f"Created: output/{filename}")

    return {
        "message": "Terraform generated ✅",
        "files": list(files.keys())
    }