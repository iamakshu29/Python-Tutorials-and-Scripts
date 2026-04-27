from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from requests.models import HTTPError
from log_utils.logger import log_event
import requests
import logging
import os


# for write access, if required
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# OAuth Code which takes credentials.json file and create temp token which get refreshed and we need to authenticate only once. Not everytime we run the script.
def get_authenticated(credentials_path,SCOPES):
    try:
        creds = None

        # Load saved credentials if they exist
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            log_event(logging.INFO,"Loading Existing Tokens")

        # If no valid creds, refresh or re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())   # silent refresh
                log_event(logging.INFO,"Tokens Refreshed")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open("token.json", 'w') as token:
                token.write(creds.to_json())
        return creds
    except requests.exceptions.SSLError as e:
        log_event(logging.ERROR,"SSL Error",error_type=type(e).__name__,error_message=str(e))
    except requests.exceptions.ConnectionError as e:
        log_event(logging.ERROR,"request_exception",error_message=str(e))
    except HTTPError as e:
        log_event(logging.ERROR,"HTTPError",error_type=type(e).__name__,error_message=str(e))