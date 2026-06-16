# 🧪 Hands-On Labs: Build & Learn

These labs build on your existing Terraform AI Agent. Each lab is 1-3 hours.

---

## Lab 1: Containerize Your Agent (Beginner - 1 hour)

**Goal:** Package agent as Docker container

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    terraform \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV LLM_MODEL=mistralai/mistral-7b-instruct

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create .dockerignore

```
__pycache__
*.pyc
.git
.env
.terraform
*.tfstate
output/
.pytest_cache
.venv
```

### Step 3: Build and Test

```bash
cd /home/lina/azure-devops-terraform-journey/iac-ai-generator

# Build image
docker build -t terraform-agent:latest .

# Run container
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY="your-key" \
  terraform-agent:latest

# Test it
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"requirement": "create storage", "cloud": "azure"}'
```

### Step 4: Push to Registry

```bash
# Azure Container Registry
az acr login --name yourregistry
docker tag terraform-agent:latest yourregistry.azurecr.io/terraform-agent:latest
docker push yourregistry.azurecr.io/terraform-agent:latest

# Docker Hub
docker tag terraform-agent:latest yourusername/terraform-agent:latest
docker push yourusername/terraform-agent:latest
```

**✅ Checkpoint:** Your agent runs in Docker

---

## Lab 2: Add Cost Estimation (Intermediate - 2 hours)

**Goal:** Estimate infrastructure costs

### Step 1: Create Cost Estimator Module

```python
# app/cost_estimator.py
import re
from typing import Dict, List

class CostEstimator:
    """Estimate Azure costs for Terraform resources"""
    
    # Simplified pricing (actual prices change)
    AZURE_PRICES = {
        "azurerm_resource_group": 0,  # Free
        "azurerm_storage_account": {
            "per_gb_month": 0.0184,
            "request_cost": 0.0000004,
        },
        "azurerm_app_service": {
            "B1": 10.95,
            "B2": 21.90,
            "B3": 43.80,
        },
        "azurerm_sql_database": {
            "Basic": 5.00,
            "Standard": 50.00,
            "Premium": 200.00,
        },
        "azurerm_kubernetes_cluster": {
            "cluster": 0.10,  # Per hour
            "per_node": 73.44,  # Per month
        },
    }
    
    def estimate(self, terraform_code: str) -> Dict:
        """Estimate costs from Terraform code"""
        resources = self.parse_resources(terraform_code)
        costs = {}
        total = 0
        
        for resource_type, count in resources.items():
            if resource_type in self.AZURE_PRICES:
                cost = count * self.get_cost(resource_type)
                costs[resource_type] = {
                    "count": count,
                    "monthly_cost": cost
                }
                total += cost
        
        return {
            "resources": costs,
            "total_monthly": round(total, 2),
            "total_annual": round(total * 12, 2),
        }
    
    def parse_resources(self, terraform_code: str) -> Dict[str, int]:
        """Count resources in Terraform code"""
        resources = {}
        
        # Find all resource declarations
        pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.findall(pattern, terraform_code)
        
        for resource_type, _ in matches:
            resources[resource_type] = resources.get(resource_type, 0) + 1
        
        return resources
    
    def get_cost(self, resource_type: str) -> float:
        """Get cost for resource type"""
        if resource_type in self.AZURE_PRICES:
            price = self.AZURE_PRICES[resource_type]
            if isinstance(price, dict):
                return price.get("cluster", 0)
            return price
        return 0
```

### Step 2: Integrate into Agent

```python
# Update app/main.py

from app.cost_estimator import CostEstimator

cost_estimator = CostEstimator()

class TerraformResponse(BaseModel):
    # ... existing fields ...
    estimated_cost: Dict = None

@app.post("/generate-with-cost")
def generate_with_cost(req: TerraformRequest):
    """Generate Terraform and estimate costs"""
    response = generate_iac(req)
    
    if response.status == "success":
        # Estimate costs
        terraform_code = response.main_tf
        response.estimated_cost = cost_estimator.estimate(terraform_code)
    
    return response
```

### Step 3: Test Cost Estimation

```bash
python3 agent.py "Create AKS cluster with storage" --cloud azure

# Should show cost breakdown
```

**✅ Checkpoint:** Costs are estimated for infrastructure

---

## Lab 3: Add Security Scanning (Intermediate - 2 hours)

**Goal:** Check for security issues in generated code

### Step 1: Create Security Scanner

