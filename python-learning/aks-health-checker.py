clusters = [
    {"name": "aks-dev", "cpu": 45},
    {"name": "aks-test", "cpu": 60},
    {"name": "aks-prod", "cpu": 90}
]

def aks_health(clusters):
    for cluster in clusters:
        if cluster["cpu"] >= 65:
            print(f"{cluster["name"]} - Healthy")
        elif cluster["cpu"] >= 80:
            print(f"{cluster["name"]} - Unhealthy")    
        else:
            print(f"{cluster["name"]} - High CPU")    
        return print("== AKS Health Check ==")

print(aks_health(clusters))
