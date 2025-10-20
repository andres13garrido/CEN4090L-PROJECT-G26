import os
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

cache = None #in process cache

def auth_gmail():
    global cache
    if cache is not None:
        return cache

    creds: Credentials | None= None

    if Path(TOKEN).exists():  #load user saved tokens to login ig they exist
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

    if not creds or not creds.valid: #if missing or invalid, runs or refreshes OAuth flow
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request()) #has tokens, but needs to refresh silently
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0) #no token yet, runs OAuth
        with open(TOKEN, "w") as f: #persistence component
            f.write(creds.to_json())
    cache = build("gmail", "v1", credentials=creds)
    return cache

