import argparse

from config.settings import GITHUB_TOKEN, OPENWEATHER_API_KEY
from services.github_service import fetch_user, fetch_repos, get_top_repos
from services.weather_service import fetch_weather
from utils.helpers import kelvin_to_celsius, generate_insight, configure_logging
from utils.file_handler import save_json, get_json_format
from models.schema import build_output

def main():
    parser = argparse.ArgumentParser(description="Fetch data from user")
    parser.add_argument("--username",default="LondheShubham153",help="Enter the GitHub Username to check the Repos")
    parser.add_argument("--city",default="Delhi",help="Enter the city name to check the weather")
    args = parser.parse_args()

    # file paths
    log_file = "./practice_and_projects/Project- Multi API Integration/logs/app.log"
    json_path = "./practice_and_projects/Project- Multi API Integration/data.json"
    
    configure_logging(log_file)
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    # Get User Info
    user = fetch_user(args.username, headers=headers)
    if not user:
        return
    
    # Get User's repo Info
    repos = fetch_repos(args.username, headers=headers)
    if not fetch_repos:
        return

    # Weather API
    weather = fetch_weather(OPENWEATHER_API_KEY, args.city)
    if not weather:
        return
    temp = kelvin_to_celsius(weather['main']['temp'])

    # merging the data from 2 APIs
    output = build_output(args.username, weather, temp, public_repos_count = user["public_repos"], top_repos = get_top_repos(repos))

    # adding insights based on temp to the final output
    output["insight"] = generate_insight(temp)

    # export the merged data to json
    save_json(json_path,output)

    # printing the output
    print(get_json_format(output))

if __name__ == "__main__":
    main()

# To use the script - python app.py --username iam-veeramalla --city Hyderabad