```python
# app/security_scanner.py
import re
from typing import List, Dict

class SecurityScanner:
    """Scan Terraform code for security issues"""
    
    SECURITY_CHECKS = {
        "hardcoded_secrets": {
            "patterns": [
                r'password\s*=\s*"[^"]*"',
                r'api_key\s*=\s*"[^"]*"',
                r'secret\s*=\s*"[^"]*"',
            ],
            "severity": "CRITICAL"
        },
        "public_access": {
            "patterns": [
                r'publicly_accessible\s*=\s*true',
                r'"0\.0\.0\.0/0"',
                r'allow_public_access\s*=\s*true',
            ],
            "severity": "HIGH"
        },
        "encryption_disabled": {
            "patterns": [
                r'https_traffic_only_enabled\s*=\s*false',
                r'encrypted\s*=\s*false',
                r'encryption_enabled\s*=\s*false',
            ],
            "severity": "HIGH"
        },
        "default_credentials": {
            "patterns": [
                r'default.*password',
                r'admin.*password.*admin',
            ],
            "severity": "CRITICAL"
        },
    }
    
    def scan(self, terraform_code: str) -> Dict:
        """Scan for security issues"""
        issues = []
        
        for check_name, check_config in self.SECURITY_CHECKS.items():
            for pattern in check_config["patterns"]:
                matches = re.finditer(pattern, terraform_code, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "check": check_name,
                        "severity": check_config["severity"],
                        "line": terraform_code[:match.start()].count('\n') + 1,
                        "message": f"{check_name}: {match.group()}"
                    })
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "passed": len(issues) == 0,
            "summary": self.get_summary(issues)
        }
    
    def get_summary(self, issues: List) -> Dict:
        """Summarize issues by severity"""
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        
        for issue in issues:
            severity = issue["severity"]
            if severity in summary:
                summary[severity] += 1
        
        return summary
```

### Step 2: Integrate Scanner

```python
# Update agent.py

from app.security_scanner import SecurityScanner

scanner = SecurityScanner()

def display_results(self, results: dict, save_files: bool = True):
    # ... existing code ...
    
    # Add security scan
    if results["success"]:
        security_report = scanner.scan(results["parsed_code"]["main.tf"])
        
        print("\n🔒 Security Scan Results:")
        if security_report["passed"]:
            print("   ✅ No issues found!")
        else:
            print(f"   ⚠️  Found {security_report['issues_found']} issues")
            for severity, count in security_report["summary"].items():
                if count > 0:
                    print(f"      {severity}: {count}")
```

### Step 3: Test Security Scanning

```bash
python3 agent.py "Create database with admin/admin credentials" --cloud azure

# Should detect hardcoded credentials as CRITICAL
```

**✅ Checkpoint:** Security issues are detected

---

## Lab 4: Create Terraform Modules (Intermediate - 3 hours)

**Goal:** Refactor code into reusable modules

### Step 1: Create Module Structure

```
terraform/
├── modules/
│   ├── azure_storage/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── azure_app_service/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── azure_kubernetes/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       └── terraform.tfvars
```

### Step 2: Create Storage Module

```hcl
# terraform/modules/azure_storage/main.tf

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  
  https_traffic_only_enabled = true
  min_tls_version            = "TLS1_2"
  
  tags = var.tags
}
```

```hcl
# terraform/modules/azure_storage/variables.tf

variable "resource_group_name" {
  type = string
}

variable "location" {
  type    = string
  default = "East US"
}

variable "storage_account_name" {
  type = string
}

variable "account_tier" {
  type    = string
  default = "Standard"
}

variable "account_replication_type" {
  type    = string
  default = "GRS"
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

```hcl
# terraform/modules/azure_storage/outputs.tf

output "storage_account_id" {
  value = azurerm_storage_account.storage.id
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}
```

### Step 3: Use Module in Environment

```hcl
# terraform/environments/dev/main.tf

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

module "storage" {
  source = "../../modules/azure_storage"
  
  resource_group_name    = var.resource_group_name
  location               = var.location
  storage_account_name   = var.storage_account_name
  account_tier           = "Standard"
  account_replication_type = "LRS"  # Cheaper for dev
  
  tags = {
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}
```

**✅ Checkpoint:** Reusable modules created

---

## Lab 5: Setup CI/CD Pipeline (Advanced - 3 hours)

**Goal:** Automate testing and deployment

### Step 1: Create GitHub Actions Workflow

```yaml
# .github/workflows/terraform.yml

name: Terraform CI/CD

on:
  push:
    branches: [ main, develop ]
    paths: [ 'terraform/**', '.github/workflows/terraform.yml' ]
  pull_request:
    branches: [ main ]
    paths: [ 'terraform/**' ]

jobs:
  terraform:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.5.0
    
