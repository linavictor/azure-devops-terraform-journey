def build_prompt(requirement: str, cloud: str = "azure") -> str:
    """
    Build an enhanced prompt for Terraform generation.
    Includes best practices and structured output requirements.
    """
    cloud_context = {
        "azure": {
            "provider": "azurerm",
            "common_resources": "Resource Groups, Virtual Networks, App Services, SQL Databases, Key Vault, AKS",
            "auth": "azurerm provider with subscription_id, client_id, client_secret, tenant_id"
        },
        "aws": {
            "provider": "aws",
            "common_resources": "VPC, EC2, RDS, S3, IAM, ECS, Lambda, ALB",
            "auth": "aws provider with access_key, secret_key, or assume_role"
        },
        "gcp": {
            "provider": "google",
            "common_resources": "Projects, Compute Instances, Cloud SQL, Cloud Storage, GKE, Cloud Functions",
            "auth": "google provider with credentials JSON"
        }
    }
    
    context = cloud_context.get(cloud.lower(), cloud_context["azure"])
    
    return f"""You are a Terraform expert specializing in {cloud.upper()} infrastructure.

REQUIREMENT:
{requirement}

CLOUD PROVIDER: {cloud.upper()}
Provider Name: {context['provider']}
Common Resources: {context['common_resources']}
Authentication: {context['auth']}

INSTRUCTIONS:
1. Generate production-ready Terraform code
2. Split code into these sections (clearly labeled):
   - MAIN.TF: Provider and resources
   - VARIABLES.TF: Input variables with descriptions
   - OUTPUTS.TF: Output values for reference
3. Best practices:
   - Use variables for all configurable values
   - Add descriptions to all variables and outputs
   - Include security defaults (encryption, private endpoints, etc.)
   - Add tags/labels for resource management
   - Use local values for repeated configurations
   - Include comments explaining complex logic
4. Output format - clearly separate each file with:
   #### MAIN.TF
   [code]
   #### VARIABLES.TF
   [code]
   #### OUTPUTS.TF
   [code]

Generate the Terraform code now:"""