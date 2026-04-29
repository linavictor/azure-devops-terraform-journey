# 🚀 AI-Powered Infrastructure as Code Generator (Azure + Terraform)

## 📌 Overview

This project demonstrates an **AI-driven DevOps workflow** that generates Terraform code from natural language requirements and validates it using a CI/CD pipeline.

---

## 🧠 What it does

* 🔹 Accepts natural language input (e.g., *"Create secure AKS cluster"*)
* 🔹 Uses LLM to generate Terraform code
* 🔹 Splits output into:

  * `main.tf`
  * `variables.tf`
  * `outputs.tf`
* 🔹 Runs CI pipeline to:

  * Validate Terraform
  * Generate execution plan
  * Apply (mocked for demo)

---

## 🏗️ Architecture

![Architecture Diagram](docs/architecture.png)

---

## ⚙️ Tech Stack

* Python (FastAPI)
* Terraform
* GitHub Actions (CI/CD)
* LLM (OpenRouter / OpenAI compatible APIs)
* Azure (design-ready, mocked in pipeline)

---

## 🔁 CI/CD Workflow

1. Code pushed to repository
2. GitHub Actions triggers pipeline
3. FastAPI generates Terraform
4. Pipeline:

   * `terraform init`
   * `terraform plan`
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
