# Tasks:
# Update a specific key in a YAML file (simulate values.yaml change).
# Parse AWS CLI JSON output and extract instance IDs.
# Convert JSON → YAML and YAML → JSON.

# pip install pyyaml

# Update a specific key in a YAML file (simulate values.yaml change).
import yaml

def change_tagValue(path):
    with open(path) as f:
        data = yaml.safe_load(f)

# yaml.safe_load turn the yml to dict and to get data from dict use the below syntax
    currValue = data['image']['tag']

    if currValue == "2.3.4":
        data['image']['tag'] = "2.3.5"
    else:
        data['image']['tag'] = "2.3.4"

    with open(path, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False)

path = "./value.yml"
# change_tagValue(path)


# ----------------------------------------------------------------------------------------------------------
# load → reads from a file (or file-like object).
# loads → reads from a string in memory.

# Parse AWS CLI JSON output and extract instance IDs.
import json

path = "./aws_cli.json"

def get_instanceID(path):
    with open(path) as f:
        data = json.load(f)

    for reservation in data.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            print(instance["InstanceId"])

get_instanceID(path)

# ============================================

#  using subprocess
import subprocess
result = subprocess.run(["aws", "ec2", "describe-instances", "--output", "json"],capture_output=True,text=True)

data = json.loads(result.stdout)


for reservation in data.get("Reservations", []):
    for instance in reservation.get("Instances", []):
        print(instance["InstanceId"])

# data.get(key, default_value) -> to get the value of key from dictionary and if key not present return default value . In this case empty list as value is a list of instances

# ----------------------------------------------------------------------------------------------------------
# Convert JSON → YAML and YAML → JSON.



# ----------------------------------------------------------------------------------------------------------

#1. How to get a VALUE for a single key
    # Works only if "key" exists
    # Otherwise raises KeyError
if "key" in data:
    value = data["key"]

#2. How to get a VALUE for nested keys (data["a"]["b"])
if "a" in data and "b" in data["a"]:
    value = data["a"]["b"]

#3. How to get KEYS
data.keys()

#4. For child keys
    # in checks KEYS, never values
for k in data["a"]:
    print(k)

#5. If you want to iterate over both keys and values, you use dict.items().
for key, value in data.items():
    print(key, value)

# =============================================

data = {
    "app": {
        "name": "myapp",
        "env": "prod"
    },
    "server": {
        "host": "localhost",
        "port": 8080
    },
    "version": "1.0"
}

#6. Nested dictionaries
for parent, child_dict in data.items():
    if isinstance(child_dict, dict): # check if the value is another dict, if we not use this it will fail at version 
        for child_key, child_value in child_dict.items():
            print(parent, child_key, child_value)
