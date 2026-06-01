# 🤖 Terraform AI Agent - Usage Guide

## Overview

The Terraform AI Agent is a powerful tool that generates production-ready Terraform infrastructure code from natural language descriptions. You can use it as a CLI tool or as a Python module in your applications.

## Quick Setup

### 1. Get an API Key

1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up and get your API key
3. Add to environment:

```bash
export OPENROUTER_API_KEY="your-key-here"
```

### 2. Install Dependencies

```bash
cd iac-ai-generator
pip install -r requirements.txt
```

## Usage Methods

### Method 1: CLI Agent (Simplest)

```bash
# Basic usage
python agent.py "create Azure storage account" --cloud azure

# AWS example
python agent.py "setup RDS database" --cloud aws

# GCP example  
python agent.py "create GCS bucket" --cloud gcp

# Interactive mode
python agent.py --interactive

# Don't save files
python agent.py "create VPC" --cloud aws --no-save

# Use specific model
python agent.py "create cluster" --model openai/gpt-4 --cloud azure
```

### Method 2: REST API

Start the server:

```bash
uvicorn app.main:app --reload
```

Then use the API:

```bash
# Generate Terraform
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Create AKS cluster",
    "cloud": "azure"
  }'

# Get formatted output
curl -X POST "http://localhost:8000/generate-and-format" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Create security group",
    "cloud": "aws"
  }'
```

### Method 3: Python Module

```python
from agent import TerraformAgent

# Create agent
agent = TerraformAgent()

# Generate code
results = agent.generate(
    "Create production AKS cluster",
    cloud="azure"
)

# Display results
agent.display_results(results)

# Access individual components
if results["success"]:
    main_tf = results["parsed_code"]["main.tf"]
    variables_tf = results["parsed_code"]["variables.tf"]
    outputs_tf = results["parsed_code"]["outputs.tf"]
```

## Common Use Cases

### 1. Quick Prototyping

```bash
# Rapidly generate infrastructure templates
python agent.py "AWS infrastructure: VPC, subnets, security groups, ALB" --cloud aws
```

### 2. Learning Terraform

```bash
# Generate examples for specific resources
python agent.py "Create Azure App Service with managed identity" --cloud azure

# Study the generated code
cat output/azure/generated/main.tf
```

### 3. Automation

```python
# Generate code in CI/CD pipeline
from agent import TerraformAgent

agent = TerraformAgent()
for requirement in requirements_list:
    results = agent.generate(requirement, cloud="azure")
    if results["success"]:
        # Process generated code
        pass
```

### 4. Multi-Cloud Strategy

```bash
# Generate for multiple clouds
python agent.py "Database cluster with backups" --cloud azure
python agent.py "Database cluster with backups" --cloud aws
python agent.py "Database cluster with backups" --cloud gcp

# Compare implementations across clouds
diff output/azure/generated/main.tf output/aws/generated/main.tf
```

## Prompt Tips

### Be Specific

❌ **Bad**: "Create database"
✅ **Good**: "Create production-grade PostgreSQL database with automatic backups, encryption at rest, and high availability"

### Include Requirements

❌ **Bad**: "Create cluster"
✅ **Good**: "Create Kubernetes cluster with 3 worker nodes, monitoring enabled, RBAC, and auto-scaling"

### Mention Security

```bash
# Security is important
python agent.py "Create secure S3 bucket with encryption, versioning, and MFA delete protection" --cloud aws
```

### Include Best Practices

```bash
# Request best practices
python agent.py "Create VPC with public/private subnets following AWS best practices" --cloud aws
```

## Advanced Features

### Custom Models

```bash
# Use GPT-4 for better quality
python agent.py "Create AKS cluster" --cloud azure --model openai/gpt-4

# Use fast and cheap model
python agent.py "Create storage" --cloud aws --model mistralai/mistral-7b-instruct
```

### Output Management

```bash
# Generate without saving
python agent.py "Create resource" --cloud azure --no-save

# Save to custom location (modify code)
# Edit agent.py save_files() method
```

