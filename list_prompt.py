import email
from imap_client import get_imap_connection
from email import message_from_bytes
from datetime import datetime

def extract_email_body(msg_obj):
    body = ""
    if msg_obj.is_multipart():
        for part in msg_obj.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
                except:
                    continue
    else:
        try:
            body = msg_obj.get_payload(decode=True).decode(errors="ignore")
        except:
            pass
    return body

def list_emails(limit, from_date=None, to_date=None, from_addr=None):
    """List emails with optional filters: from_date, to_date, sender."""
    try:
        imap = get_imap_connection()
        imap.select("inbox")
        status, data = imap.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("📭 No emails in inbox.")
            return

        email_ids = email_ids[-limit:]
        count = 1

        print(f"\n📄 Listing last {limit} emails...\n")

        for eid in reversed(email_ids):
            _, msg_data = imap.fetch(eid, "(RFC822)")
            for response in msg_data:
                if isinstance(response, tuple):
                    msg_obj = message_from_bytes(response[1])
                    subject = msg_obj.get("Subject", "(No Subject)")
                    sender = msg_obj.get("From", "")
                    date_str = msg_obj.get("Date", "")
                    body = extract_email_body(msg_obj)

                    # Parse date
                    try:
                        email_date = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
                    except:
                        email_date = None

                    # Apply filters
                    if from_date and email_date and email_date < from_date:
                        continue
                    if to_date and email_date and email_date > to_date:
                        continue
                    if from_addr and from_addr.lower() not in sender.lower():
                        continue

                    print(f"{count}) {subject}")
                    count += 1

        imap.logout()
    except Exception as e:
        print(f"❌ Error: {e}")
