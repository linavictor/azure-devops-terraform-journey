import re
from typing import Dict, List


class CostEstimator:
    """Estimate Azure infrastructure costs from Terraform code"""
    
    # Azure pricing (per month, simplified)
    AZURE_PRICES = {
        "azurerm_resource_group": 0,  # Free
        "azurerm_storage_account": {
            "base": 0.0184,  # Per GB, base tier
            "description": "Storage Account - General Purpose v2"
        },
        "azurerm_app_service_plan": {
            "B1": 10.95,
            "B2": 21.90,
            "B3": 43.80,
            "S1": 73.50,
            "S2": 147.00,
            "P1": 294.00,
            "description": "App Service Plan"
        },
        "azurerm_mssql_database": {
            "Basic": 5.00,
            "Standard": 50.00,
            "Premium": 200.00,
            "description": "SQL Database"
        },
        "azurerm_kubernetes_cluster": {
            "cluster_base": 73.44,  # Base per month
            "per_node": 73.44,
            "description": "AKS Cluster"
        },
        "azurerm_virtual_machine": {
            "B1s": 12.41,
            "B2s": 49.63,
            "D2s_v3": 98.28,
            "D4s_v3": 196.56,
            "description": "Virtual Machine"
        },
        "azurerm_public_ip": {
            "static": 2.60,
            "dynamic": 0,
            "description": "Public IP Address"
        },
        "azurerm_network_interface": {
            "base": 0,
            "description": "Network Interface"
        },
        "azurerm_virtual_network": {
            "base": 0,
            "description": "Virtual Network"
        },
        "azurerm_network_security_group": {
            "base": 0,
            "description": "Network Security Group"
        },
        "azurerm_container_registry": {
            "Basic": 5.00,
            "Standard": 50.00,
            "Premium": 166.00,
            "description": "Container Registry"
        },
        "azurerm_cosmosdb_account": {
            "base": 24.00,
            "description": "Cosmos DB Account"
        },
        "azurerm_redis_cache": {
            "basic_c0": 16.95,
            "standard_c1": 169.50,
            "premium_p1": 949.00,
            "description": "Azure Cache for Redis"
        },
    }
    
    def estimate(self, terraform_code: str) -> Dict:
        """Estimate monthly and annual costs from Terraform code"""
        resources = self.parse_resources(terraform_code)
        costs = {}
        total_monthly = 0
        
        for resource_type, count in resources.items():
            if resource_type in self.AZURE_PRICES:
                cost = self.calculate_resource_cost(resource_type, count, terraform_code)
                if cost > 0:
                    costs[resource_type] = {
                        "count": count,
                        "monthly_cost": round(cost, 2),
                        "description": self.AZURE_PRICES[resource_type].get("description", resource_type)
                    }
                    total_monthly += cost
        
        return {
            "resources": costs,
            "total_monthly_usd": round(total_monthly, 2),
            "total_annual_usd": round(total_monthly * 12, 2),
            "currency": "USD",
            "note": "Estimates are approximate and based on on-demand pricing",
            "assumptions": [
                "Pricing based on US East region",
                "Does not include data transfer costs",
                "Does not include software licenses",
                "Actual costs may vary"
            ]
        }
    
    def parse_resources(self, terraform_code: str) -> Dict[str, int]:
        """Count resources in Terraform code"""
        resources = {}
        
        # Find all resource declarations
        # Pattern: resource "azurerm_resource_type" "name" {
        pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.findall(pattern, terraform_code)
        
        for resource_type, resource_name in matches:
            resources[resource_type] = resources.get(resource_type, 0) + 1
        
        return resources
    
    def calculate_resource_cost(self, resource_type: str, count: int, terraform_code: str) -> float:
        """Calculate total cost for a resource type"""
        if resource_type not in self.AZURE_PRICES:
            return 0
        
        pricing = self.AZURE_PRICES[resource_type]
        base_cost = 0
        
        # Extract specific SKU/size from Terraform code
        if resource_type == "azurerm_app_service_plan":
            sku = self.extract_sku(terraform_code, resource_type, "sku_name")
            if sku and sku in pricing:
                base_cost = pricing[sku]
            else:
                base_cost = pricing.get("B1", 10.95)
        
        elif resource_type == "azurerm_mssql_database":
            tier = self.extract_sku(terraform_code, resource_type, "sku.name")
            if tier and tier in pricing:
                base_cost = pricing[tier]
            else:
                base_cost = pricing.get("Standard", 50.00)
        
        elif resource_type == "azurerm_kubernetes_cluster":
            # AKS has cluster base cost + per-node cost
            nodes = self.extract_node_count(terraform_code)
            base_cost = pricing.get("cluster_base", 73.44) + (nodes * pricing.get("per_node", 73.44))
        
        elif resource_type == "azurerm_virtual_machine":
            vm_size = self.extract_sku(terraform_code, resource_type, "vm_size")
            if vm_size and vm_size in pricing:
                base_cost = pricing[vm_size]
            else:
                base_cost = pricing.get("B1s", 12.41)
        
        elif resource_type == "azurerm_public_ip":
            is_static = self.is_static_ip(terraform_code)
            base_cost = pricing.get("static", 2.60) if is_static else 0
        
        elif resource_type == "azurerm_container_registry":
            sku = self.extract_sku(terraform_code, resource_type, "sku")
            if sku and sku in pricing:
                base_cost = pricing[sku]
            else:
                base_cost = pricing.get("Basic", 5.00)
        
        elif resource_type == "azurerm_redis_cache":
            sku = self.extract_sku(terraform_code, resource_type, "family")
            if sku and f"basic_{sku.lower()}" in pricing:
                base_cost = pricing[f"basic_{sku.lower()}"]
            else:
                base_cost = pricing.get("basic_c0", 16.95)
        
        elif resource_type == "azurerm_storage_account":
            # Assume 100 GB for estimation
            base_cost = pricing.get("base", 0.0184) * 100
        
        else:
            # Default to base cost if available
            if isinstance(pricing, dict) and "base" in pricing:
                base_cost = pricing["base"]
            elif isinstance(pricing, (int, float)):
                base_cost = pricing
        
        return base_cost * count
    
    def extract_sku(self, terraform_code: str, resource_type: str, field_name: str) -> str:
        """Extract SKU/size value from Terraform code"""
        # Look for pattern: field_name = "value"
        pattern = rf'{field_name}\s*=\s*"([^"]+)"'
        match = re.search(pattern, terraform_code)
        if match:
            return match.group(1)
        return None
    
    def extract_node_count(self, terraform_code: str) -> int:
        """Extract node count from Kubernetes cluster config"""
        pattern = r'node_count\s*=\s*(\d+)'
        match = re.search(pattern, terraform_code)
        if match:
            return int(match.group(1))
        return 3  # Default to 3 nodes
    
    def is_static_ip(self, terraform_code: str) -> bool:
        """Check if public IP is static"""
        pattern = r'allocation_method\s*=\s*"Static"'
        return bool(re.search(pattern, terraform_code))


