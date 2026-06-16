import re
from typing import List, Dict
from enum import Enum


class Severity(Enum):
    """Security issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class SecurityScanner:
    """Scan Terraform code for security issues and vulnerabilities"""
    
    def __init__(self):
        """Initialize security check patterns"""
        self.checks = self.setup_checks()
    
    def setup_checks(self) -> Dict:
        """Setup all security check patterns"""
        return {
            "hardcoded_secrets": {
                "patterns": [
                    r'password\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                    r'api_key\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                    r'secret\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                    r'token\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                    r'access_key\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                    r'private_key\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)[^"\']*["\']',
                ],
                "severity": Severity.CRITICAL,
                "description": "Hardcoded secrets or credentials",
                "remediation": "Use Terraform variables, AWS Secrets Manager, Azure Key Vault, or Google Secret Manager"
            },
            "public_access": {
                "patterns": [
                    r'publicly_accessible\s*=\s*true',
                    r'public_access_enabled\s*=\s*true',
                    r'allow_public_access\s*=\s*true',
                    r'enable_public_access\s*=\s*true',
                    r'cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]',
                    r'source_security_group_id\s*=\s*"0\.0\.0\.0/0"',
                    r'ingress.*from_port.*to_port.*0\.0\.0\.0/0',
                ],
                "severity": Severity.HIGH,
                "description": "Resources exposed to public internet",
                "remediation": "Restrict access to specific IPs/security groups"
            },
            "encryption_disabled": {
                "patterns": [
                    r'enabled\s*=\s*false',
                    r'https_traffic_only_enabled\s*=\s*false',
                    r'encrypted\s*=\s*false',
                    r'encryption_enabled\s*=\s*false',
                    r'storage_encryption_enabled\s*=\s*false',
                    r'tls_enabled\s*=\s*false',
                    r'ssl\s*=\s*false',
                    r'kms_key_id\s*=\s*["\']?["\']',  # Empty KMS key
                ],
                "severity": Severity.HIGH,
                "description": "Encryption disabled or missing",
                "remediation": "Enable encryption at rest and in transit. Use appropriate KMS keys"
            },
            "default_credentials": {
                "patterns": [
                    r'username\s*=\s*["\']admin["\']',
                    r'username\s*=\s*["\']root["\']',
                    r'password\s*=\s*["\']password["\']',
                    r'password\s*=\s*["\']123456["\']',
                    r'password\s*=\s*["\']admin["\']',
                    r'admin_password\s*=\s*["\'](?!var\.)(?!local\.)(?!data\.)["\']',
                ],
                "severity": Severity.CRITICAL,
                "description": "Default or weak credentials",
                "remediation": "Use strong, randomly generated passwords from secret management systems"
            },
            "unencrypted_protocols": {
                "patterns": [
                    r'protocol\s*=\s*["\']http["\']',
                    r'protocol\s*=\s*["\']ftp["\']',
                    r'protocol\s*=\s*["\']telnet["\']',
                    r'protocol\s*=\s*["\']smtp["\']',
                    r'\'http://.*\'',
                    r'"http://.*"',
                ],
                "severity": Severity.HIGH,
                "description": "Unencrypted protocols used",
                "remediation": "Use HTTPS, SFTP, SSH, SMTPS, and other encrypted alternatives"
            },
            "overly_permissive_rules": {
                "patterns": [
                    r'ingress\s*{\s*from_port\s*=\s*0\s+to_port\s*=\s*65535',
                    r'egress\s*{\s*from_port\s*=\s*0\s+to_port\s*=\s*65535',
                    r'permissions\s*=\s*\[.*"\\*".*\]',
                    r'effect\s*=\s*["\']Allow["\'].*Principal.*\*',
                ],
                "severity": Severity.HIGH,
                "description": "Overly permissive security rules",
                "remediation": "Restrict rules to specific ports and protocols needed"
            },
            "missing_logging": {
                "patterns": [
                    # Look for resources without logging enabled
                    r'resource\s+"azurerm_storage_account"[^}]*}(?!.*diagnostic_setting)',
                    r'resource\s+"aws_s3_bucket"[^}]*}(?!.*logging)',
                    r'resource\s+"google_sql_database_instance"[^}]*}(?!.*backup_configuration)',
                ],
                "severity": Severity.MEDIUM,
                "description": "Logging not configured or disabled",
                "remediation": "Enable audit logging and CloudTrail/monitoring for compliance"
            },
            "missing_tags": {
                "patterns": [
                    r'resource\s+"azurerm[^"]*"\s+"[^"]*"\s*{\s*(?!.*tags)',
                    r'resource\s+"aws[^"]*"\s+"[^"]*"\s*{\s*(?!.*tags)',
                ],
                "severity": Severity.LOW,
                "description": "Resources missing required tags",
                "remediation": "Add tags for cost allocation, environment, owner, etc."
            },
            "missing_backup": {
                "patterns": [
                    r'resource\s+"azurerm_mssql_database"[^}]*}(?!.*backup)',
                    r'resource\s+"aws_rds_cluster"[^}]*}(?!.*backup_retention_period)',
                    r'backup_retention_period\s*=\s*0',
                    r'backup_enabled\s*=\s*false',
                ],
                "severity": Severity.HIGH,
                "description": "Backup/disaster recovery not configured",
                "remediation": "Enable automated backups with appropriate retention"
            },
            "missing_network_isolation": {
                "patterns": [
                    r'resource\s+"azurerm_postgresql_server".*public_network_access_enabled\s*=\s*true',
                    r'resource\s+"aws_rds_cluster_instance".*publicly_accessible\s*=\s*true',
                    r'resource\s+"google_cloud_sql_instance".*public_ip_enabled\s*=\s*true',
                ],
                "severity": Severity.HIGH,
                "description": "Database exposed to public network",
                "remediation": "Use private endpoints or security group restrictions"
            },
            "missing_identity_auth": {
                "patterns": [
                    r'azurerm_app_service.*identity\s*{',  # Should have identity block
                    r'aws_lambda_function.*(?!execution_role)',  # Lambda needs role
                ],
                "severity": Severity.MEDIUM,
                "description": "Managed identity or role not configured",
                "remediation": "Configure managed identities for Azure, IAM roles for AWS"
            },
        }
    
    def scan(self, terraform_code: str, cloud: str = "azure") -> Dict:
        """
        Scan Terraform code for security issues.
        
        Args:
            terraform_code: The Terraform code to scan
            cloud: Cloud provider (azure, aws, gcp)
        
        Returns:
            Dict with scan results, issues, and summary
        """
        issues = []
        
        # Run all checks
        for check_name, check_config in self.checks.items():
            for pattern in check_config["patterns"]:
                try:
                    matches = re.finditer(
                        pattern,
                        terraform_code,
                        re.IGNORECASE | re.DOTALL
                    )
                    
                    for match in matches:
                        line_num = terraform_code[:match.start()].count('\n') + 1
                        
                        # Avoid duplicate issues on same line
                        if not any(i["line"] == line_num and i["check"] == check_name for i in issues):
                            issues.append({
                                "check_id": self._generate_check_id(check_name),
                                "check": check_name,
                                "severity": check_config["severity"].value,
                                "line": line_num,
                                "description": check_config["description"],
                                "remediation": check_config["remediation"],
                                "matched_text": match.group()[:50] + ("..." if len(match.group()) > 50 else ""),
                            })
                except Exception as e:
                    # Skip patterns that cause regex errors
                    pass
        
        # Cloud-specific checks
        if cloud.lower() == "azure":
            issues.extend(self._check_azure_security(terraform_code))
        elif cloud.lower() == "aws":
            issues.extend(self._check_aws_security(terraform_code))
        elif cloud.lower() == "gcp":
            issues.extend(self._check_gcp_security(terraform_code))
        
        # Summary
        passed = len(issues) == 0
        summary = self._get_summary(issues)
        
        return {
            "passed": passed,
            "issues_found": len(issues),
            "severity_counts": summary["severity_counts"],
            "issues": sorted(issues, key=lambda x: self._severity_rank(x["severity"]), reverse=True),
            "summary": summary["text"],
            "cloud": cloud,
            "compliance_score": self._calculate_compliance_score(issues)
        }
    
    def _check_azure_security(self, terraform_code: str) -> List[Dict]:
        """Azure-specific security checks"""
        issues = []
        
        # Check for Azure AD authentication
        if "azurerm_app_service" in terraform_code:
            if not re.search(r'auth_settings.*active_directory', terraform_code):
                issues.append({
                    "check_id": "AZURE_001",
                    "check": "missing_azure_ad_auth",
                    "severity": Severity.MEDIUM.value,
                    "line": 0,
                    "description": "Azure App Service missing Azure AD authentication",
                    "remediation": "Configure Azure AD provider in auth_settings"
                })
        
        # Check for managed identity on App Service
        if "azurerm_app_service" in terraform_code:
            if not re.search(r'identity\s*{\s*type\s*=\s*["\']SystemAssigned["\']', terraform_code):
                issues.append({
                    "check_id": "AZURE_002",
                    "check": "missing_managed_identity",
                    "severity": Severity.MEDIUM.value,
                    "line": 0,
                    "description": "App Service should use managed identity",
                    "remediation": "Add 'identity { type = \"SystemAssigned\" }'"
                })
        
        return issues
    
    def _check_aws_security(self, terraform_code: str) -> List[Dict]:
        """AWS-specific security checks"""
        issues = []
        
        # Check for S3 bucket versioning
        if "aws_s3_bucket" in terraform_code:
            if not re.search(r'versioning.*enabled\s*=\s*true', terraform_code):
                issues.append({
                    "check_id": "AWS_001",
                    "check": "s3_versioning_disabled",
                    "severity": Severity.MEDIUM.value,
                    "line": 0,
                    "description": "S3 bucket versioning not enabled",
                    "remediation": "Enable versioning for data protection and recovery"
                })
        
        # Check for IAM policy wildcard actions
        if "aws_iam_policy" in terraform_code or "aws_iam_role_policy" in terraform_code:
            if re.search(r'Action\s*:\s*\[.*\*.*\]', terraform_code):
                issues.append({
                    "check_id": "AWS_002",
                    "check": "iam_wildcard_actions",
                    "severity": Severity.HIGH.value,
                    "line": 0,
                    "description": "IAM policy uses wildcard actions",
                    "remediation": "Specify exact actions instead of wildcards"
                })
        
        return issues
    
    def _check_gcp_security(self, terraform_code: str) -> List[Dict]:
        """GCP-specific security checks"""
        issues = []
        
        # Check for compute instance public IP
        if "google_compute_instance" in terraform_code:
            if re.search(r'access_config\s*{\s*}', terraform_code):
                issues.append({
                    "check_id": "GCP_001",
                    "check": "compute_public_ip",
                    "severity": Severity.HIGH.value,
                    "line": 0,
                    "description": "Compute instance has public IP",
                    "remediation": "Use Cloud NAT or remove public IP if not needed"
                })
        
        return issues
    
    def _severity_rank(self, severity: str) -> int:
        """Convert severity to numeric rank for sorting"""
        ranks = {
            Severity.CRITICAL.value: 4,
            Severity.HIGH.value: 3,
            Severity.MEDIUM.value: 2,
            Severity.LOW.value: 1,
            Severity.INFO.value: 0,
        }
        return ranks.get(severity, 0)
    
    def _generate_check_id(self, check_name: str) -> str:
        """Generate check ID from check name"""
        return f"CHK_{check_name.upper()[:3]}_{''.join(c for c in check_name if c.isupper() or c.isdigit())[:3]}"
    
    def _get_summary(self, issues: List[Dict]) -> Dict:
        """Get summary of security issues"""
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
        }
        
        for issue in issues:
            severity = issue.get("severity", "INFO")
            if severity in summary:
                summary[severity] += 1
        
        # Generate text summary
        text = []
        if summary["CRITICAL"] > 0:
            text.append(f"🚨 {summary['CRITICAL']} CRITICAL issue(s) found")
        if summary["HIGH"] > 0:
            text.append(f"⚠️ {summary['HIGH']} HIGH severity issue(s)")
        if summary["MEDIUM"] > 0:
            text.append(f"⚠️ {summary['MEDIUM']} MEDIUM severity issue(s)")
        if summary["LOW"] > 0:
            text.append(f"ℹ️ {summary['LOW']} LOW severity issue(s)")
        
        if not text:
            text = ["✅ No security issues found"]
        
        return {
            "severity_counts": {k: v for k, v in summary.items() if v > 0},
            "text": " | ".join(text)
        }
    
    def _calculate_compliance_score(self, issues: List[Dict]) -> int:
        """
        Calculate compliance score (0-100).
        Deduct points based on severity of issues.
        """
        score = 100
        
        for issue in issues:
            severity = issue.get("severity", "INFO")
            if severity == Severity.CRITICAL.value:
                score -= 10
            elif severity == Severity.HIGH.value:
                score -= 5
            elif severity == Severity.MEDIUM.value:
                score -= 2
            elif severity == Severity.LOW.value:
                score -= 1
        
        return max(0, score)


class ComplianceChecker:
    """Check compliance with security frameworks"""
    
    FRAMEWORKS = {
        "cis": {
            "name": "CIS AWS Foundations Benchmark",
            "checks": [
                "encrypted",
                "logging_enabled",
                "public_access",
            ]
        },
        "pci_dss": {
            "name": "PCI DSS",
            "checks": [
                "encryption",
                "access_control",
                "logging",
                "backup",
            ]
        },
        "hipaa": {
            "name": "HIPAA",
            "checks": [
                "encryption_at_rest",
                "encryption_in_transit",
                "audit_logging",
                "access_control",
                "backup_recovery",
            ]
        }
    }
    
    def check_compliance(self, security_scan_results: Dict, framework: str = "cis") -> Dict:
        """Check compliance with a specific framework"""
        if framework not in self.FRAMEWORKS:
            return {"error": f"Unknown framework: {framework}"}
        
        framework_config = self.FRAMEWORKS[framework]
        
        # Map scan results to framework requirements
        issues = security_scan_results.get("issues", [])
        critical_issues = [i for i in issues if i.get("severity") == Severity.CRITICAL.value]
        high_issues = [i for i in issues if i.get("severity") == Severity.HIGH.value]
        
        compliance_status = "COMPLIANT" if not critical_issues else "NON_COMPLIANT"
        
        return {
            "framework": framework_config["name"],
            "status": compliance_status,
            "critical_violations": len(critical_issues),
            "high_violations": len(high_issues),
            "recommendations": self._get_recommendations(framework, issues),
            "score": security_scan_results.get("compliance_score", 0)
        }
    
    def _get_recommendations(self, framework: str, issues: List[Dict]) -> List[str]:
        """Get recommendations based on framework"""
        recommendations = []
        
        if framework == "cis":
            if any("public_access" in i["check"] for i in issues):
                recommendations.append("CIS 1.2: Restrict public access to resources")
            if any("encryption" in i["check"] for i in issues):
                recommendations.append("CIS 2.3: Enable encryption at rest")
            if any("logging" in i["check"] for i in issues):
                recommendations.append("CIS 2.4: Enable logging for all resources")
        
        elif framework == "hipaa":
            recommendations.append("HIPAA Rule 164.312(a)(2): Enable encryption for PHI")
            recommendations.append("HIPAA Rule 164.312(b): Implement audit controls")
            recommendations.append("HIPAA Rule 164.308(a)(1): Develop a security management plan")
        
        elif framework == "pci_dss":
            recommendations.append("PCI DSS 3.2: Protect stored cardholder data with encryption")
            recommendations.append("PCI DSS 10.2: Implement logging and monitoring")
            recommendations.append("PCI DSS 6.2: Maintain secure development practices")
        
        return recommendations
