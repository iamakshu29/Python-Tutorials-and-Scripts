# Practice for OAuth API using Google ecosystem (TOP priority)
# Google Sheets
# Google Drive
# Gmail
# Why:
# Almost every business uses them
# Common tasks:
# Read/write Sheets
# Upload files to Drive
# Send emails automatically

"""
ISSUE what I am facing or thinking
there are so many functions with almost same try: exception: template...so I think of creating a master function and just call all other functions to that function under try: 
"""

"""
What NEW I did this time in this???
Configure and Use OAuth 
As per the logging, I shift it to structure logging (JSON preferred)
Use the mock server to send the data
"""


"""I 
LINKS
Google Sheets API Overview - https://developers.google.com/workspace/sheets/api/reference/rest
Configure the OAuth consent screen and choose scopes - https://developers.google.com/workspace/guides/configure-oauth-consent
"""

from auth.oauth import get_authenticated
from config.settings import MOCK_SERVICE_API_KEY
from services.google_sheet_api import get_sheet_data, find_new_status
from utils.helper import save_json, save_data
from services.mock_service import send_data
from log_utils.logger import log_event, configure_logging
import argparse
import logging


def main():
# configuring argparse for user input
    parser = argparse.ArgumentParser(description="Fetch data from user")
    parser.add_argument("--sheetID",default="1cIYyoGOayEzUGWpZQm9mYmNwjMjmD3raargdEi5aXkI",help="Enter the SpreadSheet ID from Google Sheets")
    parser.add_argument("--sheetName",default="leads_data",help="Enter the Sheet Name of SpreadSheet ID from Google Sheets")
    args = parser.parse_args()

# Logging setup
    log_file = "./logs/app.log"
    configure_logging(log_file)

# Paths to send data
    json_path = "./data.json"
    output_path = "./name.txt"

# Configuring OAuth
    credentials_path = "credentials.json"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = get_authenticated(credentials_path,SCOPES)
    if not creds:
        log_event(logging.ERROR,"OAth Connection Failed")
        return
    else:
        log_event(logging.INFO,"OAth Connection Successful")

# Get data from sheets API
    get_fields = get_sheet_data(args.sheetID,args.sheetName,creds.token)
    if not get_fields:
        log_event(logging.ERROR,"Getting Error while retrieving data fields from Google Sheets API")
        return
    else:
        log_event(logging.INFO,"Data fields are retrieved from Google Sheets API")

# Export data to json
    save_json(json_path,get_fields)
    log_event(logging.INFO,f"Transformed data fields exported to {json_path}")

# Transform and Export data to .txt
    names_list = find_new_status(get_fields)

# saving data to file, .....optional, delete later.
    save_data(output_path,names_list)
    log_event(logging.INFO,f"Transformed data fields exported to {output_path}")

# send data to mock_service API
    send_data(MOCK_SERVICE_API_KEY,names_list)

    print("Done")

if __name__ == "__main__":
    main()