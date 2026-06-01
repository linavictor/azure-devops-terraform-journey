import requests
import os
import json

def call_llm(prompt: str, model: str = None, use_mock: bool = False):
    """
    Call LLM API to generate Terraform code.
    Supports both OpenRouter and direct API calls.
    
    Args:
        prompt: The prompt to send to LLM
        model: Optional model override
        use_mock: If True, return mock Terraform code (for testing)
    """
    if use_mock:
        return get_mock_terraform_code(prompt)
    
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Set OPENROUTER_API_KEY or LLM_API_KEY environment variable.")
    
    if not model:
        model = os.getenv('LLM_MODEL', 'mistralai/mistral-7b-instruct')
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://terraform-agent.local",
        "X-Title": "Terraform Agent",
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": """You are an expert Terraform engineer. Generate production-ready Terraform code.
                
Instructions:
- Output ONLY valid HCL code
- Include main.tf, variables.tf, and outputs.tf content
- Add comments for clarity
- Use best practices and security defaults
- Format code properly with 2-space indentation"""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        print(f"  Connecting to {url}...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Unexpected LLM response: {result}")
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"  ⚠️  API Error: {error_msg}")
        print(f"  💡 Tip: Verify your API key is valid at https://openrouter.ai")
        raise RuntimeError(f"LLM API call failed: {error_msg}")


def get_mock_terraform_code(requirement: str) -> str:
    """Generate mock Terraform code for testing"""
    return """
#### MAIN.TF
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_storage_account" "storage" {
  name                     = "storageaccount${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  shared_access_key_enabled        = false
  default_to_oauth_authentication = true

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}

resource "random_string" "storage_suffix" {
  length  = 8
  special = false
  upper   = false
}

#### VARIABLES.TF
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

#### OUTPUTS.TF
output "resource_group_id" {
  value       = azurerm_resource_group.rg.id
  description = "The ID of the created Resource Group"
}

output "storage_account_id" {
  value       = azurerm_storage_account.storage.id
  description = "The ID of the created Storage Account"
}

output "storage_account_name" {
  value       = azurerm_storage_account.storage.name
  description = "The name of the created Storage Account"
}
"""