import email
from imap_client import get_imap_connection

def search_emails(keyword):
    imap = get_imap_connection()
    imap.select("inbox")
    status, messages = imap.search(None, 'ALL')
    email_ids = messages[0].split()

    print(f"🔍 Searching for '{keyword}' in subject or body...")
    for eid in reversed(email_ids):
        res, msg = imap.fetch(eid, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg_obj = email.message_from_bytes(response[1])
                subject = msg_obj.get("Subject", "")
                body = ""
                if msg_obj.is_multipart():
                    for part in msg_obj.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg_obj.get_payload(decode=True).decode(errors="ignore")

                if keyword.lower() in subject.lower() or keyword.lower() in body.lower():
                    print("-" * 50)
                    print("Subject:", subject)
                    print("From:", msg_obj.get("From"))
                    print("Date:", msg_obj.get("Date"))
                    print("Body Preview:", body[:200])
    imap.logout()
