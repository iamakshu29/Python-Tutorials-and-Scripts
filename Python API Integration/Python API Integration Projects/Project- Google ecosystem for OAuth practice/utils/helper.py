import logging
import os
import json

# convert response to json in a file
def save_json(json_path,data):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path,"w") as f:
        json.dump(data,f,indent=4)

# put data to a file
def save_data(file_path,data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path,"w") as f:
        json.dump(data, f)
        f.write("\n")