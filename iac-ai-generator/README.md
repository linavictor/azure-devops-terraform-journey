# 🚀 AI-Powered Terraform Code Generator

Generate production-ready Terraform infrastructure code from natural language prompts using AI/LLM.

## ✨ Features

- 🤖 **AI-Powered Code Generation**: Convert natural language requirements into Terraform code
- ☁️ **Multi-Cloud Support**: Azure, AWS, and GCP
- 📝 **Structured Output**: Automatic splitting into main.tf, variables.tf, outputs.tf
- ✅ **Code Validation**: Basic syntax validation for generated code
- 🔒 **Security Best Practices**: Includes security defaults and best practices
- 💾 **File Management**: Automatically saves generated files
- 🌐 **REST API**: FastAPI endpoints for integration
- 🖥️ **CLI Agent**: Interactive command-line interface

## 🏗️ Architecture

```
User Input (Prompt)
       ↓
   LLM Model (OpenRouter)
       ↓
   Code Parser
       ↓
   Validation
       ↓
   Terraform Files (main.tf, variables.tf, outputs.tf)
```

## 📋 Tech Stack

- **Backend**: Python 3.10+
- **API Framework**: FastAPI
- **LLM Integration**: OpenRouter API (supports multiple models)
- **Code Parsing**: Regex-based HCL extraction
- **Server**: Uvicorn

## 🚀 Quick Start

### 1. Installation

```bash
cd iac-ai-generator
pip install -r requirements.txt
```

### 2. Setup API Key

Get your OpenRouter API key from [openrouter.ai](https://openrouter.ai)

```bash
export OPENROUTER_API_KEY="your-api-key-here"
# or
export LLM_API_KEY="your-api-key-here"
```

### 3. Use the CLI Agent

```bash
# Simple usage
python agent.py "create a secure AKS cluster" --cloud azure

# AWS example
python agent.py "setup RDS database with encryption" --cloud aws

# GCP example
python agent.py "create cloud storage bucket" --cloud gcp

# Interactive mode
python agent.py --interactive

# Don't save files
python agent.py "create VPC" --cloud aws --no-save

# Specify LLM model
python agent.py "create Azure resource group" --model openai/gpt-4
```

### 4. Run the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

## 📚 API Usage

### Generate Terraform Code

**Endpoint**: `POST /generate`

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Create a secure AKS cluster with monitoring",
    "cloud": "azure",
    "save_output": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "requirement": "Create a secure AKS cluster with monitoring",
  "cloud": "azure",
  "main_tf": "provider \"azurerm\" {...}",
  "variables_tf": "variable \"cluster_name\" {...}",
  "outputs_tf": "output \"cluster_id\" {...}",
  "parsed_successfully": true,
  "output_path": "/path/to/output/azure"
}
```

### Get Formatted Output

**Endpoint**: `POST /generate-and-format`

```bash
curl -X POST "http://localhost:8000/generate-and-format" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Create VPC with subnets",
    "cloud": "aws"
  }'
```

### Health Check

**Endpoint**: `GET /`

```bash
curl http://localhost:8000/
```

## 🎯 Usage Examples

### Azure Examples

```bash
# AKS Cluster
python agent.py "Create a production-grade AKS cluster with node pools, monitoring, and RBAC enabled" --cloud azure

# App Service
python agent.py "Deploy a web application using Azure App Service with database" --cloud azure

# Storage
python agent.py "Create secure blob storage with encryption and access controls" --cloud azure
```

### AWS Examples

```bash
# EC2 with RDS
python agent.py "Setup EC2 instances with RDS MySQL database and load balancer" --cloud aws

# Lambda
python agent.py "Create Lambda function with API Gateway and CloudWatch logging" --cloud aws

# S3
python agent.py "Create S3 bucket with versioning, encryption, and lifecycle policies" --cloud aws
```

### GCP Examples

```bash
# GKE
python agent.py "Create GKE cluster with autoscaling and monitoring" --cloud gcp

# Cloud SQL
python agent.py "Deploy Cloud SQL PostgreSQL instance with high availability" --cloud gcp

# Cloud Storage
python agent.py "Setup Cloud Storage with lifecycle policies and access logging" --cloud gcp
```

## 📁 Project Structure

```
iac-ai-generator/
├── agent.py                 # CLI agent for direct usage
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── llm_client.py       # LLM API integration
│   ├── prompt_builder.py   # Prompt engineering
│   ├── code_parser.py      # HCL code extraction
│   └── terraform_templates/
│       └── base_template.txt
├── output/
│   ├── azure/              # Generated Azure resources
│   ├── aws/                # Generated AWS resources
│   └── gcp/                # Generated GCP resources
```

## 🔧 Configuration

### Environment Variables

```bash
# LLM Configuration
OPENROUTER_API_KEY=sk-or-...          # OpenRouter API key
LLM_API_KEY=sk-or-...                 # Alternative API key
LLM_MODEL=mistralai/mistral-7b-instruct  # Model to use

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Supported LLM Models

