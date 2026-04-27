# 2_02_Oauth_authentication.py — OAuth 2.0 with Google APIs

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# =============================================
# SCOPES
# =============================================
# Defines what permissions the app requests from the user.
# "readonly" — can read sheets but cannot modify them.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# =============================================
# STEP 1: Load saved credentials
# =============================================
# token.json is created after the first login — no browser needed on repeat runs.
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# =============================================
# STEP 2: Refresh or re-authenticate if needed
# =============================================
# Credentials become invalid when expired or missing entirely.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())   # Access token expired — silently fetch a new one using refresh_token
    else:
        # First run or token revoked — opens browser for user consent
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES  # credentials.json comes from Google Cloud Console
        )
        creds = flow.run_local_server(port=0)  # port=0 lets OS pick a free port

    # =============================================
    # STEP 3: Persist credentials for next run
    # =============================================
    # Saves both access token and refresh token — avoids re-login on next run.
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        
"""
How this behaves ?
    First run:
        Opens browser → you log in
        Saves token.json
    Next runs:
        Uses saved token
        No browser popup
    When access token expires (~1 hour):
        Automatically refreshed using refresh_token
        Still no browser interaction

When you WILL be asked again
You'll re-authenticate only if:
    You delete token.json
    You change SCOPES
    The refresh token is revoked (e.g., from Google account security settings)
    You switch Google accounts
"""