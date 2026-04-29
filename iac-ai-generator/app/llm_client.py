import requests
import os

def call_llm(prompt: str):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Generate Terraform for Azure. Only output code."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print("LLM RESPONSE:", result)

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return ""