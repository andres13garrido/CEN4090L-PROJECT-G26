import base64
from email.mime.text import MIMEText
from typing import Optional, List, Dict
from googleapiclient.errors import HttpError
from auth import auth_gmail
from email.utils import getaddresses, parseaddr, formatdate, make_msgid

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
            out.append({"id": full.get("id"), "threadId": full.get("threadId"), "snippet": full.get("snippet")})
        return {"messages": out}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status": e.status_code, "detail": str(e)}}

def gmail_delete(message_id: str, permanent: bool = True) -> dict:
    """
    Delete a message. If permanent=True, permanently deletes it.
    If permanent=False, moves it to Trash.
    """
    svc = auth_gmail()
    try:
        if permanent:
            svc.users().messages().delete(userId="me", id=message_id).execute()
            return {"id": message_id, "action": "deleted"}
        else:
            svc.users().messages().trash(userId="me", id=message_id).execute()
            return {"id": message_id, "action": "trashed"}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status": e.status_code, "detail": str(e)}}

def gmail_list_unread(limit: int = 10, in_inbox: bool = True) -> dict:
    """
    List unread messages (optionally restricted to INBOX) with From/Subject/Date + snippet.
    """
    svc = auth_gmail()
    try:
        q = "is:unread"
        if in_inbox:
            q = "in:inbox " + q

        res = svc.users().messages().list(userId="me", q=q, maxResults=limit).execute()
        msgs = res.get("messages", []) or []
        out = []

        for m in msgs:
            full = svc.users().messages().get(
                userId="me",
                id=m["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()
            headers = {}
            for h in full.get("payload", {}).get("headers", []):
                name, val = h.get("name"), h.get("value")
                if name:
                    headers[name] = val
            out.append({
                "id": full.get("id"),
                "threadId": full.get("threadId"),
                "snippet": full.get("snippet"),
                "headers": {
                    "From": headers.get("From"),
                    "Subject": headers.get("Subject"),
                    "Date": headers.get("Date"),
                }
            })
        return {"messages": out}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status": e.status_code, "detail": str(e)}}

def gmail_reply(thread_id: str, body: str, html: bool = False, reply_all: bool = False) -> dict:
    """
    Reply to the latest message in a thread.
    - If reply_all=False: replies to the last sender only.
    - If reply_all=True: includes original To/Cc/From (excluding yourself).
    """
    svc = auth_gmail()
    try:
        me = svc.users().getProfile(userId="me").execute().get("emailAddress", "").lower()

        thread = svc.users().threads().get(
            userId="me",
            id=thread_id,
            format="metadata",
            metadataHeaders=["From", "To", "Cc", "Subject", "Message-Id", "References"]
        ).execute()
        messages = thread.get("messages", [])
        if not messages:
            return {"error": {"type": "NOT_FOUND", "detail": "Thread has no messages"}}

        last = messages[-1]
        hdrs = {}
        for h in last.get("payload", {}).get("headers", []):
            name, val = h.get("name"), h.get("value")
            if name:
                hdrs[name] = val

        subj = hdrs.get("Subject", "")
        if not subj.lower().startswith("re:"):
            subj = f"Re: {subj}" if subj else "Re:"

        # build the recipient list
        from_addr = parseaddr(hdrs.get("From", ""))[1]
        recipients = []

        if reply_all:
            raw = []
            for key in ("From", "To", "Cc"):
                if hdrs.get(key):
                    raw.extend(getaddresses([hdrs[key]]))
            seen = set()
            for _, email in raw:
                e = (email or "").strip().lower()
                if e and e != me and e not in seen:
                    recipients.append(e)
                    seen.add(e)
            if not recipients and from_addr:
                recipients = [from_addr]
        else:
            if from_addr:
                recipients = [from_addr]

        # build MIME
        msg = MIMEText(body, _subtype="html" if html else "plain", _charset="utf-8")
        if recipients:
            msg["To"] = ", ".join(recipients)
        msg["Subject"] = subj
        msg["Date"] = formatdate(localtime=True)
        msg["Message-Id"] = make_msgid()

        # thread headers (for proper Gmail threading)
        if hdrs.get("Message-Id"):
            msg["In-Reply-To"] = hdrs["Message-Id"]
            refs = hdrs.get("References")
            msg["References"] = (refs + " " + hdrs["Message-Id"]) if refs else hdrs["Message-Id"]

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        sent = svc.users().messages().send(
            userId="me",
            body={"raw": raw, "threadId": thread_id}
        ).execute()

        return {"id": sent.get("id"), "threadId": sent.get("threadId")}
    except HttpError as e:
        return {"error": {"type": "GMAIL_HTTP_ERROR", "status": e.status_code, "detail": str(e)}}