    - name: Terraform Format
      run: terraform fmt -check -recursive terraform/
    
    - name: Terraform Init
      run: terraform init
      working-directory: terraform/environments/dev
    
    - name: Terraform Validate
      run: terraform validate
      working-directory: terraform/environments/dev
    
    - name: Terraform Plan
      run: terraform plan -out=tfplan
      working-directory: terraform/environments/dev
      env:
        ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
        ARM_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Upload Plan
      uses: actions/upload-artifact@v3
      with:
        name: tfplan
        path: terraform/environments/dev/tfplan

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'config'
        scan-ref: 'terraform/'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### Step 2: Create Secrets in GitHub

```bash
# Go to Settings → Secrets and variables → Actions
# Add:
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx
AZURE_TENANT_ID=xxx
AZURE_SUBSCRIPTION_ID=xxx
OPENROUTER_API_KEY=xxx
```

### Step 3: Test Workflow

```bash
git add .github/workflows/terraform.yml
git commit -m "Add Terraform CI/CD pipeline"
git push origin main
```

**✅ Checkpoint:** CI/CD pipeline automated

---

## Lab 6: Deploy to Kubernetes (Advanced - 4 hours)

**Goal:** Run agent on Kubernetes

### Step 1: Create Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: terraform-agent

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: terraform-agent
  namespace: terraform-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: terraform-agent
  template:
    metadata:
      labels:
        app: terraform-agent
    spec:
      containers:
      - name: agent
        image: terraform-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: terraform-agent-service
  namespace: terraform-agent
spec:
  type: LoadBalancer
  selector:
    app: terraform-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Step 2: Deploy

```bash
# Create namespace and secrets
kubectl create namespace terraform-agent
kubectl create secret generic agent-secrets \
  --from-literal=api-key=$OPENROUTER_API_KEY \
  -n terraform-agent

# Deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n terraform-agent
kubectl get svc -n terraform-agent

# Get external IP
kubectl get service terraform-agent-service -n terraform-agent

# Test
curl http://<EXTERNAL-IP>/health
```

**✅ Checkpoint:** Agent runs on Kubernetes

---

## Lab 7: Add Monitoring (Advanced - 2 hours)

**Goal:** Monitor agent with Prometheus and Grafana

### Step 1: Add Prometheus Metrics

```python
# app/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
generations_total = Counter(
    'terraform_generations_total',
    'Total Terraform code generations',
    ['cloud_provider', 'status']
)

generation_duration = Histogram(
    'terraform_generation_duration_seconds',
    'Time to generate Terraform code'
)

active_generations = Gauge(
    'terraform_active_generations',
    'Currently active generations'
)

# Usage in agent.py
with generation_duration.time():
    result = agent.generate(requirement, cloud)
    generations_total.labels(
        cloud_provider=cloud,
        status="success" if result["success"] else "failed"
    ).inc()
```

### Step 2: Add to FastAPI

```python
# app/main.py

from prometheus_client import make_wsgi_app
from fastapi.middleware.wsgi import WSGIMiddleware

# Add Prometheus metrics endpoint
app.add_middleware(WSGIMiddleware, app=make_wsgi_app())

@app.get("/metrics")
def metrics():
    pass  # Prometheus middleware handles this
```

**✅ Checkpoint:** Metrics are collected

---

## 🎯 Lab Summary

| Lab | Topic | Time | Skills |
|-----|-------|------|--------|
| 1 | Docker | 1h | Containerization |
| 2 | Cost | 2h | Domain knowledge |
| 3 | Security | 2h | Security scanning |
| 4 | Modules | 3h | Best practices |
| 5 | CI/CD | 3h | Automation |
| 6 | Kubernetes | 4h | Orchestration |
| 7 | Monitoring | 2h | Observability |

**Total Time: ~17 hours of hands-on learning**

---

## 📋 Completion Checklist

After all labs, you'll have:
- ✅ Containerized application
- ✅ Cost estimation
- ✅ Security scanning
- ✅ Reusable modules
- ✅ Automated CI/CD
- ✅ Kubernetes deployment
- ✅ Production monitoring

---

**Start with Lab 1 today! Pick one and build.** 🚀