- `mistralai/mistral-7b-instruct` (default, free tier available)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-2-70b-chat`
- `claude-3-opus`
- And many more via OpenRouter

## 📊 How It Works

1. **Input**: Natural language requirement from user
2. **Prompt Engineering**: Build context-aware prompt with cloud-specific guidance
3. **LLM Call**: Send prompt to OpenRouter API
4. **Response Parsing**: Extract Terraform code from LLM response
5. **Validation**: Basic syntax and structure validation
6. **Output**: Split into main.tf, variables.tf, outputs.tf
7. **Storage**: Save files to output directory

## ✅ Best Practices

The generated code includes:

- ✓ No hardcoded secrets (uses variables for sensitive data)
- ✓ Encryption enabled by default
- ✓ Security groups/firewalls configured
- ✓ Monitoring and logging enabled
- ✓ High availability considerations
- ✓ Cost optimization suggestions
- ✓ Comments explaining complex resources
- ✓ Production-ready structure

## 🐛 Troubleshooting

### "No API key found"
```bash
export OPENROUTER_API_KEY="your-key-here"
# Verify:
echo $OPENROUTER_API_KEY
```

### "LLM API call failed"
- Check internet connection
- Verify API key is valid
- Check OpenRouter status page
- Increase timeout if model is slow

### "Code parsing failed"
- Check LLM response format
- Try with different model
- Increase max_tokens in code

### "Invalid HCL generated"
- The parser might not have recognized the format
- Try running `terraform init` and `terraform plan` to debug
- Report issue with the exact output

## 📝 Example Workflow

```bash
# 1. Generate infrastructure code
python agent.py "Create production-grade PostgreSQL database with backups" --cloud azure

# 2. Check generated files
ls -la output/azure/generated/

# 3. Review and customize (optional)
cat output/azure/generated/main.tf

# 4. Use with Terraform
cd output/azure/generated
terraform init
terraform plan
terraform apply
```

## 🔗 Integration

### In Python Scripts

```python
from app.prompt_builder import build_prompt
from app.llm_client import call_llm
from app.code_parser import parse_terraform_output

requirement = "Create AKS cluster"
prompt = build_prompt(requirement, "azure")
response = call_llm(prompt)
parsed = parse_terraform_output(response)
```

### In CI/CD Pipelines

See [azure-pipelines.yml](../azure-pipelines.yml) for GitHub Actions integration.

## 📚 Learning Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [HCL Syntax Guide](https://www.terraform.io/language)

## 🤝 Contributing

Improvements welcome! Areas for enhancement:

- [ ] Support for more cloud providers (Kubernetes, on-prem, etc.)
- [ ] Advanced code optimization
- [ ] Cost estimation
- [ ] Multi-cloud orchestration
- [ ] State management improvements
- [ ] Better validation and linting

## 📜 License

This project is part of the Azure DevOps Terraform Journey repository.

## 💡 Tips

1. **Be Specific**: More detailed prompts = better code
2. **Iterate**: Start with basic requirement, then enhance
3. **Review**: Always review generated code before applying
4. **Test**: Run `terraform plan` first to see changes
5. **Customize**: Adjust generated code for your specific needs

---

**Happy Terraforming! 🚀**

   * Manual approval
   * `terraform apply` (mocked using null provider)

---

## 🧪 Example Request

```json
{
  "requirement": "Create AKS cluster with private endpoints"
}
```

---

## 📂 Output Example

```
output/
├── main.tf
├── variables.tf
└── outputs.tf
```

---

## 🔐 Security Considerations

* Private endpoints supported in generated templates
* Public access disabled (SQL, Key Vault)
* Designed for integration with Azure Key Vault

---

## 🚫 Note on Deployment

To avoid cloud costs:

* Terraform execution uses `null_resource`
* No real Azure resources are created

---

## 🚀 Future Enhancements

* Azure deployment with remote state
* Integration with Azure DevOps pipelines
* Policy enforcement (OPA / Sentinel)
* Cost estimation (Infracost)
* Multi-cloud support (AWS/GCP)

---

## 💬 Interview Talking Points

* AI + DevOps integration
* Automated IaC generation
* CI/CD validation for infra code
* Secure cloud architecture patterns

---

## 👤 Author

Built as part of DevOps upskilling journey 🚀
