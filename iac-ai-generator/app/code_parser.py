import re
from typing import Dict

def parse_terraform_output(content: str) -> Dict[str, str]:
    """
    Parse LLM output and extract main.tf, variables.tf, and outputs.tf content.
    Handles various formatting styles.
    """
    result = {
        "main.tf": "",
        "variables.tf": "",
        "outputs.tf": ""
    }
    
    # Pattern 1: #### FILE_NAME format
    pattern1 = r'####\s*([A-Z_]+\.TF)\s*\n(.*?)(?=####|$)'
    matches = re.findall(pattern1, content, re.IGNORECASE | re.DOTALL)
    
    for file_name, code_block in matches:
        file_key = file_name.lower()
        if file_key in result:
            result[file_key] = code_block.strip()
    
    # Pattern 2: # FILE_NAME format
    if not any(result.values()):
        pattern2 = r'#\s*([a-z_]+\.tf)\s*\n(.*?)(?=#\s*[a-z_]+\.tf|$)'
        matches = re.findall(pattern2, content, re.IGNORECASE | re.DOTALL)
        
        for file_name, code_block in matches:
            file_key = file_name.lower()
            if file_key in result:
                result[file_key] = code_block.strip()
    
    # Pattern 3: **FILE_NAME** format (markdown)
    if not any(result.values()):
        pattern3 = r'\*\*([a-z_]+\.tf)\*\*\s*\n(.*?)(?=\*\*|$)'
        matches = re.findall(pattern3, content, re.IGNORECASE | re.DOTALL)
        
        for file_name, code_block in matches:
            file_key = file_name.lower()
            if file_key in result:
                result[file_key] = code_block.strip()
    
    # Pattern 4: Code blocks with file names
    if not any(result.values()):
        pattern4 = r'```(?:hcl|terraform)?\s*\n(.*?)```'
        code_blocks = re.findall(pattern4, content, re.DOTALL)
        
        if len(code_blocks) >= 3:
            result["main.tf"] = code_blocks[0].strip()
            result["variables.tf"] = code_blocks[1].strip()
            result["outputs.tf"] = code_blocks[2].strip()
        elif len(code_blocks) >= 1:
            result["main.tf"] = code_blocks[0].strip()
    
    # If nothing was found, try to split by common markers
    if not any(result.values()):
        result["main.tf"] = content.strip()
    
    return result


def validate_terraform_code(code: str, file_type: str = "main.tf") -> bool:
    """
    Basic validation of Terraform code.
    """
    if not code.strip():
        return False
    
    # Check for basic HCL syntax
    required_keywords = {
        "main.tf": ["resource", "provider"],
        "variables.tf": ["variable"],
        "outputs.tf": ["output"]
    }
    
    # Allow missing keywords for simplified code
    code_lower = code.lower()
    required = required_keywords.get(file_type, [])
    
    # At least some structure should be present
    if not any(keyword in code_lower for keyword in required):
        if file_type == "outputs.tf":
            # Outputs file can be empty
            return True
        return False
    
    return True


def format_terraform_output(parsed_code: Dict[str, str]) -> str:
    """
    Format parsed Terraform code into a readable string.
    """
    output = []
    
    for file_name in ["main.tf", "variables.tf", "outputs.tf"]:
        if parsed_code.get(file_name):
            output.append(f"\n{'='*60}")
            output.append(f"📄 {file_name}")
            output.append(f"{'='*60}\n")
            output.append(parsed_code[file_name])
    
    return "\n".join(output)
