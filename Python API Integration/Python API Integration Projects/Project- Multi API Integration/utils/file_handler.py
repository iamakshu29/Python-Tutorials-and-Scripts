import logging
import os
import json

# format data to JSON
def get_json_format(data):
    try:
        return json.dumps(data,indent=4)
    except TypeError as e:
        logging.error(e)

# save data to json file
def save_json(json_path, data):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path,"w") as f:
        json.dump(data,f,indent=4)