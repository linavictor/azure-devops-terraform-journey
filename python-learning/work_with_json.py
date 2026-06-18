import json

# Dictionary to Json file

# cluster = {
#     "name": "aks-prod",
#     "region": "Central India",
#     "node_count": 3
# }

# json_data = json.dumps(cluster, indent=2)

# print(json_data)

# Json to Dictionary

# response = '''
# {
#   "name": "aks-prod",
#   "status": "Running"
# }
# '''

# data = json.loads(response)

# print(data["name"])
# print(data["status"])



with open("cluster.json", "r") as file:
    cluster = json.load(file)

print(f"VM Name : {cluster['name']}")
print(f"OS : {cluster['os']}")
print(f"CPU : {cluster['cpu']}")
print(f"Memory : {cluster['memory']} GB")
