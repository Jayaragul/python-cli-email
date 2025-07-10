import email
from imap_client import get_imap_connection

def fetch_email_by_number(limit, number):
    imap = get_imap_connection()
    status, messages = imap.search(None, "ALL")
    email_ids = messages[0].split()
    selected_ids = email_ids[-limit:]
    
    try:
        eid = selected_ids[-number]
        res, msg = imap.fetch(eid, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg_obj = email.message_from_bytes(response[1])
                print("From:", msg_obj["From"])
                print("Subject:", msg_obj["Subject"])
                print("Date:", msg_obj["Date"])
                print("Body:")
                if msg_obj.is_multipart():
                    for part in msg_obj.walk():
                        if part.get_content_type() == "text/plain":
                            print(part.get_payload(decode=True).decode())
                            break
                else:
                    print(msg_obj.get_payload(decode=True).decode())
    except IndexError:
        print("❌ Invalid email number.")
    imap.logout()
