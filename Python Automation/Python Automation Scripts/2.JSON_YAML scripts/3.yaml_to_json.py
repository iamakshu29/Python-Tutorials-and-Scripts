# Convert a YAML file into a flattened JSON structure.

import json
import yaml

path = "Python Scripts\Scripts/JSON_YAML scripts/value.yml"

def yaml_to_json(path):
    with open(path,"r") as f:
        return json.dumps(yaml.safe_load(f),indent=1)

print(yaml_to_json(path))