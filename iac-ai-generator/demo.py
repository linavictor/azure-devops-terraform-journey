#!/usr/bin/env python3
"""
Demo script showing how to use the Terraform AI Agent
"""

import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import TerraformAgent


def demo():
    """Run demo examples"""
    
    print("\n" + "="*70)
    print("🎬 Terraform AI Agent - Demo")
    print("="*70 + "\n")
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
    
    if not api_key:
        print("⚠️  No API key found!")
        print("\n   To use this demo, you need to:")
        print("   1. Get an API key from https://openrouter.ai")
        print("   2. Set it as environment variable:")
        print("\n      export OPENROUTER_API_KEY='your-api-key'")
        print("\n   Then run this demo again.")
        return
    
    print("✅ API Key configured\n")
    
    # Example prompts for each cloud
    examples = {
        "azure": [
            "Create a resource group with a virtual network",
            "Setup a secure AKS cluster with monitoring",
            "Deploy Azure App Service with SQL database"
        ],
        "aws": [
            "Create VPC with public and private subnets",
            "Setup RDS database with automated backups",
            "Create S3 bucket with encryption and versioning"
        ],
        "gcp": [
            "Create a GCP project with Cloud Storage",
            "Deploy GKE cluster with autoscaling",
            "Setup Cloud SQL PostgreSQL instance"
        ]
    }
    
    print("📚 Example Prompts:\n")
    
    for cloud, prompts in examples.items():
        print(f"☁️  {cloud.upper()}:")
        for i, prompt in enumerate(prompts, 1):
            print(f"   {i}. {prompt}")
        print()
    
    print("\n" + "="*70)
    print("🚀 Quick Start Commands:")
    print("="*70 + "\n")
    
    print("# Azure - Create resource group")
    print("python agent.py \"Create a resource group with virtual network\" --cloud azure\n")
    
    print("# AWS - Create VPC")
    print("python agent.py \"Create VPC with subnets and NAT gateway\" --cloud aws\n")
    
    print("# GCP - Create storage")
    print("python agent.py \"Create Cloud Storage bucket with encryption\" --cloud gcp\n")
    
    print("# Interactive mode")
    print("python agent.py --interactive\n")
    
    print("# View help")
    print("python agent.py --help\n")


if __name__ == "__main__":
    demo()