### Batch Processing

```python
from agent import TerraformAgent

agent = TerraformAgent()

requirements = [
    ("Create VPC", "aws"),
    ("Create resource group", "azure"),
    ("Create project", "gcp"),
]

for req, cloud in requirements:
    results = agent.generate(req, cloud=cloud)
    agent.display_results(results)
```

## Output Structure

Generated files are organized as:

```
output/
├── azure/
│   └── generated/
│       ├── main.tf          # Provider and resources
│       ├── variables.tf     # Input variables
│       ├── outputs.tf       # Output values
│       └── metadata.json    # Generation metadata
├── aws/
│   └── generated/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── gcp/
    └── generated/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Using Generated Code

### 1. Review

```bash
cd output/azure/generated
cat main.tf
cat variables.tf
```

### 2. Customize

Edit files to match your specific requirements:

```bash
nano main.tf          # Edit resources
nano variables.tf     # Adjust variables
nano outputs.tf       # Modify outputs
```

### 3. Initialize Terraform

```bash
terraform init
terraform validate
terraform plan -out=tfplan
```

### 4. Apply

```bash
terraform apply tfplan
```

## Troubleshooting

### No API Key Error

```bash
# Verify key is set
echo $OPENROUTER_API_KEY

# If empty, set it
export OPENROUTER_API_KEY="sk-or-..."
```

### LLM Call Failed

Check:
- Internet connection
- API key validity
- OpenRouter service status
- Rate limits

### Bad Code Generated

- Try with different model: `--model openai/gpt-4`
- Make prompt more specific
- Review and edit generated code manually

### Module Import Error

```bash
# Ensure you're in correct directory
cd iac-ai-generator

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Environment Variables

```bash
# API Configuration
OPENROUTER_API_KEY="sk-or-..."          # Your API key
LLM_API_KEY="sk-or-..."                 # Alternative key
LLM_MODEL="mistralai/mistral-7b-instruct"  # Model to use

# Server Configuration  
HOST="0.0.0.0"
PORT="8000"

# Python Path
PYTHONPATH="/path/to/iac-ai-generator"
```

## Examples by Cloud

### Azure Examples

```bash
# Resource Group
python agent.py "Create resource group in East US" --cloud azure

# AKS Cluster
python agent.py "Create AKS cluster with system and user node pools" --cloud azure

# App Service
python agent.py "Create App Service with SQL database and Application Insights" --cloud azure

# Storage Account
python agent.py "Create storage account with blob, table, queue services and lifecycle policy" --cloud azure
```

### AWS Examples

```bash
# VPC
python agent.py "Create VPC with public/private subnets across 3 AZs" --cloud aws

# RDS
python agent.py "Create RDS MySQL database with Multi-AZ, automated backups, and encryption" --cloud aws

# Lambda
python agent.py "Create Lambda function with API Gateway, CloudWatch logs, and IAM role" --cloud aws

# S3
python agent.py "Create S3 bucket with versioning, encryption, and lifecycle policies" --cloud aws
```

### GCP Examples

```bash
# GKE Cluster
python agent.py "Create GKE cluster with node pools and monitoring" --cloud gcp

# Cloud SQL
python agent.py "Create Cloud SQL PostgreSQL with high availability and backups" --cloud gcp

# Cloud Storage
python agent.py "Create Cloud Storage bucket with uniform access and encryption" --cloud gcp

# Firestore
python agent.py "Create Firestore database with security rules" --cloud gcp
```

## Next Steps

1. ✅ Get API key
2. ✅ Install dependencies  
3. ✅ Run first generation: `python agent.py "your requirement" --cloud azure`
4. ✅ Review generated code
5. ✅ Customize for your needs
6. ✅ Run terraform init/plan/apply

## Support

For issues or improvements:
- Check error messages carefully
- Review generated code for syntax
- Try with different prompts
- Experiment with different models
- Consult Terraform documentation

---

**Happy Infrastructure Coding! 🚀**
