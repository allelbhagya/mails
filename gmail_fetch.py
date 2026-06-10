import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        # using created token
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # else create token

    if not creds or not creds.valid:
        # if token expired, refresh token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # if no token at all, open browser window to ask the user login
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_emails(n=10):

    service = get_gmail_service()

    # get only last 10 mails
    results = service.users().messages().list(userId="me", maxResults=n).execute()
    messages = results.get("messages", [])
    # only returns ids

    emails = []
    for msg in messages:
        data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = data["payload"]
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        body = ""
        if "parts" in payload:
            # emails with parts array of plain text and html - attachments
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"].get("data", "")
                    # gmail storing data as base64 encoded text
                    # safe way to transmit binary data (attachment)
                    body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
                    break
        else:
            body_data = payload.get("body", {}).get("data", "")
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
        emails.append({"subject": subject, "sender": sender, "body": body[:500]})
        # returning list of {subject, sender, body}

    return emails