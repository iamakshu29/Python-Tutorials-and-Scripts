# 2_authentication.py — API Authentication Methods (API Key, Bearer Token)

from time import sleep
import requests
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script (works regardless of CWD)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Quick debug — remove after confirming it works
print(f"API_KEY loaded: {bool(API_KEY)}, GITHUB_TOKEN loaded: {bool(GITHUB_TOKEN)}")

# =============================================
# METHOD 1: API Key as Query String (in URL)
# =============================================
# Some APIs expect auth credentials as query parameters in the URL.
# Keys must match what the API docs specify (here: "q" and "appid").

# Way 1: Manually embed params in the URL string
# Syntax: url/path?key1=value1&key2=value2
url = f"https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={API_KEY}"
response = requests.get(url)
# print(response.json())


# Way 2: Pass params as a dict — requests auto-converts to query string
# Becomes: ?q=Bangalore&appid=your_api_key
params = {
    "q":"Bangalore",
    "appid": API_KEY
    }
url = "https://api.openweathermap.org/data/2.5/weather"

response = requests.get(url,params=params)
# print(response.json())


# =============================================
# METHOD 2: Bearer Token as Headers
# =============================================
# Token-based auth sends credentials in HTTP headers, not the URL.
# "Authorization: Bearer <token>" is the standard format for OAuth tokens.
# requests maps each key–value pair in the dict directly into HTTP headers.

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}
response = requests.get("https://api.github.com/user", headers=headers)
# print(response.json())


# =============================================
# PROJECT: Authenticated API Fetch with Logging
# =============================================
# Fetches GitHub user data using Bearer token, saves to JSON, logs errors to file.

url = "https://api.github.com/user"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# Configure logging — errors go to app.log with timestamp and level
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_info():
    try:
        res = requests.get(url,headers=headers, timeout=10)
        res.raise_for_status()  # Raises HTTPError for 4xx/5xx
        data = res.json()

        # Save response to a JSON file
        with open("github_data.json","w",newline="") as f:
            json.dump(data,f,indent=4)

        return data

    # Specific exceptions first, general last (order matters)
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"General request error: {e}")
    except ValueError:
        logging.error(f"Invalid JSON Response")
    
    return None  # Returns None if any exception occurred

# get_info()