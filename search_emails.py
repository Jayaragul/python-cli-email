import email
import numpy as np
from imap_client import get_imap_connection
from sentence_transformers import SentenceTransformer
import faiss
from email import message_from_bytes

model = SentenceTransformer("all-mpnet-base-v2")

def extract_email_body(msg_obj):
    """Extract plain text from an email message object."""
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
    return body

def semantic_search_emails(query, limit=20):
    """Perform semantic search on the last N emails using MPNet + FAISS."""
    try:
        imap = get_imap_connection()
        imap.select("inbox")
        status, data = imap.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("\U0001F4ED No emails found.")
            return

        email_ids = email_ids[-limit:]  # Latest N emails
        emails, texts = [], []

        print(f"\n\U0001F4E5 Fetching last {limit} emails...\n")
        for eid in reversed(email_ids):
            _, msg_data = imap.fetch(eid, "(RFC822)")
            for resp in msg_data:
                if isinstance(resp, tuple):
                    msg_obj = message_from_bytes(resp[1])
                    subject = msg_obj.get("Subject", "")
                    sender = msg_obj.get("From", "")
                    date = msg_obj.get("Date", "")
                    body = extract_email_body(msg_obj)

                    combined = f"{subject}\n{body}".strip().replace("\r", "")
                    emails.append({
                        "subject": subject,
                        "from": sender,
                        "date": date,
                        "preview": body[:300],
                        "combined": combined
                    })
                    texts.append(combined)

        print("\U0001F9E0 Encoding with MPNet...")
        vectors = model.encode(texts, show_progress_bar=False)
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(np.array(vectors))

        query_vec = model.encode([query])
        D, I = index.search(query_vec, k=5)

        print(f"\n\U0001F50D Top semantic matches for: '{query}'\n")
        for idx in I[0]:
            mail = emails[idx]
            print("=" * 60)
            print(f"\U0001F4E7 Subject : {mail['subject']}")
            print(f"\U0001F464 From    : {mail['from']}")
            print(f"\U0001F552 Date    : {mail['date']}")
            print(f"\U0001F4C4 Preview : {mail['preview'].strip()}...\n")

        imap.logout()

    except Exception as e:
        print(f"\u274C Error: {e}")
