import json

cluster = {
    "name": "aks-prod",
    "region": "Central India",
    "node_count": 3
}

json_data = json.dumps(cluster, indent=2)

print(json_data)

import json

response = '''
{
  "name": "aks-prod",
  "status": "Running"
}
'''

data = json.loads(response)

print(data["name"])
print(data["status"])

with open("cluster.json", "w") as file:
    json.dump(cluster, file, indent=2)

print(f"VM Name : {cluster['name']}")
print(f"OS : {cluster['os']}")
print(f"CPU : {cluster['cpu']}")
print(f"Memory : {cluster['memory']} GB")
