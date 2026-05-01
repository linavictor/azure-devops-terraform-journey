def build_prompt(requirement: str, cloud: str) -> str:
    return f"""
You are a Terraform expert.

Generate production-ready Terraform code for {cloud}.

Requirements:
{requirement}

Output should include:
- main.tf
- outputs.tf

Follow best practices:
- No hardcoded secrets
- Secure defaults
- Production-ready structure
"""