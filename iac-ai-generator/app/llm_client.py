import requests
import os
import json

def call_llm(prompt: str, model: str = None):
    """
    Call LLM API to generate Terraform code.
    Supports both OpenRouter and direct API calls.
    """
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Set OPENROUTER_API_KEY or LLM_API_KEY environment variable.")
    
    if not model:
        model = os.getenv('LLM_MODEL', 'mistralai/mistral-7b-instruct')
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://terraform-agent.local",
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": """You are an expert Terraform engineer. Generate production-ready Terraform code.
                
Instructions:
- Output ONLY valid HCL code
- Include main.tf, variables.tf, and outputs.tf content
- Add comments for clarity
- Use best practices and security defaults
- Format code properly with 2-space indentation"""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Unexpected LLM response: {result}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"LLM API call failed: {str(e)}")