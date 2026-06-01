from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.prompt_builder import build_prompt
from app.llm_client import call_llm
from app.code_parser import parse_terraform_output, validate_terraform_code, format_terraform_output
import os
from pathlib import Path
import json

app = FastAPI(title="Terraform IaC AI Generator")


class TerraformRequest(BaseModel):
    """Request model for Terraform code generation"""
    requirement: str
    cloud: str = "azure"
    model: str = None
    save_output: bool = True


class TerraformResponse(BaseModel):
    """Response model for generated Terraform code"""
    status: str
    requirement: str
    cloud: str
    main_tf: str
    variables_tf: str
    outputs_tf: str
    parsed_successfully: bool
    output_path: str = None


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "IaC AI Generator API is active",
        "version": "2.0",
        "endpoints": {
            "generate": "POST /generate",
            "health": "GET /",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "Terraform IaC Generator",
        "version": "2.0"
    }


@app.post("/generate", response_model=TerraformResponse)
def generate_iac(req: TerraformRequest):
    """
    Generate Terraform code from natural language requirement.
    
    Args:
        req: TerraformRequest with requirement, cloud provider, optional model
    
    Returns:
        TerraformResponse with generated Terraform code
    """
    try:
        # Validate cloud provider
        cloud = req.cloud.lower()
        if cloud not in ["azure", "aws", "gcp"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported cloud provider: {cloud}. Use: azure, aws, or gcp"
            )
        
        # Build the prompt
        prompt = build_prompt(req.requirement, cloud)
        
        print(f"\n🚀 Generating Terraform code for {cloud.upper()}...")
        print(f"📝 Requirement: {req.requirement[:100]}...")
        
        # Call LLM
        llm_response = call_llm(prompt, model=req.model)
        
        print(f"✅ LLM Response received ({len(llm_response)} characters)")
        
        # Parse the output
        parsed_code = parse_terraform_output(llm_response)
        
        # Validate each file
        validation = {
            "main.tf": validate_terraform_code(parsed_code["main.tf"], "main.tf"),
            "variables.tf": validate_terraform_code(parsed_code["variables.tf"], "variables.tf"),
            "outputs.tf": validate_terraform_code(parsed_code["outputs.tf"], "outputs.tf"),
        }
        
        parsed_successfully = all(validation.values())
        
        print(f"✓ Validation: main.tf={validation['main.tf']}, variables.tf={validation['variables.tf']}, outputs.tf={validation['outputs.tf']}")
        
        # Save to output directory if requested
        output_path = None
        if req.save_output:
            output_path = save_terraform_files(parsed_code, cloud)
            print(f"💾 Files saved to: {output_path}")
        
        return TerraformResponse(
            status="success",
            requirement=req.requirement,
            cloud=cloud,
            main_tf=parsed_code["main.tf"],
            variables_tf=parsed_code["variables.tf"],
            outputs_tf=parsed_code["outputs.tf"],
            parsed_successfully=parsed_successfully,
            output_path=output_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def save_terraform_files(parsed_code: dict, cloud: str) -> str:
    """
    Save generated Terraform files to the output directory.
    
    Args:
        parsed_code: Dictionary with main.tf, variables.tf, outputs.tf content
        cloud: Cloud provider name
    
    Returns:
        Path to the created output directory
    """
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output" / cloud
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save each file
    for file_name, content in parsed_code.items():
        if content.strip():
            file_path = output_dir / file_name
            file_path.write_text(content)
            print(f"  ✓ Created: {file_path}")
    
    # Save metadata
    metadata = {
        "cloud": cloud,
        "files": ["main.tf", "variables.tf", "outputs.tf"]
    }
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    
    return str(output_dir)


@app.post("/generate-and-format")
def generate_formatted(req: TerraformRequest):
    """
    Generate Terraform code and return formatted for display.
    """
    response = generate_iac(req)
    
    formatted = format_terraform_output({
        "main.tf": response.main_tf,
        "variables.tf": response.variables_tf,
        "outputs.tf": response.outputs_tf
    })
    
    return {
        "status": response.status,
        "requirement": response.requirement,
        "cloud": response.cloud,
        "formatted_output": formatted,
        "parsed_successfully": response.parsed_successfully,
        "output_path": response.output_path
    }

  value = azurerm_resource_group.rg.name
}
"""

    elif cloud == "aws":
        terraform_code = """
// main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

// outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}
"""

    elif cloud == "gcp":
        terraform_code = """
// main.tf
provider "google" {
  project = "demo-project"
  region  = "us-central1"
}

resource "google_compute_network" "vpc_network" {
  name = "demo-network"
}

// outputs.tf
output "network_name" {
  value = google_compute_network.vpc_network.name
}
"""

    # ---------------------------------------------------
    # ✅ Write Terraform files
    # ---------------------------------------------------

    os.makedirs("output", exist_ok=True)

    sections = terraform_code.split("//")

    files = {
        "main.tf": "",
        "variables.tf": "",
        "outputs.tf": ""
    }

    for section in sections:
        if "main.tf" in section:
            files["main.tf"] = section.replace("main.tf", "").strip()
        elif "variables.tf" in section:
            files["variables.tf"] = section.replace("variables.tf", "").strip()
        elif "outputs.tf" in section:
            files["outputs.tf"] = section.replace("outputs.tf", "").strip()

    for filename, content in files.items():
        if content:  # ✅ avoid empty files
            with open(f"output/{filename}", "w") as f:
                f.write(content)

    return {
        "message": f"Terraform generated for {cloud}",
        "files": list(files.keys())
    }