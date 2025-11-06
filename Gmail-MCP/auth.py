# auth.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def auth_gmail():
    load_dotenv()

    cred_path = Path(os.getenv("GOOGLE_CREDENTIALS", "credentials.json"))
    token_path = Path(os.getenv("GOOGLE_TOKEN", "token.json"))

    # Basic diagnostics (optional; comment out later)
    # print(f"CWD={os.getcwd()}\ncred={cred_path} exists={cred_path.exists()}\ntoken={token_path} exists={token_path.exists()}")

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silent refresh if possible
            creds.refresh(Request())
        else:
            # Fresh consent
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            try:
                # Opens a browser on a free port
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"run_local_server failed: {e}", file=sys.stderr)
                print("Falling back to console flow…", file=sys.stderr)
                creds = flow.run_console()

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)

if __name__ == "__main__":
    # When you run: uv run python -m auth
    try:
        service = auth_gmail()
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        print("OK — OAuth works. First few labels:", [l["name"] for l in labels[:5]])
    except Exception as e:
        print(f"Auth test failed: {e}", file=sys.stderr)
        sys.exit(1)
