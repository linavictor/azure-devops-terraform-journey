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