print("Hello DevOps + AI")
name = "Lina"
experience = 5.5
learning_ai = True
print(name)
print(experience)
name = "Lina"
role = "DevOps Engineer"

print(f"My name is {name} and I am a {role}")

clouds = ["Azure", "AWS", "GCP"]

print(clouds[0])

for cloud in clouds:
    print(cloud)

engineer = {
    "name": "Lina",
    "skill": "Azure",
    "experience": 5.5
}

print(engineer["skill"])    

cpu_usage = 85

if cpu_usage > 80:
    print("High CPU")
else:
    print("CPU Normal")


def greet(name):
    print(f"Hello {name}")

greet("Lina")    

with open("config.txt", "r") as file:
    content = file.read()

print(content)


import json

data = {
    "cluster": "aks-prod",
    "nodes": 3
}

json_data = json.dumps(data, indent=2)

print(json_data)


