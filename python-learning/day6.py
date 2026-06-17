with open("clusters.txt", "r") as file:
    content = file.read()

print(content)

with open("clusters.txt", "r") as file:
    for line in file:
        print(line.strip())

with open("report.txt", "w") as file:
    file.write("AKS Health Report")        

with open("report.txt","w") as file:
    file.write("prod-vm-01")
    file.write("\n")
    file.write("prod-vm-02")
    file.write("\n")
    file.write("prod-vm-03")

with open("report.txt","r") as file:
    for line in file:
        print(f"Server : {line.strip()}")   