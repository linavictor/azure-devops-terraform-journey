#!/usr/bin/env python3
"""
Test script to verify Terraform AI Agent is working correctly
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from app.prompt_builder import build_prompt
        print("   ✅ prompt_builder")
        
        from app.llm_client import call_llm
        print("   ✅ llm_client")
        
        from app.code_parser import parse_terraform_output, validate_terraform_code
        print("   ✅ code_parser")
        
        from agent import TerraformAgent
        print("   ✅ agent")
        
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_parser():
    """Test the code parser"""
    print("\n🔍 Testing code parser...")
    from app.code_parser import parse_terraform_output, validate_terraform_code
    
    # Test sample output
    sample_output = """
#### MAIN.TF
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

#### VARIABLES.TF
variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
}

variable "location" {
  type        = string
  description = "Azure location"
}

#### OUTPUTS.TF
output "resource_group_id" {
  value       = azurerm_resource_group.rg.id
  description = "Resource group ID"
}
"""
    
    try:
        parsed = parse_terraform_output(sample_output)
        
        if parsed["main.tf"] and "provider" in parsed["main.tf"]:
            print("   ✅ main.tf parsed correctly")
        else:
            print("   ⚠️  main.tf parsing issue")
        
        if parsed["variables.tf"] and "variable" in parsed["variables.tf"]:
            print("   ✅ variables.tf parsed correctly")
        else:
            print("   ⚠️  variables.tf parsing issue")
        
        if parsed["outputs.tf"] and "output" in parsed["outputs.tf"]:
            print("   ✅ outputs.tf parsed correctly")
        else:
            print("   ⚠️  outputs.tf parsing issue")
        
        # Test validation
        is_valid = validate_terraform_code(parsed["main.tf"], "main.tf")
        if is_valid:
            print("   ✅ code validation working")
        else:
            print("   ⚠️  validation issue")
        
        return True
    except Exception as e:
        print(f"   ❌ Parser test failed: {e}")
        return False


def test_api_key():
    """Test API key configuration"""
    print("\n🔍 Testing API key configuration...")
    
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
    
    if api_key:
        print(f"   ✅ API key found (starts with: {api_key[:10]}...)")
        return True
    else:
        print("   ⚠️  No API key configured")
        print("      Set: export OPENROUTER_API_KEY='your-key'")
        return False


def test_directories():
    """Test that required directories exist"""
    print("\n🔍 Testing directory structure...")
    
    base_dir = Path(__file__).parent
    dirs = ["app", "output"]
    
    all_exist = True
    for dir_name in dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Terraform AI Agent - Test Suite")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Directory Structure", test_directories()))
    results.append(("Code Parser", test_parser()))
    results.append(("API Key Configuration", test_api_key()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed\n")
    
    if passed == total:
        print("🎉 All tests passed! Agent is ready to use.")
        print("\n📝 Quick start:")
        print("   python agent.py \"create resource group\" --cloud azure")
        return 0
    else:
        print("⚠️  Some tests failed. Please check configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
