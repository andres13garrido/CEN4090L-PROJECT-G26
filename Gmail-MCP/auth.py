import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Scopes for both Gmail and Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar"
]


def _get_credentials():
    """Handles OAuth authentication and token refresh."""
    load_dotenv()

    cred_path = Path(os.getenv("GOOGLE_CREDENTIALS", "credentials.json"))
    token_path = Path(os.getenv("GOOGLE_TOKEN", "token.json"))

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"run_local_server failed: {e}", file=sys.stderr)
                print("Falling back to console flow…", file=sys.stderr)
                creds = flow.run_console()

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def auth_gmail():
    """Return Gmail service client."""
    creds = _get_credentials()
    return build("gmail", "v1", credentials=creds)


def auth_calendar():
    """Return Calendar service client."""
    creds = _get_credentials()
    return build("calendar", "v3", credentials=creds)


if __name__ == "__main__":
    # Test both Gmail and Calendar
    try:
        gmail = auth_gmail()
        labels = gmail.users().labels().list(userId="me").execute().get("labels", [])
        print("✅ Gmail OK — First few labels:", [l["name"] for l in labels[:3]])

        calendar = auth_calendar()
        cal_list = calendar.calendarList().list(maxResults=3).execute().get("items", [])
        print("✅ Calendar OK — Found calendars:", [c["summary"] for c in cal_list])

    except Exception as e:
        print(f"❌ Auth test failed: {e}", file=sys.stderr)
        sys.exit(1)
