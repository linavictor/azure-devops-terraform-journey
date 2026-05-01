from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()


# ✅ Updated Request model (add cloud)
class Request(BaseModel):
    requirement: str
    cloud: str


@app.get("/")
def root():
    return {"message": "IaC AI Generator is running"}


@app.post("/generate")
def generate_iac(req: Request):

    # ✅ Normalize cloud input
    cloud = req.cloud.lower()

    # ✅ Basic validation
    if cloud not in ["azure", "aws", "gcp"]:
        return {"error": "Unsupported cloud provider. Use azure/aws/gcp"}

    # ✅ Build prompt with cloud
    prompt = build_prompt(req.requirement, cloud)

    # ---------------------------------------------------
    # 🔥 MOCK RESPONSE (since you're not using real LLM now)
    # ---------------------------------------------------

    if cloud == "azure":
        terraform_code = """
// main.tf
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "demo-rg"
  location = "East US"
}

// outputs.tf
output "resource_group_name" {
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