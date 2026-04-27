# Project 2 - multi-API integration
# Fetch from 2 APIs (e.g. GitHub + weather)
# Combine results
# Save merged output

"""
Tasks
Phase 1 - Setup and Planning
Task 1: Choose APIs with endpoints required - DONE
Task 2: Get API Access using api_keys or tokens, store them in .env or export them and get access with os.getenv - DONE
Task 3: Setup Project Folder structure - DONE (but need to learn properly, how to connect functions definition with func calls in main() and .env)

Phase 2 - API Integration
Task 4: GitHub API Integration - DONE
Task 5: Weather API Integration - DONE
Task 6: Error Handling - DONE

Phase 3 — Data Merging
Task 7: Combine Data - DONE
Task 8: Add Logic (important for freelancing value) - DONE

Phase 4 — Output Handling
Task 9: Save Output - DONE
Task 10: Pretty Print CLI Output - DONE

Phase 5 — Advanced
Task 11: Add CLI Inputs - DONE
Task 12: Add Logging - DONE
Task 13: Add Retry Logic - Don't Know YET
Task 14: Use Async (Bonus) - Don't Know YET
Task 14: Use Pagination - Don't Know YET

Move to structure:
clients/
    http_client.py
config/
    settings.py
    .env
logs/
    app.log
models/
    schema.py
services/
    github_service.py
    weather_service.py
utils/
    file_handler.py
    helpers.py
main.py
data.json
readme.md

Add:
retry logic ✔
pagination ✔
async (aiohttp) ✔
Optional:
expose as API (FastAPI)
"""
from json import JSONDecodeError
from pathlib import Path
import requests
import logging
import os
import json
import argparse
from dotenv import load_dotenv

# Setup basic logging
def configure_logging(log_file):
    try:
        os.makedirs(os.path.dirname(log_file),exist_ok=True)
        logging.basicConfig(
            filename = log_file,
            level = logging.INFO,
            format = "%(asctime)s - %(levelname)s - %(message)s"
        )
    except Exception as e:
        return e

# format data to JSON
def get_json_format(data):
    try:
        return json.dumps(data,indent=4)
    except TypeError as e:
        logging.error(e)

# get github token
def get_token(token):
    return {
        "Authorization": f"Bearer {token}"
    }

# get weather api_key
def build_weather_params(api_key,city):
    return {
            "appid": f"{api_key}",
            "q": f"{city}"
        }

# save data to json file
def save_data(json_path, data):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path,"w") as f:
        json.dump(data,f,indent=4)

# get API call
def get_info(url, **kwargs):
    try:
        response = requests.get(url,timeout=10,**kwargs)
        response.raise_for_status()
        logging.info("API run successfully")
        return response.json()

    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection Error {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout Error {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError {e}")
    except (KeyError,TypeError,ValueError) as e:
        logging.error(f"{e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Other Generic error {e}")
    return None

# GITHUB API
def get_user_details(repo_data, public_repos_count,list_per_page):
# to get the repos name and loop till the count of public_repos
    value_till = min(list_per_page, public_repos_count)
# To get the top repo what I need to do is Sort the res based on startgazer_count and got the top 10 repos.
# Storing the repo_name and stars in list of list and sort the stars in descending order
    ans = []
    for i in range(value_till):
        repo_name = repo_data[i]["name"]
        stars = repo_data[i]["stargazers_count"]
        ans.append([repo_name,stars])

    ans.sort(key=lambda x: x[1], reverse=True)
    return ans[:10]

# convert temp to celsius
def kelvin_to_celsius(k):
    return round(k - 273.15, 2)

# merge data retrieve from both APIs
def merge_data(username, ans, city_data, public_repos_count, temp):
        
    user_output = {
            "username": username,
            "public_repos": public_repos_count,
            "top_10_repos": [
            {"name": item[0], "stars": item[1]} for item in ans[:10]
        ]
    }
    # print(user_output)

    weather_output = {
            "city": city_data['name'],
            "temperature": temp,
            "condition": city_data['weather'][0]['description']
    }
    # print(weather_output)
    merged = {
        "developer": user_output,"location_weather": weather_output
    }
    return merged

# add insight based on temp.
def generate_insight(temp):
    if temp > 35:
        return "High temperature, consider indoor work"
    elif temp < 15:
        return "Cool weather, productive coding environment"
    else:
        return "Moderate weather, good for coding"

def main():
    parser = argparse.ArgumentParser(description="Fetch data from user")
    parser.add_argument("--username",default="LondheShubham153",help="Enter the GitHub Username to check the Repos")
    parser.add_argument("--city",default="Delhi",help="Enter the city name to check the weather")
    args = parser.parse_args()

    # file paths
    log_file = "./practice_and_projects/Project- Multi API Integration/logs/app.log"
    json_path = "./practice_and_projects/Project- Multi API Integration/data.json"
    # GitHub API → user profile + repos
    list_per_page = 30
    # Weather API
    openWeather_url = f"https://api.openweathermap.org/data/2.5/weather"
    # github urls
    github_url  = f"https://api.github.com/users/{args.username}"
    repos_url = f"{github_url }/repos?per_page={list_per_page}"
    # Credentials
    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("OPENWEATHER_API_KEY")

    configure_logging(log_file)
    load_dotenv()

    if not token or not api_key:
        raise ValueError("Missing API credentials. Check your .env file.")

    headers = get_token(token)
    params = build_weather_params(api_key, args.city)

    # Get User Info
    user_data = get_info(github_url, headers=headers)
    if not user_data:
        return
    
    # Get User's repo Info
    repo_data = get_info(repos_url, headers=headers)
    if not repo_data:
        return
    # get public Repo details of the Specific user
    public_repos_count = user_data["public_repos"]
    # get the repos with top stars, public repo count and username
    data = get_user_details(repo_data, public_repos_count,list_per_page)

    # Weather API
    city_data = get_info(openWeather_url, params=params)
    if not city_data:
        return
    temp = kelvin_to_celsius(city_data['main']['temp'])

    # merging the data from 2 APIs
    merged = merge_data(args.username, data, city_data, public_repos_count, temp)

    # adding insights based on temp to the final output
    merged["insight"] = generate_insight(temp)

    # export the merged data to json
    save_data(json_path,merged)

    # printing the output
    print(get_json_format(merged))

if __name__ == "__main__":
    main()

# To use the script - python app.py --username iam-veeramalla --city Hyderabad