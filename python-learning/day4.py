cpu_usage = 85

if cpu_usage > 80:
    print("High CPU")
else:
    print("CPU Normal")

cpu_usage = 65

if cpu_usage > 80:
    print("Critical")
elif cpu_usage > 60:
    print("Warning")
else:
    print("Healthy")

cluster = {
    "name": "aks-prod",
    "cpu": 92
}

if cluster["cpu"] > 80:
    print(f"{cluster['name']} requires investigation")    

vm = {
    "name": "prod-vm-01",
    "cpu": 75
}
def status_check(vm):
    if vm["cpu"] > 80:
        return "Critical"
    elif vm["cpu"] > 60:
        return "Warning"
    else:
        return "Healthy"

status = status_check(vm)
print(status)        

def check_memory(memory):
    if memory > 85:
        return "Critical"
    elif memory > 70:
        return "Warning"
    else:
        return "Healthy"

print(check_memory(90))
print(check_memory(65))
print(check_memory(40))