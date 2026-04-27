# Load a JSON config, validate required keys exist, and print missing keys and missing value of existed keys.

import json

path = "Python Scripts/Scripts/JSON_YAML scripts/1_config.json"
required_key = {
        "app": ["name", "env","type"],
        "server": ["host", "port","name"],
        "database": ["type", "host", "port", "name"]
}

def validate_json(path):
    with open(path,'r') as f:
        data = json.load(f)

    missing_keys = []
    invalid_values = []
    for parent, children in required_key.items():
        if parent not in data:
            for child in children:
                missing_keys.append(f"{parent}.{child}")
            continue

        for child in children:
            if child not in data[parent]:
                missing_keys.append(f"{parent}.{child}")
            else:
                value = data[parent][child]
                if value in (None,"",[]):
                    invalid_values.append(f"{parent}.{child}")

    return missing_keys,invalid_values

missing_keys,invalid_values = validate_json(path)

print(f"List of Missing Keys is: {missing_keys}")
print(f"List of keys with missing Values: {invalid_values}")