from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
from imap_client import get_imap_connection

def decode_mime_words(s):
    """Decode encoded words in MIME headers (like Subject)."""
    try:
        decoded_parts = decode_header(s)
        return ''.join([
            part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
            for part, charset in decoded_parts
        ])
    except:
        return s

def extract_email_body(msg_obj):
    """Extract plain text body from email."""
    body = ""
    if msg_obj.is_multipart():
        for part in msg_obj.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
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
    return body.strip()

def fetch_email_by_number(limit, number, from_date=None, to_date=None, from_addr=None):
    """Fetch a single email by its number in the filtered + limited list."""
    try:
        imap = get_imap_connection()
        imap.select("inbox")
        status, data = imap.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("📭 No emails found.")
            return

        selected_ids = email_ids[-limit:]
        emails = []

        for eid in reversed(selected_ids):
            _, msg_data = imap.fetch(eid, "(RFC822)")
            for resp in msg_data:
                if isinstance(resp, tuple):
                    try:
                        msg_obj = message_from_bytes(resp[1])
                        sender = msg_obj.get("From", "")
                        date_str = msg_obj.get("Date", "")
                        subject_raw = msg_obj.get("Subject", "")
                        subject = decode_mime_words(subject_raw)

                        # Filter by sender
                        if from_addr and from_addr.lower() not in sender.lower():
                            continue

                        # Filter by date
                        if from_date or to_date:
                            try:
                                msg_date = parsedate_to_datetime(date_str).date()
                                if from_date and msg_date < from_date:
                                    continue
                                if to_date and msg_date > to_date:
                                    continue
                            except:
                                continue

                        emails.append({
                            "msg_obj": msg_obj,
                            "from": sender,
                            "subject": subject,
                            "date": date_str
                        })
                    except Exception as e:
                        print(f"⚠️ Skipping email due to error: {e}")
                        continue

        if number < 1 or number > len(emails):
            print("❌ Invalid email number.")
            return

        selected_email = emails[number - 1]
        msg_obj = selected_email["msg_obj"]

        print(f"From: {selected_email['from']}")
        print(f"Subject: {selected_email['subject']}")
        print(f"Date: {selected_email['date']}")
        print("Body:")
        print(extract_email_body(msg_obj))

        imap.logout()

    except Exception as e:
        print(f"❌ Error fetching email: {e}")
