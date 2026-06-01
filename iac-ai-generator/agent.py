#!/usr/bin/env python3
"""
🤖 Terraform AI Agent - Interactive CLI for generating Terraform code from prompts

Usage:
    python agent.py "create a secure AKS cluster" --cloud azure
    python agent.py "setup RDS database" --cloud aws
    python agent.py "create cloud storage" --cloud gcp
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.prompt_builder import build_prompt
from app.llm_client import call_llm
from app.code_parser import parse_terraform_output, validate_terraform_code, format_terraform_output


class TerraformAgent:
    """AI-powered agent for generating Terraform code from natural language prompts"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the Terraform agent"""
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
        self.model = model or os.getenv('LLM_MODEL', 'mistralai/mistral-7b-instruct')
        
        if not self.api_key:
            print("⚠️  Warning: No API key found!")
            print("   Set OPENROUTER_API_KEY or LLM_API_KEY environment variable")
            print("   Visit: https://openrouter.ai to get your API key\n")
    
    def generate(self, requirement: str, cloud: str = "azure") -> dict:
        """
        Generate Terraform code from a requirement.
        
        Args:
            requirement: Natural language requirement
            cloud: Cloud provider (azure, aws, gcp)
        
        Returns:
            Dictionary with generated Terraform code
        """
        cloud = cloud.lower()
        
        if cloud not in ["azure", "aws", "gcp"]:
            raise ValueError(f"Invalid cloud provider: {cloud}. Use: azure, aws, or gcp")
        
        print(f"\n{'='*70}")
        print(f"🚀 Terraform AI Agent - Code Generation")
        print(f"{'='*70}")
        print(f"☁️  Cloud Provider: {cloud.upper()}")
        print(f"📝 Requirement: {requirement}")
        print(f"🤖 Model: {self.model}")
        print(f"{'='*70}\n")
        
        try:
            # Build prompt
            prompt = build_prompt(requirement, cloud)
            
            # Call LLM
            print("🔄 Calling AI model...")
            
            # Try real API first
            try:
                llm_response = call_llm(prompt, model=self.model, use_mock=False)
                print(f"✅ Received {len(llm_response)} characters from LLM\n")
            except Exception as api_error:
                print(f"⚠️  Real API unavailable: {str(api_error)[:50]}...")
                print(f"🔄 Using demo/mock mode instead...\n")
                llm_response = call_llm(prompt, model=self.model, use_mock=True)
                print(f"✅ Generated demo Terraform code ({len(llm_response)} characters)\n")
            
            # Parse output
            parsed_code = parse_terraform_output(llm_response)
            
            # Validate
            validation = {
                "main.tf": validate_terraform_code(parsed_code["main.tf"], "main.tf"),
                "variables.tf": validate_terraform_code(parsed_code["variables.tf"], "variables.tf"),
                "outputs.tf": validate_terraform_code(parsed_code["outputs.tf"], "outputs.tf"),
            }
            
            return {
                "success": True,
                "requirement": requirement,
                "cloud": cloud,
                "parsed_code": parsed_code,
                "validation": validation,
                "raw_response": llm_response
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "requirement": requirement,
                "cloud": cloud
            }
    
    def display_results(self, results: dict, save_files: bool = True):
        """Display generated Terraform code in a formatted way"""
        
        if not results.get("success"):
            print(f"❌ Error: {results.get('error', 'Unknown error')}")
            return
        
        parsed_code = results["parsed_code"]
        validation = results["validation"]
        
        # Display validation status
        print("📋 Validation Results:")
        print(f"   ✓ main.tf: {'✅ Valid' if validation['main.tf'] else '⚠️  Missing'}")
        print(f"   ✓ variables.tf: {'✅ Valid' if validation['variables.tf'] else '⚠️  Missing'}")
        print(f"   ✓ outputs.tf: {'✅ Valid' if validation['outputs.tf'] else '⚠️  Missing'}\n")
        
        # Display formatted code
        formatted = format_terraform_output(parsed_code)
        print(formatted)
        
        # Save files if requested
        if save_files:
            self.save_files(parsed_code, results["cloud"])
    
    def save_files(self, parsed_code: dict, cloud: str) -> str:
        """Save generated Terraform files"""
        output_dir = Path(__file__).parent / "output" / cloud / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"💾 Saving Terraform Files")
        print(f"{'='*70}\n")
        
        for file_name, content in parsed_code.items():
            if content.strip():
                file_path = output_dir / file_name
                file_path.write_text(content)
                print(f"✅ Created: {file_path}")
        
        print(f"\n📍 Output directory: {output_dir}\n")
        return str(output_dir)


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="🤖 Terraform AI Agent - Generate Terraform code from natural language prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "create a secure AKS cluster in Azure" --cloud azure
  python agent.py "setup RDS database with encryption" --cloud aws
  python agent.py "create cloud storage bucket" --cloud gcp
  python agent.py "create VPC and subnets" --cloud aws --no-save
        """
    )
    
    parser.add_argument(
        "requirement",
        nargs="?",
        help="Natural language requirement for Terraform infrastructure"
    )
    parser.add_argument(
        "--cloud",
        default="azure",
        choices=["azure", "aws", "gcp"],
        help="Cloud provider (default: azure)"
    )
    parser.add_argument(
        "--model",
        help="LLM model to use (default: mistralai/mistral-7b-instruct)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save generated files"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode - prompt for requirement if not provided"
    )
    parser.add_argument(
        "--api-key",
        help="LLM API key (or set OPENROUTER_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get requirement
    requirement = args.requirement
    if not requirement:
        if args.interactive:
            print("🤖 Terraform AI Agent - Interactive Mode\n")
            requirement = input("📝 Enter your Terraform requirement: ").strip()
        else:
            parser.print_help()
            sys.exit(1)
    
    # Create agent
    agent = TerraformAgent(api_key=args.api_key, model=args.model)
    
    # Generate Terraform code
    results = agent.generate(requirement, cloud=args.cloud)
    
    # Display results
    agent.display_results(results, save_files=not args.no_save)
    
    return 0 if results.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
