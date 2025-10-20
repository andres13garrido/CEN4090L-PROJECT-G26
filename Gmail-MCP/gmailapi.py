import base64
from email.mime.text import MIMEText
from typing import Optional, List, Dict
from googleapiclient.errors import HttpError
from tools.gmail.auth import auth_gmail

def send_email(to: str, subject: str, body: str, html: bool=False)-> dict:
    svc = auth_gmail()
    msg = MIMEText(body, _subtype="html" if html else "plain")
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        res = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"id": res["id"]}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status" : e.status_code, "detail": str(e)}}

def search_emails(query: str= "", limit: int = 10) -> dict:
    svc = auth_gmail()
    try:
        res = svc.users().messages().list(userId="me", q=query, maxResults=limit).execute()
        msgs = res.get("messages", [])

        out = []
        for m in msgs:
            full= svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
            out.append({"id": full[id], "threadId": full.get("threadId"), "snippet": full.get("snippet")})
        return {"messages": out}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status": e.status_code, "detail": str(e)}}
