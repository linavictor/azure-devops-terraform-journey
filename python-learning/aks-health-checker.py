import json
with open("aks.json","r") as file:
    cluster = json.load(file)

print(cluster)

def aks_health(cluster):
    for c in cluster:
        if c["cpu"] >= 65:
            print(f"{c['name']} - Healthy")
        elif c["cpu"] >= 80:
            print(f"{c['name']} - Unhealthy")    
        else:
            print(f"{c['name']} - High CPU")    

aks_health(cluster)