class AWSCostEstimator:
    """Estimate AWS infrastructure costs"""
    
    AWS_PRICES = {
        "aws_instance": {
            "t2.micro": 0.0116,
            "t2.small": 0.0232,
            "t2.medium": 0.0464,
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "m5.large": 0.096,
            "description": "EC2 Instance"
        },
        "aws_rds_cluster_instance": {
            "db.t3.micro": 0.017,
            "db.t3.small": 0.034,
            "db.r5.large": 0.29,
            "description": "RDS Instance"
        },
        "aws_s3_bucket": {
            "storage_gb": 0.023,
            "description": "S3 Bucket"
        },
        "aws_elb": {
            "base": 16.20,
            "description": "Classic Load Balancer"
        },
        "aws_lb": {
            "alb": 16.20,
            "nlb": 32.40,
            "description": "Application/Network Load Balancer"
        },
    }
    
    def estimate(self, terraform_code: str) -> Dict:
        """Estimate AWS costs"""
        resources = self.parse_resources(terraform_code)
        costs = {}
        total_monthly = 0
        
        for resource_type, count in resources.items():
            if resource_type in self.AWS_PRICES:
                cost = self.calculate_resource_cost(resource_type, count)
                if cost > 0:
                    costs[resource_type] = {
                        "count": count,
                        "monthly_cost": round(cost, 2),
                        "description": self.AWS_PRICES[resource_type].get("description", resource_type)
                    }
                    total_monthly += cost
        
        return {
            "resources": costs,
            "total_monthly_usd": round(total_monthly, 2),
            "total_annual_usd": round(total_monthly * 12, 2),
            "currency": "USD",
            "note": "Estimates are approximate and based on on-demand pricing (US East region)"
        }
    
    def parse_resources(self, terraform_code: str) -> Dict[str, int]:
        """Count AWS resources"""
        resources = {}
        pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.findall(pattern, terraform_code)
        
        for resource_type, _ in matches:
            resources[resource_type] = resources.get(resource_type, 0) + 1
        
        return resources
    
    def calculate_resource_cost(self, resource_type: str, count: int) -> float:
        """Calculate AWS resource cost"""
        if resource_type not in self.AWS_PRICES:
            return 0
        
        pricing = self.AWS_PRICES[resource_type]
        base_cost = pricing.get("base", pricing.get("t2.micro", 0.0116))
        return base_cost * count * 730  # Hours per month


class GCPCostEstimator:
    """Estimate GCP infrastructure costs"""
    
    GCP_PRICES = {
        "google_compute_instance": {
            "e2-micro": 0.025,
            "e2-small": 0.050,
            "n1-standard-1": 0.048,
            "description": "Compute Engine Instance"
        },
        "google_sql_database_instance": {
            "db-f1-micro": 0.01,
            "db-n1-standard-1": 0.109,
            "description": "Cloud SQL Instance"
        },
        "google_storage_bucket": {
            "storage_gb": 0.020,
            "description": "Cloud Storage Bucket"
        },
    }
    
    def estimate(self, terraform_code: str) -> Dict:
        """Estimate GCP costs"""
        resources = self.parse_resources(terraform_code)
        costs = {}
        total_monthly = 0
        
        for resource_type, count in resources.items():
            if resource_type in self.GCP_PRICES:
                cost = self.calculate_resource_cost(resource_type, count)
                if cost > 0:
                    costs[resource_type] = {
                        "count": count,
                        "monthly_cost": round(cost, 2),
                        "description": self.GCP_PRICES[resource_type].get("description", resource_type)
                    }
                    total_monthly += cost
        
        return {
            "resources": costs,
            "total_monthly_usd": round(total_monthly, 2),
            "total_annual_usd": round(total_monthly * 12, 2),
            "currency": "USD",
            "note": "Estimates are approximate (US region)"
        }
    
    def parse_resources(self, terraform_code: str) -> Dict[str, int]:
        """Count GCP resources"""
        resources = {}
        pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.findall(pattern, terraform_code)
        
        for resource_type, _ in matches:
            resources[resource_type] = resources.get(resource_type, 0) + 1
        
        return resources
    
    def calculate_resource_cost(self, resource_type: str, count: int) -> float:
        """Calculate GCP resource cost"""
        if resource_type not in self.GCP_PRICES:
            return 0
        
        pricing = self.GCP_PRICES[resource_type]
        base_cost = pricing.get("base", pricing.get("e2-micro", 0.025))
        return base_cost * count * 730  # Hours per month
