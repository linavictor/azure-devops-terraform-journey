def build_prompt(requirement, cloud):
    return f"""
    Generate
You are a senior Azure DevOps engineer.

Generate production-grade Terraform code for {cloud}.

Requirements:
{requirement}

Rules:
- Use azurerm provider
- Do NOT hardcode values (use variables)
- Include tags
- AKS must be private
- Include Key Vault and SQL
- Output ONLY Terraform code

Format:
// main.tf
<code>

// variables.tf
<code>

// outputs.tf
<code>
"""