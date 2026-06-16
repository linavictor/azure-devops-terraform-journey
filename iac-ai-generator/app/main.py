from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.prompt_builder import build_prompt
from app.llm_client import call_llm
from app.code_parser import parse_terraform_output, validate_terraform_code, format_terraform_output
from app.cost_estimator import CostEstimator, AWSCostEstimator, GCPCostEstimator
from app.security_scanner import SecurityScanner, ComplianceChecker
import os
from pathlib import Path
import json

app = FastAPI(title="Terraform IaC AI Generator")

# Initialize cost estimators
azure_estimator = CostEstimator()
aws_estimator = AWSCostEstimator()
gcp_estimator = GCPCostEstimator()

# Initialize security scanner
security_scanner = SecurityScanner()
compliance_checker = ComplianceChecker()


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
    estimated_cost: dict = None
    security_scan: dict = None


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
        
        # Call LLM with fallback to mock mode
        try:
            llm_response = call_llm(prompt, model=req.model)
            print(f"✅ LLM Response received ({len(llm_response)} characters)")
        except ValueError as e:
            print(f"⚠️  {str(e)}")
            print(f"🔄 Using demo/mock mode instead...")
            llm_response = call_llm(prompt, model=req.model, use_mock=True)
        
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


@app.post("/generate-with-cost")
def generate_with_cost(req: TerraformRequest):
    """
    Generate Terraform code and estimate infrastructure costs.
    
    Returns generated code along with monthly/annual cost estimates.
    """
    response = generate_iac(req)
    
    if response.status == "success":
        # Select cost estimator based on cloud provider
        if req.cloud.lower() == "azure":
            estimator = azure_estimator
        elif req.cloud.lower() == "aws":
            estimator = aws_estimator
        elif req.cloud.lower() == "gcp":
            estimator = gcp_estimator
        else:
            estimator = azure_estimator
        
        # Estimate costs from the generated main.tf
        cost_estimate = estimator.estimate(response.main_tf)
        response.estimated_cost = cost_estimate
        
        print(f"\n💰 Cost Estimation for {req.cloud.upper()}:")
        print(f"   Monthly: ${cost_estimate.get('total_monthly_usd', 0)}")
        print(f"   Annual: ${cost_estimate.get('total_annual_usd', 0)}")
    
    return response


@app.post("/generate-with-security")
def generate_with_security(req: TerraformRequest):
    """
    Generate Terraform code and perform security scanning.
    
    Returns generated code with security vulnerabilities identified.
    """
    response = generate_iac(req)
    
    if response.status == "success":
        # Scan the main.tf for security issues
        scan_results = security_scanner.scan(response.main_tf, cloud=req.cloud)
        response.security_scan = scan_results
        
        # Print summary
        print(f"\n🔒 Security Scan Results for {req.cloud.upper()}:")
        print(f"   {scan_results['summary']}")
        print(f"   Compliance Score: {scan_results['compliance_score']}/100")
        print(f"   Total Issues: {scan_results['issues_found']}")
    
    return response


@app.post("/scan-security")
def scan_security(req: TerraformRequest):
    """
    Scan existing Terraform code for security issues.
    
    Useful for scanning previously generated or existing infrastructure code.
    """
    # For this endpoint, requirement should contain the Terraform code to scan
    scan_results = security_scanner.scan(req.requirement, cloud=req.cloud)
    
    return {
        "cloud": req.cloud,
        "scan_results": scan_results,
        "issues": scan_results["issues"],
        "compliance_score": scan_results["compliance_score"],
        "passed": scan_results["passed"]
    }


@app.post("/check-compliance")
def check_compliance(req: TerraformRequest):
    """
    Check compliance with security frameworks (CIS, HIPAA, PCI-DSS).
    
    First scans the code, then checks compliance with requested framework.
    """
    frameworks = ["cis", "hipaa", "pci_dss"]
    
    # Scan the code
    scan_results = security_scanner.scan(req.requirement, cloud=req.cloud)
    
    # Check compliance for each framework
    compliance_results = {}
    for framework in frameworks:
        compliance_results[framework] = compliance_checker.check_compliance(
            scan_results,
            framework=framework
        )
    
    return {
        "cloud": req.cloud,
        "scan_summary": scan_results["summary"],
        "compliance_scores": {
            framework: result.get("score", 0)
            for framework, result in compliance_results.items()
        },
        "frameworks": compliance_results,
        "overall_compliance": "COMPLIANT" if scan_results["compliance_score"] >= 80 else "NEEDS_IMPROVEMENT"
    }