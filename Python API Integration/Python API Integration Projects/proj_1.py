# Project 1 - basic
# GitHub API fetch
# Add:
    # logging
    # CLI
    # file output

import logging
import requests
import json
import os

# Append and save the new response
def save_data(file_path,data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Get existing data if invalid JSON, return []
def load_existing(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
                return data
        except json.JSONDecodeError:
            logging.error("Invalid JSON in file. Resetting File")
            return []
    return [] # if file not exists somehow

def get_user_info(token,file_path):
    try:
        response = requests.get(github_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logging.info("GitHub API call successful")

        existing = load_existing(file_path)
        existing.append(data)

        save_data(file_path,existing)

        return data