variable "resource_group_name" {
  type        = string
  description = "Name of the Azure Resource Group"
  default     = "rg-terraform-demo"
}

variable "location" {
  type        = string
  description = "Azure region for resources"
  default     = "East US"
}