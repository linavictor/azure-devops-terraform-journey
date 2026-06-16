name = "Lina"
experience = 5.5
cloud = "Azure"
knows_kubernetes = True

print(f"Name: {name}")
print(f"Experience: {experience}")
print(f"Cloud: {cloud}")
print(f"Kubernetes: {knows_kubernetes}")

name = "Myl"
experience = 6
favorite_cloud = "Azure"
favorite_tool = "Terraform"
print(f"Name: {name} ; Experience: {experience} ; Favorite Cloud: {favorite_cloud} ; Favorite Tool: {favorite_tool}")

tools = ["Azure", "Terraform", "Kubernetes", "GitHub Actions"]

for tool in tools:
    print(f"Tool: {tool}")