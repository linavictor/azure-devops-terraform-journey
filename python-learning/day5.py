def check_cpu(cpu):
    if cpu > 80:
        return "High CPU"
    return "Healthy"

print(check_cpu(85))

vm = {
    "name": "prod-vm-01",
    "os": "Linux",
    "cpu": 4,
    "memory": 16
}

print(f"VM Name: {vm['name']}")
print(f"OS: {vm['os']}")
print(f"CPU: {vm['cpu']}")
print(f"Memory: {vm['memory']}")
