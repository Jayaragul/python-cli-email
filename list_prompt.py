import email
from email.header import decode_header
from imap_client import get_imap_connection

def list_emails(limit):
    imap = get_imap_connection()
    status, messages = imap.search(None, "ALL")
    email_ids = messages[0].split()
    selected_ids = email_ids[-limit:]

    for i, eid in enumerate(reversed(selected_ids), 1):
        res, msg = imap.fetch(eid, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg_obj = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg_obj["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")
                print(f"{i}) {subject}")
    imap.logout()
